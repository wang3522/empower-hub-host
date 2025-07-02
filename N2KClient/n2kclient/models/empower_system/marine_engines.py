from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants
from .channel import Channel
from ..n2k_configuration.engine import EngineDevice, EngineType


def _map_engine_type(type: EngineType) -> str:
    return {
        EngineType.NMEA2000: Constants.nmea2000,
        EngineType.SmartCraft: Constants.smartcraft,
    }[type] or Constants.unknown


class MarineEngine(Thing):
    def __init__(self, engine: EngineDevice, categories: list[str] = []):
        Thing.__init__(
            self,
            ThingType.MARINE_ENGINE,
            engine.instance.instance,
            engine.name_utf8,
            categories=categories,
        )

        if engine.engine_type is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.engineType}"
            ] = _map_engine_type(engine.engine_type)

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
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.componentStatus}"
                    ],
                ),
                Channel(
                    id="speed",
                    name="Speed",
                    type=ChannelType.NUMBER,
                    unit=Unit.ROTATIONAL_SPEED_REVOLUTIONS_PER_MINUTE,
                    read_only=True,
                    tags=[
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.speed}"
                    ],
                ),
                Channel(
                    id="engineHours",
                    name="EngineHours",
                    read_only=True,
                    type=ChannelType.NUMBER,
                    unit=Unit.TIME_HOUR,
                    tags=[
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.engineHours}"
                    ],
                ),
                Channel(
                    id="coolantTemperature",
                    name="CoolantTemperature",
                    type=ChannelType.NUMBER,
                    unit=Unit.TEMPERATURE_CELSIUS,
                    read_only=True,
                    tags=[
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.coolantTemperature}"
                    ],
                ),
                Channel(
                    id="coolantPressure",
                    name="Coolant Pressure",
                    read_only=True,
                    type=ChannelType.NUMBER,
                    unit=Unit.PRESSURE_KILOPASCAL,
                    tags=[
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.coolantPressure}"
                    ],
                ),
                Channel(
                    id="oilPressure",
                    name="Oil Pressure",
                    type=ChannelType.NUMBER,
                    unit=Unit.PRESSURE_KILOPASCAL,
                    read_only=True,
                    tags=[
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.oilPressure}"
                    ],
                ),
                Channel(
                    id="serialNumber",
                    name="Serial Number",
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    read_only=True,
                    tags=[
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.serialNumber}"
                    ],
                ),
                Channel(
                    id="status",
                    name="Status",
                    read_only=True,
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    tags=[
                        f"{Constants.empower}:{Constants.marineEngine}.{Constants.status}"
                    ],
                ),
            ]
        )

        for channel in channels:
            self._define_channel(channel)

        # pressureGain = 1
        # if engine.engine_type == EngineType.SmartCraft:
        #     pressureGain = 0.01
        # elif engine.engine_type == EngineType.NMEA2000:
        #     pressureGain = 0.001
