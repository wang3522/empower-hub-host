#pragma once

#include <boost/json.hpp>
#include "utils/logger.h"

template <typename T>
T getJsonVal(const boost::json::object &obj, const std::string &key,
          T default_val) {
  auto it = obj.find(key);
  if (it != obj.end()) {
    try {
      return boost::json::value_to<T>(it->value());
    } catch (const std::exception &e) {
      BOOST_LOG_TRIVIAL(warning) << "CzoneSettings: unknown key, " << e.what();
      return default_val;
    }
  } else {
    return default_val;
  }
};