from .thing import Thing
from ..common_enums import ThingType
from ..n2k_configuration.device import Device
from ..constants import Constants
from .channel import Channel
from ..common_enums import ChannelType, Unit


class Hub(Thing):

    def __init__(self, device: Device):

        Thing.__init__(
            self,
            type=ThingType.HUB,
            name=device.name_utf8,
            id=device.dipswitch,
            categories=[Constants.hub],
        )

        self.metadata[f"{Constants.empower}:{Constants.platform}"] = Constants.hubplus

        channels = [
            Channel(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=[
                    f"{Constants.empower}:{Constants.hub}.{Constants.componentStatus}"
                ],
            ),
            Channel(
                id="eic",
                name="Ethernet Internet Connectivity",
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{Constants.hub}.{Constants.ethernetInternetConnectivity}"
                ],
            ),
            Channel(
                id="wic",
                name="Wifi Internet Connectivity",
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                read_only=True,
                tags=[
                    f"{Constants.empower}:{Constants.hub}.{Constants.wifiInternetConnectivity}"
                ],
            ),
            Channel(
                id="wsd",
                name="Wifi SSID",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.hub}.{Constants.wifiSsid}"],
            ),
            Channel(
                id="wt",
                name="Wifi Type",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.hub}.{Constants.wifiType}"],
            ),
            Channel(
                id="wss",
                name="WiFi Signal Strength",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                tags=[
                    f"{Constants.empower}:{Constants.hub}.{Constants.wifiSignalStrength}"
                ],
            ),
            Channel(
                id="cic",
                name="Cellular Internet Connectivity",
                read_only=True,
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                tags=[
                    f"{Constants.empower}:{Constants.hub}.{Constants.cellularInternetConnectivity}"
                ],
            ),
            Channel(
                id="css",
                name="Cellular Signal Strength (dBm)",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                tags=[
                    f"{Constants.empower}:{Constants.hub}.{Constants.cellularSignalStrength}"
                ],
            ),
            Channel(
                id="iccid",
                name="Cellulr ICCID",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.hub}.{Constants.cellularIccid}"],
            ),
            Channel(
                id="cellularEid",
                name="Cellular EID",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=[f"{Constants.empower}:{Constants.hub}.{Constants.cellularEid}"],
            ),
            Channel(
                id="ac",
                name="Active Connection",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=[
                    f"{Constants.empower}:{Constants.hub}.{Constants.activeConnection}"
                ],
            ),
        ]

        for channel in channels:
            self._define_channel(channel)
