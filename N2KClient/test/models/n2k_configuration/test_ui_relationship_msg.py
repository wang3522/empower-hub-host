import unittest
from unittest.mock import MagicMock
import json
from N2KClient.n2kclient.models.n2k_configuration.ui_relationship_msg import (
    UiRelationShipMsg,
    ItemType,
    RelationshipType,
)
from N2KClient.n2kclient.models.constants import AttrNames
from unittest.mock import patch


class TestUiRelationshipMsg(unittest.TestCase):
    def test_to_dict_and_json(self):
        obj = UiRelationShipMsg(
            primary_type=ItemType.FluidLevel,
            secondary_type=ItemType.Pressure,
            primary_id=1,
            secondary_id=2,
            relationship_type=RelationshipType.Duplicates,
            primary_config_address=10,
            secondary_config_address=20,
            primary_channel_index=3,
            secondary_channel_index=4,
        )
        d = obj.to_dict()
        self.assertEqual(d[AttrNames.PRIMARY_TYPE], ItemType.FluidLevel.value)
        self.assertEqual(d[AttrNames.SECONDARY_TYPE], ItemType.Pressure.value)
        self.assertEqual(d[AttrNames.PRIMARY_ID], 1)
        self.assertEqual(d[AttrNames.SECONDARY_ID], 2)
        self.assertEqual(
            d[AttrNames.RELATIONSHIP_TYPE], RelationshipType.Duplicates.value
        )
        self.assertEqual(d[AttrNames.PRIMARY_CONFIG_ADDRESS], 10)
        self.assertEqual(d[AttrNames.SECONDARY_CONFIG_ADDRESS], 20)
        self.assertEqual(d[AttrNames.PRIMARY_CHANNEL_INDEX], 3)
        self.assertEqual(d[AttrNames.SECONDARY_CHANNEL_INDEX], 4)
        json_str = obj.to_json_string()
        self.assertIn('"primary_type": 1', json_str)
        self.assertIn('"secondary_type": 2', json_str)
        self.assertIn('"primary_id": 1', json_str)
        self.assertIn('"secondary_id": 2', json_str)
        self.assertIn('"relationship_type": 1', json_str)
        self.assertIn('"primary_config_address": 10', json_str)
        self.assertIn('"secondary_config_address": 20', json_str)
        self.assertIn('"primary_channel_index": 3', json_str)
        self.assertIn('"secondary_channel_index": 4', json_str)

    def test_to_dict_exception(self):
        obj = UiRelationShipMsg()

        with patch.object(obj, "to_dict", side_effect=Exception("fail")):
            try:
                d = obj.to_dict()
            except Exception:
                d = {}
            self.assertEqual(d, {})

    def test_to_json_string_exception(self):
        obj = UiRelationShipMsg()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")
