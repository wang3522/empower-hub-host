from typing import Optional
from ..common_enums import ThingType
from ..devices import N2kDevices
from ..empower_system.connection_status import ConnectionStatus
from ..empower_system.state_ts import StateWithTS
from ..n2k_configuration.ac import AC
from ..n2k_configuration.circuit import Circuit
from ...util.state_util import StateUtil
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, Unit
from ..n2k_configuration.binary_logic_state import BinaryLogicState
from .ac_meter import ACMeterThingBase
from reactivex import operators as ops
import reactivex as rx
from ..common_enums import (
    N2kDeviceType,
    ACMeterStates,
    BLSStates,
    CircuitStates,
)


class ShorePower(ACMeterThingBase):
    """
    Represents a shore power device in the Empower system.

    Handles the creation and management of shore power-related channels (connected, enabled),
    and integrates with N2kDevices and RxPy for real-time updates. Supports both inverter/charger and non-inverter/charger configurations.

    Connected state is determined based on the voltage of the AC lines or the component status of an associated inverter/charger, (if present).
    BLS or Signal input can be used to determine the connected state as well. The values from BLS are inverted to match the expected state, and merged with previously defined connected state.

    Methods:
        _calc_shorepower_connected: Calculates whether any shore power line is connected using external utility.
        __init__: Initializes the ShorePower with AC line configurations, N2kDevices, categories, circuit, ic_associated_line, component_status, and an optional BinaryLogicState.
        define_shorepower_connected_pipe_inverter_charger: Defines the logic for determining shore power connection when associated with an inverter/charger.
        define_shorepower_connected_pipe_non_inverter_charger: Defines the logic for determining shore power connection when not associated with an inverter/charger.
        define_shorepower_connected_channel: Defines the connected channel for the shore power device.
        define_shorepower_enabled_channel: Defines the enabled channel for the shore power device.
    """

    def _calc_shorepower_connected(self):
        """
        Calculate whether any shore power line is connected using external utility.

        Returns:
            bool: True if any line is connected, otherwise False.
        """
        return StateUtil.any_connected(self.line_connected)

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
        """
        Initialize the ShorePower thing and set up all relevant shore power channels.

        Args:
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            categories (list[str], optional): List of categories for this shore power device.
            circuit (Optional[Circuit]): Associated circuit for this shore power device, if any.
            ic_associated_line (Optional[int]): Line number associated with an integrated component (if any).
            component_status (Optional[rx.Observable[dict[str, any]]]): Observable for integrated component status (if any).
            bls (BinaryLogicState, optional): Associated binary logic state, if any.
        """
        self.line_connected = {}
        self.ac_connected_state = rx.subject.BehaviorSubject(None)
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

        self.ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"
        if circuit is not None:
            self.circuit = circuit
            self.define_shorepower_enabled_channel(circuit, n2k_devices)
        self.define_shorepower_connected_channel(
            ac_line1,
            ac_line2,
            ac_line3,
            n2k_devices,
            ic_associated_line,
            component_status,
            bls,
        )

    def define_shorepower_connected_pipe_inverter_charger(
        self, n2k_devices: N2kDevices, ac_line1: AC, ac_line2: AC, ac_line3: AC
    ):
        """
        Define the logic for determining shore power connection when associated with an inverter/charger.

        ACMeter is associated to a Inverter/Charger. We should report disconnected if
        the reported voltage value is invalid. Combi inverter/chargers do not report 0 voltage
        same way non-Combi inverter/chargers do when shorepower is disconnected

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
        """
        if ac_line1 is not None:

            def update_line1_status(status: ConnectionStatus):
                self.line_connected[1] = status
                self.ac_connected_state.on_next(self._calc_shorepower_connected())

            ac_line1_connected_subject = n2k_devices.get_channel_subject(
                self.ac_id,
                f"{ACMeterStates.ComponentStatus.value}.{1}",
                N2kDeviceType.AC,
            )

            line1_connected = ac_line1_connected_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(
                    lambda status: (
                        ConnectionStatus.CONNECTED
                        if status == "Connected"
                        else ConnectionStatus.DISCONNECTED
                    )
                ),
                ops.distinct_until_changed(),
            )
            self._disposable_list.append(line1_connected.subscribe(update_line1_status))

        if ac_line2 is not None:

            def update_line2_connected(status: ConnectionStatus):
                self.line_connected[2] = status
                self.ac_connected_state.on_next(self._calc_shorepower_connected())

            ac_line2_connected_subject = n2k_devices.get_channel_subject(
                self.ac_id,
                f"{ACMeterStates.ComponentStatus.value}.{2}",
                N2kDeviceType.AC,
            )

            line2_connected = ac_line2_connected_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(
                    lambda status: (
                        ConnectionStatus.CONNECTED
                        if status == "Connected"
                        else ConnectionStatus.DISCONNECTED
                    )
                ),
                ops.distinct_until_changed(),
            )
            self._disposable_list.append(
                line2_connected.subscribe(update_line2_connected)
            )

        if ac_line3 is not None:

            def update_line3_connected(status: ConnectionStatus):
                self.line_connected[3] = status
                self.ac_connected_state.on_next(self._calc_shorepower_connected())

            ac_line3_connected_subject = n2k_devices.get_channel_subject(
                self.ac_id,
                f"{ACMeterStates.ComponentStatus.value}.{3}",
                N2kDeviceType.AC,
            )

            line3_connected = ac_line3_connected_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(
                    lambda status: (
                        ConnectionStatus.CONNECTED
                        if status == "Connected"
                        else ConnectionStatus.DISCONNECTED
                    )
                ),
                ops.distinct_until_changed(),
            )

            self._disposable_list.append(
                line3_connected.subscribe(update_line3_connected)
            )

    def define_shorepower_connected_pipe_non_inverter_charger(
        self, n2k_devices: N2kDevices, ac_line1: AC, ac_line2: AC, ac_line3: AC
    ):
        """
        Define the logic for determining shore power connection when not associated with an inverter/charger.
        The connected state is determined by the voltage of the AC lines.
        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
        """
        # Report connected if ANY line voltage is greater than 0
        if ac_line1 is not None:

            def update_line1_status(status: ConnectionStatus):
                self.line_connected[1] = status
                self.ac_connected_state.on_next(self._calc_shorepower_connected())

            ac_line1_Voltage = n2k_devices.get_channel_subject(
                self.ac_id, f"{ACMeterStates.Voltage.value}.{1}", N2kDeviceType.AC
            )
            line1_connected = ac_line1_Voltage.pipe(
                ops.filter(lambda voltage: voltage is not None),
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

            def update_line2_connected(status: ConnectionStatus):
                self.line_connected[2] = status
                self.ac_connected_state.on_next(self._calc_shorepower_connected())

            ac_line2_Voltage = n2k_devices.get_channel_subject(
                self.ac_id, f"{ACMeterStates.Voltage.value}.{2}", N2kDeviceType.AC
            )
            line2_connected = ac_line2_Voltage.pipe(
                ops.filter(lambda voltage: voltage is not None),
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

            def update_line3_connected(status: ConnectionStatus):
                self.line_connected[3] = status
                self.ac_connected_state.on_next(self._calc_shorepower_connected())

            ac_line3_Voltage = n2k_devices.get_channel_subject(
                self.ac_id, f"{ACMeterStates.Voltage.value}.{3}", N2kDeviceType.AC
            )
            line3_connected = ac_line3_Voltage.pipe(
                ops.filter(lambda voltage: voltage is not None),
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

    def define_shorepower_connected_channel(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        ic_associated_line: Optional[int] = None,
        component_status: Optional[rx.Observable[dict[str, any]]] = None,
        bls: Optional[BinaryLogicState] = None,
    ):
        """
        Define the connected channel for the shore power device.

        Determines the connected state based on the voltage of the AC lines or the component status of an associated inverter/charger, if present.
        If an inverter/charger is associated, the connected state is determined by the inverter/charger's component status.
        If no inverter/charger is associated, the connected state is determined by the voltage of the AC lines.
        If a Binary Logic State (BLS) is provided, it is used to determine the connected state, with the values inverted to match the expected state.

        Args:
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            ic_associated_line (Optional[int]): Line number associated with an integrated component (if any).
            component_status (Optional[rx.Observable[dict[str, any]]]): Observable for integrated component status (if any).
            bls (Optional[BinaryLogicState]): Associated binary logic state, if any.
        """
        ######################
        # Connected Channel
        ######################
        channel = Channel(
            id="connected",
            name="Connected",
            read_only=True,
            type=ChannelType.BOOLEAN,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.shorepower}.connected"],
        )

        if component_status is not None and ic_associated_line is not None:
            self.define_shorepower_connected_pipe_inverter_charger(
                n2k_devices, ac_line1, ac_line2, ac_line3
            )
        else:
            self.define_shorepower_connected_pipe_non_inverter_charger(
                n2k_devices, ac_line1, ac_line2, ac_line3
            )
        connected_state = self.ac_connected_state.pipe(
            ops.filter(lambda state: state is not None)
        )
        if bls is not None:
            bls_states_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.BINARY_LOGIC_STATE}.{bls.address}",
                BLSStates.States.value,
                N2kDeviceType.BINARY_LOGIC_STATE,
            )
            bls_connected_state = bls_states_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(
                    lambda state: not StateUtil.get_bls_state(bls.address, state),
                ),
                ops.distinct_until_changed(),
            )

            connected_state = rx.merge(bls_connected_state, self.ac_connected_state)
        n2k_devices.set_subscription(self._define_channel(channel), connected_state)

    def define_shorepower_enabled_channel(
        self,
        circuit: Optional[Circuit],
        n2k_devices: N2kDevices,
    ):
        """
        Define the enabled channel for the shore power device.

        Args:
            circuit (Optional[Circuit]): Associated circuit for this shore power device, if any.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """
        ######################
        # Enabled Channel
        ######################
        channel = Channel(
            id="enabled",
            name="Enabled",
            type=ChannelType.BOOLEAN,
            unit=Unit.NONE,
            read_only=circuit.switch_type == 0,
            tags=[f"{Constants.empower}:{Constants.shorepower}.{Constants.enabled}"],
        )
        enabled_subject = n2k_devices.get_channel_subject(
            f"{JsonKeys.CIRCUITS}.{circuit.id.value}",
            CircuitStates.Level.value,
            N2kDeviceType.CIRCUIT,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            enabled_subject.pipe(
                ops.map(lambda level: level > 0), ops.distinct_until_changed()
            ),
        )
