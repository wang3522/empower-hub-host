from ...models.constants import AttrNames, JsonKeys
from ...models.common_enums import eEventType

EVENT_FIELD_MAP = {
    AttrNames.CONTENT: JsonKeys.CONTENT,
    AttrNames.ALARM_ITEM: JsonKeys.ALARM_ITEM,
    AttrNames.TIMESTAMP: JsonKeys.TIMESTAMP,
}

EVENT_ENUM_FIELD_MAP = {AttrNames.TYPE: (JsonKeys.TYPE, eEventType)}
