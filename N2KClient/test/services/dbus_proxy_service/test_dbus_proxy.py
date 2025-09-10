import unittest
from unittest.mock import MagicMock, call, patch

from N2KClient.n2kclient.models.common_enums import ConnectionStatus
from N2KClient.n2kclient.models.dbus_connection_status import DBUSConnectionStatus
from N2KClient.n2kclient.services.dbus_proxy_service.dbus_proxy import DbusProxyService
import dbus


class TestDbusProxyService(unittest.TestCase):
    """Unit test for DBUS Proxy Service"""

    def test_dbus_proxy_service_init(self):
        status_callback = MagicMock()
        event_handler = MagicMock()
        snapshot_handler = MagicMock()
        control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            status_callback=status_callback,
            event_handler=event_handler,
            snapshot_handler=snapshot_handler,
            control_max_attempts=control_max_attempts,
        )
        self.assertEqual(dbus_service.status_callback, status_callback)
        self.assertEqual(dbus_service.event_handler, event_handler)
        self.assertEqual(dbus_service.snapshot_handler, snapshot_handler)
        self.assertEqual(dbus_service.control_max_attempts, control_max_attempts)

    def test_connect(self):
        """
        Test connect updates connection state to CONNECTED and calls connect_dbus
        """
        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            status_callback=mock_status_callback,
            event_handler=mock_event_handler,
            snapshot_handler=mock_snapshot_handler,
            control_max_attempts=mock_control_max_attempts,
        )
        with patch.object(
            dbus_service, "_connect_dbus"
        ) as mock_connect_dbus, patch.object(
            dbus_service, "_report_status"
        ) as mock_report_status:
            dbus_service.connect()
            mock_connect_dbus.assert_called_once()
            mock_report_status.assert_called_once_with(True)

    def test_connect_exception_once(self):
        """
        Test connect handles exception and updates status accordingly
        Sleeps for 5 second, then retries

        Set connection state to Disconnect, then sets connection state to Connected
        """
        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )
        # Counter to break the loop after one iteration
        call_count = {"count": 0}

        def side_effect():
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise Exception("fail")
            else:
                # Succeed on second call to break loop
                return None

        with patch.object(service, "_connect_dbus", side_effect=side_effect), patch(
            "N2KClient.n2kclient.services.dbus_proxy_service.dbus_proxy.sleep",
            return_value=None,
        ) as mock_sleep, patch.object(service, "_report_status") as mock_report_status:
            service.connect()
            mock_sleep.assert_called_once_with(5)  # Sleep called once on failure
            # First call: disconnected, with reason
            mock_report_status.assert_any_call(False, "fail")
            # Second call: connected, no reason
            mock_report_status.assert_any_call(True)
            self.assertEqual(call_count["count"], 2)  # One failure, one success

    def test_connect_dbus_with_system_bus(self):
        """
        Test connect_dbus initializes bus, sets up signal handlers, and connects to the bus.
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )

        with patch.object(
            dbus_service, "_register_signal_handlers"
        ) as mock_signal_handlers, patch.object(
            dbus_service, "_register_methods"
        ) as mock_register_methods, patch(
            "dbus.SystemBus"
        ) as mock_system_bus, patch(
            "platform.system", return_value="NotDarwin"
        ), patch(
            "dbus.Interface"
        ) as mock_interface:
            # Create the bus instance and set get_object
            mock_bus_instance = MagicMock()
            mock_system_bus.return_value = mock_bus_instance
            mock_get_object_res = MagicMock()
            mock_bus_instance.get_object.return_value = mock_get_object_res

            dbus_service._connect_dbus()
            mock_register_methods.assert_called_once()
            mock_signal_handlers.assert_called_once()
            self.assertTrue(dbus_service.bus, mock_bus_instance)
            mock_interface.assert_called_once_with(
                mock_get_object_res, "org.navico.HubN2K.czone"
            )
            mock_bus_instance.get_object.assert_called_once_with(
                "org.navico.HubN2K", "/org/navico/HubN2K"
            )

    def test_connect_dbus_with_session_bus(self):
        """
        Test connect_dbus initializes bus, sets up signal handlers, and connects to the bus.
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )

        with patch.object(
            dbus_service, "_register_signal_handlers"
        ) as mock_signal_handlers, patch.object(
            dbus_service, "_register_methods"
        ) as mock_register_methods, patch(
            "dbus.SessionBus"
        ) as mock_system_bus, patch(
            "platform.system", return_value="Darwin"
        ), patch(
            "dbus.Interface"
        ) as mock_interface:
            # Create the bus instance and set get_object
            mock_bus_instance = MagicMock()
            mock_system_bus.return_value = mock_bus_instance
            mock_get_object_res = MagicMock()
            mock_bus_instance.get_object.return_value = mock_get_object_res

            dbus_service._connect_dbus()
            mock_register_methods.assert_called_once()
            mock_signal_handlers.assert_called_once()
            self.assertTrue(dbus_service.bus, mock_bus_instance)
            mock_interface.assert_called_once_with(
                mock_get_object_res, "org.navico.HubN2K.czone"
            )
            mock_bus_instance.get_object.assert_called_once_with(
                "org.navico.HubN2K", "/org/navico/HubN2K"
            )

    def test_register_signal_handlers(self):
        """
        Test _register_signal_handlers sets up the necessary signal handlers.
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )

        dbus_service.bus = MagicMock()

        dbus_service._register_signal_handlers()

        expected_calls = [
            call(
                mock_event_handler,
                dbus_interface="org.navico.HubN2K.czone",
                signal_name="Event",
                path="/org/navico/HubN2K",
            ),
            call(
                mock_snapshot_handler,
                dbus_interface="org.navico.HubN2K.czone",
                signal_name="Snapshot",
                path="/org/navico/HubN2K",
            ),
        ]

        dbus_service.bus.add_signal_receiver.assert_has_calls(
            expected_calls, any_order=True
        )

    def test_register_methods(self):
        dbus_service = DbusProxyService()
        dbus_service.n2k_dbus_interface = MagicMock()
        # Create a unique mock for each method
        mocks = [
            MagicMock(name=f"mock_{attr}") for attr, _ in dbus_service.DBUS_METHOD_MAP
        ]
        dbus_service.n2k_dbus_interface.get_dbus_method.side_effect = mocks

        dbus_service._register_methods()

        for (attr, method), mock in zip(dbus_service.DBUS_METHOD_MAP, mocks):
            self.assertIs(getattr(dbus_service, attr), mock)
            dbus_service.n2k_dbus_interface.get_dbus_method.assert_any_call(method)

    def test_report_status_connected(self):
        """
        Test report_status properly handles connected and reason
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )

        dbus_service.bus = MagicMock()
        dbus_service.n2k_dbus_interface = MagicMock()
        dbus_service._register_methods()

        dbus_service._report_status(True)

        actual_status = mock_status_callback.call_args[0][0]
        self.assertEqual(actual_status.connection_state, ConnectionStatus.CONNECTED)
        self.assertEqual(actual_status.reason, "")

    def test_report_status_disconnected(self):
        """
        Test report_status properly handles disconnected and reason
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )

        dbus_service.bus = MagicMock()
        dbus_service.n2k_dbus_interface = MagicMock()
        dbus_service._register_methods()

        dbus_service._report_status(False, "Test Reason")

        actual_status = mock_status_callback.call_args[0][0]
        self.assertEqual(actual_status.connection_state, ConnectionStatus.DISCONNECTED)
        self.assertEqual(actual_status.reason, "Test Reason")

    def test_report_status_no_callback(self):
        """
        Test report_status properly handles no callback set. No exception raised
        """

        mock_status_callback = None
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )

        dbus_service.bus = MagicMock()
        dbus_service.n2k_dbus_interface = MagicMock()
        dbus_service._register_methods()

        dbus_service._report_status(False, "Test Reason")

        pass

    def test_call_with_retry_success(self):
        """
        On success, the method should return the result and set status to true
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )
        with patch.object(dbus_service, "_report_status") as mock_report_status:
            dbus_service.test_method = MagicMock(return_value="test_result")
            result = dbus_service._call_with_retry("test_method", "test_arg")
            self.assertEqual(result, "test_result")
            self.assertTrue(dbus_service.test_method.called)
            mock_report_status.assert_called_once_with(True)

    def test_call_with_retry_1_method_fail(self):
        """
        On failure, the method should set status to false, and retry
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )
        with patch.object(dbus_service, "_report_status") as mock_report_status, patch(
            "N2KClient.n2kclient.services.dbus_proxy_service.dbus_proxy.sleep",
            return_value=None,
        ) as mock_sleep, patch.object(
            dbus_service, "_connect_dbus"
        ) as mock_connect_dbus:
            dbus_service._dbus_test_method = MagicMock(
                side_effect=[dbus.exceptions.DBusException("fail"), "ok"]
            )
            result = dbus_service._call_with_retry("_dbus_test_method", max_attempts=2)
            self.assertEqual(result, "ok")
            self.assertEqual(dbus_service._dbus_test_method.call_count, 2)
            mock_report_status.assert_any_call(False, "fail")
            mock_report_status.assert_any_call(True)
            mock_sleep.assert_called_with(dbus_service._dbus_retry_delay)
            mock_connect_dbus.assert_called_once()

    def test_call_with_retry_1_method_fail_1_dbus_connect_fail(self):
        """
        On failure, the method should set status to false, and retry, fail connect_dbus and retry that too
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )
        # Simulate _connect_dbus failing once, then succeeding
        connect_dbus_side_effects = [Exception("connect fail"), None]
        with patch.object(dbus_service, "_report_status") as mock_report_status, patch(
            "N2KClient.n2kclient.services.dbus_proxy_service.dbus_proxy.sleep",
            return_value=None,
        ) as mock_sleep, patch.object(
            dbus_service, "_connect_dbus", side_effect=connect_dbus_side_effects
        ) as mock_connect_dbus:
            dbus_service._dbus_test_method = MagicMock(
                side_effect=[dbus.exceptions.DBusException("fail"), "ok"]
            )
            result = dbus_service._call_with_retry("_dbus_test_method", max_attempts=2)
            self.assertEqual(result, "ok")
            self.assertEqual(dbus_service._dbus_test_method.call_count, 2)
            mock_report_status.assert_any_call(False, "fail")
            mock_report_status.assert_any_call(True)
            mock_sleep.assert_called_with(dbus_service._dbus_retry_delay)
            self.assertEqual(mock_connect_dbus.call_count, 2)

    def test_call_with_retry_exceed_max_attempts(self):
        """
        On failure, the method should set status to false. Exceeding max attempts stops attempts and raises exceptions
        """

        mock_status_callback = MagicMock()
        mock_event_handler = MagicMock()
        mock_snapshot_handler = MagicMock()
        mock_control_max_attempts = MagicMock()
        dbus_service = DbusProxyService(
            mock_status_callback,
            mock_event_handler,
            mock_snapshot_handler,
            mock_control_max_attempts,
        )
        with patch.object(dbus_service, "_report_status") as mock_report_status, patch(
            "N2KClient.n2kclient.services.dbus_proxy_service.dbus_proxy.sleep",
            return_value=None,
        ) as mock_sleep, patch.object(
            dbus_service, "_connect_dbus"
        ) as mock_connect_dbus, self.assertRaises(
            dbus.exceptions.DBusException
        ):
            dbus_service._dbus_test_method = MagicMock(
                side_effect=[dbus.exceptions.DBusException("fail"), "ok"]
            )
            result = dbus_service._call_with_retry("_dbus_test_method", max_attempts=1)
            self.assertEqual(result, "ok")
            self.assertEqual(dbus_service._dbus_test_method.call_count, 1)
            mock_report_status.assert_any_call(False, "fail")

    def test_get_config(self):
        """
        Test the get_config method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "config_result"
            res = dbus_service.get_config()
            self.assertEqual(res, "config_result")
            mock_call_with_retry.assert_called_once_with("_dbus_get_config")

    def test_get_config_all(self):
        """
        Test the get_config_all method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "config_result"
            res = dbus_service.get_config_all()
            self.assertEqual(res, "config_result")
            mock_call_with_retry.assert_called_once_with("_dbus_get_config_all")

    def test_get_categories(self):
        """
        Test the get_categories method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.get_categories()
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with("_dbus_get_categories")

    def test_get_settings(self):
        """
        Test the get_settings method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.get_setting("TESTARG", testkwarg="TESTKWARG")
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with(
                "_dbus_get_setting", "TESTARG", testkwarg="TESTKWARG"
            )

    def test_control(self):
        """
        Test the control method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.control("TESTARG", testkwarg="TESTKWARG")
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with(
                "_dbus_control",
                "TESTARG",
                testkwarg="TESTKWARG",
                max_attempts=dbus_service.control_max_attempts,
            )

    def test_alarm_acknowledge(self):
        """
        Test the alarm_acknowledge method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.alarm_acknowledge("TESTARG", testkwarg="TESTKWARG")
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with(
                "_dbus_alarm_acknowledge",
                "TESTARG",
                testkwarg="TESTKWARG",
                max_attempts=dbus_service.control_max_attempts,
            )

    def test_alarm_list(self):
        """
        Test the alarm_list method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.alarm_list("TESTARG", testkwarg="TESTKWARG")
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with(
                "_dbus_alarm_list", "TESTARG", testkwarg="TESTKWARG"
            )

    def test_single_snapshot(self):
        """
        Test the single snapshot method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.single_snapshot("TESTARG", testkwarg="TESTKWARG")
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with(
                "_dbus_single_snapshot", "TESTARG", testkwarg="TESTKWARG"
            )

    def test_put_file(self):
        """
        Test the put_file method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.put_file("TESTARG", testkwarg="TESTKWARG")
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with(
                "_dbus_put_file", "TESTARG", testkwarg="TESTKWARG"
            )

    def test_operation(self):
        """
        Test the operation method calls _call_with_retry with correct string for attr method
        """
        dbus_service = DbusProxyService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(dbus_service, "_call_with_retry") as mock_call_with_retry:
            mock_call_with_retry.return_value = "result"
            res = dbus_service.operation("TESTARG", testkwarg="TESTKWARG")
            self.assertEqual(res, "result")
            mock_call_with_retry.assert_called_once_with(
                "_dbus_operation", "TESTARG", testkwarg="TESTKWARG"
            )
