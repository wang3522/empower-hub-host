#include "modules/czone/configdata.h"
#include <cstring>

Instance::Instance() : m_enabled(false), m_instance(0) {}

Instance::Instance(uint32_t i, bool e) : m_enabled(e), m_instance(i) {}

Instance::Instance(const Instance &rhs) : m_enabled(rhs.m_enabled), m_instance(rhs.m_instance) {}

Instance::Instance(Instance &&rhs) : m_enabled(rhs.m_enabled), m_instance(rhs.m_instance) {}

Instance &Instance::operator=(const Instance &rhs) {
  if (this != &rhs) {
    m_enabled = rhs.m_enabled;
    m_instance = rhs.m_instance;
  }
  return *this;
}

Instance &Instance::operator=(Instance &&rhs) {
  if (this != &rhs) {
    m_enabled = rhs.m_enabled;
    m_instance = rhs.m_instance;
  }
  return *this;
}

CategoryRequest::CategoryRequest() : m_type(CategoryRequest::eCategoryType::eCategoriesAll), m_token() {}

ControlRequest::ControlRequest()
    : m_type(ControlRequest::eControlType::eActivate),
      m_throwType(ControlRequest::eThrowType::eDoubleThrow),
      m_buttonType(ControlRequest::eButtonInfoType::eButtonInfo0),
      m_id(0),
      m_value(0),
      m_token() {}

ControlTypeValueRequest::ControlTypeValueRequest() : m_instance(0), m_type(0), m_value(0), m_token() {}

ConfigRequest::ConfigRequest(eConfigType type) : m_type(type), m_token(), m_parentId(0), m_flags(0), m_subType(0) {}

DataId::DataId() : m_enabled(false), m_id(0) {}

DataId::DataId(uint32_t id, bool enable) : m_enabled(enable), m_id(id) {}

DataId::DataId(const DataId &rhs) : m_enabled(rhs.m_enabled), m_id(rhs.m_id) {}

DataId::DataId(DataId &&rhs) : m_enabled(rhs.m_enabled), m_id(rhs.m_id) {}

DataId &DataId::operator=(const DataId &rhs) {
  if (this != &rhs) {
    m_enabled = rhs.m_enabled;
    m_id = rhs.m_id;
  }
  return *this;
}

DataId &DataId::operator=(DataId &&rhs) {
  if (this != &rhs) {
    m_enabled = rhs.m_enabled;
    m_id = rhs.m_id;
  }
  return *this;
}

CategoryItem::CategoryItem() : m_nameUTF8(), m_enabled(false), m_index(0) {}

CategoryItem::CategoryItem(const std::string &name, bool enabled, uint32_t index)
    : m_nameUTF8(name), m_enabled(enabled), m_index(index) {}

CategoryItem::CategoryItem(const std::string &name, bool enabled) : m_nameUTF8(name), m_enabled(enabled), m_index(0) {}

CategoryItem::CategoryItem(const CategoryItem &rhs)
    : m_nameUTF8(rhs.m_nameUTF8), m_enabled(rhs.m_enabled), m_index(rhs.m_index) {}

CategoryItem::CategoryItem(CategoryItem &&rhs)
    : m_nameUTF8(std::move(rhs.m_nameUTF8)), m_enabled(rhs.m_enabled), m_index(rhs.m_index) {}

CategoryItem &CategoryItem::operator=(const CategoryItem &rhs) {
  if (this != &rhs) {
    m_nameUTF8 = rhs.m_nameUTF8;
    m_enabled = rhs.m_enabled;
    m_index = rhs.m_index;
  }
  return *this;
}

CategoryItem &CategoryItem::operator=(CategoryItem &&rhs) {
  if (this != &rhs) {
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_enabled = rhs.m_enabled;
    m_index = rhs.m_index;
  }
  return *this;
}

CircuitLoad::CircuitLoad()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_id(0),
      m_nameUTF8(),
      m_channelAddress(0),
      m_fuseLevel(0.0f),
      m_runningCurrent(0.0f),
      m_systemOnCurrent(0.0f),
      m_forceAcknowledgeOn(false),
      m_level(0),
      m_controlType(CircuitLoad::eControlType::eSetOutput),
      m_isSwitchedModule(false) {}

CircuitLoad::CircuitLoad(const CircuitLoad &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_channelAddress(rhs.m_channelAddress),
      m_fuseLevel(rhs.m_fuseLevel),
      m_runningCurrent(rhs.m_runningCurrent),
      m_systemOnCurrent(rhs.m_systemOnCurrent),
      m_forceAcknowledgeOn(rhs.m_forceAcknowledgeOn),
      m_level(rhs.m_level),
      m_controlType(rhs.m_controlType),
      m_isSwitchedModule(rhs.m_isSwitchedModule) {}

CircuitLoad::CircuitLoad(CircuitLoad &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_channelAddress(rhs.m_channelAddress),
      m_fuseLevel(rhs.m_fuseLevel),
      m_runningCurrent(rhs.m_runningCurrent),
      m_systemOnCurrent(rhs.m_systemOnCurrent),
      m_forceAcknowledgeOn(rhs.m_forceAcknowledgeOn),
      m_level(rhs.m_level),
      m_controlType(rhs.m_controlType),
      m_isSwitchedModule(rhs.m_isSwitchedModule) {}

CircuitLoad &CircuitLoad::operator=(const CircuitLoad &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_channelAddress = rhs.m_channelAddress;
    m_fuseLevel = rhs.m_fuseLevel;
    m_runningCurrent = rhs.m_runningCurrent;
    m_systemOnCurrent = rhs.m_systemOnCurrent;
    m_forceAcknowledgeOn = rhs.m_forceAcknowledgeOn;
    m_level = rhs.m_level;
    m_controlType = rhs.m_controlType;
    m_isSwitchedModule = rhs.m_isSwitchedModule;
  }
  return *this;
}

CircuitLoad &CircuitLoad::operator=(CircuitLoad &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_channelAddress = rhs.m_channelAddress;
    m_fuseLevel = rhs.m_fuseLevel;
    m_runningCurrent = rhs.m_runningCurrent;
    m_systemOnCurrent = rhs.m_systemOnCurrent;
    m_forceAcknowledgeOn = rhs.m_forceAcknowledgeOn;
    m_level = rhs.m_level;
    m_controlType = rhs.m_controlType;
    m_isSwitchedModule = rhs.m_isSwitchedModule;
  }
  return *this;
}

CircuitDevice::CircuitDevice()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_id(std::make_pair(0, false)),
      m_nameUTF8(),
      m_singleThrowId(),
      m_sequentialNamesUTF8(),
      m_hasComplement(false),
      m_displayCategories(0),
      m_confirmDialog(CircuitDevice::eConfirmType::eConfirmNone),
      m_voltageSource(),
      m_circuitType(CircuitDevice::eCircuitType::eCircuit),
      m_switchType(CircuitDevice::eSwitchType::eNone),
      m_minLevel(0),
      m_maxLevel(0),
      m_nonVisibleCircuit(false),
      m_dimstep(0),
      m_step(0),
      m_dimmable(false),
      m_loadSmoothStart(0),
      m_sequentialStates(0),
      m_controlId(),
      m_circuitLoads(),
      m_categories(),
      m_dcCircuit(false),
      m_acCircuit(false),
      m_modeIcon(CircuitDevice::eModeIcon::eEntertainment),
      m_primaryCircuitId(),
      m_remoteVisibility(0),
      m_switchString(),
      m_systemsOnAnd(false) {}

CircuitDevice::CircuitDevice(const CircuitDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_singleThrowId(rhs.m_singleThrowId),
      m_sequentialNamesUTF8(rhs.m_sequentialNamesUTF8),
      m_hasComplement(rhs.m_hasComplement),
      m_displayCategories(rhs.m_displayCategories),
      m_confirmDialog(rhs.m_confirmDialog),
      m_voltageSource(rhs.m_voltageSource),
      m_circuitType(rhs.m_circuitType),
      m_switchType(rhs.m_switchType),
      m_minLevel(rhs.m_minLevel),
      m_maxLevel(rhs.m_maxLevel),
      m_nonVisibleCircuit(rhs.m_nonVisibleCircuit),
      m_dimstep(rhs.m_dimstep),
      m_step(rhs.m_step),
      m_dimmable(rhs.m_dimmable),
      m_loadSmoothStart(rhs.m_loadSmoothStart),
      m_sequentialStates(rhs.m_sequentialStates),
      m_controlId(rhs.m_controlId),
      m_circuitLoads(rhs.m_circuitLoads),
      m_categories(rhs.m_categories),
      m_dcCircuit(rhs.m_dcCircuit),
      m_acCircuit(rhs.m_acCircuit),
      m_modeIcon(rhs.m_modeIcon),
      m_primaryCircuitId(rhs.m_primaryCircuitId),
      m_remoteVisibility(rhs.m_remoteVisibility),
      m_switchString(rhs.m_switchString),
      m_systemsOnAnd(rhs.m_systemsOnAnd) {}

CircuitDevice::CircuitDevice(CircuitDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(std::move(rhs.m_id)),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_singleThrowId(std::move(rhs.m_singleThrowId)),
      m_sequentialNamesUTF8(std::move(rhs.m_sequentialNamesUTF8)),
      m_hasComplement(rhs.m_hasComplement),
      m_displayCategories(rhs.m_displayCategories),
      m_confirmDialog(rhs.m_confirmDialog),
      m_voltageSource(std::move(rhs.m_voltageSource)),
      m_circuitType(rhs.m_circuitType),
      m_switchType(rhs.m_switchType),
      m_minLevel(rhs.m_minLevel),
      m_maxLevel(rhs.m_maxLevel),
      m_nonVisibleCircuit(rhs.m_nonVisibleCircuit),
      m_dimstep(rhs.m_dimstep),
      m_step(rhs.m_step),
      m_dimmable(rhs.m_dimmable),
      m_loadSmoothStart(rhs.m_loadSmoothStart),
      m_sequentialStates(rhs.m_sequentialStates),
      m_controlId(rhs.m_controlId),
      m_circuitLoads(std::move(rhs.m_circuitLoads)),
      m_categories(std::move(rhs.m_categories)),
      m_dcCircuit(rhs.m_dcCircuit),
      m_acCircuit(rhs.m_acCircuit),
      m_modeIcon(rhs.m_modeIcon),
      m_primaryCircuitId(rhs.m_primaryCircuitId),
      m_remoteVisibility(rhs.m_remoteVisibility),
      m_switchString(std::move(rhs.m_switchString)),
      m_systemsOnAnd(rhs.m_systemsOnAnd) {}

CircuitDevice &CircuitDevice::operator=(const CircuitDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_singleThrowId = rhs.m_singleThrowId;
    m_sequentialNamesUTF8 = rhs.m_sequentialNamesUTF8;
    m_hasComplement = rhs.m_hasComplement;
    m_displayCategories = rhs.m_displayCategories;
    m_confirmDialog = rhs.m_confirmDialog;
    m_voltageSource = rhs.m_voltageSource;
    m_circuitType = rhs.m_circuitType;
    m_switchType = rhs.m_switchType;
    m_minLevel = rhs.m_minLevel;
    m_maxLevel = rhs.m_maxLevel;
    m_nonVisibleCircuit = rhs.m_nonVisibleCircuit;
    m_dimstep = rhs.m_dimstep;
    m_step = rhs.m_step;
    m_dimmable = rhs.m_dimmable;
    m_loadSmoothStart = rhs.m_loadSmoothStart;
    m_sequentialStates = rhs.m_sequentialStates;
    m_controlId = rhs.m_controlId;
    m_circuitLoads = rhs.m_circuitLoads;
    m_categories = rhs.m_categories;
    m_dcCircuit = rhs.m_dcCircuit;
    m_acCircuit = rhs.m_acCircuit;
    m_modeIcon = rhs.m_modeIcon;
    m_primaryCircuitId = rhs.m_primaryCircuitId;
    m_remoteVisibility = rhs.m_remoteVisibility;
    m_switchString = rhs.m_switchString;
    m_systemsOnAnd = rhs.m_systemsOnAnd;
  }
  return *this;
}

CircuitDevice &CircuitDevice::operator=(CircuitDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = std::move(rhs.m_id);
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_singleThrowId = std::move(rhs.m_singleThrowId);
    m_sequentialNamesUTF8 = std::move(rhs.m_sequentialNamesUTF8);
    m_hasComplement = rhs.m_hasComplement;
    m_displayCategories = rhs.m_displayCategories;
    m_confirmDialog = rhs.m_confirmDialog;
    m_voltageSource = std::move(rhs.m_voltageSource);
    m_circuitType = rhs.m_circuitType;
    m_switchType = rhs.m_switchType;
    m_minLevel = rhs.m_minLevel;
    m_maxLevel = rhs.m_maxLevel;
    m_nonVisibleCircuit = rhs.m_nonVisibleCircuit;
    m_dimstep = rhs.m_dimstep;
    m_step = rhs.m_step;
    m_dimmable = rhs.m_dimmable;
    m_loadSmoothStart = rhs.m_loadSmoothStart;
    m_sequentialStates = rhs.m_sequentialStates;
    m_controlId = rhs.m_controlId;
    m_circuitLoads = std::move(rhs.m_circuitLoads);
    m_categories = std::move(rhs.m_categories);
    m_dcCircuit = rhs.m_dcCircuit;
    m_acCircuit = rhs.m_acCircuit;
    m_modeIcon = rhs.m_modeIcon;
    m_primaryCircuitId = rhs.m_primaryCircuitId;
    m_remoteVisibility = rhs.m_remoteVisibility;
    m_switchString = std::move(rhs.m_switchString);
    m_systemsOnAnd = rhs.m_systemsOnAnd;
  }
  return *this;
}

std::string &CircuitDevice::add_sequentialNamesUTF8() {
  m_sequentialNamesUTF8.emplace_back();
  return m_sequentialNamesUTF8.back();
}

CircuitLoad &CircuitDevice::add_circuitLoad() {
  m_circuitLoads.emplace_back();
  return m_circuitLoads.back();
}

CategoryItem &CircuitDevice::add_category() {
  m_categories.emplace_back();
  return m_categories.back();
}

Alarm::Alarm()
    : m_displayType(ConfigRequest::eConfigType::eAlarms),
      m_id(0),
      m_alarmType(eAlarmType::eTypeNone),
      m_severity(eSeverityType::eSeverityNone),
      m_currentState(eStateType::eStateDisabled),
      m_channelId(0),
      m_externalAlarmId(0),
      m_uniqueId(0),
      m_valid(false),
      m_activatedTime(0),
      m_acknowledgedTime(0),
      m_clearedTime(0),
      m_name(),
      m_channel(),
      m_device(),
      m_title(),
      m_description(),
      m_cZoneRawAlarm(),
      m_faultAction(),
      m_faultType(0),
      m_faultNumber(0) {}

Alarm::Alarm(const Alarm &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_alarmType(rhs.m_alarmType),
      m_severity(rhs.m_severity),
      m_currentState(rhs.m_currentState),
      m_channelId(rhs.m_channelId),
      m_externalAlarmId(rhs.m_externalAlarmId),
      m_uniqueId(rhs.m_uniqueId),
      m_valid(rhs.m_valid),
      m_activatedTime(rhs.m_activatedTime),
      m_acknowledgedTime(rhs.m_acknowledgedTime),
      m_clearedTime(rhs.m_clearedTime),
      m_name(rhs.m_name),
      m_channel(rhs.m_channel),
      m_device(rhs.m_device),
      m_title(rhs.m_title),
      m_description(rhs.m_description),
      m_cZoneRawAlarm(rhs.m_cZoneRawAlarm),
      m_faultAction(rhs.m_faultAction),
      m_faultType(rhs.m_faultType),
      m_faultNumber(rhs.m_faultNumber) {}

Alarm::Alarm(Alarm &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_alarmType(rhs.m_alarmType),
      m_severity(rhs.m_severity),
      m_currentState(rhs.m_currentState),
      m_channelId(rhs.m_channelId),
      m_externalAlarmId(rhs.m_externalAlarmId),
      m_uniqueId(rhs.m_uniqueId),
      m_valid(rhs.m_valid),
      m_activatedTime(rhs.m_activatedTime),
      m_acknowledgedTime(rhs.m_acknowledgedTime),
      m_clearedTime(rhs.m_clearedTime),
      m_name(std::move(rhs.m_name)),
      m_channel(std::move(rhs.m_channel)),
      m_device(std::move(rhs.m_device)),
      m_title(std::move(rhs.m_title)),
      m_description(std::move(rhs.m_description)),
      m_cZoneRawAlarm(std::move(rhs.m_cZoneRawAlarm)),
      m_faultAction(std::move(rhs.m_faultAction)),
      m_faultType(rhs.m_faultType),
      m_faultNumber(rhs.m_faultNumber) {}

Alarm &Alarm::operator=(const Alarm &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_alarmType = rhs.m_alarmType;
    m_severity = rhs.m_severity;
    m_currentState = rhs.m_currentState;
    m_channelId = rhs.m_channelId;
    m_externalAlarmId = rhs.m_externalAlarmId;
    m_uniqueId = rhs.m_uniqueId;
    m_valid = rhs.m_valid;
    m_activatedTime = rhs.m_activatedTime;
    m_acknowledgedTime = rhs.m_acknowledgedTime;
    m_clearedTime = rhs.m_clearedTime;
    m_name = rhs.m_name;
    m_channel = rhs.m_channel;
    m_device = rhs.m_device;
    m_title = rhs.m_title;
    m_description = rhs.m_description;
    m_cZoneRawAlarm = rhs.m_cZoneRawAlarm;
    m_faultAction = rhs.m_faultAction;
    m_faultType = rhs.m_faultType;
    m_faultNumber = rhs.m_faultNumber;
  }
  return *this;
}

Alarm &Alarm::operator=(Alarm &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_alarmType = rhs.m_alarmType;
    m_severity = rhs.m_severity;
    m_currentState = rhs.m_currentState;
    m_channelId = rhs.m_channelId;
    m_externalAlarmId = rhs.m_externalAlarmId;
    m_uniqueId = rhs.m_uniqueId;
    m_valid = rhs.m_valid;
    m_activatedTime = rhs.m_activatedTime;
    m_acknowledgedTime = rhs.m_acknowledgedTime;
    m_clearedTime = rhs.m_clearedTime;
    m_name = std::move(rhs.m_name);
    m_channel = std::move(rhs.m_channel);
    m_device = std::move(rhs.m_device);
    m_title = std::move(rhs.m_title);
    m_description = std::move(rhs.m_description);
    m_cZoneRawAlarm = std::move(rhs.m_cZoneRawAlarm);
    m_faultAction = std::move(rhs.m_faultAction);
    m_faultType = rhs.m_faultType;
    m_faultNumber = rhs.m_faultNumber;
  }
  return *this;
}

void Alarm::set_cZoneRawAlarm(const void *value, size_t size) {
  m_cZoneRawAlarm.resize(size);
  std::memcpy(m_cZoneRawAlarm.data(), value, size);
}

AlarmsList::AlarmsList() : m_alarms() {}

AlarmsList::AlarmsList(const AlarmsList &rhs) : m_alarms(rhs.m_alarms) {}

AlarmsList::AlarmsList(AlarmsList &&rhs) : m_alarms(std::move(rhs.m_alarms)) {}

AlarmsList &AlarmsList::operator=(const AlarmsList &rhs) {
  if (this != &rhs) {
    m_alarms = rhs.m_alarms;
  }
  return *this;
}

AlarmsList &AlarmsList::operator=(AlarmsList &&rhs) {
  if (this != &rhs) {
    m_alarms = std::move(rhs.m_alarms);
  }
  return *this;
}

Alarm &AlarmsList::add_alarm() {
  m_alarms.emplace_back();
  return m_alarms.back();
}

CZoneRawEvent::CZoneRawEvent() : m_type(), m_content(), m_rawAlarm(), m_deviceItem() {}

CZoneRawEvent::CZoneRawEvent(const CZoneRawEvent &rhs)
    : m_type(rhs.m_type), m_content(rhs.m_content), m_rawAlarm(rhs.m_rawAlarm), m_deviceItem(rhs.m_deviceItem) {}

CZoneRawEvent::CZoneRawEvent(CZoneRawEvent &&rhs)
    : m_type(rhs.m_type),
      m_content(std::move(rhs.m_content)),
      m_rawAlarm(std::move(rhs.m_rawAlarm)),
      m_deviceItem(std::move(rhs.m_deviceItem)) {}

CZoneRawEvent &CZoneRawEvent::operator=(const CZoneRawEvent &rhs) {
  if (this != &rhs) {
    m_type = rhs.m_type;
    m_content = rhs.m_content;
    m_rawAlarm = rhs.m_rawAlarm;
    m_deviceItem = rhs.m_deviceItem;
  }
  return *this;
}

CZoneRawEvent &CZoneRawEvent::operator=(CZoneRawEvent &&rhs) {
  if (this != &rhs) {
    m_type = rhs.m_type;
    m_content = std::move(rhs.m_content);
    m_rawAlarm = std::move(rhs.m_rawAlarm);
    m_deviceItem = std::move(rhs.m_deviceItem);
  }
  return *this;
}

void CZoneRawEvent::set_content(const void *value, size_t size) {
  m_content.resize(size);
  std::memcpy(m_content.data(), value, size);
}

void CZoneRawEvent::set_rawAlarm(const void *value, size_t size) {
  m_rawAlarm.resize(size);
  std::memcpy(m_rawAlarm.data(), value, size);
}

void CZoneRawEvent::set_deviceItem(const void *value, size_t size) {
  m_deviceItem.resize(size);
  std::memcpy(m_deviceItem.data(), value, size);
}

AlarmGlobalStatus::AlarmGlobalStatus()
    : m_highestEnabledSeverity(Alarm::eSeverityType::eSeverityNone),
      m_highestAcknowledgedSeverity(Alarm::eSeverityType::eSeverityNone) {}

AlarmGlobalStatus::AlarmGlobalStatus(const AlarmGlobalStatus &rhs)
    : m_highestEnabledSeverity(rhs.m_highestEnabledSeverity),
      m_highestAcknowledgedSeverity(rhs.m_highestAcknowledgedSeverity) {}

AlarmGlobalStatus::AlarmGlobalStatus(AlarmGlobalStatus &&rhs)
    : m_highestEnabledSeverity(rhs.m_highestEnabledSeverity),
      m_highestAcknowledgedSeverity(rhs.m_highestAcknowledgedSeverity) {}

AlarmGlobalStatus &AlarmGlobalStatus::operator=(const AlarmGlobalStatus &rhs) {
  if (this != &rhs) {
    m_highestEnabledSeverity = rhs.m_highestEnabledSeverity;
    m_highestAcknowledgedSeverity = rhs.m_highestAcknowledgedSeverity;
  }
  return *this;
}

AlarmGlobalStatus &AlarmGlobalStatus::operator=(AlarmGlobalStatus &&rhs) {
  if (this != &rhs) {
    m_highestEnabledSeverity = rhs.m_highestEnabledSeverity;
    m_highestAcknowledgedSeverity = rhs.m_highestAcknowledgedSeverity;
  }
  return *this;
}

Event::Event(eEventType type)
    : m_type(type), m_content(), m_alarmItem(), m_globalStatus(), m_czoneEvent(), m_timeStamp() {}

Event::Event(const Event &rhs)
    : m_type(rhs.m_type),
      m_content(rhs.m_content),
      m_alarmItem(rhs.m_alarmItem),
      m_globalStatus(rhs.m_globalStatus),
      m_czoneEvent(rhs.m_czoneEvent),
      m_timeStamp(rhs.m_timeStamp) {}

Event::Event(Event &&rhs)
    : m_type(rhs.m_type),
      m_content(std::move(rhs.m_content)),
      m_alarmItem(std::move(rhs.m_alarmItem)),
      m_globalStatus(std::move(rhs.m_globalStatus)),
      m_czoneEvent(std::move(rhs.m_czoneEvent)),
      m_timeStamp(std::move(rhs.m_timeStamp)) {}

Event &Event::operator=(const Event &rhs) {
  if (this != &rhs) {
    m_type = rhs.m_type;
    m_content = rhs.m_content;
    m_alarmItem = rhs.m_alarmItem;
    m_globalStatus = rhs.m_globalStatus;
    m_czoneEvent = rhs.m_czoneEvent;
    m_timeStamp = rhs.m_timeStamp;
  }
  return *this;
}

Event &Event::operator=(Event &&rhs) {
  if (this != &rhs) {
    m_type = rhs.m_type;
    m_content = std::move(rhs.m_content);
    m_alarmItem = std::move(rhs.m_alarmItem);
    m_globalStatus = std::move(rhs.m_globalStatus);
    m_czoneEvent = std::move(rhs.m_czoneEvent);
    m_timeStamp = std::move(rhs.m_timeStamp);
  }
  return *this;
}

EngineDevice::EngineDevice() :
    m_displayType(ConfigRequest::eConfigType::eNone),
    m_id(0),
    m_nameUTF8(),
    m_instance(),
    m_softwareId(),
    m_calibrationId(),
    m_serialNumber(),
    m_ecuSerialNumber(),
    m_engineType(eEngineType::eSmartCraft) {}

EngineDevice::EngineDevice(const EngineDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_softwareId(rhs.m_softwareId),
      m_calibrationId(rhs.m_calibrationId),
      m_serialNumber(rhs.m_serialNumber),
      m_ecuSerialNumber(rhs.m_ecuSerialNumber),
      m_engineType(rhs.m_engineType) {}

EngineDevice::EngineDevice(EngineDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_softwareId(std::move(rhs.m_softwareId)),
      m_calibrationId(std::move(rhs.m_calibrationId)),
      m_serialNumber(std::move(rhs.m_serialNumber)),
      m_ecuSerialNumber(std::move(rhs.m_ecuSerialNumber)),
      m_engineType(rhs.m_engineType) {}

EngineDevice &EngineDevice::operator=(const EngineDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_softwareId = rhs.m_softwareId;
    m_calibrationId = rhs.m_calibrationId;
    m_serialNumber = rhs.m_serialNumber;
    m_ecuSerialNumber = rhs.m_ecuSerialNumber;
    m_engineType = rhs.m_engineType;
  }
  return *this;
}

EngineDevice &EngineDevice::operator=(EngineDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_softwareId = std::move(rhs.m_softwareId);
    m_calibrationId = std::move(rhs.m_calibrationId);
    m_serialNumber = std::move(rhs.m_serialNumber);
    m_ecuSerialNumber = std::move(rhs.m_ecuSerialNumber);
    m_engineType = rhs.m_engineType;
  }
  return *this;
}

