from .common_enums import ConnectionStatus


class DBUSConnectionStatus:
    """Enum for DBUS connection status."""

    connection_state: ConnectionStatus
    reason: str
    timestamp: int

    def __init__(self, connection_state: ConnectionStatus, reason: str, timestamp: int):
        self.connection_state = connection_state
        self.reason = reason
        self.timestamp = timestamp

    def to_json(self) -> dict:
        return {
            "connection_state": self.connection_state.value,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }
