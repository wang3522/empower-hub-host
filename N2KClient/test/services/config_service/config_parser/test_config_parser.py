import json
from logging import Logger
import unittest
from unittest.mock import MagicMock, MagicMock, patch

from N2KClient.n2kclient.models.empower_system.alarm_list import AlarmList
from N2KClient.n2kclient.models.n2k_configuration.ac import AC
from N2KClient.n2kclient.models.n2k_configuration.ac_meter import ACMeter
from N2KClient.n2kclient.models.n2k_configuration.alarm_limit import AlarmLimit
from N2KClient.n2kclient.models.n2k_configuration.audio_stereo import AudioStereoDevice
from N2KClient.n2kclient.models.n2k_configuration.binary_logic_state import (
    BinaryLogicState,
)
from N2KClient.n2kclient.models.n2k_configuration.category_item import CategoryItem
from N2KClient.n2kclient.models.n2k_configuration.circuit import Circuit, CircuitLoad
from N2KClient.n2kclient.models.n2k_configuration.config_metadata import ConfigMetadata
from N2KClient.n2kclient.models.n2k_configuration.data_id import DataId
from N2KClient.n2kclient.models.n2k_configuration.dc import DC
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineDevice
from N2KClient.n2kclient.models.n2k_configuration.engine_configuration import (
    EngineConfiguration,
)
from N2KClient.n2kclient.models.n2k_configuration.factory_metadata import (
    FactoryMetadata,
)
from N2KClient.n2kclient.models.n2k_configuration.gnss import GNSSDevice
from N2KClient.n2kclient.models.n2k_configuration.instance import Instance
from N2KClient.n2kclient.models.n2k_configuration.inverter_charger import (
    InverterChargerDevice,
)
from N2KClient.n2kclient.models.n2k_configuration.pressure import Pressure
from N2KClient.n2kclient.models.n2k_configuration.sequential_name import SequentialName
from N2KClient.n2kclient.models.n2k_configuration.tank import Tank
from N2KClient.n2kclient.models.n2k_configuration.ui_relationship_msg import (
    UiRelationShipMsg,
)
from N2KClient.n2kclient.models.n2k_configuration.value_u32 import ValueU32
from N2KClient.n2kclient.services.config_service.config_parser.config_parser import (
    ConfigParser,
)
from N2KClient.n2kclient.models.n2k_configuration.device import Device
from N2KClient.n2kclient.models.n2k_configuration.hvac import HVACDevice
from N2KClient.n2kclient.models.n2k_configuration.ac import ACLine


class TestConfigParser(unittest.TestCase):
    """
    Unit tests for ConfigParser
    """

    def test_config_parser_init(self):
        """
        Tests parsing of configuration data.
        """
        config_parser = ConfigParser()

        self.assertIsNotNone(config_parser)
        self.assertIsInstance(config_parser, ConfigParser)
        self.assertIsInstance(config_parser._logger, Logger)

    def test_parse_sequential_name(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            res = config_parser.parse_sequential_name("test_name")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, SequentialName)

    def test_parse_sequential_name_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_sequential_name("test_name")

    def test_parse_value_u32(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            res = config_parser.parse_value_u32("test_name")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, ValueU32)

    def test_parse_value_u32_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_value_u32("test_name")

    def test_parse_value_data_id(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            res = config_parser.parse_data_id("test_name")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, DataId)

    def test_parse_value_data_id_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_data_id("test_name")

    def test_parse__instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            res = config_parser.parse_instance("test_name")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, Instance)

    def test_parse_instance_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_instance("test_name")

    def test_parse_gnss_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            gnss_json = {"Instance": "testinstance"}
            res = config_parser.parse_gnss(gnss_json=gnss_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            self.assertIsInstance(res, GNSSDevice)

    def test_parse_gnss_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            gnss_json = {}
            res = config_parser.parse_gnss(gnss_json=gnss_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            self.assertIsInstance(res, GNSSDevice)

    def test_parse_value_instance_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_instance("test_name")

    def test_parse_circuit_load(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields:
            res = config_parser.parse_circuit_load("test_name")
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            self.assertIsInstance(res, CircuitLoad)

    def test_parse_circuit_load_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_circuit_load("test_name")

    def test_parse_category(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            res = config_parser.parse_category("test_name")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, CategoryItem)

    def test_parse_category_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_category("test_name")

    def test_parse_alarm_limit(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            res = config_parser.parse_alarm_limit("test_name")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, AlarmLimit)

    def test_parse_alarm_limit_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_alarm_limit("test_name")

    def test_parse_circuit(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id, patch.object(
            config_parser, "parse_value_u32"
        ) as mock_parse_value_u32:
            circuit_json = {
                "VoltageSource": "testinstance",
                "SingleThrowId": "testid",
                "Id": "testid",
            }
            res = config_parser.parse_circuit(circuit_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_called_once_with("testid")
            mock_parse_value_u32.assert_called_once_with("testid")
            self.assertIsInstance(res, Circuit)

    def test_parse_circuit_no_id(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id, patch.object(
            config_parser, "parse_value_u32"
        ) as mock_parse_value_u32:
            circuit_json = {
                "VoltageSource": "testinstance",
                "SingleThrowId": "testid",
            }
            res = config_parser.parse_circuit(circuit_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_called_once_with("testid")
            mock_parse_value_u32.assert_not_called()
            self.assertIsInstance(res, Circuit)

    def test_parse_circuit_no_single_throw_id(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id, patch.object(
            config_parser, "parse_value_u32"
        ) as mock_parse_value_u32:
            circuit_json = {
                "VoltageSource": "testinstance",
                "Id": "testid",
            }
            res = config_parser.parse_circuit(circuit_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_not_called()
            mock_parse_value_u32.assert_called_once_with("testid")
            self.assertIsInstance(res, Circuit)

    def test_parse_circuit_no_voltage_source(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id, patch.object(
            config_parser, "parse_value_u32"
        ) as mock_parse_value_u32:
            circuit_json = {
                "SingleThrowId": "testid",
                "Id": "testid",
            }
            res = config_parser.parse_circuit(circuit_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            mock_parse_data_id.assert_called_once_with("testid")
            mock_parse_value_u32.assert_called_once_with("testid")
            self.assertIsInstance(res, Circuit)

    def test_parse_circuit_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_circuit("test_name")

    def test_parse_dc(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            dc_json = {
                "HighVoltage": "testHighVoltage",
                "Instance": "testinstance",
            }
            res = config_parser.parse_dc(dc_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_alarm_limit.assert_called_once_with("testHighVoltage")
            self.assertIsInstance(res, DC)

    def test_parse_dc_no_alarm_limit(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            dc_json = {
                "Instance": "testinstance",
            }
            res = config_parser.parse_dc(dc_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_alarm_limit.assert_not_called()
            self.assertIsInstance(res, DC)

    def test_parse_dc_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            dc_json = {
                "HighVoltage": "testHighVoltage",
            }
            res = config_parser.parse_dc(dc_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            mock_parse_alarm_limit.assert_called_once_with("testHighVoltage")
            self.assertIsInstance(res, DC)

    def test_parse_dc_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            dc_json = {
                "HighVoltage": "testHighVoltage",
                "Instance": "testinstance",
            }
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_dc("test_name")

    def test_parse_ac(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            ac_json = {
                "HighVoltage": "testHighVoltage",
                "Instance": "testinstance",
            }
            res = config_parser.parse_ac(ac_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_alarm_limit.assert_called_once_with("testHighVoltage")
            self.assertIsInstance(res, AC)

    def test_parse_ac_no_alarm_limit(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            ac_json = {
                "Instance": "testinstance",
            }
            res = config_parser.parse_ac(ac_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_alarm_limit.assert_not_called()
            self.assertIsInstance(res, AC)

    def test_parse_ac_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            ac_json = {
                "HighVoltage": "testHighVoltage",
            }
            res = config_parser.parse_ac(ac_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            mock_parse_alarm_limit.assert_called_once_with("testHighVoltage")
            self.assertIsInstance(res, AC)

    def test_parse_ac_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            ac_json = {
                "HighVoltage": "testHighVoltage",
                "Instance": "testinstance",
            }
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_ac(ac_json)

    def test_parse_tank(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            tank_json = {
                "HighLimit": "testHighLimit",
                "Instance": "testinstance",
                "CircuitId": "testCircuitId",
            }
            res = config_parser.parse_tank(tank_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_alarm_limit.assert_called_once_with("testHighLimit")
            mock_parse_data_id.assert_called_once_with("testCircuitId")
            self.assertIsInstance(res, Tank)

    def test_parse_tank_no_data_id(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            tank_json = {
                "HighLimit": "testHighLimit",
                "Instance": "testinstance",
            }
            res = config_parser.parse_tank(tank_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_alarm_limit.assert_called_once_with("testHighLimit")
            mock_parse_data_id.assert_not_called()
            self.assertIsInstance(res, Tank)

    def test_parse_tank_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            tank_json = {
                "HighLimit": "testHighLimit",
                "CircuitId": "testCircuitId",
            }
            res = config_parser.parse_tank(tank_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            mock_parse_alarm_limit.assert_called_once_with("testHighLimit")
            mock_parse_data_id.assert_called_once_with("testCircuitId")
            self.assertIsInstance(res, Tank)

    def test_parse_tank_no_alarm_list(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields, patch.object(
            config_parser, "parse_alarm_limit"
        ) as mock_parse_alarm_limit, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            tank_json = {
                "Instance": "testinstance",
                "CircuitId": "testCircuitId",
            }
            res = config_parser.parse_tank(tank_json)
            mock_map_fields.assert_called_once()
            mock_map_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_alarm_limit.assert_not_called()
            mock_parse_data_id.assert_called_once_with("testCircuitId")
            self.assertIsInstance(res, Tank)

    def test_calculate_inverter_charger_instance(self):
        config_parser = ConfigParser()
        inverter_charger_json = {
            "InverterInstance": {"Instance": 1111, "Enabled": True},
            "ChargerInstance": {"Instance": 2222, "Enabled": True},
        }
        res = config_parser.calculate_inverter_charger_instance(inverter_charger_json)
        self.assertTrue(res, (1111 << 8) | 1111)

    def test_calculate_inverter_charger_instance_none(self):
        config_parser = ConfigParser()
        inverter_charger_json = {
            "InverterInstance": {"Instance": 1111, "Enabled": False},
            "ChargerInstance": {"Instance": 2222, "Enabled": False},
        }
        res = config_parser.calculate_inverter_charger_instance(inverter_charger_json)
        self.assertIsNone(res)

    def test_calculate_inverter_charger_exception(self):
        """
        Test exception reraised
        """
        config_parser = ConfigParser()
        with self.assertRaises(Exception):
            config_parser.calculate_inverter_charger_instance("NOTADICT")

    def test_parse_inverter_charger(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            inverter_charger_json = {
                "InverterInstance": "testinstance",
                "InverterACId": "testInverterAcId",
            }
            res = config_parser.parse_inverter_charger(inverter_charger_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_called_once_with("testInverterAcId")
            self.assertIsInstance(res, InverterChargerDevice)

    def test_parse_inverter_charger_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            inverter_charger_json = {
                "InverterACId": "testInverterAcId",
            }
            res = config_parser.parse_inverter_charger(inverter_charger_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            mock_parse_data_id.assert_called_once_with("testInverterAcId")
            self.assertIsInstance(res, InverterChargerDevice)

    def test_parse_inverter_charger_no_data_id(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            inverter_charger_json = {
                "InverterInstance": "testinstance",
            }
            res = config_parser.parse_inverter_charger(inverter_charger_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_not_called()
            self.assertIsInstance(res, InverterChargerDevice)

    def test_parse_inverter_charger_instance_none(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            inverter_charger_json = {
                "InverterInstance": None,
                "InverterACId": "testInverterAcId",
            }
            res = config_parser.parse_inverter_charger(inverter_charger_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            mock_parse_data_id.assert_called_once_with("testInverterAcId")
            self.assertIsInstance(res, InverterChargerDevice)

    def test_parse_inverter_charger_data_none(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            inverter_charger_json = {
                "InverterInstance": "testinstance",
                "InverterACId": None,
            }
            res = config_parser.parse_inverter_charger(inverter_charger_json)
            mock_map_fields.assert_called_once()
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_not_called()
            self.assertIsInstance(res, InverterChargerDevice)

    def test_parse_inverter_charger_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            inverter_charger_json = {
                "InverterInstance": "testinstance",
                "InverterACId": None,
            }
            with self.assertRaises(Exception):
                config_parser.parse_inverter_charger(inverter_charger_json)

    def test_parse_device(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_map_enum_fields:
            res = config_parser.parse_device("device_json")
            mock_map_enum_fields.assert_called_once()
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, Device)

    def test_parse_device_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_device("device_json")

    def test_parse_hvac(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            hvac_json = {
                "Instance": "testinstance",
                "FanModeId": "testFanModeId",
            }
            res = config_parser.parse_hvac(hvac_json)
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_called_once_with("testFanModeId")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, HVACDevice)

    def test_parse_hvac(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            hvac_json = {
                "Instance": "testinstance",
            }
            res = config_parser.parse_hvac(hvac_json)
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_parse_data_id.assert_not_called()
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, HVACDevice)

    def test_parse_hvac_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, mock_map_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            hvac_json = {
                "FanModeId": "testFanModeId",
            }
            res = config_parser.parse_hvac(hvac_json)
            mock_parse_instance.assert_not_called()
            mock_parse_data_id.assert_called_once_with("testFanModeId")
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, HVACDevice)

    def test_parse_hvac_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_hvac("hvac_json")

    def test_parse_audio_stereo(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_list_fields"
        ) as mock_list_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            audio_json = {
                "Instance": "testinstance",
            }
            res = config_parser.parse_audio_stereo(audio_json)
            mock_parse_instance.assert_called_once_with("testinstance")
            mock_list_fields.assert_called_once()
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, AudioStereoDevice)

    def test_parse_audio_stereo_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_list_fields"
        ) as mock_list_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            audio_json = {}
            res = config_parser.parse_audio_stereo(audio_json)
            mock_parse_instance.assert_not_called()
            mock_list_fields.assert_called_once()
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, AudioStereoDevice)

    def test_parse_audio_stereo_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_audio_stereo("audio_json")

    def test_parse_binary_logic_state(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            binary_logic_json = {}
            res = config_parser.parse_binary_logic_state(binary_logic_json)
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, BinaryLogicState)

    def test_parse_binary_logic_state_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_binary_logic_state("binary_logic_json")

    def test_parse_ui_relationship(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_enum_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            ui_relationship_json = {}
            res = config_parser.parse_ui_relationship(ui_relationship_json)
            mock_parse_instance.assert_not_called()
            mock_enum_fields.assert_called_once()
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, UiRelationShipMsg)

    def test_parse_ui_relationship_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_ui_relationship("ui_relationship_json")

    def test_parse_pressure(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_enum_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            pressure_json = {"Instance": "1", "CircuitId": "2"}
            res = config_parser.parse_pressure(pressure_json)
            mock_map_fields.assert_called_once()
            mock_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_with("1")
            mock_parse_data_id.assert_called_with("2")
            self.assertIsInstance(res, Pressure)

    def test_parse_pressure_no_data_id(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_enum_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            pressure_json = {"Instance": "1"}
            res = config_parser.parse_pressure(pressure_json)
            mock_map_fields.assert_called_once()
            mock_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_with("1")
            mock_parse_data_id.assert_not_called()
            self.assertIsInstance(res, Pressure)

    def test_parse_pressure_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_enum_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance, patch.object(
            config_parser, "parse_data_id"
        ) as mock_parse_data_id:
            pressure_json = {"CircuitId": "2"}
            res = config_parser.parse_pressure(pressure_json)
            mock_map_fields.assert_called_once()
            mock_enum_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            mock_parse_data_id.assert_called_with("2")
            self.assertIsInstance(res, Pressure)

    def test_parse_pressure_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_pressure("pressure_json")

    def test_parse_engine(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_enum_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            engine_json = {"Instance": "1"}
            res = config_parser.parse_engine(engine_json)
            mock_map_fields.assert_called_once()
            mock_enum_fields.assert_called_once()
            mock_parse_instance.assert_called_with("1")
            self.assertIsInstance(res, EngineDevice)

    def test_parse_engine_no_instance(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_enum_fields"
        ) as mock_enum_fields, patch.object(
            config_parser, "parse_instance"
        ) as mock_parse_instance:
            engine_json = {}
            res = config_parser.parse_engine(engine_json)
            mock_map_fields.assert_called_once()
            mock_enum_fields.assert_called_once()
            mock_parse_instance.assert_not_called()
            self.assertIsInstance(res, EngineDevice)

    def test_parse_engine_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            engine_json = {"Instance": "1"}
            with self.assertRaises(Exception):
                config_parser.parse_engine(engine_json)

    def test_parse_factory_metadata(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            engine_json = {"FactoryDataSettings": {}}
            res = config_parser.parse_factory_metadata(engine_json)
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, FactoryMetadata)

    def test_parse_factory_metadata_no_key(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            engine_json = {}
            res = config_parser.parse_factory_metadata(engine_json)
            mock_map_fields.assert_not_called()
            self.assertIsInstance(res, FactoryMetadata)

    def test_parse_config_metadata(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            config_metadata = {}
            res = config_parser.parse_config_metadata(config_metadata)
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, ConfigMetadata)

    def test_parse_config_metadata_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            config_metadata = {}
            mock_map_fields.side_effect = Exception("Test exception")
            with self.assertRaises(Exception):
                config_parser.parse_config_metadata(config_metadata)

    def test_parse_categories(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            categories_json = {"Categories": []}
            res = config_parser.parse_categories(categories_json)
            mock_map_fields.assert_called_once()
            self.assertIsInstance(res, CategoryItem)

    def test_parse_categories_exception(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.map_fields"
        ) as mock_map_fields:
            mock_map_fields.side_effect = Exception("Test exception")
            categories_json = {"Categories": []}
            with self.assertRaises(Exception):
                config_parser.parse_categories(categories_json)

    def test_parse_config_gnss(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_gnss") as mock_parse_gnss:
            mock_gnss = MagicMock(instance=MagicMock(instance=0, enabled=True))
            mock_parse_gnss.return_value = mock_gnss
            res = config_parser.parse_config('{"GNSS": [{}]}', "{}", "{}")
            mock_parse_gnss.assert_called_once()
            self.assertEqual(len(res.gnss), 1)
            self.assertIn(0, res.gnss)
            self.assertEqual(res.gnss[0], mock_gnss)

    def test_parse_config_gnss_instance_none(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_gnss") as mock_parse_gnss:
            mock_gnss = MagicMock(instance=None)
            mock_parse_gnss.return_value = mock_gnss
            res = config_parser.parse_config('{"GNSS": [{}]}', "{}", "{}")
            mock_parse_gnss.assert_called_once()
            self.assertEqual(len(res.gnss), 0)
            self.assertNotIn(0, res.gnss)

    def test_parse_config_circuit_nonvisible(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_circuit") as mock_parse_circuit:
            mock_circuit = MagicMock(
                id=MagicMock(valid=True, value=0), non_visible_circuit=True
            )
            mock_parse_circuit.return_value = mock_circuit
            res = config_parser.parse_config('{"Circuits": [{}]}', "{}", "{}")
            mock_parse_circuit.assert_called_once()
            self.assertEqual(len(res.hidden_circuit), 1)
            self.assertIn(0, res.hidden_circuit)
            self.assertEqual(res.hidden_circuit[0], mock_circuit)

    def test_parse_config_circuit_no_id(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_circuit") as mock_parse_circuit:
            mock_circuit = MagicMock(id=None, non_visible_circuit=True)
            mock_parse_circuit.return_value = mock_circuit
            res = config_parser.parse_config('{"Circuits": [{}]}', "{}", "{}")
            mock_parse_circuit.assert_called_once()
            self.assertEqual(len(res.hidden_circuit), 0)
            self.assertNotIn(0, res.hidden_circuit)

    def test_parse_config_circuit_visible(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_circuit") as mock_parse_circuit:
            mock_circuit = MagicMock(
                id=MagicMock(valid=True, value=0),
                non_visible_circuit=False,
                control_id=123,
            )
            mock_parse_circuit.return_value = mock_circuit
            res = config_parser.parse_config('{"Circuits": [{}]}', "{}", "{}")
            mock_parse_circuit.assert_called_once()
            self.assertEqual(len(res.circuit), 1)
            self.assertIn(123, res.circuit)
            self.assertEqual(res.circuit[123], mock_circuit)

    def test_parse_config_ac_line_1(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_ac") as mock_parse_ac:
            mock_ac = MagicMock(
                instance=MagicMock(enabled=True, instance=123), line=ACLine.Line1
            )
            mock_parse_ac.return_value = mock_ac
            res = config_parser.parse_config('{"ACs": [{}]}', "{}", "{}")
            mock_parse_ac.assert_called_once()
            self.assertEqual(len(res.ac), 1)
            self.assertIn(123, res.ac)
            self.assertEqual(res.ac[123].line[1], mock_ac)

    def test_parse_config_ac_line_2(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_ac") as mock_parse_ac:
            mock_ac = MagicMock(
                instance=MagicMock(enabled=True, instance=123), line=ACLine.Line2
            )
            mock_parse_ac.return_value = mock_ac
            res = config_parser.parse_config('{"ACs": [{}]}', "{}", "{}")
            mock_parse_ac.assert_called_once()
            self.assertEqual(len(res.ac), 1)
            self.assertIn(123, res.ac)
            self.assertEqual(res.ac[123].line[2], mock_ac)

    def test_parse_config_ac_line_3(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_ac") as mock_parse_ac:
            mock_ac = MagicMock(
                instance=MagicMock(enabled=True, instance=123), line=ACLine.Line3
            )
            mock_parse_ac.return_value = mock_ac
            res = config_parser.parse_config('{"ACs": [{}]}', "{}", "{}")
            mock_parse_ac.assert_called_once()
            self.assertEqual(len(res.ac), 1)
            self.assertIn(123, res.ac)
            self.assertEqual(res.ac[123].line[3], mock_ac)

    def test_parse_config_no_instance(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_ac") as mock_parse_ac:
            mock_ac = MagicMock(instance=None, line=ACLine.Line1)
            mock_parse_ac.return_value = mock_ac
            res = config_parser.parse_config('{"ACs": [{}]}', "{}", "{}")
            mock_parse_ac.assert_called_once()
            self.assertEqual(len(res.ac), 0)

    def test_parse_config_default_instance_0(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_ac") as mock_parse_ac:
            mock_ac = MagicMock(
                instance=MagicMock(enabled=True, instance=None), line=ACLine.Line1
            )
            mock_parse_ac.return_value = mock_ac
            res = config_parser.parse_config('{"ACs": [{}]}', "{}", "{}")
            mock_parse_ac.assert_called_once()
            self.assertEqual(len(res.ac), 1)
            self.assertIn(0, res.ac)
            self.assertEqual(res.ac[0].line[1], mock_ac)

    def test_parse_config_adds_ac_meter(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_ac") as mock_parse_ac:
            mock_ac = MagicMock(instance=MagicMock(enabled=True, instance=None))
            mock_parse_ac.return_value = mock_ac
            res = config_parser.parse_config('{"ACs": [{}]}', "{}", "{}")
            mock_parse_ac.assert_called_once()
            self.assertEqual(len(res.ac), 1)
            self.assertIn(0, res.ac)
            self.assertIsInstance(res.ac[0], ACMeter)

    def test_parse_config_tank(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_tank") as mock_parse_tank:
            mock_tank = MagicMock(instance=MagicMock(enabled=True, instance=0))
            mock_parse_tank.return_value = mock_tank
            res = config_parser.parse_config('{"Tanks": [{}]}', "{}", "{}")
            mock_parse_tank.assert_called_once()
            self.assertEqual(len(res.tank), 1)
            self.assertIn(0, res.tank)
            self.assertEqual(res.tank[0], mock_tank)

    def test_parse_config_tank_no_instance(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_tank") as mock_parse_tank:
            mock_tank = MagicMock(instance=None)
            mock_parse_tank.return_value = mock_tank
            res = config_parser.parse_config('{"Tanks": [{}]}', "{}", "{}")
            mock_parse_tank.assert_called_once()
            self.assertEqual(len(res.tank), 0)

    def test_parse_config_inverter_chargers(self):
        config_parser = ConfigParser()
        with patch.object(
            config_parser, "parse_inverter_charger"
        ) as mock_parse_inverter_charger, patch.object(
            config_parser, "calculate_inverter_charger_instance"
        ) as mock_calculate_inverter_charger_instance:
            mock_calculate_inverter_charger_instance.return_value = 0
            mock_inverter_charger = MagicMock(
                instance=MagicMock(enabled=True, instance=0)
            )
            mock_parse_inverter_charger.return_value = mock_inverter_charger
            res = config_parser.parse_config('{"InverterChargers": [{}]}', "{}", "{}")
            mock_parse_inverter_charger.assert_called_once()
            mock_calculate_inverter_charger_instance.assert_called_once()
            self.assertEqual(len(res.inverter_charger), 1)
            self.assertIn(0, res.inverter_charger)
            self.assertEqual(res.inverter_charger[0], mock_inverter_charger)

    def test_parse_config_devices(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_device") as mock_parse_device:
            mock_device = MagicMock(dipswitch=1234)
            mock_parse_device.return_value = mock_device
            res = config_parser.parse_config('{"Devices": [{}]}', "{}", "{}")
            mock_parse_device.assert_called_once()
            self.assertEqual(len(res.device), 1)
            self.assertIn(1234, res.device)
            self.assertEqual(res.device[1234], mock_device)

    def test_parse_config_devices_no_dipswitch(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_device") as mock_parse_device:
            mock_device = MagicMock(dipswitch=None)
            mock_parse_device.return_value = mock_device
            res = config_parser.parse_config('{"Devices": [{}]}', "{}", "{}")
            mock_parse_device.assert_called_once()
            self.assertEqual(len(res.device), 0)

    def test_parse_config_hvacs(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_hvac") as mock_parse_hvac:
            mock_hvac = MagicMock(instance=MagicMock(enabled=True, instance=0))
            mock_parse_hvac.return_value = mock_hvac
            res = config_parser.parse_config('{"HVACs": [{}]}', "{}", "{}")
            mock_parse_hvac.assert_called_once()
            self.assertEqual(len(res.hvac), 1)
            self.assertIn(0, res.hvac)
            self.assertEqual(res.hvac[0], mock_hvac)

    def test_parse_config_hvacs_no_instance(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_hvac") as mock_parse_hvac:
            mock_hvac = MagicMock(instance=None)
            mock_parse_hvac.return_value = mock_hvac
            res = config_parser.parse_config('{"HVACs": [{}]}', "{}", "{}")
            mock_parse_hvac.assert_called_once()
            self.assertEqual(len(res.hvac), 0)

    def test_parse_config_binary_logic_states(self):
        config_parser = ConfigParser()
        with patch.object(
            config_parser, "parse_binary_logic_state"
        ) as mock_parse_binary_logic_state:
            mock_binary_logic_state = MagicMock(id=1)
            mock_parse_binary_logic_state.return_value = mock_binary_logic_state
            res = config_parser.parse_config('{"BinaryLogicStates": [{}]}', "{}", "{}")
            mock_parse_binary_logic_state.assert_called_once()
            self.assertEqual(len(res.binary_logic_state), 1)
            self.assertIn(1, res.binary_logic_state)
            self.assertEqual(res.binary_logic_state[1], mock_binary_logic_state)

    def test_parse_config_ui_relationships(self):
        config_parser = ConfigParser()
        with patch.object(
            config_parser, "parse_ui_relationship"
        ) as mock_parse_ui_relationship:
            mock_ui_relationship = MagicMock(id=1)
            mock_parse_ui_relationship.return_value = mock_ui_relationship
            res = config_parser.parse_config('{"UiRelationships": [{}]}', "{}", "{}")
            mock_parse_ui_relationship.assert_called_once()
            self.assertEqual(len(res.ui_relationships), 1)
            self.assertEqual(res.ui_relationships[0], mock_ui_relationship)

    def test_parse_config_pressure(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_pressure") as mock_parse_pressure:
            mock_pressure = MagicMock(instance=MagicMock(enabled=True, instance=0))
            mock_parse_pressure.return_value = mock_pressure
            res = config_parser.parse_config('{"Pressures": [{}]}', "{}", "{}")
            mock_parse_pressure.assert_called_once()
            self.assertEqual(len(res.pressure), 1)
            self.assertIn(0, res.pressure)
            self.assertEqual(res.pressure[0], mock_pressure)

    def test_parse_config_pressure_no_instance(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_pressure") as mock_parse_pressure:
            mock_pressure = MagicMock(instance=None)
            mock_parse_pressure.return_value = mock_pressure
            res = config_parser.parse_config('{"Pressures": [{}]}', "{}", "{}")
            mock_parse_pressure.assert_called_once()
            self.assertEqual(len(res.pressure), 0)

    def test_parse_config_mode(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_circuit") as mock_parse_circuit:
            mock_mode = MagicMock(id=MagicMock(valid=True, value=0))
            mock_parse_circuit.return_value = mock_mode
            res = config_parser.parse_config('{"Modes": [{}]}', "{}", "{}")
            mock_parse_circuit.assert_called_once()
            self.assertEqual(len(res.mode), 1)
            self.assertIn(0, res.mode)
            self.assertEqual(res.mode[0], mock_mode)

    def test_parse_config_mode_no_id(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_circuit") as mock_parse_circuit:
            mock_mode = MagicMock(id=None)
            mock_parse_circuit.return_value = mock_mode
            res = config_parser.parse_config('{"Modes": [{}]}', "{}", "{}")
            mock_parse_circuit.assert_called_once()
            self.assertEqual(len(res.mode), 0)

    def test_parse_config_categories(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_category") as mock_parse_category:
            mock_category = MagicMock(name_utf8="testname")
            mock_parse_category.return_value = mock_category
            categories_str = '{"Items": [{}]}'
            res = config_parser.parse_config("{}", categories_str, "{}")
            mock_parse_category.assert_called_once()
            self.assertEqual(len(res.category), 1)
            self.assertEqual(res.category[0], mock_category)

    def test_parse_config_categories_no_name(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_category") as mock_parse_category:
            mock_category = MagicMock(name_utf8="")
            mock_parse_category.return_value = mock_category
            categories_str = '{"Items": [{}]}'
            res = config_parser.parse_config("{}", categories_str, "{}")
            mock_parse_category.assert_called_once()
            self.assertEqual(len(res.category), 0)

    def test_parse_config_metadata(self):
        config_parser = ConfigParser()
        with patch.object(
            config_parser, "parse_config_metadata"
        ) as mock_parse_config_metadata:
            mock_metadata = MagicMock()
            mock_parse_config_metadata.return_value = mock_metadata
            config_metadata_str = '{"Test": "Value"}'
            res = config_parser.parse_config("{}", "{}", config_metadata_str)
            mock_parse_config_metadata.assert_called_once_with({"Test": "Value"})
            self.assertEqual(res.config_metadata, mock_metadata)

    def test_parse_config_bls_alarm_mappings(self):
        config_parser = ConfigParser()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.get_bls_alarm_channel"
        ) as mock_get_bls_alarm_channel, patch.object(
            config_parser, "parse_binary_logic_state"
        ) as mock_parse_binary_logic_state:

            mock_binary_logic_state = MagicMock(id=123)
            mock_parse_binary_logic_state.return_value = mock_binary_logic_state
            mock_channel = MagicMock()
            mock_get_bls_alarm_channel.return_value = mock_channel

            res = config_parser.parse_config('{"BinaryLogicStates": [{}]}', "{}", "{}")
            mock_get_bls_alarm_channel.assert_called_once()
            self.assertEqual(len(res.bls_alarm_mappings), 1)
            self.assertEqual(res.bls_alarm_mappings[123].alarm_channel, mock_channel)
            self.assertEqual(res.bls_alarm_mappings[123].bls, mock_binary_logic_state)

    def test_parse_config_exception(self):
        config_parser = ConfigParser()
        with patch.object(config_parser, "parse_circuit") as mock_parse_circuit:
            mock_parse_circuit.side_effect = Exception("Test Exception")
            with self.assertRaises(Exception):
                config_parser.parse_config('{"Modes": [{}]}', "{}", "{}")

    def test_parse_engine_configuration(self):
        config_parser = ConfigParser()
        engine_configuration = EngineConfiguration()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.get_device_instance_value"
        ) as mock_get_device_instance_value, patch.object(
            config_parser, "parse_engine"
        ) as mock_parse_engine:
            mock_get_device_instance_value.return_value = 0
            mock_engine = MagicMock()
            mock_parse_engine.return_value = mock_engine
            res = config_parser.parse_engine_configuration(
                '{"Engines": [{}]}', engine_configuration
            )
            mock_parse_engine.assert_called_once()
            self.assertEqual(res.devices[0], mock_engine)

    def test_parse_engine_configuration_no_instance(self):
        config_parser = ConfigParser()
        engine_configuration = EngineConfiguration()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.get_device_instance_value"
        ) as mock_get_device_instance_value, patch.object(
            config_parser, "parse_engine"
        ) as mock_parse_engine:
            mock_get_device_instance_value.return_value = None
            mock_engine = MagicMock()
            mock_parse_engine.return_value = mock_engine
            res = config_parser.parse_engine_configuration(
                '{"Engines": [{}]}', engine_configuration
            )
            mock_parse_engine.assert_not_called()
            self.assertEqual(len(res.devices), 0)

    def test_parse_engine_configuration_exception(self):
        config_parser = ConfigParser()
        engine_configuration = EngineConfiguration()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_parser.config_parser.get_device_instance_value"
        ) as mock_get_device_instance_value:
            mock_get_device_instance_value.side_effect = Exception("Test Exception")
            with self.assertRaises(Exception):
                config_parser.parse_engine_configuration(
                    '{"Engines": [{}]}', engine_configuration
                )
