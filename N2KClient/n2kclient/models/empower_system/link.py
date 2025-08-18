class Link:
    """
    Represents a link between different components in the Empower system.
    This class encapsulates the relationship between a thing and its associated tags,
    allowing for easy identification and management of linked components.

    (ex) a Circuit linked to a Tank or a Binary Logic State (BLS) linked to a Light Circuit.
        an AC linked to a binary logic state for shore power connected detection.

    Attributes:
        id: The unique identifier of the linked thing.
        tags: A list of tags associated with the link, providing context about the relationship.
    Methods:
        to_json: Converts the Link instance to a JSON-compatible dictionary.
    """

    id: str
    tags: list[str]

    def __init__(self, id: str, tags: list[str]):
        self.id = id
        self.tags = tags

    def to_json(self):
        """
        Convert the Link instance to a JSON-compatible dictionary.
        Returns:
            A dictionary representation of the Link instance.
        """
        return {"thing": self.id, "tags": self.tags}
