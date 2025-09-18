import unittest
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.services.control_service.control_service_helpers import (
    get_circuit_config,
    is_circuit_on,
    determine_circuit_control_operation,
    control_circuit_switch,
    control_circuit_level,
)
from N2KClient.n2kclient.models.common_enums import (
    SwitchType,
    ThrowType,
    ControlRequest,
)
from N2KClient.n2kclient.util.common_utils import send_and_validate_response


class TestControlHelpers(unittest.TestCase):
    """
    Unit tests for ControlHelpers
    """

    def test_get_circuit_config(self):
        """Tests get circuit config with valid circuit in config returns circuit"""
        mock_circuit = MagicMock()
        mock_config = MagicMock(circuit={1: mock_circuit})
        result = get_circuit_config(mock_config, 1, logger=MagicMock())
        self.assertEqual(result, mock_circuit)

    def test_get_circuit_config_none(self):
        """Tests get circuit config with invalid circuit in config returns None"""
        mock_config = MagicMock(circuit={})
        result = get_circuit_config(mock_config, 1, logger=MagicMock())
        self.assertIsNone(result)

    def test_get_circuit_config_none_no_logger(self):
        """Tests get circuit config with invalid circuit in config returns None"""
        mock_config = MagicMock(circuit={})
        result = get_circuit_config(mock_config, 1)
        self.assertIsNone(result)

    def test_is_circuit_on_ON(self):
        """Tests is_circuit_on_ with circuit 0 in config returns True"""
        mock_circuit_device = MagicMock(channels={"Level": 11})
        result = is_circuit_on(mock_circuit_device)
        self.assertTrue(result)

    def test_is_circuit_on_OFF(self):
        """Tests is_circuit_on_ with circuit 0 not in config returns False"""
        mock_circuit_device = MagicMock(channels={"Level": 0})
        result = is_circuit_on(mock_circuit_device)
        self.assertFalse(result)

    def test_determine_circuit_control_operation_no_complement_on(self):
        """
        Tests determine_circuit_control_operation with valid inputs.

        Not has complement

        Switch that can turn on is turned on
        """
        mock_circuit_config = MagicMock(
            has_complement=False, switch_type=SwitchType.DimLinearUp
        )
        result = determine_circuit_control_operation(mock_circuit_config, True, False)
        self.assertEqual(result, "SingleThrow")

    def test_determine_circuit_control_operation_no_complement_off(self):
        """
        Tests determine_circuit_control_operation with valid inputs.

        Not has complement.

        Switch that can turn off is turned off
        """
        mock_circuit_config = MagicMock(
            has_complement=False, switch_type=SwitchType.DimLinearDown
        )
        result = determine_circuit_control_operation(mock_circuit_config, False, True)
        self.assertEqual(result, "SingleThrow")

    def test_determine_circuit_control_operation_complement_double_throw(
        self,
    ):
        """
        Tests determine_circuit_control_operation with valid inputs.

        has complement, target off, double throw
        """
        mock_circuit_config = MagicMock(
            has_complement=True, switch_type=SwitchType.DimLinearUp
        )
        result = determine_circuit_control_operation(mock_circuit_config, False, True)
        self.assertEqual(result, "DoubleThrow")

    def test_determine_circuit_control_operation_complement_single_throw(
        self,
    ):
        """
        Tests determine_circuit_control_operation with valid inputs.

        has complement, target on, single throw
        """
        mock_circuit_config = MagicMock(
            has_complement=True, switch_type=SwitchType.DimLinearUp
        )
        result = determine_circuit_control_operation(mock_circuit_config, True, False)
        self.assertEqual(result, "SingleThrow")

    def test_determine_circuit_control_operation_on_and_off_same(
        self,
    ):
        """
        Tests determine_circuit_control_operation with valid inputs.

        has complement, target on, single throw
        """
        mock_circuit_config = MagicMock(
            has_complement=True, switch_type=SwitchType.DimLinearUp
        )
        result = determine_circuit_control_operation(mock_circuit_config, True, True)
        self.assertIsNone(result)

    def test_determine_circuit_control_operation_wrong_switch_type_on(
        self,
    ):
        """
        Tests determine_circuit_control_operation with valid inputs.

        No complement, target on and switch type doesn't support on
        """
        mock_circuit_config = MagicMock(
            has_complement=False, switch_type=SwitchType.DimLinearUp
        )
        with self.assertRaises(Exception):
            determine_circuit_control_operation(mock_circuit_config, False, True)

    def test_determine_circuit_control_operation_wrong_switch_type_off(
        self,
    ):
        """
        Tests determine_circuit_control_operation with valid inputs.

        No complement, target off and switch type doesn't support off
        """
        mock_circuit_config = MagicMock(
            has_complement=False, switch_type=SwitchType.DimLinearDown
        )
        with self.assertRaises(Exception):
            determine_circuit_control_operation(mock_circuit_config, True, False)

    def test_control_circuit_switch(self):
        """
        Tests control_circuit_switch with valid inputs calls to send and validate response with activate and release
        """
        mock_send_control = MagicMock()
        mock_send_control.return_value = True
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.return_value = True
            result = control_circuit_switch(mock_send_control, 1, ThrowType.SingleThrow)
            first_call_args = mock_send_and_validate_response.call_args_list[0]
            args, kwargs = first_call_args
            self.assertEqual(args[0], mock_send_control)
            self.assertEqual(args[1]["Type"], ControlRequest.Activate.value)
            self.assertEqual(args[1]["Id"], 1)
            self.assertEqual(args[1]["ThrowType"], ThrowType.SingleThrow.value)
            mock_sleep.assert_called_once()

            second_call_args = mock_send_and_validate_response.call_args_list[1]
            args, kwargs = second_call_args
            self.assertEqual(args[0], mock_send_control)
            self.assertEqual(args[1]["Type"], ControlRequest.Release.value)
            self.assertEqual(args[1]["Id"], 1)
            self.assertEqual(mock_send_and_validate_response.call_count, 2)
            self.assertTrue(result)

    def test_control_circuit_switch_first_false(self):
        """
        Tests control_circuit_switch with valid inputs calls to send and validate response with activate and release
        """
        mock_send_control = MagicMock()
        mock_send_control.return_value = True
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.return_value = False
            result = control_circuit_switch(mock_send_control, 1, ThrowType.SingleThrow)
            mock_sleep.assert_not_called()
            self.assertEqual(mock_send_and_validate_response.call_count, 1)
            self.assertFalse(result)

    def test_control_circuit_switch_second_false(self):
        """
        Tests control_circuit_switch with valid inputs calls to send and validate response with activate and release
        """
        mock_send_control = MagicMock()
        mock_send_control.return_value = True
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.side_effect = [True, False]
            result = control_circuit_switch(mock_send_control, 1, ThrowType.SingleThrow)
            mock_sleep.assert_called_once()
            self.assertEqual(mock_send_and_validate_response.call_count, 2)
            self.assertFalse(result)

    def test_control_circuit_level(self):
        """
        Tests control_circuit_switch with valid inputs calls to send and validate response with activate and release
        """
        mock_send_control = MagicMock()
        mock_send_control.return_value = True
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.return_value = True
            result = control_circuit_level(mock_send_control, 1, 100)
            first_call_args = mock_send_and_validate_response.call_args_list[0]
            args, kwargs = first_call_args
            self.assertEqual(args[0], mock_send_control)
            self.assertEqual(args[1]["Type"], ControlRequest.SetAbsolute.value)
            self.assertEqual(args[1]["Id"], 1)
            self.assertEqual(args[1]["Level"], 100)
            mock_sleep.assert_called_once()

            second_call_args = mock_send_and_validate_response.call_args_list[1]
            args, kwargs = second_call_args
            self.assertEqual(args[0], mock_send_control)
            self.assertEqual(args[1]["Type"], ControlRequest.Release.value)
            self.assertEqual(args[1]["Id"], 1)
            self.assertEqual(mock_send_and_validate_response.call_count, 2)
            self.assertTrue(result)

    def test_control_circuit_level_first_false(self):
        """
        Tests control_circuit_level with valid inputs calls to send and validate response with activate and release
        """
        mock_send_control = MagicMock()
        mock_send_control.return_value = True
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.return_value = False
            result = control_circuit_level(mock_send_control, 1, 100)
            mock_sleep.assert_not_called()
            self.assertEqual(mock_send_and_validate_response.call_count, 1)
            self.assertFalse(result)

    def test_control_circuit_level_second_false(self):
        """
        Tests control_circuit_level with valid inputs calls to send and validate response with activate and release
        """
        mock_send_control = MagicMock()
        mock_send_control.return_value = True
        with patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.send_and_validate_response"
        ) as mock_send_and_validate_response, patch(
            "N2KClient.n2kclient.services.control_service.control_service_helpers.sleep"
        ) as mock_sleep:
            mock_send_and_validate_response.side_effect = [True, False]
            result = control_circuit_level(mock_send_control, 1, 100)
            mock_sleep.assert_called_once()
            self.assertEqual(mock_send_and_validate_response.call_count, 2)
            self.assertFalse(result)
