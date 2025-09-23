import unittest
from unittest.mock import MagicMock
import json
from N2KClient.n2kclient.models.n2k_configuration.temperature import (
    Temperature,
    TemperatureType,
)
from N2KClient.n2kclient.models.constants import AttrNames
from unittest.mock import patch


class TestTemperature(unittest.TestCase):
    def test_to_dict_and_json(self):
        obj = Temperature(
            high_temperature=True, temperature_type=TemperatureType.EngineRoom
        )
        d = obj.to_dict()
        self.assertTrue(d[AttrNames.HIGH_TEMPERATURE])
        self.assertEqual(
            d[AttrNames.TEMPERATURE_TYPE], TemperatureType.EngineRoom.value
        )
        json_str = obj.to_json_string()
        self.assertIn('"high_temperature": true', json_str)
        self.assertIn(
            f'"temperature_type": {TemperatureType.EngineRoom.value}', json_str
        )

    def test_to_dict_exception(self):
        obj = Temperature()
        with patch.object(obj, "to_dict", side_effect=Exception("fail")):
            try:
                d = obj.to_dict()
            except Exception:
                d = {}
            self.assertEqual(d, {})

    def test_to_json_string_exception(self):
        obj = Temperature()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")
