from .engine import EngineDevice
from ..constants import AttrNames


class EngineConfiguration:
    devices: dict[int, EngineDevice]
    should_reset: bool

    def __init__(
        self, devices: dict[int, EngineDevice] = None, should_reset: bool = False
    ):
        self.devices = devices if devices is not None else {}
        self.should_reset = should_reset

    def to_dict(self) -> dict:
        try:
            return {
                AttrNames.ENGINE: {
                    engine_id: engine.to_dict()
                    for engine_id, engine in self.devices.items()
                },
                AttrNames.SHOULD_RESET: self.should_reset,
            }
        except Exception as e:
            print(f"Error serializing EngineConfiguration to dict: {e}")
            return {}

    def __eq__(self, other):
        if not isinstance(other, EngineConfiguration):
            return False
        return self.to_dict() == other.to_dict()
