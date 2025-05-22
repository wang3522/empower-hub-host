import json
from ..constants import AttrNames


class ConfigItem:
    id: int
    name_utf8: str

    def to_dict(self) -> dict[str, str]:
        return {
            AttrNames.ID: self.id,
            AttrNames.NAMEUTF8: self.name_utf8,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
