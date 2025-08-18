# N2KClient/n2kclient/dbus_proxy.py

import logging
import threading
from typing import Callable
import dbus
from time import sleep

from ...util.settings_util import SettingsUtil
from ...models.constants import Constants
from ...models.dbus_connection_status import DBUSConnectionStatus
from ...util.time_util import TimeUtil
import platform
from ...models.common_enums import ConnectionStatus


class DbusProxyService:
    """
    Proxy service for interacting with the N2K DBus interface.
    Handles connection, method registration, signal handling, and retry logic for DBus calls.
    Attributes:
        status_callback: Optional callback function to report connection status changes.
        event_handler: Optional handler function for DBus events.
        snapshot_handler: Optional handler function for DBus snapshots.
        control_max_attempts: Maximum number of retry attempts for control operations.
        lock: Threading lock to ensure thread-safe DBus access.
        _logger: Logger instance for logging messages.
        _dbus_retry_delay: Delay in seconds between DBus retry attempts, read from settings
    Methods:
        __init__: Initializes the DBus proxy service with optional callbacks and settings.
        connect: Establishes the DBus connection with retry logic.
        _connect_dbus: Internal method to set up the DBus connection and register handlers.
        _register_signal_handlers: Registers signal handlers (Event + Snapshot) for DBus events and snapshots.
        _register_methods: Maps DBus service methods to instance attributes.
        _report_status: Helper to report connection status via callback.
        _call_with_retry: Calls a DBus method with retry logic and status reporting.
        get_config: Retrieves specific component type N2K configuration via DBus.
        get_config_all: Retrieves full N2K configurations via DBus.
        get_categories: Retrieves categories via DBus.
        get_setting: Retrieves setting via DBus.
        control: Sends control command via DBus with retry.
        alarm_acknowledge: Acknowledges alarm via DBus with retry.
        alarm_list: Retrieves full alarm list via DBus.
        single_snapshot: Retrieves full single snapshot via DBus.
        put_file: Sends a file to the host via DBus.
        operation: Performs an operation on the host via DBus.
    """

    _logger = logging.getLogger("DBUS Proxy Helper")
    _dbus_retry_delay = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.WORKER_KEY,
        Constants.DBUS_RETRY_DELAY_KEY,
        default_value=5,
    )

    # Class-level constant for DBus method name mapping
    DBUS_METHOD_MAP = [
        ("_dbus_get_config", Constants.GET_CONFIG_SERVICE_METHOD_NAME),
        ("_dbus_get_config_all", Constants.GET_CONFIG_ALL_SERVICE_METHOD_NAME),
        ("_dbus_get_categories", Constants.GET_CATEGORIES_SERVICE_METHOD_NAME),
        ("_dbus_get_setting", Constants.GET_SETTING_SERVICE_METHOD_NAME),
        ("_dbus_control", Constants.CONTROL_SERVICE_METHOD_NAME),
        ("_dbus_alarm_acknowledge", Constants.ALARM_ACKNOWLEDGE_SERVICE_METHOD_NAME),
        ("_dbus_alarm_list", Constants.ALARM_LIST_SERVICE_METHOD_NAME),
        ("_dbus_single_snapshot", Constants.SINGLE_SNAPSHOT_SERVICE_METHOD_NAME),
        ("_dbus_put_file", Constants.PUT_FILE_SERVICE_METHOD_NAME),
        ("_dbus_operation", Constants.OPERATION_SERVICE_METHOD_NAME),
    ]

    def __init__(
        self,
        status_callback=None,
        event_handler=None,
        snapshot_handler=None,
        control_max_attempts=3,
    ):

        self.status_callback = status_callback
        self.event_handler = event_handler
        self.control_max_attempts = control_max_attempts
        self.lock = threading.Lock()
        self.snapshot_handler = snapshot_handler

    def connect(self):
        """
        Attempt to connect to DBus, retrying on failure until successful.

        This should be called on startup to ensure the proxy is ready.

        Returns:
            None
        """
        while True:
            try:
                self._connect_dbus()
                if self.status_callback:
                    self.status_callback(
                        DBUSConnectionStatus(
                            connection_state=ConnectionStatus.CONNECTED,
                            reason="",
                            timestamp=TimeUtil.current_time(),
                        )
                    )
                break
            except Exception as e:
                self._logger.error(f"DBus initial connect failed: {e}")
                if self.status_callback:
                    self.status_callback(
                        DBUSConnectionStatus(
                            connection_state=ConnectionStatus.DISCONNECTED,
                            reason=str(e),
                            timestamp=TimeUtil.current_time(),
                        )
                    )
                sleep(self._dbus_retry_delay)

    def _connect_dbus(self):
        """
        Establish a connection to the DBus (SessionBus on macOS, SystemBus on Linux).
        Registers signal handlers and DBus methods.

        Returns:
            None
        """
        # Mac uses SessionBus, Linux uses SystemBus
        if platform.system() == "Darwin":
            self.bus = dbus.SessionBus()
        else:
            self.bus = dbus.SystemBus()

        n2k_dbus_object = self.bus.get_object(
            Constants.N2K_SERVICE_NAME, Constants.N2K_OBJECT_PATH
        )
        self.n2k_dbus_interface = dbus.Interface(
            n2k_dbus_object, Constants.N2K_INTERFACE_NAME
        )
        self._register_signal_handlers()
        self._register_methods()

    def _register_signal_handlers(self):
        """
        Register signal handlers for DBus events and snapshots.

        Returns:
            None
        """
        self.bus.add_signal_receiver(
            self.event_handler,
            dbus_interface=Constants.N2K_INTERFACE_NAME,
            signal_name=Constants.EVENT_SIGNAL_NAME,
            path=Constants.N2K_OBJECT_PATH,
        )
        self.bus.add_signal_receiver(
            self.snapshot_handler,
            dbus_interface=Constants.N2K_INTERFACE_NAME,
            signal_name=Constants.SNAPSHOT_SIGNAL_NAME,
            path=Constants.N2K_OBJECT_PATH,
        )

    def _register_methods(self):
        """
        Initialize N2k dbus Service Methods.
        Map DBus service methods to instance attributes for easy access.

        Returns:
            None
        """
        for attr, method in self.DBUS_METHOD_MAP:
            setattr(self, attr, self.n2k_dbus_interface.get_dbus_method(method))

    def _report_status(self, connected: bool, reason: str = ""):
        """
        Helper to report connection status via callback.

        Args:
            connected (bool): True if connected, False if disconnected.
            reason (str): Optional reason for status change.

        Returns:
            None
        """
        if self.status_callback:
            self.status_callback(
                DBUSConnectionStatus(
                    connection_state=(
                        ConnectionStatus.CONNECTED
                        if connected
                        else ConnectionStatus.DISCONNECTED
                    ),
                    reason=reason,
                    timestamp=TimeUtil.current_time(),
                )
            )

    def _call_with_retry(
        self, method_name: str, *args, max_attempts: int = None, **kwargs
    ) -> object:
        """
        Call a DBus method with retry logic and status reporting.

        Args:
            method_name (str): The name of the DBus method attribute to call.
            *args: Positional arguments to pass to the DBus method.
            max_attempts (int, optional): Maximum number of retry attempts. If None, retry indefinitely.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.

        Raises:
            dbus.exceptions.DBusException: If the call fails after max_attempts.
        """
        attempt = 0
        while True:
            with self.lock:
                method = getattr(self, method_name)
                try:
                    result = method(*args, **kwargs)
                    self._report_status(True)
                    return result
                except dbus.exceptions.DBusException as e:
                    attempt += 1
                    self._logger.warning(f"DBus call failed (attempt {attempt}): {e}")
                    self._report_status(False, str(e))
                    if max_attempts and attempt >= max_attempts:
                        self._logger.error(
                            f"DBus call failed after {attempt} attempts. Giving up."
                        )
                        raise
            sleep(self._dbus_retry_delay)
            while True:
                try:
                    self._connect_dbus()
                    break
                except Exception as conn_exc:
                    self._logger.error(f"DBus reconnect failed: {conn_exc}")
                    sleep(self._dbus_retry_delay)

    def get_config(self, *args, **kwargs) -> object:
        """
        Get N2K configuration via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_get_config", *args, **kwargs)

    def get_config_all(self, *args, **kwargs) -> object:
        """
        Get all N2K configurations via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_get_config_all", *args, **kwargs)

    def get_categories(self, *args, **kwargs) -> object:
        """
        Get N2K categories via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_get_categories", *args, **kwargs)

    def get_setting(self, *args, **kwargs) -> object:
        """
        Get N2K setting via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_get_setting", *args, **kwargs)

    def control(self, *args, **kwargs) -> object:
        """
        Send control command via DBus with retry.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry(
            "_dbus_control", *args, max_attempts=self.control_max_attempts, **kwargs
        )

    def alarm_acknowledge(self, *args, **kwargs) -> object:
        """
        Acknowledge alarm via DBus with retry.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry(
            "_dbus_alarm_acknowledge",
            *args,
            max_attempts=self.control_max_attempts,
            **kwargs,
        )

    def alarm_list(self, *args, **kwargs) -> object:
        """
        Get alarm list via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_alarm_list", *args, **kwargs)

    def single_snapshot(self, *args, **kwargs) -> object:
        """
        Get single snapshot via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_single_snapshot", *args, **kwargs)

    def put_file(self, *args, **kwargs) -> object:
        """
        Send a file to the host via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_put_file", *args, **kwargs)

    def operation(self, *args, **kwargs) -> object:
        """
        Perform an operation on the host via DBus.

        Args:
            *args: Arguments to pass to the DBus method.
            **kwargs: Keyword arguments to pass to the DBus method.

        Returns:
            object: The result of the DBus method call.
        """
        return self._call_with_retry("_dbus_operation", *args, **kwargs)
