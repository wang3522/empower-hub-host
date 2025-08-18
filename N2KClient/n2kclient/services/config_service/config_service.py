import json
from ...models.n2k_configuration.n2k_configuation import (
    N2kConfiguration,
)
from ...models.n2k_configuration.engine_configuration import EngineConfiguration
from .config_parser.config_parser import ConfigParser
from .config_processor.config_processor import ConfigProcessor
from ..dbus_proxy_service.dbus_proxy import DbusProxyService
from ...models.constants import Constants, JsonKeys
from ...models.devices import N2kDevices
from ...models.common_enums import ConfigOperationType
from ...models.empower_system.empower_system import EmpowerSystem
import logging
from typing import Callable


from time import sleep

from ...models.devices import N2kDevices
from ...util.common_utils import send_and_validate_response
import threading

WRITE_CONFIG_SLEEP_TIME = 1


class ConfigService:
    """
    Service for managing N2K configuration operations.
    This service handles reading and writing configurations.
    Attributes:
        dbus_proxy: DbusProxyService instance for DBus operations.
        config_parser: ConfigParser instance for parsing config.
        config_processor: ConfigProcessor instance for processing config.
        lock: threading.Lock for thread safety.
        get_latest_devices: Function to get the latest N2kDevices.
        set_devices: Function to update devices (calls on_next on subject).
        set_config: Function to update config (calls on_next on subject).
        set_empower_system: Function to update EmpowerSystem (calls on_next on subject).
        dispose_empower_system: Function to dispose EmpowerSystem instance.
        get_engine_config: Function to get the latest EngineConfiguration.
        get_engine_list: Function to get the latest engine list.
        set_engine_config: Function to update EngineConfiguration.
        set_engine_list: Function to update engine list.
        set_factory_metadata: Function to update factory metadata.
        request_state_snapshot: Function to trigger a state update/snapshot.
    Methods:
        write_configuration: Writes the configuration to the host.
        scan_factory_metadata: Scans and updates factory metadata.
        get_configuration: Retrieves the current configuration from the host.
        scan_marine_engine_config: Scans the marine configuration and updates the engine configuration.
        _scan_config_metadata: Scans and retrieves configuration metadata.
    """

    _logger = logging.getLogger(Constants.N2K_CONFIG_SERVICE)

    def __init__(
        self,
        dbus_proxy: DbusProxyService,
        lock: threading.Lock,
        # --- Device state accessors ---
        get_latest_devices: Callable[[], N2kDevices],
        set_devices: Callable[[N2kDevices], None] = None,
        set_config: Callable[[N2kConfiguration], None] = None,
        set_empower_system: Callable[[EmpowerSystem], None] = None,
        dispose_empower_system: Callable[[], None] = None,
        # --- Engine state accessors ---
        get_engine_config: Callable[[], EngineConfiguration] = None,
        get_engine_list: Callable[[], N2kDevices] = None,
        set_engine_config: Callable[[EngineConfiguration], None] = None,
        set_engine_list: Callable[[N2kDevices], None] = None,
        # --- Factory metadata accessors ---
        set_factory_metadata: Callable[[dict], None] = None,
        # --- State update trigger ---
        request_state_snapshot: Callable[[], None] = None,
    ):
        """
        ConfigService constructor.

        Args:
            dbus_proxy: DbusProxyService instance for DBus operations.
            config_parser: ConfigParser instance for parsing config.
            config_processor: ConfigProcessor instance for processing config.
            lock: threading.Lock for thread safety.
            get_latest_devices: Function to get the latest N2kDevices.
            set_devices: Function to update devices (calls on_next on subject).
            set_config: Function to update config (calls on_next on subject).
            set_empower_system: Function to update EmpowerSystem (calls on_next on subject).
            dispose_empower_system: Function to dispose EmpowerSystem instance.
            get_engine_config: Function to get the latest EngineConfiguration.
            get_engine_list: Function to get the latest engine list.
            set_engine_config: Function to update EngineConfiguration.
            set_engine_list: Function to update engine list.
            set_factory_metadata: Function to update factory metadata.
            request_state_snapshot: Function to trigger a state update/snapshot.
        """
        # Core dependencies
        self._dbus_proxy = dbus_proxy
        self._config_parser = ConfigParser()
        self._config_processor = ConfigProcessor()
        self._lock = lock

        # Device state accessors
        self._get_latest_devices = get_latest_devices
        self._set_devices = set_devices
        self._set_config = set_config
        self._set_empower_system = set_empower_system
        self._dispose_empower_system = dispose_empower_system

        # Engine state accessors
        self._get_engine_config = get_engine_config
        self._get_engine_list = get_engine_list
        self._set_engine_config = set_engine_config
        self._set_engine_list = set_engine_list

        # Factory metadata accessors
        self._set_factory_metadata = set_factory_metadata
        # State update trigger
        self._request_state_snapshot = request_state_snapshot

    ######################################
    # Write Configuration
    ######################################

    def write_configuration(self, config_hex: str) -> None:
        """
        Write the configuration to the host.

        Args:
            config_hex: Configuration data encoded as hex.
        """
        self._logger.debug("Writing configuration to host")
        if not send_and_validate_response(
            self._dbus_proxy.put_file,
            {JsonKeys.CONTENT: config_hex},
            logger=self._logger,
        ):
            return False

        sleep(WRITE_CONFIG_SLEEP_TIME)

        return send_and_validate_response(
            self._dbus_proxy.operation,
            {
                JsonKeys.type: ConfigOperationType.WriteConfig.value,
            },
            logger=self._logger,
        )

    def scan_factory_metadata(self):
        """
        Scans and updates factory metadata.
        This method retrieves the factory metadata from the DBus proxy and updates the factory metadata in the service.
        It uses the ConfigParser to parse the metadata JSON and sets it using the set_factory_metadata
        """
        try:
            self._logger.info("Loading factory metadata...")
            factory_metadata_response = self._dbus_proxy.get_setting(
                Constants.FactoryData
            )
            factory_metadata_json = json.loads(factory_metadata_response)
            factory_metadata = self._config_parser.parse_factory_metadata(
                factory_metadata_json
            )
            self._set_factory_metadata(factory_metadata)
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Factory Metadata response: {e}")

    def get_configuration(self):
        """
        Retrieves the current configuration from the host.
        This method fetches the configuration from the DBus proxy, parses it using the ConfigParser,
        and updates the N2kConfiguration and EmpowerSystem in the service.
        It also disposes of the current nonengine devices and requests a state snapshot.
        """
        # Raw Czone Config
        try:
            with self._lock:
                latest_devices = self._get_latest_devices()
                latest_devices.dispose_devices(is_engine=False)
                self._set_devices(latest_devices)
            categories_json = self._dbus_proxy.get_categories()
            config_json = self._dbus_proxy.get_config_all()
            config_metadata_json = self._dbus_proxy.get_setting(Constants.Config)
            raw_config = self._config_parser.parse_config(
                config_json, categories_json, config_metadata_json
            )
            self._set_config(raw_config)

            # Empower System
            self._dispose_empower_system()
            processed_config = self._config_processor.build_empower_system(
                raw_config, latest_devices
            )
            self._set_empower_system(processed_config)
            self._request_state_snapshot()
        except Exception as e:
            self._logger.error(
                f"Error reading dbus Get Config response: {e}", exc_info=True
            )

    def scan_marine_engine_config(self, should_reset: bool = False) -> bool:
        """
        Scans the marine configuration and updates the engine configuration.

        This method retrieves the engine configuration from the data provider
        and updates the engine configuration in the `EngineConfiguration` object.

        Returns:
            None
        """
        engine_configuration = self._get_engine_config()

        self._logger.info(
            "Loading Engine configuration with should_reset = %r...", should_reset
        )

        # Engine Config
        try:
            latest_devices = self._get_latest_devices()
            if should_reset:
                with self._lock:
                    latest_devices.dispose_devices(True)
                    self._set_devices(latest_devices)
                latest_engine_list = self._get_engine_list()
                if latest_engine_list is not None:
                    latest_engine_list.dispose()
            engine_config_json = self._dbus_proxy.get_config(JsonKeys.ENGINES)
            raw_engine_config = self._config_parser.parse_engine_configuration(
                engine_config_json, engine_configuration
            )

            raw_engine_config.should_reset = should_reset

            self._set_engine_config(raw_engine_config)

            # Engine List
            engine_list = self._config_processor.build_engine_list(
                raw_engine_config, latest_devices
            )
            self._set_engine_list(engine_list)
            self._request_state_snapshot()
            return True
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Engine response: {e}")
            return False

    def _scan_config_metadata(self):
        """
        Scans and retrieves configuration metadata.
        This method fetches the configuration metadata from the DBus proxy and returns it.
        Returns:
            dict: Configuration metadata dictionary.
        """
        try:
            self._logger.info("Loading config metadata...")
            config_metadata = self._dbus_proxy.get_setting(Constants.Config)
            return config_metadata
        except Exception as e:
            self._logger.error(f"Error reading dbus Get Config Metadata response: {e}")
            return {}
