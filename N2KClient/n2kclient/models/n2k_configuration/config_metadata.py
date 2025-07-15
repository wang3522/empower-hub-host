from ..constants import AttrNames


class ConfigMetadata:
    id: int
    name: str
    version: int
    config_file_version: int

    def __init__(self):
        self.id = 0
        self.version = 0
        self.config_file_version = 0
        self.name = ""

    def to_dict(self) -> dict[str, str]:
        return {
            AttrNames.ID: str(self.id),
            AttrNames.NAME: self.name,
            AttrNames.VERSION: str(self.version),
            AttrNames.CONFIG_FILE_VERSION: str(self.config_file_version),
        }
