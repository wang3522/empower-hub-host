from .alarm import Alarm
from typing import Any


class AlarmList:
    """
    Container for multiple Alarm instances.
    This class manages a collection of alarms, allowing for easy access and manipulation of alarm data.
    Attributes:
        alarm: A dictionary mapping alarm IDs to their corresponding Alarm instances.
    Methods:
        to_alarm_dict: Converts the alarm list to a dictionary representation."""

    alarm: dict[int, Alarm]

    def __init__(self):
        self.alarm = {}

    def to_alarm_dict(self) -> dict[str, Any]:
        """Convert the AlarmList to a dictionary representation."""
        return {alarm_id: alarm.to_dict() for [alarm_id, alarm] in self.alarm.items()}
