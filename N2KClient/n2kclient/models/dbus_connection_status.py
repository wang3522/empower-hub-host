from .common_enums import ConnectionStatus


class DBUSConnectionStatus:
    """
    Represents the status of a DBUS connection.
    Attributes:
        connection_state (ConnectionStatus): The current state of the connection.
        reason (str): Reason for the current connection state.
        timestamp (int): Timestamp of the status update.
    Methods:
        to_json: Converts the DBUSConnectionStatus object to a JSON-serializable dictionary.
    """

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
