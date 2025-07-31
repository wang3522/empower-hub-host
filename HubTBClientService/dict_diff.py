"""
Dict diff functions
Contains the fucntions to merge two dictionaries and to see the difference between two dictionaries.
"""

def merge_two_dicts(x, y):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


# do diff and only send diff
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
