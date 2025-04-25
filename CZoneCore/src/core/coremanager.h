#ifndef CORE_MANAGER_H
#define CORE_MANAGER_H

#include "modules/dbus/dbusservice.h"
#include "modules/network/canservice.h"

#include <atomic>
#include <memory>

class CoreManager {
public:
  CoreManager(const CoreManager &) = delete;
  CoreManager(CoreManager &&) = delete;
  CoreManager &operator=(const CoreManager &) = delete;
  CoreManager &operator=(CoreManager &&) = delete;
  static CoreManager &getInstance();
  void start();
  void stop();

private:
  std::atomic<bool> m_running;
  std::shared_ptr<DbusService> m_dbusService;

  CoreManager();
  ~CoreManager();
  void run();
};

#endif // CORE_MANAGER_H