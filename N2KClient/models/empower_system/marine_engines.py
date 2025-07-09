from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit, EngineState, MarineEngineStatus
from ..constants import Constants, JsonKeys
from .channel import Channel
from N2KClient.models.n2k_configuration.engine import EngineDevice, EngineType
from reactivex import operators as ops
from N2KClient.models.filters import Engine, Temperature, Pressure
import N2KClient.util.rx as rxu
import reactivex as rx
from N2KClient.models.common_enums import N2kDeviceType, MarineEngineStates


def _map_engine_type(type: EngineType) -> str:
    return {
        EngineType.NMEA2000: Constants.nmea2000,
        EngineType.SmartCraft: Constants.smartcraft,
    }[type] or Constants.unknown


class MarineEngine(Thing):
    def __init__(
        self, engine: EngineDevice, n2k_devices: N2kDevices, categories: list[str] = []
    ):
        Thing.__init__(
            self,
            ThingType.MARINE_ENGINE,
            engine.instance.instance,
            engine.name_utf8,
            categories=categories,
        )
        self.engine_device_id = f"{JsonKeys.ENGINE}.{engine.instance.instance}"
        if engine.engine_type is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.engineType}"
            ] = _map_engine_type(engine.engine_type)

        self.define_engine_channels(n2k_devices, engine)

    def define_engine_channels(self, n2k_devices: N2kDevices, engine: EngineDevice):
        self.define_component_status_channel(n2k_devices)
        self.define_speed_channel(n2k_devices)
        self.define_engine_hours_channel(n2k_devices, engine)
        self.define_coolant_temperature_channel(n2k_devices, engine)
        self.define_pressure_channels(n2k_devices, engine)
        self.define_status_channel(n2k_devices)
        self.define_serial_number_channel(n2k_devices, engine)

    def define_component_status_channel(self, n2k_devices: N2kDevices):
        #############################
        # Component Status
        #############################
        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.componentStatus}"
            ],
        )
        self._define_channel(channel)
        component_status_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.ComponentStatus.value,
            N2kDeviceType.ENGINE,
        )
        n2k_devices.set_subscription(
            channel.id,
            component_status_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(
                    lambda status: (
                        ConnectionStatus.CONNECTED
                        if status == "Connected"
                        else ConnectionStatus.DISCONNECTED
                    )
                ),
                ops.map(lambda status: StateWithTS(status).to_json()),
                ops.distinct_until_changed(lambda state: state[Constants.state]),
            ),
        )

    def define_speed_channel(self, n2k_devices: N2kDevices):
        ##############################
        # Speed
        ##############################
        channel = Channel(
            id="speed",
            name="Speed",
            type=ChannelType.NUMBER,
            unit=Unit.ROTATIONAL_SPEED_REVOLUTIONS_PER_MINUTE,
            read_only=True,
            tags=[f"{Constants.empower}:{Constants.marineEngine}.{Constants.speed}"],
        )
        self._define_channel(channel)
        speed_subject = n2k_devices.get_channel_subject(
            self.engine_device_id, MarineEngineStates.Speed.value, N2kDeviceType.ENGINE
        )

        n2k_devices.set_subscription(
            channel.id,
            speed_subject.pipe(
                ops.filter(lambda state: state is not None),
                Engine.SPEED_SAMPLE_TIMER,
                Engine.SPEED_FILTER,
                ops.map(lambda state: StateWithTS(state).to_json()),
            ),
        )

    def define_engine_hours_channel(
        self, n2k_devices: N2kDevices, engine: EngineDevice
    ):
        ##############################
        # Engine Hours
        ##############################
        channel = Channel(
            id="engineHours",
            name="EngineHours",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.TIME_HOUR,
            tags=[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.engineHours}"
            ],
        )
        self._define_channel(channel)

        engine_hours_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.EngineHours.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            channel.id,
            engine_hours_subject.pipe(
                ops.filter(lambda state: state is not None),
                Engine.ENGINE_HOURS_FILTER,
                ops.map(lambda state: state / 60),
            ),
        )

    def define_coolant_temperature_channel(
        self, n2k_devices: N2kDevices, engine: EngineDevice
    ):
        ###############################
        # Coolant Temperature
        ###############################
        channel = Channel(
            id="coolantTemperature",
            name="CoolantTemperature",
            type=ChannelType.NUMBER,
            unit=Unit.TEMPERATURE_CELSIUS,
            read_only=True,
            tags=[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.coolantTemperature}"
            ],
        )
        self._define_channel(channel)

        coolant_temp_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.CoolantTemperature.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            channel.id,
            coolant_temp_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round(Temperature.ROUND_VALUE),
                Temperature.FILTER,
            ),
        )

    def define_pressure_channels(self, n2k_devices: N2kDevices, engine: EngineDevice):

        ###############################
        # Coolant Pressure
        ###############################

        # Default for Smartcraft pressure gain
        pressureGain = 0.01
        if engine.engine_type == EngineType.NMEA2000:
            pressureGain = pressureGain * 0.1  # PressureGain will now equal 0.001

        channel = Channel(
            id="coolantPressure",
            name="Coolant Pressure",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.PRESSURE_KILOPASCAL,
            tags=[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.coolantPressure}"
            ],
        )
        self._define_channel(channel)

        coolant_pressure_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.CoolantPressure.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            channel.id,
            coolant_pressure_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: state * pressureGain),
                rxu.round(Pressure.ROUND_VALUE),
                Pressure.FILTER,
            ),
        )

        #################################
        # Oil Pressure
        #################################
        channel = Channel(
            id="oilPressure",
            name="Oil Pressure",
            type=ChannelType.NUMBER,
            unit=Unit.PRESSURE_KILOPASCAL,
            read_only=True,
            tags=[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.oilPressure}"
            ],
        )
        self._define_channel(channel)

        oil_pressure_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.OilPressure.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            channel.id,
            oil_pressure_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: state * pressureGain),
                Pressure.FILTER,
            ),
        )

    def define_status_channel(self, n2k_devices: N2kDevices):
        ##################################
        # Status
        ##################################
        def resolve_engine_status(state: int):
            if state in (
                EngineState.Dead.value,
                EngineState.Crank.value,
                EngineState.PowerOff.value,
                EngineState.Stall.value,
            ):
                return MarineEngineStatus.OFF.value
            elif state == EngineState.Run.value:
                return MarineEngineStatus.RUNNING.value

        channel = Channel(
            id="status",
            name="Status",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.marineEngine}.{Constants.status}"],
        )
        self._define_channel(channel)

        engine_state_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.EngineState.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            channel.id,
            engine_state_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: resolve_engine_status(state)),
                ops.distinct_until_changed(),
            ),
        )

    def define_serial_number_channel(
        self, n2k_devices: N2kDevices, engine: EngineDevice
    ):
        ##################################
        # Serial Number
        ##################################
        channel = Channel(
            id="serialNumber",
            name="Serial Number",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=True,
            tags=[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.serialNumber}"
            ],
        )
        self._define_channel(channel)

        n2k_devices.set_subscription(channel.id, rx.just(engine.serial_number))
