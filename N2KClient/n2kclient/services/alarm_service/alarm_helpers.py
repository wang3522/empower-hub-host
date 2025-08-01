from typing import Optional

from ...models.n2k_configuration.engine import EngineDevice

from ...util.time_util import TimeUtil
from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.n2k_configuration.engine_configuration import EngineConfiguration
from ...models.empower_system.engine_alarm_list import EngineAlarmList
from ...models.empower_system.engine_alarm import EngineAlarm


def get_inverter_charger_alarm_title(config: N2kConfiguration, ac_id: int):
    for [_, ac_meter] in config.ac.items():
        for [_, ac_line] in ac_meter.line.items():
            if ac_id == ac_line.id:
                return ac_line.name_utf8
    return None


def generate_alarms_from_discrete_status(
    status_alarms: list,
    discrete_status: int,
    merged_engine_alert_list: EngineAlarmList,
    prev_discrete_status1: Optional[int],
    prev_discrete_status2: Optional[int],
    current_discrete_status1: Optional[int],
    current_discrete_status2: Optional[int],
    prev_engine_alert_list: EngineAlarmList,
    engine_id: int,
    engine_config: EngineDevice,
    discrete_status_word: int,
):
    """
    Generates alarms based on the discrete status and updates the merged engine alert list.

    This method iterates through the provided status alarms and checks if the corresponding bit
    in the discrete status is set. If the bit is set and the alarm is not already present
    in the previous engine alert list, it creates a new EngineAlert and adds it to the merged
    engine alert list. If the alarm text is already present, it updates the merged engine alert
    list with the existing alert from the previous engine alert list.

    Args:
        status_alarms (list): A list of tuples where each tuple contains a bit shift and an alarm text.
        discrete_status (int): The current discrete status represented as an integer.
        merged_engine_alert_list (EngineAlertList): The list where the generated or updated engine alerts will be stored.
        prev_discrete_status1 (Optional[int]): The previous discrete status 1.
        prev_discrete_status2 (Optional[int]): The previous discrete status 2.
        current_discrete_status1 (Optional[int]): The current discrete status 1.
        current_discrete_status2 (Optional[int]): The current discrete status 2.
        prev_engine_alert_list (EngineAlertList): The list of engine alerts from the previous state.
        engine_id (int): The ID of the engine.
        engine_config (EngineConfiguration): The configuration of the engine.
        discrete_status_word (int): The discrete status word number (1 or 2).

    Returns:
        None
    """
    for bit_shift, alarm_text in status_alarms:
        alarm_id = (
            f"engine.{engine_id}.discrete_status{discrete_status_word}.{bit_shift}"
        )
        if (discrete_status >> bit_shift) & 1:
            if (
                engine_id not in prev_engine_alert_list.engine_alarms
                or alarm_text not in prev_engine_alert_list.engine_alarms[engine_id]
            ):
                date_active = TimeUtil.current_time()
                engine_alert = EngineAlarm(
                    date_active=date_active,
                    alarm_text=alarm_text,
                    engine=engine_config,
                    prev_discrete_status1=prev_discrete_status1,
                    prev_discrete_status2=prev_discrete_status2,
                    current_discrete_status1=current_discrete_status1,
                    current_discrete_status2=current_discrete_status2,
                    alarm_id=alarm_id,
                )
                merged_engine_alert_list.engine_alarms[alarm_id] = engine_alert
        elif alarm_id in merged_engine_alert_list.engine_alarms:
            merged_engine_alert_list.engine_alarms.pop(alarm_id)
