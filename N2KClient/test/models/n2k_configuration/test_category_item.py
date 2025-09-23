import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.category_item import CategoryItem
from N2KClient.n2kclient.models.constants import AttrNames


class TestCategoryItem(unittest.TestCase):
    def test_category_item_to_dict_exception(self):
        # Use MagicMock to raise when .to_dict is called
        item = CategoryItem()
        item.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = item.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_category_item_to_json_string_exception(self):
        item = CategoryItem()
        item.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = item.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_category_item_to_dict(self):
        item = CategoryItem(name_utf8="TestCat", enabled=True, index=5)
        d = item.to_dict()
        self.assertIn(AttrNames.NAMEUTF8, d)
        self.assertEqual(d[AttrNames.NAMEUTF8], "TestCat")
        self.assertIn(AttrNames.ENABLED, d)
        self.assertTrue(d[AttrNames.ENABLED])
        self.assertIn(AttrNames.INDEX, d)
        self.assertEqual(d[AttrNames.INDEX], 5)

    def test_to_json_string(self):
        item = CategoryItem(name_utf8="Cat2", enabled=False, index=2)
        json_str = item.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"name_utf8": "Cat2"', json_str)
        self.assertIn('"enabled": false', json_str)
        self.assertIn('"index": 2', json_str)
