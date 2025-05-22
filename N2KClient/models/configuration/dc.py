import json
from .metering_device import MeteringDevice
from ..constants import AttrNames


class DC(MeteringDevice):
    capacity: int
    show_state_of_charge: bool
    show_temperature: bool
    show_time_of_remaining: bool

    def to_dict(self) -> dict[str, str]:
        return {
            **super().to_dict(),
            AttrNames.CAPACITY: self.capacity,
            AttrNames.SHOW_STATE_OF_CHARGE: self.show_state_of_charge,
            AttrNames.SHOW_TEMPERATURE: self.show_temperature,
            AttrNames.SHOW_TIME_OF_REMAINING: self.show_time_of_remaining,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
