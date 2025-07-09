from reactivex import Observable
from reactivex import operators as ops


def round(decimal_places: int):
    def _round(obs: Observable[float]):
        return obs.pipe(ops.map(lambda val: float.__round__(val, decimal_places)))

    return _round
