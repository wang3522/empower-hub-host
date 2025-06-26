#pragma once

#include <mutex>
#include <unordered_map>
#include <vector>

#include "modules/czone/monitoringdata.h"
#include "modules/n2k/canservice.h"
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

  N2KMonitoring::SnapshotInstanceIdMap Snapshot(bool &empty, N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot);

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
  //   void SetWakeupDcMeters(const google::protobuf::Map<google::protobuf::uint32, Nmea2k::DC> &dcMap) {
  //     m_WakeUp = true;
  //     m_WakeDcMap = dcMap;
  //   }

private:
  CanService &m_canService;

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

  // template <typename T>
  // bool isMapSame(const T &a, const T &b) {
  //   if (a.size() != b.size()) {
  //     return false;
  //   }
  //   for (auto &it : a) {
  //     if (b.find(it.first) == b.end()) {
  //       return false;
  //     }
  //     google::protobuf::util::MessageDifferencer differencer;
  //     if (!differencer.Compare(it.second, b.at(it.first))) {
  //       return false;
  //     }
  //   }
  //   return true;
  // }

  std::mutex m_SnapshotMutex;
  N2KMonitoring::SnapshotInstanceIdMap m_Snapshot;
  N2KMonitoring::MonitoringKeyValueMap m_SnapshotKeyValue;
  tUnitConversion m_UnitConversion;

  std::map<uint32_t, uint32_t> m_DataTypeIndex;
  std::mutex m_NetworkStatusMutex;
  N2KMonitoring::NetworkStatus m_NetworkStatus;
  bool m_WakeUp = false;
  // google::protobuf::Map<google::protobuf::uint32, Nmea2k::DC> m_WakeDcMap;
};