from datetime import datetime, timezone
from typing import Any
from ..constants import Constants
from ...util.time_util import TimeUtil


class LocationState:
    """
    Represents the state of a location with latitude, longitude, speed, and timestamp.
    This class is used to encapsulate the location data, including the latitude, longitude,
    speed, and the timestamp of when the location was recorded.
    Attributes:
        lat (float): The latitude of the location.
        long (float): The longitude of the location.
        sp (float): The speed at the location.
        ts (int): The timestamp when the location was recorded, in UTC.
    Methods:
        __init__: Initializes the LocationState with latitude, longitude, and speed.
        to_json: Converts the LocationState object to a JSON-compatible dictionary.
    """

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
