#ifndef LOGGER_H
#define LOGGER_H

#include <boost/log/trivial.hpp>

namespace logging = boost::log;
namespace keywords = boost::log::keywords;
namespace expr = boost::log::expressions;

void initLogger();
void setLogLevel(logging::trivial::severity_level level);

#endif // LOGGER_H