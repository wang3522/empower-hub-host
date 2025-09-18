import unittest
from N2KClient.n2kclient.services.config_service.config_parser.config_parser_helpers import (
    get_device_instance_value,
    get_bls_alarm_channel,
)
from N2KClient.n2kclient.models.n2k_configuration.binary_logic_state import (
    BinaryLogicState,
)
from N2KClient.n2kclient.models.n2k_configuration.ui_relationship_msg import (
    UiRelationShipMsg,
    ItemType,
)


class TestConfigParserHelpers(unittest.TestCase):
    """
    Unit tests for ConfigParser helpers
    """

    def test_get_device_instance_value(self):
        mock_instance = {"Instance": {"Instance": "test_instance", "Enabled": True}}
        res = get_device_instance_value(mock_instance)
        self.assertEqual(res, "test_instance")

    def test_get_device_instance_not_enabled(self):
        mock_instance = {"Instance": {"Instance": "test_instance", "Enabled": False}}
        res = get_device_instance_value(mock_instance)
        self.assertIsNone(res)

    def test_get_device_instance_none(self):
        mock_instance = {"Instance": {"Enabled": True}}
        res = get_device_instance_value(mock_instance)
        self.assertIsNone(res)

    def test_get_device_instance_all_none(self):
        mock_instance = {"Instance": None}
        res = get_device_instance_value(mock_instance)
        self.assertIsNone(res)

    def test_get_bls_alarm_channel_primary(self):

        bls = BinaryLogicState(address=0x1234)
        ui_relationships = [
            UiRelationShipMsg(
                primary_type=ItemType.BinaryLogicState,
                primary_id=0x1234,
                primary_config_address=0x1200,
                primary_channel_index=0x34,
                secondary_type=ItemType.AcMeter,
                secondary_id=0,
                secondary_config_address=0,
                secondary_channel_index=0,
            )
        ]
        res = get_bls_alarm_channel(bls, ui_relationships)
        self.assertEqual(res, (0x1200 & 0xFF00) + (0x34 & 0x0FF))

    def test_get_bls_alarm_channel_secondary(self):
        bls = BinaryLogicState(address=0x1234)
        ui_relationships = [
            UiRelationShipMsg(
                primary_type=ItemType.AcMeter,
                primary_id=0,
                primary_config_address=0,
                primary_channel_index=0,
                secondary_type=ItemType.BinaryLogicState,
                secondary_id=0x1234,
                secondary_config_address=0x1234,
                secondary_channel_index=0x34,
            )
        ]
        res = get_bls_alarm_channel(bls, ui_relationships)
        self.assertEqual(res, (0x1234 & 0xFF00) + (0x34 & 0x0FF))

    def test_get_bls_alarm_channel_none(self):
        bls = BinaryLogicState(address=0x5555)
        ui_relationships = [
            UiRelationShipMsg(
                primary_type=ItemType.AcMeter,
                primary_id=0,
                primary_config_address=0,
                primary_channel_index=0,
                secondary_type=ItemType.BinaryLogicState,
                secondary_id=0x1234,
                secondary_config_address=0x1234,
                secondary_channel_index=0x34,
            )
        ]
        res = get_bls_alarm_channel(bls, ui_relationships)
        self.assertIsNone(res)
