from .alarm import Alarm
from typing import Any


class AlarmList:
    alarm: dict[int, Alarm]

    def __init__(self):
        self.alarm = {}

    def to_alarm_dict(self) -> dict[str, Any]:
        return {alarm_id: alarm.to_dict() for [alarm_id, alarm] in self.alarm.items()}
