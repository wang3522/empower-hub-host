import unittest
from unittest.mock import MagicMock, call, patch, ANY

from N2KClient.n2kclient.models.devices import N2kDevice, N2kDevices
from N2KClient.n2kclient.models.common_enums import (
    ChannelType,
    N2kDeviceType,
    Unit,
    ThingType,
)
import reactivex as rx


class TestN2KDevices(unittest.TestCase):

    # Device
    def test_init_n2k_device(self):
        dev = N2kDevice(type=N2kDeviceType.AC)
        self.assertEqual(dev.type, N2kDeviceType.AC)
        self.assertEqual(dev.channels, {})
        self.assertEqual(dev._channel_subjects, {})

    def test_update_channel_doesnt_exists(self):
        dev = N2kDevice(type=N2kDeviceType.AC)
        dev.update_channel("test_channel", "test_value")
        self.assertEqual(dev.channels["test_channel"], "test_value")

    def test_update_channel_exists(self):
        dev = N2kDevice(type=N2kDeviceType.AC)
        dev.channels["test_channel"] = "old_value"
        mock_subject = MagicMock()
        dev._channel_subjects["test_channel"] = mock_subject
        dev.update_channel("test_channel", "new_value")
        self.assertEqual(dev.channels["test_channel"], "new_value")
        mock_subject.on_next.assert_called_once_with("new_value")

    def test_del(self):
        dev = N2kDevice(type=N2kDeviceType.AC)
        dev.channels["test_channel"] = "value"
        dev._channel_subjects["test_channel"] = MagicMock()
        with patch.object(N2kDevice, "dispose") as mock_dispose:
            del dev
            mock_dispose.assert_called_once()

    def test_dispose(self):
        dev = N2kDevice(type=N2kDeviceType.AC)
        dev.channels["test_channel"] = "value"
        dev._channel_subjects["test_channel"] = MagicMock()
        dev.dispose()
        self.assertEqual(dev.channels, {})
        self.assertEqual(dev._channel_subjects, {})

    # Devices

    def test_devices_init(self):
        devices = N2kDevices()
        self.assertEqual(devices.devices, {})
        self.assertEqual(devices.engine_devices, {})
        self.assertEqual(devices.mobile_channels, {})
        self.assertEqual(devices._pipe_subscriptions, {})
        self.assertEqual(devices._engine_pipe_subscriptions, {})

    def test_dispose_devices_is_engine(self):
        devices = N2kDevices()
        devices.devices["dev1"] = MagicMock()
        devices.engine_devices["eng1"] = MagicMock()
        devices.mobile_channels["chan1"] = MagicMock()
        devices.engine_mobile_channels["echan1"] = MagicMock()
        devices._pipe_subscriptions["sub1"] = MagicMock()
        devices._engine_pipe_subscriptions["esub1"] = MagicMock()
        devices.dispose_devices(is_engine=True)
        self.assertNotEqual(devices.devices, {})
        self.assertEqual(devices.engine_devices, {})
        self.assertNotEqual(devices.mobile_channels, {})
        self.assertEqual(devices.engine_mobile_channels, {})
        self.assertNotEqual(devices._pipe_subscriptions, {})
        self.assertEqual(devices._engine_pipe_subscriptions, {})

    def test_dispose_devices_not_is_engine(self):
        devices = N2kDevices()
        devices.devices["dev1"] = MagicMock()
        devices.engine_devices["eng1"] = MagicMock()
        devices.mobile_channels["chan1"] = MagicMock()
        devices.engine_mobile_channels["echan1"] = MagicMock()
        devices._pipe_subscriptions["sub1"] = MagicMock()
        devices._engine_pipe_subscriptions["esub1"] = MagicMock()
        devices.dispose_devices()
        self.assertEqual(devices.devices, {})
        self.assertNotEqual(devices.engine_devices, {})
        self.assertEqual(devices.mobile_channels, {})
        self.assertNotEqual(devices.engine_mobile_channels, {})
        self.assertEqual(devices._pipe_subscriptions, {})
        self.assertNotEqual(devices._engine_pipe_subscriptions, {})

    def test_add(self):
        devices = N2kDevices()
        dev = MagicMock()
        dev.type = N2kDeviceType.AC
        devices.add("dev1", dev)
        self.assertIn("dev1", devices.devices)
        self.assertEqual(devices.devices["dev1"], dev)

    def test_add_engine(self):
        devices = N2kDevices()
        dev = MagicMock()
        dev.type = N2kDeviceType.ENGINE
        devices.add("eng1", dev)
        self.assertIn("eng1", devices.engine_devices)
        self.assertEqual(devices.engine_devices["eng1"], dev)

    def test_get_channel_subject(self):
        devices = N2kDevices()
        dev = N2kDevice(type=N2kDeviceType.AC)
        devices.add("dev1", dev)
        subject = devices.get_channel_subject("dev1", "chan1", N2kDeviceType.AC)
        self.assertIsInstance(subject, rx.subject.BehaviorSubject)
        self.assertIn("chan1", dev._channel_subjects)
        self.assertEqual(dev._channel_subjects["chan1"], subject)

    def test_set_subscription(self):
        devices = N2kDevices()
        sub = MagicMock()
        result = sub.subscribe.return_value
        devices.set_subscription("sub1", sub)
        self.assertIn("sub1", devices._pipe_subscriptions)
        self.assertEqual(devices._pipe_subscriptions["sub1"], result)

    def test_set_engine_subscription(self):
        devices = N2kDevices()
        sub = MagicMock()
        result = sub.subscribe.return_value
        devices.set_subscription("esub1", sub, True)
        self.assertIn("esub1", devices._engine_pipe_subscriptions)
        self.assertEqual(devices._engine_pipe_subscriptions["esub1"], result)

    def test_update_mobile_channel(self):
        devices = N2kDevices()
        subject = MagicMock()
        devices._update_mobile_channel("chan1", subject)
        self.assertIn("chan1", devices.mobile_channels)
        self.assertEqual(devices.mobile_channels["chan1"], subject)

    def test_update_engine_mobile_channel(self):
        devices = N2kDevices()
        subject = MagicMock()
        devices._update_mobile_channel("echan1", subject, True)
        self.assertIn("echan1", devices.engine_mobile_channels)
        self.assertEqual(devices.engine_mobile_channels["echan1"], subject)

    def test_to_mobile_dict(self):
        devices = N2kDevices()
        subject1 = MagicMock()
        subject2 = MagicMock()
        devices._update_mobile_channel("chan1", subject1)
        devices._update_mobile_channel("chan2", subject2)
        mobile_dict = devices.to_mobile_dict()
        self.assertIn("chan1", mobile_dict)
        self.assertIn("chan2", mobile_dict)
        self.assertEqual(mobile_dict["chan1"], subject1)
        self.assertEqual(mobile_dict["chan2"], subject2)

    def test_eq(self):
        devices1 = N2kDevices()
        devices2 = N2kDevices()
        mobile_channels = {"chan1": MagicMock()}
        devices1.mobile_channels = mobile_channels
        devices2.mobile_channels = mobile_channels
        engine_mobile_channels = {"echan1": MagicMock()}
        devices1.engine_mobile_channels = engine_mobile_channels
        devices2.engine_mobile_channels = engine_mobile_channels
        self.assertEqual(devices1, devices2)
        dev1 = MagicMock()
        dev1.type = N2kDeviceType.AC
        devices1.add("dev1", dev1)
        self.assertNotEqual(devices1, devices2)
        devices2.add("dev1", dev1)
        self.assertEqual(devices1, devices2)

    def test_eq_not_n2kdevices(self):
        devices = N2kDevices()
        self.assertNotEqual(devices, "not a N2kDevices instance")
