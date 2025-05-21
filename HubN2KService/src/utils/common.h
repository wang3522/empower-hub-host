#pragma once

#include <tCZoneInterface.h>

typedef __uint8_t uint8_t;
typedef __uint16_t uint16_t;
typedef __uint32_t uint32_t;

typedef __int8_t int8_t;
typedef __int16_t int16_t;
typedef __int32_t int32_t;


namespace CzoneSystemConstants {

constexpr uint8_t DEFAULT_DIPSWITCH = 128U;
constexpr char DEFAULT_CAN_CHANNEL[] = "can0";
constexpr uint32_t DEFAULT_NEMA_CHANNEL = 0;
constexpr bool DEFAULT_MERCURY_ENGINE_S = false;
constexpr uint8_t LAST_SOURCE_ADDRESS = 0;

constexpr uint16_t CZ_BEP_PROPRIETARY_CODE = 0x9927;
constexpr char CZ_FIRMWARE_VERSION_SERVER_STR[] = "1.0.0";
constexpr uint16_t CZ_PRODUCT_CODE = 0;
constexpr uint16_t CZ_BACKLIGHT = 100;

constexpr char CZ_SETTINGS_FILE[] = "czone-settings.json";

constexpr char DBUS_CZONE_OBJECTPATH[] = "/org/navico/HubN2K";
constexpr char DBUS_CZONE_SERVICENAME[] = "org.navico.HubN2K";

typedef struct CZoneUIDisplayData {
  tCZoneDisplayType Type;
  union {
    tCZoneDeviceItem Device;
    tCZoneDisplayDipswitches Dipswitch;
    tCZoneDisplayAlarm Alarm;
    tCZoneDisplayCircuit Circuit;
    tCZoneDisplayMonitoringDevice MonitoringDevice;
    tCZoneDisplayMeteringDevice MeteringDevice;
    tCZoneDisplayInverterChargerDevice InverterChargerDevice;
    tCZoneDisplayACMainsDevice ACMainsDevice;
    tCZoneMenuItem MenuItem;
    tCZoneCategoryItem CategoryItem;
    tCZoneFavouritesInfo FavouritesInfo;
    tCZoneMonitoringSelection MonitoringSelection;
    tCZoneScreenConfigPageImageItem ScreenConfigPageImageItems;
    tCZoneScreenConfigPageImage ScreenConfigPageImages;
    tCZoneScreenConfigPageGridItem ScreenConfigPageGridItems;
    tCZoneScreenConfigPage ScreenConfigPages;
    tCZoneScreenConfigMode ScreenConfigModes;
    tCZoneScreenConfig ScreenConfigs;
    tCZoneDisplayHvacDevice HvacDevice;
    tCZoneDisplayZipdeeAwningDevice AwningDevice;
    tCZoneDisplayFantasticFanDevice FantasticFanDevice;
    tCZoneDisplayThirdPartyGeneratorDevice ThirdPartyGeneratorDevice;
    tCZoneDisplayShoreFuseDevice ShoreFuseDevice;
    tCZoneDisplayTyrePressureDevice TyrePressure;
    tCZoneDisplayAudioStereoDevice AudioStereoDevice;
    tCZoneDisplayCircuitLoads CircuitLoads;
    tCZoneDisplayDynamicDevice DynamicDevice;
    tCZoneDisplayDCConfiguration DCConfigure;
    tCZoneDisplayADConfiguration ADConfigure;
    tCZoneDisplayOutputConfiguration OutputConfigure;
    tCZoneDisplayUIRelationship UiRelationship;
    tCZoneDisplayBinaryLogicState BinaryLogicState;
  };
} CZoneUIStruct;

enum EventType {
  EventTypeConfiguration = 0,
  EventTypeAlarmAdded,
  EventTypeAlarmChanged,
  EventTypeAlarmRemoved,
  EventTypeAlarmActivated,
  EventTypeAlarmDeactivated,
  EventTypeAlarmLogUpdate,
  EventTypeAlarmGlobalStatus
};

} // namespace CzoneSystemConstants
