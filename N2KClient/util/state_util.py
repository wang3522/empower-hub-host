from N2KClient.models.constants import JsonKeys
from N2KClient.models.empower_system.connection_status import ConnectionStatus


class StateUtil:

    @staticmethod
    def any_connected(connection_status: dict[int, ConnectionStatus]):
        """
        Check if any of the ConnectionStatus in dictionary are CONNECTED

        Parameters:
        values (object): The dict of ConnectionStatus to check the value of.

        Returns:
        True if any attribute is CONNECTED, otherwise False.
        """
        any_connected = False
        for status in connection_status.values():
            if status == ConnectionStatus.CONNECTED:
                any_connected = True
        return any_connected

    @staticmethod
    def any_true(bools: dict[int, bool]):
        """
        Check if any of the specified attributes in 'bools' are True.

        Parameters:
        bools (object): The dict of booleans to check value of
        Returns:
        True if any attribute is True, otherwise False.
        """
        any_connected = False
        for status in bools.values():
            if status:
                any_connected = True
        return any_connected

    @staticmethod
    def any_valid(values, attributes_to_check):
        """
        Check if any of the specified attributes in 'values' are valid.

        Parameters:
        values (object): The object to check the attributes of.
        attributes_to_check (list): A list of attribute names to check.

        Returns:
        ConnectionStatus.CONNECTED if any attribute is valid, otherwise ConnectionStatus.DISCONNECTED.
        """
        for attr in attributes_to_check:
            value = getattr(values, attr, None)
            if value and getattr(value, "Valid", False):
                return ConnectionStatus.CONNECTED
        return ConnectionStatus.DISCONNECTED

    @staticmethod
    def any_valid_bool(values, attributes_to_check):
        """
        Check if any of the specified attributes in 'values' are valid.

        Parameters:
        values (object): The object to check the attributes of.
        attributes_to_check (list): A list of attribute names to check.

        Returns:
        True if any attribute is valid, otherwise False.
        """
        for attr in attributes_to_check:
            value = getattr(values, attr, None)
            if value and getattr(value, "Valid", False):
                return True
        return False

    @staticmethod
    def any_non_empty(state, fields):
        """
        Check if any of the specified fields in 'state' are non-empty.

        Parameters:
        state (object): The object to check the fields of.
        fields (list): A list of field names to check.

        Returns:
        ConnectionStatus.CONNECTED if any field is non-empty, otherwise ConnectionStatus.DISCONNECTED.
        """
        return (
            ConnectionStatus.CONNECTED
            if any(getattr(state, field, None) for field in fields)
            else ConnectionStatus.DISCONNECTED
        )

    @staticmethod
    def get_bls_state(address, bls_state: dict[str, any]):
        """
        Get the state of the BLS.

        Parameters:
        address (int): The address of the BLS.
        bls_state (nmea2k.BinaryLogicState): The BLS state message.

        Returns:
            bool: True if the state matches, False otherwise.
        """
        dipswitch = (address >> 8) & 0xFF
        instance = (address & 0xFF) >> 5
        valueIndex = address & 0x1F

        if (
            bls_state[JsonKeys.INSTANCE] == instance
            and bls_state[JsonKeys.DIPSWITCH] == dipswitch
        ):
            return (bls_state[JsonKeys.States][JsonKeys.VALUE] & (1 << valueIndex)) > 0

        return False

    @staticmethod
    def is_circuit_connected(isOffline: bool):
        """
        Get the connection status of circuit from isOffline attribute.

        Disconnected if True, False otherwise
        """
        if isOffline:
            return ConnectionStatus.DISCONNECTED
        else:
            return ConnectionStatus.CONNECTED
