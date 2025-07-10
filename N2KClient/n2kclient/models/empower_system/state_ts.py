from typing import Any

from ..constants import Constants
from ...util.time_util import TimeUtil


class StateWithTS:
    """
    Represents a state object with a timestamp.

    Attributes:
        ts (int): The timestamp of the state.
        state (Any): The state object.
    """

    ts: int
    state: Any

    def __init__(self, state: Any, timestamp=None):
        # Set the timestamp to the current time in UTC
        self.ts = TimeUtil.current_time() if timestamp is None else timestamp
        self.state = state

    def to_json(self):
        """
        Converts the StateWithTS object to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the StateWithTS object.
        """
        return {Constants.ts: self.ts, Constants.state: self.state}
