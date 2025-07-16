#pragma once

#include <mutex>
#include <unordered_map>
#include <vector>

#include "modules/czone/monitoringdata.h"
#include "modules/dbus/dbusservice.h"
#include "modules/n2k/canservice.h"
#include "utils/asyncworker.h"
#include "utils/json.hpp"

#include "DevelopmentLib/Utils/tUnitConversion.h"

using json = nlohmann::json;

enum CZoneDbSettingsType {
  CZoneDbSettingsDepthOffset = 0,
  CZoneDbSettingsMagneticVariation,
  CZoneDbSettingsTimeOffset,
  CZoneDbSettingsDipswitch,
  CZoneDbSettingsEnableBatteryCharger,
};

struct MonitoringValue {
  bool Valid;
  float Value;
  bool LimitValid;
  float Min;
  float Max;
  float WarnLow;
  float WarnHigh;
};

class CzoneDatabase final {
public:
  CzoneDatabase(CanService &canService);
  ~CzoneDatabase();

  void LoadDatabase();
  void Update(N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void Clear();

  bool Snapshot();

  bool GetSetting(CZoneDbSettingsType type, int32_t &value) const;
  bool GetSetting(CZoneDbSettingsType type, float &value) const;

  bool AddSetting(CZoneDbSettingsType type, int32_t value) const;
  bool AddSetting(CZoneDbSettingsType type, float value) const;
  bool AddSetting(CZoneDbSettingsType type, uint32_t value) const;
  bool AddSetting(CZoneDbSettingsType type, bool value) const;

  uint32_t CreateDataIndex(uint32_t type, uint32_t instance);
  uint32_t CreateDataIndexComplex(const uint8_t *data, uint32_t length);
  bool GetMonitoringData(uint32_t key, float &value);
  bool GetMonitoringDataLimits(uint32_t key, float &min, float &max, float &warnLow, float &warnHigh);
  void SetNetworkStatus(const N2KMonitoring::NetworkStatus &network);

  void GetHealthStatus(N2KMonitoring::HealthStatus &health, const int64_t timeout = 60000);
  void SetWakeupDcMeters(const std::unordered_map<uint32_t, N2KMonitoring::DC> &dcMap) {
    m_WakeUp = true;
    m_WakeDcMap.clear();
    for (auto &d : dcMap) {
      m_WakeDcMap[d.first] = std::make_shared<N2KMonitoring::DC>(d.second);
    }
  }

  void registerDbus(std::shared_ptr<DbusService> dbusService);

private:
  CanService &m_canService;
  WorkerPool m_workerpool;

  void UpdateMonitoringCircuits(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringModes(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                             N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringACMainContactors(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                        N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringTanks(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                             N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringEngines(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                               N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringACs(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                           N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringDCs(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                           N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringTemperatures(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                    N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringPressures(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                 N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringHVACs(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                             N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringAwnings(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                               N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringThirdPartyGenerators(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                            N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringInverterChargers(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                        N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringTyrepressures(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                     N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringAudioStereos(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                    N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringGNSS(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                            N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateMonitoringBinaryLogicStates(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                         N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);
  void UpdateNetworkStatus(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                           N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);

  std::mutex m_SnapshotMutex;
  N2KMonitoring::SnapshotInstanceIdMap m_Snapshot;         // delta
  N2KMonitoring::SnapshotInstanceIdMap m_LastSnapshot;     // save bw scan
  N2KMonitoring::MonitoringKeyValueMap m_SnapshotKeyValue; // temp keyvalue
  tUnitConversion m_UnitConversion;

  std::map<uint32_t, uint32_t> m_DataTypeIndex;
  std::mutex m_NetworkStatusMutex;
  N2KMonitoring::NetworkStatus m_NetworkStatus;
  bool m_WakeUp = false;
  std::unordered_map<uint32_t, std::shared_ptr<N2KMonitoring::DC>> m_WakeDcMap;

  struct Field {
    tCZoneDataType Type;
    bool Valid;
    float Value;
    std::string FieldName;
    uint32_t Instance;
  };

  template <typename T>
  uint32_t CreateKey(tCZoneDataType dataType, T instanceOrId);
  template <typename T>
  int32_t ValueS32(tCZoneDataType dataType, T instanceOrId, bool &valid, std::map<uint32_t, uint32_t> &dataTypeIndex);
  template <typename T>
  float Value(tCZoneDataType dataType, T instanceOrId, bool &valid, std::map<uint32_t, uint32_t> &dataTypeIndex,
              std::unordered_map<uint32_t, struct MonitoringValue> &valueMap);
  bool GetValuesForInstanceOrId(std::vector<Field> &fields, tUnitConversion &unitConversion,
                                std::map<uint32_t, uint32_t> &dataTypeIndex,
                                std::unordered_map<uint32_t, struct MonitoringValue> &valueMap);
  template <typename T>
  bool UpdateMessageIfDifferent(T *message1, T *message2, const std::vector<Field> &fields, bool forceUpdate);
  template <typename T1, typename T2>
  void ProcessFields(std::vector<Field> &fields, T1 instance, N2KMonitoring::IdMap<T2> &snapshot,
                     N2KMonitoring::IdMap<T2> &lastSnapshot, tUnitConversion &unitConversion,
                     std::map<uint32_t, uint32_t> &dataTypeIndex);
};