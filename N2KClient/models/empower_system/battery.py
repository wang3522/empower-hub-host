from typing import Optional

from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.empower_system.mapping_utility import (
    MappingUtils,
    RegisterMappingUtility,
)
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
        self.instance = battery.instance.instance

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
            RegisterMappingUtility.register_enable_mapping(
                n2k_devices=n2k_devices,
                thing_id=self.id,
                circuit_id=self.battery_circuit_id,
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
            # Register voltage mapping
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices=n2k_devices,
                mobile_key=f"{self.id}.voltage",
                device_key=f"{JsonKeys.DC}.{self.instance}",
                channel_key="Voltage",
                label="voltage",
            )
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
            # Register current mapping
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices=n2k_devices,
                mobile_key=f"{self.id}.current",
                device_key=f"{JsonKeys.DC}.{self.instance}",
                channel_key="Current",
                label="current",
            )

            # Register status mapping
            def battery_status_transform(
                values: dict, last_updated: dict
            ) -> Optional[str]:
                current_value = MappingUtils.get_value_or_default(
                    values, "current", None
                )
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
            # Register temperature mapping
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices=n2k_devices,
                mobile_key=f"{self.id}.temperature",
                device_key=f"{JsonKeys.DC}.{self.instance}",
                channel_key="Temperature",
                label="temperature",
            )
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
            # Register state of charge mapping
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices=n2k_devices,
                mobile_key=f"{self.id}.stateOfCharge",
                device_key=f"{JsonKeys.DC}.{self.instance}",
                channel_key="StateOfCharge",
                label="stateofcharge",
            )
            # Register capacity remaining mapping
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices=n2k_devices,
                mobile_key=f"{self.id}.capacityRemaining",
                device_key=f"{JsonKeys.DC}.{self.instance}",
                channel_key="CapacityRemaining",
                label="capacityremaining",
            )
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
            # Register time remaining mapping
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices=n2k_devices,
                mobile_key=f"{self.id}.timeRemaining",
                device_key=f"{JsonKeys.DC}.{self.instance}",
                channel_key="TimeRemaining",
                label="timeremaining",
            )
            # Register time to charge mapping
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices=n2k_devices,
                mobile_key=f"{self.id}.timeToCharge",
                device_key=f"{JsonKeys.DC}.{self.instance}",
                channel_key="TimeToCharge",
                label="timetocharge",
            )

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
