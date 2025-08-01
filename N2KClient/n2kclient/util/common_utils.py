import logging
from typing import Any
from ..models.n2k_configuration.n2k_configuation import N2kConfiguration
from ..models.n2k_configuration.ui_relationship_msg import ItemType
from ..models.n2k_configuration.inverter_charger import InverterChargerDevice
from ..models.n2k_configuration.category_item import CategoryItem


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


def calculate_inverter_charger_instance(inverter_charger: InverterChargerDevice):
    """
    Given an inveter/charger, calculate its instance number from the instances
    of the inverter and charger separately.
    """

    return (
        inverter_charger.inverter_instance.instance << 8
        | inverter_charger.charger_instance.instance
    )


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


def map_fields(source: dict[str, Any], target: object, field_map: dict) -> None:
    """
    Map fields from source dictionary to target object.
    """
    for attr, key in field_map.items():
        value = source.get(key)
        if value is not None:
            setattr(target, attr, value)


# Map enum fields from source dictionary to target object
def map_enum_fields(
    logger: logging.Logger, source: dict[str, Any], target: object, field_map: dict
) -> None:
    """
    Map enum fields from source dictionary to target object.
    Skips None, empty string, and invalid enum values to avoid ValueError.
    """
    for attr, (key, enum_cls) in field_map.items():
        value = source.get(key)
        if value not in (None, ""):
            try:
                setattr(target, attr, enum_cls(value))
            except ValueError:
                try:
                    # Try converting string to int if possible
                    setattr(target, attr, enum_cls(int(value)))
                except Exception:
                    logger.warning(
                        f"Invalid value '{value}' for enum '{enum_cls.__name__}' in field '{key}'. Skipping."
                    )


# Map list fields from source dictionary to target object
def map_list_fields(source: dict[str, Any], target: object, field_map: dict) -> None:
    """
    Map list fields from source dictionary to target object, using a parsing function for each item.
    field_map: {attr_name: (json_key, parse_func)}
    """
    for attr, (key, parse_func) in field_map.items():
        value = source.get(key)
        if value is not None:
            setattr(target, attr, [parse_func(item) for item in value])
