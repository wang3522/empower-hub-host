from .binary_logic_state import BinaryLogicState


class BLSAlarmMapping:
    alarm_channel: int
    bls: BinaryLogicState

    def __init__(self, alarm_channel: int, bls: BinaryLogicState):
        self.alarm_channel = alarm_channel
        self.bls = bls
