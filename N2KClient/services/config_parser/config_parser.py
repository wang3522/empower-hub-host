import json
import logging
from typing import Any

from N2KClient.models.configuration.configuation import N2KConfiguration
from N2KClient.models.configuration.gnss import GNSSDevice
from N2KClient.models.configuration.circuit import (
    Circuit,
    CircuitLoad,
    CategoryItem,
)
from N2KClient.models.configuration.dc import DC
from N2KClient.models.configuration.ac import AC
from N2KClient.models.configuration.tank import Tank
from N2KClient.models.configuration.inverter_charger import InverterChargerDevice
from N2KClient.models.configuration.device import Device
from N2KClient.models.configuration.hvac import HVACDevice
from N2KClient.models.configuration.audio_stereo import AudioStereoDevice
from N2KClient.models.configuration.binary_logic_state import BinaryLogicStates
from N2KClient.models.configuration.ui_relationship_msg import (
    UiRelationShipMsg,
)
from N2KClient.models.configuration.pressure import Pressure
from N2KClient.models.configuration.engine import EnginesDevice
from N2KClient.models.configuration.sequential_name import SequentialName
from N2KClient.models.configuration.instance import Instance
from N2KClient.models.configuration.data_id import DataId
from N2KClient.models.constants import Constants, JsonKeys, AttrNames
from N2KClient.services.config_parser.field_maps import *
from N2KClient.services.config_parser.config_parser_helpers import (
    map_enum_fields,
    map_fields,
    map_list_fields,
    get_device_instance_value,
)


class ConfigParser:
    _config: N2KConfiguration
    _logger = logging.getLogger(
        f"{Constants.DBUS_N2K_CLIENT}: {Constants.Config_Parser}"
    )

    def __init__(self):
        self._config = N2KConfiguration()
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
            map_fields(circuit_load_json, circuit_load, CIRCUIT_LOAD_ENUM_FIELD_MAP)
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
            inverter_instance = inverter_instance_json.get(JsonKeys.INSTANCE_, None)
            charger_instance = charger_instance_json.get(JsonKeys.INSTANCE_, None)

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
    ) -> BinaryLogicStates:
        """
        Parse the Binary Logic State object from the configuration.
        """
        try:
            binary_logic_state = BinaryLogicStates()
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

    def parse_engine(self, engine_json: dict[str, Any]) -> EnginesDevice:
        """
        Parse the Engine device from the configuration.
        """
        try:
            engine_device = EnginesDevice()
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
                    gnss_id = gnss_json.get(JsonKeys.ID)
                    if gnss_id is not None:
                        device_id = f"{AttrNames.GNSS}.{gnss_id}"
                        n2k_configuration.gnss[device_id] = self.parse_gnss(gnss_json)

            # Circuit
            if JsonKeys.CIRCUIT in config_json:
                for circuit_json in config_json[JsonKeys.CIRCUIT]:
                    circuit_id = circuit_json.get(JsonKeys.ID)
                    if circuit_id is not None:
                        device_id = f"{AttrNames.CIRCUIT}.{circuit_id}"
                        n2k_configuration.circuit[device_id] = self.parse_circuit(
                            circuit_json
                        )

            # DC
            if JsonKeys.DC in config_json:
                for dc_json in config_json[JsonKeys.DC]:
                    dc_instance = get_device_instance_value(dc_json)
                    if dc_instance is not None:
                        device_id = f"{AttrNames.DC}.{dc_instance}"
                        n2k_configuration.dc[device_id] = self.parse_dc(dc_json)

            # AC
            if JsonKeys.AC in config_json:
                for ac_json in config_json[JsonKeys.AC]:
                    ac_instance = get_device_instance_value(ac_json)
                    if ac_instance is not None:
                        device_id = f"{AttrNames.AC}.{ac_instance}"
                        n2k_configuration.ac[device_id] = self.parse_ac(ac_json)

            # Tank
            if JsonKeys.TANK in config_json:
                for tank_json in config_json[JsonKeys.TANK]:
                    tank_instance = get_device_instance_value(tank_json)
                    if tank_instance is not None:
                        device_id = f"{AttrNames.TANK}.{tank_instance}"
                        n2k_configuration.tank[device_id] = self.parse_tank(tank_json)

            # Inverter Charger
            if JsonKeys.INVERTER_CHARGER in config_json:
                for inverter_charger_json in config_json[JsonKeys.INVERTER_CHARGER]:
                    inverter_charger_instance = (
                        self.calculate_inverter_charger_instance(inverter_charger_json)
                    )
                    if inverter_charger_instance is not None:
                        inverter_charger_device_id = (
                            f"{AttrNames.INVERTER_CHARGER}.{inverter_charger_instance}"
                        )
                        # Add the Inverter Charger device to the configuration
                        n2k_configuration.inverter_charger[
                            inverter_charger_device_id
                        ] = self.parse_inverter_charger(inverter_charger_json)

            # Device
            if JsonKeys.DEVICE in config_json:
                for device_json in config_json[JsonKeys.DEVICE]:
                    device_dipswitch = device_json.get(JsonKeys.DIPSWITCH)
                    if device_dipswitch is not None:
                        device_id = f"{AttrNames.DEVICE}.{device_dipswitch}"
                        # Add the Device to the configuration
                        n2k_configuration.device[device_id] = self.parse_device(
                            device_json
                        )

            # HVAC
            if JsonKeys.HVAC in config_json:
                for hvac_json in config_json[JsonKeys.HVAC]:
                    hvac_instance = get_device_instance_value(hvac_json)
                    self._logger.debug(f"hvac_instance: {hvac_instance}")
                    if hvac_instance is not None:
                        self._logger.debug("HERE hvac")
                        device_id = f"{AttrNames.HVAC}.{hvac_instance}"
                        n2k_configuration.hvac[device_id] = self.parse_hvac(hvac_json)

            # Audio Stereo
            if JsonKeys.AUDIO_STEREO in config_json:
                for audio_stereo_json in config_json[JsonKeys.AUDIO_STEREO]:
                    audio_stereo_instance = get_device_instance_value(audio_stereo_json)
                    self._logger.debug(
                        f"audio_stereo_instance: {audio_stereo_instance}"
                    )
                    if audio_stereo_instance is not None:
                        device_id = f"{AttrNames.AUDIO_STEREO}.{audio_stereo_instance}"

                        n2k_configuration.audio_stereo[device_id] = (
                            self.parse_audio_stereo(audio_stereo_json)
                        )

            # Binary Logic State
            if JsonKeys.BINARY_LOGIC_STATE in config_json:
                for binary_logic_state_json in config_json[JsonKeys.BINARY_LOGIC_STATE]:
                    binary_logic_state_id = binary_logic_state_json.get(JsonKeys.ID)
                    if binary_logic_state_id is not None:
                        device_id = (
                            f"{AttrNames.BINARY_LOGIC_STATE}.{binary_logic_state_id}"
                        )
                        n2k_configuration.binary_logic_state[device_id] = (
                            self.parse_binary_logic_state(binary_logic_state_json)
                        )
            # UI Relationships
            if JsonKeys.UI_RELATIONSHIP in config_json:
                for ui_relationship_json in config_json[JsonKeys.UI_RELATIONSHIP]:
                    ui_relationship_id = ui_relationship_json.get(JsonKeys.ID)
                    if ui_relationship_id is not None:
                        n2k_configuration.ui_relationships.append(
                            self.parse_ui_relationship(ui_relationship_json)
                        )
            # Pressure
            if JsonKeys.PRESSURE in config_json:
                for pressure_json in config_json[JsonKeys.PRESSURE]:
                    pressure_instance = get_device_instance_value(pressure_json)
                    if pressure_instance is not None:
                        device_id = f"{AttrNames.PRESSURE}.{pressure_instance}"
                        # Add the Pressure device to the configuration
                        n2k_configuration.pressure[device_id] = self.parse_pressure(
                            pressure_json
                        )

            # Mode
            if JsonKeys.MODE in config_json:
                for mode_json in config_json[JsonKeys.MODE]:
                    mode_id = mode_json.get(JsonKeys.ID)
                    if mode_id is not None:
                        device_id = f"{AttrNames.MODE}.{mode_id}"
                        n2k_configuration.mode[device_id] = self.parse_circuit(
                            mode_json
                        )

            # Engine
            if JsonKeys.ENGINE in config_json:
                for engine in config_json[JsonKeys.ENGINE]:
                    engine_instance = engine.get(JsonKeys.INSTANCE)
                    if engine_instance is not None:
                        engine_instance_value = engine_instance.get(JsonKeys.VALUE)
                        if engine_instance_value is not None:
                            device_id = f"{AttrNames.ENGINE}.{engine_instance_value}"
                            n2k_configuration.engine[device_id] = self.parse_engine(
                                engine
                            )

            return n2k_configuration

        except Exception as e:
            self._logger.error(f"Failed to parse config: {e}")
            raise
