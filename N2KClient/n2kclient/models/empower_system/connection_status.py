from enum import Enum


class ConnectionStatus(str, Enum):
    """
    Enumeration of connection statuses for N2KDevices, and connection to DBUS host.
    This class defines various states that a connection can be in, such as:
    - UNKNOWN: The connection status is unknown.
    - DISCONNECTED: The connection is not established.
    - CONNECTED: The connection is established.
    - LOW_POWER: The connection is in a low power state.
    - IDLE: The connection is idle, not yet established or actively used.
    """

    UNKNOWN = "Unknown"
    DISCONNECTED = "Disconnected"
    CONNECTED = "Connected"
    LOW_POWER = "LowPower"
    IDLE = "Idle"
