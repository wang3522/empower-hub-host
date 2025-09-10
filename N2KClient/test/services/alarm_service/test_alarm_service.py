import json
import unittest
from N2KClient.n2kclient.models.constants import Constants
from N2KClient.n2kclient.models.empower_system.alarm import Alarm, AlarmState
from N2KClient.n2kclient.models.empower_system.alarm_list import AlarmList
from N2KClient.n2kclient.models.empower_system.component_reference import (
    ComponentReference,
)
from N2KClient.n2kclient.models.n2k_configuration.dc import DCType
from N2KClient.n2kclient.models.n2k_configuration.ac import ACType
from N2KClient.n2kclient.services.alarm_service.alarm_service import AlarmService
from unittest.mock import ANY, call, patch, MagicMock
from N2KClient.n2kclient.models.n2k_configuration.alarm import (
    Alarm as N2KAlarm,
    eSeverityType,
)
from N2KClient.n2kclient.models.common_enums import (
    ComponentType,
    eStateType,
    eAlarmType,
)
from N2KClient.n2kclient.models.n2k_configuration.tank import TankType
from N2KClient.n2kclient.models.empower_system.engine_alarm_list import EngineAlarmList


class AlarmServiceTest(unittest.TestCase):
    """Unit tests for Alarm Service"""

    def test_alarm_service_init(self):
        """
        Test the initialization of the Alarm Service.
        """
        alarm_list_func = MagicMock()
        get_latest_alarms_func = MagicMock()
        get_config_func = MagicMock()
        get_engine_config_func = MagicMock()
        get_engine_alarms_func = MagicMock()
        set_alarm_list = MagicMock()
        set_engine_alarms = MagicMock()
        acknowledge_alarm_func = MagicMock()
        get_latest_empower_system_func = MagicMock()
        get_latest_engine_list_func = MagicMock()

        alarm_service = AlarmService(
            alarm_list_func,
            get_latest_alarms_func,
            get_config_func,
            get_engine_config_func,
            get_engine_alarms_func,
            set_alarm_list,
            set_engine_alarms,
            acknowledge_alarm_func,
            get_latest_empower_system_func,
            get_latest_engine_list_func,
        )
        self.assertIsNotNone(alarm_service)

    def test_acknowledge_alarm(self):
        """
        Test the acknowledge_alarm method. Alarm exists and is not acknowledged
        """
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.send_and_validate_response"
        ) as mock_send:
            mock_latest_alarms = AlarmList()
            mock_latest_alarms.alarm[0] = Alarm()
            mock_latest_alarms.alarm[0].current_state = AlarmState.ENABLED
            alarm_list_func = MagicMock()
            get_latest_alarms_func = MagicMock()
            get_latest_alarms_func.return_value = mock_latest_alarms
            get_config_func = MagicMock()
            get_engine_config_func = MagicMock()
            get_engine_alarms_func = MagicMock()
            set_alarm_list = MagicMock()
            set_engine_alarms = MagicMock()
            acknowledge_alarm_func = MagicMock()
            get_latest_empower_system_func = MagicMock()
            get_latest_engine_list_func = MagicMock()

            alarm_service = AlarmService(
                alarm_list_func,
                get_latest_alarms_func,
                get_config_func,
                get_engine_config_func,
                get_engine_alarms_func,
                set_alarm_list,
                set_engine_alarms,
                acknowledge_alarm_func,
                get_latest_empower_system_func,
                get_latest_engine_list_func,
            )

            res = alarm_service.acknowledge_alarm(0)
            self.assertTrue(res)
            mock_send.assert_called_once()

    def test_acknowledge_alarm_not_found(self):
        """
        Test the acknowledge_alarm method. Alarm exists and is not acknowledged
        """
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.send_and_validate_response"
        ) as mock_send:
            mock_latest_alarms = AlarmList()
            mock_latest_alarms.alarm[1] = Alarm()
            mock_latest_alarms.alarm[1].current_state = AlarmState.ENABLED
            alarm_list_func = MagicMock()
            get_latest_alarms_func = MagicMock()
            get_latest_alarms_func.return_value = mock_latest_alarms
            get_config_func = MagicMock()
            get_engine_config_func = MagicMock()
            get_engine_alarms_func = MagicMock()
            set_alarm_list = MagicMock()
            set_engine_alarms = MagicMock()
            acknowledge_alarm_func = MagicMock()
            get_latest_empower_system_func = MagicMock()
            get_latest_engine_list_func = MagicMock()

            alarm_service = AlarmService(
                alarm_list_func,
                get_latest_alarms_func,
                get_config_func,
                get_engine_config_func,
                get_engine_alarms_func,
                set_alarm_list,
                set_engine_alarms,
                acknowledge_alarm_func,
                get_latest_empower_system_func,
                get_latest_engine_list_func,
            )

            res = alarm_service.acknowledge_alarm(0)

            mock_send.assert_not_called()
            self.assertFalse(res)

    def test_load_active_alarms_valid_str(self):
        """
        Test the load_active_alarms method with a valid string input and different alarm lists
        """
        alarm_list_func = MagicMock(return_value="testStr")
        set_alarm_list = MagicMock()
        # Mock latest_alarms with to_alarm_dict returning something different from merged
        mock_latest_alarms = MagicMock()
        mock_latest_alarms.to_alarm_dict.return_value = {"baz": "qux"}
        get_latest_alarms_func = MagicMock(return_value=mock_latest_alarms)

        alarm_service = AlarmService(
            alarm_list_func,
            get_latest_alarms_func,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            set_alarm_list,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        # Patch only what's needed to trigger the set_alarm_list call
        mock_merged_alarm_list = MagicMock()
        mock_merged_alarm_list.to_alarm_dict.return_value = {"foo": "bar"}
        with patch.object(
            alarm_service, "_merge_alarm_lists", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "_verify_alarm_things", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "parse_alarm_list", return_value=[MagicMock()]
        ):
            alarm_service.load_active_alarms()

        set_alarm_list.assert_called_once()

    def test_load_active_alarms_invalid_str(self):
        """
        Test the load_active_alarms method with an invalid string input.
        """
        alarm_list_func = MagicMock(return_value=None)
        set_alarm_list = MagicMock()
        # Mock latest_alarms with to_alarm_dict returning something different from merged
        mock_latest_alarms = MagicMock()
        mock_latest_alarms.to_alarm_dict.return_value = {"baz": "qux"}
        get_latest_alarms_func = MagicMock(return_value=mock_latest_alarms)

        alarm_service = AlarmService(
            alarm_list_func,
            get_latest_alarms_func,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            set_alarm_list,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        # Patch only what's needed to trigger the set_alarm_list call
        mock_merged_alarm_list = MagicMock()
        mock_merged_alarm_list.to_alarm_dict.return_value = {"foo": "bar"}
        with patch.object(
            alarm_service, "_merge_alarm_lists", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "_verify_alarm_things", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "parse_alarm_list", return_value=[MagicMock()]
        ):
            alarm_service.load_active_alarms()

        set_alarm_list.assert_not_called()

    def test_load_active_alarms_same_list(self):
        """
        Test the load_active_alarms, same list is returned so set_alarm_list is not called.
        """
        alarm_list_func = MagicMock(return_value="testStr")
        set_alarm_list = MagicMock()
        # Mock latest_alarms with to_alarm_dict returning something different from merged
        mock_latest_alarms = MagicMock()
        mock_latest_alarms.to_alarm_dict.return_value = {"foo": "bar"}
        get_latest_alarms_func = MagicMock(return_value=mock_latest_alarms)

        alarm_service = AlarmService(
            alarm_list_func,
            get_latest_alarms_func,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            set_alarm_list,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        # Patch only what's needed to trigger the set_alarm_list call
        mock_merged_alarm_list = MagicMock()
        mock_merged_alarm_list.to_alarm_dict.return_value = {"foo": "bar"}
        with patch.object(
            alarm_service, "_merge_alarm_lists", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "_verify_alarm_things", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "parse_alarm_list", return_value=[MagicMock()]
        ):
            alarm_service.load_active_alarms()

        set_alarm_list.assert_not_called()

    def test_load_active_alarms_same_list_force(self):
        """
        Test the load_active_alarms, same list is returned, but force is true so set_alarm_list is called.
        """
        alarm_list_func = MagicMock(return_value="testStr")
        set_alarm_list = MagicMock()
        # Mock latest_alarms with to_alarm_dict returning something different from merged
        mock_latest_alarms = MagicMock()
        mock_latest_alarms.to_alarm_dict.return_value = {"foo": "bar"}
        get_latest_alarms_func = MagicMock(return_value=mock_latest_alarms)

        alarm_service = AlarmService(
            alarm_list_func,
            get_latest_alarms_func,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            set_alarm_list,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        # Patch only what's needed to trigger the set_alarm_list call
        mock_merged_alarm_list = MagicMock()
        mock_merged_alarm_list.to_alarm_dict.return_value = {"foo": "bar"}
        with patch.object(
            alarm_service, "_merge_alarm_lists", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "_verify_alarm_things", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "parse_alarm_list", return_value=[MagicMock()]
        ):
            alarm_service.load_active_alarms(True)

        set_alarm_list.assert_called_once()

    def test_load_active_alarms_exception(self):
        """
        Test the load_active_alarms, exception is raised so set_alarm_list is not called. False is returned
        """
        alarm_list_func = MagicMock(side_effect=Exception("Test Exception"))
        set_alarm_list = MagicMock()
        # Mock latest_alarms with to_alarm_dict returning something different from merged
        mock_latest_alarms = MagicMock()
        mock_latest_alarms.to_alarm_dict.return_value = {"foo": "bar"}
        get_latest_alarms_func = MagicMock(return_value=mock_latest_alarms)

        alarm_service = AlarmService(
            alarm_list_func,
            get_latest_alarms_func,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            set_alarm_list,
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        # Patch only what's needed to trigger the set_alarm_list call
        mock_merged_alarm_list = MagicMock()
        mock_merged_alarm_list.to_alarm_dict.return_value = {"foo": "bar"}
        with patch.object(
            alarm_service, "_merge_alarm_lists", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "_verify_alarm_things", return_value=mock_merged_alarm_list
        ), patch.object(
            alarm_service, "parse_alarm_list", return_value=[MagicMock()]
        ):
            res = alarm_service.load_active_alarms(True)

        set_alarm_list.assert_not_called()
        self.assertFalse(res[0])

    def test_merge_alarm_lists(self):
        """
        Test the _merge_alarm_lists function. Add single alarm to merged list when processed alarm is not None.
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "_process_and_merge_alarm", return_value=(1, MagicMock())
        ):
            res = alarm_service._merge_alarm_lists(
                [MagicMock()], MagicMock(), MagicMock(), MagicMock()
            )

        self.assertIsInstance(res, AlarmList)
        self.assertEqual(len(res.alarm), 1)

    def test_merge_alarm_lists_no_processed_alarm(self):
        """
        Test the _merge_alarm_lists function. No alarm is added to merged list when processed alarm is None.
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "_process_and_merge_alarm", return_value=(None, None)
        ):
            res = alarm_service._merge_alarm_lists(
                [MagicMock()], MagicMock(), MagicMock(), MagicMock()
            )

        self.assertIsInstance(res, AlarmList)
        self.assertEqual(len(res.alarm), 0)

    def test_process_and_merge_alarm_update_acknowledged(self):
        """
        Test the _process_and_merge_alarm function. Update state to acknowledged
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        res = alarm_service._process_and_merge_alarm(
            MagicMock(unique_id=1, current_state=eStateType.StateAcknowledged),
            MagicMock(alarm={1: MagicMock()}),
            MagicMock(),
            MagicMock(),
        )

        self.assertEqual(res[0], 1)
        self.assertEqual(res[0].current_state, AlarmState.ACKNOWLEDGED)

    def test_process_and_merge_alarm_update_acknowledged(self):
        """
        Test the _process_and_merge_alarm function. New alarm is created and returned when no matching alarm is found.
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "build_reportable_alarm"
        ) as mock_build_reportable_alarm:
            mock_build_reportable_alarm.return_value = MagicMock()
            res = alarm_service._process_and_merge_alarm(
                MagicMock(
                    unique_id=1,
                    current_state=eStateType.StateAcknowledged,
                    external_alarm_id=1,
                ),
                MagicMock(),
                MagicMock(),
                MagicMock(),
            )

        self.assertEqual(res[0], 1)
        self.assertEqual(res[1], mock_build_reportable_alarm.return_value)
        mock_build_reportable_alarm.assert_called_once()

    def test_process_and_merge_alarm_update_enabled_update(self):
        """
        Test the _process_and_merge_alarm function. If enabled and alarm is in list but not enabled, it should be updated.
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        res = alarm_service._process_and_merge_alarm(
            MagicMock(unique_id=1, current_state=eStateType.StateEnabled),
            MagicMock(alarm={1: MagicMock(current_state=AlarmState.DISABLED)}),
            MagicMock(),
            MagicMock(),
        )

        self.assertEqual(res[0], 1)
        self.assertEqual(res[1].current_state, AlarmState.ENABLED)

    def test_process_and_merge_alarm_update_enabled_update(self):
        """
        Test the _process_and_merge_alarm function. If enabled and alarm is in list is enabled, it should remain enabled.
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        res = alarm_service._process_and_merge_alarm(
            MagicMock(unique_id=1, current_state=eStateType.StateEnabled),
            MagicMock(alarm={1: MagicMock(current_state=AlarmState.ENABLED)}),
            MagicMock(),
            MagicMock(),
        )

        self.assertEqual(res[0], 1)
        self.assertEqual(res[1].current_state, AlarmState.ENABLED)

    def test_process_and_merge_alarm_update_acknowledged(self):
        """
        Test the _process_and_merge_alarm function. New alarm is created and returned when no matching alarm is found for state enabled
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "build_reportable_alarm"
        ) as mock_build_reportable_alarm:
            mock_build_reportable_alarm.return_value = MagicMock()
            res = alarm_service._process_and_merge_alarm(
                MagicMock(
                    unique_id=1,
                    current_state=eStateType.StateEnabled,
                    external_alarm_id=1,
                ),
                MagicMock(),
                MagicMock(),
                MagicMock(),
            )

        self.assertEqual(res[0], 1)
        self.assertEqual(res[1], mock_build_reportable_alarm.return_value)
        mock_build_reportable_alarm.assert_called_once()

    def test_build_reportable_alarm_valid_references_things_post_processing(self):
        """
        Test creating a reportable alarm with valid references and post-processing, thing links. Should return alarm
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "get_alarm_related_components"
        ) as mock_get_alarm_related_components, patch.object(
            alarm_service, "get_alarm_things"
        ) as mock_get_alarm_things, patch.object(
            alarm_service, "post_process_alarm_configuration"
        ) as mock_post_process_alarm_configuration:
            mock_get_alarm_related_components.return_value = [MagicMock()]
            mock_get_alarm_things.return_value = MagicMock()
            mock_post_process_alarm_configuration.return_value = MagicMock()
            res = alarm_service.build_reportable_alarm(
                MagicMock(channel_id=1234, alarm_type=eAlarmType.External),
                MagicMock(),
                1234,
                MagicMock(),
                MagicMock(),
            )
            mock_get_alarm_related_components.assert_called_once()
            mock_get_alarm_things.assert_called_once()
            mock_post_process_alarm_configuration.assert_called_once()
            self.assertIsNotNone(res)

    def test_build_reportable_alarm_invalid_channel_id(self):
        """
        Test creating a reportable alarm with invalid channel id. Should not process alarm
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "get_alarm_related_components"
        ) as mock_get_alarm_related_components, patch.object(
            alarm_service, "get_alarm_things"
        ) as mock_get_alarm_things, patch.object(
            alarm_service, "post_process_alarm_configuration"
        ) as mock_post_process_alarm_configuration:
            mock_get_alarm_related_components.return_value = [MagicMock()]
            mock_get_alarm_things.return_value = MagicMock()
            mock_post_process_alarm_configuration.return_value = MagicMock()
            res = alarm_service.build_reportable_alarm(
                MagicMock(alarm_type=eAlarmType.External, channel_id=None),
                MagicMock(),
                1234,
                MagicMock(),
                MagicMock(),
            )
            mock_get_alarm_related_components.assert_not_called()
            mock_get_alarm_things.assert_not_called()
            mock_post_process_alarm_configuration.assert_not_called()
            self.assertIsNone(res)

    def test_build_reportable_alarm_invalid_alarm(self):
        """
        Test creating a reportable alarm with invalid alarm from N2K DBUS. Should not process alarm
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "get_alarm_related_components"
        ) as mock_get_alarm_related_components, patch.object(
            alarm_service, "get_alarm_things"
        ) as mock_get_alarm_things, patch.object(
            alarm_service, "post_process_alarm_configuration"
        ) as mock_post_process_alarm_configuration:
            mock_get_alarm_related_components.return_value = [MagicMock()]
            mock_get_alarm_things.return_value = MagicMock()
            mock_post_process_alarm_configuration.return_value = MagicMock()
            res = alarm_service.build_reportable_alarm(
                None,
                MagicMock(),
                1234,
                MagicMock(),
                MagicMock(),
            )
            mock_get_alarm_related_components.assert_not_called()
            mock_get_alarm_things.assert_not_called()
            mock_post_process_alarm_configuration.assert_not_called()
            self.assertIsNone(res)

    def test_build_reportable_alarm_invalid_type(self):
        """
        Test creating a reportable alarm with invalid alarm type (DeviceMissing) from N2K DBUS. Should not process alarm
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "get_alarm_related_components"
        ) as mock_get_alarm_related_components, patch.object(
            alarm_service, "get_alarm_things"
        ) as mock_get_alarm_things, patch.object(
            alarm_service, "post_process_alarm_configuration"
        ) as mock_post_process_alarm_configuration:
            mock_get_alarm_related_components.return_value = [MagicMock()]
            mock_get_alarm_things.return_value = MagicMock()
            mock_post_process_alarm_configuration.return_value = MagicMock()
            res = alarm_service.build_reportable_alarm(
                MagicMock(alarm_type=eAlarmType.TypeDeviceMissing, channel_id=1234),
                MagicMock(),
                1234,
                MagicMock(),
                MagicMock(),
            )
            mock_get_alarm_related_components.assert_not_called()
            mock_get_alarm_things.assert_not_called()
            mock_post_process_alarm_configuration.assert_not_called()
            self.assertIsNone(res)

    def test_build_reportable_alarm_no_references(self):
        """
        Test creating a reportable alarm with alarm that has no thing references. Should not create reportable alarm + Return None
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "get_alarm_related_components"
        ) as mock_get_alarm_related_components, patch.object(
            alarm_service, "get_alarm_things"
        ) as mock_get_alarm_things, patch.object(
            alarm_service, "post_process_alarm_configuration"
        ) as mock_post_process_alarm_configuration:
            mock_get_alarm_related_components.return_value = []
            mock_get_alarm_things.return_value = MagicMock()
            mock_post_process_alarm_configuration.return_value = MagicMock()
            res = alarm_service.build_reportable_alarm(
                MagicMock(channel_id=1234),
                MagicMock(),
                1234,
                MagicMock(),
                MagicMock(),
            )
            mock_get_alarm_things.assert_not_called()
            mock_post_process_alarm_configuration.assert_not_called()
            self.assertIsNone(res)

    def test_build_reportable_alarm_no_references(self):
        """
        Test creating a reportable alarm with alarm that has no alarm things
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "get_alarm_related_components"
        ) as mock_get_alarm_related_components, patch.object(
            alarm_service, "get_alarm_things"
        ) as mock_get_alarm_things, patch.object(
            alarm_service, "post_process_alarm_configuration"
        ) as mock_post_process_alarm_configuration:
            mock_get_alarm_related_components.return_value = [MagicMock()]
            mock_get_alarm_things.return_value = None
            mock_post_process_alarm_configuration.return_value = MagicMock()
            res = alarm_service.build_reportable_alarm(
                MagicMock(channel_id=1234),
                MagicMock(),
                1234,
                MagicMock(),
                MagicMock(),
            )
            self.assertIsNone(res)

    def test_build_reportable_alarm_no_references(self):
        """
        Test creating a reportable alarm with alarm that failed post-processing checks, should return None
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch.object(
            alarm_service, "get_alarm_related_components"
        ) as mock_get_alarm_related_components, patch.object(
            alarm_service, "get_alarm_things"
        ) as mock_get_alarm_things, patch.object(
            alarm_service, "post_process_alarm_configuration"
        ) as mock_post_process_alarm_configuration:
            mock_get_alarm_related_components.return_value = [MagicMock()]
            mock_get_alarm_things.return_value = MagicMock()
            mock_post_process_alarm_configuration.return_value = None
            res = alarm_service.build_reportable_alarm(
                MagicMock(channel_id=1234),
                MagicMock(),
                1234,
                MagicMock(),
                MagicMock(),
            )
            self.assertIsNone(res)

    def test_get_alarm_related_components_nonengine(self):
        """
        Test get_alarm_related_components. Not engine alarm
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_device_alarms"
        ) as mock_process_device_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_dc_meter_alarms"
        ) as mock_process_dc_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_ac_meter_alarms"
        ) as mock_process_ac_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_tank_alarms"
        ) as mock_process_tank_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_circuit_load_alarms"
        ) as mock_process_circuit_load_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_bls_alarms"
        ) as mock_process_bls_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_smartcraft_alarms"
        ) as mock_process_smartcraft_alarms, patch.object(
            alarm_service, "_is_dc_meter_alarm"
        ) as mock_is_dc_meter_alarm:
            alarm = N2KAlarm(
                external_alarm_id=1,
                channel_id=1234,
            )
            mock_is_dc_meter_alarm.return_value = False
            n2k_config = MagicMock()
            engine_config = MagicMock()
            alarm_service.get_alarm_related_components(
                alarm=alarm, config=n2k_config, engine_config=engine_config
            )

            mock_is_dc_meter_alarm.assert_called_once()
            mock_process_ac_alarms.assert_called_once()
            mock_process_device_alarms.assert_called_once()
            mock_process_dc_alarms.assert_called_once()
            mock_process_tank_alarms.assert_called_once()
            mock_process_circuit_load_alarms.assert_called_once()
            mock_process_bls_alarms.assert_called_once()
            mock_process_smartcraft_alarms.assert_not_called()

    def test_get_alarm_related_components_engine(self):
        """
        Test get_alarm_related_components. Engine alarm
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_device_alarms"
        ) as mock_process_device_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_dc_meter_alarms"
        ) as mock_process_dc_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_ac_meter_alarms"
        ) as mock_process_ac_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_tank_alarms"
        ) as mock_process_tank_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_circuit_load_alarms"
        ) as mock_process_circuit_load_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_bls_alarms"
        ) as mock_process_bls_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_smartcraft_alarms"
        ) as mock_process_smartcraft_alarms, patch.object(
            alarm_service, "_is_dc_meter_alarm"
        ) as mock_is_dc_meter_alarm:
            alarm = N2KAlarm(
                external_alarm_id=11111111111,
                channel_id=1234,
            )
            mock_is_dc_meter_alarm.return_value = False
            n2k_config = MagicMock()
            engine_config = MagicMock()
            alarm_service.get_alarm_related_components(
                alarm=alarm, config=n2k_config, engine_config=engine_config
            )

            mock_is_dc_meter_alarm.assert_called_once()
            mock_process_ac_alarms.assert_called_once()
            mock_process_device_alarms.assert_called_once()
            mock_process_dc_alarms.assert_called_once()
            mock_process_tank_alarms.assert_called_once()
            mock_process_circuit_load_alarms.assert_called_once()
            mock_process_bls_alarms.assert_called_once()
            mock_process_smartcraft_alarms.assert_called_once()

    def test_get_alarm_related_components_is_dc_alarm_alarm_channel_id(self):
        """
        Test get_alarm_related_components. ChannelId is reduced by 3 when it is a DC meter alarm
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_device_alarms"
        ) as mock_process_device_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_dc_meter_alarms"
        ) as mock_process_dc_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_ac_meter_alarms"
        ) as mock_process_ac_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_tank_alarms"
        ) as mock_process_tank_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_circuit_load_alarms"
        ) as mock_process_circuit_load_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_bls_alarms"
        ) as mock_process_bls_alarms, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.process_smartcraft_alarms"
        ) as mock_process_smartcraft_alarms, patch.object(
            alarm_service, "_is_dc_meter_alarm"
        ) as mock_is_dc_meter_alarm:
            alarm = N2KAlarm(
                external_alarm_id=1,
                channel_id=1234,
            )
            mock_is_dc_meter_alarm.return_value = True
            n2k_config = MagicMock()
            engine_config = MagicMock()
            alarm_service.get_alarm_related_components(
                alarm=alarm, config=n2k_config, engine_config=engine_config
            )
            mock_is_dc_meter_alarm.assert_called_once()
            mock_process_ac_alarms.assert_any_call(
                logger=ANY,
                resolved_alarm_channel_id=1231,
                config=ANY,
                affected_components=ANY,
                alarm=ANY,
                is_dc_alarm=ANY,
            )
            mock_process_device_alarms.assert_any_call(
                logger=ANY,
                resolved_alarm_channel_id=1231,
                config=ANY,
                affected_components=ANY,
                alarm=ANY,
                is_dc_alarm=ANY,
            )
            mock_process_dc_alarms.assert_any_call(
                logger=ANY,
                resolved_alarm_channel_id=1231,
                config=ANY,
                affected_components=ANY,
                alarm=ANY,
                is_dc_alarm=ANY,
            )
            mock_process_tank_alarms.assert_any_call(
                logger=ANY,
                resolved_alarm_channel_id=1231,
                config=ANY,
                affected_components=ANY,
                alarm=ANY,
                is_dc_alarm=ANY,
            )
            mock_process_circuit_load_alarms.assert_any_call(
                logger=ANY,
                resolved_alarm_channel_id=1231,
                config=ANY,
                affected_components=ANY,
                alarm=ANY,
                is_dc_alarm=ANY,
            )
            mock_process_bls_alarms.assert_any_call(
                logger=ANY,
                resolved_alarm_channel_id=1231,
                config=ANY,
                affected_components=ANY,
                alarm=ANY,
                is_dc_alarm=ANY,
            )
            mock_process_smartcraft_alarms.assert_not_called()

    def test_is_dc_meter_alarm_true(self):
        """
        Test if the alarm is a DC meter alarm. True
        """
        alarm = N2KAlarm(
            external_alarm_id=4,
            channel_id=1234,
        )

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        self.assertTrue(alarm_service._is_dc_meter_alarm(alarm))

    def test_is_dc_meter_alarm_false(self):
        """
        Test if the alarm is a DC meter alarm. False
        """
        alarm = N2KAlarm(
            external_alarm_id=0,
            channel_id=1234,
        )

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        self.assertFalse(alarm_service._is_dc_meter_alarm(alarm))

    def test_get_alarm_things(self):
        """
        Test get_alarm_things properly loops reference list and returns list of things.
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        calls = []

        def side_effect(references, config, things):
            calls.append(references)
            return references

        with patch.object(alarm_service, "_get_alarm_thing") as mock_get_alarm_thing:
            mock_get_alarm_thing.side_effect = side_effect
            references = ["ref1", "ref2", "ref3"]
            res = alarm_service.get_alarm_things(references, MagicMock())

            self.assertEqual(mock_get_alarm_thing.call_count, 3)
            self.assertGreater(len(res), 3)

    def test_get_alarm_thing_lights(self):
        """
        Test case for get_alarm_things,
        ensure light thing is added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        reference = ComponentReference(
            component_type=ComponentType.CIRCUIT,
            thing=MagicMock(remote_visibility=1, control_id=1),
        )

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.is_in_category"
        ) as mock_is_in_category:

            def is_in_category_side_effect(categories, category_name):
                if category_name == Constants.Lighting:
                    return True
                return False

            mock_is_in_category.side_effect = is_in_category_side_effect
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], "light.1")

    def test_get_alarm_thing_lights_visibility_0(self):
        """
        Test case for get_alarm_things,
        ensure light thing not added if visbility is 0
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        reference = ComponentReference(
            component_type=ComponentType.CIRCUIT, thing=MagicMock(remote_visibility=0)
        )

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.is_in_category"
        ) as mock_is_in_category:
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_is_in_category.assert_not_called()
            self.assertEqual(len(res), 0)

    def test_get_alarm_thing_bilge(self):
        """
        Test case for get_alarm_things,
        ensure bilge thing is added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        reference = ComponentReference(
            component_type=ComponentType.CIRCUIT,
            thing=MagicMock(remote_visibility=1, control_id=1),
        )

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.is_in_category"
        ) as mock_is_in_category:

            def is_in_category_side_effect(categories, category_name):
                if category_name == Constants.BilgePumps:
                    return True
                return False

            mock_is_in_category.side_effect = is_in_category_side_effect
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], "bilgePump.1")

    def test_get_alarm_thing_pump(self):
        """
        Test case for get_alarm_things,
        ensure pump thing is added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        reference = ComponentReference(
            component_type=ComponentType.CIRCUIT,
            thing=MagicMock(remote_visibility=1, control_id=1),
        )

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.is_in_category"
        ) as mock_is_in_category:

            def is_in_category_side_effect(categories, category_name):
                if category_name == Constants.Pumps:
                    return True
                return False

            mock_is_in_category.side_effect = is_in_category_side_effect
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], "pump.1")

    def test_get_alarm_thing_no_category(self):
        """
        Test case for get_alarm_things,
        ensure no thing is added when doesn't match any corresponding type
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        reference = ComponentReference(
            component_type=ComponentType.CIRCUIT,
            thing=MagicMock(remote_visibility=1, control_id=1),
        )

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.is_in_category"
        ) as mock_is_in_category:

            def is_in_category_side_effect(categories, category_name):
                return False

            mock_is_in_category.side_effect = is_in_category_side_effect
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            self.assertEqual(len(res), 0)

    def test_get_alarm_thing_recursive(self):
        """
        Test case for get_alarm_things,
        ensure with power thing. Recursive call to _get_alarm_thing is made
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        reference = ComponentReference(
            component_type=ComponentType.CIRCUIT,
            thing=MagicMock(remote_visibility=1, control_id=1),
        )

        real_func = alarm_service._get_alarm_thing
        call_counter = {"count": 0}

        def side_effect(reference, config, things):
            call_counter["count"] += 1
            if call_counter["count"] == 1:
                return real_func(reference, config, things)
            elif call_counter["count"] == 2:
                return ["MOCKED"]

        def is_in_category_side_effect(categories, category_name):
            if category_name == Constants.Power:
                return True
            return False

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.is_in_category"
        ) as mock_is_in_category, patch.object(
            alarm_service, "get_switch_thing"
        ) as mock_get_switch_thing, patch.object(
            alarm_service, "_get_alarm_thing"
        ) as mock_get_alarm_thing:
            mock_get_alarm_thing.side_effect = side_effect

            mock_get_switch_thing.return_value = MagicMock()
            mock_is_in_category.side_effect = is_in_category_side_effect
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_switch_thing.assert_called_once()
            self.assertEqual(len(res), 1)
            self.assertEqual(mock_get_alarm_thing.call_count, 2)
            self.assertEqual(res[0], "MOCKED")

    def test_get_alarm_thing_recursive_generic(self):
        """
        Test case for get_alarm_things,
        ensure with power thing. Generic circuit is added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        reference = ComponentReference(
            component_type=ComponentType.CIRCUIT,
            thing=MagicMock(remote_visibility=1, control_id=1),
        )

        real_func = alarm_service._get_alarm_thing
        call_counter = {"count": 0}

        def side_effect(reference, config, things):
            call_counter["count"] += 1
            if call_counter["count"] == 1:
                return real_func(reference, config, things)
            elif call_counter["count"] == 2:
                return ["MOCKED"]

        def is_in_category_side_effect(categories, category_name):
            if category_name == Constants.Power:
                return True
            return False

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.is_in_category"
        ) as mock_is_in_category, patch.object(
            alarm_service, "get_switch_thing"
        ) as mock_get_switch_thing, patch.object(
            alarm_service, "_get_alarm_thing"
        ) as mock_get_alarm_thing:
            mock_get_alarm_thing.side_effect = side_effect
            mock_get_switch_thing.return_value = None
            mock_is_in_category.side_effect = is_in_category_side_effect
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_switch_thing.assert_called_once()
            self.assertEqual(len(res), 1)
            self.assertEqual(mock_get_alarm_thing.call_count, 1)
            self.assertEqual(res[0], "genericCircuit.1")

    def test_get_alarm_things_dc_meter_battery(self):
        """
        Test case for get_alarm_things,
        ensure with DC thing.
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.dc_type = DCType.Battery
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.DCMETER,
            thing=thing,
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_combi_charger",
            side_effect=lambda dc_id, things, config: things,
        ) as mock_get_combi_charger:
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_combi_charger.assert_called_once()
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], "battery.1")

    def test_get_alarm_thing_dc_meter_non_battery(self):
        """
        Test case for get_alarm_things,
        ensure with DC thing.

        Non battery so it should not be added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.dc_type = DCType.Alternator
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.DCMETER,
            thing=thing,
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_combi_charger",
            side_effect=lambda dc_id, things, config: things,
        ) as mock_get_combi_charger:
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_combi_charger.assert_not_called()
            self.assertEqual(len(res), 0)

    def test_get_alarm_thing_ac_shorepower(self):
        """
        Test case for get_alarm_things,
        ensure with AC

        Shorepower link added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.ac_type = ACType.ShorePower
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.ACMETER,
            thing=thing,
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_combi_inverter",
            side_effect=lambda ac_id, things, config: things,
        ) as mock_get_combi_inverter:
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_combi_inverter.assert_called_once()
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], "shorePower.1")

    def test_get_alarm_thing_ac_inverter(self):
        """
        Test case for get_alarm_things,
        ensure with AC
        Inverter link added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.ac_type = ACType.Inverter
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.ACMETER,
            thing=thing,
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_combi_inverter",
            side_effect=lambda ac_id, things, config: things,
        ) as mock_get_combi_inverter:
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_combi_inverter.assert_called_once()
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], "inverter.1")

    def test_get_alarm_thing_ac_charger(self):
        """
        Test case for get_alarm_things,
        ensure with AC thing

        Charger link added
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.ac_type = ACType.Charger
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.ACMETER,
            thing=thing,
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_combi_inverter",
            side_effect=lambda ac_id, things, config: things,
        ) as mock_get_combi_inverter:
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_combi_inverter.assert_called_once()
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0], "charger.1")

    def test_get_alarm_thing_ac_other(self):
        """
        Test case for get_alarm_things,
        ensure with AC thing.

        No link added for invalid type
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.ac_type = ACType.Outlet
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.ACMETER,
            thing=thing,
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_combi_inverter",
            side_effect=lambda ac_id, things, config: things,
        ) as mock_get_combi_inverter:
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            mock_get_combi_inverter.assert_called_once()
            self.assertEqual(len(res), 0)

    def test_get_alarm_thing_tank_fuel(self):
        """
        Test case for get_alarm_things,
        ensure with tank thing.

        Fuel link added for fuel tank
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.tank_type = TankType.Fuel
        thing.id = 1
        reference = ComponentReference(
            component_type=ComponentType.TANK,
            thing=thing,
        )
        res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "fuelTank.1")

    def test_get_alarm_thing_tank_oil(self):
        """
        Test case for get_alarm_things,
        ensure with tank thing.

        Fuel link added for oil tank
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.tank_type = TankType.Oil
        thing.id = 1
        reference = ComponentReference(
            component_type=ComponentType.TANK,
            thing=thing,
        )
        res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "fuelTank.1")

    def test_get_alarm_thing_tank_fresh_water(self):
        """
        Test case for get_alarm_things,
        ensure with fresh water tank.

        Link to water tank
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.tank_type = TankType.FreshWater
        thing.id = 1
        reference = ComponentReference(
            component_type=ComponentType.TANK,
            thing=thing,
        )
        res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "waterTank.1")

    def test_get_alarm_thing_tank_waste_water(self):
        """
        Test case for get_alarm_things,
        ensure with waste water tank.

        Link to water tank
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.tank_type = TankType.WasteWater
        thing.id = 1
        reference = ComponentReference(
            component_type=ComponentType.TANK,
            thing=thing,
        )
        res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "waterTank.1")

    def test_get_alarm_thing_tank_black_water(self):
        """
        Test case for get_alarm_things,
        ensure with black water tank.

        Link to water tank
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.tank_type = TankType.BlackWater
        thing.id = 1
        reference = ComponentReference(
            component_type=ComponentType.TANK,
            thing=thing,
        )
        res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "waterTank.1")

    def test_get_alarm_thing_tank_livewell(self):
        """
        Test case for get_alarm_things,
        ensure with livewell tank.

        Link to water tank
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.tank_type = TankType.LiveWell
        thing.id = 1
        reference = ComponentReference(
            component_type=ComponentType.TANK,
            thing=thing,
        )
        res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "waterTank.1")

    def test_get_alarm_thing_marine_engine(self):
        """
        Test case for get_alarm_things,
        ensure with marine engine.

        Link to marine engine
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.MARINE_ENGINE,
            thing=thing,
        )
        res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], "marineEngine.1")

    def test_get_alarm_thing_marine_engine(self):
        """
        Test case for get_alarm_things,
        ensure with marine engine.

        Link to marine engine
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        thing = MagicMock()
        thing.instance = MagicMock()
        thing.instance.instance = 1
        reference = ComponentReference(
            component_type=ComponentType.INVERTERCHARGER,
            thing=thing,
        )
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.calculate_inverter_charger_instance"
        ) as mock_calculate_inverter_charger_instance:
            mock_calculate_inverter_charger_instance.return_value = 1234
            res = alarm_service._get_alarm_thing(reference, MagicMock(), things=[])
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0], "inverter.1234")
            self.assertEqual(res[1], "charger.1234")

    def test_get_switch_things_dc(self):
        """
        get_switch_things returns asociated component for DC
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        config = MagicMock()
        config.dc = {1: MagicMock()}
        switch = MagicMock(control_id=22)
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_associated_circuit"
        ) as mock_get_associated_circuit:
            mock_get_associated_circuit.return_value = MagicMock(control_id=22)
            res = alarm_service.get_switch_thing(config, switch)

            mock_get_associated_circuit.assert_called_once()
            self.assertEqual(res.component_type, ComponentType.DCMETER)
            self.assertEqual(res.thing, config.dc[1])

    def test_get_switch_things_ac(self):
        """
        get_switch_things returns asociated component for AC
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        config = MagicMock()
        config.ac = {1: MagicMock(line={1: MagicMock(id=123)})}
        switch = MagicMock(control_id=22)
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_associated_circuit"
        ) as mock_get_associated_circuit:
            mock_get_associated_circuit.return_value = MagicMock(control_id=22)
            res = alarm_service.get_switch_thing(config, switch)

            mock_get_associated_circuit.assert_called_once()
            self.assertEqual(res.component_type, ComponentType.ACMETER)
            self.assertEqual(res.thing, config.ac[1])

    def test_get_switch_things_tanks(self):
        """
        get_switch_things returns asociated component for Tanks
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        config = MagicMock()
        config.tank = {1: MagicMock(id=1)}
        switch = MagicMock(control_id=22)
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_associated_circuit"
        ) as mock_get_associated_circuit:
            mock_get_associated_circuit.return_value = MagicMock(control_id=22)
            res = alarm_service.get_switch_thing(config, switch)

            mock_get_associated_circuit.assert_called_once()
            self.assertEqual(res.component_type, ComponentType.TANK)
            self.assertEqual(res.thing, config.tank[1])

    def test_get_switch_things_none(self):
        """
        get_switch_things returns None for unassociated components
        """

        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )

        config = MagicMock()
        switch = MagicMock(control_id=22)
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.get_associated_circuit"
        ) as mock_get_associated_circuit:
            mock_get_associated_circuit.return_value = MagicMock(control_id=22)
            res = alarm_service.get_switch_thing(config, switch)

            mock_get_associated_circuit.assert_not_called()
            self.assertIsNone(res)

    def test_verify_alarm_things(self):
        """
        verfiy alarm things does not modify list if things are in empower system
        """
        mock_get_latest_empower_system = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_latest_empower_system,
            MagicMock(),
        )

        alarm_list = MagicMock()
        alarm_list.alarm = {1: MagicMock(things=["thing1", "thing2"])}
        mock_get_latest_empower_system.return_value = MagicMock(
            things=["thing1", "thing2", "thing3"]
        )
        res = alarm_service._verify_alarm_things(alarm_list)

        mock_get_latest_empower_system.assert_called_once()
        self.assertEqual(alarm_list, res)

    def test_verify_alarm_things_remove_thing(self):
        """
        verfiy alarm things removes things that are not in empower system
        """
        mock_get_latest_empower_system = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_latest_empower_system,
            MagicMock(),
        )

        alarm_list = MagicMock()
        alarm_list.alarm = {1: MagicMock(things=["thing1", "thing2"])}
        mock_get_latest_empower_system.return_value = MagicMock(
            things=["thing1", "thing3"]
        )
        res = alarm_service._verify_alarm_things(alarm_list)

        mock_get_latest_empower_system.assert_called_once()
        self.assertNotIn("thing2", res.alarm[1].things)

    def test_verify_alarm_things_remove_alarm(self):
        """
        verfiy alarm things removes alarm that has no things that are in empower system
        """
        mock_get_latest_empower_system = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_latest_empower_system,
            MagicMock(),
        )

        alarm_list = MagicMock()
        alarm_list.alarm = {1: MagicMock(things=["thing1", "thing2"])}
        mock_get_latest_empower_system.return_value = MagicMock(things=["thing3"])
        res = alarm_service._verify_alarm_things(alarm_list)

        mock_get_latest_empower_system.assert_called_once()
        self.assertNotIn(1, res.alarm)

    def test_verify_engine_alarm_things(self):
        """
        verfiy alarm engine alarm things does not modify list if engine things are in empower system
        """
        mock_get_latest_engine_list = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_latest_engine_list,
        )

        alarm_list = MagicMock()
        alarm_list.engine_alarms = {1: MagicMock(things=["thing1", "thing2"])}
        mock_get_latest_engine_list.return_value = MagicMock(
            engines=["thing1", "thing2", "thing3"]
        )
        res = alarm_service._verify_engine_alarm_things(alarm_list)

        mock_get_latest_engine_list.assert_called_once()
        self.assertEqual(alarm_list, res)

    def test_verify_engine_alarm_things_remove_thing(self):
        """
        verfiy alarm engine alarm things removes thing from list if engine things are not in empower system
        """
        mock_get_latest_engine_list = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_latest_engine_list,
        )

        alarm_list = MagicMock()
        alarm_list.engine_alarms = {1: MagicMock(things=["thing1", "thing2"])}
        mock_get_latest_engine_list.return_value = MagicMock(
            engines=["thing2", "thing3"]
        )
        res = alarm_service._verify_engine_alarm_things(alarm_list)

        mock_get_latest_engine_list.assert_called_once()
        self.assertNotIn("thing1", res.engine_alarms[1].things)
        self.assertIn("thing2", res.engine_alarms[1].things)

    def test_verify_engine_alarm_things_remove_alarm(self):
        """
        verfiy alarm engine alarm things removes alarm from list if no valid things in empower system
        """
        mock_get_latest_engine_list = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_latest_engine_list,
        )

        alarm_list = MagicMock()
        alarm_list.engine_alarms = {1: MagicMock(things=["thing1", "thing2"])}
        mock_get_latest_engine_list.return_value = MagicMock(engines=["thing3"])
        res = alarm_service._verify_engine_alarm_things(alarm_list)

        mock_get_latest_engine_list.assert_called_once()
        self.assertNotIn(1, res.engine_alarms)

    def test_post_process_alarm_configuration_alarm(self):
        """
        verify post process alarm configuration returns alarm if bls is None and severity is not SIO
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        alarm = MagicMock(severity=eSeverityType.SeverityCritical)
        bls = MagicMock()
        res = alarm_service.post_process_alarm_configuration(alarm, bls)

        self.assertEqual(res, alarm)

    def test_post_process_alarm_configuration_alarm_sio(self):
        """
        verify post process alarm configuration returns alarm if bls is None and severity is SIO
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        alarm = MagicMock(severity=eSeverityType.SeveritySIO)
        bls = MagicMock()
        res = alarm_service.post_process_alarm_configuration(alarm, bls)

        self.assertEqual(res, alarm)

    def test_post_process_alarm_configuration_alarm_bls(self):
        """
        verify post process alarm configuration returns alarm if bls is not None and severity is not SIO
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        alarm = MagicMock(severity=eSeverityType.SeverityCritical)
        bls = {1: MagicMock(alarm_channel=1)}
        res = alarm_service.post_process_alarm_configuration(alarm, bls)

        self.assertEqual(res, alarm)

    def test_post_process_alarm_configuration_alarm_bls_sio(self):
        """
        verify post process alarm configuration returns None if severity is SIO and BLS is not None
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        alarm = MagicMock(severity=eSeverityType.SeveritySIO, channel_id=1)
        bls = {1: MagicMock(alarm_channel=1)}
        res = alarm_service.post_process_alarm_configuration(alarm, bls)

        self.assertIsNone(res)

    def test_parse_alarm_list(self):
        """
        Verify parse alarm list returns a list of alarms for given input, calls parser for each alarm
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        alarm_json = {"Alarms": ["TESTALARMJSON", "ANOTHERTEST"]}
        with patch.object(alarm_service, "parse_alarm") as mock_parse_alarm:
            mock_parse_alarm.return_value = Alarm()
            res = alarm_service.parse_alarm_list(json.dumps(alarm_json))

            expected_calls = [call("TESTALARMJSON"), call("ANOTHERTEST")]
            mock_parse_alarm.assert_has_calls(expected_calls, any_order=False)
            self.assertEqual(len(res), 2)

    def test_parse_alarm_list_exception(self):
        """
        Verify parse alarm list raises exception for invalid input
        """
        try:
            alarm_service = AlarmService(
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
            )
            alarm_json = {"Alarms": ["TESTALARMJSON", "ANOTHERTEST"]}
            with patch.object(alarm_service, "parse_alarm") as mock_parse_alarm:
                mock_parse_alarm.return_value = Alarm()
                mock_parse_alarm.side_effect = Exception("Test Exception")
                res = alarm_service.parse_alarm_list(json.dumps(alarm_json))
                self.assertTrue(False)
        except:
            pass

    def test_parse_alarm(self):
        """
        Verify parse alarm returns an Alarm object for valid input
        """
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        alarm_json = {"TESTJSON"}
        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.map_enum_fields"
        ) as mock_map_enum_fields:
            alarm_service.parse_alarm(alarm_json)
            mock_map_enum_fields.assert_called_once()
            mock_map_fields.assert_called_once()

    def test_parse_alarm_exception(self):
        """
        Verify parse alarm raises an exception for invalid input
        """
        try:
            alarm_service = AlarmService(
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
                MagicMock(),
            )
            alarm_json = {"TESTJSON"}
            with patch(
                "N2KClient.n2kclient.services.alarm_service.alarm_service.map_fields"
            ) as mock_map_fields, patch(
                "N2KClient.n2kclient.services.alarm_service.alarm_service.map_enum_fields"
            ) as mock_map_enum_fields:
                mock_map_fields.side_effect = Exception("Test Exception")
                alarm_service.parse_alarm(alarm_json)
                mock_map_enum_fields.assert_called_once()
                mock_map_fields.assert_called_once()
                self.assertTrue(False)
        except:
            pass

    def test_process_engine_alarm_from_snapshots_discrete_status_1(self):
        """
        Verify that engine alarms are properly generated from snapshots
        """
        mock_get_engine_alarm = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_latest_engine_config = MagicMock()
        mock_latest_engine_config.devices = {1: MagicMock()}
        mock_get_engine_config.return_value = mock_latest_engine_config
        mock_set_engine_alarms = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_engine_config,
            mock_get_engine_alarm,
            MagicMock(),
            mock_set_engine_alarms,
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        snapshot_dict = {"Engines": {"marineEngine.1": {"DiscreteStatus1": 1}}}

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.generate_alarms_from_discrete_status"
        ) as mock_generate_alarms_from_discrete_status, patch.object(
            alarm_service, "_verify_engine_alarm_things"
        ) as mock_verify_engine_alarm_things:
            alarm_service.process_engine_alarm_from_snapshots(snapshot_dict)
            mock_generate_alarms_from_discrete_status.assert_called_once()
            mock_verify_engine_alarm_things.assert_called_once()
            mock_set_engine_alarms.assert_called_once()

    def test_process_engine_alarm_from_snapshots_discrete_status_2(self):
        """
        Verify that engine alarms are properly generated from snapshots
        """
        mock_get_engine_alarm = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_latest_engine_config = MagicMock()
        mock_latest_engine_config.devices = {1: MagicMock()}
        mock_get_engine_config.return_value = mock_latest_engine_config
        mock_set_engine_alarms = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_engine_config,
            mock_get_engine_alarm,
            MagicMock(),
            mock_set_engine_alarms,
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        snapshot_dict = {"Engines": {"marineEngine.1": {"DiscreteStatus2": 1}}}

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.generate_alarms_from_discrete_status"
        ) as mock_generate_alarms_from_discrete_status, patch.object(
            alarm_service, "_verify_engine_alarm_things"
        ) as mock_verify_engine_alarm_things:
            alarm_service.process_engine_alarm_from_snapshots(snapshot_dict)
            mock_generate_alarms_from_discrete_status.assert_called_once()
            mock_verify_engine_alarm_things.assert_called_once()
            mock_set_engine_alarms.assert_called_once()

    def test_process_engine_alarm_from_snapshots_discrete_status_both(self):
        """
        Verify that engine alarms are properly generated from snapshots
        """
        mock_get_engine_alarm = MagicMock()
        mock_get_engine_config = MagicMock()
        mock_latest_engine_config = MagicMock()
        mock_latest_engine_config.devices = {1: MagicMock()}
        mock_get_engine_config.return_value = mock_latest_engine_config
        mock_set_engine_alarms = MagicMock()
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_engine_config,
            mock_get_engine_alarm,
            MagicMock(),
            mock_set_engine_alarms,
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        snapshot_dict = {
            "Engines": {"marineEngine.1": {"DiscreteStatus1": 1, "DiscreteStatus2": 1}}
        }

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.generate_alarms_from_discrete_status"
        ) as mock_generate_alarms_from_discrete_status, patch.object(
            alarm_service, "_verify_engine_alarm_things"
        ) as mock_verify_engine_alarm_things:
            alarm_service.process_engine_alarm_from_snapshots(snapshot_dict)
            mock_verify_engine_alarm_things.assert_called_once()
            mock_set_engine_alarms.assert_called_once()
            discrete_status_1 = [
                call.kwargs.get("current_discrete_status1")
                for call in mock_generate_alarms_from_discrete_status.call_args_list
            ]
            assert 1 in discrete_status_1

            discrete_status_2 = [
                call.kwargs.get("current_discrete_status2")
                for call in mock_generate_alarms_from_discrete_status.call_args_list
            ]
            assert 1 in discrete_status_2

            engine_ids = [
                call.kwargs.get("engine_id")
                for call in mock_generate_alarms_from_discrete_status.call_args_list
            ]
            assert 1 in engine_ids

            discrete_status_word = [
                call.kwargs.get("discrete_status_word")
                for call in mock_generate_alarms_from_discrete_status.call_args_list
            ]
            assert 1 in discrete_status_word
            assert 2 in discrete_status_word

    def test_process_engine_alarm_from_snapshots_same_engine_list(self):
        """
        Verify that engine alarms not set or validated if alarm list doesn't change
        """
        mock_get_engine_config = MagicMock()
        mock_latest_engine_config = MagicMock()
        mock_latest_engine_config.devices = {1: MagicMock()}
        mock_get_engine_config.return_value = mock_latest_engine_config
        mock_set_engine_alarms = MagicMock()
        engine_alarm_list = EngineAlarmList()
        mock_get_engine_alarm = MagicMock(return_value=engine_alarm_list)
        alarm_service = AlarmService(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            mock_get_engine_config,
            mock_get_engine_alarm,
            MagicMock(),
            mock_set_engine_alarms,
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
        snapshot_dict = {"Engines": {"marineEngine.1": {}}}

        with patch(
            "N2KClient.n2kclient.services.alarm_service.alarm_service.generate_alarms_from_discrete_status"
        ) as mock_generate_alarms_from_discrete_status, patch.object(
            alarm_service, "_verify_engine_alarm_things"
        ) as mock_verify_engine_alarm_things:
            mock_generate_alarms_from_discrete_status.return_value = engine_alarm_list
            alarm_service.process_engine_alarm_from_snapshots(snapshot_dict)
            mock_generate_alarms_from_discrete_status.assert_not_called()
            mock_verify_engine_alarm_things.assert_not_called()
            mock_set_engine_alarms.assert_not_called()
