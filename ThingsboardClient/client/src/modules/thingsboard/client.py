from multiprocessing import Queue
import queue
import threading
import time

import certifi
from ..common.models.control_result import ControlResult
from ..empower.utils.dict_utils import dict_diff
from ..common.tb_constants import TBConstants
from n2k_client.models import ConnectionStatus, Constants
from n2k_client.util.setting_util import SettingsUtil
from n2k_client.util.backoff_util import retry_backoff
import backoff
import datetime
from itertools import islice
import json
from typing import Any, Callable
import simplejson
import os
import logging
import reactivex as rx
from reactivex import operators as ops
from tb_device_mqtt import TBDeviceMqttClient, ProvisionClient
import random
import string
import ssl
import tb_device_mqtt
from enum import Enum

logger = logging.getLogger("ThingsBoardClient")


class CustomJsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


class AttributeDataType(Enum):
    FACTORY_META_DATA = 1
    N2K_SERVER_CONNECTION_STATE = 2
    CLOUD_CONFIG = 3
    ALARM = 4
    BLE_AUTH_KEY = 5
    LOCATION = 6
    POWER_STATUS = 7
    OTHER = 8
    ENGINE_CLOUD_CONFIG = 9


class TelemetryDataType(Enum):
    LOCATION = 1
    OTHER = 2


class EmpowerProvisionClient(ProvisionClient):
    # TLS has to be enabled but ProvisionClient doesn't provide that option
    def __init__(self, host, port, provision_request):
        super().__init__(host, port, provision_request)

    def provision(self, ca_certs=None, cert_file=None, key_file=None):
        logger.info("[EmpowerProvisionClient] Connecting to ThingsBoard")
        self.__credentials = None
        try:
            self.tls_set(
                ca_certs=ca_certs,
                certfile=cert_file,
                keyfile=key_file,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                ciphers=None,
            )
            self.tls_insecure_set(False)
        except ValueError:
            pass
        self.connect(self._host, self._port, 120)
        self.loop_forever()


class ThingsBoardClient:
    _client: TBDeviceMqttClient
    _logger: logging.Logger
    _rpc_handlers: dict[str, Callable[[dict[str, Any]], Any]]
    is_connected: rx.Observable[bool]
    _is_connected_internal: rx.subject.BehaviorSubject[bool]
    _ble_secret_key_uploaded_observable: rx.subject.BehaviorSubject
    _initial_active_alarm_synced_observable: rx.subject.BehaviorSubject
    _initial_attribute_data_synced_observable: rx.subject.BehaviorSubject
    _initial_telemetry_data_synced_observable: rx.subject.BehaviorSubject
    _location_fulfilled_observable: rx.subject.BehaviorSubject
    _location_queued_observable: rx.subject.BehaviorSubject

    # Offline cached values
    offline_attributes: {string, any}
    offline_telemetry_queue: Queue
    telemetry_thread: threading.Thread
    telemetry_thread_event: threading.Event
    # Get the max queue size from appsettings.json
    TELEMETRY_KEY = "TELEMETRY"
    OFFLINE_QUEUE_TELEMETRY_QUEUE_SIZE_KEY = "OFFLINE_QUEUE_TELEMETRY_QUEUE_SIZE"
    queue_size = SettingsUtil.get_setting(
        TELEMETRY_KEY, OFFLINE_QUEUE_TELEMETRY_QUEUE_SIZE_KEY, default_value=3000
    )

    TELEMETRY_OFFLINE_CHUNK_SIZE = "TELEMETRY_OFFLINE_CHUNK_SIZE"
    telemetry_chunk_size = SettingsUtil.get_setting(
        TELEMETRY_KEY, TELEMETRY_OFFLINE_CHUNK_SIZE, default_value=100
    )

    def __init__(self):
        self._logger = logging.getLogger("ThingsBoardClient")
        self._ble_secret_key_uploaded_observable = rx.subject.BehaviorSubject(False)
        self._initial_active_alarm_synced_observable = rx.subject.BehaviorSubject(False)
        self._initial_attribute_data_synced_observable = rx.subject.BehaviorSubject(
            False
        )
        self._initial_telemetry_data_synced_observable = rx.subject.BehaviorSubject(
            False
        )
        self._location_fulfilled_observable = rx.subject.BehaviorSubject(False)
        self._location_queued_observable = rx.subject.BehaviorSubject(False)
        self._is_connected = False
        self.offline_attributes = {}
        self.offline_telemetry_queue = Queue(maxsize=self.queue_size)
        self._client = TBDeviceMqttClient(
            host=get_tb_host(), username=self._get_access_token(), port=get_tb_port()
        )

        # Thingsboard SDK does not have __on_disconnect available to
        # listen to. Set Paho's on_disconnect function to client.py
        # on_disconnect, then pass it to Thingsboard SDK.
        self._client._client.on_disconnect = self.__on_disconnect

        self._client.set_server_side_rpc_request_handler(
            self.__on_server_side_rpc_request
        )

        self._rpc_handlers = {}

        self._is_connected_internal = rx.subject.BehaviorSubject(False)
        self.is_connected = self._is_connected_internal.pipe(
            ops.distinct_until_changed()
        )

        def connection_callback(connected_value):
            # If we are connected, and we have offline state to publish
            # Go through and update the state to thingsboard
            if connected_value:
                if len(self.offline_attributes) > 0:
                    self._logger.info(
                        "Came back from offline state."
                        + " Syncing and updating with stored state"
                    )
                    # Check to see if the value is the same from cloud
                    # Only publish the changes.
                    self.request_state_and_update_cloud()
            else:
                print(
                    "Connection status: " + str(connected_value),
                    " offline attribute size: " + str(len(self.offline_attributes)),
                )

        self._is_connected_internal.subscribe(connection_callback)

        # Create the telemetry thread
        self.telemetry_thread_event = threading.Event()
        self.telemetry_thread = threading.Thread(
            target=self.telemetry_worker, name="Telemetry worker"
        )
        self.telemetry_thread.start()

    def telemetry_worker(self):
        """
        Function to be used on the thread for telemetry
        If we are offline, then we will add the values into this queue.
        We check every wait interval to see if the queue is not empty
        and we are online. We will go back to sleep until we iterate again
        """
        while not self.telemetry_thread_event.wait(0.5):
            try:
                # Check to see if we have any pending items,
                # if there are items, make sure we are connected
                if (
                    not self.offline_telemetry_queue.empty()
                    and self._is_connected_internal.value
                ):
                    chunk_iteration = 0
                    # Need to check the connection status in this queue while we loop so
                    # we don't keep adding the same items back into the queue
                    while (
                        not self.offline_telemetry_queue.empty()
                        and chunk_iteration < self.telemetry_chunk_size
                        and self._is_connected_internal.value
                    ):
                        # Get the oldest message in the telemetry queue
                        telemetry_attributes = self.offline_telemetry_queue.get_nowait()
                        self._logger.info(
                            "Attempting to add telemetry from offline state %s",
                            json.dumps(telemetry_attributes),
                        )
                        # Send it to thingsboard and increment the chunk counter
                        self.send_telemetry(
                            telemetry_attributes, TelemetryDataType.OTHER
                        )
                        chunk_iteration += 1
                        # Need to sleep in between messages otherwise thingsboard will lose messages
                        time.sleep(0.001)
            # Caught an exception, print it out and continue. Need to keep this thread running
            # all the time.
            except Exception as error:
                self._logger.error("Telemetry worker ran into an error")
                self._logger.error(error)
        self._logger.debug("Closing telemetry thread")

    def __del__(self):
        # Stop the telemetry thread
        self.telemetry_thread_event.set()
        # Disconnect from mqtt if we are connected
        # when the destructor is called
        if self._is_connected:
            self._client.disconnect()

    @retry_backoff(
        on_unauthenticated=(),
        giveup=lambda e: not isinstance(e, OSError)
        and "Network is unreachable" not in str(e),
        on_backoff=lambda details: details,
        backoff_algo=backoff.constant,
        interval=10,
    )
    def connect(self):
        self._client.connect(
            callback=self.__on_connect, tls=True, ca_certs=certifi.where()
        )
        self._logger.info("Initiating connection to ThingsBoard...")

    def disconnect(self):
        self._client.disconnect()
        self._logger.info("Disconnecting from ThingsBoard...")

    def request_state_and_update_cloud(self):
        configuration_message_entry = {}
        # If the config is updated when offline pop it from the queue so we
        # don't request it.
        if TBConstants.CONFIG_KEY in self.offline_attributes:
            configuration_message_entry[TBConstants.CONFIG_KEY] = (
                self.offline_attributes.pop(TBConstants.CONFIG_KEY)
            )

        # Get the value from the thingsboard state
        def get_cloud_state_and_store(value):
            self.offline_attributes = dict_diff(value, self.offline_attributes)

            if len(self.offline_attributes) > 0:
                self._logger.info(
                    "Updating offline attributes\n %s",
                    json.dumps(self.offline_attributes),
                )
                # If the checksum is still present, then the config was changed from cloud.
                # Push the configuration as well. Checksum is pushed from offline state.
                if TBConstants.CONFIG_CHECKSUM_KEY in self.offline_attributes:
                    configuration_message_entry[TBConstants.CONFIG_CHECKSUM_KEY] = (
                        self.offline_attributes.pop(TBConstants.CONFIG_CHECKSUM_KEY)
                    )
                    self._logger.info(
                        "Updating offline configuration state with checksum"
                    )
                    self.update_attributes(
                        configuration_message_entry, AttributeDataType.OTHER
                    )
                    # Need to add a sleep so TB client to process both messages.
                    time.sleep(0.001)
                self._logger.info("Updating state from offline")
                self.update_attributes(self.offline_attributes, AttributeDataType.OTHER)
                self.offline_attributes.clear()
            else:
                self._logger.info("No change from offline sync")
                self.handle_attribute_data_synced()

        # Request the values from cloud first.
        self._logger.info("Subscribing to thingsboard request_attributes ")
        # Setup the subscription
        offline_sync_subscription = rx.Subject()
        # Set the subscription callback funciton
        offline_sync_subscription.subscribe(get_cloud_state_and_store)
        self._logger.info("Requesting thingsboard state - offline sync")
        self.request_attributes_state(
            client_attributes=self.offline_attributes.keys(),
            subject=offline_sync_subscription,
        )

    def set_rpc_handler(
        self, method_name: str, handler: Callable[[dict[str, any]], None]
    ):
        self._rpc_handlers[method_name] = handler

    def __on_server_side_rpc_request(self, request_id, request_body):
        logger.info(f"Received RPC request: {request_id} {request_body}")

        if not "method" in request_body:
            logger.error("Invalid RPC request")
            return

        method_name = request_body["method"]
        params = request_body["params"] or {}

        if method_name in self._rpc_handlers:
            try:
                response = self._rpc_handlers[method_name](params)
                if response is not None:
                    self._client.send_rpc_reply(request_id, response)
                else:
                    logger.error(f"Invalid RPC Response from N2k Client")
                    response = ControlResult(
                        False, "Invalid RPC Response from N2k Client"
                    )
                    self._client.send_rpc_reply(request_id, response.to_json())
            except Exception as error:
                logger.error(f"Failed to process RPC request: {error}")
                response = ControlResult(False, str(error))
                self._client.send_rpc_reply(request_id, response.to_json())
        else:
            logger.error(f"RPC method not")
            response = ControlResult(False, "RPC method not found")
            self._client.send_rpc_reply(request_id, response.to_json())

    def to_write_ble_secret_key_to_file_system(self, to_write):
        if to_write:
            json_data = {"secret_key": str(self.ble_auth_key)}
            with open(
                TBConstants.BLE_SECRET_AUTH_KEY_PATH, "w"
            ) as bt_secret_local_file:
                bt_secret_local_file.write(json.dumps(json_data))

    def __on_connect(self, client, userdata, flags, result_code, *extra_params):
        found_auth_key = False
        if os.path.exists(TBConstants.BLE_SECRET_AUTH_KEY_PATH):
            try:
                with open(TBConstants.BLE_SECRET_AUTH_KEY_PATH, "r") as f:
                    json_data = json.load(f)
                    key = json_data["secret_key"]
                    if len(key) == 64:
                        self.ble_auth_key = key
                        found_auth_key = True
                        logger.info("Found valid key")
                    else:
                        os.remove(TBConstants.BLE_SECRET_AUTH_KEY_PATH)
                        logger.info(
                            "Found the key but it's not a valid string. Removing the file"
                        )
            except json.JSONDecodeError as e:
                logger.error(
                    "Failed to parse auth token: " + str(e) + ". Removing the file"
                )
                os.remove(TBConstants.BLE_SECRET_AUTH_KEY_PATH)
            except IOError as e:
                logger.error("Failed to read auth token from file: " + str(e))
        if not found_auth_key:
            raw_key = os.urandom(32)
            self.ble_auth_key = "".join("{:02x}".format(x) for x in raw_key)
            logger.info("Generating a new key to be uploaded to the cloud")
            ble_key_uploaded_observable = self.subscribe_ble_secret_key_uploaded()
            ble_key_uploaded_observable.subscribe(
                lambda to_write: self.to_write_ble_secret_key_to_file_system(to_write)
            )
        self._is_connected_internal.on_next(True)
        self.update_attributes(
            {"BLE_SECRET_AUTH_KEY": self.ble_auth_key}, AttributeDataType.BLE_AUTH_KEY
        )

    def __on_rpc_reply(self, client, userdata, flags, *extra_params):
        logger.debug(userdata)

    def __on_disconnect(self, client, userdata, result_code, properties=None):
        self._is_connected_internal.on_next(False)
        # Send the disconnect event to Thingsboard client, so it can know of the
        # disconnect.
        # pylint: disable=protected-access
        self._client._on_disconnect(client, userdata, result_code, properties)

    def update_attributes(
        self, attributes: dict[str, Any], data_type: AttributeDataType
    ):

        # Check to make sure we are connected first
        if self._is_connected_internal.value:
            try:
                # Function to divide attributes into chunks of 100 items each
                def chunk_attributes(data, size):
                    return (
                        dict(islice(data, item, item + size))
                        for item in range(0, len(data), size)
                    )

                # Divide attributes into chunks of 100
                attributes_chunks = chunk_attributes(attributes.items(), 100)
                attributes_upload_success = True
                for chunk in attributes_chunks:
                    result = self._client.send_attributes(chunk, wait_for_publish=True)
                    if result.get() != tb_device_mqtt.TBPublishInfo.TB_ERR_SUCCESS:
                        attributes_upload_success = False
                if attributes_upload_success:
                    if data_type == AttributeDataType.ALARM:
                        self.handle_alarm_synced()
                    elif data_type == AttributeDataType.OTHER:
                        self.handle_attribute_data_synced()
                    elif data_type == AttributeDataType.BLE_AUTH_KEY:
                        self._handle_ble_secret_key_uploaded()
                    elif data_type == AttributeDataType.LOCATION:
                        self.handle_location_fulfilled()

            except Exception as error:
                logger.error("Failed to update attributes")
                logger.error(error)
                return
        else:
            # If we are not currently connected, add it to the offline state publish attributes
            if attributes is not None:
                self.offline_attributes.update(attributes)
                if data_type == AttributeDataType.LOCATION:
                    self.handle_geolocation_queued()
                    self._logger.info("geolocation attribute update queued")
                self._logger.info("Added state to offline attributes")

    def subscribe_attribute(
        self, attribute_name: str, default_value: Any
    ) -> rx.Observable[Any]:
        # define a default observable
        observable = rx.subject.BehaviorSubject(default_value)

        def handle_attr_update(val, val2):
            observable.on_next(val)

        self._client.subscribe_to_attribute(attribute_name, handle_attr_update)
        return observable

    def subscribe_all_attributes(self, default_value: Any) -> rx.Observable[Any]:
        # define a default observable
        observable = rx.subject.BehaviorSubject(default_value)

        def handle_attr_update(val, val2):
            # data = (val, val2)
            observable.on_next(val)

        self._client.subscribe_to_all_attributes(handle_attr_update)
        return observable

    def _handle_ble_secret_key_uploaded(self):
        self._ble_secret_key_uploaded_observable.on_next(True)

    def subscribe_ble_secret_key_uploaded(self) -> rx.Observable[Any]:
        return self._ble_secret_key_uploaded_observable

    def handle_alarm_synced(self):
        self._initial_active_alarm_synced_observable.on_next(True)

    def subscribe_initial_active_alarm_synced(self) -> rx.Observable[Any]:
        return self._initial_active_alarm_synced_observable

    def handle_attribute_data_synced(self):
        self._initial_attribute_data_synced_observable.on_next(True)

    def subscribe_initial_attribute_data_synced(self) -> rx.Observable[Any]:
        return self._initial_attribute_data_synced_observable

    def _handle_telemetry_data_synced(self):
        self._initial_telemetry_data_synced_observable.on_next(True)

    def subscribe_initial_telemetry_data_synced(self) -> rx.Observable[Any]:
        return self._initial_telemetry_data_synced_observable

    def handle_location_fulfilled(self):
        self._location_fulfilled_observable.on_next(True)

    def subscribe_location_fulfilled(self) -> rx.Observable[Any]:
        return self._location_fulfilled_observable

    def handle_geolocation_queued(self):
        self._location_queued_observable.on_next(True)

    def subscribe_geolocation_queued(self) -> rx.Observable[Any]:
        return self._location_queued_observable

    def send_telemetry(
        self,
        telemetry: dict[str, Any],
        data_type: TelemetryDataType,
        timestamp: int = None,
    ):
        if telemetry is None:
            return

        values_key = "values"
        current_time = int(time.time() * 1000)
        # If timestamp was provided. Convert the dictionary
        # to send TB server to use the timestamp
        if timestamp is not None:
            if timestamp <= current_time:
                new_telemetry = {Constants.ts: timestamp, values_key: {}}
                # add the keys into the values dictionary
                for key in telemetry.keys():
                    new_telemetry[values_key][key] = telemetry[key]
                telemetry = new_telemetry
            else:
                self._logger.debug(
                    f"Failed to use timestamp to send telemetry. Timestamp is ahead of the current time. ts - {timestamp} : values - {telemetry}"
                )

        # If we are connected, then send the telemetry off to mqtt
        # If we are not, then add it to the telemetry queue.
        if self._is_connected_internal.value:
            try:
                result = self._client.send_telemetry(telemetry, wait_for_publish=False)
                if result.get() == tb_device_mqtt.TBPublishInfo.TB_ERR_SUCCESS:
                    if data_type == TelemetryDataType.LOCATION:
                        self.handle_location_fulfilled()
                    elif data_type == TelemetryDataType.OTHER:
                        self._handle_telemetry_data_synced()

            except Exception as error:
                logger.error("Failed to send telemetry")
                logger.error(error)
                return
        else:
            # Try to add the telemetry into the queue. Catch if the exception was that the queue
            # was full. If it is, dequeue the oldest value to put this new value to the back of
            # the queue.
            try:
                logger.info("putting telemetry to offline queue")
                self.offline_telemetry_queue.put_nowait(telemetry)
            except queue.Full:
                # Queue was full when attempting to add
                # Remove the oldest value in order to add the newest value in
                self._logger.info(
                    "Failed to add telemetry,"
                    + " removing oldest value before adding new value"
                )
                # Get the oldest value
                dequeue_value = self.offline_telemetry_queue.get_nowait()
                # Print the value we are removing
                self._logger.info("Removed Telemetry Item %s", dequeue_value)
                # Insert the newest value into thte queue
                self.offline_telemetry_queue.put_nowait(telemetry)

    def send_client_side_rpc_request(self, method, params):
        try:
            result = self._client.send_rpc_call(
                method, params, callback=self.__on_rpc_reply
            )
        except Exception as error:
            logger.error("Failed to send rpc command")
            logger.error(error)
            return

    def _get_access_token(self):
        # Case 1: TB_ACCESS_TOKEN exists in env (Testing with device already provisioned manually)
        logger.info("getting access token")
        if (
            "TB_ACCESS_TOKEN" in os.environ
            and os.environ["TB_ACCESS_TOKEN"] != ""
            and os.environ["TB_ACCESS_TOKEN"] != "{YOUR ACCESS TOKEN}"
        ):
            logger.info("Found TB_ACCES_TOKEN in env. Overriding local access token")
            return os.environ["TB_ACCESS_TOKEN"]
        else:
            if os.path.exists(TBConstants.TB_ACCESS_TOKEN_PATH):
                with open(TBConstants.TB_ACCESS_TOKEN_PATH, "r") as file:
                    tb_access_token = file.read().rstrip()
                    # Case 2: TB_ACCESS_TOKEN doesn't exist in env but we have the access token stored in /data/ (Device provisioned by itself previously)
                    logger.info("Found TB_ACCES_TOKEN in local file")
                    return tb_access_token
            else:
                logger.warning("tb_access_token file not found")
                # Case 3: TB_ACCESS_TOKEN doesn't exist in env and no access token stored in /data/ but we have TB_PROV_KEY and TB_PROV_SECRET in env (Device ready for provisioning)
                if "TB_PROV_KEY" in os.environ and "TB_PROV_SECRET" in os.environ:
                    if os.path.exists(TBConstants.SN_PATH):
                        with open(TBConstants.SN_PATH, "r") as file:
                            logger.info(
                                "Found PROV_KEY, PROV_SECRET, and SN. Ready to provision"
                            )
                            serial_number = file.read().rstrip()
                            provision_request = {
                                "provisionDeviceKey": os.environ["TB_PROV_KEY"],
                                "provisionDeviceSecret": os.environ["TB_PROV_SECRET"],
                            }
                            provision_request["deviceName"] = serial_number
                            prov_client = EmpowerProvisionClient(
                                get_tb_host(), get_tb_port(), provision_request
                            )
                            prov_client.provision()
                            credentials = prov_client.get_credentials()
                            if (
                                credentials is not None
                                and credentials.get("status") == "SUCCESS"
                            ):
                                if credentials["credentialsType"] == "ACCESS_TOKEN":
                                    tb_access_token = credentials["credentialsValue"]
                                    # Remove BT Access token if it exists
                                    if os.path.exists(
                                        TBConstants.BLE_SECRET_AUTH_KEY_PATH
                                    ):
                                        self._logger.info(
                                            "Removing BT ACCESS token file"
                                        )
                                        os.remove(TBConstants.BLE_SECRET_AUTH_KEY_PATH)
                                    else:
                                        self._logger.info(
                                            "No BT ACCESS token file found"
                                        )
                                    with open(
                                        TBConstants.TB_ACCESS_TOKEN_PATH, "w"
                                    ) as credentials_file:
                                        credentials_file.write(tb_access_token)
                                    return tb_access_token
                                else:
                                    logger.error("credentials type doesn't match")
                            else:
                                logger.error("provisioning failed")
                            return None
                    else:
                        # Case 4: Not provisioned and can't provision itself because there is no serial number
                        logger.error("serial_number file not found, can't provision")
                        return None
                # Case 5: Not provisioned and can't provision itself because there is no PROV_KEY and PROV_SECRET
                logger.error("TB_PROV_KEY and/or SECRET not found, can't provision")
                return None

    def request_attributes_state(
        self,
        subject: rx.Subject,
        client_attributes: list[str] = None,
        shared_attributes: list[str] = None,
    ):
        """
        Get the values of the specified attributes from Thingsboard.

        Parameters:
        - subject: The subscription to return the values from the Thingsboard call.
        - client_attributes: List of client attributes to get the values of.
        - shared_attributes: List of shared attributes to get the values of.
        """
        try:
            # Function to process the return value from thingsboard.request_attributes
            def return_values(value, exception):
                # If there was an exception from the call return {} and log the error
                if exception is not None:
                    subject.on_next({})
                    subject.on_completed()
                    logger.error("There was an error in the request_attributes")
                    logger.error(exception)
                else:
                    # Else the call was successful, process the data
                    # Remove the 'client' entry to process
                    # Client entry are the client attributes from thingsboard
                    client_key = "client"
                    attribute_dict = {}
                    if client_key in value:
                        attribute_dict = value.pop(client_key)
                    # Go through each of the 'client' keys
                    for key in attribute_dict.keys():
                        if isinstance(attribute_dict[key], dict):
                            dict_val = attribute_dict[key]
                            if Constants.state in dict_val.keys() and not isinstance(
                                dict_val[Constants.state], bool
                            ):
                                attribute_dict[key][Constants.state] = ConnectionStatus(
                                    dict_val[Constants.state]
                                )
                        # If the value returned was a list, convert it to a
                        # dict entry with the state and timestamp
                        elif isinstance(attribute_dict[key], list):
                            list_val = attribute_dict[key]
                            # Check the length of the list
                            if len(list_val) != 2:
                                continue
                            # Convert the connection string to the enum value
                            conn_status = ConnectionStatus(list_val[0])
                            # Create the dictionary entry for that key
                            attribute_dict[key] = {
                                Constants.ts: list_val[1],
                                Constants.state: conn_status,
                            }
                    # merge the value dictionary into the client dictionary
                    # return the client_dictionary
                    attribute_dict.update(value)

                    shared_key = "shared"
                    if shared_key in value:
                        attribute_dict.update(value.pop(shared_key))

                    subject.on_next(attribute_dict)
                    subject.on_completed()

            logger.info("Try to get updated results")
            # Make the thingsboard client request, set the callback to the processing function
            if self._is_connected_internal.value:
                self._client.request_attributes(
                    client_keys=client_attributes,
                    shared_keys=shared_attributes,
                    callback=return_values,
                )
            else:
                # We are currently offline, return empty dictionary
                return_values({}, None)
        except Exception as error:
            logger.error("Error trying to attributes")
            logger.error(error)


def get_tb_host():
    if (
        "TB_HOST" in os.environ
        and os.environ["TB_HOST"] != ""
        and os.environ["TB_HOST"] != "{YOUR TB HOST ENDPOINT}"
    ):
        return os.environ["TB_HOST"]
    else:
        return "mqtt.empower-czone.com"


def get_tb_port():
    if (
        "TB_PORT" in os.environ
        and os.environ["TB_PORT"] != ""
        and os.environ["TB_PORT"] != "[TB_PORT]"
        and os.environ["TB_PORT"] != "{YOUR TB HOST PORT}"
    ):
        try:
            return int(os.environ["TB_PORT"])
        except ValueError as e:
            logger.error(e)
            logger.info("returning default port 8883")
            return 8883
    else:
        return 8883
