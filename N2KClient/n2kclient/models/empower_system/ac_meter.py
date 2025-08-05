from typing import Optional

from ..devices import N2kDevices
from ..empower_system.connection_status import ConnectionStatus
from ..empower_system.state_ts import StateWithTS
from ...util.state_util import StateUtil
from .thing import Thing
from ..common_enums import ThingType
from ..n2k_configuration.ac import AC
from ..constants import Constants, JsonKeys, LINE_CONST_MAP
from .channel import Channel
from ..common_enums import ChannelType, Unit
from reactivex import operators as ops
from ...util import rx as rxu
from ...models.filters import Current, Voltage, Frequency, Power
import reactivex as rx
from ...models.common_enums import N2kDeviceType, ACMeterStates


class ACMeterThingBase(Thing):
    """
    Base class for AC meter devices in the Empower system.

    Handles the creation and management of AC line channels (voltage, current, frequency, power, and status)
    for up to three AC lines. Tracks connection status and provides integration with N2kDevices and RxPy.
    """

    def _calc_connection_status(self):
        """
        Calculate the overall connection status for the AC meter based on the status of all lines.

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
        type: ThingType,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        categories: list[str],
        ic_associated_line: Optional[int],
        ic_component_status: Optional[rx.Observable[dict[str, any]]] = None,
    ):
        """
        Initialize the AC meter thing with up to three AC lines and set up all relevant channels.

        Args:
            type (ThingType): The type of the thing (e.g., AC_METER).
            ac_line1 (AC): The first AC line configuration
            ac_line2 (AC): The second AC line configuration
            ac_line3 (AC): The third AC line configuration
            n2k_devices (N2KDevices): The N2K device manager for channel subjects and subscriptions.
            categories (list[str]): List of categories for this thing.
            ic_associated_line (Optional[int]): Line number of acmeter that is associated with inverter charger (optional).
            ic_component_status (Optional[rx.Observable[dict[str, any]]]): Observable for component status of associated inverter charger (optional).
        """
        self.line_status = {}
        self.connection_status_subject = rx.subject.BehaviorSubject(None)
        Thing.__init__(
            self,
            type,
            ac_line1.instance.instance,
            ac_line1.name_utf8,
            categories=categories,
            links=[],
        )

        self.ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"

        self.define_ac_channels(
            ac_line1,
            ac_line2,
            ac_line3,
            n2k_devices,
            ic_associated_line,
            ic_component_status,
        )

    def define_ac_channels(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        ic_associated_line: Optional[int],
        ic_component_status: Optional[rx.Observable[dict[str, any]]] = None,
    ):
        """
        Define all AC line channels (voltage, current, frequency, power, and status) for up to three lines.
        Also defines the overall component status channel for the AC meter.

        Args:
            ac_line1 (AC): The first AC line configuration
            ac_line2 (AC): The second AC line configuration
            ac_line3 (AC): The third AC line configuration
            n2k_devices (N2KDevices): The N2K device manager for channel subjects and subscriptions.
            ic_associated_line (Optional[int]): Line number of acmeter that is associated with inverter charger (if any).
            ic_component_status (Optional[rx.Observable[dict[str, any]]]): Observable for component status of associated inverter charger (if any).
        """
        if ac_line1 is not None:
            self.define_ac_line_channels(
                1, n2k_devices, ic_associated_line, ic_component_status
            )
        if ac_line2 is not None:
            self.define_ac_line_channels(
                2, n2k_devices, ic_associated_line, ic_component_status
            )
        if ac_line3 is not None:
            self.define_ac_line_channels(
                3, n2k_devices, ic_associated_line, ic_component_status
            )

        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[f"{Constants.empower}:{self.type.value}.{Constants.componentStatus}"],
        )

        componenet_status = self.connection_status_subject.pipe(
            ops.filter(lambda state: state is not None),
            ops.map(lambda status: StateWithTS(status).to_json()),
            ops.distinct_until_changed(lambda state: state[Constants.state]),
        )

        n2k_devices.set_subscription(self._define_channel(channel), componenet_status)

    def define_ac_line_channels(
        self,
        line_number: int,
        n2k_devices: N2kDevices,
        ic_associated_line: Optional[int],
        ic_component_status: Optional[rx.Observable[dict[str, any]]] = None,
    ):
        """
        Define all channels for a single AC line (component status, voltage, current, frequency, power).

        Args:
            line_number (int): The AC line number (1, 2, or 3).
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            ic_associated_line (Optional[int]): Line number of acmeter that is associated with inverter charger (if any).
            ic_component_status (Optional[rx.Observable[dict[str, any]]]): Observable for component status of associated inverter charger (if any).
        """
        line_const = LINE_CONST_MAP.get(line_number)

        def update_line_status(status: dict[str, any]):
            self.line_status[line_number] = status[Constants.state]
            self.connection_status_subject.on_next(self._calc_connection_status())

        ###############################
        # Line Component Status
        ###############################

        channel = Channel(
            id=f"l{line_number}cs",
            name=f"Line {line_number} Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{self.type.value}.{line_const}.{Constants.componentStatus}"
            ],
        )

        if ic_associated_line == line_number and ic_component_status is not None:
            line_component_status_subject = ic_component_status
        else:
            line_component_status_subject = n2k_devices.get_channel_subject(
                self.ac_id,
                f"{ACMeterStates.ComponentStatus.value}.{line_number}",
                N2kDeviceType.AC,
            )

            line_component_status = line_component_status_subject.pipe(
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
            self._define_channel(channel), line_component_status
        )

        line_component_status.subscribe(update_line_status)
        self._disposable_list.append(line_component_status)

        ###################################
        # Line Voltage
        ###################################
        channel = Channel(
            id=f"l{line_number}v",
            name=f"Line {line_number} Voltage",
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_VOLT,
            read_only=True,
            tags=[
                f"{Constants.empower}:{self.type.value}.{line_const}.{Constants.voltage}"
            ],
        )

        line_voltage_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Voltage.value}.{line_number}", N2kDeviceType.AC
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            line_voltage_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Voltage.ROUND_VALUE),
                Voltage.FILTER,
            ),
        )

        ##############################
        # Line Current
        ##############################
        channel = Channel(
            id=f"l{line_number}c",
            name=f"Line {line_number} Current",
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_AMP,
            read_only=True,
            tags=[
                f"{Constants.empower}:{self.type.value}.{line_const}.{Constants.current}"
            ],
        )

        line_current_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Current.value}.{line_number}", N2kDeviceType.AC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            line_current_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Current.ROUND_VALUE),
                Current.FILTER,
            ),
        )

        ##############################
        # Line Frequency
        ##############################
        channel = Channel(
            id=f"l{line_number}f",
            name=f"Line {line_number} Frequency",
            type=ChannelType.NUMBER,
            unit=Unit.FREQUENCY_HERTZ,
            read_only=True,
            tags=[
                f"{Constants.empower}:{self.type.value}.{line_const}.{Constants.frequency}"
            ],
        )
        line_frequency_subject = n2k_devices.get_channel_subject(
            self.ac_id,
            f"{ACMeterStates.Frequency.value}.{line_number}",
            N2kDeviceType.AC,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            line_frequency_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Frequency.ROUND_VALUE),
                Frequency.FILTER,
            ),
        )

        ##############################
        # Line Power
        ##############################
        channel = Channel(
            id=f"l{line_number}p",
            name=f"Line {line_number} Power",
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_VOLT,
            read_only=True,
            tags=[
                f"{Constants.empower}:{self.type.value}.{line_const}.{Constants.power}"
            ],
        )

        line_power_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Power.value}.{line_const}", N2kDeviceType.AC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            line_power_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Power.ROUND_VALUE),
                Power.FILTER,
            ),
        )
