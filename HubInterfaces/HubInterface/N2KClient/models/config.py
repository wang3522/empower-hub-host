from typing import Optional
from .common_enums import SwitchType, PressureType, TankType, TemperatureType, ACLine, ACType

class Instance:
    value: bool
    valid: bool

class DataId:
    enabled: bool
    id: int    

class ConfigItem:
    id:int
    name:str

class MonitoringDevice(ConfigItem):
    instance: Instance
    circuit_id: Optional[DataId]
    switch_type: SwitchType
    circuit_name: Optional[str]
    address: int 

class Pressure(MonitoringDevice):
    pressure_type: PressureType
    atmospheric_pressure: bool

class Tank(MonitoringDevice):
    tank_type: TankType
    tank_capacity: float

class Temperature(MonitoringDevice):
    high_temperature: bool
    temperature_type:TemperatureType
    

class MeteringDevice(ConfigItem):
    instance: Instance
    
    line: ACLine
    output: bool
    nominal_voltage: int
    address: int
    
    warning_low: float
    warning_high: float

    show_voltage: bool
    show_current: bool

class AC(MeteringDevice):
    line: ACLine
    output: bool

    nominal_frequency: int

    ac_type: ACType

class DC(MeteringDevice):
    capacity: int
    show_state_of_charge: int
    show_temperature: int
    show_time_remainig: int

class InverterChargerDevice:
    model: int
    type: int
    sub_type: int
    inverter_instance: Instance
    inverter_ac_id: DataId
    inverter_circuit_id: DataId
    inverter_toggle_circuit_id: DataId
    charger_instance: Instance
    charger_ac_id: DataId
    charger_circuit_id: DataId
    charger_toggle_circuit_id: DataId
    battery_bank_1_id: DataId
    battery_bank_2_id: DataId
    battery_bank_3_id: DataId
    position_column: int
    position_row: int
    clustered: bool
    primary: bool
    primary_phase: int
    device_instance: int
    dipswitch: int
    channel_index: int

class Circuit:
    single_throw_id: DataId
    sequential_names_utf8: list[str]
    fuse_level: float
    running_current: float
    sy

class GNSS:

class Engines:

class BinaryLogicStates:

class Devices:

class N2KConfiguration:
    dcs: DC