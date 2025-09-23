import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.alarm import Alarm
from N2KClient.n2kclient.models.constants import AttrNames
from N2KClient.n2kclient.models.common_enums import (
    eAlarmType,
    eSeverityType,
    eStateType,
)


class TestAlarm(unittest.TestCase):
    def test_alarm_to_dict_exception(self):
        # Simulate an attribute missing a .value (e.g., not an enum)
        alarm = Alarm(
            id=1,
            alarm_type="not_an_enum",
            severity="not_an_enum",
            current_state="not_an_enum",
        )
        d = alarm.to_dict()
        self.assertEqual(d, {})

    def test_alarm_to_json_string_exception(self):
        # Simulate to_dict raising an exception by patching it
        alarm = Alarm()
        original_to_dict = alarm.to_dict

        def broken_to_dict():
            raise Exception("fail")

        alarm.to_dict = broken_to_dict
        json_str = alarm.to_json_string()
        self.assertEqual(json_str, "{}")
        # Restore original method
        alarm.to_dict = original_to_dict

    def test_alarm_to_dict(self):
        alarm = Alarm(
            id=1,
            alarm_type=eAlarmType.External,
            severity=eSeverityType.SeverityCritical,
            current_state=eStateType.StateEnabled,
            channel_id=10,
            external_alarm_id=20,
            unique_id=30,
            valid=True,
            activated_time=1000,
            acknowledged_time=2000,
            cleared_time=3000,
            name="Test Alarm",
            channel="Channel1",
            device="Device1",
            title="Alarm Title",
            description="Alarm Desc",
            czone_raw_alarm=b"raw",
            fault_action="Action",
            fault_type=2,
            fault_number=3,
        )
        d = alarm.__dict__
        self.assertEqual(d["id"], 1)
        self.assertEqual(d["alarm_type"], eAlarmType.External)
        self.assertEqual(d["severity"], eSeverityType.SeverityCritical)
        self.assertEqual(d["current_state"], eStateType.StateEnabled)
        self.assertEqual(d["channel_id"], 10)
        self.assertEqual(d["external_alarm_id"], 20)
        self.assertEqual(d["unique_id"], 30)
        self.assertTrue(d["valid"])
        self.assertEqual(d["activated_time"], 1000)
        self.assertEqual(d["acknowledged_time"], 2000)
        self.assertEqual(d["cleared_time"], 3000)
        self.assertEqual(d["name"], "Test Alarm")
        self.assertEqual(d["channel"], "Channel1")
        self.assertEqual(d["device"], "Device1")
        self.assertEqual(d["title"], "Alarm Title")
        self.assertEqual(d["description"], "Alarm Desc")
        self.assertEqual(d["czone_raw_alarm"], b"raw")
        self.assertEqual(d["fault_action"], "Action")
        self.assertEqual(d["fault_type"], 2)
        self.assertEqual(d["fault_number"], 3)
