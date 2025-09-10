import unittest
import logging
from N2KClient.n2kclient.models.constants import Constants
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineDevice
from N2KClient.n2kclient.models.n2k_configuration.engine_configuration import (
    EngineConfiguration,
)
from N2KClient.n2kclient.models.n2k_configuration.value_u32 import ValueU32
from N2KClient.n2kclient.services.alarm_service.alarm_processors import (
    process_device_alarms,
    process_ac_meter_alarms,
    process_bls_alarms,
    process_circuit_load_alarms,
    process_dc_meter_alarms,
    process_smartcraft_alarms,
    process_tank_alarms,
    map_sc_engine_instance_to_engine_name,
)
from N2KClient.n2kclient.models.empower_system.component_reference import (
    ComponentReference,
)
from N2KClient.n2kclient.models.common_enums import ComponentType, eAlarmType
from N2KClient.n2kclient.models.n2k_configuration.n2k_configuation import (
    N2kConfiguration,
)
from N2KClient.n2kclient.models.n2k_configuration.alarm import Alarm

from N2KClient.n2kclient.models.n2k_configuration.circuit import Circuit, CircuitLoad
from N2KClient.n2kclient.models.n2k_configuration.ac_meter import ACMeter
from N2KClient.n2kclient.models.n2k_configuration.instance import Instance
from N2KClient.n2kclient.models.n2k_configuration.ac import AC
from N2KClient.n2kclient.models.n2k_configuration.dc import DC
from N2KClient.n2kclient.models.n2k_configuration.tank import Tank
from N2KClient.n2kclient.models.n2k_configuration.category_item import CategoryItem
from N2KClient.n2kclient.models.n2k_configuration.inverter_charger import (
    InverterChargerDevice,
)

from N2KClient.n2kclient.models.n2k_configuration.instance import Instance
from N2KClient.n2kclient.models.n2k_configuration.data_id import DataId
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.models.n2k_configuration.device import Device, DeviceType
from N2KClient.n2kclient.models.n2k_configuration.ui_relationship_msg import (
    UiRelationShipMsg,
    ItemType,
    RelationshipType,
)
from N2KClient.n2kclient.models.n2k_configuration.alarm_limit import AlarmLimit
from N2KClient.n2kclient.models.n2k_configuration.bls_alarm_mapping import (
    BLSAlarmMapping,
)
from N2KClient.n2kclient.models.n2k_configuration.binary_logic_state import (
    BinaryLogicState,
)


class AlarmProcessorTest(unittest.TestCase):
    """Unit tests for the alarm processing functions."""

    def test_process_device_alarm_circuit(self):
        """
        Verifies that process_device_alarms returns a CIRCUIT component when a matching circuit
        is present in the configuration and the alarm type is TypeSleepWarning.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 4
        config = N2kConfiguration()
        circuit = Circuit(
            id=ValueU32(value=1, valid=True),
            name_utf8="testCircuitDevice",
            control_id=1,
            dimmable=False,
            categories=[CategoryItem(name_utf8="testCategory", enabled=True, index=0)],
            circuit_loads=[CircuitLoad(channel_address=resolved_alarm_channel_id << 8)],
        )
        config.circuit[0] = circuit
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.TypeSleepWarning)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertTrue(any(c.component_type == ComponentType.CIRCUIT for c in res))
        self.assertEqual(res[0].thing.control_id, 1)

    def test_process_device_alarm_circuit_channel_address_none(self):
        """
        Verifies that process_device_alarms returns a CIRCUIT component when a matching circuit
        is present in the configuration and the alarm type is TypeSleepWarning.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 4
        config = N2kConfiguration()
        circuit = Circuit(
            id=ValueU32(value=1, valid=True),
            name_utf8="testCircuitDevice",
            control_id=1,
            dimmable=False,
            categories=[
                CategoryItem(
                    name_utf8="testCategory",
                    enabled=True,
                    index=0,
                )
            ],
            circuit_loads=[MagicMock(channel_address=None)],
        )
        config.circuit[0] = circuit
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.TypeSleepWarning)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertFalse(any(c.component_type == ComponentType.CIRCUIT for c in res))

    def test_process_device_alarm_ac(self):
        """
        Verifies that process_device_alarms returns an ACMETER component when a matching AC meter
        is present in the configuration and the alarm type is TypeSleepWarning.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 4
        config = N2kConfiguration()
        ac_meter = ACMeter(
            line={1: AC(address=1234)},
        )
        config.ac[0] = ac_meter
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.TypeSleepWarning)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertTrue(any(c.component_type == ComponentType.ACMETER for c in res))
        self.assertEqual(res[0].thing.address, 1234)

    def test_process_device_alarm_dc(self):
        """
        Verifies that process_device_alarms returns a DCMETER component and correct instance
        when a matching DC meter is present in the configuration and the alarm type is TypeSleepWarning.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 4
        config = N2kConfiguration()
        dc_meter = DC(instance=Instance(enabled=True, instance=1), address=1234)
        config.dc[0] = dc_meter
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.TypeSleepWarning)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.instance.instance, 1)

    def test_process_device_alarm_dc_address_none(self):
        """
        Verifies that process_device_alarms returns a DCMETER component and correct instance
        when a matching DC meter is present in the configuration and the alarm type is TypeSleepWarning.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 4
        config = N2kConfiguration()
        dc_meter = DC(instance=Instance(enabled=True, instance=1), address=None)
        config.dc[0] = dc_meter
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.TypeSleepWarning)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertFalse(any(c.component_type == ComponentType.DCMETER for c in res))

    def test_process_device_alarm_invalid(self):
        """
        Verifies that process_device_alarms returns an empty list when the alarm type is DipswitchConflict,
        indicating no valid components should be returned for this alarm type.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 4
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.DipswitchConflict)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertEqual(res, [])

    def test_process_device_alarm_match(self):
        """
        Verifies that process_device_alarms does not add duplicate components to the result when
        affected_components already contains matching CIRCUIT, DCMETER, and ACMETER components.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 4
        config = N2kConfiguration()
        # DC
        dc_meter = DC(instance=Instance(enabled=True, instance=1), address=1234, id=1)
        config.dc[0] = dc_meter
        # AC
        ac_line = AC(address=1234, instance=Instance(enabled=True, instance=1))
        ac_meter = ACMeter(line={1: ac_line})
        config.ac[0] = ac_meter
        # Circuit
        circuit = Circuit(
            name_utf8="testCircuitDevice",
            control_id=44,
            id=ValueU32(value=0, valid=True),
            dimmable=False,
            categories=[CategoryItem(name_utf8="testCategory", enabled=True, index=0)],
            circuit_loads=[CircuitLoad(channel_address=1234)],
        )
        config.circuit[0] = circuit
        # Existing components
        affected_components = []
        affected_components.append(
            ComponentReference(component_type=ComponentType.CIRCUIT, thing=circuit)
        )
        affected_components.append(
            ComponentReference(component_type=ComponentType.DCMETER, thing=dc_meter)
        )
        affected_components.append(
            ComponentReference(component_type=ComponentType.ACMETER, thing=ac_line)
        )
        alarm = Alarm(alarm_type=eAlarmType.TypeSleepWarning)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertEqual(len(res), 3)

    def test_process_device_alarm_inverter_charger(self):
        """
        Verifies that process_device_alarms correctly identifies and processes alarms related to inverter chargers.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 1234
        inverter_charger = InverterChargerDevice(
            model=1,
            type=1,
            inverter_instance=Instance(enabled=True, instance=111),
            inverter_ac_id=DataId(id=4, enabled=True),
            inverter_circuit_id=DataId(id=6, enabled=True),
            inverter_toggle_circuit_id=DataId(id=7, enabled=True),
            charger_instance=Instance(enabled=True, instance=1),
            charger_ac_id=DataId(id=5, enabled=True),
            charger_circuit_id=DataId(id=8, enabled=True),
            charger_toggle_circuit_id=DataId(id=9, enabled=True),
            battery_bank_1_id=DataId(id=10, enabled=True),
            battery_bank_2_id=DataId(id=11, enabled=True),
            battery_bank_3_id=DataId(id=12, enabled=True),
            position_column=1,
            position_row=1,
            clustered=True,
            primary=True,
            primary_phase=1,
            device_instance=1,
            dipswitch=4,
            channel_index=210,
        )

        config = N2kConfiguration()
        config.inverter_charger[0] = inverter_charger
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertTrue(
            any(c.component_type == ComponentType.INVERTERCHARGER for c in res)
        )
        self.assertEqual(res[0].thing.inverter_instance.instance, 111)

    def test_process_device_alarm_inverter_charger_alarms_no_ac(self):
        """
        Verifies that get_inverter_charger_alarm_title is called correctly when processing alarms for inverter chargers.
        Verifies that when get_inverter_charger_alarm_title does not return a title, the original alarm.title is preserved.
        """
        logger = logging.getLogger("test")
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_processors.get_inverter_charger_alarm_title",
            return_value=None,
        ) as mock_get_inverter_charger_alarm_title:
            resolved_alarm_channel_id = 1234
            inverter_charger = InverterChargerDevice(
                model=1,
                type=1,
                inverter_instance=Instance(enabled=True, instance=111),
                inverter_ac_id=DataId(id=4, enabled=True),
                inverter_circuit_id=DataId(id=6, enabled=True),
                inverter_toggle_circuit_id=DataId(id=7, enabled=True),
                charger_instance=Instance(enabled=True, instance=1),
                charger_ac_id=DataId(id=5, enabled=True),
                charger_circuit_id=DataId(id=8, enabled=True),
                charger_toggle_circuit_id=DataId(id=9, enabled=True),
                battery_bank_1_id=DataId(id=10, enabled=True),
                battery_bank_2_id=DataId(id=11, enabled=True),
                battery_bank_3_id=DataId(id=12, enabled=True),
                position_column=1,
                position_row=1,
                clustered=True,
                primary=True,
                primary_phase=1,
                device_instance=1,
                dipswitch=4,
                channel_index=210,
            )

            config = N2kConfiguration()
            config.inverter_charger[0] = inverter_charger
            affected_components = []
            alarm = Alarm(alarm_type=eAlarmType.External, title="Original Title")
            res = process_device_alarms(
                logger,
                resolved_alarm_channel_id,
                config,
                affected_components,
                alarm,
                None,
            )
            self.assertTrue(
                any(c.component_type == ComponentType.INVERTERCHARGER for c in res)
            )
            self.assertEqual(res[0].thing.inverter_instance.instance, 111)
            self.assertEqual(alarm.title, "Original Title")
            mock_get_inverter_charger_alarm_title.assert_called_once()

    def test_process_device_alarm_inverter_charger_ac(self):
        """
        Verifies that get_inverter_charger_alarm_title is called correctly when processing alarms for inverter chargers.
        Verifies that when get_inverter_charger_alarm_title returns a title, the alarm's title is overwritten with this new title.
        """
        logger = logging.getLogger("test")
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_processors.get_inverter_charger_alarm_title",
            return_value="New Alarm Title",
        ) as mock_get_inverter_charger_alarm_title:
            resolved_alarm_channel_id = 1234
            inverter_charger = InverterChargerDevice(
                model=1,
                type=1,
                inverter_instance=Instance(enabled=True, instance=111),
                inverter_ac_id=DataId(id=4, enabled=True),
                inverter_circuit_id=DataId(id=6, enabled=True),
                inverter_toggle_circuit_id=DataId(id=7, enabled=True),
                charger_instance=Instance(enabled=True, instance=1),
                charger_ac_id=DataId(id=5, enabled=True),
                charger_circuit_id=DataId(id=8, enabled=True),
                charger_toggle_circuit_id=DataId(id=9, enabled=True),
                battery_bank_1_id=DataId(id=10, enabled=True),
                battery_bank_2_id=DataId(id=11, enabled=True),
                battery_bank_3_id=DataId(id=12, enabled=True),
                position_column=1,
                position_row=1,
                clustered=True,
                primary=True,
                primary_phase=1,
                device_instance=1,
                dipswitch=4,
                channel_index=210,
            )

            config = N2kConfiguration()
            config.inverter_charger[0] = inverter_charger
            affected_components = []
            alarm = Alarm(alarm_type=eAlarmType.External, title="Original Title")
            res = process_device_alarms(
                logger,
                resolved_alarm_channel_id,
                config,
                affected_components,
                alarm,
                None,
            )
            self.assertTrue(
                any(c.component_type == ComponentType.INVERTERCHARGER for c in res)
            )
            self.assertEqual(res[0].thing.inverter_instance.instance, 111)
            self.assertEqual(alarm.title, "New Alarm Title")
            mock_get_inverter_charger_alarm_title.assert_called_once()

    def test_process_device_alarm_inverter_charger_no_match_dipswitch(self):
        """
        Verifies that when the dipswitch setting does not match, the alarm is not processed for the inverter charger.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 1234
        inverter_charger = InverterChargerDevice(
            model=1,
            type=1,
            inverter_instance=Instance(enabled=True, instance=111),
            inverter_ac_id=DataId(id=4, enabled=True),
            inverter_circuit_id=DataId(id=6, enabled=True),
            inverter_toggle_circuit_id=DataId(id=7, enabled=True),
            charger_instance=Instance(enabled=True, instance=1),
            charger_ac_id=DataId(id=5, enabled=True),
            charger_circuit_id=DataId(id=8, enabled=True),
            charger_toggle_circuit_id=DataId(id=9, enabled=True),
            battery_bank_1_id=DataId(id=10, enabled=True),
            battery_bank_2_id=DataId(id=11, enabled=True),
            battery_bank_3_id=DataId(id=12, enabled=True),
            position_column=1,
            position_row=1,
            clustered=True,
            primary=True,
            primary_phase=1,
            device_instance=1,
            dipswitch=4444,
            channel_index=210,
        )

        config = N2kConfiguration()
        config.inverter_charger[0] = inverter_charger
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertFalse(
            any(c.component_type == ComponentType.INVERTERCHARGER for c in res)
        )
        # Since no components should be affected, res should be empty
        self.assertEqual(len(res), 0)

    def test_process_device_alarm_inverter_charger_no_match_channel_id(self):
        """
        Verifies that when the channel ID does not match, the alarm is not processed for the inverter charger.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 1234
        inverter_charger = InverterChargerDevice(
            model=1,
            type=1,
            inverter_instance=Instance(enabled=True, instance=111),
            inverter_ac_id=DataId(id=4, enabled=True),
            inverter_circuit_id=DataId(id=6, enabled=True),
            inverter_toggle_circuit_id=DataId(id=7, enabled=True),
            charger_instance=Instance(enabled=True, instance=1),
            charger_ac_id=DataId(id=5, enabled=True),
            charger_circuit_id=DataId(id=8, enabled=True),
            charger_toggle_circuit_id=DataId(id=9, enabled=True),
            battery_bank_1_id=DataId(id=10, enabled=True),
            battery_bank_2_id=DataId(id=11, enabled=True),
            battery_bank_3_id=DataId(id=12, enabled=True),
            position_column=1,
            position_row=1,
            clustered=True,
            primary=True,
            primary_phase=1,
            device_instance=1,
            dipswitch=4,
            channel_index=2222,
        )

        config = N2kConfiguration()
        config.inverter_charger[0] = inverter_charger
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            None,
        )
        self.assertFalse(
            any(c.component_type == ComponentType.INVERTERCHARGER for c in res)
        )
        self.assertEqual(len(res), 0)

    def test_process_device_alarm_inverter_charger_duplicate(self):
        """
        Verifies that processing the same alarm for an inverter charger multiple times does not create duplicate entries.
        """
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_processors.get_inverter_charger_alarm_title",
            return_value="New Alarm Title",
        ) as mock_get_inverter_charger_alarm_title:
            logger = logging.getLogger("test")
            resolved_alarm_channel_id = 1234
            inverter_charger = InverterChargerDevice(
                model=1,
                type=1,
                inverter_instance=Instance(enabled=True, instance=111),
                inverter_ac_id=DataId(id=4, enabled=True),
                inverter_circuit_id=DataId(id=6, enabled=True),
                inverter_toggle_circuit_id=DataId(id=7, enabled=True),
                charger_instance=Instance(enabled=True, instance=1),
                charger_ac_id=DataId(id=5, enabled=True),
                charger_circuit_id=DataId(id=8, enabled=True),
                charger_toggle_circuit_id=DataId(id=9, enabled=True),
                battery_bank_1_id=DataId(id=10, enabled=True),
                battery_bank_2_id=DataId(id=11, enabled=True),
                battery_bank_3_id=DataId(id=12, enabled=True),
                position_column=1,
                position_row=1,
                clustered=True,
                primary=True,
                primary_phase=1,
                device_instance=1,
                dipswitch=4,
                channel_index=210,
            )

            config = N2kConfiguration()
            config.inverter_charger[0] = inverter_charger
            affected_components = []
            alarm = Alarm(alarm_type=eAlarmType.External)
            affected_components.append(
                ComponentReference(
                    component_type=ComponentType.INVERTERCHARGER, thing=inverter_charger
                )
            )
            res = process_device_alarms(
                logger,
                resolved_alarm_channel_id,
                config,
                affected_components,
                alarm,
                None,
            )

            mock_get_inverter_charger_alarm_title.assert_not_called()
            self.assertTrue(len(res) == 1)

    def test_process_device_alarm_inverter_charger_no_match_channel_id_recursive(self):
        """
        Verifies that processing an alarm with a channel ID that does not match any inverter charger,
        but is within 3 of a valid channel ID, will still create and map the affected component correctly,
        from the function calling itself recursively.
        """
        logger = logging.getLogger("test")
        resolved_alarm_channel_id = 1234
        inverter_charger = InverterChargerDevice(
            model=1,
            type=1,
            inverter_instance=Instance(enabled=True, instance=111),
            inverter_ac_id=DataId(id=4, enabled=True),
            inverter_circuit_id=DataId(id=6, enabled=True),
            inverter_toggle_circuit_id=DataId(id=7, enabled=True),
            charger_instance=Instance(enabled=True, instance=1),
            charger_ac_id=DataId(id=5, enabled=True),
            charger_circuit_id=DataId(id=8, enabled=True),
            charger_toggle_circuit_id=DataId(id=9, enabled=True),
            battery_bank_1_id=DataId(id=10, enabled=True),
            battery_bank_2_id=DataId(id=11, enabled=True),
            battery_bank_3_id=DataId(id=12, enabled=True),
            position_column=1,
            position_row=1,
            clustered=True,
            primary=True,
            primary_phase=1,
            device_instance=1,
            dipswitch=4,
            channel_index=213,
        )

        config = N2kConfiguration()
        config.inverter_charger[0] = inverter_charger
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External)
        res = process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            True,
        )
        self.assertTrue(
            any(c.component_type == ComponentType.INVERTERCHARGER for c in res)
        )
        self.assertEqual(res[0].thing.inverter_instance.instance, 111)

    def test_process_device_alarms_battery(self):
        """
        Verifies that processing an alarm for a battery device correctly identifies and maps the affected component.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        relationship = UiRelationShipMsg(
            primary_type=ItemType.DcMeter,
            secondary_type=ItemType.DcMeter,
            primary_id=2345,
            secondary_id=1,
            relationship_type=RelationshipType.Normal,
            primary_config_address=1,
            secondary_config_address=1234,
            primary_channel_index=1,
            secondary_channel_index=1,
        )
        alarm = Alarm(alarm_type=eAlarmType.External)

        dc = DC(instance=Instance(enabled=True, instance=1), address=1234, id=2345)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        config.dc[0] = dc
        config.ui_relationships.append(relationship)
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 2345)

    def test_process_device_alarms_battery_no_match_dipswitch(self):
        """
        Verifies that processing an alarm for a battery device with a non-matching dipswitch does not identify any affected components.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4444,
        )

        alarm = Alarm(alarm_type=eAlarmType.External)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertEqual(len(res), 0)

    def test_process_device_alarms_battery_no_match_device_type(self):
        """
        Verifies that processing an alarm for a battery device with a non-matching device type does not identify any affected components.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.ControlX,  # Intentionally incorrect device type
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        alarm = Alarm(alarm_type=eAlarmType.External)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertEqual(len(res), 0)

    def test_process_device_alarms_battery_no_match_relationship_primary_type(self):
        """
        Verifies that processing an alarm for a battery device with a non-matching primary relationship type does not identify any affected components.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        relationship = UiRelationShipMsg(
            primary_type=ItemType.AcMeter,
            secondary_type=ItemType.DcMeter,
            primary_id=2345,
            secondary_id=1,
            relationship_type=RelationshipType.Normal,
            primary_config_address=1,
            secondary_config_address=1234,
            primary_channel_index=1,
            secondary_channel_index=1,
        )

        alarm = Alarm(alarm_type=eAlarmType.External)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        config.ui_relationships.append(relationship)
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertEqual(len(res), 0)

    def test_process_device_alarms_battery_no_match_relationship_secondary_type(self):
        """
        Verifies that processing an alarm for a battery device with a non-matching secondary relationship type does not identify any affected components.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        relationship = UiRelationShipMsg(
            primary_type=ItemType.DcMeter,
            secondary_type=ItemType.AcMeter,
            primary_id=2345,
            secondary_id=1,
            relationship_type=RelationshipType.Normal,
            primary_config_address=1,
            secondary_config_address=1234,
            primary_channel_index=1,
            secondary_channel_index=1,
        )

        alarm = Alarm(alarm_type=eAlarmType.External)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        config.ui_relationships.append(relationship)
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertEqual(len(res), 0)

    def test_process_device_alarms_battery_no_match_relationship_dipswitch(self):
        """
        Verifies that processing an alarm for a battery device with a non-matching dipswitch setting in the UI relationship does not identify any affected components.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        relationship = UiRelationShipMsg(
            primary_type=ItemType.DcMeter,
            secondary_type=ItemType.DcMeter,
            primary_id=2345,
            secondary_id=1,
            relationship_type=RelationshipType.Normal,
            primary_config_address=1,
            secondary_config_address=4444,
            primary_channel_index=1,
            secondary_channel_index=1,
        )

        alarm = Alarm(alarm_type=eAlarmType.External)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        config.ui_relationships.append(relationship)
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertEqual(len(res), 0)

    def test_process_device_alarms_battery_no_match_relationship_type(self):
        """
        Verifies that processing an alarm for a battery device with a non-matching dipswitch setting in the UI relationship does not identify any affected components.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        relationship = UiRelationShipMsg(
            primary_type=ItemType.DcMeter,
            secondary_type=ItemType.DcMeter,
            primary_id=2345,
            secondary_id=1,
            relationship_type=RelationshipType.Duplicates,
            primary_config_address=1,
            secondary_config_address=4444,
            primary_channel_index=1,
            secondary_channel_index=1,
        )

        alarm = Alarm(alarm_type=eAlarmType.External)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        config.ui_relationships.append(relationship)
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertEqual(len(res), 0)

    def test_process_device_alarms_battery_no_match_dc_instance(self):
        """
        Verifies that processing an alarm for a battery device with a non-matching DC instance in the UI relationship does not identify any affected components.
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        relationship = UiRelationShipMsg(
            primary_type=ItemType.DcMeter,
            secondary_type=ItemType.DcMeter,
            primary_id=2345,
            secondary_id=1,
            relationship_type=RelationshipType.Normal,
            primary_config_address=1,
            secondary_config_address=4444,
            primary_channel_index=1,
            secondary_channel_index=2,  # Non-matching DC instance
        )

        alarm = Alarm(alarm_type=eAlarmType.External)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        config.ui_relationships.append(relationship)
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )

        self.assertEqual(len(res), 0)

    def test_process_device_alarms_battery_dc_match_skipped(self):
        """
        Verifies that processing an alarm for a battery device, where the battery device is already a member of affected components, it will not be added again
        """
        logger = logging.getLogger("test")
        device = Device(
            name_utf8="BatteryDevice",
            source_address=0,
            conflict=False,
            device_type=DeviceType.Battery,
            valid=True,
            transient=True,
            version="test",
            dipswitch=4,
        )

        relationship = UiRelationShipMsg(
            primary_type=ItemType.DcMeter,
            secondary_type=ItemType.DcMeter,
            primary_id=2345,
            secondary_id=1,
            relationship_type=RelationshipType.Normal,
            primary_config_address=1,
            secondary_config_address=1234,
            primary_channel_index=1,
            secondary_channel_index=1,
        )
        alarm = Alarm(alarm_type=eAlarmType.External)

        dc = DC(instance=Instance(enabled=True, instance=1), address=1234, id=2345)
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        config.device[0] = device
        config.dc[0] = dc
        config.ui_relationships.append(relationship)
        affected_components = []

        res = process_device_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        res = process_device_alarms(logger, resolved_alarm_id, config, res, alarm, True)

        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 2345)
        self.assertEqual(len(res), 1)

    def test_process_dc_meter_alarms_high_voltage(self):
        """
        Test processing of DC meter alarms with high voltage condition.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        dc = DC(high_voltage=AlarmLimit(enabled=True, id=1), id=1234)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_dc_meter_alarms_low_voltage(self):
        """
        Test processing of DC meter alarms with low voltage condition.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=2)

        dc = DC(low_voltage=AlarmLimit(enabled=True, id=2), id=1234)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_dc_meter_alarms_very_low_voltage(self):
        """
        Test processing of DC meter alarms with very low voltage condition.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=3)

        dc = DC(very_low_limit=AlarmLimit(enabled=True, id=3), id=1234)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_dc_meter_alarms_high_limit(self):
        """
        Test processing of DC meter alarms with high limit condition.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=4)

        dc = DC(very_high_limit=AlarmLimit(enabled=True, id=4), id=1234)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_dc_meter_alarms_very_high_limit(self):
        """
        Test processing of DC meter alarms with very high limit condition.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=5)

        dc = DC(very_high_limit=AlarmLimit(enabled=True, id=5), id=12345)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 12345)

    def test_process_dc_meter_alarms_low_limit(self):
        """
        Test processing of DC meter alarms with low limit condition.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=6)

        dc = DC(low_limit=AlarmLimit(enabled=True, id=6), id=1234)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_dc_meter_alarms_very_low_limit(self):
        """
        Test processing of DC meter alarms with low limit condition.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 1234
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=6)

        dc = DC(very_low_limit=AlarmLimit(enabled=True, id=6), id=1234)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_dc_meter_alarms_address(self):
        """
        Test processing of DC meter alarms with address condition. Address matches the resolved alarm ID.
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 2222
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=6)

        dc = DC(very_low_limit=AlarmLimit(enabled=True, id=6), id=1234, address=222)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertTrue(any(c.component_type == ComponentType.DCMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_dc_meter_alarms_no_match(self):
        """
        Test processing of DC meter alarms where no DC meter matches the alarm criteria.
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999  # An ID that does not match any DC meter
        config = N2kConfiguration()
        affected_components = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=7)

        dc = DC(very_low_limit=AlarmLimit(enabled=True, id=11111), id=1234, address=222)
        config.dc[0] = dc
        res = process_dc_meter_alarms(
            logger, resolved_alarm_id, config, affected_components, alarm, True
        )
        self.assertFalse(any(c.component_type == ComponentType.DCMETER for c in res))

    def test_process_ac_meter_alarms_high_limit(self):
        """
        Test processing of AC meter alarm matches ac config for high limit alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        ac = ACMeter(line={0: AC(high_limit=AlarmLimit(enabled=True, id=1), id=1234)})
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.ACMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_ac_meter_alarms_low_limit(self):
        """
        Test processing of AC meter alarm matches ac config for low limit alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        ac = ACMeter(line={0: AC(low_limit=AlarmLimit(enabled=True, id=1), id=1234)})
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.ACMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_ac_meter_alarms_very_high_limit(self):
        """
        Test processing of AC meter alarm matches ac config for very high limit alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        ac = ACMeter(
            line={0: AC(very_high_limit=AlarmLimit(enabled=True, id=1), id=1234)}
        )
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.ACMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_ac_meter_alarms_high_voltage(self):
        """
        Test processing of AC meter alarm matches ac config for high voltage alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        ac = ACMeter(line={0: AC(high_voltage=AlarmLimit(enabled=True, id=1), id=1234)})
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.ACMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_ac_meter_alarms_frequency(self):
        """
        Test processing of AC meter alarm matches ac config for frequency alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        ac = ACMeter(line={0: AC(frequency=AlarmLimit(enabled=True, id=1), id=1234)})
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.ACMETER for c in res))
        self.assertEqual(res[0].thing.id, 1234)

    def test_process_ac_meter_alarms_no_match(self):
        """
        Test processing of AC meter alarm does not match any AC meter config
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=9999)

        ac = ACMeter(line={0: AC(id=1234, address=222)})
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertFalse(any(c.component_type == ComponentType.ACMETER for c in res))

    def test_process_ac_meter_alarms_no_match(self):
        """
        Test processing of AC meter alarm does not match any AC meter config
        """
        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=9999)

        ac = ACMeter(line={0: AC(id=1234, address=222)})
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertFalse(any(c.component_type == ComponentType.ACMETER for c in res))

    def test_process_ac_alarms_address_match(self):
        """
        Test processing of AC alarm matches AC config for the resolved id
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 222
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=9999)

        ac = ACMeter(line={0: AC(id=1234, address=222)})
        config.ac[0] = ac
        res = process_ac_meter_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.ACMETER for c in res))

    def test_process_tank_alarms_very_low_limit(self):
        """
        Test processing of tank alarm matches tank config for low limit alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        tank = Tank(
            very_low_limit=AlarmLimit(enabled=True, id=1),
            instance=Instance(enabled=True, instance=1234),
        )

        config.tank[0] = tank
        res = process_tank_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.TANK for c in res))
        self.assertEqual(res[0].thing.instance.instance, 1234)

    def test_process_tank_alarms_low_limit(self):
        """
        Test processing of tank alarm matches tank config for low limit alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        tank = Tank(
            low_limit=AlarmLimit(enabled=True, id=1),
            instance=Instance(enabled=True, instance=1234),
        )

        config.tank[0] = tank
        res = process_tank_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.TANK for c in res))
        self.assertEqual(res[0].thing.instance.instance, 1234)

    def test_process_tank_alarms_high_limit(self):
        """
        Test processing of tank alarm matches tank config for high limit alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        tank = Tank(
            high_limit=AlarmLimit(enabled=True, id=1),
            instance=Instance(enabled=True, instance=1234),
        )

        config.tank[0] = tank
        res = process_tank_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.TANK for c in res))
        self.assertEqual(res[0].thing.instance.instance, 1234)

    def test_process_tank_alarms_very_high_limit(self):
        """
        Test processing of tank alarm matches tank config for very high limit alarm
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        tank = Tank(
            very_high_limit=AlarmLimit(enabled=True, id=1),
            instance=Instance(enabled=True, instance=1234),
        )

        config.tank[0] = tank
        res = process_tank_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.TANK for c in res))
        self.assertEqual(res[0].thing.instance.instance, 1234)

    def test_process_tank_alarms_resolved_alarm_id_match(self):
        """
        Test processing of tank alarm matches tank config for resolved alarm ID match
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=9999)

        tank = Tank(
            address=9999,
            instance=Instance(enabled=True, instance=1234),
        )

        config.tank[0] = tank
        res = process_tank_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.TANK for c in res))
        self.assertEqual(res[0].thing.instance.instance, 1234)

    def test_process_tank_alarms_no_match(self):
        """
        Test processing of tank alarm does not match any tank config, not added to affected components
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=9999)

        tank = Tank(
            address=8888,
            instance=Instance(enabled=True, instance=1234),
        )

        config.tank[0] = tank
        res = process_tank_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertFalse(any(c.component_type == ComponentType.TANK for c in res))

    def test_process_circuit_load_alarms_match(self):
        """
        Test processing of circuit load alarm matches circuit load config
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        circuit_load = Circuit(
            circuit_loads=[CircuitLoad(level=1, channel_address=9999)], control_id=123
        )

        config.circuit[0] = circuit_load
        res = process_circuit_load_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertTrue(any(c.component_type == ComponentType.CIRCUIT for c in res))
        self.assertEqual(res[0].thing.control_id, 123)

    def test_process_circuit_load_alarms_no_match(self):
        """
        Test processing of circuit load alarm does not match any circuit load config
        """

        logger = logging.getLogger("test")
        resolved_alarm_id = 9999
        config = N2kConfiguration()
        affected_component = []
        alarm = Alarm(alarm_type=eAlarmType.External, unique_id=1)

        circuit_load = Circuit(
            circuit_loads=[CircuitLoad(level=1, channel_address=8888)], control_id=123
        )

        config.circuit[0] = circuit_load
        res = process_circuit_load_alarms(
            logger,
            resolved_alarm_id,
            config,
            affected_component,
            alarm,
            False,
        )
        self.assertFalse(any(c.component_type == ComponentType.CIRCUIT for c in res))

    def test_process_bls_alarms_ac(self):
        """
        Test case for process_bls_alarm
        bls associated ACMeter are added
        to component_reference
        """

        logger = logging.getLogger("test")
        config = N2kConfiguration()
        config.ui_relationships.append(
            UiRelationShipMsg(
                secondary_config_address=1234,
                secondary_type=ItemType.BinaryLogicState,
                relationship_type=RelationshipType.Normal,
                primary_type=ItemType.AcMeter,
                primary_id=567,
            )
        )

        resolved_alarm_id = None
        config.ac[0] = ACMeter(line={1: AC(id=567)})

        affected_components = []
        bls_alarms = BLSAlarmMapping(
            alarm_channel=1, bls=BinaryLogicState(address=1234)
        )
        config.bls_alarm_mappings[0] = bls_alarms

        alarm = Alarm(alarm_type=eAlarmType.External, channel_id=1)

        res = process_bls_alarms(
            logger,
            config,
            affected_components,
            alarm,
            resolved_alarm_id,
            False,
        )

        self.assertEqual(res[0].component_type, ComponentType.BINARYLOGICSTATE)
        self.assertEqual(res[1].component_type, ComponentType.ACMETER)
        self.assertEqual(res[1].thing.id, 567)

    def test_process_bls_alarms_dc(self):
        """
        Test case for process_bls_alarm
        bls associated DCMeter are added
        to component_reference
        """

        logger = logging.getLogger("test")
        config = N2kConfiguration()
        config.ui_relationships.append(
            UiRelationShipMsg(
                secondary_config_address=1234,
                secondary_type=ItemType.BinaryLogicState,
                relationship_type=RelationshipType.Normal,
                primary_type=ItemType.DcMeter,
                primary_id=567,
            )
        )

        resolved_alarm_id = None
        config.dc[0] = DC(id=567)

        affected_components = []
        bls_alarms = BLSAlarmMapping(
            alarm_channel=1, bls=BinaryLogicState(address=1234)
        )
        config.bls_alarm_mappings[0] = bls_alarms

        alarm = Alarm(alarm_type=eAlarmType.External, channel_id=1)

        res = process_bls_alarms(
            logger,
            config,
            affected_components,
            alarm,
            resolved_alarm_id,
            False,
        )

        self.assertEqual(res[0].component_type, ComponentType.BINARYLOGICSTATE)
        self.assertEqual(res[1].component_type, ComponentType.DCMETER)
        self.assertEqual(res[1].thing.id, 567)

    def test_process_bls_alarms_fluid(self):
        """
        Test case for process_bls_alarm
        bls associated Tank are added
        to component_reference
        """

        logger = logging.getLogger("test")
        config = N2kConfiguration()
        config.ui_relationships.append(
            UiRelationShipMsg(
                secondary_config_address=1234,
                secondary_type=ItemType.BinaryLogicState,
                relationship_type=RelationshipType.Normal,
                primary_type=ItemType.FluidLevel,
                primary_id=567,
            )
        )

        resolved_alarm_id = None
        config.tank[0] = Tank(id=567)

        affected_components = []
        bls_alarms = BLSAlarmMapping(
            alarm_channel=1, bls=BinaryLogicState(address=1234)
        )
        config.bls_alarm_mappings[0] = bls_alarms

        alarm = Alarm(alarm_type=eAlarmType.External, channel_id=1)

        res = process_bls_alarms(
            logger,
            config,
            affected_components,
            alarm,
            resolved_alarm_id,
            False,
        )

        self.assertEqual(res[0].component_type, ComponentType.BINARYLOGICSTATE)
        self.assertEqual(res[1].component_type, ComponentType.TANK)
        self.assertEqual(res[1].thing.id, 567)

    def test_process_bls_alarms_circuit(self):
        """
        Test case for process_bls_alarm
        bls associated Circuit are added
        to component_reference
        """

        logger = logging.getLogger("test")
        config = N2kConfiguration()
        config.ui_relationships.append(
            UiRelationShipMsg(
                secondary_config_address=1234,
                secondary_type=ItemType.BinaryLogicState,
                relationship_type=RelationshipType.Normal,
                primary_type=ItemType.Circuit,
                primary_config_address=567,
            )
        )

        resolved_alarm_id = None
        config.circuit[0] = Circuit(control_id=567)

        affected_components = []
        bls_alarms = BLSAlarmMapping(
            alarm_channel=1, bls=BinaryLogicState(address=1234)
        )
        config.bls_alarm_mappings[0] = bls_alarms

        alarm = Alarm(alarm_type=eAlarmType.External, channel_id=1)

        res = process_bls_alarms(
            logger,
            config,
            affected_components,
            alarm,
            resolved_alarm_id,
            False,
        )

        self.assertEqual(res[0].component_type, ComponentType.BINARYLOGICSTATE)
        self.assertEqual(res[1].component_type, ComponentType.CIRCUIT)
        self.assertEqual(res[1].thing.control_id, 567)

    def test_process_bls_alarms_single_bls(self):
        """
        Test case for process_bls_alarm
        bls associated with nothing
        """

        logger = logging.getLogger("test")
        config = N2kConfiguration()
        config.ui_relationships.append(
            UiRelationShipMsg(
                secondary_config_address=1234,
                secondary_type=ItemType.BinaryLogicState,
                relationship_type=RelationshipType.Normal,
                primary_type=ItemType.FluidLevel,
                primary_config_address=11111,
            )
        )

        resolved_alarm_id = None
        affected_components = []
        bls_alarms = BLSAlarmMapping(
            alarm_channel=1, bls=BinaryLogicState(address=1234)
        )
        config.bls_alarm_mappings[0] = bls_alarms

        alarm = Alarm(alarm_type=eAlarmType.External, channel_id=1)

        res = process_bls_alarms(
            logger,
            config,
            affected_components,
            alarm,
            resolved_alarm_id,
            False,
        )

        self.assertEqual(res[0].component_type, ComponentType.BINARYLOGICSTATE)
        self.assertEqual(len(res), 1)

    def test_process_bls_alarms_nothing(self):
        """
        Test case for process_bls_alarm
        no bls
        """

        logger = logging.getLogger("test")
        config = N2kConfiguration()

        affected_components = []

        alarm = Alarm(alarm_type=eAlarmType.External, channel_id=1)
        resolved_alarm_id = None
        res = process_bls_alarms(
            logger,
            config,
            affected_components,
            alarm,
            resolved_alarm_id,
            False,
        )

        self.assertEqual(len(res), 0)

    def test_process_smartcraft_alarms(self):
        """
        Test case for process_smartcraft_alarms
        Engine match adds engine alarm to affected_components
        """

        resolved_alarm_channel_id = 0

        config = EngineConfiguration()
        config.devices[0] = EngineDevice(
            Instance(enabled=True, instance=0), name_utf8=Constants.starboardEngine
        )

        affected_components = []

        res = process_smartcraft_alarms(
            None,
            resolved_alarm_channel_id,
            config,
            affected_components,
            None,
            False,
        )

        self.assertEqual(res[0].component_type, ComponentType.MARINE_ENGINE)
        self.assertEqual(res[0].thing.instance.instance, 0)

    def test_process_smartcraft_alarms_None(self):
        """
        Test case for process_smartcraft_alarms
        Engine does not match adds engine alarm to affected_components
        """

        resolved_alarm_channel_id = 45

        config = EngineConfiguration()
        config.devices[0] = EngineDevice(
            Instance(enabled=True, instance=47), name_utf8=Constants.starboardEngine
        )

        affected_components = []

        res = process_smartcraft_alarms(
            None,
            resolved_alarm_channel_id,
            config,
            affected_components,
            None,
            False,
        )

        self.assertEqual(len(res), 0)

    def test_map_sc_engine_instance_to_engine_name_starboard(self):
        """
        Instance found in mapping. Starboard Engine
        """

        instance = 0
        engine_name = map_sc_engine_instance_to_engine_name(instance)
        self.assertEqual(engine_name, Constants.starboardEngine)

    def test_map_sc_engine_instance_to_engine_name_port(self):
        """
        Instance found in mapping. Port Engine
        """

        instance = 1
        engine_name = map_sc_engine_instance_to_engine_name(instance)
        self.assertEqual(engine_name, Constants.portEngine)

    def test_map_sc_engine_instance_to_engine_name_starboard_inner(self):
        """
        Instance found in mapping. Starboard Inner Engine
        """

        instance = 2
        engine_name = map_sc_engine_instance_to_engine_name(instance)
        self.assertEqual(engine_name, Constants.starboardInnerEngine)

    def test_map_sc_engine_instance_to_engine_name_port_inner(self):
        """
        Instance found in mapping. Port Inner Engine
        """

        instance = 3
        engine_name = map_sc_engine_instance_to_engine_name(instance)
        self.assertEqual(engine_name, Constants.portInnerEngine)

    def test_map_sc_engine_instance_to_engine_name_one(self):
        """
        Instance found not found in mapping, returns None
        """

        instance = 11
        engine_name = map_sc_engine_instance_to_engine_name(instance)
        self.assertIsNone(engine_name)
