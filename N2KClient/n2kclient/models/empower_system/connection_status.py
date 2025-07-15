from enum import Enum


class ConnectionStatus(str, Enum):
    UNKNOWN = "Unknown"
    DISCONNECTED = "Disconnected"
    CONNECTED = "Connected"
    LOW_POWER = "LowPower"
    IDLE = "Idle"
