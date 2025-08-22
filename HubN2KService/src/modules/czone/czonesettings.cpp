#include "modules/czone/czonesettings.h"
#include "utils/common.h"
#include "utils/fileutil.h"
#include <fstream>
#include <iostream>
#include <sstream>

CzoneSettings &CzoneSettings::getInstance() {
  static CzoneSettings _instance;
  return _instance;
}

CzoneSettings::CzoneSettings() : m_settingsversion(3) {
  std::string data;
  bool load_factory = false;

  resetAndInitializeCZonelibSettings();

  m_settingFilePath = getCzoneConfigPath() + CzoneSystemConstants::CZ_SETTINGS_FILE;

  if (!loadFromFile(data, m_settingFilePath)) {
    BOOST_LOG_TRIVIAL(warning) << "CzoneSettings: failed to load file, " << CzoneSystemConstants::CZ_SETTINGS_FILE;
    load_factory = true;
  } else {
    try {
      m_settings = json::parse(data);

      if (GetJsonValueInt("SettingsVersion") != m_settingsversion) {
        BOOST_LOG_TRIVIAL(warning) << "CzoneSettings: setting version mistmatch, reset to factory";
        load_factory = true;
      }
    } catch (const std::exception &err) {
      BOOST_LOG_TRIVIAL(error) << "CzoneSettings: failed to parse json with error, " << err.what();
      load_factory = true;
    }
  }

  if (load_factory) {
    factoryReset();
    if (!loadFromFile(data, m_settingFilePath)) {
      BOOST_LOG_TRIVIAL(warning) << "CzoneSettings: failed to load file, " << CzoneSystemConstants::CZ_SETTINGS_FILE;
      return;
    }
  }

  m_insecure = false;
  m_dipswitch = GetJsonValueInt("Dipswitch");
  m_sourceaddress = GetJsonValueInt("SourceAddress");

  m_t_czonesettings.SetValue(tSetting(eSettingTimeOffset, GetJsonValueInt("TimeOffset")));
  m_t_czonesettings.SetValue(tSetting(eSettingDepthOffset, GetJsonValueFloat("DepthOffset")));
  m_t_czonesettings.SetValue(tSetting(eSettingMagneticVariation, GetJsonValueFloat("MagneticVariation")));

  for (auto i = 0; i < eNumUnitTypes; i++) {
    auto key = "Units" + std::to_string(i);
    m_t_czonesettings.SetValue(tSetting(tUnitTypes(i), GetJsonValueInt("Units" + std::to_string(i))));
  }

  m_serialnumber = GetJsonValueString("SerialNumber");
  m_factoryICCID = GetJsonValueString("FactoryICCID");
  m_factoryIMEI = GetJsonValueString("FactoryIMEI");
  m_appFirmwareVersion = getAPPFirmwareVersion();
  m_hardwareVersions = GetJsonValueString("HardwareVersions");
  m_enable_batterycharger = GetJsonValueBoolen("EnableBatteryCharger");

  BOOST_LOG_TRIVIAL(debug) << "CzoneSettings::CzoneSettings::m_serialnumber " << m_serialnumber; // [x] debug
}

CzoneSettings::~CzoneSettings() {}

void CzoneSettings::resetAndInitializeCZonelibSettings() { m_t_czonesettings.FactoryReset(); }

bool CzoneSettings::loadFromFile(std::string &output, const std::string &fileName) {
  std::lock_guard<std::mutex> lock(m_filemutex);
  std::ifstream file(fileName);
  if (!file.is_open()) {
    return false;
  }
  std::stringstream buffer;
  buffer << file.rdbuf();
  output = buffer.str();
  file.close();
  return true;
}

bool CzoneSettings::saveToFile(const std::string &data, const std::string &filename) {
  std::lock_guard<std::mutex> lock(m_filemutex);
  std::ofstream file(filename, std::ios::out | std::ios::trunc);
  if (!file.is_open()) {
    return false;
  }
  try {
    file << data;
    file.flush();
    file.close();
  } catch (const std::exception &e) {
    BOOST_LOG_TRIVIAL(error) << "CzoneSettings: failed to save settings to file: " << e.what();
    file.close();
  }
  return true;
}

void CzoneSettings::setInsecure(const bool insecure) { m_insecure = insecure; }

bool CzoneSettings::insecure() const { return m_insecure; }

void CzoneSettings::setDipswitch(const uint8_t dipswitch) {
  if (m_dipswitch != dipswitch) {
    m_dipswitch = dipswitch;
    m_settings["Dipswitch"] = dipswitch;
    saveSettings();
  }
}

void CzoneSettings::setSourceAddress(const uint8_t address) {
  if (m_sourceaddress != address) {
    m_sourceaddress = address;
    m_settings["SourceAddress"] = address;
    saveSettings();
  }
}

void CzoneSettings::setTimeOffset(const int32_t offset) {
  if (getTimeOffset() != offset) {
    m_t_czonesettings.SetValue(tSetting(eSettingTimeOffset, offset));
    m_settings["TimeOffset"] = offset;
    saveSettings();
  }
}

void CzoneSettings::setDepthOffset(const float offset) {
  if (getDepthOffset() != offset) {
    m_t_czonesettings.SetValue(tSetting(eSettingDepthOffset, offset));
    m_settings["DepthOffset"] = offset;
    saveSettings();
  }
}

void CzoneSettings::setMagneticVariation(const float val) {
  if (getMagneticVariation() != val) {
    m_t_czonesettings.SetValue(tSetting(eSettingMagneticVariation, val));
    m_settings["MagneticVariation"] = val;
    saveSettings();
  }
}

std::string CzoneSettings::getHardwareVersions() { return m_hardwareVersions; }

std::string CzoneSettings::getAdditionalSoftwareVersions() {
  return "Core: " + m_appFirmwareVersion + ", Host: " + m_hostArtifactInfo;
}

void CzoneSettings::setEnableBatteryCharger(const bool val) {
  if (m_enable_batterycharger != val) {
    m_enable_batterycharger = val;
    m_settings["EnableBatteryCharger"] = val;
    saveSettings();
  }
}

void CzoneSettings::setUnits(const tUnitTypes unitType, const int32_t value) {
  if (m_t_czonesettings.SetValue(tSetting(unitType, value))) {
    m_settings["Units" + std::to_string(unitType)] = value;
    saveSettings();
  }
}

uint8_t CzoneSettings::getDipswitch() { return m_dipswitch; }
uint8_t CzoneSettings::getSourceAddress() { return m_sourceaddress; }
std::string CzoneSettings::getSerialNumber() { return m_serialnumber; }
std::string CzoneSettings::getFactoryICCID() { return m_factoryICCID; }
std::string CzoneSettings::getFactoryIMEI() { return m_factoryIMEI; }
std::string CzoneSettings::getAPPFirmwareVersion() { return m_appFirmwareVersion; }
std::string CzoneSettings::getHostArtifactInfo() { return m_hostArtifactInfo; }
bool CzoneSettings::getEnableBatteryCharger() { return m_enable_batterycharger; }
int32_t CzoneSettings::getTimeOffset() {
  return boost::any_cast<int32_t>(m_t_czonesettings.Setting(eSettingTimeOffset).Value);
}
float CzoneSettings::getDepthOffset() {
  return boost::any_cast<float>(m_t_czonesettings.Setting(eSettingDepthOffset).Value);
}
float CzoneSettings::getMagneticVariation() {
  return boost::any_cast<float>(m_t_czonesettings.Setting(eSettingMagneticVariation).Value);
}
int32_t CzoneSettings::getUnits(const tUnitTypes unitType) {
  return boost::any_cast<int32_t>(m_t_czonesettings.Setting(unitType).Value);
}
std::string CzoneSettings::getConfigurationPath() {
  return getCzoneConfigPath() + GetJsonValueString("ConfigurationPath");
}
std::string CzoneSettings::getCircuitsLogPath() { return getLogPath() + GetJsonValueString("CircuitsLog"); }
std::string CzoneSettings::getMonitoringLogPath() { return getLogPath() + GetJsonValueString("MonitoringLog"); }
std::string CzoneSettings::getAlarmsLogPath() { return getLogPath() + GetJsonValueString("AlarmsLog"); }
std::string CzoneSettings::getAlarmCustomizedDescriptionPath() {
  return getCzoneConfigPath() + GetJsonValueString("AlarmCustomizedDescription");
}
std::string CzoneSettings::getAlarmDescriptionPath() {
  return getCzoneConfigPath() + GetJsonValueString("AlarmDescription");
}

void CzoneSettings::saveSettings() {
  BOOST_LOG_TRIVIAL(info) << "CZoneSettings: saving czone settings to file";
  saveToFile(m_settings.dump(), m_settingFilePath);
}

std::string CzoneSettings::_getCpuHostId() {
  std::string output = "CPUHOSTID";
  return (output);
}

std::string CzoneSettings::_getSerialNumber() {
  std::string output = "1234567890";
  return (output);
}

std::string CzoneSettings::_getFactoryICCID() {
  std::string output = "unknown";
  const std::string versionFilePath = "/data/factory/hub-telit.iccid";
  std::ifstream versionFile;

  // Check if file exists before opening
  if (std::ifstream(versionFilePath)) {
    try {
      versionFile.open(versionFilePath);
      if (versionFile.is_open()) {
        std::getline(versionFile, output);
        versionFile.close();
        if (output.empty()) {
          output = "unknown";
        }
      }
    } catch (const std::exception &e) {
      if (versionFile.is_open()) {
        versionFile.close();
      }
      BOOST_LOG_TRIVIAL(error) << "CzoneSettings: failed to read ICCID info: " << e.what();
      output = "unknown";
    }
  }
  return output;
}

std::string CzoneSettings::_getFactoryIMEI() {
  std::string output = "unknown";
  const std::string versionFilePath = "/data/factory/hub-telit.imei";
  std::ifstream versionFile;

  // Check if file exists before opening
  if (std::ifstream(versionFilePath)) {
    try {
      versionFile.open(versionFilePath);
      if (versionFile.is_open()) {
        std::getline(versionFile, output);
        versionFile.close();
        if (output.empty()) {
          output = "unknown";
        }
      }
    } catch (const std::exception &e) {
      if (versionFile.is_open()) {
        versionFile.close();
      }
      BOOST_LOG_TRIVIAL(error) << "CzoneSettings: failed to read IMEI info: " << e.what();
      output = "unknown";
    }
  }
  return output;
}

std::string CzoneSettings::_getAPPFirmwareVersion() {
  std::string output = "unknown";
  const std::string versionFilePath = "/data/factory/hub-n2k.version";
  std::ifstream versionFile;

  // Check if file exists before opening
  if (std::ifstream(versionFilePath)) {
    try {
      versionFile.open(versionFilePath);
      if (versionFile.is_open()) {
        std::getline(versionFile, output);
        versionFile.close();
        if (output.empty()) {
          output = "unknown";
        }
      }
    } catch (const std::exception &e) {
      if (versionFile.is_open()) {
        versionFile.close();
      }
      BOOST_LOG_TRIVIAL(error) << "CzoneSettings: failed to read application info: " << e.what();
      output = "unknown";
    }
  }
  return output;
}

std::string CzoneSettings::_getHostArtifactInfo() {
  std::string output = "unknown";
  const std::string versionFilePath = "/data/factory/hub.version";
  std::ifstream versionFile;

  // Check if file exists before opening
  if (std::ifstream(versionFilePath)) {
    try {
      versionFile.open(versionFilePath);
      if (versionFile.is_open()) {
        std::getline(versionFile, output);
        versionFile.close();
        if (output.empty()) {
          output = "unknown";
        }
      }
    } catch (const std::exception &e) {
      if (versionFile.is_open()) {
        versionFile.close();
      }
      BOOST_LOG_TRIVIAL(error) << "CzoneSettings: failed to read host artifact info: " << e.what();
      output = "unknown";
    }
  }
  return output;
}

std::string CzoneSettings::_getHardwareVersions() { return "unknown"; }

void CzoneSettings::factoryReset() {
  std::lock_guard<std::mutex> lock(m_settingsmutex);

  BOOST_LOG_TRIVIAL(debug) << "CzoneSettings: factory reset";

  resetAndInitializeCZonelibSettings();

  m_settings.clear();
  m_settings["SettingsVersion"] = m_settingsversion;
  m_settings["Dipswitch"] = CzoneSystemConstants::DEFAULT_DIPSWITCH;
  m_settings["SourceAddress"] = 0;
  m_settings["TimeOffset"] = getTimeOffset();
  m_settings["DepthOffset"] = getDepthOffset();
  m_settings["MagneticVariation"] = getMagneticVariation();
  m_settings["ServerCertPath"] = std::string("server.crt");
  m_settings["ServerKeyPath"] = std::string("server.key");
  m_settings["RootCertChainPath"] = std::string("ca.crt");
  m_settings["JWTCertPath"] = std::string("server.crt");
  m_settings["JWTKeyPath"] = std::string("server.key");

  m_settings["ConfigurationPath"] = std::string("default.zcf");
  m_settings["CircuitsLog"] = std::string("log_circuits.bin");
  m_settings["MonitoringLog"] = std::string("log_minmax.bin");
  m_settings["AlarmsLog"] = std::string("log_alarm.bin");
  m_settings["AlarmCustomizedDescription"] = std::string("alarmcustomized.json");
  m_settings["AlarmDescription"] = std::string("alarm_desc.bin");
  m_settings["DataDirectory"] = std::string("/data/hub/config/data");
  m_settings["CertDirectory"] = std::string("/data/hub/config/Certs");
  m_settings["KeyDirectory"] = std::string("/data/hub/config/Certs");
  m_settings["SerialNumber"] = _getSerialNumber();
  m_settings["FactoryICCID"] = _getFactoryICCID();
  m_settings["FactoryIMEI"] = _getFactoryIMEI();
  m_settings["APPFirmwareVersion"] = _getAPPFirmwareVersion();
  m_settings["HostArtifactInfo"] = _getHostArtifactInfo();
  m_settings["HardwareVersions"] = _getHardwareVersions();
  m_settings["EnableBatteryCharger"] = false;
  for (uint32_t i = 0; i < eNumUnitTypes; i++) {
    m_settings["Units" + std::to_string(i)] = boost::any_cast<int32_t>(m_t_czonesettings.Setting(tUnitTypes(i)).Value);
  }
}
