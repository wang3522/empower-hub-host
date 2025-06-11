from typing import Optional

from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.mapping_utility import (
    RegisterMappingUtility,
)
from .thing import Thing
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants
from .channel import Channel
from N2KClient.models.empower_system.ac_meter import ACMeterThingBase


class CombiCharger(Thing):
    instance: int

    def __init__(
        self,
        inverter_charger: InverterChargerDevice,
        dc1: DC,
        dc2: DC,
        dc3: DC,
        categories: list[str],
        instance: int,
        n2k_devices: N2kDevices,
        charger_circuit: Optional[Circuit] = None,
    ):
        if charger_circuit is not None:
            self.charger_circuit = charger_circuit.control_id

        Thing.__init__(
            self,
            type=ThingType.CHARGER,
            id=instance,
            name=inverter_charger.name_utf8,
            categories=categories,
        )
        self.instance = instance

        # TODO Component Status for charger
        channels = []
        if dc1 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.name}"
            ] = dc1.name_utf8

            channels.extend(
                [
                    Channel(
                        id="dc1cs",
                        name=" Battery 1 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="dc1v",
                        name="Battery 1 Voltage",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="dc1c",
                        name="Battery 1 Current",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery1}.{Constants.current}"
                        ],
                    ),
                ]
            )

            RegisterMappingUtility.register_dc_line_mappings(
                n2k_devices=n2k_devices,
                dc=dc1,
                mobile_key_prefix=self.id,
                line=1,
            )

        if dc2 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.name}"
            ] = dc2.name_utf8

            channels.extend(
                [
                    Channel(
                        id="dc2cs",
                        name=" Battery 2 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="dc2v",
                        name="Battery 2 Voltage",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="dc2c",
                        name="Battery 2 Current",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery2}.{Constants.current}"
                        ],
                    ),
                ]
            )
            RegisterMappingUtility.register_dc_line_mappings(
                n2k_devices=n2k_devices,
                dc=dc2,
                mobile_key_prefix=self.id,
                line=2,
            )

        if dc3 is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.name}"
            ] = dc3.name_utf8

            channels.extend(
                [
                    Channel(
                        id="dc3cs",
                        name=" Battery 3 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="dc3v",
                        name="Battery 3 Voltage",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="dc3c",
                        name="Battery 3 Current",
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.charger}.{Constants.battery3}.{Constants.current}"
                        ],
                    ),
                ]
            )
            RegisterMappingUtility.register_dc_line_mappings(
                n2k_devices=n2k_devices,
                dc=dc3,
                mobile_key_prefix=self.id,
                line=3,
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
                        f"{Constants.empower}:{Constants.charger}.{Constants.componentStatus}"
                    ],
                ),
                Channel(
                    id="ce",
                    name="Charger Enabled",
                    read_only=(
                        charger_circuit.switch_type == 0
                        if charger_circuit is not None
                        else True
                    ),
                    type=ChannelType.NUMBER,
                    unit=Unit.NONE,
                    tags=[f"{Constants.empower}:{Constants.charger}.enabled"],
                ),
                Channel(
                    id="cst",
                    name="Charger Status",
                    read_only=True,
                    type=ChannelType.STRING,
                    unit=Unit.NONE,
                    tags=[f"{Constants.empower}:{Constants.charger}.status"],
                ),
            ]
        )
        for channel in channels:
            self._define_channel(channel)

        RegisterMappingUtility.register_charger_enable_mapping(
            n2k_devices=n2k_devices,
            thing_id=self.id,
            charger_circuit=(
                charger_circuit.control_id if charger_circuit is not None else None
            ),
            instance=instance,
        )

        RegisterMappingUtility.register_charger_state_mapping(
            n2k_devices=n2k_devices,
            instance=instance,
            thing_id=self.id,
        )


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
