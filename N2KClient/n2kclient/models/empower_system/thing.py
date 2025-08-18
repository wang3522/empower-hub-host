from abc import ABC
from typing import Any, Union
from .channel import Channel
from .link import Link
from ..common_enums import ThingType
import reactivex as rx
from ..alarm_setting import AlarmSetting


class Thing(ABC):
    """
    Abstract base class representing a logical device or entity (a "Thing") in the Empower system.

    A Thing aggregates channels (data points), metadata, links to other Things, and alarm settings.
    It provides methods for channel registration, resource cleanup, and serialization to configuration dictionaries.
    Subclasses should implement specific device or system models (e.g., Battery, Engine).

    Attributes:
        channels: Dictionary mapping channel IDs to Channel instances.
        id: Unique identifier for this Thing, constructed from its type and instance.
        type: The type of the Thing, represented as a ThingType enum.
        name: Human-readable name for this Thing.
        metadata: Dictionary for storing additional information about the Thing (e.g., capacity).
        links: List of Link instances representing connections to other Things.
        _disposable_list: List of RxPy DisposableBase instances for managing subscriptions.
        alarm_settings: List of AlarmSetting instances associated with this Thing, used for alarm management. Within mobile app, these are used to enable/disable alarms.
    Methods:
        __init__: Initializes the Thing with its type, id, name, categories, and optional
        links.
        dispose: Cleans up resources associated with this Thing, disposing of all RxPy subscriptions and
        clearing the channels dictionary.
        _define_channel: Registers a Channel with this Thing and assigns its full channel id.
        to_config_dict: Converts this Thing and its properties to a configuration dictionary.
    """

    channels: dict[str, Channel]
    id: str
    type: ThingType
    name: str
    metadata: dict[str, Union[str, int, float, bool]]
    links: list[Link]
    _disposable_list: list[rx.abc.DisposableBase]
    alarm_settings: list[AlarmSetting]

    def __init__(
        self, type: ThingType, id: str, name: str, categories: list[str], links=[]
    ):
        self.channels = {}
        self.id = f"{type.value}.{id}"
        self.type = type
        self.name = name
        self.metadata = {}
        self.links = links or []
        self.categories = categories
        self._disposable_list = []
        self.alarm_settings = []

    def __del__(self):
        """
        Destructor to ensure all resources are cleaned up when the object is deleted.
        Calls dispose() to release any subscriptions and clear channels.
        """
        self.dispose()

    def dispose(self):
        """
        Dispose of all resources associated with this Thing.
        Disposes all RxPy subscriptions and clears the channels dictionary.
        """
        for disposable in self._disposable_list:
            disposable.dispose()
        self.channels.clear()

    def _define_channel(self, channel: Channel):
        """
        Register a channel with this Thing and assign its full channel id.

        The full channel id is constructed as "{thing_id}.{channel_id}" and is used as the key
        in the channels dictionary. This method adds the channel to the Thing and returns the full id.

        Args:
            channel (Channel): The channel to register.

        Returns:
            str: The full channel id (e.g., "Battery.1.voltage").
        """
        channel_full_id = f"{self.id}.{channel.id}"
        self.channels[channel_full_id] = channel
        return channel_full_id

    def to_config_dict(self) -> dict[str, Any]:
        """
        Convert this Thing and its properties to a configuration dictionary.

        Returns:
            dict[str, Any]: A dictionary representation of the Thing, including id, type, name,
            metadata, categories, channels, links, and alarm settings.
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "metadata": self.metadata,
            "categories": self.categories,
            "channels": {
                channel_id: channel.to_json()
                for channel_id, channel in self.channels.items()
            },
            "links": [link.to_json() for link in self.links],
            "settings": [
                alarm_setting.to_json() for alarm_setting in self.alarm_settings
            ],
        }
