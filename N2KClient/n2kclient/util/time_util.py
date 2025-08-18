from datetime import datetime, timezone


class TimeUtil:
    @staticmethod
    def current_time():
        """
        Get the current time in milliseconds since epoch.
        Returns:
            int: Current time in milliseconds since epoch.
        """
        return int(datetime.now(timezone.utc).timestamp() * 1000)
