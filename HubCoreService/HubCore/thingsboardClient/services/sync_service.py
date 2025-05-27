"""
SyncService class for Thingsboard Client
"""
import logging
import os
import sys
import threading
import typing
import reactivex as rx
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
#pylint: disable=import-error, wrong-import-position
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
    _initialized = False

    _mqtt_client = ThingsBoardClient()

    _attributes: dict[str, rx.subject.BehaviorSubject] = {}
    _disposables: list[rx.disposable.Disposable] = []

    _last_connected_value = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
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
            files_and_paths = [(os.path.join(Constants.TB_CONSENTS_PATH, f), f) for f in files
                    if os.path.isfile(os.path.join(Constants.TB_CONSENTS_PATH, f))
                ]
            print("FILES AND PATHS:", files_and_paths)
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
        disposable = self._mqtt_client.is_connected.subscribe(connection_callback)
        self._disposables.append(disposable)

    def __del__(self):
        """
        Clean up the instance when it is deleted.
        """
        if self._mqtt_client._is_connected_internal.value:
            self._logger.info("Disconnecting from Thingsboard...")
            self._mqtt_client.disconnect()
        self._logger.info("Deleting mqtt client instance...")
        self._mqtt_client.__del__()
        self._instance = None
        self._initialized = False
        self._attributes.clear()

    def get_attribute_dictionary(self):
        """
        Get the attributes stored in the SyncService.
        """
        return self._attributes

    def get_attribute_subject(self, key):
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

    def _update_value(self, value: typing.Optional[dict[str, any]]):
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
                    self._logger.info("Attribute '%s' changed from '%s' to '%s'.",
                        key,
                        self._attributes[key].value,
                        val
                    )
                    self._attributes[key].on_next(val)
            else:
                self._logger.warning("%s not found or attribute %s is none", key, str(val))
                self._attributes[key] = rx.subject.BehaviorSubject(val)
                self._logger.info("Created new BehaviorSubject for attribute '%s'.", key)

    def subscribe_to_attribute(self, key: str):
        """
        Subscribe to an attribute in the SyncService.
        If the attribute does not exist, it will be created.
        """
        if key not in self._attributes:
            self._logger.info("Creating new BehaviorSubject for attribute '%s'.", key)
            self._attributes[key] = rx.subject.BehaviorSubject(None)
            attribute_subscription = self._mqtt_client.subscribe_attribute(key, None)
            self._disposables.append(attribute_subscription.subscribe(self._update_value))
        else:
            self._logger.info("Attribute '%s' already exists, subscription exists", key)

    def reconnect_sync(self):
        """
        Reconnect to the Thingsboard client and grab all of the attributes.
        This method should be called when the Thingsboard client reconnects.
        """
        if len(self._attributes.keys()) == 0:
            self._logger.warning("No attributes to resubscribe to, skipping reconnection.")
            return
        self._logger.info("Reconnecting to Thingsboard and syncing attributes...")
        keys = list(self._attributes.keys())
        subject = rx.subject.BehaviorSubject(None)
        subject.subscribe(self._update_value)
        self._mqtt_client.request_attributes_state(subject=subject, shared_attributes=keys)
