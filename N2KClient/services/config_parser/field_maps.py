from N2KClient.models.common_enums import SwitchType
from N2KClient.models.n2k_configuration.ac import ACLine, ACType
from N2KClient.models.n2k_configuration.circuit import (
    CircuitType,
    ControlType,
)
from N2KClient.models.n2k_configuration.device import DeviceType
from N2KClient.models.n2k_configuration.engine import EngineType
from N2KClient.models.n2k_configuration.pressure import (
    PressureType,
)
from N2KClient.models.n2k_configuration.tank import TankType
from N2KClient.models.n2k_configuration.ui_relationship_msg import (
    ItemType,
    RelationshipType,
)
from N2KClient.models.constants import AttrNames, JsonKeys

CIRCUIT_LOAD_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.CHANNEL_ADDRESS: JsonKeys.CHANNEL_ADDRESS,
    AttrNames.FUSE_LEVEL: JsonKeys.FUSE_LEVEL,
    AttrNames.RUNNING_CURRENT: JsonKeys.RUNNING_CURRENT,
    AttrNames.SYSTEM_ON_CURRENT: JsonKeys.SYSTEM_ON_CURRENT,
    AttrNames.FORCE_ACKNOWLEDGE_ON: JsonKeys.FORCE_ACKNOWLEDGE_ON,
    AttrNames.LEVEL: JsonKeys.LEVEL,
    AttrNames.IS_SWITCHED_MODULE: JsonKeys.IS_SWITCHED_MODULE,
}

CIRCUIT_LOAD_ENUM_FIELD_MAP = {
    AttrNames.CONTROL_TYPE: (JsonKeys.CONTROL_TYPE, ControlType),
}

DATA_ID_FIELD_MAP = {
    AttrNames.ENABLED: JsonKeys.ENABLED,
    AttrNames.ID: JsonKeys.ID,
}

INSTANCE_FIELD_MAP = {
    AttrNames.ENABLED: JsonKeys.ENABLED,
    AttrNames.INSTANCE: JsonKeys.INSTANCE,
}

SEQUENTIAL_NAMES_FIELD_MAP = {
    AttrNames.NAME: JsonKeys.NAME,
}

GNSS_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.IS_EXTERNAL: JsonKeys.IS_EXTERNAL,
}

CATEGORY_FIELD_MAP = {
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.ENABLED: JsonKeys.ENABLED,
    AttrNames.INDEX: JsonKeys.INDEX,
}

CIRCUIT_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.HAS_COMPLEMENT: JsonKeys.HAS_COMPLEMENT,
    AttrNames.DISPLAY_CATEGORIES: JsonKeys.DISPLAY_CATEGORIES,
    AttrNames.MIN_LEVEL: JsonKeys.MIN_LEVEL,
    AttrNames.MAX_LEVEL: JsonKeys.MAX_LEVEL,
    AttrNames.NONVISIBLE_CIRCUIT: JsonKeys.NONVISIBLE_CIRCUIT,
    AttrNames.DIMSTEP: JsonKeys.DIMSTEP,
    AttrNames.STEP: JsonKeys.STEP,
    AttrNames.DIMMABLE: JsonKeys.DIMMABLE,
    AttrNames.LOAD_SMOOTH_START: JsonKeys.LOAD_SMOOTH_START,
    AttrNames.SEQUENTIAL_STATES: JsonKeys.SEQUENTIAL_STATES,
    AttrNames.CONTROL_ID: JsonKeys.CONTROL_ID,
    AttrNames.DC_CIRCUIT: JsonKeys.DC_CIRCUIT,
    AttrNames.AC_CIRCUIT: JsonKeys.AC_CIRCUIT,
    AttrNames.PRIMARY_CIRCUIT_ID: JsonKeys.PRIMARY_CIRCUIT_ID,
    AttrNames.REMOTE_VISIBILITY: JsonKeys.REMOTE_VISIBILITY,
    AttrNames.SWITCH_STRING: JsonKeys.SWITCH_STRING,
    AttrNames.SYSTEMS_ON_AND: JsonKeys.SYSTEMS_ON_AND,
    AttrNames.SINGLE_THROW_ID: JsonKeys.SINGLE_THROW_ID,
}

CIRCUIT_ENUM_FIELD_MAP = {
    AttrNames.CIRCUIT_TYPE: (JsonKeys.CIRCUIT_TYPE, CircuitType),
    AttrNames.SWITCH_TYPE: (JsonKeys.SWITCH_TYPE, SwitchType),
}


DC_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.OUTPUT: JsonKeys.OUTPUT,
    AttrNames.NOMINAL_VOLTAGE: JsonKeys.NOMINAL_VOLTAGE,
    AttrNames.ADDRESS: JsonKeys.ADDRESS,
    AttrNames.SHOW_VOLTAGE: JsonKeys.SHOW_VOLTAGE,
    AttrNames.SHOW_CURRENT: JsonKeys.SHOW_CURRENT,
    AttrNames.CAPACITY: JsonKeys.CAPACITY,
    AttrNames.SHOW_TEMPERATURE: JsonKeys.SHOW_TEMPERATURE,
    AttrNames.SHOW_TIME_OF_REMAINING: JsonKeys.SHOW_TIME_OF_REMAINING,
    AttrNames.SHOW_STATE_OF_CHARGE: JsonKeys.SHOW_STATE_OF_CHARGE,
}

AC_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.OUTPUT: JsonKeys.OUTPUT,
    AttrNames.NOMINAL_VOLTAGE: JsonKeys.NOMINAL_VOLTAGE,
    AttrNames.ADDRESS: JsonKeys.ADDRESS,
    AttrNames.SHOW_VOLTAGE: JsonKeys.SHOW_VOLTAGE,
    AttrNames.SHOW_CURRENT: JsonKeys.SHOW_CURRENT,
    AttrNames.OUTPUT: JsonKeys.OUTPUT,
    AttrNames.NOMINAL_FREQUENCY: JsonKeys.NOMINAL_FREQUENCY,
}


AC_EMUM_FIELD_MAP = {
    AttrNames.LINE: (JsonKeys.LINE, ACLine),
    AttrNames.AC_TYPE: (JsonKeys.AC_TYPE, ACType),
}

TANK_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.CIRCUIT_NAME_UTF8: JsonKeys.CIRCUIT_NAME_UTF8,
    AttrNames.ADDRESS: JsonKeys.ADDRESS,
    AttrNames.TANK_CAPACITY: JsonKeys.TANK_CAPACITY,
}

TANK_ENUM_FIELD_MAP = {
    AttrNames.TANK_TYPE: (JsonKeys.TANK_TYPE, TankType),
    AttrNames.SWITCH_TYPE: (JsonKeys.SWITCH_TYPE, SwitchType),
}

INVERTER_CHARGER_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.MODEL: JsonKeys.MODEL,
    AttrNames.TYPE: JsonKeys.TYPE,
    AttrNames.SUB_TYPE: JsonKeys.SUB_TYPE,
    AttrNames.POSITION_COLUMN: JsonKeys.POSITION_COLUMN,
    AttrNames.POSITION_ROW: JsonKeys.POSITION_ROW,
    AttrNames.CLUSTERED: JsonKeys.CLUSTERED,
    AttrNames.PRIMARY: JsonKeys.PRIMARY,
    AttrNames.PRIMARY_PHASE: JsonKeys.PRIMARY_PHASE,
    AttrNames.DEVICE_INSTANCE: JsonKeys.DEVICE_INSTANCE,
}

INVERTER_CHARGER_DATA_ID_FIELD_MAP = {
    AttrNames.INVERTER_AC_ID: JsonKeys.INVERTER_AC_ID,
    AttrNames.INVERTER_CIRCUIT_ID: JsonKeys.INVERTER_CIRCUIT_ID,
    AttrNames.INVERTER_TOGGLE_CIRCUIT_ID: JsonKeys.INVERTER_TOGGLE_CIRCUIT_ID,
    AttrNames.CHARGER_AC_ID: JsonKeys.CHARGER_AC_ID,
    AttrNames.CHARGER_CIRCUIT_ID: JsonKeys.CHARGER_CIRCUIT_ID,
    AttrNames.CHARGER_TOGGLE_CIRCUIT_ID: JsonKeys.CHARGER_TOGGLE_CIRCUIT_ID,
    AttrNames.BATTERY_BANK_1_ID: JsonKeys.BATTERY_BANK_1_ID,
    AttrNames.BATTERY_BANK_2_ID: JsonKeys.BATTERY_BANK_2_ID,
    AttrNames.BATTERY_BANK_3_ID: JsonKeys.BATTERY_BANK_3_ID,
}

INVERTER_CHARGER_INSTANCE_FIELD_MAP = {
    AttrNames.INVERTER_INSTANCE: JsonKeys.INVERTER_INSTANCE,
    AttrNames.CHARGER_INSTANCE: JsonKeys.CHARGER_INSTANCE,
}

DEVICE_FIELD_MAP = {
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.SOURCE_ADDRESS: JsonKeys.SOURCE_ADDRESS,
    AttrNames.CONFLICT: JsonKeys.CONFLICT,
    AttrNames.VALID: JsonKeys.VALID,
    AttrNames.TRANSIENT: JsonKeys.TRANSIENT,
    AttrNames.VERSION: JsonKeys.VERSION,
    AttrNames.DIPSWITCH: JsonKeys.DIPSWITCH,
}

DEVICE_ENUM_FIELD_MAP = {
    AttrNames.DEVICE_TYPE: (JsonKeys.DEVICE_TYPE, DeviceType),
}

HVAC_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.FAN_SPEED_COUNT: JsonKeys.FAN_SPEED_COUNT,
    AttrNames.OPERATING_MODES_MASK: JsonKeys.OPERATING_MODES_MASK,
    AttrNames.MODEL: JsonKeys.MODEL,
    AttrNames.SETPOINT_TEMPERATURE_MIN: JsonKeys.SETPOINT_TEMPERATURE_MIN,
    AttrNames.SETPOINT_TEMPERATURE_MAX: JsonKeys.SETPOINT_TEMPERATURE_MAX,
    AttrNames.FAN_SPEED_OFF_MODES_MASK: JsonKeys.FAN_SPEED_OFF_MODES_MASK,
    AttrNames.FAN_SPEED_AUTO_MODES_MASK: JsonKeys.FAN_SPEED_AUTO_MODES_MASK,
    AttrNames.FAN_SPEED_MANUAL_MODES_MASK: JsonKeys.FAN_SPEED_MANUAL_MODES_MASK,
}

HVAC_INSTANCE_FIELD_MAP = {
    AttrNames.INSTANCE: JsonKeys.INSTANCE,
    AttrNames.TEMPERATURE_INSTANCE: JsonKeys.TEMPERATURE_INSTANCE,
}

HVAC_DATA_ID_FIELD_MAP = {
    AttrNames.OPERATING_MODE_ID: JsonKeys.OPERATING_MODE_ID,
    AttrNames.FAN_MODE_ID: JsonKeys.FAN_MODE_ID,
    AttrNames.FAN_SPEED_ID: JsonKeys.FAN_SPEED_ID,
    AttrNames.SETPOINT_TEPERATURE_ID: JsonKeys.SETPOINT_TEPERATURE_ID,
    AttrNames.OPERATING_MODE_TOGGLE_ID: JsonKeys.OPERATING_MODE_TOGGLE_ID,
    AttrNames.FAN_MODE_TOGGLE_ID: JsonKeys.FAN_MODE_TOGGLE_ID,
    AttrNames.FAN_SPEED_TOGGLE_ID: JsonKeys.FAN_SPEED_TOGGLE_ID,
    AttrNames.SET_POINT_TEMPERATURE_TOGGLE_ID: JsonKeys.SET_POINT_TEMPERATURE_TOGGLE_ID,
    AttrNames.TEMPERATURE_MONITORING_ID: JsonKeys.TEMPERATURE_MONITORING_ID,
}


AUDIO_STEREO_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.MUTE_ENABLED: JsonKeys.MUTE_ENABLED,
}

BINARY_LOGIC_STATE_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.ADDRESS: JsonKeys.ADDRESS,
}

UI_RELATIONSHIPS_FIELD_MAP = {
    AttrNames.PRIMARY_ID: JsonKeys.PRIMARY_ID,
    AttrNames.SECONDARY_ID: JsonKeys.SECONDARY_ID,
    AttrNames.PRIMARY_CONFIG_ADDRESS: JsonKeys.PRIMARY_CONFIG_ADDRESS,
    AttrNames.SECONDARY_CONFIG_ADDRESS: JsonKeys.SECONDARY_CONFIG_ADDRESS,
    AttrNames.PRIMARY_CHANNEL_INDEX: JsonKeys.PRIMARY_CHANNEL_INDEX,
    AttrNames.SECONDARY_CHANNEL_INDEX: JsonKeys.SECONDARY_CHANNEL_INDEX,
}

UI_RELATIONSHIPS_ENUM_FIELD_MAP = {
    AttrNames.PRIMARY_TYPE: (JsonKeys.PRIMARY_TYPE, ItemType),
    AttrNames.SECONDARY_TYPE: (JsonKeys.SECONDARY_TYPE, ItemType),
    AttrNames.RELATIONSHIP_TYPE: (
        JsonKeys.RELATIONSHIP_TYPE,
        RelationshipType,
    ),
}

PRESSURE_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.CIRCUIT_NAME_UTF8: JsonKeys.CIRCUIT_NAME_UTF8,
    AttrNames.ADDRESS: JsonKeys.ADDRESS,
    AttrNames.ATMOSPHERIC_PRESSURE: JsonKeys.ATMOSPHERIC_PRESSURE,
}

PRESSURE_ENUM_FIELD_MAP = {
    AttrNames.PRESSURE_TYPE: (JsonKeys.PRESSURE_TYPE, PressureType),
    AttrNames.SWITCH_TYPE: (JsonKeys.SWITCH_TYPE, SwitchType),
}

PRESSURE_DATA_ID_FIELD_MAP = {
    AttrNames.CIRCUIT_ID: JsonKeys.CIRCUIT_ID,
}

ENGINE_FIELD_MAP = {
    AttrNames.ID: JsonKeys.ID,
    AttrNames.NAMEUTF8: JsonKeys.NAMEUTF8,
    AttrNames.SOFTWARE_ID: JsonKeys.SOFTWARE_ID,
    AttrNames.CALIBRATION_ID: JsonKeys.CALIBRATION_ID,
    AttrNames.SERIAL_NUMBER: JsonKeys.SERIAL_NUMBER,
    AttrNames.ECU_SERIAL_NUMBER: JsonKeys.ECU_SERIAL_NUMBER,
}

ENGINE_ENUM_FIELD_MAP = {
    AttrNames.ENGINE_TYPE: (JsonKeys.ENGINE_TYPE, EngineType),
}
