from collections.abc import Callable
import json
import logging
import threading
from typing import Any

from ...models.common_enums import N2kDeviceType

from ...models.devices import N2kDevices

from ...models.n2k_configuration.engine_configuration import EngineConfiguration

from ..dbus_proxy_service.dbus_proxy import DbusProxyService
from ...models.constants import Constants, JsonKeys
from ...util.settings_util import SettingsUtil


class SnapshotService:
    """
    Service for managing snapshots of the N2KClient State.
    """

    _snapshot_interval = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.WORKER_KEY,
        Constants.SNAPSHOT_INTERVAL_KEY,
        default_value=60,
    )

    def __init__(
        self,
        dbus_proxy: DbusProxyService,
        lock: threading.Lock,
        get_latest_devices: Callable[[], N2kDevices],
        set_devices: Callable[[N2kDevices], None],
        get_latest_engine_config: Callable[[], EngineConfiguration],
        process_engine_alarms_from_snapshot: Callable[[dict[str, Any]], None],
    ):
        """
        Initialize the SnapshotService.
        """
        self._dbus_proxy = dbus_proxy
        self.lock = lock
        self._logger = logging.getLogger(__name__)
        self._get_latest_devices = get_latest_devices
        self._get_latest_engine_config = get_latest_engine_config
        self._set_devices = set_devices
        self._process_engine_alarms_from_snapshot = process_engine_alarms_from_snapshot

        self._set_periodic_snapshot_timer()

    def snapshot_handler(self, snapshot_json: str):
        """
        Handle a received snapshot JSON string.
        Parse the JSON and update device states accordingly. Also processes engine alarms from the snapshot.
        Also restarts the periodic snapshot timer.
        Args:
            snapshot_json: JSON string representing the snapshot.
        """
        try:
            self._logger.info("Received snapshot")
            self._start_snapshot_timer()
            snapshot_dict: dict[str, dict[str, Any]] = json.loads(snapshot_json)

            latest_engine_config = self._get_latest_engine_config()
            if latest_engine_config:
                self._process_engine_alarms_from_snapshot(snapshot_dict)

            state_update = self._process_state_from_snapshot(snapshot_dict)
            self._merge_state_update(state_update)
        except Exception as e:
            self._logger.error(f"Failed to handle snapshot: {e}")
            return

    def _process_state_from_snapshot(self, snapshot_dict: dict[str, dict[str, Any]]):
        """
        Process state information from the snapshot dictionary.
        Extracts state updates for various device types from the snapshot dictionary.
        Args:
            snapshot_dict: The snapshot dictionary containing state information.

        Returns:
            A dictionary mapping device IDs to their state updates.
        """
        state_update = {}
        # Circuits
        if JsonKeys.CIRCUITS in snapshot_dict:
            for circuit_id, circuit_state in snapshot_dict[JsonKeys.CIRCUITS].items():
                state_update[circuit_id] = circuit_state

        # Tanks
        if JsonKeys.TANKS in snapshot_dict:
            for tank_id, tank_state in snapshot_dict[JsonKeys.TANKS].items():
                state_update[tank_id] = tank_state

        # Engines
        if JsonKeys.ENGINES in snapshot_dict:
            for engine_id, engine_state in snapshot_dict[JsonKeys.ENGINES].items():
                state_update[engine_id] = engine_state
        # AC
        if JsonKeys.AC in snapshot_dict:
            for ac_id, ac_state in snapshot_dict[JsonKeys.AC].items():
                state_update[ac_id] = ac_state

        # DC
        if JsonKeys.DC in snapshot_dict:
            for dc_id, dc_state in snapshot_dict[JsonKeys.DC].items():
                state_update[dc_id] = dc_state

        # Hvacs
        if JsonKeys.HVACS in snapshot_dict:
            for hvac_id, hvac_state in snapshot_dict[JsonKeys.HVACS].items():
                state_update[hvac_id] = hvac_state

        # InverterChargers
        if JsonKeys.INVERTER_CHARGERS in snapshot_dict:
            for inverter_charger_id, inverter_state in snapshot_dict[
                JsonKeys.INVERTER_CHARGERS
            ].items():
                state_update[inverter_charger_id] = inverter_state

        # GNSS
        if JsonKeys.GNSS in snapshot_dict:
            for gnss_id, gnss_state in snapshot_dict[JsonKeys.GNSS].items():
                state_update[gnss_id] = gnss_state

        # Binary Logic State
        if JsonKeys.BINARY_LOGIC_STATE in snapshot_dict:
            for bls_id, logic_state in snapshot_dict[
                JsonKeys.BINARY_LOGIC_STATE
            ].items():
                state_update[bls_id] = logic_state
        return state_update

    def _merge_state_update(self, state_updates: dict[str, dict[str, Any]]):
        """
        Merge state updates into the current device list. State updates for engine devices and non-engine devices update separate lists.
        ACLines within AC devices are handled specially to keep line data together.
        Args:
            state_updates: A dictionary mapping device IDs to their state updates.
        """
        with self.lock:
            device_list_copy = self._get_latest_devices()
            for id, state_update in state_updates.items():
                if id in device_list_copy.devices:
                    # Devices of type AC contain multiple AC Lines,
                    # We want to keep ACLine data together within same device, but each lines data accessable by knowing the line ID
                    # For this reason, we are creating channels within the AC device named as {channel_id}.{line_id}
                    if device_list_copy.devices[id].type == N2kDeviceType.AC:
                        lines: dict[int, dict[str, any]] = state_update.get(
                            "AClines", {}
                        )
                        if lines is not None:
                            for line_id, line_value in lines.items():
                                for channel_id, value in line_value.items():
                                    device_list_copy.devices[id].update_channel(
                                        f"{channel_id}.{int(line_id)}", value
                                    )
                    else:
                        for channel_id, value in state_update.items():
                            device_list_copy.devices[id].update_channel(
                                channel_id, value
                            )
                elif id in device_list_copy.engine_devices:
                    for channel_id, value in state_update.items():
                        device_list_copy.engine_devices[id].update_channel(
                            channel_id, value
                        )
            self._set_devices(device_list_copy)

    def _set_periodic_snapshot_timer(self):
        """
        Set a timer to periodically request a snapshot.
        This ensures that state is up to date + dbus connection is alive, if we haven't received a snapshot in a while.
        """
        self._periodic_snapshot_timer = threading.Timer(
            self._snapshot_interval, self._single_snapshot
        )

    def _start_snapshot_timer(self):
        """
        Start a timer to periodically request a snapshot.
        """
        try:
            # Only cancel if timer exists and is alive
            if (
                hasattr(self, "_periodic_snapshot_timer")
                and self._periodic_snapshot_timer.is_alive()
            ):
                self._periodic_snapshot_timer.cancel()
            self._set_periodic_snapshot_timer()
            self._periodic_snapshot_timer.start()
        except Exception as e:
            self._logger.error(f"Error starting snapshot timer: {e}")

    def _single_snapshot(self):
        """
        Request a single snapshot from the host.
        """
        try:
            snapshot = self._dbus_proxy.single_snapshot()
            self.snapshot_handler(snapshot)
        except Exception as e:
            self._logger.error(f"Error getting single snapshot: {e}")
