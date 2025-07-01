from typing import Optional
from N2KClient.models.common_enums import ThingType
from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit
from N2KClient.util.state_util import StateUtil
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, Unit
from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState
from N2KClient.models.empower_system.ac_meter import ACMeterThingBase
from reactivex import operators as ops
import reactivex as rx


class ShorePower(ACMeterThingBase):

    def _calc_connection_status(self):
        return (
            ConnectionStatus.CONNECTED
            if StateUtil.any_connected(self.line_status)
            else ConnectionStatus.DISCONNECTED
        )

    def __init__(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
        circuit: Optional[Circuit] = None,
        ic_associated_line: Optional[int] = None,
        component_status: Optional[rx.Observable[dict[str, any]]] = None,
        bls: BinaryLogicState = None,
    ):
        self.line_status = {}
        self.ac_connected_state = rx.subject.BehaviorSubject(
            self._calc_connection_status()
        )
        ACMeterThingBase.__init__(
            self,
            ThingType.SHORE_POWER,
            ac_line1,
            ac_line2,
            ac_line3,
            n2k_devices,
            categories,
            ic_associated_line,
            component_status,
        )

        ######################
        # Component Status
        ######################
        channel = Channel(
            id="connected",
            name="Connected",
            read_only=True,
            type=ChannelType.BOOLEAN,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.shorepower}.connected"],
        )
        self._define_channel(channel)

        if component_status is not None and ic_associated_line is not None:
            # ACMeter is associated to a Inverter/Charger. We should report disconnected if
            # the reported voltage value is invalid. Combi inverter/chargers do not report 0 voltage
            # same way non-Combi inverter/chargers do when shorepower is disconnected
            if ac_line1 is not None:

                def update_line1_status(status: dict[str, any]):
                    self.line_status[1] = status[Constants.state]
                    self.ac_connected_state.on_next(self._calc_connection_status())

                ac_line1_id = (
                    f"{JsonKeys.AC}.{ac_line1.instance.instance}.{ac_line1.line.name}"
                )

                ac_line1_connected_subject = n2k_devices.get_channel_subject(
                    ac_line1_id, JsonKeys.ComponentStatus
                )

                line1_connected = ac_line1_connected_subject.pipe(
                    ops.map(
                        lambda status: (
                            ConnectionStatus.CONNECTED
                            if status == "Connected"
                            else "Disconnected"
                        )
                    ),
                    ops.map(lambda status: StateWithTS(status).to_json()),
                    ops.distinct_until_changed(),
                )
                disposable = line1_connected.subscribe(update_line1_status)
                self._disposable_list.append(disposable)

            if ac_line2 is not None:

                def update_line2_connected(status: dict[str, any]):
                    self.line_status[2] = status[Constants.state]
                    self.ac_connected_state.on_next(self._calc_connection_status())

                ac_line2_id = (
                    f"{JsonKeys.AC}.{ac_line2.instance.instance}.{ac_line2.line.name}"
                )

                ac_line2_connected_subject = n2k_devices.get_channel_subject(
                    ac_line2_id, JsonKeys.ComponentStatus
                )

                line2_connected = ac_line2_connected_subject.pipe(
                    ops.map(
                        lambda status: (
                            ConnectionStatus.CONNECTED
                            if status == "Connected"
                            else "Disconnected"
                        )
                    ),
                    ops.map(lambda status: StateWithTS(status).to_json()),
                    ops.distinct_until_changed(),
                )
                disposable = line2_connected.subscribe(update_line2_connected)
                self._disposable_list.append(disposable)

            if ac_line3 is not None:

                def update_line3_connected(status: dict[str, any]):
                    self.line_status[3] = status[Constants.state]
                    self.ac_connected_state.on_next(self._calc_connection_status())

                ac_line3_id = (
                    f"{JsonKeys.AC}.{ac_line3.instance.instance}.{ac_line3.line.name}"
                )

                ac_line3_connected_subject = n2k_devices.get_channel_subject(
                    ac_line3_id, JsonKeys.ComponentStatus
                )

                line3_connected = ac_line3_connected_subject.pipe(
                    ops.map(
                        lambda status: (
                            ConnectionStatus.CONNECTED
                            if status == "Connected"
                            else "Disconnected"
                        )
                    ),
                    ops.map(lambda status: StateWithTS(status).to_json()),
                    ops.distinct_until_changed(),
                )
                disposable = line3_connected.subscribe(update_line3_connected)
                self._disposable_list.append(disposable)

        else:
            # Report connected if ANY line voltage is greater than 0
            if ac_line1 is not None:

                def update_line1_status(status: dict[str, any]):
                    self.line_status[1] = status[Constants.state]
                    self.ac_connected_state.on_next(self._calc_connection_status())

                ac_line1_id = (
                    f"{JsonKeys.AC}.{ac_line1.instance.instance}.{ac_line1.line.name}"
                )
                ac_line1_Voltage = n2k_devices.get_channel_subject(
                    ac_line1_id, JsonKeys.Voltage
                )
                line1_connected = ac_line1_Voltage.pipe(
                    ops.map(
                        lambda voltage: (
                            ConnectionStatus.CONNECTED
                            if voltage > 0
                            else ConnectionStatus.DISCONNECTED
                        )
                    ),
                    ops.distinct_until_changed(),
                )
                disposable = line1_connected.subscribe(update_line1_status)
                self._disposable_list.append(disposable)

            if ac_line2 is not None:

                def update_line2_connected(status: dict[str, any]):
                    self.line_status[2] = status[Constants.state]
                    self.ac_connected_state.on_next(self._calc_connection_status())

                ac_line2_id = (
                    f"{JsonKeys.AC}.{ac_line2.instance.instance}.{ac_line2.line.name}"
                )
                ac_line2_Voltage = n2k_devices.get_channel_subject(
                    ac_line2_id, JsonKeys.Voltage
                )
                line2_connected = ac_line2_Voltage.pipe(
                    ops.map(
                        lambda voltage: (
                            ConnectionStatus.CONNECTED
                            if voltage > 0
                            else ConnectionStatus.DISCONNECTED
                        )
                    ),
                    ops.distinct_until_changed(),
                )
                disposable = line2_connected.subscribe(update_line2_connected)
                self._disposable_list.append(disposable)

            if ac_line3 is not None:

                def update_line3_connected(status: dict[str, any]):
                    self.line_status[3] = status[Constants.state]
                    self.ac_connected_state.on_next(self._calc_connection_status())

                ac_line3_id = (
                    f"{JsonKeys.AC}.{ac_line3.instance.instance}.{ac_line3.line.name}"
                )
                ac_line3_Voltage = n2k_devices.get_channel_subject(
                    ac_line3_id, JsonKeys.Voltage
                )
                line3_connected = ac_line3_Voltage.pipe(
                    ops.map(
                        lambda voltage: (
                            ConnectionStatus.CONNECTED
                            if voltage > 0
                            else ConnectionStatus.DISCONNECTED
                        )
                    ),
                    ops.distinct_until_changed(),
                )
                disposable = line3_connected.subscribe(update_line3_connected)
                self._disposable_list.append(disposable)

        if bls is not None:
            bls_states_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.BINARY_LOGIC_STATE}.{bls.address}",
                JsonKeys.States,
            )
            bls_connected_state = bls_states_subject.pipe(
                ops.map(
                    lambda state: not StateUtil.get_bls_state(bls.address, state),
                ),
                ops.distinct_until_changed(),
            )

            n2k_devices.set_subscription(
                channel.id, rx.merge(bls_connected_state, self.ac_connected_state)
            )

        if circuit is not None:
            self.circuit = circuit
            ######################
            # Enabled Channel
            ######################
            channel = Channel(
                id="enabled",
                name="Enabled",
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                read_only=circuit.switch_type == 0,
                tags=[
                    f"{Constants.empower}:{Constants.shorepower}.{Constants.enabled}"
                ],
            )
            self._define_channel(channel)
            enabled_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.CIRCUIT}.{circuit.control_id}",
                JsonKeys.Level,
            )
            n2k_devices.set_subscription(
                channel.id,
                enabled_subject.pipe(
                    ops.map(lambda level: level > 0), ops.distinct_until_changed()
                ),
            )
