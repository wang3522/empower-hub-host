from ...models.common_enums import (
    eAlarmType,
    ComponentType,
)

from typing import Any, List, Optional, Union
from ...models.empower_system.component_reference import ComponentReference
from ...models.empower_system.alarm_type import AlarmType
from ...models.n2k_configuration.device import DeviceType
from ...models.n2k_configuration.ui_relationship_msg import (
    ItemType,
    RelationshipType,
)

from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.n2k_configuration.engine_configuration import EngineConfiguration
from ...models.n2k_configuration.alarm import Alarm
from .alarm_helpers import get_inverter_charger_alarm_title
from logging import Logger


def process_device_alarms(
    logger: Logger,
    resolved_alarm_channel_id: int,
    config: N2kConfiguration,
    affected_components: List[ComponentReference],
    alarm: Optional[Alarm] = None,
    is_dc_alarm: Optional[bool] = None,
) -> List[ComponentReference]:
    """
    Process device alarms and update affected components.
    This function checks if the alarm is related to device circuits, AC meters, DC meters, inverter chargers, or battery devices(clustered) via dipswitch matching to configuration data.
    If a match is found, it creates a ComponentReference for the relevant component and adds it to the affected components list.
    Args:
        logger: Logger instance for logging errors or information.
        resolved_alarm_channel_id: The resolved channel ID for the alarm.
        config: The N2kConfiguration containing device definitions.
        affected_components: List to which affected components will be added.
        alarm: Optional Alarm object that may contain additional information.
        is_dc_alarm: Optional boolean indicating if the alarm is related to DC.
    Returns:
        List of affected components with device references added if applicable.
    """
    alarm_device_dipswitch = None
    if alarm is not None and alarm.alarm_type == eAlarmType.TypeSleepWarning:
        alarm_device_dipswitch = resolved_alarm_channel_id
    elif not alarm.alarm_type == eAlarmType.Externel:
        logger.warning("Invalid Alarm")
        return affected_components

    if alarm_device_dipswitch is not None:
        # Circuit and circuit loads
        for [key, circuit] in config.circuit.items():
            if circuit.circuit_loads is not None:
                for load in circuit.circuit_loads:
                    if load.channel_address is None:
                        continue
                    if not any(
                        c.component_type == ComponentType.CIRCUIT
                        and c.thing.id.value == key
                        for c in affected_components
                    ):
                        load_channel = load.channel_address >> 8
                        if load_channel == alarm_device_dipswitch:
                            component_reference = ComponentReference(
                                ComponentType.CIRCUIT,
                                thing=circuit,
                            )
                            affected_components.append(component_reference)
        # AC Meters
        for [_, ac_meter] in config.ac.items():
            for [_, ac_line] in ac_meter.line.items():
                if ac_line is not None and ac_line.address is not None:
                    if not any(
                        c.component_type == ComponentType.ACMETER
                        and c.thing.instance.instance == ac_line.instance.instance
                        for c in affected_components
                    ):
                        address = ac_line.address >> 8
                        if address == alarm_device_dipswitch:
                            component_reference = ComponentReference(
                                ComponentType.ACMETER, thing=ac_meter.line[1]
                            )
                            affected_components.append(component_reference)

        # DC Meters
        for [_, dc_meter] in config.dc.items():
            if not any(
                c.component_type == ComponentType.DCMETER
                and c.thing.address == dc_meter.address
                for c in affected_components
            ):
                if dc_meter.address is None:
                    continue
                address = dc_meter.address >> 8
                if address == alarm_device_dipswitch:
                    component_reference = ComponentReference(
                        ComponentType.DCMETER, thing=dc_meter
                    )
                    affected_components.append(component_reference)

    # Inverter Chargers
    for [_, inverter_charger] in config.inverter_charger.items():
        if not any(
            c.component_type == ComponentType.INVERTERCHARGER
            and c.thing.inverter_ac_id == inverter_charger.inverter_ac_id
            and c.thing.charger_ac_id == inverter_charger.charger_ac_id
            for c in affected_components
        ):
            if (resolved_alarm_channel_id >> 8) == inverter_charger.dipswitch and (
                resolved_alarm_channel_id & 0xFF
            ) == inverter_charger.channel_index:
                if inverter_charger.inverter_ac_id.enabled:
                    title = get_inverter_charger_alarm_title(
                        config, inverter_charger.inverter_ac_id.id
                    )
                    if title:
                        alarm.title = title
                component_reference = ComponentReference(
                    ComponentType.INVERTERCHARGER, thing=inverter_charger
                )
                affected_components.append(component_reference)

    # Battery Device Alarms
    for [_, device] in config.device.items():
        if (
            device.dipswitch is None
            or device.device_type is not DeviceType.Battery
            or (resolved_alarm_channel_id >> 8) != device.dipswitch
        ):
            continue
        address = device.dipswitch

        relationship = next(
            (
                rel
                for rel in config.ui_relationships
                if rel.primary_type == ItemType.DcMeter
                and rel.secondary_type == ItemType.DcMeter
                and (rel.secondary_config_address >> 8) == device.dipswitch
                and rel.relationship_type == RelationshipType.Normal
            ),
            None,
        )
        if relationship is not None:
            dc = next(
                (
                    dc
                    for [_, dc] in config.dc.items()
                    if dc.id == relationship.primary_id
                ),
                None,
            )
            if dc is not None and not any(
                c.component_type == ComponentType.DCMETER
                and c.thing.address == dc.address
                for c in affected_components
            ):
                component_reference = ComponentReference(
                    ComponentType.DCMETER, thing=dc
                )
                affected_components.append(component_reference)

    # If no component reference was added and is_dc_alarm is True, try again with resolved_alarm_channel_id -= 3
    # This addresses edge case where Combi reports incorrect ChannelIndex,
    if not affected_components and is_dc_alarm:
        resolved_alarm_channel_id += 3
        return process_device_alarms(
            logger,
            resolved_alarm_channel_id,
            config,
            affected_components,
            alarm,
            False,
        )
    return affected_components


def process_dc_meter_alarms(
    logger: Logger,
    resolved_alarm_channel_id: int,
    config: N2kConfiguration,
    affected_components: List[ComponentReference],
    alarm: Optional[Alarm] = None,
    is_dc_alarm: Optional[bool] = None,
) -> List[ComponentReference]:
    """
    Process DC meter alarms and update affected components.
    This function checks if the alarm is related to DC meters, by matching unique id of alarm, to alarms in config of device.
    Secondly, it checks if the alarm channel id matches the address of any DC meter in the configuration.
    If a match is found, it creates a ComponentReference for the DC meter and adds
    it to the affected components list.
    Args:
        logger: Logger instance for logging errors or information.
        resolved_alarm_channel_id: The resolved channel ID for the alarm.
        config: The N2kConfiguration containing DC meter definitions.
        affected_components: List to which affected components will be added.
        alarm: Optional Alarm object that may contain additional information.
        is_dc_alarm: Optional boolean indicating if the alarm is related to DC.
    Returns:
        List of affected components with DC meter references added if applicable.
    """
    for [_, dc] in config.dc.items():
        if any(
            alarm_config is not None
            and alarm_config.enabled
            and alarm_config.id > 0
            and alarm_config.id == alarm.unique_id
            for alarm_config in [
                dc.high_voltage,
                dc.low_voltage,
                dc.very_low_voltage,
                dc.high_limit,
                dc.low_limit,
                dc.very_low_limit,
            ]
        ) or (
            resolved_alarm_channel_id is not None
            and is_dc_alarm
            and dc.address == resolved_alarm_channel_id
        ):
            component_reference = ComponentReference(ComponentType.DCMETER, thing=dc)
            affected_components.append(component_reference)
    return affected_components


def process_ac_meter_alarms(
    logger: Logger,
    resolved_alarm_channel_id: int,
    config: N2kConfiguration,
    affected_components: List[ComponentReference],
    alarm: Optional[Alarm] = None,
    is_dc_alarm: Optional[bool] = None,
) -> List[ComponentReference]:
    """
    Process AC meter alarms and update affected components.
    This function checks if the alarm is related to AC meters by matching alarm properties to configuration data for AC lines.
    If a match is found, it creates a ComponentReference for the AC meter line and adds it to the affected components list.
    Args:
        logger: Logger instance for logging errors or information.
        resolved_alarm_channel_id: The resolved channel ID for the alarm.
        config: The N2kConfiguration containing AC meter definitions.
        affected_components: List to which affected components will be added.
        alarm: Optional Alarm object that may contain additional information.
        is_dc_alarm: Optional boolean indicating if the alarm is related to DC.
    Returns:
        List of affected components with AC meter references added if applicable.
    """
    for [_, ac] in config.ac.items():
        for [_, line] in ac.line.items():
            if any(
                alarm_config is not None
                and alarm_config.enabled
                and alarm_config.id == alarm.unique_id
                for alarm_config in [
                    line.high_limit,
                    line.low_limit,
                    line.very_high_limit,
                    line.high_voltage,
                    line.frequency,
                ]
            ) or (
                resolved_alarm_channel_id is not None
                and not is_dc_alarm
                and line.address == resolved_alarm_channel_id
            ):
                component_reference = ComponentReference(
                    ComponentType.ACMETER, thing=line
                )
                affected_components.append(component_reference)
    return affected_components


def process_tank_alarms(
    logger: Logger,
    resolved_alarm_channel_id: int,
    config: N2kConfiguration,
    affected_components: List[ComponentReference],
    alarm: Optional[Alarm] = None,
    is_dc_alarm: Optional[bool] = None,
) -> List[ComponentReference]:
    """
    Process tank alarms and update affected components.
    This function checks if the alarm is related to tanks by matching alarm properties to configuration data for tanks.
    If a match is found, it creates a ComponentReference for the tank and adds it to the affected components list.
    Args:
        logger: Logger instance for logging errors or information.
        resolved_alarm_channel_id: The resolved channel ID for the alarm.
        config: The N2kConfiguration containing tank definitions.
        affected_components: List to which affected components will be added.
        alarm: Optional Alarm object that may contain additional information.
        is_dc_alarm: Optional boolean indicating if the alarm is related to DC.
    Returns:
        List of affected components with tank references added if applicable.
    """
    for [_, tank] in config.tank.items():
        if any(
            alarm_config is not None
            and alarm_config.enabled
            and alarm_config.id > 0
            and alarm_config.id == alarm.unique_id
            for alarm_config in [
                tank.very_low_limit,
                tank.low_limit,
                tank.high_limit,
                tank.very_high_limit,
            ]
        ) or (
            (
                resolved_alarm_channel_id is not None
                and tank.address == resolved_alarm_channel_id
            )
        ):
            component_reference = ComponentReference(ComponentType.TANK, thing=tank)
            affected_components.append(component_reference)
    return affected_components


def process_circuit_load_alarms(
    logger: Logger,
    resolved_alarm_channel_id: int,
    config: N2kConfiguration,
    affected_components: List[ComponentReference],
    alarm: Optional[Alarm] = None,
    is_dc_alarm: Optional[bool] = None,
) -> List[ComponentReference]:
    """
    Process circuit load alarms and update affected components.
    This function checks if the alarm is related to circuit loads by matching the resolved alarm channel ID to the channel address of circuit loads in the configuration.
    If a match is found, it creates a ComponentReference for the circuit and adds it to the affected components list.
    Args:
        logger: Logger instance for logging errors or information.
        resolved_alarm_channel_id: The resolved channel ID for the alarm.
        config: The N2kConfiguration containing circuit definitions.
        affected_components: List to which affected components will be added.
        alarm: Optional Alarm object that may contain additional information.
        is_dc_alarm: Optional boolean indicating if the alarm is related to DC.
    Returns:
        List of affected components with circuit references added if applicable.
    """
    if resolved_alarm_channel_id is not None:
        for [_, circuit] in config.circuit.items():
            if circuit.circuit_loads is not None:
                for load in circuit.circuit_loads:
                    if (
                        load.level > 0
                        and load.channel_address == resolved_alarm_channel_id
                    ):
                        component_reference = ComponentReference(
                            ComponentType.CIRCUIT, thing=circuit
                        )
                        affected_components.append(component_reference)
    return affected_components


def process_bls_alarms(
    logger: Logger,
    config: N2kConfiguration,
    affected_components: List[ComponentReference],
    alarm: Optional[Alarm] = None,
    resolved_alarm_channel_id: Optional[int] = None,
    is_dc_alarm: Optional[bool] = None,
) -> List[ComponentReference]:
    """
    Process BLS (Binary Logic State) alarms and update affected components.
    This function checks if the alarm is related to a BLS mapping by matching the alarm channel to BLS alarm mappings in the configuration.
    If a match is found, it creates a ComponentReference for the BLS and adds it to the affected components list.
    It also adds related AC meters, DC meters, tanks, or circuits based on UI relationships.
    Args:
        logger: Logger instance for logging errors or information.
        config: The N2kConfiguration containing BLS alarm mappings and UI relationships.
        affected_components: List to which affected components will be added.
        alarm: Optional Alarm object that may contain additional information.
        resolved_alarm_channel_id: Optional resolved channel ID for the alarm.
        is_dc_alarm: Optional boolean indicating if the alarm is related to DC.
    Returns:
        List of affected components with BLS and related references added if applicable.
    """
    bls = next(
        (
            bls.bls
            for [_, bls] in config.bls_alarm_mappings.items()
            if bls.alarm_channel == alarm.channel_id
        ),
        None,
    )
    if bls is not None:
        component_reference = ComponentReference(ComponentType.BINARYLOGICSTATE, bls)
        affected_components.append(component_reference)
        for rel in config.ui_relationships:
            if (
                rel.secondary_type == ItemType.BinaryLogicState
                and rel.secondary_config_address == bls.address
                and rel.relationship_type
                in (
                    RelationshipType.Normal,
                    RelationshipType.Duplicates,
                )
            ):
                if rel.primary_type == ItemType.AcMeter:
                    ac_meter = next(
                        (
                            ac
                            for [_, ac] in config.ac.items()
                            if ac.line[1].id == rel.primary_id
                        ),
                        None,
                    )
                    if ac_meter is not None:
                        component_reference = ComponentReference(
                            ComponentType.ACMETER, ac_meter.line[1]
                        )
                        affected_components.append(component_reference)
                elif rel.primary_type == ItemType.DcMeter:
                    dc_meter = next(
                        (
                            dc
                            for [_, dc] in config.dc.items()
                            if dc.id == rel.primary_id
                        ),
                        None,
                    )
                    if dc_meter is not None:
                        component_reference = ComponentReference(
                            ComponentType.DCMETER, dc_meter
                        )
                        affected_components.append(component_reference)
                elif rel.primary_type == ItemType.FluidLevel:
                    tank = next(
                        (
                            tank
                            for [_, tank] in config.tank.items()
                            if tank.id == rel.primary_id
                        ),
                        None,
                    )
                    if tank is not None:
                        component_reference = ComponentReference(
                            ComponentType.TANK, tank
                        )
                        affected_components.append(component_reference)
                elif rel.primary_type == ItemType.Circuit:
                    circuit = next(
                        (
                            circuit
                            for [_, circuit] in config.circuit.items()
                            if circuit.control_id == rel.primary_config_address
                        ),
                        None,
                    )
                    if circuit is not None:
                        component_reference = ComponentReference(
                            ComponentType.CIRCUIT, circuit
                        )
                        affected_components.append(component_reference)
    return affected_components


def process_smartcraft_alarms(
    logger: Logger,
    resolved_alarm_channel_id: int,
    config: EngineConfiguration,
    affected_components: List[ComponentReference],
    alarm: Optional[Alarm] = None,
    is_dc_alarm: Optional[bool] = None,
) -> List[ComponentReference]:
    """
    Process SmartCraft engine alarms and update affected components.
    This function checks if the alarm is related to a SmartCraft engine by mapping the resolved alarm channel ID to an engine instance name and matching it to engine devices in the configuration.
    If a match is found, it creates a ComponentReference for the marine engine and adds it to the affected components list.
    Args:
        logger: Logger instance for logging errors or information.
        resolved_alarm_channel_id: The resolved channel ID for the alarm.
        config: The EngineConfiguration containing engine device definitions.
        affected_components: List to which affected components will be added.
        alarm: Optional Alarm object that may contain additional information.
        is_dc_alarm: Optional boolean indicating if the alarm is related to DC.
    Returns:
        List of affected components with marine engine references added if applicable.
    """
    engine_instance = resolved_alarm_channel_id & 0x00FF
    engine_name = map_sc_engine_instance_to_engine_name(engine_instance)
    if engine_name is not None:
        engine = next(
            (
                engine
                for [_, engine] in config.devices.items()
                if engine.name_utf8 == engine_name
            ),
            None,
        )
        if not engine is None:
            component_reference = ComponentReference(
                ComponentType.MARINE_ENGINE, thing=engine
            )
            affected_components.append(component_reference)
    return affected_components


def map_sc_engine_instance_to_engine_name(engine_instance: int) -> Optional[str]:
    """
    Map a SmartCraft engine instance number to its engine name string.
    Args:
        engine_instance: The engine instance number (int).
    Returns:
        The engine name string if found, otherwise None.
    """
    smartcraft_options = {
        0: "StarboardEngine",
        1: "PortEngine",
        2: "StartboardInnerEngine",
        3: "PortInnerEngine",
    }
    if engine_instance in smartcraft_options:
        return smartcraft_options[engine_instance]
    return None
