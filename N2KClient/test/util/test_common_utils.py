import logging
import unittest
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.models.n2k_configuration.ui_relationship_msg import ItemType
from N2KClient.n2kclient.util.common_utils import (
    is_in_category,
    calculate_inverter_charger_instance,
    get_associated_circuit,
    map_fields,
    map_enum_fields,
    map_list_fields,
    send_and_validate_response,
)
import types


class MyEnum:
    VALUE1 = 1
    VALUE2 = 2

    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, MyEnum):
            return int(self.value) == int(other.value)
        return int(self.value) == int(other)


class TestCommonUtils(unittest.TestCase):

    def test_is_in_category(self):
        categories = [MagicMock(name_utf8="TestCategory", enabled=True, index=3)]
        category_name = "TestCategory"
        self.assertTrue(
            is_in_category(categories=categories, category_name=category_name)
        )

    def test_is_in_category_not(self):
        categories = [MagicMock(name_utf8="TestCategory", enabled=True, index=3)]
        category_name = "NonExistentCategory"
        self.assertFalse(
            is_in_category(categories=categories, category_name=category_name)
        )

    def test_calculate_inverter_charger_instance(self):
        inverter_charger = MagicMock(
            inverter_instance=MagicMock(instance=2),
            charger_instance=MagicMock(instance=3),
        )
        expected_instance = (2 << 8) | 3
        self.assertEqual(
            calculate_inverter_charger_instance(inverter_charger), expected_instance
        )

    def test_get_associated_circuit(self):
        config = MagicMock()
        config.ui_relationships = [
            MagicMock(
                primary_type=ItemType.DcMeter,
                secondary_type=ItemType.Circuit,
                primary_id=1,
                secondary_id=10,
            )
        ]

        config.hidden_circuit = {10: MagicMock(control_id=20)}
        mock_circuit = MagicMock()
        config.circuit = {20: mock_circuit}

        associated_circuit = get_associated_circuit(ItemType.DcMeter, 1, config)
        self.assertEqual(associated_circuit, mock_circuit)

    def test_get_associated_circuit_no_rel(self):
        config = MagicMock()
        config.ui_relationships = [
            MagicMock(
                primary_type=ItemType.DcMeter,
                secondary_type=ItemType.DcMeter,
                primary_id=1,
                secondary_id=10,
            )
        ]

        config.hidden_circuit = {10: MagicMock(control_id=20)}
        mock_circuit = MagicMock()
        config.circuit = {20: mock_circuit}

        associated_circuit = get_associated_circuit(ItemType.DcMeter, 1, config)
        self.assertIsNone(associated_circuit)

    def test_get_associated_circuit_no_hidden_circuit(self):
        config = MagicMock()
        config.ui_relationships = [
            MagicMock(
                primary_type=ItemType.DcMeter,
                secondary_type=ItemType.Circuit,
                primary_id=1,
                secondary_id=10,
            )
        ]

        config.hidden_circuit = {11: MagicMock(control_id=20)}
        mock_circuit = MagicMock()
        config.circuit = {20: mock_circuit}

        associated_circuit = get_associated_circuit(ItemType.DcMeter, 1, config)
        self.assertIsNone(associated_circuit)

    def test_get_associated_circuit_no_circuit(self):
        config = MagicMock()
        config.ui_relationships = [
            MagicMock(
                primary_type=ItemType.DcMeter,
                secondary_type=ItemType.Circuit,
                primary_id=1,
                secondary_id=10,
            )
        ]

        config.hidden_circuit = {10: MagicMock(control_id=20)}
        mock_circuit = MagicMock()
        config.circuit = {24: mock_circuit}

        associated_circuit = get_associated_circuit(ItemType.DcMeter, 1, config)
        self.assertIsNone(associated_circuit)

    def test_map_fields(self):
        source = {"a": 1, "b": 2}
        target = types.SimpleNamespace()
        field_map = {
            "x": "a",
            "y": "b",
            "z": "c",
        }  # target.x = source["a"], target.y = source["b"]

        map_fields(source, target, field_map)

        self.assertEqual(target.x, 1)
        self.assertEqual(target.y, 2)

    def test_map_enum_fields(self):
        class MyEnum:
            VALUE1 = 1
            VALUE2 = 2

            def __init__(self, value):
                self.value = value

            def __eq__(self, other):
                if isinstance(other, MyEnum):
                    return self.value == other.value
                return self.value == other

        source = {"a": 1, "b": 2}
        target = types.SimpleNamespace()
        field_map = {"x": ("a", MyEnum), "y": ("b", MyEnum)}

        logger = logging.getLogger("test")
        map_enum_fields(logger, source, target, field_map)

        self.assertEqual(target.x, MyEnum(1))
        self.assertEqual(target.y, MyEnum(2))

    def test_map_enum_fields_valueerror(self):
        source = {"a": "1"}  # string, will cause ValueError in MyEnum("1")
        target = types.SimpleNamespace()
        field_map = {"x": ("a", MyEnum)}
        logger = logging.getLogger("test")

        map_enum_fields(logger, source, target, field_map)
        self.assertEqual(target.x, MyEnum(1))  # Should succeed on int("1")

    def test_map_enum_fields_valueerror_both(self):
        class AlwaysFailEnum:
            def __init__(self, value):
                raise ValueError("Always fails")

        source = {"a": "bad"}
        target = types.SimpleNamespace()
        field_map = {"x": ("a", AlwaysFailEnum)}
        logger = MagicMock()

        map_enum_fields(logger, source, target, field_map)
        # The attribute should NOT be set
        self.assertFalse(hasattr(target, "x"))
        # The logger should have been called with a warning
        logger.warning.assert_called_once()

    def test_map_list_fields(self):
        source = {"numbers": [1, 2, 3]}
        target = types.SimpleNamespace()
        field_map = {"squared": ("numbers", lambda x: x * x)}

        map_list_fields(source, target, field_map)

        self.assertEqual(target.squared, [1, 4, 9])

    def test_send_and_validate_response_success(self):
        mock_dbus_command = MagicMock()
        request = {"key": "value"}
        mock_response = '{"Result": "Ok"}'
        mock_dbus_command.return_value = mock_response

        result = send_and_validate_response(mock_dbus_command, request)
        self.assertTrue(result)
        mock_dbus_command.assert_called_once_with('{"key": "value"}')

    def test_send_and_validate_response_fail(self):
        mock_dbus_command = MagicMock()
        request = {"key": "value"}
        mock_response = '{"Result": "Error"}'
        mock_dbus_command.return_value = mock_response

        result = send_and_validate_response(mock_dbus_command, request)
        self.assertFalse(result)
        mock_dbus_command.assert_called_once_with('{"key": "value"}')

    def test_send_and_validate_response_exception(self):
        mock_dbus_command = MagicMock()
        request = {"key": "value"}
        logger = MagicMock()
        with patch("json.loads", side_effect=Exception("fail")):
            result = send_and_validate_response(mock_dbus_command, request, logger)
            self.assertFalse(result)
            logger.error.assert_called_once()
