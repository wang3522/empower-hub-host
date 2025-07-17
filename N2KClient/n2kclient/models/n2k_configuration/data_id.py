import json
from ..constants import AttrNames


class DataId:
    enabled: bool
    id: int

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
