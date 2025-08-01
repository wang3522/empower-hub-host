import json
from ...models.constants import AttrNames


class AlarmLimit:
    id: int
    enabled: bool
    on: float
    off: float

    def to_dict(self) -> dict[str, str]:
        try:
            return {
                AttrNames.ID: self.id,
                AttrNames.ENABLED: self.enabled,
                AttrNames.ON: self.on,
                AttrNames.OFF: self.off,
            }
        except Exception as e:
            print(f"Error serializing AlarmLimit to dict: {e}")
            return {}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing AlarmLimit to JSON: {e}")
            return "{}"
