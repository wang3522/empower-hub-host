#include "modules/czone/monitoringdata.h"

void N2KMonitoring::SnapshotInstanceIdMap::Clear() {
  m_Circuits.clear();
  m_Modes.clear();
  m_Tanks.clear();
  m_Engines.clear();
  m_AC.clear();
  m_DC.clear();
  m_Temperatures.clear();
  m_Pressures.clear();
  m_Hvacs.clear();
  m_Awnings.clear();
  m_ThirdPartyGenerators.clear();
  m_InverterChargers.clear();
  m_Tyrepressures.clear();
  m_AudioStereos.clear();
  m_ACMainContactors.clear();
  m_GNSS.clear();
  m_MonitoringKeyValue.clear();
  m_BinaryLogicState.clear();

  m_NetworkStatus.clear();
  m_TimeStamp = "";
}

void N2KMonitoring::NetworkStatus::clear() {
  EthernetStatus = "";
  EthernetInternetConnectivity = false;
  EthernetIp = "";
  EthernetId = "";
  WifiStatus = "";
  WifiInternetConnectivity = false;
  WifiIp = "";
  WifiSsid = "";
  WifiSecurity = "";
  WifiType = "";
  WifiChannel = 0;
  WifiSignalStrengthDbm = 0;
  HotspotStatus = "";
  HotspotIp = "";
  HotspotSsid = "";
  HotspotPassword = "";
  HotspotSecurity = "";
  HotspotType = "";
  HotspotChannel = 0;
  CellularStatus = "";
  CelllularInternetConnectivity = false;
  CellularIp = "";
  CellularOperator = "";
  CellularType = "";
  CellularSignalStrengthDbm = 0;
  CellularSimIccid = "";
  CellularSimEid = "";
  CellularSimImsi = "";
}

void N2KMonitoring::MonitoringKeyValueMap::Clear() { KeyValueMap.clear(); }
