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
from N2KClient.models.n2k_configuration.hvac import HVACDevice


class Climate(Thing):
    def __init__(
        self,
        hvac: HVACDevice,
        categories: list[str] = [],
    ):
        Thing.__init__(
            self,
            type=ThingType.CLIMATE,
            id=hvac.instance.instance,
            name=hvac.instance.name_utf8,
            categories=categories,
        )
