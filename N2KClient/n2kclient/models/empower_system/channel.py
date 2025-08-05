from ..common_enums import Unit, ChannelType


class Channel:
    """
    Represents a data channel for a Thing in the Empower system.

    Each channel has an id, name, type, unit, tags, and read-only status. Used for modeling device data points.
    """

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
        """
        Initialize a Channel instance.

        Args:
            id (str): The unique channel id (eg. "p" for POWER, "c" for CURRENT).
            name (str): Human-readable channel name.
            type (ChannelType): The type of channel (e.g., NUMBER, STRING, BOOLEAN).
            unit (Unit): The unit of measurement for the channel.
            tags (list[str]): List of tags for metadata
            read_only (bool): Whether the channel is read-only.
        """
        self.id = id
        self.name = name
        self.read_only = read_only
        self.type = type
        self.tags = tags or []
        self.unit = unit

    def to_json(self) -> dict[str, str | bool | list[str]]:
        """
        Return a dictionary representation of this Channel suitable for JSON serialization.

        Returns:
            dict: A dictionary containing the channel's id, name, read_only status, type, unit, and tags.
        """
        return {
            "id": self.id,
            "name": self.name,
            "read_only": self.read_only,
            "type": self.type.value,
            "unit": self.unit.value,
            "tags": self.tags,
        }
