#include <DevelopmentLib/Utils/tCZoneNmea2kName.h>
#include <Monitoring/tCZoneDataId.h>

#include "modules/czone/czonedatabase.h"
#include "utils/logger.h"

CzoneDatabase::CzoneDatabase(CanService &canService) : m_canService(canService) {
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

CzoneDatabase::~CzoneDatabase() {}

void CzoneDatabase::LoadDatabase() { Clear(); }

void CzoneDatabase::Clear() { m_DataTypeIndex.clear(); }

void CzoneDatabase::Update(N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  m_Snapshot.clear();
  m_SnapshotKeyValue.clear();
  // UpdateMonitoringCircuits(m_Snapshot, lastSnapshot);
  // UpdateMonitoringModes(m_Snapshot, lastSnapshot);
  // UpdateMonitoringACMainContactors(m_Snapshot, lastSnapshot);
  // UpdateMonitoringTanks(m_Snapshot, lastSnapshot);
  // UpdateMonitoringEngines(m_Snapshot, lastSnapshot);
  // UpdateMonitoringACs(m_Snapshot, lastSnapshot);
  // UpdateMonitoringDCs(m_Snapshot, lastSnapshot);
  // UpdateMonitoringTemperatures(m_Snapshot, lastSnapshot);
  // UpdateMonitoringPressures(m_Snapshot, lastSnapshot);
  // UpdateMonitoringHVACs(m_Snapshot, lastSnapshot);
  // UpdateMonitoringAwnings(m_Snapshot, lastSnapshot);
  // UpdateMonitoringThirdPartyGenerators(m_Snapshot, lastSnapshot);
  // UpdateMonitoringInverterChargers(m_Snapshot, lastSnapshot);
  // UpdateMonitoringTyrepressures(m_Snapshot, lastSnapshot);
  // UpdateMonitoringAudioStereos(m_Snapshot, lastSnapshot);
  // UpdateMonitoringGNSS(m_Snapshot, lastSnapshot);
  // UpdateMonitoringBinaryLogicStates(m_Snapshot, lastSnapshot);
  // UpdateNetworkStatus(m_Snapshot, lastSnapshot);
}

N2KMonitoring::SnapshotInstanceIdMap CzoneDatabase::Snapshot(bool &empty,
                                                             N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  const std::lock_guard<std::mutex> lock(m_SnapshotMutex);
  Update(lastSnapshot);

  empty = true;
  if (m_Snapshot.m_ac.size() > 0 || m_Snapshot.m_acMainContactors.size() > 0 || m_Snapshot.m_audioStereos.size() > 0 ||
      m_Snapshot.m_awnings.size() > 0 || m_Snapshot.m_circuits.size() > 0 || m_Snapshot.m_dc.size() > 0 ||
      m_Snapshot.m_engines.size() > 0 || m_Snapshot.m_inverterChargers.size() > 0 || m_Snapshot.m_hvacs.size() > 0 ||
      m_Snapshot.m_modes.size() > 0 || m_Snapshot.m_pressures.size() > 0 || m_Snapshot.m_tanks.size() > 0 ||
      m_Snapshot.m_temperatures.size() > 0 || m_Snapshot.m_thirdPartyGenerators.size() > 0 ||
      m_Snapshot.m_tyrepressures.size() > 0 || m_Snapshot.m_gnss.size() > 0 ||
      m_Snapshot.m_binaryLogicState.size() > 0 || m_Snapshot.m_networkStatus != nullptr) {
    empty = false;
    for (auto &it : m_SnapshotKeyValue.m_keyValueMap) {
      //[x] verify need swallow copy or deep copy
      m_Snapshot.m_monitoringKeyValue[it.first] = it.second;
    }
  }

  return m_Snapshot;
}

bool CzoneDatabase::GetSetting(CZoneDbSettingsType type, int32_t &value) const {
  switch (type) {
  case CZoneDbSettingsTimeOffset: value = m_canService.Settings()->getTimeOffset(); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "GetSetting for int32_t, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::GetSetting(CZoneDbSettingsType type, float &value) const {
  switch (type) {
  case CZoneDbSettingsDepthOffset: value = m_canService.Settings()->getDepthOffset(); break;
  case CZoneDbSettingsMagneticVariation: value = m_canService.Settings()->getMagneticVariation(); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "GetSetting for float, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, uint32_t value) const {
  switch (type) {
  case CZoneDbSettingsDipswitch: m_canService.Settings()->setDipswitch(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for uint32_t, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, int32_t value) const {
  switch (type) {
  case CZoneDbSettingsTimeOffset: m_canService.Settings()->setTimeOffset(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for int32_t, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, float value) const {
  switch (type) {
  case CZoneDbSettingsDepthOffset: m_canService.Settings()->setDepthOffset(value); break;
  case CZoneDbSettingsMagneticVariation: m_canService.Settings()->setMagneticVariation(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for float, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, bool value) const {
  switch (type) {
  case CZoneDbSettingsEnableBatteryCharger: m_canService.Settings()->setEnableBatteryCharger(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for bool, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

uint32_t CzoneDatabase::CreateDataIndex(uint32_t type, uint32_t instance) {
  uint32_t key = type << 16 | instance & 0xffff;
  auto it = m_DataTypeIndex.find(key);

  if (it == m_DataTypeIndex.end()) {
    auto index = CZoneMonitoringCreateDataIndex(tCZoneDataType(type), instance);
    m_DataTypeIndex[key] = index;
  }
  return m_DataTypeIndex[key];
}

uint32_t CzoneDatabase::CreateDataIndexComplex(const uint8_t *data, uint32_t length) {
  tCZoneDataId id;
  id.FromByteBuffer(data, length);

  if (id.DataType() >= eNumberOfDataTypes) {
    return (uint32_t)(eDataTypeInvalid & 0xfff) << 20;
  }

  uint32_t key = hash_value(id) | 0x800000000;

  auto it = m_DataTypeIndex.find(key);
  if (it == m_DataTypeIndex.end()) {
    m_DataTypeIndex[key] = CZoneMonitoringCreateComplexDataIndex(data, length);
  }

  return m_DataTypeIndex[key];
}

bool CzoneDatabase::GetMonitoringData(uint32_t key, float &value) { return CZoneMonitoringData(key, &value); }

bool CzoneDatabase::GetMonitoringDataLimits(uint32_t key, float &min, float &max, float &warnLow, float &warnHigh) {
  return CZoneMonitoringDataLimits(key, &min, &max, &warnLow, &warnHigh);
}

void CzoneDatabase::SetNetworkStatus(const N2KMonitoring::NetworkStatus &network) {
  const std::lock_guard<std::mutex> lock(m_NetworkStatusMutex);
  m_NetworkStatus = network;
}

void CzoneDatabase::GetHealthStatus(N2KMonitoring::HealthStatus &health, const int64_t timeout) {
  health.m_serviceThread = N2KMonitoring::eHealth::HealthOk; // implicitly, if this call functions

  bool network = m_canService.HealthStatus(timeout);
  health.m_networkThread = (network ? N2KMonitoring::eHealth::HealthOk : N2KMonitoring::eHealth::HealthBad);

  // [x] smart craft
  health.m_scThread = N2KMonitoring::eHealth::HealthNone;

  // [x] gnss
  health.m_gnssThread = N2KMonitoring::eHealth::HealthNone;
  health.m_gnssLatLon = N2KMonitoring::eHealth::HealthNone;
  health.m_gnssFix = N2KMonitoring::eHealth::HealthNone;
}