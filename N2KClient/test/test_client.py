import unittest

from N2KClient.n2kclient.models.empower_system.engine_list import EngineList

from N2KClient.n2kclient.models.n2k_configuration.factory_metadata import (
    FactoryMetadata,
)

from N2KClient.n2kclient.models.n2k_configuration.engine_configuration import (
    EngineConfiguration,
)

from N2KClient.n2kclient.models.n2k_configuration.instance import Instance

from N2KClient.n2kclient.models.empower_system.engine_alarm import EngineAlarm
from N2KClient.n2kclient.models.empower_system.engine_alarm_list import EngineAlarmList

from N2KClient.n2kclient.services.alarm_service.alarm_service import AlarmService
from N2KClient.n2kclient.services.config_service.config_service import ConfigService
from N2KClient.n2kclient.services.control_service.control_service import ControlService
from N2KClient.n2kclient.services.event_service.event_service import EventService
from N2KClient.n2kclient.services.snapshot_service.snapshot_service import (
    SnapshotService,
)
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineDevice
from N2KClient.n2kclient.models.n2k_configuration.n2k_configuation import (
    N2kConfiguration,
)
from N2KClient.n2kclient.client import N2KClient
from N2KClient.n2kclient.services.dbus_proxy_service.dbus_proxy import DbusProxyService
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineType
from N2KClient.n2kclient.models.empower_system.alarm import AlarmState, AlarmSeverity
from N2KClient.n2kclient.models.empower_system.alarm_list import AlarmList
from N2KClient.n2kclient.models.empower_system.alarm import Alarm
from N2KClient.n2kclient.models.devices import N2kDevices, N2kDevice

from N2KClient.n2kclient.models.common_enums import N2kDeviceType
from N2KClient.n2kclient.models.n2k_configuration.config_metadata import ConfigMetadata
from N2KClient.n2kclient.models.empower_system.empower_system import EmpowerSystem
from N2KClient.n2kclient.models.empower_system.thing import Thing
from N2KClient.n2kclient.models.common_enums import ThingType
from N2KClient.n2kclient.models.dbus_connection_status import DBUSConnectionStatus
from N2KClient.n2kclient.models.common_enums import ConnectionStatus
from unittest.mock import patch
import reactivex as rx
from unittest.mock import MagicMock


class N2KClientTest(unittest.TestCase):
    """
    Unit tests for the N2KClient class.
    """

    def test_n2k_client_initialization(self):
        """
        Test the initialization of the N2KClient.
        """
        client = N2KClient()
        self.assertIsNotNone(client)

    def test_n2k_client_services_initialization(self):
        """
        Test the initialization of the N2KClient services. Ensure they are not None and of correct type
        """
        with patch(
            "N2KClient.n2kclient.client.N2KClient._setup_subscriptions"
        ) as mock_setup_subscriptions:
            client = N2KClient()
            self.assertIsNotNone(client._config_service)
            self.assertIsNotNone(client.control_service)
            self.assertIsNotNone(client._alarm_service)
            self.assertIsNotNone(client._snapshot_service)
            self.assertIsNotNone(client._event_service)
            self.assertIsNotNone(client._dbus_proxy)
            self.assertIsInstance(client._config_service, ConfigService)
            self.assertIsInstance(client.control_service, ControlService)
            self.assertIsInstance(client._alarm_service, AlarmService)
            self.assertIsInstance(client._snapshot_service, SnapshotService)
            self.assertIsInstance(client._event_service, EventService)
            self.assertIsInstance(client._dbus_proxy, DbusProxyService)
            self.assertIsNotNone(
                client._dbus_proxy.snapshot_handler, "snapshot_handler should be set"
            )
            self.assertIsNotNone(
                client._dbus_proxy.event_handler, "event_handler should be set"
            )

            mock_setup_subscriptions.assert_called_once()

    def test_run_mainloop(self):
        """
        Test the run_mainloop method of the N2KClient. Ensure all functions called
        """
        client = N2KClient()
        with patch.object(client._dbus_proxy, "connect") as mock_connect, patch.object(
            client._config_service, "scan_factory_metadata"
        ) as mock_scan_factory, patch.object(
            client._config_service, "get_configuration"
        ) as mock_get_config, patch.object(
            client._config_service, "scan_marine_engine_config"
        ) as mock_scan_engine:
            with patch("gi.repository.GLib.MainLoop") as mock_mainloop:
                client.run_mainloop()
                mock_connect.assert_called_once()
                mock_scan_factory.assert_called_once()
                mock_get_config.assert_called_once()
                mock_scan_engine.assert_called_once()
                mock_mainloop.return_value.run.assert_called_once()

    def test_setup_subscriptions(self):
        """
        Test the setup_subscriptions method of the N2KClient.
        """
        client = N2KClient()
        expected_subscriptions = len(client._disposable_list)
        client._setup_subscriptions()
        expected_subscriptions += (
            9  # for the new subscriptions, adjust if more subs are added
        )
        self.assertEqual(len(client._disposable_list), expected_subscriptions)
        for disposable in client._disposable_list:
            self.assertTrue(hasattr(disposable, "dispose"))

    def test_update_latest_engine_alarms(self):
        """
        Test the update_latest_engine_alarms method of the N2KClient.
        """

        # Arrange: Set up client and mock alarm/device
        client = N2KClient()
        mock_engine_alarm_list = EngineAlarmList()
        mock_engine_device = EngineDevice()
        instance = Instance()
        instance.enabled = True
        instance.instance = 1

        mock_engine_device.instance = instance
        mock_engine_device.calibration_id = "calibration_id"
        mock_engine_device.ecu_serial_number = "ecu_serial_number"
        mock_engine_device.engine_type = EngineType.NMEA2000
        mock_engine_device.id = 1
        mock_engine_device.serial_number = "serial_number"
        mock_engine_device.software_id = "software_id"
        mock_engine_device.name_utf8 = "Test Engine"

        mock_alarm = EngineAlarm(
            date_active=1,
            alarm_text="test_alarm",
            engine=mock_engine_device,
            current_discrete_status1=1,
            current_discrete_status2=2,
            prev_discrete_status1=3,
            prev_discrete_status2=4,
            alarm_id="test_id",
        )
        mock_engine_alarm_list.engine_alarms["alarm1"] = mock_alarm

        # Act: Update latest engine alarms
        client._update_latest_engine_alarms(mock_engine_alarm_list)

        # Assert:
        self.assertEqual(client._latest_engine_alarms, mock_engine_alarm_list)

    def test_update_latest_alarms(self):
        """
        Test the update_latest_alarms method of the N2KClient.
        """

        # Arrange: Set up client and mock alarm/device
        client = N2KClient()
        mock_alarm_list = AlarmList()
        mock_alarm = Alarm(
            state=AlarmState.ENABLED,
            date_active=1,
            things=["battery.1"],
            title="Test Alarm",
            name="Test Alarm",
            description="Test Alarm",
            unique_id=123,
            severity=AlarmSeverity.CRITICAL,
        )

        mock_alarm_list.alarm["alarm1"] = mock_alarm

        # Act: Update latest alarms
        client._update_latest_alarms(mock_alarm_list)

        # Assert
        self.assertEqual(client._latest_alarms, mock_alarm_list)

    def test_update_latest_devices(self):
        """
        Test the update_latest_devices method of the N2KClient.
        """

        # Arrange: Set up client and mock device
        client = N2KClient()
        mock_device_list = N2kDevices()
        mock_device = N2kDevice(N2kDeviceType.DC)
        mock_device_list.add("device1", mock_device)

        mock_device_list.devices["device1"] = mock_device

        # Act: Update latest devices
        client._update_latest_devices(mock_device_list)

        # Assert: Check all expected fields
        device = client._latest_devices.devices["device1"]
        self.assertIn("device1", client._latest_devices.devices)
        self.assertEqual(device.type, N2kDeviceType.DC)

    def test_update_latest_config(self):
        """
        Test the update_latest_config method of the N2KClient.
        """

        # Arrange: set up client and mock config
        client = N2KClient()
        mock_config = N2kConfiguration()
        mock_config.metadata = ConfigMetadata()
        mock_config.metadata.version = "1.0"
        mock_config.metadata.name = "Test Config"
        mock_config.metadata.config_file_version = "Test Config Description"

        # Act
        client._update_latest_config(mock_config)

        # Assert
        self.assertEqual(client._latest_config, mock_config)

    def test_update_latest_empower_system(self):
        """
        Test the update latest empower system method of the N2KClient.
        """

        # Arrange: set up client and mock empower_system
        client = N2KClient()
        mock_empower_system = EmpowerSystem(config_metadata=None)
        thing = Thing(
            type=ThingType.BATTERY,
            id="battery1",
            name="Test Batt",
            categories=[],
            links=[],
        )
        mock_empower_system.add_thing(thing)

        # Act
        client._update_latest_empower_system(mock_empower_system)

        # Assert
        self.assertEqual(client._latest_empower_system, mock_empower_system)

    def test_update_latest_engine_config(self):
        """
        Test the update_latest_engine_config method of the N2KClient.
        """

        # Arrange: set up client and mock engine config
        client = N2KClient()
        mock_engine_config = EngineConfiguration()
        mock_engine_config.devices["device1"] = EngineDevice()
        mock_engine_config.devices["device1"].id = 1
        mock_engine_config.devices["device1"].name_utf8 = "Engine Device 1"
        mock_engine_config.devices["device1"].instance = Instance()
        mock_engine_config.devices["device1"].instance.instance = 1
        mock_engine_config.devices["device1"].instance.enabled = True
        mock_engine_config.devices["device1"].software_id = "v1.0"
        mock_engine_config.devices["device1"].calibration_id = "cal_123"
        mock_engine_config.devices["device1"].serial_number = "SN123456"
        mock_engine_config.devices["device1"].engine_type = EngineType.NMEA2000
        mock_engine_config.devices["device1"].ecu_serial_number = "v1.0.0"
        # Act
        client._update_latest_engine_config(mock_engine_config)

        # Assert
        self.assertEqual(client._latest_engine_config, mock_engine_config)

    def test_update_latest_engine_list(self):
        """
        Test the update_latest_engine_list method of the N2KClient.
        """
        client = N2KClient()
        mock_engine_list = EngineList(should_reset=False)
        client._latest_engine_list = mock_engine_list

        client._update_latest_engine_list(mock_engine_list)
        self.assertEqual(client._latest_engine_list, mock_engine_list)

    def test_update_latest_factory_metadata(self):
        """
        Test the update_latest_factory_metadata
        """

        # Arrange: set up client and mock engine config
        client = N2KClient()
        mock_factory_metadata = FactoryMetadata()
        mock_factory_metadata.mender_artifact_info = "test_mender_artifact_info"
        mock_factory_metadata.rt_firmware_version = "test_rt_firmware_version"
        mock_factory_metadata.serial_number = "test_serial_number"

        # Act
        client._update_latest_factory_metadata(mock_factory_metadata)

        # Assert
        self.assertEqual(client._latest_factory_metadata, mock_factory_metadata)

    def test_handle_dbus_connection_status_updated_disconnected(self):
        """
        Test the handle_dbus_connection_status_updated method of the N2KClient.
        """
        client = N2KClient()
        with patch.object(
            client._config_service, "scan_marine_engine_config"
        ) as mock_scan_marine_engine_config, patch.object(
            client._alarm_service, "load_active_alarms"
        ) as mock_load_active_alarms:
            mock_status = DBUSConnectionStatus(
                connection_state=ConnectionStatus.DISCONNECTED,
                reason="Test Reason",
                timestamp=1234567890,
            )
            # Act
            client._handle_dbus_connection_status_updated(mock_status)

            # Assert
            self.assertTrue(
                client.previous_n2k_dbus_connection_status.connection_state
                == ConnectionStatus.DISCONNECTED
            )
            mock_scan_marine_engine_config.assert_not_called()
            mock_load_active_alarms.assert_not_called()

    def test_handle_dbus_connection_status_updated_connected(self):
        """
        Test the handle_dbus_connection_status_updated method of the N2KClient.
        """
        client = N2KClient()
        with patch.object(
            client._config_service, "scan_marine_engine_config"
        ) as mock_scan_marine_engine_config, patch.object(
            client._alarm_service, "load_active_alarms"
        ) as mock_load_active_alarms:
            mock_status = DBUSConnectionStatus(
                connection_state=ConnectionStatus.CONNECTED,
                reason="Test Reason",
                timestamp=1234567890,
            )
            # Set previous state to DISCONNECTED to trigger the logic
            client.previous_n2k_dbus_connection_status.connection_state = (
                ConnectionStatus.DISCONNECTED
            )

            # Act
            client._handle_dbus_connection_status_updated(mock_status)

            # Assert
            self.assertTrue(
                client.previous_n2k_dbus_connection_status.connection_state
                == ConnectionStatus.CONNECTED
            )
            mock_scan_marine_engine_config.assert_called_once()
            mock_load_active_alarms.assert_called_once()

    def test_write_configuration(self):
        """
        Test the write_configuration public api method of the N2KClient.
        """

        client = N2KClient()
        with patch.object(
            client._config_service, "write_configuration"
        ) as mock_write_configuration:
            # Act
            client.write_configuration("test")

            # Assert
            mock_write_configuration.assert_called_once_with("test")

    def test_request_state_snapshot(self):
        """
        Test the request_state_snapshot public api method of the N2KClient.
        """

        client = N2KClient()
        with patch.object(
            client._snapshot_service, "_single_snapshot"
        ) as mock_single_snapshot:
            # Act
            client.request_state_snapshot()

            # Assert
            mock_single_snapshot.assert_called_once()

    def test_acknowledge_alarm(self):
        """
        Test the acknowledge_alarm public api method of N2KClient
        """

        client = N2KClient()
        with patch.object(
            client._alarm_service, "acknowledge_alarm"
        ) as mock_acknowledge_alarm:
            # Act
            client.acknowledge_alarm(1)

            # Assert
            mock_acknowledge_alarm.assert_called_once_with(1)

    def test_refresh_active_alarms(self):
        """
        Test the refresh_active_alarms public api method of N2KClient
        """

        client = N2KClient()
        with patch.object(
            client._alarm_service, "load_active_alarms", return_value=(True, "")
        ) as mock_load_active_alarms:
            # Act
            client.refresh_active_alarms()

            # Assert
            mock_load_active_alarms.assert_called_once()

    def test_refresh_active_alarms_false(self):
        """
        Test the refresh_active_alarms public api method of N2KClient. Returns false on fail
        """

        client = N2KClient()
        with patch.object(
            client._alarm_service,
            "load_active_alarms",
            return_value=(False, "TESTERROR"),
        ) as mock_load_active_alarms:
            # Act
            res = client.refresh_active_alarms()

            # Assert
            mock_load_active_alarms.assert_called_once()
            self.assertFalse(res[0])
            self.assertEqual(res[1], "TESTERROR")

    def test_scan_marine_engines_reset(self):
        """
        Test the scan_marine_engines public api method of N2KClient
        Default should reset engines
        """

        client = N2KClient()
        with patch.object(
            client._config_service, "scan_marine_engine_config"
        ) as mock_scan_marine_engine_config:
            # Act
            client.scan_marine_engines()

            # Assert
            mock_scan_marine_engine_config.assert_called_once_with(should_reset=True)

    def test_scan_marine_engines_no_reset(self):
        """
        Test the scan_marine_engines public api method for N2kClient.
        It should not reset engines if sent with False
        """

        client = N2KClient()
        with patch.object(
            client._config_service, "scan_marine_engine_config"
        ) as mock_scan_marine_engine_config:
            # Act
            client.scan_marine_engines(False)

            # Assert
            mock_scan_marine_engine_config.assert_called_once_with(should_reset=False)

    def test_set_circuit_power_state_true(self):
        """
        Test the set_circuit_power_state public api method of N2KClient.
        """

        client = N2KClient()
        with patch.object(
            client.control_service, "set_circuit_power_state"
        ) as mock_set_circuit_power_state:
            # Act
            client.set_circuit_power_state(1, True)

            # Assert
            mock_set_circuit_power_state.assert_called_once_with(
                runtime_id=1, target_on=True
            )

    def test_set_circuit_power_state_exception(self):
        """
        Test the set_circuit_power_state public api method of N2KClient.
        """

        client = N2KClient()
        with patch.object(
            client.control_service, "set_circuit_power_state"
        ) as mock_set_circuit_power_state:
            # Act
            mock_set_circuit_power_state.side_effect = Exception("fail")
            res = client.set_circuit_power_state(1, True)

            # Assert
            mock_set_circuit_power_state.assert_called_once_with(
                runtime_id=1, target_on=True
            )
            self.assertFalse(res)

    def test_update_latest_alarms_none(self):
        """
        Edge case: update_latest_alarms with None input (should not update)
        """
        client = N2KClient()
        original = client._latest_alarms
        client._update_latest_alarms(None)
        self.assertIs(client._latest_alarms, original)

    def test_update_latest_devices_none(self):
        """
        Edge case: update_latest_devices with None input (should not update)
        """
        client = N2KClient()
        original = client._latest_devices
        client._update_latest_devices(None)
        self.assertIs(client._latest_devices, original)

    def test_update_latest_devices_empty(self):
        """
        Edge case: update_latest_devices with empty N2kDevices
        """
        client = N2KClient()
        empty_devices = N2kDevices()
        client._update_latest_devices(empty_devices)
        self.assertEqual(len(client._latest_devices.devices), 0)

    def test_update_latest_engine_alarms_none(self):
        """
        Edge case: update_latest_engine_alarms with None input (should not update)
        """
        client = N2KClient()
        original = client._latest_engine_alarms
        client._update_latest_engine_alarms(None)
        self.assertIs(client._latest_engine_alarms, original)

    def test_update_latest_engine_alarms_empty(self):
        """
        Edge case: update_latest_engine_alarms with empty EngineAlarmList
        """
        client = N2KClient()
        empty_alarms = EngineAlarmList()
        client._update_latest_engine_alarms(empty_alarms)
        self.assertEqual(len(client._latest_engine_alarms.engine_alarms), 0)

    def test_update_latest_config_none(self):
        """
        Edge case: update_latest_config with None input (should not update)
        """
        client = N2KClient()
        original = client._latest_config
        client._update_latest_config(None)
        self.assertIs(client._latest_config, original)

    def test_update_latest_config_empty_metadata(self):
        """
        Edge case: update_latest_config with missing metadata
        """
        client = N2KClient()
        config = N2kConfiguration()
        config.metadata = None
        client._update_latest_config(config)
        self.assertIsNone(client._latest_config.metadata)

    def test_update_latest_empower_system_none(self):
        """
        Edge case: update_latest_empower_system with None input (should not update)
        """
        client = N2KClient()
        original = client._latest_empower_system
        client._update_latest_empower_system(None)
        self.assertIs(client._latest_empower_system, original)

    def test_update_latest_engine_config_none(self):
        """
        Edge case: update_latest_engine_config with None input (should not update)
        """
        client = N2KClient()
        original = client._latest_engine_config
        client._update_latest_engine_config(None)
        self.assertIs(client._latest_engine_config, original)

    def test_update_latest_factory_metadata_none(self):
        """
        Edge case: update_latest_factory_metadata with None input (should not update)
        Handles missing attribute gracefully.
        """
        client = N2KClient()
        # If attribute does not exist, method should not create it
        has_attr_before = hasattr(client, "_latest_factory_metadata")
        client._update_latest_factory_metadata(None)
        has_attr_after = hasattr(client, "_latest_factory_metadata")
        self.assertEqual(has_attr_before, has_attr_after)

    def test_duplicate_device_ids(self):
        """
        Edge case: duplicate device IDs in N2kDevices
        """
        client = N2KClient()
        devices = N2kDevices()
        device1 = N2kDevice(N2kDeviceType.DC)
        device2 = N2kDevice(N2kDeviceType.DC)
        devices.add("dup_id", device1)
        devices.add("dup_id", device2)
        client._update_latest_devices(devices)
        # Should only keep the last added device for the duplicate key
        self.assertEqual(client._latest_devices.devices["dup_id"], device2)

    def test_handle_dbus_connection_status_updated_invalid_state(self):
        """
        Edge case: handle_dbus_connection_status_updated with unknown state
        """
        client = N2KClient()

        class FakeStatus:
            connection_state = "UNKNOWN"
            reason = "Test"
            timestamp = 0

        # Should not raise, but not change previous state
        prev_state = client.previous_n2k_dbus_connection_status.connection_state
        client._handle_dbus_connection_status_updated(FakeStatus())
        self.assertEqual(
            client.previous_n2k_dbus_connection_status.connection_state, prev_state
        )

    def test_write_configuration_exception(self):
        """
        Edge case: write_configuration raises exception in service
        """
        client = N2KClient()
        with patch.object(
            client._config_service,
            "write_configuration",
            side_effect=Exception("fail"),
        ):
            with self.assertRaises(Exception):
                client.write_configuration("bad_config")

    def test_set_circuit_power_state_false(self):
        """
        Test the set_circuit_power_state public api method of N2KClient.
        """

        client = N2KClient()
        with patch.object(
            client.control_service, "set_circuit_power_state"
        ) as mock_set_circuit_power_state:
            # Act
            client.set_circuit_power_state(1, False)

            # Assert
            mock_set_circuit_power_state.assert_called_once_with(
                runtime_id=1, target_on=False
            )

    def test_set_circuit_level(self):
        """
        Test the set_circuit_level public api method of N2KClient.
        """

        client = N2KClient()
        with patch.object(
            client.control_service, "set_circuit_level"
        ) as mock_set_circuit_level:
            # Act
            client.set_circuit_level(1, 5)

            # Assert
            mock_set_circuit_level.assert_called_once_with(runtime_id=1, level=5)

    def test_set_circuit_level_exception(self):
        """
        Test the set_circuit_level public api method of N2KClient.
        """

        client = N2KClient()
        with patch.object(
            client.control_service, "set_circuit_level"
        ) as mock_set_circuit_level:
            mock_set_circuit_level.side_effect = Exception("fail")
            # Act
            res = client.set_circuit_level(1, 5)

            # Assert
            mock_set_circuit_level.assert_called_once_with(runtime_id=1, level=5)
            self.assertFalse(res)

    def test_get_latest_devices(self):
        """
        Test the get_latest_devices public api method of N2KClient.
        """
        client = N2KClient()
        mock_device_list = N2kDevices()
        mock_device = N2kDevice(N2kDeviceType.DC)
        mock_device_list.add("device1", mock_device)

        mock_device_list.devices["device1"] = mock_device
        client._latest_devices = mock_device_list

        latest_devices = client.get_latest_devices()
        # Assert the internal state or effect
        self.assertEqual(latest_devices, mock_device_list)

    def test_get_devices_observable(self):
        """
        Test the get_device_observable method of N2KClient.
        """
        client = N2KClient()
        mock_device_list = N2kDevices()
        mock_device = N2kDevice(N2kDeviceType.DC)
        mock_device_list.add("device1", mock_device)

        mock_device_list.devices["device1"] = mock_device
        devices_observable = rx.subject.BehaviorSubject(mock_device_list)

        client.devices = devices_observable
        res = client.get_devices_observable()
        # Assert the internal state or effect
        self.assertEqual(res, devices_observable)

    def test_get_latest_config(self):
        """
        Test the get_latest_config method of N2KClient.
        """
        client = N2KClient()
        mock_config = N2kConfiguration()
        client._latest_config = mock_config

        latest_config = client.get_latest_config()
        # Assert the internal state or effect
        self.assertEqual(latest_config, mock_config)

    def test_get_config_observable(self):
        """
        Test the get_config_observable method of N2KClient.
        """
        client = N2KClient()
        mock_config = N2kConfiguration()
        config_observable = rx.subject.BehaviorSubject(mock_config)

        client.config = config_observable
        res = client.get_config_observable()
        # Assert the internal state or effect
        self.assertEqual(res, config_observable)

    def test_get_latest_empower_system(self):
        """
        Test the get_latest_empower_system method of N2KClient.
        """
        client = N2KClient()
        mock_empower_system = EmpowerSystem(None)
        client._latest_empower_system = mock_empower_system

        latest_empower_system = client.get_latest_empower_system()
        # Assert the internal state or effect
        self.assertEqual(latest_empower_system, mock_empower_system)

    def test_get_empower_system_observable(self):
        """
        Test the get_empower_system_observable method of N2KClient.
        """
        client = N2KClient()
        mock_empower_system = EmpowerSystem(None)
        empower_system_observable = rx.subject.BehaviorSubject(mock_empower_system)

        client.empower_system = empower_system_observable
        res = client.get_empower_system_observable()
        # Assert the internal state or effect
        self.assertEqual(res, empower_system_observable)

    def test_get_factory_metadata(self):
        """
        Test the get_factory_metadata method of N2KClient.
        """
        client = N2KClient()
        mock_factory_metadata = FactoryMetadata()
        client._latest_factory_metadata = mock_factory_metadata

        latest_factory_metadata = client.get_factory_metadata()
        # Assert the internal state or effect
        self.assertEqual(latest_factory_metadata, mock_factory_metadata)

    def test_get_factory_metadata_observable(self):
        """
        Test the get_factory_metadata_observable method of N2KClient.
        """
        client = N2KClient()
        mock_factory_metadata = FactoryMetadata()
        factory_metadata_observable = rx.subject.BehaviorSubject(mock_factory_metadata)

        client.factory_metadata = factory_metadata_observable
        res = client.get_factory_metadata_observable()
        # Assert the internal state or effect
        self.assertEqual(res, factory_metadata_observable)

    def test_get_latest_engine_list(self):
        """
        Test the get_latest_engine_list method of N2KClient.
        """
        client = N2KClient()
        mock_engine_list = EngineList(should_reset=False)
        client._latest_engine_list = mock_engine_list

        latest_engine_list = client.get_latest_engine_list()
        # Assert the internal state or effect
        self.assertEqual(latest_engine_list, mock_engine_list)

    def test_get_engine_list_observable(self):
        """
        Test the get_engine_list_observable method of N2KClient.
        """
        client = N2KClient()
        mock_engine_list = EngineList(should_reset=False)
        engine_list_observable = rx.subject.BehaviorSubject(mock_engine_list)

        client.engine_list = engine_list_observable
        res = client.get_engine_list_observable()
        # Assert the internal state or effect
        self.assertEqual(res, engine_list_observable)

    def test_get_engine_alarms(self):
        """
        Test the get_engine_alarms method of N2KClient.
        """
        client = N2KClient()
        mock_engine_alarms = EngineAlarmList()
        client._latest_engine_alarms = mock_engine_alarms

        latest_engine_alarms = client.get_engine_alarms()
        # Assert the internal state or effect
        self.assertEqual(latest_engine_alarms, mock_engine_alarms)

    def test_get_engine_alarms_observable(self):
        """
        Test the get_engine_alarms_observable method of N2KClient.
        """
        client = N2KClient()
        mock_engine_alarms = EngineAlarmList()
        engine_alarms_observable = rx.subject.BehaviorSubject(mock_engine_alarms)

        client._engine_alarms = engine_alarms_observable
        res = client.get_engine_alarms_observable()
        # Assert the internal state or effect
        self.assertEqual(res, engine_alarms_observable)

    def test_get_latest_alarms(self):
        """
        Test the get_latest_alarms method of N2KClient.
        """
        client = N2KClient()
        mock_alarms = AlarmList()
        client._latest_alarms = mock_alarms

        latest_alarms = client.get_latest_alarms()
        # Assert the internal state or effect
        self.assertEqual(latest_alarms, mock_alarms)

    def test_get_alarms_observable(self):
        """
        Test the get_alarms_observable method of N2KClient.
        """
        client = N2KClient()
        mock_alarms = AlarmList()
        alarms_observable = rx.subject.BehaviorSubject(mock_alarms)

        client._active_alarms = alarms_observable
        res = client.get_alarms_observable()
        # Assert the internal state or effect
        self.assertEqual(res, alarms_observable)

    def test_get_latest_engine_config(self):
        """
        Test the get_latest_engine_config method of N2KClient.
        """
        client = N2KClient()
        mock_engine_config = EngineConfiguration()
        client._latest_engine_config = mock_engine_config

        latest_engine_config = client.get_latest_engine_config()
        # Assert the internal state or effect
        self.assertEqual(latest_engine_config, mock_engine_config)

    def test_set_devices(self):
        """
        Test the set_devices method of N2KClient.
        """
        client = N2KClient()
        mock_devices = N2kDevices()
        client.set_devices(mock_devices)

        # Assert the internal state or effect
        self.assertEqual(client._latest_devices, mock_devices)

    def test_set_config(self):
        """
        Test the set_config method of N2KClient.
        """
        client = N2KClient()
        mock_config = N2kConfiguration()
        client.set_config(mock_config)

        # Assert the internal state or effect
        self.assertEqual(client._latest_config, mock_config)

    def test_set_empower_system(self):
        """
        Test the set_empower_system method of N2KClient.
        """
        client = N2KClient()
        mock_empower_system = EmpowerSystem(config_metadata=None)
        client.set_empower_system(mock_empower_system)

        # Assert the internal state or effect
        self.assertEqual(client._latest_empower_system, mock_empower_system)

    def test_set_engine_list(self):
        """
        Test the set_engine_list method of N2KClient.
        """
        client = N2KClient()
        mock_engine_list = EngineList(should_reset=False)
        client.set_engine_list(mock_engine_list)

        # Assert the internal state or effect
        self.assertEqual(client._latest_engine_list, mock_engine_list)

    def test_set_engine_config(self):
        """
        Test the set_engine_config method of N2KClient.
        """
        client = N2KClient()
        mock_engine_config = EngineConfiguration()
        client.set_engine_config(mock_engine_config)

        # Assert the internal state or effect
        self.assertEqual(client._latest_engine_config, mock_engine_config)

    def test_set_factory_metadata(self):
        """
        Test the set_factory_metadata method of N2KClient.
        """
        client = N2KClient()
        mock_factory_metadata = FactoryMetadata()
        client.set_factory_metadata(mock_factory_metadata)

        # Assert the internal state or effect
        self.assertEqual(client._latest_factory_metadata, mock_factory_metadata)

    def test_set_alarm_list(self):
        """
        Test the set_alarm_list public api method of N2KClient.
        """
        client = N2KClient()
        mock_alarm_list = AlarmList()
        mock_alarm = Alarm(
            state=AlarmState.ENABLED,
            date_active=1,
            things=["battery.1"],
            title="Test Alarm",
            name="Test Alarm",
            description="Test Alarm",
            unique_id=123,
            severity=AlarmSeverity.CRITICAL,
        )

        mock_alarm_list.alarm["alarm1"] = mock_alarm
        # Optionally, patch or spy on on_next if needed
        client._set_alarm_list(mock_alarm_list)
        # Assert the internal state or effect
        self.assertEqual(client._latest_alarms, mock_alarm_list)

    def test_set_engine_alarms(self):
        """
        Test the set_engine_alarms public api method of N2KClient.
        """
        client = N2KClient()
        mock_engine_alarm_list = EngineAlarmList()
        mock_engine_device = EngineDevice()
        instance = Instance()
        instance.enabled = True
        instance.instance = 1

        mock_engine_device.instance = instance
        mock_engine_device.calibration_id = "calibration_id"
        mock_engine_device.ecu_serial_number = "ecu_serial_number"
        mock_engine_device.engine_type = EngineType.NMEA2000
        mock_engine_device.id = 1
        mock_engine_device.serial_number = "serial_number"
        mock_engine_device.software_id = "software_id"
        mock_engine_device.name_utf8 = "Test Engine"

        mock_alarm = EngineAlarm(
            date_active=1,
            alarm_text="test_alarm",
            engine=mock_engine_device,
            current_discrete_status1=1,
            current_discrete_status2=2,
            prev_discrete_status1=3,
            prev_discrete_status2=4,
            alarm_id="test_id",
        )
        mock_engine_alarm_list.engine_alarms["alarm1"] = mock_alarm
        # Optionally, patch or spy on on_next if needed
        client._set_engine_alarms(mock_engine_alarm_list)
        # Assert the internal state or effect
        self.assertEqual(client._latest_engine_alarms, mock_engine_alarm_list)

    def test_dispose_empower_system(self):
        """
        Test the dispose_empower_system public api method of N2KClient.
        """
        client = N2KClient()
        client._latest_empower_system = EmpowerSystem(config_metadata=None)
        thing = Thing(
            type=ThingType.BATTERY,
            id="battery1",
            name="Test Batt",
            categories=[],
            links=[],
        )
        client._latest_empower_system.add_thing(thing)

        self.assertEqual(len(client._latest_empower_system.things), 1)

        client.dispose_empower_system()

        # Assert the internal state or effect
        self.assertEqual(len(client._latest_empower_system.things), 0)

    def test_client_disposes_disposables(self):
        client = N2KClient()
        mock_disposable1 = MagicMock()
        mock_disposable2 = MagicMock()
        client._disposable_list = [mock_disposable1, mock_disposable2]

        # Call the disposal logic explicitly
        client.__del__()

        mock_disposable1.dispose.assert_called_once()
        mock_disposable2.dispose.assert_called_once()

    def test_start_creates_and_starts_thread(self):
        client = N2KClient()
        with patch("threading.Thread") as mock_thread_class:
            mock_thread_instance = MagicMock()
            mock_thread_class.return_value = mock_thread_instance

            client.start()

            mock_thread_class.assert_called_once_with(
                target=client.run_mainloop, daemon=True
            )
            mock_thread_instance.start.assert_called_once()
