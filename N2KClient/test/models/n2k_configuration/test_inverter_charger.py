import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.inverter_charger import (
    InverterChargerDevice,
)
from N2KClient.n2kclient.models.n2k_configuration.inverter_charger import AttrNames


class TestInverterChargerDevice(unittest.TestCase):
    def test_inverter_charger_device_to_dict_exception(self):
        obj = InverterChargerDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_inverter_charger_device_to_json_string_exception(self):
        obj = InverterChargerDevice()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        json_str = obj.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_inverter_charger_device_to_dict(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        data_id_mock = MagicMock()
        data_id_mock.to_dict.return_value = "data_id_dict"
        obj = InverterChargerDevice(
            model=1,
            type=2,
            sub_type=3,
            inverter_instance=instance_mock,
            inverter_ac_id=data_id_mock,
            inverter_circuit_id=data_id_mock,
            inverter_toggle_circuit_id=data_id_mock,
            charger_instance=instance_mock,
            charger_ac_id=data_id_mock,
            charger_circuit_id=data_id_mock,
            charger_toggle_circuit_id=data_id_mock,
            battery_bank_1_id=data_id_mock,
            battery_bank_2_id=data_id_mock,
            battery_bank_3_id=data_id_mock,
            position_column=4,
            position_row=5,
            clustered=True,
            primary=True,
            primary_phase=6,
            device_instance=7,
            dipswitch=8,
            channel_index=9,
        )
        d = obj.to_dict()
        self.assertIn(AttrNames.MODEL, d)
        self.assertEqual(d[AttrNames.MODEL], 1)
        self.assertIn(AttrNames.TYPE, d)
        self.assertEqual(d[AttrNames.TYPE], 2)
        self.assertIn(AttrNames.SUB_TYPE, d)
        self.assertEqual(d[AttrNames.SUB_TYPE], 3)
        self.assertIn(AttrNames.INVERTER_INSTANCE, d)
        self.assertEqual(d[AttrNames.INVERTER_INSTANCE], "instance_dict")
        self.assertIn(AttrNames.INVERTER_AC_ID, d)
        self.assertEqual(d[AttrNames.INVERTER_AC_ID], "data_id_dict")
        self.assertIn(AttrNames.INVERTER_CIRCUIT_ID, d)
        self.assertEqual(d[AttrNames.INVERTER_CIRCUIT_ID], "data_id_dict")
        self.assertIn(AttrNames.INVERTER_TOGGLE_CIRCUIT_ID, d)
        self.assertEqual(d[AttrNames.INVERTER_TOGGLE_CIRCUIT_ID], "data_id_dict")
        self.assertIn(AttrNames.CHARGER_INSTANCE, d)
        self.assertEqual(d[AttrNames.CHARGER_INSTANCE], "instance_dict")
        self.assertIn(AttrNames.CHARGER_AC_ID, d)
        self.assertEqual(d[AttrNames.CHARGER_AC_ID], "data_id_dict")
        self.assertIn(AttrNames.CHARGER_CIRCUIT_ID, d)
        self.assertEqual(d[AttrNames.CHARGER_CIRCUIT_ID], "data_id_dict")
        self.assertIn(AttrNames.CHARGER_TOGGLE_CIRCUIT_ID, d)
        self.assertEqual(d[AttrNames.CHARGER_TOGGLE_CIRCUIT_ID], "data_id_dict")
        self.assertIn(AttrNames.BATTERY_BANK_1_ID, d)
        self.assertEqual(d[AttrNames.BATTERY_BANK_1_ID], "data_id_dict")
        self.assertIn(AttrNames.BATTERY_BANK_2_ID, d)
        self.assertEqual(d[AttrNames.BATTERY_BANK_2_ID], "data_id_dict")
        self.assertIn(AttrNames.BATTERY_BANK_3_ID, d)
        self.assertEqual(d[AttrNames.BATTERY_BANK_3_ID], "data_id_dict")
        self.assertIn(AttrNames.POSITION_COLUMN, d)
        self.assertEqual(d[AttrNames.POSITION_COLUMN], 4)
        self.assertIn(AttrNames.POSITION_ROW, d)
        self.assertEqual(d[AttrNames.POSITION_ROW], 5)
        self.assertIn(AttrNames.CLUSTERED, d)
        self.assertTrue(d[AttrNames.CLUSTERED])
        self.assertIn(AttrNames.PRIMARY, d)
        self.assertTrue(d[AttrNames.PRIMARY])
        self.assertIn(AttrNames.PRIMARY_PHASE, d)
        self.assertEqual(d[AttrNames.PRIMARY_PHASE], 6)
        self.assertIn(AttrNames.DEVICE_INSTANCE, d)
        self.assertEqual(d[AttrNames.DEVICE_INSTANCE], 7)
        self.assertIn(AttrNames.DIPSWITCH, d)
        self.assertEqual(d[AttrNames.DIPSWITCH], 8)
        self.assertIn(AttrNames.CHANNEL_INDEX, d)
        self.assertEqual(d[AttrNames.CHANNEL_INDEX], 9)

    def test_to_json_string(self):
        instance_mock = MagicMock()
        instance_mock.to_dict.return_value = "instance_dict"
        data_id_mock = MagicMock()
        data_id_mock.to_dict.return_value = "data_id_dict"
        obj = InverterChargerDevice(
            model=1,
            type=2,
            sub_type=3,
            inverter_instance=instance_mock,
            inverter_ac_id=data_id_mock,
            inverter_circuit_id=data_id_mock,
            inverter_toggle_circuit_id=data_id_mock,
            charger_instance=instance_mock,
            charger_ac_id=data_id_mock,
            charger_circuit_id=data_id_mock,
            charger_toggle_circuit_id=data_id_mock,
            battery_bank_1_id=data_id_mock,
            battery_bank_2_id=data_id_mock,
            battery_bank_3_id=data_id_mock,
            position_column=4,
            position_row=5,
            clustered=True,
            primary=True,
            primary_phase=6,
            device_instance=7,
            dipswitch=8,
            channel_index=9,
        )
        json_str = obj.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"model": 1', json_str)
        self.assertIn('"type": 2', json_str)
        self.assertIn('"sub_type": 3', json_str)
        self.assertIn('"inverter_instance": "instance_dict"', json_str)
        self.assertIn('"inverter_ac_id": "data_id_dict"', json_str)
        self.assertIn('"inverter_circuit_id": "data_id_dict"', json_str)
        self.assertIn('"inverter_toggle_circuit_id": "data_id_dict"', json_str)
        self.assertIn('"charger_instance": "instance_dict"', json_str)
        self.assertIn('"charger_ac_id": "data_id_dict"', json_str)
        self.assertIn('"charger_circuit_id": "data_id_dict"', json_str)
        self.assertIn('"charger_toggle_circuit_id": "data_id_dict"', json_str)
        self.assertIn('"battery_bank_1_id": "data_id_dict"', json_str)
        self.assertIn('"battery_bank_2_id": "data_id_dict"', json_str)
        self.assertIn('"battery_bank_3_id": "data_id_dict"', json_str)
        self.assertIn('"position_column": 4', json_str)
        self.assertIn('"position_row": 5', json_str)
        self.assertIn('"clustered": true', json_str)
        self.assertIn('"primary": true', json_str)
        self.assertIn('"primary_phase": 6', json_str)
        self.assertIn('"device_instance": 7', json_str)
        self.assertIn('"dipswitch": 8', json_str)
        self.assertIn('"channel_index": 9', json_str)
