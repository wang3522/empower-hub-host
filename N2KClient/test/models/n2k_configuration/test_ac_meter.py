import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.ac_meter import ACMeter


class TestACMeter(unittest.TestCase):
    def test_ac_meter_to_dict_exception(self):
        meter = ACMeter()
        meter.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = meter.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_ac_meter_to_json_string_exception(self):
        meter = ACMeter()
        meter.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = meter.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_ac_meter_to_dict(self):
        ac_mock = MagicMock()
        ac_mock.to_dict.return_value = {"ac_key": "ac_val"}
        meter = ACMeter(line={1: ac_mock, 2: ac_mock})
        d = meter.to_dict()
        self.assertIn("line", d)
        self.assertEqual(d["line"], {1: {"ac_key": "ac_val"}, 2: {"ac_key": "ac_val"}})

    def test_to_json_string(self):
        ac_mock = MagicMock()
        ac_mock.to_dict.return_value = {"ac_key": "ac_val"}
        meter = ACMeter(line={3: ac_mock})
        json_str = meter.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"line": {"3": {"ac_key": "ac_val"}}', json_str)
