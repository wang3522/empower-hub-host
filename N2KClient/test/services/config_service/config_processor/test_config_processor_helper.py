import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.common_enums import ThingType
from N2KClient.n2kclient.models.n2k_configuration.ui_relationship_msg import (
    ItemType,
    RelationshipType,
    UiRelationShipMsg,
)
from N2KClient.n2kclient.services.config_service.config_processor.config_processor_helpers import (
    get_category_list,
    get_primary_dc_meter,
    get_fallback_dc_meter,
    get_ac_meter_associated_bls,
    get_circuit_associated_bls,
    create_link,
    get_child_circuits,
    get_associated_tank,
)


class TestConfigProcessorHelper(unittest.TestCase):
    def test_get_category_list(self):
        config = MagicMock(
            category=[MagicMock(index=3, name_utf8="Test Category")],
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.Category,
                    secondary_id=8,
                )
            ],
        )
        item_type = ItemType.DcMeter
        primary_id = 1
        categories = get_category_list(item_type, primary_id, config)
        self.assertEqual(len(categories), 1)

    def test_get_category_list_not_ui_relationship_msg(self):
        config = MagicMock(
            category=[MagicMock(index=3, name_utf8="Test Category")],
            ui_relationships=[
                MagicMock(
                    primary_id=1,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.Category,
                    secondary_id=8,
                )
            ],
        )
        item_type = ItemType.DcMeter
        primary_id = 1
        categories = get_category_list(item_type, primary_id, config)
        self.assertEqual(len(categories), 0)

    def test_get_category_list_no_index(self):
        config = MagicMock(
            category=[MagicMock(name_utf8="Test Category")],
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.Category,
                    secondary_id=8,
                )
            ],
        )
        item_type = ItemType.DcMeter
        primary_id = 1
        categories = get_category_list(item_type, primary_id, config)
        self.assertEqual(len(categories), 0)

    def test_get_category_list_not_is_in_category(self):
        config = MagicMock(
            category=[MagicMock(index=12345123, name_utf8="Test Category")],
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.Category,
                    secondary_id=8,
                )
            ],
        )
        item_type = ItemType.DcMeter
        primary_id = 1
        categories = get_category_list(item_type, primary_id, config)
        self.assertEqual(len(categories), 0)

    def test_primary_dc_meter(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.DcMeter,
                    relationship_type=RelationshipType.Duplicates,
                )
            ],
            dc={1: MagicMock(id=1), 2: MagicMock(id=2)},
        )
        primary_dc = get_primary_dc_meter(2, config)
        self.assertIsNotNone(primary_dc)
        self.assertEqual(primary_dc.id, 1)

    def test_primary_dc_meter_relationship_not_found(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=3,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.DcMeter,
                    relationship_type=RelationshipType.Duplicates,
                )
            ],
            dc={1: MagicMock(id=1), 2: MagicMock(id=2)},
        )
        primary_dc = get_primary_dc_meter(2, config)
        self.assertIsNone(primary_dc)

    def test_primary_dc_meter_dc_none(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.DcMeter,
                    relationship_type=RelationshipType.Duplicates,
                )
            ],
        )
        primary_dc = get_primary_dc_meter(2, config)
        self.assertIsNone(primary_dc)

    def test_fallback_dc_meter(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.DcMeter,
                    relationship_type=RelationshipType.Duplicates,
                )
            ],
            dc={1: MagicMock(id=1), 2: MagicMock(id=2)},
        )
        fallback_dc = get_fallback_dc_meter(1, config)
        self.assertIsNotNone(fallback_dc)
        self.assertEqual(fallback_dc.id, 2)

    def test_fallback_dc_meter_no_relationship(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=33,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.DcMeter,
                    relationship_type=RelationshipType.Duplicates,
                )
            ],
            dc={1: MagicMock(id=1), 2: MagicMock(id=2)},
        )
        fallback_dc = get_fallback_dc_meter(1, config)
        self.assertIsNone(fallback_dc)

    def test_fallback_dc_meter_dc_none(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.DcMeter,
                    relationship_type=RelationshipType.Duplicates,
                )
            ],
            dc={},
        )
        fallback_dc = get_fallback_dc_meter(1, config)
        self.assertIsNone(fallback_dc)

    def test_get_ac_meter_associated_bls(self):
        config = MagicMock(
            binary_logic_state={1: MagicMock(address=1234, id=2)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    secondary_config_address=1234,
                    primary_type=ItemType.AcMeter,
                    secondary_type=ItemType.BinaryLogicState,
                )
            ],
        )
        ac_meter = MagicMock(id=1, line={1: MagicMock(id=1), 2: MagicMock(id=2)})
        associated_bls = get_ac_meter_associated_bls(ac_meter, config)
        self.assertEqual(associated_bls.address, 1234)

    def test_get_ac_meter_associated_bls_none(self):
        config = MagicMock(
            binary_logic_state={1: MagicMock(address=1234, id=2)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    secondary_config_address=1234,
                    primary_type=ItemType.DcMeter,
                    secondary_type=ItemType.BinaryLogicState,
                )
            ],
        )
        ac_meter = MagicMock(id=1, line={1: MagicMock(id=1), 2: MagicMock(id=2)})
        associated_bls = get_ac_meter_associated_bls(ac_meter, config)
        self.assertIsNone(associated_bls)

    def test_get_circuit_associated_bls(self):
        config = MagicMock(
            binary_logic_state={1: MagicMock(address=1234, id=2)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_config_address=444,
                    secondary_config_address=1234,
                    primary_type=ItemType.Circuit,
                    secondary_type=ItemType.BinaryLogicState,
                )
            ],
        )
        circuit = MagicMock(id=1, control_id=444)
        associated_bls = get_circuit_associated_bls(circuit, config)
        self.assertEqual(associated_bls.address, 1234)

    def test_get_circuit_associated_bls_no_rel(self):
        config = MagicMock(
            binary_logic_state={1: MagicMock(address=1234, id=2)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_config_address=444,
                    secondary_config_address=1234,
                    primary_type=ItemType.Circuit,
                    secondary_type=ItemType.BinaryLogicState,
                )
            ],
        )
        circuit = MagicMock(id=1, control_id=1)
        associated_bls = get_circuit_associated_bls(circuit, config)
        self.assertIsNone(associated_bls)

    def test_get_circuit_associated_bls_no_bls(self):
        config = MagicMock(
            binary_logic_state={1: MagicMock(address=1111, id=2)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_config_address=444,
                    secondary_config_address=1234,
                    primary_type=ItemType.Circuit,
                    secondary_type=ItemType.BinaryLogicState,
                )
            ],
        )
        circuit = MagicMock(id=1, control_id=444)
        associated_bls = get_circuit_associated_bls(circuit, config)
        self.assertIsNone(associated_bls)

    def test_create_link(self):
        link_thing_type = ThingType.PUMP
        primary_type = ThingType.WATER_TANK
        linked_id = 123
        link = create_link(link_thing_type, primary_type, linked_id)
        self.assertEqual(link.id, "pump.123")
        self.assertEqual(link.tags[0], "empower:waterTank.link.pump")

    def test_get_child_circuits(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.Circuit,
                    secondary_type=ItemType.Circuit,
                    relationship_type=RelationshipType.Normal,
                )
            ],
            hidden_circuit={
                2: MagicMock(id=MagicMock(value=2), control_id=444),
                3: MagicMock(id=3),
            },
            circuit={1: MagicMock(id=MagicMock(value=555), control_id=444)},
        )
        child_circuits = get_child_circuits(1, config)
        self.assertEqual(len(child_circuits), 1)
        self.assertEqual(child_circuits[0].id.value, 555)

    def test_get_child_circuits_no_hidden_circuit(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.Circuit,
                    secondary_type=ItemType.Circuit,
                    relationship_type=RelationshipType.Normal,
                )
            ],
            hidden_circuit={2: MagicMock(id=MagicMock(value=1234), control_id=444)},
            circuit={1: MagicMock(id=MagicMock(value=555), control_id=444)},
        )
        child_circuits = get_child_circuits(1, config)
        self.assertEqual(len(child_circuits), 0)

    def test_get_child_circuits_no_circuit_match(self):
        config = MagicMock(
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.Circuit,
                    secondary_type=ItemType.Circuit,
                    relationship_type=RelationshipType.Normal,
                )
            ],
            hidden_circuit={
                2: MagicMock(id=MagicMock(value=2), control_id=444),
            },
            circuit={1: MagicMock(id=MagicMock(value=555), control_id=1234)},
        )
        child_circuits = get_child_circuits(1, config)
        self.assertEqual(len(child_circuits), 0)

    def test_get_associated_tank(self):
        config = MagicMock(
            tank={1: MagicMock(id=1)},
            hidden_circuit={2: MagicMock(id=MagicMock(value=2), control_id=1)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.FluidLevel,
                    secondary_type=ItemType.Circuit,
                )
            ],
        )
        associated_tank = get_associated_tank(1, config)
        self.assertIsNotNone(associated_tank)
        self.assertEqual(associated_tank.id, 1)

    def test_get_associated_tank_no_hidden_circuit(self):
        config = MagicMock(
            tank={1: MagicMock(id=1)},
            hidden_circuit={2: MagicMock(id=MagicMock(value=2), control_id=123)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.FluidLevel,
                    secondary_type=ItemType.Circuit,
                )
            ],
        )
        associated_tank = get_associated_tank(1, config)
        self.assertIsNone(associated_tank)

    def test_get_associated_tank_no_rel(self):
        config = MagicMock(
            tank={1: MagicMock(id=1)},
            hidden_circuit={2: MagicMock(id=MagicMock(value=2), control_id=1)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2222,
                    primary_type=ItemType.FluidLevel,
                    secondary_type=ItemType.Circuit,
                )
            ],
        )
        associated_tank = get_associated_tank(1, config)
        self.assertIsNone(associated_tank)

    def test_get_associated_tank_no_tank(self):
        config = MagicMock(
            tank={1: MagicMock(id=1234)},
            hidden_circuit={2: MagicMock(id=MagicMock(value=2), control_id=1)},
            ui_relationships=[
                UiRelationShipMsg(
                    primary_id=1,
                    secondary_id=2,
                    primary_type=ItemType.FluidLevel,
                    secondary_type=ItemType.Circuit,
                )
            ],
        )
        associated_tank = get_associated_tank(1, config)
        self.assertIsNone(associated_tank)
