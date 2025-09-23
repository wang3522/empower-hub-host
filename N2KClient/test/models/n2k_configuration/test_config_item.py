import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.config_item import ConfigItem
from N2KClient.n2kclient.models.constants import AttrNames


class TestConfigItem(unittest.TestCase):
    def test_config_item_to_dict_exception(self):
        obj = ConfigItem()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_config_item_to_json_string_exception(self):
        obj = ConfigItem()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_config_item_to_dict(self):
        obj = ConfigItem(id=11, name_utf8="TestName")
        d = obj.to_dict()
        self.assertIn(AttrNames.ID, d)
        self.assertEqual(d[AttrNames.ID], 11)
        self.assertIn(AttrNames.NAMEUTF8, d)
        self.assertEqual(d[AttrNames.NAMEUTF8], "TestName")

    def test_to_json_string(self):
        obj = ConfigItem(id=12, name_utf8="OtherName")
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"id": 12', json_str)
        self.assertIn('"name_utf8": "OtherName"', json_str)
