from typing import Any
import logging
from ...models.constants import JsonKeys
from ...models.n2k_configuration.binary_logic_state import BinaryLogicState
from ...models.n2k_configuration.ui_relationship_msg import (
    UiRelationShipMsg,
    ItemType,
)


def get_device_instance_value(
    instance_json: dict[str, dict[str, Any]],
) -> str | None:
    """
    Get the device instance value from the JSON object.
    """
    device_instace = instance_json.get(JsonKeys.INSTANCE, {})
    device_instance_enabled = device_instace.get(JsonKeys.ENABLED, False)
    device_instance_value = device_instace.get(JsonKeys.INSTANCE, None)
    if device_instance_enabled and device_instance_value is not None:
        return device_instance_value
    return None


def get_bls_alarm_channel(
    bls: BinaryLogicState, ui_relationships: list[UiRelationShipMsg]
):
    """
    Given an bls message and configuration id map build a list of
    Component References for any give alarm, to associate alarm to things.
    """

    primary_relationship = next(
        (
            rel
            for rel in ui_relationships
            if rel.primary_type == ItemType.BinaryLogicState
            and rel.primary_id == bls.address
        ),
        None,
    )

    if primary_relationship:
        return (primary_relationship.primary_config_address & 0xFF00) + (
            primary_relationship.primary_channel_index & 0x0FF
        )

    secondary_relationship = next(
        (
            rel
            for rel in ui_relationships
            if rel.secondary_type == ItemType.BinaryLogicState
            and rel.secondary_config_address == bls.address
        ),
        None,
    )

    if secondary_relationship:
        return (secondary_relationship.secondary_config_address & 0xFF00) + (
            secondary_relationship.secondary_channel_index & 0xFF
        )
    return None
