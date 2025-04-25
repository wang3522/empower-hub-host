#pragma once

#include <string>
#include <vector>

//--------------------------------------------------------------------------
// Common settings structures used by EuropaConfigUtils and EuropaRestServer
//--------------------------------------------------------------------------
namespace CommonSettings {
constexpr uint8_t DEFAULT_DIPSWITCH = 128U;
constexpr char DEFAULT_CAN_CHANNEL[] = "can0";
constexpr uint32_t DEFAULT_NEMA_CHANNEL = 0;
constexpr bool DEFAULT_MERCURY_ENGINE_S = false;
constexpr uint8_t LAST_SOURCE_ADDRESS = 0;

constexpr uint16_t CZ_BEP_PROPRIETARY_CODE = 0x9927;
constexpr char CZ_FIRMWARE_VERSION[] = "1.0.0";
constexpr uint16_t CZ_PRODUCT_CODE = 0;
constexpr uint16_t CZ_BACKLIGHT = 100;
} // namespace CommonSettings
