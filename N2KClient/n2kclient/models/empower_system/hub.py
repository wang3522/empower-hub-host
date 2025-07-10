import reactivex as rx
from ..devices import N2kDevices
from ..empower_system.connection_status import ConnectionStatus
from ..empower_system.state_ts import StateWithTS
from .thing import Thing
from ..common_enums import ThingType
from ..n2k_configuration.device import Device
from ..constants import Constants, JsonKeys
from .channel import Channel
from ..common_enums import ChannelType, ConnectionType, Unit
from reactivex import operators as ops
from ..common_enums import N2kDeviceType, HubStates


class Hub(Thing):

    def __init__(self, device: Device, n2k_devices: N2kDevices):

        Thing.__init__(
            self,
            type=ThingType.HUB,
            name=device.name_utf8,
            id=device.dipswitch,
            categories=[Constants.hub],
        )
        self.n2k_device_id = f"{JsonKeys.DEVICE}.{device.dipswitch}"

        self.metadata[f"{Constants.empower}:{Constants.platform}"] = Constants.hubplus

        self.define_hub_channels(n2k_devices)

    def define_ethernet_internet_connectivity_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Ethernet Internet Connectivity
        ##########################
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
            self.n2k_device_id,
            HubStates.EthernetInternetConnectivity.value,
            N2kDeviceType.DEVICE,
        )
        if ethernet_internet_connectivity_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                ethernet_internet_connectivity_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_wifi_internet_connectivity_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Wifi Internet Connectivity
        ##########################
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
            self.n2k_device_id,
            HubStates.WifiInternetConnectivity.value,
            N2kDeviceType.DEVICE,
        )
        if wifi_internet_connectivity_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_internet_connectivity_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_wifi_ssid_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Wifi SSID
        ##########################
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
            self.n2k_device_id, HubStates.WifiSsid.value, N2kDeviceType.DEVICE
        )
        if wifi_ssid_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_ssid_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_wifi_type_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Wifi Type
        ##########################
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
            self.n2k_device_id, HubStates.WifiType.value, N2kDeviceType.DEVICE
        )
        if wifi_type_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_type_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_wifi_signal_strength_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Wifi Signal Strength
        ##########################
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
            self.n2k_device_id, HubStates.WifiSignalStrength.value, N2kDeviceType.DEVICE
        )
        if wifi_signal_strength_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                wifi_signal_strength_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_cellular_internet_connectivity_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Cellular Internet Connectivity
        ##########################
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
            self.n2k_device_id,
            HubStates.CellularInternetConnectivity.value,
            N2kDeviceType.DEVICE,
        )
        if cellular_internet_connectivity_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_internet_connectivity_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_cellular_signal_strength_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Cellular Signal Strength
        ##########################
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
            self.n2k_device_id,
            HubStates.CellularSignalStrengthDbm.value,
            N2kDeviceType.DEVICE,
        )
        if cellular_signal_strength_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_signal_strength_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_cellular_iccid_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Cellular ICCID
        ##########################
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
            self.n2k_device_id, HubStates.CellularSimIccid.value, N2kDeviceType.DEVICE
        )
        if cellular_iccid_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_iccid_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_cellular_eid_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Cellular EID
        ##########################
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
            self.n2k_device_id, HubStates.CellularSimEid.value, N2kDeviceType.DEVICE
        )
        if cellular_eid_subject is not None:
            n2k_devices.set_subscription(
                channel.id,
                cellular_eid_subject.pipe(
                    ops.filter(lambda state: state is not None),
                    ops.distinct_until_changed(),
                ),
            )

    def define_active_connection_channel(self, n2k_devices: N2kDevices):
        ##########################
        # Active Connection
        ##########################
        channel = Channel(
            id="ac",
            name="Active Connection",
            read_only=True,
            type=ChannelType.STRING,
            unit=Unit.NONE,
            tags=[f"{Constants.empower}:{Constants.hub}.{Constants.activeConnection}"],
        )
        self._define_channel(channel)

        ethernet_internet_connectivity_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            HubStates.EthernetInternetConnectivity.value,
            N2kDeviceType.DEVICE,
        )
        wifi_internet_connectivity_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            HubStates.WifiInternetConnectivity.value,
            N2kDeviceType.DEVICE,
        )
        cellular_internet_connectivity_subject = n2k_devices.get_channel_subject(
            self.n2k_device_id,
            HubStates.CellularInternetConnectivity.value,
            N2kDeviceType.DEVICE,
        )
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
                        ops.distinct_until_changed()
                    ),
                ).pipe(
                    ops.filter(lambda status: any(status)),
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

    def define_hub_channels(self, n2k_devices: N2kDevices):
        self.define_ethernet_internet_connectivity_channel(n2k_devices)
        self.define_wifi_internet_connectivity_channel(n2k_devices)
        self.define_wifi_ssid_channel(n2k_devices)
        self.define_wifi_type_channel(n2k_devices)
        self.define_wifi_signal_strength_channel(n2k_devices)
        self.define_cellular_internet_connectivity_channel(n2k_devices)
        self.define_cellular_signal_strength_channel(n2k_devices)
        self.define_cellular_iccid_channel(n2k_devices)
        self.define_cellular_eid_channel(n2k_devices)
        self.define_active_connection_channel(n2k_devices)
