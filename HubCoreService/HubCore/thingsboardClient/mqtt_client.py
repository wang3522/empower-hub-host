"""
Thingsboard Client
This module is used to connect to Thingsboard and send telemetry and attributes.
It uses the Thingsboard MQTT client to connect to the Thingsboard server and send data.
It also handles offline state and stores telemetry and attributes in a queue when offline.
It uses the reactivex library to handle observables and subscriptions.
"""
from multiprocessing import Queue
import queue
import threading
import time
from typing import Any, Callable
import logging
from itertools import islice
import json
import string
import reactivex as rx
from reactivex import operators as ops
from tb_device_mqtt import TBDeviceMqttClient
#pylint: disable=import-error
from tb_utils.tb_client_logger import configure_logging
from tb_utils.constants import Constants
from tb_utils.utility import (
    ConnectionStatus,
    ControlResult,
    MessageType,
    get_tb_host,
    get_tb_port,
    get_access_token
)
from dict_diff import dict_diff

class ThingsBoardClient:
    """
    Thingsboard Client singleton class to connect to Thingsboard and send telemetry and attributes.
    """
    _client: TBDeviceMqttClient
    _logger = logging.getLogger("ThingsBoardClient")
    _rpc_handlers: dict[str, Callable[[dict[str, Any]], Any]]
    is_connected: rx.Observable[bool]
    _is_connected_internal: rx.subject.BehaviorSubject[bool]

    # Offline cached values
    offline_attributes: {string, any}
    offline_telemetry_queue: Queue
    telemetry_thread: threading.Thread
    telemetry_thread_event: threading.Event
    attributes_thread: threading.Thread
    attributes_thread_event: threading.Event
    # Get the max queue size from appsettings.json
    queue_size = 3000
    telemetry_chunk_size = 100

    # Cached last known values
    last_telemetry: dict[str, Any] = {}
    last_attributes: dict[str, Any] = {}
    last_attributes_lock = threading.Lock()

    attribute_dictionary: dict[str, Any] = {}
    attribute_dictionary_lock = threading.Lock()

    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ThingsBoardClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True
        self._is_connected = False
        self.offline_attributes = {}
        self.offline_telemetry_queue = Queue(maxsize=self.queue_size)
        self._client = TBDeviceMqttClient(
            host=get_tb_host(), username=get_access_token(), port=get_tb_port()
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

    def _create_attributes_thread(self):
        """
        Create the attributes thread
        """
        self.attributes_thread_event = threading.Event()
        self.attributes_thread = threading.Thread(
            target=self.attributes_worker, name="Attributes worker"
        )
        self.attributes_thread.start()

    def attributes_worker(self):
        """
        Function to be used on the thread for attributes
        This will check every wait interval to see if there are any attributes
        to send to Thingsboard. If we are online, then we will send the attributes then update
        the last known attributes.
        """
        self._logger.info("Starting attributes worker thread")
        while not self.attributes_thread_event.wait(0.5):
            try:
                # Check to see if we have any pending items,
                # if there are items, make sure we are connected
                if (
                    len(self.attribute_dictionary) != 0
                    and self._is_connected_internal.value
                ):
                    # Copy the attribute dictionary to a temporary dictionary and clear the original
                    temp_attributes = {}
                    with self.attribute_dictionary_lock:
                        temp_attributes = self.attribute_dictionary.copy()
                        self.attribute_dictionary.clear()
                    # Send the attributes to Thingsboard
                    self._chunk_and_send_attributes(temp_attributes)
                    # Update the last known state with the attributes we sent
                    with self.last_attributes_lock:
                        self.last_attributes.update(temp_attributes)
                    self._logger.info(
                        "Sending attributes from attribute dictionary %s",
                        json.dumps(temp_attributes),
                    )
            except Exception as error:
                # Caught an exception, print it out and continue. Need to keep this thread running
                # all the time.
                self._logger.error("Attributes worker ran into an error")
                self._logger.error(error)
        self._logger.debug("Closing attributes thread")


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
                        self.send_telemetry(telemetry_attributes)
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
        # Stop the attributes thread
        self.attributes_thread_event.set()
        # Disconnect from mqtt if we are connected
        # when the destructor is called
        if self._is_connected:
            self._client.disconnect()

    # TODO Add some sort of backoff retry logic to this
    def connect(self):
        """
        Connect to Thingsboard.
        """
        self._client.connect(callback=self.__on_connect, tls=True)
        self._logger.info("Initiating connection to ThingsBoard...")

    def disconnect(self):
        """
        Disconnect from Thingsboard.
        """
        self._client.disconnect()
        self._logger.info("Disconnecting from ThingsBoard...")

    def request_state_and_update_cloud(self):
        """
        Request the state from Thingsboard and update the cloud with the
        offline attributes.
        This is used when the device comes back online and has offline
        attributes to update.
        """
        configuration_message_entry = {}
        # If the config is updated when offline pop it from the queue so we
        # don't request it.
        if Constants.CONFIG_KEY in self.offline_attributes:
            configuration_message_entry[Constants.CONFIG_KEY] = (
                self.offline_attributes.pop(Constants.CONFIG_KEY)
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
                if Constants.CONFIG_CHECKSUM_KEY in self.offline_attributes:
                    configuration_message_entry[Constants.CONFIG_CHECKSUM_KEY] = (
                        self.offline_attributes.pop(Constants.CONFIG_CHECKSUM_KEY)
                    )
                    self._logger.info(
                        "Updating offline configuration state with checksum"
                    )
                    self.update_attributes(configuration_message_entry)
                    # Need to add a sleep so TB client to process both messages.
                    time.sleep(0.001)
                self._logger.info("Updating state from offline")
                self.update_attributes(self.offline_attributes)
                self.offline_attributes.clear()
            else:
                self._logger.info("No change from offline sync")

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
        """
        Set the RPC handler for the given method name.
        """
        self._rpc_handlers[method_name] = handler

    def __on_server_side_rpc_request(self, request_id, request_body):
        self._logger.info("Received RPC request: %s %s", str(request_id), request_body)

        method_name = request_body.get("method", None)
        params = request_body.get("params", {})

        if method_name is None or method_name not in self._rpc_handlers:
            self._logger.error("RPC method not found: %s", method_name)
            response = ControlResult(False, "RPC method not found")
            self._client.send_rpc_reply(request_id, response.to_json())

        try:
            response = self._rpc_handlers[method_name](params)
            if response is not None:
                self._client.send_rpc_reply(request_id, response)
            else:
                self._logger.error("Invalid RPC Response from N2k Client")
                response = ControlResult(
                    False, "Invalid RPC Response from N2k Client"
                )
                self._client.send_rpc_reply(request_id, response.to_json())
        except Exception as error:
            self._logger.error("Failed to process RPC request: %s", error)
            response = ControlResult(False, str(error))
            self._client.send_rpc_reply(request_id, response.to_json())


    # pylint: disable=unused-argument
    def __on_connect(self, client, userdata, flags, result_code, *extra_params):
        self._is_connected_internal.on_next(True)
        self._create_attributes_thread()

    def __on_disconnect(self, client, userdata, result_code, properties=None):
        try:
            self.attributes_thread_event.set()
        except Exception as error:
            self._logger.error("Failed to stop attributes thread upon disconnect")
            self._logger.error(error)
        self._is_connected_internal.on_next(False)
        # Send the disconnect event to Thingsboard client, so it can know of the
        # disconnect.
        # pylint: disable=protected-access
        self._client._on_disconnect(client, userdata, result_code, properties)

    def process_changes(self,
                new_changes: dict[str, Any],
                last_known_state: dict[str, Any],
                log_message,
            ):
        """
        Process the changes to the attributes/telemetry and send them to Thingsboard.
        """
        attrs_to_send = None
        # If there are no changes, then return None
        if not last_known_state:
            last_known_state.update(new_changes)
            attrs_to_send = new_changes
        else:
            # Check to see if the new changes are in the last known state
            diff_attrs = dict_diff(last_known_state, new_changes)
            # If there are changes, then update the last known state
            if diff_attrs:
                last_known_state.update(new_changes)
                attrs_to_send = diff_attrs
        # If there are changes, then reutrn the changes
        # If there are no changes, then return None
        if attrs_to_send:
            self._logger.debug("%s %s", log_message, json.dumps(attrs_to_send))
            return attrs_to_send
        return None


    def update_attributes(self, attributes: dict[str, Any]):
        """
        Update the attributes on Thingsboard. If we are not connected,
        add the attributes to the offline queue.
        If we are connected, send the attributes to Thingsboard.
        """

        # Check to make sure we are connected first
        if self._is_connected_internal.value is False:
            # If we are not currently connected, add it to the offline state publish attributes
            if attributes is not None:
                self.offline_attributes.update(attributes)
                self._logger.info("Added state to offline attributes %s", attributes.keys())
                return
        # If we are connected, then send the attributes off to mqtt
        try:
            # Check to see if the attributes are in the last known state.
            not_cached, not_cached_dict, attributes = self.check_for_missing_cache(
                attributes=attributes,
                message_type=MessageType.ATTRIBUTE,
            )

            # Check to see if the attributes are in the last known state.
            # If they are not, then add them to the list to send out.
            new_attributes = self.process_changes(
                new_changes=attributes,
                last_known_state=self.last_attributes,
                log_message="Adding attributes to state",
            )

            if (new_attributes is None or len(new_attributes) == 0) and len(not_cached) == 0:
                self._logger.debug("No changes in attributes to send")
                return

            if len(not_cached) > 0:
                if new_attributes is None:
                    new_attributes = {}
                # Check from cloud to see if the value is the same
                # Only publish the changes.
                self._logger.info(
                    "Requesting attributes from cloud to check for changes %s",
                    json.dumps(not_cached)
                )
                # Request the attributes from Thingsboard and update
                # the attributes with the new values.
                self.request_then_update_attributes(
                    not_cached=not_cached,
                    not_cached_dict=not_cached_dict,
                    new_attributes=new_attributes
                )
            else:
                # The value is different from the last known state
                # Update the last known state
                self._logger.info(
                    "Updating last known state with new attributes %s",
                    json.dumps(new_attributes)
                )
                with self.last_attributes_lock:
                    self.last_attributes.update(new_attributes)
                self._add_attributes_to_dictionary(new_attributes)
        except Exception as error:
            self._logger.error("Failed to update attributes")
            self._logger.error(error)
            return

    def request_then_update_attributes(self,
            not_cached: list[str],
            not_cached_dict: dict[str, Any],
            new_attributes: dict[str, Any]
        ):
        """
        Request the attributes from Thingsboard and update the attributes with the new values.
        """
        request_subject = rx.Subject()
        def request_attributes_callback(value):
            # If the value is different from the last known state
            # Update the last known state
            self._logger.info(
                "Updating last known state with new attributes %s",
                json.dumps(value)
            )
            attribtues_to_send = self.process_changes(
                    new_changes=not_cached_dict,
                    last_known_state=value,
                    log_message="Adding attributes to state from cloud sync"
                ) or {}
            new_attributes.update(attribtues_to_send)
            # Update the last known state first with the not cached values in the event
            # that the values are not in the last known state and are the same as the cloud.
            # Then update the last known state with the new attributes.
            with self.last_attributes_lock:
                self.last_attributes.update(not_cached_dict)
                self.last_attributes.update(new_attributes)
            # Check to see if the value is the same from cloud
            # Only publish the changes.
            self._add_attributes_to_dictionary(new_attributes)

        request_subject.subscribe(request_attributes_callback)
        self.request_attributes_state(
            subject=request_subject,
            client_attributes=not_cached,
            shared_attributes=None,
        )

    def check_for_missing_cache(self, attributes: dict[str, Any], message_type: MessageType):
        """
        Check to see if the attributes are in the last known state.
        If they are not, then add them to the not cached list.
        """
        dict_to_check = {}
        if message_type == MessageType.ATTRIBUTE:
            dict_to_check = self.last_attributes
        elif message_type == MessageType.TELEMETRY:
            dict_to_check = self.last_telemetry
        not_cached = []
        not_cached_dict = {}
        attribute_keys = attributes.keys()
        for key in attribute_keys:
            if key not in dict_to_check:
                not_cached.append(key)
        for key in not_cached:
            if key in attributes:
                not_cached_dict[key] = attributes.pop(key)

        return not_cached, not_cached_dict, attributes

    def _add_attributes_to_dictionary(self, attributes: dict[str, Any]):
        """
        Add the attributes to the attribute dictionary.
        This is used to update the attributes when we are offline.
        """
        if attributes is None or len(attributes) == 0:
            self._logger.debug("No attributes to add to dictionary")
            return
        with self.attribute_dictionary_lock:
            self.attribute_dictionary.update(attributes)
            self._logger.info(
                "Adding attributes to dictionary %s", json.dumps(attributes)
            )

    def _chunk_and_send_attributes(
        self, attributes: dict[str, Any], chunk_size: int = 100):
        if attributes is None or len(attributes) == 0:
            self._logger.debug("chunk_and_send_attributes No attributes to send")
            return

        self._logger.debug(
            "chunk_and_send_attributes %s", json.dumps(attributes)
        )
        try:
            # Function to divide attributes into chunks of 100 items each
            def chunk_attributes(data, size):
                return (
                    dict(islice(data, item, item + size))
                    for item in range(0, len(data), size)
                )

            # Divide attributes into chunks of 100
            attributes_chunks = chunk_attributes(attributes.items(), 100)
            for chunk in attributes_chunks:
                _ = self._client.send_attributes(chunk, wait_for_publish=True)
        except Exception as error:
            self._logger.error("Failed to send attributes")
            self._logger.error(error)
            return


    def subscribe_attribute(
        self, attribute_name: str, default_value: Any
    ) -> rx.Observable[Any]:
        """
        Subscribe to a specific attribute and return an observable that emits
        the attribute value whenever it changes.
        """
        # define a default observable
        observable = rx.subject.BehaviorSubject(default_value)

        def handle_attr_update(val, val2):
            observable.on_next(val)

        self._client.subscribe_to_attribute(attribute_name, handle_attr_update)
        return observable

    def send_telemetry(
        self,
        telemetry: dict[str, Any],
        timestamp: int = None,
    ):
        """
        Send telemetry to Thingsboard. If we are not connected, add the telemetry
        to the offline queue. If we are connected, send the telemetry to Thingsboard.
        """
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
                    "Failed to use timestamp to send telemetry."+
                    "Timestamp is ahead of the current time. ts - %d : values - %s",
                    timestamp,
                    telemetry
                )

        # If we are connected, then send the telemetry off to mqtt
        # If we are not, then add it to the telemetry queue.
        if self._is_connected_internal.value:
            try:
                _ = self._client.send_telemetry(telemetry, wait_for_publish=False)
            except Exception as error:
                self._logger.error("Failed to send telemetry")
                self._logger.error(error)
                return
        else:
            # Try to add the telemetry into the queue. Catch if the exception was that the queue
            # was full. If it is, dequeue the oldest value to put this new value to the back of
            # the queue.
            try:
                self._logger.info("putting telemetry to offline queue")
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
                    self._logger.error("There was an error in the request_attributes")
                    self._logger.error(exception)
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

            self._logger.info("Try to get updated results")
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
            self._logger.error("Error trying to attributes")
            self._logger.error(error)

if __name__ == "__main__":
    configure_logging()
    # Example usage
    outside_client = ThingsBoardClient()
    outside_client.connect()
    #pylint: disable=protected-access
    while not outside_client._is_connected_internal.value:
        time.sleep(1)
    print("Connected to Thingsboard")
    COUNTER = 0
    while COUNTER < 5:
        print("Sending telemetry and attributes")
        # Simulate sending telemetry
        loop_client = ThingsBoardClient()
        loop_client.send_telemetry({"temperature": 25, "humidity": 60})
        # Simulate updating attributes
        if COUNTER == 1:
            loop_client.update_attributes({"location": "home", "status": "active"})
        else:
            loop_client.update_attributes({"location": "home"})
        COUNTER += 1
        time.sleep(3)
    outside_client.disconnect()
    outside_client.__del__()
    print("Disconnected from Thingsboard")
