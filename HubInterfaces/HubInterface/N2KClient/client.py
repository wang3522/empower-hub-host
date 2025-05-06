import logging
from typing import Any, List
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service
import reactivex as rx
import json

from models.state import N2KChannel, N2KState
from reactivex import operators as ops
from gi.repository import GLib

logger = logging.getLogger(__name__)


class N2KClient(dbus.service.Object):
    state: rx.Observable[N2KState]
    # constants?
    n2k_dbus_inteface = "org.navico.CZoneCpp"
    n2k_dbus_monitor_signal_name = "n2kMonitor"
    n2k_dbus_control_signal_name = "n2kControl"
    n2k_dbus_path = "/org/navico/CZoneCpp"

    _disposable_list: List[rx.abc.DisposableBase]

    def __init__(self):
        self._logger = logging.getLogger("N2KClient")
        self._latest_state = None
        self._disposable_list = []
        self._factory_metadata = rx.Subject()
        self._snapshot = rx.Subject()

        self.state = self._snapshot.pipe(
            ops.scan(self.__merge_state, N2KState()), ops.publish(), ops.ref_count()
        )
        self.factory_metadata = self._factory_metadata.pipe(
            ops.publish(), ops.ref_count()
        )

        self._disposable_list = []

        bus = dbus.SystemBus()

        bus.add_signal_receiver(
            self.n2k_signal_handler,
            signal_name=self.n2k_dbus_monitor_signal_name,
            dbus_interface=self.n2k_dbus_inteface,
            path=self.n2k_dbus_path,
        )

        def update_latest_state(state: N2KState):
            self._latest_state = state

        self._disposable_list.append(self.state.subscribe(update_latest_state))

    def __del__(self):
        if self._disposable_list is not None:
            for disposable in self._disposable_list:
                disposable.dispose()
            self._disposable_list = []

    def n2k_signal_handler(self, n2k_state):
        print("Received signal", n2k_state)

        state_obj = json.loads(n2k_state)
        self._snapshot.on_next(state_obj)

    def __merge_state(self, state: N2KState, snapshot: Any):
        state[snapshot["id"]] = state
