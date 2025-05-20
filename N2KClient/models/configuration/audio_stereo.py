from .config_item import ConfigItem
from .instance import Instance
from .data_id import DataId


class AudioStereoDevice(ConfigItem):
    instance: Instance
    mute_enabled: bool
    circuit_ids: list[DataId]
