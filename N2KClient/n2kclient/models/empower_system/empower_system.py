import logging
from typing import Union
from .thing import Thing
from ..constants import Constants
from ..n2k_configuration.config_metadata import ConfigMetadata


class EmpowerSystem:
    """
    Representation of the Empower system, containing a collection of things and metadata.
    This class serves as a container for various components of the Empower system, including power management devices, circuits, and other entities.
    It provides methods to add things and convert the system's state to a configuration dictionary.
    Creating instance of this object from raw Config data also sets subscriptions to N2kDevices for real-time updates of State data.
    Attributes:
        things: A dictionary mapping thing IDs to their corresponding Thing instances.
        logger: A logging.Logger instance for logging purposes.
        metadata: A dictionary containing metadata about the Empower system, such as configuration name and version.
    Methods:
        add_thing: Adds a new thing to the Empower system.
        to_config_dict: Converts the Empower system's state to a configuration dictionary.
        dispose: Cleans up resources associated with the Empower system.
    """

    things: dict[str, Thing]
    logger: logging.Logger
    metadata: dict[str, Union[str, int, float, bool]]

    def __init__(self, config_metadata: ConfigMetadata):
        self.things = {}
        self.metadata = {}
        if config_metadata is not None:
            if config_metadata.name is not None:
                self.metadata[f"{Constants.empower}:{Constants.configName}"] = (
                    config_metadata.name
                )
            if config_metadata.id is not None:
                self.metadata[f"{Constants.empower}:{Constants.configId}"] = (
                    config_metadata.id
                )

            if config_metadata.config_file_version is not None:
                self.metadata[f"{Constants.empower}:{Constants.configFileVersion}"] = (
                    config_metadata.config_file_version
                )

            if config_metadata.version is not None:
                self.metadata[f"{Constants.empower}:{Constants.version}"] = (
                    config_metadata.version
                )

    def add_thing(self, thing: Thing):
        """
        Add a thing to the Empower system.
        Args:
            thing: The Thing instance to add.
        """
        self.things[thing.id] = thing

    def to_config_dict(self) -> dict[str, Union[str, int, float, bool]]:
        """
        Convert the Empower system's state to a configuration dictionary.
        Returns:
            A dictionary representation of the Empower system's configuration.
        """
        return {
            "things": {
                thing_id: thing.to_config_dict()
                for thing_id, thing in self.things.items()
            },
            "metadata": self.metadata,
        }

    def __del__(self):
        """
        Clean up the Empower system instance when it is deleted.
        This method ensures that all things in the Empower system are disposed of properly.
        """
        self.dispose()

    def dispose(self):
        """
        Dispose of the Empower system instance.
        This method iterates through all things in the Empower system and calls their dispose method.
        It ensures that resources are released and any necessary cleanup is performed.
        """
        for disposable in self.things.values():
            disposable.dispose()
        self.things.clear()

    def __eq__(self, other):
        if not isinstance(other, EmpowerSystem):
            return False
        return self.to_config_dict() == other.to_config_dict()
