import json
import logging
from typing import Any

from ....models.n2k_configuration.alarm_limit import AlarmLimit

from ....models.n2k_configuration.n2k_configuation import N2kConfiguration
from ....models.n2k_configuration.gnss import GNSSDevice
from ....models.n2k_configuration.circuit import (
    Circuit,
    CircuitLoad,
    CategoryItem,
)
from ....models.n2k_configuration.dc import DC
from ....models.n2k_configuration.ac import AC, ACLine
from ....models.n2k_configuration.tank import Tank
from ....models.n2k_configuration.inverter_charger import InverterChargerDevice
from ....models.n2k_configuration.device import Device
from ....models.n2k_configuration.hvac import HVACDevice
from ....models.n2k_configuration.audio_stereo import AudioStereoDevice
from ....models.n2k_configuration.binary_logic_state import BinaryLogicState
from ....models.n2k_configuration.ui_relationship_msg import (
    UiRelationShipMsg,
)
from ....models.n2k_configuration.pressure import Pressure
from ....models.n2k_configuration.engine import EngineDevice
from ....models.n2k_configuration.sequential_name import SequentialName
from ....models.n2k_configuration.instance import Instance
from ....models.n2k_configuration.data_id import DataId
from ....models.constants import Constants, JsonKeys, AttrNames
from ....models.n2k_configuration.value_u32 import ValueU32
from .field_maps import *
from .config_parser_helpers import (
    get_device_instance_value,
    get_bls_alarm_channel,
)
from ....models.n2k_configuration.ac_meter import ACMeter
from ....models.n2k_configuration.engine_configuration import EngineConfiguration
from ....models.n2k_configuration.config_metadata import ConfigMetadata
from ....models.n2k_configuration.factory_metadata import FactoryMetadata
from ....models.n2k_configuration.bls_alarm_mapping import BLSAlarmMapping
from ....util.common_utils import map_fields, map_enum_fields, map_list_fields


class ConfigParser:
    _logger = logging.getLogger(
        f"{Constants.DBUS_N2K_CLIENT}: {Constants.Config_Parser}"
    )

    def __init__(self):
        self._circuit_list_field_map = {
            AttrNames.CIRCUIT_LOADS: (JsonKeys.CIRCUIT_LOADS, self.parse_circuit_load),
            AttrNames.CATEGORIES: (JsonKeys.CATEGORIES, self.parse_category),
            AttrNames.SEQUENTIAL_NAMES_UTF8: (
                JsonKeys.SEQUENTIAL_NAMES_UTF8,
                self.parse_sequential_name,
            ),
        }
        self._audio_stereo_list_field_map = {
            AttrNames.CIRCUIT_IDS: (JsonKeys.CIRCUIT_IDS, self.parse_data_id),
        }

    # Parse functions for different device types
    def parse_sequential_name(
        self, sequential_name_json: dict[str, str]
    ) -> SequentialName:
        """
        Parse the sequential name from the configuration.
        """
        try:
            sequential_name = SequentialName()
            map_fields(
                sequential_name_json, sequential_name, SEQUENTIAL_NAMES_FIELD_MAP
            )
            return sequential_name
        except Exception as e:
            self._logger.error(f"Failed to parse sequential name: {e}")
            raise

    def parse_value_u32(self, value_u32_json: dict[str, Any]) -> ValueU32:
        """
        Parse the ValueU32 object from the configuration.
        """
        try:
            value_u32 = ValueU32()
            map_fields(value_u32_json, value_u32, VALUE_U32_FIELD_MAP)
            return value_u32
        except Exception as e:
            self._logger.error(f"Failed to parse ValueU32: {e}")
            raise

    def parse_data_id(self, data_id_json: dict[str, Any]) -> DataId:
        """
        Parse the DataId object from the configuration.
        """
        try:
            data_id = DataId()
            map_fields(data_id_json, data_id, DATA_ID_FIELD_MAP)
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
            map_fields(instance_json, instance, INSTANCE_FIELD_MAP)
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
            map_fields(gnss_json, gnss_device, GNSS_FIELD_MAP)
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

            map_fields(circuit_load_json, circuit_load, CIRCUIT_LOAD_FIELD_MAP)

            # Handle enum fields
            map_enum_fields(
                self._logger,
                circuit_load_json,
                circuit_load,
                CIRCUIT_LOAD_ENUM_FIELD_MAP,
            )
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
            map_fields(category_json, category, CATEGORY_FIELD_MAP)
            return category
        except Exception as e:
            self._logger.error(f"Failed to parse CategoryItem: {e}")
            raise

    def parse_alarm_limit(self, alarm_limit_json: dict[str, Any]) -> AlarmLimit:
        """
        Parse the AlarmLimit object from the configuration.
        """
        try:
            alarm_limit = AlarmLimit()
            map_fields(alarm_limit_json, alarm_limit, ALARM_LIMIT_FIELD_MAP)
            return alarm_limit
        except Exception as e:
            self._logger.error(f"Failed to parse AlarmLimit: {e}")
            raise

    def parse_circuit(self, circuit_json: dict[str, Any]) -> Circuit:
        """
        Parse the Circuit device from the configuration.
        """
        try:
            circuit_device = Circuit()
            # Combine required and optional fields into a single field map
            map_fields(circuit_json, circuit_device, CIRCUIT_FIELD_MAP)

            # Handle enum fields
            map_enum_fields(
                self._logger, circuit_json, circuit_device, CIRCUIT_ENUM_FIELD_MAP
            )

            voltage_source_json = circuit_json.get(JsonKeys.VOLTAGE_SOURCE)
            if voltage_source_json is not None:
                circuit_device.voltage_source = self.parse_instance(voltage_source_json)

            single_throw_id_json = circuit_json.get(JsonKeys.SINGLE_THROW_ID)
            if single_throw_id_json is not None:
                circuit_device.single_throw_id = self.parse_data_id(
                    single_throw_id_json
                )
            id = circuit_json.get(JsonKeys.ID)
            if id is not None:
                circuit_device.id = self.parse_value_u32(id)
            # Parse circuit_loads and categories
            map_list_fields(circuit_json, circuit_device, self._circuit_list_field_map)

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

            map_fields(dc_json, dc_device, DC_FIELD_MAP)
            map_enum_fields(self._logger, dc_json, dc_device, DC_ENUM_FIELD_MAP)
            for attr, key in DC_ALARM_LIMIT_FIELD_MAP.items():
                field_json = dc_json.get(key)
                if field_json is not None:
                    setattr(dc_device, attr, self.parse_alarm_limit(field_json))
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
            map_fields(ac_json, ac_device, AC_FIELD_MAP)
            map_enum_fields(self._logger, ac_json, ac_device, AC_EMUM_FIELD_MAP)
            # Parse instance if present
            instance_json = ac_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                ac_device.instance = self.parse_instance(instance_json)

            for attr, key in AC_ALARM_LIMIT_FIELD_MAP.items():
                field_json = ac_json.get(key)
                if field_json is not None:
                    setattr(ac_device, attr, self.parse_alarm_limit(field_json))
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
            map_fields(tank_json, tank_device, TANK_FIELD_MAP)

            # Parse instance if present
            instance_json = tank_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                tank_device.instance = self.parse_instance(instance_json)
            # Parse circuit_id if present
            circuit_id_json = tank_json.get(JsonKeys.CIRCUIT_ID)
            if circuit_id_json is not None:
                tank_device.circuit_id = self.parse_data_id(circuit_id_json)

            map_enum_fields(self._logger, tank_json, tank_device, TANK_ENUM_FIELD_MAP)

            for attr, key in TANK_ALARM_LIMIT_FIELD_MAP.items():
                field_json = tank_json.get(key)
                if field_json is not None:
                    setattr(tank_device, attr, self.parse_alarm_limit(field_json))
            return tank_device
        except Exception as e:
            self._logger.error(f"Failed to parse Tank device: {e}")
            raise

    def calculate_inverter_charger_instance(
        self, inverter_charger_json: dict[str, Any]
    ) -> int | None:
        """
        Calculate the inverter charger instance from the configuration.
        Returns the combined instance if both inverter and charger are enabled and present, else None.
        """
        try:
            inverter_instance_json = inverter_charger_json.get(
                JsonKeys.INVERTER_INSTANCE, {}
            )
            charger_instance_json = inverter_charger_json.get(
                JsonKeys.CHARGER_INSTANCE, {}
            )

            inverter_enabled = inverter_instance_json.get(JsonKeys.ENABLED, False)
            charger_enabled = charger_instance_json.get(JsonKeys.ENABLED, False)
            inverter_instance = inverter_instance_json.get(JsonKeys.INSTANCE, None)
            charger_instance = charger_instance_json.get(JsonKeys.INSTANCE, None)
            if (
                inverter_instance is not None
                and inverter_enabled
                and charger_instance is not None
                and charger_enabled
            ):
                return (inverter_instance << 8) | charger_instance

            return None

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

            map_fields(
                inverter_charger_json,
                inverter_charger_device,
                INVERTER_CHARGER_FIELD_MAP,
            )

            # Parse instance-related fields if present
            for attr, key in INVERTER_CHARGER_INSTANCE_FIELD_MAP.items():
                field_json = inverter_charger_json.get(key)
                if field_json is not None:
                    setattr(
                        inverter_charger_device, attr, self.parse_instance(field_json)
                    )

            # Parse data id fields if present
            for attr, key in INVERTER_CHARGER_DATA_ID_FIELD_MAP.items():
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
            map_fields(device_json, device, DEVICE_FIELD_MAP)

            # Handle enum fields
            map_enum_fields(self._logger, device_json, device, DEVICE_ENUM_FIELD_MAP)
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
            map_fields(hvac_json, hvac_device, HVAC_FIELD_MAP)

            # Handle instance fields
            for attr, key in HVAC_INSTANCE_FIELD_MAP.items():
                field_json = hvac_json.get(key)
                if field_json is not None:
                    setattr(hvac_device, attr, self.parse_instance(field_json))

            # Handle data id fields
            for attr, key in HVAC_DATA_ID_FIELD_MAP.items():
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
            map_fields(audio_stereo_json, audio_stereo_device, AUDIO_STEREO_FIELD_MAP)
            # Parse instance if present
            instance_json = audio_stereo_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                audio_stereo_device.instance = self.parse_instance(instance_json)
            # Parse circuit_ids if present
            map_list_fields(
                audio_stereo_json,
                audio_stereo_device,
                self._audio_stereo_list_field_map,
            )

            return audio_stereo_device
        except Exception as e:
            self._logger.error(f"Failed to parse Audio Stereo device: {e}")
            raise

    def parse_binary_logic_state(
        self, binary_logic_state_json: dict[str, Any]
    ) -> BinaryLogicState:
        """
        Parse the Binary Logic State object from the configuration.
        """
        try:
            binary_logic_state = BinaryLogicState()
            # Map required fields directly
            map_fields(
                binary_logic_state_json,
                binary_logic_state,
                BINARY_LOGIC_STATE_FIELD_MAP,
            )
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
            map_fields(
                ui_relationship_json, ui_relationship, UI_RELATIONSHIPS_FIELD_MAP
            )
            # Handle enum fields
            map_enum_fields(
                self._logger,
                ui_relationship_json,
                ui_relationship,
                UI_RELATIONSHIPS_ENUM_FIELD_MAP,
            )
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
            map_fields(pressure_json, pressure, PRESSURE_FIELD_MAP)
            # Parse instance if present
            instance_json = pressure_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                pressure.instance = self.parse_instance(instance_json)
            # Parse enum fields
            map_enum_fields(
                self._logger, pressure_json, pressure, PRESSURE_ENUM_FIELD_MAP
            )
            # Parse data id fields if present
            for attr, key in PRESSURE_DATA_ID_FIELD_MAP.items():
                field_json = pressure_json.get(key)
                if field_json is not None:
                    setattr(pressure, attr, self.parse_data_id(field_json))
            return pressure
        except Exception as e:
            self._logger.error(f"Failed to parse Pressure: {e}")
            raise

    def parse_engine(self, engine_json: dict[str, Any]) -> EngineDevice:
        """
        Parse the Engine device from the configuration.
        """
        try:
            engine_device = EngineDevice()
            # Map required fields directly
            map_fields(engine_json, engine_device, ENGINE_FIELD_MAP)
            # Parse instance if present
            instance_json = engine_json.get(JsonKeys.INSTANCE)
            if instance_json is not None:
                engine_device.instance = self.parse_instance(instance_json)
            # Handle enum fields
            map_enum_fields(
                self._logger, engine_json, engine_device, ENGINE_ENUM_FIELD_MAP
            )
            return engine_device
        except Exception as e:
            self._logger.error(f"Failed to parse Engine device: {e}")
            raise

    def parse_factory_metadata(
        self, factory_metadata_json: dict[str, Any]
    ) -> FactoryMetadata:
        """
        Parse the FactoryMetadata object from the configuration.
        """
        try:
            factory_metadata = FactoryMetadata()
            if Constants.FactoryDataSettings in factory_metadata_json:
                factory_metadata_value = factory_metadata_json[
                    Constants.FactoryDataSettings
                ]
                map_fields(
                    factory_metadata_value, factory_metadata, FACTORY_METADATA_FIELD_MAP
                )
            return factory_metadata
        except Exception as e:
            self._logger.error(f"Failed to parse factory metadata: {e}")
            raise

    def parse_config_metadata(
        self, config_metadata_json: dict[str, Any]
    ) -> ConfigMetadata:
        try:
            config_metadata = ConfigMetadata()
            map_fields(config_metadata_json, config_metadata, CONFIG_METADATA_FIELD_MAP)
            return config_metadata
        except Exception as e:
            self._logger.error(f"Failed to parse configuration metadata: {e}")
            raise

    def parse_categories(self, categories_json: dict[str, Any]) -> list[CategoryItem]:
        """
        Parse the Categories from the configuration.
        """
        try:
            category_item = CategoryItem()
            # Map required fields directly
            map_fields(categories_json, category_item, CATEGORY_FIELD_MAP)
            return category_item
        except Exception as e:
            self._logger.error(f"Failed to parse Categories: {e}")
            raise

    def parse_config(
        self,
        config_string: str,
        categories_str: str,
        config_metadata_str: str,
    ) -> N2kConfiguration:
        """
        Parse the configuration string and return a N2KConfiguration object.
        """
        try:
            n2k_configuration = N2kConfiguration()
            # Parse the configuration string
            config_json: dict[str, list[Any]] = json.loads(config_string)
            categories_json = json.loads(categories_str)
            config_metadata_json = json.loads(config_metadata_str)

            # GNSS
            if JsonKeys.GNSS in config_json:
                for gnss_json in config_json[JsonKeys.GNSS]:
                    gnss = self.parse_gnss(gnss_json)
                    if (gnss.instance is None) or (gnss.instance.enabled == False):
                        continue
                    n2k_configuration.gnss[gnss.instance.instance] = gnss

            # Circuit
            if JsonKeys.CIRCUITS in config_json:
                for circuit_json in config_json[JsonKeys.CIRCUITS]:
                    circuit = self.parse_circuit(circuit_json)
                    if (circuit.id is None) or (circuit.id.valid == False):
                        continue
                    if circuit.non_visible_circuit:
                        n2k_configuration.hidden_circuit[circuit.id.value] = circuit
                    else:
                        n2k_configuration.circuit[circuit.control_id] = circuit

            # DC
            if JsonKeys.DCS in config_json:
                for dc_json in config_json[JsonKeys.DCS]:
                    dc = self.parse_dc(dc_json)
                    if (dc.instance is None) or dc.instance.enabled == False:
                        continue
                    n2k_configuration.dc[dc.instance.instance] = dc

            # AC
            if JsonKeys.ACS in config_json:
                for ac_json in config_json[JsonKeys.ACS]:
                    ac_line = self.parse_ac(ac_json)
                    if ac_line.instance is None or ac_line.instance.enabled == False:
                        continue
                    resolved_instance = (
                        ac_line.instance.instance
                        if ac_line.instance.instance is not None
                        else 0
                    )
                    if not resolved_instance in n2k_configuration.ac:
                        n2k_configuration.ac[resolved_instance] = ACMeter()
                    if ac_line.line == ACLine.Line1:
                        n2k_configuration.ac[resolved_instance].line[1] = ac_line
                    elif ac_line.line == ACLine.Line2:
                        n2k_configuration.ac[resolved_instance].line[2] = ac_line
                    elif ac_line.line == ACLine.Line3:
                        n2k_configuration.ac[resolved_instance].line[3] = ac_line

            # Tank
            if JsonKeys.TANKS in config_json:
                for tank_json in config_json[JsonKeys.TANKS]:
                    tank = self.parse_tank(tank_json)
                    if (tank.instance is None) or (tank.instance.enabled == False):
                        continue
                    n2k_configuration.tank[tank.instance.instance] = tank

            # Inverter Charger
            if JsonKeys.INVERTER_CHARGERS in config_json:
                for inverter_charger_json in config_json[JsonKeys.INVERTER_CHARGERS]:
                    inverter_charger = self.parse_inverter_charger(
                        inverter_charger_json
                    )
                    instance = self.calculate_inverter_charger_instance(
                        inverter_charger_json
                    )
                    n2k_configuration.inverter_charger[instance] = inverter_charger

            # Device
            if JsonKeys.DEVICES in config_json:
                for device_json in config_json[JsonKeys.DEVICES]:
                    device = self.parse_device(device_json)
                    if (device.dipswitch is None) or (device.dipswitch == False):
                        continue
                    n2k_configuration.device[device.dipswitch] = device

            # HVAC
            if JsonKeys.HVACS in config_json:
                for hvac_json in config_json[JsonKeys.HVACS]:
                    hvac = self.parse_hvac(hvac_json)
                    if hvac.instance is None or hvac.instance.enabled == False:
                        continue
                    n2k_configuration.hvac[hvac.instance.instance] = hvac

            # Audio Stereo
            if JsonKeys.AUDIO_STEREOS in config_json:
                for audio_stereo_json in config_json[JsonKeys.AUDIO_STEREOS]:
                    audio = self.parse_audio_stereo(audio_stereo_json)
                    if audio.instance is None or audio.instance.enabled == False:
                        continue
                    n2k_configuration.audio_stereo[audio.instance.instance] = audio

            # Binary Logic State
            if JsonKeys.BINARY_LOGIC_STATES in config_json:
                for binary_logic_state_json in config_json[
                    JsonKeys.BINARY_LOGIC_STATES
                ]:
                    binary_logic_state = self.parse_binary_logic_state(
                        binary_logic_state_json
                    )
                    n2k_configuration.binary_logic_state[binary_logic_state.id] = (
                        binary_logic_state
                    )

            # UI Relationships
            if JsonKeys.UI_RELATIONSHIPS in config_json:
                for ui_relationship_json in config_json[JsonKeys.UI_RELATIONSHIPS]:
                    n2k_configuration.ui_relationships.append(
                        self.parse_ui_relationship(ui_relationship_json)
                    )

            # Pressure
            if JsonKeys.PRESSURES in config_json:
                for pressure_json in config_json[JsonKeys.PRESSURES]:
                    pressure = self.parse_pressure(pressure_json)
                    if pressure.instance is None or pressure.instance.enabled == False:
                        continue
                    n2k_configuration.pressure[pressure.instance.instance] = pressure

            # Mode
            if JsonKeys.MODES in config_json:
                for mode_json in config_json[JsonKeys.MODES]:
                    mode = self.parse_circuit(mode_json)
                    if (mode.id is None) or (mode.id.valid == False):
                        continue
                    n2k_configuration.mode[mode.id.value] = mode

            # Categories
            if JsonKeys.Items in categories_json:
                for category_json in categories_json[JsonKeys.Items]:
                    category = self.parse_category(category_json)

                    if category.name_utf8 == "":
                        continue
                    n2k_configuration.category.append(category)

            # Config Metadata
            n2k_configuration.config_metadata = self.parse_config_metadata(
                config_metadata_json
            )

            # BLS Alarm Mappings
            for bls in n2k_configuration.binary_logic_state.values():
                channel = get_bls_alarm_channel(bls, n2k_configuration.ui_relationships)
                if channel is not None:
                    bls_alarm_mapping = BLSAlarmMapping(alarm_channel=channel, bls=bls)
                    n2k_configuration.bls_alarm_mappings[bls.id] = bls_alarm_mapping
            return n2k_configuration

        except Exception as e:
            self._logger.error(f"Failed to parse config: {e}")
            raise

    def parse_engine_configuration(
        self, config_string: str, engine_configuration: EngineConfiguration
    ) -> EngineConfiguration:
        """
        Parse the engine configuration string and return an EngineConfiguration object.
        """
        try:
            # Parse the configuration string
            config_json: dict[str, list[Any]] = json.loads(config_string)

            # Engine
            if JsonKeys.ENGINES in config_json:
                for engine in config_json[JsonKeys.ENGINES]:
                    engine_instance_value = get_device_instance_value(engine)
                    if engine_instance_value is not None:
                        engine_configuration.devices[engine_instance_value] = (
                            self.parse_engine(engine)
                        )

            return engine_configuration

        except Exception as e:
            self._logger.error(f"Failed to parse engine config: {e}")
            raise
