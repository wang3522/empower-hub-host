import json
from ..models.common_enums import eEventType
from ..models.dbus_alarm import Dbus_Alarm


class Event:
    """
    Represents an event in the N2K system.
    This class is used to handle events that are emitted by the DBUS service.
    Can be related to alarms or config change events.
    """

    type: eEventType
    content: str
    alarm_item: Dbus_Alarm
    timestamp: str

    def to_dict(self) -> dict:
        """
        Converts the Event object to a dictionary representation.
        :return: Dictionary representation of the event.
        """
        return {
            "event_type": self.type.value,
            "content": self.content,
            "alarm_item": self.alarm_item.to_dict() if self.alarm_item else None,
            "timestamp": self.timestamp,
        }

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Event to JSON: {e}")
            return "{}"
