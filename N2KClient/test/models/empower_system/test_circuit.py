import unittest
from unittest.mock import MagicMock, patch, ANY

from N2KClient.n2kclient.models.empower_system.circuit_thing import CircuitThing
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    Unit,
    ThingType,
)


class TestCircuit(unittest.TestCase):

    def test_circuit_init(self):
        mock_circuit = MagicMock()
        mock_circuit.control_id = 11
        mock_circuit.name_utf8 = "Test Circuit"
        n2k_devices = MagicMock()
        mock_bls = MagicMock()
        type = ThingType.GENERIC_CIRCUIT
        with patch.object(
            CircuitThing, "define_circuit_channels"
        ) as mock_define_circuit_channels:
            circuit = CircuitThing(
                type, mock_circuit, [MagicMock()], n2k_devices, bls=mock_bls
            )
            mock_define_circuit_channels.assert_called_once()

    def test_define_circuit_channels_dimmable(self):
        mock_circuit = MagicMock()
        mock_circuit.control_id = 11
        mock_circuit.name_utf8 = "Test Circuit"
        mock_circuit.dimmable = True
        n2k_devices = MagicMock()
        mock_bls = MagicMock()
        type = ThingType.GENERIC_CIRCUIT
        circuit = CircuitThing(
            type, mock_circuit, [MagicMock()], n2k_devices, bls=mock_bls
        )
        with patch.object(
            CircuitThing, "define_circuit_component_status_channel"
        ) as define_circuit_component_status_channel, patch.object(
            CircuitThing, "define_circuit_current_channel"
        ) as define_circuit_current_channel, patch.object(
            CircuitThing, "define_circuit_level_channel"
        ) as define_circuit_level_channel:
            circuit.define_circuit_channels(n2k_devices, mock_bls)

            define_circuit_component_status_channel.assert_called_once()
            define_circuit_current_channel.assert_called_once()
            define_circuit_level_channel.assert_called_once()

    def test_define_circuit_channels_nondimmable(self):
        mock_circuit = MagicMock()
        mock_circuit.control_id = 11
        mock_circuit.name_utf8 = "Test Circuit"
        mock_circuit.dimmable = False
        n2k_devices = MagicMock()
        mock_bls = MagicMock()
        type = ThingType.GENERIC_CIRCUIT
        circuit = CircuitThing(
            type, mock_circuit, [MagicMock()], n2k_devices, bls=mock_bls
        )
        with patch.object(
            CircuitThing, "define_circuit_component_status_channel"
        ) as define_circuit_component_status_channel, patch.object(
            CircuitThing, "define_circuit_current_channel"
        ) as define_circuit_current_channel, patch.object(
            CircuitThing, "define_circuit_power_channel"
        ) as define_circuit_power_channel:
            circuit.define_circuit_channels(n2k_devices, mock_bls)

            define_circuit_component_status_channel.assert_called_once()
            define_circuit_current_channel.assert_called_once()
            define_circuit_power_channel.assert_called_once()

    def test_define_circuit_component_status_channel(self):
        mock_circuit = MagicMock()
        mock_circuit.control_id = 11
        mock_circuit.name_utf8 = "Test Circuit"
        mock_circuit.dimmable = False
        n2k_devices = MagicMock()
        mock_bls = MagicMock()
        type = ThingType.GENERIC_CIRCUIT
        circuit = CircuitThing(
            type, mock_circuit, [MagicMock()], n2k_devices, bls=mock_bls
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.circuit_thing.Channel"
        ) as mock_channel, patch.object(
            CircuitThing, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            circuit.define_circuit_component_status_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[f"empower:{ThingType.GENERIC_CIRCUIT}.componentStatus"],
            )
            mock_define_channel.assert_called_once()

    def test_define_circuit_level(self):
        mock_circuit = MagicMock()
        mock_circuit.control_id = 11
        mock_circuit.name_utf8 = "Test Circuit"
        mock_circuit.dimmable = False
        n2k_devices = MagicMock()
        mock_bls = MagicMock()
        type = ThingType.GENERIC_CIRCUIT
        circuit = CircuitThing(
            type, mock_circuit, [MagicMock()], n2k_devices, bls=mock_bls
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.circuit_thing.Channel"
        ) as mock_channel, patch.object(
            CircuitThing, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            circuit.define_circuit_level_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="lvl",
                name="Level",
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                read_only=False,
                tags=[f"empower:{ThingType.GENERIC_CIRCUIT}.level"],
            )
            mock_define_channel.assert_called_once()

    def test_define_circuit_power_channel(self):
        mock_circuit = MagicMock()
        mock_circuit.control_id = 11
        mock_circuit.name_utf8 = "Test Circuit"
        mock_circuit.dimmable = False
        mock_circuit.switch_type = 1
        n2k_devices = MagicMock()
        mock_bls = MagicMock()
        type = ThingType.GENERIC_CIRCUIT
        circuit = CircuitThing(
            type, mock_circuit, [MagicMock()], n2k_devices, bls=mock_bls
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.circuit_thing.Channel"
        ) as mock_channel, patch.object(
            CircuitThing, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            circuit.define_circuit_power_channel(n2k_devices, mock_bls, mock_circuit)
            mock_channel.assert_called_once_with(
                id="p",
                name="Power",
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                read_only=False,
                tags=[f"empower:{ThingType.GENERIC_CIRCUIT}.power"],
            )
            mock_define_channel.assert_called_once()
