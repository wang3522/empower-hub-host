cmake_minimum_required(VERSION 3.16.3)

if(NOT MSVC AND NOT IOS)
  add_compile_options("-fPIC")
endif()

message(STATUS "Starting czonelib.cmake")

include(FetchContent)

FetchContent_Declare(
  czonelib
  GIT_REPOSITORY git@bitbucket.org:bepmarine/git-czone-ui.git
  GIT_TAG        ${CZONELIB_TAG_REV_VERSION}
  SOURCE_SUBDIR  CZoneLib
)
# FetchContent_MakeAvailable(czonelib)

FetchContent_Populate(czonelib)
add_subdirectory(${czonelib_SOURCE_DIR}/CZoneLib/ ${czonelib_BINARY_DIR})

include_directories(${czonelib_BINARY_DIR}/Base)
include_directories(${czonelib_BINARY_DIR}/CZoneCoreLib)
include_directories(${czonelib_BINARY_DIR}/CZoneCoreLib/Monitoring)
include_directories(${czonelib_SOURCE_DIR}/Common)
include_directories(${czonelib_SOURCE_DIR}/Common/Base)
include_directories(${czonelib_SOURCE_DIR}/Common/Nmea2kLib)
include_directories(${czonelib_SOURCE_DIR}/Common/Integration)
include_directories(${czonelib_SOURCE_DIR}/Common/ZoneConfiguration)
include_directories(${czonelib_SOURCE_DIR}/Common/DcMetering)
include_directories(${czonelib_SOURCE_DIR}/Common/Utils)
include_directories(${czonelib_SOURCE_DIR}/Common/AnalogueControl)
include_directories(${czonelib_SOURCE_DIR}/CZoneLib/CZoneCoreLib)
include_directories(${czonelib_SOURCE_DIR}/CZoneLib/NetworkProtocol)

message(STATUS "--------------------")
message(STATUS ${czonelib_SOURCE_DIR})
message(STATUS ${czonelib_BINARY_DIR})
message(STATUS "--------------------")

set(CZONELIB_LIBRARY CZoneCore)
set(NMEA2K_LIBRARY Nmea2k)

message(STATUS "Done with czonelib.cmake")
