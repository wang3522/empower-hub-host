from abc import ABC
from typing import Any, Union
from .channel import Channel
from .link import Link
from ..common_enums import ThingType


class Thing(ABC):
    channels: dict[str, Channel]
    id: str
    type: ThingType
    name: str
    metadata: dict[str, Union[str, int, float, bool]]
    links: list[Link]

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

    def _define_channel(self, channel: Channel):
        channel_full_id = f"{self.id}.{channel.id}"
        self.channels[channel_full_id] = channel

    def _define_outside_(self, link: Link):
        self.links.append(link)

    def to_config_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self,
            "name": self.name,
            "metadata": self.metadata,
            "categories": self.categories,
            "channels": {
                channel_id: channel.to_json()
                for channel_id, channel in self.channels.items()
            },
            "links": [link.to_json() for link in self.links],
        }
