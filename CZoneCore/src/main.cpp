#include "core/coremanager.h"
#include "utils/logger.h"

int main() {
  try {
    initLogger();
    setLogLevel(logging::trivial::debug);
    BOOST_LOG_TRIVIAL(info) << "Starting CZone C++ Core...";

    CoreManager &coreManager = CoreManager::getInstance();
    coreManager.start();
  } catch (const std::exception &e) {
    BOOST_LOG_TRIVIAL(error) << std::string("Exception: ") + e.what();
    return 1;
  }

  return 0;
}