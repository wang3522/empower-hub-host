from N2KClient.models.constants import Constants, JsonKeys
from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.channel import Channel
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from .thing import Thing
from N2KClient.models.common_enums import ChannelType, ThingType, Unit
from N2KClient.models.n2k_configuration.gnss import GNSSDevice
from N2KClient.models.empower_system.location_state import LocationState
from reactivex import operators as ops
import reactivex as rx
from N2KClient.models.filters import Location


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
        gnss_device_id = f"{JsonKeys.GNSS}.{self.instance}"

        self.metadata[
            f"{Constants.empower}:{Constants.location}.{Constants.external}"
        ] = gnss.is_external

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
            gnss_device_id, JsonKeys.ComponentStatus
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
            gnss_device_id, JsonKeys.FixType
        )
        n2k_devices.set_subscription(
            channel.id,
            fix_type_subject.pipe(
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
            gnss_device_id, JsonKeys.LatitudeDeg
        )

        longitude_subject = n2k_devices.get_channel_subject(
            gnss_device_id, JsonKeys.LongitudeDeg
        )

        sog_subject = n2k_devices.get_channel_subject(gnss_device_id, JsonKeys.Sog)

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
