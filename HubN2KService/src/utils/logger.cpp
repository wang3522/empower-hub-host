#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/sources/record_ostream.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/utility/setup/common_attributes.hpp>
#include <boost/log/utility/setup/console.hpp>
#include <boost/log/utility/setup/file.hpp>
#include <iomanip>
#include <string>

#include "utils/fileutil.h"
#include "utils/logger.h"

std::ostream &operator<<(std::ostream &os, const boost::posix_time::ptime &pt) {
  os << boost::posix_time::to_iso_extended_string(pt);
  return os;
}

void initLogger() {
  logging::add_common_attributes();

  logging::add_console_log(
      std::cout, keywords::format = expr::stream << "[" << expr::attr<boost::posix_time::ptime>("TimeStamp") << "] "
                                                 << "[" << std::setw(7) << std::left << logging::trivial::severity
                                                 << "] " << expr::message);

  auto filename = getLogPath() + "HubCZoneCore.log";

  logging::add_file_log(keywords::file_name = filename, keywords::rotation_size = 10 * 1024 * 1024,
                        keywords::auto_flush = true, keywords::open_mode = std::ios_base::app,
                        keywords::format = expr::stream
                                           << "[" << expr::attr<boost::posix_time::ptime>("TimeStamp") << "] "
                                           << "[" << std::setw(7) << std::left << logging::trivial::severity << "] "
                                           << expr::smessage);
  logging::core::get()->flush();
}

void setLogLevel(logging::trivial::severity_level level) {
  logging::core::get()->set_filter(logging::trivial::severity >= level);
}