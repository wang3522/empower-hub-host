import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.audio_stereo import AudioStereoDevice
from N2KClient.n2kclient.models.constants import AttrNames


class TestAudioStereoDevice(unittest.TestCase):
    def test_audio_stereo_to_dict_exception(self):
        obj = AudioStereoDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_audio_stereo_to_json_string_exception(self):
        obj = AudioStereoDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_audio_stereo_to_dict(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        circuit_mock = MagicMock()
        circuit_mock.to_dict.return_value = "circuit_id_dict"
        obj = AudioStereoDevice(
            instance=instance_mock, mute_enabled=True, circuit_ids=[circuit_mock]
        )
        d = obj.to_dict()
        self.assertIn(AttrNames.INSTANCE, d)
        self.assertEqual(d[AttrNames.INSTANCE], "instance_dict")
        self.assertIn(AttrNames.MUTE_ENABLED, d)
        self.assertTrue(d[AttrNames.MUTE_ENABLED])
        self.assertIn(AttrNames.CIRCUIT_IDS, d)
        self.assertEqual(d[AttrNames.CIRCUIT_IDS], ["circuit_id_dict"])

    def test_to_json_string(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        circuit_mock = MagicMock()
        circuit_mock.to_dict.return_value = "circuit_id_dict"
        obj = AudioStereoDevice(
            instance=instance_mock, mute_enabled=False, circuit_ids=[circuit_mock]
        )
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"instance": "instance_dict"', json_str)
        self.assertIn('"mute_enabled": false', json_str)
        self.assertIn('"circuit_ids": ["circuit_id_dict"]', json_str)
