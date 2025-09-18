import unittest
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.services.control_service.control_service import ControlService


class TestControlService(unittest.TestCase):
    """
    Unit tests for ControlService
    """

    def test_control_service(self):
        mock_get_config_func = MagicMock()
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        self.assertIsNotNone(control_service)
        self.assertIsNotNone(control_service._logger)

    def test_set_circuit_power_state_off_valid_throw(self):
        """
        Tests set circuit power state with....

        Valid circuit config
        Valid Circuit Device
        Circuit State Off
        Valid Throw
        """
        mock_get_config_func = MagicMock()
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        mock_config = MagicMock()
        mock_devices = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func.return_value = mock_devices
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1)),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_device",
            return_value=(None, MagicMock()),
        ) as mock_get_circuit_device, patch(
            "N2KClient.n2kclient.services.control_service.control_service.is_circuit_on",
            return_value=False,
        ) as mock_is_circuit_on, patch(
            "N2KClient.n2kclient.services.control_service.control_service.determine_circuit_control_operation",
            return_value="throw_type",
        ) as mock_determine_circuit_control_operation, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_switch",
            return_value=True,
        ) as mock_control_circuit_switch:
            result = control_service.set_circuit_power_state(
                runtime_id=1, target_on=True
            )
            self.assertTrue(result)
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_get_circuit_device.assert_called_once_with(
                mock_devices, mock_get_circuit_config.return_value
            )
            mock_is_circuit_on.assert_called_once_with(
                mock_get_circuit_device.return_value[1]
            )
            mock_determine_circuit_control_operation.assert_called_once_with(
                mock_get_circuit_config.return_value, True, False
            )
            mock_control_circuit_switch.assert_called_once_with(
                mock_send_func,
                1,
                mock_determine_circuit_control_operation.return_value,
                logger=control_service._logger,
            )

    def test_set_circuit_power_state_valid_config_get_config_none(self):
        """
        Tests set circuit power state with....

        None for circuit config
        """
        mock_get_config_func = MagicMock()
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        mock_config = MagicMock()
        mock_devices = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func.return_value = mock_devices
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=None,
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_device",
            return_value=(None, MagicMock()),
        ) as mock_get_circuit_device, patch(
            "N2KClient.n2kclient.services.control_service.control_service.is_circuit_on",
            return_value=False,
        ) as mock_is_circuit_on, patch(
            "N2KClient.n2kclient.services.control_service.control_service.determine_circuit_control_operation",
            return_value="throw_type",
        ) as mock_determine_circuit_control_operation, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_switch",
            return_value=True,
        ) as mock_control_circuit_switch:
            result = control_service.set_circuit_power_state(
                runtime_id=1, target_on=True
            )
            self.assertFalse(result)
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_get_circuit_device.assert_not_called()
            mock_is_circuit_on.assert_not_called()
            mock_determine_circuit_control_operation.assert_not_called()
            mock_control_circuit_switch.assert_not_called()

    def test_set_circuit_power_state_valid_config_determine_circuit_control_operation_none(
        self,
    ):
        """
        Tests set circuit power state with....

        Valid config for circuit config
        Control Operation returns none
        """
        mock_get_config_func = MagicMock()
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        mock_config = MagicMock()
        mock_devices = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func.return_value = mock_devices
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1)),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_device",
            return_value=(None, MagicMock()),
        ) as mock_get_circuit_device, patch(
            "N2KClient.n2kclient.services.control_service.control_service.is_circuit_on",
            return_value=False,
        ) as mock_is_circuit_on, patch(
            "N2KClient.n2kclient.services.control_service.control_service.determine_circuit_control_operation",
            return_value=None,
        ) as mock_determine_circuit_control_operation, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_switch",
            return_value=True,
        ) as mock_control_circuit_switch:
            result = control_service.set_circuit_power_state(
                runtime_id=1, target_on=True
            )
            self.assertTrue(result)
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_get_circuit_device.assert_called_once_with(
                mock_devices, mock_get_circuit_config.return_value
            )
            mock_is_circuit_on.assert_called_once_with(
                mock_get_circuit_device.return_value[1]
            )
            mock_determine_circuit_control_operation.assert_called_once_with(
                mock_get_circuit_config.return_value, True, False
            )
            mock_control_circuit_switch.assert_not_called()

    def test_set_circuit_power_state_valid_config_no_device(self):
        """
        Tests set circuit power state with....

        valid config for circuit config
        no device found
        """
        mock_get_config_func = MagicMock()
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        mock_config = MagicMock()
        mock_devices = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func.return_value = mock_devices
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1)),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_device",
            return_value=(None, None),
        ) as mock_get_circuit_device, patch(
            "N2KClient.n2kclient.services.control_service.control_service.is_circuit_on",
            return_value=False,
        ) as mock_is_circuit_on, patch(
            "N2KClient.n2kclient.services.control_service.control_service.determine_circuit_control_operation",
            return_value=None,
        ) as mock_determine_circuit_control_operation, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_switch",
            return_value=True,
        ) as mock_control_circuit_switch:
            result = control_service.set_circuit_power_state(
                runtime_id=1, target_on=True
            )
            self.assertFalse(result)
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_get_circuit_device.assert_called_once_with(
                mock_devices, mock_get_circuit_config.return_value
            )
            mock_is_circuit_on.assert_not_called()
            mock_determine_circuit_control_operation.assert_not_called()
            mock_control_circuit_switch.assert_not_called()

    def test_set_circuit_power_state_valid_config_no_device(self):
        """
        Tests set circuit power state with....

        valid config for circuit config
        no device found
        """
        mock_get_config_func = MagicMock()
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        mock_config = MagicMock()
        mock_devices = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func.return_value = mock_devices
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1)),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_device",
            return_value=(None, None),
        ) as mock_get_circuit_device, patch(
            "N2KClient.n2kclient.services.control_service.control_service.is_circuit_on",
            return_value=False,
        ) as mock_is_circuit_on, patch(
            "N2KClient.n2kclient.services.control_service.control_service.determine_circuit_control_operation",
            return_value=None,
        ) as mock_determine_circuit_control_operation, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_switch",
            return_value=True,
        ) as mock_control_circuit_switch:
            result = control_service.set_circuit_power_state(
                runtime_id=1, target_on=True
            )
            self.assertFalse(result)
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_get_circuit_device.assert_called_once_with(
                mock_devices, mock_get_circuit_config.return_value
            )
            mock_is_circuit_on.assert_not_called()
            mock_determine_circuit_control_operation.assert_not_called()
            mock_control_circuit_switch.assert_not_called()

    def test_set_circuit_power_state_valid_config_exception(self):
        """
        Tests set circuit power state.
        Exception is properly handled and returns False
        """
        mock_get_config_func = MagicMock()
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        mock_config = MagicMock()
        mock_devices = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func.return_value = mock_devices
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1)),
            side_effect=Exception("Test Exception"),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_device",
            return_value=(None, None),
        ) as mock_get_circuit_device, patch(
            "N2KClient.n2kclient.services.control_service.control_service.is_circuit_on",
            return_value=False,
        ) as mock_is_circuit_on, patch(
            "N2KClient.n2kclient.services.control_service.control_service.determine_circuit_control_operation",
            return_value=None,
        ) as mock_determine_circuit_control_operation, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_switch",
            return_value=True,
        ) as mock_control_circuit_switch:
            result = control_service.set_circuit_power_state(
                runtime_id=1, target_on=True
            )
            self.assertFalse(result)
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_get_circuit_device.assert_not_called()
            mock_is_circuit_on.assert_not_called()
            mock_determine_circuit_control_operation.assert_not_called()
            mock_control_circuit_switch.assert_not_called()

    def test_set_circuit_level_valid_circuit_config_not_dimmable_in_range(self):
        """
        Tests set circuit level method.

        Valid circuit config not dimmable in range (0-100)
        """

        mock_config = MagicMock()
        mock_get_config_func = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1), dimmable=True),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_level",
            return_value=True,
        ) as mock_control_circuit_level:
            result = control_service.set_circuit_level(runtime_id=1, target_level=50)
            mock_get_config_func.assert_called_once()
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_control_circuit_level.assert_called_once_with(
                mock_send_func,
                1,
                50,
                logger=control_service._logger,
            )
            self.assertTrue(result)

    def test_set_circuit_level_valid_circuit_config_over_range(self):
        """
        Tests set circuit level method.

        Valid circuit, target level not in range (0-100)
        Over range
        """

        mock_config = MagicMock()
        mock_get_config_func = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        result = control_service.set_circuit_level(runtime_id=1, target_level=110)
        self.assertFalse(result)

    def test_set_circuit_level_valid_circuit_config_under_range(self):
        """
        Tests set circuit level method.

        Valid circuit, target level not in range (0-100)
        Over range
        """

        mock_config = MagicMock()
        mock_get_config_func = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        result = control_service.set_circuit_level(runtime_id=1, target_level=-50)
        self.assertFalse(result)

    def test_set_circuit_level_not_valid_circuit_config(self):
        """
        Tests set circuit level method.

        Non-Valid circuit config returned
        """

        mock_config = MagicMock()
        mock_get_config_func = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=None,
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_level",
            return_value=True,
        ) as mock_control_circuit_level:
            result = control_service.set_circuit_level(runtime_id=1, target_level=50)
            mock_get_config_func.assert_called_once()
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_control_circuit_level.assert_not_called()
            self.assertFalse(result)

    def test_set_circuit_level_not_dimmable(self):
        """
        Tests set circuit level method.

        valid not dimmable config
        """

        mock_config = MagicMock()
        mock_get_config_func = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1), dimmable=False),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_level",
            return_value=True,
        ) as mock_control_circuit_level:
            result = control_service.set_circuit_level(runtime_id=1, target_level=50)
            mock_get_config_func.assert_called_once()
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_control_circuit_level.assert_not_called()
            self.assertFalse(result)

    def test_set_circuit_level_exception(self):
        """
        Tests set circuit level method.

        Exception returns none
        """

        mock_config = MagicMock()
        mock_get_config_func = MagicMock()
        mock_get_config_func.return_value = mock_config
        mock_get_devices_func = MagicMock()
        mock_send_func = MagicMock()
        control_service = ControlService(
            get_config_func=mock_get_config_func,
            get_devices_func=mock_get_devices_func,
            send_control_func=mock_send_func,
        )
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service.get_circuit_config",
            return_value=MagicMock(id=MagicMock(value=1), dimmable=False),
            side_effect=Exception("TESTEXCEPTION"),
        ) as mock_get_circuit_config, patch(
            "N2KClient.n2kclient.services.control_service.control_service.control_circuit_level",
            return_value=True,
        ) as mock_control_circuit_level:
            result = control_service.set_circuit_level(runtime_id=1, target_level=50)
            mock_get_config_func.assert_called_once()
            mock_get_circuit_config.assert_called_once_with(
                mock_config, 1, logger=control_service._logger
            )
            mock_control_circuit_level.assert_not_called()
            self.assertFalse(result)
