import unittest
from unittest.mock import MagicMock, patch

from N2KClient.n2kclient.models.empower_system.charger import CombiCharger
from N2KClient.n2kclient.models.empower_system.engine_alarm import EngineAlarm
from N2KClient.n2kclient.models.empower_system.engine_alarm_list import EngineAlarmList

from N2KClient.n2kclient.models.n2k_configuration.n2k_configuation import (
    N2kConfiguration,
)

from N2KClient.n2kclient.models.n2k_configuration.ac import AC
from N2KClient.n2kclient.models.n2k_configuration.ac_meter import ACMeter
from N2KClient.n2kclient.services.alarm_service.alarm_helpers import (
    get_inverter_charger_alarm_title,
    generate_alarms_from_discrete_status,
    get_combi_charger,
    get_combi_inverter,
)
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineDevice


class AlarmHelpersTest(unittest.TestCase):
    """
    Unit tests for the AlarmHelpers class.
    """

    def test_generate_alarms_from_discrete_status_add_alarm(self):
        """
        Should add an alarm when the corresponding bit is set and not present in previous list.
        """
        status_alarms = [(0, "Alarm0"), (1, "Alarm1")]
        discrete_status = 1  # Only bit 0 set
        merged_engine_alarm_list = EngineAlarmList()
        prev_engine_alarm_list = EngineAlarmList()
        engine_config = EngineDevice()
        engine_config.name_utf8 = "TestEngine"
        engine_id = 1
        engine_config.id = engine_id
        generate_alarms_from_discrete_status(
            status_alarms,
            discrete_status,
            merged_engine_alarm_list,
            None,
            None,
            None,
            None,
            prev_engine_alarm_list,
            engine_id,
            engine_config,
            1,
        )
        alarm_id = f"engine.{engine_id}.discrete_status1.0"
        self.assertIn(alarm_id, merged_engine_alarm_list.engine_alarms)

    def test_generate_alarms_from_discrete_status_no_alarm(self):
        """
        Should not add any alarm when no bits are set.
        """
        status_alarms = [(0, "Alarm0"), (1, "Alarm1")]
        discrete_status = 0
        merged_engine_alarm_list = EngineAlarmList()
        prev_engine_alarm_list = EngineAlarmList()
        engine_config = EngineDevice()
        engine_config.name_utf8 = "TestEngine"
        engine_id = 1
        engine_config.id = engine_id
        generate_alarms_from_discrete_status(
            status_alarms,
            discrete_status,
            merged_engine_alarm_list,
            None,
            None,
            None,
            None,
            prev_engine_alarm_list,
            engine_id,
            engine_config,
            1,
        )
        self.assertEqual(len(merged_engine_alarm_list.engine_alarms), 0)

    def test_generate_alarms_from_discrete_status_remove_alarm(self):
        """
        Should remove alarm if bit is not set but alarm is present.
        """
        status_alarms = [(0, "Alarm0")]
        discrete_status = 0
        merged_engine_alarm_list = EngineAlarmList()
        engine_config = EngineDevice()
        engine_config.name_utf8 = "TestEngine"
        engine_id = 1
        engine_config.id = engine_id
        alarm_id = f"engine.{engine_id}.discrete_status1.0"
        # Pre-populate with an alarm
        merged_engine_alarm_list.engine_alarms[alarm_id] = EngineAlarm(
            date_active="now",
            alarm_text="Alarm0",
            engine=engine_config,
            prev_discrete_status1=None,
            prev_discrete_status2=None,
            current_discrete_status1=None,
            current_discrete_status2=None,
            alarm_id=alarm_id,
        )
        prev_engine_alarm_list = EngineAlarmList()
        generate_alarms_from_discrete_status(
            status_alarms,
            discrete_status,
            merged_engine_alarm_list,
            None,
            None,
            None,
            None,
            prev_engine_alarm_list,
            engine_id,
            engine_config,
            1,
        )
        self.assertNotIn(alarm_id, merged_engine_alarm_list.engine_alarms)

    def test_generate_alarms_from_discrete_status_multiple_bits(self):
        """
        Should add multiple alarms when multiple bits are set.
        """
        status_alarms = [(0, "Alarm0"), (1, "Alarm1"), (2, "Alarm2")]
        discrete_status = 0b101  # bits 0 and 2 set
        merged_engine_alarm_list = EngineAlarmList()
        prev_engine_alarm_list = EngineAlarmList()
        engine_config = EngineDevice()
        engine_config.name_utf8 = "TestEngine"
        engine_id = 1
        engine_config.id = engine_id
        generate_alarms_from_discrete_status(
            status_alarms,
            discrete_status,
            merged_engine_alarm_list,
            None,
            None,
            None,
            None,
            prev_engine_alarm_list,
            engine_id,
            engine_config,
            1,
        )
        self.assertIn(
            f"engine.{engine_id}.discrete_status1.0",
            merged_engine_alarm_list.engine_alarms,
        )
        self.assertIn(
            f"engine.{engine_id}.discrete_status1.2",
            merged_engine_alarm_list.engine_alarms,
        )
        self.assertNotIn(
            f"engine.{engine_id}.discrete_status1.1",
            merged_engine_alarm_list.engine_alarms,
        )

    def test_get_inverter_charger_alarm_title(self):
        """
        Test the get_inverter_charger_alarm_title function.
        """
        n2k_config = N2kConfiguration()
        # AC1
        ac1 = ACMeter()
        ac1.line[0] = AC()
        ac1.line[0].id = 1234
        ac1.line[0].name_utf8 = "Inverter Charger 1"
        n2k_config.ac[0] = ac1
        name = get_inverter_charger_alarm_title(n2k_config, 1234)

        self.assertEqual(name, "Inverter Charger 1")

    def test_get_inverter_charger_alarm_title_not_found(self):
        """
        Test the get_inverter_charger_alarm_title function scenerio where ac not found
        """

        n2k_config = N2kConfiguration()
        # AC1
        ac1 = ACMeter()
        ac1.line[0] = AC()
        ac1.line[0].id = 1234
        ac1.line[0].name_utf8 = "Inverter Charger 1"
        n2k_config.ac[0] = ac1

        # ACT
        name = get_inverter_charger_alarm_title(n2k_config, 999)

        # Assert
        self.assertIsNone(name, "Expected None when AC ID is not found")

    def test_get_combi_charger(self):
        """
        Test the get_combi_charger function.
        """
        n2k_config = N2kConfiguration()
        n2k_config.inverter_charger = {
            1: MagicMock(battery_bank_1_id=MagicMock(id=1, enabled=True))
        }
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_helpers.calculate_inverter_charger_instance",
            return_value=12345,
        ):
            res = get_combi_charger(n2k_config, 1, [])
            self.assertIn("charger.12345", res)

    def test_get_combi_charger_duplicate(self):
        """
        Test the get_combi_charger function. Duplicate not added
        """
        n2k_config = N2kConfiguration()
        n2k_config.inverter_charger = {
            1: MagicMock(battery_bank_1_id=MagicMock(id=1, enabled=True))
        }
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_helpers.calculate_inverter_charger_instance",
            return_value=12345,
        ):
            res = get_combi_charger(n2k_config, 1, [])
            res = get_combi_charger(n2k_config, 1, res)
            self.assertIn("charger.12345", res)
            self.assertEqual(len(res), 1)

    def test_get_combi_charger_no_match(self):
        """
        Test the get_combi_charger function. Not matching battery_bank. Not added
        """
        n2k_config = N2kConfiguration()
        n2k_config.inverter_charger = {
            1: MagicMock(battery_bank_1_id=MagicMock(id=2, enabled=True))
        }
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_helpers.calculate_inverter_charger_instance",
            return_value=12345,
        ):
            res = get_combi_charger(n2k_config, 1, [])
            self.assertNotIn("charger.12345", res)
            self.assertEqual(len(res), 0)

    def test_get_combi_inverter(self):
        """
        Test the get_combi_inverter function.
        """
        n2k_config = N2kConfiguration()
        n2k_config.inverter_charger = {
            1: MagicMock(inverter_ac_id=MagicMock(id=1, enabled=True))
        }
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_helpers.calculate_inverter_charger_instance",
            return_value=12345,
        ):
            res = get_combi_inverter(n2k_config, 1, [])
            self.assertIn("inverter.12345", res)

    def test_get_combi_inverter_duplicate(self):
        """
        Test the get_combi_inverter function. Duplicate not added
        """
        n2k_config = N2kConfiguration()
        n2k_config.inverter_charger = {
            1: MagicMock(inverter_ac_id=MagicMock(id=1, enabled=True))
        }
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_helpers.calculate_inverter_charger_instance",
            return_value=12345,
        ):
            res = get_combi_inverter(n2k_config, 1, [])
            res = get_combi_inverter(n2k_config, 1, res)
            self.assertIn("inverter.12345", res)
            self.assertEqual(len(res), 1)

    def test_get_combi_inverter_no_match(self):
        """
        Test the get_combi_inverter function. Not matching inverter_ac_id. Not added
        """
        n2k_config = N2kConfiguration()
        n2k_config.inverter_charger = {
            1: MagicMock(inverter_ac_id=MagicMock(id=2, enabled=True))
        }
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_helpers.calculate_inverter_charger_instance",
            return_value=12345,
        ):
            res = get_combi_inverter(n2k_config, 1, [])
            self.assertNotIn("inverter.12345", res)
            self.assertEqual(len(res), 0)
