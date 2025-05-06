from typing import Any


class N2KChannel:
    id: int
    pgn_number: int
    data: str

    def __init__(self, id: int, pgn_number: int, data: str):
        self.id = id
        self.pgn_number = pgn_number
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        return {"pgnNumber": self.pgn_number, "data": self.data}
