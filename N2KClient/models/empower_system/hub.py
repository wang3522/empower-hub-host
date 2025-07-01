import reactivex as rx
from N2KClient.models.devices import N2kDevices
from N2KClient.models.empower_system.connection_status import ConnectionStatus
from N2KClient.models.empower_system.state_ts import StateWithTS
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.device import Device
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, ConnectionType, Unit
from reactivex import operators as ops


class Hub(Thing):

    def __init__(self, device: Device, n2k_devices: N2kDevices):

        Thing.__init__(
            self,
            type=ThingType.HUB,
            name=device.name_utf8,
            id=device.dipswitch,
            categories=[Constants.hub],
        )
        n2k_device_id = f"{JsonKeys.DEVICE}.{device.dipswitch}"

        self.metadata[f"{Constants.empower}:{Constants.platform}"] = Constants.hubplus

        # Component Status
        channel = Channel(
            id="cs",
            name="Component Status",
            type=ChannelType.STRING,
            unit=Unit.NONE,
            read_only=False,
            tags=[f"{Constants.empower}:{Constants.hub}.{Constants.componentStatus}"],
        )
        self._define_channel(channel)

        component_status_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.ComponentStatus
        )
        if component_status_subject is not None:
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

        # Ethernet Internet Connectivity
        channel = Channel(
            id="eic",
            name="Ethernet Internet Connectivity",
            type=ChannelType.BOOLEAN,
            unit=Unit.NONE,
            read_only=True,
            tags=[
                f"{Constants.empower}:{Constants.hub}.{Constants.ethernetInternetConnectivity}"
            ],
        )
        self._define_channel(channel)

        ethernet_internet_connectivity_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.EthernetInternetConnectivity
        )
        if ethernet_internet_connectivity_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                ethernet_internet_connectivity_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Wifi Internet Connectivity
        channel = Channel(
            id="wic",
            name="Wifi Internet Connectivity",
            type=ChannelType.BOOLEAN,
            unit=Unit.NONE,
            read_only=True,
            tags=[
                f"{Constants.empower}:{Constants.hub}.{Constants.wifiInternetConnectivity}"
            ],
        )
        self._define_channel(channel)

        wifi_internet_connectivity_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.WifiInternetConnectivity
        )
        if wifi_internet_connectivity_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_internet_connectivity_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Wifi SSID
        channel = Channel(
            id="wsd",
            name="Wifi SSID",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hub}.{Constants.wifiSsid}"],
        )
        self._define_channel(channel)

        wifi_ssid_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.WifiSsid
        )
        if wifi_ssid_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_ssid_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Wifi Type
        channel = Channel(
            id="wt",
            name="Wifi Type",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hub}.{Constants.wifiType}"],
        )
        self._define_channel(channel)

        wifi_type_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.WifiType
        )
        if wifi_type_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_type_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Wifi Signal Strength
        channel = Channel(
            id="wss",
            name="WiFi Signal Strength",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.NONE,
            tags=[
                f"{Constants.empower}:{Constants.hub}.{Constants.wifiSignalStrength}"
            ],
        )
        self._define_channel(channel)

        wifi_signal_strength_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.WifiSignalStrength
        )
        if wifi_signal_strength_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_signal_strength_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Cellular Internet Connectivity
        channel = Channel(
            id="cic",
            name="Cellular Internet Connectivity",
            read_only=True,
            type=ChannelType.BOOLEAN,
            unit=Unit.NONE,
            tags=[
                f"{Constants.empower}:{Constants.hub}.{Constants.cellularInternetConnectivity}"
            ],
        )
        self._define_channel(channel)

        cellular_internet_connectivity_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.CellularInternetConnectivity
        )
        if cellular_internet_connectivity_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_internet_connectivity_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Cellular Signal Strength
        channel = Channel(
            id="css",
            name="Cellular Signal Strength (dBm)",
            read_only=True,
            type=ChannelType.NUMBER,
            unit=Unit.NONE,
            tags=[
                f"{Constants.empower}:{Constants.hub}.{Constants.cellularSignalStrength}"
            ],
        )
        self._define_channel(channel)

        cellular_signal_strength_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.CellularSignalStrengthDbm
        )
        if cellular_signal_strength_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_signal_strength_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Cellular ICCID
        channel = Channel(
            id="iccid",
            name="Cellulr ICCID",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hub}.{Constants.cellularIccid}"],
        )
        self._define_channel(channel)

        cellular_iccid_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.CellularSimIccid
        )
        if cellular_iccid_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_iccid_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Cellular EID
        channel = Channel(
            id="cellularEid",
            name="Cellular EID",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hub}.{Constants.cellularEid}"],
        )
        self._define_channel(channel)

        cellular_eid_subject = n2k_devices.get_channel_subject(
            n2k_device_id, JsonKeys.CellularSimEid
        )
        if cellular_eid_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_eid_subject.pipe(
                    ops.distinct_until_changed(),
                ),
            )

        # Active Connection
        channel = Channel(
            id="ac",
            name="Active Connection",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hub}.{Constants.activeConnection}"],
        )
        self._define_channel(channel)

        if (
            ethernet_internet_connectivity_subject is not None
            and wifi_internet_connectivity_subject is not None
            and cellular_internet_connectivity_subject is not None
        ):
            n2k_devices.set_subscription(
                channel.id,
                rx.combine_latest(
                    ethernet_internet_connectivity_subject.pipe(
                        ops.distinct_until_changed()
                    ),
                    wifi_internet_connectivity_subject.pipe(
                        ops.distinct_until_changed()
                    ),
                    cellular_internet_connectivity_subject.pipe(
                        ops.distinct_until_changed
                    ),
                ).pipe(
                    ops.map(
                        # status is [EthernetInternetConnectivity, WiFiInternetConnectivity, CellularInternetConnectivity]
                        lambda status: (
                            ConnectionType.ETHERNET.value
                            if status[0]
                            else (
                                ConnectionType.WIFI.value
                                if status[1]
                                else (
                                    ConnectionType.CELLULAR.value
                                    if status[2]
                                    else ConnectionType.NONE.value
                                )
                            )
                        )
                    ),
                    ops.filter(lambda status: status is not None),
                    ops.distinct_until_changed(),
                ),
            )
