from typing import Optional

from reactivex import operators as ops
import reactivex as rx
from ..devices import N2kDevices
from ..empower_system.connection_status import ConnectionStatus
from ..empower_system.state_ts import StateWithTS
from ...util.state_util import StateUtil
from .thing import Thing
from ..n2k_configuration.inverter_charger import InverterChargerDevice
from ..n2k_configuration.ac import AC
from ..n2k_configuration.dc import DC
from ..n2k_configuration.circuit import Circuit
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants, JsonKeys, BATTERY_CONST_MAP
from .channel import Channel
from .ac_meter import ACMeterThingBase
from ...services.config_processor.config_processor_helpers import (
    calculate_inverter_charger_instance,
)
from ..empower_system.ac_meter import ACMeterThingBase
from ...util import rx as rxu
from ..filters import Current, Voltage
from ..common_enums import (
    N2kDeviceType,
    CombiChargerStates,
    CircuitStates,
    ACMeterStates,
    DCMeterStates,
    ChargerStatus,
)

CHARGER_STATE_MAPPING = {
    ChargerStatus.ABSORPTION: "absorption",
    ChargerStatus.BULK: "bulk",
    ChargerStatus.CONSTANTVI: "constantVI",
    ChargerStatus.NOTCHARGING: "notCharging",
    ChargerStatus.EQUALIZE: "equalize",
    ChargerStatus.OVERCHARGE: "overcharge",
    ChargerStatus.FLOAT: "float",
    ChargerStatus.NOFLOAT: "noFloat",
    ChargerStatus.FAULT: "fault",
    ChargerStatus.DISABLED: "disabled",
}


def map_charger_state(state: str) -> str:
    try:
        enum_state = ChargerStatus(state)
        return CHARGER_STATE_MAPPING.get(enum_state, "unknown")
    except ValueError:
        return "unknown"


class CombiCharger(Thing):
    instance: int
    component_status: rx.Observable[dict[str, any]]

    def __init__(
        self,
        inverter_charger: InverterChargerDevice,
        dc1: DC,
        dc2: DC,
        dc3: DC,
        categories: list[str],
        instance: int,
        n2k_devices: N2kDevices,
        charger_circuit: Optional[Circuit] = None,
    ):
        if charger_circuit is not None:
            self.charger_circuit = charger_circuit.id.value
            self.charger_circuit_control_id = charger_circuit.control_id
        self.n2k_device_id = f"{JsonKeys.INVERTER_CHARGER}.{instance}"
        Thing.__init__(
            self,
            type=ThingType.CHARGER,
            id=instance,
            name=inverter_charger.name_utf8,
            categories=categories,
        )
        self.instance = instance

        ############################
        # DC Lines
        ############################
        self.define_dc_lines(dc1, dc2, dc3, n2k_devices)
        self.define_combi_channels(charger_circuit, n2k_devices)

    def define_dc_lines(self, dc1: DC, dc2: DC, dc3: DC, n2k_devices: N2kDevices):
        if dc1 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.name}"
            ] = dc1.name_utf8

            self.define_dc_line_channels(1, n2k_devices, dc1)

        if dc2 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.name}"
            ] = dc2.name_utf8

            self.define_dc_line_channels(2, n2k_devices, dc2)

        if dc3 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.name}"
            ] = dc3.name_utf8

            self.define_dc_line_channels(3, n2k_devices, dc3)

    def define_dc_line_channels(
        self, battery_number: int, n2k_devices: N2kDevices, dc: DC
    ):
        dc_device_id = f"{JsonKeys.DC}.{dc.instance.instance}"

        battery_const = BATTERY_CONST_MAP.get(battery_number)
        ############################
        #  DC Line Component Status
        ###########################
        channel = Channel(
            id=f"dc{battery_number}cs",
            name=f"Battery {battery_number} Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.charger}.{battery_const}.{Constants.componentStatus}"
            ],
        )
        self._define_channel(channel)

        dc1_component_status_subject = n2k_devices.get_channel_subject(
            dc_device_id, DCMeterStates.ComponentStatus.value, N2kDeviceType.DC
        )

        n2k_devices.set_subscription(
            channel.id,
            dc1_component_status_subject.pipe(
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
            ),
        )

        ####################
        #  DC Line Voltage
        ####################
        channel = Channel(
            id=f"dc{battery_number}v",
            name=f"Battery {battery_number} Voltage",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.charger}.{battery_const}.{Constants.voltage}"
            ],
        )

        self._define_channel(channel)
        dc_voltage_subject = n2k_devices.get_channel_subject(
            dc_device_id, DCMeterStates.Voltage.value, N2kDeviceType.DC
        )

        n2k_devices.set_subscription(
            channel.id,
            dc_voltage_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Voltage.ROUND_VALUE),
                Voltage.FILTER,
            ),
        )

        ####################
        #  DC Line Current
        ####################
        channel = Channel(
            id=f"dc{battery_number}c",
            name=f"Battery {battery_number} Current",
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_AMP,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.charger}.{battery_const}.{Constants.current}"
            ],
        )
        self._define_channel(channel)
        dc_current_subject = n2k_devices.get_channel_subject(
            dc_device_id, DCMeterStates.Current.value, N2kDeviceType.DC
        )
        n2k_devices.set_subscription(
            channel.id,
            dc_current_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Current.ROUND_VALUE),
                Current.FILTER,
            ),
        )

    def define_combi_channels(
        self, charger_circuit: Optional[Circuit], n2k_devices: N2kDevices
    ):
        ####################
        #  Charger Enabled
        ####################
        channel = Channel(
            id="ce",
            name="Charger Enabled",
            read_only=(
                charger_circuit.switch_type == 0
                if charger_circuit is not None
                else True
            ),
            type=ChannelType.NUMBER,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.charger}.enabled"],
        )
        self._define_channel(channel)

        charger_enable_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            CombiChargerStates.ChargerEnable.value,
            N2kDeviceType.INVERTERCHARGER,
        )
        charger_ce = charger_enable_subject.pipe(
            ops.filter(lambda state: state is not None),
            ops.distinct_until_changed(),
        )
        charger_enable = charger_ce
        if charger_circuit is not None:
            circuit_level_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.CIRCUIT}.{self.charger_circuit}",
                CircuitStates.Level.value,
                N2kDeviceType.CIRCUIT,
            )

            circuit_ce = circuit_level_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda level: 1 if level > 0 else 0),
                ops.distinct_until_changed(),
            )
            charger_enable = rx.merge(charger_ce, circuit_ce)
        n2k_devices.set_subscription(channel.id, charger_enable)

        ####################
        #  Charger Status
        ####################
        channel = Channel(
            id="cst",
            name="Charger Status",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.charger}.status"],
        )
        self._define_channel(channel)

        inverter_charger_status_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            CombiChargerStates.ChargerState.value,
            N2kDeviceType.INVERTERCHARGER,
        )

        n2k_devices.set_subscription(
            channel.id,
            inverter_charger_status_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: map_charger_state(state)),
                ops.distinct_until_changed(),
            ),
        )


class ACMeterCharger(ACMeterThingBase):
    def _calc_charger_state(self) -> str:
        return "charging" if StateUtil.any_true(self.line_connected) else "disabled"

    def __init__(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        categories: list[str],
        circuit: Optional[Circuit] = None,
    ):
        ACMeterThingBase.__init__(
            self, ThingType.CHARGER, ac_line1, ac_line2, ac_line3, categories
        )

        self.line_connected = {}
        self.line_state_subject = rx.subject.BehaviorSubject(self._calc_charger_state)

        ###########################
        # Channels
        ###########################
        self.define_ac_meter_charger_channels(
            ac_line1, ac_line2, ac_line3, n2k_devices, circuit
        )

    def define_ac_meter_charger_channels(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevices,
        circuit: Optional[Circuit] = None,
    ):
        self.define_ac_meter_charger_status_channel(
            ac_line1, ac_line2, ac_line3, n2k_devices
        )
        if circuit is not None:
            self.define_ac_meter_charger_circuit_enable_channel(circuit, n2k_devices)

    def define_ac_meter_charger_circuit_enable_channel(
        self, circuit: Circuit, n2k_devices: N2kDevices
    ):
        self.charger_circuit = circuit.id.value
        self.charger_circuit_control_id = circuit.control_id
        ####################
        #  Charger Enabled
        ####################
        channel = Channel(
            id="ce",
            name="Charger Enabled",
            read_only=(circuit.switch_type == 0 if circuit is not None else True),
            type=ChannelType.NUMBER,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.charger}.{Constants.enabled}"],
        )
        self._define_channel(channel)

        circuit_level_subject = n2k_devices.get_channel_subject(
            f"{JsonKeys.CIRCUIT}.{self.charger_circuit}",
            CircuitStates.Level.value,
            N2kDeviceType.CIRCUIT,
        )

        charger_enable = circuit_level_subject.pipe(
            ops.filter(lambda state: state is not None),
            ops.map(lambda level: 1 if level > 0 else 0),
            ops.distinct_until_changed(),
        )
        n2k_devices.set_subscription(channel.id, charger_enable)

    def define_ac_meter_charger_status_channel(
        self, ac_line1: AC, ac_line2: AC, ac_line3: AC, n2k_devices: N2kDevices
    ):
        ####################
        #  Charger Status
        ####################
        channel = Channel(
            id="cst",
            name="Charger Status",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.charger}.{Constants.status}"],
        )

        self._define_channel(channel)

        ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"
        if ac_line1 is not None:

            def update_ac_line1_state(status: bool):
                self.line_connected[1] = status
                self.line_state_subject.on_next(self._calc_charger_state())

            ac_line1_state_subject = n2k_devices.get_channel_subject(
                ac_id, f"{ACMeterStates.Voltage.value}.{1}", N2kDeviceType.AC
            )

            ac_line1_state = ac_line1_state_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda voltage: voltage > 0),
            ).subscribe(update_ac_line1_state)
            self._disposable_list.append(ac_line1_state)

        if ac_line2 is not None:

            def update_ac_line2_state(status: bool):
                self.line_connected[2] = status
                self.line_state_subject.on_next(self._calc_charger_state())

            ac_line2_state_subject = n2k_devices.get_channel_subject(
                ac_id, f"{ACMeterStates.Voltage.value}.{2}", N2kDeviceType.AC
            )

            ac_line2_state = ac_line2_state_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda voltage: voltage > 0),
            ).subscribe(update_ac_line2_state)
            self._disposable_list.append(ac_line2_state)
        if ac_line3 is not None:

            def update_ac_line3_state(status: bool):
                self.line_connected[3] = status
                self.line_state_subject.on_next(self._calc_charger_state())

            ac_line3_state_subject = n2k_devices.get_channel_subject(
                ac_id, f"{ACMeterStates.Voltage.value}.{3}", N2kDeviceType.AC
            )

            ac_line3_state = ac_line3_state_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda voltage: voltage > 0),
            ).subscribe(update_ac_line3_state)
            self._disposable_list.append(ac_line3_state)

        n2k_devices.set_subscription(
            channel.id,
            self.line_state_subject.pipe(
                ops.distinct_until_changed(),
            ),
        )
