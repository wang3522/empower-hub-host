import unittest
from unittest.mock import MagicMock
import json
from N2KClient.n2kclient.models.n2k_configuration.value_u32 import ValueU32
from N2KClient.n2kclient.models.constants import AttrNames
from unittest.mock import patch


class TestValueU32(unittest.TestCase):

    def test_to_dict_and_json(self):
        obj = ValueU32(valid=True, value=123456)
        d = obj.to_dict()
        self.assertTrue(d[AttrNames.VALID])
        self.assertEqual(d[AttrNames.VALUE], 123456)
        json_str = obj.to_json_string()
        self.assertIn('"valid": true', json_str)
        self.assertIn('"value": 123456', json_str)
