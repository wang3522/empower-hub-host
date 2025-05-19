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
from N2KClient.models.constants import Constants, JsonKeys, AttrNames


class ConfigParser:
    _logger = logging.getLogger(
        f"{Constants.DBUS_N2K_CLIENT}: {Constants.Config_Parser}"
    )

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
                AttrNames.ENABLED: JsonKeys.ENABLED,
                AttrNames.ID: JsonKeys.ID,
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
                AttrNames.VALUE: JsonKeys.VALUE,
                AttrNames.VALID: JsonKeys.VALID,
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.IS_EXTERNAL: JsonKeys.IS_EXTERNAL,
            }
            self._map_fields(gnss_json, gnss_device, field_map)
            # Parse instance if present
            instance_json = gnss_json.get(JsonKeys.INSTANCE)
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.CHANNEL_ADDRESS: JsonKeys.CHANNEL_ADDRESS,
                AttrNames.FUSE_LEVEL: JsonKeys.FUSE_LEVEL,
                AttrNames.RUNNING_CURRENT: JsonKeys.RUNNING_CURRENT,
                AttrNames.SYSTEMS_ON_CURRENT: JsonKeys.SYSTEMS_ON_CURRENT,
                AttrNames.FORCE_ACKNOWLEDGE: JsonKeys.FORCE_ACKNOWLEDGE,
                AttrNames.LEVEL: JsonKeys.LEVEL,
                AttrNames.IS_SWITCHED_MODULE: JsonKeys.IS_SWITCHED_MODULE,
            }
            self._map_fields(circuit_load_json, circuit_load, field_map)

            # Handle enum fields
            enum_fields = {
                AttrNames.CONTROL_TYPE: (JsonKeys.CONTROL_TYPE, ControlType),
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
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.ENABLED: JsonKeys.ENABLED,
                AttrNames.INDEX: JsonKeys.INDEX,
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.SINGLE_THROW_ID: JsonKeys.SINGLE_THROW_ID,
                AttrNames.HAS_COMPLEMENT: JsonKeys.HAS_COMPLEMENT,
                AttrNames.DISPLAY_CATEGORIES: JsonKeys.DISPLAY_CATEGORIES,
                AttrNames.MIN_LEVEL: JsonKeys.MIN_LEVEL,
                AttrNames.MAX_LEVEL: JsonKeys.MAX_LEVEL,
                AttrNames.NONVISIBLE_CIRCUIT: JsonKeys.NONVISIBLE_CIRCUIT,
                AttrNames.DIMSTEP: JsonKeys.DIMSTEP,
                AttrNames.STEP: JsonKeys.STEP,
                AttrNames.DIMMABLE: JsonKeys.DIMMABLE,
                AttrNames.LOAD_SMOOTH_START: JsonKeys.LOAD_SMOOTH_START,
                AttrNames.SEQUENTIAL_STATES: JsonKeys.SEQUENTIAL_STATES,
                AttrNames.CONTROL_ID: JsonKeys.CONTROL_ID,
                AttrNames.DC_CIRCUIT: JsonKeys.DC_CIRCUIT,
                AttrNames.AC_CIRCUIT: JsonKeys.AC_CIRCUIT,
                AttrNames.PRIMARY_CIRCUIT_ID: JsonKeys.PRIMARY_CIRCUIT_ID,
                AttrNames.REMOTE_VISIBILITY: JsonKeys.REMOTE_VISIBILITY,
                AttrNames.SWITCH_STRING: JsonKeys.SWITCH_STRING,
                AttrNames.SYSTEMS_ON_AND: JsonKeys.SYSTEMS_ON_AND,
            }
            self._map_fields(circuit_json, circuit_device, field_map)

            # Handle enum fields
            enum_fields = {
                AttrNames.CIRCUIT_TYPE: (JsonKeys.CIRCUIT_TYPE, CircuitType),
                AttrNames.SWITCH_TYPE: (JsonKeys.SWITCH_STRING, SwitchType),
            }
            for attr, (json_key, enum_cls) in enum_fields.items():
                value = circuit_json.get(json_key)
                if value is not None:
                    setattr(circuit_device, attr, enum_cls(value))

            # Parse voltage_source if present
            if (
                voltage_source := circuit_json.get(JsonKeys.VOLTAGE_SOURCE)
            ) is not None:
                circuit_device.voltage_source = self.parse_instance(voltage_source)

            # Parse circuit_loads and categories
            list_fields = {
                AttrNames.CIRCUIT_LOADS: (
                    JsonKeys.CIRCUIT_LOADS,
                    self.parse_circuit_load,
                ),
                AttrNames.CATEGORIES: (JsonKeys.CATEGORIES, self.parse_category),
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.OUTPUT: JsonKeys.OUTPUT,
                AttrNames.NOMINAL_VOLTAGE: JsonKeys.NOMINAL_VOLTAGE,
                AttrNames.ADDRESS: JsonKeys.ADDRESS,
                AttrNames.SHOW_VOLTAGE: JsonKeys.SHOW_VOLTAGE,
                AttrNames.SHOW_CURRENT: JsonKeys.SHOW_CURRENT,
                AttrNames.BATTERY_CAPACITY: JsonKeys.BATTERY_CAPACITY,
                AttrNames.BATTERY_STATE_OF_CHARGE: JsonKeys.BATTERY_STATE_OF_CHARGE,
            }

            for attr, key in field_map.items():
                value = dc_json.get(key)
                if value is not None:
                    setattr(dc_device, attr, value)

            # Parse instance if present
            instance_json = dc_json.get(JsonKeys.INSTANCE)
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.OUTPUT: JsonKeys.OUTPUT,
                AttrNames.NOMINAL_VOLTAGE: JsonKeys.NOMINAL_VOLTAGE,
                AttrNames.ADDRESS: JsonKeys.ADDRESS,
                AttrNames.SHOW_VOLTAGE: JsonKeys.SHOW_VOLTAGE,
                AttrNames.SHOW_CURRENT: JsonKeys.SHOW_CURRENT,
                AttrNames.OUTPUT: JsonKeys.OUTPUT,
                AttrNames.NOMINAL_FREQUENCY: JsonKeys.NOMINAL_FREQUENCY,
            }
            self._map_fields(ac_json, ac_device, field_map)

            enum_fields = {
                AttrNames.LINE: (JsonKeys.LINE, ACLine),
                AttrNames.AC_TYPE: (JsonKeys.AC_TYPE, ACType),
            }
            self._map_enum_fields(ac_json, ac_device, enum_fields)
            # Parse instance if present
            instance_json = ac_json.get(JsonKeys.INSTANCE)
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.CIRCUIT_NAME: JsonKeys.CIRCUIT_NAME,
                AttrNames.ADDRESS: JsonKeys.ADDRESS,
                AttrNames.TANK_CAPACITY: JsonKeys.TANK_CAPACITY,
            }
            self._map_fields(tank_json, tank_device, field_map)

            # Parse instance if present
            instance_json = tank_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                tank_device.instance = self.parse_instance(instance_json)
            # Parse circuit_id if present
            circuit_id_json = tank_json.get(JsonKeys.CIRCUIT_ID)
            if circuit_id_json is not None:
                tank_device.circuit_id = self.parse_data_id(circuit_id_json)

            enum_fields = {
                AttrNames.TANK_TYPE: (JsonKeys.TANK_TYPE, TankType),
                AttrNames.SWITCH_TYPE: (JsonKeys.SWITCH_TYPE, SwitchType),
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
            inverter_instance: int = inverter_charger_json.get(
                JsonKeys.INVERTER_INSTANCE
            )(JsonKeys.INSTANCE)
            charger_instance: int = inverter_charger_json.get(
                JsonKeys.CHARGER_INSTANCE
            )(JsonKeys.INSTANCE)

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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.MODEL: JsonKeys.MODEL,
                AttrNames.TYPE: JsonKeys.TYPE,
                AttrNames.SUB_TYPE: JsonKeys.SUB_TYPE,
                AttrNames.POSITION_COLUMN: JsonKeys.POSITION_COLUMN,
                AttrNames.POSITION_ROW: JsonKeys.POSITION_ROW,
                AttrNames.CLUSTERED: JsonKeys.CLUSTERED,
                AttrNames.PRIMARY: JsonKeys.PRIMARY,
                AttrNames.PRIMARY_PHASE: JsonKeys.PRIMARY_PHASE,
                AttrNames.DEVICE_INSTANCE: JsonKeys.DEVICE_INSTANCE,
                AttrNames.DIPSWITCH: JsonKeys.DIPSWITCH,
                AttrNames.CHANNEL_INDEX: JsonKeys.CHANNEL_INDEX,
            }
            self._map_fields(inverter_charger_json, inverter_charger_device, field_map)

            # Parse instance-related fields if present
            instance_fields = {
                AttrNames.INVERTER_INSTANCE: JsonKeys.INVERTER_INSTANCE,
                AttrNames.CHARGER_INSTANCE: JsonKeys.CHARGER_INSTANCE,
            }
            for attr, key in instance_fields.items():
                field_json = inverter_charger_json.get(key)
                if field_json is not None:
                    setattr(
                        inverter_charger_device, attr, self.parse_instance(field_json)
                    )

            # Parse data id fields if present
            data_id_fields = {
                AttrNames.INVERTER_AC_ID: JsonKeys.INVERTER_AC_ID,
                AttrNames.INVERTER_CIRCUIT_ID: JsonKeys.INVERTER_CIRCUIT_ID,
                AttrNames.INVERTER_TOGGLE_CIRCUIT_ID: JsonKeys.INVERTER_TOGGLE_CIRCUIT_ID,
                AttrNames.CHARGER_AC_ID: JsonKeys.CHARGER_AC_ID,
                AttrNames.CHARGER_CIRCUIT_ID: JsonKeys.CHARGER_CIRCUIT_ID,
                AttrNames.CHARGER_TOGGLE_CIRCUIT_ID: JsonKeys.CHARGER_TOGGLE_CIRCUIT_ID,
                AttrNames.BATTERY_BANK_1_ID: JsonKeys.BATTERY_BANK_1_ID,
                AttrNames.BATTERY_BANK_2_ID: JsonKeys.BATTERY_BANK_2_ID,
                AttrNames.BATTERY_BANK_3_ID: JsonKeys.BATTERY_BANK_3_ID,
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
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.SOURCE_ADDRESS: JsonKeys.SOURCE_ADDRESS,
                AttrNames.CONFLICT: JsonKeys.CONFLICT,
                AttrNames.VALID: JsonKeys.VALID,
                AttrNames.TRANSIENT: JsonKeys.TRANSIENT,
                AttrNames.VERSION: JsonKeys.VERSION,
            }
            self._map_fields(device_json, device, field_map)

            enum_fields = {
                AttrNames.DEVICE_TYPE: (JsonKeys.DEVICE_TYPE, DeviceType),
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.FAN_SPEED_COUNT: JsonKeys.FAN_SPEED_COUNT,
                AttrNames.OPERATING_MODES_MASK: JsonKeys.OPERATING_MODES_MASK,
                AttrNames.MODEL: JsonKeys.MODEL,
                AttrNames.SETPOINT_TEMPERATURE_MAX: JsonKeys.SETPOINT_TEMPERATURE_MIN,
                AttrNames.SETPOINT_TEMPERATURE_MAX: JsonKeys.SETPOINT_TEMPERATURE_MAX,
                AttrNames.FAN_SPEED_OFF_MODES_MASK: JsonKeys.FAN_SPEED_OFF_MODES_MASK,
                AttrNames.FAN_SPEED_AUTO_MODES_MASK: JsonKeys.FAN_SPEED_AUTO_MODES_MASK,
                AttrNames.FAN_SPEED_MANUAL_MODES_MASK: JsonKeys.FAN_SPEED_MANUAL_MODES_MASK,
            }
            self._map_fields(hvac_json, hvac_device, field_map)

            # Handle instance fields
            instance_fields = {
                AttrNames.INSTANCE: JsonKeys.INSTANCE,
                AttrNames.TEMPERATURE_INSTANCE: JsonKeys.TEMPERATURE_INSTANCE,
            }
            for attr, key in instance_fields.items():
                field_json = hvac_json.get(key)
                if field_json is not None:
                    setattr(hvac_device, attr, self.parse_instance(field_json))

            # Handle data id fields
            data_id_fields = {
                AttrNames.OPERATING_MODE_ID: JsonKeys.OPERATING_MODE_ID,
                AttrNames.FAN_MODE_ID: JsonKeys.FAN_MODE_ID,
                AttrNames.FAN_SPEED_ID: JsonKeys.FAN_SPEED_ID,
                AttrNames.SETPOINT_TEPERATURE_ID: JsonKeys.SETPOINT_TEPERATURE_ID,
                AttrNames.OPERATING_MODE_TEMPERATURE_ID: JsonKeys.OPERATING_MODE_TEMPERATURE_ID,
                AttrNames.FAN_MODE_TOGGLE_ID: JsonKeys.FAN_MODE_TOGGLE_ID,
                AttrNames.FAN_SPEED_TOGGLE_ID: JsonKeys.FAN_SPEED_TOGGLE_ID,
                AttrNames.SET_POINT_TEMPERATURE_TOGGLE_ID: JsonKeys.SET_POINT_TEMPERATURE_TOGGLE_ID,
                AttrNames.TEMPERATURE_MONITORING_ID: JsonKeys.TEMPERATURE_MONITORING_ID,
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.MUTE_ENABLED: JsonKeys.MUTE_ENABLED,
            }
            self._map_fields(audio_stereo_json, audio_stereo_device, field_map)
            # Parse instance if present
            instance_json = audio_stereo_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                audio_stereo_device.instance = self.parse_instance(instance_json)
            # Parse circuit_ids if present
            list_fields = {
                AttrNames.CIRCUIT_IDS: JsonKeys.CIRCUIT_IDS,
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.ADDRESS: JsonKeys.ADDRESS,
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
                AttrNames.PRIMARY_ID: JsonKeys.PRIMARY_ID,
                AttrNames.SECONDARY_ID: JsonKeys.SECONDARY_ID,
                AttrNames.PRIMARY_CONFIG_ADDRESS: JsonKeys.PRIMARY_CONFIG_ADDRESS,
                AttrNames.SECONDARY_CONFIG_ADDRESS: JsonKeys.SECONDARY_CONFIG_ADDRESS,
                AttrNames.PRIMARY_CHANNEL_INDEX: JsonKeys.PRIMARY_CHANNEL_INDEX,
                AttrNames.SECONDARY_CHANNEL_INDEX: JsonKeys.SECONDARY_CHANNEL_INDEX,
            }
            self._map_fields(ui_relationship_json, ui_relationship, field_map)
            # Handle enum fields
            enum_fields = {
                AttrNames.PRIMARY_TYPE: (JsonKeys.PRIMARY_TYPE, ItemType),
                AttrNames.SECONDARY_TYPE: (JsonKeys.SECONDARY_TYPE, ItemType),
                AttrNames.RELATIONSHIP_TYPE: (
                    JsonKeys.RELATIONSHIP_TYPE,
                    RelationshipType,
                ),
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.CIRCUIT_NAME: JsonKeys.CIRCUIT_NAME,
                AttrNames.ADDRESS: JsonKeys.ADDRESS,
                AttrNames.ATMOSPHERIC_PRESSURE: JsonKeys.ATMOSPHERIC_PRESSURE,
            }
            self._map_fields(pressure_json, pressure, field_map)
            # Parse instance if present
            instance_json = pressure_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                pressure.instance = self.parse_instance(instance_json)
            # parese enum fields
            enum_fields = {
                AttrNames.PRESSURE_TYPE: (JsonKeys.PRESSURE_TYPE, PressureType),
                AttrNames.SWITCH_TYPE: (JsonKeys.SWITCH_TYPE, SwitchType),
            }
            self._map_enum_fields(pressure_json, pressure, enum_fields)
            # Parse data id fields if present
            data_id_fields = {
                AttrNames.CIRCUIT_ID: JsonKeys.CIRCUIT_ID,
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
                AttrNames.ID: JsonKeys.ID,
                AttrNames.NAME: JsonKeys.NAME,
                AttrNames.SOFTWARE_ID: JsonKeys.SOFTWARE_ID,
                AttrNames.CALIBRATION_ID: JsonKeys.CALIBRATION_ID,
                AttrNames.SERIAL_NUMBER: JsonKeys.SERIAL_NUMBER,
                AttrNames.ECU_SERIAL_NUMBER: JsonKeys.ECU_SERIAL_NUMBER,
            }
            self._map_fields(engine_json, engine_device, field_map)
            # Parse instance if present
            instance_json = engine_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                engine_device.instance = self.parse_instance(instance_json)
            # Handle enum fields
            enum_fields = {
                AttrNames.ENGINE_TYPE: (JsonKeys.ENGINE_TYPE, EngineType),
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
            if JsonKeys.GNSS in config_json:
                for gnss_json in config_json[JsonKeys.GNSS]:
                    gnss_id = f"{AttrNames.GNSS}.{gnss_json[JsonKeys.ID]}"
                    gnss_device = self.parse_gnss(gnss_json)
                    # Add the GNSS device to the configuration
                    n2k_configuration.gnss[gnss_id] = gnss_device

            # Circuit
            if JsonKeys.CIRCUIT in config_json:
                for circuit_json in config_json[JsonKeys.CIRCUIT]:
                    circuit_id = (
                        f"{AttrNames.CIRCUIT}.{circuit_json[JsonKeys.CONTROL_ID]}"
                    )
                    circuit_device = self.parse_circuit(circuit_json)
                    # Add the Circuit device to the configuration
                    n2k_configuration.circuit[circuit_id] = circuit_device

            # DC
            if JsonKeys.DC in config_json:
                for dc_json in config_json[JsonKeys.DC]:
                    dc_id = (
                        f"{AttrNames.DC}.{dc_json[JsonKeys.INSTANCE][JsonKeys.VALUE]}"
                    )
                    dc_device = self.parse_dc(dc_json)
                    # Add the DC device to the configuration
                    n2k_configuration.dc[dc_id] = dc_device

            # AC
            if JsonKeys.AC in config_json:
                for ac_json in config_json[JsonKeys.AC]:
                    ac_id = (
                        f"{AttrNames.AC}.{ac_json[JsonKeys.INSTANCE][JsonKeys.VALUE]}"
                    )
                    ac_device = self.parse_ac(ac_json)
                    # Add the AC device to the configuration
                    n2k_configuration.ac[ac_id] = ac_device

            # Tank
            if JsonKeys.TANK in config_json:
                for tank_json in config_json[JsonKeys.TANK]:
                    tank_id = f"{AttrNames.TANK}.{tank_json[JsonKeys.INSTANCE][JsonKeys.VALUE]}"
                    tank_device = self.parse_tank(tank_json)
                    # Add the Tank device to the configuration
                    n2k_configuration.tank[tank_id] = tank_device

            # Inverter Charger
            if JsonKeys.INVERTER_CHARGER in config_json:
                for inverter_charger_json in config_json[JsonKeys.INVERTER_CHARGER]:
                    inverter_charger_id = self.calculate_inverter_charger_instance(
                        inverter_charger_json
                    )
                    inverter_charger_device = self.parse_inverter_charger(
                        inverter_charger_json
                    )
                    inverter_charger_device_id = (
                        f"{AttrNames.INVERTER_CHARGER}.{inverter_charger_id}"
                    )
                    # Add the Inverter Charger device to the configuration
                    n2k_configuration.inverter_charger[inverter_charger_device_id] = (
                        inverter_charger_device
                    )

            # Device
            if JsonKeys.DEVICE in config_json:
                for device_json in config_json[JsonKeys.DEVICE]:
                    device_id = f"{AttrNames.DEVICE}.{device_json[JsonKeys.DIPSWITCH]}"
                    device = self.parse_device(device_json)
                    # Add the Device to the configuration
                    n2k_configuration.device[device_id] = device

            # HVAC
            if JsonKeys.HVAC in config_json:
                for hvac_json in config_json[JsonKeys.HVAC]:
                    hvac_id = f"{AttrNames.HVAC}.{hvac_json[JsonKeys.INSTANCE][JsonKeys.VALUE]}"
                    hvac_device = self.parse_hvac(hvac_json)
                    # Add the HVAC device to the configuration
                    n2k_configuration.hvac[hvac_id] = hvac_device

            # Audio Stereo
            if JsonKeys.AUDIO_STEREO in config_json:
                for audio_stereo_json in config_json[JsonKeys.AUDIO_STEREO]:
                    audio_stereo_id = f"{AttrNames.AUDIO_STEREO}.{audio_stereo_json[JsonKeys.INSTANCE][JsonKeys.VALUE]}"
                    audio_stereo_device = self.parse_audio_stereo(audio_stereo_json)
                    # Add the Audio Stereo device to the configuration
                    n2k_configuration.audio_stereo[audio_stereo_id] = (
                        audio_stereo_device
                    )

            # Binary Logic State
            if JsonKeys.BINARY_LOGIC_STATE in config_json:
                for binary_logic_state in config_json[JsonKeys.BINARY_LOGIC_STATE]:
                    binary_logic_state_id = f"{AttrNames.BINARY_LOGIC_STATE}.{binary_logic_state[JsonKeys.ID]}"
                    binary_logic_state_device = self.parse_binary_logic_state(
                        binary_logic_state
                    )
                    # Add the Binary Logic State device to the configuration
                    n2k_configuration.binary_logic_state[binary_logic_state_id] = (
                        binary_logic_state_device
                    )

            # UI Relationships
            if JsonKeys.UI_RELATIONSHIP in config_json:
                for ui_relationship_json in config_json[JsonKeys.UI_RELATIONSHIP]:
                    n2k_configuration.ui_relationships.append(
                        self.parse_ui_relationship(ui_relationship_json)
                    )
            # Pressure
            if JsonKeys.PRESSURE in config_json:
                for pressure in config_json[JsonKeys.PRESSURE]:
                    pressure_id = f"{AttrNames.PRESSURE}.{pressure[JsonKeys.INSTANCE][JsonKeys.VALUE]}"
                    pressure_device = self.parse_pressure(pressure)
                    # Add the Pressure device to the configuration
                    n2k_configuration.pressure[pressure_id] = pressure_device

            # Mode
            if JsonKeys.MODE in config_json:
                for mode in config_json[JsonKeys.MODE]:
                    mode_id = f"{AttrNames.MODE}.{mode[JsonKeys.CONTROL_ID]}"
                    mode_device = self.parse_circuit(circuit_json)
                    # Add the Circuit device to the configuration
                    n2k_configuration.mode[mode_id] = mode_device

            # Engine
            if JsonKeys.ENGINE in config_json:
                for engine in config_json[JsonKeys.ENGINE]:
                    engine_id = f"{AttrNames.ENGINE}.{engine[JsonKeys.INSTANCE][JsonKeys.VALUE]}"
                    engine_device = self.parse_engine(engine)
                    # Add the Engine device to the configuration
                    n2k_configuration.engine[engine_id] = engine_device

        except Exception as e:
            self._logger.error(f"Failed to parse config: {e}")
            raise
