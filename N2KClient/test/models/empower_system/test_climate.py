import unittest
from unittest.mock import MagicMock, call, patch

from reactivex import Subject
from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.climate import (
    Climate,
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


class TestClimateInit(unittest.TestCase):
    def test_climate_init(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        with patch.object(Climate, "define_climate_channels") as mock_define_channels:
            climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
            mock_define_channels.assert_called_once_with(mock_n2k_devices)
            self.assertEqual(
                climate.hvac_device_id, f"hvac.{mock_hvac.instance.instance}"
            )

    def test_define_climate_channels(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
        with patch.object(
            climate, "define_climate_component_status_channel"
        ) as mock_comp_status, patch.object(
            climate, "def_mode_channel"
        ) as mock_mode, patch.object(
            climate, "define_set_point_channel"
        ) as mock_set_point, patch.object(
            climate, "define_ambient_temperature_channel"
        ) as mock_ambient, patch.object(
            climate, "define_fan_speed_channel"
        ) as mock_fan_speed, patch.object(
            climate, "define_fan_mode_channel"
        ) as mock_fan_mode:
            climate.define_climate_channels(mock_n2k_devices)
            mock_comp_status.assert_called_once_with(mock_n2k_devices)
            mock_mode.assert_called_once_with(mock_n2k_devices)
            mock_set_point.assert_called_once_with(mock_n2k_devices)
            mock_ambient.assert_called_once_with(mock_n2k_devices)
            mock_fan_speed.assert_called_once_with(mock_n2k_devices)
            mock_fan_mode.assert_called_once_with(mock_n2k_devices)

    def test_define_climate_component_status_channel(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.climate.Channel"
        ) as mock_channel, patch.object(
            Climate, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            mock_n2k_devices.get_channel_subject.reset_mock()
            climate.define_climate_component_status_channel(mock_n2k_devices)
            mock_channel.assert_called_once_with(
                id="cs",
                name="Component Status",
                unit=Unit.NONE,
                read_only=False,
                type=ChannelType.STRING,
                tags=["empower:hvac.componentStatus"],
            )
            mock_define_channel.assert_called_once()
            mock_n2k_devices.get_channel_subject.assert_called_once_with(
                climate.hvac_device_id, "ComponentStatus", N2kDeviceType.HVAC
            )

    def test_define_climate_mode_channel(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.climate.Channel"
        ) as mock_channel, patch.object(
            Climate, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            mock_n2k_devices.get_channel_subject.reset_mock()
            climate.def_mode_channel(mock_n2k_devices)
            mock_channel.assert_called_once_with(
                id="mode",
                name="Mode",
                unit=Unit.NONE,
                read_only=True,
                type=ChannelType.STRING,
                tags=["empower:hvac.mode"],
            )
            mock_define_channel.assert_called_once()
            mock_n2k_devices.get_channel_subject.assert_called_once_with(
                climate.hvac_device_id, "Mode", N2kDeviceType.HVAC
            )

    def test_define_climate_mode_channel(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.climate.Channel"
        ) as mock_channel, patch.object(
            Climate, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            mock_n2k_devices.get_channel_subject.reset_mock()
            climate.define_set_point_channel(mock_n2k_devices)
            mock_channel.assert_called_once_with(
                id="sp",
                name="Set Point",
                unit=Unit.TEMPERATURE_CELSIUS,
                read_only=False,
                type=ChannelType.NUMBER,
                tags=["empower:hvac.setPoint"],
            )
            mock_define_channel.assert_called_once()
            mock_n2k_devices.get_channel_subject.assert_called_once_with(
                climate.hvac_device_id, "SetPoint", N2kDeviceType.HVAC
            )

    def test_define_ambient_temperature_channel(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.climate.Channel"
        ) as mock_channel, patch.object(
            Climate, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            mock_n2k_devices.get_channel_subject.reset_mock()
            climate.define_ambient_temperature_channel(mock_n2k_devices)
            mock_channel.assert_called_once_with(
                id="at",
                name="Ambient Temperature",
                unit=Unit.TEMPERATURE_CELSIUS,
                read_only=True,
                type=ChannelType.NUMBER,
                tags=["empower:hvac.ambientTemperature"],
            )
            mock_define_channel.assert_called_once()
            mock_n2k_devices.get_channel_subject.assert_called_once_with(
                climate.hvac_device_id, "AmbientTemperature", N2kDeviceType.HVAC
            )

    def test_define_fan_speed_channel(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.climate.Channel"
        ) as mock_channel, patch.object(
            Climate, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            mock_n2k_devices.get_channel_subject.reset_mock()
            climate.define_fan_speed_channel(mock_n2k_devices)
            mock_channel.assert_called_once_with(
                id="fs",
                name="Fan Speed",
                unit=Unit.NONE,
                read_only=False,
                type=ChannelType.STRING,
                tags=["empower:hvac.fanSpeed"],
            )
            mock_define_channel.assert_called_once()
            mock_n2k_devices.get_channel_subject.assert_called_once_with(
                climate.hvac_device_id, "FanSpeed", N2kDeviceType.HVAC
            )

    def test_define_fan_mode_channel(self):
        mock_n2k_devices = MagicMock()
        mock_hvac = MagicMock()
        mock_hvac.instance = MagicMock(instance=1)
        climate = Climate(mock_hvac, mock_n2k_devices, categories=["test"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.climate.Channel"
        ) as mock_channel, patch.object(
            Climate, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            mock_n2k_devices.get_channel_subject.reset_mock()
            climate.define_fan_mode_channel(mock_n2k_devices)
            mock_channel.assert_called_once_with(
                id="fm",
                name="Fan Mode",
                unit=Unit.NONE,
                read_only=False,
                type=ChannelType.STRING,
                tags=["empower:hvac.fanMode"],
            )
            mock_define_channel.assert_called_once()
            mock_n2k_devices.get_channel_subject.assert_called_once_with(
                climate.hvac_device_id, "FanMode", N2kDeviceType.HVAC
            )
