"""
Centralized mapping utility for Thing classes.
This module provides common mapping functions and utilities to reduce code duplication
across the empower_system classes.
"""

from typing import Any, Optional
from N2KClient.models.devices import ChannelSource, MobileChannelMapping, N2kDevices
from N2KClient.models.n2k_configuration.ac import AC
from N2KClient.models.n2k_configuration.dc import DC
from N2KClient.models.n2k_configuration.binary_logic_state import BinaryLogicState
from N2KClient.models.constants import JsonKeys


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


class RegisterMappingUtility:
    """
    Utility class for registering common mappings used across different Thing classes.
    """

    #############################################################################
    # STATE MAPPING CONSTANTS
    #############################################################################

    # Inverter state mapping dictionary
    INVERTER_STATE_MAPPING = {
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
    }

    # Charger state mapping dictionary
    CHARGER_STATE_MAPPING = {
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
    }

    #############################################################################
    # AC COMPONENT MAPPING METHODS
    #############################################################################

    @staticmethod
    def register_ac_line_mappings(
        n2k_devices: N2kDevices,
        ac: AC,
        line: int,
        mobile_key_prefix: str,
        ic_associated_line: Optional[int] = None,
    ):
        """
        Register standard AC line mobile channel mappings (voltage, current, frequency, power).

        Args:
            n2k_devices: The N2kDevices object to register the mappings with
            ac: The AC configuration
            line: The line number (1, 2, or 3)
            mobile_key_prefix: The prefix to use for the mobile key (usually the thing's ID)
            ic_associated_line: Optional line number associated with an inverter charger
        """
        # Check if the device exists
        ac_meter_device = n2k_devices.devices.get(
            f"{JsonKeys.AC}.{ac.instance.instance}"
        )
        if not ac_meter_device:
            return

        # Voltage
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{mobile_key_prefix}l{line}v",
            device_key=f"{JsonKeys.AC}.{ac.instance.instance}",
            channel_key=f"line{line}.Voltage",
            label="Voltage",
        )

        # Current
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{mobile_key_prefix}l{line}c",
            device_key=f"{JsonKeys.AC}.{ac.instance.instance}",
            channel_key=f"line{line}.Current",
            label="Current",
        )

        # Frequency
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{mobile_key_prefix}l{line}f",
            device_key=f"{JsonKeys.AC}.{ac.instance.instance}",
            channel_key=f"line{line}.Frequency",
            label="Frequency",
        )

        # Power
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{mobile_key_prefix}l{line}p",
            device_key=f"{JsonKeys.AC}.{ac.instance.instance}",
            channel_key=f"line{line}.Power",
            label="Power",
        )

        # Component Status
        if ic_associated_line is not None and line == ic_associated_line:
            # If this is the line associated with the Inverter Charger, use that inverter charger's component status
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices,
                mobile_key=f"{mobile_key_prefix}l{line}cs",
                device_key=f"{JsonKeys.INVERTER_CHARGERS}.{ic_associated_line}",
                channel_key=f"line{line}.ComponentStatus",
                label="Component Status",
            )
        else:
            RegisterMappingUtility.register_simple_mapping(
                n2k_devices,
                mobile_key=f"{mobile_key_prefix}l{line}cs",
                device_key=f"{JsonKeys.AC}.{ac.instance.instance}",
                channel_key=f"line{line}.ComponentStatus",
                label="Component Status",
            )

    @staticmethod
    def register_ac_meter_component_status_mapping(
        n2k_devices: N2kDevices,
        mobile_key_prefix: str,
        ac_instance: int,
        ic_associated_line: Optional[int] = None,
    ):
        """
        Register a component status mapping that checks all AC lines.

        Args:
            n2k_devices: The N2kDevices object to register the mapping with
            mobile_key_prefix: The prefix to use for the mobile key (usually the thing's ID)
            ac: The AC configuration
            ic_associated_line: Optional line number associated with an inverter charger
        """
        # Build list of channel sources for all AC lines
        channel_sources = []

        # Add component status sources for each line
        for line in range(1, 4):
            if ic_associated_line is not None and line == ic_associated_line:
                # If this line is associated with an inverter charger, use the inverter charger's component status
                channel_sources.append(
                    ChannelSource(
                        label=f"line{line}_status",
                        device_key=f"{JsonKeys.INVERTER_CHARGERS}.{ic_associated_line}",
                        channel_key=f"line{line}.ComponentStatus",
                    )
                )
            else:
                # Otherwise use the AC meter's line component status
                channel_sources.append(
                    ChannelSource(
                        label=f"line{line}_status",
                        device_key=f"{JsonKeys.AC}.{ac.instance.instance}",
                        channel_key=f"line{line}.ComponentStatus",
                    )
                )

        def component_status_transform(values: dict, last_updated: dict):
            # Check if any line is connected
            line1_connected = MappingUtils.get_value_or_default(
                values, "line1_status", False
            )
            line2_connected = MappingUtils.get_value_or_default(
                values, "line2_status", False
            )
            line3_connected = MappingUtils.get_value_or_default(
                values, "line3_status", False
            )

            # If any line is connected, use "Connected", otherwise "Disconnected"
            any_line_connected = line1_connected or line2_connected or line3_connected

            # Return appropriate status based on line connection
            if any_line_connected:
                return "Connected"
            else:
                return "Disconnected"

        mapping = MobileChannelMapping(
            mobile_key=f"{mobile_key_prefix}cs",
            channel_sources=channel_sources,
            transform=component_status_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    # TODO Fix BLS value for shorepower connected state, see what is reported from dbus server test with Krushit. Old logic may not apply
    @staticmethod
    def register_shorepower_connected_mappings(
        n2k_devices: N2kDevices,
        thing_id: str,
        bls: BinaryLogicState,
        ac_line1: Optional[AC],
        ac_line2: Optional[AC],
        ac_line3: Optional[AC],
        ic_associated_line: Optional[int],
    ):
        """
        Register mappings for Binary Logic State channels with AC line sources.
        This merges BLS state with AC line data to determine connection status.

        Args:
            n2k_devices: The N2kDevices object to register the mappings with
            thing_id: The ID of the Thing
            bls: The Binary Logic State object
            ac_line1: AC configuration for line 1
            ac_line2: AC configuration for line 2
            ac_line3: AC configuration for line 3
            ic_associated_line: Optional line number associated with an inverter charger
        """
        # Create connection state mapping that incorporates BLS state with all AC line sources
        # This way we get direct access to all sources rather than trying to access the cached value

        # For inverter/charger we need component status sources
        if ic_associated_line is not None:
            # Collect all the AC line component status sources
            channel_sources = []

            if bls is not None:
                # Add BLS state source
                channel_sources.append(
                    ChannelSource(
                        label="bls_connection_state",
                        device_key=f"{JsonKeys.BINARY_LOGIC_STATE}.{bls.address}",
                        channel_key="State",
                    )
                )

            # Add the AC line sources
            if ac_line1 is not None:
                channel_sources.append(
                    ChannelSource(
                        label="line1_connected",
                        device_key=f"{JsonKeys.AC}.{ac_line1.instance.instance}.1",
                        channel_key="ComponentStatus",
                    )
                )

            if ac_line2 is not None:
                channel_sources.append(
                    ChannelSource(
                        label="line2_connected",
                        device_key=f"{JsonKeys.AC}.{ac_line2.instance.instance}.2",
                        channel_key="ComponentStatus",
                    )
                )

            if ac_line3 is not None:
                channel_sources.append(
                    ChannelSource(
                        label="line3_connected",
                        device_key=f"{JsonKeys.AC}.{ac_line3.instance.instance}.3",
                        channel_key="ComponentStatus",
                    )
                )

            def bls_inverter_charger_transform(values: dict, last_updated: dict):
                # Get BLS state
                bls_connection_state = MappingUtils.get_value_or_default(
                    values, "bls_connection_state", None
                )

                # Get AC line states
                line1_connected = MappingUtils.get_value_or_default(
                    values, "line1_connected", False
                )
                line2_connected = MappingUtils.get_value_or_default(
                    values, "line2_connected", False
                )
                line3_connected = MappingUtils.get_value_or_default(
                    values, "line3_connected", False
                )

                # Determine connected state from AC lines
                ac_lines_connected = (
                    line1_connected or line2_connected or line3_connected
                )

                # Get timestamps
                bls_timestamp = last_updated.get("bls_connection_state", 0)

                # Use latest line timestamp
                line_timestamps = [
                    last_updated.get("line1_connected", 0),
                    last_updated.get("line2_connected", 0),
                    last_updated.get("line3_connected", 0),
                ]
                ac_timestamp = max(line_timestamps) if line_timestamps else 0

                # Use BLS if it's available and more recent
                if bls_connection_state is not None and bls_timestamp >= ac_timestamp:
                    return bls_connection_state == 1

                # Otherwise use AC line connected state
                return ac_lines_connected

            # Create the mapping that combines BLS with AC line sources
            connected_mapping = MobileChannelMapping(
                mobile_key=f"{thing_id}.connected",
                channel_sources=channel_sources,
                transform=bls_inverter_charger_transform,
            )

        # For non-inverter/charger we need voltage sources
        else:
            # Collect all voltage sources plus BLS
            channel_sources = []

            if bls is not None:
                # Add BLS state source
                channel_sources.append(
                    ChannelSource(
                        label="bls_connection_state",
                        device_key=f"{JsonKeys.BINARY_LOGIC_STATE}.{bls.address}",
                        channel_key="State",
                    )
                )

            # Add the voltage sources
            if ac_line1 is not None:
                channel_sources.append(
                    ChannelSource(
                        label="ac_line1_voltage",
                        device_key=f"{JsonKeys.AC}.{ac_line1.instance.instance}.1",
                        channel_key="Voltage",
                    )
                )

            if ac_line2 is not None:
                channel_sources.append(
                    ChannelSource(
                        label="ac_line2_voltage",
                        device_key=f"{JsonKeys.AC}.{ac_line2.instance.instance}.2",
                        channel_key="Voltage",
                    )
                )

            if ac_line3 is not None:
                channel_sources.append(
                    ChannelSource(
                        label="ac_line3_voltage",
                        device_key=f"{JsonKeys.AC}.{ac_line3.instance.instance}.3",
                        channel_key="Voltage",
                    )
                )

            def bls_non_inverter_charger_transform(values: dict, last_updated: dict):
                # Get BLS state
                connection_state = MappingUtils.get_value_or_default(
                    values, "bls_connection_state", None
                )

                # Get AC line voltages
                ac_line1_voltage = MappingUtils.get_value_or_default(
                    values, "ac_line1_voltage", 0
                )
                ac_line2_voltage = MappingUtils.get_value_or_default(
                    values, "ac_line2_voltage", 0
                )
                ac_line3_voltage = MappingUtils.get_value_or_default(
                    values, "ac_line3_voltage", 0
                )

                # Determine connected state from AC voltages
                ac_voltage_connected = (
                    ac_line1_voltage > 0 or ac_line2_voltage > 0 or ac_line3_voltage > 0
                )

                # Get timestamps
                bls_timestamp = last_updated.get("bls_connection_state", 0)

                # Use latest voltage timestamp
                voltage_timestamps = [
                    last_updated.get("ac_line1_voltage", 0),
                    last_updated.get("ac_line2_voltage", 0),
                    last_updated.get("ac_line3_voltage", 0),
                ]
                ac_timestamp = max(voltage_timestamps) if voltage_timestamps else 0

                # Use BLS if it's available and more recent
                if connection_state is not None and bls_timestamp >= ac_timestamp:
                    # Here is where we will do bitmapping logic for BLS
                    return connection_state == 1

                # Otherwise use AC voltage connected state
                return ac_voltage_connected

            # Create the mapping that combines BLS with AC voltage sources
            connected_mapping = MobileChannelMapping(
                mobile_key=f"{thing_id}.connected",
                channel_sources=channel_sources,
                transform=bls_non_inverter_charger_transform,
            )

        # Add the final combined mapping
        n2k_devices.add_mobile_channel_mapping(connected_mapping)

    #############################################################################
    # DC COMPONENT MAPPING METHODS
    #############################################################################

    @staticmethod
    def register_dc_line_mappings(
        n2k_devices: N2kDevices,
        dc: DC,
        mobile_key_prefix: str,
        line: Optional[int] = None,
    ):
        # Check if the device exists
        dc_meter_device = n2k_devices.devices.get(
            f"{JsonKeys.DC}.{dc.instance.instance}"
        )
        if not dc_meter_device:
            return

        # Define the key prefix based on whether a line is provided
        key_suffix = f".dc.{line}" if line is not None else ""

        # Voltage
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{mobile_key_prefix}{key_suffix}.voltage",
            device_key=f"{JsonKeys.DC}.{dc.instance.instance}",
            channel_key="Voltage",
            label="Voltage",
        )

        # Current
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{mobile_key_prefix}{key_suffix}.current",
            device_key=f"{JsonKeys.DC}.{dc.instance.instance}",
            channel_key="Current",
            label="Current",
        )

    #############################################################################
    # CORE MAPPING UTILITIES
    #############################################################################

    @staticmethod
    def register_simple_mapping(
        n2k_devices: N2kDevices,
        mobile_key: str,
        device_key: str,
        channel_key: str,
        label: str,
    ):
        """
        Register a simple channel mapping that applies to both AC and DC channels.

        Args:
            n2k_devices: The N2kDevices object to register the mapping with
            mobile_key: The mobile key for the mapping
            device_key: The device key
            channel_key: The channel key
            label: The label for the channel source
        """
        mapping = MobileChannelMapping(
            mobile_key=mobile_key,
            channel_sources=[
                ChannelSource(
                    label=label,
                    device_key=device_key,
                    channel_key=channel_key,
                )
            ],
            transform=lambda v, _: MappingUtils.get_value_or_default(v, label, None),
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    @staticmethod
    def register_enable_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        circuit_id: int,
    ):
        """
        Register an enable/disable mapping for components that have enable controls.

        Args:
            n2k_devices: The N2kDevices object to register the mappings with
            thing_id: The ID of the Thing
            circuit_id: The ID of the circuit that controls enable/disable
            device_key_prefix: The prefix for the device key (default: JsonKeys.CIRCUIT)
            channel_key: The channel key to read (default: "Level")
        """

        def enable_transform(values: dict, last_updated: dict) -> Optional[bool]:
            enable_value = MappingUtils.get_value_or_default(
                values, "circuit_power", None
            )
            if enable_value is not None:
                return enable_value > 0
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{thing_id}.enabled",
            channel_sources=[
                ChannelSource(
                    label="circuit_power",
                    device_key=f"{JsonKeys.CIRCUIT}.{circuit_id}",
                    channel_key="Level",
                )
            ],
            transform=enable_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    #############################################################################
    # LOCATION MAPPING METHODS
    #############################################################################

    @staticmethod
    def register_location_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        device_key: str,
        location_state_class: Any,
    ):
        """
        Register a mapping for location data from a GNSS device.

        Args:
            n2k_devices: The N2kDevices object to register the mappings with
            thing_id: The ID of the Thing
            device_key: The device key (e.g., JsonKeys.GNSS.{instance})
            location_state_class: The LocationState class to use for creating location objects
        """

        def location_transform(values: dict, last_updated: dict):
            lat_value = MappingUtils.get_value_or_default(values, "lat", None)
            long_value = MappingUtils.get_value_or_default(values, "long", None)
            sog_value = MappingUtils.get_value_or_default(values, "sog", None)
            return location_state_class(lat_value, long_value, sog_value)

        mapping = MobileChannelMapping(
            mobile_key=f"{thing_id}.loc",
            channel_sources=[
                ChannelSource(
                    label="lat",
                    device_key=device_key,
                    channel_key="LatitudeDeg",
                ),
                ChannelSource(
                    label="long",
                    device_key=device_key,
                    channel_key="LongitudeDeg",
                ),
                ChannelSource(
                    label="sog",
                    device_key=device_key,
                    channel_key="SOG",
                ),
            ],
            transform=location_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    #############################################################################
    # CHARGER MAPPING METHODS
    #############################################################################

    @staticmethod
    def register_charger_enable_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        instance: str,
        charger_circuit: Optional[int] = None,
    ):
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
            mobile_key=f"{thing_id}.ce",
            channel_sources=[
                ChannelSource(
                    label="charger_enable",
                    device_key=f"{JsonKeys.INVERTER_CHARGER}.{instance}",
                    channel_key="ChargerEnable",
                )
            ],
            transform=charger_enable_transform,
        )

        if charger_circuit is not None:
            mapping.channel_sources.append(
                ChannelSource(
                    label="circuit_power",
                    device_key=f"{JsonKeys.CIRCUIT}.{charger_circuit}",
                    channel_key="Level",
                )
            )
        n2k_devices.add_mobile_channel_mapping(mapping)

    @staticmethod
    def register_charger_state_mapping(
        n2k_devices: N2kDevices, thing_id: str, instance: int
    ):
        """
        Register a charger state mapping that transforms state values into user-friendly strings.

        Args:
            n2k_devices: The N2kDevices object to register the mappings with
            thing_id: The ID of the Thing
            instance: The instance ID of the charger
            mobile_key: The suffix for the mobile key (default: "cst" for charger state)
        """

        def charger_state_transform(values: dict, last_updated: dict) -> Optional[str]:
            state_value = MappingUtils.get_value_or_default(
                values, "charger_state", None
            )
            if state_value is not None:
                return RegisterMappingUtility.CHARGER_STATE_MAPPING.get(
                    state_value, "unknown"
                )
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{thing_id}.cst",
            channel_sources=[
                ChannelSource(
                    label="charger_state",
                    device_key=f"{JsonKeys.INVERTER_CHARGER}.{instance}",
                    channel_key="ChargerState",
                )
            ],
            transform=charger_state_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def register_ac_meter_charger_state_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        ac_line1: AC,
        ac_line2: AC,
        ac_line3: AC,
    ):

        channel_sources = []

        if ac_line1 is not None:
            channel_sources.append(
                ChannelSource(
                    label="line1_connected",
                    device_key=f"{JsonKeys.AC}.{ac_line1.instance.instance}",
                    channel_key="line1.ComponentStatus",
                )
            )
        if ac_line2 is not None:
            channel_sources.append(
                ChannelSource(
                    label="line2_connected",
                    device_key=f"{JsonKeys.AC}.{ac_line2.instance.instance}",
                    channel_key="line2.ComponentStatus",
                )
            )
        if ac_line3 is not None:
            channel_sources.append(
                ChannelSource(
                    label="line3_connected",
                    device_key=f"{JsonKeys.AC}.{ac_line3.instance.instance}",
                    channel_key="line3.ComponentStatus",
                )
            )

    def ac_meter_charger_state_transform(
        values: dict, last_updated: dict
    ) -> Optional[bool]:
        # Check if any line is connected
        line1_connected = MappingUtils.get_value_or_default(
            values, "line1_connected", False
        )
        line2_connected = MappingUtils.get_value_or_default(
            values, "line2_connected", False
        )
        line3_connected = MappingUtils.get_value_or_default(
            values, "line3_connected", False
        )

        ac_lines_connected = line1_connected or line2_connected or line3_connected

        if ac_lines_connected:
            return "charging"
        else:
            return "disabled"

    connected_mapping = MobileChannelMapping(
        mobile_key=f"{thing_id}.cst",
        channel_sources=channel_sources,
        transform=ac_meter_charger_state_transform,
    )

    n2k_devices.add_mobile_channel_mapping(connected_mapping)

    #############################################################################
    # INVERTER MAPPING METHODS
    #############################################################################

    @staticmethod
    def register_inverter_enable_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        instance: int | None,
        inverter_circuit_id: Optional[int] = None,
    ):
        """
        Register an inverter enable mapping that combines circuit power and inverter enable sources.

        Args:
            n2k_devices: The N2kDevices object to register the mappings with
            thing_id: The ID of the Thing
            instance: The instance ID of the inverter
            inverter_circuit_id: Optional circuit ID that controls the inverter's power
        """

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
            mobile_key=f"{thing_id}.ie",
            channel_sources=[],
            transform=inverter_enable_transform,
        )
        if instance is not None:
            ChannelSource(
                label="inverter_enable",
                device_key=f"{JsonKeys.INVERTER_CHARGER}.{instance}",
                channel_key="InverterEnable",
            )
        if inverter_circuit_id is not None:
            mapping.channel_sources.append(
                ChannelSource(
                    label="circuit_power",
                    device_key=f"{JsonKeys.CIRCUIT}.{inverter_circuit_id}",
                    channel_key="Level",
                )
            )
        n2k_devices.add_mobile_channel_mapping(mapping)

    @staticmethod
    def register_inverter_state_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        instance: int,
    ):
        """
        Register an inverter state mapping that transforms state values into user-friendly strings.

        Args:
            n2k_devices: The N2kDevices object to register the mappings with
            thing_id: The ID of the Thing
            instance: The instance ID of the inverter
            mobile_key: The suffix for the mobile key (default: "is" for inverter state)
        """

        def inverter_state_transform(values: dict, last_updated: dict) -> Optional[str]:
            state_value = MappingUtils.get_value_or_default(
                values, "inverter_state", None
            )
            if state_value is not None:
                return RegisterMappingUtility.INVERTER_STATE_MAPPING.get(
                    state_value, "unknown"
                )
            return None

        mapping = MobileChannelMapping(
            mobile_key=f"{thing_id}.is",
            channel_sources=[
                ChannelSource(
                    label="inverter_state",
                    device_key=f"{JsonKeys.INVERTER_CHARGER}.{instance}",
                    channel_key="InverterState",
                )
            ],
            transform=inverter_state_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def register_ac_meter_inverter_state_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        ac_line1: Optional[AC],
        ac_line2: Optional[AC],
        ac_line3: Optional[AC],
    ):

        channel_sources = []

        if ac_line1 is not None:
            channel_sources.append(
                ChannelSource(
                    label="line1_connected",
                    device_key=f"{JsonKeys.AC}.{ac_line1.instance.instance}",
                    channel_key="line1.ComponentStatus",
                )
            )
        if ac_line2 is not None:
            channel_sources.append(
                ChannelSource(
                    label="line2_connected",
                    device_key=f"{JsonKeys.AC}.{ac_line2.instance.instance}",
                    channel_key="line2.ComponentStatus",
                )
            )
        if ac_line3 is not None:
            channel_sources.append(
                ChannelSource(
                    label="line3_connected",
                    device_key=f"{JsonKeys.AC}.{ac_line3.instance.instance}",
                    channel_key="line3.ComponentStatus",
                )
            )

        def ac_meter_inverter_state_transform(
            values: dict, last_updated: dict
        ) -> Optional[bool]:
            # Check if any line is connected
            line1_connected = MappingUtils.get_value_or_default(
                values, "line1_connected", False
            )
            line2_connected = MappingUtils.get_value_or_default(
                values, "line2_connected", False
            )
            line3_connected = MappingUtils.get_value_or_default(
                values, "line3_connected", False
            )

            ac_lines_connected = line1_connected or line2_connected or line3_connected

            if ac_lines_connected:
                return "inverting"
            else:
                return "disabled"

        connected_mapping = MobileChannelMapping(
            mobile_key=f"{thing_id}.is",
            channel_sources=channel_sources,
            transform=ac_meter_inverter_state_transform,
        )

        n2k_devices.add_mobile_channel_mapping(connected_mapping)

    #############################################################################
    # TANK MAPPING METHODS
    #############################################################################

    def register_tanks_mappings(n2k_devices: N2kDevices, thing_id: str, instance: int):
        # Level Absolute
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.levelAbsolute",
            device_key=f"{JsonKeys.TANK}.{instance}",
            channel_key="LevelAbsolute",
            label="LevelAbsolute",
        )

        # Level Percent
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.levelPercent",
            device_key=f"{JsonKeys.TANK}.{instance}",
            channel_key="LevelPercent",
            label="LevelPercent",
        )

        # Component Status

        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.cs",
            device_key=f"{JsonKeys.TANK}.{instance}",
            channel_key="ComponentStatus",
            label="ComponentStatus",
        )

    #############################################################################
    # CLIMATE MAPPING METHODS
    #############################################################################

    def register_climate_mappings(
        n2k_devices: N2kDevices, thing_id: str, instance: int
    ):
        # Component Status
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.cs",
            device_key=f"{JsonKeys.HVAC}.{instance}",
            channel_key="ComponentStatus",
            label="ComponentStatus",
        )

        # Mode
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.mode",
            device_key=f"{JsonKeys.HVAC}.{instance}",
            channel_key="Mode",
            label="Mode",
        )

        # Set Point
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.sp",
            device_key=f"{JsonKeys.HVAC}.{instance}",
            channel_key="SetPoint",
            label="SetPoint",
        )
        # Ambient Temperature
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.at",
            device_key=f"{JsonKeys.HVAC}.{instance}",
            channel_key="AmbientTemperature",
            label="AmbientTemperature",
        )

        # Fan Speed
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.fs",
            device_key=f"{JsonKeys.HVAC}.{instance}",
            channel_key="FanSpeed",
            label="FanSpeed",
        )

        # Fan Mode
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.fm",
            device_key=f"{JsonKeys.HVAC}.{instance}",
            channel_key="FanMode",
            label="FanMode",
        )

    #############################################################################
    # CIRCUIT MAPPING METHODS
    #############################################################################

    def register_circuit_mappings(
        n2k_devices: N2kDevices, thing_id: str, instance: int
    ):
        # Current
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.c",
            device_key=f"{JsonKeys.CIRCUIT}.{instance}",
            channel_key="Current",
            label="Current",
        )

        # Component Status
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.cs",
            device_key=f"{JsonKeys.CIRCUIT}.{instance}",
            channel_key="ComponentStatus",
            label="ComponentStatus",
        )

    # TODO fix the bls value determination logic. I think there is some other mapping I am missing
    def register_circuit_power_mapping(
        n2k_devices: N2kDevices,
        thing_id: str,
        instance: int,
        bls: BinaryLogicState,
    ):
        def power_transform(values: dict, last_updated: dict) -> Optional[bool]:
            level_value = MappingUtils.get_value_or_default(
                values, "circuit_level", None
            )

            bls_power_state = MappingUtils.get_value_or_default(
                values, "bls_power_state", None
            )

            bls_timestamp = last_updated.get("bls_power_state", 0)

            level_timestamp = last_updated.get("circuit_level", 0)
            if level_timestamp > bls_timestamp:
                return level_value > 0
            else:
                return bls_power_state > 0

        channel_sources = []
        if bls is not None:
            # Add BLS state source
            channel_sources.append(
                ChannelSource(
                    label="bls_power_state",
                    device_key=f"{JsonKeys.BINARY_LOGIC_STATE}.{bls.address}",
                    channel_key="State",
                )
            )
        channel_sources.append(
            ChannelSource(
                label="circuit_power",
                device_key=f"{JsonKeys.CIRCUIT}.{instance}",
                channel_key="Level",
            )
        )

        mapping = MobileChannelMapping(
            mobile_key=f"{thing_id}.p",
            channel_sources=channel_sources,
            transform=power_transform,
        )
        n2k_devices.add_mobile_channel_mapping(mapping)

    def register_circuit_level_mapping(
        n2k_devices: N2kDevices, thing_id: str, instance: int
    ):
        RegisterMappingUtility.register_simple_mapping(
            n2k_devices,
            mobile_key=f"{thing_id}.lvl",
            device_key=f"{JsonKeys.CIRCUIT}.{instance}",
            channel_key="Level",
            label="Level",
        )
