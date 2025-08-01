import json
from logging import Logger
from time import sleep
from typing import Optional, Tuple
from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.devices import N2kDevices, N2kDevice
from ...models.constants import JsonKeys
from ...models.common_enums import CircuitStates, ThrowType, ControlRequest
from ...models.n2k_configuration.circuit import Circuit, SwitchType

CONTROL_SLEEP_TIME = 0.1


def get_circuit_config(
    config: N2kConfiguration, runtime_id: int, logger: Optional[Logger] = None
) -> Optional[Circuit]:
    circuit_config = config.circuit.get(runtime_id)
    if circuit_config is None and logger:
        logger.error("No circuit found for runtime_id %s", runtime_id)
    return circuit_config


def get_circuit_device(
    devices: N2kDevices, circuit_config: Circuit
) -> Tuple[str, Optional[N2kDevice]]:
    circuit_id = f"{JsonKeys.CIRCUIT}.{circuit_config.id.value}"
    return circuit_id, devices.devices.get(circuit_id)


def is_circuit_on(circuit_device: Optional[N2kDevice]) -> bool:
    if not circuit_device:
        return False
    return circuit_device.channels.get(CircuitStates.Level, 0) > 0


def determine_circuit_control_operation(
    circuit_config: Circuit, target_on: bool, current_is_on: bool
) -> Optional[ThrowType]:
    if target_on == current_is_on:
        return None
    if circuit_config.has_complement:
        return ThrowType.DoubleThrow if not target_on else ThrowType.SingleThrow
    switch_type = circuit_config.switch_type
    if switch_type in (
        SwitchType.DimLinearUp,
        SwitchType.DimExponentialUp,
        SwitchType.LatchOn,
        SwitchType.MomentaryOn,
    ):
        if not target_on:
            raise Exception(
                f"Cannot turn OFF circuit {circuit_config.id.value} with switch type {switch_type}"
            )
    elif switch_type in (
        SwitchType.DimLinearDown,
        SwitchType.DimExponentialDown,
        SwitchType.LatchOff,
        SwitchType.MomentaryOff,
    ):
        if target_on:
            raise Exception(
                f"Cannot turn ON circuit {circuit_config.id.value} with switch type {switch_type}"
            )
    return ThrowType.SingleThrow


def control_circuit_switch(
    send_control, circuit_id: str, throw_type: ThrowType, logger=None
) -> bool:
    if not send_and_check(
        send_control,
        {
            JsonKeys.TYPE: ControlRequest.Activate.value,
            JsonKeys.ID: circuit_id,
            JsonKeys.THROW_TYPE: throw_type.value,
        },
        logger=logger,
    ):
        return False
    sleep(CONTROL_SLEEP_TIME)
    return send_and_check(
        send_control,
        {JsonKeys.TYPE: ControlRequest.Release.value, JsonKeys.ID: circuit_id},
        logger=logger,
    )


def control_circuit_level(
    send_control, circuit_id: str, target_level: int, logger=None
) -> bool:
    if not send_and_check(
        send_control,
        {
            JsonKeys.TYPE: ControlRequest.SetAbsolute.value,
            JsonKeys.ID: circuit_id,
            JsonKeys.LEVEL: target_level,
        },
        logger=logger,
    ):
        return False
    sleep(CONTROL_SLEEP_TIME)
    return send_and_check(
        send_control,
        {JsonKeys.TYPE: ControlRequest.Release.value, JsonKeys.ID: circuit_id},
        logger=logger,
    )


def send_and_check(send_control, request: dict, logger=None) -> bool:
    response = send_control(json.dumps(request))
    try:
        response_json: dict = json.loads(response)
        result = response_json.get(JsonKeys.Result)
        return result == JsonKeys.OK
    except Exception as e:
        if logger:
            logger.error("Invalid response from control request: %s (%s)", response, e)
        return False
