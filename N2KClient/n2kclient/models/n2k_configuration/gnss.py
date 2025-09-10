import json
from .config_item import ConfigItem
from .instance import Instance
from ..constants import AttrNames


class GNSSDevice(ConfigItem):
    instance: Instance
    is_external: bool

    def __init__(self, instance=None, is_external=False):
        self.instance = instance if instance is not None else Instance()
        self.is_external = is_external

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.INSTANCE: self.instance.to_dict(),
                AttrNames.IS_EXTERNAL: self.is_external,
            }
        except Exception as e:
            print(f"Error serializing GNSSDevice to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing GNSSDevice to JSON: {e}")
            return "{}"
