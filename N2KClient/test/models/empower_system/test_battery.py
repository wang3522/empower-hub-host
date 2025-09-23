import unittest
from unittest.mock import MagicMock, call, patch

from reactivex import Subject
from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.battery import (
    Battery,
)
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    SwitchType,
    Unit,
    ThingType,
)

from N2KClient.n2kclient.models.alarm_setting import (
    AlarmSettingLimit,
    AlarmSettingFactory,
)


class TestBattery(unittest.TestCase):

    def test_battery_init(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=1)

        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)
        with patch.object(
            Battery, "define_battery_metadata"
        ) as mock_define_battery_metadata, patch.object(
            Battery, "define_battery_channels"
        ) as mock_define_battery_channels, patch.object(
            AlarmSettingFactory, "get_alarm_setting", return_value=MagicMock()
        ) as mock_get_alarm_setting:
            battery = Battery(
                battery=mock_battery,
                n2k_devices=MagicMock(),
                categories=["test"],
                battery_circuit=MagicMock(),
                primary_battery=MagicMock(),
                fallback_battery=MagicMock(),
            )

            self.assertEqual(battery.instance, 1)
            expected_calls = len(AlarmSettingLimit) * 2
            self.assertEqual(mock_get_alarm_setting.call_count, expected_calls)
            # Check that alarm_settings was extended
            self.assertEqual(len(battery.alarm_settings), expected_calls)
            mock_define_battery_metadata.assert_called_once()
            mock_define_battery_channels.assert_called_once()
            self.assertEqual(battery.battery_device_id, "DC.1")

    def test_define_battery_metadata(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)
        battery = Battery(
            battery=mock_battery,
            n2k_devices=MagicMock(),
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )
        battery.define_battery_metadata(
            mock_battery, mock_fallback_battery, mock_primary_battery
        )
        self.assertEqual(
            battery.metadata["empower:battery.fallbackBattery"], "battery.4"
        )
        self.assertEqual(
            battery.metadata["empower:battery.primaryBattery"], "battery.3"
        )
        self.assertEqual(battery.metadata["empower:battery.capacity"], 123)

    def test_define_battery_channels(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        with patch.object(
            Battery, "define_circuit_enabled_channel"
        ) as define_circuit_enabled_channel, patch.object(
            Battery, "define_battery_voltage_channel"
        ) as define_battery_voltage_channel, patch.object(
            Battery, "define_battery_current_channel"
        ) as define_battery_current_channel, patch.object(
            Battery, "define_battery_status_channel"
        ) as define_battery_status_channel, patch.object(
            Battery, "define_temperature_channel"
        ) as define_temperature_channel, patch.object(
            Battery, "define_state_of_charge"
        ) as mock_state_of_charge, patch.object(
            Battery, "define_capacity_remaining_channel"
        ) as define_capacity_remaining_channel, patch.object(
            Battery, "define_time_remaining_channel"
        ) as define_time_remaining_channel, patch.object(
            Battery, "define_time_to_charge_channel"
        ) as define_time_to_charge_channel, patch.object(
            Battery, "define_component_status_channel"
        ) as define_component_status_channel:

            battery = Battery(
                battery=mock_battery,
                n2k_devices=MagicMock(),
                categories=["test"],
                battery_circuit=mock_battery_circuit,
                primary_battery=mock_primary_battery,
                fallback_battery=mock_fallback_battery,
            )
            define_circuit_enabled_channel.assert_called_once()
            define_battery_voltage_channel.assert_called_once()
            define_battery_current_channel.assert_called_once()
            define_battery_status_channel.assert_called_once()
            define_temperature_channel.assert_called_once()
            mock_state_of_charge.assert_called_once()
            define_capacity_remaining_channel.assert_called_once()
            define_time_remaining_channel.assert_called_once()
            define_time_to_charge_channel.assert_called_once()
            define_component_status_channel.assert_called_once()

    def test_define_battery_enable_channel(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=MagicMock(),
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_circuit_enabled_channel(mock_battery_circuit, mock_battery)

            mock_channel.assert_called_once_with(
                id="enabled",
                name="Enabled",
                read_only=False,
                unit=Unit.NONE,
                type=ChannelType.BOOLEAN,
                tags=["empower:battery.enabled"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_battery_voltage_channel(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_battery_voltage_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="voltage",
                name="Voltage",
                read_only=True,
                unit=Unit.ENERGY_VOLT,
                type=ChannelType.NUMBER,
                tags=["empower:battery.voltage"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_battery_current_channel(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_battery_current_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="current",
                name="Current",
                read_only=True,
                unit=Unit.ENERGY_AMP,
                type=ChannelType.NUMBER,
                tags=["empower:battery.current"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_battery_status_channel(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_battery_status_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="status",
                name="Status",
                read_only=True,
                unit=Unit.NONE,
                type=ChannelType.STRING,
                tags=["empower:battery.status"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_battery_temperature_channel(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_temperature_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="temperature",
                name="Temperature",
                read_only=True,
                unit=Unit.TEMPERATURE_CELSIUS,
                type=ChannelType.NUMBER,
                tags=["empower:battery.temperature"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_battery_state_of_charge(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_state_of_charge(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="stateOfCharge",
                name="State of Charge",
                read_only=True,
                unit=Unit.PERCENT,
                type=ChannelType.NUMBER,
                tags=["empower:battery.stateOfCharge"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_battery_capacity_remaining(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_capacity_remaining_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="capacityRemaining",
                name="Capacity Remaining",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ENERGY_AMP_HOURS,
                tags=["empower:battery.capacityRemaining"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_time_remaining_channel(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_time_remaining_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="timeRemaining",
                name="Time Remaining",
                read_only=True,
                unit=Unit.TIME_MINUTE,
                type=ChannelType.NUMBER,
                tags=["empower:battery.timeRemaining"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_time_to_charge(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_time_to_charge_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="timeToCharge",
                name="Time to Charge",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.TIME_MINUTE,
                tags=["empower:battery.timeToCharge"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)

    def test_define_component_status(self):
        mock_battery = MagicMock()
        mock_battery.instance = MagicMock(instance=2)
        mock_battery.capacity = 123

        mock_battery_circuit = MagicMock(instance=MagicMock(instance=2))
        mock_primary_battery = MagicMock(instance=MagicMock(instance=3))
        mock_fallback_battery = MagicMock(instance=MagicMock(instance=4))
        mock_n2k_devices = MagicMock()
        for limit in AlarmSettingLimit:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_battery, limit.value, mock_limit)

        battery = Battery(
            battery=mock_battery,
            n2k_devices=mock_n2k_devices,
            categories=["test"],
            battery_circuit=mock_battery_circuit,
            primary_battery=mock_primary_battery,
            fallback_battery=mock_fallback_battery,
        )

        with patch(
            "N2KClient.n2kclient.models.empower_system.battery.Channel"
        ) as mock_channel, patch.object(
            Battery, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            battery.define_component_status_channel(mock_n2k_devices)

            mock_channel.assert_called_once_with(
                id="cs",
                name="Component Status",
                read_only=False,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=["empower:battery.componentStatus"],
            )

            mock_define_channel.assert_called_once_with(mock_channel.return_value)
