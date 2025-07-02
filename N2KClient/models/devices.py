import json
from typing import Any, Dict
import reactivex as rx
from reactivex.subject import BehaviorSubject
from N2KClient.models.common_enums import N2kDeviceType
from reactivex.disposable import Disposable


class N2kDevice:
    type: N2kDeviceType
    channels: Dict[str, Any]
    _channel_subjects: Dict[str, BehaviorSubject]

    def __init__(self, type: N2kDeviceType):
        self.type = type
        # Raw channel values
        self.channels = {}
        # Channel subjects for reactive programming
        self._channel_subjects = {}

    def update_channel(self, channel_key: str, value: Any):
        """Update a channel's value"""
        # Update raw value
        self.channels[channel_key] = value

        # Update subject if it exists
        if channel_key in self._channel_subjects:
            self._channel_subjects[channel_key].on_next(value)

    def get_channel_subject(self, channel_key: str) -> BehaviorSubject:
        if channel_key not in self._channel_subjects:
            initial_value = self.channels.get(channel_key)
            self._channel_subjects[channel_key] = BehaviorSubject(initial_value)
        return self._channel_subjects[channel_key]

    def dispose(self):
        """Clean up subjects"""
        self._channel_subjects.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.value, "channels": self.channels}

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())


class N2kDevices:
    devices: Dict[str, N2kDevice]
    mobile_channels: Dict[str, Any]
    _pipe_subscriptions: Dict[str, Disposable]

    def __init__(self):
        self.devices = {}
        # Mobile channel values
        self.mobile_channels = {}
        # Subscriptions for pipes
        self._pipe_subscriptions = {}

    def add(self, key: str, device: N2kDevice):
        """Add a device"""
        if key in self.devices:
            # Update type, but keep the same object and subjects
            self.devices[key].type = device.type
            # Optionally update other metadata here
        else:
            self.devices[key] = device

    def update_channel(self, device_key: str, channel_key: str, value: Any):
        """Update a channel in a device"""
        if device_key in self.devices:
            self.devices[device_key].update_channel(channel_key, value)

    def get_channel_subject(
        self, device_key: str, channel_key: str, device_type: N2kDeviceType
    ) -> BehaviorSubject:
        # Ensure device entry exists. If not, create it. Config builder will provide expected device type
        if device_key not in self.devices:
            self.devices[device_key] = N2kDevice(type=device_type)
        return self.devices[device_key].get_channel_subject(channel_key)

    def set_subscription(self, mobile_key: str, observable: rx.Observable):
        """Set a subscription from an observable to a mobile channel"""
        # Create the subscription
        subscription = observable.subscribe(
            on_next=lambda value: self._update_mobile_channel(mobile_key, value)
        )

        # Clean up any existing subscription
        if mobile_key in self._pipe_subscriptions:
            self._pipe_subscriptions[mobile_key].dispose()

        # Store the new subscription
        self._pipe_subscriptions[mobile_key] = subscription

    def _update_mobile_channel(self, mobile_key: str, value: Any):
        """Update a mobile channel value"""
        self.mobile_channels[mobile_key] = value
        print(f"Mobile channel {mobile_key} updated to {value}")

    def to_mobile_dict(self) -> Dict[str, Any]:
        """Return mobile channel values from all devices"""
        return self.mobile_channels

    def dispose(self):
        """Clean up all device subscriptions"""
        for subscription in self._pipe_subscriptions.values():
            subscription.dispose()
        self._pipe_subscriptions.clear()
        for device in self.devices.values():
            device.dispose()
