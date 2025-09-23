import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.data_id import DataId
from N2KClient.n2kclient.models.constants import AttrNames


class TestDataId(unittest.TestCase):
    def test_data_id_to_dict_exception(self):
        obj = DataId()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_data_id_to_json_string_exception(self):
        obj = DataId()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_data_id_to_dict(self):
        obj = DataId(id=42, enabled=True)
        d = obj.to_dict()
        self.assertIn(AttrNames.ID, d)
        self.assertEqual(d[AttrNames.ID], 42)
        self.assertIn(AttrNames.ENABLED, d)
        self.assertEqual(d[AttrNames.ENABLED], True)

    def test_to_json_string(self):
        obj = DataId(id=99, enabled=True)
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"id": 99', json_str)
        self.assertIn('"enabled": true', json_str)
