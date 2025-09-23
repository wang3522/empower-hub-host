from typing import Optional, Union

from ..devices import N2kDevices
from ..empower_system.connection_status import ConnectionStatus
from ..empower_system.state_ts import StateWithTS
from .thing import Thing
from ..common_enums import ThingType, BatteryStatus
from ..n2k_configuration.dc import DC
from ..n2k_configuration.circuit import Circuit
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, Unit
from reactivex import operators as ops
from ...util import rx as rxu
from ..filters import Current, Voltage, Temperature, CapacityRemaining
import reactivex as rx
from ..common_enums import N2kDeviceType, DCMeterStates, CircuitStates
from ...models.alarm_setting import (
    AlarmSettingFactory,
    AlarmSettingLimit,
    AlarmSettingType,
)
from ..n2k_configuration.alarm_limit import AlarmLimit


class Battery(Thing):
    """
    Represents a battery device in the Empower system.

    Handles the creation and management of battery-related channels (voltage, current, temperature, etc.),
    metadata, and alarm settings. Integrates with N2kDevices and RxPy for real-time updates.
    """

    battery_circuit_id: Optional[int] = None
    battery_circuit_control_id: Optional[int] = None
    instance: int

    def __init__(
        self,
        battery: DC,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
        battery_circuit: Circuit = None,
        primary_battery: DC = None,
        fallback_battery: DC = None,
    ):
        """
        Initialize the Battery thing and set up all relevant channels, metadata, and alarm settings.

        Args:
            battery (DC): The DC configuration for this battery.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            categories (list[str], optional): List of categories for this battery.
            battery_circuit (Circuit, optional): Associated circuit for this battery, if any.
            primary_battery (DC, optional): Reference to the primary battery, if any.
            fallback_battery (DC, optional): Reference to the fallback battery, if any.
        """
        Thing.__init__(
            self,
            ThingType.BATTERY,
            battery.instance.instance,
            battery.name_utf8,
            categories,
            links=[],
        )
        self.instance = battery.instance.instance
        self.battery_device_id = f"{JsonKeys.DC}.{self.instance}"

        self.define_battery_metadata(battery, fallback_battery, primary_battery)

        self.define_battery_channels(n2k_devices, battery, battery_circuit)

        self.metadata[
            f"{Constants.empower}:{Constants.battery}.{Constants.timeUnitFixed}"
        ] = True

        for limit in AlarmSettingLimit:
            if hasattr(battery, limit.value):
                attr: AlarmLimit = getattr(battery, limit.value)
                if attr is not None and attr.enabled and attr.id > 0:
                    limit_on = AlarmSettingFactory.get_alarm_setting(
                        AlarmSettingType.BATTERY,
                        limit,
                        attr.id,
                        attr.on,
                        is_on=True,
                    )
                    limit_off = AlarmSettingFactory.get_alarm_setting(
                        AlarmSettingType.BATTERY,
                        limit,
                        attr.id,
                        attr.off,
                        is_on=False,
                    )
                    self.alarm_settings.extend([limit_on, limit_off])

    def define_battery_metadata(
        self,
        battery: DC,
        fallback_battery: DC,
        primary_battery: DC,
    ):
        """
        Define and set metadata for the battery, including fallback/primary references and capacity.

        Args:
            battery (DC): The DC configuration for this battery.
            fallback_battery (DC): Reference to the fallback battery, if any.
            primary_battery (DC): Reference to the primary battery, if any.
        """
        if fallback_battery is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.battery}.{Constants.fallbackBattery}"
            ] = f"{ThingType.BATTERY.value}.{fallback_battery.instance.instance}"

        if primary_battery is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.battery}.{Constants.primaryBattery}"
            ] = f"{ThingType.BATTERY.value}.{primary_battery.instance.instance}"

        if battery.capacity is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.battery}.{Constants.capacity}"
            ] = battery.capacity

    def define_battery_channels(
        self, n2k_devices: N2kDevices, battery: DC, battery_circuit: Circuit
    ):
        """
        Define all battery-related channels (voltage, current, temperature, etc.) for this battery.
        Also defines the component status channel.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            battery (DC): The DC configuration for this battery.
            battery_circuit (Circuit): Associated circuit for this battery, if any.
        """
        if battery_circuit is not None:
            self.define_circuit_enabled_channel(n2k_devices, battery_circuit)

        if battery.show_voltage:
            self.define_battery_voltage_channel(n2k_devices)

        if battery.show_current:
            self.define_battery_current_channel(n2k_devices)
            self.define_battery_status_channel(n2k_devices)

        if battery.show_temperature:
            self.define_temperature_channel(n2k_devices)

        if battery.show_state_of_charge:
            self.define_state_of_charge(n2k_devices)
            self.define_capacity_remaining_channel(n2k_devices)

        if battery.show_time_of_remaining:
            self.define_time_remaining_channel(n2k_devices)
            self.define_time_to_charge_channel(n2k_devices)

        self.define_component_status_channel(n2k_devices)

    def define_circuit_enabled_channel(
        self, n2k_devices: N2kDevices, battery_circuit: Circuit = None
    ):
        """
        Define the channel that indicates whether the battery circuit is enabled.
        """
        self.battery_circuit_id = battery_circuit.id.value
        self.battery_circuit_control_id = battery_circuit.control_id
        ######################
        # Circuit Enabled Channel
        ######################
        channel = Channel(
            id="enabled",
            name="Enabled",
            read_only=battery_circuit.switch_type == 0,
            unit=Unit.NONE,
            type=ChannelType.BOOLEAN,
            tags=[f"{Constants.empower}:{Constants.battery}.{Constants.enabled}"],
        )
        battery_enable_subject = n2k_devices.get_channel_subject(
            f"{JsonKeys.CIRCUITS}.{self.battery_circuit_id}",
            CircuitStates.Level.value,
            N2kDeviceType.CIRCUIT,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            battery_enable_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda level: level > 0),
                ops.distinct_until_changed(),
            ),
        )

    def define_battery_voltage_channel(self, n2k_devices: N2kDevices):
        """
        Define the channel for battery voltage.
        This channel will provide real-time updates on the battery's voltage level.
        """
        ##############################
        # Voltage Channel
        ##############################
        channel = Channel(
            id=Constants.voltage,
            name="Voltage",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_VOLT,
            tags=[f"{Constants.empower}:{Constants.battery}.{Constants.voltage}"],
        )
        dc_voltage_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.Voltage.value, N2kDeviceType.DC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_voltage_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Voltage.ROUND_VALUE),
                Voltage.FILTER,
            ),
        )

    def define_battery_current_channel(self, n2k_devices: N2kDevices):
        """
        Define the channel for battery current.
        This channel will provide real-time updates on the battery's current level.
        """
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
        dc_current_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.Current.value, N2kDeviceType.DC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_current_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Current.ROUND_VALUE),
                Current.FILTER,
            ),
        )

    def define_battery_status_channel(self, n2k_devices: N2kDevices):
        """
        Define the channel for battery status.
        This channel will provide real-time updates on the battery's status.

        If battery current is available, it determines the status based on the current value:
        - If current is None, the status is unknown.
        - If state of charge is 100%, the status is CHARGED.
        - If current is less than or equal to 0.3, the status is DISCHARGING.
        - Otherwise, the status is CHARGING.
        """
        ############################
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

        dc_current_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.Current.value, N2kDeviceType.DC
        )
        dc_state_of_charge_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.StateOfCharge.value, N2kDeviceType.DC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            rx.combine_latest(dc_current_subject, dc_state_of_charge_subject).pipe(
                ops.filter(lambda state: state[0] is not None or state[1] is not None),
                ops.map(lambda state: resolve_battery_status(state[0], state[1])),
                ops.distinct_until_changed(),
            ),
        )

    def define_temperature_channel(self, n2k_devices: N2kDevices):
        """
        Define the channel for battery temperature.
        This channel will provide real-time updates on the battery's temperature level.
        """
        #####################
        # Temperature Channel
        #####################
        channel = Channel(
            id="temperature",
            name="Temperature",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.TEMPERATURE_CELSIUS,
            tags=[f"{Constants.empower}:{Constants.battery}.{Constants.temperature}"],
        )

        dc_temperature_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.Temperature.value, N2kDeviceType.DC
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_temperature_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Temperature.ROUND_VALUE),
                Temperature.FILTER,
            ),
        )

    def define_state_of_charge(self, n2k_devices: N2kDevices):
        """
        Define the channel that shows the state of charge of the battery.
        This channel will provide real-time updates on the battery's state of charge."""
        #########################
        # State of Charge Channel
        #########################
        channel = Channel(
            id="stateOfCharge",
            name="State of Charge",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.PERCENT,
            tags=[f"{Constants.empower}:{Constants.battery}.{Constants.stateOfCharge}"],
        )
        dc_state_of_charge_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.StateOfCharge.value, N2kDeviceType.DC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_state_of_charge_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.distinct_until_changed(),
            ),
        )

    def define_capacity_remaining_channel(self, n2k_devices: N2kDevices):
        """
        Define the channel for capacity remaining.
        This channel will provide real-time updates on the remaining capacity of the battery.
        """
        ##############################
        # Capacity Remaining Channel
        ##############################
        channel = Channel(
            id="capacityRemaining",
            name="Capacity Remaining",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.ENERGY_AMP_HOURS,
            tags=[
                f"{Constants.empower}:{Constants.battery}.{Constants.capacityRemaining}"
            ],
        )
        dc_capacity_remaining_subject = n2k_devices.get_channel_subject(
            self.battery_device_id,
            DCMeterStates.CapacityRemaining.value,
            N2kDeviceType.DC,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_capacity_remaining_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(CapacityRemaining.ROUND_VALUE),
                ops.distinct_until_changed(),
            ),
        )

    def define_time_remaining_channel(self, n2k_devices: N2kDevices):
        """ "
        Define the channel for time remaining.
        This channel will provide real-time updates on the time remaining for the battery.
        """
        ################################
        # Time Remaining Channel
        ################################
        channel = Channel(
            id="timeRemaining",
            name="Time Remaining",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.TIME_MINUTE,
            tags=[f"{Constants.empower}:{Constants.battery}.{Constants.timeRemaining}"],
        )
        dc_time_remaining_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.TimeRemaining.value, N2kDeviceType.DC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_time_remaining_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.distinct_until_changed(),
            ),
        )

    def define_time_to_charge_channel(self, n2k_devices: N2kDevices):
        """
        Define the channel for time to charge.
        This channel will provide real-time updates on the time remaining to fully charge the battery.
        """
        ################################
        # Time to Charge Channel
        ################################
        channel = Channel(
            id="timeToCharge",
            name="Time to Charge",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.TIME_MINUTE,
            tags=[f"{Constants.empower}:{Constants.battery}.{Constants.timeToCharge}"],
        )
        dc_time_to_charge_subject = n2k_devices.get_channel_subject(
            self.battery_device_id, DCMeterStates.TimeToCharge.value, N2kDeviceType.DC
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_time_to_charge_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.distinct_until_changed(),
            ),
        )

    def define_component_status_channel(self, n2k_devices: N2kDevices):
        """
        Define the channel for component status.
        This channel will provide real-time updates on the component status of the battery.
        """
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
        dc_component_status_subject = n2k_devices.get_channel_subject(
            self.battery_device_id,
            DCMeterStates.ComponentStatus.value,
            N2kDeviceType.DC,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
            dc_component_status_subject.pipe(
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
