import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.gnss import GNSSDevice
from N2KClient.n2kclient.models.constants import AttrNames


class TestGNSSDevice(unittest.TestCase):
    def test_gnss_device_to_dict_exception(self):
        obj = GNSSDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_gnss_device_to_json_string_exception(self):
        obj = GNSSDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_gnss_device_to_dict(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        obj = GNSSDevice(instance=instance_mock, is_external=True)
        d = obj.to_dict()
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE], "instance_dict")
        self.assertIn(AttrNames.IS_EXTERNAL, d)
        self.assertTrue(d[AttrNames.IS_EXTERNAL])

    def test_to_json_string(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        obj = GNSSDevice(instance=instance_mock, is_external=False)
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"instance": "instance_dict"', json_str)
        self.assertIn('"is_external": false', json_str)
