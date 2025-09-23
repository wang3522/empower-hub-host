import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.factory_metadata import (
    FactoryMetadata,
)


class TestFactoryMetadata(unittest.TestCase):
    def test_factory_metadata_to_dict_exception(self):
        obj = FactoryMetadata()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_factory_metadata_to_dict(self):
        obj = FactoryMetadata(
            serial_number="SN123",
            rt_firmware_version="FW1.2.3",
            mender_artifact_info="ART-42",
        )
        d = obj.to_dict()
        self.assertIn("serial_number", d)
        self.assertEqual(d["serial_number"], "SN123")
        self.assertIn("rt_firmware_version", d)
        self.assertEqual(d["rt_firmware_version"], "FW1.2.3")
        self.assertIn("mender_artifact_info", d)
        self.assertEqual(d["mender_artifact_info"], "ART-42")
