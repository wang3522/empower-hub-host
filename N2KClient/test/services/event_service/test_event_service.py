from logging import Logger
import unittest
from unittest.mock import MagicMock, patch

from N2KClient.n2kclient.models.common_enums import eEventType
from N2KClient.n2kclient.services.event_service.event_service import (
    EventService,
)

from N2KClient.n2kclient.services.event_service.event_parser.event_parser import (
    EventParser,
)


class EventServiceTest(unittest.TestCase):
    """Unit tests for the EventService"""

    def test_event_service_init(self):
        """
        Test the EventService initialization.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )

        self.assertIsNotNone(event_service)
        self.assertEqual(event_service._alarm_service, mock_alarm_service)
        self.assertEqual(event_service._config_service, mock_config_service)
        self.assertEqual(type(event_service._logger), Logger)
        self.assertEqual(type(event_service._event_parser), EventParser)

    def test_event_handler_engine_config_changed(self):
        """
        Test the event handler when the engine configuration is changed.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        mock_parsed_event = MagicMock(type=eEventType.EngineConfigChanged)
        with patch.object(EventParser, "parse_event", return_value=mock_parsed_event):
            event_service.event_handler("{}")
            mock_config_service.scan_marine_engine_config.assert_called_once()

    def test_event_handler_changed(self):
        """
        Test the event handler when the configuration is changed.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        mock_parsed_event = MagicMock(type=eEventType.ConfigChanged)
        with patch.object(EventParser, "parse_event", return_value=mock_parsed_event):
            event_service.event_handler("{}")
            mock_config_service.get_configuration.assert_called_once()

    def test_event_handler_alarm_added(self):
        """
        Test the event handler when the configuration alarm is added.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        mock_parsed_event = MagicMock(type=eEventType.AlarmAdded)
        with patch.object(EventParser, "parse_event", return_value=mock_parsed_event):
            event_service.event_handler("{}")
            mock_alarm_service.load_active_alarms.assert_called_once()

    def test_event_handler_alarm_removed(self):
        """
        Test the event handler when the configuration alarm is removed.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        mock_parsed_event = MagicMock(type=eEventType.AlarmRemoved)
        with patch.object(EventParser, "parse_event", return_value=mock_parsed_event):
            event_service.event_handler("{}")
            mock_alarm_service.load_active_alarms.assert_called_once()

    def test_event_handler_alarm_changed(self):
        """
        Test the event handler when the configuration alarm is changed.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        mock_parsed_event = MagicMock(type=eEventType.AlarmChanged)
        with patch.object(EventParser, "parse_event", return_value=mock_parsed_event):
            event_service.event_handler("{}")
            mock_alarm_service.load_active_alarms.assert_called_once()

    def test_event_handler_alarm_activated(self):
        """
        Test the event handler when the configuration alarm is activated.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        mock_parsed_event = MagicMock(type=eEventType.AlarmActivated)
        with patch.object(EventParser, "parse_event", return_value=mock_parsed_event):
            event_service.event_handler("{}")
            mock_alarm_service.load_active_alarms.assert_called_once()

    def test_event_handler_alarm_deactivated(self):
        """
        Test the event handler when the configuration alarm is deactivated.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        mock_parsed_event = MagicMock(type=eEventType.AlarmDeactivated)
        with patch.object(EventParser, "parse_event", return_value=mock_parsed_event):
            event_service.event_handler("{}")
            mock_alarm_service.load_active_alarms.assert_called_once()

    def test_event_handler_exception(self):
        """
        Test exception handling in event handler.
        """
        mock_alarm_service = MagicMock()
        mock_config_service = MagicMock()
        event_service = EventService(
            alarm_service=mock_alarm_service,
            config_service=mock_config_service,
        )
        with patch.object(
            EventParser, "parse_event", side_effect=Exception("Test Exception")
        ):
            res = event_service.event_handler("{}")
            self.assertEqual(res, None)
