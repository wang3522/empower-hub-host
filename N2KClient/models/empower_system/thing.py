from abc import ABC
from typing import Any, Union
from .channel import Channel
from .link import Link
from ..common_enums import ThingType
import reactivex as rx


class Thing(ABC):
    channels: dict[str, Channel]
    id: str
    type: ThingType
    name: str
    metadata: dict[str, Union[str, int, float, bool]]
    links: list[Link]
    _disposable_list: list[rx.abc.DisposableBase]

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

    def __del__(self):
        self.dispose()

    def dispose(self):
        for disposable in self._disposable_list:
            disposable.dispose()
        self.channels.clear()

    def _define_channel(self, channel: Channel):
        channel_full_id = f"{self.id}.{channel.id}"
        channel.id = channel_full_id
        self.channels[channel_full_id] = channel

    def to_config_dict(self) -> dict[str, Any]:
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
        }
