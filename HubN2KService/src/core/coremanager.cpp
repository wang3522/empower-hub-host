#include "core/coremanager.h"
#include "N2KCoreApp_version.h"
#include "utils/common.h"
#include "utils/logger.h"

#include <App/ContourZoneProductIds.h>

#include <chrono>
#include <cstdlib>
#include <thread>

void setCANBaudRate(const std::string &iface, int baudrate) {
  std::string cmd = "sudo ip link set " + iface +
                    " down && "
                    "sudo ip link set " +
                    iface + " type can bitrate " + std::to_string(baudrate) +
                    " && "
                    "sudo ip link set " +
                    iface + " up";
  auto i = system(cmd.c_str());
  if (i != 0) {
    BOOST_LOG_TRIVIAL(error) << "Failed to set CAN baud rate on interface " << iface;
    throw std::runtime_error("Failed to set CAN baud rate");
  }
  BOOST_LOG_TRIVIAL(debug) << "setCANBaudRate: CAN baud rate set to " << baudrate << " on interface " << iface;
}

CoreManager::CoreManager()
    : m_running(false),
      m_canService(CanService::getInstance()),
      m_dbusService(std::make_shared<DbusService>(CzoneSystemConstants::DBUS_CZONE_SERVICENAME,
                                                  CzoneSystemConstants::DBUS_CZONE_OBJECTPATH)) {}

CoreManager::~CoreManager() { stop(); }

CoreManager &CoreManager::getInstance() {
  static CoreManager _instance;
  return _instance;
}

void CoreManager::start() {
  if (m_running.load()) {
    BOOST_LOG_TRIVIAL(error) << "CoreManager is already running!";
    return;
  }

  // Initialize default configuration values
  auto dipswitch = CzoneSystemConstants::DEFAULT_DIPSWITCH;
  auto insecure = true;
  uint32_t uniqueId = mtEuropa;
  uint16_t productId = CZ_PRODUCT_CODE_EUROPA;
  uint8_t lastSourceAddress = 0;
  auto &can_channel = CzoneSystemConstants::DEFAULT_CAN_CHANNEL;
  auto &nema_channel = CzoneSystemConstants::DEFAULT_NEMA_CHANNEL;
  auto &mercury_engine = CzoneSystemConstants::DEFAULT_MERCURY_ENGINE_S;

  // Reset CAN network to ensure correct baud rate
  setCANBaudRate(can_channel, 250000);

  // Retrieve and update Czone settings
  auto &czonesettings = CzoneSettings::getInstance();
  auto stored_dipswitch = czonesettings.getDipswitch();
  if ((stored_dipswitch == 0) && (dipswitch != 0)) {
    stored_dipswitch = dipswitch;
    czonesettings.setDipswitch(stored_dipswitch);
  }
  czonesettings.setInsecure(insecure);

  // Initialize Czone interface and database
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Initializing";
  auto czoneInterface = std::make_shared<CzoneInterface>(czonesettings, m_canService.getCanServiceMutex());
  auto czoneData = std::make_shared<CzoneDatabase>(m_canService);

  // Initialize Czone interface
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Interface intializing.";
  czoneInterface->init(stored_dipswitch, uniqueId);
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Interface initialized.";

  // Initialize CAN service with all required parameters
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: CanService intializing.";
  m_canService.initialise(&czonesettings, czoneInterface.get(), can_channel, stored_dipswitch, uniqueId, productId,
                          lastSourceAddress, nema_channel, mercury_engine);
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: CanService initialized.";

  // Start CAN service main loop
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: Starting CanService...";
  m_canService.service(true);
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::start: CanService started.";

  // Initialize and run D-Bus service, register Czone interface
  m_dbusService->initialize();

  m_dbusService->registerService("version", "status", []() { return std::string(N2KCoreApp::VERSION_STRING); });

  m_dbusService->registerService(
      "GetSetting", "czone",
      [ptr = this, &czonesettings, czoneInterface, czoneData](std::string settingRequestStr) -> std::string {
        BOOST_LOG_TRIVIAL(debug) << settingRequestStr; // [x] debug
        try {
          json req;
          req["Type"] = settingRequestStr;
          SettingRequest request(req);
          auto r = ptr->getSettings(request, czonesettings, *czoneInterface.get(), *czoneData.get());
          return r.dump();
        } catch (const std::exception &e) {
          BOOST_LOG_TRIVIAL(error) << "GetSetting:Error " << e.what();
          ptr->m_dbusService->throwError("GetSetting:Error " + std::string(e.what()));
        }
        return "";
      });

  m_dbusService->registerService(
      "AddSetting", "czone", [ptr = this, &czonesettings, czoneInterface, czoneData](std::string settingRequestStr) {
        try {
          SettingRequest request(json::parse(settingRequestStr));
          ptr->addSettings(request, czonesettings, *czoneInterface.get(), *czoneData.get());
        } catch (const std::exception &e) {
          BOOST_LOG_TRIVIAL(error) << "AddSetting:Error " << e.what();
          ptr->m_dbusService->throwError("AddSetting:Error " + std::string(e.what()));
        }
      });

  czoneInterface->registerDbus(m_dbusService);
  czoneData->registerDbus(m_dbusService);

  m_dbusService->run();

  // Mark as running and enter main loop
  m_running.store(true);
  this->run();
}

void CoreManager::stop() {
  // Stop all services and clean up resources
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::stop: Stopping CoreManager...";

  m_canService.setShutdownSignal(true);
  m_canService.service(false);
  m_canService.reset();

  if (m_dbusService) {
    m_dbusService->stop();
    m_dbusService.reset();
  }
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::stop: DbusService stopped.";

  if (!m_running.load()) {
    return;
  }
  m_running.store(false);
}

void CoreManager::run() {
  while (m_running.load()) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
  BOOST_LOG_TRIVIAL(debug) << "CoreManager::run: CoreManager has stopped.";
}

json CoreManager::getSettings(const SettingRequest &request, CzoneSettings &czoneSettings,
                              CzoneInterface &czoneInterface, CzoneDatabase &czoneData) {
  json result;

  switch (request.m_Type) {
  case SettingRequest::eSettingType::eFactoryData: {
    result["FactoryData"] = json::object();
    auto &factoryData = result["FactoryData"];
    factoryData["SerialNumber"] = czoneSettings.getSerialNumber();
    factoryData["FactoryICCID"] = czoneSettings.getFactoryICCID();
    factoryData["FactoryIMEI"] = czoneSettings.getFactoryIMEI();
    factoryData["RTFirmwareVersion"] = czoneSettings.getAPPFirmwareVersion(); //[x] remove after its change in N2K Client
    factoryData["APPFirmwareVersion"] = czoneSettings.getAPPFirmwareVersion();
    factoryData["ArtifactInfo"] = czoneSettings.getHostArtifactInfo();
    factoryData["ApplicationVersion"] = std::string(N2KCoreApp::VERSION_STRING);
  } break;
  case SettingRequest::eSettingType::eGlobal: {
    CzoneInterface::ConfigGlobalInformation info;
    czoneInterface.getConfigGlobalInformation(info);
    result["SleepEnabled"] = info.SleepEnabled;
    result["SleepCircuitId"] = info.SleepCircuitId;
  } break;
  case SettingRequest::eSettingType::eConfig: {
    CzoneInterface::ConfigurationInformation info;
    czoneInterface.getConfigurationInformation(info);
    result["ConfigId"] = info.ConfigurationId;
    result["ConfigVersion"] = info.ConfigurationVersion;
    result["ConfigFileVersion"] = info.ConfigurationFileVersion;
    std::string cName = czoneInterface.configName();
    if (cName.length() > 0) {
      result["ConfigName"] = cName;
    }
    std::string libVersion = czoneInterface.libraryVersion();
    if (libVersion.length() > 0) {
      result["LibraryVersion"] = libVersion;
    }
  } break;
  case SettingRequest::eSettingType::eDipswitch: {
    result["DipswitchValue"] = czoneInterface.getDipswitch();
  } break;

  case SettingRequest::eSettingType::eDepthOffset: {
    float value;
    if (czoneData.GetSetting(CZoneDbSettingsDepthOffset, value)) {
      result["DepthOffset"] = value;
    }
  } break;
  case SettingRequest::eSettingType::eMagneticVariation: {
    float value;
    if (czoneData.GetSetting(CZoneDbSettingsMagneticVariation, value)) {
      result["MagneticVariation"] = value;
    }
  } break;
  case SettingRequest::eSettingType::eTimeOffset: {
    int32_t value;
    if (czoneData.GetSetting(CZoneDbSettingsTimeOffset, value)) {
      result["TimeOffset"] = value;
    }
  } break;
  case SettingRequest::eSettingType::eAlarmGlobal: {
    result["AlarmGlobalSettings"] = json::object();
    auto &alarmGlobalSettings = result["AlarmGlobalSettings"];

    switch (czoneInterface.highestEnabledSeverity()) {
    case eCZoneAlarmSeverityCritical:
      alarmGlobalSettings["HighestEnabledSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityCritical);
      break;
    case eCZoneAlarmSeverityImportant:
      alarmGlobalSettings["HighestEnabledSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityImportant);
      break;
    case eCZoneAlarmSeverityStandard:
      alarmGlobalSettings["HighestEnabledSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityStandard);
      break;
    case eCZoneAlarmSeverityWarning:
      alarmGlobalSettings["HighestEnabledSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityWarning);
      break;
    case eCZoneAlarmSeveritySIO:
      alarmGlobalSettings["HighestEnabledSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeveritySIO);
      break;
    default:
      alarmGlobalSettings["HighestEnabledSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityWarning);
      break;
    }

    switch (czoneInterface.highestAcknowledgedSeverity()) {
    case eCZoneAlarmSeverityCritical:
      alarmGlobalSettings["HighestAcknowledgedSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityCritical);
      break;
    case eCZoneAlarmSeverityImportant:
      alarmGlobalSettings["HighestAcknowledgedSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityImportant);
      break;
    case eCZoneAlarmSeverityStandard:
      alarmGlobalSettings["HighestAcknowledgedSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityStandard);
      break;
    case eCZoneAlarmSeverityWarning:
      alarmGlobalSettings["HighestAcknowledgedSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityWarning);
      break;
    case eCZoneAlarmSeveritySIO:
      alarmGlobalSettings["HighestAcknowledgedSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeveritySIO);
      break;
    default:
      alarmGlobalSettings["HighestAcknowledgedSeverity"] = Alarm::to_string(Alarm::eSeverityType::eSeverityWarning);
      break;
    }
  } break;

  default: break;
  }
  return result;
}

void CoreManager::addSettings(const SettingRequest &request, CzoneSettings &czoneSettings,
                              CzoneInterface &czoneInterface, CzoneDatabase &czoneData) {

  switch (request.m_Type) {
  case SettingRequest::eSettingType::eDipswitch:
    if (request.m_DipswitchValue != nullptr) {
      czoneInterface.setDipswitch(*request.m_DipswitchValue);
    }
    break;
  case SettingRequest::eSettingType::eTimeOffset:
    if (request.m_TimeOffsetValue != nullptr) {
      czoneInterface.setTimeOffset(*request.m_TimeOffsetValue);
    }
    break;
  case SettingRequest::eSettingType::eMagneticVariation:
    if (request.m_MagneticVariationValue != nullptr) {
      czoneInterface.setMagneticVariation(*request.m_MagneticVariationValue);
    }
    break;
  case SettingRequest::eSettingType::eDepthOffset:
    if (request.m_DepthOffsetValue != nullptr) {
      czoneInterface.setDepthOffset(*request.m_DepthOffsetValue);
    }
    break;
  case SettingRequest::eSettingType::eDateTime:
    if (request.m_Payload != nullptr) {
      tCZoneTimeData dateTime;
      memcpy((void *)&dateTime, request.m_Payload->data(), sizeof(tCZoneTimeData));
      czoneInterface.setDateTime(dateTime);
    }
    break;
  case SettingRequest::eSettingType::eBacklightLevel:
    if (request.m_BacklightValue != nullptr) {
      czoneInterface.setBacklightLevel(*request.m_BacklightValue);
    }
    break;
  case SettingRequest::eSettingType::eBatteryFull:
    if (request.m_BatteryFullValue != nullptr) {
      czoneInterface.setBatteryFull(*request.m_BatteryFullValue);
    }
    break;
  default: break;
  }
}