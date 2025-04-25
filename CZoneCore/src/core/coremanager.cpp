#include "core/coremanager.h"
#include "common/commonSettings.h"
#include "utils/logger.h"

#include <chrono>
#include <thread>

CoreManager::CoreManager()
    : m_running(false), m_dbusService(std::make_shared<DbusService>()) {}

CoreManager::~CoreManager() { stop(); }

CoreManager &CoreManager::getInstance() {
  static CoreManager _instance;
  return _instance;
}

int intHandler(int value) { return value * 2; }

void CoreManager::start() {
  if (m_running.load()) {
    BOOST_LOG_TRIVIAL(error) << "CoreManager is already running!";
    return;
  }

  // dbus init and register method
  m_dbusService->initialize();
  m_dbusService->registerService("processInt", "Manager", intHandler);
  m_dbusService->run();

  // can init
  BOOST_LOG_TRIVIAL(debug) << "CoreManager, Initializing CanService...";
  auto &canService = CanService::getInstance();
  canService.initialize(CommonSettings::DEFAULT_CAN_CHANNEL,
                        CommonSettings::DEFAULT_DIPSWITCH,
                        CommonSettings::DEFAULT_NEMA_CHANNEL,
                        CommonSettings::DEFAULT_MERCURY_ENGINE_S);
  BOOST_LOG_TRIVIAL(debug) << "Coremanager, CanService initialized.";

  BOOST_LOG_TRIVIAL(debug) << "CoreManager, Starting CanService...";
  canService.start();
  BOOST_LOG_TRIVIAL(debug) << "CoreManager, CanService started.";

  m_running.store(true);
  this->run();
}

void CoreManager::stop() {
  BOOST_LOG_TRIVIAL(debug) << "Stopping CoreManager...";

  if (m_dbusService) {
    m_dbusService->stop();
    m_dbusService.reset();
  }
  BOOST_LOG_TRIVIAL(debug) << "DbusService stopped.";

  if (!m_running.load()) {
    return;
  }
  m_running.store(false);
}

void CoreManager::run() {
  while (m_running.load()) {
    std::this_thread::sleep_for(std::chrono::seconds(1));
  }
  BOOST_LOG_TRIVIAL(debug) << "CoreManager has stopped.";
}