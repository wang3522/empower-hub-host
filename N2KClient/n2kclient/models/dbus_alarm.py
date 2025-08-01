import json
from .common_enums import eAlarmType, eSeverityType, eStateType
from .constants import AttrNames


class Dbus_Alarm:
    id: int
    alarm_type: eAlarmType
    severity: eSeverityType
    current_state: eStateType
    channel_id: int
    external_alarm_id: int
    unique_id: int
    valid: bool
    activated_time: int
    acknowledged_time: int
    cleared_time: int
    name: str
    channel: str
    device: str
    title: str
    description: str
    czone_raw_alarm: bytes
    fault_action: str
    fault_type: int
    fault_number: int

    def to_dict(self):
        try:
            return {
                AttrNames.ID: self.id,
                AttrNames.ALARM_TYPE: self.alarm_type.value,
                AttrNames.SEVERITY: self.severity.value,
                AttrNames.CURRENT_STATE: self.current_state.value,
                AttrNames.CHANNEL_ID: self.channel_id,
                AttrNames.EXTERNAL_ALARM_ID: self.external_alarm_id,
                AttrNames.UNIQUE_ID: self.unique_id,
                AttrNames.VALID: self.valid,
                AttrNames.ACTIVATED_TIME: self.activated_time,
                AttrNames.ACKNOWLEDGED_TIME: self.acknowledged_time,
                AttrNames.CLEARED_TIME: self.cleared_time,
                AttrNames.NAME: self.name,
                AttrNames.CHANNEL: self.channel,
                AttrNames.DEVICE: self.device,
                AttrNames.TITLE: self.title,
                AttrNames.DESCRIPTION: self.description,
                AttrNames.CZONE_RAW_ALARM: (
                    self.czone_raw_alarm.hex() if self.czone_raw_alarm else None
                ),
                AttrNames.FAULT_ACTION: self.fault_action,
                AttrNames.FAULT_TYPE: self.fault_type,
                AttrNames.FAULT_NUMBER: self.fault_number,
            }
        except Exception as e:
            print(f"Error serializing Alarm to dict: {e}")
            return {}

    def to_json_string(self):
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Alarm to JSON string: {e}")
            return ""
