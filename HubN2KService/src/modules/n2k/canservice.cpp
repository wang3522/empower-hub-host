#include <chrono>
#include <future>
#include <iomanip>
#include <mutex>
#include <sstream>
#include <thread>
#include <vector>

#include "modules/czone/czoneinterface.h"
#include "modules/n2k/canservice.h"
#include "modules/n2k/pgn/PGN_126208_Msg.h"
#include "modules/n2k/pgn/PGN_59392_Msg.h"
#include "modules/n2k/pgn/PGN_59904_Msg.h"
#include "modules/n2k/pgn/pgninfo.h"
#include "utils/common.h"
#include "utils/logger.h"

#include <ZoneConfiguration/tCZoneModuleTypes.h>
#include <tCZoneFirmwareVersion.h>
#include <tCZoneInterface.h>

CzoneInterface *CanService::m_interface = nullptr;
CzoneSettings *CanService::m_settings = nullptr;
std::atomic<bool> CanService::m_shutdownSignal{false};

CanService::CanService() { m_initialised = false; }

CanService::~CanService() { reset(); }

void CanService::reset() {
  stopThread();

  for (auto &i : m_TxCanInfo) {
    delete i.second;
  }
  for (auto &i : m_RxCanInfo) {
    delete i.second;
  }
}

void CanService::initialise(CzoneSettings *settings, CzoneInterface *interface, const std::string &channel,
                            const uint8_t dipswitch, const uint32_t id, const uint16_t productId,
                            const uint8_t lastSourceAddress, const uint32_t nmeaChannel,
                            const bool mercuryEngineState) {
  if (m_initialised) {
    return;
  }

  m_settings = settings;
  m_interface = interface;
  m_running = false;
  m_shutdownSignal = false;
  m_isStarted = false;

  CZoneDisableWakeInInit(); // [x] ??

  SetNetworkSourceAddressChanged(CanService::sourceAddressChanged);
  SetNetworkTickTimer(CanService::tickCount);

  Nmea2kStackSetSerial(m_settings->getSerialNumber().c_str());
  Nmea2kStackSetHardwareVersion(m_settings->getHardwareVersions().c_str());
  SetAdditionalSoftwareVersions(m_settings->getAdditionalSoftwareVersions().c_str());

  auto handle = Nmea2kStackInit(dipswitch, id, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE, lastSourceAddress,
                                nmeaChannel, productId, CZ_FIRMWARE_VERSION_WIFI_BRIDGE_STR);

  std::vector<PGNInfo> txPgnList = {PGNInfo(59392, true, 0),
                                    PGNInfo(65280, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65281, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65284, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65285, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65288, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65290, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65291, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65292, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65293, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65294, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65295, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65296, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65297, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65299, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65300, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65301, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65302, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65305, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65307, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65308, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65310, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65311, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65316, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(65325, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(126208, false, 0),
                                    PGNInfo(126996, false, 0),
                                    PGNInfo(130816, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(130817, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(130818, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(130819, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(130820, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(130821, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(130822, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(130825, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
                                    PGNInfo(127488, true, 0),
                                    PGNInfo(127489, false, 0),
                                    PGNInfo(127503, false, 0),
                                    PGNInfo(127504, false, 0),
                                    PGNInfo(127505, true, 0),
                                    PGNInfo(127506, false, 0),
                                    PGNInfo(127507, false, 0),
                                    PGNInfo(127508, true, 0),
                                    PGNInfo(127509, false, 0),
                                    PGNInfo(128267, true, 0),
                                    PGNInfo(129025, true, 0),
                                    PGNInfo(129026, true, 0),
                                    PGNInfo(126992, true, 0),
                                    PGNInfo(130306, true, 0),
                                    PGNInfo(130312, true, 0),
                                    PGNInfo(130314, true, 0),
                                    PGNInfo(130316, true, 0)};

  for (auto &pgn : txPgnList) {
    tTxCanInfo *info = new tTxCanInfo;
    memset(info, 0, sizeof(tTxCanInfo));

    info->Handle = handle;
    info->Pgn = pgn.PGN;
    info->FastPacketFrameCount = 0;
    info->ProprietaryCode = pgn.ProprietaryCode;
    info->PacketType = pgn.SingleFrame ? eSingleFrame : eFastPacket;
    info->PackPGN = PGNTxPack;
    m_TxCanInfo[pgn.PGN] = info;
  }

  std::vector<PGNInfo> rxPgnList = {
      PGNInfo(59392, true, 0),
      PGNInfo(65268, true, 0),
      PGNInfo(65280, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65281, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65282, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65283, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65284, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65285, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE, false),
      PGNInfo(65285, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE, true),
      PGNInfo(65286, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65287, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65288, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65290, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65291, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65292, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65293, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65294, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65295, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65296, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65297, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65300, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65301, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65302, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65304, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65306, true, 0),
      PGNInfo(65308, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE, true), // Loopback Binary Logic States
      PGNInfo(65309, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65310, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65311, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65314, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65316, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(65325, true, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(126208, false, 0),
      PGNInfo(126992, false, 0),
      PGNInfo(126996, false, 0),
      PGNInfo(130816, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(130817, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(130818, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(130819, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(130820, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(130821, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(130822, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(130825, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE),
      PGNInfo(127488, true, 0),
      PGNInfo(127489, false, 0),
      PGNInfo(127498, false, 0),
      PGNInfo(127503, false, 0),
      PGNInfo(127504, false, 0),
      PGNInfo(127505, true, 0, false),
      PGNInfo(127505, true, 0, true),
      PGNInfo(127506, false, 0, false),
      PGNInfo(127506, false, 0, true),
      PGNInfo(127507, false, 0),
      PGNInfo(127508, true, 0, false),
      PGNInfo(127508, true, 0, true),
      PGNInfo(127509, false, 0),
      PGNInfo(128267, true, 0),
      PGNInfo(129025, true, 0),
      PGNInfo(129026, true, 0),
      PGNInfo(130306, true, 0),
      PGNInfo(130312, true, 0, false),
      PGNInfo(130312, true, 0, true),
      PGNInfo(130314, true, 0, false),
      PGNInfo(130314, true, 0, true),
      PGNInfo(130316, true, 0, false),
      PGNInfo(130316, true, 0, true),
      PGNInfo(127258, true, 0),
      PGNInfo(129029, false, 0),
      PGNInfo(129539, true, 0),
      PGNInfo(129540, false, 0),
      PGNInfo(127258, true, 0, PGNInfo::eGNSS),
      PGNInfo(129026, true, 0, PGNInfo::eGNSS),
      PGNInfo(129029, false, 0, PGNInfo::eGNSS),
      PGNInfo(129539, true, 0, PGNInfo::eGNSS),
      PGNInfo(129540, false, 0, PGNInfo::eGNSS),
      PGNInfo(130826, false, CzoneSystemConstants::CZ_BEP_PROPRIETARY_CODE, PGNInfo::eSmartCraft)};

  for (auto &rxPGN : rxPgnList) {
    tRxCanInfo *info = new tRxCanInfo;
    memset(info, 0, sizeof(tRxCanInfo));

    info->Handle = 0;
    info->Pgn = rxPGN.PGN;
    info->ProprietaryCode = rxPGN.ProprietaryCode;
    info->PacketType = rxPGN.SingleFrame ? eSingleFrame : eFastPacket;
    info->ProcessPGNCallback = PGNRxCallBack;
    info->TxLoopback = rxPGN.LoopBack ? CZONE_TRUE : CZONE_FALSE;

    if (rxPGN.Source == PGNInfo::eNmea2k) {
      RegisterRxCanPGN(info->Handle, info);
    }
    m_RxCanInfo[info->Pgn] = info;
  }

  CZoneSetCZoneEventCallback(event);
  CZoneInitialise(mtEuropa, dipswitch, 0, 100, CzoneSystemConstants::CZ_FIRMWARE_VERSION_SERVER_STR);

  CZoneSetValue(eCZoneLastSourceAddress, static_cast<float>(lastSourceAddress));

  m_initialised = true;
}

void CanService::service(const bool start) {
  if (start && !m_isStarted) {
    startThread();
    CZoneService(CZONE_TRUE, CZONE_TRUE, eCZoneConfigFileTypeStandard, CZONE_TRUE);
    m_isStarted = true;
  } else if (!start && m_isStarted) {
    stopThread();
    CZoneService(CZONE_FALSE, CZONE_TRUE, eCZoneConfigFileTypeStandard, CZONE_TRUE);
    m_isStarted = false;
  } else {
    BOOST_LOG_TRIVIAL(warning) << "CanService::service is called in a wrong state, m_isStarted: " << m_isStarted
                               << ", service start: " << start;
  }
}

void CanService::startThread() {
  auto n2k = [&]() {
    struct timespec ts, rem;
    m_lastThreadTimestamp = std::chrono::steady_clock::now();

    while (m_running) {
      ts.tv_sec = 0;
      ts.tv_nsec = 20000000;

      if (nanosleep(&ts, &rem) == 0) {
        const std::lock_guard<std::mutex> lock(m_mutex);
        m_lastThreadTimestamp = std::chrono::steady_clock::now();
        ProcessNetworkStack();

        if (NetworkSourceAddress() < 253) {
          CZoneProcess();
          // m_Interface->HandleLEDs();
        }
      }
    }

    return true;
  };

  m_running = true;
  m_future = std::async(std::launch::async, n2k);
}

void CanService::stopThread() {
  if (m_initialised && m_running) {
    m_running = false;
    m_future.wait();
  }
}

bool CanService::checkSystemHealth(const int64_t timeout) {
  if (m_running) {
    if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - m_lastThreadTimestamp)
            .count() < timeout) {
      return true;
    } else {
      return false;
    }
  } else {
    return false;
  }
}

void CanService::sourceAddressChanged(const uint8_t address) {
  CanService::getInstance().Settings()->setSourceAddress(address);
  CZoneSetValue(eCZoneLastSourceAddress, static_cast<float>(address));
}

uint32_t CanService::tickCount() {
  auto milliseconds =
      std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now().time_since_epoch())
          .count();
  return static_cast<uint32_t>(milliseconds);
}

void CanService::event(const tCZoneEventType czoneEvent, void *data, const uint32_t sizeOfData) {
  if (m_shutdownSignal == true) {
    return;
  }

  switch (czoneEvent) {
  case eCZoneTransmitPGN: {
    tCZoneTransmitPGNData *transmitData = static_cast<tCZoneTransmitPGNData *>(data);
    if (CanService::getInstance().TransmitPGN(transmitData->PGN, transmitData->Data)) {
      transmitData->Result = CZONE_TRUE;
    } else {
      BOOST_LOG_TRIVIAL(warning) << "CanService::event::eCZoneTransmitPGN: failed to transmit pgn["
                                 << std::to_string(transmitData->PGN) << "]";
    }
  } break;

  case eCZoneNetworkStatus: {
    tCZoneNetworkStatusData *networkData = static_cast<tCZoneNetworkStatusData *>(data);
    networkData->Status = (NetworkReady() != 0) ? CZONE_TRUE : CZONE_FALSE;
    networkData->FaultStatus = NetworkFaultStatus();
  } break;

  case eCZoneRequestPGN: {
    tCZoneRequestPGNData *requestData = static_cast<tCZoneRequestPGNData *>(data);
    RequestPgn(requestData->SourceAddress, requestData->PGN);
  } break;

  default: {
    CanService::getInstance().Interface()->event(czoneEvent, data, sizeOfData);
  } break;
  }
}

bool CanService::TransmitPGN(const uint32_t pgn, void *data) {
  // Attempt to find the PGN in the transmit info map
  auto info = m_TxCanInfo.find(pgn);
  if (info != m_TxCanInfo.end()) {
    info->second->Data = data; // data is already void*, no cast needed
    return TransmitCanPgn(info->second->Handle, info->second) == CZONE_TRUE;
  } else {
    BOOST_LOG_TRIVIAL(warning) << "CanService::TransmitPGN: unknown pgn[" << std::to_string(pgn) << "]";
  }
  return false;
}

void CanService::PGNRxCallBack(const tCZoneNetworkMsg *msg) {
  if (msg != nullptr) {
    switch (msg->Pgn.whole) {
    case 59904: {
      tNmea2kPGN59904Data data;
      NetworkUnpackPGN(msg, &data);

      // check addressed to us
      if (msg->DestAddress == NetworkSourceAddress()) {
        switch (data.PGN) {
        case 126996: {
        } break;

        case 60928: {
          // handled by stack
        } break;

        // BEP PGNS
        case 65280:
        case 65281:
        case 65284:
        case 65285:
        case 65288:
        case 65290:
        case 65291:
        case 65293:
        case 65294:
        case 65295:
        case 65296:
        case 65297:
        case 65299:
        case 65300:
        case 65301:
        case 65302:
        case 130816:
        case 130817:
        case 130818:
        case 130819:
        case 130820:
        case 130821:
        case 130822: {
          tNmea2kPGN59392Data pgn59392Data;
          pgn59392Data.DestinationAddress = msg->SrcAddress;
          pgn59392Data.PGN = data.PGN;
          pgn59392Data.Acknowledgement = ISO_ACKNOWLEDGE_ACCESS_DENIED;
          CanService::getInstance().TransmitPGN(59392, &pgn59392Data);
        } break;

        default: {
          tNmea2kPGN59392Data pgn59392Data;
          pgn59392Data.DestinationAddress = msg->SrcAddress;
          pgn59392Data.PGN = data.PGN;
          pgn59392Data.Acknowledgement = ISO_ACKNOWLEDGE_NOTSUPPORTED;
          CanService::getInstance().TransmitPGN(59392, &pgn59392Data);
        } break;
        }
      }
    } break;

    default: {
      CZoneProcessPGN(msg);
      break;
    }
    }
  }
}

void CanService::PGNTxPack(tCZoneNetworkMsg *msg, const void *data) {
  switch (msg->Pgn.whole) {
  case 59392:
  case 126208: {
    NetworkPackPGN(msg->Pgn.whole, msg, data);
  } break;

  default: {
    CZonePackPGN(msg->Pgn.whole, msg, data);
  } break;
  }
}

void CanService::setShutdownSignal(bool flag) { m_shutdownSignal = flag; }

bool CanService::HealthStatus(const int64_t timeout) {
  if (m_running) {
    if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - m_lastThreadTimestamp)
            .count() < timeout) {
      return true;
    } else {
      return false;
    }
  } else {
    // Device is in low-power mode, health assumed ok...
    return true;
  }
}