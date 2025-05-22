from typing import Any
import logging
from N2KClient.models.constants import JsonKeys


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
                logger.warning(
                    f"Invalid value '{value}' for enum '{enum_cls.__name__}' in field '{key}'. Skipping."
                )
                pass


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


def get_device_instance_value(
    instance_json: dict[str, dict[str, Any]],
) -> str | None:
    """
    Get the device instance value from the JSON object.
    """
    device_instace = instance_json.get(JsonKeys.INSTANCE, {})
    device_instance_enabled = device_instace.get(JsonKeys.ENABLED, False)
    device_instance_value = device_instace.get(JsonKeys.INSTANCE_, None)
    if device_instance_enabled and device_instance_value is not None:
        return device_instance_value
    return None
