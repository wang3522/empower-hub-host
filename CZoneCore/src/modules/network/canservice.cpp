#include "modules/network/canservice.h"
#include "common/commonSettings.h"
#include "utils/logger.h"

#include <App/ContourZoneProductIds.h>
#include <Base/CZonePlatform.h>
#include <Nmea2kLib/tNetworkInterface.h>
#include <Nmea2kLib/tNetworkTypes.h>
#include <ZoneConfiguration/tCZoneModuleTypes.h>

#include <iomanip>
#include <sstream>
#include <string>
#include <thread>

CanService *CanService::m_instance = nullptr;

CanService &CanService::getInstance() {
  static CanService _instance;
  m_instance = &_instance;
  return *m_instance;
}

void CanService::initialize(const std::string &channel, const uint8_t dipswitch,
                            const uint32_t nmeaChannel,
                            bool mercuryEngineState) {
  if (!m_instance) {
    throw std::runtime_error("CanService instance must be created using "
                             "getInstance() before calling initialize().");
  }

  BOOST_LOG_TRIVIAL(info) << "Initializing CanService...";

  const std::lock_guard<std::mutex> lock(m_initmutex);
  m_init.store(InitStatus::INITIALIZING);
  SetNetworkSourceAddressChanged([](const uint8_t address) {
    CanService::getInstance().sourceAddressChanged(address);
  });
  SetNetworkTickTimer([]() -> uint32_t {
    auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(
                            std::chrono::steady_clock::now().time_since_epoch())
                            .count();
    return static_cast<uint32_t>(milliseconds);
  });
  Nmea2kStackSetSerial(m_serialnumber.c_str());
  Nmea2kStackSetHardwareVersion(m_hardwareVersions.c_str());
  SetAdditionalSoftwareVersions(m_additionalSoftwareVersion.c_str());

  uint16_t id = mtEuropa;
  uint16_t proprietaryCode = CommonSettings::CZ_BEP_PROPRIETARY_CODE;
  uint16_t productId = CZ_PRODUCT_CODE_EUROPA;

  BOOST_LOG_TRIVIAL(debug) << "CanService, dipswitch: " << dipswitch
                           << ", id: " << id
                           << ", proprietaryCode: " << proprietaryCode
                           << ", productId: " << productId;
  auto h = Nmea2kStackInit(dipswitch, id, proprietaryCode,
                           CommonSettings::LAST_SOURCE_ADDRESS, nmeaChannel,
                           productId, CommonSettings::CZ_FIRMWARE_VERSION);
  BOOST_LOG_TRIVIAL(debug) << "CanService, Nmea2kStackInit: " << h;

  CZoneSetCZoneEventCallback(
      [](const tCZoneEventType event, void *data, const uint32_t size) -> void {
        CanService::getInstance().eventCallback(event, data, size);
      });

  BOOST_LOG_TRIVIAL(debug) << "CanService, CZoneSetCZoneEventCallback";

  BOOST_LOG_TRIVIAL(debug) << "CanService, Initializing CZone...";

  CZoneInitialise(id, dipswitch, CommonSettings::CZ_PRODUCT_CODE,
                  CommonSettings::CZ_BACKLIGHT,
                  CommonSettings::CZ_FIRMWARE_VERSION);

  CZoneSetValue(eCZoneLastSourceAddress,
                static_cast<float>(CommonSettings::LAST_SOURCE_ADDRESS));

  BOOST_LOG_TRIVIAL(debug) << "CanService, CZoneInitialise completed.";

  m_init.store(InitStatus::INITIALIZED);
}

CanService::CanService() {
  m_running.store(RunStatus::NONE);
  m_init.store(InitStatus::NONE);
  m_n2kThreadRunning.store(false);
  m_serialnumber = "hubserialnumber";
  m_hardwareVersions = "0.0.1";
  m_additionalSoftwareVersion = "0.0.1";
}

CanService::~CanService() {
  m_running.store(RunStatus::NONE);
  m_init.store(InitStatus::NONE);
  m_n2kThreadRunning.store(false);
  m_txCanInfo.clear();
  m_rxCanInfo.clear();
}

void CanService::sourceAddressChanged(const uint8_t address) {
  getInstance().m_sourceAddress = address;
  CZoneSetValue(eCZoneLastSourceAddress, static_cast<float>(address));
}

void CanService::eventCallback(const tCZoneEventType eventType, void *data,
                               const uint32_t size) {

  std::stringstream ss;
  for (uint32_t i = 0; i < size; i++) {
    ss << std::hex << std::setw(2) << std::setfill('0')
       << static_cast<int>(static_cast<uint8_t *>(data)[i]);
  }
  BOOST_LOG_TRIVIAL(debug) << "Event type: " << std::to_string(eventType)
                           << ", data: " << ss.str();

  if (m_running.load() != RunStatus::STARTED ||
      m_init.load() != InitStatus::INITIALIZED) {
    BOOST_LOG_TRIVIAL(error) << "CanService not initialized or not running.";
    return;
  }

  switch (eventType) {
  case eCZoneTransmitPGN: {
    tCZoneTransmitPGNData *transmitData =
        static_cast<tCZoneTransmitPGNData *>(data);
    if (transmitPGN(transmitData->PGN, transmitData)) {
      transmitData->Result = CZONE_TRUE;
    }
    break;
  }
  case eCZoneNetworkStatus: {
    tCZoneNetworkStatusData *networkData =
        static_cast<tCZoneNetworkStatusData *>(data);
    networkData->Status = (NetworkReady() != 0) ? CZONE_TRUE : CZONE_FALSE;
    networkData->FaultStatus = NetworkFaultStatus();
  }
  case eCZoneRequestPGN: {
    tCZoneRequestPGNData *requestData =
        static_cast<tCZoneRequestPGNData *>(data);
    RequestPgn(requestData->SourceAddress, requestData->PGN);
  }
  default: {
    break;
  }
  }
}

bool CanService::transmitPGN(const pgn_t pgn, void *data) {
  auto found = m_txCanInfo.find(pgn);
  if (found != m_txCanInfo.end()) {
    found->second->Data = (void *)data;
    return TransmitCanPgn(found->second->Handle, found->second.get());
  }
  return false;
}

void CanService::start() {
  if (m_init.load() != InitStatus::INITIALIZED) {
    BOOST_LOG_TRIVIAL(error) << "CanService not initialized.";
    return;
  }
  if (m_running.load() != RunStatus::NONE) {
    BOOST_LOG_TRIVIAL(error) << "CanService is already running.";
    return;
  }

  BOOST_LOG_TRIVIAL(info) << "Starting CanService...";

  const std::lock_guard<std::mutex> lock(m_runmutex);
  m_running.store(RunStatus::STARTING);
  m_n2kThreadRunning.store(true);
  m_n2kThreadFuture =
      std::async(std::launch::async, &CanService::n2kthread, this);
  CZoneService(CZONE_TRUE, CZONE_TRUE, eCZoneConfigFileTypeStandard,
               CZONE_TRUE);

  m_running.store(RunStatus::STARTED);
}

bool CanService::n2kthread() {
  while (m_n2kThreadRunning.load()) {
    m_n2kLastTickTime = std::chrono::steady_clock::now();
    ProcessNetworkStack();
    if (NetworkSourceAddress() < 253) {
      CZoneProcess();
    }
    std::this_thread::sleep_for(std::chrono::nanoseconds(m_n2kThreadInterval));
  }
  return true;
}