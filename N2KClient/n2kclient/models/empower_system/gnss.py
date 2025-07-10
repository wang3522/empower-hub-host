from ..constants import Constants, JsonKeys
from ..devices import N2kDevices
from .channel import Channel
from ..empower_system.connection_status import ConnectionStatus
from ..empower_system.state_ts import StateWithTS
from .thing import Thing
from ..common_enums import ChannelType, ThingType, Unit
from ..n2k_configuration.gnss import GNSSDevice
from ..empower_system.location_state import LocationState
from reactivex import operators as ops
import reactivex as rx
from ..filters import Location
from ..common_enums import N2kDeviceType, GNSSStates


class GNSS(Thing):
    def __init__(
        self,
        gnss: GNSSDevice,
        n2k_devices: N2kDevices,
        categories: list[str] = [],
    ):
        Thing.__init__(
            self,
            ThingType.GNSS,
            gnss.instance.instance,
            gnss.name_utf8,
            categories,
        )
        self.instance = gnss.instance.instance
        self.gnss_device_id = f"{JsonKeys.GNSS}.{self.instance}"

        self.metadata[
            f"{Constants.empower}:{Constants.location}.{Constants.external}"
        ] = gnss.is_external

        self.define_gnss_channels(n2k_devices)

    def define_gnss_channels(self, n2k_devices: N2kDevices):
        self.define_component_status(n2k_devices)
        self.define_fix_type_channel(n2k_devices)
        self.define_location_channel(n2k_devices)

    def define_component_status(self, n2k_devices: N2kDevices):
        ##########################
        # Component Status
        ##########################
        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[
                f"{Constants.empower}:{Constants.location}.{Constants.componentStatus}"
            ],
        )
        self._define_channel(channel)
        component_status_subject = n2k_devices.get_channel_subject(
            self.gnss_device_id, GNSSStates.ComponentStatus.value, N2kDeviceType.GNSS
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

    def define_fix_type_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Fix Type
        ##########################
        channel = Channel(
            id="ft",
            name="Fix Type",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.location}.fixType"],
        )
        self._define_channel(channel)
        fix_type_subject = n2k_devices.get_channel_subject(
            self.gnss_device_id, GNSSStates.FixType.value, N2kDeviceType.GNSS
        )
        n2k_devices.set_subscription(
            channel.id,
            fix_type_subject.pipe(
                ops.filter(lambda state: state is not None),
                ops.map(
                    lambda state: (
                        Constants.TWO_D_FIX
                        if state == "2D Fix"
                        else (
                            Constants.THREE_D_FIX
                            if state == "3D Fix"
                            else Constants.NONE
                        )
                    )
                ),
            ),
        )

    def define_location_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Location
        ##########################
        channel = Channel(
            id="loc",
            name="Location",
            read_only=True,
            type=ChannelType.POINT,
            unit=Unit.GEOJSON_POINT,
            tags=[f"{Constants.empower}:{Constants.location}.position"],
        )
        self._define_channel(channel)
        lattitude_subject = n2k_devices.get_channel_subject(
            self.gnss_device_id, GNSSStates.LatitudeDeg.value, N2kDeviceType.GNSS
        )

        longitude_subject = n2k_devices.get_channel_subject(
            self.gnss_device_id, GNSSStates.LongitudeDeg.value, N2kDeviceType.GNSS
        )

        sog_subject = n2k_devices.get_channel_subject(
            self.gnss_device_id, GNSSStates.Sog.value, N2kDeviceType.GNSS
        )

        n2k_devices.set_subscription(
            channel.id,
            rx.combine_latest(
                lattitude_subject,
                longitude_subject,
                sog_subject,
            ).pipe(
                ops.sample(Location.LOCATION_GNSS_UPDATE_SAMPLE),
                ops.filter(lambda state: all(x is not None for x in state)),
                ops.map(
                    lambda state: LocationState(
                        round(state[0], 5),
                        round(state[1], 5),
                        round(state[2], 2),
                    ).to_json()
                ),
                ops.distinct_until_changed(
                    lambda state: (
                        state[Constants.lat],
                        state[Constants.long],
                        state[Constants.sp],
                    )
                ),
            ),
        )
