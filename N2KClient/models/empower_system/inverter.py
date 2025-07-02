from typing import Optional
from reactivex import operators as ops
import reactivex as rx

from N2KClient.models.empower_system.state_ts import StateWithTS
from .thing import Thing
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit, SwitchType
from N2KClient.models.common_enums import ThingType
from .channel import Channel, ChannelType
from N2KClient.models.common_enums import Unit
from N2KClient.models.constants import Constants, JsonKeys
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.devices import (
    N2kDevice,
    N2kDevices,
)
import N2KClient.util.rx as rxu
from N2KClient.models.filters import Current, Voltage, Frequency, Power
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.util.state_util import StateUtil
from N2KClient.models.common_enums import N2kDeviceType

INVERTER_STATE_MAPPING = {
    JsonKeys.INVERTING: "inverting",
    JsonKeys.AC_PASSTHRU: "acPassthrough",
    JsonKeys.LOAD_SENSE: "loadSense",
    JsonKeys.FAULT: "fault",
    JsonKeys.DISABLED: "disabled",
    JsonKeys.CHARGING: "charging",
    JsonKeys.ENERGY_SAVING: "energySaving",
    JsonKeys.ENERGY_SAVING2: "energySaving",
    JsonKeys.SUPPORTING: "supporting",
    JsonKeys.SUPPORTING2: "supporting",
    JsonKeys.ERROR: "error",
    JsonKeys.DATA_NOT_AVAILABLE: "unknown",
}


def map_inverter_state(state: str) -> str:
    """
    Maps the inverter state from the N2K JSON keys to a more readable format.
    """
    return INVERTER_STATE_MAPPING.get(state, "unknown")


class InverterBase(Thing):
    ac_line1: Optional[AC] = None
    ac_line2: Optional[AC] = None
    ac_line3: Optional[AC] = None

    def _calc_connection_status(self):
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

        ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"
        #########################################
        # Line 1
        #########################################
        if ac_line1 is not None:

            def update_line1_status(status: dict[str, any]):
                self.line_status[1] = status[Constants.state]
                self.connection_status_subject.on_next(self._calc_connection_status())

            # Line 1 Component Status
            channel = Channel(
                id="l1cs",
                name="Line 1 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.componentStatus}"
                ],
            )

            self._define_channel(channel)

            if inverter_component_status is not None and status_ac_line == 1:
                line1_component_status = inverter_component_status
            else:
                ac1_component_status_subject = n2k_devices.get_channel_subject(
                    ac_id, f"{JsonKeys.ComponentStatus}.{1}", N2kDeviceType.AC
                )
                line1_component_status = ac1_component_status_subject.pipe(
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

            line1_component_status.subscribe(update_line1_status)
            self._disposable_list.append(line1_component_status)

            n2k_devices.set_subscription(channel.id, line1_component_status)

            # Line 1 Voltage
            channel = Channel(
                id="l1v",
                name="Line 1 Voltage",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)

            ac1_voltage_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Voltage}.{1}", N2kDeviceType.AC
            )

            n2k_devices.set_subscription(
                channel.id,
                ac1_voltage_subject.pipe(
                    rxu.round(Voltage.ROUND_VALUE), Voltage.FILTER
                ),
            )

            # Line 1 Current
            channel = Channel(
                id="l1c",
                name="Line 1 Current",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.current}"
                ],
            )
            self._define_channel(channel)
            ac1_current_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Current}.{1}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac1_current_subject.pipe(
                    rxu.round(Current.ROUND_VALUE), Current.FILTER
                ),
            )
            #######################
            # Line 1 Frequency
            #######################
            channel = Channel(
                id="l1f",
                name="Line 1 Frequency",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.frequency}"
                ],
            )
            self._define_channel(channel)
            ac1_frequency_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Frequency}.{1}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac1_frequency_subject.pipe(
                    rxu.round(Frequency.ROUND_VALUE), Frequency.FILTER
                ),
            )

            # Line 1 Power
            channel = Channel(
                id="l1p",
                name="Line 1 Power",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_WATT,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.power}"
                ],
            )
            self._define_channel(channel)
            ac1_power_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Power}.{1}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac1_power_subject.pipe(rxu.round(Power.ROUND_VALUE), Power.FILTER),
            )

        #########################################
        # Line 2
        #########################################
        if ac_line2 is not None:

            def update_line2_status(status: dict[str, any]):
                self.line_status[2] = status[Constants.state]
                self.connection_status_subject.on_next(self._calc_connection_status())

            # Line 2 Component Status
            channel = Channel(
                id="l2cs",
                name="Line 2 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.componentStatus}"
                ],
            )

            self._define_channel(channel)

            if inverter_component_status is not None and status_ac_line == 2:
                line_2_component_status = inverter_component_status
            else:
                ac2_component_status_subject = n2k_devices.get_channel_subject(
                    ac_id, f"{JsonKeys.ComponentStatus}.{2}", N2kDeviceType.AC
                )
                line_2_component_status = ac2_component_status_subject.pipe(
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

            line_2_component_status.subscribe(update_line2_status)
            self._disposable_list.append(line_2_component_status)

            n2k_devices.set_subscription(channel.id, line_2_component_status)

            # Line 2 Voltage
            channel = Channel(
                id="l2v",
                name="Line 2 Voltage",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)
            ac2_voltage_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Voltage}.{2}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac2_voltage_subject.pipe(
                    rxu.round(Voltage.ROUND_VALUE), Voltage.FILTER
                ),
            )

            # Line 2 Current
            channel = Channel(
                id="l2c",
                name="Line 2 Current",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.current}"
                ],
            )
            self._define_channel(channel)
            ac2_current_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Current}.{2}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac2_current_subject.pipe(
                    rxu.round(Current.ROUND_VALUE), Current.FILTER
                ),
            )

            # Line 2 Frequency
            channel = Channel(
                id="l2f",
                name="Line 2 Frequency",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.frequency}"
                ],
            )
            self._define_channel(channel)
            ac2_frequency_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Frequency}.{2}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac2_frequency_subject.pipe(
                    rxu.round(Frequency.ROUND_VALUE), Frequency.FILTER
                ),
            )

            # Line 2 Power
            channel = Channel(
                id="l2p",
                name="Line 2 Power",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_WATT,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.power}"
                ],
            )
            self._define_channel(channel)
            ac2_power_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Power}.{2}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac2_power_subject.pipe(rxu.round(Power.ROUND_VALUE), Power.FILTER),
            )

        #########################################
        # Line 3
        #########################################
        if ac_line3 is not None:

            def update_line3_status(status: dict[str, any]):
                self.line_status[3] = status[Constants.state]
                self.connection_status_subject.on_next(self._calc_connection_status())

            # Line 3 Component Status
            channel = Channel(
                id="l3cs",
                name="Line 3 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.componentStatus}"
                ],
            )
            self._define_channel(channel)

            if inverter_component_status is not None and status_ac_line == 3:
                line_3_component_status = inverter_component_status
            else:
                ac3_component_status_subject = n2k_devices.get_channel_subject(
                    ac_id, f"{JsonKeys.ComponentStatus}.{3}", N2kDeviceType.AC
                )
                line_3_component_status = ac3_component_status_subject.pipe(
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

            line_3_component_status.subscribe(update_line3_status)
            self._disposable_list.append(line_3_component_status)

            n2k_devices.set_subscription(channel.id, line_3_component_status)

            # Line 3 Voltage
            channel = Channel(
                id="l3v",
                name="Line 3 Voltage",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)
            ac3_voltage_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Voltage}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac3_voltage_subject.pipe(
                    rxu.round(Voltage.ROUND_VALUE), Voltage.FILTER
                ),
            )

            # Line 3 Current
            channel = Channel(
                id="l3c",
                name="Line 3 Current",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.current}"
                ],
            )

            self._define_channel(channel)
            ac3_current_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Current}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac3_current_subject.pipe(
                    rxu.round(Current.ROUND_VALUE), Current.FILTER
                ),
            )

            # Line 3 Frequency
            channel = Channel(
                id="l3f",
                name="Line 3 Frequency",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.frequency}"
                ],
            )

            self._define_channel(channel)
            ac3_frequency_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Frequency}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac3_frequency_subject.pipe(
                    rxu.round(Frequency.ROUND_VALUE), Frequency.FILTER
                ),
            )
            # Line 3 Power
            channel = Channel(
                id="l3p",
                name="Line 3 Power",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_WATT,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.power}"
                ],
            )
            self._define_channel(channel)
            ac3_power_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Power}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                ac3_power_subject.pipe(rxu.round(Power.ROUND_VALUE), Power.FILTER),
            )
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
                ops.map(lambda status: StateWithTS(status).to_json()),
                ops.distinct_until_changed(lambda state: state[Constants.state]),
            )

            n2k_devices.set_subscription(channel.id, component_status)


class AcMeterInverter(InverterBase):

    def _calc_inverter_state(self) -> str:
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
        self.line_connected = {}
        self.inverter_state_subject = rx.subject.BehaviorSubject(
            self._calc_inverter_state
        )

        if circuit is not None:
            self.inverter_circuit_id = circuit.control_id
        InverterBase.__init__(
            self,
            id=ac_line1.instance.instance,
            name=ac_line1.name_utf8,
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
        )

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
                ac_id, f"{JsonKeys.Voltage}.{1}", N2kDeviceType.AC
            )

            ac_line1_state = ac_line1_state_subject.pipe(
                ops.map(lambda voltage: voltage > 0), ops.distinct_until_changed()
            ).subscribe(update_ac_line1_state)
            self._disposable_list.append(ac_line1_state)

        if ac_line2 is not None:

            def update_ac_line2_state(status: bool):
                self.line_connected[2] = status
                self.connection_status_subject.on_next(self._calc_inverter_state())

            ac_line2_status_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Voltage}.{2}", N2kDeviceType.AC
            )

            ac_line2_state = ac_line2_status_subject.pipe(
                ops.map(lambda voltage: voltage > 0), ops.distinct_until_changed()
            ).subscribe(update_ac_line2_state)
            self._disposable_list.append(ac_line2_state)

        if ac_line3 is not None:

            def update_ac_line3_state(status: bool):
                self.line_connected[3] = status
                self.connection_status_subject.on_next(self._calc_inverter_state())

            ac_line3_status_subject = n2k_devices.get_channel_subject(
                ac_id, JsonKeys.Voltage, N2kDeviceType.AC
            )

            ac_line3_state = ac_line3_status_subject.pipe(
                ops.map(lambda voltage: voltage > 0), ops.distinct_until_changed()
            ).subscribe(update_ac_line3_state)
            self._disposable_list.append(ac_line3_state)

        n2k_devices.set_subscription(
            channel.id,
            self.inverter_state_subject.pipe(
                ops.distinct_until_changed(),
            ),
        )

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
            self._define_channel(channel)

            circuit_level_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.CIRCUIT}.{circuit.control_id}",
                JsonKeys.Level,
                N2kDeviceType.CIRCUIT,
            )
            inverter_enable = circuit_level_subject.pipe(
                ops.map(lambda level: 1 if level > 0 else 0),
                ops.distinct_until_changed(),
            )
            n2k_devices.set_subscription(
                channel.id,
                inverter_enable,
            )


class CombiInverter(InverterBase):
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
            self.inverter_circuit_id = inverter_circuit.control_id

        n2k_device_id = f"{JsonKeys.INVERTER_CHARGER}.{instance}"

        # Inverter State
        channel = Channel(
            id="is",
            name="Inverter State",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=True,
            tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.state}"],
        )
        self._define_channel(channel)

        inverter_state_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.InverterState, N2kDeviceType.INVERTERCHARGER
        )
        n2k_devices.set_subscription(
            channel.id,
            inverter_state_subject.pipe(
                ops.map(lambda state: map_inverter_state(state)),
                ops.distinct_until_changed(),
            ),
        )

        # Component Status
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
        self._define_channel(channel)

        component_status_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.ComponentStatus, N2kDeviceType.INVERTERCHARGER
        )

        component_status = component_status_subject.pipe(
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
            component_status,
        )

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

        self._define_channel(channel)
        inverter_enable_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.InverterEnable, N2kDeviceType.INVERTERCHARGER
        )
        inverter_ie = inverter_enable_subject.pipe(ops.distinct_until_changed())
        inverter_enable = inverter_ie

        if inverter_circuit is not None:
            circuit_device_id = f"{JsonKeys.CIRCUIT}.{inverter_circuit.control_id}"

            circuit_level_subject = n2k_devices.get_channel_subject(
                circuit_device_id, JsonKeys.Level, N2kDeviceType.CIRCUIT
            )

            circuit_ie = circuit_level_subject.pipe(
                ops.map(lambda level: 1 if level > 0 else 0),
                ops.distinct_until_changed(),
            )
            inverter_enable = rx.merge(inverter_ie, circuit_ie)

        n2k_devices.set_subscription(channel.id, inverter_enable)
