from typing import Optional
from .config_item import ConfigItem
from .instance import Instance
from .data_id import DataId

from ..common_enums import SwitchType


class MonitoringDevice(ConfigItem):
    instance: Instance
    circuit_id: Optional[DataId]
    switch_type: SwitchType
    circuit_name: Optional[str]
    address: int
