from typing import Any, Optional


class FactoryMetadata:
    serial_number: Optional[str] = None
    rt_firmware_version: Optional[str] = None
    mender_artifact_info: Optional[str] = None

    def __init__(self):
        self.serial_number = ""
        self.rt_firmware_version = ""
        self.mender_artifact_info = ""

    def to_dict(self) -> dict[str, Any]:
        factory_dict = {}
        if self.serial_number is not None:
            factory_dict["serial_number"] = self.serial_number
        if self.rt_firmware_version is not None:
            factory_dict["rt_firmware_version"] = self.rt_firmware_version
        if self.mender_artifact_info is not None:
            factory_dict["mender_artifact_info"] = self.mender_artifact_info
        return factory_dict
