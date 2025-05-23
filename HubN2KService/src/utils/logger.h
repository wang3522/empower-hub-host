#pragma once

#include <boost/log/trivial.hpp>

namespace logging = boost::log;
namespace keywords = boost::log::keywords;
namespace expr = boost::log::expressions;

void initLogger();
void setLogLevel(logging::trivial::severity_level level);
