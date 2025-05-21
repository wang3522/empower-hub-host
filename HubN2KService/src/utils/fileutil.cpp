#include "utils/fileutil.h"

#include <filesystem>

namespace fs = std::filesystem;

std::string getCzoneConfigPath() {
  std::string pathStr = "/etc/hub/czonedata/";
  const char *HUB_CONFIGDIR = std::getenv("HUB_CZONE_CONFIGDIR");
  if (HUB_CONFIGDIR != nullptr) {
    pathStr = std::string(HUB_CONFIGDIR);
  }

  auto path = fs::path(pathStr);
  if (!fs::exists(path)) {
    try {
      fs::create_directories(path);
    } catch (const std::exception &e) {
      pathStr = "/tmp";
    }
  }

  if (pathStr.back() != '/') {
    pathStr += "/";
  }

  return pathStr;
}

std::string getLogPath() {
  std::string pathStr = "/var/log/hub";
  const char *LOG_PATH = std::getenv("HUB_LOGDIR");

  if (LOG_PATH != nullptr) {
    pathStr = std::string(LOG_PATH);
  }

  auto path = fs::path(pathStr);
  if (!fs::exists(path)) {
    try {
      fs::create_directories(path);
    } catch (const std::exception &e) {
      pathStr = "/tmp";
    }
  }

  if (pathStr.back() != '/') {
    pathStr += "/";
  }

  return pathStr;
}
