cmake_minimum_required(VERSION 3.16.3)

# Project name
project(N2KCoreApp)

# Set C++ standard
set(APPLICATION_NAME ${CMAKE_PROJECT_NAME})
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS OFF)

# Option to build for CZone Europa
option(CZONE_EUROPA_BUILD "Build for CZone Europa" ON)

# Set default tag revision version if not defined
if(NOT DEFINED CZONELIB_TAG_REV_VERSION)
  set(CZONELIB_TAG_REV_VERSION "develop-europa-hub")
endif()

find_package(PkgConfig REQUIRED)

# Find Boost libraries
find_package(Boost REQUIRED COMPONENTS log log_setup thread filesystem system json)
if(Boost_FOUND)
    message(STATUS "Boost found: ${Boost_VERSION}")
    message(STATUS "Boost include dirs: ${Boost_INCLUDE_DIRS}")
    message(STATUS "Boost libraries: ${Boost_LIBRARIES}")
    include_directories(${Boost_INCLUDE_DIRS})
else()
    message(FATAL_ERROR "Boost not found")
endif()

# Include the CZoneLib dependency
include(./cmake/czonelib.cmake)
include(./cmake/versioning.cmake)


pkg_check_modules(SDBUSCPP REQUIRED sdbus-c++)
if(SDBUSCPP_FOUND)
    message(STATUS "sdbus-c++_FOUND")
    message(STATUS ${SDBUSCPP_INCLUDE_DIRS})
else()
    message(FATAL_ERROR "sdbus-c++ not found")
endif()


include_directories(src ${CMAKE_CURRENT_BINARY_DIR}/src)

# Source files
set(SOURCES
    src/core/coremanager.cpp
    src/modules/czone/configdata.cpp
    src/modules/czone/czonedatabase.cpp
    src/modules/czone/czoneinterface.cpp
    src/modules/czone/czonesettings.cpp
    src/modules/czone/czoneunitutils.cpp
    src/modules/czone/monitoringdata.cpp
    src/modules/dbus/dbusservice.cpp
    src/modules/n2k/canservice.cpp
    src/utils/asyncworker.cpp
    src/utils/fileutil.cpp
    src/utils/logger.cpp
    src/main.cpp
)

# Add the executable
add_executable(
  ${APPLICATION_NAME} 
  ${SOURCES} 
  ${${APP_NAME}_VERSION_SOURCE}
)

# Link libraries
target_link_libraries(${APPLICATION_NAME}
  PRIVATE
  ${SDBUSCPP_LIBRARIES}
  ${NMEA2K_LIBRARY}
  ${CZONELIB_LIBRARY}
  pthread
  Boost::log
  Boost::log_setup
  Boost::thread
  Boost::filesystem
  Boost::system
  Boost::json
)

# Set target properties
set_target_properties(${APPLICATION_NAME}
  PROPERTIES
  CXX_STANDARD 20
  CXX_STANDARD_REQUIRED ON
  CXX_EXTENSIONS OFF
  # VERSION ${${APP_NAME}_VERSION}
)

# Install the executable
install(TARGETS ${APPLICATION_NAME} DESTINATION bin)

# Print build info
message(STATUS "========= Build Configuration =========")
message(STATUS "APP: ${APPLICATION_NAME}")
message(STATUS "Version: ${${APP_NAME}_VERSION}")
message(STATUS "=======================================")
