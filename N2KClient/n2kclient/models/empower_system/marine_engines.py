from ..devices import N2kDevices
from .connection_status import ConnectionStatus
from .state_ts import StateWithTS
from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit, EngineState, MarineEngineStatus
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..n2k_configuration.engine import EngineDevice, EngineType
from reactivex import operators as ops
from ..filters import Engine, Temperature, Pressure
from ...util import rx as rxu
import reactivex as rx
from ..common_enums import N2kDeviceType, MarineEngineStates


def _map_engine_type(type: EngineType) -> str:
    return {
        EngineType.NMEA2000: Constants.nmea2000,
        EngineType.SmartCraft: Constants.smartcraft,
    }[type] or Constants.unknown


class MarineEngine(Thing):
    """
    Represents a marine engine device in the Empower system.

    Handles the creation and management of engine-related channels (component status, speed, engine hours, coolant temperature, pressures, status, serial number),
    and integrates with N2kDevices and RxPy for real-time updates.
    """

    def __init__(
        self, engine: EngineDevice, n2k_devices: N2kDevices, categories: list[str] = []
    ):
        """
        Initialize the MarineEngine and set up all relevant engine channels.

        Args:
            engine (EngineDevice): The engine device configuration for this marine engine.
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            categories (list[str], optional): List of categories for this marine engine.
        """
        Thing.__init__(
            self,
            ThingType.MARINE_ENGINE,
            engine.instance.instance,
            engine.name_utf8,
            categories=categories,
        )
        self.engine_device_id = f"{JsonKeys.ENGINES}.{engine.instance.instance}"
        if engine.engine_type is not None:
            self.metadata[
                f"{Constants.empower}:{Constants.marineEngine}.{Constants.engineType}"
            ] = _map_engine_type(engine.engine_type)

        self.define_engine_channels(n2k_devices, engine)

    def define_engine_channels(self, n2k_devices: N2kDevices, engine: EngineDevice):
        """
        Define all engine-related channels for the marine engine.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            engine (EngineDevice): The engine device configuration for this marine engine.
        """
        self.define_component_status_channel(n2k_devices)
        self.define_speed_channel(n2k_devices)
        self.define_engine_hours_channel(n2k_devices, engine)
        self.define_coolant_temperature_channel(n2k_devices, engine)
        self.define_pressure_channels(n2k_devices, engine)
        self.define_status_channel(n2k_devices)
        self.define_serial_number_channel(n2k_devices, engine)

    def define_component_status_channel(self, n2k_devices: N2kDevices):
        """
        Define the component status channel for the marine engine.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """
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
        component_status_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.ComponentStatus.value,
            N2kDeviceType.ENGINE,
        )
        n2k_devices.set_subscription(
            self._define_channel(channel),
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
        """
        Define the speed channel for the marine engine.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """
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
        speed_subject = n2k_devices.get_channel_subject(
            self.engine_device_id, MarineEngineStates.Speed.value, N2kDeviceType.ENGINE
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
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
        """
        Define the engine hours channel for the marine engine.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            engine (EngineDevice): The engine device configuration for this marine engine.
        """
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

        engine_hours_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.EngineHours.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            engine_hours_subject.pipe(
                ops.filter(lambda state: state is not None),
                Engine.ENGINE_HOURS_FILTER,
                ops.map(lambda state: state / 60),
            ),
        )

    def define_coolant_temperature_channel(
        self, n2k_devices: N2kDevices, engine: EngineDevice
    ):
        """
        Define the coolant temperature channel for the marine engine.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            engine (EngineDevice): The engine device configuration for this marine engine.
        """
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

        coolant_temp_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.CoolantTemperature.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            coolant_temp_subject.pipe(
                ops.filter(lambda state: state is not None),
                rxu.round_float(Temperature.ROUND_VALUE),
                Temperature.FILTER,
            ),
        )

    def define_pressure_channels(self, n2k_devices: N2kDevices, engine: EngineDevice):
        """
        Define the coolant and oil pressure channels for the marine engine, as well as their gain adjustments.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            engine (EngineDevice): The engine device configuration for this marine engine.
        """

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

        coolant_pressure_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.CoolantPressure.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            coolant_pressure_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: state * pressureGain),
                rxu.round_float(Pressure.ROUND_VALUE),
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

        oil_pressure_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.OilPressure.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            oil_pressure_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: state * pressureGain),
                Pressure.FILTER,
            ),
        )

    def define_status_channel(self, n2k_devices: N2kDevices):
        """
        Define the status channel for the marine engine.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
        """

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

        engine_state_subject = n2k_devices.get_channel_subject(
            self.engine_device_id,
            MarineEngineStates.EngineState.value,
            N2kDeviceType.ENGINE,
        )

        n2k_devices.set_subscription(
            self._define_channel(channel),
            engine_state_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(lambda state: resolve_engine_status(state)),
                ops.distinct_until_changed(),
            ),
        )

    def define_serial_number_channel(
        self, n2k_devices: N2kDevices, engine: EngineDevice
    ):
        """
        Define the serial number channel for the marine engine. This value should be static as it is provided by config.

        Args:
            n2k_devices (N2kDevices): The N2K device manager for channel subjects and subscriptions.
            engine (EngineDevice): The engine device configuration for this marine engine.
        """
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
        n2k_devices.set_subscription(
            self._define_channel(channel), rx.just(engine.serial_number)
        )
