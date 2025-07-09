from typing import Optional

from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from N2KClient.util.state_util import StateUtil
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.ac import AC
from ..constants import Constants, JsonKeys, LINE_CONST_MAP
from .channel import Channel
from ..common_enums import ChannelType, Unit
from reactivex import operators as ops
import N2KClient.util.rx as rxu
from N2KClient.models.filters import Current, Voltage, Frequency, Power
import reactivex as rx
from N2KClient.models.common_enums import N2kDeviceType, ACMeterStates


class ACMeterThingBase(Thing):
    def _calc_connection_status(self):
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
        self.line_status = {}
        self.connection_status_subject = rx.subject.BehaviorSubject(
            ConnectionStatus.DISCONNECTED.value
        )
        Thing.__init__(
            self,
            type,
            ac_line1.instance.instance,
            ac_line1.name_utf8,
            categories=categories,
            links=[],
        )

        self.ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"
        self.type = type

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
        self._define_channel(channel)

        componenet_status = self.connection_status_subject.pipe(
            ops.filter(lambda state: state is not None),
            ops.map(lambda status: StateWithTS(status).to_json()),
            ops.distinct_until_changed(lambda state: state[Constants.state]),
        )

        n2k_devices.set_subscription(channel.id, componenet_status)

    def define_ac_line_channels(
        self,
        line_number: int,
        n2k_devices: N2kDevices,
        ic_associated_line: Optional[int],
        ic_component_status: Optional[rx.Observable[dict[str, any]]] = None,
    ):
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

        self._define_channel(channel)

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
                        else "Disconnected"
                    )
                ),
                ops.map(lambda status: StateWithTS(status).to_json()),
                ops.distinct_until_changed(),
            )

        n2k_devices.set_subscription(channel.id, line_component_status)

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
        self._define_channel(channel)

        line_voltage_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Voltage.value}.{line_number}", N2kDeviceType.AC
        )

        n2k_devices.set_subscription(
            channel.id,
            line_voltage_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Voltage.ROUND_VALUE),
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
        self._define_channel(channel)

        line_current_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Current.value}.{line_number}", N2kDeviceType.AC
        )
        n2k_devices.set_subscription(
            channel.id,
            line_current_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Current.ROUND_VALUE),
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
        self._define_channel(channel)
        line_frequency_subject = n2k_devices.get_channel_subject(
            self.ac_id,
            f"{ACMeterStates.Frequency.value}.{line_number}",
            N2kDeviceType.AC,
        )
        n2k_devices.set_subscription(
            channel.id,
            line_frequency_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Frequency.ROUND_VALUE),
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
        self._define_channel(channel)

        line_power_subject = n2k_devices.get_channel_subject(
            self.ac_id, f"{ACMeterStates.Power.value}.{line_const}", N2kDeviceType.AC
        )
        n2k_devices.set_subscription(
            channel.id,
            line_power_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Power.ROUND_VALUE),
                Power.FILTER,
            ),
        )
