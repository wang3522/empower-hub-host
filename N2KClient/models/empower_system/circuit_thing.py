import reactivex as rx
from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from N2KClient.util.state_util import StateUtil
from .thing import Thing
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants, JsonKeys
from .channel import Channel
from .link import Link
from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState
from N2KClient.models.n2k_configuration.category_item import CategoryItem
from reactivex import operators as ops
from N2KClient.models.filters import Current
import N2KClient.util.rx as rxu
from N2KClient.models.common_enums import N2kDeviceType


def get_enabled_categories(categories: list[CategoryItem]):
    return [category.name_utf8 for category in categories if category.enabled == True]


class CircuitThing(Thing):
    circuit: Circuit

    def __init__(
        self,
        type: ThingType,
        circuit: Circuit,
        links: list[Link],
        n2k_devices: N2kDevices,
        bls: BinaryLogicState = None,
    ):
        Thing.__init__(
            self,
            type,
            circuit.control_id,
            circuit.name_utf8,
            get_enabled_categories(circuit.categories),
            links=links,
        )
        self.circuit = circuit
        self.circuit_runtime_id = circuit.control_id

        circuit_device_id = f"{JsonKeys.CIRCUIT}.{circuit.control_id}"
        #############################
        # Component Status
        #############################
        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[f"{Constants.empower}:{type.value}.{Constants.componentStatus}"],
        )
        self._define_channel(channel)
        component_status_subject = n2k_devices.get_channel_subject(
            circuit_device_id, JsonKeys.ComponentStatus, N2kDeviceType.CIRCUIT
        )
        n2k_devices.set_subscription(
            channel.id,
            component_status_subject.pipe(
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

        ##############################
        # Current
        ##############################
        channel = Channel(
            id="c",
            name="Current",
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_AMP,
            read_only=True,
            tags=[f"{Constants.empower}:{type.value}.current"],
        )
        self._define_channel(channel)
        current_subject = n2k_devices.get_channel_subject(
            circuit_device_id, JsonKeys.Current, N2kDeviceType.CIRCUIT
        )

        n2k_devices.set_subscription(
            channel.id,
            current_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Current.ROUND_VALUE),
                Current.FILTER,
            ),
        )
        if circuit.dimmable:
            ##############################
            # Dimming Level
            ##############################
            channel = Channel(
                id="lvl",
                name="Level",
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                read_only=False,
                tags=[f"{Constants.empower}:{type.value}.level"],
            )
            self._define_channel(channel)

            level_subject = n2k_devices.get_channel_subject(
                circuit_device_id, JsonKeys.Level, N2kDeviceType.CIRCUIT
            )
            n2k_devices.set_subscription(
                channel.id,
                level_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )
        else:
            ##############################
            # Power
            ##############################

            power_subject = n2k_devices.get_channel_subject(
                circuit_device_id, JsonKeys.Level, N2kDeviceType.CIRCUIT
            )
            circuit_power_state = power_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda level: StateWithTS(level > 0).to_json()),
                ops.distinct_until_changed(lambda state: state[Constants.state]),
            )
            power_state = circuit_power_state
            if bls is not None and power_subject is not None:
                bls_states_subject = n2k_devices.get_channel_subject(
                    f"{JsonKeys.BINARY_LOGIC_STATE}.{bls.address}",
                    JsonKeys.States,
                    N2kDeviceType.BINARY_LOGIC_STATE,
                )

                bls_power_state = bls_states_subject.pipe(
                    ops.map(
                        lambda state: StateWithTS(
                            StateUtil.get_bls_state(bls.address, state)
                        ).to_json()
                    ),
                    ops.distinct_until_changed(lambda state: state[Constants.state]),
                )
                power_state = rx.merge(circuit_power_state, bls_power_state)

            channel = Channel(
                id="p",
                name="Power",
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                read_only=circuit.switch_type == 0,
                tags=[f"{Constants.empower}:{type.value}.power"],
            )
            self._define_channel(channel)
            n2k_devices.set_subscription(
                channel.id,
                power_state,
            )
