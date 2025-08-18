from .thing import Thing


class EngineList:
    """
    Container for multiple Engine instances.
    This class manages a collection of engine devices, allowing for easy access and manipulation of engine data

    Attributes:
        engines: A dictionary mapping engine IDs to their corresponding Thing instances.
        should_reset: A boolean flag indicating whether the engine list should reset/remove existing cloud engines from list on update.

    Methods:
        add_engine: Adds a new engine to the list.
        to_config_dict: Converts the engine list to a configuration dictionary.
        dispose: Cleans up resources associated with the engine list.
    """

    engines: dict[str, Thing]
    should_reset: bool

    def __init__(self, should_reset):
        self.engines = {}
        self.should_reset = should_reset

    def add_engine(self, engine: Thing):
        """
        Add an engine to the EngineList.
        Args:
            engine: The Thing instance representing the engine to add.
        """
        self.engines[engine.id] = engine

    def to_config_dict(self) -> dict[str, bool]:
        """
        Convert the EngineList to a dictionary representation.
        Returns:
            A dictionary where keys are engine IDs and values are their corresponding configuration dictionaries.
        """
        return {
            engine_id: engine.to_config_dict()
            for [engine_id, engine] in self.engines.items()
        }

    def __del__(self):
        """
        Clean up the EngineList instance when it is deleted.
        This method ensures that all engines in the list are disposed of properly.
        """
        self.dispose()

    def dispose(self):
        """
        Dispose of the EngineList instance.
        This method iterates through all engines in the list and calls their dispose method.
        It ensures that resources are released and any necessary cleanup is performed.
        """
        for disposable in self.engines.values():
            disposable.dispose()
        self.engines.clear()
