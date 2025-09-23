import unittest
from unittest.mock import MagicMock, call, patch, ANY

from N2KClient.n2kclient.models.alarm_setting import AlarmSettingLimit
from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.tank import (
    TankBase,
    FuelTank,
    WaterTank,
    BlackWaterTank,
    WasteWaterTank,
    FreshWaterTank,
)
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineType
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    Unit,
    ThingType,
)
import reactivex as rx


class TestTank(unittest.TestCase):

    def test_tank_init(self):

        # Set only supported Tank limits and restrict mock_tank to those attributes
        tank_supported_limits = [
            AlarmSettingLimit.VeryLowLimit.value,
            AlarmSettingLimit.LowLimit.value,
            AlarmSettingLimit.HighLimit.value,
            AlarmSettingLimit.VeryHighLimit.value,
        ]
        # Add 'instance', 'tank_capacity', and 'name_utf8' to the allowed attributes
        mock_tank = MagicMock(
            spec_set=tank_supported_limits + ["instance", "tank_capacity", "name_utf8"]
        )
        for limit in tank_supported_limits:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_tank, limit, mock_limit)
        mock_tank.instance = MagicMock(instance=1)
        mock_tank.tank_capacity = 100
        mock_tank.name_utf8 = "Test Tank"
        n2k_devices = MagicMock()
        type = ThingType.FUEL_TANK
        with patch.object(
            TankBase, "define_component_status_channel"
        ) as mock_component_status_channel, patch.object(
            TankBase, "define_level_channels"
        ) as mock_define_level_channels:
            tank = TankBase(
                type, mock_tank, n2k_devices, categories=["test"], links=[MagicMock()]
            )
            mock_component_status_channel.assert_called_once()
            mock_define_level_channels.assert_called_once()
            self.assertEqual(tank.metadata["empower:tank.capacity"], 100)

    def test_tank_define_component_status(self):
        # Set only supported Tank limits and restrict mock_tank to those attributes
        tank_supported_limits = [
            AlarmSettingLimit.VeryLowLimit.value,
            AlarmSettingLimit.LowLimit.value,
            AlarmSettingLimit.HighLimit.value,
            AlarmSettingLimit.VeryHighLimit.value,
        ]
        # Add 'instance', 'tank_capacity', and 'name_utf8' to the allowed attributes
        mock_tank = MagicMock(
            spec_set=tank_supported_limits + ["instance", "tank_capacity", "name_utf8"]
        )
        for limit in tank_supported_limits:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_tank, limit, mock_limit)
        mock_tank.instance = MagicMock(instance=1)
        mock_tank.tank_capacity = 100
        mock_tank.name_utf8 = "Test Tank"
        n2k_devices = MagicMock()
        type = ThingType.FUEL_TANK

        tank = TankBase(
            type, mock_tank, n2k_devices, categories=["test"], links=[MagicMock()]
        )
        n2k_devices.get_channel_subject.reset_mock()
        with patch(
            "N2KClient.n2kclient.models.empower_system.tank.Channel"
        ) as mock_channel, patch.object(
            TankBase, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            tank.define_component_status_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:tank.componentStatus"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                tank.tank_device_id, "ComponentStatus", N2kDeviceType.TANK
            )
            mock_define_channel.assert_called_once()

    def test_tank_define_level_channels(self):
        # Set only supported Tank limits and restrict mock_tank to those attributes
        tank_supported_limits = [
            AlarmSettingLimit.VeryLowLimit.value,
            AlarmSettingLimit.LowLimit.value,
            AlarmSettingLimit.HighLimit.value,
            AlarmSettingLimit.VeryHighLimit.value,
        ]
        # Add 'instance', 'tank_capacity', and 'name_utf8' to the allowed attributes
        mock_tank = MagicMock(
            spec_set=tank_supported_limits + ["instance", "tank_capacity", "name_utf8"]
        )
        for limit in tank_supported_limits:
            mock_limit = MagicMock()
            mock_limit.id = 1
            mock_limit.enabled = True
            mock_limit.on = 12.3
            mock_limit.off = 4.5
            setattr(mock_tank, limit, mock_limit)
        mock_tank.instance = MagicMock(instance=1)
        mock_tank.tank_capacity = 100
        mock_tank.name_utf8 = "Test Tank"
        n2k_devices = MagicMock()
        type = ThingType.FUEL_TANK

        tank = TankBase(
            type, mock_tank, n2k_devices, categories=["test"], links=[MagicMock()]
        )
        n2k_devices.get_channel_subject.reset_mock()
        with patch(
            "N2KClient.n2kclient.models.empower_system.tank.Channel"
        ) as mock_channel, patch.object(
            TankBase, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            tank.define_level_channels(n2k_devices)

            n2k_devices.get_channel_subject.assert_any_call(
                tank.tank_device_id, "Level", N2kDeviceType.TANK
            )

            n2k_devices.get_channel_subject.assert_any_call(
                tank.tank_device_id, "LevelPercent", N2kDeviceType.TANK
            )

            mock_channel.assert_any_call(
                id="levelPercent",
                name="Level Percent",
                type=ChannelType.NUMBER,
                unit=Unit.PERCENT,
                read_only=True,
                tags=["empower:tank.levelPercent"],
            )

            mock_channel.assert_any_call(
                id="levelAbsolute",
                name="Level Absolute",
                type=ChannelType.NUMBER,
                unit=Unit.VOLUME_LITRE,
                read_only=True,
                tags=["empower:tank.levelAbsolute"],
            )

    def test_fuel_tank(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.tank.TankBase.__init__",
            return_value=None,
        ) as mock_tankbase_init:
            tank = MagicMock()
            n2k_devices = MagicMock()
            fuel_tank = FuelTank(tank, n2k_devices)

            mock_tankbase_init.assert_called_once_with(
                ANY, ThingType.FUEL_TANK, tank, n2k_devices=n2k_devices
            )

    def test_water_tank(self):
        with patch(
            "N2KClient.n2kclient.models.empower_system.tank.TankBase.__init__",
            return_value=None,
        ) as mock_tankbase_init:
            tank = MagicMock()
            n2k_devices = MagicMock()
            links = [MagicMock()]
            water_tank = WaterTank(tank, links, n2k_devices)

            mock_tankbase_init.assert_called_once_with(
                ANY, ThingType.WATER_TANK, tank, n2k_devices=n2k_devices, links=links
            )
