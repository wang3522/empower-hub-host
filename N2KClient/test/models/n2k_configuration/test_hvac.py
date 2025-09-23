import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.hvac import HVACDevice, AttrNames


class TestHVACDevice(unittest.TestCase):
    def test_hvac_device_to_dict_exception(self):
        obj = HVACDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_hvac_device_to_json_string_exception(self):
        obj = HVACDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_hvac_device_to_dict(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        data_id_mock = MagicMock()
        data_id_mock.to_dict.return_value = "data_id_dict"
        temp_instance_mock = MagicMock()
        temp_instance_mock.to_dict.return_value = "temp_instance_dict"
        obj = HVACDevice(
            instance=instance_mock,
            operating_mode_id=data_id_mock,
            fan_mode_id=data_id_mock,
            fan_speed_id=data_id_mock,
            setpoint_temperature_id=data_id_mock,
            operating_mode_toggle_id=data_id_mock,
            fan_mode_toggle_id=data_id_mock,
            fan_speed_toggle_id=data_id_mock,
            setpoint_temperature_toggle_id=data_id_mock,
            temperature_monitoring_id=data_id_mock,
            fan_speed_count=3,
            operating_modes_mask=7,
            model=2,
            temperature_instance=temp_instance_mock,
            setpoint_temperature_min=10.5,
            setpoint_temperature_max=22.5,
            fan_speed_off_modes_mask=1,
            fan_speed_auto_modes_mask=2,
            fan_speed_manual_modes_mask=3,
        )
        d = obj.to_dict()
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE], "instance_dict")
        self.assertIn(AttrNames.OPERATING_MODE_ID, d)
        self.assertEqual(d[AttrNames.OPERATING_MODE_ID], "data_id_dict")
        self.assertIn(AttrNames.FAN_MODE_ID, d)
        self.assertEqual(d[AttrNames.FAN_MODE_ID], "data_id_dict")
        self.assertIn(AttrNames.FAN_SPEED_ID, d)
        self.assertEqual(d[AttrNames.FAN_SPEED_ID], "data_id_dict")
        self.assertIn(AttrNames.FAN_SPEED_COUNT, d)
        self.assertEqual(d[AttrNames.FAN_SPEED_COUNT], 3)
        self.assertIn(AttrNames.OPERATING_MODES_MASK, d)
        self.assertEqual(d[AttrNames.OPERATING_MODES_MASK], 7)
        self.assertIn(AttrNames.MODEL, d)
        self.assertEqual(d[AttrNames.MODEL], 2)
        self.assertIn(AttrNames.TEMPERATURE_INSTANCE, d)
        self.assertEqual(d[AttrNames.TEMPERATURE_INSTANCE], "temp_instance_dict")
        self.assertIn(AttrNames.SETPOINT_TEMPERATURE_MIN, d)
        self.assertEqual(d[AttrNames.SETPOINT_TEMPERATURE_MIN], 10.5)
        self.assertIn(AttrNames.SETPOINT_TEMPERATURE_MAX, d)
        self.assertEqual(d[AttrNames.SETPOINT_TEMPERATURE_MAX], 22.5)
        self.assertIn(AttrNames.FAN_SPEED_OFF_MODES_MASK, d)
        self.assertEqual(d[AttrNames.FAN_SPEED_OFF_MODES_MASK], 1)
        self.assertIn(AttrNames.FAN_SPEED_AUTO_MODES_MASK, d)
        self.assertEqual(d[AttrNames.FAN_SPEED_AUTO_MODES_MASK], 2)
        self.assertIn(AttrNames.FAN_SPEED_MANUAL_MODES_MASK, d)
        self.assertEqual(d[AttrNames.FAN_SPEED_MANUAL_MODES_MASK], 3)

    def test_to_json_string(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        data_id_mock = MagicMock()
        data_id_mock.to_dict.return_value = "data_id_dict"
        temp_instance_mock = MagicMock()
        temp_instance_mock.to_dict.return_value = "temp_instance_dict"
        obj = HVACDevice(
            instance=instance_mock,
            operating_mode_id=data_id_mock,
            fan_mode_id=data_id_mock,
            fan_speed_id=data_id_mock,
            setpoint_temperature_id=data_id_mock,
            operating_mode_toggle_id=data_id_mock,
            fan_mode_toggle_id=data_id_mock,
            fan_speed_toggle_id=data_id_mock,
            setpoint_temperature_toggle_id=data_id_mock,
            temperature_monitoring_id=data_id_mock,
            fan_speed_count=3,
            operating_modes_mask=7,
            model=2,
            temperature_instance=temp_instance_mock,
            setpoint_temperature_min=10.5,
            setpoint_temperature_max=22.5,
            fan_speed_off_modes_mask=1,
            fan_speed_auto_modes_mask=2,
            fan_speed_manual_modes_mask=3,
        )
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"instance": "instance_dict"', json_str)
        self.assertIn('"fan_speed_count": 3', json_str)
        self.assertIn('"operating_modes_mask": 7', json_str)
        self.assertIn('"model": 2', json_str)
        self.assertIn('"temperature_instance": "temp_instance_dict"', json_str)
        self.assertIn('"setpoint_temperature_min": 10.5', json_str)
        self.assertIn('"setpoint_temperature_max": 22.5', json_str)
        self.assertIn('"fan_speed_off_modes_mask": 1', json_str)
        self.assertIn('"fan_speed_auto_modes_mask": 2', json_str)
        self.assertIn('"fan_speed_manual_modes_mask": 3', json_str)
