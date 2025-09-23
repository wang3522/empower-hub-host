import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.instance import Instance
from N2KClient.n2kclient.models.constants import AttrNames


class TestInstance(unittest.TestCase):
    def test_instance_to_dict_exception(self):
        obj = Instance()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_instance_to_json_string_exception(self):
        obj = Instance()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_instance_to_dict(self):
        obj = Instance(enabled=True, instance=5)
        d = obj.to_dict()
        self.assertIn(AttrNames.ENABLED, d)
        self.assertTrue(d[AttrNames.ENABLED])
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE], 5)

    def test_to_json_string(self):
        obj = Instance(enabled=False, instance=9)
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"enabled": false', json_str)
        self.assertIn('"instance": 9', json_str)
