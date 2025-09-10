import unittest
from unittest.mock import MagicMock, patch
from N2KClient.n2kclient.services.event_service.event_parser.event_parser import (
    EventParser,
)
from N2KClient.n2kclient.models.event import Event


class EventParserTest(unittest.TestCase):
    """Unit tests for the EventParser"""

    def test_parse_event(self):
        """
        Test the parsing of an event.
        """

        event_json = MagicMock()

        event_parser = EventParser()
        with patch(
            "N2KClient.n2kclient.services.event_service.event_parser.event_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.event_service.event_parser.event_parser.map_enum_fields"
        ) as mock_map_enum_fields:
            res = event_parser.parse_event(event_json)
            mock_map_enum_fields.assert_called_once()
            mock_map_fields.assert_called_once()
            self.assertEqual(type(res), Event)

    def test_parse_event_exception(self):
        """
        Test exception handling in event parser.
        """
        event_json = MagicMock()
        event_parser = EventParser()
        with patch(
            "N2KClient.n2kclient.services.event_service.event_parser.event_parser.map_fields"
        ) as mock_map_fields, patch(
            "N2KClient.n2kclient.services.event_service.event_parser.event_parser.map_enum_fields"
        ) as mock_map_enum_fields:
            mock_map_fields.side_effect = Exception("Test Exception")
            res = event_parser.parse_event(event_json)
            self.assertIsNone(res)
