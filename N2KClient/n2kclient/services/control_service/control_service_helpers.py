"""
Helper functions for N2K circuit control operations.

This module provides utility functions for:
- Finding and validating circuit configurations
- Determining circuit states and control operations
- Sending control commands to N2K devices
- Managing switch types and throw operations
"""

from logging import Logger
from time import sleep
from typing import Optional, Tuple
from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.devices import N2kDevices, N2kDevice
from ...models.constants import JsonKeys
from ...models.common_enums import CircuitStates, ThrowType, ControlRequest
from ...models.n2k_configuration.circuit import Circuit, SwitchType
from ...util.common_utils import send_and_validate_response

# Sleep time between control operations to allow device processing
CONTROL_SLEEP_TIME = 0.1


def get_circuit_config(
    config: N2kConfiguration, runtime_id: int, logger: Optional[Logger] = None
) -> Optional[Circuit]:
    """
    Retrieve circuit configuration by runtime ID.

    Args:
        config: The N2K configuration containing circuit definitions
        runtime_id: The runtime identifier for the circuit
        logger: Optional logger for error reporting

    Returns:
        Circuit configuration if found, None otherwise
    """
    circuit_config = config.circuit.get(runtime_id)
    if circuit_config is None and logger:
        logger.error("No circuit found for runtime_id %s", runtime_id)
    return circuit_config


def get_circuit_device(
    devices: N2kDevices, circuit_config: Circuit
) -> Tuple[str, Optional[N2kDevice]]:
    """
    Get the device associated with a circuit configuration.

    Args:
        devices: Collection of N2K devices
        circuit_config: Circuit configuration to find device for

    Returns:
        Tuple of (circuit_id_string, device_object_or_None)
    """
    circuit_id = f"{JsonKeys.CIRCUITS}.{circuit_config.id.value}"
    return circuit_id, devices.devices.get(circuit_id)


def is_circuit_on(circuit_device: Optional[N2kDevice]) -> bool:
    """
    Determine if a circuit is currently on/active.

    A circuit is considered "on" if its level is greater than 0.

    Args:
        circuit_device: The N2K device representing the circuit

    Returns:
        True if circuit is on (level > 0), False otherwise
    """
    return circuit_device.channels.get(CircuitStates.Level, 0) > 0


def determine_circuit_control_operation(
    circuit_config: Circuit, target_on: bool, current_is_on: bool
) -> Optional[ThrowType]:
    """
    Determine what type of control operation is needed to reach target state.

    Analyzes the circuit configuration and current state to determine if a
    single throw, double throw, or no operation is needed.

    Args:
        circuit_config: Circuit configuration with switch type and complement info
        target_on: Desired on/off state
        current_is_on: Current on/off state

    Returns:
        ThrowType for the operation needed, or None if already at target state

    Raises:
        Exception: If the switch type cannot perform the requested operation
    """
    if target_on == current_is_on:
        return None

    # Handle circuits with complement (can switch between two states)
    if circuit_config.has_complement:
        return ThrowType.DoubleThrow if not target_on else ThrowType.SingleThrow

    # Handle switch types that can only turn ON
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

    # Handle switch types that can only turn OFF
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
    send_control, circuit_id: int, throw_type: ThrowType, logger=None
) -> bool:
    """
    Control a circuit switch by activating and then releasing it.

    Sends an activate command followed by a release command with a brief delay.
    This simulates pressing and releasing a physical switch.

    Args:
        send_control: Function to send control commands
        circuit_id: ID of the circuit to control
        throw_type: Type of throw operation (single/double)
        logger: Optional logger for error reporting

    Returns:
        True if both activate and release commands succeeded, False otherwise
    """
    if not send_and_validate_response(
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
    return send_and_validate_response(
        send_control,
        {JsonKeys.TYPE: ControlRequest.Release.value, JsonKeys.ID: circuit_id},
        logger=logger,
    )


def control_circuit_level(
    send_control, circuit_id: int, target_level: int, logger=None
) -> bool:
    """
    Set the dimming level of a circuit.

    Sends a SetAbsolute command to set the circuit to a specific level,
    followed by a Release command.

    Args:
        send_control: Function to send control commands
        circuit_id: ID of the circuit to control
        target_level: Desired level (0-100)
        logger: Optional logger for error reporting

    Returns:
        True if both set and release commands succeeded, False otherwise
    """
    if not send_and_validate_response(
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
    return send_and_validate_response(
        send_control,
        {JsonKeys.TYPE: ControlRequest.Release.value, JsonKeys.ID: circuit_id},
        logger=logger,
    )
