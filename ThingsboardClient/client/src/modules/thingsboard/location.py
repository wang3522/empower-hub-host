import copy
import re
import threading
import time
import os
from typing import Any, Dict, Optional
import logging
import json
import reactivex as rx
import gpsd
from n2k_client.client import N2kClient
from n2k_client.models import ChannelStateChange
from n2k_client.models.constants import Constants
from n2k_client.util.geo_util import GeoUtil
from n2k_client.util.setting_util import SettingsUtil
from n2k_client.models.configuration import N2kConfiguration
from n2k_client.models.location_state import LocationState
from n2k_client.models.alarm import AlarmSeverity, AlarmState
from .models.geo_status import GeoStatus
from .models.geofence import GeoPoint, Geofence

# pylint: disable=relative-beyond-top-level
from ..thingsboard import client
from ..config import location_filter_pattern, location_priority_sources
from ..common.tb_constants import TBConstants
from ..psv.psv_client import configure_update

# Cloud publish interval in seconds
LOCATION_CLOUD_PUBLISH_INTERVAL = SettingsUtil.get_setting(
    Constants.GNSS,
    Constants.LOCATION,
    Constants.CLOUD_PUBLISH_INTERVAL,
    default_value=600,
)
# number of updates to flush (i.e. if any one gps thing has 20 updates, flush all)
LOCATION_FLUSH_MAX_UPDATES = SettingsUtil.get_setting(
    Constants.GNSS, Constants.LOCATION, Constants.FLUSH_MAX_UPDATES, default_value=20
)
# GPSD update interval in seconds
LOCATION_GPSD_UPDATE_INTERVAL = SettingsUtil.get_setting(
    Constants.GNSS, Constants.LOCATION, Constants.GPSD_UPDATE_INTERVAL, default_value=10
)
# Minimum distance in meters
MINIMUM_DISTANCE = SettingsUtil.get_setting(
    Constants.GNSS, Constants.DISTANCE, Constants.MIN_CHANGE, default_value=50
)
# Minimum speed in m/s
MINIMUM_SPEED = SettingsUtil.get_setting(
    Constants.GNSS, Constants.SPEED, Constants.MIN_CHANGE, default_value=5
)
# Acceptable error margin for stationary gps coord reading
STATIONARY_ERR = SettingsUtil.get_setting(
    Constants.GNSS,
    Constants.LOCATION,
    TBConstants.GPSD_STATIONARY_ERR_MARGIN,
    default_value=10,
)
# Acceptable error margin for moving gps coord reading
MOVING_ERR = SettingsUtil.get_setting(
    Constants.GNSS,
    Constants.LOCATION,
    TBConstants.GPSD_MOVING_ERR_MARGIN,
    default_value=20,
)
# How many times in a row we need to be out of the geofence before sending the push notification
OUT_OF_GEOFENCE_COUNT = SettingsUtil.get_setting(
    Constants.GNSS,
    Constants.LOCATION,
    TBConstants.OUT_OF_GEOFENCE_COUNT,
    default_value=3,
)
# Geofence alarm push notification title
OUTSIDE_GEOFENCE_TITLE = "Geofence Update"
# Geofence alarm push notification description
OUTSIDE_GEOFENCE_DESCRIPTION = "Your boat moved outside of its geofence boundaries"

GPSD_PORT = 2947


class LocationService:
    location_thread_timer_name = "Location Flush Timer"
    dispose_array: list[rx.abc.DisposableBase] = []

    thingsboard_client: client.ThingsBoardClient
    n2k_client: N2kClient

    gpsd_data_thread: threading.Thread
    gpsd_thread_event: threading.Event
    _max_updates_in_queue: int
    last_known_trip_location: LocationState
    last_attribute_location: LocationState
    geofence_ready = rx.subject.BehaviorSubject(None)
    configuration: N2kConfiguration

    # indicates whether the device is moving or not (is_idle) and if the boat is idle
    # and how long it has been idle
    geo_status: GeoStatus = None

    # geofence_point: the center point of the geofence
    geofence_point: GeoPoint = GeoPoint(None, None)
    # geofence_radius: the radius of the geofence circle
    geofence_radius: float = None
    # geofence_alarm: the current geofence alarm state in cloud
    geofence_alarm: dict = {}
    geofence_consent: rx.Observable[bool]
    location_consent: rx.Observable[bool]
    geofence: rx.Observable[Geofence]
    geofence_counter: int = 0

    _location_updates_lock = threading.Lock()
    _location_updates = {}
    _previous_coordinate: dict = None
    _flush_interval = float(LOCATION_CLOUD_PUBLISH_INTERVAL)
    _flush_timer = threading.Timer

    def __init__(
        self, thingsboard_client: client.ThingsBoardClient, n2k_client: N2kClient
    ):
        self.thingsboard_client = thingsboard_client
        self.n2k_client = n2k_client
        self._logger = logging.getLogger("LocationService")
        self.gpsd_data_thread = None
        self.gpsd_thread_event = None
        self.configuration = None
        # Default consent values
        self.location_consent = True
        self.geofence_consent = True
        geofence_state = TBConstants.GEOFENCE_DISABLED
        if os.path.exists(TBConstants.GEOFENCE_CONSENT_PATH):
            try:
                with open(
                    TBConstants.GEOFENCE_CONSENT_PATH, "r", encoding="utf-8"
                ) as file:
                    consent = json.load(file)
                    if consent[TBConstants.IS_ENABLED_KEY]:
                        geofence_state = TBConstants.GEOFENCE_DEFAULT_ENABLED
            except Exception as error:
                self._logger.warning("Local Geofence consent is invalid or not found")
                self._logger.error(error)
        else:
            self._logger.info("could not find geofence consent file")

        if os.path.exists(TBConstants.LOCATION_CONSENT_PATH):
            try:
                with open(TBConstants.LOCATION_CONSENT_PATH) as file:
                    consent = json.load(file)
                    self._logger.debug(f"Location consent from file: {consent}")
                    self.location_consent = consent
            except Exception as error:
                self._logger.warning("Local Location Consent is invalid or not found")
                self._logger.error(error)
        else:
            self._logger.info("Could not find location consent file")

        self.geofence_ready.on_next(geofence_state)
        self.last_known_trip_location = None
        self.last_attribute_location = None
        # indicates whether the device is moving or not (is_idle) and if the boat is idle
        # and how long it has been idle
        self.geo_status = GeoStatus()
        # Check to see if we current location file present
        if os.path.exists(TBConstants.CURRENT_LOCATION_FILE):
            # File is present, open and parse it
            with open(
                TBConstants.CURRENT_LOCATION_FILE, "r", encoding="utf-8"
            ) as current_location_file:
                try:
                    json_object = json.load(current_location_file)
                    self.last_known_trip_location = LocationState(
                        lat=json_object["lat"], long=json_object["long"], sp=0
                    )
                    self.last_known_trip_location.ts = json_object[Constants.ts]
                except json.decoder.JSONDecodeError:
                    self._logger.warning(
                        "current_location_file cannot be parsed as a json object. Latitude and Longitude not loaded!!"
                    )
        else:
            self._logger.warning("Current location file does not exist")

    def __del__(self):
        if len(self.dispose_array) > 0:
            for item in self.dispose_array:
                item.dispose()
        if self.gpsd_thread_event:
            self.gpsd_thread_event.set()
        if self.geo_status:
            self.geo_status.__del__()

    def _get_cloud_consents(self, value):
        if value:
            consent_sub = rx.Subject()
            consent_sub.subscribe(self._set_consents)
            self.thingsboard_client.request_attributes_state(
                shared_attributes=[
                    Constants.geofence,
                    Constants.locationConsentEnabled,
                    Constants.geofenceEnabled,
                ],
                subject=consent_sub,
            )

    def start(self):
        """
        Initializes the LocationService.

        Args:
            thingsboard_client (client.ThingsBoardClient): The ThingsBoard client object.

        """

        if len(self.dispose_array) > 0:
            for item in self.dispose_array:
                item.dispose()
            self.dispose_array = []

        if self.gpsd_data_thread is not None:
            self.gpsd_thread_event.set()
            self.gpsd_data_thread.join()
            self.gpsd_data_thread = None
            self.gpsd_thread_event = None

        self.configuration = None
        self.dispose_array.append(
            self.n2k_client.configuration.subscribe(self._config_changed)
        )

        # location consent: user can disable the location tracking feature.
        # This will disable geofence and live location updates
        self.location_consent = self.thingsboard_client.subscribe_attribute(
            Constants.locationConsentEnabled,
            {Constants.locationConsentEnabled: True},
        )
        # geofence consent: user can disable just the geofence feature.
        # The device geofence notifications will only be sent if this feature is enabled
        self.geofence_consent = self.thingsboard_client.subscribe_attribute(
            Constants.geofenceEnabled, {Constants.geofenceEnabled: True}
        )

        # geofence setting: this setting is used to get a
        # Geofence center and radius set in the cloud shared attribute
        self.geofence = self.thingsboard_client.subscribe_attribute(
            Constants.geofence, None
        )

        for observable in [self.location_consent, self.geofence_consent, self.geofence]:
            if isinstance(observable, rx.Observable):
                self.dispose_array.append(observable.subscribe(self._set_consents))

        self._location_updates_lock = threading.Lock()
        self._location_updates = {}
        self._previous_coordinate = None
        self._flush_interval = float(LOCATION_CLOUD_PUBLISH_INTERVAL)
        self._flush_timer = threading.Timer(
            self._flush_interval,
            self._prepare_and_publish_location,
        )
        self._flush_timer.name = self.location_thread_timer_name
        self._flush_timer.start()
        try:
            if os.environ["RUNNING_PLATFORM"] == "CONNECT1":
                self.gpsd_thread_event = threading.Event()
                self.gpsd_data_thread = threading.Thread(
                    target=self.get_gpsd_data, name="__gpsdDataThread"
                )
                self.gpsd_data_thread.start()
        except Exception as e:
            self._logger.error("Error starting gpsd thread: %s", e)
        geofence_sub = rx.Subject()
        self.dispose_array.append(geofence_sub.subscribe(self._set_consents))
        # If we are connected when this happens, then put in the request.
        # pylint: disable=protected-access
        if self.thingsboard_client._is_connected_internal.value:
            self.thingsboard_client.request_attributes_state(
                shared_attributes=[
                    Constants.geofence,
                    Constants.locationConsentEnabled,
                    Constants.geofenceEnabled,
                ],
                subject=geofence_sub,
            )
        else:
            # If we are not connected, subscribe to the connection state
            # before putting in the request
            subscribe_disposable: rx.abc.DisposableBase

            def request_for_gefence_when_connected(value):
                if value:
                    self.thingsboard_client.request_attributes_state(
                        shared_attributes=[
                            Constants.geofence,
                            Constants.locationConsentEnabled,
                            Constants.geofenceEnabled,
                        ],
                        subject=geofence_sub,
                    )
                    # Dispose of subscription
                    subscribe_disposable.dispose()

            # pylint: disable=protected-access
            subscribe_disposable = (
                self.thingsboard_client._is_connected_internal.subscribe(
                    request_for_gefence_when_connected
                )
            )
        self.thingsboard_client._is_connected_internal.subscribe(
            self._get_cloud_consents
        )

    def _get_host_ip_address(self):
        if "SSH_HOST" in os.environ and os.environ["SSH_HOST"] != "":
            self._logger.info("SSH_HOST IP is %s", os.environ["SSH_HOST"])
            return os.environ["SSH_HOST"]
        else:
            self._logger.error(
                "SSH_HOST IP address in ENV either doesn't exist or is not valid. Using 10.42.0.1"
            )
            return "10.42.0.1"

    def _set_consents(self, val: Optional[Dict[str, Any]]) -> None:
        if not val:
            self._logger.warning("No data provided.")
            return

        try:
            geofence = val.get(Constants.geofence)
            new_location_consent = val.get(Constants.locationConsentEnabled)
            new_geofence_consent = val.get(Constants.geofenceEnabled)

            if new_location_consent is not None:
                self.location_consent = new_location_consent
                self._logger.info("Location consent set to %s", new_location_consent)
            else:
                # Try to check and see if we have a cached value in the event we didn't
                # receive an update with this call.
                new_location_consent = self.location_consent
                if isinstance(self.location_consent, rx.subject.BehaviorSubject):
                    new_location_consent = self.location_consent.value
                    if isinstance(new_location_consent, dict):
                        new_location_consent = new_location_consent[
                            Constants.locationConsentEnabled
                        ]
                self._logger.info("Using old Location consent %s", new_location_consent)

            if new_geofence_consent is not None:
                self.geofence_consent = new_geofence_consent
                self._logger.info("Geofence consent set to %s", new_geofence_consent)
            else:
                # Try to check and see if we have a cached value in the event we didn't
                # receive an update with this call.
                new_geofence_consent = self.geofence_consent
                if isinstance(self.geofence_consent, rx.subject.BehaviorSubject):
                    new_geofence_consent = self.geofence_consent.value
                    if isinstance(new_geofence_consent, dict):
                        new_geofence_consent = new_geofence_consent[
                            Constants.geofenceEnabled
                        ]
                self._logger.info("Using old Geofence consent %s", new_geofence_consent)

            # Check to see if geofence was given in the set of values.
            # If we did not receive a new geofence, then try to load the old values
            if geofence is None:
                # Check if the geofence config file path exists
                if os.path.exists(TBConstants.GEOFENCE_CONFIG_PATH):
                    self._logger.info("Using old geofence from file")
                    try:
                        with open(
                            TBConstants.GEOFENCE_CONFIG_PATH, "r", encoding="utf-8"
                        ) as geofence_file:
                            json_object = json.load(geofence_file)
                            # Set the geofence dictionary to mock the dictionary we get from
                            # thingsboard attribute for the next codeblock below
                            geofence = {
                                Constants.center: {
                                    Constants.latitude: float(
                                        json_object[Constants.latitude]
                                    ),
                                    Constants.longitude: float(
                                        json_object[Constants.longitude]
                                    ),
                                },
                                Constants.radius: float(json_object[Constants.radius]),
                            }
                    except Exception as error:
                        self._logger.warning("Error in reading geofence config file")
                        self._logger.error(error)
                else:
                    self._logger.info("Could not find geofence config in file")
                    # We did not have the geofence file available, try to load the cached values
                    if (
                        self.geofence_point is not None
                        and self.geofence_radius is not None
                    ):
                        self._logger.info(
                            "Using cached version of the geofence configuration"
                        )
                        geofence = {
                            Constants.center: {
                                Constants.latitude: float(self.geofence_point.latitude),
                                Constants.longitude: float(
                                    self.geofence_point.longitude
                                ),
                            },
                            Constants.radius: float(self.geofence_radius),
                        }

            if geofence:
                geofence_center = geofence.get(Constants.center)
                geofence_radius = geofence.get(Constants.radius)

                if not geofence_center or not isinstance(geofence_center, dict):
                    raise ValueError(
                        "Invalid geofence center data. Expected a dictionary."
                    )
                if geofence_radius is None or not isinstance(
                    geofence_radius, (int, float)
                ):
                    raise ValueError("Invalid geofence radius data. Expected a number.")

                latitude = geofence_center.get(Constants.latitude)
                longitude = geofence_center.get(Constants.longitude)

                if latitude is None or longitude is None:
                    raise ValueError(
                        "Geofence center must include both latitude and longitude."
                    )

                # Determine if the incoming new geofence is the same as the one
                # we already had. If it is, then we don't need to reset the geofence alarm
                is_same_geofence = (
                    self.geofence_point is not None
                    and self.geofence_point.latitude == latitude
                    and self.geofence_point.longitude == longitude
                )

                # Only reset the geofence alarm if the alarm wasn't set because we woke up
                # due to TIMER on host (periodic check) or if the geofence corrdinates are the same
                if not (
                    TBConstants.TIMER_HOST_WAKEUP
                    == self.geofence_alarm.get(TBConstants.WAKEUP_REASON, "")
                ):
                    if not is_same_geofence:
                        self._logger.info("Setting self.geofence_alarm")
                        # Reset the previous alarm if we had a new geofence come in
                        self.geofence_alarm = {}

                self.geofence_point = GeoPoint(latitude, longitude)
                self.geofence_radius = float(geofence_radius)

                self._logger.info(
                    "Geofence set to coordinates: (%f, %f), radius: %f",
                    self.geofence_point.latitude,
                    self.geofence_point.longitude,
                    self.geofence_radius,
                )
            if new_location_consent is not None:
                try:
                    location_consent_should_update = True
                    # Check to see if we have location consent file present
                    if os.path.exists(TBConstants.LOCATION_CONSENT_PATH):
                        with open(
                            TBConstants.LOCATION_CONSENT_PATH, "r+", encoding="utf-8"
                        ) as location_consent_file:
                            file_location_consent = json.load(location_consent_file)
                            if file_location_consent == new_location_consent:
                                location_consent_should_update = False
                    if location_consent_should_update:
                        with open(
                            TBConstants.LOCATION_CONSENT_PATH, "w", encoding="utf-8"
                        ) as location_consent_file:
                            location_consent_file.write(
                                json.dumps(new_location_consent)
                            )
                            self._logger.info(
                                "Wrote location consent file with %s",
                                new_location_consent,
                            )
                    else:
                        self._logger.debug("Location consent file has not changed")
                except Exception as err:
                    self._logger.debug(
                        "not able to write to local location consent file %s", err
                    )

                if new_geofence_consent is not None:
                    update_to_send = TBConstants.GEOFENCE_DISABLED
                    geofence_is_enabled = False
                    if new_location_consent and new_geofence_consent and geofence:
                        update_to_send = TBConstants.GEOFENCE_ENABLED
                        geofence_is_enabled = True
                    self.geofence_ready.on_next(update_to_send)
                    try:
                        # Check to see if we have geofence consent file present
                        if os.path.exists(TBConstants.GEOFENCE_CONSENT_PATH):
                            with open(
                                TBConstants.GEOFENCE_CONSENT_PATH,
                                "r+",
                                encoding="utf-8",
                            ) as geofence_consent_local_file:
                                data = json.load(geofence_consent_local_file)
                                # See if we have a different value from the file
                                # If the values are different, then write the file, otherwise
                                # leave the file alone.
                                if (
                                    data[TBConstants.IS_ENABLED_KEY]
                                    != geofence_is_enabled
                                ):
                                    geofence_consent_local_file.seek(0)
                                    json_data = {
                                        TBConstants.IS_ENABLED_KEY: geofence_is_enabled
                                    }
                                    geofence_consent_local_file.write(
                                        json.dumps(json_data)
                                    )
                                    geofence_consent_local_file.truncate()
                        else:
                            # The file was not present, create it with the required content
                            with open(
                                TBConstants.GEOFENCE_CONSENT_PATH, "w", encoding="utf-8"
                            ) as geofence_consent_file:
                                json_data = {
                                    TBConstants.IS_ENABLED_KEY: geofence_is_enabled
                                }
                                geofence_consent_file.write(json.dumps(json_data))
                            self._logger.info("Created geofence file")
                    except Exception as e:
                        self._logger.error(
                            "not able to write local geofence consent file %s", e
                        )

                    # If location consent is now false, remove the current location file.
                    if new_location_consent is False and os.path.exists(
                        TBConstants.CURRENT_LOCATION_FILE
                    ):
                        try:
                            os.remove(TBConstants.CURRENT_LOCATION_FILE)
                            self._logger.info("Removed current location file")
                        except Exception as err:
                            self._logger.error(
                                "Unable to remove current location file %s", err
                            )

        except Exception as e:
            self._logger.error("Error setting geofence or consents: %s", e)

    def _config_changed(self, config):
        if config:
            self.configuration = config

    def process_geofence(self, change: Optional[ChannelStateChange]) -> None:
        """
        Processes the geofence data and updates the geofence state.
        Args:
            change (ChannelStateChange): The channel state change object
                containing the current location data.
        Returns:
            None
        """
        if not self.geofence_consent or not self.location_consent:
            self._logger.warning("Geofence or location consent is set to disabled")
            return False

        if not self.geofence:
            self._logger.warning("Geofence is not set.")
            return False

        if not change or not change.state:
            self._logger.warning("No change or state data provided.")
            return False

        try:
            distance = GeoUtil.calculate_distance(
                self.geofence_point.longitude,
                self.geofence_point.latitude,
                change.state[Constants.long],
                change.state[Constants.lat],
            )
            geofence_alarm = {}

            if distance is not None and distance > self.geofence_radius:
                self.geofence_counter += 1
                self._logger.info(
                    "Geofence alarm triggered %d times in a row", self.geofence_counter
                )

                # Boat is outside of geofence. Create the alarm
                if self.geofence_counter >= OUT_OF_GEOFENCE_COUNT:
                    geofence_alarm = {
                        TBConstants.TITLE: OUTSIDE_GEOFENCE_TITLE,
                        TBConstants.NAME: OUTSIDE_GEOFENCE_TITLE,
                        TBConstants.DESCRIPTION: OUTSIDE_GEOFENCE_DESCRIPTION,
                        TBConstants.SEVERITY: AlarmSeverity.IMPORTANT,
                        TBConstants.CURRENT_STATE: AlarmState.ENABLED,
                        TBConstants.DATE_ACTIVE: int(time.time() * 1000),
                        TBConstants.THINGS: [change.thing_id],
                    }
                else:
                    geofence_alarm = {}
            elif distance < self.geofence_radius:
                self._logger.info("Boat is inside the geofence")
                self.geofence_counter = 0
                geofence_alarm = {}

            # Check to see that both alarms are not enabled
            if (
                self.geofence_alarm
                and geofence_alarm
                and self.geofence_alarm.get(TBConstants.CURRENT_STATE)
                == AlarmState.ENABLED
                and geofence_alarm.get(TBConstants.CURRENT_STATE) == AlarmState.ENABLED
            ):
                self._logger.info(
                    "Geofence alarm already enabled. No update will be sent."
                )
                return False
            else:
                # Check to make sure that the alarm isn't the same
                # before sending to thingsboard
                # Do not send geofence alarm with no body i.e {}
                return_value = False
                if self.geofence_alarm != geofence_alarm and geofence_alarm:
                    self._logger.info("Publishing geofence alarm telemetry")
                    self.thingsboard_client.send_telemetry(
                        {TBConstants.ALARM_GEOFENCE_KEY: geofence_alarm},
                        data_type=client.TelemetryDataType.OTHER,
                    )
                    return_value = True
                # Don't reset the geofence alarm if we have woken up due to telemetry
                if not (
                    TBConstants.TIMER_HOST_WAKEUP
                    == self.geofence_alarm.get(TBConstants.WAKEUP_REASON, "")
                ):
                    self._logger.info("Setting self.geofence_alarm")
                    self.geofence_alarm = geofence_alarm
                return return_value

        except KeyError as e:
            self._logger.error("Missing key in state data: %s", e)
        except Exception as e:
            self._logger.error("Error processing geofence: %s", e)

    def queue_location_update(self, change: ChannelStateChange):
        """
        Queues a location update for the given channel state change.

        Args:
            change (ChannelStateChange): The channel state change object containing
                the updated location.

        Returns:
            None
        """

        # Check if location consent is True
        if self.location_consent is None or not self.location_consent:
            self.thingsboard_client.handle_location_fulfilled()
            return

        publish = False

        with self._location_updates_lock:
            # Process geofence inside of lock.
            # This ensures we don't send multiple alarms with different sources
            if self.geofence_consent:
                publish = self.process_geofence(change)

            new_location = self.__convert_channel_state_to_location_state(change=change)

            if (
                change.channel_id in self._location_updates
                and self._location_updates[change.channel_id]
            ):
                last_update = self._location_updates[change.channel_id][-1]

                last_update_location_state = LocationState(
                    lat=last_update[Constants.lat],
                    long=last_update[Constants.long],
                    sp=last_update[Constants.sp],
                )

                if self.__is_past_threshold(
                    last_update_location_state,
                    new_location,
                ):
                    self._location_updates[change.channel_id].append(change.state)

            else:
                if self.last_known_trip_location is None:
                    # We had no last location, add the coord to the list
                    self._location_updates[change.channel_id] = [change.state]
                else:
                    if self.__is_past_threshold(
                        self.last_known_trip_location,
                        new_location,
                    ):
                        # Change in gps data, add it to the list
                        self._location_updates[change.channel_id] = [change.state]

            self._update_position(change)

            if len(self._location_updates) >= LOCATION_FLUSH_MAX_UPDATES or any(
                len(updates) >= LOCATION_FLUSH_MAX_UPDATES
                for updates in self._location_updates.values()
            ):
                publish = True

        # check if we need to publish the location updates. set publish to False once we publish
        if publish:
            self._prepare_and_publish_location()
            publish = False

    def __set_last_attribute_location(self, new_location: LocationState):
        """
        Set the last location attribute.
        If it was previously None (startup), then publish that to cloud immediately
        """
        should_publish = self.last_attribute_location is None
        self.last_attribute_location = new_location

        if should_publish:
            self._update_position_attribute()

    def _update_position(self, change: ChannelStateChange):
        """
        Update the position based on the state change.

        Args:
            change (ChannelStateChange): The state change containing new location data.
        """
        incoming_location = self.__convert_channel_state_to_location_state(
            change=change
        )
        # Set the last attribute location
        self.__set_last_attribute_location(incoming_location)
        # Check if the last known location is None
        if self.last_known_trip_location is None:
            # Initialize the last known location with the current state
            # set the attribute in ThingsBoard
            self.last_known_trip_location = incoming_location
            self._logger.info(
                "Updated trip location %s", self.last_known_trip_location.to_json()
            )
            return

        if self.__is_past_threshold(
            self.last_known_trip_location,
            incoming_location,
        ):
            # Update last known location
            self.last_known_trip_location = incoming_location
            self._logger.info(
                "Updated trip location %s", self.last_known_trip_location.to_json()
            )
            self.geo_status.is_idle = False
        else:
            # Else if we haven't changed location. Update last_known's timestamp
            self.geo_status.is_idle = True

    # Helper function to convert ChannelStateChange to LocationState class
    def __convert_channel_state_to_location_state(self, change: ChannelStateChange):
        return LocationState(
            lat=change.state[Constants.lat],
            long=change.state[Constants.long],
            sp=change.state[Constants.sp],
        )

    # Helper function to calculate if we have gone farther or faster than the
    # threshold values
    def __is_past_threshold(
        self, prev_point: LocationState, latest_point: LocationState
    ):
        # Calculate the distance between the last known location and the new location
        distance = GeoUtil.calculate_distance(
            prev_point.lat,
            prev_point.long,
            latest_point.lat,
            latest_point.long,
        )

        # Check if the distance is greater than the minimum distance or
        # the speed is greater than the minimum speed
        return distance > MINIMUM_DISTANCE or latest_point.sp > MINIMUM_SPEED

    def _update_position_attribute(self):
        """
        Update the ThingsBoard client attributes with the new state.

        Args:
            state (Dict[str, float]): The new state containing location data.
        """
        # Don't upload the current location if we don't have location consent
        if self.location_consent is None or not self.location_consent:
            return
        try:
            self.thingsboard_client.update_attributes(
                {
                    f"{TBConstants.POSITION}.{TBConstants.LAT}": self.last_attribute_location.lat,
                    f"{TBConstants.POSITION}.{TBConstants.LONG}": self.last_attribute_location.long,
                    f"{TBConstants.POSITION}.{TBConstants.TS}": self.last_attribute_location.ts,
                },
                client.AttributeDataType.LOCATION,
            )
            self._logger.info(
                "Successfully updated ThingsBoard attributes for position."
            )

            try:
                with open(
                    TBConstants.CURRENT_LOCATION_FILE, "w", encoding="utf-8"
                ) as current_location_file:
                    current_location_file.write(
                        json.dumps(self.last_attribute_location.to_json())
                    )
                    self._logger.info("Successfully wrote current location file")
            except Exception as err:
                self._logger.error("Error writing to current file location %s", err)
        except Exception as e:
            # Handle potential errors during attribute update
            self._logger.error("Error updating ThingsBoard attribute position: %s", e)

    def _prepare_and_publish_location(self, manual_flush=False):
        """
        Prepares and publishes the location updates to the ThingsBoard client.

        If there are any location updates in the queue, they will be sent to the ThingsBoard client
        as telemetry data. After sending the updates, the queue will be cleared.

        The method also resets the flush timer to schedule the next flush operation.

        Note: This method is intended to be called internally and should not be called directly.

        Returns:
            None
        """
        try:
            selected_source = None
            telemetry_to_send = None

            # Acquire lock and copy location updates
            with self._location_updates_lock:
                telemetry_to_send = copy.deepcopy(self._location_updates)
                self._location_updates.clear()

            # Process or send the updates
            if telemetry_to_send and len(telemetry_to_send) > 0:
                location_sources = list(
                    telemetry_to_send.keys()
                )  # Extract location source keys
                selected_source = self._prioritize_location_sources(location_sources)
                if selected_source:
                    self._logger.info(
                        "Flushing location updates: %s",
                        {selected_source: telemetry_to_send[selected_source]},
                    )
                    self.thingsboard_client.send_telemetry(
                        {
                            # Send all of the trip gps coordinates available
                            Constants.trips: {
                                selected_source: telemetry_to_send[selected_source]
                            }
                        },
                        client.TelemetryDataType.LOCATION,
                        # Include the timestamp from the first point
                        # Time needs to be in ms instead of seconds
                        telemetry_to_send[selected_source][0][Constants.ts],
                    )
                    # Call psv client to configure the update only if it is not a manual flush
                    # Manual flushes can be triggered from psv_server, avoids infinite loop of
                    # calling configure update before going back to sleep
                    if manual_flush is False:
                        try:
                            self._logger.info("Updating ublox geofence")
                            configure_update()
                        except Exception as e:
                            self._logger.error("Error updating ublox geofence: %s", e)

            # Update the position attribute with the latest location
            self._update_position_attribute()
        except Exception as e:
            self._logger.error("Error flushing location updates: %s", e)

        try:
            # Reset the timer
            self._flush_timer.cancel()  # Stop the current timer
            self._flush_timer = threading.Timer(
                self._flush_interval,
                self._prepare_and_publish_location,
            )
            self._flush_timer.name = self.location_thread_timer_name
            self._flush_timer.start()
        except Exception as e:
            self._logger.error("Error in flush_location_updates: %s", e)
            raise e

    def _prioritize_location_sources(self, sources):
        """
        Prioritizes the location sources based on the given priority list.

        Args:
            sources (list): List of location sources to prioritize.

        Returns:
            str or None: The highest priority location source that matches the priority list,
            or None if no matching source is found.

        """
        external_source = None  # Initialize external_source outside the loop

        # Pre-compile regular expressions for filter_pattern
        pattern = re.compile(location_filter_pattern)  # Compile once per priority

        for priority in location_priority_sources:
            for source in sources:
                if not isinstance(source, str):
                    continue

                matched_source = pattern.search(source)
                match = matched_source.group(1)
                if match:
                    if match == priority:
                        return source if not external_source else external_source

                    # Check if source matches the current priority
                    if priority == Constants.n2k:
                        id_str = matched_source.group(1)
                        try:
                            priority_id = int(
                                id_str
                            )  # Attempt to convert id_str to an integer
                            gnss = self.configuration.gnss.get(priority_id)
                            if gnss and not gnss.IsExternal:
                                return source  # Return immediately if an internal source matches
                            elif gnss and gnss.IsExternal and not external_source:
                                external_source = (
                                    source  # Save the first external source found
                                )
                        except ValueError:
                            # id_str was not a valid integer, ignore
                            continue

        return (
            external_source if external_source else None
        )  # Return any external source if no internal source was found

    def stop(self):
        # Call this method to stop the timer when the service is stopping
        self._flush_timer.cancel()
        self.gpsd_thread_event.set()

    def manually_flush_trip_data(self):
        """
        Call to manually flush the queue.
        Will be used by psv_server to try and flush the data before going to sleep
        """
        self._logger.info("Manual flush called, publishing trips telemetry to cloud")
        self._prepare_and_publish_location(manual_flush=True)

    def get_gpsd_data(self):
        """
        Fetches the current GPS data and sends it to the server.

        This method continuously fetches the current GPS data using the `gpsd` library and sends it
        to the server by queuing a location update. It checks if the GPS has a valid fix
        and extracts the latitude, longitude, and horizontal speed from the GPS data. The location
        update is then queued with a timestamp and sent to the server.

        Note: This method runs in an infinite loop and sleeps for 1 second between each iteration.

        Returns:
            None
        """
        self._logger.info("start collecting and sending geolocation data periodically")
        _log_counter = 0  # Initialize the counter

        # Try to connect to gpsd
        self._logger.info("Trying to connect to gpsd")
        successfully_connected = False
        while not successfully_connected:
            try:
                gpsd.connect(host=self._get_host_ip_address(), port=GPSD_PORT)
                successfully_connected = True
            except Exception as e:
                successfully_connected = False
                self._logger.error("Error connecting to gpsd: %s", e)
                time.sleep(10)

        sleep_time = 0
        while not self.gpsd_thread_event.wait(sleep_time):
            try:
                # Fetch the current GPS data
                packet = gpsd.get_current()

                # Initialize default data
                data = LocationState(0, 0, 0)
                # Check if we have a valid fix
                if packet.mode >= 3 or (packet.lat != 0.0) or (packet.lon != 0.0):
                    data.lat = round(packet.lat, 5)
                    data.long = round(packet.lon, 5)
                    if packet.mode >= 3:
                        data.sp = round(packet.hspeed, 2)  # Horizontal speed

                    # Get state dictionary
                    location_dict = data.to_json()
                    # Add additional information from the packet
                    location_dict["err"] = {
                        "x": round(packet.error["x"]),
                        "y": round(packet.error["y"]),
                    }
                    location_dict["sats_valid"] = packet.sats_valid
                    # We had a previous value that was None, wait to get multiple coordinates
                    # before testing the thresholding
                    if (
                        # Case when we have no previous coordinate, set the value and poll again
                        self._previous_coordinate is None
                        or
                        # Case where we have alternating between zero
                        # and non zero speed (potential noise)
                        (
                            self._previous_coordinate[Constants.sp] == 0
                            and location_dict[Constants.sp] != 0
                        )
                        or (
                            self._previous_coordinate[Constants.sp] != 0
                            and location_dict[Constants.sp] == 0
                        )
                    ):
                        self._previous_coordinate = location_dict
                        sleep_time = LOCATION_GPSD_UPDATE_INTERVAL
                        continue

                    # Last remaining cases are both are non zero speed, or both speed values.
                    x_err = self._previous_coordinate["err"]["x"]
                    y_err = self._previous_coordinate["err"]["y"]
                    # It has been shown when the errors were 0 that the gps
                    # coordinate could've been off from where antenna is located
                    if x_err == 0 or y_err == 0:
                        sleep_time = LOCATION_GPSD_UPDATE_INTERVAL / 2
                        self._previous_coordinate = location_dict
                        continue
                    # If the speed is 0 and we are not within the stricter margin of error.
                    # Don't queue this into trip data and try at a faster rate.
                    if self._previous_coordinate[Constants.sp] == 0.0 and (
                        x_err > STATIONARY_ERR or y_err > STATIONARY_ERR
                    ):
                        # Set the interval time to half if we had high margin
                        # of err
                        sleep_time = LOCATION_GPSD_UPDATE_INTERVAL / 2
                        # If we are stationary and we are within margin of error for the speed
                        if x_err < MOVING_ERR and y_err < MOVING_ERR:
                            # Set the current location to the previous, the accepted value
                            data = LocationState(
                                self._previous_coordinate[Constants.lat],
                                self._previous_coordinate[Constants.long],
                                self._previous_coordinate[Constants.sp],
                            )
                            data.ts = self._previous_coordinate[Constants.ts]
                            # We can update the current location
                            self.__set_last_attribute_location(data)
                        self._previous_coordinate = location_dict
                        continue
                    elif self._previous_coordinate[Constants.sp] != 0.0 and (
                        x_err > MOVING_ERR or y_err > MOVING_ERR
                    ):
                        # Set the interval time to half if we had high margin
                        # of err while moving
                        sleep_time = LOCATION_GPSD_UPDATE_INTERVAL / 2
                        self._previous_coordinate = location_dict
                        continue
                    # Log the previous coordinate to queue and see if it is a good to
                    # add to the trips data
                    self._logger.info(
                        "Previous GPS Data: %s", self._previous_coordinate
                    )
                    self.queue_location_update(
                        ChannelStateChange(
                            channel_id=Constants.gnss
                            + "."
                            + Constants.gpsd
                            + "."
                            + Constants.loc,
                            state=self._previous_coordinate,
                            thing_id=Constants.gnss + "." + Constants.gpsd,
                            thing_type=Constants.gnss,
                        )
                    )
                    if (
                        self._previous_coordinate[Constants.sp] != 0
                        and location_dict[Constants.sp] != 0
                    ):
                        self._previous_coordinate = location_dict
                    else:
                        self._previous_coordinate = None
                elif packet.mode >= 2:
                    # Increment the counter, then mod it by 10
                    _log_counter = (_log_counter + 1) % 10
                    # Check if the counter is a multiple of 10
                    if _log_counter == 0:
                        self._logger.info("No valid fix. Mode: %s", packet.mode)
            except Exception as e:
                self._logger.error("Error getting gpsd data: %s", e)
            # Set the gpsd interval back to the original config version
            sleep_time = LOCATION_GPSD_UPDATE_INTERVAL
