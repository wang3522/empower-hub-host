import json
from .config_item import ConfigItem
from .instance import Instance
from .data_id import DataId
from ..constants import AttrNames


class AudioStereoDevice(ConfigItem):
    instance: Instance
    mute_enabled: bool
    circuit_ids: list[DataId]

    def to_dict(self) -> dict[str, str]:
        return {
            **super().to_dict(),
            AttrNames.INSTANCE: self.instance.to_dict(),
            AttrNames.MUTE_ENABLED: self.mute_enabled,
            AttrNames.CIRCUIT_IDS: [
                circuit_id.to_dict() for circuit_id in self.circuit_ids
            ],
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
