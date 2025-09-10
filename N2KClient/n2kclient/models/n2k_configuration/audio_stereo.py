import json
from .config_item import ConfigItem
from .instance import Instance
from .data_id import DataId
from ..constants import AttrNames


class AudioStereoDevice(ConfigItem):
    instance: Instance
    mute_enabled: bool
    circuit_ids: list

    def __init__(self, instance=None, mute_enabled=False, circuit_ids=None):
        self.instance = instance if instance is not None else Instance()
        self.mute_enabled = mute_enabled
        self.circuit_ids = circuit_ids if circuit_ids is not None else []

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.INSTANCE: self.instance.to_dict(),
                AttrNames.MUTE_ENABLED: self.mute_enabled,
                AttrNames.CIRCUIT_IDS: [
                    circuit_id.to_dict() for circuit_id in self.circuit_ids
                ],
            }
        except Exception as e:
            print(f"Error serializing AudioStereoDevice to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing AudioStereoDevice to JSON: {e}")
            return "{}"
