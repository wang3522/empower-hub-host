import copy
import re
import threading
import time
import os
from typing import Any, Dict, Optional
import logging
import json
import reactivex as rx
# pylint: disable=import-error,no-name-in-module
from tb_utils.constants import Constants
from tb_utils.gps_parser import GPSParser
from tb_utils.geo_util import GeoUtil
from mqtt_client import ThingsBoardClient

from n2kclient.client import N2KClient
from n2kclient.models.empower_system.location_state import LocationState
from n2kclient.util.settings_util import SettingsUtil
from n2kclient.models.empower_system.alarm import AlarmSeverity, AlarmState

from .models.geofence import GeoPoint, Geofence
from .sync_service import SyncService

from .config import location_priority_sources, location_filter_pattern

# Port for GNSS connection
SERIAL_PORT = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.SERIAL_PORT,
    default_value="/dev/ttyUSB1"
)
# # Cloud publish interval in seconds
LOCATION_CLOUD_PUBLISH_INTERVAL = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.LOCATION,
    Constants.CLOUD_PUBLISH_INTERVAL,
    default_value=600
)
# number of updates to flush (i.e. if any one gps thing has 20 updates, flush all)
LOCATION_FLUSH_MAX_UPDATES = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.LOCATION,
    Constants.FLUSH_MAX_UPDATES,
    default_value=20
)
# GPSD update interval in seconds
LOCATION_GPSD_UPDATE_INTERVAL = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.LOCATION,
    Constants.GPSD_UPDATE_INTERVAL,
    default_value=10
)
# Minimum distance in meters
MINIMUM_DISTANCE = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.DISTANCE,
    Constants.MIN_CHANGE,
    default_value=50
)
# Minimum speed in m/s
MINIMUM_SPEED = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.SPEED,
    Constants.MIN_CHANGE,
    default_value=5
)
# Acceptable error margin for stationary gps coord reading
STATIONARY_ERR = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.LOCATION,
    Constants.GPSD_STATIONARY_ERR_MARGIN,
    default_value=10,
)
# Acceptable error margin for moving gps coord reading
MOVING_ERR = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.LOCATION,
    Constants.GPSD_MOVING_ERR_MARGIN,
    default_value=20,
)
# How many times in a row we need to be out of the geofence before sending the push notification
OUT_OF_GEOFENCE_COUNT = SettingsUtil.get_setting(
    Constants.THINGSBOARD_SETTINGS_KEY,
    Constants.GNSS,
    Constants.LOCATION,
    Constants.OUT_OF_GEOFENCE_COUNT,
    default_value=3,
)
# Geofence alarm push notification title
OUTSIDE_GEOFENCE_TITLE = "Geofence Update"
# Geofence alarm push notification description
OUTSIDE_GEOFENCE_DESCRIPTION = "Your boat moved outside of its geofence boundaries"

class LocationService:
    location_thread_timer_name = "Location Flush Timer"
    dispose_array: list[rx.abc.DisposableBase] = []

    thingsboard_client: ThingsBoardClient = ThingsBoardClient()
    sync_service: SyncService = SyncService()
    n2k_client: N2KClient
    gnss_connection: GPSParser = GPSParser(SERIAL_PORT)

    gpsd_data_thread: threading.Thread
    gpsd_thread_event: threading.Event
    _max_updates_in_queue: int
    last_known_trip_location: LocationState
    last_attribute_location: LocationState
    geofence_ready = rx.subject.BehaviorSubject(None)
    # configuration: N2kConfiguration

    # geofence_point: the center point of the geofence.
    geofence_point: GeoPoint = GeoPoint(None, None)
    # geofence_radius: the radius of the geofence circle
    geofence_radius: float = None
    # geofence_alarm: the current geofence alarm state in cloud
    geofence_alarm: dict = {}
    geofence_consent: bool
    location_consent: bool
    geofence: rx.Observable[Geofence]
    geofence_counter: int = 0

    _location_updates_lock = threading.Lock()
    _location_updates = {}
    _previous_coordinate: dict = None
    _flush_interval = float(LOCATION_CLOUD_PUBLISH_INTERVAL)
    _flush_timer = threading.Timer

    def __init__(
        self, n2k_client: N2KClient
    ):
        self.n2k_client = n2k_client
        self._logger = logging.getLogger("LocationService")
        self.gpsd_data_thread = None
        self.gpsd_thread_event = None
        self.configuration = None
        # Default consent values
        self.location_consent = True
        self.geofence_consent = True

        self.last_known_trip_location = None
        self.last_attribute_location = None
        # Check to see if we current location file present
        if os.path.exists(Constants.CURRENT_LOCATION_FILE):
            # File is present, open and parse it
            with open(
                Constants.CURRENT_LOCATION_FILE, "r", encoding="utf-8"
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

        self._set_consent_subscriptions()

    def __del__(self):
        if len(self.dispose_array) > 0:
            for item in self.dispose_array:
                item.dispose()
        if self.gpsd_thread_event:
            self.gpsd_thread_event.set()

    def start(self):
        """
        Initializes the LocationService.

        Args:
            thingsboard_client (client.ThingsBoardClient): The ThingsBoard client object.

        """
        if self.gpsd_data_thread is not None:
            self.gpsd_thread_event.set()
            self.gpsd_data_thread.join()
            self.gpsd_data_thread = None
            self.gpsd_thread_event = None

        # self.configuration = None
        # self.dispose_array.append(
        #     self.n2k_client.configuration.subscribe(self._config_changed)
        # )

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
            # if os.environ["RUNNING_PLATFORM"] == "CONNECT1":
            self.gpsd_thread_event = threading.Event()
            self.gpsd_data_thread = threading.Thread(
                target=self.get_gpsd_data, name="__gpsdDataThread"
            )
            self.gpsd_data_thread.start()
        except Exception as e:
            self._logger.error("Error starting gpsd thread: %s", e)


    def _get_host_ip_address(self):
        if "SSH_HOST" in os.environ and os.environ["SSH_HOST"] != "":
            self._logger.info("SSH_HOST IP is %s", os.environ["SSH_HOST"])
            return os.environ["SSH_HOST"]
        else:
            self._logger.error(
                "SSH_HOST IP address in ENV either doesn't exist or is not valid. Using 10.42.0.1"
            )
            return "10.42.0.1"

    def _set_consent_subscriptions(self):
        # location consent: user can disable the location tracking feature.
        # This will disable geofence and live location updates
        self.sync_service.subscribe_to_attribute(Constants.LOCATION_CONSENT_ENABLED_KEY)
        behavior_subject = self.sync_service.get_attribute_subject(
            key=Constants.LOCATION_CONSENT_ENABLED_KEY
        )
        if behavior_subject is not None:
            dispose = behavior_subject.subscribe(self.set_location_consent)
            self.dispose_array.append(dispose)
        # geofence consent: user can disable just the geofence feature.
        # The device geofence notifications will only be sent if this feature is enabled
        self.sync_service.subscribe_to_attribute(Constants.GEOFENCE_ENABLED_KEY)
        behavior_subject = self.sync_service.get_attribute_subject(
            key=Constants.GEOFENCE_ENABLED_KEY
        )
        if behavior_subject is not None:
            dispose = behavior_subject.subscribe(self.set_geofence_consent)
            self.dispose_array.append(dispose)

        # geofence setting: this setting is used to get a
        # Geofence center and radius set in the cloud shared attribute
        self.sync_service.subscribe_to_attribute(Constants.GEOFENCE_KEY)
        behavior_subject = self.sync_service.get_attribute_subject(key=Constants.GEOFENCE_KEY)
        if behavior_subject is not None:
            dispose = behavior_subject.subscribe(self.set_geofence_point)
            self.dispose_array.append(dispose)

    def set_location_consent(self, value: bool):
        if value is not None:
            self.location_consent = value
            self._logger.info("Location consent set to %s", value)

    def set_geofence_consent(self, value: bool):
        if value is not None:
            self.geofence_consent = value
            self._logger.info("Geofence consent set to %s", value)
            if value is False:
                self.geofence_counter = 0

    def set_geofence_point(self, value: dict):
        """
        Sets the geofence point and radius from the given value.

        Args:
            value (dict): A dictionary containing 'latitude', 'longitude', and 'radius'.

        """
        self._logger.info("Setting geofence point and radius from value: %s", value)
        if value is not None:
            geofence_center = value.get(Constants.center)
            new_geofence_point = GeoPoint(
                latitude=geofence_center.get(Constants.latitude),
                longitude=geofence_center.get(Constants.longitude),
            )
            new_geofence_radius = value.get(Constants.radius)
            if (
                new_geofence_point.latitude is not None and new_geofence_point.longitude is not None
                and (
                    new_geofence_point.latitude != self.geofence_point.latitude
                    or new_geofence_point.longitude != self.geofence_point.longitude
                )
                or new_geofence_radius != self.geofence_radius
            ):
                self._logger.info(
                    "Geofence point set to lat %s long %s with radius %s",
                    new_geofence_point.latitude,
                    new_geofence_point.longitude,
                    new_geofence_radius,
                )
                self.geofence_point = new_geofence_point
                self.geofence_radius = new_geofence_radius
                self.geofence_ready.on_next(True)
                # New geofence point is set, reset the geofence counter
                self.geofence_counter = 0
            else:
                self._logger.debug("Geofence point not changed or invalid")
        else:
            self.geofence_point = GeoPoint(None, None)

    def _config_changed(self, config):
        if config:
            self.configuration = config

    def process_geofence(self, change: Optional[Dict]) -> None:
        """
        Processes the geofence data and updates the geofence state.
        Args:
            change (ChannelStateChange): The channel state change object
                containing the current location data.
        Returns:
            None
        """
        if (
            self.geofence_consent is None
            or not self.geofence_consent
            or self.location_consent is None
            or not self.location_consent
        ):
            self._logger.warning("Geofence or location consent is set to disabled")
            return False

        if not change or len(change) == 0:
            self._logger.warning("No change or state data provided.")
            return False

        try:
            distance = GeoUtil.calculate_distance(
                self.geofence_point.longitude,
                self.geofence_point.latitude,
                change[Constants.LONG],
                change[Constants.LAT],
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
                        Constants.TITLE: OUTSIDE_GEOFENCE_TITLE,
                        Constants.NAME: OUTSIDE_GEOFENCE_TITLE,
                        Constants.DESCRIPTION: OUTSIDE_GEOFENCE_DESCRIPTION,
                        Constants.SEVERITY: AlarmSeverity.IMPORTANT,
                        Constants.CURRENT_STATE: AlarmState.ENABLED,
                        Constants.DATE_ACTIVE: int(time.time() * 1000),
                        Constants.THINGS: [change.get(Constants.THINGS, "gnss.gpsd")],
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
                and self.geofence_alarm.get(Constants.CURRENT_STATE)
                == AlarmState.ENABLED
                and geofence_alarm.get(Constants.CURRENT_STATE) == AlarmState.ENABLED
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
                        {Constants.ALARM_GEOFENCE_KEY: geofence_alarm},
                    )
                    return_value = True
                # Store the geofence alarm state so we don't send the alarm again
                self.geofence_alarm = geofence_alarm
                return return_value
        except KeyError as e:
            self._logger.error("Missing key in state data: %s", e)
        except Exception as e:
            self._logger.error("Error processing geofence: %s", e)

    def queue_location_update(self, change: Dict[str, Any], channel_id: str) -> None:
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
            self._logger.warning("Location consent is set to disabled")
            return

        publish = False

        with self._location_updates_lock:
            # Process geofence inside of lock.
            # This ensures we don't send multiple alarms with different sources
            if self.geofence_consent:
                publish = self.process_geofence(change)

            new_location = self.__convert_channel_state_to_location_state(change=change)

            if (
                channel_id in self._location_updates
                and self._location_updates[channel_id]
            ):
                last_update = self._location_updates[channel_id][-1]

                last_update_location_state = LocationState(
                    lat=last_update[Constants.LAT],
                    long=last_update[Constants.LONG],
                    sp=last_update[Constants.sp],
                )

                if self.__is_past_threshold(
                    last_update_location_state,
                    new_location,
                ):
                    self._location_updates[channel_id].append(change)

            else:
                if self.last_known_trip_location is None:
                    # We had no last location, add the coord to the list
                    self._location_updates[channel_id] = [change]
                else:
                    if self.__is_past_threshold(
                        self.last_known_trip_location,
                        new_location,
                    ):
                        # Change in gps data, add it to the list
                        self._location_updates[channel_id] = [change]

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

    def _update_position(self, change: Dict[str, Any]):
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
        else:
            # Else if we haven't changed location. Update last_known's timestamp
            pass

    # Helper function to convert ChannelStateChange to LocationState class
    def __convert_channel_state_to_location_state(self, change: Dict[str, Any]) -> LocationState:
        return LocationState(
            lat=change[Constants.LAT],
            long=change[Constants.LONG],
            sp=change[Constants.sp],
        )

    # Helper function to calculate if we have gone farther or faster than the
    # threshold values
    def __is_past_threshold(
        self, prev_point: LocationState, latest_point: LocationState
    ):
        # Calculate the distance between the last known location and the new location
        distance = GeoUtil.calculate_distance(
            prev_point.long,
            prev_point.lat,
            latest_point.long,
            latest_point.lat,
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
                    f"{Constants.POSITION}.{Constants.LAT}": self.last_attribute_location.lat,
                    f"{Constants.POSITION}.{Constants.LONG}": self.last_attribute_location.long,
                    f"{Constants.POSITION}.{Constants.ts}": self.last_attribute_location.ts,
                }
            )
            self._logger.info(
                "Successfully updated ThingsBoard attributes for position."
            )

            try:
                with open(
                    Constants.CURRENT_LOCATION_FILE, "w", encoding="utf-8"
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
                        # Include the timestamp from the first point
                        # Time needs to be in ms instead of seconds
                        timestamp=telemetry_to_send[selected_source][0][Constants.ts],
                    )
                    # TODO: Do we have the ability or want to configure geofence?
                    # Call psv client to configure the update only if it is not a manual flush
                    # Manual flushes can be triggered from psv_server, avoids infinite loop of
                    # calling configure update before going back to sleep
                    if manual_flush is False:
                        try:
                            self._logger.info("Updating ublox geofence")
                            # configure_update()
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
                self.gnss_connection.connect_serial_and_start_gnss()
                successfully_connected = True
            except Exception as e:
                successfully_connected = False
                self._logger.error("Error connecting to gpsd: %s", e)
                time.sleep(10)

        sleep_time = 0
        while not self.gpsd_thread_event.wait(sleep_time):
            if self.location_consent is None or not self.location_consent:
                self._logger.warning(
                    "Location consent is set to disabled, not fetching GPS data"
                )
                sleep_time = LOCATION_GPSD_UPDATE_INTERVAL
                continue
            try:
                # Fetch the current GPS data
                packet = self.gnss_connection.get_location()
                # Initialize default data
                data = LocationState(0, 0, 0)
                # Check if we have a valid 3d fix
                if packet["mode"] >= 3 or (packet[Constants.LAT] != 0.0) or (packet[Constants.LONG] != 0.0):
                    data.lat = round(packet[Constants.LAT], 5)
                    data.long = round(packet[Constants.LONG], 5)
                    data.ts = packet[Constants.ts]
                    if packet["mode"] >= 3:
                        data.sp = round(packet[Constants.sp], 2)  # Horizontal speed

                    # Get state dictionary
                    location_dict = data.to_json()
                    # Add additional information from the packet
                    location_dict["err"] = {
                        "x": round(packet["error"]["x"]),
                        "y": round(packet["error"]["y"]),
                    }
                    location_dict["sats_valid"] = packet["sats_valid"]
                    location_dict[Constants.THINGS] = "gnss.gpsd"
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
                                self._previous_coordinate[Constants.LAT],
                                self._previous_coordinate[Constants.LONG],
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
                        self._previous_coordinate,
                        "gnss.gpsd.loc"
                    )
                    if (
                        self._previous_coordinate[Constants.sp] != 0
                        and location_dict[Constants.sp] != 0
                    ):
                        self._previous_coordinate = location_dict
                    else:
                        self._previous_coordinate = None
                elif packet["mode"] >= 2:
                    # Increment the counter, then mod it by 10
                    _log_counter = (_log_counter + 1) % 10
                    # Check if the counter is a multiple of 10
                    if _log_counter == 0:
                        self._logger.info("No valid fix. Mode: %s", packet["mode"])
            except Exception as e:
                self._logger.error("Error getting gpsd data: %s", e)
            # Set the gpsd interval back to the original config version
            sleep_time = LOCATION_GPSD_UPDATE_INTERVAL
            self._logger.debug("sleeping for %s seconds", sleep_time)
