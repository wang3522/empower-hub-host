import unittest
from unittest.mock import MagicMock, call, patch

from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.shore_power import (
    ShorePower,
)
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    Unit,
)


class TestShorePower(unittest.TestCase):
    def test_shorepower_init(self):
        ac_line1 = MagicMock()
        ac_line1.instance = MagicMock(instance=1)
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        mock_circuit = MagicMock()
        mock_component_status = MagicMock()
        mock_bls = MagicMock()

        with patch.object(
            ShorePower, "define_shorepower_enabled_channel"
        ) as define_shorepower_enabled_channel, patch.object(
            ShorePower, "define_shorepower_connected_channel"
        ) as define_shorepower_connected_channel:
            shore_power = ShorePower(
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                n2k_devices=n2k_devices,
                categories=["test"],
                circuit=mock_circuit,
                ic_associated_line=1,
                component_status=mock_component_status,
                bls=mock_bls,
            )

            define_shorepower_enabled_channel.assert_called_once()
            define_shorepower_connected_channel.assert_called_once()
            self.assertEqual(shore_power.ac_id, "AC.1")
            self.assertEqual(shore_power.circuit, mock_circuit)

    def test_define_shorepower_connected_channel(self):
        ac_line1 = MagicMock()
        ac_line1.instance = MagicMock(instance=1)
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        mock_circuit = MagicMock()
        mock_component_status = MagicMock()
        mock_bls = MagicMock()
        mock_bls.address = 123

        shore_power = ShorePower(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            n2k_devices=n2k_devices,
            categories=["test"],
            circuit=mock_circuit,
            ic_associated_line=1,
            component_status=mock_component_status,
            bls=mock_bls,
        )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()
        with patch.object(
            ShorePower, "define_shorepower_connected_pipe_inverter_charger"
        ) as define_shorepower_connected_pipe_inverter_charger, patch.object(
            ShorePower, "define_shorepower_connected_pipe_non_inverter_charger"
        ) as define_shorepower_connected_pipe_non_inverter_charger, patch(
            "N2KClient.n2kclient.models.empower_system.shore_power.Channel"
        ) as mock_channel:
            shore_power.define_shorepower_connected_channel(
                ac_line1,
                ac_line2,
                ac_line3,
                n2k_devices,
                1,
                mock_component_status,
                mock_bls,
            )
            mock_channel.assert_called_with(
                id="connected",
                name="Connected",
                read_only=True,
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                tags=["empower:shorepower.connected"],
            )

            define_shorepower_connected_pipe_inverter_charger.assert_called_once()
            n2k_devices.get_channel_subject.assert_any_call(
                "BinaryLogicState.123", "States", N2kDeviceType.BINARY_LOGIC_STATE
            )
            self.assertEqual(n2k_devices.set_subscription.call_count, 1)

    def test_define_shorepower_connected_channel_non_inverter(self):
        ac_line1 = MagicMock()
        ac_line1.instance = MagicMock(instance=1)
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        mock_circuit = MagicMock()
        mock_component_status = MagicMock()
        mock_bls = MagicMock()
        mock_bls.address = 123

        shore_power = ShorePower(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            n2k_devices=n2k_devices,
            categories=["test"],
            circuit=mock_circuit,
            ic_associated_line=1,
            component_status=None,
            bls=mock_bls,
        )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()
        with patch.object(
            ShorePower, "define_shorepower_connected_pipe_inverter_charger"
        ) as define_shorepower_connected_pipe_inverter_charger, patch.object(
            ShorePower, "define_shorepower_connected_pipe_non_inverter_charger"
        ) as define_shorepower_connected_pipe_non_inverter_charger:
            shore_power.define_shorepower_connected_channel(
                ac_line1,
                ac_line2,
                ac_line3,
                n2k_devices,
                None,
                None,
                mock_bls,
            )

            define_shorepower_connected_pipe_non_inverter_charger.assert_called_once()
            n2k_devices.get_channel_subject.assert_any_call(
                "BinaryLogicState.123", "States", N2kDeviceType.BINARY_LOGIC_STATE
            )
            self.assertEqual(n2k_devices.set_subscription.call_count, 1)

    def test_define_shorepower_pipe_inverter(self):
        ac_line1 = MagicMock()
        ac_line1.instance = MagicMock(instance=1)
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        mock_circuit = MagicMock()
        mock_component_status = MagicMock()
        mock_bls = MagicMock()
        mock_bls.address = 123

        shore_power = ShorePower(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            n2k_devices=n2k_devices,
            categories=["test"],
            circuit=mock_circuit,
            ic_associated_line=1,
            component_status=mock_component_status,
            bls=mock_bls,
        )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()

        shore_power.define_shorepower_connected_pipe_inverter_charger(
            n2k_devices, ac_line1, ac_line2, ac_line3
        )

        n2k_devices.get_channel_subject.assert_any_call(
            shore_power.ac_id, "ComponentStatus.1", N2kDeviceType.AC
        )
        n2k_devices.get_channel_subject.assert_any_call(
            shore_power.ac_id, "ComponentStatus.2", N2kDeviceType.AC
        )
        n2k_devices.get_channel_subject.assert_any_call(
            shore_power.ac_id, "ComponentStatus.3", N2kDeviceType.AC
        )

    def test_define_shorepower_pipe_noninverter(self):
        ac_line1 = MagicMock()
        ac_line1.instance = MagicMock(instance=1)
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        mock_circuit = MagicMock()
        mock_component_status = MagicMock()
        mock_bls = MagicMock()
        mock_bls.address = 123

        shore_power = ShorePower(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            n2k_devices=n2k_devices,
            categories=["test"],
            circuit=mock_circuit,
            ic_associated_line=1,
            component_status=mock_component_status,
            bls=mock_bls,
        )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()

        shore_power.define_shorepower_connected_pipe_non_inverter_charger(
            n2k_devices, ac_line1, ac_line2, ac_line3
        )

        n2k_devices.get_channel_subject.assert_any_call(
            shore_power.ac_id, "Voltage.1", N2kDeviceType.AC
        )
        n2k_devices.get_channel_subject.assert_any_call(
            shore_power.ac_id, "Voltage.2", N2kDeviceType.AC
        )
        n2k_devices.get_channel_subject.assert_any_call(
            shore_power.ac_id, "Voltage.3", N2kDeviceType.AC
        )

    def test_define_shorepower_enabled(self):
        ac_line1 = MagicMock()
        ac_line1.instance = MagicMock(instance=1)
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        mock_circuit = MagicMock()
        mock_component_status = MagicMock()
        mock_bls = MagicMock()
        mock_bls.address = 123

        shore_power = ShorePower(
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            n2k_devices=n2k_devices,
            categories=["test"],
            circuit=mock_circuit,
            ic_associated_line=1,
            component_status=mock_component_status,
            bls=mock_bls,
        )
        n2k_devices.set_subscription.reset_mock()
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.shore_power.Channel"
        ) as mock_channel, patch.object(
            ShorePower, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            shore_power.define_shorepower_enabled_channel(mock_circuit, n2k_devices)
            mock_channel.assert_called_with(
                id="enabled",
                name="Enabled",
                read_only=False,
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                tags=["empower:shorepower.enabled"],
            )
            mock_define_channel.assert_called_once()
