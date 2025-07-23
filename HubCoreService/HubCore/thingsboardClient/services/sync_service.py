"""
SyncService class for Thingsboard Client
"""
import json
import logging
import os
import sys
import threading
from typing import Optional, Any
import reactivex as rx

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# pylint: disable=import-error, wrong-import-position
from mqtt_client import ThingsBoardClient
from tb_utils.constants import Constants

class SyncService:
    """
    Thingsboard Client singleton class to connect to sync and store values from
    the thingsboard attribute that need to persist locally via file and synced
    again after reconnecting.

    Currently will only do shared attributes from thingsboard.
    """
    _logger = logging.getLogger(__name__)

    _instance = None
    _lock = threading.Lock()

    _mqtt_client = ThingsBoardClient()
    _attributes: dict[str, rx.subject.BehaviorSubject] = {}
    _connection_disposable: rx.disposable.Disposable = None
    _disposables: list[rx.disposable.Disposable] = []
    _last_connected_value = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SyncService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        # Read files here and have connection subscription for thingsboard client
        try:
            # Read the files from the local directory
            self._logger.info("Reading files for attributes...")
            files = os.listdir(Constants.TB_CONSENTS_PATH)
            files_and_paths = [
                (os.path.join(Constants.TB_CONSENTS_PATH, f), f)
                for f in files
                if (
                    os.path.isfile(os.path.join(Constants.TB_CONSENTS_PATH, f))
                    and f.endswith('.json')
                )
            ]
            self._logger.debug("Files and paths: %s", files_and_paths)
            for file_path, file_name in files_and_paths:
                try:
                    attribute_name = file_name[:-5]  # Remove .json extension
                    self._logger.debug("Attribute name: %s", attribute_name)
                    with open(file_path, 'r', encoding="utf-8") as file:
                        json_data = json.load(file)
                        if json_data and "value" in json_data:
                            value = json_data.get("value", None)
                            if attribute_name not in self._attributes:
                                self._logger.info(
                                    "Creating BehaviorSubject for attribute '%s' with '%s'",
                                    attribute_name,
                                    str(value)
                                )
                                self._attributes[attribute_name] = rx.subject.BehaviorSubject(value)
                            else:
                                self._logger.info(
                                    "Attribute '%s' already exists, skipping creation.",
                                    attribute_name
                                )
                                self._attributes[attribute_name].on_next(value)
                            self.subscribe_to_attribute(attribute_name)
                except Exception as e:
                    self._logger.error(
                        "Error extracting attribute name from file %s: %s", file_name, e
                    )
                    if len(file_name) > 5 and file_name.endswith('.json'):
                        self.subscribe_to_attribute(file_name[:-5])  # Fallback to subscribe to attribute name
                    continue
        except FileNotFoundError as e:
            self._logger.error("Directory %s not found: %s", Constants.TB_CONSENTS_PATH, e)
            self._logger.info("Creating directory %s...", Constants.TB_CONSENTS_PATH)
            os.makedirs(Constants.TB_CONSENTS_PATH, exist_ok=True)
            return
        except Exception as e:
            self._logger.error("Error reading files: %s", e)

        def connection_callback(connected_value):
            if connected_value and self._last_connected_value is False:
                self._logger.info("Connected to Thingsboard, syncing attributes...")
                self.reconnect_sync()
            self._last_connected_value = connected_value

        self._connection_disposable = self._mqtt_client.is_connected.subscribe(connection_callback)

    def __del__(self):
        """
        Clean up the instance when it is deleted.
        """
        try:
            if getattr(self._mqtt_client, "_is_connected_internal", None) and getattr(self._mqtt_client._is_connected_internal, "value", False):
                self._logger.info("Disconnecting from Thingsboard...")
                self._mqtt_client.disconnect()
            self._logger.info("Deleting mqtt client instance...")
            self._mqtt_client.__del__()
        except Exception as e:
            self._logger.error("Error during cleanup: %s", e)
        self._instance = None
        self._initialized = False
        if hasattr(self, "_attributes"):
            self._attributes.clear()
        if hasattr(self, "_connection_disposable") and self._connection_disposable:
            self._connection_disposable.dispose()
        if hasattr(self, "_disposables"):
            for disposable in self._disposables:
                if disposable is not None:
                    disposable.dispose()

    def get_attribute_dictionary(self):
        """
        Get the attributes stored in the SyncService.
        """
        return self._attributes

    def get_attribute_subject(self, key: str):
        """
        Get a specific attribute subject from the SyncService.
        Will return None if the attribute does not exist.
        """
        if key not in self._attributes:
            self._logger.error("Attribute '%s' not found in SyncService.", key)
            return None
        return self._attributes.get(key, None)

    def get_attribute_value(self, key: str):
        """
        Get a specific attribute value from the SyncService.
        Will return None if the attribute does not exist.
        """
        result = self.get_attribute_subject(key)
        if result is not None:
            return result.value
        return None

    def _update_value(self, value: Optional[dict[str, Any]]):
        """
        Update the value of the attributes in the sync service and notify subscribers.
        This method is called when a new value is received from the Thingsboard client.
        If the value is None, it will not update the attributes.
        """
        if value is None:
            self._logger.warning("Received None value, not updating attributes.")
            return

        for key, val in value.items():
            if key in self._attributes and val is not None:
                if val != self._attributes[key].value:
                    self._logger.info(
                        "Attribute '%s' changed from '%s' to '%s'.",
                        key,
                        self._attributes[key].value,
                        val
                    )
                    self._attributes[key].on_next(val)
                    self._update_file(key, val)
            else:
                if key != "shared": # Shared key is just another dictionary for shared attributes
                    self._logger.warning("%s not found, creating new entry with %s", key, str(val))
                    self._attributes[key] = rx.subject.BehaviorSubject(val)
                    self._logger.info("Created new BehaviorSubject for attribute '%s'.", key)

    def _update_file(self, key: str, value: Any):
        """
        Update the file for the attribute with the given key.
        This method will create a new file if it does not exist.
        """
        file_path = os.path.join(Constants.TB_CONSENTS_PATH, f"{key}.json")
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(json.dumps({"value": value}, ensure_ascii=False, indent=2))
            self._logger.info("Updated file for attribute '%s' with value '%s'.", key, str(value))
        except Exception as e:
            self._logger.error("Error updating file for attribute '%s': %s", key, e)

    def subscribe_to_attribute(self, key: str):
        """
        Subscribe to an attribute in the SyncService.
        If the attribute does not exist, it will be created.
        """
        if key not in self._attributes:
            self._logger.info("Creating new BehaviorSubject for attribute '%s'.", key)
            self._attributes[key] = rx.subject.BehaviorSubject(None)
        else:
            self._logger.info("Attribute '%s' already exists", key)
        self._logger.info("Thingsboard subscribing to attribute '%s'.", key)
        attribute_subscription = self._mqtt_client.subscribe_attribute(key, None)
        self._disposables.append(attribute_subscription.subscribe(self._update_value))

    def reconnect_sync(self):
        """
        Reconnect to the Thingsboard client and grab all of the attributes.
        This method should be called when the Thingsboard client reconnects.
        """
        if len(self._attributes.keys()) == 0:
            self._logger.warning("No attributes to resubscribe to, skipping reconnection.")
            return
        self._logger.info("Reconnecting to Thingsboard and syncing attributes...")
        for disposable in self._disposables:
            if disposable is not None:
                disposable.dispose()
        self._disposables.clear()
        keys = list(self._attributes.keys())
        for key in keys:
            self.subscribe_to_attribute(key)
        self._logger.info("Requesting attributes state for keys: %s", keys)
        subject = rx.subject.BehaviorSubject(None)
        subject.subscribe(self._update_value)
        self._mqtt_client.request_attributes_state(subject=subject, shared_attributes=keys)
