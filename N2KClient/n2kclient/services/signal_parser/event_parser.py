import json
import logging
from typing import Optional

from ...models.constants import Constants
from ...models.event import Event
from ...util.common_utils import map_fields, map_enum_fields
from .field_maps import EVENT_FIELD_MAP, EVENT_ENUM_FIELD_MAP


class EventParser:
    _logger = logging.getLogger(
        f"{Constants.DBUS_N2K_CLIENT}: {Constants.EVENT_PARSER}"
    )

    def parse_event(self, event_json: str) -> Optional[Event]:
        """
        Parses a JSON event into an Event object.
        :param event_json: JSON representation of the event.
        :return: Event object.
        """
        try:
            event = Event()
            map_fields(event_json, event, EVENT_FIELD_MAP)
            map_enum_fields(self._logger, event_json, event, EVENT_ENUM_FIELD_MAP)
            return event

        except Exception as e:
            self._logger.error(f"Failed to parse event: {e}")
            return None
