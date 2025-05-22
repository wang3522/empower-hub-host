import json
from ..constants import AttrNames


class SequentialName:
    name: str

    def to_dict(self) -> dict[str, str]:
        return {
            AttrNames.NAME: self.name,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
