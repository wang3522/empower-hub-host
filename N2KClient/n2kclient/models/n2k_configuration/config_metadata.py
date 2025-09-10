from ..constants import AttrNames


class ConfigMetadata:
    id: int
    name: str
    version: int
    config_file_version: int

    def __init__(self, id=0, name="", version=0, config_file_version=0):
        self.id = id
        self.name = name
        self.version = version
        self.config_file_version = config_file_version

    def to_dict(self) -> dict[str, str]:
        return {
            AttrNames.ID: str(self.id),
            AttrNames.NAME: self.name,
            AttrNames.VERSION: str(self.version),
            AttrNames.CONFIG_FILE_VERSION: str(self.config_file_version),
        }

    def __eq__(self, other):
        if not isinstance(other, ConfigMetadata):
            return False
        return self.to_dict() == other.to_dict()
