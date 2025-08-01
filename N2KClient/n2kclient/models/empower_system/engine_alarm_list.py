from typing import Any
from .engine_alarm import EngineAlarm


class EngineAlarmList:
    engine_alarms: dict[str, EngineAlarm]

    def __init__(self):
        self.engine_alarms = {}

    def to_alarm_dict(self) -> dict[str, Any]:
        return {
            alarm_id: engine_alarm.to_dict()
            for alarm_id, engine_alarm in self.engine_alarms.items()
        }
