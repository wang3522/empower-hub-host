#pragma once

#include <DevelopmentLib/Utils/tSettings.h>
#include <boost/json.hpp>
#include <mutex>

#include "utils/common.h"

class CzoneSettings {
public:
  CzoneSettings(const CzoneSettings &) = delete;
  CzoneSettings(CzoneSettings &&) = delete;
  CzoneSettings &operator=(const CzoneSettings &) = delete;
  CzoneSettings &operator=(const CzoneSettings &&) = delete;
  static CzoneSettings &getInstance();

  void setInsecure(const bool insecure);
  bool insecure() const;

  void setDipswitch(const uint8_t dipswitch);
  void setSourceAddress(const uint8_t sourceAddress);
  void setTimeOffset(const int32_t value);
  void setDepthOffset(const float value);
  void setMagneticVariation(const float value);
  void setEnableBatteryCharger(const bool value);
  void setUnits(const tUnitTypes unitType, const int32_t value);

  uint8_t getDipswitch();
  uint8_t getSourceAddress();
  int32_t getTimeOffset();
  float getDepthOffset();
  float getMagneticVariation();
  bool getEnableBatteryCharger();
  int32_t getUnits(const tUnitTypes unitType);

  std::string getSerialNumber();
  std::string getFactoryICCID();
  std::string getFactoryIMEI();
  std::string getRTFirmwareVersion();
  std::string getHardwareVersions();
  std::string getAdditionalSoftwareVersions();
  std::string getHostArtifactInfo();

  std::string getConfigurationPath();
  std::string getCircuitsLogPath();
  std::string getMonitoringLogPath();
  std::string getAlarmsLogPath();
  std::string getAlarmCustomizedDescriptionPath();
  std::string getAlarmDescriptionPath();

  void factoryReset();
  void resetAndInitializeCZonelibSettings();

private:
  CzoneSettings();
  ~CzoneSettings();

  std::mutex m_filemutex;
  std::mutex m_settingsmutex;

  boost::json::object m_settings;
  std::string m_settingFilePath;
  bool m_insecure;

  uint8_t m_dipswitch;
  uint8_t m_sourceaddress;
  tSettings m_t_czonesettings;
  const int m_settingsversion;

  std::string m_serialnumber;
  std::string m_factoryICCID;
  std::string m_factoryIMEI;
  std::string m_RTFirmwareVersion;
  std::string m_hardwareVersions;
  std::string m_hostArtifactInfo;

  bool m_enable_batterycharger;

  inline void saveSettings();
  bool saveToFile(const std::string &content, const std::string &fileName);
  bool loadFromFile(std::string &output, const std::string &fileName);

  std::string _getCpuHostId();
  std::string _getSerialNumber();
  std::string _getFactoryICCID();
  std::string _getFactoryIMEI();
  std::string _getRTFirmwareVersion();
  std::string _getHostArtifactInfo();
  std::string _getEuropaHardwareVersions();
};