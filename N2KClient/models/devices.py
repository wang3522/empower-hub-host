import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Sequence, Tuple
from N2KClient.models.common_enums import N2kDeviceType


class ChannelSource(NamedTuple):
    label: str  # semantic label for the value, e.g. 'circuit_level', 'inverter_enable'
    device_key: str
    channel_key: str


@dataclass
class MobileChannelMapping:
    mobile_key: str
    channel_sources: List[ChannelSource]  # list of sources with labels
    transform: Callable[[Dict[str, Any], Dict[str, float]], Any]  # now receives values and last_updated


class N2kDevice:
    type: N2kDeviceType
    channels: Dict[str, Any]
    channel_last_updated: Dict[str, float]

    def __init__(self, type: N2kDeviceType):
        self.type = type
        self.channels = {}
        self.channel_last_updated = {}

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.value, "channels": self.channels}

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())


class N2kDevices:
    def __init__(self):
        self.devices: Dict[str, N2kDevice] = {}
        self.mobile_channel_mappings: List[MobileChannelMapping] = []

    def add(self, key: str, device: N2kDevice):
        self.devices[key] = device

    def add_mobile_channel_mapping(self, mapping: MobileChannelMapping):
        self.mobile_channel_mappings.append(mapping)

    def aggregate_mobile_channels(self) -> Dict[str, Any]:
        result = {}
        for mapping in self.mobile_channel_mappings:
            values = {}
            last_updated = {}
            for source in mapping.channel_sources:
                device = self.devices.get(source.device_key)
                if device and source.channel_key in device.channels:
                    values[source.label] = device.channels[source.channel_key]
                    last_updated[source.label] = device.channel_last_updated.get(source.channel_key, 0)
            result[mapping.mobile_key] = mapping.transform(values, last_updated)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "devices": {key: device.to_dict() for key, device in self.devices.items()},
        }
