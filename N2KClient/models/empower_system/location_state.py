from datetime import datetime, timezone
from typing import Any
from ..constants import Constants
from ...util.time_util import TimeUtil


class LocationState:
    lat: float
    long: float
    sp: float
    ts: int

    def __init__(self, lat, long, sp):
        # Set the timestamp to the current time in UTC
        self.lat = lat
        self.long = long
        self.sp = sp
        self.ts = TimeUtil.current_time()

    def to_json(self):
        """
        Converts the LocationState object to a JSON-compatible dictionary.

        Returns:
            dict: A dictionary representation of the LocationState object.
        """
        return {
            Constants.ts: self.ts,
            Constants.lat: self.lat,
            Constants.long: self.long,
            Constants.sp: self.sp,
        }
