from ..devices import N2kDevices
from ..empower_system.connection_status import ConnectionStatus
from ..empower_system.state_ts import StateWithTS
from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit
from ..constants import Constants, JsonKeys
from .channel import Channel
from .link import Link
from ..n2k_configuration.tank import Tank
from ..common_enums import WaterTankType
from reactivex import operators as ops
import reactivex as rx
from ..filters import Volume
from ..common_enums import N2kDeviceType, TankStates
from ...models.alarm_setting import (
    AlarmSettingFactory,
    AlarmSettingLimit,
    AlarmSettingType,
)
from ..n2k_configuration.alarm_limit import AlarmLimit


class TankBase(Thing):

    def __init__(
        self,
        type: ThingType,
        tank: Tank,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
        links: list[Link] = [],
    ):

        Thing.__init__(
            self,
            type,
            tank.instance.instance,
            tank.name_utf8,
            categories=categories,
            links=links,
        )
        self.tank_device_id = f"{JsonKeys.TANK}.{tank.instance.instance}"
        if tank.tank_capacity is not None and tank.tank_capacity != 0:
            self.metadata[
                f"{Constants.empower}:{Constants.tank}.{Constants.capacity}"
            ] = tank.tank_capacity
        self.define_component_status_channel(n2k_devices)
        self.define_level_channels(n2k_devices)

        for limit in AlarmSettingLimit:
            if hasattr(tank, limit.value):
                attr: AlarmLimit = getattr(tank, limit.value)
                if attr is not None and attr.enabled and attr.id > 0:
                    limit_on = AlarmSettingFactory.get_alarm_setting(
                        AlarmSettingType.TANK, limit, attr.id, attr.on, is_on=True
                    )
                    limit_off = AlarmSettingFactory.get_alarm_setting(
                        AlarmSettingType.TANK, limit, attr.id, attr.off, is_on=False
                    )
                    self.alarm_settings.extend([limit_on, limit_off])

    def define_component_status_channel(self, n2k_devices: N2kDevices):
        ###################################
        # Component Status
        ###################################

        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[f"{Constants.empower}:{Constants.tank}.{Constants.componentStatus}"],
        )
        self._define_channel(channel)
        component_status_subject = n2k_devices.get_channel_subject(
            self.tank_device_id, TankStates.ComponentStatus.value, N2kDeviceType.TANK
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

    def define_level_channels(self, n2k_devices: N2kDevices):
        ###################################
        # Level Absolute
        ###################################
        channel = Channel(
            id="levelAbsolute",
            name="Level Absolute",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.VOLUME_LITRE,
            tags=[f"{Constants.empower}:{Constants.tank}.levelAbsolute"],
        )
        self._define_channel(channel)
        level_absolute_subject = n2k_devices.get_channel_subject(
            self.tank_device_id, TankStates.Level.value, N2kDeviceType.TANK
        )
        n2k_devices.set_subscription(
            channel.id,
            rx.merge(
                level_absolute_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    Volume.LEVEL_ABSOLUTE_FILTER,
                ),
                level_absolute_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.sample(rx.interval(Volume.SAMPLE_TIMER)),
                    ops.distinct_until_changed(),
                ),
            ),
        )
        ###################################
        # Level Percent
        ###################################
        channel = Channel(
            id="levelPercent",
            name="Level Percent",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.PERCENT,
            tags=[f"{Constants.empower}:{Constants.tank}.levelPercent"],
        )
        self._define_channel(channel)

        level_percent_subject = n2k_devices.get_channel_subject(
            self.tank_device_id, TankStates.LevelPercent.value, N2kDeviceType.TANK
        )
        n2k_devices.set_subscription(
            channel.id,
            rx.merge(
                level_percent_subject.pipe(
                    ops.filter(lambda state: state is not None), Volume.FILTER
                ),
                level_percent_subject.pipe(
                    ops.sample(Volume.SAMPLE_TIMER),
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            ),
        )


class FuelTank(TankBase):

    def __init__(self, tank: Tank, n2k_devices: N2kDevices):
        TankBase.__init__(self, ThingType.FUEL_TANK, tank, n2k_devices=n2k_devices)


class WaterTank(TankBase):

    def __init__(self, tank: Tank, links: list[Link], n2k_devices: N2kDevices):
        TankBase.__init__(
            self, ThingType.WATER_TANK, tank, n2k_devices=n2k_devices, links=links
        )


class BlackWaterTank(WaterTank):
    def __init__(self, tank: Tank, links: list[Link], n2k_devices: N2kDevices):
        WaterTank.__init__(self, tank, links, n2k_devices=n2k_devices)

        self.metadata[f"{Constants.empower}:{Constants.tank}.{Constants.type}"] = (
            WaterTankType.BLACKWATER.value
        )


class WasteWaterTank(WaterTank):
    def __init__(
        self,
        tank: Tank,
        links: list[Link],
        n2k_devices: N2kDevices,
    ):
        WaterTank.__init__(self, tank, links, n2k_devices=n2k_devices)

        self.metadata[f"{Constants.empower}:{Constants.tank}.{Constants.type}"] = (
            WaterTankType.WASTEWATER.value
        )


class FreshWaterTank(WaterTank):
    def __init__(
        self,
        tank: Tank,
        links: list[Link],
        n2k_devices: N2kDevices,
    ):
        WaterTank.__init__(self, tank, links, n2k_devices=n2k_devices)

        self.metadata[f"{Constants.empower}:{Constants.tank}.{Constants.type}"] = (
            WaterTankType.FRESHWATER.value
        )
