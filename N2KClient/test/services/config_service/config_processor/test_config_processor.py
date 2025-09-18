import unittest
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.models.common_enums import ThingType
from N2KClient.n2kclient.models.n2k_configuration.ui_relationship_msg import ItemType
from N2KClient.n2kclient.services.config_service.config_processor.config_processor import (
    ConfigProcessor,
)
from N2KClient.n2kclient.models.n2k_configuration.device import DeviceType
from N2KClient.n2kclient.models.empower_system.hub import Hub
from N2KClient.n2kclient.models.n2k_configuration.dc import DCType
from N2KClient.n2kclient.models.n2k_configuration.ac import ACType
from N2KClient.n2kclient.models.n2k_configuration.tank import TankType


class TestConfigProcessor(unittest.TestCase):

    def test_config_processor_init(self):
        config_processor = ConfigProcessor()
        self.assertIsInstance(config_processor, ConfigProcessor)
        self.assertEqual(config_processor._things, [])
        self.assertEqual(config_processor._acMeter_inverter_instances, [])
        self.assertEqual(config_processor._dcMeter_charger_instances, [])
        self.assertEqual(config_processor._ic_component_status, {})
        self.assertEqual(config_processor._associated_circuit_instances, [])

    def test_process_devices(self):
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.Hub"
        ) as mock_hub:
            config_processor = ConfigProcessor()
            device_mock = MagicMock()
            device_mock.device_type = DeviceType.Europa
            config = MagicMock()
            config.device = {0: device_mock}
            n2k_devices = MagicMock()
            config_processor.process_devices(config, n2k_devices)
            assert len(config_processor._things) == 1
            mock_hub.assert_called_once_with(device_mock, n2k_devices)

    def test_process_inverter_circuit(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(inverter_circuit_id=MagicMock(enabled=True, id=1))
        inverter_visible_circuit = MagicMock()
        config = MagicMock(
            hidden_circuit={1: MagicMock(control_id=2)},
            circuit={2: inverter_visible_circuit},
        )
        res = config_processor.process_inverter_circuit(inverter_charger, config)
        self.assertEqual(inverter_visible_circuit, res)
        self.assertIn(2, config_processor._associated_circuit_instances)

    def test_process_inverter_circuit_none_in_inverter(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(inverter_circuit_id=MagicMock(enabled=False, id=1))
        inverter_visible_circuit = MagicMock()
        config = MagicMock(
            hidden_circuit={1: MagicMock(control_id=2)},
            circuit={2: inverter_visible_circuit},
        )
        res = config_processor.process_inverter_circuit(inverter_charger, config)
        self.assertIsNone(res)

    def test_process_inverter_circuit_hidden_circuit_none(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(inverter_circuit_id=MagicMock(enabled=True, id=1))
        inverter_visible_circuit = MagicMock()
        config = MagicMock(
            hidden_circuit={},
            circuit={2: inverter_visible_circuit},
        )
        res = config_processor.process_inverter_circuit(inverter_charger, config)
        self.assertIsNone(res)

    def test_process_inverter_circuit_circuit_none(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(inverter_circuit_id=MagicMock(enabled=True, id=1))
        config = MagicMock(
            hidden_circuit={1: MagicMock(control_id=2)},
            circuit={},
        )
        res = config_processor.process_inverter_circuit(inverter_charger, config)
        self.assertIsNone(res)

    def test_process_charger_circuit(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(charger_circuit_id=MagicMock(enabled=True, id=1))
        charger_visible_circuit = MagicMock()
        config = MagicMock(
            hidden_circuit={1: MagicMock(control_id=2)},
            circuit={2: charger_visible_circuit},
        )
        res = config_processor.process_charger_circuit(inverter_charger, config)
        self.assertEqual(charger_visible_circuit, res)
        self.assertIn(2, config_processor._associated_circuit_instances)

    def test_process_charger_circuit_none_in_charger(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(charger_circuit_id=MagicMock(enabled=False, id=1))
        charger_visible_circuit = MagicMock()
        config = MagicMock(
            hidden_circuit={1: MagicMock(control_id=2)},
            circuit={2: charger_visible_circuit},
        )
        res = config_processor.process_charger_circuit(inverter_charger, config)
        self.assertIsNone(res)

    def test_process_charger_circuit_hidden_circuit_none(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(charger_circuit_id=MagicMock(enabled=True, id=1))
        charger_visible_circuit = MagicMock()
        config = MagicMock(
            hidden_circuit={},
            circuit={2: charger_visible_circuit},
        )
        res = config_processor.process_charger_circuit(inverter_charger, config)
        self.assertIsNone(res)

    def test_process_charger_circuit_circuit_none(self):
        config_processor = ConfigProcessor()
        inverter_charger = MagicMock(charger_circuit_id=MagicMock(enabled=True, id=1))
        config = MagicMock(
            hidden_circuit={1: MagicMock(control_id=2)},
            circuit={},
        )
        res = config_processor.process_charger_circuit(inverter_charger, config)
        self.assertIsNone(res)

    def test_process_inverters(self):
        config_processor = ConfigProcessor()
        with patch.object(
            config_processor, "process_inverter_circuit", return_value=MagicMock()
        ) as mock_process_inverter_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CombiInverter"
        ) as mock_combi_inverter:
            mock_get_category_list.return_value = [MagicMock(name="test_category")]
            mock_process_inverter_circuit.return_value = MagicMock()
            ac_line_1 = MagicMock(id=1, instance=MagicMock(instance=1234))
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            inverter_charger = MagicMock(inverter_ac_id=MagicMock(enabled=True, id=1))
            categories = [MagicMock(name="Inverter")]
            n2k_devices = MagicMock()
            config_processor.process_inverters(
                config, inverter_charger, categories, n2k_devices, 1
            )

            # Assert
            mock_process_inverter_circuit.assert_called_once_with(
                inverter_charger, config
            )
            self.assertEqual(len(config_processor._things), 1)
            mock_get_category_list.assert_called_once_with(ItemType.AcMeter, 1, config)
            self.assertIn(1234, config_processor._acMeter_inverter_instances)
            mock_combi_inverter.assert_called_once_with(
                inverter_charger=inverter_charger,
                ac_line1=ac_line_1,
                ac_line2=None,
                ac_line3=None,
                categories=mock_get_category_list.return_value,
                instance=1,
                inverter_circuit=mock_process_inverter_circuit.return_value,
                status_ac_line=1,
                n2k_devices=n2k_devices,
            )

    def test_process_inverter_no_inverter_ac_id(self):
        config_processor = ConfigProcessor()
        with patch.object(
            config_processor, "process_inverter_circuit", return_value=MagicMock()
        ) as mock_process_inverter_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CombiInverter"
        ):
            mock_get_category_list.return_value = [MagicMock(name="test_category")]
            mock_process_inverter_circuit.return_value = MagicMock()
            ac_line_1 = MagicMock(id=1, instance=MagicMock(instance=1234))
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            inverter_charger = MagicMock(inverter_ac_id=None)
            categories = [MagicMock(name="Inverter")]
            n2k_devices = MagicMock()
            config_processor.process_inverters(
                config, inverter_charger, categories, n2k_devices, 1
            )

            # Assert
            self.assertEqual(len(config_processor._acMeter_inverter_instances), 0)
            mock_get_category_list.assert_not_called()

    def test_process_chargers(self):
        """
        Ensure creating charger properly gets all dcmeters for battery banks and visible circuit, and calls to create Charger appropriately
        """
        config_processor = ConfigProcessor()
        with patch.object(
            config_processor, "process_charger_circuit", return_value=MagicMock()
        ) as mock_process_charger_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CombiCharger"
        ) as mock_charger:
            mock_process_charger_circuit.return_value = MagicMock()
            dc_line_1 = MagicMock(id=1)
            dc_line_2 = MagicMock(id=2)
            dc_line_3 = MagicMock(id=3)
            config = MagicMock(
                dc={
                    1: dc_line_1,
                    2: dc_line_2,
                    3: dc_line_3,
                }
            )
            inverter_charger = MagicMock(
                battery_bank_1_id=MagicMock(enabled=True, id=1),
                battery_bank_2_id=MagicMock(enabled=False, id=2),
                battery_bank_3_id=MagicMock(enabled=False, id=3),
            )
            categories = [MagicMock(name="Charger")]
            n2k_devices = MagicMock()
            config_processor.process_chargers(
                config, inverter_charger, categories, n2k_devices, 1
            )

            # Assert
            mock_process_charger_circuit.assert_called_once_with(
                inverter_charger, config
            )
            self.assertEqual(len(config_processor._things), 1)
            # self.assertIn(5678, config_processor._dcMeter_charger_instances)
            mock_charger.assert_called_once_with(
                inverter_charger=inverter_charger,
                dc1=dc_line_1,
                dc2=dc_line_2,
                dc3=dc_line_3,
                categories=categories,
                charger_circuit=mock_process_charger_circuit.return_value,
                instance=1,
                n2k_devices=n2k_devices,
            )
            self.assertEqual(3, len(config_processor._dcMeter_charger_instances))

    def test_process_charger_adds_shorepower(self):
        config_processor = ConfigProcessor()
        with patch.object(
            config_processor, "process_charger_circuit", return_value=MagicMock()
        ) as mock_process_charger_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CombiCharger"
        ) as mock_charger:
            """
            Check that associated shorepower for charger is stored with component status of this charger
            """
            mock_charger.return_value = MagicMock(component_status=MagicMock())
            mock_process_charger_circuit.return_value = MagicMock()
            ac_line_value = MagicMock(id=1234, instance=MagicMock(instance=1234))
            ac_meter = MagicMock()
            dc_line_1 = MagicMock(id=1)
            ac_meter.line = {1: ac_line_value}
            config = MagicMock(dc={1: dc_line_1}, ac={1: ac_meter})
            inverter_charger = MagicMock(
                charger_ac_id=MagicMock(enabled=True, id=1234),
                battery_bank_1_id=MagicMock(enabled=True, id=1),
                battery_bank_2_id=MagicMock(enabled=False, id=2),
                battery_bank_3_id=MagicMock(enabled=False, id=3),
                shore_power_id=MagicMock(enabled=True, id=4),
            )
            mock_category = MagicMock(name="Charger")
            categories = [mock_category]
            n2k_devices = MagicMock()
            config_processor.process_chargers(
                config, inverter_charger, categories, n2k_devices, 1
            )

            # Assert
            mock_process_charger_circuit.assert_called_once_with(
                inverter_charger, config
            )
            self.assertEqual(len(config_processor._ic_component_status), 1)
            self.assertIn(1234, config_processor._ic_component_status)

    def test_process_inverter_charger(self):
        config_processor = ConfigProcessor()
        with patch.object(
            config_processor, "process_inverters"
        ) as mock_process_inverters, patch.object(
            config_processor, "process_chargers"
        ) as mock_process_chargers, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.calculate_inverter_charger_instance"
        ) as mock_calculate_instance, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list:
            inverter_charger = MagicMock(device_type=DeviceType.Europa, instance=1)
            categories = [MagicMock(name="TEST")]
            config = MagicMock(inverter_charger={1: inverter_charger})
            mock_calculate_instance.return_value = 1
            mock_get_category_list.return_value = categories
            n2k_devices = MagicMock()
            config_processor.process_inverter_chargers(
                config,
                n2k_devices,
            )

            mock_process_inverters.assert_called_once_with(
                config, inverter_charger, categories, n2k_devices, 1
            )

            mock_process_chargers.assert_called_once_with(
                config, inverter_charger, categories, n2k_devices, 1
            )

    def test_process_dc_meters_in_charger_instances(self):
        """
        Ensure we don't continue processing if instance already associated with charger
        """
        config_processor = ConfigProcessor()
        config_processor._dcMeter_charger_instances = [1]
        n2k_devices = MagicMock()
        config = MagicMock(dc={1: MagicMock(instance=MagicMock(instance=1))})
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list:
            config_processor.process_dc_meters(
                config,
                n2k_devices,
            )
            mock_get_category_list.assert_not_called()

    def test_process_dc_meters(self):
        config_processor = ConfigProcessor()
        n2k_devices = MagicMock()
        config = MagicMock(
            dc={
                1: MagicMock(
                    instance=MagicMock(instance=1), id=1234, dc_type=DCType.Battery
                )
            }
        )
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_primary_dc_meter"
        ) as mock_get_primary_dc_meter, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_fallback_dc_meter"
        ) as mock_get_fallback_dc_meter, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.Battery"
        ) as mock_battery:
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            config_processor.process_dc_meters(
                config,
                n2k_devices,
            )
            mock_get_category_list.assert_called_once_with(
                ItemType.DcMeter, 1234, config
            )

            mock_get_associated_circuit.assert_called_once_with(
                ItemType.DcMeter, 1234, config
            )
            mock_get_primary_dc_meter.assert_called_once_with(1234, config)
            mock_get_fallback_dc_meter.assert_called_once_with(1234, config)

    def test_process_dc_meters_no_circuit(self):
        config_processor = ConfigProcessor()
        n2k_devices = MagicMock()
        mock_dc = MagicMock(
            instance=MagicMock(instance=1), id=1234, dc_type=DCType.Battery
        )
        config = MagicMock(dc={1: mock_dc})
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_primary_dc_meter"
        ) as mock_get_primary_dc_meter, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_fallback_dc_meter"
        ) as mock_get_fallback_dc_meter, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.Battery"
        ) as mock_battery:
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_associated_circuit.return_value = MagicMock(control_id=0)
            config_processor.process_dc_meters(
                config,
                n2k_devices,
            )
            mock_get_category_list.assert_called_once_with(
                ItemType.DcMeter, 1234, config
            )

            mock_get_associated_circuit.assert_called_once_with(
                ItemType.DcMeter, 1234, config
            )
            mock_get_primary_dc_meter.assert_called_once_with(1234, config)
            mock_get_fallback_dc_meter.assert_called_once_with(1234, config)
            self.assertIn(0, config_processor._associated_circuit_instances)
            mock_battery.assert_called_once_with(
                battery=mock_dc,
                categories=mock_get_category_list.return_value,
                battery_circuit=mock_get_associated_circuit.return_value,
                primary_battery=mock_get_primary_dc_meter.return_value,
                fallback_battery=mock_get_fallback_dc_meter.return_value,
                n2k_devices=n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 1)

    def test_process_dc_meters_no_circuit(self):
        config_processor = ConfigProcessor()
        n2k_devices = MagicMock()
        mock_dc = MagicMock(
            instance=MagicMock(instance=1), id=1234, dc_type=DCType.Battery
        )
        config = MagicMock(dc={1: mock_dc})
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_primary_dc_meter"
        ) as mock_get_primary_dc_meter, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_fallback_dc_meter"
        ) as mock_get_fallback_dc_meter, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.Battery"
        ) as mock_battery:
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_associated_circuit.return_value = None
            config_processor.process_dc_meters(
                config,
                n2k_devices,
            )
            mock_get_category_list.assert_called_once_with(
                ItemType.DcMeter, 1234, config
            )

            mock_get_associated_circuit.assert_called_once_with(
                ItemType.DcMeter, 1234, config
            )
            mock_get_primary_dc_meter.assert_called_once_with(1234, config)
            mock_get_fallback_dc_meter.assert_called_once_with(1234, config)
            self.assertEqual(len(config_processor._associated_circuit_instances), 0)
            mock_battery.assert_called_once_with(
                battery=mock_dc,
                categories=mock_get_category_list.return_value,
                battery_circuit=mock_get_associated_circuit.return_value,
                primary_battery=mock_get_primary_dc_meter.return_value,
                fallback_battery=mock_get_fallback_dc_meter.return_value,
                n2k_devices=n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 1)

    def test_process_gnss(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.GNSS"
        ) as mock_gnss:
            gnss_device = MagicMock(instance=1)
            n2k_devices = MagicMock()
            config = MagicMock(gnss={1: gnss_device})
            config_processor.process_gnss(
                config,
                n2k_devices,
            )
            mock_gnss.assert_called_once_with(
                gnss_device,
                n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 1)

    def test_process_ac_meter_not_in_ac_instances_in_component_status_shorepower(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_ac_meter_associated_bls"
        ) as mock_get_ac_meter_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.ShorePower"
        ) as mock_shorepower:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = MagicMock(control_id=1111)
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_ac_meter_associated_bls.return_value = MagicMock()

            ac_line_1 = MagicMock(
                id=1, instance=MagicMock(instance=1234), ac_type=ACType.ShorePower
            )
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            n2k_devices = MagicMock()
            component_status = MagicMock()
            ic_associated_line = 1
            config_processor._ic_component_status = {
                1234: {component_status, ic_associated_line}
            }

            # Act
            config_processor.process_ac_meters(
                config,
                n2k_devices,
            )

            # Assert
            self.assertIn(1111, config_processor._associated_circuit_instances)
            mock_get_associated_circuit.assert_called_once_with(
                ItemType.AcMeter, 1, config
            )
            mock_get_category_list.assert_called_once_with(ItemType.AcMeter, 1, config)
            mock_get_ac_meter_associated_bls.assert_called_once()
            mock_shorepower.assert_called_once()
            self.assertEqual(len(config_processor._things), 1)

    def test_process_ac_meter_not_in_ac_instances_in_component_status_inverter(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_ac_meter_associated_bls"
        ) as mock_get_ac_meter_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.AcMeterInverter"
        ) as mock_inverter:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = MagicMock(control_id=1111)
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_ac_meter_associated_bls.return_value = MagicMock()

            ac_line_1 = MagicMock(
                id=1, instance=MagicMock(instance=1234), ac_type=ACType.Inverter
            )
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            n2k_devices = MagicMock()
            component_status = MagicMock()
            ic_associated_line = 1
            config_processor._ic_component_status = {
                1234: {component_status, ic_associated_line}
            }

            # Act
            config_processor.process_ac_meters(
                config,
                n2k_devices,
            )

            # Assert
            self.assertIn(1111, config_processor._associated_circuit_instances)
            mock_get_associated_circuit.assert_called_once_with(
                ItemType.AcMeter, 1, config
            )
            mock_get_category_list.assert_called_once_with(ItemType.AcMeter, 1, config)
            mock_get_ac_meter_associated_bls.assert_called_once()
            mock_inverter.assert_called_once()
            self.assertEqual(len(config_processor._things), 1)

    def test_process_ac_meter_not_in_ac_instances_in_component_status_charger(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_ac_meter_associated_bls"
        ) as mock_get_ac_meter_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.ACMeterCharger"
        ) as mock_charger:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = MagicMock(control_id=1111)
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_ac_meter_associated_bls.return_value = MagicMock()

            ac_line_1 = MagicMock(
                id=1, instance=MagicMock(instance=1234), ac_type=ACType.Charger
            )
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            n2k_devices = MagicMock()
            component_status = MagicMock()
            ic_associated_line = 1
            config_processor._ic_component_status = {
                1234: {component_status, ic_associated_line}
            }

            # Act
            config_processor.process_ac_meters(
                config,
                n2k_devices,
            )

            # Assert
            self.assertIn(1111, config_processor._associated_circuit_instances)
            mock_get_associated_circuit.assert_called_once_with(
                ItemType.AcMeter, 1, config
            )
            mock_get_category_list.assert_called_once_with(ItemType.AcMeter, 1, config)
            mock_get_ac_meter_associated_bls.assert_called_once()
            mock_charger.assert_called_once()
            self.assertEqual(len(config_processor._things), 1)

    def test_process_ac_meter_not_in_ac_instances_in_component_status_not_supported(
        self,
    ):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_ac_meter_associated_bls"
        ) as mock_get_ac_meter_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.ShorePower"
        ) as mock_shorepower:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = MagicMock(control_id=1111)
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_ac_meter_associated_bls.return_value = MagicMock()

            ac_line_1 = MagicMock(
                id=1, instance=MagicMock(instance=1234), ac_type=ACType.Outlet
            )
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            n2k_devices = MagicMock()
            component_status = MagicMock()
            ic_associated_line = 1
            config_processor._ic_component_status = {
                1234: {component_status, ic_associated_line}
            }

            # Act
            config_processor.process_ac_meters(
                config,
                n2k_devices,
            )

            # Assert
            self.assertIn(1111, config_processor._associated_circuit_instances)
            mock_get_associated_circuit.assert_called_once_with(
                ItemType.AcMeter, 1, config
            )
            mock_get_category_list.assert_not_called()
            mock_get_ac_meter_associated_bls.assert_not_called()
            mock_shorepower.assert_not_called()
            self.assertEqual(len(config_processor._things), 0)

    def test_process_ac_meter_circuit_none(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_ac_meter_associated_bls"
        ) as mock_get_ac_meter_associated_bls:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = None
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_ac_meter_associated_bls.return_value = MagicMock()

            ac_line_1 = MagicMock(
                id=1, instance=MagicMock(instance=1234), ac_type=ACType.ShorePower
            )
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            n2k_devices = MagicMock()
            component_status = MagicMock()
            ic_associated_line = 1
            config_processor._ic_component_status = {
                1234: {component_status, ic_associated_line}
            }

            # Act
            config_processor.process_ac_meters(
                config,
                n2k_devices,
            )

            # Assert
            self.assertEqual(0, len(config_processor._associated_circuit_instances))

    def test_process_ac_meter_circuit_in_inverter_instances(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_ac_meter_associated_bls"
        ) as mock_get_ac_meter_associated_bls:
            # Arrange Mocks
            config_processor._acMeter_inverter_instances = [1234]
            mock_get_associated_circuit.return_value = None
            mock_get_category_list.return_value = [MagicMock(name="TEST")]
            mock_get_ac_meter_associated_bls.return_value = MagicMock()

            ac_line_1 = MagicMock(
                id=1, instance=MagicMock(instance=1234), ac_type=ACType.ShorePower
            )
            config = MagicMock(ac={1: MagicMock(line={1: ac_line_1})})
            n2k_devices = MagicMock()
            component_status = MagicMock()
            ic_associated_line = 1
            config_processor._ic_component_status = {
                1234: {component_status, ic_associated_line}
            }

            # Act
            config_processor.process_ac_meters(
                config,
                n2k_devices,
            )

            # Assert
            mock_get_associated_circuit.assert_not_called()
            mock_get_category_list.assert_not_called()
            mock_get_ac_meter_associated_bls.assert_not_called()
            self.assertEqual(len(config_processor._things), 0)

    def test_process_tanks_fuel(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.FuelTank"
        ) as mock_fuel_tank, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit:
            tank = MagicMock(instance=1, tank_type=TankType.Fuel)
            config = MagicMock(tank={1: tank})
            n2k_devices = MagicMock()
            config_processor.process_tanks(
                config,
                n2k_devices,
            )
            mock_fuel_tank.assert_called_once_with(tank=tank, n2k_devices=n2k_devices)
            self.assertEqual(len(config_processor._things), 1)
            mock_get_associated_circuit.assert_not_called()

    def test_process_tanks_oil(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.FuelTank"
        ) as mock_fuel_tank, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit:
            tank = MagicMock(instance=1, tank_type=TankType.Oil)
            config = MagicMock(tank={1: tank})
            n2k_devices = MagicMock()
            config_processor.process_tanks(
                config,
                n2k_devices,
            )
            mock_fuel_tank.assert_called_once_with(tank=tank, n2k_devices=n2k_devices)
            self.assertEqual(len(config_processor._things), 1)
            mock_get_associated_circuit.assert_not_called()

    def test_process_tanks_fresh_water(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.FreshWaterTank"
        ) as mock_fresh_water_tank, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            tank = MagicMock(instance=1, id=3, tank_type=TankType.FreshWater)
            config = MagicMock(tank={1: tank})
            n2k_devices = MagicMock()
            config_processor.process_tanks(
                config,
                n2k_devices,
            )
            mock_fresh_water_tank.assert_called_once_with(
                tank=tank,
                links=[mock_create_link.return_value],
                n2k_devices=n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 1)
            mock_get_associated_circuit.assert_called_once_with(
                ItemType.FluidLevel, 3, config
            )
            mock_create_link.assert_called_once()

    def test_process_tanks_waste_water(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.WasteWaterTank"
        ) as mock_waste_water_tank, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            tank = MagicMock(instance=1, id=3, tank_type=TankType.WasteWater)
            config = MagicMock(tank={1: tank})
            n2k_devices = MagicMock()
            config_processor.process_tanks(
                config,
                n2k_devices,
            )
            mock_waste_water_tank.assert_called_once_with(
                tank=tank,
                links=[mock_create_link.return_value],
                n2k_devices=n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 1)
            mock_get_associated_circuit.assert_called_once_with(
                ItemType.FluidLevel, 3, config
            )
            mock_create_link.assert_called_once()

    def test_process_tanks_black_water(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.BlackWaterTank"
        ) as mock_black_water_tank, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            tank = MagicMock(instance=1, id=3, tank_type=TankType.BlackWater)
            config = MagicMock(tank={1: tank})
            n2k_devices = MagicMock()
            config_processor.process_tanks(
                config,
                n2k_devices,
            )
            mock_black_water_tank.assert_called_once_with(
                tank=tank,
                links=[mock_create_link.return_value],
                n2k_devices=n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 1)
            mock_get_associated_circuit.assert_called_once_with(
                ItemType.FluidLevel, 3, config
            )
            mock_create_link.assert_called_once()

    def test_process_tanks_circuit_none(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.BlackWaterTank"
        ) as mock_black_water_tank, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_circuit"
        ) as mock_get_associated_circuit, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            # Arrange Mocks
            mock_get_associated_circuit.return_value = None
            mock_create_link.return_value = MagicMock()
            tank = MagicMock(instance=1, id=3, tank_type=TankType.BlackWater)
            config = MagicMock(tank={1: tank})
            n2k_devices = MagicMock()
            config_processor.process_tanks(
                config,
                n2k_devices,
            )
            mock_get_associated_circuit.assert_called_once()
            mock_create_link.assert_not_called()

    def test_process_hvac(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.Climate"
        ) as mock_climate, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_category_list"
        ) as mock_get_category_list:
            hvac = MagicMock(id=1)
            config = MagicMock(hvac={1: hvac})
            n2k_devices = MagicMock()
            config_processor.process_hvac(
                config,
                n2k_devices,
            )
            mock_climate.assert_called_once_with(
                hvac=hvac,
                categories=mock_get_category_list.return_value,
                n2k_devices=n2k_devices,
            )
            mock_get_category_list.assert_called_once_with(
                ItemType.Temperature, 1, config
            )
            self.assertEqual(len(config_processor._things), 1)

    def test_process_circuit_lighting(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitLight"
        ) as mock_circuit_light, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            mock_is_in_category.side_effect = [True, False, False, False]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            circuit = MagicMock(id=MagicMock(), remote_visibility=1)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            mock_circuit_light.assert_called_once_with(
                circuit=circuit,
                links=[mock_create_link.return_value],
                bls=mock_get_circuit_associated_bls.return_value,
                n2k_devices=n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 1)
            mock_create_link.assert_called_once()

    def test_process_circuit_skip_visibility(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitLight"
        ) as mock_circuit_light, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            mock_is_in_category.side_effect = [True, False, False, False]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            circuit = MagicMock(id=MagicMock(), remote_visibility=111)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            mock_circuit_light.assert_not_called()
            self.assertEqual(len(config_processor._things), 0)

    def test_process_circuit_bilge(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitBilgePump"
        ) as mock_circuit_bilge, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            mock_is_in_category.side_effect = [False, True, False, False]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            circuit = MagicMock(id=MagicMock(), remote_visibility=1)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            mock_circuit_bilge.assert_called_once_with(
                circuit,
                [],
                n2k_devices,
                mock_get_circuit_associated_bls.return_value,
            )
            self.assertEqual(len(config_processor._things), 1)
            mock_create_link.assert_not_called()

    def test_process_circuit_bilge_skipped(self):
        config_processor = ConfigProcessor()
        config_processor._associated_circuit_instances = {111}
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitBilgePump"
        ) as mock_circuit_bilge, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link:
            mock_is_in_category.side_effect = [False, True, False, False]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            circuit = MagicMock(id=MagicMock(), control_id=111, remote_visibility=1)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            mock_circuit_bilge.assert_not_called()
            self.assertEqual(len(config_processor._things), 0)

    def test_process_circuit_pump(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitWaterPump"
        ) as mock_circuit_pump, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_tank"
        ) as mock_get_associated_tank:
            # Arrange Mocks
            mock_is_in_category.side_effect = [False, False, True, False]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            mock_get_associated_tank.return_value = MagicMock()

            circuit = MagicMock(id=MagicMock(), remote_visibility=1)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            mock_circuit_pump.assert_called_once_with(
                circuit,
                [mock_create_link.return_value],
                n2k_devices,
                mock_get_circuit_associated_bls.return_value,
            )
            self.assertEqual(len(config_processor._things), 1)
            mock_create_link.assert_called_once_with(
                ThingType.WATER_TANK,
                ThingType.PUMP,
                mock_get_associated_tank.return_value.instance.instance,
            )

    def test_process_power_circuit(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitPowerSwitch"
        ) as mock_circuit_power_switch, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_tank"
        ) as mock_get_associated_tank:
            # Arrange Mocks
            mock_is_in_category.side_effect = [False, False, False, True]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            mock_get_associated_tank.return_value = MagicMock()

            circuit = MagicMock(id=MagicMock(), remote_visibility=1)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            mock_circuit_power_switch.assert_called_once_with(
                circuit,
                [],
                n2k_devices,
                mock_get_circuit_associated_bls.return_value,
            )
            self.assertEqual(len(config_processor._things), 1)

    def test_process_power_circuit_skip(self):
        config_processor = ConfigProcessor()
        config_processor._associated_circuit_instances = {555}
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitPowerSwitch"
        ) as mock_circuit_power_switch, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_tank"
        ) as mock_get_associated_tank:
            # Arrange Mocks
            mock_is_in_category.side_effect = [False, False, False, True]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            mock_get_associated_tank.return_value = MagicMock()

            circuit = MagicMock(id=MagicMock(), control_id=555, remote_visibility=1)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            mock_circuit_power_switch.assert_not_called()
            self.assertEqual(len(config_processor._things), 0)

    def test_process_type_not_supported(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.CircuitPowerSwitch"
        ) as mock_circuit_power_switch, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_circuit_associated_bls"
        ) as mock_get_circuit_associated_bls, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_child_circuits"
        ) as mock_get_child_circuits, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.is_in_category"
        ) as mock_is_in_category, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.create_link"
        ) as mock_create_link, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.get_associated_tank"
        ) as mock_get_associated_tank:
            # Arrange Mocks
            mock_is_in_category.side_effect = [False, False, False, False]
            mock_get_circuit_associated_bls.return_value = MagicMock()
            mock_create_link.return_value = MagicMock()
            mock_get_child_circuits.return_value = [MagicMock()]
            mock_get_associated_tank.return_value = MagicMock()

            circuit = MagicMock(id=MagicMock(), remote_visibility=1)
            config = MagicMock(circuit={1: circuit})
            n2k_devices = MagicMock()
            config_processor.process_circuits(
                config,
                n2k_devices,
            )
            self.assertEqual(len(config_processor._things), 0)

    def test_build_empower_system(self):
        def fake_process_devices(*args, **kwargs):
            config_processor._things.append(MagicMock())

        config_processor = ConfigProcessor()
        config_processor._things = [MagicMock()]
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.EmpowerSystem"
        ) as mock_empower_system, patch.object(
            config_processor, "process_devices"
        ) as mock_process_devices, patch.object(
            config_processor, "process_inverter_chargers"
        ) as mock_inverter_chargers, patch.object(
            config_processor, "process_dc_meters"
        ) as mock_process_dc_meter, patch.object(
            config_processor, "process_gnss"
        ) as mock_process_gnss, patch.object(
            config_processor, "process_ac_meters"
        ) as mock_process_ac_meters, patch.object(
            config_processor, "process_tanks"
        ) as mock_process_tanks, patch.object(
            config_processor, "process_hvac"
        ) as mock_process_hvac, patch.object(
            config_processor, "process_circuits", side_effect=fake_process_devices
        ) as mock_process_circuits:
            config = MagicMock()
            n2k_devices = MagicMock()
            mock_empower_system_return = MagicMock()
            mock_empower_system.return_value = mock_empower_system_return
            res = config_processor.build_empower_system(
                config,
                n2k_devices,
            )
            mock_process_devices.assert_called_once()
            mock_inverter_chargers.assert_called_once()
            mock_process_dc_meter.assert_called_once()
            mock_process_gnss.assert_called_once()
            mock_process_ac_meters.assert_called_once()
            mock_process_tanks.assert_called_once()
            mock_process_hvac.assert_called_once()
            mock_process_circuits.assert_called_once()
            mock_empower_system_return.add_thing.assert_called_once()
            self.assertEqual(res, mock_empower_system.return_value)

    def test_build_empower_system_exception(self):
        def fake_process_devices(*args, **kwargs):
            config_processor._things.append(MagicMock())

        config_processor = ConfigProcessor()
        config_processor._things = [MagicMock()]
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.EmpowerSystem"
        ) as mock_empower_system, patch.object(
            config_processor, "process_devices"
        ) as mock_process_devices:
            mock_process_devices.side_effect = Exception("Test Exception")
            config = MagicMock()
            n2k_devices = MagicMock()
            mock_empower_system_return = MagicMock()
            mock_empower_system.return_value = mock_empower_system_return
            self.assertRaises(
                Exception, config_processor.build_empower_system, config, n2k_devices
            )

    def test_build_engine_list(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.MarineEngine"
        ) as mock_engine, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.EngineList"
        ) as mock_engine_list:
            mock_engine.return_value = MagicMock()
            engine = MagicMock(instance=1)
            config = MagicMock(devices={1: engine})
            n2k_devices = MagicMock()
            res = config_processor.build_engine_list(
                config,
                n2k_devices,
            )
            mock_engine.assert_any_call(engine, n2k_devices)
            mock_engine_list.assert_called_once()
            mock_engine_list.return_value.add_engine.assert_called_once()
            self.assertEqual(res, mock_engine_list.return_value)

    def test_build_engine_list_exception(self):
        config_processor = ConfigProcessor()
        with patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.MarineEngine"
        ) as mock_engine, patch(
            "N2KClient.n2kclient.services.config_service.config_processor.config_processor.EngineList"
        ) as mock_engine_list:
            mock_engine.return_value = MagicMock()
            mock_engine.side_effect = Exception("Test Exception")
            engine = MagicMock(instance=1)
            config = MagicMock(devices={1: engine})
            n2k_devices = MagicMock()
            self.assertRaises(
                Exception, config_processor.build_engine_list, config, n2k_devices
            )
