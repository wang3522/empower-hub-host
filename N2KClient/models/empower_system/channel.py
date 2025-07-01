import reactivex as rx
from ..common_enums import Unit, ChannelType


class Channel:
    id: str
    name: str
    read_only: bool
    type: ChannelType
    tags: list[str]
    unit: Unit

    def __init__(
        self,
        id: str,
        name: str,
        type: ChannelType,
        unit: Unit,
        tags: list[str],
        read_only: bool,
    ):
        self.id = id
        self.name = name
        self.read_only = read_only
        self.type = type
        self.tags = tags or []
        self.unit = unit

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "read_only": self.read_only,
            "type": self.type.value,
            "unit": self.unit.value,
            "tags": self.tags,
        }
