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
    DEVICE = "device"
    UNKNOWN = "unknown"
    GNSS = "gnss"
    BINARY_LOGIC_STATE = "binary_logic_state"


class ConnectionType(str, Enum):
    UNKNOWN = "unknown"
    NONE = "none"
    ETHERNET = "ethernet"
    WIFI = "wifi"
    CELLULAR = "cellular"


class BatteryStatus(str, Enum):
    CHARGED = "charged"
    CHARGING = "charging"
    DISCHARGING = "discharging"


class MarineEngineStatus(str, Enum):
    RUNNING = "running"
    OFF = "off"


class EngineState(Enum):
    Dead = 0
    Stall = 1
    Crank = 2
    Run = 3
    PowerOff = 4


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


class Unit(str, Enum):
    NONE = "none"
    PERCENT = "percent"

    PRESSURE_KILOPASCAL = "pressure:kilopascal"
    PRESSURE_POUND_PER_SQUARE_INCH = "pressure:psi"
    PRESSURE_INCH_OF_MERCURY = "pressure:hg"
    PRESSURE_BAR = "pressure:bar"
    PRESSURE_PASCAL = "pressure:pa"

    TEMPERATURE_FAHRENHEIT = "temperature:fahrenheit"
    TEMPERATURE_CELSIUS = "temperature:celsius"
    TEMPERATURE_KELVIN = "temperature:kelvin"

    ENERGY_AMP = "energy:amp"
    ENERGY_VOLT = "energy:volt"
    ENERGY_WATT = "energy:watt"
    ENERGY_KILOWATT = "energy:kilowatt"
    ENERGY_AMP_HOURS = "energy:ampHours"

    VOLUME_LITRE = "volume:liter"
    VOLUME_GALLON = "volume:gallon"

    TIME_SECOND = "time:second"
    TIME_MINUTE = "time:minute"
    TIME_HOUR = "time:hour"

    TIMESTAMP_EPOCH = "timestamp:epoch"
    TIMESTAMP_ISO = "timestamp:iso"

    SIGNAL_DECIBEL = "signal:dB"
    SIGNAL_DECIBEL_MILLIWATT = "signal:dBm"

    LINEAR_SPEED_KILOMETERS_PER_HOUR = "linearSpeed:kph"
    LINEAR_SPEED_MILES_PER_HOUR = "linearSpeed:mph"
    LINEAR_SPEED_KNOT = "linearSpeed:knot"
    LINEAR_SPEED_METERS_PER_SECOND = "linearSpeed:metersPerSecond"

    ROTATIONAL_SPEED_REVOLUTIONS_PER_MINUTE = "rotationalSpeed:rpm"

    FREQUENCY_HERTZ = "frequency:hertz"

    GEOJSON_POINT = "geojson:point"
    GEOJSON_POLYGON = "geojson:polygon"

    DISTANCE_FEET = "distance:feet"
    DISTANCE_METER = "distance:meter"
    DISTANCE_MILE = "distance:mile"
    DISTANCE_KILOMETER = "distance:km"
    DISTANCE_NAUTICAL_MILE = "distance:nmi"

    FUEL_RATE_CUBIC_METER_PER_HOUR = "fuelRate:cubicMeterPerHour"


class ChannelType(str, Enum):
    UNKNOWN = "unknown"
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    POINT = "point"
    POLYGON = "polygon"


class ThingType(str, Enum):
    GENERIC_CIRCUIT = "genericCircuit"
    UNKNOWN = "unknown"
    LIGHT = "light"
    BILGE_PUMP = "bilgePump"
    PUMP = "pump"
    BATTERY = "battery"
    MARINE_ENGINE = "marineEngine"
    CLIMATE = "climate"
    AUDIO = "audio"
    LOCATION = "location"
    WATER_TANK = "waterTank"
    FUEL_TANK = "fuelTank"
    SHORE_POWER = "shorePower"
    INVERTER = "inverter"
    CHARGER = "charger"
    HUB = "hub"
    GNSS = "gnss"


class WaterTankType(str, Enum):
    BLACKWATER = "blackWater"
    WASTEWATER = "wasteWater"
    FRESHWATER = "freshWater"


class ACMeterStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    Voltage = "Voltage"
    Current = "Current"
    Frequency = "Frequency"
    Power = "Power"


class DCMeterStates(str, Enum):
    Voltage = "Voltage"
    Current = "Current"
    StateOfCharge = "StateOfCharge"
    Temperature = "Temperature"
    CapacityRemaining = "CapacityRemaining"
    TimeRemaining = "TimeRemaining"
    TimeToCharge = "TimeToCharge"
    ComponentStatus = "ComponentStatus"


class CombiChargerStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    ChargerEnable = "ChargerEnable"
    ChargerState = "ChargerState"


class CircuitStates(str, Enum):
    Current = "Current"
    Level = "Level"
    IsOffline = "IsOffline"


class BLSStates(str, Enum):
    States = "States"


class ClimateStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    Mode = "Mode"
    SetPoint = "SetPoint"
    AmbientTemperature = "AmbientTemperature"
    FanSpeed = "FanSpeed"
    FanMode = "FanMode"


class GNSSStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    FixType = "FixType"
    LatitudeDeg = "LatitudeDeg"
    LongitudeDeg = "LongitudeDeg"
    Sog = "Sog"


class HubStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    EthernetInternetConnectivity = "EthernetInternetConnectivity"
    WifiInternetConnectivity = "WifiInternetConnectivity"
    WifiSignalStrength = "WifiSignalStrength"
    WifiSsid = "WifiSsid"
    WifiType = "WifiType"
    CellularInternetConnectivity = "CellularInternetConnectivity"
    CellularType = "CellularType"
    CellularSignalStrengthDbm = "CellularSignalStrengthDbm"
    CellularSimIccid = "CellularSimIccid"
    CellularSimEid = "CellularSimEid"


class CombiInverterStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    InverterEnable = "InverterEnable"
    InverterState = "InverterState"


class MarineEngineStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    Speed = "Speed"
    EngineHours = "EngineHours"
    CoolantTemperature = "CoolantTemperature"
    CoolantPressure = "CoolantPressure"
    OilPressure = "OilPressure"
    EngineState = "EngineState"


class TankStates(str, Enum):
    ComponentStatus = "ComponentStatus"
    Level = "Level"
    LevelPercent = "LevelPercent"


class ChargerStatus(str, Enum):
    ABSORPTION = "Absorption"
    BULK = "Bulk"
    CONSTANTVI = "ConstantVI"
    NOTCHARGING = "NotCharging"
    EQUALIZE = "Equalize"
    OVERCHARGE = "Overcharge"
    FLOAT = "Float"
    NOFLOAT = "NoFloat"
    FAULT = "Fault"
    DISABLED = "Disabled"


class InverterStatus(str, Enum):
    INVERTING = "Inverting"
    AC_PASSTHRU = "AcPassthru"
    LOAD_SENSE = "LoadSense"
    FAULT = "Fault"
    DISABLED = "Disabled"
    CHARGING = "Charging"
    ENERGY_SAVING = "EnergySaving"
    ENERGY_SAVING2 = "EnergySaving2"
    SUPPORTING = "Supporting"
    SUPPORTING2 = "Supporting2"
    ERROR = "Error"
    DATA_NOT_AVAILABLE = "DataNotAvailable"


class ThrowType(str, Enum):
    SingleThrow = "SingleThrow"
    DoubleThrow = "DoubleThrow"


class ControlRequest(str, Enum):
    Activate = "Activate"
    Release = "Release"
    Ping = "Ping"
    SetAbsolute = "SetAbsolute"
