#include "modules/czone/configdata.h"
#include "utils/timestamp.h"
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

ControlRequest::ControlRequest(const json &j) {
  try {
    if (j.contains("Type")) {
      m_type = std::make_unique<eControlType>(from_string_control(j["Type"].get<std::string>()));
    }

    if (j.contains("Id")) {
      m_id = std::make_unique<uint32_t>(j["Id"].get<uint32_t>());
    }

    if (j.contains("ThrowType")) {
      m_throwType = std::make_unique<eThrowType>(from_string_throw(j["ThrowType"].get<std::string>()));
    }

    if (j.contains("Level")) {
      m_value = std::make_unique<uint32_t>(j["Level"].get<uint32_t>());
    }

    if (j.contains("ButtonType")) {
      m_buttonType = std::make_unique<eButtonInfoType>(from_string_button(j["ButtonType"].get<std::string>()));
    }

    if (j.contains("Token")) {
      m_token = std::make_unique<std::string>(j["Token"].get<std::string>());
    }

  } catch (const std::invalid_argument &e) {
    throw std::invalid_argument(e.what());
  } catch (const std::exception &e) {
    throw std::runtime_error("ControlRequest::ControlRequest error while generating ControlRequest object.");
  }
}

ControlRequest::ControlRequest(const ControlRequest &other) {
  if (other.m_type)
    m_type = std::make_unique<eControlType>(*other.m_type);
  if (other.m_throwType)
    m_throwType = std::make_unique<eThrowType>(*other.m_throwType);
  if (other.m_buttonType)
    m_buttonType = std::make_unique<eButtonInfoType>(*other.m_buttonType);
  if (other.m_id)
    m_id = std::make_unique<uint32_t>(*other.m_id);
  if (other.m_value)
    m_value = std::make_unique<uint32_t>(*other.m_value);
  if (other.m_token)
    m_token = std::make_unique<std::string>(*other.m_token);
}

FileRequest::FileRequest(const json &j) {
  try {
    if (j.contains("Type")) {
      m_type = std::make_unique<eFileType>(from_string_fileType(j["Type"].get<std::string>()));
    }

    if (j.contains("ResourceType")) {
      m_resourceType = std::make_unique<eResourceType>(from_string_ResourceType(j["ResourceType"].get<std::string>()));
    }

    if (j.contains("Content")) {
      m_content = std::make_unique<std::string>(j["Content"].get<std::string>());
    }

  } catch (const std::invalid_argument &e) {
    throw std::invalid_argument(e.what());
  } catch (const std::exception &e) {
    throw std::runtime_error("FileRequest::FileRequest error while generating FileRequest object.");
  }
}

FileRequest::FileRequest(const FileRequest &other) {
  if (other.m_type)
    m_type = std::make_unique<eFileType>(*other.m_type);
  if (other.m_resourceType)
    m_resourceType = std::make_unique<eResourceType>(*other.m_resourceType);
  if (other.m_content)
    m_content = std::make_unique<std::string>(*other.m_content);
}

OperationRequest::OperationRequest(const json &j) {
  try {
    if (j.contains("Type")) {
      m_type = std::make_unique<eOperationType>(from_string_OperationType(j["Type"].get<std::string>()));
    }
    if (j.contains("type")) {
      m_type = std::make_unique<eOperationType>(from_string_OperationType(j["type"].get<std::string>()));
    }

    if (j.contains("ReadConfigForce")) {
      m_readConfigForce = std::make_unique<bool>(j["ReadConfigForce"].get<bool>());
    } else {
      m_readConfigForce = std::make_unique<bool>(false);
    }

    if (j.contains("ReadConfigMode")) {
      m_readConfigMode = std::make_unique<bool>(j["ReadConfigMode"].get<bool>());
    } else {
      m_readConfigMode = std::make_unique<bool>(false);
    }

    if (j.contains("CZoneRawOperation")) {
      m_cZoneRawOperation = std::make_unique<uint32_t>(j["CZoneRawOperation"].get<uint32_t>());
    }
  } catch (const std::invalid_argument &e) {
    throw std::invalid_argument(e.what());
  } catch (const std::exception &e) {
    throw std::runtime_error("FileRequest::FileRequest error while generating FileRequest object.");
  }
}

OperationRequest::OperationRequest(const OperationRequest &other) {
  if (other.m_type)
    m_type = std::make_unique<eOperationType>(*other.m_type);
  if (other.m_readConfigForce)
    m_readConfigForce = std::make_unique<bool>(*other.m_readConfigForce);
  if (other.m_readConfigMode)
    m_readConfigMode = std::make_unique<bool>(*other.m_readConfigMode);
  if (other.m_cZoneRawOperation)
    m_cZoneRawOperation = std::make_unique<uint32_t>(*other.m_cZoneRawOperation);
}

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
    : m_type(type), m_content(), m_alarmItem(), m_globalStatus(), m_czoneEvent(), m_timeStamp(getCurrentTimeString()) {}

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

EngineDevice::EngineDevice()
    : m_displayType(ConfigRequest::eConfigType::eNone),
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

MeteringDevice::MeteringDevice() {
  m_displayType = ConfigRequest::eConfigType::eNone;
  m_id = 0;
  m_nameUTF8.clear();
  m_instance = Instance();
  m_line = eACLine::eLine1;
  m_output = false;
  m_nominalVoltage = 0;
  m_nominalFrequency = 0;
  m_address = 0;
  m_capacity = 0;
  m_warningLow = 0.0f;
  m_warningHigh = 0.0f;
  m_lowLimit = AlarmLimit();
  m_veryLowLimit = AlarmLimit();
  m_highLimit = AlarmLimit();
  m_veryHighLimit = AlarmLimit();
  m_frequency = AlarmLimit();
  m_lowVoltage = AlarmLimit();
  m_veryLowVoltage = AlarmLimit();
  m_highVoltage = AlarmLimit();
  m_canResetCapacity = false;
  m_dcType = eDCType::eOther;
  m_showVoltage = false;
  m_showCurrent = false;
  m_showStateOfCharge = false;
  m_showTemperature = false;
  m_showTimeOfRemaining = false;
  m_acType = eACType::eUnknown;
}

MeteringDevice::MeteringDevice(const MeteringDevice &rhs) {
  m_displayType = rhs.m_displayType;
  m_id = rhs.m_id;
  m_nameUTF8 = rhs.m_nameUTF8;
  m_instance = rhs.m_instance;
  m_line = rhs.m_line;
  m_output = rhs.m_output;
  m_nominalVoltage = rhs.m_nominalVoltage;
  m_nominalFrequency = rhs.m_nominalFrequency;
  m_address = rhs.m_address;
  m_capacity = rhs.m_capacity;
  m_warningLow = rhs.m_warningLow;
  m_warningHigh = rhs.m_warningHigh;
  m_lowLimit = rhs.m_lowLimit;
  m_veryLowLimit = rhs.m_veryLowLimit;
  m_highLimit = rhs.m_highLimit;
  m_veryHighLimit = rhs.m_veryHighLimit;
  m_frequency = rhs.m_frequency;
  m_lowVoltage = rhs.m_lowVoltage;
  m_veryLowVoltage = rhs.m_veryLowVoltage;
  m_highVoltage = rhs.m_highVoltage;
  m_canResetCapacity = rhs.m_canResetCapacity;
  m_dcType = rhs.m_dcType;
  m_showVoltage = rhs.m_showVoltage;
  m_showCurrent = rhs.m_showCurrent;
  m_showStateOfCharge = rhs.m_showStateOfCharge;
  m_showTemperature = rhs.m_showTemperature;
  m_showTimeOfRemaining = rhs.m_showTimeOfRemaining;
  m_acType = rhs.m_acType;
}

MeteringDevice::MeteringDevice(MeteringDevice &&rhs) {
  m_displayType = rhs.m_displayType;
  m_id = rhs.m_id;
  m_nameUTF8 = std::move(rhs.m_nameUTF8);
  m_instance = std::move(rhs.m_instance);
  m_line = rhs.m_line;
  m_output = rhs.m_output;
  m_nominalVoltage = rhs.m_nominalVoltage;
  m_nominalFrequency = rhs.m_nominalFrequency;
  m_address = rhs.m_address;
  m_capacity = rhs.m_capacity;
  m_warningLow = rhs.m_warningLow;
  m_warningHigh = rhs.m_warningHigh;
  m_lowLimit = std::move(rhs.m_lowLimit);
  m_veryLowLimit = std::move(rhs.m_veryLowLimit);
  m_highLimit = std::move(rhs.m_highLimit);
  m_veryHighLimit = std::move(rhs.m_veryHighLimit);
  m_frequency = std::move(rhs.m_frequency);
  m_lowVoltage = std::move(rhs.m_lowVoltage);
  m_veryLowVoltage = std::move(rhs.m_veryLowVoltage);
  m_highVoltage = std::move(rhs.m_highVoltage);
  m_canResetCapacity = rhs.m_canResetCapacity;
  m_dcType = rhs.m_dcType;
  m_showVoltage = rhs.m_showVoltage;
  m_showCurrent = rhs.m_showCurrent;
  m_showStateOfCharge = rhs.m_showStateOfCharge;
  m_showTemperature = rhs.m_showTemperature;
  m_showTimeOfRemaining = rhs.m_showTimeOfRemaining;
  m_acType = rhs.m_acType;
}

MeteringDevice &MeteringDevice::operator=(const MeteringDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_line = rhs.m_line;
    m_output = rhs.m_output;
    m_nominalVoltage = rhs.m_nominalVoltage;
    m_nominalFrequency = rhs.m_nominalFrequency;
    m_address = rhs.m_address;
    m_capacity = rhs.m_capacity;
    m_warningLow = rhs.m_warningLow;
    m_warningHigh = rhs.m_warningHigh;
    m_lowLimit = rhs.m_lowLimit;
    m_veryLowLimit = rhs.m_veryLowLimit;
    m_highLimit = rhs.m_highLimit;
    m_veryHighLimit = rhs.m_veryHighLimit;
    m_frequency = rhs.m_frequency;
    m_lowVoltage = rhs.m_lowVoltage;
    m_veryLowVoltage = rhs.m_veryLowVoltage;
    m_highVoltage = rhs.m_highVoltage;
    m_canResetCapacity = rhs.m_canResetCapacity;
    m_dcType = rhs.m_dcType;
    m_showVoltage = rhs.m_showVoltage;
    m_showCurrent = rhs.m_showCurrent;
    m_showStateOfCharge = rhs.m_showStateOfCharge;
    m_showTemperature = rhs.m_showTemperature;
    m_showTimeOfRemaining = rhs.m_showTimeOfRemaining;
    m_acType = rhs.m_acType;
  }
  return *this;
}

MeteringDevice &MeteringDevice::operator=(MeteringDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_line = rhs.m_line;
    m_output = rhs.m_output;
    m_nominalVoltage = rhs.m_nominalVoltage;
    m_nominalFrequency = rhs.m_nominalFrequency;
    m_address = rhs.m_address;
    m_capacity = rhs.m_capacity;
    m_warningLow = rhs.m_warningLow;
    m_warningHigh = rhs.m_warningHigh;
    m_lowLimit = std::move(rhs.m_lowLimit);
    m_veryLowLimit = std::move(rhs.m_veryLowLimit);
    m_highLimit = std::move(rhs.m_highLimit);
    m_veryHighLimit = std::move(rhs.m_veryHighLimit);
    m_frequency = std::move(rhs.m_frequency);
    m_lowVoltage = std::move(rhs.m_lowVoltage);
    m_veryLowVoltage = std::move(rhs.m_veryLowVoltage);
    m_highVoltage = std::move(rhs.m_highVoltage);
    m_canResetCapacity = rhs.m_canResetCapacity;
    m_dcType = rhs.m_dcType;
    m_showVoltage = rhs.m_showVoltage;
    m_showCurrent = rhs.m_showCurrent;
    m_showStateOfCharge = rhs.m_showStateOfCharge;
    m_showTemperature = rhs.m_showTemperature;
    m_showTimeOfRemaining = rhs.m_showTimeOfRemaining;
    m_acType = rhs.m_acType;
  }
  return *this;
}

MonitoringDevice::MonitoringDevice() {
  m_displayType = ConfigRequest::eConfigType::eNone;
  m_id = 0;
  m_nameUTF8.clear();
  m_instance = Instance();
  m_tankType = MonitoringType::eTankType::eBlackWater;
  m_pressureType = MonitoringType::ePressureType::eAtmospheric;
  m_temperatureType = MonitoringType::eTemperatureType::eBaitWell;
  m_circuitId = DataId();
  m_switchType = CircuitDevice::eSwitchType::eNone;
  m_confirmDialog = CircuitDevice::eConfirmType::eConfirmNone;
  m_circuitNameUTF8 = "";
  m_highTemperature = false;
  m_atmosphericPressure = false;
  m_veryLowLimit = AlarmLimit();
  m_lowLimit = AlarmLimit();
  m_highLimit = AlarmLimit();
  m_veryHighLimit = AlarmLimit();
  m_tankCapacity = 0.0f;
  m_address = 0;
}

MonitoringDevice::MonitoringDevice(const MonitoringDevice &rhs) {
  m_displayType = rhs.m_displayType;
  m_id = rhs.m_id;
  m_nameUTF8 = rhs.m_nameUTF8;
  m_instance = rhs.m_instance;
  m_tankType = rhs.m_tankType;
  m_pressureType = rhs.m_pressureType;
  m_temperatureType = rhs.m_temperatureType;
  m_circuitId = rhs.m_circuitId;
  m_switchType = rhs.m_switchType;
  m_confirmDialog = rhs.m_confirmDialog;
  m_circuitNameUTF8 = rhs.m_circuitNameUTF8;
  m_highTemperature = rhs.m_highTemperature;
  m_atmosphericPressure = rhs.m_atmosphericPressure;
  m_veryLowLimit = rhs.m_veryLowLimit;
  m_lowLimit = rhs.m_lowLimit;
  m_highLimit = rhs.m_highLimit;
  m_veryHighLimit = rhs.m_veryHighLimit;
  m_tankCapacity = rhs.m_tankCapacity;
  m_address = rhs.m_address;
}

MonitoringDevice::MonitoringDevice(MonitoringDevice &&rhs) {
  m_displayType = rhs.m_displayType;
  m_id = rhs.m_id;
  m_nameUTF8 = std::move(rhs.m_nameUTF8);
  m_instance = std::move(rhs.m_instance);
  m_tankType = rhs.m_tankType;
  m_pressureType = rhs.m_pressureType;
  m_temperatureType = rhs.m_temperatureType;
  m_circuitId = std::move(rhs.m_circuitId);
  m_switchType = rhs.m_switchType;
  m_confirmDialog = rhs.m_confirmDialog;
  m_circuitNameUTF8 = std::move(rhs.m_circuitNameUTF8);
  m_highTemperature = rhs.m_highTemperature;
  m_atmosphericPressure = rhs.m_atmosphericPressure;
  m_veryLowLimit = std::move(rhs.m_veryLowLimit);
  m_lowLimit = std::move(rhs.m_lowLimit);
  m_highLimit = std::move(rhs.m_highLimit);
  m_veryHighLimit = std::move(rhs.m_veryHighLimit);
  m_tankCapacity = rhs.m_tankCapacity;
  m_address = rhs.m_address;
}

MonitoringDevice &MonitoringDevice::operator=(const MonitoringDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_tankType = rhs.m_tankType;
    m_pressureType = rhs.m_pressureType;
    m_temperatureType = rhs.m_temperatureType;
    m_circuitId = rhs.m_circuitId;
    m_switchType = rhs.m_switchType;
    m_confirmDialog = rhs.m_confirmDialog;
    m_circuitNameUTF8 = rhs.m_circuitNameUTF8;
    m_highTemperature = rhs.m_highTemperature;
    m_atmosphericPressure = rhs.m_atmosphericPressure;
    m_veryLowLimit = rhs.m_veryLowLimit;
    m_lowLimit = rhs.m_lowLimit;
    m_highLimit = rhs.m_highLimit;
    m_veryHighLimit = rhs.m_veryHighLimit;
    m_tankCapacity = rhs.m_tankCapacity;
    m_address = rhs.m_address;
  }
  return *this;
}

MonitoringDevice &MonitoringDevice::operator=(MonitoringDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_tankType = rhs.m_tankType;
    m_pressureType = rhs.m_pressureType;
    m_temperatureType = rhs.m_temperatureType;
    m_circuitId = std::move(rhs.m_circuitId);
    m_switchType = rhs.m_switchType;
    m_confirmDialog = rhs.m_confirmDialog;
    m_circuitNameUTF8 = std::move(rhs.m_circuitNameUTF8);
    m_highTemperature = rhs.m_highTemperature;
    m_atmosphericPressure = rhs.m_atmosphericPressure;
    m_veryLowLimit = std::move(rhs.m_veryLowLimit);
    m_lowLimit = std::move(rhs.m_lowLimit);
    m_highLimit = std::move(rhs.m_highLimit);
    m_veryHighLimit = std::move(rhs.m_veryHighLimit);
    m_tankCapacity = rhs.m_tankCapacity;
    m_address = rhs.m_address;
  }
  return *this;
}

ACMainContactorDevice::ACMainContactorDevice()
    : m_systemStateId(0),
      m_nameUTF8(),
      m_contactorId(),
      m_contactorToggleId(),
      m_ac1Id(),
      m_ac2Id(),
      m_ac3Id(),
      m_displayIndex(0),
      m_loadGroupIndex(0),
      m_loadGroupParallelIndex(0),
      m_isParallel(false),
      m_acInputType(eShipPower) {}

ACMainContactorDevice::ACMainContactorDevice(const ACMainContactorDevice &rhs)
    : m_systemStateId(rhs.m_systemStateId),
      m_nameUTF8(rhs.m_nameUTF8),
      m_contactorId(rhs.m_contactorId),
      m_contactorToggleId(rhs.m_contactorToggleId),
      m_ac1Id(rhs.m_ac1Id),
      m_ac2Id(rhs.m_ac2Id),
      m_ac3Id(rhs.m_ac3Id),
      m_displayIndex(rhs.m_displayIndex),
      m_loadGroupIndex(rhs.m_loadGroupIndex),
      m_loadGroupParallelIndex(rhs.m_loadGroupParallelIndex),
      m_isParallel(rhs.m_isParallel),
      m_acInputType(rhs.m_acInputType) {}

ACMainContactorDevice::ACMainContactorDevice(ACMainContactorDevice &&rhs)
    : m_systemStateId(rhs.m_systemStateId),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_contactorId(std::move(rhs.m_contactorId)),
      m_contactorToggleId(std::move(rhs.m_contactorToggleId)),
      m_ac1Id(std::move(rhs.m_ac1Id)),
      m_ac2Id(std::move(rhs.m_ac2Id)),
      m_ac3Id(std::move(rhs.m_ac3Id)),
      m_displayIndex(rhs.m_displayIndex),
      m_loadGroupIndex(rhs.m_loadGroupIndex),
      m_loadGroupParallelIndex(rhs.m_loadGroupParallelIndex),
      m_isParallel(rhs.m_isParallel),
      m_acInputType(rhs.m_acInputType) {}

ACMainContactorDevice &ACMainContactorDevice::operator=(const ACMainContactorDevice &rhs) {
  if (this != &rhs) {
    m_systemStateId = rhs.m_systemStateId;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_contactorId = rhs.m_contactorId;
    m_contactorToggleId = rhs.m_contactorToggleId;
    m_ac1Id = rhs.m_ac1Id;
    m_ac2Id = rhs.m_ac2Id;
    m_ac3Id = rhs.m_ac3Id;
    m_displayIndex = rhs.m_displayIndex;
    m_loadGroupIndex = rhs.m_loadGroupIndex;
    m_loadGroupParallelIndex = rhs.m_loadGroupParallelIndex;
    m_isParallel = rhs.m_isParallel;
    m_acInputType = rhs.m_acInputType;
  }
  return *this;
}

ACMainContactorDevice &ACMainContactorDevice::operator=(ACMainContactorDevice &&rhs) {
  if (this != &rhs) {
    m_systemStateId = rhs.m_systemStateId;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_contactorId = std::move(rhs.m_contactorId);
    m_contactorToggleId = std::move(rhs.m_contactorToggleId);
    m_ac1Id = std::move(rhs.m_ac1Id);
    m_ac2Id = std::move(rhs.m_ac2Id);
    m_ac3Id = std::move(rhs.m_ac3Id);
    m_displayIndex = rhs.m_displayIndex;
    m_loadGroupIndex = rhs.m_loadGroupIndex;
    m_loadGroupParallelIndex = rhs.m_loadGroupParallelIndex;
    m_isParallel = rhs.m_isParallel;
    m_acInputType = rhs.m_acInputType;
  }
  return *this;
}

ACMainLoadGroupDevice::ACMainLoadGroupDevice() : m_nameUTF8(), m_loadGroupIndex(0) {}

ACMainLoadGroupDevice::ACMainLoadGroupDevice(const ACMainLoadGroupDevice &rhs)
    : m_nameUTF8(rhs.m_nameUTF8), m_loadGroupIndex(rhs.m_loadGroupIndex) {}

ACMainLoadGroupDevice::ACMainLoadGroupDevice(ACMainLoadGroupDevice &&rhs)
    : m_nameUTF8(std::move(rhs.m_nameUTF8)), m_loadGroupIndex(rhs.m_loadGroupIndex) {}

ACMainLoadGroupDevice &ACMainLoadGroupDevice::operator=(const ACMainLoadGroupDevice &rhs) {
  if (this != &rhs) {
    m_nameUTF8 = rhs.m_nameUTF8;
    m_loadGroupIndex = rhs.m_loadGroupIndex;
  }
  return *this;
}

ACMainLoadGroupDevice &ACMainLoadGroupDevice::operator=(ACMainLoadGroupDevice &&rhs) {
  if (this != &rhs) {
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_loadGroupIndex = rhs.m_loadGroupIndex;
  }
  return *this;
}

ACMainDevice::ACMainDevice()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_id(0),
      m_nameUTF8(),
      m_dipswitch(0),
      m_contactors(),
      m_loadGroups() {
  m_contactors.clear();
  m_loadGroups.clear();
}

ACMainDevice::ACMainDevice(const ACMainDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_dipswitch(rhs.m_dipswitch),
      m_contactors(rhs.m_contactors),
      m_loadGroups(rhs.m_loadGroups) {}

ACMainDevice::ACMainDevice(ACMainDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_dipswitch(rhs.m_dipswitch),
      m_contactors(std::move(rhs.m_contactors)),
      m_loadGroups(std::move(rhs.m_loadGroups)) {}

ACMainDevice &ACMainDevice::operator=(const ACMainDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_dipswitch = rhs.m_dipswitch;
    m_contactors = rhs.m_contactors;
    m_loadGroups = rhs.m_loadGroups;
  }
  return *this;
}

ACMainDevice &ACMainDevice::operator=(ACMainDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_dipswitch = rhs.m_dipswitch;
    m_contactors = std::move(rhs.m_contactors);
    m_loadGroups = std::move(rhs.m_loadGroups);
  }
  return *this;
}

InverterChargerDevice::InverterChargerDevice()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_id(0),
      m_nameUTF8(),
      m_model(0),
      m_type(0),
      m_subType(0),
      m_inverterInstance(),
      m_inverterACId(),
      m_inverterCircuitId(),
      m_inverterToggleCircuitId(),
      m_chargerInstance(),
      m_chargerACId(),
      m_chargerCircuitId(),
      m_chargerToggleCircuitId(),
      m_batteryBank1Id(),
      m_batteryBank2Id(),
      m_batteryBank3Id(),
      m_positionColumn(0),
      m_positionRow(0),
      m_clustered(false),
      m_primary(false),
      m_primaryPhase(0),
      m_deviceInstance(0),
      m_dipswitch(0),
      m_channelIndex(0) {}

InverterChargerDevice::InverterChargerDevice(const InverterChargerDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_model(rhs.m_model),
      m_type(rhs.m_type),
      m_subType(rhs.m_subType),
      m_inverterInstance(rhs.m_inverterInstance),
      m_inverterACId(rhs.m_inverterACId),
      m_inverterCircuitId(rhs.m_inverterCircuitId),
      m_inverterToggleCircuitId(rhs.m_inverterToggleCircuitId),
      m_chargerInstance(rhs.m_chargerInstance),
      m_chargerACId(rhs.m_chargerACId),
      m_chargerCircuitId(rhs.m_chargerCircuitId),
      m_chargerToggleCircuitId(rhs.m_chargerToggleCircuitId),
      m_batteryBank1Id(rhs.m_batteryBank1Id),
      m_batteryBank2Id(rhs.m_batteryBank2Id),
      m_batteryBank3Id(rhs.m_batteryBank3Id),
      m_positionColumn(rhs.m_positionColumn),
      m_positionRow(rhs.m_positionRow),
      m_clustered(rhs.m_clustered),
      m_primary(rhs.m_primary),
      m_primaryPhase(rhs.m_primaryPhase),
      m_deviceInstance(rhs.m_deviceInstance),
      m_dipswitch(rhs.m_dipswitch),
      m_channelIndex(rhs.m_channelIndex) {}

InverterChargerDevice::InverterChargerDevice(InverterChargerDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_model(rhs.m_model),
      m_type(rhs.m_type),
      m_subType(rhs.m_subType),
      m_inverterInstance(std::move(rhs.m_inverterInstance)),
      m_inverterACId(std::move(rhs.m_inverterACId)),
      m_inverterCircuitId(std::move(rhs.m_inverterCircuitId)),
      m_inverterToggleCircuitId(std::move(rhs.m_inverterToggleCircuitId)),
      m_chargerInstance(std::move(rhs.m_chargerInstance)),
      m_chargerACId(std::move(rhs.m_chargerACId)),
      m_chargerCircuitId(std::move(rhs.m_chargerCircuitId)),
      m_chargerToggleCircuitId(std::move(rhs.m_chargerToggleCircuitId)),
      m_batteryBank1Id(std::move(rhs.m_batteryBank1Id)),
      m_batteryBank2Id(std::move(rhs.m_batteryBank2Id)),
      m_batteryBank3Id(std::move(rhs.m_batteryBank3Id)),
      m_positionColumn(rhs.m_positionColumn),
      m_positionRow(rhs.m_positionRow),
      m_clustered(rhs.m_clustered),
      m_primary(rhs.m_primary),
      m_primaryPhase(rhs.m_primaryPhase),
      m_deviceInstance(rhs.m_deviceInstance),
      m_dipswitch(rhs.m_dipswitch),
      m_channelIndex(rhs.m_channelIndex) {}

InverterChargerDevice &InverterChargerDevice::operator=(const InverterChargerDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_model = rhs.m_model;
    m_type = rhs.m_type;
    m_subType = rhs.m_subType;
    m_inverterInstance = rhs.m_inverterInstance;
    m_inverterACId = rhs.m_inverterACId;
    m_inverterCircuitId = rhs.m_inverterCircuitId;
    m_inverterToggleCircuitId = rhs.m_inverterToggleCircuitId;
    m_chargerInstance = rhs.m_chargerInstance;
    m_chargerACId = rhs.m_chargerACId;
    m_chargerCircuitId = rhs.m_chargerCircuitId;
    m_chargerToggleCircuitId = rhs.m_chargerToggleCircuitId;
    m_batteryBank1Id = rhs.m_batteryBank1Id;
    m_batteryBank2Id = rhs.m_batteryBank2Id;
    m_batteryBank3Id = rhs.m_batteryBank3Id;
    m_positionColumn = rhs.m_positionColumn;
    m_positionRow = rhs.m_positionRow;
    m_clustered = rhs.m_clustered;
    m_primary = rhs.m_primary;
    m_primaryPhase = rhs.m_primaryPhase;
    m_deviceInstance = rhs.m_deviceInstance;
    m_dipswitch = rhs.m_dipswitch;
    m_channelIndex = rhs.m_channelIndex;
  }
  return *this;
}

InverterChargerDevice &InverterChargerDevice::operator=(InverterChargerDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_model = rhs.m_model;
    m_type = rhs.m_type;
    m_subType = rhs.m_subType;
    m_inverterInstance = std::move(rhs.m_inverterInstance);
    m_inverterACId = std::move(rhs.m_inverterACId);
    m_inverterCircuitId = std::move(rhs.m_inverterCircuitId);
    m_inverterToggleCircuitId = std::move(rhs.m_inverterToggleCircuitId);
    m_chargerInstance = std::move(rhs.m_chargerInstance);
    m_chargerACId = std::move(rhs.m_chargerACId);
    m_chargerCircuitId = std::move(rhs.m_chargerCircuitId);
    m_chargerToggleCircuitId = std::move(rhs.m_chargerToggleCircuitId);
    m_batteryBank1Id = std::move(rhs.m_batteryBank1Id);
    m_batteryBank2Id = std::move(rhs.m_batteryBank2Id);
    m_batteryBank3Id = std::move(rhs.m_batteryBank3Id);
    m_positionColumn = rhs.m_positionColumn;
    m_positionRow = rhs.m_positionRow;
    m_clustered = rhs.m_clustered;
    m_primary = rhs.m_primary;
    m_primaryPhase = rhs.m_primaryPhase;
    m_deviceInstance = rhs.m_deviceInstance;
    m_dipswitch = rhs.m_dipswitch;
    m_channelIndex = rhs.m_channelIndex;
  }
  return *this;
}

HVACDevice::HVACDevice()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_id(0),
      m_nameUTF8(),
      m_instance(),
      m_operatingModeId(),
      m_fanModeId(),
      m_fanSpeedId(),
      m_setpointTemperatureId(),
      m_operatingModeToggleId(),
      m_fanModeToggleId(),
      m_fanSpeedToggleId(),
      m_setpointTemperatureToggleId(),
      m_temperatureMonitoringId(),
      m_fanSpeedCount(0),
      m_operatingModesMask(0),
      m_model(0),
      m_temperatureInstance(),
      m_setpointTemperatureMin(0.0f),
      m_setpointTemperatureMax(0.0f),
      m_fanSpeedOffModesMask(0),
      m_fanSpeedAutoModesMask(0),
      m_fanSpeedManualModesMask(0) {}

HVACDevice::HVACDevice(const HVACDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_operatingModeId(rhs.m_operatingModeId),
      m_fanModeId(rhs.m_fanModeId),
      m_fanSpeedId(rhs.m_fanSpeedId),
      m_setpointTemperatureId(rhs.m_setpointTemperatureId),
      m_operatingModeToggleId(rhs.m_operatingModeToggleId),
      m_fanModeToggleId(rhs.m_fanModeToggleId),
      m_fanSpeedToggleId(rhs.m_fanSpeedToggleId),
      m_setpointTemperatureToggleId(rhs.m_setpointTemperatureToggleId),
      m_temperatureMonitoringId(rhs.m_temperatureMonitoringId),
      m_fanSpeedCount(rhs.m_fanSpeedCount),
      m_operatingModesMask(rhs.m_operatingModesMask),
      m_model(rhs.m_model),
      m_temperatureInstance(rhs.m_temperatureInstance),
      m_setpointTemperatureMin(rhs.m_setpointTemperatureMin),
      m_setpointTemperatureMax(rhs.m_setpointTemperatureMax),
      m_fanSpeedOffModesMask(rhs.m_fanSpeedOffModesMask),
      m_fanSpeedAutoModesMask(rhs.m_fanSpeedAutoModesMask),
      m_fanSpeedManualModesMask(rhs.m_fanSpeedManualModesMask) {}

HVACDevice::HVACDevice(HVACDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_operatingModeId(std::move(rhs.m_operatingModeId)),
      m_fanModeId(std::move(rhs.m_fanModeId)),
      m_fanSpeedId(std::move(rhs.m_fanSpeedId)),
      m_setpointTemperatureId(std::move(rhs.m_setpointTemperatureId)),
      m_operatingModeToggleId(std::move(rhs.m_operatingModeToggleId)),
      m_fanModeToggleId(std::move(rhs.m_fanModeToggleId)),
      m_fanSpeedToggleId(std::move(rhs.m_fanSpeedToggleId)),
      m_setpointTemperatureToggleId(std::move(rhs.m_setpointTemperatureToggleId)),
      m_temperatureMonitoringId(std::move(rhs.m_temperatureMonitoringId)),
      m_fanSpeedCount(rhs.m_fanSpeedCount),
      m_operatingModesMask(rhs.m_operatingModesMask),
      m_model(rhs.m_model),
      m_temperatureInstance(std::move(rhs.m_temperatureInstance)),
      m_setpointTemperatureMin(rhs.m_setpointTemperatureMin),
      m_setpointTemperatureMax(rhs.m_setpointTemperatureMax),
      m_fanSpeedOffModesMask(rhs.m_fanSpeedOffModesMask),
      m_fanSpeedAutoModesMask(rhs.m_fanSpeedAutoModesMask),
      m_fanSpeedManualModesMask(rhs.m_fanSpeedManualModesMask) {}

HVACDevice &HVACDevice::operator=(const HVACDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_operatingModeId = rhs.m_operatingModeId;
    m_fanModeId = rhs.m_fanModeId;
    m_fanSpeedId = rhs.m_fanSpeedId;
    m_setpointTemperatureId = rhs.m_setpointTemperatureId;
    m_operatingModeToggleId = rhs.m_operatingModeToggleId;
    m_fanModeToggleId = rhs.m_fanModeToggleId;
    m_fanSpeedToggleId = rhs.m_fanSpeedToggleId;
    m_setpointTemperatureToggleId = rhs.m_setpointTemperatureToggleId;
    m_temperatureMonitoringId = rhs.m_temperatureMonitoringId;
    m_fanSpeedCount = rhs.m_fanSpeedCount;
    m_operatingModesMask = rhs.m_operatingModesMask;
    m_model = rhs.m_model;
    m_temperatureInstance = rhs.m_temperatureInstance;
    m_setpointTemperatureMin = rhs.m_setpointTemperatureMin;
    m_setpointTemperatureMax = rhs.m_setpointTemperatureMax;
    m_fanSpeedOffModesMask = rhs.m_fanSpeedOffModesMask;
    m_fanSpeedAutoModesMask = rhs.m_fanSpeedAutoModesMask;
    m_fanSpeedManualModesMask = rhs.m_fanSpeedManualModesMask;
  }
  return *this;
}

HVACDevice &HVACDevice::operator=(HVACDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_operatingModeId = std::move(rhs.m_operatingModeId);
    m_fanModeId = std::move(rhs.m_fanModeId);
    m_fanSpeedId = std::move(rhs.m_fanSpeedId);
    m_setpointTemperatureId = std::move(rhs.m_setpointTemperatureId);
    m_operatingModeToggleId = std::move(rhs.m_operatingModeToggleId);
    m_fanModeToggleId = std::move(rhs.m_fanModeToggleId);
    m_fanSpeedToggleId = std::move(rhs.m_fanSpeedToggleId);
    m_setpointTemperatureToggleId = std::move(rhs.m_setpointTemperatureToggleId);
    m_temperatureMonitoringId = std::move(rhs.m_temperatureMonitoringId);
    m_fanSpeedCount = rhs.m_fanSpeedCount;
    m_operatingModesMask = rhs.m_operatingModesMask;
    m_model = rhs.m_model;
    m_temperatureInstance = std::move(rhs.m_temperatureInstance);
    m_setpointTemperatureMin = rhs.m_setpointTemperatureMin;
    m_setpointTemperatureMax = rhs.m_setpointTemperatureMax;
    m_fanSpeedOffModesMask = rhs.m_fanSpeedOffModesMask;
    m_fanSpeedAutoModesMask = rhs.m_fanSpeedAutoModesMask;
    m_fanSpeedManualModesMask = rhs.m_fanSpeedManualModesMask;
  }
  return *this;
}

ZipdeeAwningDevice::ZipdeeAwningDevice()
    : m_displayType(ConfigRequest::eConfigType::eZipdeeAwning),
      m_id(0),
      m_nameUTF8(""),
      m_instance(),
      m_openId(),
      m_closeId(),
      m_tiltLeftId(),
      m_tiltRightId(),
      m_binarySignals() {
  m_binarySignals.clear();
}

ZipdeeAwningDevice::ZipdeeAwningDevice(const ZipdeeAwningDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_openId(rhs.m_openId),
      m_closeId(rhs.m_closeId),
      m_tiltLeftId(rhs.m_tiltLeftId),
      m_tiltRightId(rhs.m_tiltRightId),
      m_binarySignals(rhs.m_binarySignals) {}

ZipdeeAwningDevice::ZipdeeAwningDevice(ZipdeeAwningDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_openId(std::move(rhs.m_openId)),
      m_closeId(std::move(rhs.m_closeId)),
      m_tiltLeftId(std::move(rhs.m_tiltLeftId)),
      m_tiltRightId(std::move(rhs.m_tiltRightId)),
      m_binarySignals(std::move(rhs.m_binarySignals)) {}

ZipdeeAwningDevice &ZipdeeAwningDevice::operator=(const ZipdeeAwningDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_openId = rhs.m_openId;
    m_closeId = rhs.m_closeId;
    m_tiltLeftId = rhs.m_tiltLeftId;
    m_tiltRightId = rhs.m_tiltRightId;
    m_binarySignals = rhs.m_binarySignals;
  }
  return *this;
}

ZipdeeAwningDevice &ZipdeeAwningDevice::operator=(ZipdeeAwningDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_openId = std::move(rhs.m_openId);
    m_closeId = std::move(rhs.m_closeId);
    m_tiltLeftId = std::move(rhs.m_tiltLeftId);
    m_tiltRightId = std::move(rhs.m_tiltRightId);
    m_binarySignals = std::move(rhs.m_binarySignals);
  }
  return *this;
}

BinarySignalBitAddress::BinarySignalBitAddress() : m_dataType(0), m_dipswitch(0), m_bit(0) {}

BinarySignalBitAddress::BinarySignalBitAddress(uint32_t dataType, uint32_t dipswitch, uint32_t bit)
    : m_dataType(dataType), m_dipswitch(dipswitch), m_bit(bit) {}

BinarySignalBitAddress::BinarySignalBitAddress(const BinarySignalBitAddress &rhs)
    : m_dataType(rhs.m_dataType), m_dipswitch(rhs.m_dipswitch), m_bit(rhs.m_bit) {}

BinarySignalBitAddress::BinarySignalBitAddress(BinarySignalBitAddress &&rhs)
    : m_dataType(std::move(rhs.m_dataType)), m_dipswitch(std::move(rhs.m_dipswitch)), m_bit(std::move(rhs.m_bit)) {}

BinarySignalBitAddress &BinarySignalBitAddress::operator=(const BinarySignalBitAddress &rhs) {
  if (this != &rhs) {
    m_dataType = rhs.m_dataType;
    m_dipswitch = rhs.m_dipswitch;
    m_bit = rhs.m_bit;
  }
  return *this;
}

BinarySignalBitAddress &BinarySignalBitAddress::operator=(BinarySignalBitAddress &&rhs) {
  if (this != &rhs) {
    m_dataType = std::move(rhs.m_dataType);
    m_dipswitch = std::move(rhs.m_dipswitch);
    m_bit = std::move(rhs.m_bit);
  }
  return *this;
}

ThirdPartyGeneratorDevice::ThirdPartyGeneratorDevice()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_id(0),
      m_nameUTF8(),
      m_instance(),
      m_startControlId(),
      m_stopControlId(),
      m_associatedAcMetersInstance(),
      m_acMeterLine1Id(),
      m_acMeterLine2Id(),
      m_acMeterLine3Id() {}

ThirdPartyGeneratorDevice::ThirdPartyGeneratorDevice(const ThirdPartyGeneratorDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_startControlId(rhs.m_startControlId),
      m_stopControlId(rhs.m_stopControlId),
      m_associatedAcMetersInstance(rhs.m_associatedAcMetersInstance),
      m_acMeterLine1Id(rhs.m_acMeterLine1Id),
      m_acMeterLine2Id(rhs.m_acMeterLine2Id),
      m_acMeterLine3Id(rhs.m_acMeterLine3Id) {}

ThirdPartyGeneratorDevice::ThirdPartyGeneratorDevice(ThirdPartyGeneratorDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_startControlId(std::move(rhs.m_startControlId)),
      m_stopControlId(std::move(rhs.m_stopControlId)),
      m_associatedAcMetersInstance(std::move(rhs.m_associatedAcMetersInstance)),
      m_acMeterLine1Id(std::move(rhs.m_acMeterLine1Id)),
      m_acMeterLine2Id(std::move(rhs.m_acMeterLine2Id)),
      m_acMeterLine3Id(std::move(rhs.m_acMeterLine3Id)) {}

ThirdPartyGeneratorDevice &ThirdPartyGeneratorDevice::operator=(const ThirdPartyGeneratorDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_startControlId = rhs.m_startControlId;
    m_stopControlId = rhs.m_stopControlId;
    m_associatedAcMetersInstance = rhs.m_associatedAcMetersInstance;
    m_acMeterLine1Id = rhs.m_acMeterLine1Id;
    m_acMeterLine2Id = rhs.m_acMeterLine2Id;
    m_acMeterLine3Id = rhs.m_acMeterLine3Id;
  }
  return *this;
}

ThirdPartyGeneratorDevice &ThirdPartyGeneratorDevice::operator=(ThirdPartyGeneratorDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_startControlId = std::move(rhs.m_startControlId);
    m_stopControlId = std::move(rhs.m_stopControlId);
    m_associatedAcMetersInstance = std::move(rhs.m_associatedAcMetersInstance);
    m_acMeterLine1Id = std::move(rhs.m_acMeterLine1Id);
    m_acMeterLine2Id = std::move(rhs.m_acMeterLine2Id);
    m_acMeterLine3Id = std::move(rhs.m_acMeterLine3Id);
  }
  return *this;
}

TyrePressureDevice::TyrePressureDevice()
    : m_displayType(ConfigRequest::eConfigType::eTyrePressure),
      m_id(0),
      m_nameUTF8(),
      m_instance(),
      m_numberOfAxles(0),
      m_tyresAxle1(0),
      m_tyresAxle2(0),
      m_tyresAxle3(0),
      m_tyresAxle4(0),
      m_spareAxle(0),
      m_tyreInstances(),
      m_tyreSpareInstances() {}

TyrePressureDevice::TyrePressureDevice(const TyrePressureDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_numberOfAxles(rhs.m_numberOfAxles),
      m_tyresAxle1(rhs.m_tyresAxle1),
      m_tyresAxle2(rhs.m_tyresAxle2),
      m_tyresAxle3(rhs.m_tyresAxle3),
      m_tyresAxle4(rhs.m_tyresAxle4),
      m_spareAxle(rhs.m_spareAxle),
      m_tyreInstances(rhs.m_tyreInstances),
      m_tyreSpareInstances(rhs.m_tyreSpareInstances) {}

TyrePressureDevice::TyrePressureDevice(TyrePressureDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_numberOfAxles(rhs.m_numberOfAxles),
      m_tyresAxle1(rhs.m_tyresAxle1),
      m_tyresAxle2(rhs.m_tyresAxle2),
      m_tyresAxle3(rhs.m_tyresAxle3),
      m_tyresAxle4(rhs.m_tyresAxle4),
      m_spareAxle(rhs.m_spareAxle),
      m_tyreInstances(std::move(rhs.m_tyreInstances)),
      m_tyreSpareInstances(std::move(rhs.m_tyreSpareInstances)) {}

TyrePressureDevice &TyrePressureDevice::operator=(const TyrePressureDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_numberOfAxles = rhs.m_numberOfAxles;
    m_tyresAxle1 = rhs.m_tyresAxle1;
    m_tyresAxle2 = rhs.m_tyresAxle2;
    m_tyresAxle3 = rhs.m_tyresAxle3;
    m_tyresAxle4 = rhs.m_tyresAxle4;
    m_spareAxle = rhs.m_spareAxle;
    m_tyreInstances = rhs.m_tyreInstances;
    m_tyreSpareInstances = rhs.m_tyreSpareInstances;
  }
  return *this;
}

TyrePressureDevice &TyrePressureDevice::operator=(TyrePressureDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_numberOfAxles = rhs.m_numberOfAxles;
    m_tyresAxle1 = rhs.m_tyresAxle1;
    m_tyresAxle2 = rhs.m_tyresAxle2;
    m_tyresAxle3 = rhs.m_tyresAxle3;
    m_tyresAxle4 = rhs.m_tyresAxle4;
    m_spareAxle = rhs.m_spareAxle;
    m_tyreInstances = std::move(rhs.m_tyreInstances);
    m_tyreSpareInstances = std::move(rhs.m_tyreSpareInstances);
  }
  return *this;
}

AudioStereoDevice::AudioStereoDevice()
    : m_displayType(ConfigRequest::eConfigType::eAudioStereo),
      m_id(0),
      m_nameUTF8(),
      m_instance(),
      m_muteEnabled(false),
      m_circuitIds() {}

AudioStereoDevice::AudioStereoDevice(const AudioStereoDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_muteEnabled(rhs.m_muteEnabled),
      m_circuitIds(rhs.m_circuitIds) {}

AudioStereoDevice::AudioStereoDevice(AudioStereoDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_muteEnabled(rhs.m_muteEnabled),
      m_circuitIds(std::move(rhs.m_circuitIds)) {}

AudioStereoDevice &AudioStereoDevice::operator=(const AudioStereoDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_muteEnabled = rhs.m_muteEnabled;
    m_circuitIds = rhs.m_circuitIds;
  }
  return *this;
}

AudioStereoDevice &AudioStereoDevice::operator=(AudioStereoDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_muteEnabled = rhs.m_muteEnabled;
    m_circuitIds = std::move(rhs.m_circuitIds);
  }
  return *this;
}

ShoreFuseDevice::ShoreFuseDevice()
    : m_displayType(ConfigRequest::eConfigType::eShoreFuse),
      m_id(0),
      m_nameUTF8(),
      m_instance(),
      m_shoreFuseControlId() {}

ShoreFuseDevice::ShoreFuseDevice(const ShoreFuseDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_shoreFuseControlId(rhs.m_shoreFuseControlId) {}

ShoreFuseDevice::ShoreFuseDevice(ShoreFuseDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_shoreFuseControlId(std::move(rhs.m_shoreFuseControlId)) {}

ShoreFuseDevice &ShoreFuseDevice::operator=(const ShoreFuseDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_shoreFuseControlId = rhs.m_shoreFuseControlId;
  }
  return *this;
}

ShoreFuseDevice &ShoreFuseDevice::operator=(ShoreFuseDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_shoreFuseControlId = std::move(rhs.m_shoreFuseControlId);
  }
  return *this;
}

FantasticFanDevice::FantasticFanDevice()
    : m_displayType(ConfigRequest::eConfigType::eFantasticFan),
      m_id(0),
      m_nameUTF8(),
      m_instance(),
      m_directionForwardCircuitId(),
      m_directionReverseCircuitId(),
      m_lidOpenCircuitId(),
      m_lidCloseCircuitId(),
      m_fanCircuitId() {}

FantasticFanDevice::FantasticFanDevice(const FantasticFanDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_directionForwardCircuitId(rhs.m_directionForwardCircuitId),
      m_directionReverseCircuitId(rhs.m_directionReverseCircuitId),
      m_lidOpenCircuitId(rhs.m_lidOpenCircuitId),
      m_lidCloseCircuitId(rhs.m_lidCloseCircuitId),
      m_fanCircuitId(rhs.m_fanCircuitId) {}

FantasticFanDevice::FantasticFanDevice(FantasticFanDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_directionForwardCircuitId(std::move(rhs.m_directionForwardCircuitId)),
      m_directionReverseCircuitId(std::move(rhs.m_directionReverseCircuitId)),
      m_lidOpenCircuitId(std::move(rhs.m_lidOpenCircuitId)),
      m_lidCloseCircuitId(std::move(rhs.m_lidCloseCircuitId)),
      m_fanCircuitId(std::move(rhs.m_fanCircuitId)) {}

FantasticFanDevice &FantasticFanDevice::operator=(const FantasticFanDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_directionForwardCircuitId = rhs.m_directionForwardCircuitId;
    m_directionReverseCircuitId = rhs.m_directionReverseCircuitId;
    m_lidOpenCircuitId = rhs.m_lidOpenCircuitId;
    m_lidCloseCircuitId = rhs.m_lidCloseCircuitId;
    m_fanCircuitId = rhs.m_fanCircuitId;
  }
  return *this;
}

FantasticFanDevice &FantasticFanDevice::operator=(FantasticFanDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_directionForwardCircuitId = std::move(rhs.m_directionForwardCircuitId);
    m_directionReverseCircuitId = std::move(rhs.m_directionReverseCircuitId);
    m_lidOpenCircuitId = std::move(rhs.m_lidOpenCircuitId);
    m_lidCloseCircuitId = std::move(rhs.m_lidCloseCircuitId);
    m_fanCircuitId = std::move(rhs.m_fanCircuitId);
  }
  return *this;
}

ScreenConfigHeader::ScreenConfigHeader()
    : m_displayType(ConfigRequest::eConfigType::eScreenConfig),
      m_id(0),
      m_targetDisplayType(0),
      m_targetId(0),
      m_confirmationType(0),
      m_smoothStart(0),
      m_index(0),
      m_parentIndex(0),
      m_controlId(0) {}

ScreenConfigHeader::ScreenConfigHeader(const ScreenConfigHeader &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_targetDisplayType(rhs.m_targetDisplayType),
      m_targetId(rhs.m_targetId),
      m_confirmationType(rhs.m_confirmationType),
      m_smoothStart(rhs.m_smoothStart),
      m_index(rhs.m_index),
      m_parentIndex(rhs.m_parentIndex),
      m_controlId(rhs.m_controlId) {}

ScreenConfigHeader::ScreenConfigHeader(ScreenConfigHeader &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_targetDisplayType(rhs.m_targetDisplayType),
      m_targetId(rhs.m_targetId),
      m_confirmationType(rhs.m_confirmationType),
      m_smoothStart(rhs.m_smoothStart),
      m_index(rhs.m_index),
      m_parentIndex(rhs.m_parentIndex),
      m_controlId(rhs.m_controlId) {}

ScreenConfigHeader &ScreenConfigHeader::operator=(const ScreenConfigHeader &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_targetDisplayType = rhs.m_targetDisplayType;
    m_targetId = rhs.m_targetId;
    m_confirmationType = rhs.m_confirmationType;
    m_smoothStart = rhs.m_smoothStart;
    m_index = rhs.m_index;
    m_parentIndex = rhs.m_parentIndex;
    m_controlId = rhs.m_controlId;
  }
  return *this;
}

ScreenConfigHeader &ScreenConfigHeader::operator=(ScreenConfigHeader &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_targetDisplayType = rhs.m_targetDisplayType;
    m_targetId = rhs.m_targetId;
    m_confirmationType = rhs.m_confirmationType;
    m_smoothStart = rhs.m_smoothStart;
    m_index = rhs.m_index;
    m_parentIndex = rhs.m_parentIndex;
    m_controlId = rhs.m_controlId;
  }
  return *this;
}

ScreenConfigPageImageItem::ScreenConfigPageImageItem()
    : m_header(),
      m_locationX(0.0f),
      m_locationY(0.0f),
      m_targetX(0.0f),
      m_targetY(0.0f),
      m_icon(0),
      m_name(),
      m_hideWhenOff(false) {}

ScreenConfigPageImageItem::ScreenConfigPageImageItem(const ScreenConfigPageImageItem &rhs)
    : m_header(rhs.m_header),
      m_locationX(rhs.m_locationX),
      m_locationY(rhs.m_locationY),
      m_targetX(rhs.m_targetX),
      m_targetY(rhs.m_targetY),
      m_icon(rhs.m_icon),
      m_name(rhs.m_name),
      m_hideWhenOff(rhs.m_hideWhenOff) {}

ScreenConfigPageImageItem::ScreenConfigPageImageItem(ScreenConfigPageImageItem &&rhs)
    : m_header(std::move(rhs.m_header)),
      m_locationX(rhs.m_locationX),
      m_locationY(rhs.m_locationY),
      m_targetX(rhs.m_targetX),
      m_targetY(rhs.m_targetY),
      m_icon(rhs.m_icon),
      m_name(std::move(rhs.m_name)),
      m_hideWhenOff(rhs.m_hideWhenOff) {}

ScreenConfigPageImageItem &ScreenConfigPageImageItem::operator=(const ScreenConfigPageImageItem &rhs) {
  if (this != &rhs) {
    m_header = rhs.m_header;
    m_locationX = rhs.m_locationX;
    m_locationY = rhs.m_locationY;
    m_targetX = rhs.m_targetX;
    m_targetY = rhs.m_targetY;
    m_icon = rhs.m_icon;
    m_name = rhs.m_name;
    m_hideWhenOff = rhs.m_hideWhenOff;
  }
  return *this;
}

ScreenConfigPageImageItem &ScreenConfigPageImageItem::operator=(ScreenConfigPageImageItem &&rhs) {
  if (this != &rhs) {
    m_header = std::move(rhs.m_header);
    m_locationX = rhs.m_locationX;
    m_locationY = rhs.m_locationY;
    m_targetX = rhs.m_targetX;
    m_targetY = rhs.m_targetY;
    m_icon = rhs.m_icon;
    m_name = std::move(rhs.m_name);
    m_hideWhenOff = rhs.m_hideWhenOff;
  }
  return *this;
}

ScreenConfigPageGridItem::ScreenConfigPageGridItem()
    : m_header(),
      m_gridX(0),
      m_gridY(0),
      m_targetX(0.0f),
      m_targetY(0.0f),
      m_targetWidth(0.0f),
      m_targetHeight(0.0f),
      m_icon(0),
      m_name(),
      m_columnSpan(1),
      m_rowSpan(1),
      m_doubleThrowType(0) {}

ScreenConfigPageGridItem::ScreenConfigPageGridItem(const ScreenConfigPageGridItem &rhs)
    : m_header(rhs.m_header),
      m_gridX(rhs.m_gridX),
      m_gridY(rhs.m_gridY),
      m_targetX(rhs.m_targetX),
      m_targetY(rhs.m_targetY),
      m_targetWidth(rhs.m_targetWidth),
      m_targetHeight(rhs.m_targetHeight),
      m_icon(rhs.m_icon),
      m_name(rhs.m_name),
      m_columnSpan(rhs.m_columnSpan),
      m_rowSpan(rhs.m_rowSpan),
      m_doubleThrowType(rhs.m_doubleThrowType) {}

ScreenConfigPageGridItem::ScreenConfigPageGridItem(ScreenConfigPageGridItem &&rhs)
    : m_header(std::move(rhs.m_header)),
      m_gridX(rhs.m_gridX),
      m_gridY(rhs.m_gridY),
      m_targetX(rhs.m_targetX),
      m_targetY(rhs.m_targetY),
      m_targetWidth(rhs.m_targetWidth),
      m_targetHeight(rhs.m_targetHeight),
      m_icon(rhs.m_icon),
      m_name(std::move(rhs.m_name)),
      m_columnSpan(rhs.m_columnSpan),
      m_rowSpan(rhs.m_rowSpan),
      m_doubleThrowType(rhs.m_doubleThrowType) {}

ScreenConfigPageGridItem &ScreenConfigPageGridItem::operator=(const ScreenConfigPageGridItem &rhs) {
  if (this != &rhs) {
    m_header = rhs.m_header;
    m_gridX = rhs.m_gridX;
    m_gridY = rhs.m_gridY;
    m_targetX = rhs.m_targetX;
    m_targetY = rhs.m_targetY;
    m_targetWidth = rhs.m_targetWidth;
    m_targetHeight = rhs.m_targetHeight;
    m_icon = rhs.m_icon;
    m_name = rhs.m_name;
    m_columnSpan = rhs.m_columnSpan;
    m_rowSpan = rhs.m_rowSpan;
    m_doubleThrowType = rhs.m_doubleThrowType;
  }
  return *this;
}

ScreenConfigPageGridItem &ScreenConfigPageGridItem::operator=(ScreenConfigPageGridItem &&rhs) {
  if (this != &rhs) {
    m_header = std::move(rhs.m_header);
    m_gridX = rhs.m_gridX;
    m_gridY = rhs.m_gridY;
    m_targetX = rhs.m_targetX;
    m_targetY = rhs.m_targetY;
    m_targetWidth = rhs.m_targetWidth;
    m_targetHeight = rhs.m_targetHeight;
    m_icon = rhs.m_icon;
    m_name = std::move(rhs.m_name);
    m_columnSpan = rhs.m_columnSpan;
    m_rowSpan = rhs.m_rowSpan;
    m_doubleThrowType = rhs.m_doubleThrowType;
  }
  return *this;
}

ScreenConfigPageImage::ScreenConfigPageImage()
    : m_header(),
      m_gridX(0),
      m_gridY(0),
      m_gridWidth(0),
      m_gridHeight(0),
      m_sourceWidth(0.0f),
      m_sourceHeight(0.0f),
      m_targetX(0.0f),
      m_targetY(0.0f),
      m_targetWidth(0.0f),
      m_targetHeight(0.0f),
      m_fileName(),
      m_backgroundColourR(0),
      m_backgroundColourG(0),
      m_backgroundColourB(0),
      m_showBackground(0),
      m_cropToFit(0) {}

ScreenConfigPageImage::ScreenConfigPageImage(const ScreenConfigPageImage &rhs)
    : m_header(rhs.m_header),
      m_gridX(rhs.m_gridX),
      m_gridY(rhs.m_gridY),
      m_gridWidth(rhs.m_gridWidth),
      m_gridHeight(rhs.m_gridHeight),
      m_sourceWidth(rhs.m_sourceWidth),
      m_sourceHeight(rhs.m_sourceHeight),
      m_targetX(rhs.m_targetX),
      m_targetY(rhs.m_targetY),
      m_targetWidth(rhs.m_targetWidth),
      m_targetHeight(rhs.m_targetHeight),
      m_fileName(rhs.m_fileName),
      m_backgroundColourR(rhs.m_backgroundColourR),
      m_backgroundColourG(rhs.m_backgroundColourG),
      m_backgroundColourB(rhs.m_backgroundColourB),
      m_showBackground(rhs.m_showBackground),
      m_cropToFit(rhs.m_cropToFit) {}

ScreenConfigPageImage::ScreenConfigPageImage(ScreenConfigPageImage &&rhs)
    : m_header(std::move(rhs.m_header)),
      m_gridX(rhs.m_gridX),
      m_gridY(rhs.m_gridY),
      m_gridWidth(rhs.m_gridWidth),
      m_gridHeight(rhs.m_gridHeight),
      m_sourceWidth(rhs.m_sourceWidth),
      m_sourceHeight(rhs.m_sourceHeight),
      m_targetX(rhs.m_targetX),
      m_targetY(rhs.m_targetY),
      m_targetWidth(rhs.m_targetWidth),
      m_targetHeight(rhs.m_targetHeight),
      m_fileName(std::move(rhs.m_fileName)),
      m_backgroundColourR(rhs.m_backgroundColourR),
      m_backgroundColourG(rhs.m_backgroundColourG),
      m_backgroundColourB(rhs.m_backgroundColourB),
      m_showBackground(rhs.m_showBackground),
      m_cropToFit(rhs.m_cropToFit) {}

ScreenConfigPageImage &ScreenConfigPageImage::operator=(const ScreenConfigPageImage &rhs) {
  if (this != &rhs) {
    m_header = rhs.m_header;
    m_gridX = rhs.m_gridX;
    m_gridY = rhs.m_gridY;
    m_gridWidth = rhs.m_gridWidth;
    m_gridHeight = rhs.m_gridHeight;
    m_sourceWidth = rhs.m_sourceWidth;
    m_sourceHeight = rhs.m_sourceHeight;
    m_targetX = rhs.m_targetX;
    m_targetY = rhs.m_targetY;
    m_targetWidth = rhs.m_targetWidth;
    m_targetHeight = rhs.m_targetHeight;
    m_fileName = rhs.m_fileName;
    m_backgroundColourR = rhs.m_backgroundColourR;
    m_backgroundColourG = rhs.m_backgroundColourG;
    m_backgroundColourB = rhs.m_backgroundColourB;
    m_showBackground = rhs.m_showBackground;
    m_cropToFit = rhs.m_cropToFit;
  }
  return *this;
}

ScreenConfigPageImage &ScreenConfigPageImage::operator=(ScreenConfigPageImage &&rhs) {
  if (this != &rhs) {
    m_header = std::move(rhs.m_header);
    m_gridX = rhs.m_gridX;
    m_gridY = rhs.m_gridY;
    m_gridWidth = rhs.m_gridWidth;
    m_gridHeight = rhs.m_gridHeight;
    m_sourceWidth = rhs.m_sourceWidth;
    m_sourceHeight = rhs.m_sourceHeight;
    m_targetX = rhs.m_targetX;
    m_targetY = rhs.m_targetY;
    m_targetWidth = rhs.m_targetWidth;
    m_targetHeight = rhs.m_targetHeight;
    m_fileName = std::move(rhs.m_fileName);
    m_backgroundColourR = rhs.m_backgroundColourR;
    m_backgroundColourG = rhs.m_backgroundColourG;
    m_backgroundColourB = rhs.m_backgroundColourB;
    m_showBackground = rhs.m_showBackground;
    m_cropToFit = rhs.m_cropToFit;
  }
  return *this;
}

ScreenConfigPage::ScreenConfigPage() : m_header() {}

ScreenConfigPage::ScreenConfigPage(const ScreenConfigPage &rhs) : m_header(rhs.m_header) {}

ScreenConfigPage::ScreenConfigPage(ScreenConfigPage &&rhs) : m_header(std::move(rhs.m_header)) {}

ScreenConfigPage &ScreenConfigPage::operator=(const ScreenConfigPage &rhs) {
  if (this != &rhs) {
    m_header = rhs.m_header;
  }
  return *this;
}

ScreenConfigPage &ScreenConfigPage::operator=(ScreenConfigPage &&rhs) {
  if (this != &rhs) {
    m_header = std::move(rhs.m_header);
  }
  return *this;
}

ScreenConfigMode::ScreenConfigMode() : m_header(), m_name() {}

ScreenConfigMode::ScreenConfigMode(const ScreenConfigMode &rhs) : m_header(rhs.m_header), m_name(rhs.m_name) {}

ScreenConfigMode::ScreenConfigMode(ScreenConfigMode &&rhs)
    : m_header(std::move(rhs.m_header)), m_name(std::move(rhs.m_name)) {}

ScreenConfigMode &ScreenConfigMode::operator=(const ScreenConfigMode &rhs) {
  if (this != &rhs) {
    m_header = rhs.m_header;
    m_name = rhs.m_name;
  }
  return *this;
}

ScreenConfigMode &ScreenConfigMode::operator=(ScreenConfigMode &&rhs) {
  if (this != &rhs) {
    m_header = std::move(rhs.m_header);
    m_name = std::move(rhs.m_name);
  }
  return *this;
}

ScreenConfig::ScreenConfig()
    : m_header(), m_gridWidth(0), m_gridHeight(0), m_landscape(0), m_displayName(), m_relativePath() {}

ScreenConfig::ScreenConfig(const ScreenConfig &rhs)
    : m_header(rhs.m_header),
      m_gridWidth(rhs.m_gridWidth),
      m_gridHeight(rhs.m_gridHeight),
      m_landscape(rhs.m_landscape),
      m_displayName(rhs.m_displayName),
      m_relativePath(rhs.m_relativePath) {}

ScreenConfig::ScreenConfig(ScreenConfig &&rhs)
    : m_header(std::move(rhs.m_header)),
      m_gridWidth(rhs.m_gridWidth),
      m_gridHeight(rhs.m_gridHeight),
      m_landscape(rhs.m_landscape),
      m_displayName(std::move(rhs.m_displayName)),
      m_relativePath(std::move(rhs.m_relativePath)) {}

ScreenConfig &ScreenConfig::operator=(const ScreenConfig &rhs) {
  if (this != &rhs) {
    m_header = rhs.m_header;
    m_gridWidth = rhs.m_gridWidth;
    m_gridHeight = rhs.m_gridHeight;
    m_landscape = rhs.m_landscape;
    m_displayName = rhs.m_displayName;
    m_relativePath = rhs.m_relativePath;
  }
  return *this;
}

ScreenConfig &ScreenConfig::operator=(ScreenConfig &&rhs) {
  if (this != &rhs) {
    m_header = std::move(rhs.m_header);
    m_gridWidth = rhs.m_gridWidth;
    m_gridHeight = rhs.m_gridHeight;
    m_landscape = rhs.m_landscape;
    m_displayName = std::move(rhs.m_displayName);
    m_relativePath = std::move(rhs.m_relativePath);
  }
  return *this;
}

FavouritesInfo::FavouritesInfo()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_id(0),
      m_targetDisplayType(0),
      m_targetId(0),
      m_x(0),
      m_y(0) {}

FavouritesInfo::FavouritesInfo(const FavouritesInfo &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_targetDisplayType(rhs.m_targetDisplayType),
      m_targetId(rhs.m_targetId),
      m_x(rhs.m_x),
      m_y(rhs.m_y) {}

FavouritesInfo::FavouritesInfo(FavouritesInfo &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_targetDisplayType(rhs.m_targetDisplayType),
      m_targetId(rhs.m_targetId),
      m_x(rhs.m_x),
      m_y(rhs.m_y) {}

FavouritesInfo &FavouritesInfo::operator=(const FavouritesInfo &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_targetDisplayType = rhs.m_targetDisplayType;
    m_targetId = rhs.m_targetId;
    m_x = rhs.m_x;
    m_y = rhs.m_y;
  }
  return *this;
}

FavouritesInfo &FavouritesInfo::operator=(FavouritesInfo &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_targetDisplayType = rhs.m_targetDisplayType;
    m_targetId = rhs.m_targetId;
    m_x = rhs.m_x;
    m_y = rhs.m_y;
  }
  return *this;
}

Device::Device()
    : m_displayType(ConfigRequest::eConfigType::eNone),
      m_nameUTF8(),
      m_dipswitch(0),
      m_sourceAddress(0),
      m_conflict(false),
      m_deviceType(Device::eNone),
      m_valid(false),
      m_transient(false),
      m_version() {}

Device::Device(const Device &rhs)
    : m_displayType(rhs.m_displayType),
      m_nameUTF8(rhs.m_nameUTF8),
      m_dipswitch(rhs.m_dipswitch),
      m_sourceAddress(rhs.m_sourceAddress),
      m_conflict(rhs.m_conflict),
      m_deviceType(rhs.m_deviceType),
      m_valid(rhs.m_valid),
      m_transient(rhs.m_transient),
      m_version(rhs.m_version) {}

Device::Device(Device &&rhs)
    : m_displayType(rhs.m_displayType),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_dipswitch(rhs.m_dipswitch),
      m_sourceAddress(rhs.m_sourceAddress),
      m_conflict(rhs.m_conflict),
      m_deviceType(rhs.m_deviceType),
      m_valid(rhs.m_valid),
      m_transient(rhs.m_transient),
      m_version(std::move(rhs.m_version)) {}

Device &Device::operator=(const Device &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_dipswitch = rhs.m_dipswitch;
    m_sourceAddress = rhs.m_sourceAddress;
    m_conflict = rhs.m_conflict;
    m_deviceType = rhs.m_deviceType;
    m_valid = rhs.m_valid;
    m_transient = rhs.m_transient;
    m_version = rhs.m_version;
  }
  return *this;
}

Device &Device::operator=(Device &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_dipswitch = rhs.m_dipswitch;
    m_sourceAddress = rhs.m_sourceAddress;
    m_conflict = rhs.m_conflict;
    m_deviceType = rhs.m_deviceType;
    m_valid = rhs.m_valid;
    m_transient = rhs.m_transient;
    m_version = std::move(rhs.m_version);
  }
  return *this;
}

GNSSDevice::GNSSDevice()
    : m_displayType(ConfigRequest::eConfigType::eNone), m_id(0), m_nameUTF8(), m_instance(), m_isExternal(false) {}

GNSSDevice::GNSSDevice(const GNSSDevice &rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(rhs.m_nameUTF8),
      m_instance(rhs.m_instance),
      m_isExternal(rhs.m_isExternal) {}

GNSSDevice::GNSSDevice(GNSSDevice &&rhs)
    : m_displayType(rhs.m_displayType),
      m_id(rhs.m_id),
      m_nameUTF8(std::move(rhs.m_nameUTF8)),
      m_instance(std::move(rhs.m_instance)),
      m_isExternal(rhs.m_isExternal) {}

GNSSDevice &GNSSDevice::operator=(const GNSSDevice &rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = rhs.m_nameUTF8;
    m_instance = rhs.m_instance;
    m_isExternal = rhs.m_isExternal;
  }
  return *this;
}

GNSSDevice &GNSSDevice::operator=(GNSSDevice &&rhs) {
  if (this != &rhs) {
    m_displayType = rhs.m_displayType;
    m_id = rhs.m_id;
    m_nameUTF8 = std::move(rhs.m_nameUTF8);
    m_instance = std::move(rhs.m_instance);
    m_isExternal = rhs.m_isExternal;
  }
  return *this;
}

UiRelationshipMsg::UiRelationshipMsg()
    : m_displaytype(ConfigRequest::eConfigType::eNone),
      m_id(0),
      m_primarytype(eNone),
      m_secondarytype(eNone),
      m_primaryid(0),
      m_secondaryid(0),
      m_relationshiptype(eNormal),
      m_primaryconfigaddress(0),
      m_secondaryconfigaddress(0),
      m_primarychannelindex(0),
      m_secondarychannelindex(0) {}

UiRelationshipMsg::UiRelationshipMsg(const UiRelationshipMsg &rhs)
    : m_displaytype(rhs.m_displaytype),
      m_id(rhs.m_id),
      m_primarytype(rhs.m_primarytype),
      m_secondarytype(rhs.m_secondarytype),
      m_primaryid(rhs.m_primaryid),
      m_secondaryid(rhs.m_secondaryid),
      m_relationshiptype(rhs.m_relationshiptype),
      m_primaryconfigaddress(rhs.m_primaryconfigaddress),
      m_secondaryconfigaddress(rhs.m_secondaryconfigaddress),
      m_primarychannelindex(rhs.m_primarychannelindex),
      m_secondarychannelindex(rhs.m_secondarychannelindex) {}

UiRelationshipMsg::UiRelationshipMsg(UiRelationshipMsg &&rhs)
    : m_displaytype(rhs.m_displaytype),
      m_id(rhs.m_id),
      m_primarytype(rhs.m_primarytype),
      m_secondarytype(rhs.m_secondarytype),
      m_primaryid(rhs.m_primaryid),
      m_secondaryid(rhs.m_secondaryid),
      m_relationshiptype(rhs.m_relationshiptype),
      m_primaryconfigaddress(rhs.m_primaryconfigaddress),
      m_secondaryconfigaddress(rhs.m_secondaryconfigaddress),
      m_primarychannelindex(rhs.m_primarychannelindex),
      m_secondarychannelindex(rhs.m_secondarychannelindex) {}

UiRelationshipMsg &UiRelationshipMsg::operator=(const UiRelationshipMsg &rhs) {
  if (this != &rhs) {
    m_displaytype = rhs.m_displaytype;
    m_id = rhs.m_id;
    m_primarytype = rhs.m_primarytype;
    m_secondarytype = rhs.m_secondarytype;
    m_primaryid = rhs.m_primaryid;
    m_secondaryid = rhs.m_secondaryid;
    m_relationshiptype = rhs.m_relationshiptype;
    m_primaryconfigaddress = rhs.m_primaryconfigaddress;
    m_secondaryconfigaddress = rhs.m_secondaryconfigaddress;
    m_primarychannelindex = rhs.m_primarychannelindex;
    m_secondarychannelindex = rhs.m_secondarychannelindex;
  }
  return *this;
}

UiRelationshipMsg &UiRelationshipMsg::operator=(UiRelationshipMsg &&rhs) {
  if (this != &rhs) {
    m_displaytype = rhs.m_displaytype;
    m_id = rhs.m_id;
    m_primarytype = rhs.m_primarytype;
    m_secondarytype = rhs.m_secondarytype;
    m_primaryid = rhs.m_primaryid;
    m_secondaryid = rhs.m_secondaryid;
    m_relationshiptype = rhs.m_relationshiptype;
    m_primaryconfigaddress = rhs.m_primaryconfigaddress;
    m_secondaryconfigaddress = rhs.m_secondaryconfigaddress;
    m_primarychannelindex = rhs.m_primarychannelindex;
    m_secondarychannelindex = rhs.m_secondarychannelindex;
  }
  return *this;
}

BinaryLogicStateMsg::BinaryLogicStateMsg()
    : m_displaytype(ConfigRequest::eConfigType::eNone), m_id(0), m_address(0), m_nameutf8() {}

BinaryLogicStateMsg::BinaryLogicStateMsg(const BinaryLogicStateMsg &rhs)
    : m_displaytype(rhs.m_displaytype), m_id(rhs.m_id), m_address(rhs.m_address), m_nameutf8(rhs.m_nameutf8) {}

BinaryLogicStateMsg::BinaryLogicStateMsg(BinaryLogicStateMsg &&rhs)
    : m_displaytype(rhs.m_displaytype),
      m_id(rhs.m_id),
      m_address(rhs.m_address),
      m_nameutf8(std::move(rhs.m_nameutf8)) {}

BinaryLogicStateMsg &BinaryLogicStateMsg::operator=(const BinaryLogicStateMsg &rhs) {
  if (this != &rhs) {
    m_displaytype = rhs.m_displaytype;
    m_id = rhs.m_id;
    m_address = rhs.m_address;
    m_nameutf8 = rhs.m_nameutf8;
  }
  return *this;
}

BinaryLogicStateMsg &BinaryLogicStateMsg::operator=(BinaryLogicStateMsg &&rhs) {
  if (this != &rhs) {
    m_displaytype = rhs.m_displaytype;
    m_id = rhs.m_id;
    m_address = rhs.m_address;
    m_nameutf8 = std::move(rhs.m_nameutf8);
  }
  return *this;
}

SwitchPositiveNegtive::SwitchPositiveNegtive()
    : m_channelAddress(0), m_channel(0), m_mode(eSwitchBatteryPositive), m_binaryStatusIndex(0) {}

SwitchPositiveNegtive::SwitchPositiveNegtive(const SwitchPositiveNegtive &rhs)
    : m_channelAddress(rhs.m_channelAddress),
      m_channel(rhs.m_channel),
      m_mode(rhs.m_mode),
      m_binaryStatusIndex(rhs.m_binaryStatusIndex) {}

SwitchPositiveNegtive::SwitchPositiveNegtive(SwitchPositiveNegtive &&rhs)
    : m_channelAddress(rhs.m_channelAddress),
      m_channel(rhs.m_channel),
      m_mode(rhs.m_mode),
      m_binaryStatusIndex(rhs.m_binaryStatusIndex) {}

SwitchPositiveNegtive &SwitchPositiveNegtive::operator=(const SwitchPositiveNegtive &rhs) {
  if (this != &rhs) {
    m_channelAddress = rhs.m_channelAddress;
    m_channel = rhs.m_channel;
    m_mode = rhs.m_mode;
    m_binaryStatusIndex = rhs.m_binaryStatusIndex;
  }
  return *this;
}

SwitchPositiveNegtive &SwitchPositiveNegtive::operator=(SwitchPositiveNegtive &&rhs) {
  if (this != &rhs) {
    m_channelAddress = rhs.m_channelAddress;
    m_channel = rhs.m_channel;
    m_mode = rhs.m_mode;
    m_binaryStatusIndex = rhs.m_binaryStatusIndex;
  }
  return *this;
}

RTCoreMapEntry::RTCoreMapEntry()
    : m_displaytype(ConfigRequest::eConfigType::eNone),
      m_circuitLoads(),
      m_dcMeters(),
      m_monitoringDevice(),
      m_switchPositiveNegtive(),
      m_alarms(),
      m_circuits() {}

RTCoreMapEntry::RTCoreMapEntry(const RTCoreMapEntry &rhs)
    : m_displaytype(rhs.m_displaytype),
      m_circuitLoads(rhs.m_circuitLoads),
      m_dcMeters(rhs.m_dcMeters),
      m_monitoringDevice(rhs.m_monitoringDevice),
      m_switchPositiveNegtive(rhs.m_switchPositiveNegtive),
      m_alarms(rhs.m_alarms),
      m_circuits(rhs.m_circuits) {}

RTCoreMapEntry::RTCoreMapEntry(RTCoreMapEntry &&rhs)
    : m_displaytype(rhs.m_displaytype),
      m_circuitLoads(std::move(rhs.m_circuitLoads)),
      m_dcMeters(std::move(rhs.m_dcMeters)),
      m_monitoringDevice(std::move(rhs.m_monitoringDevice)),
      m_switchPositiveNegtive(std::move(rhs.m_switchPositiveNegtive)),
      m_alarms(std::move(rhs.m_alarms)),
      m_circuits(std::move(rhs.m_circuits)) {}

RTCoreMapEntry &RTCoreMapEntry::operator=(const RTCoreMapEntry &rhs) {
  if (this != &rhs) {
    m_displaytype = rhs.m_displaytype;
    m_circuitLoads = rhs.m_circuitLoads;
    m_dcMeters = rhs.m_dcMeters;
    m_monitoringDevice = rhs.m_monitoringDevice;
    m_switchPositiveNegtive = rhs.m_switchPositiveNegtive;
    m_alarms = rhs.m_alarms;
    m_circuits = rhs.m_circuits;
  }
  return *this;
}

RTCoreMapEntry &RTCoreMapEntry::operator=(RTCoreMapEntry &&rhs) {
  if (this != &rhs) {
    m_displaytype = rhs.m_displaytype;
    m_circuitLoads = std::move(rhs.m_circuitLoads);
    m_dcMeters = std::move(rhs.m_dcMeters);
    m_monitoringDevice = std::move(rhs.m_monitoringDevice);
    m_switchPositiveNegtive = std::move(rhs.m_switchPositiveNegtive);
    m_alarms = std::move(rhs.m_alarms);
    m_circuits = std::move(rhs.m_circuits);
  }
  return *this;
}

RTCoreLogicalIdToDeviceConfig::RTCoreLogicalIdToDeviceConfig()
    : m_circuitLoads(), m_dcMeters(), m_monitoringDevice(), m_switchPositiveNegtive() {}

RTCoreLogicalIdToDeviceConfig::RTCoreLogicalIdToDeviceConfig(const RTCoreLogicalIdToDeviceConfig &rhs)
    : m_circuitLoads(rhs.m_circuitLoads),
      m_dcMeters(rhs.m_dcMeters),
      m_monitoringDevice(rhs.m_monitoringDevice),
      m_switchPositiveNegtive(rhs.m_switchPositiveNegtive) {}

RTCoreLogicalIdToDeviceConfig::RTCoreLogicalIdToDeviceConfig(RTCoreLogicalIdToDeviceConfig &&rhs)
    : m_circuitLoads(std::move(rhs.m_circuitLoads)),
      m_dcMeters(std::move(rhs.m_dcMeters)),
      m_monitoringDevice(std::move(rhs.m_monitoringDevice)),
      m_switchPositiveNegtive(std::move(rhs.m_switchPositiveNegtive)) {}

RTCoreLogicalIdToDeviceConfig &RTCoreLogicalIdToDeviceConfig::operator=(const RTCoreLogicalIdToDeviceConfig &rhs) {
  if (this != &rhs) {
    m_circuitLoads = rhs.m_circuitLoads;
    m_dcMeters = rhs.m_dcMeters;
    m_monitoringDevice = rhs.m_monitoringDevice;
    m_switchPositiveNegtive = rhs.m_switchPositiveNegtive;
  }
  return *this;
}

RTCoreLogicalIdToDeviceConfig &RTCoreLogicalIdToDeviceConfig::operator=(RTCoreLogicalIdToDeviceConfig &&rhs) {
  if (this != &rhs) {
    m_circuitLoads = std::move(rhs.m_circuitLoads);
    m_dcMeters = std::move(rhs.m_dcMeters);
    m_monitoringDevice = std::move(rhs.m_monitoringDevice);
    m_switchPositiveNegtive = std::move(rhs.m_switchPositiveNegtive);
  }
  return *this;
}

CZoneRawConfig::CZoneRawConfig() : m_type(0), m_length(0), m_sizeOfData(0), m_contents() {}

CZoneRawConfig::CZoneRawConfig(const CZoneRawConfig &rhs)
    : m_type(rhs.m_type), m_length(rhs.m_length), m_sizeOfData(rhs.m_sizeOfData), m_contents(rhs.m_contents) {}

CZoneRawConfig::CZoneRawConfig(CZoneRawConfig &&rhs)
    : m_type(rhs.m_type),
      m_length(rhs.m_length),
      m_sizeOfData(rhs.m_sizeOfData),
      m_contents(std::move(rhs.m_contents)) {}

CZoneRawConfig &CZoneRawConfig::operator=(const CZoneRawConfig &rhs) {
  if (this != &rhs) {
    m_type = rhs.m_type;
    m_length = rhs.m_length;
    m_sizeOfData = rhs.m_sizeOfData;
    m_contents = rhs.m_contents;
  }
  return *this;
}

CZoneRawConfig &CZoneRawConfig::operator=(CZoneRawConfig &&rhs) {
  if (this != &rhs) {
    m_type = rhs.m_type;
    m_length = rhs.m_length;
    m_sizeOfData = rhs.m_sizeOfData;
    m_contents = std::move(rhs.m_contents);
  }
  return *this;
}

Categories::Categories() : m_items() {}

Categories::Categories(const Categories &rhs) : m_items(rhs.m_items) {}

Categories::Categories(Categories &&rhs) : m_items(std::move(rhs.m_items)) {}

Categories &Categories::operator=(const Categories &rhs) {
  if (this != &rhs) {
    m_items = rhs.m_items;
  }
  return *this;
}

Categories &Categories::operator=(Categories &&rhs) {
  if (this != &rhs) {
    m_items = std::move(rhs.m_items);
  }
  return *this;
}

void to_json(nlohmann::json &j, const Categories &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const CategoryItem &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const AlarmLimit &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const Instance &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const Alarm &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const MeteringDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const MonitoringDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const DataId &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ACMainDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ACMainContactorDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ACMainLoadGroupDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const InverterChargerDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const HVACDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ThirdPartyGeneratorDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ZipdeeAwningDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const BinarySignalBitAddress &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const TyrePressureDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const AudioStereoDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ShoreFuseDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const CircuitDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const CircuitLoad &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const FantasticFanDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ScreenConfigPageImageItem &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ScreenConfigMode &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ScreenConfigHeader &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ScreenConfigPageGridItem &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ScreenConfigPageImage &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ScreenConfigPage &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const ScreenConfig &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const FavouritesInfo &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const Device &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const GNSSDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const EngineDevice &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const UiRelationshipMsg &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const BinaryLogicStateMsg &c) { j = c.tojson(); }
void to_json(nlohmann::json &j, const Event &c) { j = c.tojson(); }

json Categories::tojson() const {
  json result;
  result["Items"] = m_items;
  return result;
}

json CategoryItem::tojson() const {
  json result;

  result["NameUTF8"] = m_nameUTF8;
  result["Enabled"] = m_enabled;
  result["Index"] = m_index;

  return result;
}

json ConfigResult::tojson() const {
  json result;
  result["Status"] = to_string(m_status);

  if (m_alarms.size() > 0) {
    result["Alarms"] = m_alarms;
  }
  if (m_dcs.size() > 0) {
    result["DCs"] = m_dcs;
  }
  if (m_acs.size() > 0) {
    result["ACs"] = m_acs;
  }
  if (m_pressures.size() > 0) {
    result["Pressures"] = m_pressures;
  }
  if (m_tanks.size() > 0) {
    result["Tanks"] = m_tanks;
  }
  if (m_temperatures.size() > 0) {
    result["Temperatures"] = m_temperatures;
  }
  if (m_acMains.size() > 0) {
    result["ACMains"] = m_acMains;
  }
  if (m_inverterChargers.size() > 0) {
    result["InverterChargers"] = m_inverterChargers;
  }
  if (m_hvacs.size() > 0) {
    result["HVACs"] = m_hvacs;
  }
  if (m_zipdeeAwnings.size() > 0) {
    result["ZipdeeAwnings"] = m_zipdeeAwnings;
  }
  if (m_thirdPartyGenerators.size() > 0) {
    result["ThirdPartyGenerators"] = m_thirdPartyGenerators;
  }
  if (m_tyrePressures.size() > 0) {
    result["TyrePressures"] = m_tyrePressures;
  }
  if (m_audioStereos.size() > 0) {
    result["AudioStereos"] = m_audioStereos;
  }
  if (m_shoreFuses.size() > 0) {
    result["ShoreFuses"] = m_shoreFuses;
  }
  if (m_circuits.size() > 0) {
    result["Circuits"] = m_circuits;
  }
  if (m_modes.size() > 0) {
    result["Modes"] = m_modes;
  }
  if (m_fantasticFans.size() > 0) {
    result["FantasticFans"] = m_fantasticFans;
  }
  if (m_screenConfigPageImageItems.size() > 0) {
    result["ScreenConfigPageImageItems"] = m_screenConfigPageImageItems;
  }
  if (m_screenConfigPageGridItems.size() > 0) {
    result["ScreenConfigPageGridItems"] = m_screenConfigPageGridItems;
  }
  if (m_screenConfigPageImages.size() > 0) {
    result["ScreenConfigPageImages"] = m_screenConfigPageImages;
  }
  if (m_screenConfigPages.size() > 0) {
    result["ScreenConfigPages"] = m_screenConfigPages;
  }
  if (m_screenConfigModes.size() > 0) {
    result["ScreenConfigModes"] = m_screenConfigModes;
  }
  if (m_screenConfigs.size() > 0) {
    result["ScreenConfigs"] = m_screenConfigs;
  }
  if (m_favouritesModes.size() > 0) {
    result["FavouritesModes"] = m_favouritesModes;
  }
  if (m_favouritesControls.size() > 0) {
    result["FavouritesControls"] = m_favouritesControls;
  }
  if (m_favouritesMonitorings.size() > 0) {
    result["FavouritesMonitorings"] = m_favouritesMonitorings;
  }
  if (m_favouritesAlarms.size() > 0) {
    result["FavouritesAlarms"] = m_favouritesAlarms;
  }
  if (m_favouritesACMains.size() > 0) {
    result["FavouritesACMains"] = m_favouritesACMains;
  }
  if (m_favouritesInverterChargers.size() > 0) {
    result["FavouritesInverterChargers"] = m_favouritesInverterChargers;
  }
  if (m_favouritesBoatViews.size() > 0) {
    result["FavouritesBoatViews"] = m_favouritesBoatViews;
  }
  if (m_devices.size() > 0) {
    result["Devices"] = m_devices;
  }
  if (m_gnss.size() > 0) {
    result["GNSS"] = m_gnss;
  }
  if (m_engines.size() > 0) {
    result["Engines"] = m_engines;
  }
  if (m_uiRelationships.size() > 0) {
    result["UiRelationships"] = m_uiRelationships;
  }
  if (m_binaryLogicStates.size() > 0) {
    result["BinaryLogicStates"] = m_binaryLogicStates;
  }

  return result;
}

json Alarm::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["AlarmType"] = static_cast<int>(m_alarmType);
  result["Severity"] = static_cast<int>(m_severity);
  result["CurrentState"] = static_cast<int>(m_currentState);
  result["ChannelId"] = m_channelId;
  result["ExternalAlarmId"] = m_externalAlarmId;
  result["UniqueId"] = m_uniqueId;
  result["Valid"] = m_valid;
  result["ActivatedTime"] = m_activatedTime;
  result["AcknowledgedTime"] = m_acknowledgedTime;
  result["ClearedTime"] = m_clearedTime;
  result["Name"] = m_name;
  result["Channel"] = m_channel;
  result["Device"] = m_device;
  result["Title"] = m_title;
  result["Description"] = m_description;
  result["CZoneRawAlarm"] = m_cZoneRawAlarm;
  result["FaultAction"] = m_faultAction;
  result["FaultType"] = m_faultType;
  result["FaultNumber"] = m_faultNumber;

  return result;
}

json MeteringDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["Line"] = static_cast<int>(m_line);
  result["Output"] = m_output;
  result["NominalVoltage"] = m_nominalVoltage;
  result["NominalFrequency"] = m_nominalFrequency;
  result["Address"] = m_address;
  result["Capacity"] = m_capacity;
  result["WarningLow"] = m_warningLow;
  result["WarningHigh"] = m_warningHigh;
  result["LowLimit"] = m_lowLimit;
  result["VeryLowLimit"] = m_veryLowLimit;
  result["HighLimit"] = m_highLimit;
  result["VeryHighLimit"] = m_veryHighLimit;
  result["Frequency"] = m_frequency;
  result["LowVoltage"] = m_lowVoltage;
  result["VeryLowVoltage"] = m_veryLowVoltage;
  result["HighVoltage"] = m_highVoltage;
  result["CanResetCapacity"] = m_canResetCapacity;
  result["DCType"] = static_cast<int>(m_dcType);
  result["ShowVoltage"] = m_showVoltage;
  result["ShowCurrent"] = m_showCurrent;
  result["ShowStateOfCharge"] = m_showStateOfCharge;
  result["ShowTemperature"] = m_showTemperature;
  result["ShowTimeOfRemaining"] = m_showTimeOfRemaining;
  result["ACType"] = static_cast<int>(m_acType);

  return result;
}

json Instance::tojson() const {
  json result;

  result["Enabled"] = m_enabled;
  result["Instance"] = m_instance;

  return result;
}

json AlarmLimit::tojson() const {
  json result;

  result["Enabled"] = enabled;
  result["On"] = on;
  result["Off"] = off;
  result["Id"] = id;

  return result;
}

json MonitoringDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["TankType"] = static_cast<int>(m_tankType);
  result["PressureType"] = static_cast<int>(m_pressureType);
  result["TemperatureType"] = static_cast<int>(m_temperatureType);
  result["CircuitId"] = m_circuitId;
  result["SwitchType"] = static_cast<int>(m_switchType);
  result["ConfirmDialog"] = static_cast<int>(m_confirmDialog);
  result["CircuitNameUTF8"] = m_circuitNameUTF8;
  result["HighTemperature"] = m_highTemperature;
  result["AtmosphericPressure"] = m_atmosphericPressure;
  result["VeryLowLimit"] = m_veryLowLimit;
  result["LowLimit"] = m_lowLimit;
  result["HighLimit"] = m_highLimit;
  result["VeryHighLimit"] = m_veryHighLimit;
  result["TankCapacity"] = m_tankCapacity;
  result["Address"] = m_address;

  return result;
}

json DataId::tojson() const {
  json result;

  result["Enabled"] = m_enabled;
  result["Id"] = m_id;

  return result;
}

json ACMainDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Dipswitch"] = m_dipswitch;
  result["Contactors"] = m_contactors;
  result["LoadGroups"] = m_loadGroups;

  return result;
}

json ACMainContactorDevice::tojson() const {
  json result;

  result["SystemStateId"] = m_systemStateId;
  result["NameUTF8"] = m_nameUTF8;
  result["ContactorId"] = m_contactorId;
  result["ContactorToggleId"] = m_contactorToggleId;
  result["AC1Id"] = m_ac1Id;
  result["AC2Id"] = m_ac2Id;
  result["AC3Id"] = m_ac3Id;
  result["DisplayIndex"] = m_displayIndex;
  result["LoadGroupIndex"] = m_loadGroupIndex;
  result["LoadGroupParallelIndex"] = m_loadGroupParallelIndex;
  result["IsParallel"] = m_isParallel;
  result["ACInputType"] = static_cast<int>(m_acInputType);

  return result;
}

json ACMainLoadGroupDevice::tojson() const {
  json result;

  result["NameUTF8"] = m_nameUTF8;
  result["LoadGroupIndex"] = m_loadGroupIndex;

  return result;
}

json InverterChargerDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Model"] = m_model;
  result["Type"] = m_type;
  result["SubType"] = m_subType;
  result["InverterInstance"] = m_inverterInstance;
  result["InverterACId"] = m_inverterACId;
  result["InverterCircuitId"] = m_inverterCircuitId;
  result["InverterToggleCircuitId"] = m_inverterToggleCircuitId;
  result["ChargerInstance"] = m_chargerInstance;
  result["ChargerACId"] = m_chargerACId;
  result["ChargerCircuitId"] = m_chargerCircuitId;
  result["ChargerToggleCircuitId"] = m_chargerToggleCircuitId;
  result["BatteryBank1Id"] = m_batteryBank1Id;
  result["BatteryBank2Id"] = m_batteryBank2Id;
  result["BatteryBank3Id"] = m_batteryBank3Id;
  result["PositionColumn"] = m_positionColumn;
  result["PositionRow"] = m_positionRow;
  result["Clustered"] = m_clustered;
  result["Primary"] = m_primary;
  result["PrimaryPhase"] = m_primaryPhase;
  result["DeviceInstance"] = m_deviceInstance;
  result["Dipswitch"] = m_dipswitch;
  result["ChannelIndex"] = m_channelIndex;

  return result;
}

json HVACDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["OperatingModeId"] = m_operatingModeId;
  result["FanModeId"] = m_fanModeId;
  result["FanSpeedId"] = m_fanSpeedId;
  result["SetpointTemperatureId"] = m_setpointTemperatureId;
  result["OperatingModeToggleId"] = m_operatingModeToggleId;
  result["FanModeToggleId"] = m_fanModeToggleId;
  result["FanSpeedToggleId"] = m_fanSpeedToggleId;
  result["SetpointTemperatureToggleId"] = m_setpointTemperatureToggleId;
  result["TemperatureMonitoringId"] = m_temperatureMonitoringId;
  result["FanSpeedCount"] = m_fanSpeedCount;
  result["OperatingModesMask"] = m_operatingModesMask;
  result["Model"] = m_model;
  result["TemperatureInstance"] = m_temperatureInstance;
  result["SetpointTemperatureMin"] = m_setpointTemperatureMin;
  result["SetpointTemperatureMax"] = m_setpointTemperatureMax;
  result["FanSpeedOffModesMask"] = m_fanSpeedOffModesMask;
  result["FanSpeedAutoModesMask"] = m_fanSpeedAutoModesMask;
  result["FanSpeedManualModesMask"] = m_fanSpeedManualModesMask;

  return result;
}

json ThirdPartyGeneratorDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["StartControlId"] = m_startControlId;
  result["StopControlId"] = m_stopControlId;
  result["AssociatedAcMetersInstance"] = m_associatedAcMetersInstance;
  result["AcMeterLine1Id"] = m_acMeterLine1Id;
  result["AcMeterLine2Id"] = m_acMeterLine2Id;
  result["AcMeterLine3Id"] = m_acMeterLine3Id;

  return result;
}

json ZipdeeAwningDevice::tojson() const {
  json result;

  result["DisplayType"] = m_displayType;
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["OpenId"] = m_openId;
  result["CloseId"] = m_closeId;
  result["TiltLeftId"] = m_tiltLeftId;
  result["TiltRightId"] = m_tiltRightId;
  result["BinarySignals"] = m_binarySignals;

  return result;
}

json BinarySignalBitAddress::tojson() const {
  json result;

  result["DataType"] = m_dataType;
  result["Dipswitch"] = m_dipswitch;
  result["Bit"] = m_bit;

  return result;
}

json TyrePressureDevice::tojson() const {
  json result;

  result["DisplayType"] = m_displayType;
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["NumberOfAxles"] = m_numberOfAxles;
  result["TyresAxle1"] = m_tyresAxle1;
  result["TyresAxle2"] = m_tyresAxle2;
  result["TyresAxle3"] = m_tyresAxle3;
  result["TyresAxle4"] = m_tyresAxle4;
  result["SpareAxle"] = m_spareAxle;
  result["TyreInstances"] = m_tyreInstances;
  result["TyreSpareInstances"] = m_tyreSpareInstances;

  return result;
}

json AudioStereoDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["MuteEnabled"] = m_muteEnabled;
  result["CircuitIds"] = m_circuitIds;

  return result;
}

json ShoreFuseDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["ShoreFuseControlId"] = m_shoreFuseControlId;

  return result;
}

json CircuitDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = json::object();
  result["Id"]["Valid"] = m_id.second;
  result["Id"]["Value"] = m_id.first;
  result["NameUTF8"] = m_nameUTF8;
  result["SingleThrowId"] = m_singleThrowId;
  result["SequentialNamesUTF8"] = json::array();
  for (const auto &s : m_sequentialNamesUTF8) {
    result["SequentialNamesUTF8"].emplace_back(json::object({{"Name", s}}));
  }

  result["HasComplement"] = m_hasComplement;
  result["DisplayCategories"] = m_displayCategories;
  result["ConfirmDialog"] = static_cast<int>(m_confirmDialog);
  result["VoltageSource"] = m_voltageSource;
  result["CircuitType"] = static_cast<int>(m_circuitType);
  result["SwitchType"] = static_cast<int>(m_switchType);
  result["MinLevel"] = m_minLevel;
  result["MaxLevel"] = m_maxLevel;
  result["NonVisibleCircuit"] = m_nonVisibleCircuit;
  result["Dimstep"] = m_dimstep;
  result["Step"] = m_step;
  result["Dimmable"] = m_dimmable;
  result["LoadSmoothStart"] = m_loadSmoothStart;
  result["SequentialStates"] = m_sequentialStates;
  result["ControlId"] = m_controlId;
  result["CircuitLoads"] = m_circuitLoads;
  result["Categories"] = m_categories;
  result["DCCircuit"] = m_dcCircuit;
  result["ACCircuit"] = m_acCircuit;
  result["ModeIcon"] = static_cast<int>(m_modeIcon);
  result["PrimaryCircuitId"] = m_primaryCircuitId;
  result["RemoteVisibility"] = m_remoteVisibility;
  result["SwitchString"] = m_switchString;
  result["SystemsOnAnd"] = m_systemsOnAnd;

  return result;
}

json CircuitLoad::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["ChannelAddress"] = m_channelAddress;
  result["FuseLevel"] = m_fuseLevel;
  result["RunningCurrent"] = m_runningCurrent;
  result["SystemOnCurrent"] = m_systemOnCurrent;
  result["ForceAcknowledgeOn"] = m_forceAcknowledgeOn;
  result["Level"] = m_level;
  result["ControlType"] = static_cast<int>(m_controlType);
  result["IsSwitchedModule"] = m_isSwitchedModule;

  return result;
}

json FantasticFanDevice::tojson() const {
  json result;

  result["DisplayType"] = m_displayType;
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["DirectionForwardCircuitId"] = m_directionForwardCircuitId;
  result["DirectionReverseCircuitId"] = m_directionReverseCircuitId;
  result["LidOpenCircuitId"] = m_lidOpenCircuitId;
  result["LidCloseCircuitId"] = m_lidCloseCircuitId;
  result["FanCircuitId"] = m_fanCircuitId;

  return result;
}

json ScreenConfigMode::tojson() const {
  json result;

  result["Header"] = m_header;
  result["Name"] = m_name;

  return result;
}

json ScreenConfigHeader::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["TargetDisplayType"] = m_targetDisplayType;
  result["TargetId"] = m_targetId;
  result["ConfirmationType"] = m_confirmationType;
  result["SmoothStart"] = m_smoothStart;
  result["Index"] = m_index;
  result["ParentIndex"] = m_parentIndex;
  result["ControlId"] = m_controlId;

  return result;
}

json ScreenConfigPageGridItem::tojson() const {
  json result;

  result["Header"] = m_header;
  result["GridX"] = m_gridX;
  result["GridY"] = m_gridY;
  result["TargetX"] = m_targetX;
  result["TargetY"] = m_targetY;
  result["TargetWidth"] = m_targetWidth;
  result["TargetHeight"] = m_targetHeight;
  result["Icon"] = m_icon;
  result["Name"] = m_name;
  result["ColumnSpan"] = m_columnSpan;
  result["RowSpan"] = m_rowSpan;
  result["DoubleThrowType"] = m_doubleThrowType;

  return result;
}

json ScreenConfigPageImage::tojson() const {
  json result;

  result["Header"] = m_header;
  result["GridX"] = m_gridX;
  result["GridY"] = m_gridY;
  result["GridWidth"] = m_gridWidth;
  result["GridHeight"] = m_gridHeight;
  result["SourceWidth"] = m_sourceWidth;
  result["SourceHeight"] = m_sourceHeight;
  result["TargetX"] = m_targetX;
  result["TargetY"] = m_targetY;
  result["TargetWidth"] = m_targetWidth;
  result["TargetHeight"] = m_targetHeight;
  result["FileName"] = m_fileName;
  result["BackgroundColourR"] = m_backgroundColourR;
  result["BackgroundColourG"] = m_backgroundColourG;
  result["BackgroundColourB"] = m_backgroundColourB;
  result["ShowBackground"] = m_showBackground;
  result["CropToFit"] = m_cropToFit;

  return result;
}

json ScreenConfigPage::tojson() const {
  json result;

  result["Header"] = m_header;

  return result;
}

json ScreenConfig::tojson() const {
  json result;

  result["Header"] = m_header;
  result["GridWidth"] = m_gridWidth;
  result["GridHeight"] = m_gridHeight;
  result["Landscape"] = m_landscape;
  result["DisplayName"] = m_displayName;
  result["RelativePath"] = m_relativePath;

  return result;
}

json FavouritesInfo::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["TargetDisplayType"] = m_targetDisplayType;
  result["TargetId"] = m_targetId;
  result["X"] = m_x;
  result["Y"] = m_y;

  return result;
}

json Device::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["NameUTF8"] = m_nameUTF8;
  result["Dipswitch"] = m_dipswitch;
  result["SourceAddress"] = m_sourceAddress;
  result["Conflict"] = m_conflict;
  result["DeviceType"] = static_cast<int>(m_deviceType);
  result["Valid"] = m_valid;
  result["Transient"] = m_transient;
  result["Version"] = m_version;

  return result;
}

json GNSSDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["IsExternal"] = m_isExternal;

  return result;
}

json EngineDevice::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displayType);
  result["Id"] = m_id;
  result["NameUTF8"] = m_nameUTF8;
  result["Instance"] = m_instance;
  result["SoftwareId"] = m_softwareId;
  result["CalibrationId"] = m_calibrationId;
  result["SerialNumber"] = m_serialNumber;
  result["ECUSerialNumber"] = m_ecuSerialNumber;
  result["EngineType"] = m_engineType;

  return result;
}

json UiRelationshipMsg::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displaytype);
  result["Id"] = m_id;
  result["PrimaryType"] = static_cast<int>(m_primarytype);
  result["SecondaryType"] = static_cast<int>(m_secondarytype);
  result["PrimaryId"] = m_primaryid;
  result["SecondaryId"] = m_secondaryid;
  result["RelationshipType"] = static_cast<int>(m_relationshiptype);
  result["PrimaryConfigAddress"] = m_primaryconfigaddress;
  result["SecondaryConfigAddress"] = m_secondaryconfigaddress;
  result["PrimaryChannelIndex"] = m_primarychannelindex;
  result["SecondaryChannelIndex"] = m_secondarychannelindex;

  return result;
}

json BinaryLogicStateMsg::tojson() const {
  json result;

  result["DisplayType"] = static_cast<int>(m_displaytype);
  result["Id"] = m_id;
  result["Address"] = m_address;
  result["NameUTF8"] = m_nameutf8;

  return result;
}

json ScreenConfigPageImageItem::tojson() const {
  json result;

  result["Header"] = m_header;
  result["LocationX"] = m_locationX;
  result["LocationY"] = m_locationY;
  result["TargetX"] = m_targetX;
  result["TargetY"] = m_targetY;
  result["Icon"] = m_icon;
  result["Name"] = m_name;
  result["HideWhenOff"] = m_hideWhenOff;

  return result;
}

json Event::tojson() const {
  json result;

  auto toHexString = [](const std::vector<std::byte> &data) -> std::string {
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (size_t i = 0; i < data.size(); ++i) {
      if (i > 0) {
        oss << " ";
      }
      oss << std::setw(2) << static_cast<unsigned>(std::to_integer<uint8_t>(data[i]));
    }
    return oss.str();
  };

  result["Type"] = static_cast<int>(m_type);
  result["TypeName"] = to_string(m_type);
  result["Content"] = m_content;
  result["AlarmItem"] = m_alarmItem;
  result["GlobalStatus"] = json::object();
  result["GlobalStatus"]["HighestEnabledSeverity"] = static_cast<int>(m_globalStatus.get_highestEnabledSeverity());
  result["GlobalStatus"]["HighestAcknowledgedSeverity"] =
      static_cast<int>(m_globalStatus.get_highestAcknowledgedSeverity());
  result["CZoneEvent"] = json::object();
  result["CZoneEvent"]["Type"] = m_czoneEvent.get_type();
  result["CZoneEvent"]["Content"] = toHexString(m_czoneEvent.get_content());
  result["CZoneEvent"]["RawAlarm"] = toHexString(m_czoneEvent.get_rawAlarm());
  result["CZoneEvent"]["DeviceItem"] = toHexString(m_czoneEvent.get_deviceItem());

  result["TimeStamp"] = m_timeStamp;

  return result;
}

SettingRequest::SettingRequest(const json &j) : m_Type(eConfig) {
  try {
    if (j.contains("Type")) {
      m_Type = from_string(j["Type"].get<std::string>());
    } else {
      throw std::invalid_argument("SettingRequest::SettingRequest [Type] argument is missing");
    }

    if (j.contains("DipswitchValue")) {
      m_DipswitchValue = std::make_unique<uint32_t>(j["DipswitchValue"].get<uint32_t>());
    }

    if (j.contains("TimeOffsetValue")) {
      m_TimeOffsetValue = std::make_unique<float>(j["TimeOffsetValue"].get<float>());
    }

    if (j.contains("MagneticVariationValue")) {
      m_MagneticVariationValue = std::make_unique<float>(j["MagneticVariationValue"].get<float>());
    }

    if (j.contains("DepthOffsetValue")) {
      m_DepthOffsetValue = std::make_unique<float>(j["DepthOffsetValue"].get<float>());
    }

    if (j.contains("BacklightValue")) {
      m_BacklightValue = std::make_unique<float>(j["BacklightValue"].get<float>());
    }

    if (j.contains("BatteryFullValue")) {
      m_BatteryFullValue = std::make_unique<uint32_t>(j["BatteryFullValue"].get<uint32_t>());
    }

    if (j.contains("Payload")) {
      auto payloadArray = j["Payload"]; // [x] need confirm payload example
      m_Payload = std::make_unique<std::vector<std::byte>>();
      m_Payload->clear();
      m_Payload->reserve(payloadArray.size());
      for (const auto &byte : payloadArray) {
        m_Payload->push_back(static_cast<std::byte>(byte.get<uint8_t>()));
      }
    }
  } catch (const std::invalid_argument &e) {
    throw std::invalid_argument(e.what());
  } catch (const std::exception &e) {
    throw std::runtime_error("SettingRequest::SettingRequest error while generating SettingRequest object.");
  }
}

SettingRequest::SettingRequest(const SettingRequest &other) : m_Type(other.m_Type) {
  if (other.m_DipswitchValue) {
    m_DipswitchValue = std::make_unique<uint32_t>(*other.m_DipswitchValue);
  }

  if (other.m_TimeOffsetValue) {
    m_TimeOffsetValue = std::make_unique<float>(*other.m_TimeOffsetValue);
  }

  if (other.m_MagneticVariationValue) {
    m_MagneticVariationValue = std::make_unique<float>(*other.m_MagneticVariationValue);
  }

  if (other.m_DepthOffsetValue) {
    m_DepthOffsetValue = std::make_unique<float>(*other.m_DepthOffsetValue);
  }

  if (other.m_BacklightValue) {
    m_BacklightValue = std::make_unique<float>(*other.m_BacklightValue);
  }

  if (other.m_BatteryFullValue) {
    m_BatteryFullValue = std::make_unique<uint32_t>(*other.m_BatteryFullValue);
  }

  if (other.m_Payload) {
    m_Payload = std::make_unique<std::vector<std::byte>>(*other.m_Payload);
  }
}

SettingRequest &SettingRequest::operator=(const SettingRequest &other) {
  if (this != &other) {
    m_Type = other.m_Type;

    // Reset and reassign all unique_ptr members
    m_DipswitchValue.reset();
    if (other.m_DipswitchValue) {
      m_DipswitchValue = std::make_unique<uint32_t>(*other.m_DipswitchValue);
    }

    m_TimeOffsetValue.reset();
    if (other.m_TimeOffsetValue) {
      m_TimeOffsetValue = std::make_unique<float>(*other.m_TimeOffsetValue);
    }

    m_MagneticVariationValue.reset();
    if (other.m_MagneticVariationValue) {
      m_MagneticVariationValue = std::make_unique<float>(*other.m_MagneticVariationValue);
    }

    m_DepthOffsetValue.reset();
    if (other.m_DepthOffsetValue) {
      m_DepthOffsetValue = std::make_unique<float>(*other.m_DepthOffsetValue);
    }

    m_BacklightValue.reset();
    if (other.m_BacklightValue) {
      m_BacklightValue = std::make_unique<float>(*other.m_BacklightValue);
    }

    m_BatteryFullValue.reset();
    if (other.m_BatteryFullValue) {
      m_BatteryFullValue = std::make_unique<uint32_t>(*other.m_BatteryFullValue);
    }

    m_Payload.reset();
    if (other.m_Payload) {
      m_Payload = std::make_unique<std::vector<std::byte>>(*other.m_Payload);
    }
  }
  return *this;
}

AlarmRequest::AlarmRequest(const json &j) {
  try {
    if (j.contains("Id")) {
      m_id = std::make_unique<uint32_t>(j["Id"].get<uint32_t>());
    }
    if (j.contains("Accepted")) {
      m_accepted = std::make_unique<bool>(j["Accepted"].get<bool>());
    }

  } catch (const std::exception &e) {
    throw std::runtime_error("AlarmRequest::AlarmRequest error while generating AlarmRequest object.");
  }
}

AlarmRequest::AlarmRequest(const AlarmRequest &other) {
  if (other.m_id) {
    m_id = std::make_unique<uint32_t>(*other.m_id);
  }
  if (other.m_accepted) {
    m_accepted = std::make_unique<bool>(*other.m_accepted);
  }
}