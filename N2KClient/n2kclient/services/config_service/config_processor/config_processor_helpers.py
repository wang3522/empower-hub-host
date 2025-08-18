from ....models.n2k_configuration.n2k_configuation import N2kConfiguration
from ....models.n2k_configuration.category_item import CategoryItem
from ....models.n2k_configuration.ui_relationship_msg import (
    ItemType,
    UiRelationShipMsg,
    RelationshipType,
)
from ....models.n2k_configuration.ac_meter import ACMeter
from ....models.common_enums import ThingType
from ....models.empower_system.link import Link
from ....models.constants import Constants
from ....models.n2k_configuration.circuit import Circuit


def get_category_list(
    item_type: ItemType,
    primary_id: int,
    config: N2kConfiguration,
) -> list[CategoryItem]:
    """
    Get the list of categories associated with a component given it's item type and primary ID.
    Args:
        item_type: The type of the primary item (e.g., DcMeter, AcMeter, etc.)
        primary_id: The ID of the primary item
        config: The N2kConfiguration containing relationships and categories
    Returns:
        A list of CategoryItem objects associated with the primary item.
    """
    category_relationships = filter(
        lambda rel: rel.secondary_type == ItemType.Category,
        config.ui_relationships,
    )

    categories = []

    for rel in category_relationships:
        if not isinstance(rel, UiRelationShipMsg):
            continue

        category_id_map = rel.secondary_id

        if rel.primary_type == item_type and rel.primary_id == primary_id:
            for category in config.category:
                if category.index is None:
                    continue

                is_in_category = (
                    ((1 << category.index) & category_id_map) >> category.index
                ) == 1

                if is_in_category:
                    categories.append(category.name_utf8)

    return categories


def get_primary_dc_meter(id: int, config: N2kConfiguration):
    """
    Get the primary DC meter associated with a given ID. Case where the given dc ID is a fallback battery.
    This function checks for a relationship where the primary type is DcMeter and the secondary type is also DcMeter,
    indicating that the primary is a fallback for the secondary.
    Args:
        id: The ID of the secondary DC meter to find the primary for.
        config: The N2kConfiguration containing relationships and DC meters.
    Returns:
        The primary DC meter if found, None otherwise."""
    rel = next(
        (
            rel
            for rel in config.ui_relationships
            if rel.primary_type == ItemType.DcMeter
            and rel.secondary_type == ItemType.DcMeter
            and rel.relationship_type == RelationshipType.Duplicates
            and rel.secondary_id == id
        ),
        None,
    )
    if rel is not None:
        dc = next(
            (dc for dc in config.dc.values() if dc.id == rel.primary_id),
            None,
        )

        if dc is not None:
            return dc
    return None


def get_fallback_dc_meter(id: int, config: N2kConfiguration):
    """
    Get the fallback DC meter for a given ID. Case where the given dc ID is a primary battery.
    This function checks for a relationship where the primary type is DcMeter and the secondary type is also DcMeter,
    indicating that the primary is a fallback for the secondary.
    Args:
        id: The ID of the primary DC meter to find a fallback for.
        config: The N2kConfiguration containing relationships and DC meters.
    Returns:
        The fallback DC meter if found, None otherwise.
    """
    rel = next(
        (
            rel
            for rel in config.ui_relationships
            if rel.primary_type == ItemType.DcMeter
            and rel.secondary_type == ItemType.DcMeter
            and rel.relationship_type == RelationshipType.Duplicates
            and rel.primary_id == id
        ),
        None,
    )
    if rel is not None:
        dc = next(
            (dc for dc in config.dc.values() if dc.Id == rel.SecondaryId),
            None,
        )

        if dc is not None:
            return dc
    return None


def get_ac_meter_associated_bls(ac_meter: ACMeter, config: N2kConfiguration):
    """
    Get the BinaryLogicState associated with an AC meter.
    Args:
        ac_meter: The ACMeter configuration to find the associated BinaryLogicState for.
        config: The N2kConfiguration containing relationships and BinaryLogicStates.
    Returns:
        The associated BinaryLogicState if found, None otherwise.
    """
    for ac_line in ac_meter.line.values():
        for relationship in config.ui_relationships:
            if (
                relationship.secondary_type == ItemType.BinaryLogicState
                and relationship.primary_type == ItemType.AcMeter
            ):
                if relationship.primary_id == ac_line.id:
                    bls_address = relationship.secondary_config_address
                    bls = next(
                        (
                            bls
                            for _, bls in config.binary_logic_state.items()
                            if bls.address == bls_address
                        ),
                        None,
                    )
                    return bls
    return None


def get_circuit_associated_bls(circuit: Circuit, config: N2kConfiguration):
    """
    Get the BinaryLogicState associated with a circuit configuration.
    Args:
        circuit: The Circuit configuration to find the associated BinaryLogicState for.
        config: The N2kConfiguration containing relationships and BinaryLogicStates.
    Returns:
        The associated BinaryLogicState if found, None otherwise.
    """
    relationship = next(
        (
            relationship
            for relationship in config.ui_relationships
            if relationship.secondary_type == ItemType.BinaryLogicState
            and relationship.primary_type == ItemType.Circuit
            and relationship.primary_config_address == circuit.control_id
        ),
        None,
    )

    if relationship is not None:
        bls_address = relationship.secondary_config_address
        bls = next(
            (
                bls
                for _, bls in config.binary_logic_state.items()
                if bls.address == bls_address
            ),
            None,
        )
        return bls
    return None


def create_link(
    link_thing_type: ThingType,
    primary_type: ThingType,
    linked_id: int,
):
    """Create a Link object for the specified primary type and linked ID.
    Args:
        link_thing_type: The type of the link being created.
        primary_type: The primary type of the item being linked.
        linked_id: The ID of the item being linked.
    Returns:
        A Link object with the specified type and ID.
    """
    link = Link(
        id=f"{link_thing_type.value}.{linked_id}",
        tags=[
            f"{Constants.empower}:{primary_type.value}.{Constants.link}.{link_thing_type.value}"
        ],
    )
    return link


def get_child_circuits(id: int, config: N2kConfiguration) -> list[Circuit]:
    """
    Get the child circuits associated with a given circuit ID.
    Args:
        id: The ID of the parent circuit
        config: The N2kConfiguration containing relationships and circuits
    Returns:
        A list of child circuits associated with the parent circuit ID.
    """

    child_circuits = []

    for rel in config.ui_relationships:
        if (
            rel.primary_type == ItemType.Circuit
            and rel.secondary_type == ItemType.Circuit
            and rel.relationship_type == RelationshipType.Normal
            and rel.primary_id == id
        ):
            hidden_circuit = next(
                (
                    circuit
                    for circuit in config.hidden_circuit.values()
                    if circuit.id == rel.secondary_id
                ),
                None,
            )

            if hidden_circuit is not None:
                child_circuit = next(
                    (
                        circuit
                        for circuit in config.circuit.values()
                        if circuit.control_id == hidden_circuit.control_id
                    ),
                    None,
                )
                if child_circuit is not None:
                    child_circuits.append(child_circuit)
    return child_circuits


def get_associated_tank(id: int, config: N2kConfiguration):
    """
    Get the tank associated with a circuit (pump) by its ID.
    Args:
        id: The ID of the circuit
        config: The N2kConfiguration containing relationships and tanks
    Returns:
        The associated tank if found, None otherwise
    """
    hidden_circuit = next(
        (
            circuit
            for circuit in config.hidden_circuit.values()
            if circuit.control_id == id
        ),
        None,
    )

    if hidden_circuit is not None:
        tank_pump_relationship = next(
            (
                rel
                for rel in config.ui_relationships
                if rel.primary_type == ItemType.FluidLevel
                and rel.secondary_type == ItemType.Circuit
                and rel.secondary_id == hidden_circuit.id.value
            ),
            None,
        )

        if tank_pump_relationship is not None:
            tank = next(
                (
                    tank
                    for tank in config.tank.values()
                    if tank.id == tank_pump_relationship.primary_id
                ),
                None,
            )
            return tank
    return None
