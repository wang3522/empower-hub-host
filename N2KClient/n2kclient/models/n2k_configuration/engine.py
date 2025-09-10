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

    def __init__(
        self,
        instance=None,
        software_id="",
        calibration_id="",
        serial_number="",
        ecu_serial_number="",
        engine_type=EngineType.SmartCraft,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.instance = instance if instance is not None else Instance()
        self.software_id = software_id
        self.calibration_id = calibration_id
        self.serial_number = serial_number
        self.ecu_serial_number = ecu_serial_number
        self.engine_type = engine_type

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
