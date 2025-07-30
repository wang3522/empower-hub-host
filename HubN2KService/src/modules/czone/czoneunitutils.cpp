#include "modules/czone/czoneunitutils.h"

tUnitTypes Utils::Units::UnitsFromDataType(const tCZoneDataType dataType)
{
    switch (dataType)
    {
        case eCZone_DC_Potential:
        case eCZone_LogDC_MinVoltage:
        case eCZone_LogDC_MaxVoltage:
        case eCZone_Engine_AlternatorPotential:
            return eUnitType_Voltage;

        case eCZone_DC_Current:
            return eUnitType_Current;

        case eCZone_DC_Temperature:
        case eCZone_Engine_EngineCoolantTemperature:
            return eUnitType_Temperature;

        case eCZone_DC_StateOfCharge:
            return eUnitType_Percent;

        case eCZone_DC_TimeRemaining:
        case eCZone_DC_TimeToCharge:
        case eCZone_DC_TimeRemainingOrToCharge:
            return eUnitType_Time;

        case eCZone_DC_TimeRemaining_Days:
        case eCZone_DC_TimeToCharge_Days:
        case eCZone_DC_TimeRemainingOrToCharge_Days:
            return eUnitType_Days;

        case eCZone_DC_TimeRemaining_Hours:
        case eCZone_DC_TimeToCharge_Hours:
        case eCZone_DC_TimeRemainingOrToCharge_Hours:
            return eUnitType_Hours;

        case eCZone_DC_TimeRemaining_Minutes:
        case eCZone_DC_TimeToCharge_Minutes:
        case eCZone_DC_TimeRemainingOrToCharge_Minutes:
            return eUnitType_Minutes;

        case eCZone_DC_CapacityRemaining:
        case eCZone_LogDC_MinCapacityRemaining:
            return eUnitType_BatteryCapacity;

        case eCZone_DC_RippleVoltage:
            return eUnitType_RMSVoltage;

        case eCZone_AC1_In_Voltage:
        case eCZone_AC2_In_Voltage:
        case eCZone_AC3_In_Voltage:
        case eCZone_AC_Average_In_Voltage:
        case eCZone_AC1_Out_Voltage:
        case eCZone_AC2_Out_Voltage:
        case eCZone_AC3_Out_Voltage:
        case eCZone_AC_Average_Out_Voltage:
        case eCZone_LogAC_MinVoltage:
        case eCZone_LogAC_MaxVoltage:
            return eUnitType_RMSVoltage;

        case eCZone_AC1_In_Current:
        case eCZone_AC2_In_Current:
        case eCZone_AC3_In_Current:
        case eCZone_AC_Average_In_Current:
        case eCZone_AC1_Out_Current:
        case eCZone_AC2_Out_Current:
        case eCZone_AC3_Out_Current:
        case eCZone_AC_Average_Out_Current:
        case eCZone_LogAC_MaxCurrent:
            return eUnitType_Current;

        case eCZone_AC1_In_Frequency:
        case eCZone_AC2_In_Frequency:
        case eCZone_AC3_In_Frequency:
        case eCZone_AC_Average_In_Frequency:
        case eCZone_AC1_Out_Frequency:
        case eCZone_AC2_Out_Frequency:
        case eCZone_AC3_Out_Frequency:
        case eCZone_AC_Average_Out_Frequency:
        case eCZone_LogAC_MinFrequency:
        case eCZone_LogAC_MaxFrequency:
            return eUnitType_Frequency;

        case eCZone_AC1_In_BreakerSize:
        case eCZone_AC2_In_BreakerSize:
        case eCZone_AC3_In_BreakerSize:
        case eCZone_AC_Average_In_BreakerSize:
        case eCZone_AC1_Out_BreakerSize:
        case eCZone_AC2_Out_BreakerSize:
        case eCZone_AC3_Out_BreakerSize:
        case eCZone_AC_Average_Out_BreakerSize:
            return eUnitType_Current;

        case eCZone_AC1_In_RealPower:
        case eCZone_AC2_In_RealPower:
        case eCZone_AC3_In_RealPower:
        case eCZone_AC_Average_In_RealPower:
        case eCZone_AC1_Out_RealPower:
        case eCZone_AC2_Out_RealPower:
        case eCZone_AC3_Out_RealPower:
        case eCZone_AC_Average_Out_RealPower:
            return eUnitType_Power;

        case eCZone_AC1_In_ReactivePower:
        case eCZone_AC2_In_ReactivePower:
        case eCZone_AC3_In_ReactivePower:
        case eCZone_AC_Average_In_ReactivePower:
        case eCZone_AC1_Out_ReactivePower:
        case eCZone_AC2_Out_ReactivePower:
        case eCZone_AC3_Out_ReactivePower:
        case eCZone_AC_Average_Out_ReactivePower:
            return eUnitType_ReactivePower;

        case eCZone_Tank_LevelPercent:
        case eCZone_Engine_Trim:
        case eCZone_Engine_EngineLoad:
        case eCZone_Engine_EngineTorque:
            return eUnitType_Percent;

        case eCZone_Tank_Level:
            return eUnitType_Volume;

        case eCZone_Tank_Capacity:
            return eUnitType_Volume;

        case eCZone_Circuit_Current:
            return eUnitType_Current;

        case eCZone_Environment_Pressure:
        case eCZone_Engine_BoostPressure:
        case eCZone_Engine_OilPressure:
        case eCZone_Engine_EngineCoolantPressure:
        case eCZone_Engine_FuelPressure:
        case eCZone_Tyre_Pressure:
            return eUnitType_Pressure;

        case eCZone_Environment_AtmosphericPressure:
            return eUnitType_BarometricPressure;

        case eCZone_Environment_Temperature:
        case eCZone_Environment_SetTemperature:
        case eCZone_Engine_OilTemperature:
        case eCZone_Engine_Temperature:
        case eCZone_Tyre_Temperature:
            return eUnitType_Temperature;

        case eCZone_Environment_HighTemperature:
            return eUnitType_Temperature;

        case eCZone_Wind_SpeedTrue:
            return eUnitType_WindSpeed;

        case eCZone_Wind_SpeedApparent:
            return eUnitType_WindSpeed;

        case eCZone_Wind_Heading:
            return eUnitType_Heading;

        case eCZone_Wind_Direction_True:
            return eUnitType_Heading;

        case eCZone_Wind_Direction_Apparent:
            return eUnitType_Heading;

        case eCZone_Depth:
            return eUnitType_Depth;

        case eCZone_Depth_Offset:
            return eUnitType_Depth;

        case eCZone_GPS_Latitude:
            return eUnitType_Position;

        case eCZone_GPS_Longitude:
            return eUnitType_Position;

        case eCZone_GPS_Cog:
            return eUnitType_Heading;

        case eCZone_GPS_Sog:
            return eUnitType_BoatSpeed;

        case eCZone_GPS_MagneticVariation:
            return eUnitType_Angle;

        case eCZone_Engine_Speed:
            return eUnitType_FrequencyOfRotation;

        case eCZone_Engine_FuelRate:
            return eUnitType_Flowrate;

        case eCZone_Signal_OnTime:
            return eUnitType_Hours;
        case eCZone_Engine_TotalEngineHours:
            return eUnitType_EngineHours;
        default:
            break;
    }

    return eUnitType_None;
}