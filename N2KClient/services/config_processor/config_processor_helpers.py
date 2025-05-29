from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState
from N2KClient.models.n2k_configuration.n2k_configuation import N2kConfiguration
from N2KClient.models.n2k_configuration.category_item import CategoryItem
from N2KClient.models.n2k_configuration.ui_relationship_msg import (
    ItemType,
    UiRelationShipMsg,
    RelationshipType,
)
from N2KClient.models.n2k_configuration.ac_meter import ACMeter
from N2KClient.models.common_enums import ThingType
from N2KClient.models.empower_system.link import Link
from N2KClient.models.constants import Constants
from N2KClient.models.n2k_configuration.circuit import Circuit


def get_category_list(
    item_type: ItemType,
    primary_id: int,
    config: N2kConfiguration,
) -> list[CategoryItem]:
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


def get_associated_circuit(
    item_type: ItemType,
    primary_id: int,
    config: N2kConfiguration,
):
    association_relationship = next(
        (
            rel
            for rel in config.ui_relationships
            if rel.primary_type == item_type
            and rel.secondary_type == ItemType.Circuit
            and rel.primary_id == primary_id
            and rel.secondary_id is not None
        ),
        None,
    )

    if association_relationship is not None:
        hidden_circuit = next(
            (
                circuit
                for id, circuit in config.hidden_circuit.items()
                if id == association_relationship.secondary_id
            ),
            None,
        )
        if hidden_circuit is not None:
            associated_circuit = next(
                (
                    circuit
                    for id, circuit in config.circuit.items()
                    if id == hidden_circuit.control_id
                ),
                None,
            )
            return associated_circuit
    return None


def get_primary_dc_meter(id: int, config: N2kConfiguration):
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
    link = Link(
        id=f"{link_thing_type.value}.{linked_id}",
        tags=[
            f"{Constants.empower}:{primary_type.value}.{Constants.link}.{link_thing_type.value}"
        ],
    )
    return link


def is_in_category(categories: list[CategoryItem], category_name: str) -> bool:
    return (
        next(
            (
                cat
                for cat in categories
                if cat.name_utf8 == category_name and cat.enabled == True
            ),
            None,
        )
        is not None
    )


def get_child_circuits(id: int, config: N2kConfiguration) -> list[Circuit]:

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
