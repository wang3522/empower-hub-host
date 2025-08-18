from typing import Optional
from ..empower_system.alarm import Alarm, AlarmState, AlarmSeverity
from ..n2k_configuration.engine import EngineDevice


class EngineAlarm(Alarm):
    """
    Representation of an engine alarm, extending the base Alarm class with engine-specific properties.
    This class encapsulates the details of an engine alarm, including its association with a specific engine device
    and additional status information relevant to engine alarms.
    Attributes:
        current_discrete_status1: The current discrete status 1 of the engine alarm.
        current_discrete_status2: The current discrete status 2 of the engine alarm.
        prev_discrete_status1: The previous discrete status 1 of the engine alarm.
        prev_discrete_status2: The previous discrete status 2 of the engine alarm.
    Methods:
        to_dict: Converts the EngineAlarm instance to a dictionary representation.
    """

    current_discrete_status1: Optional[int] = None
    current_discrete_status2: Optional[int] = None
    prev_discrete_status1: Optional[int] = None
    prev_discrete_status2: Optional[int] = None

    def __init__(
        self,
        date_active: int,
        alarm_text: str,
        engine: EngineDevice,
        current_discrete_status1: int,
        current_discrete_status2: int,
        prev_discrete_status1: int,
        prev_discrete_status2: int,
        alarm_id=str,
    ):
        engine_name = engine.name_utf8

        self.current_discrete_status1 = current_discrete_status1
        self.current_discrete_status2 = current_discrete_status2
        self.prev_discrete_status1 = prev_discrete_status1
        self.prev_discrete_status2 = prev_discrete_status2

        # use constant below
        thing_id = f"marineEngine.{engine.id}"
        super().__init__(
            title=engine_name,
            name=alarm_text,
            description=alarm_text,
            unique_id=alarm_id,
            date_active=date_active,
            state=AlarmState.ENABLED,
            severity=AlarmSeverity.IMPORTANT,
            things=[thing_id],
            context={},
            fault_action="",
        )

    def to_dict(self):
        """
        Convert the EngineAlarm instance to a dictionary representation.
        Returns:
            A dictionary containing the properties of the EngineAlarm instance."""
        alarm_dict = super().to_dict()
        alarm_dict.update(
            {
                "current_discrete_status1": self.current_discrete_status1,
                "current_discrete_status2": self.current_discrete_status2,
                "prev_discrete_status1": self.prev_discrete_status1,
                "prev_discrete_status2": self.prev_discrete_status2,
            }
        )
        return alarm_dict
