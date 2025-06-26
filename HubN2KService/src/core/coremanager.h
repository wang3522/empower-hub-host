#pragma once

#include "modules/czone/czonesettings.h"
#include "modules/dbus/dbusservice.h"
#include "modules/n2k/canservice.h"

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
  CanService &m_canService;

  CoreManager();
  ~CoreManager();
  void run();
};