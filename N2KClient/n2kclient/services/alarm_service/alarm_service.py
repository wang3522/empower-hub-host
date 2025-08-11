import copy
import json
import logging
from typing import Any, Callable, Optional, Union

from ...models.empower_system.engine_list import EngineList

from ...models.empower_system.empower_system import EmpowerSystem

from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.n2k_configuration.engine_configuration import EngineConfiguration
from ...models.empower_system.engine_alarm_list import EngineAlarmList
from ...models.constants import Constants, JsonKeys
from ...models.empower_system.alarm import Alarm, AlarmState
from ...models.n2k_configuration.alarm import Alarm as N2KAlarm
from ...models.empower_system.alarm_list import AlarmList
from ...util.time_util import TimeUtil
from ...models.common_enums import (
    eStateType,
    eAlarmType,
    ComponentType,
    ThingType,
    eSeverityType,
)
from ...models.empower_system.component_reference import ComponentReference
from ...models.empower_system.alarm_type import AlarmType
from ...models.n2k_configuration.ui_relationship_msg import (
    ItemType,
)
from ...util.common_utils import (
    is_in_category,
    calculate_inverter_charger_instance,
    get_associated_circuit,
    map_fields,
    map_enum_fields,
)
from ...models.n2k_configuration.circuit import Circuit
from ...models.n2k_configuration.dc import DCType
from ...models.n2k_configuration.ac import ACType
from ...models.n2k_configuration.tank import TankType
from ...models.n2k_configuration.bls_alarm_mapping import BLSAlarmMapping
from .field_maps import ALARM_FIELD_MAP, ALARM_ENUM_FIELD_MAP
from .alarm_helpers import generate_alarms_from_discrete_status


class AlarmService:
    _logger = logging.getLogger(
        f"{Constants.DBUS_N2K_CLIENT}.{Constants.Alarm_Service}"
    )
    _prev_discrete_status1: dict[Optional[int]]
    _prev_discrete_status2: dict[Optional[int]]

    def __init__(
        self,
        alarm_list_func: Callable[[], AlarmList],
        get_latest_alarms_func: Callable[[], AlarmList],
        get_config_func: Callable[[], N2kConfiguration],
        get_engine_config_func: Callable[[], EngineConfiguration],
        get_engine_alarms_func: Callable[[], EngineAlarmList],
        set_alarm_list: Callable[[AlarmList], None],
        set_engine_alarms: Callable[[EngineAlarmList], None],
        acknowledge_alarm_func: Callable[[dict], None],
        get_latest_empower_system_func: Callable[[], EmpowerSystem],
        get_latest_engine_list_func: Callable[[], EngineList],
    ):
        self.alarm_list = alarm_list_func
        self.get_latest_alarms = get_latest_alarms_func
        self.get_config = get_config_func
        self.get_engine_config = get_engine_config_func
        self.get_engine_alarms = get_engine_alarms_func
        self.set_alarm_list = set_alarm_list
        self.set_engine_alarms = set_engine_alarms
        self.acknowledge_alarm_func = acknowledge_alarm_func
        self.get_latest_empower_system = get_latest_empower_system_func
        self.get_latest_engine_list = get_latest_engine_list_func

        self._prev_discrete_status1 = {}
        self._prev_discrete_status2 = {}

    ###############################
    # Public Methods
    ###############################
    def acknowledge_alarm(self, alarm_id: int) -> bool:
        try:
            alarm = self.get_latest_alarms().alarm.get(alarm_id)
            if alarm is None:
                self._logger.error(
                    f"Attempted to acknowledge alarm {alarm_id}. Alarm not found in active list."
                )
                return False
            if alarm.current_state == AlarmState.ACKNOWLEDGED:
                self._logger.debug(f"Alarm {alarm_id} is already acknowledged.")
                return True

            acknowledge_request = {
                JsonKeys.ID: alarm.unique_id,
                JsonKeys.ACCEPTED: True,
            }
            response = self.acknowledge_alarm_func(json.dumps(acknowledge_request))
            try:
                response_json: dict = json.loads(response)
                result = response_json.get(JsonKeys.Result)
                return result == JsonKeys.OK
            except Exception as e:
                self._logger.error(
                    "Invalid response from acknowledge alarm request %s: %s",
                    alarm_id,
                    e,
                )
                return False

        except Exception as e:
            self._logger.error("Failed to acknowledge alarm %s: %s", alarm_id, e)
            return False

    def load_active_alarms(self, force: bool = False) -> None:
        """
        Load active alarms from the alarm list dbus method and update the latest alarms.
        """
        try:
            latest_alarms = self.get_latest_alarms()
            merged_alarm_list = AlarmList()
            alarm_list_str = self.alarm_list()
            if alarm_list_str:
                alarm_list = self.parse_alarm_list(alarm_list_str)
                for alarm in alarm_list:
                    alarm_id = alarm.unique_id
                    processed_alarm = None
                    date_active = TimeUtil.current_time()
                    # ACKNOWLEDGED
                    if alarm.current_state == eStateType.StateAcknowledged:
                        if alarm_id in latest_alarms.alarm:
                            processed_alarm = copy.deepcopy(
                                latest_alarms.alarm[alarm_id]
                            )
                            processed_alarm.current_state = AlarmState.ACKNOWLEDGED
                        else:
                            processed_alarm = self.build_reportable_alarm(
                                alarm,
                                AlarmState.ACKNOWLEDGED,
                                date_active,
                                self.get_config(),
                                self.get_engine_config(),
                            )
                    # ENABLED
                    elif alarm.current_state == eStateType.StateEnabled:
                        if alarm_id in latest_alarms.alarm:
                            processed_alarm = copy.deepcopy(
                                latest_alarms.alarm[alarm_id]
                            )
                            if processed_alarm.current_state != AlarmState.ENABLED:
                                processed_alarm.current_state = AlarmState.ENABLED
                                processed_alarm.date_active = date_active
                        else:
                            processed_alarm = self.build_reportable_alarm(
                                alarm,
                                AlarmState.ENABLED,
                                date_active,
                                self.get_config(),
                                self.get_engine_config(),
                            )
                    # FINALLY
                    if processed_alarm is not None:
                        merged_alarm_list.alarm[alarm_id] = processed_alarm

            if (
                merged_alarm_list.to_alarm_dict() != latest_alarms.to_alarm_dict()
                or force
            ):
                merged_alarm_list = self._verify_alarm_things(merged_alarm_list)
                self.set_alarm_list(merged_alarm_list)
        except Exception as e:
            self._logger.error("Failed to load active alarms: %s", e)
            return False

    ######################
    # Alarm Processors
    ######################

    def build_reportable_alarm(
        self,
        alarm: N2KAlarm,
        state: AlarmState,
        date_active: int,
        config: N2kConfiguration,
        engine_config: Optional[N2kConfiguration] = None,
    ):
        """
        Build a reportable alarm object from raw alarm data and state.
        """
        if (
            alarm.channel_id is not None
            and alarm is not None
            and alarm.alarm_type is not eAlarmType.TypeDeviceMissing
        ):
            references = self.get_alarm_related_components(
                alarm,
                config,
                engine_config,
            )
            if references and len(references) > 0:
                alarm_things = self.get_alarm_things(references, config)
                processed_alarm = self.post_process_alarm_configuration(
                    alarm, config.bls_alarm_mappings
                )
                if alarm_things and processed_alarm:
                    reportable_alarm = Alarm(
                        alarm, state, date_active=date_active, things=alarm_things
                    )
                    return reportable_alarm
        return None

    def get_alarm_related_components(
        self,
        alarm: N2KAlarm,
        config: N2kConfiguration,
        engine_config: Optional[EngineConfiguration] = None,
    ) -> list[str]:
        """
        Given an alarm, configuration and previously processed bls_alarm id map build a list of
        Component References for any give alarm, to associate alarm to things.
        """
        from .alarm_processors import (
            process_device_alarms,
            process_dc_meter_alarms,
            process_ac_meter_alarms,
            process_tank_alarms,
            process_circuit_load_alarms,
            process_bls_alarms,
            process_smartcraft_alarms,
        )

        affected_components: list[ComponentReference] = []
        is_dc_alarm = self._is_dc_meter_alarm(alarm)

        resolved_alarm_channel_id = alarm.channel_id
        if is_dc_alarm:
            resolved_alarm_channel_id -= 3

        alarm_processors = [
            process_device_alarms,
            process_dc_meter_alarms,
            process_ac_meter_alarms,
            process_tank_alarms,
            process_circuit_load_alarms,
            process_bls_alarms,
        ]

        for processor in alarm_processors:
            affected_components = processor(
                logger=self._logger,
                resolved_alarm_channel_id=resolved_alarm_channel_id,
                config=config,
                affected_components=affected_components,
                alarm=alarm,
                is_dc_alarm=is_dc_alarm,
            )

        if alarm.external_alarm_id and alarm.external_alarm_id >= 0x4100:
            affected_components = process_smartcraft_alarms(
                logger=self._logger,
                resolved_alarm_channel_id=resolved_alarm_channel_id,
                config=engine_config,
                affected_components=affected_components,
                is_dc_alarm=is_dc_alarm,
            )

        return affected_components

    def _is_dc_meter_alarm(self, alarm: N2KAlarm) -> bool:
        """
        Determine if alarm is associated with DCMeter based on Type
        """
        if alarm.external_alarm_id in (
            AlarmType.CZ_ALARM_DC_LOW_VOLTAGE_ALARM_CODE,
            AlarmType.CZ_ALARM_DC_VERY_LOW_VOLTAGE_ALARM_CODE,
            AlarmType.CZ_ALARM_DC_HIGH_VOLTAGE_ALARM_CODE,
            AlarmType.CZ_ALARM_DC_LOW_BATTERY_CAPACITY_ALARM_CODE,
            AlarmType.CZ_ALARM_DC_VERY_LOW_BATTERY_CAPACITY_ALARM_CODE,
            AlarmType.CZ_ALARM_DC_HIGH_BATTERY_CAPACITY_ALARM_CODE,
            AlarmType.CZ_ALARM_DC_LOAD_SHED_LOW_ALARM_CODE,
            AlarmType.CZ_ALARM_DC_LOAD_SHED_VERY_LOW_ALARM_CODE,
            AlarmType.CZ_ALARM_BATTERY_SAFETY,
            AlarmType.CZ_ALARM_BATTERY_STOP_CHARGE,
            AlarmType.CZ_ALARM_BATTERY_RELAY_FAILURE,
            AlarmType.CZ_ALARM_BATTERY_HARDWARE_FAILURE,
            AlarmType.CZ_ALARM_BATTERY_OVER_CURRENT,
            AlarmType.CZ_ALARM_BATTERY_TEMP_HIGH,
            AlarmType.CZ_ALARM_BATTERY_TEMP_LOW,
            AlarmType.CZ_ALARM_BATTERY_LAST_100,
            AlarmType.CZ_ALARM_MSH_FUSE_BLOWN,
            AlarmType.CZ_ALARM_WRONG_MODEL_INVALID_CONFIG,
        ):
            return True
        return False

    def get_alarm_things(
        self, references: list[str], config: N2kConfiguration
    ) -> list[str]:
        """
        Given a list of alarm references, proccess alarm references
        to find associated thing id and return list of thing ids
        """
        things: list[str] = []
        for ref in references:
            things = self._get_alarm_thing(ref, config, things)
        return things

    def _get_alarm_thing(
        self, reference: ComponentReference, config: N2kConfiguration, things: list[str]
    ):
        thing = reference.thing
        ref_type = reference.component_type
        if ref_type == ComponentType.CIRCUIT:
            if thing.remote_visibility != 1 and thing.remote_visibility != 2:
                return things

            if is_in_category(thing.categories, Constants.Lighting):
                things.append(f"{ThingType.LIGHT.value}.{thing.control_id}")
            elif is_in_category(thing.categories, Constants.BilgePumps):
                things.append(f"{ThingType.BILGE_PUMP.value}.{thing.control_id}")
            elif is_in_category(thing.categories, Constants.Pumps):
                things.append(f"{ThingType.PUMP.value}.{thing.control_id}")
            elif is_in_category(thing.categories, Constants.Power):
                associated_thing = self.get_switch_thing(config, thing)
                if associated_thing is not None:
                    things = self._get_alarm_thing(associated_thing, config, things)
                else:
                    things.append(
                        f"{ThingType.GENERIC_CIRCUIT.value}.{thing.control_id}"
                    )
        elif ref_type == ComponentType.DCMETER and thing.dc_type == DCType.Battery:
            things.append(f"{ThingType.BATTERY.value}.{thing.instance.instance}")
            # things = self.get_combi_charger(dc=thing, things=things, config=config)
        elif ref_type == ComponentType.ACMETER:
            if thing.ac_type == ACType.ShorePower:
                things.append(
                    f"{ThingType.SHORE_POWER.value}.{thing.instance.instance}"
                )
            elif thing.ac_type == ACType.Inverter:
                things.append(f"{ThingType.INVERTER.value}.{thing.instance.instance}")
            elif thing.ac_type == ACType.Charger:
                things.append(f"{ThingType.CHARGER.value}.{thing.instance.instance}")
            # things = self.get_combi_inverter(ac=thing, things=things, config=config)
        elif ref_type == ComponentType.TANK:
            if thing.tank_type in (TankType.Fuel, TankType.Oil):
                things.append(f"{ThingType.FUEL_TANK.value}.{thing.id}")
            else:
                things.append(f"{ThingType.WATER_TANK.value}.{thing.id}")
        elif ref_type == ComponentType.MARINE_ENGINE:
            things.append(
                f"{ThingType.MARINE_ENGINE.value}.{calculate_inverter_charger_instance(inverter_charger=thing)}"
            )
        elif ref_type == ComponentType.INVERTERCHARGER:
            things.append(
                f"{ThingType.INVERTER.value}.{calculate_inverter_charger_instance(inverter_charger=thing)}"
            )
        return things

    def get_switch_thing(self, config: N2kConfiguration, switch: Circuit):
        # DC
        for dc in config.dc.values():
            circuit = get_associated_circuit(ItemType.DcMeter, dc.id, config)
            if circuit is not None and circuit.control_id == switch.control_id:
                return ComponentReference(
                    component_type=ComponentType.DCMETER, thing=dc
                )

        # AC
        for ac_meter in config.ac.values():
            circuit = next(
                (
                    circuit
                    for line in ac_meter.line.values()
                    if (
                        circuit := get_associated_circuit(
                            ItemType.AcMeter, line.id, config
                        )
                    )
                    is not None
                ),
                None,
            )
            if circuit is not None and circuit.control_id == switch.control_id:
                return ComponentReference(
                    component_type=ComponentType.ACMETER, thing=ac_meter
                )
        # Tanks
        for tank in config.tank.values():
            circuit = get_associated_circuit(ItemType.FluidLevel, tank.id, config)
            if circuit is not None and circuit.control_id == switch.control_id:
                return ComponentReference(component_type=ComponentType.TANK, thing=tank)
        return None

    def _verify_alarm_things(self, alarm_list: AlarmList):
        """
        Verify each alarm contain thing that is part of reported system and remove any alarm that do not.
        """
        alarm_list_copy = copy.deepcopy(alarm_list)
        for id, alarm in list(alarm_list.alarm.items()):
            valid_things = []
            for thing in alarm.things:
                if thing in self.get_latest_empower_system().things:
                    valid_things.append(thing)
            alarm_list.alarm[id].things = valid_things
            if len(valid_things) == 0:
                del alarm_list.alarm[id]
        return alarm_list_copy

    def _verify_engine_alarm_things(self, engine_alarm_list: EngineAlarmList):
        """
        Verify each engine alarm contains things that are part of the latest engine list and remove any alarm that do not.
        """
        engine_alarm_list_copy = copy.deepcopy(engine_alarm_list)
        for id, engine_alarm in list(engine_alarm_list.engine_alarms.items()):
            valid_things = []
            for thing in engine_alarm.things:
                if thing in self.get_latest_engine_list().engines:
                    valid_things.append(thing)
            engine_alarm_list.engine_alarms[id].things = valid_things
            if len(valid_things) == 0:
                del engine_alarm_list.engine_alarms[id]
        return engine_alarm_list_copy

    def post_process_alarm_configuration(
        self, alarm: N2KAlarm, bls_alarms: dict[int, BLSAlarmMapping]
    ) -> Union[N2KAlarm | None]:
        """
        Given config, return BLSAlarms objects which links bls alarm channel with binary logic state
        """
        bls = next(
            (
                bls
                for [_, bls] in bls_alarms.items()
                if bls.alarm_channel == alarm.channel_id
            ),
            None,
        )

        if alarm.severity == eSeverityType.SeveritySIO and bls is not None:
            return None
        return alarm

    def parse_alarm_list(self, alarm_list_str: str) -> list[Alarm]:
        try:
            alarms = []
            alarm_list_json = json.loads(alarm_list_str)
            if JsonKeys.Alarms in alarm_list_json:
                for alarm in alarm_list_json[JsonKeys.Alarms]:
                    alarm_obj = self.parse_alarm(alarm)
                    alarms.append(alarm_obj)
            return alarms
        except Exception as e:
            self._logger.error(f"Failed to parse alarm list: {e}")
            raise

    def parse_alarm(self, alarm_json: dict[str, Any]) -> Alarm:
        try:
            alarm = Alarm()
            map_fields(alarm_json, alarm, ALARM_FIELD_MAP)
            map_enum_fields(self._logger, alarm_json, alarm, ALARM_ENUM_FIELD_MAP)
            return alarm
        except Exception as e:
            self._logger.error(f"Failed to parse alarm: {e}")
            raise

    def process_engine_alarm_from_snapshot(
        self, snapshot_dict: dict[str, dict[str, Any]]
    ) -> None:
        """
        Processes engine alerts from a given snapshot and generates a merged list of engine alerts.

        Args:
            snapshot (nmea2k.SnapshotInstanceIdMap): The snapshot containing engine data.

        """

        latest_engine_alarm_list = self.get_engine_alarms()
        merged_engine_alarm_list = copy.deepcopy(latest_engine_alarm_list)

        latest_engine_config = self.get_engine_config()
        if JsonKeys.ENGINES in snapshot_dict:
            for engine_id, engine_state in snapshot_dict[JsonKeys.ENGINES].items():
                engine_id = int(engine_id.split(".")[1])
                if engine_id in latest_engine_config.devices:
                    prev_discrete_status1 = self._prev_discrete_status1.get(
                        engine_id, None
                    )
                    prev_discrete_status2 = self._prev_discrete_status2.get(
                        engine_id, None
                    )

                    current_discrete_status1 = prev_discrete_status1
                    current_discrete_status2 = prev_discrete_status2

                    if JsonKeys.DISCRETE_STATUS_1 in engine_state:
                        discrete_status_1 = engine_state[JsonKeys.DISCRETE_STATUS_1]
                        self._prev_discrete_status1[engine_id] = discrete_status_1
                        current_discrete_status1 = discrete_status_1

                    if JsonKeys.DISCRETE_STATUS_2 in engine_state:
                        discrete_status_2 = engine_state[JsonKeys.DISCRETE_STATUS_2]
                        self._prev_discrete_status2[engine_id] = discrete_status_2
                        current_discrete_status2 = discrete_status_2

                    # Discrete Status 1
                    if JsonKeys.DISCRETE_STATUS_1 in engine_state:
                        status_alarms = [
                            Constants.checkEngineAlarm,
                            Constants.overTemperatureAlarm,
                            Constants.lowOilPressureAlarm,
                            Constants.lowOilLevelAlarm,
                            Constants.lowFuelPressureAlarm,
                            Constants.lowSystemVoltageAlarm,
                            Constants.lowCoolantLevelAlarm,
                            Constants.waterFlowAlarm,
                            Constants.waterInFuelAlarm,
                            Constants.chargeIndicatorAlarm,
                            Constants.preheatIndicatorAlarm,
                            Constants.highBoostPressureAlarm,
                            Constants.revLimitExceededAlarm,
                            Constants.egrSystemAlarm,
                            Constants.throttlePositionSensorAlarm,
                            # Constants.engineEmergencyStopAlarm
                        ]

                        generate_alarms_from_discrete_status(
                            status_alarms=status_alarms,
                            discrete_status=current_discrete_status1,
                            merged_engine_alert_list=merged_engine_alarm_list,
                            prev_discrete_status1=prev_discrete_status1,
                            prev_discrete_status2=prev_discrete_status2,
                            current_discrete_status1=current_discrete_status1,
                            current_discrete_status2=current_discrete_status2,
                            prev_engine_alert_list=latest_engine_alarm_list,
                            engine_id=engine_id,
                            engine_config=latest_engine_config.devices[engine_id],
                            discrete_status_word=1,
                        )
                    if JsonKeys.DISCRETE_STATUS_2 in engine_state:
                        status_alarms = [
                            Constants.warningLevel1Alarm,
                            Constants.warningLevel2Alarm,
                            Constants.powerReductionAlarm,
                            Constants.maintenanceNeededAlarm,
                            Constants.engineCommErrorAlarm,
                            Constants.subOrSecondaryThrottleAlarm,
                            Constants.neutralStartProtectAlarm,
                            Constants.engineShuttingDownAlarm,
                            Constants.sensorMalfunctionAlarm,
                        ]

                        generate_alarms_from_discrete_status(
                            status_alarms=status_alarms,
                            discrete_status=current_discrete_status2,
                            merged_engine_alert_list=merged_engine_alarm_list,
                            prev_discrete_status1=prev_discrete_status1,
                            prev_discrete_status2=prev_discrete_status2,
                            current_discrete_status1=current_discrete_status1,
                            current_discrete_status2=current_discrete_status2,
                            prev_engine_alert_list=latest_engine_alarm_list,
                            engine_id=engine_id,
                            engine_config=latest_engine_config.devices[engine_id],
                            discrete_status_word=2,
                        )
        if (
            merged_engine_alarm_list.to_alarm_dict()
            != latest_engine_alarm_list.to_alarm_dict()
        ):
            merged_engine_alarm_list = self._verify_engine_alarm_things(
                merged_engine_alarm_list
            )
            self.set_engine_alarms(merged_engine_alarm_list)
