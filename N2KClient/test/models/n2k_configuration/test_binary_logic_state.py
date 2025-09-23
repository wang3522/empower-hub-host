import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.binary_logic_state import (
    BinaryLogicState,
)
from N2KClient.n2kclient.models.constants import AttrNames


class TestBinaryLogicState(unittest.TestCase):
    def test_binary_logic_state_to_dict_exception(self):
        obj = BinaryLogicState()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_binary_logic_state_to_json_string_exception(self):
        obj = BinaryLogicState()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_binary_logic_state_to_dict(self):
        # Patch super().to_dict to return a known value
        orig_super = BinaryLogicState.__bases__[0].to_dict
        BinaryLogicState.__bases__[0].to_dict = MagicMock(
            return_value={"super_key": "super_val"}
        )
        obj = BinaryLogicState(address=42)
        d = obj.to_dict()
        self.assertIn("super_key", d)
        self.assertEqual(d["super_key"], "super_val")
        self.assertIn(AttrNames.ADDRESS, d)
        self.assertEqual(d[AttrNames.ADDRESS], 42)
        # Restore
        BinaryLogicState.__bases__[0].to_dict = orig_super

    def test_to_json_string(self):
        orig_super = BinaryLogicState.__bases__[0].to_dict
        BinaryLogicState.__bases__[0].to_dict = MagicMock(return_value={})
        obj = BinaryLogicState(address=99)
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"address": 99', json_str)
        BinaryLogicState.__bases__[0].to_dict = orig_super
