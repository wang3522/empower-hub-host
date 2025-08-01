from enum import Enum
from typing import Any, List, Optional, Union

from ..constants import Constants
from ..dbus_alarm import Dbus_Alarm
from ..common_enums import eSeverityType


class AlarmSeverity(str, Enum):
    IMPORTANT = "important"
    STANDARD = "standard"
    CRITICAL = "critical"
    WARNING = "warning"
    NONE = "none"
    SYSTEMSON = "systemsOn"


class AlarmState(str, Enum):
    ACKNOWLEDGED = "acknowledged"
    ENABLED = "enabled"
    DISABLED = "disabled"


severity_map = {
    eSeverityType.SeverityCritical: AlarmSeverity.CRITICAL,
    eSeverityType.SeverityImportant: AlarmSeverity.IMPORTANT,
    eSeverityType.SeverityWarning: AlarmSeverity.WARNING,
    eSeverityType.SeverityStandard: AlarmSeverity.STANDARD,
    eSeverityType.SeverityNone: AlarmSeverity.STANDARD,
    eSeverityType.SeveritySIO: AlarmSeverity.SYSTEMSON,
}


class Alarm:
    id: str
    title: str
    name: str
    description: str
    fault_action: str
    severity: AlarmSeverity
    current_state: AlarmState
    unique_id: int
    fault_action: str

    date_active: int
    context: dict[str, Union[str, int, float, bool]]
    things: list[str]

    def __init__(
        self,
        alarm: Optional[Dbus_Alarm] = None,
        state: Optional[AlarmState] = None,
        date_active: Optional[int] = None,
        things: Optional[List[str]] = None,
        title: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        unique_id: Optional[int] = None,
        fault_action: Optional[str] = None,
        severity: Optional[AlarmSeverity] = None,
        context: Optional[dict[str, Union[str, int, float, bool]]] = None,
    ):
        if alarm:
            self.id = f"{Constants.alarm}.{alarm.unique_id}"
            self.title = alarm.title
            self.name = alarm.name
            self.description = alarm.description
            self.unique_id = alarm.unique_id
            self.date_active = date_active
            self.fault_action = alarm.fault_action

            self.current_state = state
            self.context = {}
            self.things = things or []
            self.severity = severity_map.get(alarm.severity, AlarmSeverity.NONE)

        else:
            self.id = f"{Constants.alarm}.{unique_id}"
            self.title = title
            self.name = name
            self.description = description
            self.unique_id = unique_id
            self.date_active = date_active
            self.fault_action = fault_action
            self.current_state = state
            self.context = context or {}
            self.things = things or []
            self.severity = severity

    @classmethod
    def from_manual_settings(
        cls,
        title: str,
        name: str,
        description: str,
        unique_id: int,
        date_active: int,
        fault_action: str,
        state: AlarmState,
        severity: AlarmSeverity,
        things: Optional[List[str]] = None,
        context: Optional[dict[str, Union[str, int, float, bool]]] = None,
    ):
        return cls(
            title=title,
            name=name,
            description=description,
            unique_id=unique_id,
            date_active=date_active,
            fault_action=fault_action,
            state=state,
            severity=severity,
            things=things,
            context=context,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "name": self.name,
            "description": self.description,
            "severity": self.severity.value,
            "currentState": self.current_state.value,
            "things": self.things,
            "dateActive": self.date_active,
            "faultAction": self.fault_action,
            "context": self.context,
        }
