import logging
import os
import threading
from typing import Any, Dict, Optional
from HubInterfaces.HubInterface.N2KClient.client import N2KClient
from modules.thingsboard import client
from modules.thingsboard.location import LocationService
import reactivex as rx
from ..common.tb_constants import TBConstants
import json
from HubInterfaces.HubInterface.N2KClient.models.state import N2KState
from HubInterfaces.HubInterface.N2KClient.models.channel import N2KChannel
import re
from modules.config import (
    telemetry_filter_patterns
)

class EmpowerService:
    _logger: logging.Logger
    n2k_client: N2KClient
    thingsboard_client: client.ThingsBoardClient
    location_service: LocationService
    last_state_attrs = {}
    last_telemetry = {}
    telemetry_consent = {}

    _service_init_disposable: list[rx.abc.DisposableBase]

    _stdout = ""
    _stdin = ""
    _stderr = ""

    def __init__(self):
        self._logger = logging.getLogger("EmpowerService")
        self.n2k_client = N2KClient()
        self.thingsboard_client = client.ThingsBoardClient()
        self.location_service = LocationService(
            self.thingsboard_client, self.n2k_client
        )
        self._service_init_disposable = []

        consent = self.thingsboard_client.subscribe_all_attributes(None)

        def callback(result, *args):
            self._logger.info(f"received attribute update kvp: {result}")
            if not isinstance(result, dict):
                return
            key = list(result.keys())[0]
            state = result[key]

            for thing_id in self._latest_cloud_config.things:
                thing = self._latest_cloud_config.things[thing_id]
                for channel_id in thing.channels:
                    if channel_id == key:
                        channel = thing.channels[channel_id]
                        self.__control_component(thing, channel, state)

        self._service_init_disposable.append(consent.subscribe(callback))

        def __publish_state_changes(state: N2KState):
            for channel in state.channels:
                if any(
                    re.match(pattern, channel)
                    for pattern in telemetry_filter_patterns
                )
        
    def register_rpc_callbacks(self):
        """
        Register the rpc related commands to the thingsboard client.
        """
        self.thingsboard_client.set_rpc_handler("control", self.__control_rpc_handler)

    def _get_telemetry_consent(self):
        """
        Reads telemetry consent data from a local file.

        Checks if the file exists, then reads and parses it as JSON. Logs a warning if
        the file is invalid or missing.

        Returns:
            dict or None: Parsed telemetry consent data, or None if unavailable.
        """
        if os.path.exists(TBConstants.TELEMETRY_CONSET_PATH):
            try:
                with open(
                    TBConstants.TELEMETRY_CONSET_PATH, "r", encoding="utf-8"
                ) as file:
                    return json.load(file)
            except Exception as error:
                self._logger.warning("Local telemetry consent is invalid or not found")
                self._logger.error(error)
        else:
            self._logger.info("Could not find telemetry consent file")
        return None

    def _set_consents(self, val: Optional[Dict[str, Any]]) -> None:
        try:
            if val is None:
                return
            telemetry_consent = val.get(TBConstants.telemetryConsentEnabled)

            if telemetry_consent is not None:
                self.current_telemetry_consent = telemetry_consent
                self._logger.info(f"Telemetry consent set to {telemetry_consent}")
                try:
                    should_update = True
                    # Write to file here
                    if os.path.exists(TBConstants.TELEMETRY_CONSET_PATH):
                        with open(
                            TBConstants.TELEMETRY_CONSET_PATH, "r", encoding="utf-8"
                        ) as telemetry_consent_file_read:
                            telemetry_file_content = json.load(
                                telemetry_consent_file_read
                            )
                            if telemetry_file_content == telemetry_consent:
                                should_update = False

                    if should_update:
                        with open(
                            TBConstants.TELEMETRY_CONSET_PATH, "w", encoding="utf-8"
                        ) as telemetry_consent_file:
                            telemetry_consent_file.write(json.dumps(telemetry_consent))
                            self._logger.info(
                                "Wrote telemetry consent file with %s",
                                telemetry_consent,
                            )
                    else:
                        self._logger.debug("Telemetry consent file has not changed")
                except Exception as err:
                    self._logger.error("not able to write local consent file %s", err)

        except (KeyError, TypeError, ValueError) as e:
            self._logger.error(f"Error setting consents: {e}")

    def run(self):
        self._logger.info("Starting Empower Service")
        self._logger.debug("Starting ThingsBoard client...")
        thingsboard_connect_thread = threading.Thread(
            target=self.thingsboard_client.connect, name="Thingsboard connect thread"
        )
        thingsboard_connect_thread.start()
        self._logger.debug("Starting location service")
        self.location_service.start()

        if self.thingsboard_client._is_connected_internal.value:
            self.thingsboard_client.subscribe_attribute(
                TBConstants.telemetryConsentEnabled, None
            ).subscribe(self._set_consents)
            # Create Start
            self.n2k_client.start()
