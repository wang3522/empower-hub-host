from datetime import datetime, timezone


class TimeUtil:
    @staticmethod
    def current_time():
        return int(datetime.now(timezone.utc).timestamp() * 1000)
