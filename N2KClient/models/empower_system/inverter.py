from typing import Optional, Dict, Any
from .thing import Thing
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit, SwitchType
from N2KClient.models.common_enums import ThingType
from .channel import Channel, ChannelType
from N2KClient.models.common_enums import Unit
from N2KClient.models.constants import Constants
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.devices import (
    N2kDevice,
    N2kDevices,
)
from N2KClient.models.empower_system.mapping_utility import (
    RegisterMappingUtility,
)


class InverterBase(Thing):
    ac_line1: Optional[AC] = None
    ac_line2: Optional[AC] = None
    ac_line3: Optional[AC] = None

    def __init__(
        self,
        id: str,
        name: str,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
        status_ac_line: int,
        n2k_devices: Optional[N2kDevices] = None,
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
        # TODO Component Status, Talking to Krushit about sending the component status directly, instead of us determining it
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
            self.register_line_mobile_channel_mappings(n2k_devices, ac=ac_line1, line=1)

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
            self.register_line_mobile_channel_mappings(n2k_devices, ac=ac_line2, line=2)

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
            self.register_line_mobile_channel_mappings(n2k_devices, ac=ac_line3, line=3)

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

    def register_line_mobile_channel_mappings(
        self, n2k_devices: N2kDevices, ac: AC, line: int
    ):
        """
        Register mobile channel mappings for a specified AC line.
        """
        # Use the centralized RegisterMappingUtility to register all AC line mappings
        RegisterMappingUtility.register_ac_line_mappings(
            n2k_devices=n2k_devices,
            ac=ac,
            line=line,
            mobile_key_prefix=self.id,
        )


class AcMeterInverter(InverterBase):

    def __init__(
        self,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        n2k_devices: N2kDevice,
        categories: list[str],
        circuit: Circuit,
    ):

        if circuit is not None:
            self.inverter_circuit_id = circuit.control_id
        InverterBase.__init__(
            self,
            id=ac_line1.instance.instance,
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
        RegisterMappingUtility.register_ac_meter_inverter_state_mapping(
            n2k_devices=n2k_devices,
            thing_id=self.id,
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
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

            RegisterMappingUtility.register_inverter_enable_mapping(
                n2k_devices=n2k_devices,
                thing_id=self.id,
                instance=ac_line1.instance.instance,
                inverter_circuit_id=self.inverter_circuit_id,
            )


class CombiInverter(InverterBase):
    inverter_circuit_id: Optional[str] = None
    instance: int

    def __init__(
        self,
        inverter_charger: InverterChargerDevice,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
        categories: list[str],
        instance: int,
        status_ac_line: int,
        inverter_circuit: Optional[Circuit] = None,
        n2k_devices: Optional[N2kDevices] = None,
    ):
        self.instance = instance
        if inverter_circuit is not None:
            self.inverter_circuit_id = inverter_circuit.control_id

        InverterBase.__init__(
            self,
            id=instance,
            name=ac_line1.name_utf8 if ac_line1 else inverter_charger.name_utf8,
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=categories,
            n2k_devices=n2k_devices,
            status_ac_line=status_ac_line,
        )

        # Define CombiInverter specific channels
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

        RegisterMappingUtility.register_inverter_state_mapping(
            n2k_devices=n2k_devices, thing_id=self.id, instance=self.instance
        )

        self._define_channel(
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

        if inverter_circuit is not None:
            self._define_channel(
                Channel(
                    id="ie",
                    name="Inverter Enable",
                    type=ChannelType.NUMBER,
                    unit=Unit.NONE,
                    read_only=(inverter_circuit.switch_type == SwitchType.Not_Set),
                    tags=[
                        f"{Constants.empower}:{Constants.inverter}.{Constants.enabled}"
                    ],
                )
            )
            RegisterMappingUtility.register_inverter_enable_mapping(
                n2k_devices=n2k_devices,
                thing_id=self.id,
                instance=self.instance,
                inverter_circuit_id=self.inverter_circuit_id,
            )
