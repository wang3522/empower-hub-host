#include <DevelopmentLib/Utils/tCZoneNmea2kName.h>
#include <Monitoring/tCZoneDataId.h>

#include "modules/czone/czonedatabase.h"
#include "modules/czone/czoneunitutils.h"
#include "utils/logger.h"

template <typename T>
uint32_t CreateKey(tCZoneDataType dataType, T instanceOrId) {
  return (static_cast<uint32_t>(dataType) << 16) | instanceOrId & 0xffff;
}

template <typename T>
int32_t ValueS32(tCZoneDataType dataType, T instanceOrId, bool &valid, std::map<uint32_t, uint32_t> &dataTypeIndex) {
  int32_t value = 0.0;

  auto key = CreateKey(dataType, instanceOrId);
  auto it = dataTypeIndex.find(key);

  if (it == dataTypeIndex.end()) {
    auto index = CZoneMonitoringCreateDataIndex(dataType, instanceOrId);
    dataTypeIndex[key] = index;
    valid = CZoneMonitoringDataS32(index, &value);
  } else {
    valid = CZoneMonitoringDataS32(it->second, &value);
  }

  return value;
}

template <typename T>
float Value(tCZoneDataType dataType, T instanceOrId, bool &valid, std::map<uint32_t, uint32_t> &dataTypeIndex,
            std::unordered_map<uint32_t, struct MonitoringValue> &valueMap) {
  float value = 0.0f;

  auto key = CreateKey(dataType, instanceOrId);
  auto it = dataTypeIndex.find(key);

  bool limitValid;
  float min;
  float max;
  float warnLow;
  float warnHigh;

  if (it == dataTypeIndex.end()) {
    auto index = CZoneMonitoringCreateDataIndex(dataType, instanceOrId);
    dataTypeIndex[key] = index;
    valid = CZoneMonitoringData(index, &value);
    limitValid = CZoneMonitoringDataLimits(index, &min, &max, &warnLow, &warnHigh);
  } else {
    valid = CZoneMonitoringData(it->second, &value);
    limitValid = CZoneMonitoringDataLimits(it->second, &min, &max, &warnLow, &warnHigh);
  }

  struct MonitoringValue mValue;
  mValue.Valid = valid;
  mValue.Value = value;
  mValue.LimitValid = limitValid;
  mValue.Min = min;
  mValue.Max = max;
  mValue.WarnLow = warnLow;
  mValue.WarnHigh = warnHigh;
  valueMap[dataTypeIndex[key]] = mValue;
  return value;
}

// template <typename T1, typename T2>
// T1 *CreateValue(const bool valid, float value) {
//   T1 *v = new T1();
//   v->set_valid(valid);
//   v->set_value(static_cast<T2>(value));
//   return v;
// }

struct Field {
  tCZoneDataType Type;
  bool Valid;
  float Value;
  std::string FieldName;
  uint32_t Instance;
};

bool GetValuesForInstanceOrId(std::vector<Field> &fields, tUnitConversion &unitConversion,
                              std::map<uint32_t, uint32_t> &dataTypeIndex,
                              std::unordered_map<uint32_t, struct MonitoringValue> &valueMap) {
  bool validValue = false;
  for (auto &f : fields) {
    if (f.Type == eCZone_Generic_Instance) {
      f.Value = f.Instance;
      f.Valid = true;
    } else {
      f.Value = Value(f.Type, f.Instance, f.Valid, dataTypeIndex, valueMap);
      if (f.Valid) {
        validValue = true;
        auto units = Utils::Units::UnitsFromDataType(f.Type);
        f.Value = unitConversion.SystemValueToUserValue(units, f.Value);
      }
    }
  }
  return validValue;
}

// template <typename T1, typename T2, typename T3, typename T4>
// bool CheckAndAddIfDifferent(T3 *message1, T3 *message2, T4 *ref1, T4 *ref2, const google::protobuf::FieldDescriptor *df,
//                             const Field &f, bool forceUpdate) {
//   // Assumes T1 is a field of the form:
//   // bool Valid;
//   // T2 Value;

//   bool equivalent = false;
//   auto m = static_cast<T1 *>(ref2->MutableMessage(message2, df));
//   if (m) {
//     equivalent = static_cast<T2>(f.Value) == m->value() && f.Valid == m->valid();
//   }

//   if (!equivalent || forceUpdate) {
//     ref1->SetAllocatedMessage(message1, CreateValue<T1, T2>(f.Valid, f.Value), df);
//     m->set_valid(f.Valid);
//     m->set_value(static_cast<T2>(f.Value));
//     return false;
//   }

//   return equivalent;
// }

// Define message structs to replace protobuf messages

template <typename T1, typename T2>
void ProcessFields(std::vector<Field> &fields, T1 instance, N2KMonitoring::IdMap<T2> &snapshot,
                   N2KMonitoring::IdMap<T2> &lastSnapshot, tUnitConversion &unitConversion,
                   std::map<uint32_t, uint32_t> &dataTypeIndex) {
  std::unordered_map<uint32_t, struct MonitoringValue> valueMap;
  bool validValue = GetValuesForInstanceOrId(fields, unitConversion, dataTypeIndex, valueMap);

  auto lastSnapShotEntry = lastSnapshot.find(instance);
  if (lastSnapShotEntry == lastSnapshot.end()) {
    T2 item1, item2;
    UpdateMessageIfDifferent(&item1, &item2, fields, !validValue);
    (*snapshot)[instance] = item1;
    (*lastSnapshot)[instance] = item2;
    for (auto &it : valueMap) {
      Nmea2k::MonitoringKeyValue mValue;
      mValue.set_valid(it.second.Valid);
      mValue.set_value(it.second.Value);
      mValue.set_limitvalid(it.second.LimitValid);
      mValue.set_min(it.second.Min);
      mValue.set_max(it.second.Max);
      mValue.set_warnlow(it.second.WarnLow);
      mValue.set_warnhigh(it.second.WarnHigh);
      (*m_SnapshotKeyValue.mutable_keyvaluemap())[it.first] = mValue;
    }
  } else {
    T2 item;
    if (UpdateMessageIfDifferent(&item, &lastSnapShotEntry->second, fields, false)) {
      (*snapshot)[instance] = item;
      for (auto &it : valueMap) {
        Nmea2k::MonitoringKeyValue mValue;
        mValue.set_valid(it.second.Valid);
        mValue.set_value(it.second.Value);
        mValue.set_limitvalid(it.second.LimitValid);
        mValue.set_min(it.second.Min);
        mValue.set_max(it.second.Max);
        mValue.set_warnlow(it.second.WarnLow);
        mValue.set_warnhigh(it.second.WarnHigh);
        (*m_SnapshotKeyValue.mutable_keyvaluemap())[it.first] = mValue;
      }
    }
  }
}

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
      //[x] deep copy
      m_Snapshot.m_monitoringKeyValue[it.first] = it.second;
      if (it.second) {
        m_Snapshot.m_monitoringKeyValue[it.first] = std::make_shared<N2KMonitoring::MonitoringKeyValue>(*it.second);
      }
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

void CzoneDatabase::UpdateMonitoringCircuits(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                             N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto circuits = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayCircuits);
  for (auto &c : circuits) {
    if (c.Circuit.CircuitType == 0 /*CZ_CT_STANDARD_CIRCUIT*/) {
      uint32_t id = c.Circuit.Id;

      std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Id", id},
                                   {eCZone_Circuit_SystemOnState, false, 0.0f, "SystemsOn", id},
                                   {eCZone_Circuit_Level, false, 0.0f, "Level", id},
                                   {eCZone_Circuit_Current, false, 0.0f, "Current", id},
                                   {eCZone_Circuit_Fault, false, 0.0f, "Fault", id},
                                   {eCZone_Circuit_OnCount, false, 0.0f, "OnCount", id},
                                   {eCZone_Circuit_OnTime, false, 0.0f, "OnTime", id},
                                   {eCZone_Circuit_SequentialState, false, 0.0f, "SequentialState", id},
                                   {eCZone_Circuit_ACSourceAvailable, false, 0.0f, "ACSourceAvailable", id},
                                   {eCZone_Circuit_IsOffline, false, 0.0f, "IsOffline", id}};

      ProcessFields(fields, id, snapshot.m_circuits, lastSnapshot.m_circuits, m_UnitConversion, m_DataTypeIndex);
    }
  }
}