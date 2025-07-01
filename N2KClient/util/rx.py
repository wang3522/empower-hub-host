from collections import namedtuple
from typing import Any
import logging
import reactivex as rx
from reactivex import Observable
from reactivex import operators as ops
from datetime import datetime


def trace():
    def _trace(obs: Observable[Any]):

        id = 0
        logger = logging.getLogger("Trace")

        def trace_observable(observer, scheduler):
            id += 1

            def trace_log(msg: str):
                logger.info(f"Observable {id}: {msg}")

            def on_next(value):
                trace_log(f"on_next: {value}")
                observer.on_next(value)

            def on_error(error):
                trace_log(f"on_error: {error}")
                observer.on_error(error)

            def on_completed():
                trace_log("on_completed")
                observer.on_completed()

            obs.subscribe(on_next, on_error, on_completed)

        return rx.create(trace_observable)

    return _trace


def round(decimal_places: int):
    def _round(obs: Observable[float]):
        return obs.pipe(ops.map(lambda val: float.__round__(val, decimal_places)))

    return _round


CycleInfo = namedtuple("CycleInfo", ["start", "end"])


def create_on_off_cycles():

    def _eval_cycle(
        acc: CycleInfo,
        val: bool,
    ) -> CycleInfo:
        if val == True:
            if acc.start is None:
                return CycleInfo(datetime.now(), None)
            else:
                return CycleInfo(acc.start, None)
        else:
            if acc.start is not None:
                return CycleInfo(acc.start, datetime.now())
            else:
                return CycleInfo(None, None)

    def _create_cycles(obs: Observable[bool]) -> Observable[CycleInfo]:
        logger = logging.getLogger("Create Cycles")
        return obs.pipe(
            ops.scan(
                _eval_cycle,
                CycleInfo(start=None, end=None),
            ),
            ops.do_action(lambda cycle: logger.info(cycle)),
            ops.filter(lambda cycle: cycle.start is not None and cycle.end is not None),
        )

    return _create_cycles


def filter_location_consent(is_consent_granted: Observable[bool]):

    def _do_filtering(state: list[Any], is_consent_granted: bool):
        if is_consent_granted:
            return state
        else:
            return filter(lambda x: str(x.thing_type) != "location", state)

    def _filter_location_consent(obs: Observable[list[Any]]):

        return rx.combine_latest(obs, is_consent_granted).pipe(
            ops.map(lambda combined: _do_filtering(combined[0], combined[1]))
        )

    return _filter_location_consent
