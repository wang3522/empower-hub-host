from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants
from .channel import Channel
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

        channels = []
        channels.extend(
            [
                Channel(
                    id="cs",
                    name="Component Status",
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    read_only=False,
                    tags=[
                        f"{Constants.empower}:{Constants.tank}.{Constants.componentStatus}"
                    ],
                ),
                Channel(
                    id="levelAbsolute",
                    name="Level Absolute",
                    read_only=True,
                    type=ChannelType.NUMBER,
                    unit=Unit.VOLUME_LITRE,
                    tags=[f"{Constants.empower}:{Constants.tank}.levelAbsolute"],
                ),
                Channel(
                    id="levelPercent",
                    name="Level Percent",
                    read_only=True,
                    type=ChannelType.NUMBER,
                    unit=Unit.PERCENT,
                    tags=[f"{Constants.empower}:{Constants.tank}.levelPercent"],
                ),
            ]
        )
        for channel in channels:
            self._define_channel(channel)


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
