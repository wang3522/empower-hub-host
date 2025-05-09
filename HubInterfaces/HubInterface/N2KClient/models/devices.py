from typing import Any
from models.common_enums import DeviceType
from models.constants import Constants


class N2kDevice:
    type: DeviceType
    channels: dict[str, Any]

    def __init__(self, type: DeviceType):
        self.type = type
        self.channels = {}

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type.value, "channels": self.channels}
