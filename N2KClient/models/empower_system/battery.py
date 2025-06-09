from typing import Optional

from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.empower_system.inverter import MappingUtils
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, Unit


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
        instance = battery.instance.instance

        channels = []

        if battery_circuit is not None:
            self.battery_circuit_id = battery_circuit.control_id
            channels.append(
                Channel(
                    id="enabled",
                    name="Enabled",
                    read_only=battery_circuit.switch_type == 0,
                    unit=Unit.NONE,
                    type=ChannelType.BOOLEAN,
                    tags=[
                        f"{Constants.empower}:{Constants.battery}.{Constants.enabled}"
                    ],
                )
            )
            self._register_enable_mapping(self, n2k_devices)
        if fallback_battery is not None:
            self.fallback_battery = fallback_battery

        if primary_battery is not None:
            self.primary_battery = primary_battery

        if battery.capacity is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.battery}.{Constants.capacity}"
            ] = battery.capacity

        if battery.show_voltage:
            channels.append(
                Channel(
                    id=Constants.voltage,
                    name="Voltage",
                    read_only=True,
                    type=ChannelType.NUMBER,
                    unit=Unit.ENERGY_VOLT,
                    tags=[
                        f"{Constants.empower}:{Constants.battery}.{Constants.voltage}"
                    ],
                )
            )
            self._register_voltage_mapping(self, n2k_devices)
        if battery.show_current:
            channels.extend(
                [
                    Channel(
                        id="current",
                        name="Current",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        tags=[
                            f"{Constants.empower}:{Constants.battery}.{Constants.current}"
                        ],
                    ),
                    Channel(
                        id="status",
                        name="Status",
                        read_only=True,
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        tags=[
                            f"{Constants.empower}:{Constants.battery}.{Constants.status}"
                        ],
                    ),
                ]
            )
            self._register_current_mapping(self, n2k_devices)
            self._register_status_mapping(self, n2k_devices)
        if battery.show_temperature:
            channels.append(
                Channel(
                    id="temperature",
                    name="Temperature",
                    read_only=True,
                    type=ChannelType.NUMBER,
                    unit=Unit.TEMPERATURE_CELSIUS,
                    tags=[
                        f"{Constants.empower}:{Constants.battery}.{Constants.temperature}"
                    ],
                )
            )
            self._register_temperature_mapping(self, n2k_devices)
        if battery.show_state_of_charge:
            channels.extend(
                [
                    Channel(
                        id="stateOfCharge",
                        name="State of Charge",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.PERCENT,
                        tags=[
                            f"{Constants.empower}:{Constants.battery}.{Constants.stateOfCharge}"
                        ],
                    ),
                    Channel(
                        id="capactiyRemaining",
                        name="Capacity Remaining",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP_HOURS,
                        tags=[
                            f"{Constants.empower}:{Constants.battery}.{Constants.capacityRemaining}"
                        ],
                    ),
                ]
            )
            self._register_state_of_charge_mapping(self, n2k_devices)
            self._register_capacity_remaining_mapping(self, n2k_devices)
        if battery.show_time_of_remaining:
            channels.extend(
                [
                    Channel(
                        id="timeRemaining",
                        name="Time Remaining",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.TIME_SECOND,
                        tags=[
                            f"{Constants.empower}:{Constants.battery}.{Constants.timeRemaining}"
                        ],
                    ),
                    Channel(
                        id="timeToCharge",
                        name="Time to Charge",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.TIME_SECOND,
                        tags=[
                            f"{Constants.empower}:{Constants.battery}.{Constants.timeToCharge}"
                        ],
                    ),
                ]
            )
            self._register_time_remaining_mapping(self, n2k_devices)
            self._register_time_to_charge_mapping(self, n2k_devices)

        channels.extend(
            [
                Channel(
                    id="cs",
                    name="Component Status",
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    read_only=False,
                    tags=[
                        f"{Constants.empower}:{Constants.battery}.{Constants.componentStatus}"
                    ],
                ),
            ]
        )
        for channel in channels:
            self._define_channel(channel)

    def _register_enable_mapping(self, n2k_devices: N2kDevices):
        """
        Register the enable mapping
        """

        def battery_enable_transform(values: dict, last_updated: dict) -> Optional[int]:
            charger_enable_value = MappingUtils.get_value_or_default(
                values, "circuit_power", None
            )
            if charger_enable_value is not None:
                return True if charger_enable_value > 0 else False
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.enabled",
            channel_sources=[
                ChannelSource(
                    label="circuit_power",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="Level",
                )
            ],
            transform=battery_enable_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_voltage_mapping(self, n2k_devices: N2kDevices):
        """
        Register the voltage mapping
        """

        def battery_voltage_transform(
            values: dict, last_updated: dict
        ) -> Optional[float]:
            voltage_value = MappingUtils.get_value_or_default(values, "voltage", None)
            if voltage_value is not None:
                return voltage_value
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.voltage",
            channel_sources=[
                ChannelSource(
                    label="voltage",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="Voltage",
                )
            ],
            transform=battery_voltage_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_current_mapping(self, n2k_devices: N2kDevices):
        """
        Register the current mapping
        """

        def battery_current_transform(
            values: dict, last_updated: dict
        ) -> Optional[float]:
            current_value = MappingUtils.get_value_or_default(values, "current", None)
            if current_value is not None:
                return current_value
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.current",
            channel_sources=[
                ChannelSource(
                    label="current",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="Current",
                )
            ],
            transform=battery_current_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_status_mapping(self, n2k_devices: N2kDevices):
        """
        Register the status mapping
        """

        def battery_status_transform(values: dict, last_updated: dict) -> Optional[str]:
            current_value = MappingUtils.get_value_or_default(values, "current", None)

            state_of_charge_value = MappingUtils.get_value_or_default(
                values, "state_of_charge", None
            )
            if current_value is not None:
                if state_of_charge_value == 100:
                    return "charged"
                elif current_value <= 0.3:
                    return "discharging"
                else:
                    return "charging"
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.status",
            channel_sources=[
                ChannelSource(
                    label="current",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="Current",
                ),
                ChannelSource(
                    label="state_of_charge",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="StateOfCharge",
                ),
            ],
            transform=battery_status_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_temperature_mapping(self, n2k_devices: N2kDevices):
        """
        Register the temperature mapping
        """

        def battery_temperature_transform(
            values: dict, last_updated: dict
        ) -> Optional[float]:
            temperature_value = MappingUtils.get_value_or_default(
                values, "temperature", None
            )
            return temperature_value

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.temperature",
            channel_sources=[
                ChannelSource(
                    label="temperature",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="Temperature",
                )
            ],
            transform=battery_temperature_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_state_of_charge_mapping(self, n2k_devices: N2kDevices):
        """
        Register the state of charge mapping
        """

        def battery_state_of_charge_transform(
            values: dict, last_updated: dict
        ) -> Optional[float]:
            state_of_charge_value = MappingUtils.get_value_or_default(
                values, "state_of_charge", None
            )
            return state_of_charge_value

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.stateOfCharge",
            channel_sources=[
                ChannelSource(
                    label="state_of_charge",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="StateOfCharge",
                )
            ],
            transform=battery_state_of_charge_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_capacity_remaining_mapping(self, n2k_devices: N2kDevices):
        """
        Register the capacity remaining mapping
        """

        def battery_capacity_remaining_transform(
            values: dict, last_updated: dict
        ) -> Optional[float]:
            capacity_remaining_value = MappingUtils.get_value_or_default(
                values, "capacity_remaining", None
            )
            return capacity_remaining_value

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.capacityRemaining",
            channel_sources=[
                ChannelSource(
                    label="capacity_remaining",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="CapacityRemaining",
                )
            ],
            transform=battery_capacity_remaining_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_time_remaining_mapping(self, n2k_devices: N2kDevices):
        """
        Register the time remaining mapping
        """

        def battery_time_remaining_transform(
            values: dict, last_updated: dict
        ) -> Optional[float]:
            time_remaining_value = MappingUtils.get_value_or_default(
                values, "time_remaining", None
            )
            return time_remaining_value

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.timeRemaining",
            channel_sources=[
                ChannelSource(
                    label="time_remaining",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="TimeRemaining",
                )
            ],
            transform=battery_time_remaining_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_time_to_charge_mapping(self, n2k_devices: N2kDevices):
        """
        Register the time to charge mapping
        """

        def battery_time_to_charge_transform(
            values: dict, last_updated: dict
        ) -> Optional[float]:
            time_to_charge_value = MappingUtils.get_value_or_default(
                values, "time_to_charge", None
            )
            return time_to_charge_value

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.timeToCharge",
            channel_sources=[
                ChannelSource(
                    label="time_to_charge",
                    device_key=f"{JsonKeys.DC}.{self.instance}",
                    channel_key="TimeToCharge",
                )
            ],
            transform=battery_time_to_charge_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)
