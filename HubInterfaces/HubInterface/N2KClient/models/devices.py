import json
from typing import Any
from N2KClient.models.common_enums import N2kDeviceType
from N2KClient.models.constants import Constants


class N2kDevice:
    type: N2kDeviceType
    channels: dict[str, Any]

    def __init__(self, type: N2kDeviceType):
        self.type = type
        self.channels = {}

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type.value, "channels": self.channels}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
