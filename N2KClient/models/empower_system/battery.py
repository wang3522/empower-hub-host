from typing import Optional, Union

from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from .thing import Thing
from N2KClient.models.common_enums import ThingType, BatteryStatus
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, Unit
from reactivex import operators as ops
import N2KClient.util.rx as rxu
from N2KClient.models.filters import Current, Voltage, Temperature, CapacityRemaining
import reactivex as rx


class Battery(Thing):
    battery_circuit_id: Optional[int] = None
    instance = int

    def __init__(
        self,
        battery: DC,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
        battery_circuit: Circuit = None,
        primary_battery: DC = None,
        fallback_battery: DC = None,
    ):
        Thing.__init__(
            self,
            ThingType.BATTERY,
            battery.instance.instance,
            battery.name_utf8,
            categories,
            links=[],
        )
        self.instance = battery.instance.instance
        battery_device_id = f"{JsonKeys.DC}.{self.instance}"
        if battery_circuit is not None:
            self.battery_circuit_id = battery_circuit.control_id
            ######################
            # Circuit Channel
            ######################
            channel = Channel(
                id="enabled",
                name="Enabled",
                read_only=battery_circuit.switch_type == 0,
                unit=Unit.NONE,
                type=ChannelType.BOOLEAN,
                tags=[f"{Constants.empower}:{Constants.battery}.{Constants.enabled}"],
            )
            self._define_channel(channel)
            battery_enable_subject = n2k_devices.get_channel_subject(
                f"{JsonKeys.CIRCUIT}.{self.battery_circuit_id}", JsonKeys.Level
            )
            n2k_devices.set_subscription(
                channel.id,
                battery_enable_subject.pipe(
                    ops.map(lambda level: level > 0),
                    ops.distinct_until_changed(),
                ),
            )

        if fallback_battery is not None:
            self.fallback_battery = fallback_battery

        if primary_battery is not None:
            self.primary_battery = primary_battery

        if battery.capacity is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.battery}.{Constants.capacity}"
            ] = battery.capacity

        if battery.show_voltage:
            ##############################
            # Voltage Channel
            ##############################
            channel = Channel(
                id=Constants.voltage,
                name="Voltage",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                tags=[f"{Constants.empower}:{Constants.battery}.{JsonKeys.Voltage}"],
            )
            self._define_channel(channel)
            dc_voltage_subject = n2k_devices.get_channel_subject(
                battery_device_id, Constants.voltage
            )
            n2k_devices.set_subscription(
                channel.id,
                dc_voltage_subject.pipe(rxu.round(Voltage.ROUND_VALUE), Voltage.FILTER),
            )

        if battery.show_current:
            #############################
            # Current Channel
            #############################
            channel = Channel(
                id="current",
                name="Current",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                tags=[f"{Constants.empower}:{Constants.battery}.{Constants.current}"],
            )
            self._define_channel(channel)
            dc_current_subject = n2k_devices.get_channel_subject(
                battery_device_id, JsonKeys.Current
            )
            n2k_devices.set_subscription(
                channel.id,
                dc_current_subject.pipe(rxu.round(Current.ROUND_VALUE), Current.FILTER),
            )

            #############################
            # Status Channel
            ############################
            def resolve_battery_status(
                current: Union[float, None], state_of_charge: Union[int, None]
            ):

                if current is not None:
                    if state_of_charge == 100:
                        return BatteryStatus.CHARGED.value
                    elif current <= 0.3:
                        return BatteryStatus.DISCHARGING.value
                    else:
                        return BatteryStatus.CHARGING.value

                return None

            channel = Channel(
                id="status",
                name="Status",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.battery}.{Constants.status}"],
            )

            self._define_channel(channel)
            dc_state_of_charge_subject = n2k_devices.get_channel_subject(
                battery_device_id, JsonKeys.StateOfCharge
            )
            n2k_devices.set_subscription(
                channel.id,
                rx.combine_latest(dc_current_subject, dc_state_of_charge_subject).pipe(
                    ops.map(lambda state: resolve_battery_status(state[0], state[1])),
                    ops.distinct_until_changed(),
                ),
            )

        if battery.show_temperature:
            #####################
            # Temperature Channel
            #####################
            channel = Channel(
                id="temperature",
                name="Temperature",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.TEMPERATURE_CELSIUS,
                tags=[
                    f"{Constants.empower}:{Constants.battery}.{Constants.temperature}"
                ],
            )

            self._define_channel(channel)
            dc_temperature_subject = n2k_devices.get_channel_subject(
                battery_device_id, JsonKeys.Temperature
            )

            n2k_devices.set_subscription(
                channel.id,
                dc_temperature_subject.pipe(
                    rxu.round(Temperature.ROUND_VALUE), Temperature.FILTER
                ),
            )
        if battery.show_state_of_charge:
            #########################
            # State of Charge Channel
            #########################
            channel = Channel(
                id="stateOfCharge",
                name="State of Charge",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.PERCENT,
                tags=[
                    f"{Constants.empower}:{Constants.battery}.{Constants.stateOfCharge}"
                ],
            )
            self._define_channel(channel)
            dc_soc_subject = n2k_devices.get_channel_subject(
                battery_device_id, JsonKeys.StateOfCharge
            )
            n2k_devices.set_subscription(
                channel.id,
                dc_soc_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

            ##############################
            # Capacity Remaining Channel
            ##############################
            channel = Channel(
                id="capactiyRemaining",
                name="Capacity Remaining",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP_HOURS,
                tags=[
                    f"{Constants.empower}:{Constants.battery}.{Constants.capacityRemaining}"
                ],
            )
            self._define_channel(channel)
            dc_capacity_remaining_subject = n2k_devices.get_channel_subject(
                battery_device_id, JsonKeys.CapacityRemaining
            )
            n2k_devices.set_subscription(
                channel.id,
                dc_capacity_remaining_subject.pipe(
                    rxu.round(CapacityRemaining.ROUND_VALUE),
                    ops.distinct_until_changed(),
                ),
            )
        if battery.show_time_of_remaining:
            ##############################
            # Time Remaining Channel
            ##############################
            channel = Channel(
                id="timeRemaining",
                name="Time Remaining",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.TIME_SECOND,
                tags=[
                    f"{Constants.empower}:{Constants.battery}.{Constants.timeRemaining}"
                ],
            )
            self._define_channel(channel)
            dc_time_remaining_subject = n2k_devices.get_channel_subject(
                battery_device_id, JsonKeys.TimeRemaining
            )
            n2k_devices.set_subscription(
                channel.id,
                dc_time_remaining_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

            ################################
            # Time to Charge Channel
            ################################
            channel = Channel(
                id="timeToCharge",
                name="Time to Charge",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.TIME_SECOND,
                tags=[
                    f"{Constants.empower}:{Constants.battery}.{Constants.timeToCharge}"
                ],
            )
            self._define_channel(channel)
            dc_time_to_charge_subject = n2k_devices.get_channel_subject(
                battery_device_id, JsonKeys.TimeToCharge
            )
            n2k_devices.set_subscription(
                channel.id,
                dc_time_to_charge_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        #################################
        # Component Status Channel
        #################################
        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.battery}.{Constants.componentStatus}"
            ],
        )
        self._define_channel(channel)
        dc_component_status_subject = n2k_devices.get_channel_subject(
            battery_device_id, JsonKeys.ComponentStatus
        )
        n2k_devices.set_subscription(
            channel.id,
            dc_component_status_subject.pipe(
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
