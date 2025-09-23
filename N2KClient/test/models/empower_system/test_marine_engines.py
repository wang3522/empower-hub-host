import unittest
from unittest.mock import MagicMock, call, patch

from N2KClient.n2kclient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.n2kclient.models.empower_system.marine_engines import (
    MarineEngine,
)
from N2KClient.n2kclient.models.n2k_configuration.engine import EngineType
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    Unit,
)
import reactivex as rx


class TestMarineEngines(unittest.TestCase):

    def test_marine_engines_init(self):
        engine = MagicMock()
        engine.engine_type = MagicMock()
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )

        self.assertEqual(Engine.engine_device_id, "Engines.1")

    def test_marine_engines_init_nmea2k(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )

        self.assertEqual(Engine.engine_device_id, "Engines.1")
        self.assertEqual(Engine.metadata["empower:marineEngine.engineType"], "nmea2000")

    def test_define_engine_channels(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        with patch.object(
            MarineEngine, "define_component_status_channel"
        ) as define_component_status_channel, patch.object(
            MarineEngine, "define_speed_channel"
        ) as define_speed_channel, patch.object(
            MarineEngine, "define_engine_hours_channel"
        ) as define_engine_hours_channel, patch.object(
            MarineEngine, "define_coolant_temperature_channel"
        ) as define_engine_coolant_temp_channel, patch.object(
            MarineEngine, "define_pressure_channels"
        ) as define_pressure_channels, patch.object(
            MarineEngine, "define_status_channel"
        ) as define_status_channel, patch.object(
            MarineEngine, "define_serial_number_channel"
        ) as define_serial_number_channel:
            Engine.define_engine_channels(n2k_devices, engine)

            define_component_status_channel.assert_called_once()
            define_speed_channel.assert_called_once()
            define_engine_hours_channel.assert_called_once()
            define_engine_coolant_temp_channel.assert_called_once()
            define_pressure_channels.assert_called_once()
            define_status_channel.assert_called_once()
            define_serial_number_channel.assert_called_once()

    def test_define_component_status_channel(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.marine_engines.Channel"
        ) as mock_channel, patch.object(
            Engine, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            Engine.define_component_status_channel(n2k_devices)

            n2k_devices.get_channel_subject.assert_called_once_with(
                Engine.engine_device_id, "ComponentStatus", N2kDeviceType.ENGINE
            )
            mock_channel.assert_called_once_with(
                id="cs",
                name="Component Status",
                read_only=False,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=["empower:marineEngine.componentStatus"],
            )
            mock_define_channel.assert_called_once()

    def test_define_speed_channel(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.marine_engines.Channel"
        ) as mock_channel, patch.object(
            Engine, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            Engine.define_speed_channel(n2k_devices)

            n2k_devices.get_channel_subject.assert_called_once_with(
                Engine.engine_device_id, "Speed", N2kDeviceType.ENGINE
            )
            mock_channel.assert_called_once_with(
                id="speed",
                name="Speed",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.ROTATIONAL_SPEED_REVOLUTIONS_PER_MINUTE,
                tags=["empower:marineEngine.speed"],
            )
            mock_define_channel.assert_called_once()

    def test_define_engine_hours_channel(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.marine_engines.Channel"
        ) as mock_channel, patch.object(
            Engine, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            Engine.define_engine_hours_channel(n2k_devices)

            n2k_devices.get_channel_subject.assert_called_once_with(
                Engine.engine_device_id, "EngineHours", N2kDeviceType.ENGINE
            )
            mock_channel.assert_called_once_with(
                id="engineHours",
                name="EngineHours",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.TIME_HOUR,
                tags=["empower:marineEngine.engineHours"],
            )
            mock_define_channel.assert_called_once()

    def test_define_engine_coolant_temperature_channel(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.marine_engines.Channel"
        ) as mock_channel, patch.object(
            Engine, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            Engine.define_coolant_temperature_channel(n2k_devices)

            n2k_devices.get_channel_subject.assert_called_once_with(
                Engine.engine_device_id, "CoolantTemperature", N2kDeviceType.ENGINE
            )
            mock_channel.assert_called_once_with(
                id="coolantTemperature",
                name="CoolantTemperature",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.TEMPERATURE_CELSIUS,
                tags=["empower:marineEngine.coolantTemperature"],
            )
            mock_define_channel.assert_called_once()

    def test_define_engine_coolant_pressure_channel(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.marine_engines.Channel"
        ) as mock_channel, patch.object(
            Engine, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            Engine.define_pressure_channels(n2k_devices, engine)

            n2k_devices.get_channel_subject.assert_any_call(
                Engine.engine_device_id, "CoolantPressure", N2kDeviceType.ENGINE
            )

            n2k_devices.get_channel_subject.assert_any_call(
                Engine.engine_device_id, "OilPressure", N2kDeviceType.ENGINE
            )
            mock_channel.assert_any_call(
                id="coolantPressure",
                name="Coolant Pressure",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.PRESSURE_KILOPASCAL,
                tags=["empower:marineEngine.coolantPressure"],
            )
            mock_channel.assert_any_call(
                id="oilPressure",
                name="Oil Pressure",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.PRESSURE_KILOPASCAL,
                tags=["empower:marineEngine.oilPressure"],
            )
            self.assertEqual(mock_define_channel.call_count, 2)

    def test_define_status_channel(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        n2k_devices.get_channel_subject.reset_mock()

        with patch(
            "N2KClient.n2kclient.models.empower_system.marine_engines.Channel"
        ) as mock_channel, patch.object(
            Engine, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            Engine.define_status_channel(n2k_devices)

            n2k_devices.get_channel_subject.assert_called_once_with(
                Engine.engine_device_id, "EngineState", N2kDeviceType.ENGINE
            )
            mock_channel.assert_called_once_with(
                id="status",
                name="Status",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=["empower:marineEngine.status"],
            )
            mock_define_channel.assert_called_once()

    def test_define_serial_number_channel(self):
        engine = MagicMock()
        engine.engine_type = EngineType.NMEA2000
        engine.instance = MagicMock(instance=1)
        engine.serial_number = "123456"
        n2k_devices = MagicMock()

        Engine = MarineEngine(
            engine=engine,
            n2k_devices=n2k_devices,
            categories=["test"],
        )
        n2k_devices.get_channel_subject.reset_mock()
        n2k_devices.set_subscription.reset_mock()
        with patch(
            "N2KClient.n2kclient.models.empower_system.marine_engines.Channel"
        ) as mock_channel, patch.object(
            Engine, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            Engine.define_serial_number_channel(n2k_devices, engine)
            mock_channel.assert_called_once_with(
                id="serialNumber",
                name="Serial Number",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=["empower:marineEngine.serialNumber"],
            )
            mock_define_channel.assert_called_once()
