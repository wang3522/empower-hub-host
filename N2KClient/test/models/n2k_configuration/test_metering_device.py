import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.metering_device import MeteringDevice
from N2KClient.n2kclient.models.constants import AttrNames
import json


class TestMeteringDevice(unittest.TestCase):

    def test_metering_device_to_dict(self):

        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        alarm_mock = MagicMock()
        alarm_mock.to_dict.return_value = "alarm_dict"

        device = MeteringDevice(
            instance=instance_mock,
            output=True,
            nominal_voltage=24,
            address=7,
            show_voltage=True,
            show_current=False,
            low_limit=alarm_mock,
            very_low_limit=alarm_mock,
            high_limit=alarm_mock,
            very_high_limit=alarm_mock,
            frequency=alarm_mock,
            low_voltage=alarm_mock,
            very_low_voltage=alarm_mock,
            high_voltage=alarm_mock,
        )
        d = device.to_dict()
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE], "instance_dict")
        self.assertIn(AttrNames.OUTPUT, d)
        self.assertTrue(d[AttrNames.OUTPUT])
        self.assertIn(AttrNames.NOMINAL_VOLTAGE, d)
        self.assertEqual(d[AttrNames.NOMINAL_VOLTAGE], 24)
        self.assertIn(AttrNames.ADDRESS, d)
        self.assertEqual(d[AttrNames.ADDRESS], 7)
        self.assertIn(AttrNames.SHOW_VOLTAGE, d)
        self.assertTrue(d[AttrNames.SHOW_VOLTAGE])
        self.assertIn(AttrNames.SHOW_CURRENT, d)
        self.assertFalse(d[AttrNames.SHOW_CURRENT])
        self.assertIn(AttrNames.LOW_LIMIT, d)
        self.assertEqual(d[AttrNames.LOW_LIMIT], "alarm_dict")
        self.assertIn(AttrNames.VERY_LOW_LIMIT, d)
        self.assertEqual(d[AttrNames.VERY_LOW_LIMIT], "alarm_dict")
        self.assertIn(AttrNames.HIGH_LIMIT, d)
        self.assertEqual(d[AttrNames.HIGH_LIMIT], "alarm_dict")
        self.assertIn(AttrNames.VERY_HIGH_LIMIT, d)
        self.assertEqual(d[AttrNames.VERY_HIGH_LIMIT], "alarm_dict")
        self.assertIn(AttrNames.FREQUENCY, d)
        self.assertEqual(d[AttrNames.FREQUENCY], "alarm_dict")
        self.assertIn(AttrNames.LOW_VOLTAGE, d)
        self.assertEqual(d[AttrNames.LOW_VOLTAGE], "alarm_dict")
        self.assertIn(AttrNames.VERY_LOW_VOLTAGE, d)
        self.assertEqual(d[AttrNames.VERY_LOW_VOLTAGE], "alarm_dict")
        self.assertIn(AttrNames.HIGH_VOLTAGE, d)
        self.assertEqual(d[AttrNames.HIGH_VOLTAGE], "alarm_dict")

    def test_metering_device_to_dict_exception(self):

        device = MeteringDevice()
        device.instance.to_dict = MagicMock(side_effect=Exception("Test exception"))
        d = device.to_dict()
        self.assertEqual(d, {})  # Expecting empty dict on exception

    def test_to_json_string(self):

        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        alarm_mock = MagicMock()
        alarm_mock.to_dict.return_value = "alarm_dict"

        device = MeteringDevice(
            instance=instance_mock,
            output=True,
            nominal_voltage=24,
            address=7,
            show_voltage=True,
            show_current=False,
            low_limit=alarm_mock,
            very_low_limit=alarm_mock,
            high_limit=alarm_mock,
            very_high_limit=alarm_mock,
            frequency=alarm_mock,
            low_voltage=alarm_mock,
            very_low_voltage=alarm_mock,
            high_voltage=alarm_mock,
        )
        json_str = device.to_json_string()
        self.assertIsInstance(json_str, str)
        # Check that the JSON string contains expected keys and values
        self.assertIn('"instance": "instance_dict"', json_str)
        self.assertIn('"output": true', json_str)
        self.assertIn('"nominal_voltage": 24', json_str)
        self.assertIn('"address": 7', json_str)
        self.assertIn('"show_voltage": true', json_str)
        self.assertIn('"show_current": false', json_str)
        self.assertIn('"low_limit": "alarm_dict"', json_str)
        self.assertIn('"very_low_limit": "alarm_dict"', json_str)
        self.assertIn('"high_limit": "alarm_dict"', json_str)
        self.assertIn('"very_high_limit": "alarm_dict"', json_str)
        self.assertIn('"frequency": "alarm_dict"', json_str)
        self.assertIn('"low_voltage": "alarm_dict"', json_str)
        self.assertIn('"very_low_voltage": "alarm_dict"', json_str)
        self.assertIn('"high_voltage": "alarm_dict"', json_str)

    def test_to_json_string_exception(self):

        device = MeteringDevice()
        device.to_dict = MagicMock(side_effect=Exception("Test exception"))
        json_str = device.to_json_string()
        self.assertEqual(json_str, "{}")  # Expecting empty JSON object on exception
