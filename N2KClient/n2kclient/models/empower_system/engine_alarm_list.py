from typing import Any
from .engine_alarm import EngineAlarm


class EngineAlarmList:
    """
    Container for multiple EngineAlarm instances.
    This class manages a collection of engine alarms, allowing for easy access and manipulation of alarm data
    Attributes:
        engine_alarms: A dictionary mapping alarm IDs to their corresponding EngineAlarm instances.
    Methods:
        to_alarm_dict: Converts the engine alarm list to a dictionary representation.
    """

    engine_alarms: dict[str, EngineAlarm]

    def __init__(self):
        self.engine_alarms = {}

    def to_alarm_dict(self) -> dict[str, Any]:
        """
        Convert the EngineAlarmList to a dictionary representation.
        Returns:
            A dictionary where keys are alarm IDs and values are their corresponding EngineAlarm instances.
        """
        return {
            alarm_id: engine_alarm.to_dict()
            for alarm_id, engine_alarm in self.engine_alarms.items()
        }
