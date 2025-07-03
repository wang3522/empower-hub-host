from typing import Optional

from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from N2KClient.util.state_util import StateUtil
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.ac import AC
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, Unit
from reactivex import operators as ops
import N2KClient.util.rx as rxu
from N2KClient.models.filters import Current, Voltage, Frequency, Power
import reactivex as rx
from N2KClient.models.common_enums import N2kDeviceType


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

        ac_id = f"{JsonKeys.AC}.{ac_line1.instance.instance}"
        if ac_line1 is not None:

            def update_line_1_status(status: dict[str, any]):
                self.line_status[1] = status[Constants.state]
                self.connection_status_subject.on_next(self._calc_connection_status())

            ##############################
            # Line 1 Component Status
            ##############################
            channel = Channel(
                id="l1cs",
                name="Line 1 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{ac_line1.instance.instance}.{ac_line1.line.name}"
                ],
            )

            self._define_channel(channel)

            if ic_associated_line == 1 and ic_component_status is not None:
                line_1_component_status_subject = ic_component_status
            else:
                line_1_component_status_subject = n2k_devices.get_channel_subject(
                    ac_id, f"{JsonKeys.ComponentStatus}.{1}", N2kDeviceType.AC
                )

                line_1_component_status = line_1_component_status_subject.pipe(
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

            n2k_devices.set_subscription(
                channel.id,
                line_1_component_status,
            )

            line_1_component_status.subscribe(update_line_1_status)
            self._disposable_list.append(line_1_component_status)

            ##############################
            # Line 1 Voltage
            ##############################
            channel = Channel(
                id="l1v",
                name="Line 1 Voltage",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)

            line1_voltage_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Voltage}.{1}", N2kDeviceType.AC
            )

            n2k_devices.set_subscription(
                channel.id,
                line1_voltage_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Voltage.ROUND_VALUE),
                    Voltage.FILTER,
                ),
            )

            ##############################
            # Line 1 Current
            ##############################
            channel = Channel(
                id="l1c",
                name="Line 1 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.current}"
                ],
            )
            self._define_channel(channel)

            line1_current_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Current}.{1}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line1_current_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Current.ROUND_VALUE),
                    Current.FILTER,
                ),
            )

            ##############################
            # Line 1 Frequency
            ##############################
            channel = Channel(
                id="l1f",
                name="Line 1 Frequency",
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.frequency}"
                ],
            )
            self._define_channel(channel)
            line1_frequency_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Frequency}.{1}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line1_frequency_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Frequency.ROUND_VALUE),
                    Frequency.FILTER,
                ),
            )

            ##############################
            # Line 1 Power
            ##############################
            channel = Channel(
                id="l1p",
                name="Line 1 Power",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line1}.{Constants.power}"
                ],
            )
            self._define_channel(channel)

            line1_power_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Power}.{1}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line1_power_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Power.ROUND_VALUE),
                    Power.FILTER,
                ),
            )

        if ac_line2 is not None:

            def update_line_2_status(status: dict[str, any]):
                self.line_status[2] = status[Constants.state]
                self.connection_status_subject.on_next(self._calc_connection_status())

            ################################
            # Line 2 Component Status
            ################################
            channel = Channel(
                id="l2cs",
                name="Line 2 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.componentStatus}"
                ],
            )
            self._define_channel(channel)

            if ic_associated_line == 2 and ic_component_status is not None:
                line_2_component_status = ic_component_status
            else:
                line_2_component_status_subject = n2k_devices.get_channel_subject(
                    ac_id, f"{JsonKeys.ComponentStatus}.{2}", N2kDeviceType.AC
                )

                line_2_component_status = line_2_component_status_subject.pipe(
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

            n2k_devices.set_subscription(channel.id, line_2_component_status)

            line_2_component_status.subscribe(update_line_2_status)
            self._disposable_list.append(line_2_component_status)

            #################################
            # Line 2 Voltage
            #################################
            channel = Channel(
                id="l2v",
                name="Line 2 Voltage",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)

            line_2_voltage_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Voltage}.{2}", N2kDeviceType.AC
            )

            n2k_devices.set_subscription(
                channel.id,
                line_2_voltage_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Voltage.ROUND_VALUE),
                    Voltage.FILTER,
                ),
            )

            #################################
            # Line 2 Current
            #################################
            channel = Channel(
                id="l2c",
                name="Line 2 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.current}"
                ],
            )
            self._define_channel(channel)

            line_2_current_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Current}.{2}", N2kDeviceType.AC
            )

            n2k_devices.set_subscription(
                channel.id,
                line_2_current_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Current.ROUND_VALUE),
                    Current.FILTER,
                ),
            )

            #################################
            # Line 2 Frequency
            #################################
            channel = Channel(
                id="l2f",
                name="Line 2 Frequency",
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.frequency}"
                ],
            )
            self._define_channel(channel)

            line_2_frequency_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Frequency}.{2}", N2kDeviceType.AC
            )

            n2k_devices.set_subscription(
                channel.id,
                line_2_frequency_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Frequency.ROUND_VALUE),
                    Frequency.FILTER,
                ),
            )
            #################################
            # Line 2 Power
            #################################
            channel = Channel(
                id="l2p",
                name="Line 2 Power",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_WATT,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line2}.{Constants.power}"
                ],
            )
            self._define_channel(channel)

            line_2_power_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Power}.{2}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line_2_power_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Power.ROUND_VALUE),
                    Power.FILTER,
                ),
            )
            self._define_channel(channel)

        if ac_line3 is not None:

            def update_line_3_status(status: dict[str, any]):
                self.line_status[3] = status[Constants.state]
                self.connection_status_subject.on_next(self._calc_connection_status())

            ##################################
            # Line 3 Component Status
            ##################################
            channel = Channel(
                id="l3cs",
                name="Line 3 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.componentStatus}"
                ],
            )
            self._define_channel(channel)

            if ic_associated_line == 3 and ic_component_status is not None:
                line_3_component_status = ic_component_status
            else:
                line_3_component_status_subject = n2k_devices.get_channel_subject(
                    ac_id, f"{JsonKeys.ComponentStatus}.{3}", N2kDeviceType.AC
                )

                line_3_component_status = line_3_component_status_subject.pipe(
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
            n2k_devices.set_subscription(
                channel.id,
                line_3_component_status,
            )

            line_3_component_status.subscribe(update_line_3_status)

            self._disposable_list.append(line_3_component_status)

            ##################################
            # Line 3 Voltage
            ##################################
            channel = Channel(
                id="l3v",
                name="Line 3 Voltage",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.voltage}"
                ],
            )
            self._define_channel(channel)

            line_3_voltage_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Voltage}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line_3_voltage_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Voltage.ROUND_VALUE),
                    Voltage.FILTER,
                ),
            )

            ##################################
            # Line 3 Current
            ##################################
            channel = Channel(
                id="l3c",
                name="Line 3 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.current}"
                ],
            )
            self._define_channel(channel)

            line_3_current_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Current}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line_3_current_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Current.ROUND_VALUE),
                    Current.FILTER,
                ),
            )

            ##################################
            # Line 3 Frequency
            ##################################
            channel = Channel(
                id="l3f",
                name="Line 3 Frequency",
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.frequency}"
                ],
            )
            self._define_channel(channel)

            line_3_frequency_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Frequency}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line_3_frequency_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Frequency.ROUND_VALUE),
                    Frequency.FILTER,
                ),
            )

            ##################################
            # Line 3 Power
            ##################################
            channel = Channel(
                id="l3p",
                name="Line 3 Power",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_WATT,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{type.value}.{Constants.line3}.{Constants.power}"
                ],
            )

            line_3_power_subject = n2k_devices.get_channel_subject(
                ac_id, f"{JsonKeys.Power}.{3}", N2kDeviceType.AC
            )
            n2k_devices.set_subscription(
                channel.id,
                line_3_power_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    rxu.round(Power.ROUND_VALUE),
                    Power.FILTER,
                ),
            )
            self._define_channel(channel)

        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[f"{Constants.empower}:{type.value}.{Constants.componentStatus}"],
        )
        self._define_channel(channel)

        componenet_status = self.connection_status_subject.pipe(
            ops.filter(lambda state: state is not None),
            ops.map(lambda status: StateWithTS(status).to_json()),
            ops.distinct_until_changed(lambda state: state[Constants.state]),
        )

        n2k_devices.set_subscription(channel.id, componenet_status)
