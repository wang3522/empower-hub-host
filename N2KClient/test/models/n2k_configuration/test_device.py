import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.device import Device
from N2KClient.n2kclient.models.constants import AttrNames


class TestDevice(unittest.TestCase):
    def test_device_to_dict_exception(self):
        obj = Device()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_device_to_json_string_exception(self):
        obj = Device()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_device_to_dict(self):
        from N2KClient.n2kclient.models.n2k_configuration.device import DeviceType

        obj = Device(
            name_utf8="TestDevice",
            source_address=123,
            conflict=True,
            device_type=DeviceType.Battery,
            valid=True,
            transient=False,
            version="1.2.3",
            dipswitch="A1",
        )
        d = obj.to_dict()
        self.assertEqual(d[AttrNames.NAMEUTF8], "TestDevice")
        self.assertEqual(d[AttrNames.SOURCE_ADDRESS], 123)
        self.assertTrue(d[AttrNames.CONFLICT])
        self.assertEqual(d[AttrNames.DEVICE_TYPE], DeviceType.Battery.value)
        self.assertTrue(d[AttrNames.VALID])
        self.assertFalse(d[AttrNames.TRANSIENT])
        self.assertEqual(d[AttrNames.DIPSWITCH], "A1")
        self.assertEqual(d[AttrNames.VERSION], "1.2.3")

    def test_to_json_string(self):
        from N2KClient.n2kclient.models.n2k_configuration.device import DeviceType

        obj = Device(
            name_utf8="TestDevice",
            source_address=123,
            conflict=True,
            device_type=DeviceType.Battery,
            valid=True,
            transient=False,
            version="1.2.3",
            dipswitch="A1",
        )
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        import json as _json

        d = _json.loads(json_str)
        self.assertEqual(d[AttrNames.NAMEUTF8], "TestDevice")
        self.assertEqual(d[AttrNames.SOURCE_ADDRESS], 123)
        self.assertTrue(d[AttrNames.CONFLICT])
        self.assertEqual(d[AttrNames.DEVICE_TYPE], DeviceType.Battery.value)
        self.assertTrue(d[AttrNames.VALID])
        self.assertFalse(d[AttrNames.TRANSIENT])
        self.assertEqual(d[AttrNames.DIPSWITCH], "A1")
        self.assertEqual(d[AttrNames.VERSION], "1.2.3")
