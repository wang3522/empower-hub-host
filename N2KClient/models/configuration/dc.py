import json
from .metering_device import MeteringDevice
from ..constants import AttrNames


class DC(MeteringDevice):
    capacity: int
    show_state_of_charge: bool
    show_temperature: bool
    show_time_of_remaining: bool

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.CAPACITY: self.capacity,
                AttrNames.SHOW_STATE_OF_CHARGE: self.show_state_of_charge,
                AttrNames.SHOW_TEMPERATURE: self.show_temperature,
                AttrNames.SHOW_TIME_OF_REMAINING: self.show_time_of_remaining,
            }
        except Exception as e:
            print(f"Error serializing DC to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing DC to JSON: {e}")
            return "{}"
