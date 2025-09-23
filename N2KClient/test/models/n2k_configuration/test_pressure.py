import unittest
from unittest.mock import MagicMock
import json
from N2KClient.n2kclient.models.n2k_configuration.pressure import Pressure, PressureType
from N2KClient.n2kclient.models.constants import AttrNames
from unittest.mock import patch


class TestPressure(unittest.TestCase):

    def test_to_dict_and_json(self):
        obj = Pressure(pressure_type=PressureType.Water, atmospheric_pressure=True)
        d = obj.to_dict()
        self.assertEqual(d[AttrNames.PRESSURE_TYPE], PressureType.Water.value)
        self.assertTrue(d[AttrNames.ATMOSPHERIC_PRESSURE])
        json_str = obj.to_json_string()
        self.assertIn('"pressure_type": 1', json_str)
        self.assertIn('"atmospheric_pressure": true', json_str)

    def test_to_json_string_exception(self):
        obj = Pressure()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")
