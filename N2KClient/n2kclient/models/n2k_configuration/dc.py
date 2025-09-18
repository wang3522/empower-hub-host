from enum import Enum
import json
from .metering_device import MeteringDevice
from ..constants import AttrNames


class DCType(Enum):
    Battery = 0
    Alternator = 1
    Convertor = 2
    Solar = 3
    Wind = 4
    Other = 5


class DC(MeteringDevice):
    capacity: int
    show_state_of_charge: bool
    show_temperature: bool
    show_time_of_remaining: bool

    dc_type: DCType

    def __init__(
        self,
        capacity=0,
        show_state_of_charge=False,
        show_temperature=False,
        show_time_of_remaining=False,
        dc_type=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.capacity = capacity
        self.show_state_of_charge = show_state_of_charge
        self.show_temperature = show_temperature
        self.show_time_of_remaining = show_time_of_remaining
        self.dc_type = dc_type

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.INSTANCE: self.instance.to_dict(),
                AttrNames.CAPACITY: self.capacity,
                AttrNames.SHOW_STATE_OF_CHARGE: self.show_state_of_charge,
                AttrNames.SHOW_TEMPERATURE: self.show_temperature,
                AttrNames.SHOW_TIME_OF_REMAINING: self.show_time_of_remaining,
                AttrNames.DC_TYPE: self.dc_type.value,
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
