from typing import Optional
from ..empower_system.alarm import Alarm, AlarmState, AlarmSeverity
from ..n2k_configuration.engine import EngineDevice


class EngineAlarm(Alarm):
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

        # Uncomment to hide from mobile app. If so, make sure to set cloud rule chain to send pns for this new key.

        # self.id = f"engineAlarm.{alarm_id}"

    def to_dict(self):
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
