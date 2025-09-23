import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.circuit import Circuit, CircuitLoad


class TestCircuit(unittest.TestCase):

    def test_circuit_to_dict(self):
        from N2KClient.n2kclient.models.constants import AttrNames

        # Setup MagicMocks/dummy values for all Circuit attributes
        id_mock = MagicMock()
        id_mock.to_dict.return_value = 123
        single_throw_id_mock = MagicMock()
        single_throw_id_mock.to_dict.return_value = 456
        sequential_name_mock = MagicMock()
        sequential_name_mock.to_dict.return_value = "seq_name"
        voltage_source_mock = MagicMock()
        voltage_source_mock.to_dict.return_value = "voltage_source"
        category_mock = MagicMock()
        category_mock.to_dict.return_value = "category"
        circuit_load_mock = MagicMock()
        circuit_load_mock.to_dict.return_value = {
            AttrNames.ID: 1,
            AttrNames.ENABLED: True,
        }
        circuit_type_mock = MagicMock()
        circuit_type_mock.value = "circuit_type_value"
        switch_type_mock = MagicMock()
        switch_type_mock.value = "switch_type_value"

        circuit = Circuit(
            id=id_mock,
            single_throw_id=single_throw_id_mock,
            sequential_names_utf8=[sequential_name_mock],
            has_complement=True,
            display_categories=2,
            circuit_type=circuit_type_mock,
            switch_type=switch_type_mock,
            min_level=0,
            max_level=100,
            dimstep=5,
            step=1,
            dimmable=True,
            load_smooth_start=10,
            sequential_states=3,
            control_id=1,
            circuit_loads=[circuit_load_mock],
            categories=[category_mock],
            name_utf8="Test Circuit",
            non_visible_circuit=False,
            voltage_source=voltage_source_mock,
            dc_circuit=True,
            ac_circuit=False,
            primary_circuit_id=99,
            remote_visibility=1,
            switch_string="switch_str",
            systems_on_and=True,
        )

        circuit_dict = circuit.to_dict()
        print("circuit_dict:", circuit_dict)
        # Assert the expected keys and values for all Circuit attributes
        self.assertIn(AttrNames.SINGLE_THROW_ID, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.SINGLE_THROW_ID], 456)
        self.assertIn(AttrNames.SEQUENTIAL_NAMES_UTF8, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.SEQUENTIAL_NAMES_UTF8], ["seq_name"])
        self.assertIn(AttrNames.HAS_COMPLEMENT, circuit_dict)
        self.assertTrue(circuit_dict[AttrNames.HAS_COMPLEMENT])
        self.assertIn(AttrNames.DISPLAY_CATEGORIES, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.DISPLAY_CATEGORIES], 2)
        self.assertIn(AttrNames.CIRCUIT_TYPE, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.CIRCUIT_TYPE], "circuit_type_value")
        self.assertIn(AttrNames.SWITCH_TYPE, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.SWITCH_TYPE], "switch_type_value")
        self.assertIn(AttrNames.MIN_LEVEL, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.MIN_LEVEL], 0)
        self.assertIn(AttrNames.MAX_LEVEL, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.MAX_LEVEL], 100)
        self.assertIn(AttrNames.NONVISIBLE_CIRCUIT, circuit_dict)
        self.assertFalse(circuit_dict[AttrNames.NONVISIBLE_CIRCUIT])
        self.assertIn(AttrNames.DIMSTEP, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.DIMSTEP], 5)
        self.assertIn(AttrNames.STEP, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.STEP], 1)
        self.assertIn(AttrNames.DIMMABLE, circuit_dict)
        self.assertTrue(circuit_dict[AttrNames.DIMMABLE])
        self.assertIn(AttrNames.LOAD_SMOOTH_START, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.LOAD_SMOOTH_START], 10)
        self.assertIn(AttrNames.SEQUENTIAL_STATES, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.SEQUENTIAL_STATES], 3)
        self.assertIn(AttrNames.CONTROL_ID, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.CONTROL_ID], 1)
        self.assertIn(AttrNames.ID, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.ID], 123)
        self.assertIn(AttrNames.NAMEUTF8, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.NAMEUTF8], "Test Circuit")
        self.assertIn(AttrNames.VOLTAGE_SOURCE, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.VOLTAGE_SOURCE], "voltage_source")
        self.assertIn(AttrNames.CIRCUIT_LOADS, circuit_dict)
        self.assertEqual(len(circuit_dict[AttrNames.CIRCUIT_LOADS]), 1)
        self.assertEqual(circuit_dict[AttrNames.CIRCUIT_LOADS][0][AttrNames.ID], 1)
        self.assertTrue(circuit_dict[AttrNames.CIRCUIT_LOADS][0][AttrNames.ENABLED])
        self.assertIn(AttrNames.CATEGORIES, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.CATEGORIES], ["category"])
        self.assertIn(AttrNames.DC_CIRCUIT, circuit_dict)
        self.assertTrue(circuit_dict[AttrNames.DC_CIRCUIT])
        self.assertIn(AttrNames.AC_CIRCUIT, circuit_dict)
        self.assertFalse(circuit_dict[AttrNames.AC_CIRCUIT])
        self.assertIn(AttrNames.PRIMARY_CIRCUIT_ID, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.PRIMARY_CIRCUIT_ID], 99)
        self.assertIn(AttrNames.REMOTE_VISIBILITY, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.REMOTE_VISIBILITY], 1)
        self.assertIn(AttrNames.SWITCH_STRING, circuit_dict)
        self.assertEqual(circuit_dict[AttrNames.SWITCH_STRING], "switch_str")
        self.assertIn(AttrNames.SYSTEMS_ON_AND, circuit_dict)
        self.assertTrue(circuit_dict[AttrNames.SYSTEMS_ON_AND])

    def test_to_json_string(self):
        from N2KClient.n2kclient.models.constants import AttrNames

        circuit = Circuit(
            id=MagicMock(to_dict=MagicMock(return_value=123)),
            single_throw_id=MagicMock(to_dict=MagicMock(return_value=456)),
            sequential_names_utf8=[
                MagicMock(to_dict=MagicMock(return_value="seq_name"))
            ],
            has_complement=True,
            display_categories=2,
            circuit_type=MagicMock(value="circuit_type_value"),
            switch_type=MagicMock(value="switch_type_value"),
            min_level=0,
            max_level=100,
            dimstep=5,
            step=1,
            dimmable=True,
            load_smooth_start=10,
            sequential_states=3,
            control_id=1,
            circuit_loads=[
                MagicMock(
                    to_dict=MagicMock(
                        return_value={AttrNames.ID: 1, AttrNames.ENABLED: True}
                    )
                )
            ],
            categories=[MagicMock(to_dict=MagicMock(return_value="category"))],
            name_utf8="Test Circuit",
            non_visible_circuit=False,
            voltage_source=MagicMock(to_dict=MagicMock(return_value="voltage_source")),
            dc_circuit=True,
            ac_circuit=False,
            primary_circuit_id=99,
            remote_visibility=1,
            switch_string="switch_str",
            systems_on_and=True,
        )

    def test_to_json_string(self):
        from N2KClient.n2kclient.models.constants import AttrNames

        circuit = Circuit(
            id=MagicMock(to_dict=MagicMock(return_value=123)),
            single_throw_id=MagicMock(to_dict=MagicMock(return_value=456)),
            sequential_names_utf8=[
                MagicMock(to_dict=MagicMock(return_value="seq_name"))
            ],
            has_complement=True,
            display_categories=2,
            circuit_type=MagicMock(value="circuit_type_value"),
            switch_type=MagicMock(value="switch_type_value"),
            min_level=0,
            max_level=100,
            dimstep=5,
            step=1,
            dimmable=True,
            load_smooth_start=10,
            sequential_states=3,
            control_id=1,
            circuit_loads=[
                MagicMock(
                    to_dict=MagicMock(
                        return_value={AttrNames.ID: 1, AttrNames.ENABLED: True}
                    )
                )
            ],
            categories=[MagicMock(to_dict=MagicMock(return_value="category"))],
            name_utf8="Test Circuit",
            non_visible_circuit=False,
            voltage_source=MagicMock(to_dict=MagicMock(return_value="voltage_source")),
            dc_circuit=True,
            ac_circuit=False,
            primary_circuit_id=99,
            remote_visibility=1,
            switch_string="switch_str",
            systems_on_and=True,
        )

        json_str = circuit.to_json_string()
        print("json_str:", json_str)
        self.assertIn('"single_throw_id": 456', json_str)
        self.assertIn('"sequential_names_utf8": ["seq_name"]', json_str)
        self.assertIn('"has_complement": true', json_str)
        self.assertIn('"display_categories": 2', json_str)
        self.assertIn('"circuit_type": "circuit_type_value"', json_str)
        self.assertIn('"switch_type": "switch_type_value"', json_str)
        self.assertIn('"min_level": 0', json_str)
        self.assertIn('"max_level": 100', json_str)
        self.assertIn('"non_visible_circuit": false', json_str)
        self.assertIn('"dimstep": 5', json_str)
        self.assertIn('"step": 1', json_str)
        self.assertIn('"dimmable": true', json_str)
        self.assertIn('"load_smooth_start": 10', json_str)
        self.assertIn('"sequential_states": 3', json_str)
        self.assertIn('"control_id": 1', json_str)
        self.assertIn('"id": 123', json_str)
        self.assertIn('"name_utf8": "Test Circuit"', json_str)
        self.assertIn('"voltage_source": "voltage_source"', json_str)
        self.assertIn('"circuit_loads": [{"id": 1, "enabled": true}]', json_str)
        self.assertIn('"categories": ["category"]', json_str)
        self.assertIn('"dc_circuit": true', json_str)
        self.assertIn('"ac_circuit": false', json_str)
        self.assertIn('"primary_circuit_id": 99', json_str)
        self.assertIn('"remote_visibility": 1', json_str)
        self.assertIn('"switch_string": "switch_str"', json_str)
        self.assertIn('"systems_on_and": true', json_str)

    def test_to_json_string_exception(self):
        circuit = Circuit()
        # Force to_dict to raise an exception
        circuit.to_dict = MagicMock(side_effect=Exception("Test Exception"))
        json_str = circuit.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_to_dict_exception(self):
        circuit = Circuit()
        # Force an attribute access to raise an exception
        circuit.single_throw_id = MagicMock(side_effect=Exception("Test Exception"))
        circuit.to_dict()  # Should handle the exception and return {}
        self.assertEqual(circuit.to_dict(), {})  # Expecting empty dict on exception

    def test_circuit_load_to_dict(self):
        from N2KClient.n2kclient.models.constants import AttrNames
        from N2KClient.n2kclient.models.n2k_configuration.circuit import ControlType

        circuit_load = CircuitLoad(
            channel_address=42,
            fuse_level=15.5,
            running_current=2.3,
            system_on_current=1.1,
            force_acknowledge_on=True,
            level=7,
            control_type=ControlType.SetOutput,
            is_switched_module=True,
        )
        load_dict = circuit_load.to_dict()
        self.assertIn(AttrNames.CHANNEL_ADDRESS, load_dict)
        self.assertEqual(load_dict[AttrNames.CHANNEL_ADDRESS], 42)
        self.assertIn(AttrNames.FUSE_LEVEL, load_dict)
        self.assertEqual(load_dict[AttrNames.FUSE_LEVEL], 15.5)
        self.assertIn(AttrNames.RUNNING_CURRENT, load_dict)
        self.assertEqual(load_dict[AttrNames.RUNNING_CURRENT], 2.3)
        self.assertIn(AttrNames.SYSTEM_ON_CURRENT, load_dict)
        self.assertEqual(load_dict[AttrNames.SYSTEM_ON_CURRENT], 1.1)
        self.assertIn(AttrNames.FORCE_ACKNOWLEDGE_ON, load_dict)
        self.assertTrue(load_dict[AttrNames.FORCE_ACKNOWLEDGE_ON])
        self.assertIn(AttrNames.LEVEL, load_dict)
        self.assertEqual(load_dict[AttrNames.LEVEL], 7)
        self.assertIn(AttrNames.CONTROL_TYPE, load_dict)
        self.assertEqual(load_dict[AttrNames.CONTROL_TYPE], ControlType.SetOutput.value)
        self.assertIn(AttrNames.IS_SWITCHED_MODULE, load_dict)
        self.assertTrue(load_dict[AttrNames.IS_SWITCHED_MODULE])

    def test_circuit_load_to_json_string(self):
        from N2KClient.n2kclient.models.constants import AttrNames
        from N2KClient.n2kclient.models.n2k_configuration.circuit import ControlType

        circuit_load = CircuitLoad(
            channel_address=42,
            fuse_level=15.5,
            running_current=2.3,
            system_on_current=1.1,
            force_acknowledge_on=True,
            level=7,
            control_type=ControlType.SetOutput,
            is_switched_module=True,
        )
        json_str = circuit_load.to_json_string()
        self.assertIn('"channel_address": 42', json_str)
        self.assertIn('"fuse_level": 15.5', json_str)
        self.assertIn('"running_current": 2.3', json_str)
        self.assertIn('"system_on_current": 1.1', json_str)
        self.assertIn('"force_acknowledge_on": true', json_str)
        self.assertIn('"level": 7', json_str)
        self.assertIn(f'"control_type": {ControlType.SetOutput.value}', json_str)
        self.assertIn('"is_switched_module": true', json_str)

    def test_circuit_load_to_json_string_exception(self):
        circuit_load = CircuitLoad()
        # Force to_dict to raise an exception
        circuit_load.to_dict = MagicMock(side_effect=Exception("Test Exception"))
        json_str = circuit_load.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_circuit_load_to_dict_exception(self):
        circuit_load = CircuitLoad()
        # Force an attribute access to raise an exception
        circuit_load.channel_address = MagicMock(
            side_effect=Exception("Test Exception")
        )
        circuit_load.to_dict()  # Should handle the exception and return {}
