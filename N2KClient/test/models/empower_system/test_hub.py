import unittest
from unittest.mock import MagicMock, call, patch, ANY

from N2KClient.n2kclient.models.empower_system.hub import Hub
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    Unit,
    ThingType,
)


class TestHub(unittest.TestCase):

    def test_hub_init(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        with patch.object(Hub, "define_hub_channels") as mock_define_hub_channels:
            hub = Hub(mock_hub, n2k_devices)

            self.assertEqual(hub.n2k_device_id, "Device.123")
            self.assertEqual(hub.metadata["empower:platform"], "hub+")
            mock_define_hub_channels.assert_called_once()

    def test_hub_define_hub_channels(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch.object(
            Hub, "define_ethernet_internet_connectivity_channel"
        ) as define_ethernet_internet_connectivity_channel, patch.object(
            Hub, "define_wifi_internet_connectivity_channel"
        ) as define_wifi_internet_connectivity_channel, patch.object(
            Hub, "define_wifi_ssid_channel"
        ) as define_wifi_ssid_channel, patch.object(
            Hub, "define_wifi_type_channel"
        ) as define_wifi_type_channel, patch.object(
            Hub, "define_wifi_signal_strength_channel"
        ) as define_wifi_signal_strength_channel, patch.object(
            Hub, "define_cellular_internet_connectivity_channel"
        ) as define_cellular_internet_connectivity_channel, patch.object(
            Hub, "define_cellular_signal_strength_channel"
        ) as define_cellular_signal_strength_channel, patch.object(
            Hub, "define_cellular_iccid_channel"
        ) as define_cellular_iccid_channel, patch.object(
            Hub, "define_cellular_eid_channel"
        ) as define_cellular_eid_channel, patch.object(
            Hub, "define_active_connection_channel"
        ) as define_active_connection_channel:

            hub.define_hub_channels(n2k_devices)
            define_ethernet_internet_connectivity_channel.assert_called_once()
            define_wifi_internet_connectivity_channel.assert_called_once()
            define_wifi_ssid_channel.assert_called_once()
            define_wifi_type_channel.assert_called_once()
            define_wifi_signal_strength_channel.assert_called_once()
            define_cellular_internet_connectivity_channel.assert_called_once()
            define_cellular_signal_strength_channel.assert_called_once()
            define_cellular_iccid_channel.assert_called_once()
            define_cellular_eid_channel.assert_called_once()
            define_active_connection_channel.assert_called_once()

    def test_hub_define_ethernet_internet_connectivity_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_ethernet_internet_connectivity_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="eic",
                name="Ethernet Internet Connectivity",
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:hub.ethernetInternetConnectivity"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "EthernetInternetConnectivity",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_wifi_internet_connectivity_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_wifi_internet_connectivity_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="wic",
                name="Wifi Internet Connectivity",
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:hub.wifiInternetConnectivity"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "WifiInternetConnectivity",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_wifi_ssid_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_wifi_ssid_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="wsd",
                name="Wifi SSID",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:hub.wifiSsid"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "WifiSsid",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_wifi_type_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_wifi_type_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="wt",
                name="Wifi Type",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:hub.wifiType"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "WifiType",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_wifi_signal_strength_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_wifi_signal_strength_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="wss",
                name="WiFi Signal Strength",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                tags=["empower:hub.wifiSignalStrength"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "WifiSignalStrength",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_wifi_signal_strength_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_wifi_signal_strength_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="wss",
                name="WiFi Signal Strength",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                tags=["empower:hub.wifiSignalStrength"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "WifiSignalStrength",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_cellular_internet_connectivity_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_cellular_internet_connectivity_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="cic",
                name="Cellular Internet Connectivity",
                read_only=True,
                type=ChannelType.BOOLEAN,
                unit=Unit.NONE,
                tags=["empower:hub.cellularInternetConnectivity"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "CellularInternetConnectivity",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_cellular_signal_strength_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_cellular_signal_strength_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="css",
                name="Cellular Signal Strength (dBm)",
                read_only=True,
                type=ChannelType.NUMBER,
                unit=Unit.NONE,
                tags=["empower:hub.cellularSignalStrength"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "CellularSignalStrengthDbm",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_cellular_iccid_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_cellular_iccid_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="iccid",
                name="Cellular ICCID",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=["empower:hub.cellularIccid"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "WifiSignalStrength",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_cellular_iccid_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_cellular_eid_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="cellularEid",
                name="Cellular EID",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=["empower:hub.cellularEid"],
            )
            n2k_devices.get_channel_subject.assert_called_once_with(
                hub.n2k_device_id,
                "CellularSimEid",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()

    def test_hub_define_active_connection_channel(self):
        mock_hub = MagicMock()
        mock_hub.dipswitch = 123
        n2k_devices = MagicMock()

        hub = Hub(mock_hub, n2k_devices)
        with patch(
            "N2KClient.n2kclient.models.empower_system.hub.Channel"
        ) as mock_channel, patch.object(
            Hub, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:
            n2k_devices.get_channel_subject.reset_mock()
            hub.define_active_connection_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="ac",
                name="Active Connection",
                read_only=True,
                type=ChannelType.STRING,
                unit=Unit.NONE,
                tags=["empower:hub.activeConnection"],
            )
            n2k_devices.get_channel_subject.assert_any_call(
                hub.n2k_device_id,
                "EthernetInternetConnectivity",
                N2kDeviceType.DEVICE,
            )
            n2k_devices.get_channel_subject.assert_any_call(
                hub.n2k_device_id,
                "WifiInternetConnectivity",
                N2kDeviceType.DEVICE,
            )
            n2k_devices.get_channel_subject.assert_any_call(
                hub.n2k_device_id,
                "CellularInternetConnectivity",
                N2kDeviceType.DEVICE,
            )
            mock_define_channel.assert_called_once()
