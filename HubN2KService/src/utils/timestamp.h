#pragma once

#include <chrono>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>

inline std::string getCurrentTimeString() {
  auto now = std::chrono::system_clock::now();                   // Get current time
  std::time_t now_c = std::chrono::system_clock::to_time_t(now); // Convert to time_t
  std::tm tm;
  localtime_r(&now_c, &tm); // Convert to tm struct

  std::ostringstream oss;
  oss << std::put_time(&tm, "%Y-%m-%d %H:%M:%S"); // Format as string
  return oss.str();
}