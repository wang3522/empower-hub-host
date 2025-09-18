import unittest
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.inverter import (
    map_inverter_state,
    InverterBase,
    AcMeterInverter,
)
from N2KClient.n2kclient.models.common_enums import ChannelType, InverterStatus, Unit


class TestInverter(unittest.TestCase):

    def test_map_inverter_state(self):
        self.assertEqual(map_inverter_state("Inverting"), "inverting")
        self.assertEqual(map_inverter_state("AcPassthru"), "acPassthrough")
        self.assertEqual(map_inverter_state("LoadSense"), "loadSense")
        self.assertEqual(map_inverter_state("Fault"), "fault")
        self.assertEqual(map_inverter_state("Disabled"), "disabled")
        self.assertEqual(map_inverter_state("Charging"), "charging")
        self.assertEqual(map_inverter_state("EnergySaving"), "energySaving")
        self.assertEqual(map_inverter_state("EnergySaving2"), "energySaving")
        self.assertEqual(map_inverter_state("Supporting"), "supporting")
        self.assertEqual(map_inverter_state("Supporting2"), "supporting")
        self.assertEqual(map_inverter_state("Error"), "error")
        self.assertEqual(map_inverter_state("DataNotAvailable"), "unknown")

    def test_map_inverter_state_value_error(self):
        self.assertEqual(map_inverter_state("notReal"), "unknown")

    def test_calc_connection_status(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.inverter.StateUtil.any_connected",
            return_value=True,
        ):
            inverter_base = InverterBase(
                id="TEST",
                name="Test Inverter",
                ac_line1=MagicMock(),
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                categories=["test"],
                status_ac_line=1,
                inverter_component_status=MagicMock(),
                n2k_devices=MagicMock(),
            )

            res = inverter_base._calc_connection_status()
            self.assertEqual(res, ConnectionStatus.CONNECTED)

    def test_calc_connection_status_disconnected(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.inverter.StateUtil.any_connected",
            return_value=False,
        ):
            inverter_base = InverterBase(
                id="TEST",
                name="Test Inverter",
                ac_line1=MagicMock(),
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                categories=["test"],
                status_ac_line=1,
                inverter_component_status=MagicMock(),
                n2k_devices=MagicMock(),
            )

            res = inverter_base._calc_connection_status()
            self.assertEqual(res, ConnectionStatus.DISCONNECTED)

    def test_inverter_base_init(self):
        with patch.object(
            InverterBase, "define_inverter_ac_lines"
        ) as mock_define_lines, patch.object(
            InverterBase, "define_component_status_channel"
        ) as mock_define_status:
            ac_line1 = MagicMock()
            ac_line1.instance.instance = 1
            inverter_base = InverterBase(
                id="TEST",
                name="Test Inverter",
                ac_line1=ac_line1,
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                categories=["test"],
                status_ac_line=1,
                inverter_component_status=MagicMock(),
                n2k_devices=MagicMock(),
            )
            self.assertEqual(inverter_base.id, "inverter.TEST")
            self.assertEqual(inverter_base.name, "Test Inverter")
            self.assertEqual(inverter_base.categories, ["test"])
            self.assertEqual("AC.1", inverter_base.ac_id)

            mock_define_lines.assert_called_once()
            mock_define_status.assert_called_once()

    def test_inverter_base_define_inverter_ac_lines(self):
        with patch.object(
            InverterBase, "define_component_status_channel"
        ) as mock_define_status, patch.object(
            InverterBase, "define_inverter_ac_line_channels"
        ) as mock_define_inverter_ac_line_channels:
            ac_line1 = MagicMock()
            ac_line1.instance.instance = 1
            ac_line2 = MagicMock()
            ac_line2.instance.instance = 2
            ac_line3 = MagicMock()
            ac_line3.instance.instance = 3

            mock_n2k_devices = MagicMock()
            mock_inverter_component_status = MagicMock()

            inverter_base = InverterBase(
                id="TEST",
                name="Test Inverter",
                ac_line1=ac_line1,
                ac_line2=ac_line2,
                ac_line3=ac_line3,
                categories=["test"],
                status_ac_line=2,
                inverter_component_status=mock_inverter_component_status,
                n2k_devices=mock_n2k_devices,
            )
            inverter_base.define_inverter_ac_lines(
                mock_n2k_devices,
                2,
                ac_line1,
                ac_line2,
                ac_line3,
                mock_inverter_component_status,
            )
            mock_define_inverter_ac_line_channels.assert_any_call(
                1, mock_n2k_devices, mock_inverter_component_status, 2
            )
            mock_define_inverter_ac_line_channels.assert_any_call(
                2, mock_n2k_devices, mock_inverter_component_status, 2
            )
            mock_define_inverter_ac_line_channels.assert_any_call(
                3, mock_n2k_devices, mock_inverter_component_status, 2
            )

    def test_define_inverter_ac_line_channels(self):
        line_number = 1
        ac_line1 = MagicMock()
        ac_line1.instance.instance = 1
        ac_line2 = MagicMock()
        ac_line2.instance.instance = 2
        ac_line3 = MagicMock()
        ac_line3.instance.instance = 3

        mock_n2k_devices = MagicMock()
        mock_inverter_component_status = MagicMock()
        inverter_base = InverterBase(
            id="TEST",
            name="Test Inverter",
            ac_line1=ac_line1,
            ac_line2=ac_line2,
            ac_line3=ac_line3,
            categories=["test"],
            status_ac_line=2,
            inverter_component_status=mock_inverter_component_status,
            n2k_devices=mock_n2k_devices,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.inverter.Channel"
        ) as mock_channel:
            inverter_base.define_inverter_ac_line_channels(
                1, mock_n2k_devices, mock_inverter_component_status, 1
            )
            mock_channel.assert_any_call(
                id="l1cs",
                name="Line 1 Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:inverter.line1.componentStatus"],
            )

            mock_channel.assert_any_call(
                id="l1v",
                name="Line 1 Voltage",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_VOLT,
                read_only=True,
                tags=["empower:inverter.line1.voltage"],
            )

            mock_channel.assert_any_call(
                id="l1c",
                name="Line 1 Current",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP,
                read_only=True,
                tags=["empower:inverter.line1.current"],
            )

            mock_channel.assert_any_call(
                id="l1f",
                name="Line 1 Frequency",
                type=ChannelType.NUMBER,
                unit=Unit.FREQUENCY_HERTZ,
                read_only=True,
                tags=["empower:inverter.line1.frequency"],
            )

            mock_channel.assert_any_call(
                id="l1p",
                name="Line 1 Power",
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_WATT,
                read_only=True,
                tags=["empower:inverter.line1.power"],
            )

            # Assert get_channel_subject calls
            expected_get_channel_subject_calls = [
                (
                    (
                        inverter_base.ac_id,
                        "ComponentStatus.1",
                    ),
                ),
                (
                    (
                        inverter_base.ac_id,
                        "Voltage.1",
                    ),
                ),
                (
                    (
                        inverter_base.ac_id,
                        "Current.1",
                    ),
                ),
                (
                    (
                        inverter_base.ac_id,
                        "Frequency.1",
                    ),
                ),
                (
                    (
                        inverter_base.ac_id,
                        "Power.1",
                    ),
                ),
            ]
            actual_get_channel_subject_calls = [
                (tuple(call.args[:2]),)
                for call in mock_n2k_devices.get_channel_subject.call_args_list
            ]
            for expected_call in expected_get_channel_subject_calls:
                self.assertIn(expected_call, actual_get_channel_subject_calls)

    def test_define_inverter_ac_line_channels_set_subscription_mocks(self):
        """
        Test that set_subscription is called with the result of _define_channel and a mock .pipe() for each channel, without testing RxPy internals.
        """
        ac_line1 = MagicMock()
        ac_line1.instance.instance = 1
        mock_n2k_devices = MagicMock()
        mock_inverter_component_status = None  # Force .pipe() path for all channels
        inverter_base = InverterBase(
            id="TEST",
            name="Test Inverter",
            ac_line1=ac_line1,
            ac_line2=None,
            ac_line3=None,
            categories=["test"],
            status_ac_line=1,
            inverter_component_status=mock_inverter_component_status,
            n2k_devices=mock_n2k_devices,
        )

        # Reset the mock to ignore calls from __init__
        mock_n2k_devices.set_subscription.reset_mock()

        with patch("N2KClient.n2kclient.models.empower_system.inverter.Channel"):
            # Patch _define_channel to return a unique mock for each call
            channel_ids = [
                f"inverter.TEST.l1cs",
                f"inverter.TEST.l1v",
                f"inverter.TEST.l1c",
                f"inverter.TEST.l1f",
                f"inverter.TEST.l1p",
            ]
            define_channel_mocks = [MagicMock(name=cid) for cid in channel_ids]
            with patch.object(
                inverter_base, "_define_channel", side_effect=define_channel_mocks
            ):
                # Patch get_channel_subject to return a mock with a .pipe method returning a unique mock
                pipe_mocks = [MagicMock(name=f"pipe_{cid}") for cid in channel_ids]
                pipe_mocks_backup = list(pipe_mocks)  # Save for assertion after pop

                def get_channel_subject_side_effect(*args, **kwargs):
                    m = MagicMock()
                    m.pipe.return_value = pipe_mocks.pop(0)
                    return m

                mock_n2k_devices.get_channel_subject.side_effect = (
                    get_channel_subject_side_effect
                )

                inverter_base.define_inverter_ac_line_channels(
                    1, mock_n2k_devices, mock_inverter_component_status, 1
                )

        # Assert set_subscription was called with the expected pairs
        actual_calls = [
            call.args for call in mock_n2k_devices.set_subscription.call_args_list
        ]
        for ch_mock, pipe_mock in zip(define_channel_mocks, pipe_mocks_backup):
            self.assertIn((ch_mock, pipe_mock), actual_calls)

    def test_define_inverter_ac_line_channels_else_branch(self):
        """
        Test that when inverter_component_status is not None but status_ac_line != line_number,
        the else branch is taken and set_subscription is called with a .pipe() result.
        """
        ac_line1 = MagicMock()
        ac_line1.instance.instance = 1
        mock_n2k_devices = MagicMock()
        mock_inverter_component_status = MagicMock()
        inverter_base = InverterBase(
            id="TEST",
            name="Test Inverter",
            ac_line1=ac_line1,
            ac_line2=None,
            ac_line3=None,
            categories=["test"],
            status_ac_line=2,  # Not equal to line_number below
            inverter_component_status=mock_inverter_component_status,
            n2k_devices=mock_n2k_devices,
        )

        with patch("N2KClient.n2kclient.models.empower_system.inverter.Channel"):
            # Patch _define_channel to return a mock
            channel_mock = MagicMock(name="channel_mock")
            with patch.object(
                inverter_base, "_define_channel", return_value=channel_mock
            ):
                # Patch get_channel_subject to return a mock with a .pipe method returning a unique mock
                pipe_mock = MagicMock(name="pipe_mock")
                subj_mock = MagicMock()
                subj_mock.pipe.return_value = pipe_mock
                mock_n2k_devices.get_channel_subject.return_value = subj_mock

                inverter_base.define_inverter_ac_line_channels(
                    1, mock_n2k_devices, mock_inverter_component_status, 2
                )

        # Assert set_subscription was called with the .pipe() result, not inverter_component_status
        actual_calls = [
            call.args for call in mock_n2k_devices.set_subscription.call_args_list
        ]
        found = any(
            channel_mock == call[0] and pipe_mock == call[1] for call in actual_calls
        )
        self.assertTrue(
            found,
            "set_subscription should be called with the .pipe() result when status_ac_line != line_number",
        )

    def test_define_component_status_channel_none_branch(self):
        """
        Test that define_component_status_channel wires up set_subscription with the .pipe() result when inverter_component_status and status_ac_line are None.
        """
        ac_line1 = MagicMock()
        ac_line1.instance.instance = 1
        mock_n2k_devices = MagicMock()
        inverter_base = InverterBase(
            id="TEST",
            name="Test Inverter",
            ac_line1=ac_line1,
            ac_line2=None,
            ac_line3=None,
            categories=["test"],
            status_ac_line=None,
            inverter_component_status=None,
            n2k_devices=mock_n2k_devices,
        )

        # Reset the mock to ignore calls from __init__
        mock_n2k_devices.set_subscription.reset_mock()

        with patch("N2KClient.n2kclient.models.empower_system.inverter.Channel"):
            # Patch _define_channel to return a mock
            channel_mock = MagicMock(name="channel_mock")
            with patch.object(
                inverter_base, "_define_channel", return_value=channel_mock
            ):
                # Patch .pipe() on the connection_status_subject to return a unique mock
                pipe_mock = MagicMock(name="pipe_mock")
                inverter_base.connection_status_subject.pipe = MagicMock(
                    return_value=pipe_mock
                )

                inverter_base.define_component_status_channel(
                    status_ac_line=None,
                    n2k_devices=mock_n2k_devices,
                    inverter_component_status=None,
                )

        # Assert set_subscription was called with the .pipe() result
        actual_calls = [
            call.args for call in mock_n2k_devices.set_subscription.call_args_list
        ]
        self.assertEqual(len(actual_calls), 1)
        found = any(
            channel_mock == call[0] and pipe_mock == call[1] for call in actual_calls
        )
        self.assertTrue(
            found,
            "set_subscription should be called with the .pipe() result when both args are None",
        )

    def test_define_component_status_channel_1_branch(self):
        """
        Test that define_component_status_channel wires up set_subscription with the .pipe() result when inverter_component_status and status_ac_line are None.
        """
        ac_line1 = MagicMock()
        ac_line1.instance.instance = 1
        mock_n2k_devices = MagicMock()
        inverter_base = InverterBase(
            id="TEST",
            name="Test Inverter",
            ac_line1=ac_line1,
            ac_line2=None,
            ac_line3=None,
            categories=["test"],
            status_ac_line=None,
            inverter_component_status=None,
            n2k_devices=mock_n2k_devices,
        )

        # Reset the mock to ignore calls from __init__
        mock_n2k_devices.set_subscription.reset_mock()

        with patch("N2KClient.n2kclient.models.empower_system.inverter.Channel"):
            # Patch _define_channel to return a mock
            channel_mock = MagicMock(name="channel_mock")
            with patch.object(
                inverter_base, "_define_channel", return_value=channel_mock
            ):
                # Patch .pipe() on the connection_status_subject to return a unique mock
                pipe_mock = MagicMock(name="pipe_mock")
                inverter_base.connection_status_subject.pipe = MagicMock(
                    return_value=pipe_mock
                )

                inverter_base.define_component_status_channel(
                    status_ac_line=1,
                    n2k_devices=mock_n2k_devices,
                    inverter_component_status=None,
                )

        # Assert set_subscription was called with the .pipe() result
        actual_calls = [
            call.args for call in mock_n2k_devices.set_subscription.call_args_list
        ]
        self.assertEqual(len(actual_calls), 0)
        found = any(
            channel_mock == call[0] and pipe_mock == call[1] for call in actual_calls
        )
        self.assertFalse(
            found,
            "set_subscription should be called with the .pipe() result when both args are None",
        )

    # AC Meter Inveter
    def test_ac_meter_inverter_calc_inverter_state(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.inverter.StateUtil.any_true",
            return_value=True,
        ):
            ac_inverter = AcMeterInverter(
                ac_line1=MagicMock(),
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                n2k_devices=MagicMock(),
                categories=["test"],
                circuit=MagicMock(),
            )

            res = ac_inverter._calc_inverter_state()
            self.assertEqual(res, "inverting")

    def test_ac_meter_inverter_calc_inverter_state_disabled(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.inverter.StateUtil.any_true",
            return_value=False,
        ):
            ac_inverter = AcMeterInverter(
                ac_line1=MagicMock(),
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                n2k_devices=MagicMock(),
                categories=["test"],
                circuit=MagicMock(),
            )

            res = ac_inverter._calc_inverter_state()
            self.assertEqual(res, "disabled")

    def test_ac_meter_inverter_calc_inverter_state(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.inverter.StateUtil.any_true",
            return_value=True,
        ):
            ac_inverter = AcMeterInverter(
                ac_line1=MagicMock(),
                ac_line2=MagicMock(),
                ac_line3=MagicMock(),
                n2k_devices=MagicMock(),
                categories=["test"],
                circuit=MagicMock(),
            )

            res = ac_inverter._calc_inverter_state()
            self.assertEqual(res, "inverting")
