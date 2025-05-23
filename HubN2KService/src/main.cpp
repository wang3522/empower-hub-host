#include "core/coremanager.h"
#include "utils/logger.h"
#include <cstdlib>

int main() {
  try {
    const char *LOG_LEVEL = std::getenv("HUB_LOG_LEVEL");

    initLogger();
    if (strcmp(LOG_LEVEL, "DEBUG") == 0) {
      setLogLevel(logging::trivial::debug);
    } else if (strcmp(LOG_LEVEL, "ERROR") == 0) {
      setLogLevel(logging::trivial::error);
    } else if (strcmp(LOG_LEVEL, "WARNING") == 0) {
      setLogLevel(logging::trivial::warning);
    } else {
      setLogLevel(logging::trivial::info);
    }

    BOOST_LOG_TRIVIAL(info) << "Starting CZone C++ Core...";

    CoreManager &coreManager = CoreManager::getInstance();
    coreManager.start();
  } catch (const std::exception &e) {
    BOOST_LOG_TRIVIAL(error) << std::string("Exception: ") + e.what();
    return 1;
  }

  return 0;
}