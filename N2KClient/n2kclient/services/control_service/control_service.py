import logging
from time import sleep
from typing import Callable

from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.devices import N2kDevices
from ...models.constants import Constants
from ...services.control_service.control_service_helpers import (
    get_circuit_config,
    get_circuit_device,
    is_circuit_on,
    determine_circuit_control_operation,
    control_circuit_switch,
    control_circuit_level,
)


class ControlService:
    """Service for controlling N2K devices"""

    _logger = logging.getLogger(Constants.N2K_CONTROL_SERVICE)

    def __init__(
        self,
        get_config_func: Callable[[], N2kConfiguration],
        get_devices_func: Callable[[], N2kDevices],
        send_control_func: Callable[[dict], str],
    ):
        """
        Args:
            get_config_func: Returns the latest N2kConfiguration.
            get_devices_func: Returns the latest N2kDevices.
            send_control_func: Sends a control request, returns JSON string response.
        """
        self.get_config = get_config_func
        self.get_devices = get_devices_func
        self.send_control = send_control_func

    #####################################
    # Circuit Control
    #####################################

    def set_circuit_power_state(self, runtime_id: int, target_on: bool) -> bool:
        try:
            config = self.get_config()
            devices = self.get_devices()
            circuit_config = get_circuit_config(config, runtime_id, logger=self._logger)
            if not circuit_config:
                return False

            _, circuit_device = get_circuit_device(devices, circuit_config)
            current_is_on = is_circuit_on(circuit_device)
            self._logger.debug(
                "Circuit %s current state: %s", runtime_id, current_is_on
            )

            throw_type = determine_circuit_control_operation(
                circuit_config, target_on, current_is_on
            )
            if throw_type is None:
                self._logger.debug(
                    "Circuit %s already at target state %s", runtime_id, target_on
                )
                return True

            return control_circuit_switch(
                self.send_control,
                circuit_config.id.value,
                throw_type,
                logger=self._logger,
            )
        except Exception as e:
            self._logger.error(
                "Failed to set circuit %s to %s: %s", runtime_id, target_on, e
            )
            return False

    def set_circuit_level(self, runtime_id: int, target_level: int) -> bool:
        """Set the dimming level of a circuit (0-100)."""

        if not (0 <= target_level <= 100):
            self._logger.error(
                "Invalid target level %s for circuit %s", target_level, runtime_id
            )
            return False
        try:
            config = self.get_config()
            circuit_config = get_circuit_config(config, runtime_id, logger=self._logger)
            if not circuit_config or not circuit_config.dimmable:
                self._logger.error("Circuit %s is not dimmable", runtime_id)
                return False

            return control_circuit_level(
                self.send_control,
                circuit_config.id.value,
                target_level,
                logger=self._logger,
            )
        except Exception as e:
            self._logger.error(
                "Failed to set level for circuit %s to %s: %s",
                runtime_id,
                target_level,
                e,
            )
            return False
