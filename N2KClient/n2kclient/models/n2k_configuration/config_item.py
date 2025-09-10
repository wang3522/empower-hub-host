import json
from ..constants import AttrNames


class ConfigItem:
    id: int
    name_utf8: str

    def __init__(self, id=0, name_utf8=""):
        self.id = id
        self.name_utf8 = name_utf8

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.ID: self.id,
                AttrNames.NAMEUTF8: self.name_utf8,
            }
        except Exception as e:
            print(f"Error serializing ConfigItem to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing ConfigItem to JSON: {e}")
            return "{}"
