from .config_item import ConfigItem
from .instance import Instance


class GNSSDevice(ConfigItem):
    instance: Instance
    is_external: bool
