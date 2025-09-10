from typing import Optional

from ...models.common_enums import ThingType

from ...models.n2k_configuration.engine import EngineDevice

from ...util.time_util import TimeUtil
from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.empower_system.engine_alarm_list import EngineAlarmList
from ...models.empower_system.engine_alarm import EngineAlarm
from ...util.common_utils import calculate_inverter_charger_instance


def get_inverter_charger_alarm_title(config: N2kConfiguration, ac_id: int):
    """
    Get the title of the inverter charger alarm based on the AC ID.
    Args:
        config: The N2K configuration containing AC definitions.
        ac_id: The AC ID to find the corresponding alarm title.

    Returns:
        The title of the inverter charger alarm or None if not found.
    """
    for [_, ac_meter] in config.ac.items():
        for [_, ac_line] in ac_meter.line.items():
            if ac_id == ac_line.id:
                return ac_line.name_utf8
    return None


def generate_alarms_from_discrete_status(
    status_alarms: list,
    discrete_status: int,
    merged_engine_alarm_list: EngineAlarmList,
    prev_discrete_status1: Optional[int],
    prev_discrete_status2: Optional[int],
    current_discrete_status1: Optional[int],
    current_discrete_status2: Optional[int],
    prev_engine_alarm_list: EngineAlarmList,
    engine_id: int,
    engine_config: EngineDevice,
    discrete_status_word: int,
):
    """
    Generates alarms based on the discrete status and updates the merged engine alert list.

    This method iterates through the provided status alarms and checks if the corresponding bit
    in the discrete status is set. If the bit is set and the alarm is not already present
    in the previous engine alert list, it creates a new EngineAlert and adds it to the merged
    engine alert list.

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
            if alarm_id not in prev_engine_alarm_list.engine_alarms:
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
                merged_engine_alarm_list.engine_alarms[alarm_id] = engine_alert
        elif alarm_id in merged_engine_alarm_list.engine_alarms:
            merged_engine_alarm_list.engine_alarms.pop(alarm_id)


def get_combi_charger(
    config: N2kConfiguration, dc_id: int, things: list[str]
) -> list[str]:
    """
    Given a config and dc meter charger, append id for charger to list of things
    """
    inverter_charger = next(
        (
            inverter_charger
            for inverter_charger in config.inverter_charger.values()
            if any(
                battery_bank is not None
                and battery_bank.enabled
                and battery_bank.id == dc_id
                for battery_bank in [
                    inverter_charger.battery_bank_1_id,
                    inverter_charger.battery_bank_2_id,
                    inverter_charger.battery_bank_3_id,
                ]
            )
        ),
        None,
    )

    if inverter_charger is not None:
        charger_id = f"{ThingType.CHARGER.value}.{calculate_inverter_charger_instance(inverter_charger)}"
        if charger_id not in things:
            things.append(charger_id)
    return things


def get_combi_inverter(
    config: N2kConfiguration, ac_id: int, things: list[str]
) -> list[str]:
    """
    Given a config and ac meter inverter, append id for inverter to list of things
    """
    inverter_charger = next(
        (
            inverter_charger
            for inverter_charger in config.inverter_charger.values()
            if inverter_charger.inverter_ac_id.id == ac_id
            and inverter_charger.inverter_ac_id.enabled
        ),
        None,
    )

    if inverter_charger is not None:
        inverter_id = f"{ThingType.INVERTER.value}.{calculate_inverter_charger_instance(inverter_charger)}"
        if inverter_id not in things:
            things.append(inverter_id)
    return things
