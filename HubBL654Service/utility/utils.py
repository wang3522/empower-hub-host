# TO-DO - Make common util for TBClient and Hubl654service to use
telemetry_filter_patterns = [
    "marineEngine.\\d+.speed",
]

location_filter_pattern = r"gnss\.(.+?)\.loc"

class Constants:
    powerChannel = "p"
    levelChannel = "lvl"
    enabled = "enabled"
    chargerEnable = "ce"
    inverterEnable = "ie"

class ControlResult:
    """
    Class to represent the result of a control operation.
    """
    successful: bool
    error: str

    def __init__(self, successful: bool, error: str):
        self.successful = successful
        self.error = error

    def to_json(self):
        """
        Convert the ControlResult to a JSON object."""
        if self.successful:
            return {"successful": self.successful}
        else:
            return {
                "successful": self.successful,
                "error": self.error,
            }

def dict_diff(dict1, dict2):
    """_summary_:
        Merge logic for dictionaries. If new dict has new key, add that key and value to
        merged dictionary.

        If both dict values are tuples and not equal, set diff value for key to new dict to key.

        If both dict values are unequal dicts, and both dicts dict has key for "s" that are equal
    Args:
        dict1 (_type_): _description_
        dict2 (_type_): _description_

    Returns:
        _type_: _description_
    """
    diff = {}
    for key in dict2.keys():
        if (
            key not in dict1
            or (
                isinstance(dict1[key], tuple)
                and isinstance(dict2[key], tuple)
                and dict1[key][0] != dict2[key][0]
            )
            or (not isinstance(dict1[key], tuple) and dict1[key] != dict2[key])
        ):
            # If both dict1[key] and dict2[key] are a dictionary then check to see if the state
            # is the same. We do not consider the dictionaries different if only the
            # timestamp differ from each other
            if (
                key in dict1
                and isinstance(dict1[key], dict)
                and isinstance(dict2[key], dict)
            ):
                if "s" in dict1[key] and "s" in dict2[key]:
                    if dict1[key]["s"] == dict2[key]["s"]:
                        continue
            diff[key] = dict2[key]
    return diff