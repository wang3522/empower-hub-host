from typing import Optional
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..constants import Constants
from .channel import Channel
from ..common_enums import ChannelType, Unit


class Battery(Thing):
    battery_circuit_id: Optional[int] = None

    def __init__(
        self,
        battery: DC,
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
