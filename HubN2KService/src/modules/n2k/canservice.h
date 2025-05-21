#pragma once

#include <atomic>
#include <chrono>
#include <future>
#include <map>
#include <mutex>

#include <CZonePlatform.h>
#include <tNetworkInterface.h>
#include <tNetworkTypes.h>

#include "modules/czone/czoneinterface.h"
#include "modules/czone/czonesettings.h"

class CanService {
public:
  ~CanService();
  CanService(const CanService &) = delete;
  CanService(CanService &&) = delete;
  CanService &operator=(const CanService &) = delete;
  CanService &operator=(CanService &&) = delete;

  void initialise(CzoneSettings *settings, CzoneInterface *interface, const std::string &channel,
                  const uint8_t dipswitch, const uint32_t id, const uint16_t productId, const uint8_t lastSourceAddress,
                  const uint32_t nmeaChannel, const bool mercuryEngineState);
  void service(const bool start);
  void reset();
  bool checkSystemHealth(const int64_t timeout = 60000);

  bool TransmitPGN(uint32_t pgn, void *data);
  static void setShutdownSignal(bool flag);

  static CanService &getInstance() {
    static CanService _canServiceInstance;
    return _canServiceInstance;
  }

  std::mutex &getCanServiceMutex() { return m_mutex; }

  CzoneInterface *Interface() { return m_interface; }
  CzoneSettings *Settings() { return m_settings; }

private:
  CanService();

  static void event(const tCZoneEventType czoneEvent, void *data, const uint32_t sizeOfData);
  static void sourceAddressChanged(const uint8_t address);
  static void PGNRxCallBack(const tCZoneNetworkMsg *msg);
  static void PGNTxPack(tCZoneNetworkMsg *msg, const void *data);
  static uint32_t tickCount();
  void startThread();
  void stopThread();

  static CzoneInterface *m_interface;
  static CzoneSettings *m_settings;

  std::mutex m_mutex;
  std::future<bool> m_future;

  std::atomic<bool> m_initialised;
  std::atomic<bool> m_running;
  static std::atomic<bool> m_shutdownSignal;
  std::atomic<bool> m_isStarted = false;
  std::chrono::steady_clock::time_point m_lastThreadTimestamp;

  std::map<uint32_t, tTxCanInfo *> m_TxCanInfo;
  std::map<uint32_t, tRxCanInfo *> m_RxCanInfo;
};
