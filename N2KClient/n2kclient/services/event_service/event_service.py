import json
from ...models.common_enums import eEventType
import logging
from ..alarm_service.alarm_service import AlarmService
from ..config_service.config_service import ConfigService
from .event_parser.event_parser import EventParser


class EventService:
    """Service for handling events in the N2K client."""

    def __init__(self, alarm_service: AlarmService, config_service: ConfigService):
        self._alarm_service = alarm_service
        self._config_service = config_service
        self._logger = logging.getLogger(__name__)
        self._event_parser = EventParser()

    def event_handler(self, event_json: str):
        """
        Handle incoming event JSON string.
        Parses the JSON, determines the event type, and calls appropriate service methods.
        Args:
            event_json: JSON string representing the event data
        """
        try:
            event_dict = json.loads(event_json)
            parsed_event = self._event_parser.parse_event(event_dict)
            if parsed_event.type is eEventType.EngineConfigChanged:
                self._logger.info("Received EngineConfigChanged event")
                self._config_service.scan_marine_engine_config()
            if parsed_event.type is eEventType.ConfigChanged:
                self._logger.info("Received ConfigChanged event")
                self._config_service.get_configuration()
            if parsed_event.type in [
                eEventType.AlarmAdded,
                eEventType.AlarmRemoved,
                eEventType.AlarmChanged,
                eEventType.AlarmActivated,
                eEventType.AlarmDeactivated,
            ]:
                self._logger.info("Received Alarm event")
                self._alarm_service.load_active_alarms()
            self._logger.debug("Event received and processed")

        except Exception as e:
            self._logger.error(f"Failed to handle Event: {e}, raw: {event_json}")
            return
