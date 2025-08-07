from typing import Optional
from reactivex import operators as ops
import reactivex as rx

from .state_ts import StateWithTS
from .thing import Thing
from ..n2k_configuration.ac import AC
from ..n2k_configuration.circuit import Circuit, SwitchType
from ..common_enums import ThingType, Unit
from .channel import Channel, ChannelType
from ..constants import Constants, JsonKeys, LINE_CONST_MAP
from ..n2k_configuration.inverter_charger import InverterChargerDevice
from ..devices import N2kDevices
from ...util import rx as rxu
from ..filters import Current, Voltage, Frequency, Power
from .connection_status import ConnectionStatus
from ...util.state_util import StateUtil
from ..common_enums import (
    N2kDeviceType,
    ACMeterStates,
    CircuitStates,
    CombiInverterStates,
    InverterStatus,
)

INVERTER_STATE_MAPPING = {
    InverterStatus.INVERTING: "inverting",
    InverterStatus.AC_PASSTHRU: "acPassthrough",
    InverterStatus.LOAD_SENSE: "loadSense",
    InverterStatus.FAULT: "fault",
    InverterStatus.DISABLED: "disabled",
    InverterStatus.CHARGING: "charging",
    InverterStatus.ENERGY_SAVING: "energySaving",
    InverterStatus.ENERGY_SAVING2: "energySaving",
    InverterStatus.SUPPORTING: "supporting",
    InverterStatus.SUPPORTING2: "supporting",
    InverterStatus.ERROR: "error",
    InverterStatus.DATA_NOT_AVAILABLE: "unknown",
}


def map_inverter_state(state: str) -> str:
    """
    Maps the inverter state from the N2K JSON keys to a more readable format.
    """
    try:
        enum_state = InverterStatus(state)
        return INVERTER_STATE_MAPPING.get(enum_state, "unknown")
    except ValueError:
        return "unknown"


class InverterBase(Thing):
    """
    Base class for inverter devices in the Empower system.

    Handles the creation and management of AC line channels, component status, and inverter state.
    Integrates with N2kDevices and RxPy for real-time updates.
    """

    ac_line1: Optional[AC] = None
    ac_line2: Optional[AC] = None
    ac_line3: Optional[AC] = None

    def _calc_connection_status(self):
        """
        Calculate the overall connection status for the inverter based on the status of all lines.

        Returns:
            ConnectionStatus: CONNECTED if any line is connected, otherwise DISCONNECTED.
        """
        return (
            ConnectionStatus.CONNECTED
            if StateUtil.any_connected(self.line_status)
            else ConnectionStatus.DISCONNECTED
        )

    def __init__(
        self,
        id: str,
        name: str,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
        status_ac_line: int,
        inverter_component_status: Optional[rx.Observable] = None,
        n2k_devices: Optional[N2kDevices] = None,
    ):
        """
        Initialize the InverterBase and set up all relevant AC line channels and component status.

        Args:
            id (str): The unique id for this inverter.
            name (str): Human-readable name for this inverter.
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            categories (list[str]): List of categories for this inverter.
            status_ac_line (int): The AC line number associated with the main status.
            inverter_component_status (Optional[rx.Observable]): Observable for component status, if any.
            n2k_devices (Optional[N2kDevices]): The N2K device manager for channel subjects and subscriptions.
        """
        self.line_status = {}
        self.connection_status_subject = rx.subject.BehaviorSubject(
            self._calc_connection_status()
        )
        Thing.__init__(
            self,
            type=ThingType.INVERTER,
            id=id,
            name=name,
            categories=categories,
            links=[],
        )

        self.ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"

        self.define_inverter_ac_lines(
            n2k_devices,
            status_ac_line,
            ac_line1,
            ac_line2,
            ac_line3,
            inverter_component_status,
        )

        self.define_component_status_channel(
            status_ac_line, n2k_devices, inverter_component_status
        )

    def define_inverter_ac_lines(
        self,
        n2k_devices: N2kDevices,
        status_ac_line: int,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        inverter_component_status: Optional[rx.Observable] = None,
    ):
        """
        Define all AC line channels for the inverter.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            status_ac_line (int): The AC line number associated with the main status.
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            inverter_component_status (Optional[rx.Observable]): Observable for component status, if any.
        """
        if ac_line1 is not None:
            self.define_inverter_ac_line_channels(
                1,
                n2k_devices,
                inverter_component_status,
                status_ac_line,
            )
        if ac_line2 is not None:
            self.define_inverter_ac_line_channels(
                2,
                n2k_devices,
                inverter_component_status,
                status_ac_line,
            )
        if ac_line3 is not None:
            self.define_inverter_ac_line_channels(
                3,
                n2k_devices,
                inverter_component_status,
                status_ac_line,
            )

    def define_inverter_ac_line_channels(
        self,
        line_number: int,
        n2k_devices: N2kDevices,
        inverter_component_status: Optional[rx.Observable],
        status_ac_line: int,
    ):
        """
        Define all channels for a single AC line (component status, voltage, current, frequency, power).

        Args:
            line_number (int): The AC line number (1, 2, or 3).
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            inverter_component_status (Optional[rx.Observable]): Observable for component status, overrides the status of status_ac_line.
            status_ac_line (int): The AC line number associated with component status.
        """
        line_const = LINE_CONST_MAP.get(line_number)

        def update_line_status(status: dict[str, any]):
            self.line_status[line_number] = status[Constants.state]
            self.connection_status_subject.on_next(self._calc_connection_status())

        ##############################
        # Line Component Status
        ##############################
        channel = Channel(
            id=f"l{line_number}cs",
            name=f"Line {line_number} Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.inverter}.{line_const}.{Constants.componentStatus}"
            ],
        )

        if inverter_component_status is not None and status_ac_line == line_number:
            line_component_status = inverter_component_status
        else:
            ac_component_status_subject = n2k_devices.get_channel_subject(
                self.ac_id,
                f"{ACMeterStates.ComponentStatus.value}.{line_number}",
                N2kDeviceType.AC,
            )
            line_component_status = ac_component_status_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(
                    lambda status: (
                        ConnectionStatus.CONNECTED
                        if status == "Connected"
                        else ConnectionStatus.DISCONNECTED
                    )
                ),
                ops.map(lambda status: StateWithTS(status).to_json()),
                ops.distinct_until_changed(lambda state: state[Constants.state]),
            )

        line_component_status_disposable = line_component_status.subscribe(
            update_line_status
        )

        self._disposable_list.append(line_component_status_disposable)

        n2k_devices.set_subscription(
            self._define_channel(channel), line_component_status
        )

        #######################
        # Line Voltage
        #######################
        channel = Channel(
            id=f"l{line_number}v",
            name=f"Line {line_number} Voltage",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_VOLT,
            tags=[
                f"{Constants.empower}:{Constants.inverter}.{line_const}.{Constants.voltage}"
            ],
        )

        ac_voltage_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Voltage.value}.{line_number}", N2kDeviceType.AC
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            ac_voltage_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Voltage.ROUND_VALUE),
                Voltage.FILTER,
            ),
        )

        #######################
        # Line 1 Current
        #######################
        channel = Channel(
            id=f"l{line_number}c",
            name=f"Line {line_number} Current",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_AMP,
            tags=[
                f"{Constants.empower}:{Constants.inverter}.{line_const}.{Constants.current}"
            ],
        )
        ac_current_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Current.value}.{line_number}", N2kDeviceType.AC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            ac_current_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Current.ROUND_VALUE),
                Current.FILTER,
            ),
        )

        #######################
        # Line Frequency
        #######################
        channel = Channel(
            id=f"l{line_number}f",
            name=f"Line {line_number} Frequency",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.FREQUENCY_HERTZ,
            tags=[
                f"{Constants.empower}:{Constants.inverter}.{line_const}.{Constants.frequency}"
            ],
        )
        ac_frequency_subject = n2k_devices.get_channel_subject(
            self.ac_id,
            f"{ACMeterStates.Frequency.value}.{line_number}",
            N2kDeviceType.AC,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            ac_frequency_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Frequency.ROUND_VALUE),
                Frequency.FILTER,
            ),
        )

        #######################
        # Line Power
        #######################
        channel = Channel(
            id=f"l{line_number}p",
            name=f"Line {line_number} Power",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_WATT,
            tags=[
                f"{Constants.empower}:{Constants.inverter}.{line_const}.{Constants.power}"
            ],
        )
        ac_power_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Power.value}.{line_number}", N2kDeviceType.AC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            ac_power_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Power.ROUND_VALUE),
                Power.FILTER,
            ),
        )

    def define_component_status_channel(
        self,
        status_ac_line: int,
        n2k_devices: N2kDevices,
        inverter_component_status: Optional[rx.Observable],
    ):
        """
        Define the component status channel for the inverter if inverter_component_status is not provided.

        Args:
            status_ac_line (int): The AC line number associated with the main status.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            inverter_component_status (Optional[rx.Observable]): Observable for component status, if any.
        """
        if inverter_component_status is None and status_ac_line is None:
            channel = Channel(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.componentStatus}"
                ],
            )

            component_status = self.connection_status_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda status: StateWithTS(status).to_json()),
                ops.distinct_until_changed(lambda state: state[Constants.state]),
            )

            n2k_devices.set_subscription(
                self._define_channel(channel), component_status
            )


class AcMeterInverter(InverterBase):
    """
    Represents an AC meter inverter device in the Empower system.

    Handles the creation and management of AC line channels, inverter state, and enable channels.
    Integrates with N2kDevices and RxPy for real-time updates.
    """

    def _calc_inverter_state(self) -> str:
        """
        Calculate the overall inverter state based on the connection status of all lines.

        Returns:
            str: "inverting" if any line is connected, otherwise "disabled".
        """
        return "inverting" if StateUtil.any_true(self.line_connected) else "disabled"

    def __init__(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        categories: list[str],
        circuit: Circuit,
    ):
        """
        Initialize the AcMeterInverter and set up all relevant AC line channels, inverter state, and enable channels.

        Args:
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            categories (list[str]): List of categories for this inverter.
            circuit (Circuit): Associated circuit for this inverter.
        """
        self.line_connected = {}
        self.inverter_state_subject = rx.subject.BehaviorSubject(
            self._calc_inverter_state
        )

        if circuit is not None:
            self.inverter_circuit_id = circuit.id.value
            self.inverter_circuit_control_id = circuit.control_id
        InverterBase.__init__(
            self,
            id=ac_line1.instance.instance,
            name=ac_line1.name_utf8,
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
        )

        self.define_acmeter_inverter_channels(
            ac_line1, ac_line2, ac_line3, n2k_devices, circuit
        )

    def define_acmeter_inverter_channels(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        circuit: Optional[Circuit] = None,
    ):
        """
        Define all AC meter inverter channels (state and enable).

        Args:
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            circuit (Optional[Circuit]): Associated circuit for this inverter, if any.
        """
        self.define_acmeter_inverter_state_channel(
            ac_line1, ac_line2, ac_line3, n2k_devices
        )
        self.define_inverter_enable_channel(circuit=circuit, n2k_devices=n2k_devices)

    def define_acmeter_inverter_state_channel(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
    ):
        """
        Define the inverter state channel for the AcMeterInverter and manage line connection state.

        Args:
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """
        ###################################
        # Inverter State
        ###################################
        channel = Channel(
            id="is",
            name="Inverter State",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=True,
            tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.state}"],
        )
        self._define_channel(channel)

        ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"
        if ac_line1 is not None:

            def update_ac_line1_state(status: bool):
                self.line_connected[1] = status
                self.connection_status_subject.on_next(self._calc_inverter_state())

            ac_line1_state_subject = n2k_devices.get_channel_subject(
                ac_id, f"{ACMeterStates.Voltage.value}.{1}", N2kDeviceType.AC
            )

            ac_line1_state = ac_line1_state_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda voltage: voltage > 0),
                ops.distinct_until_changed(),
            ).subscribe(update_ac_line1_state)
            self._disposable_list.append(ac_line1_state)

        if ac_line2 is not None:

            def update_ac_line2_state(status: bool):
                self.line_connected[2] = status
                self.connection_status_subject.on_next(self._calc_inverter_state())

            ac_line2_status_subject = n2k_devices.get_channel_subject(
                ac_id, f"{ACMeterStates.Voltage.value}.{2}", N2kDeviceType.AC
            )

            ac_line2_state = ac_line2_status_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda voltage: voltage > 0),
                ops.distinct_until_changed(),
            ).subscribe(update_ac_line2_state)
            self._disposable_list.append(ac_line2_state)

        if ac_line3 is not None:

            def update_ac_line3_state(status: bool):
                self.line_connected[3] = status
                self.connection_status_subject.on_next(self._calc_inverter_state())

            ac_line3_status_subject = n2k_devices.get_channel_subject(
                ac_id, ACMeterStates.Voltage.value, N2kDeviceType.AC
            )

            ac_line3_state = ac_line3_status_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda voltage: voltage > 0),
                ops.distinct_until_changed(),
            ).subscribe(update_ac_line3_state)
            self._disposable_list.append(ac_line3_state)

        n2k_devices.set_subscription(
            self._define_channel(channel),
            self.inverter_state_subject.pipe(
                ops.distinct_until_changed(),
            ),
        )

    def define_inverter_enable_channel(
        self,
        circuit: Optional[Circuit],
        n2k_devices: N2kDevices,
    ):
        """
        Define the inverter enable channel for the AcMeterInverter.

        Args:
            circuit (Optional[Circuit]): Associated circuit for this inverter, if any.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """
        ############################
        # Inverter Enable
        ############################
        if circuit is not None:
            channel = Channel(
                id="ie",
                name="Inverter Enable",
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                read_only=(circuit.switch_type == SwitchType.Not_Set),
                tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.enabled}"],
            )

            circuit_level_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.CIRCUITS}.{self.inverter_circuit_id}",
                CircuitStates.Level.value,
                N2kDeviceType.CIRCUIT,
            )
            inverter_enable = circuit_level_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda level: 1 if level > 0 else 0),
                ops.distinct_until_changed(),
            )
            n2k_devices.set_subscription(
                self._define_channel(channel),
                inverter_enable,
            )


class CombiInverter(InverterBase):
    """
    Represents a combined inverter/charger device in the Empower system.

    Handles the creation and management of inverter state, component status, and enable channels.
    Integrates with N2kDevices and RxPy for real-time updates.
    """

    inverter_circuit_id: Optional[str] = None
    instance: int

    def __init__(
        self,
        inverter_charger: InverterChargerDevice,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
        instance: int,
        status_ac_line: int,
        n2k_devices: N2kDevices,
        inverter_circuit: Optional[Circuit] = None,
    ):
        """
        Initialize the CombiInverter and set up all relevant inverter channels.

        Args:
            inverter_charger (InverterChargerDevice): The inverter/charger device configuration.
            ac_line1 (AC): The first AC line configuration.
            ac_line2 (AC): The second AC line configuration.
            ac_line3 (AC): The third AC line configuration.
            categories (list[str]): List of categories for this inverter.
            instance (int): The instance number for this inverter.
            status_ac_line (int): The AC line number associated with the main status.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            inverter_circuit (Optional[Circuit]): Associated circuit for this inverter, if any.
        """
        InverterBase.__init__(
            self,
            id=instance,
            name=ac_line1.name_utf8,
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
            status_ac_line=status_ac_line,
            n2k_devices=n2k_devices,
        )
        if inverter_circuit is not None:
            self.inverter_circuit_id = inverter_circuit.id.value
            self.inverter_circuit_control_id = inverter_circuit.control_id

        self.n2k_device_id = f"{JsonKeys.INVERTER_CHARGERS}.{instance}"
        self.define_inverter_channels(
            n2k_devices=n2k_devices, inverter_circuit=inverter_circuit
        )

    def define_inverter_channels(
        self, n2k_devices: N2kDevices, inverter_circuit: Optional[Circuit]
    ):
        """
        Define all inverter channels (state, component status, enable) for the CombiInverter.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            inverter_circuit (Optional[Circuit]): Associated circuit for this inverter, if any.
        """
        self.define_inverter_state_channel(n2k_devices=n2k_devices)
        self.define_inverter_component_status_channel(n2k_devices=n2k_devices)
        self.define_inverter_enable_channel(
            inverter_circuit=inverter_circuit, n2k_devices=n2k_devices
        )

    def define_inverter_state_channel(
        self,
        n2k_devices: N2kDevices,
    ):
        """
        Define the inverter state channel for the CombiInverter.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """

        ##########################
        # Inverter State
        ##########################
        channel = Channel(
            id="is",
            name="Inverter State",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=True,
            tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.state}"],
        )

        inverter_state_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            CombiInverterStates.InverterState.value,
            N2kDeviceType.INVERTERCHARGER,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            inverter_state_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: map_inverter_state(state)),
                ops.distinct_until_changed(),
            ),
        )

    def define_inverter_component_status_channel(
        self,
        n2k_devices: N2kDevices,
    ):
        """
        Define the component status channel for the CombiInverter.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """
        #############################
        # Component Status
        #############################
        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.inverter}.{Constants.componentStatus}"
            ],
        )

        component_status_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            CombiInverterStates.ComponentStatus.value,
            N2kDeviceType.INVERTERCHARGER,
        )

        component_status = component_status_subject.pipe(
            ops.filter(lambda state: state is not None),
            ops.map(
                lambda status: (
                    ConnectionStatus.CONNECTED
                    if status == "Connected"
                    else ConnectionStatus.DISCONNECTED
                )
            ),
            ops.map(lambda status: StateWithTS(status).to_json()),
            ops.distinct_until_changed(lambda state: state[Constants.state]),
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            component_status,
        )

    def define_inverter_enable_channel(
        self,
        inverter_circuit: Optional[Circuit],
        n2k_devices: N2kDevices,
    ):
        """
        Define the inverter enable channel for the CombiInverter.

        Args:
            inverter_circuit (Optional[Circuit]): Associated circuit for this inverter, if any.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """
        #############################
        # Inverter Enable
        #############################
        channel = Channel(
            id="ie",
            name="Inverter Enable",
            type=ChannelType.NUMBER,
            unit=Unit.NONE,
            read_only=(
                (inverter_circuit.switch_type == SwitchType.Not_Set)
                if inverter_circuit
                else True
            ),
            tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.enabled}"],
        )

        inverter_enable_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            CombiInverterStates.InverterEnable.value,
            N2kDeviceType.INVERTERCHARGER,
        )
        inverter_ie = inverter_enable_subject.pipe(
            ops.filter(lambda state: state is not None), ops.distinct_until_changed()
        )
        inverter_enable = inverter_ie

        if inverter_circuit is not None:
            circuit_device_id = f"{JsonKeys.CIRCUITS}.{self.inverter_circuit_id}"

            circuit_level_subject = n2k_devices.get_channel_subject(
                circuit_device_id, CircuitStates.Level.value, N2kDeviceType.CIRCUIT
            )

            circuit_ie = circuit_level_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda level: 1 if level > 0 else 0),
                ops.distinct_until_changed(),
            )
            inverter_enable = rx.merge(inverter_ie, circuit_ie)

        n2k_devices.set_subscription(self._define_channel(channel), inverter_enable)
