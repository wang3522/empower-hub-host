import unittest
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.charger import (
    map_charger_state,
    CombiCharger,
    ACMeterCharger,
)
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    SwitchType,
    Unit,
)
from N2KClient.n2kclient.models.alarm_setting import (
    AlarmSettingLimit,
    AlarmSettingFactory,
)


class TestInverter(unittest.TestCase):
    def test_map_charger_state(self):
        self.assertEqual(map_charger_state("Absorption"), "absorption")
        self.assertEqual(map_charger_state("Bulk"), "bulk")
        self.assertEqual(map_charger_state("ConstantVI"), "constantVI")
        self.assertEqual(map_charger_state("NotCharging"), "notCharging")
        self.assertEqual(map_charger_state("Equalize"), "equalize")
        self.assertEqual(map_charger_state("Overcharge"), "overcharge")
        self.assertEqual(map_charger_state("Float"), "float")
        self.assertEqual(map_charger_state("NoFloat"), "noFloat")
        self.assertEqual(map_charger_state("Fault"), "fault")
        self.assertEqual(map_charger_state("Disabled"), "disabled")

    def test_combi_charger_init(self):
        inverter_charger = MagicMock()
        dc1 = MagicMock()
        dc2 = MagicMock()
        dc3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        instance = 1
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        with patch.object(
            CombiCharger, "define_dc_lines"
        ) as mock_define_dc_lines, patch.object(
            CombiCharger, "define_combi_channels"
        ) as mock_define_combi_channels, patch.object(
            CombiCharger, "define_charger_component_status_channel"
        ) as mock_define_charger_component_status_channel:

            charger = CombiCharger(
                inverter_charger=inverter_charger,
                dc1=dc1,
                dc2=dc2,
                dc3=dc3,
                categories=categories,
                instance=instance,
                n2k_devices=n2k_devices,
                charger_circuit=charger_circuit,
            )

            self.assertEqual(charger.charger_circuit, 11)
            self.assertEqual(charger.charger_circuit_control_id, 12)
            self.assertEqual(charger.instance, 1)
            mock_define_charger_component_status_channel.assert_called_once()
            mock_define_dc_lines.assert_called_once()
            mock_define_combi_channels.assert_called_once()

    def test_define_dc_lines(self):
        inverter_charger = MagicMock()
        dc1 = MagicMock(name_utf8="Battery 1")
        dc2 = MagicMock(name_utf8="Battery 2")
        dc3 = MagicMock(name_utf8="Battery 3")
        categories = ["TEST_CATEGORY"]
        instance = 1
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        with patch.object(
            CombiCharger, "define_dc_line_channels"
        ) as mock_define_dc_line_channels:
            charger = CombiCharger(
                inverter_charger=inverter_charger,
                dc1=dc1,
                dc2=dc2,
                dc3=dc3,
                categories=categories,
                instance=instance,
                n2k_devices=n2k_devices,
                charger_circuit=charger_circuit,
            )

            mock_define_dc_line_channels.reset_mock()
            charger.define_dc_lines(dc1, dc2, dc3, n2k_devices)

            self.assertEqual(
                charger.metadata["empower:charger.battery1.name"], "Battery 1"
            )
            self.assertEqual(
                charger.metadata["empower:charger.battery2.name"], "Battery 2"
            )
            self.assertEqual(
                charger.metadata["empower:charger.battery3.name"], "Battery 3"
            )

            mock_define_dc_line_channels.assert_any_call(1, n2k_devices, dc1)
            mock_define_dc_line_channels.assert_any_call(2, n2k_devices, dc2)
            mock_define_dc_line_channels.assert_any_call(3, n2k_devices, dc3)

    def test_define_dc_line_channels(self):
        inverter_charger = MagicMock()
        dc1 = MagicMock(name_utf8="Battery 1", id=5, instance=MagicMock(instance=1))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            setattr(dc1, limit.value, mock_limit)
        categories = ["TEST_CATEGORY"]
        instance = 1
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        with patch.object(
            CombiCharger, "define_dc_line_channels"
        ) as mock_define_dc_line_channels:
            charger = CombiCharger(
                inverter_charger=inverter_charger,
                dc1=dc1,
                dc2=None,
                dc3=None,
                categories=categories,
                instance=instance,
                n2k_devices=n2k_devices,
                charger_circuit=charger_circuit,
            )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            CombiCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            charger.define_dc_line_channels(1, n2k_devices, dc1)
            mock_channel.assert_any_call(
                id="dc1cs",
                name="Battery 1 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:charger.battery1.componentStatus"],
            )

            mock_channel.assert_any_call(
                id="dc1v",
                name="Battery 1 Voltage",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:charger.battery1.voltage"],
            )

            mock_channel.assert_any_call(
                id="dc1c",
                name="Battery 1 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=False,
                tags=["empower:charger.battery1.current"],
            )
            self.assertEqual(mock_define_channel.call_count, 3)
            n2k_devices.get_channel_subject.assert_any_call(
                "DC.1", "ComponentStatus", N2kDeviceType.DC
            )
            n2k_devices.get_channel_subject.assert_any_call(
                "DC.1", "Voltage", N2kDeviceType.DC
            )
            n2k_devices.get_channel_subject.assert_any_call(
                "DC.1", "Current", N2kDeviceType.DC
            )
            self.assertEqual(n2k_devices.set_subscription.call_count, 3)
            self.assertEqual(n2k_devices.get_channel_subject.call_count, 3)
            mock_define_channel.assert_called()

    def test_define_dc_line_channels_alarm(self):
        inverter_charger = MagicMock()
        dc1 = MagicMock(name_utf8="Battery 1", id=5, instance=MagicMock(instance=1))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(dc1, limit.value, mock_limit)
        categories = ["TEST_CATEGORY"]
        instance = 1
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        with patch.object(
            CombiCharger, "define_dc_line_channels"
        ) as mock_define_dc_line_channels:
            charger = CombiCharger(
                inverter_charger=inverter_charger,
                dc1=dc1,
                dc2=None,
                dc3=None,
                categories=categories,
                instance=instance,
                n2k_devices=n2k_devices,
                charger_circuit=charger_circuit,
            )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()
        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            CombiCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel, patch.object(
            AlarmSettingFactory, "get_alarm_setting", return_value=MagicMock()
        ) as mock_get_alarm_setting:
            charger.define_dc_line_channels(1, n2k_devices, dc1)
            # There should be 2 calls per limit (on/off)
            expected_calls = len(AlarmSettingLimit) * 2
            self.assertEqual(mock_get_alarm_setting.call_count, expected_calls)
            # Check that alarm_settings was extended
            self.assertEqual(len(charger.alarm_settings), expected_calls)

    def test_define_combi_channels(self):
        inverter_charger = MagicMock()
        dc1 = MagicMock(name_utf8="Battery 1", id=5, instance=MagicMock(instance=1))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(dc1, limit.value, mock_limit)
        categories = ["TEST_CATEGORY"]
        instance = 1
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        with patch.object(
            CombiCharger, "define_dc_line_channels"
        ) as mock_define_dc_line_channels:
            charger = CombiCharger(
                inverter_charger=inverter_charger,
                dc1=dc1,
                dc2=None,
                dc3=None,
                categories=categories,
                instance=instance,
                n2k_devices=n2k_devices,
                charger_circuit=charger_circuit,
            )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()
        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            CombiCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            charger.define_combi_channels(charger_circuit, n2k_devices)
            mock_channel.assert_any_call(
                id="ce",
                name="Charger Enabled",
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:charger.enabled"],
            )

            mock_channel.assert_any_call(
                id="cst",
                name="Charger Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:charger.status"],
            )

            self.assertEqual(mock_define_channel.call_count, 2)
            n2k_devices.get_channel_subject.assert_any_call(
                charger.n2k_device_id, "ChargerState", N2kDeviceType.INVERTERCHARGER
            )
            n2k_devices.get_channel_subject.assert_any_call(
                charger.n2k_device_id, "ChargerEnable", N2kDeviceType.INVERTERCHARGER
            )

    def test_define_combi_channels_read_only_false(self):
        inverter_charger = MagicMock()
        dc1 = MagicMock(name_utf8="Battery 1", id=5, instance=MagicMock(instance=1))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(dc1, limit.value, mock_limit)
        categories = ["TEST_CATEGORY"]
        instance = 1
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.switch_type = 0
        with patch.object(
            CombiCharger, "define_dc_line_channels"
        ) as mock_define_dc_line_channels:
            charger = CombiCharger(
                inverter_charger=inverter_charger,
                dc1=dc1,
                dc2=None,
                dc3=None,
                categories=categories,
                instance=instance,
                n2k_devices=n2k_devices,
                charger_circuit=charger_circuit,
            )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()
        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            CombiCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            charger.define_combi_channels(charger_circuit, n2k_devices)
            mock_channel.assert_any_call(
                id="ce",
                name="Charger Enabled",
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:charger.enabled"],
            )

            mock_channel.assert_any_call(
                id="cst",
                name="Charger Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:charger.status"],
            )

            self.assertEqual(mock_define_channel.call_count, 2)
            n2k_devices.get_channel_subject.assert_any_call(
                charger.n2k_device_id, "ChargerState", N2kDeviceType.INVERTERCHARGER
            )
            n2k_devices.get_channel_subject.assert_any_call(
                charger.n2k_device_id, "ChargerEnable", N2kDeviceType.INVERTERCHARGER
            )
            self.assertEqual(n2k_devices.set_subscription.call_count, 2)

    def test_define_charger_component_status_channel(self):
        inverter_charger = MagicMock()
        dc1 = MagicMock(name_utf8="Battery 1", id=5, instance=MagicMock(instance=1))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(dc1, limit.value, mock_limit)
        categories = ["TEST_CATEGORY"]
        instance = 1
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        with patch.object(
            CombiCharger, "define_dc_line_channels"
        ) as mock_define_dc_line_channels:
            charger = CombiCharger(
                inverter_charger=inverter_charger,
                dc1=dc1,
                dc2=None,
                dc3=None,
                categories=categories,
                instance=instance,
                n2k_devices=n2k_devices,
                charger_circuit=charger_circuit,
            )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()
        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            CombiCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            charger.define_charger_component_status_channel(n2k_devices)
            mock_channel.assert_any_call(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:charger.componentStatus"],
            )

            self.assertEqual(mock_define_channel.call_count, 1)
            n2k_devices.get_channel_subject.assert_any_call(
                charger.n2k_device_id, "ComponentStatus", N2kDeviceType.INVERTERCHARGER
            )

    def test_init_ac_meter_charger(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        with patch.object(
            ACMeterCharger, "define_ac_meter_charger_channels"
        ) as mock_define_ac_meter_charger_channels:

            charger = ACMeterCharger(
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                categories=categories,
                n2k_devices=n2k_devices,
                circuit=charger_circuit,
            )

            mock_define_ac_meter_charger_channels.assert_called_once()

    def test_calc_charger_state(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        with patch.object(
            ACMeterCharger, "define_ac_meter_charger_channels"
        ) as mock_define_ac_meter_charger_channels, patch(
            "N2KClient.n2kclient.models.empower_system.inverter.StateUtil.any_true",
            return_value=True,
        ) as mock_any_connected:

            charger = ACMeterCharger(
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                categories=categories,
                n2k_devices=n2k_devices,
                circuit=charger_circuit,
            )
            self.assertEqual(charger._calc_charger_state(), "charging")

    def test_calc_charger_state_disabled(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        with patch.object(
            ACMeterCharger, "define_ac_meter_charger_channels"
        ) as mock_define_ac_meter_charger_channels, patch(
            "N2KClient.n2kclient.models.empower_system.inverter.StateUtil.any_true",
            return_value=False,
        ) as mock_any_connected:

            charger = ACMeterCharger(
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                categories=categories,
                n2k_devices=n2k_devices,
                circuit=charger_circuit,
            )
            self.assertEqual(charger._calc_charger_state(), "disabled")

    def test_charger_init(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        with patch.object(
            ACMeterCharger, "define_ac_meter_charger_channels"
        ) as mock_define_ac_meter_charger_channels:

            charger = ACMeterCharger(
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                categories=categories,
                n2k_devices=n2k_devices,
                circuit=charger_circuit,
            )
            mock_define_ac_meter_charger_channels.assert_called_once()

    def test_define_ac_meter_charger_channel(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        with patch.object(
            ACMeterCharger, "define_ac_meter_charger_status_channel"
        ) as mock_define_ac_meter_charger_status_channel, patch.object(
            ACMeterCharger, "define_ac_meter_charger_circuit_enable_channel"
        ) as mock_define_ac_meter_charger_circuit_enable_channel:
            charger = ACMeterCharger(
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                categories=categories,
                n2k_devices=n2k_devices,
                circuit=charger_circuit,
            )
            mock_define_ac_meter_charger_status_channel.reset_mock()
            mock_define_ac_meter_charger_circuit_enable_channel.reset_mock()
            charger.define_ac_meter_charger_channels(
                ac_line1, ac_line2, ac_line3, n2k_devices, charger_circuit
            )
            mock_define_ac_meter_charger_status_channel.assert_called_once()
            mock_define_ac_meter_charger_circuit_enable_channel.assert_called_once()

    def test_define_ac_meter_charger_enable_channel(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        charger = ACMeterCharger(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
            n2k_devices=n2k_devices,
            circuit=charger_circuit,
        )
        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            ACMeterCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.set_subscription.reset_mock()
            n2k_devices.get_channel_subject.reset_mock()
            mock_define_channel.reset_mock()
            charger.define_ac_meter_charger_circuit_enable_channel(
                charger_circuit, n2k_devices
            )
            mock_channel.assert_any_call(
                id="ce",
                name="Charger Enabled",
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:charger.enabled"],
            )
            mock_define_channel.assert_called_once()
            n2k_devices.get_channel_subject.assert_called_once_with(
                "Circuits.11", "Level", N2kDeviceType.CIRCUIT
            )

    def test_define_ac_meter_charger_enable_channel_read_only_true(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        charger_circuit.switch_type = 0
        charger = ACMeterCharger(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
            n2k_devices=n2k_devices,
            circuit=charger_circuit,
        )
        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            ACMeterCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.set_subscription.reset_mock()
            n2k_devices.get_channel_subject.reset_mock()
            mock_define_channel.reset_mock()
            charger.define_ac_meter_charger_circuit_enable_channel(
                charger_circuit, n2k_devices
            )
            mock_channel.assert_any_call(
                id="ce",
                name="Charger Enabled",
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:charger.enabled"],
            )
            mock_define_channel.assert_called_once()
            n2k_devices.get_channel_subject.assert_called_once_with(
                "Circuits.11", "Level", N2kDeviceType.CIRCUIT
            )

    def test_define_ac_meter_charger_status_channel(self):
        ac_line1 = MagicMock()
        ac_line1.instance = MagicMock(instance=1)
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        categories = ["TEST_CATEGORY"]
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()
        charger_circuit.id = MagicMock(value=11)
        charger_circuit.control_id = 12
        charger = ACMeterCharger(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
            n2k_devices=n2k_devices,
            circuit=charger_circuit,
        )
        with patch(
            "N2KClient.n2kclient.models.empower_system.charger.Channel"
        ) as mock_channel, patch.object(
            ACMeterCharger, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.set_subscription.reset_mock()
            n2k_devices.get_channel_subject.reset_mock()
            mock_define_channel.reset_mock()
            charger.define_ac_meter_charger_channels(
                ac_line1, ac_line2, ac_line3, n2k_devices
            )
            mock_channel.assert_any_call(
                id="cst",
                name="Charger Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:charger.status"],
            )
            mock_define_channel.assert_called_once()
            n2k_devices.get_channel_subject.assert_any_call(
                "AC.1", "Voltage.1", N2kDeviceType.AC
            )
            n2k_devices.get_channel_subject.assert_any_call(
                "AC.1", "Voltage.2", N2kDeviceType.AC
            )
            n2k_devices.get_channel_subject.assert_any_call(
                "AC.1", "Voltage.3", N2kDeviceType.AC
            )
            n2k_devices.set_subscription.assert_called_once()
