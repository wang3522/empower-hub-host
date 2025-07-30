#pragma once

#include <AnalogueControl/EuropaAnalogueControl.h>

#include <atomic>
#include <future>
#include <memory>
#include <mutex>
#include <string>
#include <thread>
#include <unordered_map>

#include "modules/czone/configdata.h"
#include "modules/czone/czonesettings.h"
#include "modules/dbus/dbusservice.h"
#include "utils/asyncworker.h"
#include "utils/common.h"

class CzoneInterface {
public:
  CzoneInterface(CzoneSettings &settings, std::mutex &canMutex);
  ~CzoneInterface();

  void init(const uint8_t dipswitch, const uint8_t id);
  void event(const tCZoneEventType, void *data, const uint32_t size);
  std::string filename(const tCZoneFileType czoneFile, const tCZoneConfigFileType type);
  void loadfile(const tCZoneFileType czoneFile, uint32_t index, char *buf, uint32_t &length);
  void savefile(const tCZoneFileType czoneFile, const char *buf, uint32_t length);
  void removefile(const tCZoneFileType czoneFile);

  void keyPressed(const uint32_t index, bool on);
  void keyHolding(const uint32_t index);
  void setLevel(const uint32_t index, int8_t level);
  void keyReleasedOrLostKeyFocus(const uint32_t index);
  void controlHVAC(const uint32_t instance, const uint32_t type, const uint32_t value);
  void controlFantasticFan(const uint32_t instance, const uint32_t type, const uint32_t value);
  void controlAudioStereo(const uint32_t instance, const uint32_t type, const uint32_t value);
  void controlShoreFuse(const uint32_t instance, const uint32_t type, const uint32_t value);
  void controlThirdPartyGenerator(const uint32_t instance, const uint32_t type, const uint32_t value);

  ConfigResult getConfig(const ConfigRequest &request);
  ConfigResult getAllConfig();
  Categories getCategories(const CategoryRequest::eCategoryType type);
  AlarmsList alarmList(const bool IsLog, const bool IsRaw = false);

  std::string libraryVersion() const;
  std::string configName() const;

  tCZoneDeviceItem deviceItem(const uint32_t index);

  tCZoneDisplayAlarm alarm(const uint32_t alarmId);
  void alarmAcknowledge(const uint32_t alarmId, const bool accepted);
  void alarmAcknowledgeAllBySeverity(const tCZoneAlarmSeverityType severity);
  bool alarmGetNextUnacknowledged(tCZoneDisplayAlarm *alarm, const uint32_t *alarmIds, const uint32_t length);
  std::string alarmString(const uint32_t alarmId, const tCZoneAlarmStringType type, bool translate);
  tCZoneCircuitButtonIconType circuitButtonInfo(const uint32_t circuitId, const tCZoneCircuitButtonInfoType type,
                                                bool &invert);

  std::vector<CzoneSystemConstants::CZoneUIStruct> displayList(const tCZoneDisplayType type);
  std::vector<CzoneSystemConstants::CZoneUIStruct> displayList(const tCZoneDisplayType type, const uint32_t parentId,
                                                               const uint32_t flags = 0);
  std::vector<CzoneSystemConstants::CZoneUIStruct> displayListNoLock(const tCZoneDisplayType type);
  std::vector<CzoneSystemConstants::CZoneUIStruct> displayListNoLock(const tCZoneDisplayType type,
                                                                     const uint32_t parentId, const uint32_t flags);

  void writeConfig();
  void readConfig(bool force = false, bool configMode = false);

  void setBatteryFull(const uint32_t channelId);
  uint8_t getDipswitch() const;
  void setDipswitch(const int dipswitch);
  void setBacklightLevel(const float backLightLevel);
  void setTimeOffset(const float &timeOffset);
  void setMagneticVariation(const float &magVar);
  void setDepthOffset(const float &depthOffset);
  void setDateTime(const tCZoneTimeData &dateTime);
  void syncDateTime(const int offset);
  void setAlarmLogIndex(int index);
  void setUpdaterState(const tCZoneUpdaterData *data);
  void setUpdaterProgress(const int percent);
  void setEnableBatteryCharger(const bool);
  void setInternetState(const bool isConnected);

  void resetMinMaxLog();
  void resetCircuitLog();
  void resetAlarmLog();

  void engineeringCommand(const uint8_t command, const uint8_t dipswitch, const uint8_t data1, const uint8_t data2,
                          const uint8_t data3, const uint8_t data4);

  void factoryReset();
  void registerEventCallback(std::function<void(const std::shared_ptr<Event> event)> callback);
  void publishEvent(const std::shared_ptr<Event> event);         // sync call (avoid)
  void publishEventAsync(const std::shared_ptr<Event> event);    // use worker queue
  void publishEventOnThread(const std::shared_ptr<Event> event); // use thread
  void registerEventClientsConnectedCallback(std::function<bool(void)> callback);
  bool isEventClientsConnected();
  uint32_t highestEnabledSeverity() const { return m_highestEnabledSeverity; }
  uint32_t highestAcknowledgedSeverity() const { return m_highestAcknowledgedSeverity; }
  //   CZoneSignalSlots::Signal<void()> ValidSystem;
  //   CZoneSignalSlots::Signal<void()> PreLowPowerMode;

  struct ConfigurationInformation {
    uint32_t ConfigurationId;
    uint32_t ConfigurationVersion;
    uint32_t ConfigurationFileVersion;
  };
  void getConfigurationInformation(ConfigurationInformation &info) const;

  struct ConfigGlobalInformation {
    bool SleepEnabled;
    uint32_t SleepCircuitId;
  };
  void getConfigGlobalInformation(ConfigGlobalInformation &info) const;
  void setEngineList(std::map<uint8_t, EngineDevice> engines) { m_engineList = engines; }
  void processRTCoreConfig();
  bool isCZoneSleep() const { return m_czoneSleepFlag; }
  void disableCZoneSleepFlag() { m_czoneSleepFlag = false; }

  // Only called by DisplayExporter tool.
  void setConfigReady() { m_configReady = true; }

  void setWakeUp() { m_wakeUp = true; }
  const RTCoreLogicalIdToDeviceConfig &RTCoreConfig() const { return m_RTCoreConfig; }
  void setWakeUpAlarmList(const AlarmsList &list) {
    m_wakeUp = true;
    m_wakeUpAlarmList = list;
  }

  void registerDbus(std::shared_ptr<DbusService> dbusService);

private:
  struct KeyMapValue {
    bool inUse;
    bool isAssociated;
    bool isSetLevel;
    std::chrono::system_clock::time_point timeStamp;
    std::thread timer;
    std::atomic<bool> timer_cancel{false};

    KeyMapValue() : inUse(false), isAssociated(false), isSetLevel(false), timer_cancel(false) {}

    KeyMapValue(bool inUse, bool isAssociated, bool isSetLevel)
        : inUse(inUse), isAssociated(isAssociated), isSetLevel(isSetLevel), timer_cancel(false) {}

    ~KeyMapValue() {
      if (timer.joinable()) {
        timer_cancel.store(true);
        timer.join();
      }
    }

    KeyMapValue(const KeyMapValue &) = delete;
    KeyMapValue &operator=(const KeyMapValue &) = delete;

    KeyMapValue(KeyMapValue &&other) noexcept
        : inUse(other.inUse),
          isAssociated(other.isAssociated),
          isSetLevel(other.isSetLevel),
          timeStamp(other.timeStamp),
          timer(std::move(other.timer)),
          timer_cancel(other.timer_cancel.load()) {
      other.timer_cancel.store(false);
    }
    KeyMapValue &operator=(KeyMapValue &&other) noexcept {
      if (this != &other) {
        if (timer.joinable()) {
          timer_cancel.store(true);
          timer.join();
        }
        inUse = other.inUse;
        isAssociated = other.isAssociated;
        isSetLevel = other.isSetLevel;
        timeStamp = other.timeStamp;
        timer = std::move(other.timer);
        timer_cancel.store(other.timer_cancel.load());
        other.timer_cancel.store(false);
      }
      return *this;
    }

    inline void cancel() {
      this->timer_cancel.store(true);
      if (this->timer.joinable()) {
        this->timer.join();
      }
      this->timer_cancel.store(false);
    }
  };

  void populateAlarm(Alarm &alarm, const tCZoneDisplayAlarm &displayAlarm, const bool isLog, const bool isConfig);
  void displayAlarmToEvent(const tCZoneDisplayAlarm *const DisplayAlarm, Event &event);
  void engineeringData(const tCZoneEngineeringData *data);

  std::mutex &m_canMutex;
  std::mutex m_keyMutex;
  std::mutex m_dipswitchMutex;
  std::mutex m_configMutex;

  std::unordered_map<uint32_t, KeyMapValue> m_keyMap;
  CzoneSettings &m_czoneSettings;
  int32_t m_lastBacklight;
  uint32_t m_uniqueIdBase;
  uint8_t m_dipswitch;
  ConfigResult m_config;
  bool m_configReady;
  std::vector<std::function<void(const std::shared_ptr<Event> event)>> m_eventCallbacks;
  std::function<bool(void)> m_eventClientsConnectedCallback;
  std::mutex m_alarmStringMutex;
  std::map<uint8_t, EngineDevice> m_engineList;
  uint32_t m_highestEnabledSeverity = eCZoneAlarmSeverityWarning;
  uint32_t m_highestAcknowledgedSeverity = eCZoneAlarmSeverityWarning;
  RTCoreLogicalIdToDeviceConfig m_RTCoreConfig;

  const int m_maxBrightness = 255;
  uint32_t m_lastShunt;
  uint32_t m_lastFault;
  std::future<void> m_preLowPowerModeFire;
  bool m_czoneSleepFlag;
  bool m_wakeUp = false;
  AlarmsList m_wakeUpAlarmList;

  WorkerPool m_workerpool;

  ConfigResult genConfig(const ConfigRequest &request);
};