import json
from .config_item import ConfigItem
from ..constants import AttrNames


class BinaryLogicState(ConfigItem):
    address: int

    def __init__(self, address=0):
        self.address = address

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.ADDRESS: self.address,
            }
        except Exception as e:
            print(f"Error serializing BinaryLogicStates to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing BinaryLogicStates to JSON: {e}")
            return "{}"
