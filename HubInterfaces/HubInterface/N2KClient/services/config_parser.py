import json
import logging
from typing import Any

from N2KClient.models.configuration.configuation import N2KConfiguration
from N2KClient.models.configuration.gnss import GNSSDevice
from N2KClient.models.configuration.circuit import (
    Circuit,
    CircuitType,
    CircuitLoad,
    SwitchType,
    CategoryItem,
    ControlType,
)
from N2KClient.models.configuration.dc import DC
from N2KClient.models.configuration.ac import AC, ACLine, ACType
from N2KClient.models.configuration.tank import Tank, TankType
from N2KClient.models.configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.configuration.device import Device, DeviceType
from N2KClient.models.configuration.hvac import HVACDevice
from N2KClient.models.configuration.audio_stereo import AudioStereoDevice
from N2KClient.models.configuration.binary_logic_state import BinaryLogicStates
from N2KClient.models.configuration.ui_relationship_msg import (
    UiRelationShipMsg,
    ItemType,
    RelationshipType,
)
from N2KClient.models.configuration.pressure import Pressure, PressureType
from N2KClient.models.configuration.engine import EnginesDevice, EngineType

from N2KClient.models.configuration.instance import Instance
from N2KClient.models.configuration.data_id import DataId


class ConfigParser:
    _logger = logging.getLogger("DBUS N2k Client: ConfigParser")

    def __init__(self):
        self._logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_handler.setFormatter(formatter)
        self._logger.addHandler(log_handler)
        self._config = N2KConfiguration()

    # Utility Functions

    # Map fields from source dictionary to target object
    def _map_fields(
        self, source: dict[str, Any], target: object, field_map: dict
    ) -> None:
        """
        Map fields from source dictionary to target object.
        """
        for attr, key in field_map.items():
            value = source.get(key)
            if value is not None:
                setattr(target, attr, value)

    # Map enum fields from source dictionary to target object
    def _map_enum_fields(
        self, source: dict[str, Any], target: object, field_map: dict
    ) -> None:
        """
        Map enum fields from source dictionary to target object.
        """
        for attr, (key, enum_cls) in field_map.items():
            value = source.get(key)
            if value is not None:
                setattr(target, attr, enum_cls(value))

    # Map list fields from source dictionary to target object
    def _map_list_fields(
        self, source: dict[str, Any], target: object, field_map: dict
    ) -> None:
        """
        Map list fields from source dictionary to target object.
        """
        for attr, key in field_map.items():
            value = source.get(key)
            if value is not None:
                setattr(target, attr, [item for item in value])

    # Parse functions for different device types

    def parse_data_id(self, data_id_json: dict[str, Any]) -> DataId:
        """
        Parse the DataId object from the configuration.
        """
        try:
            data_id = DataId()
            field_map = {
                "enabled": "Enabled",
                "id": "Id",
            }
            self._map_fields(data_id_json, data_id, field_map)
            return data_id
        except Exception as e:
            self._logger.error(f"Failed to parse DataId: {e}")
            raise

    def parse_instance(self, instance_json: dict[str, Any]) -> Instance:
        """
        Parse the Instance object from the configuration.
        """
        try:
            instance = Instance()
            field_map = {
                "value:": "Value",
                "valid": "Valid",
            }
            self._map_fields(instance_json, instance, field_map)
            return instance
        except Exception as e:
            self._logger.error(f"Failed to parse Instance: {e}")
            raise

    def parse_gnss(self, gnss_json: dict[str, Any]) -> GNSSDevice:
        """
        Parse the GNSS device from the configuration.
        """
        try:
            gnss_device = GNSSDevice()
            # Map simple fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "is_external": "Is_external",
            }
            self._map_fields(gnss_json, gnss_device, field_map)
            # Parse instance if present
            instance_json = gnss_json.get("Instance")
            if instance_json is not None:
                gnss_device.instance = self.parse_instance(instance_json)
            return gnss_device
        except Exception as e:
            self._logger.error(f"Failed to parse GNSS device: {e}")
            raise

    def parse_circuit_load(self, circuit_load_json: dict[str, Any]) -> CircuitLoad:
        """
        Parse the CircuitLoad object from the configuration.
        """
        try:
            circuit_load = CircuitLoad()
            # Map simple fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "channel_address": "ChannelAddress",
                "fuse_level": "FuseLevel",
                "running_current": "RunningCurrent",
                "systems_on_current": "SystemsOnCurrent",
                "force_acknowledge": "ForceAcknowledge",
                "level": "Level",
                "is_switched_module": "IsSwitchedModule",
            }
            self._map_fields(circuit_load_json, circuit_load, field_map)

            # Handle enum fields
            enum_fields = {
                "control_type": ("ControlType", ControlType),
            }
            self._map_enum_fields(circuit_load_json, circuit_load, enum_fields)
            return circuit_load
        except Exception as e:
            self._logger.error(f"Failed to parse CircuitLoad: {e}")
            raise

    def parse_category(self, category_json: dict[str, Any]) -> CategoryItem:
        """
        Parse the CategoryItem object from the configuration.
        """
        try:
            category = CategoryItem()
            field_map = {
                "name_utf8": "NameUTF8",
                "enabled": "Enabled",
                "index": "Index",
            }
            self._map_fields(category_json, category, field_map)
            return category
        except Exception as e:
            self._logger.error(f"Failed to parse CategoryItem: {e}")
            raise

    def parse_circuit(self, circuit_json: dict[str, Any]) -> Circuit:
        """
        Parse the Circuit device from the configuration.
        """
        try:
            circuit_device = Circuit()
            # Combine required and optional fields into a single field map
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "single_throw_id": "SingleThrowId",
                "has_complement": "HasComplementary",
                "display_categories": "DisplayCategories",
                "min_level": "MinLevel",
                "max_level": "MaxLevel",
                "nonvisibile_circuit": "NonvisibleCircuit",
                "dimstep": "DimStep",
                "step": "Step",
                "dimmable": "Dimmable",
                "load_smooth_start": "LoadSmoothStart",
                "sequential_states": "SequentialStates",
                "control_id": "ControlId",
                "dc_circuit": "DcCircuit",
                "ac_circuit": "AcCircuit",
                "primary_circuit_id": "PrimaryCircuitId",
                "remote_visibility": "RemoteVisibility",
                "switch_string": "SwitchString",
                "systems_on_and": "SystemsOnAnd",
            }
            self._map_fields(circuit_json, circuit_device, field_map)

            # Handle enum fields
            enum_fields = {
                "circuit_type": ("CircuitType", CircuitType),
                "switch_type": ("SwitchType", SwitchType),
            }
            for attr, (json_key, enum_cls) in enum_fields.items():
                value = circuit_json.get(json_key)
                if value is not None:
                    setattr(circuit_device, attr, enum_cls(value))

            # Parse voltage_source if present
            if (voltage_source := circuit_json.get("VoltageSource")) is not None:
                circuit_device.voltage_source = self.parse_instance(voltage_source)

            # Parse circuit_loads and categories
            list_fields = {
                "circuit_loads": ("CircuitLoads", self.parse_circuit_load),
                "categories": ("Categories", self.parse_category),
            }
            self._map_list_fields(circuit_json, circuit_device, list_fields)

            return circuit_device
        except Exception as e:
            self._logger.error(f"Failed to parse Circuit device: {e}")
            raise

    def parse_dc(self, dc_json: dict[str, Any]) -> DC:
        """
        Parse the DC device from the configuration.
        """
        try:
            dc_device = DC()
            # Map required fields directly

            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "output": "Output",
                "nominal_voltage": "NominalVoltage",
                "address": "Address",
                "warning_low": "WarningLow",
                "warning_high": "WarningHigh",
                "show_voltage": "ShowVoltage",
                "show_current": "ShowCurrent",
                "battery_capacity": "BatteryCapacity",
                "battery_state_of_charge": "BatteryStateOfCharge",
            }

            for attr, key in field_map.items():
                value = dc_json.get(key)
                if value is not None:
                    setattr(dc_device, attr, value)

            # Parse instance if present
            instance_json = dc_json.get("Instance")
            if instance_json is not None:
                dc_device.instance = self.parse_instance(instance_json)
            return dc_device
        except Exception as e:
            self._logger.error(f"Failed to parse DC device: {e}")
            raise

    def parse_ac(self, ac_json: dict[str, Any]) -> AC:
        """
        Parse the AC device from the configuration
        """
        try:
            ac_device = AC()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "instance": "Instance",
                "output": "Output",
                "nominal_voltage": "NominalVoltage",
                "address": "Address",
                "warning_low": "WarningLow",
                "warning_high": "WarningHigh",
                "show_voltage": "ShowVoltage",
                "show_current": "ShowCurrent",
                "output": "Output",
                "norminal_frequency": "NominalFrequency",
            }
            self._map_fields(ac_json, ac_device, field_map)

            enum_fields = {
                "line": ("Line", ACLine),
                "ac_type": ("ACType", ACType),
            }
            self._map_enum_fields(ac_json, ac_device, enum_fields)
            # Parse instance if present
            instance_json = ac_json.get("Instance")
            if instance_json is not None:
                ac_device.instance = self.parse_instance(instance_json)
            return ac_device
        except Exception as e:
            self._logger.error(f"Failed to parse AC device: {e}")
            raise

    def parse_tank(self, tank_json: dict[str, Any]) -> Tank:
        """
        Parse the Tank device from the configuration.
        """
        try:
            tank_device = Tank()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "instance": "Instance",
                "circuit_id": "CircuitId",
                "circuit_name": "circuitName",
                "address": "Address",
                "tank_capacity": "TankCapacity",
            }
            self._map_fields(tank_json, tank_device, field_map)

            # Parse instance if present
            instance_json = tank_json.get("Instance")
            if instance_json is not None:
                tank_device.instance = self.parse_instance(instance_json)
            # Parse circuit_id if present
            circuit_id_json = tank_json.get("CircuitId")
            if circuit_id_json is not None:
                tank_device.circuit_id = self.parse_data_id(circuit_id_json)

            enum_fields = {
                "tank_type": ("TankType", TankType),
                "switch_type": ("SwitchType", SwitchType),
            }
            self._map_enum_fields(tank_json, tank_device, enum_fields)
            return tank_device
        except Exception as e:
            self._logger.error(f"Failed to parse Tank device: {e}")
            raise

    def calculate_inverter_charger_instance(
        self, inverter_charger_json: dict[str, Any]
    ) -> int:
        """
        Calculate the inverter charger instance from the configuration.
        """
        try:
            inverter_instance: int = inverter_charger_json.get("InverterInstance")(
                "Instance"
            )
            charger_instance: int = inverter_charger_json.get("ChargerInstance")(
                "Instance"
            )

            return inverter_instance << 8 | charger_instance

        except Exception as e:
            self._logger.error(f"Failed to calculate Inverter Charger instance: {e}")
            raise

    def parse_inverter_charger(
        self, inverter_charger_json: dict[str, Any]
    ) -> InverterChargerDevice:
        """
        Parse the Inverter Charger device from the configuration.
        """
        try:
            inverter_charger_device = InverterChargerDevice()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "model": "Model",
                "type": "Type",
                "sub_type": "SubType",
                "position_column": "PositionColumn",
                "position_row": "PositionRow",
                "clustered": "Clustered",
                "primary": "Primary",
                "primary_phase": "PrimaryPhase",
                "device_instance": "DeviceInstance",
                "dipswitch": "Dipswitch",
                "channel_index": "ChannelIndex",
            }
            self._map_fields(inverter_charger_json, inverter_charger_device, field_map)

            # Parse instance-related fields if present
            instance_fields = {
                "inverter_instance": "InverterInstance",
                "charger_instance": "ChargerInstance",
            }
            for attr, key in instance_fields.items():
                field_json = inverter_charger_json.get(key)
                if field_json is not None:
                    setattr(
                        inverter_charger_device, attr, self.parse_instance(field_json)
                    )

            # Parse data id fields if present
            data_id_fields = {
                "inverter_ac_id": "InverterACId",
                "inverter_circuit_id": "InverterCircuitId",
                "inverter_toggle_circuit_id": "InverterToggleCircuitId",
                "charger_ac_id": "ChargerACId",
                "charger_circuit_id": "ChargerCircuitId",
                "charger_toggle_circuit_id": "ChargerToggleCircuitId",
                "battery_bank_1_id": "BatteryBank1Id",
                "battery_bank_2_id": "BatteryBank2Id",
                "battery_bank_3_id": "BatteryBank3Id",
            }
            for attr, key in data_id_fields.items():
                field_json = inverter_charger_json.get(key)
                if field_json is not None:
                    setattr(
                        inverter_charger_device, attr, self.parse_data_id(field_json)
                    )

            return inverter_charger_device
        except Exception as e:
            self._logger.error(f"Failed to parse Inverter Charger device: {e}")
            raise

    def parse_device(self, device_json: dict[str, Any]) -> Device:
        """
        Parse the Device object from the configuration.
        """
        try:
            device = Device()
            # Map required fields directly
            field_map = {
                "name_utf8": "NameUTF8",
                "source_address": "SourceAddress",
                "conflict": "Conflict",
                "valid": "Valid",
                "transient": "Transient",
                "version": "Version",
            }
            self._map_fields(device_json, device, field_map)

            enum_fields = {
                "device_type": ("DeviceType", DeviceType),
            }
            # Handle enum fields
            for attr, (json_key, enum_cls) in enum_fields.items():
                value = device_json.get(json_key)
                if value is not None:
                    setattr(device, attr, enum_cls(value))
            return device
        except Exception as e:
            self._logger.error(f"Failed to parse Device: {e}")
            raise

    def parse_hvac(self, hvac_json: dict[str, Any]) -> HVACDevice:
        """
        Parse the HVAC device from the configuration.
        """
        try:
            hvac_device = HVACDevice()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "fan_speed_count": "FanSpeedCount",
                "operating_modes_mask": "OperatingModesMask",
                "model": "Model",
                "setpoint_temperature_min": "SetpointTemperatureMin",
                "setpoint_temperature_max": "SetpointTemperatureMax",
                "fan_speed_off_modes_mask": "FanSpeedOffModesMask",
                "fan_speed_auto_modes_mask": "FanSpeedAutoModesMask",
                "fan_speed_manual_modes_mask": "FanSpeedManualModesMask",
            }
            self._map_fields(hvac_json, hvac_device, field_map)

            # Handle instance fields
            instance_fields = {
                "instance": "Instance",
                "temperature_instance": "TemperatureInstance",
            }
            for attr, key in instance_fields.items():
                field_json = hvac_json.get(key)
                if field_json is not None:
                    setattr(hvac_device, attr, self.parse_instance(field_json))

            # Handle data id fields
            data_id_fields = {
                "operating_mode_id": "OperatingModeId",
                "fan_mode_id": "FanModeId",
                "fan_speed_id": "FanSpeedId",
                "setpoint_temperature_id": "SetpointTemperatureId",
                "operating_mode_temperature_id": "OperatingModeTemperatureId",
                "fan_mode_toggle_id": "FanModeToggleId",
                "fan_speed_toggle_id": "FanSpeedToggleId",
                "setpoint_temperature_toggle_id": "SetpointTemperatureToggleId",
                "temperature_monitoring_id": "TemperatureMonitoringId",
            }
            for attr, key in data_id_fields.items():
                field_json = hvac_json.get(key)
                if field_json is not None:
                    setattr(hvac_device, attr, self.parse_data_id(field_json))

            return hvac_device
        except Exception as e:
            self._logger.error(f"Failed to parse HVAC device: {e}")
            raise

    def parse_audio_stereo(
        self, audio_stereo_json: dict[str, Any]
    ) -> AudioStereoDevice:
        """
        Parse the Audio Stereo device from the configuration.
        """
        try:
            audio_stereo_device = AudioStereoDevice()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "mute_enabled": "MuteEnabled",
            }
            self._map_fields(audio_stereo_json, audio_stereo_device, field_map)
            # Parse instance if present
            instance_json = audio_stereo_json.get("Instance")
            if instance_json is not None:
                audio_stereo_device.instance = self.parse_instance(instance_json)
            # Parse circuit_ids if present
            list_fields = {
                "circuit_ids": "CircuitIds",
            }
            self._map_list_fields(audio_stereo_json, audio_stereo_device, list_fields)

            return audio_stereo_device
        except Exception as e:
            self._logger.error(f"Failed to parse Audio Stereo device: {e}")
            raise

    def parse_binary_logic_state(
        self, binary_logic_state_json: dict[str, Any]
    ) -> BinaryLogicStates:
        """
        Parse the Binary Logic State object from the configuration.
        """
        try:
            binary_logic_state = BinaryLogicStates()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "address": "Address",
            }
            self._map_fields(binary_logic_state_json, binary_logic_state, field_map)
            return binary_logic_state
        except Exception as e:
            self._logger.error(f"Failed to parse Binary Logic State: {e}")
            raise

    def parse_ui_relationship(
        self, ui_relationship_json: dict[str, Any]
    ) -> UiRelationShipMsg:
        """
        Parse the UI Relationship object from the configuration.
        """
        try:
            ui_relationship = UiRelationShipMsg()
            # Map required fields directly
            field_map = {
                "primary_id": "PrimaryId",
                "secondary_id": "SecondaryId",
                "primary_config_address": "PrimaryConfigAddress",
                "secondary_config_address": "SecondaryConfigAddress",
                "primary_channel_index": "PrimaryChannelIndex",
                "secondary_channel_index": "SecondaryChannelIndex",
            }
            self._map_fields(ui_relationship_json, ui_relationship, field_map)
            # Handle enum fields
            enum_fields = {
                "primary_type": ("PrimaryType", ItemType),
                "secondary_type": ("SecondaryType", ItemType),
                "relationship_type": ("RelationshipType", RelationshipType),
            }
            self._map_enum_fields(ui_relationship_json, ui_relationship, enum_fields)
            return ui_relationship
        except Exception as e:
            self._logger.error(f"Failed to parse UI Relationship: {e}")
            raise

    def parse_pressure(self, pressure_json: dict[str, Any]) -> Pressure:
        """
        Parse the Pressure object from the configuration.
        """
        try:
            pressure = Pressure()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "circuit_id": "CircuitId",
                "circuit_name": "CircuitName",
                "address": "Address",
                "atmospheric_pressure": "AtmosphericPressure",
            }
            self._map_fields(pressure_json, pressure, field_map)
            # Parse instance if present
            instance_json = pressure_json.get("Instance")
            if instance_json is not None:
                pressure.instance = self.parse_instance(instance_json)
            # parese enum fields
            enum_fields = {
                "pressure_type": ("PressureType", PressureType),
                "switch_type": ("SwitchType", SwitchType),
            }
            self._map_enum_fields(pressure_json, pressure, enum_fields)
            # Parse data id fields if present
            data_id_fields = {
                "circuit_id": "CircuitId",
            }
            for attr, key in data_id_fields.items():
                field_json = pressure_json.get(key)
                if field_json is not None:
                    setattr(pressure, attr, self.parse_data_id(field_json))
            return pressure
        except Exception as e:
            self._logger.error(f"Failed to parse Pressure: {e}")
            raise

    def parse_engine(self, engine_json: dict[str, Any]) -> EnginesDevice:
        """
        Parse the Engine device from the configuration.
        """
        try:
            engine_device = EnginesDevice()
            # Map required fields directly
            field_map = {
                "id": "Id",
                "name": "NameUTF8",
                "software_id": "SoftwareId",
                "calibration_id": "CalibrationId",
                "serial_number": "SerialNumber",
                "ecu_serial_number": "EcuSerialNumber",
            }
            self._map_fields(engine_json, engine_device, field_map)
            # Parse instance if present
            instance_json = engine_json.get("Instance")
            if instance_json is not None:
                engine_device.instance = self.parse_instance(instance_json)
            # Handle enum fields
            enum_fields = {
                "engine_type": ("EngineType", EngineType),
            }
            self._map_enum_fields(engine_json, engine_device, enum_fields)
            return engine_device
        except Exception as e:
            self._logger.error(f"Failed to parse Engine device: {e}")
            raise

    def parse_config(self, config_string: str) -> N2KConfiguration:
        """
        Parse the configuration string and return a N2KConfiguration object.
        """
        try:
            n2k_configuration = N2KConfiguration()
            # Parse the configuration string
            config_json: dict[str, list[Any]] = json.loads(config_string)

            # GNSS
            if "gnss" in config_json:
                for gnss_json in config_json["gnss"]:
                    gnss_id = f"gnss.{gnss_json['id']}"
                    gnss_device = self.parse_gnss(gnss_json)
                    # Add the GNSS device to the configuration
                    n2k_configuration.gnss[gnss_id] = gnss_device

            # Circuit
            if "circuit" in config_json:
                for circuit_json in config_json["circuit"]:
                    circuit_id = f"circuit.{circuit_json['ControlId']}"
                    circuit_device = self.parse_circuit(circuit_json)
                    # Add the Circuit device to the configuration
                    n2k_configuration.circuit[circuit_id] = circuit_device

            # DC
            if "dc" in config_json:
                for dc_json in config_json["dc"]:
                    dc_id = f"dc.{dc_json['Instance']['Value']}"
                    dc_device = self.parse_dc(dc_json)
                    # Add the DC device to the configuration
                    n2k_configuration.dc[dc_id] = dc_device

            # AC
            if "ac" in config_json:
                for ac_json in config_json["ac"]:
                    ac_id = f"ac.{ac_json['Instance']['Value']}"
                    ac_device = self.parse_ac(ac_json)
                    # Add the AC device to the configuration
                    n2k_configuration.ac[ac_id] = ac_device

            # Tank
            if "tank" in config_json:
                for tank_json in config_json["tank"]:
                    tank_id = f"tank.{tank_json['Instance']['Value']}"
                    tank_device = self.parse_tank(tank_json)
                    # Add the Tank device to the configuration
                    n2k_configuration.tank[tank_id] = tank_device

            # Inverter Charger
            if "inverter_charger" in config_json:
                for inverter_charger_json in config_json["inverter_charger"]:
                    inverter_charger_id = self.calculate_inverter_charger_instance(
                        inverter_charger_json
                    )
                    inverter_charger_device = self.parse_inverter_charger(
                        inverter_charger_json
                    )
                    # Add the Inverter Charger device to the configuration
                    n2k_configuration.inverter_charger[inverter_charger_id] = (
                        inverter_charger_device
                    )

            # Device
            if "device" in config_json:
                for device_json in config_json["device"]:
                    device_dipswitch = device_json["Dipswitch"]
                    device = self.parse_device(device_json)
                    # Add the Device to the configuration
                    n2k_configuration.device[device_dipswitch] = device

            # HVAC
            if "hvac" in config_json:
                for hvac_json in config_json["hvac"]:
                    hvac_id = f"hvac.{hvac_json['Instance']['Value']}"
                    hvac_device = HVACDevice()
                    # Map required fields directly
                    field_map = {
                        "id": "Id",
                        "name": "NameUTF8",
                        "address": "Address",
                        "type": "Type",
                        "sub_type": "SubType",
                        "position_column": "PositionColumn",
                        "position_row": "PositionRow",
                        "clustered": "Clustered",
                        "primary": "Primary",
                        "primary_phase": "PrimaryPhase",
                    }
                    self._map_fields(hvac_json, hvac_device, field_map)
                    # Add the HVAC device to the configuration
                    n2k_configuration.hvac[hvac_id] = hvac_device

            # Audio Stereo
            if "audio_stereo" in config_json:
                for audio_stereo_json in config_json["audio_stereo"]:
                    audio_stereo_id = (
                        f"audio_stereo.{audio_stereo_json['Instance']['Value']}"
                    )
                    audio_stereo_device = self.parse_audio_stereo(audio_stereo_json)
                    # Add the Audio Stereo device to the configuration
                    n2k_configuration.audio_stereo[audio_stereo_id] = (
                        audio_stereo_device
                    )

            # Binary Logic State
            if "binary_logic_state" in config_json:
                for binary_logic_state in config_json["binary_logic_state"]:
                    binary_logic_state_id = (
                        f"binary_logic_state.{binary_logic_state['Id']}"
                    )
                    binary_logic_state_device = self.parse_binary_logic_state(
                        binary_logic_state
                    )
                    # Add the Binary Logic State device to the configuration
                    n2k_configuration.binary_logic_state[binary_logic_state_id] = (
                        binary_logic_state_device
                    )

            # UI Relationships
            if "ui_relationship" in config_json:
                for ui_relationship_json in config_json["ui_relationship"]:
                    n2k_configuration.ui_relationships.append(
                        self.parse_ui_relationship(ui_relationship_json)
                    )
            # Pressure
            if "pressure" in config_json:
                for pressure in config_json["pressure"]:
                    pressure_id = f"pressure.{pressure['Instance']['Value']}"
                    pressure_device = self.parse_pressure(pressure)
                    # Add the Pressure device to the configuration
                    n2k_configuration.pressure[pressure_id] = pressure_device

            # Mode
            if "mode" in config_json:
                for mode in config_json["mode"]:
                    mode_id = f"circuit.{circuit_json['ControlId']}"
                    mode_device = self.parse_circuit(circuit_json)
                    # Add the Circuit device to the configuration
                    n2k_configuration.mode[mode_id] = mode_device

            # Engine
            if "engine" in config_json:
                for engine in config_json["engine"]:
                    engine_id = f"engine.{engine['Instance']['Value']}"
                    engine_device = self.parse_engine(engine)
                    # Add the Engine device to the configuration
                    n2k_configuration.engine[engine_id] = engine_device

        except Exception as e:
            self._logger.error(f"Failed to parse config: {e}")
            raise
