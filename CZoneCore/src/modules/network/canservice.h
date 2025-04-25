#ifndef CAN_SERVICE_H
#define CAN_SERVICE_H

#include <tCZoneInterface.h>

#include <atomic>
#include <memory>
#include <mutex>
#include <unordered_map>
#include <future>
#include <chrono>

using pgn_t = uint32_t;

class CanService {
public:
  enum class InitStatus { NONE, INITIALIZING, INITIALIZED };
  enum class RunStatus { NONE, STARTING, STARTED };

  static CanService &getInstance();
  void initialize(const std::string &channel, const uint8_t dipswitch,
                  const uint32_t nmeaChannel, bool mercuryEngineState);
  void start();

private:
  static CanService *m_instance;

  std::atomic<RunStatus> m_running;
  std::atomic<InitStatus> m_init;
  std::atomic<bool> m_n2kThreadRunning;
  std::future<bool> m_n2kThreadFuture;
  std::chrono::steady_clock::time_point m_n2kLastTickTime;
  static constexpr int m_n2kThreadInterval = 20000000; // nanosecond
  std::mutex m_runmutex;
  std::mutex m_initmutex;
  std::unordered_map<pgn_t, std::shared_ptr<tTxCanInfo>> m_txCanInfo;
  std::unordered_map<pgn_t, std::shared_ptr<tRxCanInfo>> m_rxCanInfo;

  // Settings
  uint8_t m_sourceAddress;
  std::string m_serialnumber;
  std::string m_hardwareVersions;
  std::string m_additionalSoftwareVersion;

  CanService();
  ~CanService();

  CanService(const CanService &) = delete;
  CanService(CanService &&) = delete;
  CanService &operator=(const CanService &) = delete;
  CanService &operator=(CanService &&) = delete;

  void sourceAddressChanged(const uint8_t address);
  void eventCallback(const tCZoneEventType eventType, void *data,
                     const uint32_t size);
  bool transmitPGN(const pgn_t pgn, void *data);
  bool n2kthread();
};

#endif