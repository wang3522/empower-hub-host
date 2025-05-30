from typing import Optional
from .thing import Thing
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit, SwitchType
from N2KClient.models.common_enums import ThingType
from .channel import Channel, ChannelType
from N2KClient.models.common_enums import Unit
from N2KClient.models.constants import Constants
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.services.config_processor.config_processor_helpers import (
    calculate_inverter_charger_instance,
)


class InverterBase(Thing):

    def __init__(
        self,
        id: str,
        name: str,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
    ):
        Thing.__init__(
            self,
            type=ThingType.INVERTER,
            id=id,
            name=name,
            categories=categories,
            links=[],
        )

        channels = []

        if ac_line1 is not None:
            channels.extend(
                [
                    Channel(
                        id="l1cs",
                        name="Line 1 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="l1v",
                        name="Line 1 Voltage",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_VOLT,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="l1c",
                        name="Line 1 Current",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.current}"
                        ],
                    ),
                    Channel(
                        id="l1f",
                        name="Line 1 Frequency",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.FREQUENCY_HERTZ,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.frequency}"
                        ],
                    ),
                    Channel(
                        id="l1p",
                        name="Line 1 Power",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_WATT,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line1}.{Constants.power}"
                        ],
                    ),
                ]
            )
        if ac_line2 is not None:
            channels.extend(
                [
                    Channel(
                        id="l2cs",
                        name="Line 2 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="l2v",
                        name="Line 2 Voltage",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_VOLT,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="l2c",
                        name="Line 2 Current",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.current}"
                        ],
                    ),
                    Channel(
                        id="l2f",
                        name="Line 2 Frequency",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.FREQUENCY_HERTZ,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.frequency}"
                        ],
                    ),
                    Channel(
                        id="l2p",
                        name="Line 2 Power",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_WATT,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line2}.{Constants.power}"
                        ],
                    ),
                ]
            )

        if ac_line3 is not None:
            channels.extend(
                [
                    Channel(
                        id="l3cs",
                        name="Line 3 Component Status",
                        type=ChannelType.STRING,
                        unit=Unit.NONE,
                        read_only=False,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.componentStatus}"
                        ],
                    ),
                    Channel(
                        id="l3v",
                        name="Line 3 Voltage",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_VOLT,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.voltage}"
                        ],
                    ),
                    Channel(
                        id="l3c",
                        name="Line 3 Current",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_AMP,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.current}"
                        ],
                    ),
                    Channel(
                        id="l3f",
                        name="Line 3 Frequency",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.FREQUENCY_HERTZ,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.frequency}"
                        ],
                    ),
                    Channel(
                        id="l3p",
                        name="Line 3 Power",
                        read_only=True,
                        type=ChannelType.NUMBER,
                        unit=Unit.ENERGY_WATT,
                        tags=[
                            f"{Constants.empower}:{Constants.inverter}.{Constants.line3}.{Constants.power}"
                        ],
                    ),
                ]
            )

        channels.append(
            Channel(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.componentStatus}"
                ],
            )
        )

        for channel in channels:
            self._define_channel(channel)


class AcMeterInverter(InverterBase):

    def __init__(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
        circuit: Circuit,
    ):

        if circuit is not None:
            self.inverter_circuit_id = circuit.control_id
        InverterBase.__init__(
            self,
            id=ac_line1.instance.instance_,
            name=ac_line1.name_utf8,
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
        )

        self._define_channel(
            Channel(
                id="is",
                name="Inverter State",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=True,
                tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.state}"],
            )
        )

        if circuit is not None:
            self._define_channel(
                Channel(
                    id="ie",
                    name="Inverter Enable",
                    type=ChannelType.NUMBER,
                    unit=Unit.NONE,
                    read_only=(circuit.switch_type == SwitchType.Not_Set),
                    tags=[
                        f"{Constants.empower}:{Constants.inverter}.{Constants.enabled}"
                    ],
                )
            )


class CombiInverter(InverterBase):
    inverter_circuit_id: Optional[str] = None

    def __init__(
        self,
        inverter_charger: InverterChargerDevice,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
        status_ac_line: int,
        inverter_circuit: Optional[Circuit] = None,
    ):
        if inverter_circuit is not None:
            self.inverter_circuit_id = inverter_circuit.control_id

        InverterBase.__init__(
            self,
            id=calculate_inverter_charger_instance(inverter_charger),
            name=ac_line1.name_utf8 if ac_line1 else inverter_charger.name_utf8,
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
        )

        channels = [
            Channel(
                id="ie",
                name="Inverter Enabled",
                read_only=(
                    inverter_circuit == SwitchType.Not_Set
                    if inverter_circuit is not None
                    else True
                ),
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.enabled}"],
            ),
            Channel(
                id="is",
                name="Inverter State",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.inverter}.{Constants.state}"],
            ),
            Channel(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.inverter}.{Constants.componentStatus}"
                ],
            ),
        ]
