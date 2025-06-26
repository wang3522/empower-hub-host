#include "modules/czone/czonedatabase.h"

CZoneDb::CZoneDb(CanService &canService) : m_canService(canService) {
  m_UnitConversion.SetDefaults();

  m_UnitConversion.SetUnits(eUnitType_BoatSpeed, tSpeedConversions::MetersPerSecond);
  m_UnitConversion.SetUnits(eUnitType_WindSpeed, tSpeedConversions::MetersPerSecond);
  m_UnitConversion.SetUnits(eUnitType_Depth, tDistanceConversions::Meters);
  m_UnitConversion.SetUnits(eUnitType_Heading, tHeadingConversions::Magnetic);
  m_UnitConversion.SetUnits(eUnitType_Temperature, tTemperatureConversions::Celsius);
  m_UnitConversion.SetUnits(eUnitType_Volume, tVolumeConversions::Liters);
  m_UnitConversion.SetUnits(eUnitType_Pressure, tPressureConversions::Pascals);
  m_UnitConversion.SetUnits(eUnitType_BarometricPressure, tPressureConversions::BaroPascals);
  m_UnitConversion.SetUnits(eUnitType_BatteryCapacity, tCapacityConversions::AmpHours);
  m_UnitConversion.SetUnits(eUnitType_Angle, tAngleConversions::Degrees);
  m_UnitConversion.SetUnits(eUnitType_Flowrate, tFlowrateConversions::LitersPerHour);
  m_UnitConversion.SetUnits(eUnitType_EngineHours, tEngineHoursConversions::EngineHoursInMinutes);
}

CZoneDb::~CZoneDb() {}

void CZoneDb::LoadDatabase() { Clear(); }

void CZoneDb::Clear() { m_DataTypeIndex.clear(); }

void CZoneDb::Update(N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  m_Snapshot.Clear();
  m_SnapshotKeyValue.Clear();
  UpdateMonitoringCircuits(m_Snapshot, lastSnapshot);
  UpdateMonitoringModes(m_Snapshot, lastSnapshot);
  UpdateMonitoringACMainContactors(m_Snapshot, lastSnapshot);
  UpdateMonitoringTanks(m_Snapshot, lastSnapshot);
  UpdateMonitoringEngines(m_Snapshot, lastSnapshot);
  UpdateMonitoringACs(m_Snapshot, lastSnapshot);
  UpdateMonitoringDCs(m_Snapshot, lastSnapshot);
  UpdateMonitoringTemperatures(m_Snapshot, lastSnapshot);
  UpdateMonitoringPressures(m_Snapshot, lastSnapshot);
  UpdateMonitoringHVACs(m_Snapshot, lastSnapshot);
  UpdateMonitoringAwnings(m_Snapshot, lastSnapshot);
  UpdateMonitoringThirdPartyGenerators(m_Snapshot, lastSnapshot);
  UpdateMonitoringInverterChargers(m_Snapshot, lastSnapshot);
  UpdateMonitoringTyrepressures(m_Snapshot, lastSnapshot);
  UpdateMonitoringAudioStereos(m_Snapshot, lastSnapshot);
  UpdateMonitoringGNSS(m_Snapshot, lastSnapshot);
  UpdateMonitoringBinaryLogicStates(m_Snapshot, lastSnapshot);
  UpdateNetworkStatus(m_Snapshot, lastSnapshot);
}