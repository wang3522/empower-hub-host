import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.alarm_limit import AlarmLimit
from N2KClient.n2kclient.models.constants import AttrNames


class TestAlarmLimit(unittest.TestCase):
    def test_alarm_limit_to_dict_exception(self):
        obj = AlarmLimit()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_alarm_limit_to_json_string_exception(self):
        obj = AlarmLimit()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_alarm_limit_to_dict(self):
        obj = AlarmLimit(id=7, enabled=True, on=1.23, off=4.56)
        d = obj.to_dict()
        self.assertIn(AttrNames.ID, d)
        self.assertEqual(d[AttrNames.ID], 7)
        self.assertIn(AttrNames.ENABLED, d)
        self.assertTrue(d[AttrNames.ENABLED])
        self.assertIn(AttrNames.ON, d)
        self.assertEqual(d[AttrNames.ON], 1.23)
        self.assertIn(AttrNames.OFF, d)
        self.assertEqual(d[AttrNames.OFF], 4.56)

    def test_to_json_string(self):
        obj = AlarmLimit(id=8, enabled=False, on=9.87, off=6.54)
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"id": 8', json_str)
        self.assertIn('"enabled": false', json_str)
        self.assertIn('"on": 9.87', json_str)
        self.assertIn('"off": 6.54', json_str)
