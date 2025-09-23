import unittest
from N2KClient.n2kclient.models.n2k_configuration.config_metadata import ConfigMetadata
from N2KClient.n2kclient.models.constants import AttrNames


class TestConfigMetadata(unittest.TestCase):
    def test_config_metadata_to_dict(self):
        obj = ConfigMetadata(id=1, name="meta", version=2, config_file_version=3)
        d = obj.to_dict()
        self.assertIn(AttrNames.ID, d)
        self.assertEqual(d[AttrNames.ID], "1")
        self.assertIn(AttrNames.NAME, d)
        self.assertEqual(d[AttrNames.NAME], "meta")
        self.assertIn(AttrNames.VERSION, d)
        self.assertEqual(d[AttrNames.VERSION], "2")
        self.assertIn(AttrNames.CONFIG_FILE_VERSION, d)
        self.assertEqual(d[AttrNames.CONFIG_FILE_VERSION], "3")

    def test_config_metadata_eq(self):
        obj1 = ConfigMetadata(id=1, name="meta", version=2, config_file_version=3)
        obj2 = ConfigMetadata(id=1, name="meta", version=2, config_file_version=3)
        obj3 = ConfigMetadata(id=2, name="meta2", version=3, config_file_version=4)
        self.assertEqual(obj1, obj2)
        self.assertNotEqual(obj1, obj3)
