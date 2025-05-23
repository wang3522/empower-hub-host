#pragma once

#include "utils/common.h"

#include <tCZoneInterface.h>

#include <list>
#include <map>
#include <string>
#include <unordered_map>
#include <vector>

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
};

class CategoryRequest {
public:
  enum eCategoryType : int { eCategoriesAll = 0 };

  CategoryRequest();
  CategoryRequest(const CategoryRequest &) = delete;
  CategoryRequest(CategoryRequest &&) = delete;
  CategoryRequest &operator=(const CategoryRequest &) = delete;
  CategoryRequest &operator=(CategoryRequest &&) = delete;

private:
  eCategoryType m_type;
  std::string m_token;
};

class ControlRequest {
public:
  enum eControlType : int {
    eActivate = 0,
    eRelease = 1,
    ePing = 2,
    eSetAbsolute = 3,
  };
  enum eThrowType : int {
    eDoubleThrow = 0,
    eSingleThrow = 1,
  };
  enum eButtonInfoType : int {
    eButtonInfo0 = 0,
    eButtonInfo1 = 1,
  };

  ControlRequest();
  ControlRequest(const ControlRequest &) = delete;
  ControlRequest(ControlRequest &&) = delete;
  ControlRequest &operator=(const ControlRequest &) = delete;
  ControlRequest &operator=(ControlRequest &&) = delete;

private:
  eControlType m_type;
  eThrowType m_throwType;
  eButtonInfoType m_buttonType;
  uint32_t m_id;
  uint32_t m_value;
  std::string m_token;
};

class ControlTypeValueRequest {
public:
  enum eHVACType : int {
    eOperationMode = 0,
    eFanSpeed = 1,
    eSetTemperature = 2,
  };
  enum eFantasticFanType : int {
    eDirectionForward = 0,
    eDirectionReverse = 1,
    eLidOpen = 2,
    eLidClose = 3,
    eSpeed = 4,
  };
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
  enum eAwningType : int {
    eOpen = 0,
    eClose = 1,
    eTitleLeft = 2,
    eTitleRight = 3,
  };
  enum eShoreFuseType : int { eControl = 0 };
  enum eThirdPartyGeneratorType : int { eStart = 0, eStop = 1 };

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
};

class CircuitLoad {
public:
  enum eControlType : int {
    eSetOutput = 0,
    eLimitOneDirection = 1,
    eLimitBothDirections = 2,
    eSetAndLimit = 3,
  };

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
  enum eConfirmType : int {
    eConfirmNone = 0,
    eConfirmOn = 1,
    eConfirmOff = 2,
    eConfirmOnOff = 3,
  };
  enum eCircuitType : int {
    eCircuit = 0,
    eModeGroup1 = 1,
    eModeGroup2 = 2,
    eModeGroup3 = 3,
    eModeGroupExclusive = 4,
  };
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
public:
  std::list<CategoryItem> _items;
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
  enum eSeverityType : int {
    eSeverityCritical = 0,
    eSeverityImportant = 1,
    eSeverityStandard = 2,
    eSeverityWarning = 3,
    eSeveritySIO = 4,
    eSeverityNone = 5,
  };
  enum eStateType : int {
    eStateDisabled = 0,
    eStateEnabled = 1,
    eStateAcknowledged = 2,
  };

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
  enum eACLine : int {
    eLine1 = 0,
    eLine2 = 1,
    eLine3 = 2,
  };
  enum eACType : int {
    eUnknown = 0,
    eGenerator = 1,
    eShorePower = 2,
    eInverter = 3,
    eParallel = 4,
    eCharger = 5,
    eOutlet = 6,
  };
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  eACLine _line;
  bool _output;
  uint32_t _nominalVoltage;
  uint32_t _nominalFrequency;
  uint32_t _address;
  uint32_t _capacity;
  float _warningLow;
  float _warningHigh;
  AlarmLimit _lowLimit;
  AlarmLimit _veryLowLimit;
  AlarmLimit _highLimit;
  AlarmLimit _veryHighLimit;
  AlarmLimit _frequency;
  AlarmLimit _lowVoltage;
  AlarmLimit _veryLowVoltage;
  AlarmLimit _highVoltage;
  bool _canResetCapacity;
  eDCType _dcType;
  bool _showVoltage;
  bool _showCurrent;
  bool _showStateOfCharge;
  bool _showTemperature;
  bool _showTimeOfRemaining;
  eACType _acType;
};

class MonitoringType {
public:
  enum eTankType : int { eFuel = 0, eFreshWater = 1, eWasteWater = 2, eLiveWell = 3, eOil = 4, eBlackWater = 5 };

  enum ePressureType : int { eAtmospheric = 0, eWater = 1, eSteam = 2, eCompressedAir = 3, eHydraulic = 4 };

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
};

class MonitoringDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  MonitoringType::eTankType _tankType;
  MonitoringType::ePressureType _pressureType;
  MonitoringType::eTemperatureType _temperatureType;
  DataId _circuitId;
  CircuitDevice::eSwitchType _switchType;
  CircuitDevice::eConfirmType _confirmDialog;
  std::string _circuitNameUTF8;
  bool _highTemperature;
  bool _atmosphericPressure;
  AlarmLimit _veryLowLimit;
  AlarmLimit _lowLimit;
  AlarmLimit _highLimit;
  AlarmLimit _veryHighLimit;
  float _tankCapacity;
  uint32_t _address;
};

class ACMainContactorDevice {
public:
  enum eACInputType : int {
    eShipPower = 0,
    eShorePower = 1,
    eInverter = 2,
    eParallel = 3,
  };
  uint32_t _systemStateId;
  std::string _nameUTF8;
  DataId _contactorId;
  DataId _contactorToggleId;
  DataId _ac1Id;
  DataId _ac2Id;
  DataId _ac3Id;
  uint32_t _displayIndex;
  uint32_t _loadGroupIndex;
  uint32_t _loadGroupParallelIndex;
  bool _isParallel;
  ACMainContactorDevice::eACInputType _acInputType;
};

class ACMainLoadGroupDevice {
public:
  std::string _nameUTF8;
  uint32_t _loadGroupIndex;
};

class ACMainDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  uint32_t _dipswitch;
  std::list<ACMainContactorDevice> _contactors;
  std::list<ACMainLoadGroupDevice> _loadGroups;
};

class InverterChargerDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  uint32_t _model;
  uint32_t _type;
  uint32_t _subType;
  Instance _inverterInstance;
  DataId _inverterACId;
  DataId _inverterCircuitId;
  DataId _inverterToggleCircuitId;
  Instance _chargerInstance;
  DataId _chargerACId;
  DataId _chargerCircuitId;
  DataId _chargerToggleCircuitId;
  DataId _batteryBank1Id;
  DataId _batteryBank2Id;
  DataId _batteryBank3Id;
  uint32_t _positionColumn;
  uint32_t _positionRow;
  bool _clustered;
  bool _primary;
  uint32_t _primaryPhase;
  uint32_t _deviceInstance;
  uint32_t _dipswitch;
  uint32_t _channelIndex;
};

class HVACDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  DataId _operatingModeId;
  DataId _fanModeId;
  DataId _fanSpeedId;
  DataId _setpointTemperatureId;
  DataId _operatingModeToggleId;
  DataId _fanModeToggleId;
  DataId _fanSpeedToggleId;
  DataId _setpointTemperatureToggleId;
  DataId _temperatureMonitoringId;
  uint32_t _fanSpeedCount;
  uint32_t _operatingModesMask;
  uint32_t _model;
  Instance _temperatureInstance;
  float _setpointTemperatureMin;
  float _setpointTemperatureMax;
  uint32_t _fanSpeedOffModesMask;
  uint32_t _fanSpeedAutoModesMask;
  uint32_t _fanSpeedManualModesMask;
};

class CZoneRawConfig {
public:
  uint32_t _type;
  uint32_t _length;
  uint32_t _sizeOfData;
  std::vector<std::byte> _contents;
  void clear() { _contents.clear(); }
};

class BinarySignalBitAddress {
public:
  uint32_t _dataType;
  uint32_t _dipswitch;
  uint32_t _bit;
};

class ZipdeeAwningDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  DataId _openId;
  DataId _closeId;
  DataId _tiltLeftId;
  DataId _tiltRightId;
  std::list<BinarySignalBitAddress> _binarySignals;
};

class ThirdPartyGeneratorDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  DataId _startControlId;
  DataId _stopControlId;
  Instance _associatedAcMetersInstance;
  DataId _acMeterLine1Id;
  DataId _acMeterLine2Id;
  DataId _acMeterLine3Id;
};

class TyrePressureDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  uint32_t _numberOfAxles;
  uint32_t _tyresAxle1;
  uint32_t _tyresAxle2;
  uint32_t _tyresAxle3;
  uint32_t _tyresAxle4;
  uint32_t _spareAxle;
  std::list<Instance> _tyreInstances;
  std::list<Instance> _tyreSpareInstances;
};

class AudioStereoDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  bool _muteEnabled;
  std::list<DataId> _circuitIds;
};

class ShoreFuseDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  DataId _shoreFuseControlId;
};

class FantasticFanDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  DataId _directionForwardCircuitId;
  DataId _directionReverseCircuitId;
  DataId _lidOpenCircuitId;
  DataId _lidCloseCircuitId;
  DataId _fanCircuitId;
};

class ScreenConfigHeader {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  uint32_t _targetDisplayType;
  uint32_t _targetId;
  uint32_t _confirmationType;
  uint32_t _smoothStart;
  uint32_t _index;
  uint32_t _parentIndex;
  uint32_t _controlId;
};

class ScreenConfigPageImageItem {
public:
  ScreenConfigHeader _header;
  float _locationX;
  float _locationY;
  float _targetX;
  float _targetY;
  uint32_t _icon;
  std::string _name;
  bool _hideWhenOff;
};

class ScreenConfigPageGridItem {
public:
  ScreenConfigHeader _header;
  uint32_t _gridX;
  uint32_t _gridY;
  float _targetX;
  float _targetY;
  float _targetWidth;
  float _targetHeight;
  int _icon;
  std::string _name;
  int _columnSpan;
  int _rowSpan;
  int _doubleThrowType;
};

class ScreenConfigPageImage {
public:
  ScreenConfigHeader _header;
  uint32_t _gridX;
  uint32_t _gridY;
  uint32_t _gridWidth;
  uint32_t _gridHeight;
  float _sourceWidth;
  float _sourceHeight;
  float _targetX;
  float _targetY;
  float _targetWidth;
  float _targetHeight;
  std::string _fileName;
  uint32_t _backgroundColourR;
  uint32_t _backgroundColourG;
  uint32_t _backgroundColourB;
  uint32_t _showBackground;
  uint32_t _cropToFit;
};

class ScreenConfigPage {
public:
  ScreenConfigHeader _header;
};

class ScreenConfigMode {
public:
  ScreenConfigHeader _header;
  std::string _name;
};

class ScreenConfig {
public:
  ScreenConfigHeader _header;
  uint32_t _gridWidth;
  uint32_t _gridHeight;
  uint32_t _landscape;
  std::string _displayName;
  std::string _relativePath;
};

class FavouritesInfo {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  uint32_t _targetDisplayType;
  uint32_t _targetId;
  uint32_t _x;
  uint32_t _y;
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
  ConfigRequest::eConfigType _displayType;
  std::string _nameUTF8;
  uint32_t _dipswitch;
  uint32_t _sourceAddress;
  bool _conflict;
  Device::eDeviceType _deviceType;
  bool _valid;
  bool _transient;
  std::string _version;
};

class GNSSDevice {
public:
  ConfigRequest::eConfigType _displayType;
  uint32_t _id;
  std::string _nameUTF8;
  Instance _instance;
  bool _isExternal;
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
  enum eRelationshipType : int {
    eNormal = 0,
    eDuplicates = 1,
  };

  ConfigRequest::eConfigType _displaytype;
  uint32_t _id;
  eItemType _primarytype;
  eItemType _secondarytype;
  uint32_t _primaryid;
  uint32_t _secondaryid;
  eRelationshipType _relationshiptype;
  uint32_t _primaryconfigaddress;
  uint32_t _secondaryconfigaddress;
  uint32_t _primarychannelindex;
  uint32_t _secondarychannelindex;
};

class BinaryLogicStateMsg {
public:
  ConfigRequest::eConfigType _displaytype;
  uint32_t _id;
  uint32_t _address;
  std::string _nameutf8;
};

class SwitchPositiveNegtive {
public:
  enum eSwitchPositiveNegtiveMode : int {
    eSwitchBatteryPositive = 0,
    eSwitchBatteryNegtive = 1,
  };
  uint32_t _channelAddress;
  uint32_t _channel;
  eSwitchPositiveNegtiveMode _mode;
  uint32_t _binaryStatusIndex;
};

class RTCoreMapEntry {
public:
  ConfigRequest::eConfigType _displaytype;
  CircuitLoad _circuitLoads;
  MeteringDevice _dcMeters;
  MonitoringDevice _monitoringDevice;
  SwitchPositiveNegtive _switchPositiveNegtive;
  std::map<std::string, Alarm> _alarms;
  std::list<CircuitDevice> _circuits;
};

class RTCoreLogicalIdToDeviceConfig {
public:
  std::map<int, RTCoreMapEntry> _circuitLoads;
  std::map<int, RTCoreMapEntry> _dcMeters;
  std::map<int, RTCoreMapEntry> _monitoringDevice;
  std::map<int, RTCoreMapEntry> _switchPositiveNegtive;
  void clear() {
    _circuitLoads.clear();
    _dcMeters.clear();
    _monitoringDevice.clear();
    _switchPositiveNegtive.clear();
  }
};

class ConfigResult {
private:
  /* data */
public:
  enum eConfigResultStatus : int { eOk = 0, eNotReady = 1 };
  void clear() {
    _alarms.clear();
    _dcs.clear();
    _acs.clear();
    _pressures.clear();
    _tanks.clear();
    _temperatures.clear();
    _acMains.clear();
    _inverterChargers.clear();
    _hvacs.clear();
    _zipdeeAwnings.clear();
    _thirdPartyGenerators.clear();
    _tyrePressures.clear();
    _audioStereos.clear();
    _shoreFuses.clear();
    _circuits.clear();
    _modes.clear();
    _fantasticFans.clear();
    _screenConfigPageImageItems.clear();
    _screenConfigPageGridItems.clear();
    _screenConfigPageImages.clear();
    _screenConfigPages.clear();
    _screenConfigModes.clear();
    _screenConfigs.clear();
    _favouritesModes.clear();
    _favouritesControls.clear();
    _favouritesMonitorings.clear();
    _favouritesAlarms.clear();
    _favouritesACMains.clear();
    _favouritesInverterChargers.clear();
    _favouritesBoatViews.clear();
    _devices.clear();
    _gnss.clear();
    _engines.clear();
    _uiRelationships.clear();
    _binaryLogicStates.clear();
    _displayList.clear();
    _rtCoreLogicalIdToDeviceConfig.clear();
  }
  void set_status(eConfigResultStatus s) { _status = s; };
  std::list<Alarm> _alarms;
  std::list<MeteringDevice> _dcs;
  std::list<MeteringDevice> _acs;
  std::list<MonitoringDevice> _pressures;
  std::list<MonitoringDevice> _tanks;
  std::list<MonitoringDevice> _temperatures;
  std::list<ACMainDevice> _acMains;
  std::list<InverterChargerDevice> _inverterChargers;
  std::list<HVACDevice> _hvacs;
  std::list<ZipdeeAwningDevice> _zipdeeAwnings;
  std::list<ThirdPartyGeneratorDevice> _thirdPartyGenerators;
  std::list<TyrePressureDevice> _tyrePressures;
  std::list<AudioStereoDevice> _audioStereos;
  std::list<ShoreFuseDevice> _shoreFuses;
  std::list<CircuitDevice> _circuits;
  std::list<CircuitDevice> _modes;
  std::list<FantasticFanDevice> _fantasticFans;
  std::list<ScreenConfigPageImageItem> _screenConfigPageImageItems;
  std::list<ScreenConfigPageGridItem> _screenConfigPageGridItems;
  std::list<ScreenConfigPageImage> _screenConfigPageImages;
  std::list<ScreenConfigPage> _screenConfigPages;
  std::list<ScreenConfigMode> _screenConfigModes;
  std::list<ScreenConfig> _screenConfigs;
  std::list<FavouritesInfo> _favouritesModes;
  std::list<FavouritesInfo> _favouritesControls;
  std::list<FavouritesInfo> _favouritesMonitorings;
  std::list<FavouritesInfo> _favouritesAlarms;
  std::list<FavouritesInfo> _favouritesACMains;
  std::list<FavouritesInfo> _favouritesInverterChargers;
  std::list<FavouritesInfo> _favouritesBoatViews;
  std::list<Device> _devices;
  std::list<GNSSDevice> _gnss;
  std::list<EngineDevice> _engines;
  std::list<UiRelationshipMsg> _uiRelationships;
  std::list<BinaryLogicStateMsg> _binaryLogicStates;
  CZoneRawConfig _displayList;
  RTCoreLogicalIdToDeviceConfig _rtCoreLogicalIdToDeviceConfig;
  eConfigResultStatus _status;
};