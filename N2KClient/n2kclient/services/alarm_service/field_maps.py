from ...models.constants import AttrNames, JsonKeys
from ...models.common_enums import eAlarmType, eSeverityType, eStateType

ALARM_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.CHANNEL_ID: JsonKeys.CHANNEL_ID,
    AttrNames.EXTERNAL_ALARM_ID: JsonKeys.EXTERNAL_ALARM_ID,
    AttrNames.UNIQUE_ID: JsonKeys.UNIQUE_ID,
    AttrNames.VALID: JsonKeys.VALID,
    AttrNames.ACTIVATED_TIME: JsonKeys.ACTIVATED_TIME,
    AttrNames.ACKNOWLEDGED_TIME: JsonKeys.ACKNOWLEDGED_TIME,
    AttrNames.CLEARED_TIME: JsonKeys.CLEARED_TIME,
    AttrNames.NAME: JsonKeys.NAME,
    AttrNames.CHANNEL: JsonKeys.CHANNEL,
    AttrNames.DEVICE: JsonKeys.DEVICE,
    AttrNames.TITLE: JsonKeys.TITLE,
    AttrNames.DESCRIPTION: JsonKeys.DESCRIPTION,
    AttrNames.CZONE_RAW_ALARM: JsonKeys.CZONE_RAW_ALARM,
    AttrNames.FAULT_ACTION: JsonKeys.FAULT_ACTION,
    AttrNames.FAULT_TYPE: JsonKeys.FAULT_TYPE,
    AttrNames.FAULT_NUMBER: JsonKeys.FAULT_NUMBER,
}

ALARM_ENUM_FIELD_MAP = {
    AttrNames.ALARM_TYPE: (JsonKeys.ALARM_TYPE, eAlarmType),
    AttrNames.SEVERITY: (JsonKeys.SEVERITY, eSeverityType),
    AttrNames.CURRENT_STATE: (JsonKeys.CURRENT_STATE, eStateType),
}
