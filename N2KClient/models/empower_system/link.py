class Link:
    id: str
    tags: list[str]

    def __init__(self, id: str, tags: list[str]):
        self.id = id
        self.tags = tags

    def to_json(self):
        return {"thing": self.id, "tags": self.tags}
