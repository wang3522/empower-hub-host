# N2KClient/n2kclient/dbus_proxy.py

import logging
import threading
import dbus
from time import sleep
from ...models.constants import Constants
from ...models.dbus_connection_status import DBUSConnectionStatus
from ...util.time_util import TimeUtil
import platform
from ...models.common_enums import ConnectionStatus


class DbusProxyService:
    _logger = logging.getLogger("DBUS Proxy Helper")

    def __init__(
        self,
        status_callback=None,
        event_handler=None,
        snapshot_handler=None,
        retry_delay=5,
        control_max_attempts=3,
    ):

        self.status_callback = status_callback
        self.event_handler = event_handler
        self.snapshot_handler = snapshot_handler
        self.retry_delay = retry_delay
        self.control_max_attempts = control_max_attempts
        self.lock = threading.Lock()

    def connect(self):
        """
        Attempt to connect to DBus, retrying on failure until successful.
        This should be called on startup to ensure the proxy is ready.
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
                sleep(self.retry_delay)

    def _connect_dbus(self):
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
        # Initialize N2k dbus Service Methods
        self._dbus_get_config = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_SERVICE_METHOD_NAME
        )
        self._dbus_get_config_all = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CONFIG_ALL_SERVICE_METHOD_NAME
        )
        self._dbus_get_categories = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_CATEGORIES_SERVICE_METHOD_NAME
        )
        self._dbus_get_setting = self.n2k_dbus_interface.get_dbus_method(
            Constants.GET_SETTING_SERVICE_METHOD_NAME
        )
        self._dbus_control = self.n2k_dbus_interface.get_dbus_method(
            Constants.CONTROL_SERVICE_METHOD_NAME
        )
        self._dbus_alarm_acknowledge = self.n2k_dbus_interface.get_dbus_method(
            Constants.ALARM_ACKNOWLEDGE_SERVICE_METHOD_NAME
        )
        self._dbus_alarm_list = self.n2k_dbus_interface.get_dbus_method(
            Constants.ALARM_LIST_SERVICE_METHOD_NAME
        )
        self._dbus_single_snapshot = self.n2k_dbus_interface.get_dbus_method(
            Constants.SINGLE_SNAPSHOT_SERVICE_METHOD_NAME
        )

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

    def _retry_call(self, method_name, *args, max_attempts=None, **kwargs):
        attempt = 0
        while True:
            with self.lock:
                # Always get the latest proxy method by name
                method = getattr(self, method_name)
                try:
                    result = method(*args, **kwargs)
                    if self.status_callback:
                        self.status_callback(
                            DBUSConnectionStatus(
                                connection_state=ConnectionStatus.CONNECTED,
                                reason="",
                                timestamp=TimeUtil.current_time(),
                            )
                        )
                    return result
                except dbus.exceptions.DBusException as e:
                    attempt += 1
                    self._logger.warning(f"DBus call failed (attempt {attempt}): {e}")
                    if self.status_callback:
                        self.status_callback(
                            DBUSConnectionStatus(
                                connection_state=ConnectionStatus.DISCONNECTED,
                                reason=str(e),
                                timestamp=TimeUtil.current_time(),
                            )
                        )
                    if max_attempts and attempt >= max_attempts:
                        self._logger.error(
                            f"DBus call failed after {attempt} attempts. Giving up."
                        )
                        raise
            sleep(self.retry_delay)
            while True:
                try:
                    self._connect_dbus()
                    break
                except Exception as conn_exc:
                    self._logger.error(f"DBus reconnect failed: {conn_exc}")
                    sleep(self.retry_delay)

    def get_config(self, *args, **kwargs):
        return self._retry_call("_dbus_get_config", *args, **kwargs)

    def get_config_all(self, *args, **kwargs):
        return self._retry_call("_dbus_get_config_all", *args, **kwargs)

    def get_categories(self, *args, **kwargs):
        return self._retry_call("_dbus_get_categories", *args, **kwargs)

    def get_setting(self, *args, **kwargs):
        return self._retry_call("_dbus_get_setting", *args, **kwargs)

    def control(self, *args, **kwargs):
        return self._retry_call(
            "_dbus_control", *args, max_attempts=self.control_max_attempts, **kwargs
        )

    def alarm_acknowledge(self, *args, **kwargs):
        return self._retry_call(
            "_dbus_alarm_acknowledge",
            *args,
            max_attempts=self.control_max_attempts,
            **kwargs,
        )

    def alarm_list(self, *args, **kwargs):
        return self._retry_call("_dbus_alarm_list", *args, **kwargs)

    def single_snapshot(self, *args, **kwargs):
        return self._retry_call("_dbus_single_snapshot", *args, **kwargs)
