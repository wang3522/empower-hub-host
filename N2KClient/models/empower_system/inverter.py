from typing import Optional, Dict, Any
from .thing import Thing
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.circuit import Circuit, SwitchType
from N2KClient.models.common_enums import ThingType
from .channel import Channel, ChannelType
from N2KClient.models.common_enums import Unit
from N2KClient.models.constants import Constants, JsonKeys
from N2KClient.models.n2k_configuration.inverter_charger import InverterChargerDevice
from N2KClient.services.config_processor.config_processor_helpers import (
    calculate_inverter_charger_instance,
)
from N2KClient.models.devices import (
    N2kDevice,
    ChannelSource,
    MobileChannelMapping,
    N2kDevices,
)


class MappingUtils:
    """
    Utility functions for working with mobile channel mappings.
    This class centralizes common mapping logic for Thing classes.
    """

    @staticmethod
    def get_value_or_default(values: dict, key: str, default=None):
        """Extract a value from a values dict, handling the Valid/Value nested structure."""
        v = values.get(key)
        if isinstance(v, dict) and v.get("Valid", False):
            return v.get("Value", default)
        return default

    @staticmethod
    def most_recent_valid(
        values: dict, last_updated: dict, labels: list
    ) -> Optional[tuple]:
        """
        Returns (timestamp, label, value) for the most recent valid value among the given labels.
        """
        most_recent = None
        for label in labels:
            value = MappingUtils.get_value_or_default(values, label, None)
            ts = last_updated.get(label, 0)
            if value is not None:
                if (most_recent is None) or (ts > most_recent[0]):
                    most_recent = (ts, label, value)
        return most_recent


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

        ac_meter_device = n2k_devices.devices.get(f"{JsonKeys.AC}.{AC.instance}.{line}")

        if not ac_meter_device:
            return

        # TODO add filtering/rounding to transform
        # Current
        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}l{line}c",
            channel_sources=[
                ChannelSource(
                    label=f"Current",
                    device_key=f"{JsonKeys.AC}.{ac.instance.instance}.{line}",
                    channel_key="Current",
                )
            ],
            transform=lambda c, _: MappingUtils.get_value_or_default(
                c, "Current", None
            ),
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

        # Voltage
        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}l{line}v",
            channel_sources=[
                ChannelSource(
                    label=f"Voltage",
                    device_key=f"{JsonKeys.AC}.{ac.instance.instance}.{line}",
                    channel_key="Voltage",
                )
            ],
            transform=lambda v, _: MappingUtils.get_value_or_default(
                v, "Voltage", None
            ),
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

        # Frequency
        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}l{line}v",
            channel_sources=[
                ChannelSource(
                    label=f"Frequency",
                    device_key=f"{JsonKeys.AC}.{ac.instance.instance}.{line}",
                    channel_key="Frequency",
                )
            ],
            transform=lambda f, _: MappingUtils.get_value_or_default(
                f, "Frequency", None
            ),
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

        # Power
        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}l{line}p",
            channel_sources=[
                ChannelSource(
                    label=f"Power",
                    device_key=f"{JsonKeys.AC}.{ac.instance.instance}.{line}",
                    channel_key="Power",
                )
            ],
            transform=lambda p, _: MappingUtils.get_value_or_default(p, "Power", None),
        )
        n2k_devices.add_mobile_channel_mapping(mapping)


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

        # Register mobile channel mappings if n2k_devices is provided
        if n2k_devices:
            self.register_mobile_channel_mappings(n2k_devices)

    def register_mobile_channel_mappings(self, n2k_devices: N2kDevices):
        """
        Register all mobile channel mappings for this inverter with the N2kDevices manager.
        """
        inverter_charger_device = n2k_devices.devices.get(
            f"{JsonKeys.INVERTER_CHARGER}.{self.instance}"
        )

        if not inverter_charger_device:
            return

        # Register enable mapping
        self._register_enable_mapping(n2k_devices)

        # Register state mapping
        self._register_state_mapping(n2k_devices)

    def _register_enable_mapping(self, n2k_devices: N2kDevices):
        """Register the enable channel mapping"""

        def inverter_enable_transform(
            values: dict, last_updated: dict
        ) -> Optional[int]:
            most_recent = MappingUtils.most_recent_valid(
                values, last_updated, ["inverter_enable", "circuit_power"]
            )
            if not most_recent:
                return None
            _, label, value = most_recent
            if label == "circuit_power":
                return 1 if value == 100 else 0
            if label == "inverter_enable":
                return 1 if value else 0
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.enable",
            channel_sources=[
                ChannelSource(
                    label="inverter_enable",
                    device_key=f"{JsonKeys.INVERTER_CHARGER}.{self.instance}",
                    channel_key="InverterEnable",
                )
            ],
            transform=inverter_enable_transform,
        )

        if self.inverter_circuit_id is not None:
            mapping.channel_sources.append(
                ChannelSource(
                    label="circuit_power",
                    device_key=f"{JsonKeys.CIRCUIT}.{self.inverter_circuit_id}",
                    channel_key="Level",
                )
            )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _register_state_mapping(self, n2k_devices: N2kDevices):
        """Register the inverter state channel mapping"""

        def inverter_state_transform(values: dict, last_updated: dict) -> Optional[str]:
            inverter_state_value = MappingUtils.get_value_or_default(
                values, "inverter_state", None
            )
            if inverter_state_value is not None:
                return self._map_inverter_state(inverter_state_value)
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{self.id}.is",
            channel_sources=[
                ChannelSource(
                    label="inverter_state",
                    device_key=f"{JsonKeys.INVERTER_CHARGER}.{self.instance}",
                    channel_key="InverterState",
                )
            ],
            transform=inverter_state_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def _map_inverter_state(self, state: str) -> str:
        """Map inverter state values to mobile-friendly strings"""
        return {
            JsonKeys.INVERTING: "inverting",
            JsonKeys.AC_PASSTHRU: "acPassthrough",
            JsonKeys.LOAD_SENSE: "loadSense",
            JsonKeys.FAULT: "fault",
            JsonKeys.DISABLED: "disabled",
            JsonKeys.CHARGING: "charging",
            JsonKeys.ENERGY_SAVING: "energySaving",
            JsonKeys.ENERGY_SAVING2: "energySaving",
            JsonKeys.SUPPORTING: "supporting",
            JsonKeys.SUPPORTING2: "supporting",
            JsonKeys.ERROR: "error",
            JsonKeys.DATA_NOT_AVAILABLE: "unknown",
        }.get(state, "unknown")
