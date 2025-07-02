from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants, JsonKeys
from .channel import Channel
from N2KClient.models.n2k_configuration.hvac import HVACDevice
from reactivex import operators as ops
import N2KClient.util.rx as rxu
from N2KClient.models.filters import Temperature
from N2KClient.models.common_enums import N2kDeviceType


class Climate(Thing):
    def __init__(
        self,
        hvac: HVACDevice,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
    ):
        Thing.__init__(
            self,
            type=ThingType.CLIMATE,
            id=hvac.instance.instance,
            name=hvac.name_utf8,
            categories=categories,
        )
        hvac_device_id = f"{Constants.hvac}.{hvac.instance.instance}"
        ##########################
        # Component Status
        ##########################
        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.componentStatus}"],
        )
        self._define_channel(channel)
        component_status_subject = n2k_devices.get_channel_subject(
            hvac_device_id, JsonKeys.ComponentStatus, N2kDeviceType.HVAC
        )
        n2k_devices.set_subscription(
            channel.id,
            component_status_subject.pipe(
                ops.map(
                    lambda status: (
                        ConnectionStatus.CONNECTED
                        if status == "Connected"
                        else "Disconnected"
                    )
                ),
                ops.map(lambda status: StateWithTS(status).to_json()),
                ops.distinct_until_changed(lambda state: state[Constants.state]),
            ),
        )
        ############################
        # Mode
        ############################
        channel = Channel(
            id="mode",
            name="Mode",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=True,
            tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.mode}"],
        )
        self._define_channel(channel)
        mode_subject = n2k_devices.get_channel_subject(
            hvac_device_id, JsonKeys.Mode, N2kDeviceType.HVAC
        )
        n2k_devices.set_subscription(
            channel.id,
            mode_subject.pipe(
                ops.distinct_until_changed(),
            ),
        )
        ###############################
        # Set Point
        ###############################
        channel = Channel(
            id="sp",
            name="Set Point",
            read_only=False,
            type=ChannelType.NUMBER,
            unit=Unit.TEMPERATURE_CELSIUS,
            tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.setPoint}"],
        )
        self._define_channel(channel)
        set_point_subject = n2k_devices.get_channel_subject(
            hvac_device_id, JsonKeys.SetPoint, N2kDeviceType.HVAC
        )
        n2k_devices.set_subscription(
            channel.id,
            set_point_subject.pipe(
                rxu.round(2),
                ops.distinct_until_changed(),
            ),
        )
        ###############################
        # Ambient Temperature
        ###############################
        channel = Channel(
            id="at",
            name="Ambient Temperature",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.TEMPERATURE_CELSIUS,
            tags=[
                f"{Constants.empower}:{Constants.hvac}.{Constants.ambientTemperature}"
            ],
        )
        self._define_channel(channel)
        ambient_temp_subject = n2k_devices.get_channel_subject(
            hvac_device_id, JsonKeys.AmbientTemperature, N2kDeviceType.HVAC
        )
        n2k_devices.set_subscription(
            channel.id,
            ambient_temp_subject.pipe(
                rxu.round(Temperature.ROUND_VALUE),
                ops.distinct_until_changed(),
            ),
        )
        #################################
        # Fan Speed
        #################################
        channel = Channel(
            id="fs",
            name="Fan Speed",
            read_only=False,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.fanSpeed}"],
        )
        self._define_channel(channel)
        fan_speed_subject = n2k_devices.get_channel_subject(
            hvac_device_id, JsonKeys.FanSpeed, N2kDeviceType.HVAC
        )
        n2k_devices.set_subscription(
            channel.id,
            fan_speed_subject.pipe(
                rxu.round(2),
                ops.distinct_until_changed(),
            ),
        )
        #################################
        # Fan Mode
        #################################
        channel = Channel(
            id="fm",
            name="Fan Mode",
            read_only=False,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hvac}.{Constants.fanMode}"],
        )
        self._define_channel(channel)
        fan_mode_subject = n2k_devices.get_channel_subject(
            hvac_device_id, JsonKeys.FanMode, N2kDeviceType.HVAC
        )
        n2k_devices.set_subscription(
            channel.id,
            fan_mode_subject.pipe(
                ops.distinct_until_changed(),
            ),
        )
