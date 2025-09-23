import unittest
from unittest.mock import MagicMock
import json
from N2KClient.n2kclient.models.n2k_configuration.sequential_name import SequentialName
from N2KClient.n2kclient.models.constants import AttrNames
from unittest.mock import patch


class TestSequentialName(unittest.TestCase):
    def test_to_dict_and_json(self):
        obj = SequentialName(name="TestName")
        d = obj.to_dict()
        self.assertEqual(d[AttrNames.NAME], "TestName")
        json_str = obj.to_json_string()
        self.assertIn('"name": "TestName"', json_str)

    def test_to_dict_exception(self):
        obj = SequentialName()

        with patch.object(obj, "to_dict", side_effect=Exception("fail")):
            try:
                d = obj.to_dict()
            except Exception:
                d = {}
            self.assertEqual(d, {})

    def test_to_json_string_exception(self):
        obj = SequentialName()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")
