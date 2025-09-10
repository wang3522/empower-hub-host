import json
from ..common_enums import eSeverityType, eAlarmType, eStateType
from ..constants import AttrNames, Constants


class Alarm:
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

    def __init__(
        self,
        id=0,
        alarm_type=None,
        severity=None,
        current_state=None,
        channel_id=0,
        external_alarm_id=0,
        unique_id=0,
        valid=False,
        activated_time=0,
        acknowledged_time=0,
        cleared_time=0,
        name="",
        channel="",
        device="",
        title="",
        description="",
        czone_raw_alarm=b"",
        fault_action="",
        fault_type=0,
        fault_number=0,
    ):
        self.id = id
        self.alarm_type = alarm_type
        self.severity = severity
        self.current_state = current_state
        self.channel_id = channel_id
        self.external_alarm_id = external_alarm_id
        self.unique_id = unique_id
        self.valid = valid
        self.activated_time = activated_time
        self.acknowledged_time = acknowledged_time
        self.cleared_time = cleared_time
        self.name = name
        self.channel = channel
        self.device = device
        self.title = title
        self.description = description
        self.czone_raw_alarm = czone_raw_alarm
        self.fault_action = fault_action
        self.fault_type = fault_type
        self.fault_number = fault_number

    def to_dict(self) -> dict[str, str]:
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
                AttrNames.CZONE_RAW_ALARM: self.czone_raw_alarm,
                AttrNames.FAULT_ACTION: self.fault_action,
                AttrNames.FAULT_TYPE: self.fault_type,
                AttrNames.FAULT_NUMBER: self.fault_number,
            }

        except Exception as e:
            print(f"Error serializing Alarm to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing Alarm to JSON: {e}")
            return "{}"
