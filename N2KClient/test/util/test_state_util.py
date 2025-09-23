"""
test_state_util.py
"""

import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.util.state_util import StateUtil
from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus


# pylint: disable=too-few-public-methods
class TestValid:
    """
    Helper class for the is_valid function
    """

    Valid = None

    def __init__(self, valid) -> None:
        # pylint: disable=invalid-name
        self.Valid = valid


class TestClass:
    """
    Helper class for the is valid function
    """

    valid_class = TestValid(True)
    invalid_class = TestValid(False)

    def __init__(self):
        """
        Constructor to set the is valid class
        """


class StateUtilTest(unittest.TestCase):
    """
    Class to test the functionality of the StateUtil
    object in state_util.py
    """

    def test_any_valid_empty_values(self):
        """
        Test case where empty values are passed in to both parameters
        """
        self.assertEqual(StateUtil.any_valid([], []), ConnectionStatus.DISCONNECTED)

    def test_any_valid_populated_values_none_matching(self):
        """
        Test case where values are passed in, but are not valid
        with no matching parameter
        """
        values = TestClass()
        attributes_to_check = ["not", "real", "values"]
        self.assertEqual(
            StateUtil.any_valid(values, attributes_to_check),
            ConnectionStatus.DISCONNECTED,
        )

    def test_any_valid_populated_values_invalid(self):
        """
        Test case where values are passed in, but are not valid with
        a matching parameter
        """
        values = TestClass()
        attributes_to_check = ["invalid_class"]
        self.assertEqual(
            StateUtil.any_valid(values, attributes_to_check),
            ConnectionStatus.DISCONNECTED,
        )

    def test_any_valid_populated_values_valid(self):
        """
        Test case where values are passed in, and are valid
        """
        values = TestClass()
        attributes_to_check = ["valid_class"]
        self.assertEqual(
            StateUtil.any_valid(values, attributes_to_check), ConnectionStatus.CONNECTED
        )

    def test_any_non_empty_none(self):
        """
        Test case where any_non_empty has all empty
        values
        """
        self.assertEqual(
            StateUtil.any_non_empty(TestValid(None), ["Valid"]),
            ConnectionStatus.DISCONNECTED,
        )

    def test_any_non_empty_populated(self):
        """
        Test case where any_non_empty has a non empty value
        """
        self.assertEqual(
            StateUtil.any_non_empty(TestValid(True), ["Valid"]),
            ConnectionStatus.CONNECTED,
        )

    def test_any_true(self):
        """
        Test case where any_true has a true value
        """
        self.assertTrue(StateUtil.any_true({"one": False, "two": True, "three": False}))

    def test_any_false(self):
        """
        Test case where any_true has a false value
        """
        self.assertFalse(
            StateUtil.any_true({"one": False, "two": False, "three": False})
        )

    def test_any_valid_bool(self):
        """
        Test case where any_valid_bool has a true value in an object with Valid property
        """

        class BoolAttr:
            def __init__(self, valid):
                self.Valid = valid

        class BoolAttrs:
            one = BoolAttr(False)
            two = BoolAttr(False)
            three = BoolAttr(False)

        self.assertFalse(StateUtil.any_valid_bool(BoolAttrs(), ["one", "two", "three"]))

    def test_any_valid_bool(self):
        """
        Test case where any_valid_bool has a true value in an object with Valid property
        """

        class BoolAttr:
            def __init__(self, valid):
                self.Valid = valid

        class BoolAttrs:
            one = BoolAttr(False)
            two = BoolAttr(True)
            three = BoolAttr(False)

        self.assertTrue(StateUtil.any_valid_bool(BoolAttrs(), ["one", "two", "three"]))

    def test_is_circuit_connected(self):
        """
        Test case where is_circuit_connected has a true value
        """
        self.assertEqual(
            StateUtil.is_circuit_connected(True),
            ConnectionStatus.DISCONNECTED,
        )

    def test_is_circuit_connected_false(self):
        """
        Test case where is_circuit_connected has a false value
        """
        self.assertEqual(
            StateUtil.is_circuit_connected(False),
            ConnectionStatus.CONNECTED,
        )


if __name__ == "__main__":
    unittest.main()
