import json
from ..constants import AttrNames


class Instance:
    enabled: bool
    instance: int

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
