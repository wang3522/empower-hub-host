import json
from ..constants import AttrNames


class Instance:
    enabled: bool
    instance_: int

    def to_dict(self) -> dict[str, str]:
        return {
            AttrNames.ENABLED: self.enabled,
            AttrNames.INSTANCE_: self.instance_,
        }

    def to_json_string(self) -> str:
        return json.dumps(self.to_dict())
