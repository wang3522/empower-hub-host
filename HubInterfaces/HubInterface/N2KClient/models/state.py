from models.channel import N2KChannel
from typing import Any


class N2KState:
    channels: dict[int, N2KChannel]

    def __init__(self):
        self.channels = {}

    def to_state_dict(self) -> dict[str, Any]:
        return {
            channel_id: channel.to_dict()
            for [channel_id, channel] in self.channels.items()
        }
