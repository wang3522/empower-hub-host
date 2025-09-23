import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineDevice, EngineType
from N2KClient.n2kclient.models.constants import AttrNames


class TestEngineDevice(unittest.TestCase):
    def test_engine_device_to_dict_exception(self):
        # Use MagicMock to raise when .value is accessed
        bad_enum = MagicMock()
        type(bad_enum).value = property(
            lambda self: (_ for _ in ()).throw(Exception("fail"))
        )
        device = EngineDevice(
            instance=MagicMock(),
            software_id="swid",
            calibration_id="calid",
            serial_number="sn",
            ecu_serial_number="ecu",
            engine_type=bad_enum,
        )
        d = device.to_dict()
        self.assertEqual(d, {})

    def test_engine_device_to_json_string_exception(self):
        bad_enum = MagicMock()
        type(bad_enum).value = property(
            lambda self: (_ for _ in ()).throw(Exception("fail"))
        )
        device = EngineDevice(instance=MagicMock(), engine_type=bad_enum)
        json_str = device.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_engine_device_to_dict(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        device = EngineDevice(
            instance=instance_mock,
            software_id="swid",
            calibration_id="calid",
            serial_number="sn",
            ecu_serial_number="ecu",
            engine_type=EngineType.NMEA2000,
        )
        d = device.to_dict()
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE], "instance_dict")
        self.assertIn(AttrNames.SOFTWARE_ID, d)
        self.assertEqual(d[AttrNames.SOFTWARE_ID], "swid")
        self.assertIn(AttrNames.CALIBRATION_ID, d)
        self.assertEqual(d[AttrNames.CALIBRATION_ID], "calid")
        self.assertIn(AttrNames.SERIAL_NUMBER, d)
        self.assertEqual(d[AttrNames.SERIAL_NUMBER], "sn")
        self.assertIn(AttrNames.ECU_SERIAL_NUMBER, d)
        self.assertEqual(d[AttrNames.ECU_SERIAL_NUMBER], "ecu")
        self.assertIn(AttrNames.ENGINE_TYPE, d)
        self.assertEqual(d[AttrNames.ENGINE_TYPE], EngineType.NMEA2000.value)

    def test_to_json_string(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        device = EngineDevice(
            instance=instance_mock,
            software_id="swid2",
            calibration_id="calid2",
            serial_number="sn2",
            ecu_serial_number="ecu2",
            engine_type=EngineType.SmartCraft,
        )
        json_str = device.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"instance": "instance_dict"', json_str)
        self.assertIn('"software_id": "swid2"', json_str)
        self.assertIn('"calibration_id": "calid2"', json_str)
        self.assertIn('"serial_number": "sn2"', json_str)
        self.assertIn('"ecu_serial_number": "ecu2"', json_str)
        self.assertIn('"engine_type": 0', json_str)
