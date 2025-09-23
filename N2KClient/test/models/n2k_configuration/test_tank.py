import unittest
from unittest.mock import MagicMock
import json
from N2KClient.n2kclient.models.n2k_configuration.tank import Tank, TankType
from N2KClient.n2kclient.models.constants import AttrNames
from unittest.mock import patch


class TestTank(unittest.TestCase):

    def test_to_dict_and_json(self):
        obj = Tank(tank_type=TankType.FreshWater, tank_capacity=123.4)
        d = obj.to_dict()
        self.assertEqual(d[AttrNames.TANK_TYPE], TankType.FreshWater.value)
        self.assertEqual(d[AttrNames.TANK_CAPACITY], 123.4)
        json_str = obj.to_json_string()
        self.assertIn('"tank_type": 1', json_str)
        self.assertIn('"tank_capacity": 123.4', json_str)

    def test_to_json_string_exception(self):
        obj = Tank()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")
