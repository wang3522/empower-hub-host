import threading
from reactivex.subject import BehaviorSubject
from n2k_client.models.constants import Constants
from n2k_client.util.setting_util import SettingsUtil
from modules.common.tb_constants import TBConstants

# Idle Timer Increments in seconds
IDLE_TIMER_INCREMENTS = SettingsUtil.get_setting(
    Constants.GNSS, TBConstants.IDLE, TBConstants.INCREMENTS, default_value=60
)


class GeoStatus:
    _idle_thread_timer_name = "GeoStatus Idle Timer"

    def __init__(self):
        # Indicates whether the boat is idle (True) or not (False)
        self._is_idle = BehaviorSubject(True)  # Default value is True (idle)

        # Tracks how long the boat has been idle (in minutes)
        self._idle_since = BehaviorSubject(0)  # Default value is 0 minutes

        # Timer to increment the idle_since value every minute
        self._idle_timer = None

        # Subscribe to changes in is_idle
        self._is_idle.subscribe(self._start_idle_timer())

        # Start the idle timer immediately since the boat is idle by default
        self._start_idle_timer()

    def __del__(self):
        self._stop_idle_timer()

    @property
    def is_idle(self):
        return self._is_idle.value

    @is_idle.setter
    def is_idle(self, value: bool):
        if self._is_idle.value:
            self._is_idle.on_next(value)
        else:
            self._is_idle.on_next(value)
            self._start_idle_timer()

    @property
    def idle_since(self):
        return self._idle_since.value

    @idle_since.setter
    def idle_since(self, value: int):
        self._idle_since.on_next(value)

    def _start_idle_timer(self):
        """
        Starts the idle timer and resets idle_since to 0.
        """
        if self._idle_timer is not None:
            if self._is_idle.value:
                return  # Timer is already running
            else:
                # stop and reset the timer
                self._stop_idle_timer()

        self._idle_since.on_next(0)  # Reset idle_since to 0
        self._idle_timer = threading.Timer(
            IDLE_TIMER_INCREMENTS, self._increment_idle_since
        )
        self._idle_timer.start()

    def _stop_idle_timer(self):
        """
        Stops the idle timer.
        """
        if self._idle_timer is not None:
            self._idle_timer.cancel()
            self._idle_timer = None

    def _increment_idle_since(self):
        """
        Increments the idle_since value by 1 and restarts the idle timer.
        """
        self._idle_since.on_next(self._idle_since.value + 1)
        self._idle_timer = threading.Timer(
            IDLE_TIMER_INCREMENTS, self._increment_idle_since
        )
        self._idle_timer.name = self._idle_thread_timer_name

        self._idle_timer.start()  # Restart the timer

    def subscribe_to_is_idle(self, observer):
        """
        Allows external observers to subscribe to changes in the is_idle attribute.
        """
        return self._is_idle.subscribe(observer)

    def subscribe_to_idle_since(self, observer):
        """
        Allows external observers to subscribe to changes in the idle_since attribute.
        """
        return self._idle_since.subscribe(observer)
