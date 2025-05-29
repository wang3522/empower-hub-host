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

        if battery_circuit is not None:
            self.battery_circuit_id = battery_circuit.instance.instance

        if fallback_battery is not None:
            self.fallback_battery = fallback_battery

        if primary_battery is not None:
            self.primary_battery = primary_battery

        if battery.capacity is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.battery}.{Constants.capacity}"
            ] = battery.capacity
