from .thing import Thing


class EngineList:
    engines: dict[str, Thing]
    should_reset: bool

    def __init__(self, should_reset):
        self.engines = {}
        self.should_reset = should_reset

    def add_engine(self, engine: Thing):
        self.engines[engine.id] = engine

    def to_config_dict(self) -> dict[str, bool]:
        return {
            engine_id: engine.to_config_dict()
            for [engine_id, engine] in self.engines.items()
        }

    def __del__(self):
        self.engines.clear()
