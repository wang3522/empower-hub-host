from reactivex import Observable
from reactivex import operators as ops


def round_float(decimal_places: int):
    """Round float values in an Observable stream to a specified number of decimal places."""

    def _round(obs: Observable[float]):
        return obs.pipe(
            ops.map(lambda val: float.__round__(float(val), decimal_places))
        )

    return _round
