import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.dc import DC, DCType
from N2KClient.n2kclient.models.constants import AttrNames
from N2KClient.n2kclient.models.n2k_configuration.instance import Instance

import json


class TestDC(unittest.TestCase):

    def test_dc_to_dict_exception(self):
        obj = DC()
        # Patch a real attribute used in to_dict to raise
        from unittest.mock import patch

        with patch.object(obj, "capacity", side_effect=Exception("fail")):
            d = obj.to_dict()
            self.assertEqual(d, {})

    def test_dc_to_json_string_exception(self):
        obj = DC()
        from unittest.mock import patch

        with patch.object(obj, "capacity", side_effect=Exception("fail")):
            json_str = obj.to_json_string()
            self.assertEqual(json_str, "{}")

    def test_dc_to_dict(self):
        from N2KClient.n2kclient.models.n2k_configuration.instance import Instance

        obj = DC(
            capacity=100,
            show_state_of_charge=True,
            show_temperature=True,
            show_time_of_remaining=True,
            dc_type=DCType.Battery,
            instance=Instance(enabled=True, instance=42),
        )
        d = obj.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d[AttrNames.CAPACITY], 100)
        self.assertTrue(d[AttrNames.SHOW_STATE_OF_CHARGE])
        self.assertTrue(d[AttrNames.SHOW_TEMPERATURE])
        self.assertTrue(d[AttrNames.SHOW_TIME_OF_REMAINING])
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE][AttrNames.INSTANCE], 42)
        self.assertIn(AttrNames.ENABLED, d[AttrNames.INSTANCE])
        self.assertTrue(d[AttrNames.INSTANCE][AttrNames.ENABLED])
        self.assertIn(AttrNames.DC_TYPE, d)
        self.assertEqual(d[AttrNames.DC_TYPE], DCType.Battery.value)

    def test_to_json_string(self):
        obj = DC(
            capacity=200,
            show_state_of_charge=False,
            show_temperature=True,
            show_time_of_remaining=False,
            dc_type=DCType.Battery,
            instance=Instance(enabled=True, instance=99),
        )
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)

        d = json.loads(json_str)
        self.assertEqual(d[AttrNames.CAPACITY], 200)
        self.assertFalse(d[AttrNames.SHOW_STATE_OF_CHARGE])
        self.assertTrue(d[AttrNames.SHOW_TEMPERATURE])
        self.assertFalse(d[AttrNames.SHOW_TIME_OF_REMAINING])
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE][AttrNames.INSTANCE], 99)
        self.assertTrue(d[AttrNames.INSTANCE][AttrNames.ENABLED])
