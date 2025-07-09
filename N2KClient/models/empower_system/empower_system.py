import logging
from typing import Union
from .thing import Thing
from ..constants import Constants
from N2KClient.models.n2k_configuration.config_metadata import ConfigMetadata


class EmpowerSystem:
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
        self.things[thing.id] = thing

    def to_config_dict(self) -> dict[str, Union[str, int, float, bool]]:
        return {
            "things": {
                thing_id: thing.to_config_dict()
                for thing_id, thing in self.things.items()
            },
            "metadata": self.metadata,
        }

    def __del__(self):
        for disposable in self.things.values():
            disposable.dispose()
