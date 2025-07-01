from N2KClient.models.n2k_configuration.engine import EngineDevice
from ..constants import AttrNames


class EngineConfiguration:
    devices: dict[int, EngineDevice]
    should_reset: bool

    def __init__(self, should_reset: bool = False):
        self.devices = {}
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
