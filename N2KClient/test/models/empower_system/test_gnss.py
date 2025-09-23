import unittest
from unittest.mock import MagicMock, call, patch, ANY

from N2KClient.n2kclient.models.empower_system.gnss import GNSS
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    Unit,
    ThingType,
)
import reactivex as rx


class TestGNSS(unittest.TestCase):

    def test_gnss_init(self):
        mock_gnss = MagicMock()
        mock_gnss.instance = MagicMock(instance=1)
        mock_gnss.is_external = True
        n2k_devices = MagicMock()

        with patch.object(GNSS, "define_gnss_channels") as mock_define_gnss_channels:
            gnss = GNSS(mock_gnss, n2k_devices, ["TEST"])

            self.assertEqual(gnss.instance, 1)
            self.assertEqual(gnss.gnss_device_id, "GNSS.1")
            self.assertEqual(gnss.metadata["empower:location.external"], True)
            mock_define_gnss_channels.assert_called_once()

    def test_gnss_define_gnss_channels(self):
        mock_gnss = MagicMock()
        mock_gnss.instance = MagicMock(instance=1)
        mock_gnss.is_external = True
        n2k_devices = MagicMock()

        gnss = GNSS(mock_gnss, n2k_devices, ["TEST"])
        with patch.object(
            GNSS, "define_component_status"
        ) as mock_define_component_status, patch.object(
            GNSS, "define_fix_type_channel"
        ) as mock_define_fix_type_channel, patch.object(
            GNSS, "define_location_channel"
        ) as mock_define_location_channel:

            gnss.define_gnss_channels(n2k_devices)
            mock_define_component_status.assert_called_once()
            mock_define_fix_type_channel.assert_called_once()
            mock_define_location_channel.assert_called_once()

    def test_define_component_status(self):
        mock_gnss = MagicMock()
        mock_gnss.instance = MagicMock(instance=1)
        mock_gnss.is_external = True
        n2k_devices = MagicMock()

        gnss = GNSS(mock_gnss, n2k_devices, ["TEST"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.gnss.Channel"
        ) as mock_channel, patch.object(
            GNSS, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            gnss.define_component_status(n2k_devices)
            mock_channel.assert_called_once_with(
                id="cs",
                name="Component Status",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=False,
                tags=["empower:location.componentStatus"],
            )
            mock_define_channel.assert_called_once()

    def test_define_fix_type_channel(self):
        mock_gnss = MagicMock()
        mock_gnss.instance = MagicMock(instance=1)
        mock_gnss.is_external = True
        n2k_devices = MagicMock()

        gnss = GNSS(mock_gnss, n2k_devices, ["TEST"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.gnss.Channel"
        ) as mock_channel, patch.object(
            GNSS, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            gnss.define_fix_type_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="ft",
                name="Fix Type",
                type=ChannelType.STRING,
                unit=Unit.NONE,
                read_only=True,
                tags=["empower:location.fixType"],
            )
            mock_define_channel.assert_called_once()

    def test_define_location_channel(self):
        mock_gnss = MagicMock()
        mock_gnss.instance = MagicMock(instance=1)
        mock_gnss.is_external = True
        n2k_devices = MagicMock()

        gnss = GNSS(mock_gnss, n2k_devices, ["TEST"])
        with patch(
            "N2KClient.n2kclient.models.empower_system.gnss.Channel"
        ) as mock_channel, patch.object(
            GNSS, "_define_channel", return_value=MagicMock()
        ) as mock_define_channel:

            gnss.define_location_channel(n2k_devices)
            mock_channel.assert_called_once_with(
                id="loc",
                name="Location",
                read_only=True,
                type=ChannelType.POINT,
                unit=Unit.GEOJSON_POINT,
                tags=["empower:location.position"],
            )
            mock_define_channel.assert_called_once()
