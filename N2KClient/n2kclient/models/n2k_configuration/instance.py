import json
from ..constants import AttrNames


class Instance:
    enabled: bool
    instance: int

    def __init__(self, enabled=False, instance=0):
        self.enabled = enabled
        self.instance = instance

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.ENABLED: self.enabled,
                AttrNames.INSTANCE: self.instance,
            }
        except Exception as e:
            print(f"Error serializing Instance to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Instance to JSON: {e}")
            return "{}"

    def __eq__(self, other):
        if not isinstance(other, Instance):
            return False
        return self.to_dict() == other.to_dict()
