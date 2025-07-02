import json
from typing import Any
from .common_enums import N2kDeviceType


class N2kDevice:
    type: N2kDeviceType
    channels: dict[str, Any]

    def __init__(self, type: N2kDeviceType):
        self.type = type
        self.channels = {}

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type.value, "channels": self.channels}

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
