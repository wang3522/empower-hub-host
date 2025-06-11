import json
import time
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
    transform: Callable[
        [Dict[str, Any], Dict[str, float]], Any
    ]  # now receives values and last_updated


class N2kDevice:
    type: N2kDeviceType
    channels: Dict[str, Any]
    mobile_channels: Dict
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
        self._cached_mobile_channels: Dict[str, Any] = {}
        # Track which mappings use which sources for quick lookup during updates
        self._source_to_mappings: Dict[str, List[MobileChannelMapping]] = {}

    def add(self, key: str, device: N2kDevice):
        self.devices[key] = device

    def add_mobile_channel_mapping(self, mapping: MobileChannelMapping):
        # Index this mapping by its sources for quick lookup during updates
        for source in mapping.channel_sources:
            source_key = f"{source.device_key}.{source.channel_key}"
            if source_key not in self._source_to_mappings:
                self._source_to_mappings[source_key] = []
            self._source_to_mappings[source_key].append(mapping)

        # Apply the transform for this mapping
        self._update_mapping(mapping)

    def update_channel(
        self, device_key: str, channel_key: str, value: Any, timestamp: float = None
    ):
        """
        Update a channel value and immediately update any affected mappings.
        This method should be called when a channel value changes.

        Args:
            device_key: The key of the device to update
            channel_key: The key of the channel to update
            value: The new value for the channel
            timestamp: Optional timestamp for the update, defaults to current time
        """
        # Handle missing device
        if device_key not in self.devices:
            return

        device = self.devices[device_key]

        # Skip update if value hasn't changed (optimization)
        if channel_key in device.channels and device.channels[channel_key] == value:
            return

        # Update the channel
        device.channels[channel_key] = value
        device.channel_last_updated[channel_key] = timestamp or time.time()

        # Update any mappings that use this channel
        source_key = f"{device_key}.{channel_key}"
        if source_key in self._source_to_mappings:
            for mapping in self._source_to_mappings[source_key]:
                self._update_mapping(mapping)

    def _update_mapping(self, mapping: MobileChannelMapping):
        """Apply transform for a mapping and cache the result"""
        values = {}
        last_updated = {}

        # Collect values from all sources
        for source in mapping.channel_sources:
            device = self.devices.get(source.device_key)
            if device and source.channel_key in device.channels:
                values[source.label] = device.channels[source.channel_key]
                last_updated[source.label] = device.channel_last_updated.get(
                    source.channel_key, 0
                )

        # Apply transform if we have values
        if values:
            # Apply the transform and update the cache
            transformed_value = mapping.transform(values, last_updated)
            self._cached_mobile_channels[mapping.mobile_key] = transformed_value

            # Uncomment for debugging if needed
            # import logging
            # logging.getLogger("N2KClient").debug(
            #     f"Updated mapping {mapping.mobile_key} with value {transformed_value}"
            # )

    def to_mobile_dict(self) -> Dict[str, Any]:
        """
        Return mobile channel values from cache.
        Since transforms are applied when state changes, this is just a simple lookup.
        """
        return self._cached_mobile_channels

    def to_dict(self) -> Dict[str, Any]:
        return {
            "devices": {key: device.to_dict() for key, device in self.devices.items()},
        }
