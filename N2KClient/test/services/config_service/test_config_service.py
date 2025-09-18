import unittest
from unittest import mock
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.services.config_service.config_service import ConfigService
from N2KClient.n2kclient.models.common_enums import ConfigOperationType


class TestConfigService(unittest.TestCase):
    """
    Unit tests for ConfigService
    """

    def test_config_service_init(self):
        """Tests ConfigService initialization"""
        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        self.assertIsInstance(service, ConfigService)
        self.assertIsNotNone(service._config_processor)
        self.assertIsNotNone(service._config_parser)
        self.assertEqual(service._dbus_proxy, mock_dbus_proxy)
        self.assertEqual(service._lock, mock_lock)
        self.assertEqual(service._get_latest_devices, mock_get_latest_devices)
        self.assertEqual(service._set_devices, mock_set_devices)
        self.assertEqual(service._set_config, mock_set_config)
        self.assertEqual(service._set_empower_system, mock_set_empower_system)
        self.assertEqual(service._dispose_empower_system, mock_dispose_empower_system)
        self.assertEqual(service._get_engine_config, mock_get_engine_config)
        self.assertEqual(service._get_engine_list, mock_get_engine_list)
        self.assertEqual(service._set_engine_config, mock_set_engine_config)
        self.assertEqual(service._set_engine_list, mock_set_engine_list)
        self.assertEqual(service._set_factory_metadata, mock_set_factory_metadata)
        self.assertEqual(service._request_state_snapshot, mock_request_state_snapshot)

    def test_write_configuration(self):
        """
        Tests write configuration method.
        Ensure call to send_and_validate_config for put_file method with config hex string
        Call to send_and_validate_config for operation method with write config operation
        Returns True
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )

        config_hex_string = "deadbeef"
        with patch(
            "N2KClient.n2kclient.services.config_service.config_service.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.config_service.config_service.sleep"
        ) as mock_sleep:
            result = service.write_configuration(config_hex_string)
            first_call_args = mock_send_and_validate_response.call_args_list[0]
            args, kwargs = first_call_args
            self.assertEqual(args[0], mock_dbus_proxy.put_file)
            self.assertEqual(args[1]["Content"], config_hex_string)
            mock_sleep.assert_called_once()

            second_call_args = mock_send_and_validate_response.call_args_list[1]
            args, kwargs = second_call_args
            self.assertEqual(args[0], mock_dbus_proxy.operation)
            self.assertEqual(args[1]["type"], ConfigOperationType.WriteConfig.value)
            self.assertEqual(mock_send_and_validate_response.call_count, 2)
            self.assertTrue(result)

    def test_write_configuration_first_false(self):
        """
        Ensure call to send_and_validate_config for put_file method with config hex string,
        Returns False
        """

        service = ConfigService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        config_hex_string = "deadbeef"
        with patch(
            "N2KClient.n2kclient.services.config_service.config_service.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.config_service.config_service.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.return_value = False
            result = service.write_configuration(config_hex_string)
            mock_send_and_validate_response.assert_called_once()
            mock_sleep.assert_not_called()
            self.assertFalse(result)

    def test_write_configuration_second_false(self):
        """
        Ensure call to send_and_validate_response for put_file method with config hex string,
        calls sleep
        calls to send_and_validate_response with operation, fails
        Returns False
        """

        service = ConfigService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        config_hex_string = "deadbeef"
        with patch(
            "N2KClient.n2kclient.services.config_service.config_service.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.config_service.config_service.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.side_effect = [True, False]
            result = service.write_configuration(config_hex_string)
            self.assertEqual(mock_send_and_validate_response.call_count, 2)
            mock_sleep.assert_called_once()
            self.assertFalse(result)

    def test_scan_factory_metadata(self):
        """
        calls dbus_proxy to get settings
        calls parser to parse metadata
        calls to set metadata
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.ConfigParser.parse_factory_metadata"
        ) as mock_parse_metadata:
            mock_dbus_proxy.get_setting.return_value = '{"FactoryMetadata": "deadbeef"}'
            mock_parse_metadata.return_value = {"key": "value"}
            service.scan_factory_metadata()

            mock_dbus_proxy.get_setting.assert_called_once_with("FactoryData")
            mock_parse_metadata.assert_called_once_with({"FactoryMetadata": "deadbeef"})
            service._set_factory_metadata.assert_called_once_with({"key": "value"})

    def test_scan_factory_metadata_exception(self):
        """
        if exception is thrown, error is caught
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_dbus_proxy.get_setting.side_effect = Exception("test error")
        try:
            service.scan_factory_metadata()
            pass
        except Exception as e:
            self.fail("Exception raised")

    def test_get_configuration(self):
        """
        Ensures devices are retrieved from DBus, old devices are disposed,
        empower system is built
        single snapshot is taken
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_devices = MagicMock()
        mock_get_latest_devices.return_value = mock_devices
        mock_config_json = MagicMock()
        mock_categories_json = MagicMock()
        mock_config_metadata_json = MagicMock()
        mock_dbus_proxy.get_config_all.return_value = mock_config_json
        mock_dbus_proxy.get_categories.return_value = mock_categories_json
        mock_dbus_proxy.get_setting.return_value = mock_config_metadata_json
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.ConfigParser.parse_config"
        ) as mock_parse_configuration, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.ConfigProcessor.build_empower_system"
        ) as mock_build_empower_system:
            # Arrange
            mock_parse_configuration.return_value = MagicMock()
            mock_build_empower_system.return_value = MagicMock()

            # ACT
            service.get_configuration()

            # ASSERT

            # LOCK
            mock_lock.__enter__.assert_called_once()
            mock_get_latest_devices.assert_called_once()
            mock_devices.dispose_devices.assert_called_once()
            mock_set_devices.assert_called_once_with(mock_devices)
            mock_lock.__exit__.assert_called_once()

            # Process/Set Config
            mock_dbus_proxy.get_categories.assert_called_once()
            mock_dbus_proxy.get_config_all.assert_called_once()
            mock_dbus_proxy.get_setting.assert_called_once_with("Config")
            mock_parse_configuration.assert_called_once_with(
                mock_config_json, mock_categories_json, mock_config_metadata_json
            )

            mock_set_config.assert_called_once_with(
                mock_parse_configuration.return_value
            )

            # Process/ Set Empower System
            mock_dispose_empower_system.assert_called_once()
            mock_build_empower_system.assert_called_once_with(
                mock_parse_configuration.return_value, mock_devices
            )
            mock_set_empower_system.assert_called_once_with(
                mock_build_empower_system.return_value
            )
            mock_request_state_snapshot.assert_called_once()

    def test_get_configuration_exception(self):
        """
        Test exception handling in get_configuration
        """
        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_get_latest_devices.side_effect = Exception("Test error")
        try:
            service.get_configuration()
            pass
        except Exception as e:
            self.fail("Exception raised")

    def test_scan_marine_engine_config_should_reset_true_engine_list_not_none(self):
        """
        Ensures engine devices are retrieved from DBus, old devices are disposed,
        engine list is built
        single snapshot is taken
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_devices = MagicMock()
        mock_get_latest_devices.return_value = mock_devices
        mock_config_json = MagicMock()
        mock_categories_json = MagicMock()
        mock_config_metadata_json = MagicMock()
        mock_dbus_proxy.get_config.return_value = mock_config_json
        mock_dbus_proxy.get_categories.return_value = mock_categories_json
        mock_dbus_proxy.get_setting.return_value = mock_config_metadata_json
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.ConfigParser.parse_engine_configuration"
        ) as mock_parse_engine_configuration, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.ConfigProcessor.build_engine_list"
        ) as mock_build_engine_list:
            # Arrange
            mock_engine_configuration = MagicMock()
            mock_parse_engine_configuration.return_value = mock_engine_configuration
            mock_build_engine_list.return_value = MagicMock()
            engine_list = MagicMock()
            mock_get_engine_list.return_value = engine_list

            mock_engine_config = MagicMock()
            mock_get_engine_config.return_value = mock_engine_config

            mock_build_engine_list.return_value = MagicMock()
            # ACT
            res = service.scan_marine_engine_config(should_reset=True)

            # ASSERT

            mock_get_engine_config.assert_called_once()

            # LOCK
            mock_get_latest_devices.assert_called_once()
            mock_lock.__enter__.assert_called_once()
            mock_devices.dispose_devices.assert_called_once_with(True)
            mock_set_devices.assert_called_once_with(mock_devices)
            mock_lock.__exit__.assert_called_once()

            # Engine List
            mock_get_engine_list.assert_called_once()
            engine_list.dispose.assert_called_once()

            # Process/Set Config
            mock_dbus_proxy.get_config.assert_called_once_with("Engines")
            mock_parse_engine_configuration.assert_called_once_with(
                mock_config_json, mock_engine_config
            )
            mock_set_engine_config.assert_called_once_with(mock_engine_configuration)

            # Engine List
            mock_build_engine_list.assert_called_once_with(
                mock_engine_configuration, mock_devices
            )

            mock_set_engine_list.assert_called_once_with(
                mock_build_engine_list.return_value
            )
            mock_request_state_snapshot.assert_called_once()

            self.assertTrue(res)

    def test_scan_marine_engine_config_should_reset_true_engine_list_none(self):
        """
        Ensures engine devices are retrieved from DBus, old devices are not disposed if None
        engine list is built
        single snapshot is taken
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_devices = MagicMock()
        mock_get_latest_devices.return_value = mock_devices
        mock_config_json = MagicMock()
        mock_categories_json = MagicMock()
        mock_config_metadata_json = MagicMock()
        mock_dbus_proxy.get_config.return_value = mock_config_json
        mock_dbus_proxy.get_categories.return_value = mock_categories_json
        mock_dbus_proxy.get_setting.return_value = mock_config_metadata_json
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.ConfigParser.parse_engine_configuration"
        ) as mock_parse_engine_configuration, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.ConfigProcessor.build_engine_list"
        ) as mock_build_engine_list:
            # Arrange
            mock_engine_configuration = MagicMock()
            mock_parse_engine_configuration.return_value = mock_engine_configuration
            mock_build_engine_list.return_value = MagicMock()
            engine_list = MagicMock()
            mock_get_engine_list.return_value = None

            mock_engine_config = MagicMock()
            mock_get_engine_config.return_value = mock_engine_config

            mock_build_engine_list.return_value = MagicMock()
            # ACT
            res = service.scan_marine_engine_config(should_reset=True)

            # ASSERT

            mock_get_engine_config.assert_called_once()

            # LOCK
            mock_get_latest_devices.assert_called_once()
            mock_lock.__enter__.assert_called_once()
            mock_devices.dispose_devices.assert_called_once_with(True)
            mock_set_devices.assert_called_once_with(mock_devices)
            mock_lock.__exit__.assert_called_once()

            # Engine List
            mock_get_engine_list.assert_called_once()
            engine_list.dispose.assert_not_called()

            # Process/Set Config
            mock_dbus_proxy.get_config.assert_called_once_with("Engines")
            mock_parse_engine_configuration.assert_called_once_with(
                mock_config_json, mock_engine_config
            )
            mock_set_engine_config.assert_called_once_with(mock_engine_configuration)

            # Engine List
            mock_build_engine_list.assert_called_once_with(
                mock_engine_configuration, mock_devices
            )

            mock_set_engine_list.assert_called_once_with(
                mock_build_engine_list.return_value
            )
            mock_request_state_snapshot.assert_called_once()

            self.assertTrue(res)

    def test_scan_marine_engine_config_should_reset_false(self):
        """
        Ensures engine devices are retrieved from DBus, old devices are not disposed
        engine list is built
        single snapshot is taken
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_devices = MagicMock()
        mock_get_latest_devices.return_value = mock_devices
        mock_config_json = MagicMock()
        mock_categories_json = MagicMock()
        mock_config_metadata_json = MagicMock()
        mock_dbus_proxy.get_config.return_value = mock_config_json
        mock_dbus_proxy.get_categories.return_value = mock_categories_json
        mock_dbus_proxy.get_setting.return_value = mock_config_metadata_json
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.ConfigParser.parse_engine_configuration"
        ) as mock_parse_engine_configuration, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.ConfigProcessor.build_engine_list"
        ) as mock_build_engine_list:
            # Arrange
            mock_engine_configuration = MagicMock()
            mock_parse_engine_configuration.return_value = mock_engine_configuration
            mock_build_engine_list.return_value = MagicMock()
            engine_list = MagicMock()
            mock_get_engine_list.return_value = engine_list

            mock_engine_config = MagicMock()
            mock_get_engine_config.return_value = mock_engine_config

            mock_build_engine_list.return_value = MagicMock()
            # ACT
            res = service.scan_marine_engine_config(should_reset=False)

            # ASSERT

            mock_get_engine_config.assert_called_once()

            # LOCK
            mock_get_latest_devices.assert_called_once()
            mock_lock.__enter__.assert_not_called()
            mock_devices.dispose_devices.assert_not_called()
            mock_set_devices.assert_not_called()
            mock_lock.__exit__.assert_not_called()

            # Engine List
            mock_get_engine_list.assert_not_called()

            # Process/Set Config
            mock_dbus_proxy.get_config.assert_called_once_with("Engines")
            mock_parse_engine_configuration.assert_called_once_with(
                mock_config_json, mock_engine_config
            )
            mock_set_engine_config.assert_called_once_with(mock_engine_configuration)

            # Engine List
            mock_build_engine_list.assert_called_once_with(
                mock_engine_configuration, mock_devices
            )

            mock_set_engine_list.assert_called_once_with(
                mock_build_engine_list.return_value
            )
            mock_request_state_snapshot.assert_called_once()

            self.assertTrue(res)

    def test_scan_marine_engine_exception(self):
        """
        Ensures exception is properly handled
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_get_latest_devices.side_effect = Exception("Test error")
        res = service.scan_marine_engine_config(should_reset=False)
        self.assertFalse(res)

    def test_scan_config_metadata(self):
        """
        Get setting Config Metadata is called and returned
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )

        res = service._scan_config_metadata()
        mock_dbus_proxy.get_setting.assert_called_once_with("Config")
        self.assertEqual(res, mock_dbus_proxy.get_setting.return_value)

    def test_scan_config_metadata_exception(self):
        """
        Get setting Config Metadata is called, exception is handled and {} is returned
        """

        mock_dbus_proxy = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_set_config = MagicMock()
        mock_set_empower_system = MagicMock()
        mock_dispose_empower_system = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_get_engine_list = MagicMock()
        mock_set_engine_config = MagicMock()
        mock_set_engine_list = MagicMock()
        mock_set_factory_metadata = MagicMock()
        mock_request_state_snapshot = MagicMock()
        service = ConfigService(
            mock_dbus_proxy,
            mock_lock,
            mock_get_latest_devices,
            mock_set_devices,
            mock_set_config,
            mock_set_empower_system,
            mock_dispose_empower_system,
            mock_get_engine_config,
            mock_get_engine_list,
            mock_set_engine_config,
            mock_set_engine_list,
            mock_set_factory_metadata,
            mock_request_state_snapshot,
        )
        mock_dbus_proxy.get_setting.side_effect = Exception("Test error")
        res = service._scan_config_metadata()
        mock_dbus_proxy.get_setting.assert_called_once_with("Config")
        self.assertEqual(res, {})
