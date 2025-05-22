import json
from .config_item import ConfigItem
from ..constants import AttrNames


class BinaryLogicStates(ConfigItem):
    address: int

    def to_dict(self) -> dict[str, str]:
        return {
            **super().to_dict(),
            AttrNames.ADDRESS: self.address,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
