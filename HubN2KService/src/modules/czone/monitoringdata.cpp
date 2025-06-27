#include <tuple>

#include "modules/czone/monitoringdata.h"

namespace {
template <typename MapType>
bool deepCompareMap(const MapType &a, const MapType &b) {
  if (a.size() != b.size())
    return false;
  for (const auto &[key, value] : a) {
    auto it = b.find(key);
    if (it == b.end() || value == nullptr != (it->second == nullptr))
      return false;
    if (value && it->second && *value != *(it->second))
      return false;
  }
  return true;
}
} // namespace

N2KMonitoring::SnapshotInstanceIdMap::SnapshotInstanceIdMap() {
  m_circuits.clear();
  m_modes.clear();
  m_tanks.clear();
  m_engines.clear();
  m_ac.clear();
  m_dc.clear();
  m_temperatures.clear();
  m_pressures.clear();
  m_hvacs.clear();
  m_awnings.clear();
  m_thirdPartyGenerators.clear();
  m_inverterChargers.clear();
  m_tyrepressures.clear();
  m_audioStereos.clear();
  m_acMainContactors.clear();
  m_gnss.clear();
  m_monitoringKeyValue.clear();
  m_binaryLogicState.clear();

  m_networkStatus = nullptr;
  m_timeStamp = "";
}

N2KMonitoring::SnapshotInstanceIdMap::~SnapshotInstanceIdMap() {
  clear();
}

void N2KMonitoring::SnapshotInstanceIdMap::clear() {
  m_circuits.clear();
  m_modes.clear();
  m_tanks.clear();
  m_engines.clear();
  m_ac.clear();
  m_dc.clear();
  m_temperatures.clear();
  m_pressures.clear();
  m_hvacs.clear();
  m_awnings.clear();
  m_thirdPartyGenerators.clear();
  m_inverterChargers.clear();
  m_tyrepressures.clear();
  m_audioStereos.clear();
  m_acMainContactors.clear();
  m_gnss.clear();
  m_monitoringKeyValue.clear();
  m_binaryLogicState.clear();

  if (m_networkStatus != nullptr) {
    m_networkStatus->clear();
  }
  m_networkStatus = nullptr;
  m_timeStamp = "";
}

void N2KMonitoring::NetworkStatus::clear() {
  m_ethernetStatus = "";
  m_ethernetInternetConnectivity = false;
  m_ethernetIp = "";
  m_ethernetId = "";
  m_wifiStatus = "";
  m_wifiInternetConnectivity = false;
  m_wifiIp = "";
  m_wifiSsid = "";
  m_wifiSecurity = "";
  m_wifiType = "";
  m_wifiChannel = 0;
  m_wifiSignalStrengthDbm = 0;
  m_hotspotStatus = "";
  m_hotspotIp = "";
  m_hotspotSsid = "";
  m_hotspotPassword = "";
  m_hotspotSecurity = "";
  m_hotspotType = "";
  m_hotspotChannel = 0;
  m_cellularStatus = "";
  m_celllularInternetConnectivity = false;
  m_cellularIp = "";
  m_cellularOperator = "";
  m_cellularType = "";
  m_cellularSignalStrengthDbm = 0;
  m_cellularSimIccid = "";
  m_cellularSimEid = "";
  m_cellularSimImsi = "";
}

void N2KMonitoring::MonitoringKeyValueMap::clear() { m_keyValueMap.clear(); }

bool N2KMonitoring::AC::operator==(const N2KMonitoring::AC &other) const {
  return deepCompareMap(m_acLines, other.m_acLines) && std::tie(m_instance) == std::tie(other.m_instance);
}

bool N2KMonitoring::SnapshotInstanceIdMap::operator==(const N2KMonitoring::SnapshotInstanceIdMap &other) const {
  return deepCompareMap(m_circuits, other.m_circuits) && deepCompareMap(m_modes, other.m_modes) &&
         deepCompareMap(m_tanks, other.m_tanks) && deepCompareMap(m_engines, other.m_engines) &&
         deepCompareMap(m_ac, other.m_ac) && deepCompareMap(m_dc, other.m_dc) &&
         deepCompareMap(m_temperatures, other.m_temperatures) && deepCompareMap(m_pressures, other.m_pressures) &&
         deepCompareMap(m_hvacs, other.m_hvacs) && deepCompareMap(m_awnings, other.m_awnings) &&
         deepCompareMap(m_thirdPartyGenerators, other.m_thirdPartyGenerators) &&
         deepCompareMap(m_inverterChargers, other.m_inverterChargers) &&
         deepCompareMap(m_tyrepressures, other.m_tyrepressures) &&
         deepCompareMap(m_audioStereos, other.m_audioStereos) &&
         deepCompareMap(m_acMainContactors, other.m_acMainContactors) && deepCompareMap(m_gnss, other.m_gnss) &&
         deepCompareMap(m_monitoringKeyValue, other.m_monitoringKeyValue) &&
         deepCompareMap(m_binaryLogicState, other.m_binaryLogicState) &&
         std::tie(m_networkStatus, m_timeStamp) == std::tie(other.m_networkStatus, other.m_timeStamp);
}

bool N2KMonitoring::MonitoringKeyValueMap::operator==(const MonitoringKeyValueMap &other) const {
  return deepCompareMap(m_keyValueMap, other.m_keyValueMap);
}