import json
from typing import Any, Dict
import reactivex as rx
from reactivex.subject import BehaviorSubject

from .constants import Constants
from .common_enums import N2kDeviceType
from reactivex.disposable import Disposable


class N2kDevice:
    """
    Represents a single N2K device with its type and channels.
    Each channel has a BehaviorSubject to allow reactive updates.
    Attributes:
        type (N2kDeviceType): The type of the N2K device.
        channels (Dict[str, Any]): Dictionary of channel keys to their current values.
        _channel_subjects (Dict[str, BehaviorSubject]): Internal map of channel keys to their BehaviorSubjects.
    Methods:
        update_channel: Update the value of a channel and notify observers.
        get_channel_subject: Get the BehaviorSubject for a channel.
        dispose: Dispose of all channel subjects and clear channel values.
        to_dict: Return a dictionary representation of the device.
        to_json_string: Return a JSON string representation of the device.
    """

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
        """
        Update the value of a channel and notify any observers.
        If the channel does not have a subject, one is created.
        """
        # Update raw value
        self.channels[channel_key] = value

        # Update subject if it exists
        if channel_key in self._channel_subjects:
            self._channel_subjects[channel_key].on_next(value)
        else:
            self._channel_subjects[channel_key] = BehaviorSubject(value)

    def get_channel_subject(self, channel_key: str) -> BehaviorSubject:
        """
        Get the BehaviorSubject for a channel, creating it if it does not exist.
        The subject emits the current value and all future updates.
        """
        if channel_key not in self._channel_subjects:
            initial_value = self.channels.get(channel_key)
            self._channel_subjects[channel_key] = BehaviorSubject(initial_value)
        return self._channel_subjects[channel_key]

    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        self.dispose()

    def dispose(self):
        """
        Dispose of all channel subjects and clear channel values.
        This should be called to release resources when the device is no longer needed.
        """
        self._channel_subjects.clear()
        self.channels.clear()

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation of the device, including type and channels.
        """
        return {"type": self.type.value, "channels": self.channels}

    def to_json_string(self) -> str:
        """
        Return a JSON string representation of the device.
        """
        return json.dumps(self.to_dict())

    def __eq__(self, other):
        if not isinstance(other, N2kDevice):
            return False
        return self.to_dict() == other.to_dict()


class N2kDevices:
    """
    Collection of N2K devices, separated into engine and non-engine devices.
    Also manages mobile channel values and subscriptions for reactive updates.
    Attributes:
        devices (Dict[str, N2kDevice]): Non-engine N2K devices.
        engine_devices (Dict[str, N2kDevice]): Engine N2K devices.
        mobile_channels (Dict[str, Any]): Current values of non-engine mobile channels.
        engine_mobile_channels (Dict[str, Any]): Current values of engine mobile channels.
        _pipe_subscriptions (Dict[str, Disposable]): Subscriptions for non-engine device observables.
        _engine_pipe_subscriptions (Dict[str, Disposable]): Subscriptions for engine device observables.
    Methods:
        dispose_devices: Dispose and remove all devices, subscriptions, and mobile channels.
        add: Add a device to the appropriate collection (engine or non-engine).
        get_channel_subject: Get the BehaviorSubject for a device's channel.
        set_subscription: Subscribe to an observable and update mobile-ready channel on new values.
        _update_mobile_channel: Update the value of a mobile-ready channel.
        to_mobile_dict: Return a dictionary containing all mobile-ready channel values.
        dispose: Dispose and remove all non-engine devices, subscriptions, and mobile channels.
    """

    devices: Dict[str, N2kDevice]
    engine_devices: Dict[str, N2kDevice]
    mobile_channels: Dict[str, Any]
    engine_mobile_channels: Dict[str, Any]
    _pipe_subscriptions: Dict[str, Disposable]
    _engine_pipe_subscriptions: Dict[str, Disposable]

    def __init__(self):
        self.devices = {}
        self.engine_devices = {}
        # Mobile channel values
        self.mobile_channels = {}
        self.engine_mobile_channels = {}
        # Subscriptions for pipes
        self._pipe_subscriptions = {}
        self._engine_pipe_subscriptions = {}

    def dispose_devices(self, is_engine: bool = False):
        """
        Dispose and remove all devices, subscriptions, and mobile channels.

        Args:
            is_engine (bool, optional): If True, disposes engine devices and related resources;
                otherwise, disposes non-engine devices and resources. Defaults to False.
        Returns:
            None
        """
        if is_engine:
            subscriptions = self._engine_pipe_subscriptions
            devices = self.engine_devices
            channels = self.engine_mobile_channels
        else:
            subscriptions = self._pipe_subscriptions
            devices = self.devices
            channels = self.mobile_channels
        for subscription in subscriptions.values():
            subscription.dispose()
        subscriptions.clear()

        for device in devices.values():
            device.dispose()
        devices.clear()
        channels.clear()

    def add(self, key: str, device: N2kDevice):
        """
        Add a device to the appropriate collection (engine or non-engine).

        Args:
            key (str): The unique key for the device.
            device (N2kDevice): The device instance to add.
        Returns:
            None
        """
        if device.type == N2kDeviceType.ENGINE:
            self.engine_devices[key] = device
        else:
            self.devices[key] = device

    def get_channel_subject(
        self,
        device_key: str,
        channel_key: str,
        device_type: N2kDeviceType = N2kDeviceType.UNKNOWN,
    ) -> BehaviorSubject:
        """
        Get the BehaviorSubject for a device's channel, creating the device if necessary.

        Args:
            device_key (str): The unique key for the device.
            channel_key (str): The channel key within the device.
            device_type (N2kDeviceType, optional): The type of device (ENGINE or other).
                Determines which device collection to use. Defaults to UNKNOWN.
        Returns:
            BehaviorSubject: The subject for the specified channel, emitting current and future values.
        """
        device_dict = (
            self.devices if device_type != N2kDeviceType.ENGINE else self.engine_devices
        )
        if device_key not in device_dict:
            device_dict[device_key] = N2kDevice(type=device_type)
        return device_dict[device_key].get_channel_subject(channel_key)

    def set_subscription(
        self, mobile_key: str, observable: rx.Observable, is_engine: bool = False
    ):
        """
        Subscribe to an observable and update the appropriate mobile channel on new values.

        Args:
            mobile_key (str): The key for the mobile channel to update.
            observable (rx.Observable): The observable to subscribe to.
            is_engine (bool, optional): If True, updates engine mobile channels; otherwise, updates non-engine channels. Defaults to False.
        Returns:
            None
        """
        subscription = observable.subscribe(
            on_next=lambda value: self._update_mobile_channel(
                mobile_key, value, is_engine=is_engine
            )
        )
        if is_engine:
            pipe_subscriptions = self._engine_pipe_subscriptions
        else:
            pipe_subscriptions = self._pipe_subscriptions

        # Clean up any existing subscription
        if mobile_key in pipe_subscriptions:
            pipe_subscriptions[mobile_key].dispose()

        # Store the new subscription
        pipe_subscriptions[mobile_key] = subscription

    def _update_mobile_channel(
        self, mobile_key: str, value: Any, is_engine: bool = False
    ):
        """
        Update the value of a mobile channel.

        Args:
            mobile_key (str): The key for the mobile channel to update.
            value (Any): The new value to set for the channel.
            is_engine (bool, optional): If True, updates engine mobile channels; otherwise, updates non-engine channels. Defaults to False.
        Returns:
            None
        """
        if is_engine:
            self.engine_mobile_channels[mobile_key] = value
        else:
            self.mobile_channels[mobile_key] = value

    def to_mobile_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary containing all mobile channel values (engine and non-engine).

        Returns:
            Dict[str, Any]: A dictionary with all mobile channel values.
        """
        return {**self.mobile_channels, **self.engine_mobile_channels}

    def dispose(self):
        """
        Dispose and remove all non-engine devices, subscriptions, and mobile channels.

        This should be called to release resources for all non-engine devices.

        Returns:
            None
        """
        for subscription in self._pipe_subscriptions.values():
            subscription.dispose()
        self._pipe_subscriptions.clear()
        for device in self.devices.values():
            device.dispose()
        self.mobile_channels.clear()
        self.devices.clear()

    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        self.dispose()

    def __eq__(self, other):
        if not isinstance(other, N2kDevices):
            return False
        return (
            self.devices == other.devices
            and self.engine_devices == other.engine_devices
            and self.mobile_channels == other.mobile_channels
            and self.engine_mobile_channels == other.engine_mobile_channels
        )
