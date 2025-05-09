from enum import Enum


class DeviceType(str, Enum):
    DC = "dc"
    AC = "ac"
    TANK = "tank"
    AUDIO = "audio_sterio"
    ENGINE = "engine"
    INVERTERCHARGER = "inverter_charger"
    GENERATOR = "generator"
    CIRCUIT = "circuit"
    HVAC = "hvac"

class PressureType(Enum):
    Atmospheric = 0
    Water = 1
    Steam = 2
    CompressedAir = 3
    Hydraulic = 4

class TankType(Enum):
    Fuel = 0
    FreshWater = 1
    WasteWater = 2
    LiveWell = 3
    Oil = 4
    BlackWater = 5

class TemperatureType(Enum):
    Sea = 0
    Outside = 1
    Inside = 2
    EngineRoom = 3
    MainCabin = 4
    LiveWell1 = 5
    BaitWell = 6
    Refrigeration = 7
    HeatingSystem = 8
    DewPoint = 9
    WindChillApparent = 10
    WindChillTheoretical = 11
    HeadIndex = 12
    Freezer = 13
    ExhaustGas = 14

class SwitchType(Enum):
    None = 0
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

class ACLine(Enum):
    Line1 = 0
    Line2 = 1
    Line3 = 2

class ACType(Enum):
    Unknown = 0
    Generator = 1    
    ShorePower = 2
    Inverter = 3
    Parallel = 4
    Charger = 5
    Outlet = 6