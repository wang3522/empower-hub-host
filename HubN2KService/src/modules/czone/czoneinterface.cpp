#include <iostream>
#include <sstream>

#include <DevelopmentLib/Utils/tCZoneNmea2kName.h>
#include <DevelopmentLib/Utils/tUnitConversion.h>
#include <Monitoring/tCZoneDataId.h>
#include <Nmea2kMessages/CZoneMessageAppDefs.h>
#include <tCZoneInterface.h>
#include <tNetworkInterface.h>

#include "modules/czone/czoneinterface.h"
#include "utils/logger.h"

#define NumCZoneLibNetworkStatusStrings (18)
const char *CZoneApplicationStateStrings[NumCZoneLibNetworkStatusStrings] = {
    "Starting configuration claim",
    "No configuration available",
    "Configuration successful",
    "Configuration conflict",
    "Dipswitch conflict",
    "No modules with valid configuration detected",
    "Configuration change",
    "Communications Error",
    "Running",
    "Transmitting Configuration",
    "Receiving Configuration",
    "Loading Configuration",
    "Configuration conflict detected on network",
    "Dipswitch conflict detected on network",
    "Conflict resolved",
    "Receiving Firmware",
    "Restarting",
    "Module Identification",
};

CzoneInterface::CzoneInterface(CzoneSettings &settings, std::mutex &m_canMutex)
    : m_czoneSettings(settings), m_canMutex(m_canMutex), m_workerpool() {
  m_configReady = false;
  m_lastBacklight = 0xffff;
  m_lastShunt = UINT32_MAX;
  m_lastFault = UINT32_MAX;
  m_czoneSleepFlag = false;
}

CzoneInterface::~CzoneInterface() {}

void CzoneInterface::publishEventAsync(const std::shared_ptr<Event> event) {
  if (m_workerpool.isShutdown()) {
    BOOST_LOG_TRIVIAL(warning) << "Cannot publish event: system is shutting down";
    return;
  }

  if (m_eventCallbacks.empty()) {
    BOOST_LOG_TRIVIAL(debug) << "No event callbacks registered";
    return;
  }

  auto task = [this, event]() {
    try {
      for (auto &callback : m_eventCallbacks) {
        if (callback) {
          callback(event);
        }
      }
    } catch (const std::exception &e) {
      BOOST_LOG_TRIVIAL(error) << "Event callback exception: " << e.what();
    }
  };

  m_workerpool.addTask(std::move(task));
}

void CzoneInterface::publishEventOnThread(const std::shared_ptr<Event> event) {
  if (m_workerpool.isShutdown()) {
    BOOST_LOG_TRIVIAL(warning) << "Cannot publish event: system is shutting down";
    return;
  }

  if (m_eventCallbacks.empty()) {
    BOOST_LOG_TRIVIAL(debug) << "No event callbacks registered";
    return;
  }

  auto task = [this, event]() {
    try {
      for (auto &callback : m_eventCallbacks) {
        if (callback && !m_workerpool.isShutdown()) {
          callback(event);
        }
      }
    } catch (const std::exception &e) {
      BOOST_LOG_TRIVIAL(error) << "Event callback exception: " << e.what();
    }
  };

  m_workerpool.addTaskOnThread(std::move(task));
}

void CzoneInterface::init(const uint8_t dipswitch, const uint8_t id) {
  m_uniqueIdBase = id;
  m_dipswitch = dipswitch;
}

void CzoneInterface::event(const tCZoneEventType czoneEvent, void *data, const uint32_t sizeOfData) {
  // BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event, type " << std::to_string(czoneEvent);
  auto rawEvent = std::make_shared<Event>(Event(Event::eEventType::eCZoneRaw));
  CZoneRawEvent rawData;

  rawData.set_type(static_cast<uint32_t>(czoneEvent));
  rawData.set_content(data, sizeOfData);
  if (czoneEvent == eCZoneAlarmEvent) {
    tCZoneAlarmEventData *alarmEventData = (tCZoneAlarmEventData *)data;

    switch (alarmEventData->Action) {
    case eCZoneAlarmActionAdded:
    case eCZoneAlarmActionChanged:
    case eCZoneAlarmActionRemoved: {
      rawData.set_rawAlarm((void *)alarmEventData->Alarm, sizeof(tCZoneDisplayAlarm));
    } break;
    default: break;
    }
  } else if (czoneEvent == eCZoneDeviceStatusChanged || czoneEvent == eCZoneDeviceStatusConflict ||
             czoneEvent == eCZoneNetworkDeviceAdded || czoneEvent == eCZoneNetworkDeviceRemoved) {
    tCZoneDeviceStatusData *networkData = static_cast<tCZoneDeviceStatusData *>(data);
    rawData.set_deviceItem((void *)networkData->Device, sizeof(tCZoneDeviceItem));
  }

  rawEvent->set_czoneEvent(std::move(rawData));
  publishEventAsync(rawEvent);

  // BOOST_LOG_TRIVIAL(debug) << "CzoneInterface: EVENT";
  switch (czoneEvent) {
  case eCZoneDetected: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneDetected: CZone Detected on Network";
  } break;

  case eCZoneValidSystem: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneValidSystem: Valid Configuration";
    m_configReady = true;
    auto event = std::make_shared<Event>(Event(Event::eEventType::eConfigChange));

    event->set_content("Valid Configuration");
    publishEventAsync(event);
    // ValidSystem.fire();
    processRTCoreConfig();
  } break;

  case eCZoneBatteryFullSuccess: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneBatteryFullSuccess: Battery Full Success";
    // Battery state of charge command has been set to 100%
    // g_Globals.BatteryStateOfChargeSuccess = CZONE_TRUE;
  } break;

  case eCZoneCalibrationTimeOut: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneCalibrationTimeOut: Battery Calibration Timeout";
    // Battery state of charge command has failed
    // g_Globals.BatteryStateOfChargeTimeout = CZONE_TRUE;
  } break;

  case eCZoneOICommanderUpdate: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneOICommanderUpdate";
    // One or more Circuits has changed states. Schedule update of GUI.
  } break;

  case eCZoneStatusMessage: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneStatusMessage";
    tCZoneStatusData *statusData = static_cast<tCZoneStatusData *>(data);
    // BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneStatusMessage " << std::to_string(statusData->Status);

    // Refer to tCZoneStrings.cpp for Status string table
    if (statusData->Status < NumCZoneLibNetworkStatusStrings) {
      // BOOST_LOG_TRIVIAL(debug) << "CzoneInterface: " << CZoneApplicationStateStrings[statusData->Status] << " "
      //                          << statusData->Show << " " << statusData->Progress << ".";
      if (statusData->Status == 6) {
        auto event = std::make_shared<Event>(Event(Event::eEventType::eConfigChange));
        m_configReady = true;
        event->set_content("Valid Configuration");
        publishEventAsync(event);
        processRTCoreConfig();
      }
    }
  } break;

  case eCZoneLoadFile: {
    tCZoneFileData *fileData = static_cast<tCZoneFileData *>(data);
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneLoadFile type[" << fileData->FileType << "]";

    if (fileData->FileType == 0) {
      m_configReady = false;
    }

    if (fileData->FileType == 0 || fileData->FileType == eCZoneFavouritesFile) {
      loadfile(fileData->FileType, fileData->Index, fileData->Buf, fileData->Length);
    }
  } break;

  case eCZoneSaveFile: {
    tCZoneFileData *fileData = static_cast<tCZoneFileData *>(data);
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneSaveFile type[" << fileData->FileType << "]";

    if (fileData->FileType == 0) {
      savefile(fileData->FileType, fileData->Buf, fileData->Length);
    }
  } break;

  case eCZoneRemoveFile: {
    tCZoneFileData *fileData = static_cast<tCZoneFileData *>(data);
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneRemoveFile type[" << fileData->FileType << "]";

    if (fileData->FileType == 0) {
      removefile(fileData->FileType);
    }
  } break;

  case eCZoneAlarmEvent: {
    tCZoneAlarmEventData *alarmEventData = (tCZoneAlarmEventData *)data;

    switch (alarmEventData->Action) {
    case eCZoneAlarmActionAdded: {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneAlarmEvent::eCZoneAlarmActionAdded";
      auto event = std::make_shared<Event>(Event(Event::eEventType::eAlarmAdded));
      displayAlarmToEvent(alarmEventData->Alarm, *event);
      publishEventAsync(event);
      // Alarm has become active. Add it to an UI alarms table.
    } break;

    case eCZoneAlarmActionChanged: {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneAlarmEvent::eCZoneAlarmActionChanged";
      auto event = std::make_shared<Event>(Event(Event::eEventType::eAlarmChanged));
      displayAlarmToEvent(alarmEventData->Alarm, *event);
      publishEventAsync(event);
      // Alarm status has changed. Eg acknowledged on another display. Update UI
      // alarms table.
    } break;

    case eCZoneAlarmActionRemoved: {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneAlarmEvent::eCZoneAlarmActionRemoved";
      auto event = std::make_shared<Event>(Event(Event::eEventType::eAlarmRemoved));
      displayAlarmToEvent(alarmEventData->Alarm, *event);
      publishEventAsync(event);
      // Alarm is no longer enabled. Remove from UI alarms table.
    } break;

    case eCZoneAlarmActionActivated: {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneAlarmEvent::eCZoneAlarmActionActivated";
      auto event = std::make_shared<Event>(Event(Event::eEventType::eAlarmActivated));
      publishEventAsync(event);
      // An alarm of Standard, Important or Critical has triggered. Use this
      // event to signal the UI to bring up an alarm dialog.

      // Call CZoneAlarmGetNextUnacknowledged to get an array of unacknowledged
      // alarm ids.
    } break;

    case eCZoneAlarmActionDeactivated: {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneAlarmEvent::eCZoneAlarmActionDeactivated";
      auto event = std::make_shared<Event>(Event(Event::eEventType::eAlarmDeactivated));
      publishEventAsync(event);
      // Alarms have cleared, hide alarm dialog if visible.
    } break;

    case eCZoneAlarmActionLogUpdate: {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneAlarmEvent::eCZoneAlarmActionLogUpdate";
      auto event = std::make_shared<Event>(Event(Event::eEventType::eAlarmLogUpdate));
      publishEventAsync(event);
      // Alarms have cleared, hide alarm dialog if visible.
    } break;

    default: break;
    }
  } break;

  case eCZoneAlarmGlobalStatus: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneAlarmGlobalStatus";
    tCZoneAlarmGlobalStatusData *alarmStatusData = (tCZoneAlarmGlobalStatusData *)data;
    m_highestEnabledSeverity = alarmStatusData->HighestEnabledSeverity;
    m_highestAcknowledgedSeverity = alarmStatusData->HighestAcknowledgedSeverity;
    auto event = std::make_shared<Event>(Event(Event::eEventType::eAlarmGlobalStatus));
    event->mutable_globalStatus().set_highestEnabledSeverity(
        static_cast<Alarm::eSeverityType>(alarmStatusData->HighestEnabledSeverity));
    event->mutable_globalStatus().set_highestAcknowledgedSeverity(
        static_cast<Alarm::eSeverityType>(alarmStatusData->HighestAcknowledgedSeverity));
    publishEventAsync(event);
    // Outputs the highest enabled/active alarm severity and highest
    // acknowledged severity
  } break;

  case eCZoneDebug: {
    tCZoneDebugData *debugData = static_cast<tCZoneDebugData *>(data);
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneDebug:"
                             << debugData->Msg; // Outputs a stable 1 second message
  } break;

  case eCZoneValidConfigFile:
  case eCZoneValidConfigFileInBuffer: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneValidConfigFile/eCZoneValidConfigFileInBuffer";
    m_lastFault = UINT32_MAX;
    m_lastShunt = UINT32_MAX;

    CZoneOperation(eCZoneConfigClear);
    CZoneSetValue(eCZoneDipswitch, static_cast<float>(m_dipswitch));

    if (czoneEvent == eCZoneValidConfigFile) {
      CZoneOperation(eCZoneConfigLoad);
    }

    CZoneOperation(eCZoneConfigProcess);
    CZoneOperation(eCZoneDatabaseLoaded);
  } break;

  case eCZoneValidConfigFileNoDipswitch: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneValidConfigFileNoDipswitch";

    // Configuration has been read off the network, but the display has no
    // dipswitch.

    // Signal UI to call DisplayDipswitches function and prompt the user to
    // select a dipswitch.

    // Store the dipswitch value to settings and call SetDipswitch
  } break;

  case eCZonePowerOff: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZonePowerOff";
    // If supported, gracefully power off the display.
  } break;

  case eCZoneStandby: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneStandby";
    auto event = std::make_shared<Event>(Event(Event::eEventType::eSystemLowPowerMode));
    publishEventAsync(event);
    // If supported, go into standby/low power mode.
  } break;

  case eCZoneBacklightUpdate: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneBacklightUpdate";
    printf("eCZoneBacklightUpdate\r\n");
    // If supported, set the backlight

    /*if (g_Globals.BacklightIntegration == CZONE_TRUE)
    {
        tCZoneBacklightEventData* backlightData =
    (tCZoneBacklightEventData*)data;

        if (backlightData->BacklightLevel < 10)
        {
            // standby condition, ignore
        }
        else if (g_Globals.LastBacklight != backlightData->BacklightLevel)
        {
            // Set backlight level
            printf("Level %d\r\n", backlightData->BacklightLevel);
            g_Globals.LastBacklight = backlightData->BacklightLevel;
        }
    }*/
  } break;

  case eCZoneDeviceStatusChanged:
  case eCZoneDeviceStatusConflict:
  case eCZoneCalibrationStatus: {
    BOOST_LOG_TRIVIAL(debug)
        << "CzoneInterface::event::eCZoneDeviceStatusChanged/eCZoneDeviceStatusConflict/eCZoneCalibrationStatus";
    // Not implemented
  } break;

  case eCZoneEngineering: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneEngineering";
    tCZoneEngineeringData *engData = static_cast<tCZoneEngineeringData *>(data);
    engineeringData(engData);
  } break;

  case eCZoneUpdaterData: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneUpdaterData";
    /*tCZoneUpdaterData* updaterData = static_cast<tCZoneUpdaterData*>(data);
    CZoneSetUpdater(updaterData);

    if (updaterData->Status == eCZoneUpdaterStateChecksumVerified)
    {
        updaterReceived = true;
    }*/
  } break;

  case eCZoneDynamicDeviceChanged: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneDynamicDeviceChanged";
    tCZoneDisplayDynamicDevice *device = static_cast<tCZoneDisplayDynamicDevice *>(data);
    if (device->DisplayType == eCZoneStructDisplayGNSS) {
      auto event = std::make_shared<Event>(Event(Event::eEventType::eGNSSConfigChanged));
      publishEventAsync(event);
    } else if (device->DisplayType == eCZoneStructDisplayEngines) {
      auto event = std::make_shared<Event>(Event(Event::eEventType::eEngineConfigChanged));
      publishEventAsync(event);
    }
  } break;

  case eCZoneCalibRequsted: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneCalibRequsted";
    if (m_dipswitch) {
      uint8_t *localdata = (uint8_t *)(data);
      if (localdata[0] == 47) {
        uint8_t channel = localdata[1];
        CZoneSetValue(eCZoneCalRequest, channel);
      }
    }
  } break;

  case eCZoneBlockCanTx: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneBlockCanTx Stop CAN";
    BlockCanTx(true);
  } break;

  case eCZoneReadyToSleep: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event::eCZoneReadyToSleep PreLowPower";
    this->setEnableBatteryCharger(false);
    if (m_czoneSleepFlag) {
      // std::cout << "PreLowPower already done" << std::endl;
      break;
    }
    m_czoneSleepFlag = true;
    // PreLowPowerMode must not be called in event handling, otherwise there
    // will be deadlock. auto ayncFire = [this] { PreLowPowerMode.fire(); };
    // m_PreLowPowerModeFire = std::async(std::launch::async, ayncFire);
    // std::cout << "PreLowPower fire done" << std::endl;
  } break;

  default: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::event: Unknown event type: " << std::to_string(czoneEvent);
  } break;
  }
}

std::string CzoneInterface::filename(const tCZoneFileType czoneFile, const tCZoneConfigFileType type) {
  std::string fileName;

  BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::filename " << std::to_string(czoneFile);

  switch (czoneFile) {
  case eCZoneConfigFile: {
    fileName = m_czoneSettings.getConfigurationPath();
  } break;
  case eCZoneMinMaxLogFile: {
    fileName = m_czoneSettings.getMonitoringLogPath();
  } break;
  case eCZoneCircuitsLogFile: {
    fileName = m_czoneSettings.getCircuitsLogPath();
  } break;
  case eCZoneFirmwareUpdateFile: {
    fileName = std::string("");
  } break;
  case eCZoneAlarmCustomizedDescriptionFile: {
    fileName = m_czoneSettings.getAlarmCustomizedDescriptionPath();
  } break;
  case eCZoneAlarmDescriptionFile: {
    fileName = m_czoneSettings.getAlarmDescriptionPath();
  } break;
  case eCZoneAlarmLogFile: {
    fileName = m_czoneSettings.getAlarmsLogPath();
  } break;
  case eCZoneFavouritesFile: {
    fileName = "";
  } break;
  default: break;
  }
  return fileName;
}

void CzoneInterface::loadfile(const tCZoneFileType czoneFile, uint32_t index, char *buf, uint32_t &length) {
  std::string fileName = filename(czoneFile, eCZoneConfigFileTypeStandard);
  UNUSED(index);
  length = 0;

  // first call (buf == NULL, just return length to allow memory allocation in
  // CZone lib
  if (buf == NULL) {
    FILE *fileHandle = NULL;
    fileHandle = fopen(fileName.c_str(), "rb");

    if (fileHandle != NULL) {
      fseek(fileHandle, 0, SEEK_END);
      length = ftell(fileHandle);
      fclose(fileHandle);
    }
  } else {
    FILE *fileHandle = fopen(fileName.c_str(), "rb");
    if (fileHandle != NULL) {
      fseek(fileHandle, 0, SEEK_END);
      length = ftell(fileHandle);
      fseek(fileHandle, 0L, SEEK_SET);
      auto r = fread(buf, 1, length, fileHandle);

      if (ferror(fileHandle)) {
        length = 0;
      }

      fclose(fileHandle);
    }
  }
}

void CzoneInterface::savefile(const tCZoneFileType czoneFile, const char *buf, uint32_t length) {
  //   if (!boost::filesystem::is_directory("/data")) {
  //     boost::filesystem::create_directories("/data");
  //   }
  std::string fileName = filename(czoneFile, eCZoneConfigFileTypeStandard);
  FILE *fileHandle = fopen(fileName.c_str(), "w+b");
  if (fileHandle != NULL) {
    fwrite(buf, 1, length, fileHandle);
    fclose(fileHandle);
  }
}

void CzoneInterface::removefile(const tCZoneFileType czoneFile) {
  std::string fileName = filename(czoneFile, eCZoneConfigFileTypeStandard);
  BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::removefile, fileName: " << fileName;

  FILE *fileHandle = fopen(fileName.c_str(), "rb");
  if (fileHandle != NULL) {
    fclose(fileHandle);
    if (remove(fileName.c_str()) != 0) {
      BOOST_LOG_TRIVIAL(error) << "Failed to remove file: " << fileName;
    }
  }
}

void CzoneInterface::keyPressed(const uint32_t index, bool on) {
  std::lock_guard<std::mutex> lock(m_keyMutex);
  if (m_keyMap.find(index) == m_keyMap.end()) {
    m_keyMap.try_emplace(index, KeyMapValue{false, false, false});
  }

  // If it is not released from KeyPressed or SetLevel
  if (m_keyMap[index].inUse) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyPressed: index " << index << " is not released yet.";
    return;
  } else {
    m_keyMap[index].inUse = true;
    m_keyMap[index].isAssociated = on;
    m_keyMap[index].isSetLevel = false;
    m_keyMap[index].timeStamp = std::chrono::system_clock::now();
    m_keyMap[index].timer = std::thread([this, index]() -> void {
      m_keyMap[index].timer_cancel.store(false);
      for (size_t i = 0; i < 500; i++) {
        if (m_keyMap[index].timer_cancel.load()) {
          BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyPressed callback: index " << index << " called by cancel().";
          return;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
      }

      if (m_keyMap[index].timer_cancel.load()) {
        BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyPressed callback: index " << index << " called by cancel().";
        return;
      }
      std::lock_guard<std::mutex> lck(this->m_keyMutex);

      m_keyMap[index].inUse = false;
      CZoneKeyReleasedOrLostKeyFocusByIndex(index, m_keyMap[index].isAssociated, m_keyMap[index].isSetLevel,
                                            std::chrono::duration_cast<std::chrono::milliseconds>(
                                                std::chrono::system_clock::now() - m_keyMap[index].timeStamp)
                                                .count());
      return;
    });
    CZoneKeyPressedByIndex(index, on ? CZONE_FALSE : CZONE_TRUE);
  }
}

void CzoneInterface::keyHolding(const uint32_t index) {
  std::lock_guard<std::mutex> lock(m_keyMutex);
  if (m_keyMap.find(index) == m_keyMap.end() || !m_keyMap[index].inUse) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyHolding: index " << index << " is not pressed yet.";
    return;
  } else {
    // gpr_timespec now = gpr_now(GPR_CLOCK_MONOTONIC);
    m_keyMap[index].cancel();
    m_keyMap[index].timer = std::thread([this, index]() -> void {
      m_keyMap[index].timer_cancel.store(false);
      for (size_t i = 0; i < 500; i++) {
        if (m_keyMap[index].timer_cancel.load()) {
          BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyHolding callback: index " << index << " called by cancel().";
          return;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
      }

      if (m_keyMap[index].timer_cancel.load()) {
        BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyHolding callback: index " << index << " called by cancel().";
        return;
      }
      std::lock_guard<std::mutex> lck(this->m_keyMutex);
      m_keyMap[index].inUse = false;
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyHolding callback: index " << index << " is released.";
      CZoneKeyReleasedOrLostKeyFocusByIndex(index, m_keyMap[index].isAssociated, m_keyMap[index].isSetLevel,
                                            std::chrono::duration_cast<std::chrono::milliseconds>(
                                                std::chrono::system_clock::now() - m_keyMap[index].timeStamp)
                                                .count());
    });
  }
}

void CzoneInterface::setLevel(const uint32_t index, int8_t level) {
  std::lock_guard<std::mutex> lock(m_keyMutex);

  if (m_keyMap.find(index) == m_keyMap.end()) {
    m_keyMap.try_emplace(index, KeyMapValue{false, false, false});
  }

  // If the index is called in KeyPressed
  if (m_keyMap[index].inUse && !m_keyMap[index].isSetLevel) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::SetLevel: index " << index
                             << " is called in KeyPressed and not released.";
    return;
  }

  m_keyMap[index].isAssociated = false;
  m_keyMap[index].isSetLevel = true;
  m_keyMap[index].timeStamp = std::chrono::system_clock::now();
  // gpr_timespec now = gpr_now(GPR_CLOCK_MONOTONIC);
  if (m_keyMap[index].inUse && m_keyMap[index].isSetLevel) {
    m_keyMap[index].cancel();
  }
  m_keyMap[index].timer = std::thread([this, index]() -> void {
    m_keyMap[index].timer_cancel.store(false);
    for (size_t i = 0; i < 500; i++) {
      if (m_keyMap[index].timer_cancel.load()) {
        BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::SetLevel callback: index " << index << " called by cancel().";
        return;
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    if (m_keyMap[index].timer_cancel.load()) {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::SetLevel callback: index " << index << " called by cancel().";
      return;
    }
    std::lock_guard<std::mutex> lck(this->m_keyMutex);
    m_keyMap[index].inUse = false;
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::SetLevel callback: index " << index << " is released.";

    CZoneKeyReleasedOrLostKeyFocusByIndex(index, m_keyMap[index].isAssociated, m_keyMap[index].isSetLevel,
                                          std::chrono::duration_cast<std::chrono::milliseconds>(
                                              std::chrono::system_clock::now() - m_keyMap[index].timeStamp)
                                              .count());
  });

  bool isReleased = true;
  if (m_keyMap[index].inUse) {
    isReleased = false;
  } else {
    m_keyMap[index].inUse = true;
  }
  CZoneSetLevelByIndex(index, level, isReleased);
}

void CzoneInterface::keyReleasedOrLostKeyFocus(const uint32_t index) {
  std::lock_guard<std::mutex> lock(m_keyMutex);
  if (m_keyMap.find(index) == m_keyMap.end() || !m_keyMap[index].inUse) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyReleasedOrLostKeyFocus: index " << index << " is not set yet.";
    return;
  } else {
    m_keyMap[index].inUse = false;
    m_keyMap[index].cancel();

    CZoneKeyReleasedOrLostKeyFocusByIndex(index, m_keyMap[index].isAssociated, m_keyMap[index].isSetLevel,
                                          std::chrono::duration_cast<std::chrono::milliseconds>(
                                              std::chrono::system_clock::now() - m_keyMap[index].timeStamp)
                                              .count());
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::KeyReleasedOrLostKeyFocus: index " << index << " is released.";
  }
}

void CzoneInterface::controlHVAC(const uint32_t instance, const uint32_t type, const uint32_t value) {
  auto hvacs = displayListNoLock(eCZoneStructDisplayHvac);

  tCZoneDisplayHvacDevice *pHvac = nullptr;
  for (auto &h : hvacs) {
    if (h.HvacDevice.HvacInstance == instance) {
      pHvac = &h.HvacDevice;
      break;
    }
  }

  if (!pHvac) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlHVAC: instance " << instance << " does not exist.";
    return;
  }

  switch (type) {
  case ControlTypeValueRequest::eHVACType::eOperationMode:
    if (value >= eCZoneHvacOperatingModeEnd) {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlHVAC: OperationMode value " << value << " is not supported.";
      return;
    }
    setLevel(pHvac->OperatingModeId, value);
    keyReleasedOrLostKeyFocus(pHvac->OperatingModeId);
    break;
  case ControlTypeValueRequest::eHVACType::eFanSpeed:
    if (value >= eCZoneHvacFanSpeedOff && value <= eCZoneHvacFanSpeedAuto) {
      setLevel(pHvac->FanSpeedId, value);
      keyReleasedOrLostKeyFocus(pHvac->FanSpeedId);
    } else {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlHVAC: FanSpeed value " << value << " is not supported.";
      return;
    }
    break;
  case ControlTypeValueRequest::eHVACType::eSetTemperature:
    if ((value > pHvac->SetpointTemperatureMaxF) || (value < pHvac->SetpointTemperatureMinF)) {
      BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlHVAC: SetTemperature value " << value << " is out of range.";
      return;
    }
    setLevel(pHvac->SetpointTemperatureId, value);
    keyReleasedOrLostKeyFocus(pHvac->SetpointTemperatureId);
    break;
  default:
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlHVAC: DataProviderControlHVACsType " << value
                             << " is not supported.";
    return;
  }

  return;
}

void CzoneInterface::controlFantasticFan(const uint32_t instance, const uint32_t type, const uint32_t value) {
  auto FantasticFans = displayListNoLock(eCZoneStructDisplayFantasticFan);

  tCZoneDisplayFantasticFanDevice *pFantasticFan = nullptr;
  for (auto &f : FantasticFans) {
    if (f.FantasticFanDevice.Instance == instance) {
      pFantasticFan = &f.FantasticFanDevice;
      break;
    }
  }

  if (!pFantasticFan) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlFantasticFan: instance " << instance << " does not exist.";
    return;
  }

  uint32_t id = 0;
  switch (type) {
  case ControlTypeValueRequest::eFantasticFanType::eDirectionForward:
    id = pFantasticFan->DirectionForwardCircuitId;
    break;
  case ControlTypeValueRequest::eFantasticFanType::eDirectionReverse:
    id = pFantasticFan->DirectionReverseCircuitId;
    break;
  case ControlTypeValueRequest::eFantasticFanType::eLidOpen: id = pFantasticFan->LidOpenCircuitId; break;
  case ControlTypeValueRequest::eFantasticFanType::eLidClose: id = pFantasticFan->LidCloseCircuitId; break;
  case ControlTypeValueRequest::eFantasticFanType::eSpeed:
    setLevel(pFantasticFan->FanCircuitId, value);
    keyReleasedOrLostKeyFocus(pFantasticFan->FanCircuitId);
    return;
  default:
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlFantasticFan: type " << type << " is not supported.";
    return;
  }

  keyPressed(id, value == ControlRequest::eThrowType::eDoubleThrow);
  std::this_thread::sleep_for(std::chrono::milliseconds(50));
  keyReleasedOrLostKeyFocus(id);

  return;
}

void CzoneInterface::controlAudioStereo(const uint32_t instance, const uint32_t type, const uint32_t value) {
  auto Audios = displayListNoLock(eCZoneStructDisplayAudioStereo);

  tCZoneDisplayAudioStereoDevice *pAudio = nullptr;
  for (auto &a : Audios) {
    if (a.AudioStereoDevice.Instance == instance) {
      pAudio = &a.AudioStereoDevice;
      break;
    }
  }

  if (!pAudio) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlAudioStereo: instance " << instance << " does not exist.";
    return;
  }

  uint32_t id = 0;

  switch (type) {
  case ControlTypeValueRequest::eAudioStereoType::ePower:
  case ControlTypeValueRequest::eAudioStereoType::eSource: id = pAudio->CircuitId[0]; break;
  case ControlTypeValueRequest::eAudioStereoType::eMute: id = pAudio->CircuitId[1]; break;
  case ControlTypeValueRequest::eAudioStereoType::eVolumeUp: id = pAudio->CircuitId[3]; break;
  case ControlTypeValueRequest::eAudioStereoType::eVolumeDown: id = pAudio->CircuitId[2]; break;
  case ControlTypeValueRequest::eAudioStereoType::eTrackUp: id = pAudio->CircuitId[6]; break;
  case ControlTypeValueRequest::eAudioStereoType::eTrackDown: id = pAudio->CircuitId[4]; break;
  case ControlTypeValueRequest::eAudioStereoType::ePlay: id = pAudio->CircuitId[5]; break;
  default:
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlAudioStereo: type " << type << " is not supported.";
    return;
  }

  keyPressed(id, value == ControlRequest::eThrowType::eDoubleThrow);
  if (type == ControlTypeValueRequest::eAudioStereoType::ePower) {
    std::this_thread::sleep_for(std::chrono::milliseconds(350));
    keyHolding(id);
    std::this_thread::sleep_for(std::chrono::milliseconds(350));
  } else {
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
  }
  keyReleasedOrLostKeyFocus(id);

  return;
}

void CzoneInterface::controlShoreFuse(const uint32_t instance, const uint32_t type, const uint32_t value) {
  auto ShoreFuses = displayListNoLock(eCZoneStructDisplayShoreFuse);

  tCZoneDisplayShoreFuseDevice *pShoreFuse = nullptr;
  for (auto &s : ShoreFuses) {
    if (s.ShoreFuseDevice.ChargerInstance == instance) {
      pShoreFuse = &s.ShoreFuseDevice;
      break;
    }
  }

  if (!pShoreFuse) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlShoreFuse: instance " << instance << " does not exist.";
    return;
  }

  uint32_t id = 0;
  switch (type) {
  case ControlTypeValueRequest::eShoreFuseType::eControl: id = pShoreFuse->ShoreFuseControlId; break;
  default:
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlShoreFuse: type " << type << " is not supported.";
    return;
  }

  keyPressed(id, value == ControlRequest::eThrowType::eDoubleThrow);
  std::this_thread::sleep_for(std::chrono::milliseconds(50));
  keyReleasedOrLostKeyFocus(id);

  return;
}

void CzoneInterface::controlThirdPartyGenerator(const uint32_t instance, const uint32_t type, const uint32_t value) {
  auto generators = displayListNoLock(eCZoneStructDisplayThirdPartyGenerator);

  tCZoneDisplayThirdPartyGeneratorDevice *pGenerator = nullptr;
  for (auto &g : generators) {
    if (g.ThirdPartyGeneratorDevice.SignalInstance == instance) {
      pGenerator = &g.ThirdPartyGeneratorDevice;
      break;
    }
  }

  if (!pGenerator) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlThirdPartyGenerator: instance " << instance
                             << " does not exist.";
    return;
  }

  uint32_t id = 0;
  switch (type) {
  case ControlTypeValueRequest::eThirdPartyGeneratorType::eStart: id = pGenerator->StartControlId; break;
  case ControlTypeValueRequest::eThirdPartyGeneratorType::eStop: id = pGenerator->StopControlId; break;
  default: BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::ControlAwning: type " << type << " is not supported."; return;
  }

  keyPressed(id, value == ControlRequest::eThrowType::eDoubleThrow);
  std::this_thread::sleep_for(std::chrono::milliseconds(50));
  keyReleasedOrLostKeyFocus(id);

  return;
}

auto createInstance(const uint8_t instance) {
  auto i = Instance();
  i.set_instance(static_cast<uint32_t>(instance));
  i.set_enabled(instance < CZONE_NUMBER_OF_INSTANCES);
  return i;
}

void addInstance(Instance &t, const uint8_t instance) { t = createInstance(instance); }

ConfigResult CzoneInterface::genConfig(const ConfigRequest &request) {
  std::lock_guard<std::mutex> lock(m_configMutex);

  if (m_configReady) {
    m_config.set_status(ConfigResult::eConfigResultStatus::eOk);
  } else {
    m_config.set_status(ConfigResult::eConfigResultStatus::eNotReady);
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig: CZone configuration is not loaded.";
    return m_config;
  }

  auto addLimit = [](bool enabled, float &on, float &off, const uint32_t id) -> AlarmLimit {
    auto limit = AlarmLimit();
    limit.enabled = enabled;
    limit.on = on;
    limit.off = off;
    limit.id = static_cast<uint32_t>(id);
    return limit;
  };

  auto createDataId = [](const uint32_t id) {
    auto i = DataId(static_cast<uint32_t>(id), id != CZONE_INVALID_CIRCUIT_INDEX);
    return i;
  };

  switch (request.get_type()) {
  case ConfigRequest::eConfigType::eAlarms: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eAlarms";
    auto alarms = displayListNoLock(eCZoneStructDisplayAlarmConfig);
    for (auto &a : alarms) {
      auto &alarm = m_config.add_mutable_alarms();
      populateAlarm(alarm, a.Alarm, false, true);
    }
  } break;
  case ConfigRequest::eConfigType::eDC: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eDC";
    auto dcs = displayListNoLock(eCZoneStructDisplayMeteringDC);
    for (auto &d : dcs) {
      auto &dc = m_config.add_mutable_dcs();
      dc.set_displayType(static_cast<ConfigRequest::eConfigType>(d.MeteringDevice.DisplayType));
      dc.set_id(d.MeteringDevice.Id);
      dc.set_nameUTF8(d.MeteringDevice.NameUTF8);
      addInstance(dc.mutable_instance(), d.MeteringDevice.Instance);
      dc.set_nominalVoltage(d.MeteringDevice.NominalVoltage);
      dc.set_address(d.MeteringDevice.Address);
      dc.set_capacity(d.MeteringDevice.Capacity);
      dc.set_warningLow(d.MeteringDevice.WarningLow);
      dc.set_warningHigh(d.MeteringDevice.WarningHigh);
      dc.set_lowLimit(addLimit(d.MeteringDevice.LimitEnabledMask & eCZoneLowLimit, d.MeteringDevice.LowOnLimit,
                               d.MeteringDevice.LowOffLimit, d.MeteringDevice.LowAlarmId));
      dc.set_veryLowLimit(addLimit(d.MeteringDevice.LimitEnabledMask & eCZoneVeryLowLimit,
                                   d.MeteringDevice.VeryLowOnLimit, d.MeteringDevice.VeryLowOffLimit,
                                   d.MeteringDevice.VeryLowAlarmId));
      dc.set_highLimit(addLimit(d.MeteringDevice.LimitEnabledMask & eCZoneHighLimit, d.MeteringDevice.HighOnLimit,
                                d.MeteringDevice.HighOffLimit, d.MeteringDevice.HighAlarmId));
      dc.set_veryHighLimit(addLimit(d.MeteringDevice.LimitEnabledMask & eCZoneVeryHighLimit,
                                    d.MeteringDevice.VeryHighOnLimit, d.MeteringDevice.VeryHighOffLimit,
                                    d.MeteringDevice.VeryHighAlarmId));
      dc.set_lowVoltage(addLimit(d.MeteringDevice.LimitEnabledMask & eCZoneLowVoltage, d.MeteringDevice.LowVoltageOn,
                                 d.MeteringDevice.LowVoltageOff, d.MeteringDevice.LowVoltageAlarmId));
      dc.set_veryLowVoltage(addLimit(d.MeteringDevice.LimitEnabledMask & eCZoneVeryLowVoltage,
                                     d.MeteringDevice.VeryLowVoltageOn, d.MeteringDevice.VeryLowVoltageOff,
                                     d.MeteringDevice.VeryLowVoltageAlarmId));
      dc.set_highVoltage(addLimit(d.MeteringDevice.LimitEnabledMask & eCZoneHighVoltage, d.MeteringDevice.HighVoltageOn,
                                  d.MeteringDevice.HighVoltageOff, d.MeteringDevice.HighVoltageAlarmId));
      dc.set_canResetCapacity(static_cast<bool>(d.MeteringDevice.CanResetCapacity == CZONE_TRUE));
      dc.set_dcType(
          static_cast<MeteringDevice::eDCType>((d.MeteringDevice.Capabilities >> 24) & CZONE_TYPE_MASK_STRUCT));
      dc.set_showVoltage((d.MeteringDevice.Capabilities & CZONE_SHOW_VOLTS));
      dc.set_showCurrent((d.MeteringDevice.Capabilities & CZONE_SHOW_CURRENT));
      dc.set_showStateOfCharge((d.MeteringDevice.Capabilities & CZONE_SHOW_STATE_OF_CHARGE));
      dc.set_showTemperature((d.MeteringDevice.Capabilities & CZONE_SHOW_TEMPERATURE));
      dc.set_showTimeOfRemaining((d.MeteringDevice.Capabilities & CZONE_SHOW_TIME_REMAINING));
    }
  } break;
  case ConfigRequest::eConfigType::eAC: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eAC";
    auto acs = displayListNoLock(eCZoneStructDisplayMeteringAC);
    for (auto &a : acs) {
      auto &ac = m_config.add_mutable_acs();
      ac.set_displayType(static_cast<ConfigRequest::eConfigType>(a.MeteringDevice.DisplayType));
      ac.set_id(a.MeteringDevice.Id);
      ac.set_nameUTF8(a.MeteringDevice.NameUTF8);
      addInstance(ac.mutable_instance(), a.MeteringDevice.Instance);
      ac.set_line(static_cast<MeteringDevice::eACLine>(a.MeteringDevice.Line));
      ac.set_output(a.MeteringDevice.Output == CZONE_TRUE);
      ac.set_nominalVoltage(a.MeteringDevice.NominalVoltage);
      ac.set_nominalFrequency(a.MeteringDevice.NominalFrequency);
      ac.set_address(a.MeteringDevice.Address);
      ac.set_lowLimit(addLimit(a.MeteringDevice.LimitEnabledMask & eCZoneLowLimit, a.MeteringDevice.LowOnLimit,
                               a.MeteringDevice.LowOffLimit, a.MeteringDevice.LowAlarmId));
      ac.set_highLimit(addLimit(a.MeteringDevice.LimitEnabledMask & eCZoneHighLimit, a.MeteringDevice.HighOnLimit,
                                a.MeteringDevice.HighOffLimit, a.MeteringDevice.HighAlarmId));
      ac.set_veryHighLimit(addLimit(a.MeteringDevice.LimitEnabledMask & eCZoneVeryHighLimit,
                                    a.MeteringDevice.VeryHighOnLimit, a.MeteringDevice.VeryHighOffLimit,
                                    a.MeteringDevice.VeryHighAlarmId));
      ac.set_highVoltage(addLimit(a.MeteringDevice.LimitEnabledMask & eCZoneHighVoltage, a.MeteringDevice.HighVoltageOn,
                                  a.MeteringDevice.HighVoltageOff, a.MeteringDevice.HighVoltageAlarmId));
      ac.set_frequency(addLimit(a.MeteringDevice.LimitEnabledMask & eCZoneVeryHighLimit, a.MeteringDevice.FreqeuncyOn,
                                a.MeteringDevice.FreqeuncyOff, a.MeteringDevice.FrequencyErrorAlarmId));
      ac.set_showVoltage((a.MeteringDevice.Capabilities & CZONE_SHOW_VOLTS));
      ac.set_showCurrent((a.MeteringDevice.Capabilities & CZONE_SHOW_CURRENT));
      ac.set_acType(static_cast<MeteringDevice::eACType>(a.MeteringDevice.AcType));
    }
  } break;
  case ConfigRequest::eConfigType::ePressure: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::ePressure";
    auto pressures = displayListNoLock(eCZoneStructDisplayMonitoringPressure);
    for (auto &p : pressures) {
      auto &pressure = m_config.add_mutable_pressures();
      pressure.set_displayType(static_cast<ConfigRequest::eConfigType>(p.MonitoringDevice.DisplayType));
      pressure.set_id(p.MonitoringDevice.Id);
      pressure.set_nameUTF8(p.MonitoringDevice.NameUTF8);
      addInstance(pressure.mutable_instance(), p.MonitoringDevice.Instance);
      pressure.set_pressureType(static_cast<MonitoringType::ePressureType>(p.MonitoringDevice.Type));
      pressure.set_circuitId(createDataId(p.MonitoringDevice.CircuitId));
      pressure.set_switchType(static_cast<CircuitDevice::eSwitchType>(p.MonitoringDevice.SwitchType));
      pressure.set_confirmDialog(static_cast<CircuitDevice::eConfirmType>(p.MonitoringDevice.ConfirmDialog));
      pressure.set_circuitNameUTF8(p.MonitoringDevice.CircuitNameUTF8);
      pressure.set_atmosphericPressure((p.MonitoringDevice.AtmosphericPressure == CZONE_TRUE));
      pressure.set_lowLimit(addLimit(p.MonitoringDevice.LimitEnabledMask & eCZoneLowLimit,
                                     p.MonitoringDevice.LowOnLimit, p.MonitoringDevice.LowOffLimit,
                                     p.MonitoringDevice.LowAlarmId));
      pressure.set_veryLowLimit(addLimit(p.MonitoringDevice.LimitEnabledMask & eCZoneVeryLowLimit,
                                         p.MonitoringDevice.VeryLowOnLimit, p.MonitoringDevice.VeryLowOffLimit,
                                         p.MonitoringDevice.VeryLowAlarmId));
      pressure.set_highLimit(addLimit(p.MonitoringDevice.LimitEnabledMask & eCZoneHighLimit,
                                      p.MonitoringDevice.HighOnLimit, p.MonitoringDevice.HighOffLimit,
                                      p.MonitoringDevice.HighAlarmId));
      pressure.set_veryHighLimit(addLimit(p.MonitoringDevice.LimitEnabledMask & eCZoneVeryHighLimit,
                                          p.MonitoringDevice.VeryHighOnLimit, p.MonitoringDevice.VeryHighOffLimit,
                                          p.MonitoringDevice.VeryHighAlarmId));
      pressure.set_address(p.MonitoringDevice.Address);
    }
  } break;
  case ConfigRequest::eConfigType::eTank: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eTank";
    auto tanks = displayListNoLock(eCZoneStructDisplayMonitoringTank);
    for (auto &t : tanks) {
      auto &tank = m_config.add_mutable_tanks();
      tank.set_displayType(static_cast<ConfigRequest::eConfigType>(t.MonitoringDevice.DisplayType));
      tank.set_id(t.MonitoringDevice.Id);
      tank.set_nameUTF8(t.MonitoringDevice.NameUTF8);
      addInstance(tank.mutable_instance(), t.MonitoringDevice.Instance);
      tank.set_tankType(static_cast<MonitoringType::eTankType>(t.MonitoringDevice.Type));
      tank.set_circuitId(createDataId(t.MonitoringDevice.CircuitId));
      tank.set_switchType(static_cast<CircuitDevice::eSwitchType>(t.MonitoringDevice.SwitchType));
      tank.set_confirmDialog(static_cast<CircuitDevice::eConfirmType>(t.MonitoringDevice.ConfirmDialog));
      tank.set_circuitNameUTF8(t.MonitoringDevice.CircuitNameUTF8);
      tank.set_tankCapacity(t.MonitoringDevice.Capacity);
      tank.set_lowLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneLowLimit, t.MonitoringDevice.LowOnLimit,
                                 t.MonitoringDevice.LowOffLimit, t.MonitoringDevice.LowAlarmId));
      tank.set_veryLowLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneVeryLowLimit,
                                     t.MonitoringDevice.VeryLowOnLimit, t.MonitoringDevice.VeryLowOffLimit,
                                     t.MonitoringDevice.VeryLowAlarmId));
      tank.set_highLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneHighLimit, t.MonitoringDevice.HighOnLimit,
                                  t.MonitoringDevice.HighOffLimit, t.MonitoringDevice.HighAlarmId));
      tank.set_veryHighLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneVeryHighLimit,
                                      t.MonitoringDevice.VeryHighOnLimit, t.MonitoringDevice.VeryHighOffLimit,
                                      t.MonitoringDevice.VeryHighAlarmId));
      tank.set_address(t.MonitoringDevice.Address);
    }
  } break;
  case ConfigRequest::eConfigType::eTemperature: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eTemperature";
    auto temperatures = displayListNoLock(eCZoneStructDisplayMonitoringTemperature);
    for (auto &t : temperatures) {
      auto &temperature = m_config.add_mutable_temperatures();
      temperature.set_displayType(static_cast<ConfigRequest::eConfigType>(t.MonitoringDevice.DisplayType));
      temperature.set_id(t.MonitoringDevice.Id);
      temperature.set_nameUTF8(t.MonitoringDevice.NameUTF8);
      addInstance(temperature.mutable_instance(), t.MonitoringDevice.Instance);
      temperature.set_temperatureType(static_cast<MonitoringType::eTemperatureType>(t.MonitoringDevice.Type));
      temperature.set_circuitId(createDataId(t.MonitoringDevice.CircuitId));
      temperature.set_switchType(static_cast<CircuitDevice::eSwitchType>(t.MonitoringDevice.SwitchType));
      temperature.set_confirmDialog(static_cast<CircuitDevice::eConfirmType>(t.MonitoringDevice.ConfirmDialog));
      temperature.set_circuitNameUTF8(t.MonitoringDevice.CircuitNameUTF8);
      temperature.set_highTemperature((t.MonitoringDevice.HighTemperature == CZONE_TRUE));
      temperature.set_lowLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneLowLimit,
                                        t.MonitoringDevice.LowOnLimit, t.MonitoringDevice.LowOffLimit,
                                        t.MonitoringDevice.LowAlarmId));
      temperature.set_veryLowLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneVeryLowLimit,
                                            t.MonitoringDevice.VeryLowOnLimit, t.MonitoringDevice.VeryLowOffLimit,
                                            t.MonitoringDevice.VeryLowAlarmId));
      temperature.set_highLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneHighLimit,
                                         t.MonitoringDevice.HighOnLimit, t.MonitoringDevice.HighOffLimit,
                                         t.MonitoringDevice.HighAlarmId));
      temperature.set_veryHighLimit(addLimit(t.MonitoringDevice.LimitEnabledMask & eCZoneVeryHighLimit,
                                             t.MonitoringDevice.VeryHighOnLimit, t.MonitoringDevice.VeryHighOffLimit,
                                             t.MonitoringDevice.VeryHighAlarmId));
      temperature.set_address(t.MonitoringDevice.Address);
    }
  } break;
  case ConfigRequest::eConfigType::eACMain: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eACMain";
    auto acmains = displayListNoLock(eCZoneStructDisplayACMains);
    for (auto &a : acmains) {
      auto &acmain = m_config.add_mutable_acMains();
      acmain.set_displayType(static_cast<ConfigRequest::eConfigType>(a.ACMainsDevice.DisplayType));
      acmain.set_id(static_cast<uint32_t>(a.ACMainsDevice.Id));
      acmain.set_nameUTF8(a.ACMainsDevice.NameUTF8);
      acmain.set_dipswitch(static_cast<uint32_t>(a.ACMainsDevice.Dipswitch));
      for (uint32_t i = 0; i < a.ACMainsDevice.NumberOfContactors; i++) {
        auto &contactor = acmain.add_mutable_contactor();
        contactor.set_systemStateId(static_cast<uint32_t>(a.ACMainsDevice.Contactors[i].SystemStateId));
        contactor.set_nameUTF8(a.ACMainsDevice.Contactors[i].NameUTF8);
        contactor.set_contactorId(createDataId(a.ACMainsDevice.Contactors[i].ContactorId));
        contactor.set_contactorToggleId(createDataId(a.ACMainsDevice.Contactors[i].ContactorToggleId));
        contactor.set_ac1Id(createDataId(a.ACMainsDevice.Contactors[i].AC1Id));
        contactor.set_ac2Id(createDataId(a.ACMainsDevice.Contactors[i].AC2Id));
        contactor.set_ac3Id(createDataId(a.ACMainsDevice.Contactors[i].AC3Id));
        contactor.set_displayIndex(static_cast<uint32_t>(a.ACMainsDevice.Contactors[i].DisplayIndex));
        contactor.set_loadGroupIndex(static_cast<uint32_t>(a.ACMainsDevice.Contactors[i].LoadGroupIndex));
        contactor.set_loadGroupParallelIndex(
            static_cast<uint32_t>(a.ACMainsDevice.Contactors[i].LoadGroupParallelIndex));
        contactor.set_isParallel((a.ACMainsDevice.Contactors[i].Parallel == CZONE_TRUE));
        contactor.set_acInputType(
            static_cast<ACMainContactorDevice::eACInputType>(a.ACMainsDevice.Contactors[i].ACInputType));
      }
      for (uint32_t i = 0; i < a.ACMainsDevice.NumberOfLoadGroups; i++) {
        auto &loadgroup = acmain.add_mutable_loadGroup();
        loadgroup.set_loadGroupIndex(static_cast<uint32_t>(a.ACMainsDevice.LoadGroups[i].LoadGroupIndex));
        loadgroup.set_nameUTF8(a.ACMainsDevice.LoadGroups[i].NameUTF8);
      }
    }
  } break;
  case ConfigRequest::eConfigType::eInverterCharger: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eInverterCharger";
    auto inverterchargers = displayListNoLock(eCZoneStructDisplayInverterCharger);
    for (auto &i : inverterchargers) {
      auto &invertercharger = m_config.add_mutable_inverterChargers();
      invertercharger.set_displayType(static_cast<ConfigRequest::eConfigType>(i.InverterChargerDevice.DisplayType));
      invertercharger.set_id(static_cast<uint32_t>(i.InverterChargerDevice.Id));
      invertercharger.set_nameUTF8(i.InverterChargerDevice.NameUTF8);
      invertercharger.mutable_inverterInstance().set_instance(i.InverterChargerDevice.InverterInstance);
      invertercharger.mutable_chargerInstance().set_instance(i.InverterChargerDevice.ChargerInstance);
      invertercharger.set_model(static_cast<uint32_t>(i.InverterChargerDevice.Model));
      invertercharger.set_type(static_cast<uint32_t>(i.InverterChargerDevice.Type));
      invertercharger.set_subType(static_cast<uint32_t>(i.InverterChargerDevice.SubType));
      invertercharger.set_inverterACId(createDataId(i.InverterChargerDevice.InverterACId));
      invertercharger.set_inverterCircuitId(createDataId(i.InverterChargerDevice.InverterCircuitId));
      invertercharger.set_inverterToggleCircuitId(createDataId(i.InverterChargerDevice.InverterToggleCircuitId));
      invertercharger.set_chargerACId(createDataId(i.InverterChargerDevice.ChargerACId));
      invertercharger.set_chargerCircuitId(createDataId(i.InverterChargerDevice.ChargerCircuitId));
      invertercharger.set_chargerToggleCircuitId(createDataId(i.InverterChargerDevice.ChargerToggleCircuitId));
      invertercharger.set_batteryBank1Id(createDataId(i.InverterChargerDevice.BatteryBank1Id));
      invertercharger.set_batteryBank2Id(createDataId(i.InverterChargerDevice.BatteryBank2Id));
      invertercharger.set_batteryBank3Id(createDataId(i.InverterChargerDevice.BatteryBank3Id));
      invertercharger.set_positionColumn(
          static_cast<uint32_t>((i.InverterChargerDevice.SmartTerminalOutputVoltage & 0xff00) >> 8));
      invertercharger.set_positionRow(static_cast<uint32_t>(i.InverterChargerDevice.SmartTerminalOutputVoltage & 0xff));
      invertercharger.set_clustered((i.InverterChargerDevice.Dc3DcOutputCurrentLimit & (0x1 << 15)) ? true : false);
      invertercharger.set_primary((i.InverterChargerDevice.Dc3DcOutputCurrentLimit & (0x1 << 14)) ? true : false);
      invertercharger.set_primaryPhase((i.InverterChargerDevice.Dc3DcOutputCurrentLimit & (0x3 << 8)) >> 8);
      invertercharger.set_deviceInstance(i.InverterChargerDevice.Dc3DcOutputCurrentLimit & 0xff);
      invertercharger.set_dipswitch(i.InverterChargerDevice.Dipswitch);
      invertercharger.set_channelIndex(i.InverterChargerDevice.ChannelIndex);
    }
  } break;
  case ConfigRequest::eConfigType::eHVAC: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eHVAC";
    auto hvacs = displayListNoLock(eCZoneStructDisplayHvac);
    for (auto &h : hvacs) {
      auto &hvac = m_config.add_mutable_hvacs();
      hvac.set_displayType(static_cast<ConfigRequest::eConfigType>(h.HvacDevice.DisplayType));
      hvac.set_id(static_cast<uint32_t>(h.HvacDevice.Id));
      hvac.set_nameUTF8(h.HvacDevice.NameUTF8);
      addInstance(hvac.mutable_instance(), h.HvacDevice.HvacInstance);
      hvac.set_operatingModeId(createDataId(h.HvacDevice.OperatingModeId));
      hvac.set_fanModeId(createDataId(h.HvacDevice.FanModeId));
      hvac.set_fanSpeedId(createDataId(h.HvacDevice.FanSpeedId));
      hvac.set_temperatureMonitoringId(createDataId(h.HvacDevice.SetpointTemperatureId));
      hvac.set_operatingModeToggleId(createDataId(h.HvacDevice.OperatingModeToggleId));
      hvac.set_fanModeToggleId(createDataId(h.HvacDevice.FanModeToggleId));
      hvac.set_fanSpeedToggleId(createDataId(h.HvacDevice.FanSpeedToggleId));
      hvac.set_setpointTemperatureToggleId(createDataId(h.HvacDevice.SetpointTemperatureToggleId));
      hvac.set_temperatureMonitoringId(createDataId(h.HvacDevice.TemperatureMonitoringId));
      hvac.set_fanSpeedCount(static_cast<uint32_t>(h.HvacDevice.FanSpeedCount));
      hvac.set_operatingModesMask(static_cast<uint32_t>(h.HvacDevice.OperatingModesMask));
      hvac.set_model(static_cast<uint32_t>(h.HvacDevice.Model));
      hvac.mutable_temperatureInstance().set_instance(h.HvacDevice.TemperatureInstance);

      float minC = tTemperatureConversions::ToCelsius(static_cast<float>(h.HvacDevice.SetpointTemperatureMinF),
                                                      tTemperatureConversions::Fahrenheit);
      float maxC = tTemperatureConversions::ToCelsius(static_cast<float>(h.HvacDevice.SetpointTemperatureMaxF),
                                                      tTemperatureConversions::Fahrenheit);
      hvac.set_setpointTemperatureMin(minC);
      hvac.set_setpointTemperatureMax(maxC);
      hvac.set_fanSpeedOffModesMask(static_cast<uint32_t>(h.HvacDevice.FanSpeedOffModesMask));
      hvac.set_fanSpeedAutoModesMask(static_cast<uint32_t>(h.HvacDevice.FanSpeedAutoModesMask));
      hvac.set_fanSpeedManualModesMask(static_cast<uint32_t>(h.HvacDevice.FanSpeedManualModesMask));
    }
  } break;
  case ConfigRequest::eConfigType::eZipdeeAwning: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eZipdeeAwning";
    auto awnings = displayListNoLock(eCZoneStructDisplayZipdeeAwning);
    for (auto &a : awnings) {
      auto &awning = m_config.add_mutable_zipdeeAwnings();
      awning.set_displayType(static_cast<ConfigRequest::eConfigType>(a.AwningDevice.DisplayType));
      awning.set_id(static_cast<uint32_t>(a.AwningDevice.Id));
      awning.set_nameUTF8(a.AwningDevice.NameUTF8);
      addInstance(awning.mutable_instance(), a.AwningDevice.Instance);
      awning.set_openId(createDataId(a.AwningDevice.OpenId));
      awning.set_closeId(createDataId(a.AwningDevice.CloseId));
      awning.set_tiltLeftId(createDataId(a.AwningDevice.TiltLeft));
      awning.set_tiltRightId(createDataId(a.AwningDevice.TiltRight));
      for (uint32_t i = 0; i < 3; i++) {
        auto &signal = awning.add_mutable_binarySignal();
        signal.set_dataType(static_cast<uint32_t>(a.AwningDevice.Signals[i].DataType));
        signal.set_dipswitch(static_cast<uint32_t>(a.AwningDevice.Signals[i].Dipswitch));
        signal.set_bit(static_cast<uint32_t>(a.AwningDevice.Signals[i].Bit));
      }
    }
  } break;
  case ConfigRequest::eConfigType::eThirdPartyGenerator: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eThirdPartyGenerator";
    auto generators = displayListNoLock(eCZoneStructDisplayThirdPartyGenerator);
    for (auto &g : generators) {
      auto &generator = m_config.add_mutable_thirdPartyGenerators();
      generator.set_displayType(static_cast<ConfigRequest::eConfigType>(g.ThirdPartyGeneratorDevice.DisplayType));
      generator.set_id(static_cast<uint32_t>(g.ThirdPartyGeneratorDevice.Id));
      generator.set_nameUTF8(g.ThirdPartyGeneratorDevice.NameUTF8);
      addInstance(generator.mutable_instance(), g.ThirdPartyGeneratorDevice.SignalInstance);
      generator.set_startControlId(createDataId(g.ThirdPartyGeneratorDevice.StartControlId));
      generator.set_stopControlId(createDataId(g.ThirdPartyGeneratorDevice.StopControlId));
      generator.mutable_associatedAcMetersInstance().set_instance(
          g.ThirdPartyGeneratorDevice.AssociatedAcMetersInstance);
      generator.set_acMeterLine1Id(createDataId(g.ThirdPartyGeneratorDevice.AcMeterLine1Id));
      generator.set_acMeterLine2Id(createDataId(g.ThirdPartyGeneratorDevice.AcMeterLine2Id));
      generator.set_acMeterLine3Id(createDataId(g.ThirdPartyGeneratorDevice.AcMeterLine3Id));
    }
  } break;
  case ConfigRequest::eConfigType::eTyrePressure: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eTyrePressure";
    auto tyrepressures = displayListNoLock(eCZoneStructDisplayTyrePressure);
    for (auto &t : tyrepressures) {
      auto &tyrepressure = m_config.add_mutable_tyrePressures();
      tyrepressure.set_displayType(static_cast<ConfigRequest::eConfigType>(t.TyrePressure.DisplayType));
      tyrepressure.set_id(static_cast<uint32_t>(t.TyrePressure.Id));
      tyrepressure.set_nameUTF8(t.TyrePressure.NameUTF8);
      addInstance(tyrepressure.mutable_instance(), t.TyrePressure.Instance);
      tyrepressure.set_numberOfAxles(static_cast<uint32_t>(t.TyrePressure.NumberOfAxles));
      tyrepressure.set_tyresAxle1(static_cast<uint32_t>(t.TyrePressure.TyresAxle1));
      tyrepressure.set_tyresAxle2(static_cast<uint32_t>(t.TyrePressure.TyresAxle2));
      tyrepressure.set_tyresAxle3(static_cast<uint32_t>(t.TyrePressure.TyresAxle3));
      tyrepressure.set_tyresAxle4(static_cast<uint32_t>(t.TyrePressure.TyresAxle4));
      tyrepressure.set_spareAxle(static_cast<uint32_t>(t.TyrePressure.SpareAxle));
      for (uint32_t i = 0; i < MAX_TYRE_INSTANCES; i++) {
        auto &tyreinstance = tyrepressure.add_mutable_tyreInstance();
        tyreinstance.set_instance(static_cast<uint32_t>(t.TyrePressure.TyreInstances[i]));
        tyreinstance.set_enabled(t.TyrePressure.TyreInstances[i] < CZONE_NUMBER_OF_INSTANCES);
      }
      for (uint32_t i = 0; i < MAX_TYRE_INSTANCES; i++) {
        auto &tyreinstancespare = tyrepressure.add_mutable_tyreSpareInstance();
        tyreinstancespare.set_instance(static_cast<uint32_t>(t.TyrePressure.TyreInstanceSpare[i]));
        tyreinstancespare.set_enabled(t.TyrePressure.TyreInstanceSpare[i] < CZONE_NUMBER_OF_INSTANCES);
      }
    }
  } break;
  case ConfigRequest::eConfigType::eAudioStereo: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eAudioStereo";
    auto audiostereos = displayListNoLock(eCZoneStructDisplayAudioStereo);
    for (auto &a : audiostereos) {
      auto &audiostereo = m_config.add_mutable_audioStereos();
      audiostereo.set_displayType(static_cast<ConfigRequest::eConfigType>(a.AudioStereoDevice.DisplayType));
      audiostereo.set_id(static_cast<uint32_t>(a.AudioStereoDevice.Id));
      audiostereo.set_nameUTF8(a.AudioStereoDevice.NameUTF8);
      addInstance(audiostereo.mutable_instance(), a.AudioStereoDevice.Instance);
      audiostereo.set_muteEnabled(static_cast<uint32_t>(a.AudioStereoDevice.MuteEnabled));
      for (uint32_t i = 0; i < 8; i++) {
        audiostereo.add_circuitId(DataId(static_cast<uint32_t>(a.AudioStereoDevice.CircuitId[i]),
                                         a.AudioStereoDevice.CircuitId[i] != CZONE_INVALID_CIRCUIT_INDEX));
      }
    }
  } break;
  case ConfigRequest::eConfigType::eShoreFuse: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eShoreFuse";
    auto shorefuses = displayListNoLock(eCZoneStructDisplayShoreFuse);
    for (auto &s : shorefuses) {
      auto &shorefuse = m_config.add_mutable_shoreFuses();
      shorefuse.set_displayType(static_cast<ConfigRequest::eConfigType>(s.ShoreFuseDevice.DisplayType));
      shorefuse.set_id(static_cast<uint32_t>(s.ShoreFuseDevice.Id));
      shorefuse.set_nameUTF8(s.ShoreFuseDevice.NameUTF8);
      addInstance(shorefuse.mutable_instance(), s.ShoreFuseDevice.ChargerInstance);
      shorefuse.set_shoreFuseControlId(createDataId(s.ShoreFuseDevice.ShoreFuseControlId));
    }
  } break;
  case ConfigRequest::eConfigType::eCircuit:
  case ConfigRequest::eConfigType::eNonVisibleCircuit: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eCircuit/eNonVisibleCircuit";
    auto circuits = displayListNoLock(eCZoneStructDisplayCircuits);
    const uint32_t doubleThrowMask = 0x8000;
    for (auto &c : circuits) {
      if (c.Circuit.CircuitType == CircuitDevice::eCircuitType::eCircuit) {
        if ((c.Circuit.NonVisibleCircuit == CZONE_TRUE && request.get_type() == ConfigRequest::eConfigType::eCircuit) ||
            (c.Circuit.NonVisibleCircuit == CZONE_FALSE &&
             request.get_type() == ConfigRequest::eConfigType::eNonVisibleCircuit)) {
          continue;
        }

        auto &circuit = m_config.add_mutable_circuits();

        circuit.set_displayType(static_cast<ConfigRequest::eConfigType>(c.Circuit.DisplayType));
        circuit.set_id(std::make_pair(c.Circuit.Id, c.Circuit.Id != CZONE_INVALID_CIRCUIT_INDEX));
        circuit.set_nameUTF8(c.Circuit.NameUTF8);
        circuit.set_singleThrowId(createDataId(c.Circuit.SingleThrowId));
        for (uint32_t i = 0; i < 16; i++) {
          std::string &sequentialname = circuit.add_sequentialNamesUTF8();
          sequentialname = c.Circuit.SequentialNamesUTF8[i];
        }
        circuit.set_hasComplement((c.Circuit.HasComplement == CZONE_TRUE));
        circuit.set_displayCategories(c.Circuit.DisplayCategories);
        circuit.set_confirmDialog(static_cast<CircuitDevice::eConfirmType>(c.Circuit.ConfirmDialog));
        circuit.set_voltageSource(Instance(c.Circuit.VoltageSource, c.Circuit.VoltageSource != 0xff));
        circuit.set_circuitType(static_cast<CircuitDevice::eCircuitType>(c.Circuit.CircuitType));
        circuit.set_switchType(static_cast<CircuitDevice::eSwitchType>(c.Circuit.SwitchType &= ~doubleThrowMask));
        circuit.set_switchString(c.Circuit.SwitchString);
        circuit.set_minLevel(static_cast<uint32_t>(c.Circuit.MinLevel));
        circuit.set_maxLevel(static_cast<uint32_t>(c.Circuit.MaxLevel));
        circuit.set_dimstep(static_cast<uint32_t>(c.Circuit.Dimstep));
        circuit.set_dimmable((c.Circuit.Dimmable == CZONE_TRUE));
        circuit.set_loadSmoothStart(c.Circuit.LoadSmoothStart);
        circuit.set_sequentialStates(c.Circuit.SequentialStates);
        circuit.set_controlId(c.Circuit.ControlId);
        circuit.set_systemsOnAnd(c.Circuit.SystemsOnAnd);

        auto loads = displayListNoLock(eCZoneStructDisplayCircuitLoad, c.Circuit.ControlId, 0);
        for (auto &l : loads) {
          CircuitLoad &circuitLoad = circuit.add_circuitLoad();

          circuitLoad.set_displayType(static_cast<ConfigRequest::eConfigType>(l.CircuitLoads.DisplayType));
          circuitLoad.set_id(static_cast<uint32_t>(l.CircuitLoads.Id));
          circuitLoad.set_nameUTF8(l.CircuitLoads.NameUTF8);
          circuitLoad.set_channelAddress(l.CircuitLoads.ChannelAddress);
          circuitLoad.set_fuseLevel((static_cast<float>(l.CircuitLoads.FuseLevel) / 10.0f));
          circuitLoad.set_runningCurrent((static_cast<float>(l.CircuitLoads.RunningCurrent) / 10.0f));
          circuitLoad.set_systemOnCurrent((static_cast<float>(l.CircuitLoads.SystemOnCurrent) / 10.0f));
          circuitLoad.set_forceAcknowledgeOn(l.CircuitLoads.ForceAcknowledgeOn);
          circuitLoad.set_level(l.CircuitLoads.Level);
          circuitLoad.set_controlType(static_cast<CircuitLoad::eControlType>(l.CircuitLoads.ControlType));
          circuitLoad.set_isSwitchedModule(l.CircuitLoads.IsSwitchedModule);
        }

        auto categories = displayListNoLock(eCZoneStructDisplayEnabledCategories, c.Circuit.DisplayCategories, 0);
        for (auto &c : categories) {
          CategoryItem &category = circuit.add_category();
          category.set_nameUTF8(c.CategoryItem.NameUTF8);
          category.set_enabled(c.CategoryItem.Enabled == CZONE_TRUE);
        }

        circuit.set_dcCircuit(c.Circuit.DisplayCategories & (1 << 21));
        circuit.set_acCircuit(c.Circuit.DisplayCategories & (1 << 22));
        circuit.set_primaryCircuitId(c.Circuit.PrimaryCircuitId);
        circuit.set_remoteVisibility(c.Circuit.RemoteVisibility);
      }
    }
  } break;
  case ConfigRequest::eConfigType::eMode: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eMode";
    auto circuits = displayListNoLock(eCZoneStructDisplayModes);
    for (auto &c : circuits) {
      if (c.Circuit.CircuitType >= CircuitDevice::eCircuitType::eModeGroup1 &&
          c.Circuit.CircuitType <= CircuitDevice::eCircuitType::eModeGroupExclusive) {
        auto &circuit = m_config.add_mutable_modes();

        circuit.set_displayType(static_cast<ConfigRequest::eConfigType>(c.Circuit.DisplayType));
        circuit.set_id(std::make_pair(c.Circuit.Id, c.Circuit.Id != CZONE_INVALID_CIRCUIT_INDEX));
        circuit.set_nameUTF8(c.Circuit.NameUTF8);
        circuit.set_singleThrowId(createDataId(c.Circuit.SingleThrowId));
        for (uint32_t i = 0; i < 16; i++) {
          std::string &sequentialname = circuit.add_sequentialNamesUTF8();
          sequentialname = c.Circuit.SequentialNamesUTF8[i];
        }
        circuit.set_hasComplement((c.Circuit.HasComplement == CZONE_TRUE));
        circuit.set_displayCategories(c.Circuit.DisplayCategories);
        circuit.set_confirmDialog(static_cast<CircuitDevice::eConfirmType>(c.Circuit.ConfirmDialog));
        circuit.set_circuitType(static_cast<CircuitDevice::eCircuitType>(c.Circuit.CircuitType));
        circuit.set_switchType(static_cast<CircuitDevice::eSwitchType>(c.Circuit.SwitchType));
        circuit.set_minLevel(static_cast<uint32_t>(c.Circuit.MinLevel));
        circuit.set_maxLevel(static_cast<uint32_t>(c.Circuit.MaxLevel));
        circuit.set_dimstep(static_cast<uint32_t>(c.Circuit.Dimstep));
        circuit.set_dimmable((c.Circuit.Dimmable == CZONE_TRUE));
        circuit.set_loadSmoothStart(c.Circuit.LoadSmoothStart);
        circuit.set_sequentialStates(c.Circuit.SequentialStates);
        circuit.set_controlId(c.Circuit.ControlId);

        auto loads = displayListNoLock(eCZoneStructDisplayCircuitLoad, c.Circuit.ControlId, 0);
        for (auto &l : loads) {
          CircuitLoad &circuitLoad = circuit.add_circuitLoad();

          circuitLoad.set_displayType(static_cast<ConfigRequest::eConfigType>(l.CircuitLoads.DisplayType));
          circuitLoad.set_id(static_cast<uint32_t>(l.CircuitLoads.Id));
          circuitLoad.set_nameUTF8(l.CircuitLoads.NameUTF8);
          circuitLoad.set_channelAddress(l.CircuitLoads.ChannelAddress);
          circuitLoad.set_fuseLevel((static_cast<float>(l.CircuitLoads.FuseLevel) / 10.0f));
          circuitLoad.set_runningCurrent((static_cast<float>(l.CircuitLoads.RunningCurrent) / 10.0f));
          circuitLoad.set_systemOnCurrent((static_cast<float>(l.CircuitLoads.SystemOnCurrent) / 10.0f));
          circuitLoad.set_forceAcknowledgeOn(l.CircuitLoads.ForceAcknowledgeOn);
          circuitLoad.set_level(l.CircuitLoads.Level);
          circuitLoad.set_controlType(static_cast<CircuitLoad::eControlType>(l.CircuitLoads.ControlType));
          circuitLoad.set_isSwitchedModule(l.CircuitLoads.IsSwitchedModule);
        }

        uint32_t modeIcon = (c.Circuit.DisplayCategories & 0xffff) - 1000;
        circuit.set_modeIcon(static_cast<CircuitDevice::eModeIcon>(modeIcon));
        circuit.set_primaryCircuitId((c.Circuit.PrimaryCircuitId));
        circuit.set_remoteVisibility((c.Circuit.RemoteVisibility));
      }
    }
  } break;
  case ConfigRequest::eConfigType::eFantasticFan: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFantasticFan";
    auto fantasticfans = displayListNoLock(eCZoneStructDisplayFantasticFan);
    for (auto &f : fantasticfans) {
      auto &fantasticfan = m_config.add_mutable_fantasticFans();
      fantasticfan.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FantasticFanDevice.DisplayType));
      fantasticfan.set_id(static_cast<uint32_t>(f.FantasticFanDevice.Id));
      fantasticfan.set_nameUTF8(f.FantasticFanDevice.NameUTF8);
      addInstance(fantasticfan.mutable_instance(), f.FantasticFanDevice.Instance);
      fantasticfan.set_directionForwardCircuitId(createDataId(f.FantasticFanDevice.DirectionForwardCircuitId));
      fantasticfan.set_directionReverseCircuitId(createDataId(f.FantasticFanDevice.DirectionReverseCircuitId));
      fantasticfan.set_lidOpenCircuitId(createDataId(f.FantasticFanDevice.LidOpenCircuitId));
      fantasticfan.set_lidCloseCircuitId(createDataId(f.FantasticFanDevice.LidCloseCircuitId));
      fantasticfan.set_fanCircuitId(createDataId(f.FantasticFanDevice.FanCircuitId));
    }
  } break;
  case ConfigRequest::eConfigType::eScreenConfigPageImageItem: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eScreenConfigPageImageItem";
    auto screenconfigs = displayListNoLock(eCZoneStructScreenConfigPageImageItem);
    for (auto &s : screenconfigs) {
      auto &screenconfig = m_config.add_mutable_screenConfigPageImageItems();
      auto &header = screenconfig.mutable_header();
      header.set_displayType(static_cast<ConfigRequest::eConfigType>(s.ScreenConfigPageImageItems.Header.DisplayType));
      header.set_id(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.Id));
      header.set_targetDisplayType(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.TargetDisplayType));
      header.set_targetId(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.TargetId));
      header.set_confirmationType(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.ConfirmationType));
      header.set_smoothStart(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.SmoothStart));
      header.set_index(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.Index));
      header.set_parentIndex(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.ParentIndex));
      header.set_controlId(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Header.ControlId));
      screenconfig.set_locationX(s.ScreenConfigPageImageItems.LocationX);
      screenconfig.set_locationY(s.ScreenConfigPageImageItems.LocationY);
      screenconfig.set_targetX(s.ScreenConfigPageImageItems.TargetX);
      screenconfig.set_targetY(s.ScreenConfigPageImageItems.TargetY);
      screenconfig.set_name(s.ScreenConfigPageImageItems.Name);
      screenconfig.set_icon(static_cast<uint32_t>(s.ScreenConfigPageImageItems.Icon));
      screenconfig.set_hideWhenOff(static_cast<bool>(s.ScreenConfigPageImageItems.HideWhenOff));
    }
  } break;
  case ConfigRequest::eConfigType::eScreenConfigPageImage: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eScreenConfigPageImage";
    auto screenconfigs = displayListNoLock(eCZoneStructScreenConfigPageImage);
    for (auto &s : screenconfigs) {
      auto &screenconfig = m_config.add_mutable_screenConfigPageImages();
      auto &header = screenconfig.mutable_header();
      header.set_displayType(static_cast<ConfigRequest::eConfigType>(s.ScreenConfigPageImages.Header.DisplayType));
      header.set_id(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.Id));
      header.set_targetDisplayType(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.TargetDisplayType));
      header.set_targetId(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.TargetId));
      header.set_confirmationType(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.ConfirmationType));
      header.set_smoothStart(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.SmoothStart));
      header.set_index(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.Index));
      header.set_parentIndex(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.ParentIndex));
      header.set_controlId(static_cast<uint32_t>(s.ScreenConfigPageImages.Header.ControlId));
      screenconfig.set_gridX(static_cast<uint32_t>(s.ScreenConfigPageImages.GridX));
      screenconfig.set_gridY(static_cast<uint32_t>(s.ScreenConfigPageImages.GridY));
      screenconfig.set_gridWidth(static_cast<uint32_t>(s.ScreenConfigPageImages.GridWidth));
      screenconfig.set_gridHeight(static_cast<uint32_t>(s.ScreenConfigPageImages.GridHeight));
      screenconfig.set_sourceWidth(s.ScreenConfigPageImages.SourceWidth);
      screenconfig.set_sourceHeight(s.ScreenConfigPageImages.SourceHeight);
      screenconfig.set_targetX(s.ScreenConfigPageImages.TargetX);
      screenconfig.set_targetY(s.ScreenConfigPageImages.TargetY);
      screenconfig.set_targetWidth(s.ScreenConfigPageImages.TargetWidth);
      screenconfig.set_targetHeight(s.ScreenConfigPageImages.TargetHeight);
      screenconfig.set_fileName(s.ScreenConfigPageImages.FileName);
      screenconfig.set_backgroundColourR(static_cast<uint32_t>(s.ScreenConfigPageImages.BackgroundColourR));
      screenconfig.set_backgroundColourG(static_cast<uint32_t>(s.ScreenConfigPageImages.BackgroundColourG));
      screenconfig.set_backgroundColourB(static_cast<uint32_t>(s.ScreenConfigPageImages.BackgroundColourB));
      screenconfig.set_showBackground(static_cast<uint32_t>(s.ScreenConfigPageImages.ShowBackground));
      screenconfig.set_cropToFit(static_cast<uint32_t>(s.ScreenConfigPageImages.CropToFit));
    }
  } break;
  case ConfigRequest::eConfigType::eScreenConfigPageGridItem: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eScreenConfigPageGridItem";
    auto screenconfigs = displayListNoLock(eCZoneStructScreenConfigPageGridItem);
    for (auto &s : screenconfigs) {
      auto &screenconfig = m_config.add_mutable_screenConfigPageGridItems();
      auto &header = screenconfig.mutable_header();
      header.set_displayType(static_cast<ConfigRequest::eConfigType>(s.ScreenConfigPageGridItems.Header.DisplayType));
      header.set_id(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.Id));
      header.set_targetDisplayType(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.TargetDisplayType));
      header.set_targetId(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.TargetId));
      header.set_confirmationType(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.ConfirmationType));
      header.set_smoothStart(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.SmoothStart));
      header.set_index(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.Index));
      header.set_parentIndex(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.ParentIndex));
      header.set_controlId(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Header.ControlId));
      screenconfig.set_gridX(static_cast<uint32_t>(s.ScreenConfigPageGridItems.GridX));
      screenconfig.set_gridY(static_cast<uint32_t>(s.ScreenConfigPageGridItems.GridY));
      screenconfig.set_targetX(s.ScreenConfigPageGridItems.TargetX);
      screenconfig.set_targetY(s.ScreenConfigPageGridItems.TargetY);
      screenconfig.set_targetWidth(s.ScreenConfigPageGridItems.TargetWidth);
      screenconfig.set_targetHeight(s.ScreenConfigPageGridItems.TargetHeight);
      screenconfig.set_name(s.ScreenConfigPageGridItems.Name);
      screenconfig.set_icon(static_cast<uint32_t>(s.ScreenConfigPageGridItems.Icon));
      screenconfig.set_columnSpan(static_cast<uint32_t>(s.ScreenConfigPageGridItems.ColumnSpan));
      screenconfig.set_rowSpan(static_cast<uint32_t>(s.ScreenConfigPageGridItems.RowSpan));
      screenconfig.set_doubleThrowType(static_cast<uint32_t>(s.ScreenConfigPageGridItems.DoubleThrowType));
    }
  } break;
  case ConfigRequest::eConfigType::eScreenConfigPage: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eScreenConfigPage";
    auto screenconfigs = displayListNoLock(eCZoneStructScreenConfigPage);
    for (auto &s : screenconfigs) {
      auto &screenconfig = m_config.add_mutable_screenConfigPages();
      auto &header = screenconfig.mutable_header();
      header.set_displayType(static_cast<ConfigRequest::eConfigType>(s.ScreenConfigPages.Header.DisplayType));
      header.set_id(static_cast<uint32_t>(s.ScreenConfigPages.Header.Id));
      header.set_targetDisplayType(static_cast<uint32_t>(s.ScreenConfigPages.Header.TargetDisplayType));
      header.set_targetId(static_cast<uint32_t>(s.ScreenConfigPages.Header.TargetId));
      header.set_confirmationType(static_cast<uint32_t>(s.ScreenConfigPages.Header.ConfirmationType));
      header.set_smoothStart(static_cast<uint32_t>(s.ScreenConfigPages.Header.SmoothStart));
      header.set_index(static_cast<uint32_t>(s.ScreenConfigPages.Header.Index));
      header.set_parentIndex(static_cast<uint32_t>(s.ScreenConfigPages.Header.ParentIndex));
      header.set_controlId(static_cast<uint32_t>(s.ScreenConfigPages.Header.ControlId));
    }
  } break;
  case ConfigRequest::eConfigType::eScreenConfigMode: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eScreenConfigMode";
    auto screenconfigs = displayListNoLock(eCZoneStructScreenConfigMode);
    for (auto &s : screenconfigs) {
      auto &screenconfig = m_config.add_mutable_screenConfigModes();
      auto &header = screenconfig.mutable_header();
      header.set_displayType(static_cast<ConfigRequest::eConfigType>(s.ScreenConfigModes.Header.DisplayType));
      header.set_id(static_cast<uint32_t>(s.ScreenConfigModes.Header.Id));
      header.set_targetDisplayType(static_cast<uint32_t>(s.ScreenConfigModes.Header.TargetDisplayType));
      header.set_targetId(static_cast<uint32_t>(s.ScreenConfigModes.Header.TargetId));
      header.set_confirmationType(static_cast<uint32_t>(s.ScreenConfigModes.Header.ConfirmationType));
      header.set_smoothStart(static_cast<uint32_t>(s.ScreenConfigModes.Header.SmoothStart));
      header.set_index(static_cast<uint32_t>(s.ScreenConfigModes.Header.Index));
      header.set_parentIndex(static_cast<uint32_t>(s.ScreenConfigModes.Header.ParentIndex));
      header.set_controlId(static_cast<uint32_t>(s.ScreenConfigModes.Header.ControlId));
      screenconfig.set_name(s.ScreenConfigModes.Name);
    }
  } break;
  case ConfigRequest::eConfigType::eScreenConfig: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eScreenConfig";
    auto screenconfigs = displayListNoLock(eCZoneStructScreenConfig);
    for (auto &s : screenconfigs) {
      auto &screenconfig = m_config.add_mutable_screenConfigs();
      auto &header = screenconfig.mutable_header();
      header.set_displayType(static_cast<ConfigRequest::eConfigType>(s.ScreenConfigs.Header.DisplayType));
      header.set_id(static_cast<uint32_t>(s.ScreenConfigs.Header.Id));
      header.set_targetDisplayType(static_cast<uint32_t>(s.ScreenConfigs.Header.TargetDisplayType));
      header.set_targetId(static_cast<uint32_t>(s.ScreenConfigs.Header.TargetId));
      header.set_confirmationType(static_cast<uint32_t>(s.ScreenConfigs.Header.ConfirmationType));
      header.set_smoothStart(static_cast<uint32_t>(s.ScreenConfigs.Header.SmoothStart));
      header.set_index(static_cast<uint32_t>(s.ScreenConfigs.Header.Index));
      header.set_parentIndex(static_cast<uint32_t>(s.ScreenConfigs.Header.ParentIndex));
      header.set_controlId(static_cast<uint32_t>(s.ScreenConfigs.Header.ControlId));
      screenconfig.set_gridHeight(static_cast<uint32_t>(s.ScreenConfigs.GridWidth));
      screenconfig.set_gridHeight(static_cast<uint32_t>(s.ScreenConfigs.GridHeight));
      screenconfig.set_landscape(static_cast<uint32_t>(s.ScreenConfigs.Landscape));
      screenconfig.set_displayName(s.ScreenConfigs.DisplayName);
      screenconfig.set_relativePath(s.ScreenConfigs.RelativePath);
    }
  } break;
  case ConfigRequest::eConfigType::eFavouritesMode: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFavouritesMode";
    auto favourites = displayListNoLock(eCZoneStructDisplayFavouritesMode);
    for (auto &f : favourites) {
      auto &favourite = m_config.add_mutable_favouritesModes();
      favourite.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FavouritesInfo.DisplayType));
      favourite.set_id(static_cast<uint32_t>(f.FavouritesInfo.Id));
      favourite.set_targetDisplayType(static_cast<uint32_t>(f.FavouritesInfo.TargetDisplayType));
      favourite.set_targetId(static_cast<uint32_t>(f.FavouritesInfo.TargetId));
      favourite.set_x(static_cast<uint32_t>(f.FavouritesInfo.X));
      favourite.set_y(static_cast<uint32_t>(f.FavouritesInfo.Y));
    }
  } break;
  case ConfigRequest::eConfigType::eFavouritesControl: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFavouritesControl";
    auto favourites = displayListNoLock(eCZoneStructDisplayFavouritesControl);
    for (auto &f : favourites) {
      auto &favourite = m_config.add_mutable_favouritesControls();
      favourite.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FavouritesInfo.DisplayType));
      favourite.set_id(static_cast<uint32_t>(f.FavouritesInfo.Id));
      favourite.set_targetDisplayType(static_cast<uint32_t>(f.FavouritesInfo.TargetDisplayType));
      favourite.set_targetId(static_cast<uint32_t>(f.FavouritesInfo.TargetId));
      favourite.set_x(static_cast<uint32_t>(f.FavouritesInfo.X));
      favourite.set_y(static_cast<uint32_t>(f.FavouritesInfo.Y));
    }
  } break;
  case ConfigRequest::eConfigType::eFavouritesMonitoring: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFavouritesMonitoring";
    auto favourites = displayListNoLock(eCZoneStructDisplayFavouritesMonitoring);
    for (auto &f : favourites) {
      auto &favourite = m_config.add_mutable_favouritesMonitorings();
      favourite.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FavouritesInfo.DisplayType));
      favourite.set_id(static_cast<uint32_t>(f.FavouritesInfo.Id));
      favourite.set_targetDisplayType(static_cast<uint32_t>(f.FavouritesInfo.TargetDisplayType));
      favourite.set_targetId(static_cast<uint32_t>(f.FavouritesInfo.TargetId));
      favourite.set_x(static_cast<uint32_t>(f.FavouritesInfo.X));
      favourite.set_y(static_cast<uint32_t>(f.FavouritesInfo.Y));
    }
  } break;
  case ConfigRequest::eConfigType::eFavouritesAlarm: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFavouritesAlarm";
    auto favourites = displayListNoLock(eCZoneStructDisplayFavouritesAlarms);
    for (auto &f : favourites) {
      auto &favourite = m_config.add_mutable_favouritesAlarms();
      favourite.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FavouritesInfo.DisplayType));
      favourite.set_id(static_cast<uint32_t>(f.FavouritesInfo.Id));
      favourite.set_targetDisplayType(static_cast<uint32_t>(f.FavouritesInfo.TargetDisplayType));
      favourite.set_targetId(static_cast<uint32_t>(f.FavouritesInfo.TargetId));
      favourite.set_x(static_cast<uint32_t>(f.FavouritesInfo.X));
      favourite.set_y(static_cast<uint32_t>(f.FavouritesInfo.Y));
    }
  } break;
  case ConfigRequest::eConfigType::eFavouritesACMain: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFavouritesACMain";
    auto favourites = displayListNoLock(eCZoneStructDisplayFavouritesACMains);
    for (auto &f : favourites) {
      auto &favourite = m_config.add_mutable_favouritesACMains();
      favourite.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FavouritesInfo.DisplayType));
      favourite.set_id(static_cast<uint32_t>(f.FavouritesInfo.Id));
      favourite.set_targetDisplayType(static_cast<uint32_t>(f.FavouritesInfo.TargetDisplayType));
      favourite.set_targetId(static_cast<uint32_t>(f.FavouritesInfo.TargetId));
      favourite.set_x(static_cast<uint32_t>(f.FavouritesInfo.X));
      favourite.set_y(static_cast<uint32_t>(f.FavouritesInfo.Y));
    }
  } break;
  case ConfigRequest::eConfigType::eFavouritesInverterCharger: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFavouritesInverterCharger";
    auto favourites = displayListNoLock(eCZoneStructDisplayFavouritesInverterCharger);
    for (auto &f : favourites) {
      auto &favourite = m_config.add_mutable_favouritesInverterChargers();
      favourite.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FavouritesInfo.DisplayType));
      favourite.set_id(static_cast<uint32_t>(f.FavouritesInfo.Id));
      favourite.set_targetDisplayType(static_cast<uint32_t>(f.FavouritesInfo.TargetDisplayType));
      favourite.set_targetId(static_cast<uint32_t>(f.FavouritesInfo.TargetId));
      favourite.set_x(static_cast<uint32_t>(f.FavouritesInfo.X));
      favourite.set_y(static_cast<uint32_t>(f.FavouritesInfo.Y));
    }
  } break;
  case ConfigRequest::eConfigType::eDevice: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eDevice";
    auto devices = displayListNoLock(eCZoneStructDisplayNetworkDevice);
    for (auto &d : devices) {
      auto &device = m_config.add_mutable_devices();
      device.set_displayType(static_cast<ConfigRequest::eConfigType>(eCZoneStructDisplayNetworkDevice));
      device.set_nameUTF8(d.Device.NameUTF8);
      device.set_dipswitch(d.Device.Dipswitch);
      device.set_sourceAddress(d.Device.SourceAddress);
      device.set_version(d.Device.SoftwareVersion);
      device.set_conflict(d.Device.Conflict);
      device.set_deviceType(static_cast<Device::eDeviceType>(d.Device.DeviceType));
      device.set_valid(d.Device.Valid);
      device.set_transient(d.Device.Transient);
    }
  } break;
  case ConfigRequest::eConfigType::eFavouritesBoatView: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eFavouritesBoatView";
    auto favourites = displayListNoLock(eCZoneStructDisplayFavouritesBoatView);
    for (auto &f : favourites) {
      auto &favourite = m_config.add_mutable_favouritesBoatViews();
      favourite.set_displayType(static_cast<ConfigRequest::eConfigType>(f.FavouritesInfo.DisplayType));
      favourite.set_id(static_cast<uint32_t>(f.FavouritesInfo.Id));
      favourite.set_targetDisplayType(static_cast<uint32_t>(f.FavouritesInfo.TargetDisplayType));
      favourite.set_targetId(static_cast<uint32_t>(f.FavouritesInfo.TargetId));
      favourite.set_x(static_cast<uint32_t>(f.FavouritesInfo.X));
      favourite.set_y(static_cast<uint32_t>(f.FavouritesInfo.Y));
    }
  } break;
  case ConfigRequest::eConfigType::eEngines: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eEngines";
    // SmartCraft Engines:
    for (auto &e : m_engineList) {
      auto &engine = m_config.add_mutable_engines();
      engine = e.second;
    }

    // NMEA2000 Engines:
    auto nmea2kEngines = displayListNoLock(eCZoneStructDisplayEngines);
    unsigned int smartcraftN2kSize = 0;
    unsigned int smartcraftN2kIndex = 0;
    unsigned int smartcraftN2kManufacturerId = 0x90;

    for (auto &e : nmea2kEngines) {
      // Smartcraft with SCC N2K engines
      if (e.DynamicDevice.ManufacturerId == smartcraftN2kManufacturerId) {
        smartcraftN2kSize++;
      }
    }

    for (auto &e : nmea2kEngines) {
      auto &engine = m_config.add_mutable_engines();
      engine.set_displayType(static_cast<ConfigRequest::eConfigType>(e.DynamicDevice.DisplayType));
      engine.set_engineType(EngineDevice::eEngineType::eNMEA2000);
      engine.set_id(static_cast<uint32_t>(e.DynamicDevice.Id));

      if (e.DynamicDevice.ManufacturerId == smartcraftN2kManufacturerId) {
        switch (smartcraftN2kSize) {
        case 1:
          if (smartcraftN2kIndex == 0) {
            engine.set_nameUTF8("Starboard Engine");
          }
          smartcraftN2kIndex++;
          break;
        case 2:
          if (smartcraftN2kIndex == 0) {
            engine.set_nameUTF8("Port Engine");
          } else if (smartcraftN2kIndex == 1) {
            engine.set_nameUTF8("Starboard Engine");
          }
          smartcraftN2kIndex++;
          break;
        case 3:
          if (smartcraftN2kIndex == 0) {
            engine.set_nameUTF8("Port Engine");
          } else if (smartcraftN2kIndex == 1) {
            engine.set_nameUTF8("Center Engine");
          } else if (smartcraftN2kIndex == 2) {
            engine.set_nameUTF8("Starboard Engine");
          }
          smartcraftN2kIndex++;
          break;
        case 4:
          if (smartcraftN2kIndex == 0) {
            engine.set_nameUTF8("Port Engine");
          } else if (smartcraftN2kIndex == 1) {
            engine.set_nameUTF8("Port Inner Engine");
          } else if (smartcraftN2kIndex == 2) {
            engine.set_nameUTF8("Starboard Inner Engine");
          } else if (smartcraftN2kIndex == 3) {
            engine.set_nameUTF8("Starboard Engine");
          }
          smartcraftN2kIndex++;
          break;
        default: engine.set_nameUTF8(e.DynamicDevice.NameUTF8); break;
        }
      } else {
        engine.set_nameUTF8(e.DynamicDevice.NameUTF8);
      }

      engine.mutable_instance().set_enabled(true);
      engine.mutable_instance().set_instance(e.DynamicDevice.Instance);

      engine.set_softwareId(e.DynamicDevice.SoftwareVersion);
      engine.set_serialNumber(e.DynamicDevice.SerialNumber);
    }
  } break;
  case ConfigRequest::eConfigType::eGNSS: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eGNSS";
    auto gnssDevices = displayListNoLock(eCZoneStructDisplayGNSS);
    for (auto &g : gnssDevices) {
      auto &gnss = m_config.add_mutable_gnss();
      gnss.set_displayType(static_cast<ConfigRequest::eConfigType>(g.DynamicDevice.DisplayType));
      gnss.set_id(static_cast<uint32_t>(g.DynamicDevice.Id));
      gnss.set_nameUTF8(g.DynamicDevice.NameUTF8);

      auto name = NetworkName();
      tCZoneNmea2kName n(name);

      gnss.set_isExternal((n.DeviceInstance() != g.DynamicDevice.Instance));

      addInstance(gnss.mutable_instance(), g.DynamicDevice.Instance);
    }
  } break;
  case ConfigRequest::eConfigType::eCZoneRaw: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eCZoneRaw";
    CZoneRawConfig rawConfig;
    rawConfig.set_type(Event::eEventType::eCZoneRaw);

    void *ptr = NULL;
    uint32_t length = 0;
    uint32_t sizeOfData = 0;

    CZoneDisplayList(request.get_subType(), request.get_parentId(), request.get_flags(), (const void **)&ptr, &length,
                     &sizeOfData);

    if (length * sizeOfData > 10 * 1024 * 1024) {
      BOOST_LOG_TRIVIAL(debug) << "GetConfig: Nmea2k::ConfigRequest_eConfigType_CZoneRaw only "
                                  "support 10 * 1024 * 1024 bytes payload.";
      CZoneFreeDataArray((void **)&ptr);
      return m_config;
    }

    auto &rawConfigContents = rawConfig.mutable_contents();
    rawConfigContents.resize(length * sizeOfData);
    std::memcpy(rawConfigContents.data(), ptr, length * sizeOfData);

    rawConfig.set_length(length);
    rawConfig.set_sizeOfData(sizeOfData);
    m_config.set_displayList(rawConfig);
    CZoneFreeDataArray((void **)&ptr);
  } break;
  case ConfigRequest::eConfigType::eUiRelationships: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eUiRelationships";
    auto uiRelationships = displayListNoLock(eCZoneStructDisplayUIRelationship);

    for (auto &u : uiRelationships) {
      auto &uir = m_config.add_mutable_uiRelationships();
      uir.set_displaytype(static_cast<ConfigRequest::eConfigType>(u.UiRelationship.DisplayType));
      uir.set_id(static_cast<uint32_t>(u.UiRelationship.Id));
      uir.set_primarytype(static_cast<UiRelationshipMsg::eItemType>(u.UiRelationship.primaryType));
      uir.set_secondarytype(static_cast<UiRelationshipMsg::eItemType>(u.UiRelationship.secondaryType));
      uir.set_primaryid(static_cast<uint32_t>(u.UiRelationship.primaryId));
      uir.set_secondaryid(static_cast<uint32_t>(u.UiRelationship.secondaryId));
      uir.set_relationshiptype(static_cast<UiRelationshipMsg::eRelationshipType>(u.UiRelationship.relationshipType));
      uir.set_primaryconfigaddress(static_cast<uint32_t>(u.UiRelationship.primaryConfigId));
      uir.set_secondaryconfigaddress(static_cast<uint32_t>(u.UiRelationship.secondaryConfigId));
      uir.set_primarychannelindex(static_cast<uint32_t>(u.UiRelationship.primaryItemChannelIndex));
      uir.set_secondarychannelindex(static_cast<uint32_t>(u.UiRelationship.secondaryItemChannelIndex));
    }
  } break;

  case ConfigRequest::eConfigType::eBinaryLogicStates: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eBinaryLogicStates";
    auto bLogicStates = displayListNoLock(eCZoneStructDisplayBinaryLogicState);

    for (auto &bLogicState : bLogicStates) {
      auto &bls = m_config.add_mutable_binaryLogicStates();
      bls.set_displaytype(static_cast<ConfigRequest::eConfigType>(bLogicState.BinaryLogicState.DisplayType));
      bls.set_id(static_cast<uint32_t>(bLogicState.BinaryLogicState.Id));
      bls.set_address(static_cast<uint32_t>(bLogicState.BinaryLogicState.Address));
      bls.set_nameutf8(bLogicState.BinaryLogicState.NameUTF8);
    }
  } break;
  case ConfigRequest::eConfigType::eRTCoreMap: {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::GetConfig::eRTCoreMap";
    m_config.set_rtCoreLogicalIdToDeviceConfig(m_RTCoreConfig);
  } break;
  default:
    BOOST_LOG_TRIVIAL(error) << "CzoneInterface::GetConfig ConfigType[" << ConfigRequest::to_string(request.get_type())
                             << "] is not supported.";
    break;
  }
  return m_config;
}

Categories CzoneInterface::getCategories(const CategoryRequest::eCategoryType type) {
  Categories response;
  switch (type) {
  case CategoryRequest::eCategoryType::eCategoriesAll: {
    auto AllCategories = displayListNoLock(eCZoneStructDisplayAllCategories);
    for (auto &c : AllCategories) {
      response.add_categoryItem(CategoryItem(c.CategoryItem.NameUTF8, c.CategoryItem.Enabled, c.CategoryItem.Index));
    }
  } break;
  default:
    BOOST_LOG_TRIVIAL(error) << "CzoneInterface::getCategories::eCategoryType " << type << " is not supported.";
    break;
  }

  return response;
}

void CzoneInterface::populateAlarm(Alarm &alarm, const tCZoneDisplayAlarm &displayAlarm, const bool isLog,
                                   const bool isConfig) {
  alarm.set_displayType(ConfigRequest::eConfigType(displayAlarm.DisplayType));
  alarm.set_alarmType(Alarm::eAlarmType(displayAlarm.AlarmType));
  alarm.set_severity(Alarm::eSeverityType(displayAlarm.Severity));
  alarm.set_channelId(displayAlarm.ChannelId);
  alarm.set_externalAlarmId(displayAlarm.ExternalAlarmId);
  alarm.set_uniqueId(displayAlarm.UniqueId);
  alarm.set_valid(displayAlarm.Valid);

  if (!isConfig) {
    alarm.set_id(displayAlarm.Id);
    alarm.set_currentState(Alarm::eStateType(displayAlarm.CurrentState));
    alarm.set_activatedTime(displayAlarm.ActivatedTime);
    alarm.set_acknowledgedTime(displayAlarm.AcknowledgedTime);
    alarm.set_clearedTime(displayAlarm.ClearedTime);
  }

  std::string title;
  std::string description;
  if (isLog) {
    alarm.set_name(alarmString(displayAlarm.UniqueId, eCZoneAlarmLogName, false));
    alarm.set_channel(alarmString(displayAlarm.UniqueId, eCZoneAlarmLogChannelName, false));
    alarm.set_device(alarmString(displayAlarm.UniqueId, eCZoneAlarmLogDeviceName, false));
    title = alarmString(displayAlarm.UniqueId, eCZoneAlarmLogTitle, false);
    description = alarmString(displayAlarm.UniqueId, eCZoneAlarmLogDescription, false);
  } else {
    alarm.set_name(alarmString(displayAlarm.UniqueId, eCZoneAlarmName, false));
    alarm.set_channel(alarmString(displayAlarm.UniqueId, eCZoneAlarmChannelName, false));
    alarm.set_device(alarmString(displayAlarm.UniqueId, eCZoneAlarmDeviceName, false));
    title = alarmString(displayAlarm.UniqueId, eCZoneAlarmTitle, false);
    description = alarmString(displayAlarm.UniqueId, eCZoneAlarmDescription, false);
  }
  if (title.length() == 0) {
    alarm.set_title(alarm.get_channel());
  } else {
    alarm.set_title(std::move(title));
  }
  std::string defaultDescription = alarmString(displayAlarm.UniqueId, eCZoneAlarmDefaultDescription, false);
  std::string groupDescription = alarmString(displayAlarm.UniqueId, eCZoneAlarmGroupPolicyDescription, false);
  std::string customizedDescription = description.substr(0, description.find("$$$"));
  if (customizedDescription.length() == 0) {
    if (groupDescription.length()) {
      customizedDescription = std::move(groupDescription);
    } else if (defaultDescription.length()) {
      customizedDescription = std::move(defaultDescription);
    }
  }
  alarm.set_description(std::move(customizedDescription));
}

AlarmsList CzoneInterface::alarmList(const bool IsLog, const bool IsRaw) {
  if (m_wakeUp) {
    return m_wakeUpAlarmList;
  }

  AlarmsList response;
  auto Alarms = displayListNoLock(IsLog ? eCZoneStructDisplayAlarmLog : eCZoneStructDisplayAlarm);
  for (auto &a : Alarms) {
    auto &alarm = response.add_alarm();
    if (IsRaw) {
      alarm.set_cZoneRawAlarm(&a.Alarm, sizeof(tCZoneDisplayAlarm));
    }
    populateAlarm(alarm, a.Alarm, IsLog, false);
  }
  return response;
}

std::string CzoneInterface::libraryVersion() const {
  std::lock_guard<std::mutex> lock(m_canMutex);
  tCZoneLibraryInformation info;
  if (CZoneLibraryVersion(&info) == CZONE_TRUE) {
    std::stringstream ss;
    ss << info.Major << "." << info.Minor << "." << info.SubMinor << "." << info.Build;
    return ss.str();
  }
  return std::string();
}

std::string CzoneInterface::configName() const {
  std::lock_guard<std::mutex> lock(m_canMutex);
  tCZoneLibraryInformation info;
  if (CZoneLibraryVersion(&info) == CZONE_TRUE) {
    return std::string(info.ConfigNameUTF8);
  }
  return std::string();
}

tCZoneDeviceItem CzoneInterface::deviceItem(const uint32_t index) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  tCZoneDeviceItem item;
  CZoneDevice(index, &item);
  return item;
}

tCZoneDisplayAlarm CzoneInterface::alarm(const uint32_t alarmId) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  tCZoneDisplayAlarm alarm;
  CZoneAlarm(alarmId, &alarm);
  return alarm;
}

void CzoneInterface::alarmAcknowledge(const uint32_t alarmId, const bool accepted) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneAlarmAcknowledge(alarmId, accepted);
}

void CzoneInterface::alarmAcknowledgeAllBySeverity(const tCZoneAlarmSeverityType severity) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneAlarmAcknowledgeAllBySeverity(severity);
}

bool CzoneInterface::alarmGetNextUnacknowledged(tCZoneDisplayAlarm *alarm, const uint32_t *alarmIds,
                                                const uint32_t length) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  return (CZoneAlarmGetNextUnacknowledged(alarm, alarmIds, length) == CZONE_TRUE);
}

std::string CzoneInterface::alarmString(const uint32_t alarmId, const tCZoneAlarmStringType type, bool translate) {
  std::lock_guard<std::mutex> lock(m_alarmStringMutex);
  char *stringUTF8 = NULL;
  uint32_t length = 0;
  CZoneAlarmString(alarmId, type, &stringUTF8, &length);

  std::string str;
  if (length > 0 && stringUTF8 != NULL) {
    str = stringUTF8;
  }
  CZoneFreeDataArray((void **)&stringUTF8);

  return str;
}

tCZoneCircuitButtonIconType CzoneInterface::circuitButtonInfo(const uint32_t circuitId,
                                                              const tCZoneCircuitButtonInfoType type, bool &invert) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  tCZoneCircuitButtonIconType iconType = eCZoneCircuitButtonIconOn;
  uint8_t inv = CZONE_FALSE;

  char *stringUTF8 = NULL;
  uint32_t length = 0;

  CZoneCircuitButtonInfo(circuitId, type, &stringUTF8, &length, &iconType, &inv);

  if (length > 0 && stringUTF8 != NULL) {
    CZoneFreeDataArray((void **)&stringUTF8);
  }

  invert = (inv == CZONE_TRUE) ? true : false;
  return iconType;
}

std::vector<CzoneSystemConstants::CZoneUIStruct> CzoneInterface::displayList(const tCZoneDisplayType type) {
  return displayList(type, 0, 0);
}
std::vector<CzoneSystemConstants::CZoneUIStruct>
CzoneInterface::displayList(const tCZoneDisplayType type, const uint32_t parentId, const uint32_t flags) {
  // std::lock_guard<std::mutex> lock(m_canMutex);
  return displayListNoLock(type, parentId, flags);
}

std::vector<CzoneSystemConstants::CZoneUIStruct> CzoneInterface::displayListNoLock(const tCZoneDisplayType type) {
  return displayListNoLock(type, 0, 0);
}

std::vector<CzoneSystemConstants::CZoneUIStruct>
CzoneInterface::displayListNoLock(const tCZoneDisplayType type, const uint32_t parentId, const uint32_t flags) {
  void *ptr = NULL;
  uint32_t length = 0;
  uint32_t sizeOfData = 0;

  CZoneDisplayList(type, parentId, flags, (const void **)&ptr, &length, &sizeOfData);

  std::vector<CzoneSystemConstants::CZoneUIStruct> ret;

  uint8_t *pData = (uint8_t *)ptr;

  if (length > 0 && sizeOfData > 0 && ptr != NULL) {
    for (uint32_t i = 0; i < length; i++) {
      CzoneSystemConstants::CZoneUIStruct uiStruct;
      memset(&uiStruct, 0, sizeof(CzoneSystemConstants::CZoneUIStruct));
      uiStruct.Type = type;

      switch (type) {
      case eCZoneStructDisplayAlarm:
      case eCZoneStructDisplayAlarmConfig:
      case eCZoneStructDisplayAlarmLog: {
        uiStruct.Alarm = *reinterpret_cast<tCZoneDisplayAlarm *>(pData);
      } break;

      case eCZoneStructDisplayControl:
      case eCZoneStructDisplayCircuits:
      case eCZoneStructDisplayModes: {
        uiStruct.Circuit = *reinterpret_cast<tCZoneDisplayCircuit *>(pData);
      } break;

      case eCZoneStructDisplayMeteringAC:
      case eCZoneStructDisplayMeteringDC: {
        uiStruct.MeteringDevice = *reinterpret_cast<tCZoneDisplayMeteringDevice *>(pData);
      } break;

      case eCZoneStructDisplayMonitoringTank:
      case eCZoneStructDisplayMonitoringTemperature:
      case eCZoneStructDisplayMonitoringPressure: {
        uiStruct.MonitoringDevice = *reinterpret_cast<tCZoneDisplayMonitoringDevice *>(pData);
      } break;

      case eCZoneStructDisplayACMains: {
        uiStruct.ACMainsDevice = *reinterpret_cast<tCZoneDisplayACMainsDevice *>(pData);
      } break;

      case eCZoneStructDisplayInverterCharger:
      case eCZoneStructDisplayMBIInverterCharger: {
        uiStruct.InverterChargerDevice = *reinterpret_cast<tCZoneDisplayInverterChargerDevice *>(pData);
      } break;

      case eCZoneStructDisplayAllCZoneNetworkDevices:
      case eCZoneStructDisplayNetworkDevice: {
        uiStruct.Device = *reinterpret_cast<tCZoneDeviceItem *>(pData);
      } break;

      case eCZoneStructDisplayDipSwitches:
      case eCZoneStructDisplayDipModules: {
        uiStruct.Dipswitch = *reinterpret_cast<tCZoneDisplayDipswitches *>(pData);
      } break;

      case eCZoneStructDisplayFavouritesMode:
      case eCZoneStructDisplayFavouritesControl:
      case eCZoneStructDisplayFavouritesMonitoring:
      case eCZoneStructDisplayFavouritesAlarms:
      case eCZoneStructDisplayFavouritesACMains:
      case eCZoneStructDisplayFavouritesInverterCharger:
      case eCZoneStructDisplayFavouritesBoatView: {
        uiStruct.FavouritesInfo = *reinterpret_cast<tCZoneFavouritesInfo *>(pData);
      } break;

      case eCZoneStructScreenConfigPageImageItem: {
        uiStruct.ScreenConfigPageImageItems = *reinterpret_cast<tCZoneScreenConfigPageImageItem *>(pData);
      } break;

      case eCZoneStructScreenConfigPageImage: {
        uiStruct.ScreenConfigPageImages = *reinterpret_cast<tCZoneScreenConfigPageImage *>(pData);
      } break;

      case eCZoneStructScreenConfigPageGridItem: {
        uiStruct.ScreenConfigPageGridItems = *reinterpret_cast<tCZoneScreenConfigPageGridItem *>(pData);
      } break;

      case eCZoneStructScreenConfigPage: {
        uiStruct.ScreenConfigPages = *reinterpret_cast<tCZoneScreenConfigPage *>(pData);
      } break;

      case eCZoneStructScreenConfigMode: {
        uiStruct.ScreenConfigModes = *reinterpret_cast<tCZoneScreenConfigMode *>(pData);
      } break;

      case eCZoneStructScreenConfig: {
        uiStruct.ScreenConfigs = *reinterpret_cast<tCZoneScreenConfig *>(pData);
      } break;

      case eCZoneStructDisplayHvac: {
        uiStruct.HvacDevice = *reinterpret_cast<tCZoneDisplayHvacDevice *>(pData);
      } break;

      case eCZoneStructDisplayZipdeeAwning: {
        uiStruct.AwningDevice = *reinterpret_cast<tCZoneDisplayZipdeeAwningDevice *>(pData);
      } break;

      case eCZoneStructDisplayFantasticFan: {
        uiStruct.FantasticFanDevice = *reinterpret_cast<tCZoneDisplayFantasticFanDevice *>(pData);
      } break;

      case eCZoneStructDisplayThirdPartyGenerator: {
        uiStruct.ThirdPartyGeneratorDevice = *reinterpret_cast<tCZoneDisplayThirdPartyGeneratorDevice *>(pData);
      } break;

      case eCZoneStructDisplayShoreFuse: {
        uiStruct.ShoreFuseDevice = *reinterpret_cast<tCZoneDisplayShoreFuseDevice *>(pData);
      } break;

      case eCZoneStructDisplayTyrePressure: {
        uiStruct.TyrePressure = *reinterpret_cast<tCZoneDisplayTyrePressureDevice *>(pData);
      } break;

      case eCZoneStructDisplayAudioStereo: {
        uiStruct.AudioStereoDevice = *reinterpret_cast<tCZoneDisplayAudioStereoDevice *>(pData);
      } break;

      case eCZoneStructDisplayEnabledCategories:
      case eCZoneStructDisplayAllCategories: {
        uiStruct.CategoryItem = *reinterpret_cast<tCZoneCategoryItem *>(pData);
      } break;

      case eCZoneStructDisplayCircuitLoad: {
        uiStruct.CircuitLoads = *reinterpret_cast<tCZoneDisplayCircuitLoads *>(pData);
      } break;

      case eCZoneStructDisplayGNSS:
      case eCZoneStructDisplayEngines: {
        uiStruct.DynamicDevice = *reinterpret_cast<tCZoneDisplayDynamicDevice *>(pData);
      } break;

      case eCZoneStructEuropaCZoneDCDevices: {
        uiStruct.DCConfigure = *reinterpret_cast<tCZoneDisplayDCConfiguration *>(pData);
      } break;

      case eCZoneStructEuropaCZoneADDevices: {
        uiStruct.ADConfigure = *reinterpret_cast<tCZoneDisplayADConfiguration *>(pData);
      } break;

      case eCZoneStructEuropaCZoneOutputDevices: {
        uiStruct.OutputConfigure = *reinterpret_cast<tCZoneDisplayOutputConfiguration *>(pData);
      } break;

      case eCZoneStructDisplayUIRelationship: {
        uiStruct.UiRelationship = *reinterpret_cast<tCZoneDisplayUIRelationship *>(pData);
      } break;

      case eCZoneStructDisplayBinaryLogicState: {
        uiStruct.BinaryLogicState = *reinterpret_cast<tCZoneDisplayBinaryLogicState *>(pData);
      }

      default: {
        if ((type & CZONE_TYPE_FLAG_MENU) > 0) {
          uiStruct.MenuItem = *reinterpret_cast<tCZoneMenuItem *>(pData);
        }
      } break;
      }

      ret.push_back(uiStruct);
      pData += sizeOfData;
    }

    CZoneFreeDataArray((void **)&ptr);
  }

  return ret;
}

void CzoneInterface::writeConfig() {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneOperation(eCZoneWriteConfig);
}

void CzoneInterface::readConfig(bool force, bool configMode) {
  std::lock_guard<std::mutex> lock(m_canMutex);

  if (force) {
    CZoneOperation(eCZoneDisabledMode);
    CZoneOperation(eCZoneNormalMode);

    if (configMode) {
      CZoneOperation(eCZoneConfigMode);
    }
  } else {
    CZoneOperation(eCZoneReadConfig);
  }
}

void CzoneInterface::setBatteryFull(const uint32_t channelId) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSendBatteryFullRequest(channelId);
}

uint8_t CzoneInterface::getDipswitch() const { return m_dipswitch; }

void CzoneInterface::setDipswitch(const int dipswitch) {
  std::lock_guard<std::mutex> lock(m_dipswitchMutex);
#ifndef NO_NMEA2K_LIB
  NetworkUpdateName(m_uniqueIdBase | (dipswitch << 8), dipswitch);
#endif
  CZoneSetValue(eCZoneDipswitch, static_cast<float>(dipswitch));
  // m_LEDDataTypeIndex.clear();
  m_dipswitch = dipswitch;
}

void CzoneInterface::setEnableBatteryCharger(const bool en) {
  CZoneSetValue(eCZoneEnableBatteryCharger, static_cast<float>(en));
}

void CzoneInterface::setInternetState(const bool isConnected) {
  CZoneSetValue(eCZoneSetInternetConnectionState, static_cast<float>(isConnected));
}

void CzoneInterface::setBacklightLevel(const float backLightLevel) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetValue(eCZoneBacklight, backLightLevel);
}

void CzoneInterface::setTimeOffset(const float &timeOffset) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetValue(eCZoneTimeOffset, timeOffset);
}

void CzoneInterface::setMagneticVariation(const float &magVar) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetValue(eCZoneMagneticVariation, magVar);
}

void CzoneInterface::setDepthOffset(const float &depthOffset) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetValue(eCZoneDepthOffset, depthOffset);
}

void CzoneInterface::setDateTime(const tCZoneTimeData &dateTime) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetArrayWithObject(eCZoneArrayDateTime, (void *)&dateTime, sizeof(tCZoneTimeData));
}

void CzoneInterface::syncDateTime(const int offset) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetValue(eCZoneTimeOffset, static_cast<float>(offset));
  CZoneOperation(eCZoneConfigSyncDateTime);
}

void CzoneInterface::setAlarmLogIndex(int index) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetValue(eCZoneAlarmLogSeverity, static_cast<float>(index));
}

void CzoneInterface::setUpdaterState(const tCZoneUpdaterData *data) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetUpdater(data);
}

void CzoneInterface::setUpdaterProgress(const int percent) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneSetUpdaterProgress(percent);
}

void CzoneInterface::resetMinMaxLog() {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneOperation(eCZoneResetCircuitLog);
}

void CzoneInterface::resetCircuitLog() {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneOperation(eCZoneResetCircuitLog);
}

void CzoneInterface::resetAlarmLog() {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneOperation(eCZoneResetAlarmLog);
}

void CzoneInterface::engineeringCommand(const uint8_t command, const uint8_t dipswitch, const uint8_t data1,
                                        const uint8_t data2, const uint8_t data3, const uint8_t data4) {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneEngineeringCommand(command, dipswitch, data1, data2, data3, data4);
}

void CzoneInterface::factoryReset() {
  std::lock_guard<std::mutex> lock(m_canMutex);
  CZoneOperation(eCZoneFactoryReset);
}

void CzoneInterface::engineeringData(const tCZoneEngineeringData *data) {
  switch (data->Command) {
  case eCZoneResetAddressClaim: {
    m_czoneSettings.setSourceAddress(0);
  } break;

  case eCZoneIdentifyDevice: {
    // HandleLEDs(eCZoneAppStateIdentify);
  } break;

  case eCZoneSetDipswitch: // Called by force dipswitch
  {
#ifndef NO_NMEA2K_LIB
    uint8_t src = NetworkSourceAddress();

    if (data->Data1 == src) {
      uint8_t const dipswitch = static_cast<uint8_t>(data->Data2);

      setDipswitch(dipswitch);
      m_czoneSettings.setDipswitch(dipswitch);
      // m_Settings.SendDipswitchUpdate(dipswitch);
    }
#endif
  } break;

  default: break;
  }
}

void CzoneInterface::registerEventCallback(std::function<void(const std::shared_ptr<Event> event)> Callback) {
  m_eventCallbacks.push_back(Callback);
}

void CzoneInterface::registerEventClientsConnectedCallback(std::function<bool(void)> Callback) {
  m_eventClientsConnectedCallback = Callback;
}

bool CzoneInterface::isEventClientsConnected() {
  if (m_eventClientsConnectedCallback) {
    return m_eventClientsConnectedCallback();
  }
  return false;
}

void CzoneInterface::publishEvent(const std::shared_ptr<Event> event) {
  if (m_eventCallbacks.size() > 0) {
    for (auto &it : m_eventCallbacks) {
      it(event);
    }
  } else {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::PublishEvent: no callback registered";
  }
}

void CzoneInterface::getConfigurationInformation(ConfigurationInformation &info) const {
  tCZoneConfigurationInformation CZoneInfo;
  CZoneConfigurationInformation(&CZoneInfo);
  info.ConfigurationId = CZoneInfo.ConfigurationId;
  info.ConfigurationVersion = CZoneInfo.ConfigurationVersion;
  info.ConfigurationFileVersion = CZoneInfo.ConfigurationFileVersion;
}

void CzoneInterface::getConfigGlobalInformation(ConfigGlobalInformation &info) const {
  tCZoneConfigGlobalInformation czoneGlobalInfo;
  CZoneConfigGlobalInformation(&czoneGlobalInfo);
  info.SleepEnabled = czoneGlobalInfo.SleepEnabled;
  info.SleepCircuitId = czoneGlobalInfo.SleepCircuitId;
}

void CzoneInterface::displayAlarmToEvent(const tCZoneDisplayAlarm *const DisplayAlarm, Event &event) {
  if (!DisplayAlarm) {
    BOOST_LOG_TRIVIAL(debug) << "CzoneInterface::DisplayAlarmToEvent: DisplayAlarm can not be NULL";
    return;
  }

  event.mutable_alarmItem().set_displayType(ConfigRequest::eConfigType(DisplayAlarm->DisplayType));
  event.mutable_alarmItem().set_id(DisplayAlarm->Id);
  event.mutable_alarmItem().set_alarmType(Alarm::eAlarmType(DisplayAlarm->AlarmType));
  event.mutable_alarmItem().set_severity(Alarm::eSeverityType(DisplayAlarm->Severity));
  event.mutable_alarmItem().set_currentState(Alarm::eStateType(DisplayAlarm->CurrentState));
  event.mutable_alarmItem().set_channelId(DisplayAlarm->ChannelId);
  event.mutable_alarmItem().set_externalAlarmId(DisplayAlarm->ExternalAlarmId);
  event.mutable_alarmItem().set_uniqueId(DisplayAlarm->UniqueId);
  event.mutable_alarmItem().set_valid(DisplayAlarm->Valid);
  event.mutable_alarmItem().set_acknowledgedTime(DisplayAlarm->ActivatedTime);
  event.mutable_alarmItem().set_acknowledgedTime(DisplayAlarm->AcknowledgedTime);
  event.mutable_alarmItem().set_clearedTime(DisplayAlarm->ClearedTime);

  // In git-czone-ui, application will look for alarms created by
  // Event_eEventType_AlarmAdded when receiving Event_eEventType_AlarmChanged
  // and Event_eEventType_AlarmRemoved with the same id, But Empower seems
  // waiting for a full alarm message when receiving all alarm events.

  if (event.get_type() == Event::eEventType::eAlarmAdded || event.get_type() == Event::eEventType::eAlarmChanged ||
      event.get_type() == Event::eEventType::eAlarmRemoved) {
    std::string title;
    std::string description;

    event.mutable_alarmItem().set_name(alarmString(DisplayAlarm->UniqueId, eCZoneAlarmName, false));
    event.mutable_alarmItem().set_channel(alarmString(DisplayAlarm->UniqueId, eCZoneAlarmChannelName, false));
    event.mutable_alarmItem().set_device(alarmString(DisplayAlarm->UniqueId, eCZoneAlarmDeviceName, false));

    title = alarmString(DisplayAlarm->UniqueId, eCZoneAlarmTitle, false);
    description = alarmString(DisplayAlarm->UniqueId, eCZoneAlarmDescription, false);

    if (title.length() == 0) {
      event.mutable_alarmItem().set_title(event.mutable_alarmItem().get_channel());
    } else {
      event.mutable_alarmItem().set_title(std::move(title));
    }

    std::string defaultDescription = alarmString(DisplayAlarm->UniqueId, eCZoneAlarmDefaultDescription, false);
    std::string groupDescription = alarmString(DisplayAlarm->UniqueId, eCZoneAlarmGroupPolicyDescription, false);
    std::string customizedDescription = description.substr(0, description.find("$$$"));

    if (customizedDescription.length() == 0) {
      if (groupDescription.length()) {
        customizedDescription = std::move(groupDescription);
      } else if (defaultDescription.length()) {
        customizedDescription = std::move(defaultDescription);
      }
    }
    event.mutable_alarmItem().set_description(std::move(customizedDescription));
    event.mutable_alarmItem().set_faultAction(alarmString(DisplayAlarm->UniqueId, eCZoneAlarmAction, false));

    if (DisplayAlarm->ExternalAlarmId >= SMARTCRAFT_FAULT_OFFSET) {
      event.mutable_alarmItem().set_faultType(
          std::stoi(alarmString(DisplayAlarm->UniqueId, eCZoneAlarmFaultType, false)));
      event.mutable_alarmItem().set_faultNumber(
          std::stoi(alarmString(DisplayAlarm->UniqueId, eCZoneAlarmFaultNumber, false)));
    }
  }
}

void CzoneInterface::processRTCoreConfig() {
  auto addLimit = [](bool enabled, float on, float off, const uint32_t id) {
    auto limit = AlarmLimit();
    limit.enabled = enabled;
    limit.on = on;
    limit.off = off;
    limit.id = id;
    return limit;
  };

  auto createDataId = [](const uint32_t id) {
    auto i = DataId(id, id != CZONE_INVALID_CIRCUIT_INDEX);
    return i;
  };

  auto getAlarmContent = [this](const uint16_t id, Alarm &alarm) {
    auto alarms = displayListNoLock(eCZoneStructDisplayAlarmConfig);
    for (auto &a : alarms) {
      if (id == a.Alarm.UniqueId) {
        this->populateAlarm(alarm, a.Alarm, false, true);
        return;
      }
    }
    return;
  };

  m_RTCoreConfig.clear();

  auto dcms = displayListNoLock(eCZoneStructDisplayMeteringDC);
  auto europaDcms = displayListNoLock(eCZoneStructEuropaCZoneDCDevices);
  Alarm alarm = Alarm();
  for (auto &dcm : dcms) {
    for (const auto &europaDcm : europaDcms) {
      if (europaDcm.DCConfigure.ChannelAddress == dcm.MeteringDevice.Address) {
        RTCoreMapEntry dcEntry;
        dcEntry.set_displaytype(ConfigRequest::eConfigType::eDC);

        uint32_t index = (europaDcm.DCConfigure.ChannelAddress & 0xFF) - 48;

        if (index >= 5) {
          BOOST_LOG_TRIVIAL(error) << "ProcessRTCoreConfig invalid dc index " << index << ", skip";
          continue;
        }
        if (index == 0) {
          // index 0 is Shunt and needs to be 4
          index = 4;
        } else {
          index--;
        }

        auto &dc = dcEntry.mutable_dcMeters();
        auto &alarmMap = dcEntry.mutable_alarms();
        dc.set_displayType(static_cast<ConfigRequest::eConfigType>(dcm.MeteringDevice.DisplayType));
        dc.set_id(dcm.MeteringDevice.Id);
        dc.set_nameUTF8(dcm.MeteringDevice.NameUTF8);
        addInstance(dc.mutable_instance(), dcm.MeteringDevice.Instance);
        dc.set_nominalVoltage(dcm.MeteringDevice.NominalVoltage);
        dc.set_address(dcm.MeteringDevice.Address);
        dc.set_capacity(dcm.MeteringDevice.Capacity);
        dc.set_warningLow(dcm.MeteringDevice.WarningLow);
        dc.set_warningHigh(dcm.MeteringDevice.WarningHigh);

        dc.set_veryHighLimit(addLimit(dcm.MeteringDevice.LimitEnabledMask & eCZoneVeryHighLimit,
                                      dcm.MeteringDevice.VeryHighOnLimit, dcm.MeteringDevice.VeryHighOffLimit,
                                      dcm.MeteringDevice.VeryHighAlarmId));
        if (dcm.MeteringDevice.LimitEnabledMask & eCZoneVeryHighLimit) {
          getAlarmContent(dcm.MeteringDevice.VeryHighAlarmId, alarm);
          alarmMap["vh"] = std::move(alarm);
        }

        dc.set_highLimit(addLimit(dcm.MeteringDevice.LimitEnabledMask & eCZoneHighLimit, dcm.MeteringDevice.HighOnLimit,
                                  dcm.MeteringDevice.HighOffLimit, dcm.MeteringDevice.HighAlarmId));
        if (dcm.MeteringDevice.LimitEnabledMask & eCZoneHighLimit) {
          getAlarmContent(dcm.MeteringDevice.HighAlarmId, alarm);
          alarmMap["f"] = std::move(alarm);
        }

        dc.set_lowLimit(addLimit(dcm.MeteringDevice.LimitEnabledMask & eCZoneLowLimit, dcm.MeteringDevice.LowOnLimit,
                                 dcm.MeteringDevice.LowOffLimit, dcm.MeteringDevice.LowAlarmId));
        if (dcm.MeteringDevice.LimitEnabledMask & eCZoneLowLimit) {
          getAlarmContent(dcm.MeteringDevice.LowAlarmId, alarm);
          alarmMap["lc"] = std::move(alarm);
        }

        dc.set_veryLowLimit(addLimit(dcm.MeteringDevice.LimitEnabledMask & eCZoneVeryLowLimit,
                                     dcm.MeteringDevice.VeryLowOnLimit, dcm.MeteringDevice.VeryLowOffLimit,
                                     dcm.MeteringDevice.VeryLowAlarmId));
        if (dcm.MeteringDevice.LimitEnabledMask & eCZoneVeryLowLimit) {
          getAlarmContent(dcm.MeteringDevice.VeryLowAlarmId, alarm);
          alarmMap["vlc"] = std::move(alarm);
        }

        dc.set_lowVoltage(addLimit(dcm.MeteringDevice.LimitEnabledMask & eCZoneLowVoltage,
                                   dcm.MeteringDevice.LowVoltageOn, dcm.MeteringDevice.LowVoltageOff,
                                   dcm.MeteringDevice.LowVoltageAlarmId));
        if (dcm.MeteringDevice.LimitEnabledMask & eCZoneLowVoltage) {
          getAlarmContent(dcm.MeteringDevice.LowVoltageAlarmId, alarm);
          alarmMap["l"] = std::move(alarm);
        }
        dc.set_veryLowVoltage(addLimit(dcm.MeteringDevice.LimitEnabledMask & eCZoneVeryLowVoltage,
                                       dcm.MeteringDevice.VeryLowVoltageOn, dcm.MeteringDevice.VeryLowVoltageOff,
                                       dcm.MeteringDevice.VeryLowVoltageAlarmId));
        if (dcm.MeteringDevice.LimitEnabledMask & eCZoneVeryLowVoltage) {
          getAlarmContent(dcm.MeteringDevice.VeryLowVoltageAlarmId, alarm);
          alarmMap["vl"] = std::move(alarm);
        }
        dc.set_highVoltage(addLimit(dcm.MeteringDevice.LimitEnabledMask & eCZoneHighVoltage,
                                    dcm.MeteringDevice.HighVoltageOn, dcm.MeteringDevice.HighVoltageOff,
                                    dcm.MeteringDevice.HighVoltageAlarmId));
        if (dcm.MeteringDevice.LimitEnabledMask & eCZoneHighVoltage) {
          getAlarmContent(dcm.MeteringDevice.HighVoltageAlarmId, alarm);
          alarmMap["h"] = std::move(alarm);
        }
        dc.set_canResetCapacity((dcm.MeteringDevice.CanResetCapacity == CZONE_TRUE));
        dc.set_dcType(
            static_cast<MeteringDevice::eDCType>((dcm.MeteringDevice.Capabilities >> 24) & CZONE_TYPE_MASK_STRUCT));
        dc.set_showVoltage((dcm.MeteringDevice.Capabilities & CZONE_SHOW_VOLTS));
        dc.set_showCurrent((dcm.MeteringDevice.Capabilities & CZONE_SHOW_CURRENT));
        dc.set_showStateOfCharge((dcm.MeteringDevice.Capabilities & CZONE_SHOW_STATE_OF_CHARGE));
        dc.set_showTemperature((dcm.MeteringDevice.Capabilities & CZONE_SHOW_TEMPERATURE));
        dc.set_showTimeOfRemaining((dcm.MeteringDevice.Capabilities & CZONE_SHOW_TIME_REMAINING));
        m_RTCoreConfig.mutable_dcMeters()[index] = dcEntry;
      }
    }
  }

  auto ads = displayListNoLock(eCZoneStructEuropaCZoneADDevices);
  for (const auto &ad : ads) {
    tCZoneDisplayType type = CZONE_TYPE_INVALID_ID;
    switch (ad.ADConfigure.ADType) {
    case eCZoneADTypeFluidLevel: type = eCZoneStructDisplayMonitoringTank; break;
    case eCZoneADTypePressure: type = eCZoneStructDisplayMonitoringPressure; break;
    case eCZoneADTypeTemperature: type = eCZoneStructDisplayMonitoringTemperature; break;
    default: break;
    }

    auto items = displayListNoLock(type);
    for (const auto &item : items) {
      if (ad.ADConfigure.ChannelAddress == item.MonitoringDevice.Address) {
        RTCoreMapEntry adEntry;
        auto &md = adEntry.mutable_monitoringDevice();
        auto &alarmMap = adEntry.mutable_alarms();

        uint32_t index = (ad.ADConfigure.ChannelAddress & 0xFF) - 49;
        if (index >= 4) {
          BOOST_LOG_TRIVIAL(error) << "ProcessRTCoreConfig invalid ad index " << index << ", skip";
          continue;
        }

        switch (type) {
        case eCZoneStructDisplayMonitoringTank:
          adEntry.set_displaytype(ConfigRequest::eConfigType::eTank);
          md.set_tankType(static_cast<MonitoringType::eTankType>(item.MonitoringDevice.Type));
          md.set_tankCapacity(item.MonitoringDevice.Capacity);
          break;
        case eCZoneStructDisplayMonitoringPressure:
          adEntry.set_displaytype(ConfigRequest::eConfigType::ePressure);
          md.set_pressureType(static_cast<MonitoringType::ePressureType>(item.MonitoringDevice.Type));
          md.set_atmosphericPressure(item.MonitoringDevice.AtmosphericPressure == CZONE_TRUE);
          break;
        case eCZoneStructDisplayMonitoringTemperature:
          adEntry.set_displaytype(ConfigRequest::eConfigType::eTemperature);
          md.set_temperatureType(static_cast<MonitoringType::eTemperatureType>(item.MonitoringDevice.Type));
          md.set_highTemperature(item.MonitoringDevice.HighTemperature == CZONE_TRUE);
          break;
        default: break;
        }

        md.set_displayType(static_cast<ConfigRequest::eConfigType>(item.MonitoringDevice.DisplayType));
        md.set_id(item.MonitoringDevice.Id);
        md.set_nameUTF8(item.MonitoringDevice.NameUTF8);
        addInstance(md.mutable_instance(), item.MonitoringDevice.Instance);

        md.set_circuitId(createDataId(item.MonitoringDevice.CircuitId));
        md.set_switchType(static_cast<CircuitDevice::eSwitchType>(item.MonitoringDevice.SwitchType));
        md.set_confirmDialog(static_cast<CircuitDevice::eConfirmType>(item.MonitoringDevice.ConfirmDialog));
        md.set_circuitNameUTF8(item.MonitoringDevice.CircuitNameUTF8);

        md.set_lowLimit(addLimit(item.MonitoringDevice.LimitEnabledMask & eCZoneLowLimit,
                                 item.MonitoringDevice.LowOnLimit, item.MonitoringDevice.LowOffLimit,
                                 item.MonitoringDevice.LowAlarmId));
        if (item.MonitoringDevice.LimitEnabledMask & eCZoneLowLimit) {
          getAlarmContent(item.MonitoringDevice.LowAlarmId, alarm);
          alarmMap["l"] = std::move(alarm);
        }

        md.set_veryLowLimit(addLimit(item.MonitoringDevice.LimitEnabledMask & eCZoneVeryLowLimit,
                                     item.MonitoringDevice.VeryLowOnLimit, item.MonitoringDevice.VeryLowOffLimit,
                                     item.MonitoringDevice.VeryLowAlarmId));
        if (item.MonitoringDevice.LimitEnabledMask & eCZoneVeryLowLimit) {
          getAlarmContent(item.MonitoringDevice.VeryLowAlarmId, alarm);
          alarmMap["vl"] = std::move(alarm);
        }

        md.set_highLimit(addLimit(item.MonitoringDevice.LimitEnabledMask & eCZoneHighLimit,
                                  item.MonitoringDevice.HighOnLimit, item.MonitoringDevice.HighOffLimit,
                                  item.MonitoringDevice.HighAlarmId));
        if (item.MonitoringDevice.LimitEnabledMask & eCZoneHighLimit) {
          getAlarmContent(item.MonitoringDevice.HighAlarmId, alarm);
          alarmMap["h"] = std::move(alarm);
        }

        md.set_veryHighLimit(addLimit(item.MonitoringDevice.LimitEnabledMask & eCZoneVeryHighLimit,
                                      item.MonitoringDevice.VeryHighOnLimit, item.MonitoringDevice.VeryHighOffLimit,
                                      item.MonitoringDevice.VeryHighAlarmId));
        if (item.MonitoringDevice.LimitEnabledMask & eCZoneVeryHighLimit) {
          getAlarmContent(item.MonitoringDevice.VeryHighAlarmId, alarm);
          alarmMap["vh"] = std::move(alarm);
        }

        md.set_address(item.MonitoringDevice.Address);

        m_RTCoreConfig.mutable_monitoringDevice()[index] = adEntry;
      }
    }

    if (ad.ADConfigure.Mode == eCZoneADModeSwitchBatteryPositive ||
        ad.ADConfigure.Mode == eCZoneADModeSwitchBatteryNegtive) {
      tZoneAdChannelConfig adConfig;
      if (!tCZoneEuropaAnalogueControl::GetAdChannelConfigurationByChannelAddress(ad.ADConfigure.ChannelAddress,
                                                                                  &adConfig)) {
        BOOST_LOG_TRIVIAL(error) << "ProcessRTCoreConfig GetAdChannelConfigurationByIndex error, "
                                    "skip";
        continue;
      }

      RTCoreMapEntry adEntry;
      auto &alarmMap = adEntry.mutable_alarms();
      auto &spg = adEntry.mutable_switchPositiveNegtive();
      uint32_t index = (ad.ADConfigure.ChannelAddress & 0xFF) - 49;
      uint32_t binaryStatusIndex;
      if (ad.ADConfigure.Mode == eCZoneADModeSwitchBatteryPositive) {
        binaryStatusIndex = index + 56; // Switch to Pos Binary Logic Status Index. (See
                                        // 'bitSignalSwitchToPos' section definition in
                                        // 'Common\ZoneConfiguration\devices\EuropaItemIndexes.c')
      } else {
        binaryStatusIndex = index + 60; // Switch to Neg Binary Logic Status Index. (See
                                        // 'bitSignalSwitchToNeg' section definition in
                                        // 'Common\ZoneConfiguration\devices\EuropaItemIndexes.c')
      }

      if (index >= 4) {
        BOOST_LOG_TRIVIAL(error) << "ProcessRTCoreConfig invalid ad index " << index << ", skip";
        continue;
      }
      spg.set_binaryStatusIndex(binaryStatusIndex);
      spg.set_channelAddress(ad.ADConfigure.ChannelAddress);
      spg.set_channel(ad.ADConfigure.Channel);

// CZoneGetAlarmId is a temporary solution here, because there is no way
// to get AlarmId from tZoneAdChannelConfig or ad.ADConfigure yet.
#define CZ_ALARM_SI_SIGNAL_HIGH_ALARM_CODE 8
#define CZ_ALARM_SI_SIGNAL_LOW_ALARM_CODE 9

      if (ad.ADConfigure.Mode == eCZoneADModeSwitchBatteryPositive) {
        spg.set_mode(SwitchPositiveNegtive::eSwitchPositiveNegtiveMode::eSwitchBatteryPositive);
      } else if (ad.ADConfigure.Mode == eCZoneADModeSwitchBatteryNegtive) {
        spg.set_mode(SwitchPositiveNegtive::eSwitchPositiveNegtiveMode::eSwitchBatteryNegtive);
      }

      // this aligns with tCZoneDisplayDatabase::AddAlarms(bool simulate)
      if (adConfig.highAlarmEnabled) {
        if (ad.ADConfigure.Mode == eCZoneADModeSwitchBatteryNegtive) {
          getAlarmContent(CZoneGetAlarmId(ad.ADConfigure.ChannelAddress, CZ_ALARM_SI_SIGNAL_LOW_ALARM_CODE, false),
                          alarm);
          alarmMap["l"] = std::move(alarm);
        } else {
          getAlarmContent(CZoneGetAlarmId(ad.ADConfigure.ChannelAddress, CZ_ALARM_SI_SIGNAL_HIGH_ALARM_CODE, false),
                          alarm);
          alarmMap["h"] = std::move(alarm);
        }
      }

      if (adConfig.lowAlarmEnabled) {
        if (ad.ADConfigure.Mode == eCZoneADModeSwitchBatteryPositive) {
          getAlarmContent(CZoneGetAlarmId(ad.ADConfigure.ChannelAddress, CZ_ALARM_SI_SIGNAL_HIGH_ALARM_CODE, false),
                          alarm);
          alarmMap["h"] = std::move(alarm);
        } else {
          getAlarmContent(CZoneGetAlarmId(ad.ADConfigure.ChannelAddress, CZ_ALARM_SI_SIGNAL_LOW_ALARM_CODE, false),
                          alarm);
          alarmMap["l"] = std::move(alarm);
        }
      }

      adEntry.set_displaytype(ConfigRequest::eConfigType::eSwitchPositiveNegtive);
      m_RTCoreConfig.mutable_switchPositiveNegtive()[index] = adEntry;
    }
  }

  auto circuits = displayListNoLock(eCZoneStructDisplayCircuits);
  for (auto &c : circuits) {
    if (c.Circuit.CircuitType == CircuitDevice::eCircuitType::eCircuit) {
      if (c.Circuit.NonVisibleCircuit == CZONE_TRUE) {
        continue;
      }

      auto loads = displayListNoLock(eCZoneStructDisplayCircuitLoad, c.Circuit.ControlId, 0);
      for (const auto &l : loads) {
        uint32_t index = l.CircuitLoads.ChannelAddress & 0xff - 32;
        uint8_t dipSwitch = (uint8_t)((l.CircuitLoads.ChannelAddress >> 8) & 0xff);

        if (dipSwitch == getDipswitch()) {
          if (index >= 5) {
            BOOST_LOG_TRIVIAL(error) << "ProcessRTCoreConfig invalid CircuitLoad index " << index << ", skip";
            continue;
          }

          if (m_RTCoreConfig.get_circuitLoads().find(index) == m_RTCoreConfig.get_circuitLoads().end()) {
            RTCoreMapEntry clEntry;
            clEntry.set_displaytype(ConfigRequest::eConfigType::eCircuitLoads);
            auto &circuitLoad = clEntry.mutable_circuitLoads();

            circuitLoad.set_displayType(static_cast<ConfigRequest::eConfigType>(l.CircuitLoads.DisplayType));
            circuitLoad.set_id(static_cast<uint32_t>(l.CircuitLoads.Id));
            circuitLoad.set_nameUTF8(l.CircuitLoads.NameUTF8);
            circuitLoad.set_channelAddress(l.CircuitLoads.ChannelAddress);
            circuitLoad.set_fuseLevel((static_cast<float>(l.CircuitLoads.FuseLevel) / 10.0f));
            circuitLoad.set_runningCurrent((static_cast<float>(l.CircuitLoads.RunningCurrent) / 10.0f));
            circuitLoad.set_systemOnCurrent((static_cast<float>(l.CircuitLoads.SystemOnCurrent) / 10.0f));
            circuitLoad.set_forceAcknowledgeOn(l.CircuitLoads.ForceAcknowledgeOn);
            circuitLoad.set_level(l.CircuitLoads.Level);
            circuitLoad.set_controlType(static_cast<CircuitLoad::eControlType>(l.CircuitLoads.ControlType));
            circuitLoad.set_isSwitchedModule(l.CircuitLoads.IsSwitchedModule);

            m_RTCoreConfig.mutable_circuitLoads()[index] = clEntry;
          }

          const uint32_t doubleThrowMask = 0x8000;
          auto &circuit = m_RTCoreConfig.mutable_circuitLoads()[index].mutable_circuit();

          circuit.set_displayType(static_cast<ConfigRequest::eConfigType>(c.Circuit.DisplayType));
          circuit.set_id(std::make_pair(c.Circuit.Id, (c.Circuit.Id != CZONE_INVALID_CIRCUIT_INDEX)));
          circuit.set_nameUTF8(c.Circuit.NameUTF8);
          circuit.set_singleThrowId(createDataId(c.Circuit.SingleThrowId));
          for (uint32_t i = 0; i < 16; i++) {
            std::string &sequentialname = circuit.add_sequentialNamesUTF8();
            sequentialname = std::string(c.Circuit.SequentialNamesUTF8[i]);
          }
          circuit.set_hasComplement(c.Circuit.HasComplement == CZONE_TRUE);
          circuit.set_displayCategories(c.Circuit.DisplayCategories);
          circuit.set_confirmDialog(static_cast<CircuitDevice::eConfirmType>(c.Circuit.ConfirmDialog));
          circuit.set_voltageSource(Instance(c.Circuit.VoltageSource, c.Circuit.VoltageSource != 0xff));
          circuit.set_circuitType(static_cast<CircuitDevice::eCircuitType>(c.Circuit.CircuitType));
          circuit.set_switchType(static_cast<CircuitDevice::eSwitchType>(c.Circuit.SwitchType &= ~doubleThrowMask));
          circuit.set_switchString(c.Circuit.SwitchString);
          circuit.set_minLevel(static_cast<uint32_t>(c.Circuit.MinLevel));
          circuit.set_maxLevel(static_cast<uint32_t>(c.Circuit.MaxLevel));
          circuit.set_dimstep(static_cast<uint32_t>(c.Circuit.Dimstep));
          circuit.set_dimmable((c.Circuit.Dimmable == CZONE_TRUE));
          circuit.set_loadSmoothStart(c.Circuit.LoadSmoothStart);
          circuit.set_sequentialStates(c.Circuit.SequentialStates);
          circuit.set_controlId(c.Circuit.ControlId);
          circuit.set_systemsOnAnd(c.Circuit.SystemsOnAnd);

          auto loads = displayListNoLock(eCZoneStructDisplayCircuitLoad, c.Circuit.ControlId, 0);
          for (auto &l : loads) {
            CircuitLoad &circuitLoad = circuit.add_circuitLoad();

            circuitLoad.set_displayType(static_cast<ConfigRequest::eConfigType>(l.CircuitLoads.DisplayType));
            circuitLoad.set_id(static_cast<uint32_t>(l.CircuitLoads.Id));
            circuitLoad.set_nameUTF8(l.CircuitLoads.NameUTF8);
            circuitLoad.set_channelAddress(l.CircuitLoads.ChannelAddress);
            circuitLoad.set_fuseLevel((static_cast<float>(l.CircuitLoads.FuseLevel) / 10.0f));
            circuitLoad.set_runningCurrent((static_cast<float>(l.CircuitLoads.RunningCurrent) / 10.0f));
            circuitLoad.set_systemOnCurrent((static_cast<float>(l.CircuitLoads.SystemOnCurrent) / 10.0f));
            circuitLoad.set_forceAcknowledgeOn(l.CircuitLoads.ForceAcknowledgeOn);
            circuitLoad.set_level(l.CircuitLoads.Level);
            circuitLoad.set_controlType(static_cast<CircuitLoad::eControlType>(l.CircuitLoads.ControlType));
            circuitLoad.set_isSwitchedModule(l.CircuitLoads.IsSwitchedModule);
          }

          auto categories = displayListNoLock(eCZoneStructDisplayEnabledCategories, c.Circuit.DisplayCategories, 0);
          for (auto &c : categories) {
            CategoryItem &category = circuit.add_category();
            category.set_nameUTF8(c.CategoryItem.NameUTF8);
            category.set_enabled(c.CategoryItem.Enabled == CZONE_TRUE);
          }

          circuit.set_dcCircuit(c.Circuit.DisplayCategories & (1 << 21));
          circuit.set_acCircuit(c.Circuit.DisplayCategories & (1 << 22));
          circuit.set_primaryCircuitId(c.Circuit.PrimaryCircuitId);
          circuit.set_remoteVisibility(c.Circuit.RemoteVisibility);
        }
      }
    }
  }
}

float value(tCZoneDataType dataType, uint32_t instance, bool &valid, std::map<uint32_t, uint32_t> &dataTypeIndex) {
  auto createKey = [](tCZoneDataType dataType, uint32_t instance) -> uint32_t {
    return (static_cast<uint32_t>(dataType) << 16) | instance & 0xffff;
  };

  float value = 0.0f;
  auto key = createKey(dataType, instance);
  auto it = dataTypeIndex.find(key);

  if (it == dataTypeIndex.end()) {
    auto index = CZoneMonitoringCreateDataIndex(dataType, instance);
    dataTypeIndex[key] = index;
    valid = CZoneMonitoringData(index, &value);
  } else {
    valid = CZoneMonitoringData(it->second, &value);
  }

  return value;
}

ConfigResult CzoneInterface::getConfig(const ConfigRequest &request) {
  m_config.clear();
  return genConfig(request);
}

ConfigResult CzoneInterface::getAllConfig() {
  m_config.clear();
  genConfig(ConfigRequest(ConfigRequest::eAlarms));
  genConfig(ConfigRequest(ConfigRequest::eControl));
  genConfig(ConfigRequest(ConfigRequest::eAC));
  genConfig(ConfigRequest(ConfigRequest::eDC));
  genConfig(ConfigRequest(ConfigRequest::eTank));
  genConfig(ConfigRequest(ConfigRequest::eTemperature));
  genConfig(ConfigRequest(ConfigRequest::ePressure));
  genConfig(ConfigRequest(ConfigRequest::eACMain));
  genConfig(ConfigRequest(ConfigRequest::eInverterCharger));
  genConfig(ConfigRequest(ConfigRequest::eDevice));
  genConfig(ConfigRequest(ConfigRequest::eMode));
  genConfig(ConfigRequest(ConfigRequest::eCircuit));
  genConfig(ConfigRequest(ConfigRequest::eScreenConfigPageImageItem));
  genConfig(ConfigRequest(ConfigRequest::eScreenConfigPageImage));
  genConfig(ConfigRequest(ConfigRequest::eScreenConfigPageGridItem));
  genConfig(ConfigRequest(ConfigRequest::eScreenConfigPage));
  genConfig(ConfigRequest(ConfigRequest::eScreenConfigMode));
  genConfig(ConfigRequest(ConfigRequest::eScreenConfig));
  genConfig(ConfigRequest(ConfigRequest::eHVAC));
  genConfig(ConfigRequest(ConfigRequest::eThirdPartyGenerator));
  genConfig(ConfigRequest(ConfigRequest::eZipdeeAwning));
  genConfig(ConfigRequest(ConfigRequest::eFantasticFan));
  genConfig(ConfigRequest(ConfigRequest::eShoreFuse));
  genConfig(ConfigRequest(ConfigRequest::eTyrePressure));
  genConfig(ConfigRequest(ConfigRequest::eAudioStereo));
  genConfig(ConfigRequest(ConfigRequest::eCircuitLoads));
  genConfig(ConfigRequest(ConfigRequest::eCategories));
  genConfig(ConfigRequest(ConfigRequest::eEngines));
  genConfig(ConfigRequest(ConfigRequest::eGNSS));
  genConfig(ConfigRequest(ConfigRequest::eFavouritesMode));
  genConfig(ConfigRequest(ConfigRequest::eFavouritesControl));
  genConfig(ConfigRequest(ConfigRequest::eFavouritesMonitoring));
  genConfig(ConfigRequest(ConfigRequest::eFavouritesAlarm));
  genConfig(ConfigRequest(ConfigRequest::eFavouritesACMain));
  genConfig(ConfigRequest(ConfigRequest::eFavouritesInverterCharger));
  genConfig(ConfigRequest(ConfigRequest::eFavouritesBoatView));
  genConfig(ConfigRequest(ConfigRequest::eUiRelationships));
  genConfig(ConfigRequest(ConfigRequest::eBinaryLogicStates));
  genConfig(ConfigRequest(ConfigRequest::eCZoneRaw));
  genConfig(ConfigRequest(ConfigRequest::eRTCoreMap));
  genConfig(ConfigRequest(ConfigRequest::eSwitchPositiveNegtive));
  genConfig(ConfigRequest(ConfigRequest::eNonVisibleCircuit));
  return m_config;
}

void CzoneInterface::registerDbus(std::shared_ptr<DbusService> dbusService) {
  dbusService->registerService("GetConfigAll", "czone", [ptr = this]() -> std::string {
    auto r = ptr->getAllConfig();
    return r.tojson().dump();
  });

  dbusService->registerService("GetConfig", "czone", [ptr = this](std::string type) -> std::string {
    auto r = ptr->getConfig(ConfigRequest::from_string(type));
    return r.tojson().dump();
  });

  dbusService->registerService("GetCategories", "czone", [ptr = this](std::string type) -> std::string {
    auto r = ptr->getCategories(CategoryRequest::from_string(type));
    return r.tojson().dump();
  });

  dbusService->registerSignal("Event", "czone");
  registerEventCallback([&dbusService](std::shared_ptr<Event> event) {
    BOOST_LOG_TRIVIAL(info) << "Event callback for signal (dbus) " << Event::to_string(event->get_type());
    dbusService->emitSignal("Event", "czone", event->tojson().dump());
  });
}
