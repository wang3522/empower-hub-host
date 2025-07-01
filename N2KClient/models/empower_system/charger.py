from typing import Optional

from reactivex import operators as ops
import reactivex as rx
from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from N2KClient.util.state_util import StateUtil
from .thing import Thing
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants, JsonKeys
from .channel import Channel
from N2KClient.models.empower_system.ac_meter import ACMeterThingBase
import N2KClient.util.rx as rxu
from N2KClient.models.filters import Current, Voltage

CHARGER_STATE_MAPPING = {
    JsonKeys.ABSORPTION: "absorption",
    JsonKeys.BULK: "bulk",
    JsonKeys.CONSTANTVI: "constantVI",
    JsonKeys.NOTCHARGING: "notCharging",
    JsonKeys.EQUALIZE: "equalize",
    JsonKeys.OVERCHARGE: "overcharge",
    JsonKeys.FLOAT: "float",
    JsonKeys.NOFLOAT: "noFloat",
    JsonKeys.FAULT: "fault",
    JsonKeys.DISABLED: "disabled",
}


def map_charger_state(state: str) -> str:
    return CHARGER_STATE_MAPPING.get(state, "unknown")


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
            self.charger_circuit = charger_circuit.control_id
        n2k_device_id = f"{JsonKeys.INVERTER_CHARGER}.{instance}"
        Thing.__init__(
            self,
            type=ThingType.CHARGER,
            id=instance,
            name=inverter_charger.name_utf8,
            categories=categories,
        )
        self.instance = instance

        if dc1 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.name}"
            ] = dc1.name_utf8

            dc1_device_id = f"{JsonKeys.DC}.{dc1.instance.instance}"

            # DC 1 Component Status
            channel = Channel(
                id="dc1cs",
                name=" Battery 1 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.componentStatus}"
                ],
            )
            self._define_channel(channel)

            dc1_component_status_subject = n2k_devices.get_channel_subject(
                dc1_device_id, JsonKeys.ComponentStatus
            )

            n2k_devices.set_subscription(
                channel.id,
                dc1_component_status_subject.pipe(
                    ops.map(
                        lambda status: (
                            ConnectionStatus.CONNECTED
                            if status == "Connected"
                            else "Disconnected"
                        )
                    ),
                    ops.map(lambda status: StateWithTS(status).to_json()),
                    ops.distinct_until_changed(lambda state: state[Constants.state]),
                ),
            )

            # DC1 Voltage
            channel = Channel(
                id="dc1v",
                name="Battery 1 Voltage",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.voltage}"
                ],
            )

            self._define_channel(channel)
            dc1_voltage_subject = n2k_devices.get_channel_subject(
                dc1_device_id, JsonKeys.Voltage
            )

            n2k_devices.set_subscription(
                channel.id,
                dc1_voltage_subject.pipe(
                    rxu.round(Voltage.ROUND_VALUE), Voltage.FILTER
                ),
            )

            # DC1 Current
            channel = Channel(
                id="dc1c",
                name="Battery 1 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.current}"
                ],
            )
            self._define_channel(channel)
            dc1_current_subject = n2k_devices.get_channel_subject(
                dc1_device_id, JsonKeys.Current
            )
            n2k_devices.set_subscription(
                channel.id,
                dc1_current_subject.pipe(
                    rxu.round(Current.ROUND_VALUE), Current.FILTER
                ),
            )

        if dc2 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.name}"
            ] = dc2.name_utf8

            # DC 2 Component Status
            channel = Channel(
                id="dc2cs",
                name=" Battery 2 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.componentStatus}"
                ],
            )
            self._define_channel(channel)

            d2_component_status_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.DC}.{dc2.instance.instance}", JsonKeys.ComponentStatus
            )

            n2k_devices.set_subscription(
                channel.id,
                d2_component_status_subject.pipe(
                    ops.map(
                        lambda status: (
                            ConnectionStatus.CONNECTED
                            if status == "Connected"
                            else "Disconnected"
                        )
                    ),
                    ops.map(lambda status: StateWithTS(status).to_json()),
                    ops.distinct_until_changed(lambda state: state[Constants.state]),
                ),
            )

            # DC2 Voltage
            channel = Channel(
                id="dc2v",
                name="Battery 2 Voltage",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)

            dc2_voltage_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.DC}.{dc2.instance.instance}", JsonKeys.Voltage
            )

            n2k_devices.set_subscription(
                channel.id,
                dc2_voltage_subject.pipe(
                    rxu.round(Voltage.ROUND_VALUE), Voltage.FILTER
                ),
            )

            # DC 2 Current
            channel = Channel(
                id="dc2c",
                name="Battery 2 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.current}"
                ],
            )
            self._define_channel(channel)

            dc2_current_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.DC}.{dc2.instance.instance}", JsonKeys.Current
            )

            n2k_devices.set_subscription(
                channel.id,
                dc2_current_subject.pipe(
                    rxu.round(Current.ROUND_VALUE), Current.FILTER
                ),
            )

        if dc3 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.name}"
            ] = dc3.name_utf8

            # DC 3 Component Status
            channel = Channel(
                id="dc3cs",
                name=" Battery 3 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.componentStatus}"
                ],
            )
            self._define_channel(channel)

            dc3_component_status_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.DC}.{dc3.instance.instance}", JsonKeys.ComponentStatus
            )
            n2k_devices.set_subscription(
                channel.id,
                dc3_component_status_subject.pipe(
                    ops.map(
                        lambda status: (
                            ConnectionStatus.CONNECTED
                            if status == "Connected"
                            else "Disconnected"
                        )
                    ),
                    ops.map(lambda status: StateWithTS(status).to_json()),
                    ops.distinct_until_changed(lambda state: state[Constants.state]),
                ),
            )

            # DC3 Voltage
            channel = Channel(
                id="dc3v",
                name="Battery 3 Voltage",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)

            dc3_voltage_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.DC}.{dc3.instance.instance}", JsonKeys.Voltage
            )

            n2k_devices.set_subscription(
                channel.id,
                dc3_voltage_subject.pipe(
                    rxu.round(Voltage.ROUND_VALUE), Voltage.FILTER
                ),
            )

            # DC 3 Current
            channel = Channel(
                id="dc3c",
                name="Battery 3 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.current}"
                ],
            )
            self._define_channel(channel)

            dc3_current_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.DC}.{dc3.instance.instance}", JsonKeys.Current
            )
            n2k_devices.set_subscription(
                channel.id,
                dc3_current_subject.pipe(
                    rxu.round(Current.ROUND_VALUE), Current.FILTER
                ),
            )
            # Component Status for Charger
            channel = Channel(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.charger}.{Constants.componentStatus}"
                ],
            )
            self._define_channel(channel)

            inverter_charger_component_status_subject = n2k_devices.get_channel_subject(
                n2k_device_id,
                JsonKeys.ComponentStatus,
            )

            self.component_status = inverter_charger_component_status_subject.pipe(
                ops.map(
                    lambda status: (
                        ConnectionStatus.CONNECTED
                        if status == "Connected"
                        else "Disconnected"
                    )
                ),
                ops.map(lambda status: StateWithTS(status).to_json()),
                ops.distinct_until_changed(lambda state: state[Constants.state]),
            )

            n2k_devices.set_subscription(
                channel.id,
                inverter_charger_component_status_subject.pipe(self.component_status),
            )

            # Charger Enabled
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
                n2k_device_id,
                JsonKeys.ChargerEnable,
            )
            charger_ce = charger_enable_subject.pipe(
                ops.distinct_until_changed(),
            )
            charger_enable = charger_ce
            if charger_circuit is not None:
                circuit_level_subject = n2k_devices.get_channel_subject(
                    f"{JsonKeys.CIRCUIT}.{charger_circuit.control_id}", JsonKeys.Level
                )

                circuit_ce = circuit_level_subject.pipe(
                    ops.map(lambda level: 1 if level > 0 else 0),
                    ops.distinct_until_changed(),
                )
                charger_enable = rx.merge(charger_ce, circuit_ce)
            n2k_devices.set_subscription(channel.id, charger_enable)

            # Charger Status
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
                f"{JsonKeys.INVERTER_CHARGER}.{inverter_charger.id}",
                JsonKeys.ChargerState,
            )

            n2k_devices.set_subscription(
                channel.id,
                inverter_charger_status_subject.pipe(
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

        if circuit is not None:
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
                f"{JsonKeys.CIRCUIT}.{circuit.control_id}", JsonKeys.Level
            )

            charger_enable = circuit_level_subject.pipe(
                ops.map(lambda level: 1 if level > 0 else 0),
                ops.distinct_until_changed(),
            )
            n2k_devices.set_subscription(channel.id, charger_enable)

        channel = Channel(
            id="cst",
            name="Charger Status",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.charger}.{Constants.status}"],
        )

        self._define_channel(channel)

        if ac_line1 is not None:

            def update_ac_line1_state(status: bool):
                self.line_connected[1] = status
                self.line_state_subject.on_next(self._calc_charger_state())

            ac_line1_state_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.AC}.{ac_line1.instance.instance}", JsonKeys.Voltage
            )

            ac_line1_state = ac_line1_state_subject.pipe(
                ops.map(lambda voltage: voltage > 0)
            ).subscribe(update_ac_line1_state)
            self._disposable_list.append(ac_line1_state)

        if ac_line2 is not None:

            def update_ac_line2_state(status: bool):
                self.line_connected[2] = status
                self.line_state_subject.on_next(self._calc_charger_state())

            ac_line2_state_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.AC}.{ac_line2.instance.instance}", JsonKeys.Voltage
            )

            ac_line2_state = ac_line2_state_subject.pipe(
                ops.map(lambda voltage: voltage > 0)
            ).subscribe(update_ac_line2_state)
            self._disposable_list.append(ac_line2_state)
        if ac_line3 is not None:

            def update_ac_line3_state(status: bool):
                self.line_connected[3] = status
                self.line_state_subject.on_next(self._calc_charger_state())

            ac_line3_state_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.AC}.{ac_line3.instance.instance}", JsonKeys.Voltage
            )

            ac_line3_state = ac_line3_state_subject.pipe(
                ops.map(lambda voltage: voltage > 0)
            ).subscribe(update_ac_line3_state)
            self._disposable_list.append(ac_line3_state)

        n2k_devices.set_subscription(
            channel.id,
            self.line_state_subject.pipe(
                ops.distinct_until_changed(),
            ),
        )
