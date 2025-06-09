from typing import Optional

from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.empower_system.inverter import MappingUtils
from .thing import Thing
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.circuit import Circuit
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants, JsonKeys
from .channel import Channel
from N2KClient.models.empower_system.ac_meter import ACMeterThingBase
from N2KClient.services.config_processor.config_processor_helpers import (
    calculate_inverter_charger_instance,
)


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
            self.register_dc_line_channel_mappings(n2k_devices, dc1, 1)
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
            self.register_dc_line_channel_mappings(n2k_devices, dc2, 2)
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
            self.register_dc_line_channel_mappings(n2k_devices, dc3, 3)
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

    def register_dc_line_channel_mappings(
        self, n2k_devices: N2kDevices, dc: DC, line: int
    ):
        """
        Register mappings for DC line channels to the mobile channel mapper.
        """

        dc_meter_device = n2k_devices.devices.get(
            f"{JsonKeys.DC}.{dc.instance.instance}"
        )
        if not dc_meter_device:
            return

        # Voltage

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.dc.{line}.v",
            channel_sources=[
                ChannelSource(
                    label="Voltage",
                    device_key=f"{JsonKeys.DC}.{dc.instance.instance}",
                    channel_key="Voltage",
                ),
            ],
            transform=lambda v, _: MappingUtils.get_value_or_default(
                v, "Voltage", None
            ),
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

        # Current
        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.dc.{line}.c",
            channel_sources=[
                ChannelSource(
                    label="Current",
                    device_key=f"{JsonKeys.DC}.{dc.instance.instance}",
                    channel_key="Current",
                ),
            ],
            transform=lambda c, _: MappingUtils.get_value_or_default(
                c, "Current", None
            ),
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def register_mobile_channel_mobile_mappings(self, n2k_devices: N2kDevices):
        """
        Register mobile channel mappings for the charger
        """
        dc_meter_device = n2k_devices.devices.get(
            f"{JsonKeys.INVERTER_CHARGER}.{self.instance}"
        )
        if not dc_meter_device:
            return

        # Register enable mapping
        self._register_enable_mapping(n2k_devices)

        # Register state mapping
        self._register_state_mapping(n2k_devices)

    def _register_enable_mapping(self, n2k_devices: N2kDevices):
        """Register the enable channel mapping"""

        def charger_enable_transform(values: dict, last_updated: dict) -> Optional[int]:
            most_recent = MappingUtils.most_recent_valid(
                values, last_updated, ["charger_enable", "circuit_power"]
            )
            if not most_recent:
                return None
            _, label, value = most_recent
            if label == "circuit_power":
                return 1 if value == 100 else 0
            if label == "charger_enable":
                return 1 if value else 0
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.enable",
            channel_sources=[
                ChannelSource(
                    label="charger_enable",
                    device_key=f"{JsonKeys.INVERTER_CHARGER}.{self.instance}",
                    channel_key="ChargerEnable",
                )
            ],
            transform=charger_enable_transform,
        )

        if self.charger_circuit is not None:
            mapping.channel_sources.append(
                ChannelSource(
                    label="circuit_power",
                    device_key=f"{JsonKeys.CIRCUIT}.{self.charger_circuit}",
                    channel_key="Level",
                )
            )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_state_mapping(self, n2k_devices: N2kDevices):
        """Register the state channel mapping"""

        def charger_state_transform(values: dict, last_updated: dict) -> Optional[str]:
            charger_state_value = MappingUtils.get_value_or_default(
                values, "charger_state", None
            )
            if charger_state_value is not None:
                return self._map_charger_state(charger_state_value)
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.cst",
            channel_sources=[
                ChannelSource(
                    label="charger_state",
                    device_key=f"{JsonKeys.INVERTER_CHARGER}.{self.instance}",
                    channel_key="ChargerState",
                )
            ],
            transform=charger_state_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _map_charger_state(self, state: str) -> str:
        """Map charger state values to mobile-friendly strings"""
        return {
            JsonKeys.ABSORPTION: "absorption",
            JsonKeys.BULK: "bulk",
            JsonKeys.CONSTANTVI: "constantVI",
            JsonKeys.NOTCHARGING: "notCharging",
            JsonKeys.EQUALIZE: "equalize",
            JsonKeys.OVERCHARGE: "overcharge",
            JsonKeys.FLOAT: "float",
            JsonKeys.NOFLOAT: "noFloat",
            JsonKeys.FAULT: "fault",
            JsonKeys.DISABLED: "disabled",
        }.get(state, "unknown")


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
