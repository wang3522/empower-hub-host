import json
from ..constants import AttrNames


class SequentialName:
    name: str

    def __init__(self, name=""):
        self.name = name

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.NAME: self.name,
            }
        except Exception as e:
            print(f"Error serializing SequentialName to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing SequentialName to JSON: {e}")
            return "{}"
