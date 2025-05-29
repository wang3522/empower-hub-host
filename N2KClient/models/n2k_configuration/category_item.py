from ..constants import AttrNames
import json


class CategoryItem:
    name_utf8: str
    enabled: bool
    index: int

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.NAMEUTF8: self.name_utf8,
                AttrNames.ENABLED: self.enabled,
                AttrNames.INDEX: self.index,
            }
        except Exception as e:
            print(f"Error serializing CategoryItem to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing CategoryItem to JSON: {e}")
            return "{}"
