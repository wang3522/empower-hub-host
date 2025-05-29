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


class CombiCharger(Thing):

    def __init__(
        self,
        inverter_charger: InverterChargerDevice,
        dc1: DC,
        dc2: DC,
        dc3: DC,
        categories: list[str],
        charger_circuit: Optional[Circuit] = None,
    ):
        if charger_circuit is not None:
            self.charger_circuit = charger_circuit.control_id

        Thing.__init__(
            self,
            type=ThingType.CHARGER,
            name=inverter_charger.name_utf8,
            categories=categories,
        )

        if dc1 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.name}"
            ] = dc1.name_utf8
        if dc2 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.name}"
            ] = dc2.name_utf8
        if dc3 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.name}"
            ] = dc3.name_utf8


class ACMeterCharger(ACMeterThingBase):
    def __init__(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
        circuit: Optional[Circuit] = None,
    ):
        if circuit is not None:
            self.charger_circuit = circuit.control_id

        ACMeterThingBase.__init__(
            self, ThingType.CHARGER, ac_line1, ac_line2, ac_line3, categories
        )
