from enum import Enum


class N2kDeviceType(str, Enum):
    DC = "dc"
    AC = "ac"
    TANK = "tank"
    AUDIO = "audio_sterio"
    ENGINE = "engine"
    INVERTERCHARGER = "inverter_charger"
    GENERATOR = "generator"
    CIRCUIT = "circuit"
    HVAC = "hvac"


class SwitchType(Enum):
    Not_Set = 0
    LatchOn = 1
    LatchOff = 2
    OnOff = 3
    Toggle = 4
    MomentaryOn = 5
    MomentaryOff = 6
    StepUp = 7
    StepDown = 8
    Forward = 9
    Reverse = 10
    DimLinearUp = 11
    DimLinearDown = 12
    DimExponentialUp = 13
    DimExponentialDown = 14
    SingleDimLinear = 15
    SingleDimExponential = 16
    Sequential1 = 17
    Sequential2 = 18
    Sequential3 = 19
    Sequential4 = 20
    Sequential5 = 21
    ToggleReverse = 22
    LogicAnd = 23
    LogicOr = 24
    LogicXor = 25
    SetAbsolute = 26
    SequentialUp = 27
    SequentialDown = 28
    SequentialLong1 = 29
    SequentialLong2 = 30
    SequentialLong3 = 31
    SequentialLong4 = 32
    SequentialLong5 = 33
