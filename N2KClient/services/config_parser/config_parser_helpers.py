from typing import Any


def map_fields(self, source: dict[str, Any], target: object, field_map: dict) -> None:
    """
    Map fields from source dictionary to target object.
    """
    for attr, key in field_map.items():
        value = source.get(key)
        if value is not None:
            setattr(target, attr, value)


# Map enum fields from source dictionary to target object
def map_enum_fields(
    self, source: dict[str, Any], target: object, field_map: dict
) -> None:
    """
    Map enum fields from source dictionary to target object.
    """
    for attr, (key, enum_cls) in field_map.items():
        value = source.get(key)
        if value is not None:
            setattr(target, attr, enum_cls(value))


# Map list fields from source dictionary to target object
def map_list_fields(
    self, source: dict[str, Any], target: object, field_map: dict
) -> None:
    """
    Map list fields from source dictionary to target object, using a parsing function for each item.
    field_map: {attr_name: (json_key, parse_func)}
    """
    for attr, (key, parse_func) in field_map.items():
        value = source.get(key)
        if value is not None:
            setattr(target, attr, [parse_func(item) for item in value])
