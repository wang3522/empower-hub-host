import json
from .config_item import ConfigItem
from .instance import Instance
from ..constants import AttrNames


class GNSSDevice(ConfigItem):
    instance: Instance
    is_external: bool

    def to_dict(self) -> dict[str, str]:
        return {
            **super().to_dict(),
            AttrNames.INSTANCE: self.instance.to_dict(),
            AttrNames.IS_EXTERNAL: self.is_external,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
