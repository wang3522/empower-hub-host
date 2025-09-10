import json
from ...models.constants import AttrNames


class AlarmLimit:
    id: int
    enabled: bool
    on: float
    off: float

    def __init__(self, id=0, enabled=False, on=0.0, off=0.0):
        self.id = id
        self.enabled = enabled
        self.on = on
        self.off = off

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
