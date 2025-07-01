import json
from .ac import AC


class ACMeter:
    line: dict[int, AC]

    def __init__(self):
        self.line = {}

    def to_dict(self) -> dict[str, dict[int, dict]]:
        try:
            return {
                "line": {
                    line_number: ac.to_dict() for line_number, ac in self.line.items()
                }
            }
        except Exception as e:
            print(f"Error serializing ACMeter to dict: {e}")
            return {"line": {}}

    def to_json_string(self) -> str:
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            print(f"Error serializing ACMeter to JSON: {e}")
            return "{}"
