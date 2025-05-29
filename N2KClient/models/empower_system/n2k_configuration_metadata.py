class N2kConfigurationMetadata:
    id: int
    version: int
    config_file_version: int
    name: str

    def __init__(self):
        self.id = 0
        self.version = 0
        self.config_file_version = 0
        self.name = ""
