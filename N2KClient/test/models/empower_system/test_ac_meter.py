import unittest
from unittest.mock import MagicMock, call, patch

from reactivex import Subject
from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.ac_meter import (
    ACMeterThingBase,
)
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    SwitchType,
    Unit,
    ThingType,
)


class TestACMeter(unittest.TestCase):

    def test_calc_connection_status(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.ac_meter.StateUtil.any_connected",
            return_value=True,
        ):
            ac_meter = ACMeterThingBase(
                type=ThingType.SHORE_POWER,
                ac_line1=MagicMock(),
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                n2k_devices=MagicMock(),
                categories=["test"],
            )

            res = ac_meter._calc_connection_status()
            self.assertEqual(res, ConnectionStatus.CONNECTED)

    def test_calc_connection_status_disconnected(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.ac_meter.StateUtil.any_connected",
            return_value=False,
        ):
            ac_meter = ACMeterThingBase(
                type=ThingType.SHORE_POWER,
                ac_line1=MagicMock(),
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                n2k_devices=MagicMock(),
                categories=["test"],
            )

            res = ac_meter._calc_connection_status()
            self.assertEqual(res, ConnectionStatus.DISCONNECTED)

    def test_ac_meter_init(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()

        with patch.object(
            ACMeterThingBase, "define_ac_channels"
        ) as mock_define_ac_channels:
            mock_define_ac_channels.return_value = None
            ac_meter = ACMeterThingBase(
                type=ThingType.SHORE_POWER,
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                n2k_devices=n2k_devices,
                categories=["test"],
            )

            mock_define_ac_channels.assert_called_once_with(
                ac_line1, ac_line2, ac_line3, n2k_devices, None, None
            )

    def test_define_ac_channels(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()

        with patch.object(
            ACMeterThingBase, "define_ac_line_channels"
        ) as mock_define_ac_line_channels, patch(
            "N2KClient.n2kclient.models.empower_system.ac_meter.Channel"
        ) as mock_channel:
            ac_meter = ACMeterThingBase(
                type=ThingType.SHORE_POWER,
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                n2k_devices=n2k_devices,
                categories=["test"],
            )

            mock_define_ac_line_channels.assert_any_call(1, n2k_devices, None, None)
            mock_define_ac_line_channels.assert_any_call(2, n2k_devices, None, None)
            mock_define_ac_line_channels.assert_any_call(3, n2k_devices, None, None)

            mock_channel.assert_any_call(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:shorePower.componentStatus"],
            )

            n2k_devices.set_subscription.assert_called_once()

    def test_define_ac_line_channels_triggers_update_line_status(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        charger_circuit = MagicMock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.ac_meter.Channel"
        ) as mock_channel:
            test_subject = Subject()
            n2k_devices.get_channel_subject.return_value = test_subject
            ac_meter = ACMeterThingBase(
                type=ThingType.SHORE_POWER,
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                n2k_devices=n2k_devices,
                categories=["test"],
            )

            ac_meter.define_ac_line_channels(1, n2k_devices, None, None)
            test_subject.on_next("Connected")

            # Assert the closure was triggered
            self.assertEqual(ac_meter.line_status[1], ConnectionStatus.CONNECTED)

    def test_define_ac_line_channels_triggers_update_line_status_disconnected(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.ac_meter.Channel"
        ) as mock_channel:
            test_subject = Subject()
            n2k_devices.get_channel_subject.return_value = test_subject
            ac_meter = ACMeterThingBase(
                type=ThingType.SHORE_POWER,
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                n2k_devices=n2k_devices,
                categories=["test"],
            )

            ac_meter.define_ac_line_channels(1, n2k_devices, None, None)
            test_subject.on_next("Disconnected")

            # Assert the closure was triggered
            self.assertEqual(ac_meter.line_status[1], ConnectionStatus.DISCONNECTED)

    def test_define_ac_line_channels_ic_component_statu(self):
        ac_line1 = MagicMock()
        ac_line2 = MagicMock()
        ac_line3 = MagicMock()
        n2k_devices = MagicMock()
        mock_component_status = MagicMock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.ac_meter.Channel"
        ) as mock_channel, patch.object(
            ACMeterThingBase, "define_ac_channels"
        ) as mock_define_ac_channels:
            ac_meter = ACMeterThingBase(
                type=ThingType.SHORE_POWER,
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                n2k_devices=n2k_devices,
                categories=["test"],
                ic_associated_line=1,
                ic_component_status=mock_component_status,
            )

            ac_meter.define_ac_line_channels(
                1, n2k_devices, 1, ic_component_status=mock_component_status
            )

            mock_channel.assert_any_call(
                id="l1v",
                name="Line 1 Voltage",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                read_only=True,
                tags=["empower:shorePower.line1.voltage"],
            )

            mock_channel.assert_any_call(
                id="l1c",
                name="Line 1 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=True,
                tags=["empower:shorePower.line1.current"],
            )

            mock_channel.assert_any_call(
                id="l1f",
                name="Line 1 Frequency",
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                read_only=True,
                tags=["empower:shorePower.line1.frequency"],
            )

            mock_channel.assert_any_call(
                id="l1p",
                name="Line 1 Power",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                read_only=True,
                tags=["empower:shorePower.line1.power"],
            )

            n2k_devices.get_channel_subject.assert_any_call(
                ac_meter.ac_id, "Voltage.1", N2kDeviceType.AC
            )
            n2k_devices.get_channel_subject.assert_any_call(
                ac_meter.ac_id, "Current.1", N2kDeviceType.AC
            )
            n2k_devices.get_channel_subject.assert_any_call(
                ac_meter.ac_id, "Frequency.1", N2kDeviceType.AC
            )
            n2k_devices.get_channel_subject.assert_any_call(
                ac_meter.ac_id, "Power.1", N2kDeviceType.AC
            )

            for call in n2k_devices.get_channel_subject.call_args_list:
                assert call != unittest.mock.call(
                    ac_meter.ac_id, "ComponentStatus.line1", N2kDeviceType.AC
                )
