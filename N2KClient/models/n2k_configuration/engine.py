import json
from .config_item import ConfigItem
from .instance import Instance
from enum import Enum
from ..constants import AttrNames


class EngineType(Enum):
    SmartCraft = 0
    NMEA2000 = 1


class EngineDevice(ConfigItem):
    instance: Instance
    software_id: str
    calibration_id: str
    serial_number: str
    ecu_serial_number: str
    engine_type: EngineType

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                **super().to_dict(),
                AttrNames.INSTANCE: self.instance.to_dict(),
                AttrNames.SOFTWARE_ID: self.software_id,
                AttrNames.CALIBRATION_ID: self.calibration_id,
                AttrNames.SERIAL_NUMBER: self.serial_number,
                AttrNames.ECU_SERIAL_NUMBER: self.ecu_serial_number,
                AttrNames.ENGINE_TYPE: self.engine_type.value,
            }
        except Exception as e:
            print(f"Error serializing EnginesDevice to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing EnginesDevice to JSON: {e}")
            return "{}"
