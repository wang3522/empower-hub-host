import json
from ..constants import AttrNames


class ValueU32:
    valid: bool
    value: int

    def __init__(self, valid=False, value=0):
        self.valid = valid
        self.value = value

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.VALID: self.valid,
                AttrNames.VALUE: self.value,
            }
        except Exception as e:
            print(f"Error serializing ValueU32 to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing DataId to JSON: {e}")
            return "{}"
