import json
from ..constants import AttrNames


class DataId:
    enabled: bool
    id: int

    def __init__(self, enabled=False, id=0):
        self.enabled = enabled
        self.id = id

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.ENABLED: self.enabled,
                AttrNames.ID: self.id,
            }
        except Exception as e:
            print(f"Error serializing DataId to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing DataId to JSON: {e}")
            return "{}"
