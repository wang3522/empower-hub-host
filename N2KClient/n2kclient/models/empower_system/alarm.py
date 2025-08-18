from enum import Enum
from typing import Any, List, Optional, Union

from ..constants import Constants
from ..dbus_alarm import Dbus_Alarm
from ..common_enums import eSeverityType


class AlarmSeverity(str, Enum):
    """
    Enumeration of alarm severities.
    """

    IMPORTANT = "important"
    STANDARD = "standard"
    CRITICAL = "critical"
    WARNING = "warning"
    NONE = "none"
    SYSTEMSON = "systemsOn"


class AlarmState(str, Enum):
    """
    Enumeration of alarm states.
    """

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
    """
    This class encapsulates the details of an alarm, including its ID, title, name, description,
    severity, current state, unique ID, fault action, date active, context, and associated
    things (components).

    It provides methods to convert the alarm instance to a dictionary representation for serialization.
    Attributes:
        id: The unique identifier of the alarm.
        title: The title of the alarm.
        name: The name of the alarm.
        description: A description of the alarm.
        fault_action: The action to take when a fault occurs (Engine Alarm).
        severity: The severity level of the alarm, represented as an AlarmSeverity enum.
        current_state: The current state of the alarm, represented as an AlarmState enum.
        unique_id: A unique identifier for the alarm instance.
        date_active: The date when the alarm was activated.
        context: Additional context information related to the alarm.
        things: A list of things (components) associated with the alarm.
    Methods:
        to_dict: Converts the Alarm instance to a dictionary representation.
        __init__: Initializes the Alarm instance with the provided parameters or from a Dbus_Alarm instance.
    """

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

    def to_dict(self) -> dict[str, Any]:
        """Convert the Alarm instance to a dictionary representation."""
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
