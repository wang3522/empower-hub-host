import json
import unittest
from unittest.mock import MagicMock, patch

from N2KClient.n2kclient.models.common_enums import N2kDeviceType
from N2KClient.n2kclient.services.snapshot_service.snapshot_service import (
    SnapshotService,
)


class SnapshotServiceTest(unittest.TestCase):
    """Unit tests for the SnapshotService"""

    def test_snapshot_service_init(self):
        """
        Test the initialization of the SnapshotService.

        Timer setting is called. Service is properly initialized
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        with patch.object(
            SnapshotService,
            "_set_periodic_snapshot_timer",
        ) as mock_timer_set:
            snapshot_service = SnapshotService(
                dbus_proxy=mock_dbus_service,
                lock=mock_lock,
                get_latest_devices=mock_get_latest_devices,
                set_devices=mock_set_devices,
                get_latest_engine_config=mock_get_latest_engine_config,
                process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
            )
            self.assertIsNotNone(snapshot_service)
            self.assertIsNotNone(snapshot_service._logger)
            mock_timer_set.assert_called_once()
            self.assertEqual(mock_dbus_service, snapshot_service._dbus_proxy)
            self.assertEqual(mock_lock, snapshot_service.lock)
            self.assertEqual(
                mock_get_latest_devices, snapshot_service._get_latest_devices
            )
            self.assertEqual(mock_set_devices, snapshot_service._set_devices)
            self.assertEqual(
                mock_get_latest_engine_config,
                snapshot_service._get_latest_engine_config,
            )
            self.assertEqual(
                mock_process_engine_alarms_from_snapshot,
                snapshot_service._process_engine_alarms_from_snapshot,
            )

    def test_snapshot_handler_engine_config(self):
        """
        Test the snapshot handler.
        Ensures that process_state_from_snapshot is called with the correct arguments.
        Ensures _merge_state_update is called with the correct arguments.
        Ensures _process_engine_alarms_from_snapshot is called with the correct arguments, if latest engine config resolves to not None
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        with patch.object(
            snapshot_service, "_start_snapshot_timer"
        ) as mock_start_snapshot_timer, patch.object(
            snapshot_service, "_merge_state_update"
        ) as mock_merge_state_update:
            snapshot_json = "{}"
            mock_get_latest_engine_config.return_value = MagicMock()
            snapshot_service.snapshot_handler(snapshot_json)

            mock_start_snapshot_timer.assert_called_once()
            mock_get_latest_engine_config.assert_called_once()
            mock_process_engine_alarms_from_snapshot.assert_called_once_with(
                json.loads(snapshot_json)
            )
            mock_merge_state_update.assert_called_once_with(json.loads(snapshot_json))

    def test_snapshot_handler_engine_config_none(self):
        """
        Test the snapshot handler.
        Ensures that process_state_from_snapshot is called with the correct arguments.
        Ensures _merge_state_update is called with the correct arguments.
        Ensures _process_engine_alarms_from_snapshot is called with the correct arguments, if latest engine config resolves to not None
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        with patch.object(
            snapshot_service, "_start_snapshot_timer"
        ) as mock_start_snapshot_timer, patch.object(
            snapshot_service, "_merge_state_update"
        ) as mock_merge_state_update:
            snapshot_json = "{}"
            mock_get_latest_engine_config.return_value = None
            snapshot_service.snapshot_handler(snapshot_json)

            mock_start_snapshot_timer.assert_called_once()
            mock_get_latest_engine_config.assert_called_once()
            mock_process_engine_alarms_from_snapshot.assert_not_called()
            mock_merge_state_update.assert_called_once_with(json.loads(snapshot_json))

    def test_snapshot_handler_exception(self):
        """
        Ensures that snapshot_handler handles exceptions.
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        with patch.object(
            snapshot_service, "_start_snapshot_timer"
        ) as mock_start_snapshot_timer, patch.object(
            snapshot_service, "_merge_state_update"
        ) as mock_merge_state_update:
            snapshot_json = "{}"
            mock_start_snapshot_timer.side_effect = Exception("Test Exception")
            res = snapshot_service.snapshot_handler(snapshot_json)
            self.assertIsNone(res)

    def test_state_from_snapshot_circuits(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        Circuit
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"Circuits": {"Circuit.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("Circuit.1", res)
        self.assertEqual(res["Circuit.1"], {"TEST"})

    def test_state_from_snapshot_tank(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        Tank
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"Tanks": {"Tank.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("Tank.1", res)
        self.assertEqual(res["Tank.1"], {"TEST"})

    def test_state_from_snapshot_engines(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        Engines
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"Engines": {"Engine.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("Engine.1", res)
        self.assertEqual(res["Engine.1"], {"TEST"})

    def test_state_from_snapshot_ac(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        AC
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"AC": {"AC.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("AC.1", res)
        self.assertEqual(res["AC.1"], {"TEST"})

    def test_state_from_snapshot_dc(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        DC
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"DC": {"DC.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("DC.1", res)
        self.assertEqual(res["DC.1"], {"TEST"})

    def test_state_from_snapshot_hvac(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        Hvac
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"HVACs": {"hvac.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("hvac.1", res)
        self.assertEqual(res["hvac.1"], {"TEST"})

    def test_state_from_snapshot_inverter_chargers(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        Inverter Chargers
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"InverterChargers": {"inverter_charger.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("inverter_charger.1", res)
        self.assertEqual(res["inverter_charger.1"], {"TEST"})

    def test_state_from_snapshot_gnss(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        GNSS
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"GNSS": {"gnss.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("gnss.1", res)
        self.assertEqual(res["gnss.1"], {"TEST"})

    def test_state_from_snapshot_bls(self):
        """
        Test the state extraction from the snapshot.
        Ensures states are added and parsed properly to state structure.
        BLS
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        mock_snapshot_dict = {"BinaryLogicState": {"bls.1": {"TEST"}}}
        res = snapshot_service._process_state_from_snapshot(mock_snapshot_dict)

        self.assertIn("bls.1", res)
        self.assertEqual(res["bls.1"], {"TEST"})

    def test_merge_state_update(self):
        """
        Test merge state update
        Non AC, ensure nonac state properly updated
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )
        state_update = {"dc.1": {"voltage": "TEST"}}
        mock_device = MagicMock(type=N2kDeviceType.DC)
        mock_get_latest_devices.return_value = MagicMock(devices={"dc.1": mock_device})
        snapshot_service._merge_state_update(state_update)

        mock_device.update_channel.assert_called_once_with("voltage", "TEST")

        mock_set_devices.assert_called_once()

    def test_merge_state_update_ac(self):
        """
        Test merge state update
        AC, ensure nac state properly updated
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )
        state_update = {"ac.1": {"AClines": {1: {"voltage": "TEST"}}}}
        mock_device = MagicMock(type=N2kDeviceType.AC)
        mock_get_latest_devices.return_value = MagicMock(devices={"ac.1": mock_device})
        snapshot_service._merge_state_update(state_update)

        mock_device.update_channel.assert_called_once_with("voltage.1", "TEST")

        mock_set_devices.assert_called_once()

    def test_merge_state_update_ac_lines_none(self):
        """
        Test merge state update
        AC, ensure nac state properly updated
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )
        state_update = {"ac.1": {}}
        mock_device = MagicMock(type=N2kDeviceType.AC)
        mock_get_latest_devices.return_value = MagicMock(devices={"ac.1": mock_device})
        snapshot_service._merge_state_update(state_update)

        mock_device.update_channel.assert_not_called()

        mock_set_devices.assert_called_once()

    def test_merge_state_update_engine(self):
        """
        Test merge state update
        Engine, ensure state properly updated
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )
        state_update = {"engine.1": {"coolantPressure": "TEST"}}
        mock_device = MagicMock(type=N2kDeviceType.ENGINE)
        mock_get_latest_devices.return_value = MagicMock(
            engine_devices={"engine.1": mock_device}
        )
        snapshot_service._merge_state_update(state_update)

        mock_device.update_channel.assert_called_once_with("coolantPressure", "TEST")

        mock_set_devices.assert_called_once()

    def test_set_periodic_snapshot_timer(self):
        """
        Test set periodic snapshot timer
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )

        snapshot_service._set_periodic_snapshot_timer()
        self.assertIsNotNone(snapshot_service._periodic_snapshot_timer)
        self.assertEqual(
            snapshot_service._periodic_snapshot_timer.function,
            snapshot_service._single_snapshot,
        )

    def test_start_snapshot_timer_sets_and_starts_timer(self):
        """
        Test start snapshot timer sets and starts timer
        """

        with patch("threading.Timer") as mock_timer_cls:
            mock_timer = MagicMock()
            mock_timer_cls.return_value = mock_timer
            mock_dbus_service = MagicMock()
            mock_lock = MagicMock()
            mock_get_latest_devices = MagicMock()
            mock_set_devices = MagicMock()
            mock_get_latest_engine_config = MagicMock()
            mock_process_engine_alarms_from_snapshot = MagicMock()
            snapshot_service = SnapshotService(
                dbus_proxy=mock_dbus_service,
                lock=mock_lock,
                get_latest_devices=mock_get_latest_devices,
                set_devices=mock_set_devices,
                get_latest_engine_config=mock_get_latest_engine_config,
                process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
            )
            with patch.object(
                snapshot_service, "_set_periodic_snapshot_timer"
            ) as mock_set_periodic_snapshot_timer:
                snapshot_service._start_snapshot_timer()
                mock_set_periodic_snapshot_timer.assert_called_once()
                mock_timer.start.assert_called()

    def test_start_snapshot_timer_cancel_existing(self):
        """
        Ensure existing timer is canceled before starting a new one
        """
        with patch("threading.Timer") as mock_timer_cls:
            mock_timer = MagicMock()
            mock_timer.is_alive.return_value = True
            mock_timer_cls.return_value = mock_timer
            mock_dbus_service = MagicMock()
            mock_lock = MagicMock()
            mock_get_latest_devices = MagicMock()
            mock_set_devices = MagicMock()
            mock_get_latest_engine_config = MagicMock()
            mock_process_engine_alarms_from_snapshot = MagicMock()
            snapshot_service = SnapshotService(
                dbus_proxy=mock_dbus_service,
                lock=mock_lock,
                get_latest_devices=mock_get_latest_devices,
                set_devices=mock_set_devices,
                get_latest_engine_config=mock_get_latest_engine_config,
                process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
            )
            snapshot_service._periodic_snapshot_timer = mock_timer
            snapshot_service._start_snapshot_timer()
            mock_timer.cancel.assert_called()

    def test_start_snapshot_timer_exception(self):
        """
        Test start snapshot timer exception handling
        """
        try:
            mock_dbus_service = MagicMock()
            mock_lock = MagicMock()
            mock_get_latest_devices = MagicMock()
            mock_set_devices = MagicMock()
            mock_get_latest_engine_config = MagicMock()
            mock_process_engine_alarms_from_snapshot = MagicMock()
            snapshot_service = SnapshotService(
                dbus_proxy=mock_dbus_service,
                lock=mock_lock,
                get_latest_devices=mock_get_latest_devices,
                set_devices=mock_set_devices,
                get_latest_engine_config=mock_get_latest_engine_config,
                process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
            )
            with patch.object(
                snapshot_service, "_set_periodic_snapshot_timer"
            ) as mock_set_periodic_snapshot_timer:
                mock_set_periodic_snapshot_timer.side_effect = Exception(
                    "Test Exception"
                )
                snapshot_service._start_snapshot_timer()

                pass

        except Exception as e:
            self.assertTrue(False)

    def test_single_snapshot(self):
        """
        Ensure single snapshot calls dbus_proxy for single snapshot and handles snapshot
        """

        mock_dbus_service = MagicMock()
        mock_lock = MagicMock()
        mock_get_latest_devices = MagicMock()
        mock_set_devices = MagicMock()
        mock_get_latest_engine_config = MagicMock()
        mock_process_engine_alarms_from_snapshot = MagicMock()

        mock_dbus_service.single_snapshot.return_value = "TEST"
        snapshot_service = SnapshotService(
            dbus_proxy=mock_dbus_service,
            lock=mock_lock,
            get_latest_devices=mock_get_latest_devices,
            set_devices=mock_set_devices,
            get_latest_engine_config=mock_get_latest_engine_config,
            process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
        )
        with patch.object(
            snapshot_service, "snapshot_handler"
        ) as mock_snapshot_handler:
            snapshot_service._single_snapshot()
            mock_dbus_service.single_snapshot.assert_called_once()
            mock_snapshot_handler.assert_called_once_with("TEST")

    def test_single_snapshot_exception(self):
        """
        Ensure exceptions are handled and not elevated
        """
        try:
            mock_dbus_service = MagicMock()
            mock_lock = MagicMock()
            mock_get_latest_devices = MagicMock()
            mock_set_devices = MagicMock()
            mock_get_latest_engine_config = MagicMock()
            mock_process_engine_alarms_from_snapshot = MagicMock()
            mock_dbus_service.single_snapshot.side_effect = Exception("Test Exception")
            snapshot_service = SnapshotService(
                dbus_proxy=mock_dbus_service,
                lock=mock_lock,
                get_latest_devices=mock_get_latest_devices,
                set_devices=mock_set_devices,
                get_latest_engine_config=mock_get_latest_engine_config,
                process_engine_alarms_from_snapshot=mock_process_engine_alarms_from_snapshot,
            )
            with patch.object(
                snapshot_service, "snapshot_handler"
            ) as mock_snapshot_handler:
                snapshot_service._single_snapshot()
                pass
        except Exception as e:
            self.assertTrue(False)
