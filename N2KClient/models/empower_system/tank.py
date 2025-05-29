from typing import Optional
from .thing import Thing
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ThingType
from ..constants import Constants
from .channel import Channel
from N2KClient.models.empower_system.ac_meter import ACMeterThingBase
from .link import Link
from N2KClient.models.n2k_configuration.tank import Tank
from ..common_enums import WaterTankType


class TankBase(Thing):

    def __init__(
        self,
        type: ThingType,
        tank: Tank,
        categories: list[str] = [],
        links: list[Link] = [],
    ):

        Thing.__init__(
            self,
            type,
            tank.instance.instance,
            tank.name_utf8,
            categories=categories,
            links=links,
        )

        if tank.tank_capacity is not None and tank.tank_capacity != 0:
            self.metadata[
                f"{Constants.empower}:{Constants.tank}.{Constants.capacity}"
            ] = tank.tank_capacity


class FuelTank(TankBase):

    def __init__(self, tank: Tank):
        TankBase.__init__(self, ThingType.FUEL_TANK, tank)


class WaterTank(TankBase):

    def __init__(
        self,
        tank: Tank,
        links: list[Link],
    ):
        TankBase.__init__(self, ThingType.WATER_TANK, tank, links=links)


class BlackWaterTank(WaterTank):
    def __init__(
        self,
        tank: Tank,
        links: list[Link],
    ):
        WaterTank.__init__(self, tank, links)

        self.metadata[f"{Constants.empower}:{Constants.tank}.{Constants.type}"] = (
            WaterTankType.BLACKWATER.value
        )


class WasteWaterTank(WaterTank):
    def __init__(
        self,
        tank: Tank,
        links: list[Link],
    ):
        WaterTank.__init__(self, tank, links)

        self.metadata[f"{Constants.empower}:{Constants.tank}.{Constants.type}"] = (
            WaterTankType.WASTEWATER.value
        )


class FreshWaterTank(WaterTank):
    def __init__(
        self,
        tank: Tank,
        links: list[Link],
    ):
        WaterTank.__init__(self, tank, links)

        self.metadata[f"{Constants.empower}:{Constants.tank}.{Constants.type}"] = (
            WaterTankType.FRESHWATER.value
        )
