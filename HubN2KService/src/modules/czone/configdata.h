#pragma once

#include "utils/common.h"
#include "utils/json.hpp"

#include <tCZoneInterface.h>

#include <list>
#include <map>
#include <string>
#include <unordered_map>
#include <vector>

using json = nlohmann::json;

class Instance {
private:
  bool m_enabled;
  uint32_t m_instance;

public:
  Instance();
  Instance(uint32_t i, bool e);
  Instance(const Instance &rhs);
  Instance(Instance &&rhs);
  Instance &operator=(const Instance &rhs);
  Instance &operator=(Instance &&rhs);

  void set_instance(uint32_t i) { m_instance = i; }
  void set_enabled(bool e) { m_enabled = e; }

  json tojson() const;
};

class CategoryRequest {
public:
  enum eCategoryType : int { eNone = -1, eCategoriesAll = 0 };
  static std::string to_string(eCategoryType type) {
    switch (type) {
    case eCategoryType::eCategoriesAll: return "CategoriesAll";
    default: return "Unknown";
    }
  }
  static eCategoryType from_string(std::string type) {
    if (type == "CategoriesAll") {
      return eCategoryType::eCategoriesAll;
    }
    return eCategoryType::eNone;
  }

  CategoryRequest();
  CategoryRequest(const CategoryRequest &) = delete;
  CategoryRequest(CategoryRequest &&) = delete;
  CategoryRequest &operator=(const CategoryRequest &) = delete;
  CategoryRequest &operator=(CategoryRequest &&) = delete;

private:
  eCategoryType m_type;
  std::string m_token;
};

class AlarmRequest {
public:
  std::unique_ptr<uint32_t> m_id = nullptr;
  std::unique_ptr<bool> m_accepted = nullptr;

  AlarmRequest() = delete;
  AlarmRequest(const json &j);
  AlarmRequest(const AlarmRequest &other);
  AlarmRequest(AlarmRequest &&other) = default;
  AlarmRequest &operator=(const AlarmRequest &other) = default;
  AlarmRequest &operator=(AlarmRequest &&other) = default;
  ~AlarmRequest() = default;
};

class ControlRequest {
public:
  enum eControlType : int {
    eActivate = 0,
    eRelease = 1,
    ePing = 2,
    eSetAbsolute = 3,
  };
  static std::string to_string(eControlType type) {
    switch (type) {
    case eActivate: return "Activate";
    case eRelease: return "Release";
    case ePing: return "Ping";
    case eSetAbsolute: return "SetAbsolute";
    default: return "Unknown";
    }
  }

  enum eThrowType : int {
    eDoubleThrow = 0,
    eSingleThrow = 1,
  };
  static std::string to_string(eThrowType type) {
    switch (type) {
    case eDoubleThrow: return "DoubleThrow";
    case eSingleThrow: return "SingleThrow";
    default: return "Unknown";
    }
  }

  enum eButtonInfoType : int {
    eButtonInfo0 = 0,
    eButtonInfo1 = 1,
  };
  static std::string to_string(eButtonInfoType type) {
    switch (type) {
    case eButtonInfo0: return "ButtonInfo0";
    case eButtonInfo1: return "ButtonInfo1";
    default: return "Unknown";
    }
  }

  static eControlType from_string_control(const std::string &str) {
    if (str == "Activate")
      return eActivate;
    if (str == "Release")
      return eRelease;
    if (str == "Ping")
      return ePing;
    if (str == "SetAbsolute")
      return eSetAbsolute;
    return eActivate;
  }

  static eButtonInfoType from_string_button(const std::string &str) {
    if (str == "ButtonInfo0")
      return eButtonInfo0;
    if (str == "ButtonInfo1")
      return eButtonInfo1;
    return eButtonInfo0;
  }

  static eThrowType from_string_throw(const std::string &str) {
    if (str == "DoubleThrow")
      return eDoubleThrow;
    if (str == "SingleThrow")
      return eSingleThrow;
    return eDoubleThrow;
  }

  std::unique_ptr<eControlType> m_type = nullptr;
  std::unique_ptr<eThrowType> m_throwType = nullptr;
  std::unique_ptr<eButtonInfoType> m_buttonType = nullptr;
  std::unique_ptr<uint32_t> m_id = nullptr;
  std::unique_ptr<uint32_t> m_value = nullptr;
  std::unique_ptr<std::string> m_token = nullptr;

  ControlRequest() = delete;
  ControlRequest(const json &j);
  ControlRequest(const ControlRequest &other);
  ControlRequest(ControlRequest &&other) = default;
  ControlRequest &operator=(const ControlRequest &other) = default;
  ControlRequest &operator=(ControlRequest &&other) = default;
  ~ControlRequest() = default;
};

class FileRequest {
public:
  enum eResourceType : int {
    eTouch7 = 0,
    eTouch10 = 1,
    ePhone = 2,
  };
  static std::string to_string(eResourceType type) {
    switch (type) {
    case eTouch7: return "Touch7";
    case eTouch10: return "Touch10";
    case ePhone: return "Phone";
    default: return "Unknown";
    }
  }
    static eResourceType from_string_ResourceType(const std::string &str) {
    if (str == "Touch7")
      return eTouch7;
    if (str == "Touch10")
      return eTouch10;
    if (str == "Phone")
      return ePhone;
    return eTouch7;
  }

  enum eFileType : int {
    eDefaultZcf = 0,
    eFavouritesCfp = 1,
    eMinMaxLog = 2,
    eCircuitsLog = 3,
    eAlarmDescription = 4,
    eAlarmLog = 5,
    eAlarmCustomizedDescription = 6,
    eResource = 7
  };
  static std::string to_string(eFileType type) {
    switch (type) {
    case eDefaultZcf: return "DefaultZcf";
    case eFavouritesCfp: return "FavouritesCfp";
    case eMinMaxLog: return "MinMaxLog";
    case eCircuitsLog: return "CircuitsLog";
    case eAlarmDescription: return "AlarmDescription";
    case eAlarmLog: return "AlarmLog";
    case eAlarmCustomizedDescription: return "AlarmCustomizedDescription";
    case eResource: return "Resource";
    default: return "Unknown";
    }
  }
  static eFileType from_string_fileType(const std::string &str) {
    if (str == "DefaultZcf")
      return eDefaultZcf;
    if (str == "FavouritesCfp")
      return eFavouritesCfp;
    if (str == "MinMaxLog")
      return eMinMaxLog;
    if (str == "CircuitsLog")
      return eCircuitsLog;
    if (str == "AlarmDescription")
      return eAlarmDescription;
    if (str == "AlarmLog")
      return eAlarmLog;
    if (str == "AlarmCustomizedDescription")
      return eAlarmCustomizedDescription;
    if (str == "Resource")
      return eResource;
    return eDefaultZcf;
  }

  std::unique_ptr<eFileType> m_type = nullptr;
  std::unique_ptr<eResourceType> m_resourceType = nullptr;
  std::unique_ptr<std::string> m_content = nullptr;

  FileRequest() = delete;
  FileRequest(const json &j);
  FileRequest(const FileRequest &other);
  FileRequest(FileRequest &&other) = default;
  FileRequest &operator=(const FileRequest &other) = default;
  FileRequest &operator=(FileRequest &&other) = default;
  ~FileRequest() = default;
};

class ControlTypeValueRequest {
public:
  enum eHVACType : int {
    eOperationMode = 0,
    eFanSpeed = 1,
    eSetTemperature = 2,
  };
  static std::string to_string(eHVACType type) {
    switch (type) {
    case eOperationMode: return "OperationMode";
    case eFanSpeed: return "FanSpeed";
    case eSetTemperature: return "SetTemperature";
    default: return "Unknown";
    }
  }

  enum eFantasticFanType : int {
    eDirectionForward = 0,
    eDirectionReverse = 1,
    eLidOpen = 2,
    eLidClose = 3,
    eSpeed = 4,
  };
  static std::string to_string(eFantasticFanType type) {
    switch (type) {
    case eDirectionForward: return "DirectionForward";
    case eDirectionReverse: return "DirectionReverse";
    case eLidOpen: return "LidOpen";
    case eLidClose: return "LidClose";
    case eSpeed: return "Speed";
    default: return "Unknown";
    }
  }

  enum eAudioStereoType : int {
    ePower = 0,
    eMute = 1,
    eVolumeUp = 2,
    eVolumeDown = 3,
    eTrackUp = 4,
    eTrackDown = 5,
    ePlay = 6,
    eSource = 7,
  };
  static std::string to_string(eAudioStereoType type) {
    switch (type) {
    case ePower: return "Power";
    case eMute: return "Mute";
    case eVolumeUp: return "VolumeUp";
    case eVolumeDown: return "VolumeDown";
    case eTrackUp: return "TrackUp";
    case eTrackDown: return "TrackDown";
    case ePlay: return "Play";
    case eSource: return "Source";
    default: return "Unknown";
    }
  }

  enum eAwningType : int {
    eOpen = 0,
    eClose = 1,
    eTitleLeft = 2,
    eTitleRight = 3,
  };
  static std::string to_string(eAwningType type) {
    switch (type) {
    case eOpen: return "Open";
    case eClose: return "Close";
    case eTitleLeft: return "TitleLeft";
    case eTitleRight: return "TitleRight";
    default: return "Unknown";
    }
  }

  enum eShoreFuseType : int { eControl = 0 };
  static std::string to_string(eShoreFuseType type) {
    switch (type) {
    case eControl: return "Control";
    default: return "Unknown";
    }
  }

  enum eThirdPartyGeneratorType : int { eStart = 0, eStop = 1 };
  static std::string to_string(eThirdPartyGeneratorType type) {
    switch (type) {
    case eStart: return "Start";
    case eStop: return "Stop";
    default: return "Unknown";
    }
  }

  ControlTypeValueRequest();
  ControlTypeValueRequest(const ControlTypeValueRequest &) = delete;
  ControlTypeValueRequest(ControlTypeValueRequest &&) = delete;
  ControlTypeValueRequest &operator=(const ControlTypeValueRequest &) = delete;
  ControlTypeValueRequest &operator=(ControlTypeValueRequest &&) = delete;

private:
  uint32_t m_instance;
  uint32_t m_type;
  uint32_t m_value;
  std::string m_token;
};

class ConfigRequest {
public:
  enum eConfigType : int {
    eNone = -1,
    eAlarms = 0,
    eControl = 1,
    eAC = 2,
    eDC = 3,
    eTank = 4,
    eTemperature = 5,
    ePressure = 6,
    eACMain = 7,
    eInverterCharger = 8,
    eDevice = 12,
    eMode = 17,
    eCircuit = 18,
    eScreenConfigPageImageItem = 21,
    eScreenConfigPageImage = 22,
    eScreenConfigPageGridItem = 23,
    eScreenConfigPage = 24,
    eScreenConfigMode = 25,
    eScreenConfig = 26,
    eHVAC = 27,
    eThirdPartyGenerator = 28,
    eZipdeeAwning = 29,
    eFantasticFan = 30,
    eShoreFuse = 32,
    eTyrePressure = 33,
    eAudioStereo = 37,
    eCircuitLoads = 38,
    eCategories = 39,
    eEngines = 41,
    eGNSS = 42,
    eFavouritesMode = 64,
    eFavouritesControl = 65,
    eFavouritesMonitoring = 66,
    eFavouritesAlarm = 67,
    eFavouritesACMain = 68,
    eFavouritesInverterCharger = 69,
    eFavouritesBoatView = 70,
    eUiRelationships = 71,
    eBinaryLogicStates = 72,
    eCZoneRaw = 90,
    eRTCoreMap = 91,
    eSwitchPositiveNegtive = 92,
    eNonVisibleCircuit = 93
  };
  static std::string to_string(eConfigType type) {
    switch (type) {
    case eNone: return "None";
    case eAlarms: return "Alarms";
    case eControl: return "Control";
    case eAC: return "AC";
    case eDC: return "DC";
    case eTank: return "Tank";
    case eTemperature: return "Temperature";
    case ePressure: return "Pressure";
    case eACMain: return "ACMain";
    case eInverterCharger: return "InverterCharger";
    case eDevice: return "Device";
    case eMode: return "Mode";
    case eCircuit: return "Circuit";
    case eScreenConfigPageImageItem: return "ScreenConfigPageImageItem";
    case eScreenConfigPageImage: return "ScreenConfigPageImage";
    case eScreenConfigPageGridItem: return "ScreenConfigPageGridItem";
    case eScreenConfigPage: return "ScreenConfigPage";
    case eScreenConfigMode: return "ScreenConfigMode";
    case eScreenConfig: return "ScreenConfig";
    case eHVAC: return "HVAC";
    case eThirdPartyGenerator: return "ThirdPartyGenerator";
    case eZipdeeAwning: return "ZipdeeAwning";
    case eFantasticFan: return "FantasticFan";
    case eShoreFuse: return "ShoreFuse";
    case eTyrePressure: return "TyrePressure";
    case eAudioStereo: return "AudioStereo";
    case eCircuitLoads: return "CircuitLoads";
    case eCategories: return "Categories";
    case eEngines: return "Engines";
    case eGNSS: return "GNSS";
    case eFavouritesMode: return "FavouritesMode";
    case eFavouritesControl: return "FavouritesControl";
    case eFavouritesMonitoring: return "FavouritesMonitoring";
    case eFavouritesAlarm: return "FavouritesAlarm";
    case eFavouritesACMain: return "FavouritesACMain";
    case eFavouritesInverterCharger: return "FavouritesInverterCharger";
    case eFavouritesBoatView: return "FavouritesBoatView";
    case eUiRelationships: return "UiRelationships";
    case eBinaryLogicStates: return "BinaryLogicStates";
    case eCZoneRaw: return "CZoneRaw";
    case eRTCoreMap: return "RTCoreMap";
    case eSwitchPositiveNegtive: return "SwitchPositiveNegtive";
    case eNonVisibleCircuit: return "NonVisibleCircuit";
    default: return "Unknown";
    }
  }
  static eConfigType from_string(const std::string &type) {
    if (type == "Alarms")
      return eAlarms;
    if (type == "Control")
      return eControl;
    if (type == "AC")
      return eAC;
    if (type == "DC")
      return eDC;
    if (type == "Tank")
      return eTank;
    if (type == "Temperature")
      return eTemperature;
    if (type == "Pressure")
      return ePressure;
    if (type == "ACMain")
      return eACMain;
    if (type == "InverterCharger")
      return eInverterCharger;
    if (type == "Device")
      return eDevice;
    if (type == "Mode")
      return eMode;
    if (type == "Circuit")
      return eCircuit;
    if (type == "ScreenConfigPageImageItem")
      return eScreenConfigPageImageItem;
    if (type == "ScreenConfigPageImage")
      return eScreenConfigPageImage;
    if (type == "ScreenConfigPageGridItem")
      return eScreenConfigPageGridItem;
    if (type == "ScreenConfigPage")
      return eScreenConfigPage;
    if (type == "ScreenConfigMode")
      return eScreenConfigMode;
    if (type == "ScreenConfig")
      return eScreenConfig;
    if (type == "HVAC")
      return eHVAC;
    if (type == "ThirdPartyGenerator")
      return eThirdPartyGenerator;
    if (type == "ZipdeeAwning")
      return eZipdeeAwning;
    if (type == "FantasticFan")
      return eFantasticFan;
    if (type == "ShoreFuse")
      return eShoreFuse;
    if (type == "TyrePressure")
      return eTyrePressure;
    if (type == "AudioStereo")
      return eAudioStereo;
    if (type == "CircuitLoads")
      return eCircuitLoads;
    if (type == "Categories")
      return eCategories;
    if (type == "Engines")
      return eEngines;
    if (type == "GNSS")
      return eGNSS;
    if (type == "FavouritesMode")
      return eFavouritesMode;
    if (type == "FavouritesControl")
      return eFavouritesControl;
    if (type == "FavouritesMonitoring")
      return eFavouritesMonitoring;
    if (type == "FavouritesAlarm")
      return eFavouritesAlarm;
    if (type == "FavouritesACMain")
      return eFavouritesACMain;
    if (type == "FavouritesInverterCharger")
      return eFavouritesInverterCharger;
    if (type == "FavouritesBoatView")
      return eFavouritesBoatView;
    if (type == "UiRelationships")
      return eUiRelationships;
    if (type == "BinaryLogicStates")
      return eBinaryLogicStates;
    if (type == "CZoneRaw")
      return eCZoneRaw;
    if (type == "RTCoreMap")
      return eRTCoreMap;
    if (type == "SwitchPositiveNegtive")
      return eSwitchPositiveNegtive;
    if (type == "NonVisibleCircuit")
      return eNonVisibleCircuit;
    return eNone;
  }

  ConfigRequest(eConfigType type);
  ConfigRequest(const ConfigRequest &) = delete;
  ConfigRequest(ConfigRequest &&) = delete;
  ConfigRequest &operator=(const ConfigRequest &) = delete;
  ConfigRequest &operator=(ConfigRequest &&) = delete;

  eConfigType get_type() const { return m_type; }
  uint32_t get_parentId() const { return m_parentId; }
  uint32_t get_flags() const { return m_flags; }
  uint32_t get_subType() const { return m_subType; }

private:
  eConfigType m_type;
  std::string m_token;
  uint32_t m_parentId;
  uint32_t m_flags;
  uint32_t m_subType;
};

class SettingRequest {
public:
  enum eSettingType : int {
    eConfig = 0,
    eDipswitch = 1,
    eDepthOffset = 2,
    eMagneticVariation = 3,
    eTimeOffset = 4,
    eGlobal = 5,
    eDateTime = 6,
    eBacklightLevel = 7,
    eBatteryFull = 8,
    eAlarmGlobal = 9,
    eFactoryData = 10,
  };
  static std::string to_string(eSettingType type) {
    switch (type) {
    case eConfig: return "Config";
    case eDipswitch: return "Dipswitch";
    case eDepthOffset: return "DepthOffset";
    case eMagneticVariation: return "MagneticVariation";
    case eTimeOffset: return "TimeOffset";
    case eGlobal: return "Global";
    case eDateTime: return "DateTime";
    case eBacklightLevel: return "BacklightLevel";
    case eBatteryFull: return "BatteryFull";
    case eAlarmGlobal: return "AlarmGlobal";
    case eFactoryData: return "FactoryData";
    default: return "Unknown";
    }
  }
  static eSettingType from_string(const std::string &type) {
    if (type == "Config")
      return eConfig;
    if (type == "Dipswitch")
      return eDipswitch;
    if (type == "DepthOffset")
      return eDepthOffset;
    if (type == "MagneticVariation")
      return eMagneticVariation;
    if (type == "TimeOffset")
      return eTimeOffset;
    if (type == "Global")
      return eGlobal;
    if (type == "DateTime")
      return eDateTime;
    if (type == "BacklightLevel")
      return eBacklightLevel;
    if (type == "BatteryFull")
      return eBatteryFull;
    if (type == "AlarmGlobal")
      return eAlarmGlobal;
    if (type == "FactoryData")
      return eFactoryData;
    return eConfig;
  }

  eSettingType m_Type;
  std::unique_ptr<uint32_t> m_DipswitchValue;
  std::unique_ptr<float> m_TimeOffsetValue;
  std::unique_ptr<float> m_MagneticVariationValue;
  std::unique_ptr<float> m_DepthOffsetValue;
  std::unique_ptr<float> m_BacklightValue;
  std::unique_ptr<uint32_t> m_BatteryFullValue;
  std::unique_ptr<std::vector<std::byte>> m_Payload;

  SettingRequest(const json &j);
  SettingRequest() = delete;
  SettingRequest(const SettingRequest &other);
  SettingRequest(SettingRequest &&other) = default;
  SettingRequest &operator=(const SettingRequest &other);
  SettingRequest &operator=(SettingRequest &&other) = default;
  ~SettingRequest() = default;
};

class DataId {
public:
  DataId();
  DataId(uint32_t id, bool enable);
  DataId(const DataId &rhs);
  DataId(DataId &&rhs);
  DataId &operator=(const DataId &rhs);
  DataId &operator=(DataId &&rhs);

  bool is_enabled() const { return m_enabled; }
  uint32_t get_id() const { return m_id; }

  json tojson() const;

private:
  bool m_enabled;
  uint32_t m_id;
};

class CategoryItem {
private:
  std::string m_nameUTF8;
  bool m_enabled;
  uint32_t m_index;

public:
  CategoryItem();
  CategoryItem(const std::string &name, bool enabled, uint32_t index);
  CategoryItem(const std::string &name, bool enabled);
  CategoryItem(const CategoryItem &rhs);
  CategoryItem(CategoryItem &&rhs);
  CategoryItem &operator=(const CategoryItem &rhs);
  CategoryItem &operator=(CategoryItem &&rhs);

  const std::string &get_nameUTF8() const { return m_nameUTF8; }
  bool is_enabled() const { return m_enabled; }
  uint32_t get_index() const { return m_index; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  void set_enabled(bool enabled) { m_enabled = enabled; }
  void set_index(uint32_t index) { m_index = index; }

  json tojson() const;
};

class CircuitLoad {
public:
  enum eControlType : int {
    eSetOutput = 0,
    eLimitOneDirection = 1,
    eLimitBothDirections = 2,
    eSetAndLimit = 3,
  };
  static std::string to_string(eControlType type) {
    switch (type) {
    case eSetOutput: return "SetOutput";
    case eLimitOneDirection: return "LimitOneDirection";
    case eLimitBothDirections: return "LimitBothDirections";
    case eSetAndLimit: return "SetAndLimit";
    default: return "Unknown";
    }
  }

private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  uint32_t m_channelAddress;
  float m_fuseLevel;
  float m_runningCurrent;
  float m_systemOnCurrent;
  bool m_forceAcknowledgeOn;
  uint32_t m_level;
  CircuitLoad::eControlType m_controlType;
  bool m_isSwitchedModule;

public:
  CircuitLoad();
  CircuitLoad(const CircuitLoad &rhs);
  CircuitLoad(CircuitLoad &&rhs);
  CircuitLoad &operator=(const CircuitLoad &rhs);
  CircuitLoad &operator=(CircuitLoad &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  void set_id(uint32_t id) { m_id = id; }
  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  void set_channelAddress(uint32_t address) { m_channelAddress = address; }
  void set_fuseLevel(float level) { m_fuseLevel = level; }
  void set_runningCurrent(float current) { m_runningCurrent = current; }
  void set_systemOnCurrent(float current) { m_systemOnCurrent = current; }
  void set_forceAcknowledgeOn(bool force) { m_forceAcknowledgeOn = force; }
  void set_level(uint32_t level) { m_level = level; }
  void set_controlType(CircuitLoad::eControlType type) { m_controlType = type; }
  void set_isSwitchedModule(bool isSwitched) { m_isSwitchedModule = isSwitched; }

  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }
  uint32_t get_id() const { return m_id; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }
  uint32_t get_channelAddress() const { return m_channelAddress; }
  float get_fuseLevel() const { return m_fuseLevel; }
  float get_runningCurrent() const { return m_runningCurrent; }
  float get_systemOnCurrent() const { return m_systemOnCurrent; }
  bool get_forceAcknowledgeOn() const { return m_forceAcknowledgeOn; }
  uint32_t get_level() const { return m_level; }
  CircuitLoad::eControlType get_controlType() const { return m_controlType; }
  bool get_isSwitchedModule() const { return m_isSwitchedModule; }
};

class CircuitDevice {
public:
  enum eSwitchType : int {
    eNone = 0,
    eLatchOn = 1,
    eLatchOff = 2,
    eOnOff = 3,
    eToggle = 4,
    eMomentaryOn = 5,
    eMomentaryOff = 6,
    eStepUp = 7,
    eStepDown = 8,
    eForward = 9,
    eReverse = 10,
    eDimLinearUp = 11,
    eDimLinearDown = 12,
    eDimExponentialUp = 13,
    eDimExponentialDown = 14,
    eSingleDimLinear = 15,
    eSingleDimExponential = 16,
    eSequential1 = 17,
    eSequential2 = 18,
    eSequential3 = 19,
    eSequential4 = 20,
    eSequential5 = 21,
    eToggleReverse = 22,
    eLogicAnd = 23,
    eLogicOr = 24,
    eLogicXor = 25,
    eSetAbsolute = 26,
    eSequentialUp = 27,
    eSequentialDown = 28,
    eSequentialLong1 = 29,
    eSequentialLong2 = 30,
    eSequentialLong3 = 31,
    eSequentialLong4 = 32,
    eSequentialLong5 = 33,
  };
  static std::string to_string(eSwitchType type) {
    switch (type) {
    case eNone: return "None";
    case eLatchOn: return "LatchOn";
    case eLatchOff: return "LatchOff";
    case eOnOff: return "OnOff";
    case eToggle: return "Toggle";
    case eMomentaryOn: return "MomentaryOn";
    case eMomentaryOff: return "MomentaryOff";
    case eStepUp: return "StepUp";
    case eStepDown: return "StepDown";
    case eForward: return "Forward";
    case eReverse: return "Reverse";
    case eDimLinearUp: return "DimLinearUp";
    case eDimLinearDown: return "DimLinearDown";
    case eDimExponentialUp: return "DimExponentialUp";
    case eDimExponentialDown: return "DimExponentialDown";
    case eSingleDimLinear: return "SingleDimLinear";
    case eSingleDimExponential: return "SingleDimExponential";
    case eSequential1: return "Sequential1";
    case eSequential2: return "Sequential2";
    case eSequential3: return "Sequential3";
    case eSequential4: return "Sequential4";
    case eSequential5: return "Sequential5";
    case eToggleReverse: return "ToggleReverse";
    case eLogicAnd: return "LogicAnd";
    case eLogicOr: return "LogicOr";
    case eLogicXor: return "LogicXor";
    case eSetAbsolute: return "SetAbsolute";
    case eSequentialUp: return "SequentialUp";
    case eSequentialDown: return "SequentialDown";
    case eSequentialLong1: return "SequentialLong1";
    case eSequentialLong2: return "SequentialLong2";
    case eSequentialLong3: return "SequentialLong3";
    case eSequentialLong4: return "SequentialLong4";
    case eSequentialLong5: return "SequentialLong5";
    default: return "Unknown";
    }
  }

  enum eConfirmType : int {
    eConfirmNone = 0,
    eConfirmOn = 1,
    eConfirmOff = 2,
    eConfirmOnOff = 3,
  };
  static std::string to_string(eConfirmType type) {
    switch (type) {
    case eConfirmNone: return "ConfirmNone";
    case eConfirmOn: return "ConfirmOn";
    case eConfirmOff: return "ConfirmOff";
    case eConfirmOnOff: return "ConfirmOnOff";
    default: return "Unknown";
    }
  }

  enum eCircuitType : int {
    eCircuit = 0,
    eModeGroup1 = 1,
    eModeGroup2 = 2,
    eModeGroup3 = 3,
    eModeGroupExclusive = 4,
  };
  static std::string to_string(eCircuitType type) {
    switch (type) {
    case eCircuit: return "Circuit";
    case eModeGroup1: return "ModeGroup1";
    case eModeGroup2: return "ModeGroup2";
    case eModeGroup3: return "ModeGroup3";
    case eModeGroupExclusive: return "ModeGroupExclusive";
    default: return "Unknown";
    }
  }

  enum eModeIcon : int {
    eEntertainment = 0,
    eEntertainmentNight = 1,
    eCrusing = 2,
    eCrusingNight = 3,
    eAnchored = 4,
    eAnchoredNight = 5,
    eDockAttended = 6,
    eDockUnAttended = 7,
    eGeneric = 8,
    eFishing = 9,
    eFishingNight = 10,
    eMoodLighting = 11,
  };
  static std::string to_string(eModeIcon type) {
    switch (type) {
    case eEntertainment: return "Entertainment";
    case eEntertainmentNight: return "EntertainmentNight";
    case eCrusing: return "Crusing";
    case eCrusingNight: return "CrusingNight";
    case eAnchored: return "Anchored";
    case eAnchoredNight: return "AnchoredNight";
    case eDockAttended: return "DockAttended";
    case eDockUnAttended: return "DockUnAttended";
    case eGeneric: return "Generic";
    case eFishing: return "Fishing";
    case eFishingNight: return "FishingNight";
    case eMoodLighting: return "MoodLighting";
    default: return "Unknown";
    }
  }

private:
  ConfigRequest::eConfigType m_displayType;
  std::pair<uint32_t, bool> m_id;
  std::string m_nameUTF8;
  DataId m_singleThrowId;
  std::list<std::string> m_sequentialNamesUTF8;
  bool m_hasComplement;
  uint32_t m_displayCategories;
  CircuitDevice::eConfirmType m_confirmDialog;
  Instance m_voltageSource;
  CircuitDevice::eCircuitType m_circuitType;
  CircuitDevice::eSwitchType m_switchType;
  uint32_t m_minLevel;
  uint32_t m_maxLevel;
  bool m_nonVisibleCircuit;
  uint32_t m_dimstep;
  uint32_t m_step;
  bool m_dimmable;
  uint32_t m_loadSmoothStart;
  uint32_t m_sequentialStates;
  uint32_t m_controlId;
  std::list<CircuitLoad> m_circuitLoads;
  std::list<CategoryItem> m_categories;
  bool m_dcCircuit;
  bool m_acCircuit;
  CircuitDevice::eModeIcon m_modeIcon;
  uint32_t m_primaryCircuitId;
  uint32_t m_remoteVisibility;
  std::string m_switchString;
  bool m_systemsOnAnd;

public:
  CircuitDevice();
  CircuitDevice(const CircuitDevice &rhs);
  CircuitDevice(CircuitDevice &&rhs);
  CircuitDevice &operator=(const CircuitDevice &rhs);
  CircuitDevice &operator=(CircuitDevice &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  void set_id(std::pair<uint32_t, bool> id) { m_id = id; }
  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  void set_singleThrowId(DataId id) { m_singleThrowId = id; }
  void set_sequentialNamesUTF8(const std::list<std::string> &names) { m_sequentialNamesUTF8 = names; }
  void set_hasComplement(bool hasComplement) { m_hasComplement = hasComplement; }
  void set_displayCategories(uint32_t categories) { m_displayCategories = categories; }
  void set_confirmDialog(CircuitDevice::eConfirmType confirm) { m_confirmDialog = confirm; }
  void set_voltageSource(Instance source) { m_voltageSource = source; }
  void set_circuitType(CircuitDevice::eCircuitType type) { m_circuitType = type; }
  void set_switchType(CircuitDevice::eSwitchType type) { m_switchType = type; }
  void set_minLevel(uint32_t level) { m_minLevel = level; }
  void set_maxLevel(uint32_t level) { m_maxLevel = level; }
  void set_nonVisibleCircuit(bool nonVisible) { m_nonVisibleCircuit = nonVisible; }
  void set_dimstep(uint32_t step) { m_dimstep = step; }
  void set_step(uint32_t step) { m_step = step; }
  void set_dimmable(bool dimmable) { m_dimmable = dimmable; }
  void set_loadSmoothStart(uint32_t start) { m_loadSmoothStart = start; }
  void set_sequentialStates(uint32_t states) { m_sequentialStates = states; }
  void set_controlId(uint32_t id) { m_controlId = id; }
  void set_circuitLoads(const std::list<CircuitLoad> &loads) { m_circuitLoads = loads; }
  void set_categories(const std::list<CategoryItem> &categories) { m_categories = categories; }
  void set_dcCircuit(bool dc) { m_dcCircuit = dc; }
  void set_acCircuit(bool ac) { m_acCircuit = ac; }
  void set_modeIcon(CircuitDevice::eModeIcon icon) { m_modeIcon = icon; }
  void set_primaryCircuitId(uint32_t id) { m_primaryCircuitId = id; }
  void set_remoteVisibility(uint32_t visibility) { m_remoteVisibility = visibility; }
  void set_switchString(const std::string &str) { m_switchString = str; }
  void set_systemsOnAnd(bool systemsOn) { m_systemsOnAnd = systemsOn; }

  std::string &add_sequentialNamesUTF8();
  CircuitLoad &add_circuitLoad();
  CategoryItem &add_category();

  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }
  std::pair<uint32_t, bool> get_id() const { return m_id; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }
  const DataId &get_singleThrowId() const { return m_singleThrowId; }
  const std::list<std::string> &get_sequentialNamesUTF8() const { return m_sequentialNamesUTF8; };
  bool get_hasComplement() const { return m_hasComplement; }
  uint32_t get_displayCategories() const { return m_displayCategories; }
  CircuitDevice::eConfirmType get_confirmDialog() const { return m_confirmDialog; }
  const Instance &get_voltageSource() const { return m_voltageSource; }
  CircuitDevice::eCircuitType get_circuitType() const { return m_circuitType; }
  CircuitDevice::eSwitchType get_switchType() const { return m_switchType; }
  uint32_t get_minLevel() const { return m_minLevel; }
  uint32_t get_maxLevel() const { return m_maxLevel; }
  bool get_nonVisibleCircuit() const { return m_nonVisibleCircuit; }
  uint32_t get_dimstep() const { return m_dimstep; }
  uint32_t get_step() const { return m_step; }
  bool get_dimmable() const { return m_dimmable; }
  uint32_t get_loadSmoothStart() const { return m_loadSmoothStart; }
  uint32_t get_sequentialStates() const { return m_sequentialStates; }
  uint32_t get_controlId() const { return m_controlId; }
  const std::list<CircuitLoad> &get_circuitLoads() const { return m_circuitLoads; }
  const std::list<CategoryItem> &get_categories() const { return m_categories; }
  bool get_dcCircuit() const { return m_dcCircuit; }
  bool get_acCircuit() const { return m_acCircuit; }
  CircuitDevice::eModeIcon get_modeIcon() const { return m_modeIcon; }
  uint32_t get_primaryCircuitId() const { return m_primaryCircuitId; }
  uint32_t get_remoteVisibility() const { return m_remoteVisibility; }
  const std::string &get_switchString() const { return m_switchString; }
  bool get_systemsOnAnd() const { return m_systemsOnAnd; }
};

class Categories {
private:
  std::list<CategoryItem> m_items;

public:
  Categories();
  ~Categories() { m_items.clear(); }
  Categories(const Categories &rhs);
  Categories(Categories &&rhs);
  Categories &operator=(const Categories &rhs);
  Categories &operator=(Categories &&rhs);

  const std::list<CategoryItem> &get_items() { return m_items; }
  CategoryItem &mutable_categoryItem() {
    m_items.emplace_back();
    return m_items.back();
  }
  void add_categoryItem(CategoryItem &&iteam) { m_items.emplace_back(std::move(iteam)); }

  json tojson() const;
};

class Alarm {
public:
  enum eAlarmType : int {
    eExternal = 0,
    eDipswitchConflict = 1,
    eTypeDeviceConflict = 2,
    eTypeDeviceMissing = 3,
    eTypeConfigConflict = 4,
    eTypeSleepWarning = 5,
    eTypeNone = 6
  };
  static std::string to_string(eAlarmType type) {
    switch (type) {
    case eExternal: return "External";
    case eDipswitchConflict: return "DipswitchConflict";
    case eTypeDeviceConflict: return "TypeDeviceConflict";
    case eTypeDeviceMissing: return "TypeDeviceMissing";
    case eTypeConfigConflict: return "TypeConfigConflict";
    case eTypeSleepWarning: return "TypeSleepWarning";
    case eTypeNone: return "TypeNone";
    default: return "Unknown";
    }
  }

  enum eSeverityType : int {
    eSeverityCritical = 0,
    eSeverityImportant = 1,
    eSeverityStandard = 2,
    eSeverityWarning = 3,
    eSeveritySIO = 4,
    eSeverityNone = 5,
  };
  static std::string to_string(eSeverityType type) {
    switch (type) {
    case eSeverityCritical: return "SeverityCritical";
    case eSeverityImportant: return "SeverityImportant";
    case eSeverityStandard: return "SeverityStandard";
    case eSeverityWarning: return "SeverityWarning";
    case eSeveritySIO: return "SeveritySIO";
    case eSeverityNone: return "SeverityNone";
    default: return "Unknown";
    }
  }

  enum eStateType : int {
    eStateDisabled = 0,
    eStateEnabled = 1,
    eStateAcknowledged = 2,
  };
  static std::string to_string(eStateType type) {
    switch (type) {
    case eStateDisabled: return "StateDisabled";
    case eStateEnabled: return "StateEnabled";
    case eStateAcknowledged: return "StateAcknowledged";
    default: return "Unknown";
    }
  }

private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  eAlarmType m_alarmType;
  eSeverityType m_severity;
  eStateType m_currentState;
  uint32_t m_channelId;
  uint32_t m_externalAlarmId;
  uint32_t m_uniqueId;
  bool m_valid;
  uint32_t m_activatedTime;
  uint32_t m_acknowledgedTime;
  uint32_t m_clearedTime;
  std::string m_name;
  std::string m_channel;
  std::string m_device;
  std::string m_title;
  std::string m_description;
  std::vector<std::byte> m_cZoneRawAlarm;
  std::string m_faultAction;
  uint32_t m_faultType;
  uint32_t m_faultNumber;

public:
  Alarm();
  ~Alarm() { m_cZoneRawAlarm.clear(); }
  Alarm(const Alarm &rhs);
  Alarm(Alarm &&rhs);
  Alarm &operator=(const Alarm &rhs);
  Alarm &operator=(Alarm &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  void set_id(uint32_t id) { m_id = id; }
  void set_alarmType(eAlarmType type) { m_alarmType = type; }
  void set_severity(eSeverityType severity) { m_severity = severity; }
  void set_currentState(eStateType state) { m_currentState = state; }
  void set_channelId(uint32_t id) { m_channelId = id; }
  void set_externalAlarmId(uint32_t id) { m_externalAlarmId = id; }
  void set_uniqueId(uint32_t id) { m_uniqueId = id; }
  void set_valid(bool valid) { m_valid = valid; }
  void set_activatedTime(uint32_t time) { m_activatedTime = time; }
  void set_acknowledgedTime(uint32_t time) { m_acknowledgedTime = time; }
  void set_clearedTime(uint32_t time) { m_clearedTime = time; }
  void set_name(const std::string &name) { m_name = name; }
  void set_channel(const std::string &channel) { m_channel = channel; }
  void set_device(const std::string &device) { m_device = device; }
  void set_title(const std::string &title) { m_title = title; }
  void set_description(const std::string &description) { m_description = description; }
  void set_cZoneRawAlarm(const std::vector<std::byte> &alarm) { m_cZoneRawAlarm = alarm; }
  void set_cZoneRawAlarm(const void *value, size_t size);
  void set_faultAction(const std::string &action) { m_faultAction = action; }
  void set_faultType(uint32_t type) { m_faultType = type; }
  void set_faultNumber(uint32_t number) { m_faultNumber = number; }

  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }
  uint32_t get_id() const { return m_id; }
  eAlarmType get_alarmType() const { return m_alarmType; }
  eSeverityType get_severity() const { return m_severity; }
  eStateType get_currentState() const { return m_currentState; }
  uint32_t get_channelId() const { return m_channelId; }
  uint32_t get_externalAlarmId() const { return m_externalAlarmId; }
  uint32_t get_uniqueId() const { return m_uniqueId; }
  bool get_valid() const { return m_valid; }
  uint32_t get_activatedTime() const { return m_activatedTime; }
  uint32_t get_acknowledgedTime() const { return m_acknowledgedTime; }
  uint32_t get_clearedTime() const { return m_clearedTime; }
  const std::string &get_name() const { return m_name; }
  const std::string &get_channel() const { return m_channel; }
  const std::string &get_device() const { return m_device; }
  const std::string &get_title() const { return m_title; }
  const std::string &get_description() const { return m_description; }
  const std::vector<std::byte> &get_cZoneRawAlarm() const { return m_cZoneRawAlarm; }
  const std::string &get_faultAction() const { return m_faultAction; }
  uint32_t get_faultType() const { return m_faultType; }
  uint32_t get_faultNumber() const { return m_faultNumber; }
  json tojson() const;
};

class AlarmsList {
private:
  std::list<Alarm> m_alarms;

public:
  AlarmsList();
  AlarmsList(const AlarmsList &rhs);
  AlarmsList(AlarmsList &&rhs);
  AlarmsList &operator=(const AlarmsList &rhs);
  AlarmsList &operator=(AlarmsList &&rhs);

  Alarm &add_alarm();
  const std::list<Alarm> &get_alarms() const { return m_alarms; }
};

class AlarmGlobalStatus {
private:
  Alarm::eSeverityType m_highestEnabledSeverity;
  Alarm::eSeverityType m_highestAcknowledgedSeverity;

public:
  void set_highestEnabledSeverity(Alarm::eSeverityType severity) { m_highestEnabledSeverity = severity; }
  void set_highestAcknowledgedSeverity(Alarm::eSeverityType severity) { m_highestAcknowledgedSeverity = severity; }

  Alarm::eSeverityType get_highestEnabledSeverity() const { return m_highestEnabledSeverity; }
  Alarm::eSeverityType get_highestAcknowledgedSeverity() const { return m_highestAcknowledgedSeverity; }

  AlarmGlobalStatus();
  AlarmGlobalStatus(const AlarmGlobalStatus &rhs);
  AlarmGlobalStatus(AlarmGlobalStatus &&rhs);
  AlarmGlobalStatus &operator=(const AlarmGlobalStatus &rhs);
  AlarmGlobalStatus &operator=(AlarmGlobalStatus &&rhs);
};

class CZoneRawEvent {
private:
  int m_type;
  std::vector<std::byte> m_content;
  std::vector<std::byte> m_rawAlarm;
  std::vector<std::byte> m_deviceItem;

public:
  CZoneRawEvent();
  ~CZoneRawEvent() {
    m_content.clear();
    m_rawAlarm.clear();
    m_deviceItem.clear();
  }
  CZoneRawEvent(const CZoneRawEvent &rhs);
  CZoneRawEvent(CZoneRawEvent &&rhs);
  CZoneRawEvent &operator=(const CZoneRawEvent &rhs);
  CZoneRawEvent &operator=(CZoneRawEvent &&rhs);

  void set_type(int type) { m_type = type; }
  int get_type() const { return m_type; }

  void set_content(const std::vector<std::byte> &content) { m_content = content; }
  void set_content(const void *value, size_t size);
  const std::vector<std::byte> &get_content() const { return m_content; }

  void set_rawAlarm(const std::vector<std::byte> &rawAlarm) { m_rawAlarm = rawAlarm; }
  void set_rawAlarm(const void *value, size_t size);
  const std::vector<std::byte> &get_rawAlarm() const { return m_rawAlarm; }

  void set_deviceItem(const std::vector<std::byte> &deviceItem) { m_deviceItem = deviceItem; }
  void set_deviceItem(const void *value, size_t size);
  const std::vector<std::byte> &get_deviceItem() const { return m_deviceItem; }
};

class Event {
public:
  enum eEventType : int {
    eConfigChange = 0,
    eAlarmAdded = 1,
    eAlarmChanged = 2,
    eAlarmRemoved = 3,
    eAlarmActivated = 4,
    eAlarmDeactivated = 5,
    eAlarmLogUpdate = 6,
    eAlarmGlobalStatus = 7,
    eGNSSConfigChanged = 8,
    eEngineConfigChanged = 9,
    eCZoneRaw = 10,
    eSystemLowPowerMode = 11,
    eSystemHostActive = 12,
  };
  static std::string to_string(eEventType type) {
    switch (type) {
    case eConfigChange: return "ConfigChange";
    case eAlarmAdded: return "AlarmAdded";
    case eAlarmChanged: return "AlarmChanged";
    case eAlarmRemoved: return "AlarmRemoved";
    case eAlarmActivated: return "AlarmActivated";
    case eAlarmDeactivated: return "AlarmDeactivated";
    case eAlarmLogUpdate: return "AlarmLogUpdate";
    case eAlarmGlobalStatus: return "AlarmGlobalStatus";
    case eGNSSConfigChanged: return "GNSSConfigChanged";
    case eEngineConfigChanged: return "EngineConfigChanged";
    case eCZoneRaw: return "CZoneRaw";
    case eSystemLowPowerMode: return "SystemLowPowerMode";
    case eSystemHostActive: return "SystemHostActive";
    default: return "Unknown";
    }
  }

private:
  eEventType m_type;
  std::string m_content;
  Alarm m_alarmItem;
  AlarmGlobalStatus m_globalStatus;
  CZoneRawEvent m_czoneEvent;
  std::string m_timeStamp;

public:
  Event(eEventType type);
  Event(const Event &rhs);
  Event(Event &&rhs);
  Event &operator=(const Event &rhs);
  Event &operator=(Event &&rhs);
  json tojson() const;

  void set_type(eEventType type) { m_type = type; }
  eEventType get_type() const { return m_type; }

  void set_content(const std::string &content) { m_content = content; }
  const std::string &get_content() const { return m_content; }

  void set_alarmItem(const Alarm &alarm) { m_alarmItem = alarm; }
  const Alarm &get_alarmItem() const { return m_alarmItem; }
  Alarm &mutable_alarmItem() { return m_alarmItem; }

  void set_globalStatus(const AlarmGlobalStatus &status) { m_globalStatus = status; }
  const AlarmGlobalStatus &get_globalStatus() const { return m_globalStatus; }
  AlarmGlobalStatus &mutable_globalStatus() { return m_globalStatus; }

  void set_czoneEvent(const CZoneRawEvent &event) { m_czoneEvent = event; }
  const CZoneRawEvent &get_czoneEvent() const { return m_czoneEvent; }

  void set_timeStamp(const std::string &timeStamp) { m_timeStamp = timeStamp; }
  const std::string &get_timeStamp() const { return m_timeStamp; }
};

class EngineDevice {
public:
  enum eEngineType : int { eSmartCraft = 0, eNMEA2000 = 1 };
  static std::string to_string(eEngineType type) {
    switch (type) {
    case eSmartCraft: return "SmartCraft";
    case eNMEA2000: return "NMEA2000";
    default: return "Unknown";
    }
  }

private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  std::string m_softwareId;
  std::string m_calibrationId;
  std::string m_serialNumber;
  std::string m_ecuSerialNumber;
  eEngineType m_engineType;

public:
  EngineDevice();
  EngineDevice(const EngineDevice &rhs);
  EngineDevice(EngineDevice &&rhs);
  EngineDevice &operator=(const EngineDevice &rhs);
  EngineDevice &operator=(EngineDevice &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_softwareId(const std::string &id) { m_softwareId = id; }
  const std::string &get_softwareId() const { return m_softwareId; }

  void set_calibrationId(const std::string &id) { m_calibrationId = id; }
  const std::string &get_calibrationId() const { return m_calibrationId; }

  void set_serialNumber(const std::string &number) { m_serialNumber = number; }
  const std::string &get_serialNumber() const { return m_serialNumber; }

  void set_ecuSerialNumber(const std::string &number) { m_ecuSerialNumber = number; }
  const std::string &get_ecuSerialNumber() const { return m_ecuSerialNumber; }

  void set_engineType(eEngineType type) { m_engineType = type; }
  eEngineType get_engineType() const { return m_engineType; }
};

class AlarmLimit {
public:
  bool enabled;
  float on;
  float off;
  uint32_t id;

  json tojson() const;
};

class MeteringDevice {
public:
  enum eDCType : int {
    eBattery = 0,
    eAlternator = 1,
    eConverter = 2,
    eSolar = 3,
    eWind = 4,
    eOther = 5,
  };
  static std::string to_string(eDCType type) {
    switch (type) {
    case eBattery: return "Battery";
    case eAlternator: return "Alternator";
    case eConverter: return "Converter";
    case eSolar: return "Solar";
    case eWind: return "Wind";
    case eOther: return "Other";
    default: return "Unknown";
    }
  }

  enum eACLine : int {
    eLine1 = 0,
    eLine2 = 1,
    eLine3 = 2,
  };
  static std::string to_string(eACLine line) {
    switch (line) {
    case eLine1: return "Line1";
    case eLine2: return "Line2";
    case eLine3: return "Line3";
    default: return "Unknown";
    }
  }

  enum eACType : int {
    eUnknown = 0,
    eGenerator = 1,
    eShorePower = 2,
    eInverter = 3,
    eParallel = 4,
    eCharger = 5,
    eOutlet = 6,
  };
  static std::string to_string(eACType type) {
    switch (type) {
    case eUnknown: return "Unknown";
    case eGenerator: return "Generator";
    case eShorePower: return "ShorePower";
    case eInverter: return "Inverter";
    case eParallel: return "Parallel";
    case eCharger: return "Charger";
    case eOutlet: return "Outlet";
    default: return "Unknown";
    }
  }

private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  eACLine m_line;
  bool m_output;
  uint32_t m_nominalVoltage;
  uint32_t m_nominalFrequency;
  uint32_t m_address;
  uint32_t m_capacity;
  float m_warningLow;
  float m_warningHigh;
  AlarmLimit m_lowLimit;
  AlarmLimit m_veryLowLimit;
  AlarmLimit m_highLimit;
  AlarmLimit m_veryHighLimit;
  AlarmLimit m_frequency;
  AlarmLimit m_lowVoltage;
  AlarmLimit m_veryLowVoltage;
  AlarmLimit m_highVoltage;
  bool m_canResetCapacity;
  eDCType m_dcType;
  bool m_showVoltage;
  bool m_showCurrent;
  bool m_showStateOfCharge;
  bool m_showTemperature;
  bool m_showTimeOfRemaining;
  eACType m_acType;

public:
  MeteringDevice();
  MeteringDevice(const MeteringDevice &rhs);
  MeteringDevice(MeteringDevice &&rhs);
  MeteringDevice &operator=(const MeteringDevice &rhs);
  MeteringDevice &operator=(MeteringDevice &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_line(eACLine line) { m_line = line; }
  eACLine get_line() const { return m_line; }

  void set_output(bool output) { m_output = output; }
  bool get_output() const { return m_output; }

  void set_nominalVoltage(uint32_t voltage) { m_nominalVoltage = voltage; }
  uint32_t get_nominalVoltage() const { return m_nominalVoltage; }

  void set_nominalFrequency(uint32_t frequency) { m_nominalFrequency = frequency; }
  uint32_t get_nominalFrequency() const { return m_nominalFrequency; }

  void set_address(uint32_t address) { m_address = address; }
  uint32_t get_address() const { return m_address; }

  void set_capacity(uint32_t capacity) { m_capacity = capacity; }
  uint32_t get_capacity() const { return m_capacity; }

  void set_warningLow(float low) { m_warningLow = low; }
  float get_warningLow() const { return m_warningLow; }

  void set_warningHigh(float high) { m_warningHigh = high; }
  float get_warningHigh() const { return m_warningHigh; }

  void set_lowLimit(const AlarmLimit &limit) { m_lowLimit = limit; }
  const AlarmLimit &get_lowLimit() const { return m_lowLimit; }

  void set_veryLowLimit(const AlarmLimit &limit) { m_veryLowLimit = limit; }
  const AlarmLimit &get_veryLowLimit() const { return m_veryLowLimit; }

  void set_highLimit(const AlarmLimit &limit) { m_highLimit = limit; }
  const AlarmLimit &get_highLimit() const { return m_highLimit; }

  void set_veryHighLimit(const AlarmLimit &limit) { m_veryHighLimit = limit; }
  const AlarmLimit &get_veryHighLimit() const { return m_veryHighLimit; }

  void set_frequency(const AlarmLimit &limit) { m_frequency = limit; }
  const AlarmLimit &get_frequency() const { return m_frequency; }

  void set_lowVoltage(const AlarmLimit &limit) { m_lowVoltage = limit; }
  const AlarmLimit &get_lowVoltage() const { return m_lowVoltage; }

  void set_veryLowVoltage(const AlarmLimit &limit) { m_veryLowVoltage = limit; }
  const AlarmLimit &get_veryLowVoltage() const { return m_veryLowVoltage; }

  void set_highVoltage(const AlarmLimit &limit) { m_highVoltage = limit; }
  const AlarmLimit &get_highVoltage() const { return m_highVoltage; }

  void set_canResetCapacity(bool canReset) { m_canResetCapacity = canReset; }
  bool get_canResetCapacity() const { return m_canResetCapacity; }

  void set_dcType(eDCType type) { m_dcType = type; }
  eDCType get_dcType() const { return m_dcType; }

  void set_showVoltage(bool show) { m_showVoltage = show; }
  bool get_showVoltage() const { return m_showVoltage; }

  void set_showCurrent(bool show) { m_showCurrent = show; }
  bool get_showCurrent() const { return m_showCurrent; }

  void set_showStateOfCharge(bool show) { m_showStateOfCharge = show; }
  bool get_showStateOfCharge() const { return m_showStateOfCharge; }

  void set_showTemperature(bool show) { m_showTemperature = show; }
  bool get_showTemperature() const { return m_showTemperature; }

  void set_showTimeOfRemaining(bool show) { m_showTimeOfRemaining = show; }
  bool get_showTimeOfRemaining() const { return m_showTimeOfRemaining; }

  void set_acType(eACType type) { m_acType = type; }
  eACType get_acType() const { return m_acType; }

  json tojson() const;
};

class MonitoringType {
public:
  enum eTankType : int { eFuel = 0, eFreshWater = 1, eWasteWater = 2, eLiveWell = 3, eOil = 4, eBlackWater = 5 };
  static std::string to_string(eTankType type) {
    switch (type) {
    case eFuel: return "Fuel";
    case eFreshWater: return "FreshWater";
    case eWasteWater: return "WasteWater";
    case eLiveWell: return "LiveWell";
    case eOil: return "Oil";
    case eBlackWater: return "BlackWater";
    default: return "Unknown";
    }
  }

  enum ePressureType : int { eAtmospheric = 0, eWater = 1, eSteam = 2, eCompressedAir = 3, eHydraulic = 4 };
  static std::string to_string(ePressureType type) {
    switch (type) {
    case eAtmospheric: return "Atmospheric";
    case eWater: return "Water";
    case eSteam: return "Steam";
    case eCompressedAir: return "CompressedAir";
    case eHydraulic: return "Hydraulic";
    default: return "Unknown";
    }
  }

  enum eTemperatureType : int {
    eSea = 0,
    eOutside = 1,
    eInside = 2,
    eEngineRoom = 3,
    eMainCabin = 4,
    eLiveWell1 = 5,
    eBaitWell = 6,
    eRefrigeration = 7,
    eHeatingSystem = 8,
    eDewPoint = 9,
    eWindChillApparent = 10,
    eWindChillTheoretical = 11,
    eHeadIndex = 12,
    eFreezer = 13,
    eExhaustGas = 14
  };
  static std::string to_string(eTemperatureType type) {
    switch (type) {
    case eSea: return "Sea";
    case eOutside: return "Outside";
    case eInside: return "Inside";
    case eEngineRoom: return "EngineRoom";
    case eMainCabin: return "MainCabin";
    case eLiveWell1: return "LiveWell1";
    case eBaitWell: return "BaitWell";
    case eRefrigeration: return "Refrigeration";
    case eHeatingSystem: return "HeatingSystem";
    case eDewPoint: return "DewPoint";
    case eWindChillApparent: return "WindChillApparent";
    case eWindChillTheoretical: return "WindChillTheoretical";
    case eHeadIndex: return "HeadIndex";
    case eFreezer: return "Freezer";
    case eExhaustGas: return "ExhaustGas";
    default: return "Unknown";
    }
  }
};

class MonitoringDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  MonitoringType::eTankType m_tankType;
  MonitoringType::ePressureType m_pressureType;
  MonitoringType::eTemperatureType m_temperatureType;
  DataId m_circuitId;
  CircuitDevice::eSwitchType m_switchType;
  CircuitDevice::eConfirmType m_confirmDialog;
  std::string m_circuitNameUTF8;
  bool m_highTemperature;
  bool m_atmosphericPressure;
  AlarmLimit m_veryLowLimit;
  AlarmLimit m_lowLimit;
  AlarmLimit m_highLimit;
  AlarmLimit m_veryHighLimit;
  float m_tankCapacity;
  uint32_t m_address;

public:
  MonitoringDevice();
  MonitoringDevice(const MonitoringDevice &rhs);
  MonitoringDevice(MonitoringDevice &&rhs);
  MonitoringDevice &operator=(const MonitoringDevice &rhs);
  MonitoringDevice &operator=(MonitoringDevice &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_tankType(MonitoringType::eTankType type) { m_tankType = type; }
  MonitoringType::eTankType get_tankType() const { return m_tankType; }

  void set_pressureType(MonitoringType::ePressureType type) { m_pressureType = type; }
  MonitoringType::ePressureType get_pressureType() const { return m_pressureType; }

  void set_temperatureType(MonitoringType::eTemperatureType type) { m_temperatureType = type; }
  MonitoringType::eTemperatureType get_temperatureType() const { return m_temperatureType; }

  void set_circuitId(DataId id) { m_circuitId = id; }
  const DataId &get_circuitId() const { return m_circuitId; }

  void set_switchType(CircuitDevice::eSwitchType type) { m_switchType = type; }
  CircuitDevice::eSwitchType get_switchType() const { return m_switchType; }

  void set_confirmDialog(CircuitDevice::eConfirmType confirm) { m_confirmDialog = confirm; }
  CircuitDevice::eConfirmType get_confirmDialog() const { return m_confirmDialog; }

  void set_circuitNameUTF8(const std::string &name) { m_circuitNameUTF8 = name; }
  const std::string &get_circuitNameUTF8() const { return m_circuitNameUTF8; }

  void set_highTemperature(bool high) { m_highTemperature = high; }
  bool get_highTemperature() const { return m_highTemperature; }

  void set_atmosphericPressure(bool atmospheric) { m_atmosphericPressure = atmospheric; }
  bool get_atmosphericPressure() const { return m_atmosphericPressure; }

  void set_veryLowLimit(const AlarmLimit &limit) { m_veryLowLimit = limit; }
  const AlarmLimit &get_veryLowLimit() const { return m_veryLowLimit; }

  void set_lowLimit(const AlarmLimit &limit) { m_lowLimit = limit; }
  const AlarmLimit &get_lowLimit() const { return m_lowLimit; }

  void set_highLimit(const AlarmLimit &limit) { m_highLimit = limit; }
  const AlarmLimit &get_highLimit() const { return m_highLimit; }

  void set_veryHighLimit(const AlarmLimit &limit) { m_veryHighLimit = limit; }
  const AlarmLimit &get_veryHighLimit() const { return m_veryHighLimit; }

  void set_tankCapacity(float capacity) { m_tankCapacity = capacity; }
  float get_tankCapacity() const { return m_tankCapacity; }

  void set_address(uint32_t address) { m_address = address; }
  uint32_t get_address() const { return m_address; }

  json tojson() const;
};

class ACMainContactorDevice {
public:
  enum eACInputType : int {
    eShipPower = 0,
    eShorePower = 1,
    eInverter = 2,
    eParallel = 3,
  };
  static std::string to_string(eACInputType type) {
    switch (type) {
    case eShipPower: return "ShipPower";
    case eShorePower: return "ShorePower";
    case eInverter: return "Inverter";
    case eParallel: return "Parallel";
    default: return "Unknown";
    }
  }

private:
  uint32_t m_systemStateId;
  std::string m_nameUTF8;
  DataId m_contactorId;
  DataId m_contactorToggleId;
  DataId m_ac1Id;
  DataId m_ac2Id;
  DataId m_ac3Id;
  uint32_t m_displayIndex;
  uint32_t m_loadGroupIndex;
  uint32_t m_loadGroupParallelIndex;
  bool m_isParallel;
  ACMainContactorDevice::eACInputType m_acInputType;

public:
  ACMainContactorDevice();
  ACMainContactorDevice(const ACMainContactorDevice &rhs);
  ACMainContactorDevice(ACMainContactorDevice &&rhs);
  ACMainContactorDevice &operator=(const ACMainContactorDevice &rhs);
  ACMainContactorDevice &operator=(ACMainContactorDevice &&rhs);

  void set_systemStateId(uint32_t id) { m_systemStateId = id; }
  uint32_t get_systemStateId() const { return m_systemStateId; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_contactorId(const DataId &id) { m_contactorId = id; }
  const DataId &get_contactorId() const { return m_contactorId; }

  void set_contactorToggleId(const DataId &id) { m_contactorToggleId = id; }
  const DataId &get_contactorToggleId() const { return m_contactorToggleId; }

  void set_ac1Id(const DataId &id) { m_ac1Id = id; }
  const DataId &get_ac1Id() const { return m_ac1Id; }

  void set_ac2Id(const DataId &id) { m_ac2Id = id; }
  const DataId &get_ac2Id() const { return m_ac2Id; }

  void set_ac3Id(const DataId &id) { m_ac3Id = id; }
  const DataId &get_ac3Id() const { return m_ac3Id; }

  void set_displayIndex(uint32_t index) { m_displayIndex = index; }
  uint32_t get_displayIndex() const { return m_displayIndex; }

  void set_loadGroupIndex(uint32_t index) { m_loadGroupIndex = index; }
  uint32_t get_loadGroupIndex() const { return m_loadGroupIndex; }

  void set_loadGroupParallelIndex(uint32_t index) { m_loadGroupParallelIndex = index; }
  uint32_t get_loadGroupParallelIndex() const { return m_loadGroupParallelIndex; }

  void set_isParallel(bool isParallel) { m_isParallel = isParallel; }
  bool get_isParallel() const { return m_isParallel; }

  void set_acInputType(ACMainContactorDevice::eACInputType type) { m_acInputType = type; }
  ACMainContactorDevice::eACInputType get_acInputType() const { return m_acInputType; }

  json tojson() const;
};

class ACMainLoadGroupDevice {
private:
  std::string m_nameUTF8;
  uint32_t m_loadGroupIndex;

public:
  ACMainLoadGroupDevice();
  ACMainLoadGroupDevice(const ACMainLoadGroupDevice &rhs);
  ACMainLoadGroupDevice(ACMainLoadGroupDevice &&rhs);
  ACMainLoadGroupDevice &operator=(const ACMainLoadGroupDevice &rhs);
  ACMainLoadGroupDevice &operator=(ACMainLoadGroupDevice &&rhs);

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_loadGroupIndex(uint32_t index) { m_loadGroupIndex = index; }
  uint32_t get_loadGroupIndex() const { return m_loadGroupIndex; }

  json tojson() const;
};

class ACMainDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  uint32_t m_dipswitch;
  std::list<ACMainContactorDevice> m_contactors;
  std::list<ACMainLoadGroupDevice> m_loadGroups;

public:
  ACMainDevice();
  ~ACMainDevice() {
    m_contactors.clear();
    m_loadGroups.clear();
  }
  ACMainDevice(const ACMainDevice &rhs);
  ACMainDevice(ACMainDevice &&rhs);
  ACMainDevice &operator=(const ACMainDevice &rhs);
  ACMainDevice &operator=(ACMainDevice &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_dipswitch(uint32_t dipswitch) { m_dipswitch = dipswitch; }
  uint32_t get_dipswitch() const { return m_dipswitch; }

  ACMainContactorDevice &add_mutable_contactor() {
    m_contactors.emplace_back();
    return m_contactors.back();
  }
  const std::list<ACMainContactorDevice> &get_contactors() const { return m_contactors; }

  ACMainLoadGroupDevice &add_mutable_loadGroup() {
    m_loadGroups.emplace_back();
    return m_loadGroups.back();
  }
  const std::list<ACMainLoadGroupDevice> &get_loadGroups() const { return m_loadGroups; }

  json tojson() const;
};

class InverterChargerDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  uint32_t m_model;
  uint32_t m_type;
  uint32_t m_subType;
  Instance m_inverterInstance;
  DataId m_inverterACId;
  DataId m_inverterCircuitId;
  DataId m_inverterToggleCircuitId;
  Instance m_chargerInstance;
  DataId m_chargerACId;
  DataId m_chargerCircuitId;
  DataId m_chargerToggleCircuitId;
  DataId m_batteryBank1Id;
  DataId m_batteryBank2Id;
  DataId m_batteryBank3Id;
  uint32_t m_positionColumn;
  uint32_t m_positionRow;
  bool m_clustered;
  bool m_primary;
  uint32_t m_primaryPhase;
  uint32_t m_deviceInstance;
  uint32_t m_dipswitch;
  uint32_t m_channelIndex;

public:
  InverterChargerDevice();
  InverterChargerDevice(const InverterChargerDevice &rhs);
  InverterChargerDevice(InverterChargerDevice &&rhs);
  InverterChargerDevice &operator=(const InverterChargerDevice &rhs);
  InverterChargerDevice &operator=(InverterChargerDevice &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_model(uint32_t model) { m_model = model; }
  uint32_t get_model() const { return m_model; }

  void set_type(uint32_t type) { m_type = type; }
  uint32_t get_type() const { return m_type; }

  void set_subType(uint32_t subType) { m_subType = subType; }
  uint32_t get_subType() const { return m_subType; }

  void set_inverterInstance(const Instance &instance) { m_inverterInstance = instance; }
  const Instance &get_inverterInstance() const { return m_inverterInstance; }
  Instance &mutable_inverterInstance() { return m_inverterInstance; }

  void set_inverterACId(const DataId &id) { m_inverterACId = id; }
  const DataId &get_inverterACId() const { return m_inverterACId; }

  void set_inverterCircuitId(const DataId &id) { m_inverterCircuitId = id; }
  const DataId &get_inverterCircuitId() const { return m_inverterCircuitId; }

  void set_inverterToggleCircuitId(const DataId &id) { m_inverterToggleCircuitId = id; }
  const DataId &get_inverterToggleCircuitId() const { return m_inverterToggleCircuitId; }

  void set_chargerInstance(const Instance &instance) { m_chargerInstance = instance; }
  const Instance &get_chargerInstance() const { return m_chargerInstance; }
  Instance &mutable_chargerInstance() { return m_chargerInstance; }

  void set_chargerACId(const DataId &id) { m_chargerACId = id; }
  const DataId &get_chargerACId() const { return m_chargerACId; }

  void set_chargerCircuitId(const DataId &id) { m_chargerCircuitId = id; }
  const DataId &get_chargerCircuitId() const { return m_chargerCircuitId; }

  void set_chargerToggleCircuitId(const DataId &id) { m_chargerToggleCircuitId = id; }
  const DataId &get_chargerToggleCircuitId() const { return m_chargerToggleCircuitId; }

  void set_batteryBank1Id(const DataId &id) { m_batteryBank1Id = id; }
  const DataId &get_batteryBank1Id() const { return m_batteryBank1Id; }

  void set_batteryBank2Id(const DataId &id) { m_batteryBank2Id = id; }
  const DataId &get_batteryBank2Id() const { return m_batteryBank2Id; }

  void set_batteryBank3Id(const DataId &id) { m_batteryBank3Id = id; }
  const DataId &get_batteryBank3Id() const { return m_batteryBank3Id; }

  void set_positionColumn(uint32_t column) { m_positionColumn = column; }
  uint32_t get_positionColumn() const { return m_positionColumn; }

  void set_positionRow(uint32_t row) { m_positionRow = row; }
  uint32_t get_positionRow() const { return m_positionRow; }

  void set_clustered(bool clustered) { m_clustered = clustered; }
  bool get_clustered() const { return m_clustered; }

  void set_primary(bool primary) { m_primary = primary; }
  bool get_primary() const { return m_primary; }

  void set_primaryPhase(uint32_t phase) { m_primaryPhase = phase; }
  uint32_t get_primaryPhase() const { return m_primaryPhase; }

  void set_deviceInstance(uint32_t instance) { m_deviceInstance = instance; }
  uint32_t get_deviceInstance() const { return m_deviceInstance; }

  void set_dipswitch(uint32_t dipswitch) { m_dipswitch = dipswitch; }
  uint32_t get_dipswitch() const { return m_dipswitch; }

  void set_channelIndex(uint32_t index) { m_channelIndex = index; }
  uint32_t get_channelIndex() const { return m_channelIndex; }

  json tojson() const;
};

class HVACDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  DataId m_operatingModeId;
  DataId m_fanModeId;
  DataId m_fanSpeedId;
  DataId m_setpointTemperatureId;
  DataId m_operatingModeToggleId;
  DataId m_fanModeToggleId;
  DataId m_fanSpeedToggleId;
  DataId m_setpointTemperatureToggleId;
  DataId m_temperatureMonitoringId;
  uint32_t m_fanSpeedCount;
  uint32_t m_operatingModesMask;
  uint32_t m_model;
  Instance m_temperatureInstance;
  float m_setpointTemperatureMin;
  float m_setpointTemperatureMax;
  uint32_t m_fanSpeedOffModesMask;
  uint32_t m_fanSpeedAutoModesMask;
  uint32_t m_fanSpeedManualModesMask;

public:
  HVACDevice();
  HVACDevice(const HVACDevice &rhs);
  HVACDevice(HVACDevice &&rhs);
  HVACDevice &operator=(const HVACDevice &rhs);
  HVACDevice &operator=(HVACDevice &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_operatingModeId(const DataId &id) { m_operatingModeId = id; }
  const DataId &get_operatingModeId() const { return m_operatingModeId; }

  void set_fanModeId(const DataId &id) { m_fanModeId = id; }
  const DataId &get_fanModeId() const { return m_fanModeId; }

  void set_fanSpeedId(const DataId &id) { m_fanSpeedId = id; }
  const DataId &get_fanSpeedId() const { return m_fanSpeedId; }

  void set_setpointTemperatureId(const DataId &id) { m_setpointTemperatureId = id; }
  const DataId &get_setpointTemperatureId() const { return m_setpointTemperatureId; }

  void set_operatingModeToggleId(const DataId &id) { m_operatingModeToggleId = id; }
  const DataId &get_operatingModeToggleId() const { return m_operatingModeToggleId; }

  void set_fanModeToggleId(const DataId &id) { m_fanModeToggleId = id; }
  const DataId &get_fanModeToggleId() const { return m_fanModeToggleId; }

  void set_fanSpeedToggleId(const DataId &id) { m_fanSpeedToggleId = id; }
  const DataId &get_fanSpeedToggleId() const { return m_fanSpeedToggleId; }

  void set_setpointTemperatureToggleId(const DataId &id) { m_setpointTemperatureToggleId = id; }
  const DataId &get_setpointTemperatureToggleId() const { return m_setpointTemperatureToggleId; }

  void set_temperatureMonitoringId(const DataId &id) { m_temperatureMonitoringId = id; }
  const DataId &get_temperatureMonitoringId() const { return m_temperatureMonitoringId; }

  void set_fanSpeedCount(uint32_t count) { m_fanSpeedCount = count; }
  uint32_t get_fanSpeedCount() const { return m_fanSpeedCount; }

  void set_operatingModesMask(uint32_t mask) { m_operatingModesMask = mask; }
  uint32_t get_operatingModesMask() const { return m_operatingModesMask; }

  void set_model(uint32_t model) { m_model = model; }
  uint32_t get_model() const { return m_model; }

  void set_temperatureInstance(const Instance &instance) { m_temperatureInstance = instance; }
  const Instance &get_temperatureInstance() const { return m_temperatureInstance; }
  Instance &mutable_temperatureInstance() { return m_temperatureInstance; }

  void set_setpointTemperatureMin(float min) { m_setpointTemperatureMin = min; }
  float get_setpointTemperatureMin() const { return m_setpointTemperatureMin; }

  void set_setpointTemperatureMax(float max) { m_setpointTemperatureMax = max; }
  float get_setpointTemperatureMax() const { return m_setpointTemperatureMax; }

  void set_fanSpeedOffModesMask(uint32_t mask) { m_fanSpeedOffModesMask = mask; }
  uint32_t get_fanSpeedOffModesMask() const { return m_fanSpeedOffModesMask; }

  void set_fanSpeedAutoModesMask(uint32_t mask) { m_fanSpeedAutoModesMask = mask; }
  uint32_t get_fanSpeedAutoModesMask() const { return m_fanSpeedAutoModesMask; }

  void set_fanSpeedManualModesMask(uint32_t mask) { m_fanSpeedManualModesMask = mask; }
  uint32_t get_fanSpeedManualModesMask() const { return m_fanSpeedManualModesMask; }

  json tojson() const;
};

class BinarySignalBitAddress {
private:
  uint32_t m_dataType;
  uint32_t m_dipswitch;
  uint32_t m_bit;

public:
  BinarySignalBitAddress();
  BinarySignalBitAddress(uint32_t dataType, uint32_t dipswitch, uint32_t bit);
  BinarySignalBitAddress(const BinarySignalBitAddress &rhs);
  BinarySignalBitAddress(BinarySignalBitAddress &&rhs);
  BinarySignalBitAddress &operator=(const BinarySignalBitAddress &rhs);
  BinarySignalBitAddress &operator=(BinarySignalBitAddress &&rhs);

  void set_dataType(uint32_t dataType) { m_dataType = dataType; }
  uint32_t get_dataType() const { return m_dataType; }

  void set_dipswitch(uint32_t dipswitch) { m_dipswitch = dipswitch; }
  uint32_t get_dipswitch() const { return m_dipswitch; }

  void set_bit(uint32_t bit) { m_bit = bit; }
  uint32_t get_bit() const { return m_bit; }

  json tojson() const;
};

class ZipdeeAwningDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  DataId m_openId;
  DataId m_closeId;
  DataId m_tiltLeftId;
  DataId m_tiltRightId;
  std::list<BinarySignalBitAddress> m_binarySignals;

public:
  ZipdeeAwningDevice();
  ~ZipdeeAwningDevice() { m_binarySignals.clear(); }
  ZipdeeAwningDevice(const ZipdeeAwningDevice &rhs);
  ZipdeeAwningDevice(ZipdeeAwningDevice &&rhs);
  ZipdeeAwningDevice &operator=(const ZipdeeAwningDevice &rhs);
  ZipdeeAwningDevice &operator=(ZipdeeAwningDevice &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_openId(const DataId &id) { m_openId = id; }
  const DataId &get_openId() const { return m_openId; }

  void set_closeId(const DataId &id) { m_closeId = id; }
  const DataId &get_closeId() const { return m_closeId; }

  void set_tiltLeftId(const DataId &id) { m_tiltLeftId = id; }
  const DataId &get_tiltLeftId() const { return m_tiltLeftId; }

  void set_tiltRightId(const DataId &id) { m_tiltRightId = id; }
  const DataId &get_tiltRightId() const { return m_tiltRightId; }

  BinarySignalBitAddress &add_mutable_binarySignal() {
    m_binarySignals.emplace_back();
    return m_binarySignals.back();
  }
  const std::list<BinarySignalBitAddress> &get_binarySignals() const { return m_binarySignals; }

  json tojson() const;
};

class ThirdPartyGeneratorDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  DataId m_startControlId;
  DataId m_stopControlId;
  Instance m_associatedAcMetersInstance;
  DataId m_acMeterLine1Id;
  DataId m_acMeterLine2Id;
  DataId m_acMeterLine3Id;

public:
  ThirdPartyGeneratorDevice();
  ThirdPartyGeneratorDevice(const ThirdPartyGeneratorDevice &rhs);
  ThirdPartyGeneratorDevice(ThirdPartyGeneratorDevice &&rhs);
  ThirdPartyGeneratorDevice &operator=(const ThirdPartyGeneratorDevice &rhs);
  ThirdPartyGeneratorDevice &operator=(ThirdPartyGeneratorDevice &&rhs);

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_startControlId(const DataId &id) { m_startControlId = id; }
  const DataId &get_startControlId() const { return m_startControlId; }

  void set_stopControlId(const DataId &id) { m_stopControlId = id; }
  const DataId &get_stopControlId() const { return m_stopControlId; }

  void set_associatedAcMetersInstance(const Instance &instance) { m_associatedAcMetersInstance = instance; }
  const Instance &get_associatedAcMetersInstance() const { return m_associatedAcMetersInstance; }
  Instance &mutable_associatedAcMetersInstance() { return m_associatedAcMetersInstance; }

  void set_acMeterLine1Id(const DataId &id) { m_acMeterLine1Id = id; }
  const DataId &get_acMeterLine1Id() const { return m_acMeterLine1Id; }

  void set_acMeterLine2Id(const DataId &id) { m_acMeterLine2Id = id; }
  const DataId &get_acMeterLine2Id() const { return m_acMeterLine2Id; }

  void set_acMeterLine3Id(const DataId &id) { m_acMeterLine3Id = id; }
  const DataId &get_acMeterLine3Id() const { return m_acMeterLine3Id; }

  json tojson() const;
};

class TyrePressureDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  uint32_t m_numberOfAxles;
  uint32_t m_tyresAxle1;
  uint32_t m_tyresAxle2;
  uint32_t m_tyresAxle3;
  uint32_t m_tyresAxle4;
  uint32_t m_spareAxle;
  std::list<Instance> m_tyreInstances;
  std::list<Instance> m_tyreSpareInstances;

public:
  TyrePressureDevice();
  ~TyrePressureDevice() {
    m_tyreInstances.clear();
    m_tyreSpareInstances.clear();
  }
  TyrePressureDevice(const TyrePressureDevice &rhs);
  TyrePressureDevice(TyrePressureDevice &&rhs);
  TyrePressureDevice &operator=(const TyrePressureDevice &rhs);
  TyrePressureDevice &operator=(TyrePressureDevice &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_numberOfAxles(uint32_t number) { m_numberOfAxles = number; }
  uint32_t get_numberOfAxles() const { return m_numberOfAxles; }

  void set_tyresAxle1(uint32_t tyres) { m_tyresAxle1 = tyres; }
  uint32_t get_tyresAxle1() const { return m_tyresAxle1; }

  void set_tyresAxle2(uint32_t tyres) { m_tyresAxle2 = tyres; }
  uint32_t get_tyresAxle2() const { return m_tyresAxle2; }

  void set_tyresAxle3(uint32_t tyres) { m_tyresAxle3 = tyres; }
  uint32_t get_tyresAxle3() const { return m_tyresAxle3; }

  void set_tyresAxle4(uint32_t tyres) { m_tyresAxle4 = tyres; }
  uint32_t get_tyresAxle4() const { return m_tyresAxle4; }

  void set_spareAxle(uint32_t spare) { m_spareAxle = spare; }
  uint32_t get_spareAxle() const { return m_spareAxle; }

  Instance &add_mutable_tyreInstance() {
    m_tyreInstances.emplace_back();
    return m_tyreInstances.back();
  }
  const std::list<Instance> &get_tyreInstances() const { return m_tyreInstances; }

  Instance &add_mutable_tyreSpareInstance() {
    m_tyreSpareInstances.emplace_back();
    return m_tyreSpareInstances.back();
  }
  const std::list<Instance> &get_tyreSpareInstances() const { return m_tyreSpareInstances; }
};

class AudioStereoDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  bool m_muteEnabled;
  std::list<DataId> m_circuitIds;

public:
  AudioStereoDevice();
  ~AudioStereoDevice() { m_circuitIds.clear(); }
  AudioStereoDevice(const AudioStereoDevice &rhs);
  AudioStereoDevice(AudioStereoDevice &&rhs);
  AudioStereoDevice &operator=(const AudioStereoDevice &rhs);
  AudioStereoDevice &operator=(AudioStereoDevice &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_muteEnabled(bool enabled) { m_muteEnabled = enabled; }
  bool get_muteEnabled() const { return m_muteEnabled; }

  DataId &add_mutable_circuitId() {
    m_circuitIds.emplace_back();
    return m_circuitIds.back();
  }
  const std::list<DataId> &get_circuitIds() const { return m_circuitIds; }
  void add_circuitId(const DataId &id) { m_circuitIds.push_back(id); }
};

class ShoreFuseDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  DataId m_shoreFuseControlId;

public:
  ShoreFuseDevice();
  ShoreFuseDevice(const ShoreFuseDevice &rhs);
  ShoreFuseDevice(ShoreFuseDevice &&rhs);
  ShoreFuseDevice &operator=(const ShoreFuseDevice &rhs);
  ShoreFuseDevice &operator=(ShoreFuseDevice &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_shoreFuseControlId(const DataId &id) { m_shoreFuseControlId = id; }
  const DataId &get_shoreFuseControlId() const { return m_shoreFuseControlId; }
  DataId &mutable_shoreFuseControlId() { return m_shoreFuseControlId; }
};

class FantasticFanDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  DataId m_directionForwardCircuitId;
  DataId m_directionReverseCircuitId;
  DataId m_lidOpenCircuitId;
  DataId m_lidCloseCircuitId;
  DataId m_fanCircuitId;

public:
  FantasticFanDevice();
  FantasticFanDevice(const FantasticFanDevice &rhs);
  FantasticFanDevice(FantasticFanDevice &&rhs);
  FantasticFanDevice &operator=(const FantasticFanDevice &rhs);
  FantasticFanDevice &operator=(FantasticFanDevice &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_directionForwardCircuitId(const DataId &id) { m_directionForwardCircuitId = id; }
  const DataId &get_directionForwardCircuitId() const { return m_directionForwardCircuitId; }
  DataId &mutable_directionForwardCircuitId() { return m_directionForwardCircuitId; }

  void set_directionReverseCircuitId(const DataId &id) { m_directionReverseCircuitId = id; }
  const DataId &get_directionReverseCircuitId() const { return m_directionReverseCircuitId; }
  DataId &mutable_directionReverseCircuitId() { return m_directionReverseCircuitId; }

  void set_lidOpenCircuitId(const DataId &id) { m_lidOpenCircuitId = id; }
  const DataId &get_lidOpenCircuitId() const { return m_lidOpenCircuitId; }
  DataId &mutable_lidOpenCircuitId() { return m_lidOpenCircuitId; }

  void set_lidCloseCircuitId(const DataId &id) { m_lidCloseCircuitId = id; }
  const DataId &get_lidCloseCircuitId() const { return m_lidCloseCircuitId; }
  DataId &mutable_lidCloseCircuitId() { return m_lidCloseCircuitId; }

  void set_fanCircuitId(const DataId &id) { m_fanCircuitId = id; }
  const DataId &get_fanCircuitId() const { return m_fanCircuitId; }
  DataId &mutable_fanCircuitId() { return m_fanCircuitId; }
};

class ScreenConfigHeader {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  uint32_t m_targetDisplayType;
  uint32_t m_targetId;
  uint32_t m_confirmationType;
  uint32_t m_smoothStart;
  uint32_t m_index;
  uint32_t m_parentIndex;
  uint32_t m_controlId;

public:
  ScreenConfigHeader();
  ScreenConfigHeader(const ScreenConfigHeader &rhs);
  ScreenConfigHeader(ScreenConfigHeader &&rhs);
  ScreenConfigHeader &operator=(const ScreenConfigHeader &rhs);
  ScreenConfigHeader &operator=(ScreenConfigHeader &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_targetDisplayType(uint32_t type) { m_targetDisplayType = type; }
  uint32_t get_targetDisplayType() const { return m_targetDisplayType; }

  void set_targetId(uint32_t id) { m_targetId = id; }
  uint32_t get_targetId() const { return m_targetId; }

  void set_confirmationType(uint32_t type) { m_confirmationType = type; }
  uint32_t get_confirmationType() const { return m_confirmationType; }

  void set_smoothStart(uint32_t smooth) { m_smoothStart = smooth; }
  uint32_t get_smoothStart() const { return m_smoothStart; }

  void set_index(uint32_t index) { m_index = index; }
  uint32_t get_index() const { return m_index; }

  void set_parentIndex(uint32_t parentIndex) { m_parentIndex = parentIndex; }
  uint32_t get_parentIndex() const { return m_parentIndex; }

  void set_controlId(uint32_t controlId) { m_controlId = controlId; }
  uint32_t get_controlId() const { return m_controlId; }
};

class ScreenConfigPageImageItem {
private:
  ScreenConfigHeader m_header;
  float m_locationX;
  float m_locationY;
  float m_targetX;
  float m_targetY;
  uint32_t m_icon;
  std::string m_name;
  bool m_hideWhenOff;

public:
  ScreenConfigPageImageItem();
  ScreenConfigPageImageItem(const ScreenConfigPageImageItem &rhs);
  ScreenConfigPageImageItem(ScreenConfigPageImageItem &&rhs);
  ScreenConfigPageImageItem &operator=(const ScreenConfigPageImageItem &rhs);
  ScreenConfigPageImageItem &operator=(ScreenConfigPageImageItem &&rhs);
  json tojson() const;

  void set_header(const ScreenConfigHeader &header) { m_header = header; }
  const ScreenConfigHeader &get_header() const { return m_header; }
  ScreenConfigHeader &mutable_header() { return m_header; }

  void set_locationX(float x) { m_locationX = x; }
  float get_locationX() const { return m_locationX; }

  void set_locationY(float y) { m_locationY = y; }
  float get_locationY() const { return m_locationY; }

  void set_targetX(float x) { m_targetX = x; }
  float get_targetX() const { return m_targetX; }

  void set_targetY(float y) { m_targetY = y; }
  float get_targetY() const { return m_targetY; }

  void set_icon(uint32_t icon) { m_icon = icon; }
  uint32_t get_icon() const { return m_icon; }

  void set_name(const std::string &name) { m_name = name; }
  const std::string &get_name() const { return m_name; }

  void set_hideWhenOff(bool hide) { m_hideWhenOff = hide; }
  bool get_hideWhenOff() const { return m_hideWhenOff; }
};

class ScreenConfigPageGridItem {
private:
  ScreenConfigHeader m_header;
  uint32_t m_gridX;
  uint32_t m_gridY;
  float m_targetX;
  float m_targetY;
  float m_targetWidth;
  float m_targetHeight;
  int m_icon;
  std::string m_name;
  int m_columnSpan;
  int m_rowSpan;
  int m_doubleThrowType;

public:
  ScreenConfigPageGridItem();
  ScreenConfigPageGridItem(const ScreenConfigPageGridItem &rhs);
  ScreenConfigPageGridItem(ScreenConfigPageGridItem &&rhs);
  ScreenConfigPageGridItem &operator=(const ScreenConfigPageGridItem &rhs);
  ScreenConfigPageGridItem &operator=(ScreenConfigPageGridItem &&rhs);
  json tojson() const;

  void set_header(const ScreenConfigHeader &header) { m_header = header; }
  const ScreenConfigHeader &get_header() const { return m_header; }
  ScreenConfigHeader &mutable_header() { return m_header; }

  void set_gridX(uint32_t x) { m_gridX = x; }
  uint32_t get_gridX() const { return m_gridX; }

  void set_gridY(uint32_t y) { m_gridY = y; }
  uint32_t get_gridY() const { return m_gridY; }

  void set_targetX(float x) { m_targetX = x; }
  float get_targetX() const { return m_targetX; }

  void set_targetY(float y) { m_targetY = y; }
  float get_targetY() const { return m_targetY; }

  void set_targetWidth(float width) { m_targetWidth = width; }
  float get_targetWidth() const { return m_targetWidth; }

  void set_targetHeight(float height) { m_targetHeight = height; }
  float get_targetHeight() const { return m_targetHeight; }

  void set_icon(int icon) { m_icon = icon; }
  int get_icon() const { return m_icon; }

  void set_name(const std::string &name) { m_name = name; }
  const std::string &get_name() const { return m_name; }

  void set_columnSpan(int span) { m_columnSpan = span; }
  int get_columnSpan() const { return m_columnSpan; }

  void set_rowSpan(int span) { m_rowSpan = span; }
  int get_rowSpan() const { return m_rowSpan; }

  void set_doubleThrowType(int type) { m_doubleThrowType = type; }
  int get_doubleThrowType() const { return m_doubleThrowType; }
};

class ScreenConfigPageImage {
private:
  ScreenConfigHeader m_header;
  uint32_t m_gridX;
  uint32_t m_gridY;
  uint32_t m_gridWidth;
  uint32_t m_gridHeight;
  float m_sourceWidth;
  float m_sourceHeight;
  float m_targetX;
  float m_targetY;
  float m_targetWidth;
  float m_targetHeight;
  std::string m_fileName;
  uint32_t m_backgroundColourR;
  uint32_t m_backgroundColourG;
  uint32_t m_backgroundColourB;
  uint32_t m_showBackground;
  uint32_t m_cropToFit;

public:
  ScreenConfigPageImage();
  ScreenConfigPageImage(const ScreenConfigPageImage &rhs);
  ScreenConfigPageImage(ScreenConfigPageImage &&rhs);
  ScreenConfigPageImage &operator=(const ScreenConfigPageImage &rhs);
  ScreenConfigPageImage &operator=(ScreenConfigPageImage &&rhs);
  json tojson() const;

  void set_header(const ScreenConfigHeader &header) { m_header = header; }
  const ScreenConfigHeader &get_header() const { return m_header; }
  ScreenConfigHeader &mutable_header() { return m_header; }

  void set_gridX(uint32_t x) { m_gridX = x; }
  uint32_t get_gridX() const { return m_gridX; }

  void set_gridY(uint32_t y) { m_gridY = y; }
  uint32_t get_gridY() const { return m_gridY; }

  void set_gridWidth(uint32_t width) { m_gridWidth = width; }
  uint32_t get_gridWidth() const { return m_gridWidth; }

  void set_gridHeight(uint32_t height) { m_gridHeight = height; }
  uint32_t get_gridHeight() const { return m_gridHeight; }

  void set_sourceWidth(float width) { m_sourceWidth = width; }
  float get_sourceWidth() const { return m_sourceWidth; }

  void set_sourceHeight(float height) { m_sourceHeight = height; }
  float get_sourceHeight() const { return m_sourceHeight; }

  void set_targetX(float x) { m_targetX = x; }
  float get_targetX() const { return m_targetX; }

  void set_targetY(float y) { m_targetY = y; }
  float get_targetY() const { return m_targetY; }

  void set_targetWidth(float width) { m_targetWidth = width; }
  float get_targetWidth() const { return m_targetWidth; }

  void set_targetHeight(float height) { m_targetHeight = height; }
  float get_targetHeight() const { return m_targetHeight; }

  void set_fileName(const std::string &fileName) { m_fileName = fileName; }
  const std::string &get_fileName() const { return m_fileName; }

  void set_backgroundColourR(uint32_t r) { m_backgroundColourR = r; }
  uint32_t get_backgroundColourR() const { return m_backgroundColourR; }

  void set_backgroundColourG(uint32_t g) { m_backgroundColourG = g; }
  uint32_t get_backgroundColourG() const { return m_backgroundColourG; }

  void set_backgroundColourB(uint32_t b) { m_backgroundColourB = b; }
  uint32_t get_backgroundColourB() const { return m_backgroundColourB; }

  void set_showBackground(uint32_t show) { m_showBackground = show; }
  uint32_t get_showBackground() const { return m_showBackground; }

  uint32_t get_cropToFit() const { return m_cropToFit; }
  void set_cropToFit(uint32_t crop) { m_cropToFit = crop; }
};

class ScreenConfigPage {
private:
  ScreenConfigHeader m_header;

public:
  ScreenConfigPage();
  ScreenConfigPage(const ScreenConfigPage &rhs);
  ScreenConfigPage(ScreenConfigPage &&rhs);
  ScreenConfigPage &operator=(const ScreenConfigPage &rhs);
  ScreenConfigPage &operator=(ScreenConfigPage &&rhs);
  json tojson() const;

  void set_header(const ScreenConfigHeader &header) { m_header = header; }
  const ScreenConfigHeader &get_header() const { return m_header; }
  ScreenConfigHeader &mutable_header() { return m_header; }
};

class ScreenConfigMode {
private:
  ScreenConfigHeader m_header;
  std::string m_name;

public:
  ScreenConfigMode();
  ScreenConfigMode(const ScreenConfigMode &rhs);
  ScreenConfigMode(ScreenConfigMode &&rhs);
  ScreenConfigMode &operator=(const ScreenConfigMode &rhs);
  ScreenConfigMode &operator=(ScreenConfigMode &&rhs);
  json tojson() const;

  void set_header(const ScreenConfigHeader &header) { m_header = header; }
  const ScreenConfigHeader &get_header() const { return m_header; }
  ScreenConfigHeader &mutable_header() { return m_header; }

  void set_name(const std::string &name) { m_name = name; }
  const std::string &get_name() const { return m_name; }
};

class ScreenConfig {
private:
  ScreenConfigHeader m_header;
  uint32_t m_gridWidth;
  uint32_t m_gridHeight;
  uint32_t m_landscape;
  std::string m_displayName;
  std::string m_relativePath;

public:
  ScreenConfig();
  ScreenConfig(const ScreenConfig &rhs);
  ScreenConfig(ScreenConfig &&rhs);
  ScreenConfig &operator=(const ScreenConfig &rhs);
  ScreenConfig &operator=(ScreenConfig &&rhs);
  json tojson() const;

  void set_header(const ScreenConfigHeader &header) { m_header = header; }
  const ScreenConfigHeader &get_header() const { return m_header; }
  ScreenConfigHeader &mutable_header() { return m_header; }

  void set_gridWidth(uint32_t width) { m_gridWidth = width; }
  uint32_t get_gridWidth() const { return m_gridWidth; }

  void set_gridHeight(uint32_t height) { m_gridHeight = height; }
  uint32_t get_gridHeight() const { return m_gridHeight; }

  void set_landscape(uint32_t landscape) { m_landscape = landscape; }
  uint32_t get_landscape() const { return m_landscape; }

  void set_displayName(const std::string &name) { m_displayName = name; }
  const std::string &get_displayName() const { return m_displayName; }

  void set_relativePath(const std::string &path) { m_relativePath = path; }
  const std::string &get_relativePath() const { return m_relativePath; }
};

class FavouritesInfo {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  uint32_t m_targetDisplayType;
  uint32_t m_targetId;
  uint32_t m_x;
  uint32_t m_y;

public:
  FavouritesInfo();
  FavouritesInfo(const FavouritesInfo &rhs);
  FavouritesInfo(FavouritesInfo &&rhs);
  FavouritesInfo &operator=(const FavouritesInfo &rhs);
  FavouritesInfo &operator=(FavouritesInfo &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_targetDisplayType(uint32_t type) { m_targetDisplayType = type; }
  uint32_t get_targetDisplayType() const { return m_targetDisplayType; }

  void set_targetId(uint32_t id) { m_targetId = id; }
  uint32_t get_targetId() const { return m_targetId; }

  void set_x(uint32_t x) { m_x = x; }
  uint32_t get_x() const { return m_x; }

  void set_y(uint32_t y) { m_y = y; }
  uint32_t get_y() const { return m_y; }
};

class Device {
public:
  enum eDeviceType : int {
    eNone = 0,
    eOutputInterface = 15,
    eMeterInterface = 14,
    eSignalInterface = 13,
    eMotorControlInterface = 12,
    eSwitchInterface = 11,
    eACOutputInterface = 10,
    eACMainsInterface = 9,
    eMasterbusInterface = 8,
    eContact6 = 7,
    eSwitchPad = 3,
    eWirelessInterface = 17,
    eDisplayInterface = 16,
    eSmartBatteryHub = 27,
    eControl1 = 28,
    eKeypad = 29,
    eContact6Plus = 30,
    eCombinationOutputInterface = 31,
    eM2VSM = 32,
    eCZoneDDS = 33,
    eRV1 = 48,
    eControlX = 54,
    eEuropa = 64,
    eShunt = 128,
    eCharger = 129,
    eInverterCharger = 130,
    eBattery = 131,
  };
  static std::string to_string(eDeviceType type) {
    switch (type) {
    case eNone: return "None";
    case eOutputInterface: return "OutputInterface";
    case eMeterInterface: return "MeterInterface";
    case eSignalInterface: return "SignalInterface";
    case eMotorControlInterface: return "MotorControlInterface";
    case eSwitchInterface: return "SwitchInterface";
    case eACOutputInterface: return "ACOutputInterface";
    case eACMainsInterface: return "ACMainsInterface";
    case eMasterbusInterface: return "MasterbusInterface";
    case eContact6: return "Contact6";
    case eSwitchPad: return "SwitchPad";
    case eWirelessInterface: return "WirelessInterface";
    case eDisplayInterface: return "DisplayInterface";
    case eSmartBatteryHub: return "SmartBatteryHub";
    case eControl1: return "Control1";
    case eKeypad: return "Keypad";
    case eContact6Plus: return "Contact6Plus";
    case eCombinationOutputInterface: return "CombinationOutputInterface";
    case eM2VSM: return "M2VSM";
    case eCZoneDDS: return "CZoneDDS";
    case eRV1: return "RV1";
    case eControlX: return "ControlX";
    case eEuropa: return "Europa";
    case eShunt: return "Shunt";
    case eCharger: return "Charger";
    case eInverterCharger: return "InverterCharger";
    case eBattery: return "Battery";
    default: return "Unknown";
    }
  }

private:
  ConfigRequest::eConfigType m_displayType;
  std::string m_nameUTF8;
  uint32_t m_dipswitch;
  uint32_t m_sourceAddress;
  bool m_conflict;
  Device::eDeviceType m_deviceType;
  bool m_valid;
  bool m_transient;
  std::string m_version;

public:
  Device();
  Device(const Device &rhs);
  Device(Device &&rhs);
  Device &operator=(const Device &rhs);
  Device &operator=(Device &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_dipswitch(uint32_t dipswitch) { m_dipswitch = dipswitch; }
  uint32_t get_dipswitch() const { return m_dipswitch; }

  void set_sourceAddress(uint32_t address) { m_sourceAddress = address; }
  uint32_t get_sourceAddress() const { return m_sourceAddress; }

  void set_conflict(bool conflict) { m_conflict = conflict; }
  bool get_conflict() const { return m_conflict; }

  void set_deviceType(Device::eDeviceType type) { m_deviceType = type; }
  Device::eDeviceType get_deviceType() const { return m_deviceType; }

  void set_valid(bool valid) { m_valid = valid; }
  bool get_valid() const { return m_valid; }

  void set_transient(bool transient) { m_transient = transient; }
  bool get_transient() const { return m_transient; }

  void set_version(const std::string &version) { m_version = version; }
  const std::string &get_version() const { return m_version; }
};

class GNSSDevice {
private:
  ConfigRequest::eConfigType m_displayType;
  uint32_t m_id;
  std::string m_nameUTF8;
  Instance m_instance;
  bool m_isExternal;

public:
  GNSSDevice();
  GNSSDevice(const GNSSDevice &rhs);
  GNSSDevice(GNSSDevice &&rhs);
  GNSSDevice &operator=(const GNSSDevice &rhs);
  GNSSDevice &operator=(GNSSDevice &&rhs);
  json tojson() const;

  void set_displayType(ConfigRequest::eConfigType type) { m_displayType = type; }
  ConfigRequest::eConfigType get_displayType() const { return m_displayType; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_nameUTF8(const std::string &name) { m_nameUTF8 = name; }
  const std::string &get_nameUTF8() const { return m_nameUTF8; }

  void set_instance(const Instance &instance) { m_instance = instance; }
  const Instance &get_instance() const { return m_instance; }
  Instance &mutable_instance() { return m_instance; }

  void set_isExternal(bool isExternal) { m_isExternal = isExternal; }
  bool get_isExternal() const { return m_isExternal; }
};

class UiRelationshipMsg {
public:
  enum eItemType : int {
    eNone = 0,
    eFluidLevel = 1,
    ePressure = 2,
    eTemperature = 3,
    eDCMeter = 4,
    eACMeter = 5,
    eBinaryLogicState = 6,
    eCircuit = 7,
    eCategory = 8,
    eInverterCharger = 9,
  };
  static std::string to_string(eItemType type) {
    switch (type) {
    case eNone: return "None";
    case eFluidLevel: return "FluidLevel";
    case ePressure: return "Pressure";
    case eTemperature: return "Temperature";
    case eDCMeter: return "DCMeter";
    case eACMeter: return "ACMeter";
    case eBinaryLogicState: return "BinaryLogicState";
    case eCircuit: return "Circuit";
    case eCategory: return "Category";
    case eInverterCharger: return "InverterCharger";
    default: return "Unknown";
    }
  }

  enum eRelationshipType : int {
    eNormal = 0,
    eDuplicates = 1,
  };
  static std::string to_string(eRelationshipType type) {
    switch (type) {
    case eNormal: return "Normal";
    case eDuplicates: return "Duplicates";
    default: return "Unknown";
    }
  }

private:
  ConfigRequest::eConfigType m_displaytype;
  uint32_t m_id;
  eItemType m_primarytype;
  eItemType m_secondarytype;
  uint32_t m_primaryid;
  uint32_t m_secondaryid;
  eRelationshipType m_relationshiptype;
  uint32_t m_primaryconfigaddress;
  uint32_t m_secondaryconfigaddress;
  uint32_t m_primarychannelindex;
  uint32_t m_secondarychannelindex;

public:
  UiRelationshipMsg();
  UiRelationshipMsg(const UiRelationshipMsg &rhs);
  UiRelationshipMsg(UiRelationshipMsg &&rhs);
  UiRelationshipMsg &operator=(const UiRelationshipMsg &rhs);
  UiRelationshipMsg &operator=(UiRelationshipMsg &&rhs);
  json tojson() const;

  void set_displaytype(ConfigRequest::eConfigType type) { m_displaytype = type; }
  ConfigRequest::eConfigType get_displaytype() const { return m_displaytype; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_primarytype(eItemType type) { m_primarytype = type; }
  eItemType get_primarytype() const { return m_primarytype; }

  void set_secondarytype(eItemType type) { m_secondarytype = type; }
  eItemType get_secondarytype() const { return m_secondarytype; }

  void set_relationshiptype(eRelationshipType type) { m_relationshiptype = type; }
  eRelationshipType get_relationshiptype() const { return m_relationshiptype; }

  void set_primaryconfigaddress(uint32_t address) { m_primaryconfigaddress = address; }
  uint32_t get_primaryconfigaddress() const { return m_primaryconfigaddress; }

  void set_secondaryconfigaddress(uint32_t address) { m_secondaryconfigaddress = address; }
  uint32_t get_secondaryconfigaddress() const { return m_secondaryconfigaddress; }

  void set_primarychannelindex(uint32_t index) { m_primarychannelindex = index; }
  uint32_t get_primarychannelindex() const { return m_primarychannelindex; }

  void set_secondarychannelindex(uint32_t index) { m_secondarychannelindex = index; }
  uint32_t get_secondarychannelindex() const { return m_secondarychannelindex; }

  uint32_t get_primaryid() const { return m_primaryid; }
  void set_primaryid(uint32_t id) { m_primaryid = id; }

  uint32_t get_secondaryid() const { return m_secondaryid; }
  void set_secondaryid(uint32_t id) { m_secondaryid = id; }
};

class BinaryLogicStateMsg {
private:
  ConfigRequest::eConfigType m_displaytype;
  uint32_t m_id;
  uint32_t m_address;
  std::string m_nameutf8;

public:
  BinaryLogicStateMsg();
  BinaryLogicStateMsg(const BinaryLogicStateMsg &rhs);
  BinaryLogicStateMsg(BinaryLogicStateMsg &&rhs);
  BinaryLogicStateMsg &operator=(const BinaryLogicStateMsg &rhs);
  BinaryLogicStateMsg &operator=(BinaryLogicStateMsg &&rhs);
  json tojson() const;

  void set_displaytype(ConfigRequest::eConfigType type) { m_displaytype = type; }
  ConfigRequest::eConfigType get_displaytype() const { return m_displaytype; }

  void set_id(uint32_t id) { m_id = id; }
  uint32_t get_id() const { return m_id; }

  void set_address(uint32_t address) { m_address = address; }
  uint32_t get_address() const { return m_address; }

  void set_nameutf8(const std::string &name) { m_nameutf8 = name; }
  const std::string &get_nameutf8() const { return m_nameutf8; }
};

class SwitchPositiveNegtive {
public:
  enum eSwitchPositiveNegtiveMode : int {
    eSwitchBatteryPositive = 0,
    eSwitchBatteryNegtive = 1,
  };
  static std::string to_string(eSwitchPositiveNegtiveMode mode) {
    switch (mode) {
    case eSwitchBatteryPositive: return "SwitchBatteryPositive";
    case eSwitchBatteryNegtive: return "SwitchBatteryNegtive";
    default: return "Unknown";
    }
  }

private:
  uint32_t m_channelAddress;
  uint32_t m_channel;
  eSwitchPositiveNegtiveMode m_mode;
  uint32_t m_binaryStatusIndex;

public:
  SwitchPositiveNegtive();
  SwitchPositiveNegtive(const SwitchPositiveNegtive &rhs);
  SwitchPositiveNegtive(SwitchPositiveNegtive &&rhs);
  SwitchPositiveNegtive &operator=(const SwitchPositiveNegtive &rhs);
  SwitchPositiveNegtive &operator=(SwitchPositiveNegtive &&rhs);

  void set_channelAddress(uint32_t address) { m_channelAddress = address; }
  uint32_t get_channelAddress() const { return m_channelAddress; }

  void set_channel(uint32_t channel) { m_channel = channel; }
  uint32_t get_channel() const { return m_channel; }

  void set_mode(eSwitchPositiveNegtiveMode mode) { m_mode = mode; }
  eSwitchPositiveNegtiveMode get_mode() const { return m_mode; }

  void set_binaryStatusIndex(uint32_t index) { m_binaryStatusIndex = index; }
  uint32_t get_binaryStatusIndex() const { return m_binaryStatusIndex; }
};

class RTCoreMapEntry {
private:
  ConfigRequest::eConfigType m_displaytype;
  CircuitLoad m_circuitLoads;
  MeteringDevice m_dcMeters;
  MonitoringDevice m_monitoringDevice;
  SwitchPositiveNegtive m_switchPositiveNegtive;
  std::map<std::string, Alarm> m_alarms;
  std::list<CircuitDevice> m_circuits;

public:
  RTCoreMapEntry();
  ~RTCoreMapEntry() {
    m_alarms.clear();
    m_circuits.clear();
  }
  RTCoreMapEntry(const RTCoreMapEntry &rhs);
  RTCoreMapEntry(RTCoreMapEntry &&rhs);
  RTCoreMapEntry &operator=(const RTCoreMapEntry &rhs);
  RTCoreMapEntry &operator=(RTCoreMapEntry &&rhs);

  void set_displaytype(ConfigRequest::eConfigType type) { m_displaytype = type; }
  ConfigRequest::eConfigType get_displaytype() const { return m_displaytype; }

  void set_circuitLoads(const CircuitLoad &&circuitLoads) { m_circuitLoads = std::move(circuitLoads); }
  const CircuitLoad &get_circuitLoads() const { return m_circuitLoads; }
  CircuitLoad &mutable_circuitLoads() { return m_circuitLoads; }

  void set_dcMeters(const MeteringDevice &&dcMeters) { m_dcMeters = std::move(dcMeters); }
  const MeteringDevice &get_dcMeters() const { return m_dcMeters; }
  MeteringDevice &mutable_dcMeters() { return m_dcMeters; }

  void set_monitoringDevice(const MonitoringDevice &&monitoringDevice) {
    m_monitoringDevice = std::move(monitoringDevice);
  }
  const MonitoringDevice &get_monitoringDevice() const { return m_monitoringDevice; }
  MonitoringDevice &mutable_monitoringDevice() { return m_monitoringDevice; }

  void set_switchPositiveNegtive(const SwitchPositiveNegtive &&switchPositiveNegtive) {
    m_switchPositiveNegtive = std::move(switchPositiveNegtive);
  }
  const SwitchPositiveNegtive &get_switchPositiveNegtive() const { return m_switchPositiveNegtive; }
  SwitchPositiveNegtive &mutable_switchPositiveNegtive() { return m_switchPositiveNegtive; }

  void set_alarms(const std::map<std::string, Alarm> &&alarms) { m_alarms = std::move(alarms); }
  const std::map<std::string, Alarm> &get_alarms() const { return m_alarms; }
  std::map<std::string, Alarm> &mutable_alarms() { return m_alarms; }

  void set_circuits(const std::list<CircuitDevice> &&circuits) { m_circuits = std::move(circuits); }
  const std::list<CircuitDevice> &get_circuits() const { return m_circuits; }
  std::list<CircuitDevice> &mutable_circuits() { return m_circuits; }
  CircuitDevice &mutable_circuit() {
    m_circuits.emplace_back();
    return m_circuits.back();
  }
};

class RTCoreLogicalIdToDeviceConfig {
private:
  std::map<int, RTCoreMapEntry> m_circuitLoads;
  std::map<int, RTCoreMapEntry> m_dcMeters;
  std::map<int, RTCoreMapEntry> m_monitoringDevice;
  std::map<int, RTCoreMapEntry> m_switchPositiveNegtive;

public:
  RTCoreLogicalIdToDeviceConfig();
  ~RTCoreLogicalIdToDeviceConfig() { clear(); }
  RTCoreLogicalIdToDeviceConfig(const RTCoreLogicalIdToDeviceConfig &rhs);
  RTCoreLogicalIdToDeviceConfig(RTCoreLogicalIdToDeviceConfig &&rhs);
  RTCoreLogicalIdToDeviceConfig &operator=(const RTCoreLogicalIdToDeviceConfig &rhs);
  RTCoreLogicalIdToDeviceConfig &operator=(RTCoreLogicalIdToDeviceConfig &&rhs);

  void set_circuitLoads(const std::map<int, RTCoreMapEntry> &&circuitLoads) {
    m_circuitLoads = std::move(circuitLoads);
  }
  const std::map<int, RTCoreMapEntry> &get_circuitLoads() const { return m_circuitLoads; }
  std::map<int, RTCoreMapEntry> &mutable_circuitLoads() { return m_circuitLoads; }

  void set_dcMeters(const std::map<int, RTCoreMapEntry> &&dcMeters) { m_dcMeters = std::move(dcMeters); }
  const std::map<int, RTCoreMapEntry> &get_dcMeters() const { return m_dcMeters; }
  std::map<int, RTCoreMapEntry> &mutable_dcMeters() { return m_dcMeters; }

  void set_monitoringDevice(const std::map<int, RTCoreMapEntry> &&monitoringDevice) {
    m_monitoringDevice = std::move(monitoringDevice);
  }
  const std::map<int, RTCoreMapEntry> &get_monitoringDevice() const { return m_monitoringDevice; }
  std::map<int, RTCoreMapEntry> &mutable_monitoringDevice() { return m_monitoringDevice; }

  void set_switchPositiveNegtive(const std::map<int, RTCoreMapEntry> &&switchPositiveNegtive) {
    m_switchPositiveNegtive = std::move(switchPositiveNegtive);
  }
  const std::map<int, RTCoreMapEntry> &get_switchPositiveNegtive() const { return m_switchPositiveNegtive; }
  std::map<int, RTCoreMapEntry> &mutable_switchPositiveNegtive() { return m_switchPositiveNegtive; }

  void clear() {
    m_circuitLoads.clear();
    m_dcMeters.clear();
    m_monitoringDevice.clear();
    m_switchPositiveNegtive.clear();
  }
};

class CZoneRawConfig {
private:
  uint32_t m_type;
  uint32_t m_length;
  uint32_t m_sizeOfData;
  std::vector<std::byte> m_contents;

public:
  CZoneRawConfig();
  ~CZoneRawConfig() { clear(); }
  CZoneRawConfig(const CZoneRawConfig &rhs);
  CZoneRawConfig(CZoneRawConfig &&rhs);
  CZoneRawConfig &operator=(const CZoneRawConfig &rhs);
  CZoneRawConfig &operator=(CZoneRawConfig &&rhs);

  void set_type(uint32_t type) { m_type = type; }
  uint32_t get_type() const { return m_type; }

  void set_length(uint32_t length) { m_length = length; }
  uint32_t get_length() const { return m_length; }

  void set_sizeOfData(uint32_t size) { m_sizeOfData = size; }
  uint32_t get_sizeOfData() const { return m_sizeOfData; }

  void set_contents(const std::vector<std::byte> &contents) { m_contents = contents; }
  const std::vector<std::byte> &get_contents() const { return m_contents; }
  std::vector<std::byte> &mutable_contents() { return m_contents; }

  void clear() { m_contents.clear(); }
};

class ConfigResult {
public:
  enum eConfigResultStatus : int { eOk = 0, eNotReady = 1 };
  static std::string to_string(eConfigResultStatus c) {
    switch (c) {
    case eConfigResultStatus::eOk: return "OK";
    case eConfigResultStatus::eNotReady: return "NotReady";
    }
    return "unknown";
  }

private:
  std::list<Alarm> m_alarms;
  std::list<MeteringDevice> m_dcs;
  std::list<MeteringDevice> m_acs;
  std::list<MonitoringDevice> m_pressures;
  std::list<MonitoringDevice> m_tanks;
  std::list<MonitoringDevice> m_temperatures;
  std::list<ACMainDevice> m_acMains;
  std::list<InverterChargerDevice> m_inverterChargers;
  std::list<HVACDevice> m_hvacs;
  std::list<ZipdeeAwningDevice> m_zipdeeAwnings;
  std::list<ThirdPartyGeneratorDevice> m_thirdPartyGenerators;
  std::list<TyrePressureDevice> m_tyrePressures;
  std::list<AudioStereoDevice> m_audioStereos;
  std::list<ShoreFuseDevice> m_shoreFuses;
  std::list<CircuitDevice> m_circuits;
  std::list<CircuitDevice> m_modes;
  std::list<FantasticFanDevice> m_fantasticFans;
  std::list<ScreenConfigPageImageItem> m_screenConfigPageImageItems;
  std::list<ScreenConfigPageGridItem> m_screenConfigPageGridItems;
  std::list<ScreenConfigPageImage> m_screenConfigPageImages;
  std::list<ScreenConfigPage> m_screenConfigPages;
  std::list<ScreenConfigMode> m_screenConfigModes;
  std::list<ScreenConfig> m_screenConfigs;
  std::list<FavouritesInfo> m_favouritesModes;
  std::list<FavouritesInfo> m_favouritesControls;
  std::list<FavouritesInfo> m_favouritesMonitorings;
  std::list<FavouritesInfo> m_favouritesAlarms;
  std::list<FavouritesInfo> m_favouritesACMains;
  std::list<FavouritesInfo> m_favouritesInverterChargers;
  std::list<FavouritesInfo> m_favouritesBoatViews;
  std::list<Device> m_devices;
  std::list<GNSSDevice> m_gnss;
  std::list<EngineDevice> m_engines;
  std::list<UiRelationshipMsg> m_uiRelationships;
  std::list<BinaryLogicStateMsg> m_binaryLogicStates;
  CZoneRawConfig m_displayList;
  RTCoreLogicalIdToDeviceConfig m_rtCoreLogicalIdToDeviceConfig;
  eConfigResultStatus m_status;

public:
  void clear() {
    m_alarms.clear();
    m_dcs.clear();
    m_acs.clear();
    m_pressures.clear();
    m_tanks.clear();
    m_temperatures.clear();
    m_acMains.clear();
    m_inverterChargers.clear();
    m_hvacs.clear();
    m_zipdeeAwnings.clear();
    m_thirdPartyGenerators.clear();
    m_tyrePressures.clear();
    m_audioStereos.clear();
    m_shoreFuses.clear();
    m_circuits.clear();
    m_modes.clear();
    m_fantasticFans.clear();
    m_screenConfigPageImageItems.clear();
    m_screenConfigPageGridItems.clear();
    m_screenConfigPageImages.clear();
    m_screenConfigPages.clear();
    m_screenConfigModes.clear();
    m_screenConfigs.clear();
    m_favouritesModes.clear();
    m_favouritesControls.clear();
    m_favouritesMonitorings.clear();
    m_favouritesAlarms.clear();
    m_favouritesACMains.clear();
    m_favouritesInverterChargers.clear();
    m_favouritesBoatViews.clear();
    m_devices.clear();
    m_gnss.clear();
    m_engines.clear();
    m_uiRelationships.clear();
    m_binaryLogicStates.clear();
    m_displayList.clear();
    m_rtCoreLogicalIdToDeviceConfig.clear();
  }
  void set_status(eConfigResultStatus s) { m_status = s; };
  eConfigResultStatus get_status() const { return m_status; }

  void set_displayList(const CZoneRawConfig &displayList) { m_displayList = displayList; }
  const CZoneRawConfig &get_displayList() const { return m_displayList; }
  CZoneRawConfig &mutable_displayList() { return m_displayList; }

  void set_rtCoreLogicalIdToDeviceConfig(const RTCoreLogicalIdToDeviceConfig &config) {
    m_rtCoreLogicalIdToDeviceConfig = config;
  }
  const RTCoreLogicalIdToDeviceConfig &get_rtCoreLogicalIdToDeviceConfig() const {
    return m_rtCoreLogicalIdToDeviceConfig;
  }
  RTCoreLogicalIdToDeviceConfig &mutable_rtCoreLogicalIdToDeviceConfig() { return m_rtCoreLogicalIdToDeviceConfig; }

  auto &add_mutable_alarms() {
    m_alarms.emplace_back();
    return m_alarms.back();
  }
  auto &add_mutable_dcs() {
    m_dcs.emplace_back();
    return m_dcs.back();
  }
  auto &add_mutable_acs() {
    m_acs.emplace_back();
    return m_acs.back();
  }
  auto &add_mutable_pressures() {
    m_pressures.emplace_back();
    return m_pressures.back();
  }
  auto &add_mutable_tanks() {
    m_tanks.emplace_back();
    return m_tanks.back();
  }
  auto &add_mutable_temperatures() {
    m_temperatures.emplace_back();
    return m_temperatures.back();
  }
  auto &add_mutable_acMains() {
    m_acMains.emplace_back();
    return m_acMains.back();
  }
  auto &add_mutable_inverterChargers() {
    m_inverterChargers.emplace_back();
    return m_inverterChargers.back();
  }
  auto &add_mutable_hvacs() {
    m_hvacs.emplace_back();
    return m_hvacs.back();
  }
  auto &add_mutable_zipdeeAwnings() {
    m_zipdeeAwnings.emplace_back();
    return m_zipdeeAwnings.back();
  }
  auto &add_mutable_thirdPartyGenerators() {
    m_thirdPartyGenerators.emplace_back();
    return m_thirdPartyGenerators.back();
  }
  auto &add_mutable_tyrePressures() {
    m_tyrePressures.emplace_back();
    return m_tyrePressures.back();
  }
  auto &add_mutable_audioStereos() {
    m_audioStereos.emplace_back();
    return m_audioStereos.back();
  }
  auto &add_mutable_shoreFuses() {
    m_shoreFuses.emplace_back();
    return m_shoreFuses.back();
  }
  auto &add_mutable_circuits() {
    m_circuits.emplace_back();
    return m_circuits.back();
  }
  auto &add_mutable_modes() {
    m_modes.emplace_back();
    return m_modes.back();
  }
  auto &add_mutable_fantasticFans() {
    m_fantasticFans.emplace_back();
    return m_fantasticFans.back();
  }
  auto &add_mutable_screenConfigPageImageItems() {
    m_screenConfigPageImageItems.emplace_back();
    return m_screenConfigPageImageItems.back();
  }
  auto &add_mutable_screenConfigPageGridItems() {
    m_screenConfigPageGridItems.emplace_back();
    return m_screenConfigPageGridItems.back();
  }
  auto &add_mutable_screenConfigPageImages() {
    m_screenConfigPageImages.emplace_back();
    return m_screenConfigPageImages.back();
  }
  auto &add_mutable_screenConfigPages() {
    m_screenConfigPages.emplace_back();
    return m_screenConfigPages.back();
  }
  auto &add_mutable_screenConfigModes() {
    m_screenConfigModes.emplace_back();
    return m_screenConfigModes.back();
  }
  auto &add_mutable_screenConfigs() {
    m_screenConfigs.emplace_back();
    return m_screenConfigs.back();
  }
  auto &add_mutable_favouritesModes() {
    m_favouritesModes.emplace_back();
    return m_favouritesModes.back();
  }
  auto &add_mutable_favouritesControls() {
    m_favouritesControls.emplace_back();
    return m_favouritesControls.back();
  }
  auto &add_mutable_favouritesMonitorings() {
    m_favouritesMonitorings.emplace_back();
    return m_favouritesMonitorings.back();
  }
  auto &add_mutable_favouritesAlarms() {
    m_favouritesAlarms.emplace_back();
    return m_favouritesAlarms.back();
  }
  auto &add_mutable_favouritesACMains() {
    m_favouritesACMains.emplace_back();
    return m_favouritesACMains.back();
  }
  auto &add_mutable_favouritesInverterChargers() {
    m_favouritesInverterChargers.emplace_back();
    return m_favouritesInverterChargers.back();
  }
  auto &add_mutable_favouritesBoatViews() {
    m_favouritesBoatViews.emplace_back();
    return m_favouritesBoatViews.back();
  }
  auto &add_mutable_devices() {
    m_devices.emplace_back();
    return m_devices.back();
  }
  auto &add_mutable_gnss() {
    m_gnss.emplace_back();
    return m_gnss.back();
  }
  auto &add_mutable_engines() {
    m_engines.emplace_back();
    return m_engines.back();
  }
  auto &add_mutable_uiRelationships() {
    m_uiRelationships.emplace_back();
    return m_uiRelationships.back();
  }
  auto &add_mutable_binaryLogicStates() {
    m_binaryLogicStates.emplace_back();
    return m_binaryLogicStates.back();
  }

  const auto &get_alarms() const { return m_alarms; }
  const auto &get_dcs() const { return m_dcs; }
  const auto &get_acs() const { return m_acs; }
  const auto &get_pressures() const { return m_pressures; }
  const auto &get_tanks() const { return m_tanks; }
  const auto &get_temperatures() const { return m_temperatures; }
  const auto &get_acMains() const { return m_acMains; }
  const auto &get_inverterChargers() const { return m_inverterChargers; }
  const auto &get_hvacs() const { return m_hvacs; }
  const auto &get_zipdeeAwnings() const { return m_zipdeeAwnings; }
  const auto &get_thirdPartyGenerators() const { return m_thirdPartyGenerators; }
  const auto &get_tyrePressures() const { return m_tyrePressures; }
  const auto &get_audioStereos() const { return m_audioStereos; }
  const auto &get_shoreFuses() const { return m_shoreFuses; }
  const auto &get_circuits() const { return m_circuits; }
  const auto &get_modes() const { return m_modes; }
  const auto &get_fantasticFans() const { return m_fantasticFans; }
  const auto &get_screenConfigPageImageItems() const { return m_screenConfigPageImageItems; }
  const auto &get_screenConfigPageGridItems() const { return m_screenConfigPageGridItems; }
  const auto &get_screenConfigPageImages() const { return m_screenConfigPageImages; }
  const auto &get_screenConfigPages() const { return m_screenConfigPages; }
  const auto &get_screenConfigModes() const { return m_screenConfigModes; }
  const auto &get_screenConfigs() const { return m_screenConfigs; }
  const auto &get_favouritesModes() const { return m_favouritesModes; }
  const auto &get_favouritesControls() const { return m_favouritesControls; }
  const auto &get_favouritesMonitorings() const { return m_favouritesMonitorings; }
  const auto &get_favouritesAlarms() const { return m_favouritesAlarms; }
  const auto &get_favouritesACMains() const { return m_favouritesACMains; }
  const auto &get_favouritesInverterChargers() const { return m_favouritesInverterChargers; }
  const auto &get_favouritesBoatViews() const { return m_favouritesBoatViews; }
  const auto &get_devices() const { return m_devices; }
  const auto &get_gnss() const { return m_gnss; }
  const auto &get_engines() const { return m_engines; }
  const auto &get_uiRelationships() const { return m_uiRelationships; }
  const auto &get_binaryLogicStates() const { return m_binaryLogicStates; }
  json tojson() const;
};

void to_json(nlohmann::json &j, const Categories &c);
void to_json(nlohmann::json &j, const CategoryItem &c);
void to_json(nlohmann::json &j, const AlarmLimit &c);
void to_json(nlohmann::json &j, const Instance &c);
void to_json(nlohmann::json &j, const Alarm &c);
void to_json(nlohmann::json &j, const MeteringDevice &c);
void to_json(nlohmann::json &j, const MonitoringDevice &c);
void to_json(nlohmann::json &j, const DataId &c);
void to_json(nlohmann::json &j, const ACMainDevice &c);
void to_json(nlohmann::json &j, const ACMainContactorDevice &c);
void to_json(nlohmann::json &j, const ACMainLoadGroupDevice &c);
void to_json(nlohmann::json &j, const InverterChargerDevice &c);
void to_json(nlohmann::json &j, const HVACDevice &c);
void to_json(nlohmann::json &j, const ThirdPartyGeneratorDevice &c);
void to_json(nlohmann::json &j, const ZipdeeAwningDevice &c);
void to_json(nlohmann::json &j, const BinarySignalBitAddress &c);
void to_json(nlohmann::json &j, const TyrePressureDevice &c);
void to_json(nlohmann::json &j, const AudioStereoDevice &c);
void to_json(nlohmann::json &j, const ShoreFuseDevice &c);
void to_json(nlohmann::json &j, const CircuitDevice &c);
void to_json(nlohmann::json &j, const CircuitLoad &c);
void to_json(nlohmann::json &j, const FantasticFanDevice &c);
void to_json(nlohmann::json &j, const ScreenConfigMode &c);
void to_json(nlohmann::json &j, const ScreenConfigPageImageItem &c);
void to_json(nlohmann::json &j, const ScreenConfigHeader &c);
void to_json(nlohmann::json &j, const ScreenConfigPageGridItem &c);
void to_json(nlohmann::json &j, const ScreenConfigPageImage &c);
void to_json(nlohmann::json &j, const ScreenConfigPage &c);
void to_json(nlohmann::json &j, const ScreenConfig &c);
void to_json(nlohmann::json &j, const FavouritesInfo &c);
void to_json(nlohmann::json &j, const Device &c);
void to_json(nlohmann::json &j, const GNSSDevice &c);
void to_json(nlohmann::json &j, const EngineDevice &c);
void to_json(nlohmann::json &j, const UiRelationshipMsg &c);
void to_json(nlohmann::json &j, const BinaryLogicStateMsg &c);
void to_json(nlohmann::json &j, const Event &c);
