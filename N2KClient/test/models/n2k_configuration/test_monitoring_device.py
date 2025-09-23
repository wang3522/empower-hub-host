import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.monitoring_device import (
    MonitoringDevice,
)
from N2KClient.n2kclient.models.constants import AttrNames
import json


class TestMonitoringDevice(unittest.TestCase):

    def test_monitoring_device_to_dict(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        alarm_mock = MagicMock()
        alarm_mock.to_dict.return_value = "alarm_dict"
        switch_type_mock = MagicMock()
        switch_type_mock.value = "switch_type_value"
        circuit_id_mock = MagicMock()
        circuit_id_mock.to_dict.return_value = "circuit_id_dict"

        device = MonitoringDevice(
            id=42,
            instance=instance_mock,
            switch_type=switch_type_mock,
            address=7,
            circuit_id=circuit_id_mock,
            circuit_name_utf8="circuit_name",
            very_low_limit=alarm_mock,
            low_limit=alarm_mock,
            high_limit=alarm_mock,
            very_high_limit=alarm_mock,
        )
        d = device.to_dict()
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE], "instance_dict")
        self.assertIn(AttrNames.SWITCH_TYPE, d)
        self.assertEqual(d[AttrNames.SWITCH_TYPE], "switch_type_value")
        self.assertIn(AttrNames.ADDRESS, d)
        self.assertEqual(d[AttrNames.ADDRESS], 7)
        self.assertIn("circuit_id", d)
        self.assertEqual(d["circuit_id"], "circuit_id_dict")
        self.assertIn("circuit_name_utf8", d)
        self.assertEqual(d["circuit_name_utf8"], "circuit_name")
        self.assertIn(AttrNames.VERY_LOW_LIMIT, d)
        self.assertEqual(d[AttrNames.VERY_LOW_LIMIT], "alarm_dict")
        self.assertIn(AttrNames.LOW_LIMIT, d)
        self.assertEqual(d[AttrNames.LOW_LIMIT], "alarm_dict")
        self.assertIn(AttrNames.HIGH_LIMIT, d)
        self.assertEqual(d[AttrNames.HIGH_LIMIT], "alarm_dict")
        self.assertIn(AttrNames.VERY_HIGH_LIMIT, d)
        self.assertEqual(d[AttrNames.VERY_HIGH_LIMIT], "alarm_dict")

    def test_monitoring_device_to_dict_exception(self):
        device = MonitoringDevice()
        device.instance.to_dict = MagicMock(side_effect=Exception("Test exception"))
        d = device.to_dict()
        self.assertEqual(d, {})  # Expecting empty dict on exception

    def test_to_json_string(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        alarm_mock = MagicMock()
        alarm_mock.to_dict.return_value = "alarm_dict"
        switch_type_mock = MagicMock()
        switch_type_mock.value = "switch_type_value"
        circuit_id_mock = MagicMock()
        circuit_id_mock.to_dict.return_value = "circuit_id_dict"

        device = MonitoringDevice(
            id=42,
            instance=instance_mock,
            switch_type=switch_type_mock,
            address=7,
            circuit_id=circuit_id_mock,
            circuit_name_utf8="circuit_name",
            very_low_limit=alarm_mock,
            low_limit=alarm_mock,
            high_limit=alarm_mock,
            very_high_limit=alarm_mock,
        )
        json_str = device.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"instance": "instance_dict"', json_str)
        self.assertIn('"switch_type": "switch_type_value"', json_str)
        self.assertIn('"address": 7', json_str)
        self.assertIn('"circuit_id": "circuit_id_dict"', json_str)
        self.assertIn('"circuit_name_utf8": "circuit_name"', json_str)
        self.assertIn('"very_low_limit": "alarm_dict"', json_str)
        self.assertIn('"low_limit": "alarm_dict"', json_str)
        self.assertIn('"high_limit": "alarm_dict"', json_str)
        self.assertIn('"very_high_limit": "alarm_dict"', json_str)

    def test_to_json_string_exception(self):
        device = MonitoringDevice()
        device.to_dict = MagicMock(side_effect=Exception("Test exception"))
        json_str = device.to_json_string()
        self.assertEqual(json_str, "{}")  # Expecting empty JSON object on exception
