#include <typeinfo>
#include <variant>

#include <DevelopmentLib/Utils/tCZoneNmea2kName.h>
#include <Monitoring/tCZoneDataId.h>

#include "modules/czone/czonedatabase.h"
#include "modules/czone/czoneunitutils.h"
#include "modules/czone/monitoringdata.h"
#include "utils/logger.h"
#include "utils/timestamp.h"

/**
 * @param dataType The CZone data type identifier
 * @param instanceOrId The instance number or device ID
 * @return uint32_t Combined key with dataType in upper 16 bits, instanceOrId in lower 16 bits
 */
template <typename T>
uint32_t CzoneDatabase::CreateKey(tCZoneDataType dataType, T instanceOrId) {
  return (static_cast<uint32_t>(dataType) << 16) | instanceOrId & 0xffff;
}

/**
 * @param dataType The type of data to retrieve (e.g., circuit current, temperature)
 * @param instanceOrId The specific instance or device ID
 * @param valid Reference to boolean that will be set to indicate if the value is valid
 * @param dataTypeIndex Cache map for data type indices to improve performance
 * @return int32_t The retrieved signed integer value (0 if invalid)
 */
template <typename T>
int32_t CzoneDatabase::ValueS32(tCZoneDataType dataType, T instanceOrId, bool &valid,
                                std::map<uint32_t, uint32_t> &dataTypeIndex) {
  int32_t value = 0.0;

  // Create composite key for this data type and instance
  auto key = CreateKey(dataType, instanceOrId);
  auto it = dataTypeIndex.find(key);

  if (it == dataTypeIndex.end()) {
    // Index doesn't exist yet - create it and cache for future use
    auto index = CZoneMonitoringCreateDataIndex(dataType, instanceOrId);
    dataTypeIndex[key] = index;
    valid = CZoneMonitoringDataS32(index, &value);
  } else {
    // Use cached index for faster lookup
    valid = CZoneMonitoringDataS32(it->second, &value);
  }

  return value;
}

/**
 * @param dataType The type of data to retrieve
 * @param instanceOrId The specific instance or device ID
 * @param valid Reference to boolean indicating if the value is valid
 * @param dataTypeIndex Cache map for data type indices
 * @param valueMap Map to store complete monitoring value information including limits
 * @return float The retrieved floating-point value (0.0f if invalid)
 */
template <typename T>
float CzoneDatabase::Value(tCZoneDataType dataType, T instanceOrId, bool &valid,
                           std::map<uint32_t, uint32_t> &dataTypeIndex,
                           std::unordered_map<uint32_t, struct MonitoringValue> &valueMap) {
  float value = 0.0f;

  // Create composite key for this data type and instance
  auto key = CreateKey(dataType, instanceOrId);
  auto it = dataTypeIndex.find(key);

  // Variables to store limit information
  bool limitValid;
  float min;
  float max;
  float warnLow;
  float warnHigh;

  if (it == dataTypeIndex.end()) {
    // Index doesn't exist - create new one and retrieve both value and limits
    auto index = CZoneMonitoringCreateDataIndex(dataType, instanceOrId);
    dataTypeIndex[key] = index;
    valid = CZoneMonitoringData(index, &value);
    limitValid = CZoneMonitoringDataLimits(index, &min, &max, &warnLow, &warnHigh);
  } else {
    // Use cached index to retrieve both value and limits
    valid = CZoneMonitoringData(it->second, &value);
    limitValid = CZoneMonitoringDataLimits(it->second, &min, &max, &warnLow, &warnHigh);
  }

  // Package all monitoring information into a structured value
  struct MonitoringValue mValue;
  mValue.Valid = valid;
  mValue.Value = value;
  mValue.LimitValid = limitValid;
  mValue.Min = min;
  mValue.Max = max;
  mValue.WarnLow = warnLow;
  mValue.WarnHigh = warnHigh;

  // Store in value map for later use in snapshot generation
  valueMap[dataTypeIndex[key]] = mValue;
  return value;
}

/**
 * @param fields Vector of Field structures to process (modified in-place)
 * @param unitConversion Unit conversion system for transforming values to user units
 * @param dataTypeIndex Cache map for data type indices
 * @param valueMap Map to collect monitoring values with limit information
 * @return bool True if at least one field has a valid value, false otherwise
 */
bool CzoneDatabase::GetValuesForInstanceOrId(std::vector<Field> &fields, tUnitConversion &unitConversion,
                                             std::map<uint32_t, uint32_t> &dataTypeIndex,
                                             std::unordered_map<uint32_t, struct MonitoringValue> &valueMap) {
  bool validValue = false;

  for (auto &f : fields) {
    if (f.Type == eCZone_Generic_Instance) {
      // For generic instance fields, just copy the instance number
      f.Value = f.Instance;
      f.Valid = true;
    } else {
      // Retrieve actual monitored data value
      f.Value = Value(f.Type, f.Instance, f.Valid, dataTypeIndex, valueMap);
      if (f.Valid) {
        validValue = true;
        // Apply unit conversion to present data in user-preferred units
        auto units = Utils::Units::UnitsFromDataType(f.Type);
        f.Value = unitConversion.SystemValueToUserValue(units, f.Value);
      }
    }
  }
  return validValue;
}

/**
 * @param messageNew Pointer to the new message object to update
 * @param messageLast Pointer to the last known message state for comparison
 * @param fields Vector of fields with new values to potentially apply
 * @param forceUpdate If true, updates all fields regardless of change status
 * @return bool True if any field was actually changed/updated
 */
template <typename T>
bool CzoneDatabase::UpdateMessageIfDifferent(T *messageNew, T *messageLast, const std::vector<Field> &fields,
                                             bool forceUpdate) {
  bool hasChanged = false;

  for (const auto &field : fields) {
    try {
      // Get variant pointers to the field members in both message objects
      auto member1 = messageNew->get(field.FieldName);
      auto member2 = messageLast->get(field.FieldName);

      bool fieldChanged = false;

      // Use std::visit to handle different pointer types at compile time
      std::visit(
          [&](auto &&newPtr, auto &&lastPtr) {
            using NewType = std::decay_t<decltype(newPtr)>;
            using LastType = std::decay_t<decltype(lastPtr)>;

            // Ensure both pointers are the same type before proceeding
            if constexpr (std::is_same_v<NewType, LastType>) {
              if constexpr (std::is_same_v<NewType, int *>) {
                // Handle primitive int type
                if (forceUpdate || *newPtr != static_cast<int>(field.Value) ||
                    *lastPtr != static_cast<int>(field.Value)) {
                  *newPtr = static_cast<int>(field.Value);
                  *lastPtr = static_cast<int>(field.Value);
                  fieldChanged = true;
                }
              } else if constexpr (std::is_same_v<NewType, int32_t *>) {
                // Handle primitive int32_t type
                if (forceUpdate || *newPtr != static_cast<int32_t>(field.Value) ||
                    *lastPtr != static_cast<int32_t>(field.Value)) {
                  *newPtr = static_cast<int32_t>(field.Value);
                  *lastPtr = static_cast<int32_t>(field.Value);
                  fieldChanged = true;
                }
              } else if constexpr (std::is_same_v<NewType, int64_t *>) {
                // Handle primitive int64_t type
                if (forceUpdate || *newPtr != static_cast<int64_t>(field.Value) ||
                    *lastPtr != static_cast<int64_t>(field.Value)) {
                  *newPtr = static_cast<int64_t>(field.Value);
                  *lastPtr = static_cast<int64_t>(field.Value);
                  fieldChanged = true;
                }
              } else if constexpr (std::is_same_v<NewType, uint32_t *>) {
                // Handle primitive uint32_t type
                if (forceUpdate || *newPtr != static_cast<uint32_t>(field.Value) ||
                    *lastPtr != static_cast<uint32_t>(field.Value)) {
                  *newPtr = static_cast<uint32_t>(field.Value);
                  *lastPtr = static_cast<uint32_t>(field.Value);
                  fieldChanged = true;
                }
              } else if constexpr (std::is_same_v<NewType, uint64_t *>) {
                // Handle primitive uint64_t type
                if (forceUpdate || *newPtr != static_cast<uint64_t>(field.Value) ||
                    *lastPtr != static_cast<uint64_t>(field.Value)) {
                  *newPtr = static_cast<uint64_t>(field.Value);
                  *lastPtr = static_cast<uint64_t>(field.Value);
                  fieldChanged = true;
                }
              } else if constexpr (std::is_same_v<NewType, float *>) {
                // Handle primitive float type
                if (forceUpdate || *newPtr != field.Value || *lastPtr != field.Value) {
                  *newPtr = field.Value;
                  *lastPtr = field.Value;
                  fieldChanged = true;
                }
              } else if constexpr (std::is_same_v<NewType, double *>) {
                // Handle primitive double type
                if (forceUpdate || *newPtr != static_cast<double>(field.Value) ||
                    *lastPtr != static_cast<double>(field.Value)) {
                  *newPtr = static_cast<double>(field.Value);
                  *lastPtr = static_cast<double>(field.Value);
                  fieldChanged = true;
                }
              } else if constexpr (std::is_same_v<NewType, bool *>) {
                // Handle primitive bool type
                bool newValue = static_cast<bool>(field.Value);
                if (forceUpdate || *newPtr != newValue || *lastPtr != newValue) {
                  *newPtr = newValue;
                  *lastPtr = newValue;
                  fieldChanged = true;
                }
              } else if constexpr (std::is_enum_v<std::remove_pointer_t<NewType>>) {
                // Handle enum types by casting float value to appropriate enum
                using EnumType = std::remove_pointer_t<NewType>;
                auto newValue = static_cast<EnumType>(field.Value);
                if (forceUpdate || *newPtr != newValue || *lastPtr != newValue) {
                  *newPtr = newValue;
                  *lastPtr = newValue;
                  fieldChanged = true;
                }
              } else {
                // Handle complex objects with m_valid and m_value members (like ValueTypes)
                if constexpr (requires {
                                newPtr->m_valid;
                                newPtr->m_value;
                              }) {
                  using ValueType = decltype(newPtr->m_value);
                  auto newValue = static_cast<ValueType>(field.Value);

                  // Update both validity flag and value if either has changed
                  if (forceUpdate || newPtr->m_valid != field.Valid || newPtr->m_value != newValue ||
                      lastPtr->m_valid != field.Valid || lastPtr->m_value != newValue) {
                    newPtr->m_valid = field.Valid;
                    newPtr->m_value = newValue;
                    lastPtr->m_valid = field.Valid;
                    lastPtr->m_value = newValue;
                    fieldChanged = true;
                  }
                } else {
                  // Unhandled type - log warning for debugging
                  BOOST_LOG_TRIVIAL(warning)
                      << "Unhandled type in UpdateMessageIfDifferent for field: " << field.FieldName;
                }
              }
            }
          },
          member1, member2);

      hasChanged |= fieldChanged;

    } catch (const std::invalid_argument &e) {
      // Field not found in message structure - log error and continue with other fields
      BOOST_LOG_TRIVIAL(error) << "Field not found in message: " << field.FieldName;
    }
  }

  return hasChanged;
}

/**
 * @param fields Vector of Field structures containing data type and field mapping information
 * @param instance The instance identifier for this monitoring object
 * @param snapshot Reference to current snapshot map to populate
 * @param lastSnapshot Reference to previous snapshot map for change comparison
 * @param unitConversion Unit conversion system for value transformation
 * @param dataTypeIndex Cache map for efficient data index lookup
 */
template <typename T1, typename T2>
void CzoneDatabase::ProcessFields(std::vector<Field> &fields, T1 instance, N2KMonitoring::IdMap<T2> &snapshot,
                                  N2KMonitoring::IdMap<T2> &lastSnapshot, tUnitConversion &unitConversion,
                                  std::map<uint32_t, uint32_t> &dataTypeIndex) {
  // Container to collect monitoring values with limits and validation info
  std::unordered_map<uint32_t, struct MonitoringValue> valueMap;

  // Retrieve current values for all fields and apply unit conversions
  bool validValue = GetValuesForInstanceOrId(fields, unitConversion, dataTypeIndex, valueMap);

  // Check if this instance was present in the previous snapshot
  auto lastSnapShotEntry = lastSnapshot.find(instance);

  if (lastSnapShotEntry == lastSnapshot.end()) {
    // New instance - create both new and last snapshot entries
    auto newItem = std::make_shared<T2>();
    auto lastItem = std::make_shared<T2>();

    // Force update since this is a new instance (!validValue inverts to force when no valid data)
    UpdateMessageIfDifferent(newItem.get(), lastItem.get(), fields, !validValue);

    // Add to both snapshots
    snapshot[instance] = newItem;
    lastSnapshot[instance] = lastItem;

    // Populate global monitoring key-value map with detailed monitoring information
    for (auto &it : valueMap) {
      auto mValue = std::make_shared<N2KMonitoring::MonitoringKeyValue>();
      mValue->m_valid = it.second.Valid;
      mValue->m_value = it.second.Value;
      mValue->m_limitValid = it.second.LimitValid;
      mValue->m_min = it.second.Min;
      mValue->m_max = it.second.Max;
      mValue->m_warnLow = it.second.WarnLow;
      mValue->m_warnHigh = it.second.WarnHigh;
      m_SnapshotKeyValue.m_keyValueMap[it.first] = mValue;
    }
  } else {
    // Existing instance - only update if values have changed
    auto newItem = std::make_shared<T2>();

    // Compare with last known state and update only if different
    if (UpdateMessageIfDifferent(newItem.get(), lastSnapShotEntry->second.get(), fields, false)) {
      // Changes detected - update current snapshot
      snapshot[instance] = newItem;

      // Update global monitoring key-value map with new monitoring information
      for (auto &it : valueMap) {
        auto mValue = std::make_shared<N2KMonitoring::MonitoringKeyValue>();
        mValue->m_valid = it.second.Valid;
        mValue->m_value = it.second.Value;
        mValue->m_limitValid = it.second.LimitValid;
        mValue->m_min = it.second.Min;
        mValue->m_max = it.second.Max;
        mValue->m_warnLow = it.second.WarnLow;
        mValue->m_warnHigh = it.second.WarnHigh;
        m_SnapshotKeyValue.m_keyValueMap[it.first] = mValue;
      }
    }
    // If no changes detected, neither snapshot nor key-value map are updated
  }
}

/**
 * @brief Constructor initializes CzoneDatabase with CAN service and sets up unit conversions
 *
 * Configures the database with standard maritime and automotive unit preferences.
 * These unit settings determine how raw sensor data is converted for display to users.
 * All measurements are converted from internal system units to user-friendly units.
 */
CzoneDatabase::CzoneDatabase(CanService &canService) : m_canService(canService), m_workerpool(2) {
  // Initialize unit conversion system with default settings
  m_UnitConversion.SetDefaults();

  // Configure specific unit preferences for maritime/automotive applications
  m_UnitConversion.SetUnits(eUnitType_BoatSpeed, tSpeedConversions::MetersPerSecond);
  m_UnitConversion.SetUnits(eUnitType_WindSpeed, tSpeedConversions::MetersPerSecond);
  m_UnitConversion.SetUnits(eUnitType_Depth, tDistanceConversions::Meters);
  m_UnitConversion.SetUnits(eUnitType_Heading, tHeadingConversions::Magnetic);
  m_UnitConversion.SetUnits(eUnitType_Temperature, tTemperatureConversions::Celsius);
  m_UnitConversion.SetUnits(eUnitType_Volume, tVolumeConversions::Liters);
  m_UnitConversion.SetUnits(eUnitType_Pressure, tPressureConversions::Pascals);
  m_UnitConversion.SetUnits(eUnitType_BarometricPressure, tPressureConversions::BaroPascals);
  m_UnitConversion.SetUnits(eUnitType_BatteryCapacity, tCapacityConversions::AmpHours);
  m_UnitConversion.SetUnits(eUnitType_Angle, tAngleConversions::Degrees);
  m_UnitConversion.SetUnits(eUnitType_Flowrate, tFlowrateConversions::LitersPerHour);
  m_UnitConversion.SetUnits(eUnitType_EngineHours, tEngineHoursConversions::EngineHoursInMinutes);
}

CzoneDatabase::~CzoneDatabase() {}

/**
 * @brief Initializes/clears the database for fresh data loading
 *
 * Currently just calls Clear() to reset the data type index.
 * Could be extended for additional database initialization tasks.
 */
void CzoneDatabase::LoadDatabase() { Clear(); }

/**
 * @brief Clears the data type index cache
 *
 * Resets the mapping between data type keys and monitoring indices.
 * This forces recreation of all monitoring indices on next access,
 * which may be necessary after configuration changes or system resets.
 */
void CzoneDatabase::Clear() { m_DataTypeIndex.clear(); }

/**
 * @brief Main update function that refreshes all monitoring data categories
 *
 * This function orchestrates the complete monitoring data update cycle.
 * It calls specialized update functions for each category of monitored
 * equipment and systems. Each update function processes its specific
 * device type and populates the current snapshot with any changed data.
 *
 * @param lastSnapshot Reference to previous snapshot for change detection
 */
void CzoneDatabase::Update(N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  // Update all monitored device categories
  UpdateMonitoringCircuits(m_Snapshot, lastSnapshot);             // Electrical circuits
  UpdateMonitoringModes(m_Snapshot, lastSnapshot);                // Operation modes
  UpdateMonitoringACMainContactors(m_Snapshot, lastSnapshot);     // AC main contactors
  UpdateMonitoringTanks(m_Snapshot, lastSnapshot);                // Fuel/water tanks
  UpdateMonitoringEngines(m_Snapshot, lastSnapshot);              // Engine monitoring
  UpdateMonitoringACs(m_Snapshot, lastSnapshot);                  // AC electrical systems
  UpdateMonitoringDCs(m_Snapshot, lastSnapshot);                  // DC electrical systems
  UpdateMonitoringTemperatures(m_Snapshot, lastSnapshot);         // Temperature sensors
  UpdateMonitoringPressures(m_Snapshot, lastSnapshot);            // Pressure sensors
  UpdateMonitoringHVACs(m_Snapshot, lastSnapshot);                // HVAC systems
  UpdateMonitoringAwnings(m_Snapshot, lastSnapshot);              // Awning systems
  UpdateMonitoringThirdPartyGenerators(m_Snapshot, lastSnapshot); // External generators
  UpdateMonitoringInverterChargers(m_Snapshot, lastSnapshot);     // Inverter/charger units
  UpdateMonitoringTyrepressures(m_Snapshot, lastSnapshot);        // Tire pressure monitoring
  UpdateMonitoringAudioStereos(m_Snapshot, lastSnapshot);         // Audio systems
  UpdateMonitoringGNSS(m_Snapshot, lastSnapshot);                 // GPS/GNSS systems
  UpdateMonitoringBinaryLogicStates(m_Snapshot, lastSnapshot);    // Digital input states
  UpdateNetworkStatus(m_Snapshot, lastSnapshot);                  // Network status
}

/**
 * @brief Creates and returns a complete monitoring data snapshot
 *
 * This function is the main entry point for obtaining current monitoring data.
 * It performs a thread-safe snapshot generation by:
 * 1. Acquiring a mutex lock to prevent concurrent access
 * 2. Clearing previous snapshot data (for delta)
 * 3. Updating all monitoring categories
 * 4. Consolidating monitoring key-value data if any devices are present
 * 5. Returning the complete snapshot for consumption by other systems
 *
 * The function only includes monitoring key-value data in the final snapshot
 * if at least one monitored device category contains data, optimizing for
 * systems without extensive monitoring equipment.
 *
 * @return N2KMonitoring::SnapshotInstanceIdMap Complete snapshot of current monitoring state
 */
bool CzoneDatabase::Snapshot() {
  // Clear previous snapshot data to start fresh
  m_Snapshot.clear();
  m_SnapshotKeyValue.clear();

  // Update all monitoring categories with current data
  Update(m_LastSnapshot);
  m_LastSnapshot.m_timeStamp = getCurrentTimeString();
  m_Snapshot.m_timeStamp = getCurrentTimeString();

  // Check if any monitoring categories contain data before including key-value details
  if (m_Snapshot.m_ac.size() > 0 || m_Snapshot.m_acMainContactors.size() > 0 || m_Snapshot.m_audioStereos.size() > 0 ||
      m_Snapshot.m_awnings.size() > 0 || m_Snapshot.m_circuits.size() > 0 || m_Snapshot.m_dc.size() > 0 ||
      m_Snapshot.m_engines.size() > 0 || m_Snapshot.m_inverterChargers.size() > 0 || m_Snapshot.m_hvacs.size() > 0 ||
      m_Snapshot.m_modes.size() > 0 || m_Snapshot.m_pressures.size() > 0 || m_Snapshot.m_tanks.size() > 0 ||
      m_Snapshot.m_temperatures.size() > 0 || m_Snapshot.m_thirdPartyGenerators.size() > 0 ||
      m_Snapshot.m_tyrepressures.size() > 0 || m_Snapshot.m_gnss.size() > 0 ||
      m_Snapshot.m_binaryLogicState.size() > 0 || m_Snapshot.m_networkStatus != nullptr) {

    // Include detailed monitoring key-value data in the final snapshot
    for (auto &it : m_SnapshotKeyValue.m_keyValueMap) {
      if (it.second) {
        m_Snapshot.m_monitoringKeyValue[it.first] = it.second;
      }
    }
    return true;
  }

  return false;
}

bool CzoneDatabase::GetSetting(CZoneDbSettingsType type, int32_t &value) const {
  switch (type) {
  case CZoneDbSettingsTimeOffset: value = m_canService.Settings()->getTimeOffset(); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "GetSetting for int32_t, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::GetSetting(CZoneDbSettingsType type, float &value) const {
  switch (type) {
  case CZoneDbSettingsDepthOffset: value = m_canService.Settings()->getDepthOffset(); break;
  case CZoneDbSettingsMagneticVariation: value = m_canService.Settings()->getMagneticVariation(); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "GetSetting for float, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, uint32_t value) const {
  switch (type) {
  case CZoneDbSettingsDipswitch: m_canService.Settings()->setDipswitch(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for uint32_t, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, int32_t value) const {
  switch (type) {
  case CZoneDbSettingsTimeOffset: m_canService.Settings()->setTimeOffset(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for int32_t, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, float value) const {
  switch (type) {
  case CZoneDbSettingsDepthOffset: m_canService.Settings()->setDepthOffset(value); break;
  case CZoneDbSettingsMagneticVariation: m_canService.Settings()->setMagneticVariation(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for float, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

bool CzoneDatabase::AddSetting(CZoneDbSettingsType type, bool value) const {
  switch (type) {
  case CZoneDbSettingsEnableBatteryCharger: m_canService.Settings()->setEnableBatteryCharger(value); break;
  default: {
    BOOST_LOG_TRIVIAL(info) << "AddSetting for bool, type not supported: " << type;
    return false;
  } break;
  }
  return true;
}

/**
 * @brief Creates a simple data index for basic data types
 *
 * This function creates and caches monitoring data indices for simple data types
 * that only require a type and instance identifier. The key is constructed by
 * placing the type in the upper 16 bits and instance in the lower 16 bits.
 *
 * @param type Data type identifier as uint32_t
 * @param instance Instance number for the device/sensor
 * @return uint32_t The monitoring index for accessing this data point
 */
uint32_t CzoneDatabase::CreateDataIndex(uint32_t type, uint32_t instance) {
  // Create composite key: type in upper 16 bits, instance in lower 16 bits
  uint32_t key = type << 16 | instance & 0xffff;
  auto it = m_DataTypeIndex.find(key);

  if (it == m_DataTypeIndex.end()) {
    // Create new monitoring index and cache it
    auto index = CZoneMonitoringCreateDataIndex(tCZoneDataType(type), instance);
    m_DataTypeIndex[key] = index;
  }
  return m_DataTypeIndex[key];
}

/**
 * @brief Creates a complex data index from raw byte buffer
 *
 * This function handles complex data types that require parsing from a byte buffer
 * rather than simple type/instance pairs. It uses a hash of the data ID with a
 * special marker (0x800000000) to distinguish complex indices from simple ones.
 *
 * @param data Pointer to raw byte buffer containing data type information
 * @param length Length of the byte buffer
 * @return uint32_t The monitoring index, or error code if data type is invalid
 */
uint32_t CzoneDatabase::CreateDataIndexComplex(const uint8_t *data, uint32_t length) {
  tCZoneDataId id;
  id.FromByteBuffer(data, length);

  // Validate data type is within acceptable range
  if (id.DataType() >= eNumberOfDataTypes) {
    return (uint32_t)(eDataTypeInvalid & 0xfff) << 20;
  }

  // Create key using hash of the data ID with complex marker bit
  uint32_t key = hash_value(id) | 0x800000000;

  auto it = m_DataTypeIndex.find(key);
  if (it == m_DataTypeIndex.end()) {
    // Create and cache complex monitoring index
    m_DataTypeIndex[key] = CZoneMonitoringCreateComplexDataIndex(data, length);
  }

  return m_DataTypeIndex[key];
}

/**
 * @brief Retrieves monitoring data value by index key
 *
 * Simple wrapper around the CZone monitoring system to get a float value.
 *
 * @param key Monitoring index key
 * @param value Reference to store the retrieved value
 * @return bool True if value retrieval was successful
 */
bool CzoneDatabase::GetMonitoringData(uint32_t key, float &value) { return CZoneMonitoringData(key, &value); }

/**
 * @brief Retrieves monitoring data limits by index key
 *
 * Gets the operational and warning limits for a monitored parameter.
 * This information is used for alarm generation and data validation.
 *
 * @param key Monitoring index key
 * @param min Reference to store minimum operational limit
 * @param max Reference to store maximum operational limit
 * @param warnLow Reference to store low warning threshold
 * @param warnHigh Reference to store high warning threshold
 * @return bool True if limit retrieval was successful
 */
bool CzoneDatabase::GetMonitoringDataLimits(uint32_t key, float &min, float &max, float &warnLow, float &warnHigh) {
  return CZoneMonitoringDataLimits(key, &min, &max, &warnLow, &warnHigh);
}

/**
 * @brief Thread-safe setter for network status information
 *
 * Updates the current network status with mutex protection to ensure
 * thread safety when accessing from multiple contexts.
 *
 * @param network New network status to store
 */
void CzoneDatabase::SetNetworkStatus(const N2KMonitoring::NetworkStatus &network) {
  const std::lock_guard<std::mutex> lock(m_NetworkStatusMutex);
  m_NetworkStatus = network;
}

/**
 * @brief Retrieves overall system health status
 *
 * Performs health checks on various system components and populates
 * a health status structure. This function checks:
 * - Service thread health (implicitly OK if function executes)
 * - Network/CAN bus health with timeout check
 * - Smart craft subsystem (currently disabled)
 * - GNSS subsystem (currently disabled)
 *
 * @param health Reference to health status structure to populate
 * @param timeout Timeout value for network health check
 */
void CzoneDatabase::GetHealthStatus(N2KMonitoring::HealthStatus &health, const int64_t timeout) {
  // Service thread is healthy if this function can execute
  health.m_serviceThread = N2KMonitoring::eHealth::HealthOk;

  // Check network/CAN bus health with timeout
  bool network = m_canService.HealthStatus(timeout);
  health.m_networkThread = (network ? N2KMonitoring::eHealth::HealthOk : N2KMonitoring::eHealth::HealthBad);

  // Smart craft subsystem health (currently not implemented)
  health.m_scThread = N2KMonitoring::eHealth::HealthNone;

  // GNSS subsystem health status (currently not implemented)
  health.m_gnssThread = N2KMonitoring::eHealth::HealthNone;
  health.m_gnssLatLon = N2KMonitoring::eHealth::HealthNone;
  health.m_gnssFix = N2KMonitoring::eHealth::HealthNone;
}

/**
 * @brief Updates monitoring data for electrical circuits
 *
 * Processes all electrical circuits in the CZone system, filtering for standard
 * circuits (type 0) and extracting their operational parameters. Creates a field
 * mapping that associates CZone data types with message field names, then uses
 * the ProcessFields function to handle value retrieval, change detection, and
 * snapshot updates.
 *
 * Each circuit is identified by its unique ID and monitored for:
 * - System on/off state
 * - Current level/intensity
 * - Current draw
 * - Fault conditions
 * - Usage statistics (on count, on time)
 * - Sequential operation state
 * - AC source availability
 * - Online/offline status
 *
 * @param snapshot Reference to current snapshot to populate with circuit data
 * @param lastSnapshot Reference to previous snapshot for change detection
 */
void CzoneDatabase::UpdateMonitoringCircuits(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                             N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  // Get list of all circuits from CAN interface without locking
  auto circuits = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayCircuits);

  for (auto &c : circuits) {
    // Only process standard circuits (type 0), ignore other circuit types
    if (c.Circuit.CircuitType == 0 /*CZ_CT_STANDARD_CIRCUIT*/) {
      uint32_t id = c.Circuit.Id;

      // Define field mapping: data type -> field name -> instance ID
      // This creates the bridge between CZone monitoring data and message structure
      std::vector<Field> fields = {
          {eCZone_Generic_Instance, false, 0.0f, "Id", id},                         // Circuit identifier
          {eCZone_Circuit_SystemOnState, false, 0.0f, "SystemsOn", id},             // On/off state
          {eCZone_Circuit_Level, false, 0.0f, "Level", id},                         // Circuit level/intensity
          {eCZone_Circuit_Current, false, 0.0f, "Current", id},                     // Current draw
          {eCZone_Circuit_Fault, false, 0.0f, "Fault", id},                         // Fault status
          {eCZone_Circuit_OnCount, false, 0.0f, "OnCount", id},                     // Number of times turned on
          {eCZone_Circuit_OnTime, false, 0.0f, "OnTime", id},                       // Total time in on state
          {eCZone_Circuit_SequentialState, false, 0.0f, "SequentialState", id},     // Sequential operation state
          {eCZone_Circuit_ACSourceAvailable, false, 0.0f, "ACSourceAvailable", id}, // AC power availability
          {eCZone_Circuit_IsOffline, false, 0.0f, "IsOffline", id}                  // Online/offline status
      };

      // Process the field collection to update circuit monitoring data
      ProcessFields(fields, id, snapshot.m_circuits, lastSnapshot.m_circuits, m_UnitConversion, m_DataTypeIndex);
    }
  }
}

/**
 * @brief Updates monitoring data for tank level sensors
 *
 * Processes all tank monitoring devices in the system to track fluid levels.
 * Tanks typically monitor fuel, fresh water, grey water, black water, or other
 * fluid storage systems. The function extracts tank parameters and uses the
 * standard field processing pipeline for change detection and updates.
 *
 * Each tank sensor provides:
 * - Instance identifier for the specific tank
 * - Level as percentage (0-100%)
 * - Absolute level in volume units
 * - Total tank capacity
 * - Tank type classification (fuel, water, etc.)
 *
 * @param snapshot Reference to current snapshot to populate with tank data
 * @param lastSnapshot Reference to previous snapshot for change detection
 */
void CzoneDatabase::UpdateMonitoringTanks(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                          N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  // Retrieve all tank monitoring devices from the CAN interface
  auto tanks = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayMonitoringTank);

  for (auto &t : tanks) {
    uint8_t instance = t.MonitoringDevice.Instance;

    // Define tank monitoring field mappings
    std::vector<Field> fields = {
        {eCZone_Generic_Instance, false, 0.0f, "Instance", instance},      // Tank instance ID
        {eCZone_Tank_LevelPercent, false, 0.0f, "LevelPercent", instance}, // Level as percentage
        {eCZone_Tank_Level, false, 0.0f, "Level", instance},               // Absolute level volume
        {eCZone_Tank_Capacity, false, 0.0f, "Capacity", instance},         // Total tank capacity
        {eCZone_Tank_Type, false, 0.0f, "TankType", instance}              // Tank type (fuel/water/etc)
    };

    // Process tank fields using the standard monitoring pipeline
    ProcessFields(fields, instance, snapshot.m_tanks, lastSnapshot.m_tanks, m_UnitConversion, m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringModes(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                          N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto circuits = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayCircuits);
  for (auto &c : circuits) {
    if (c.Circuit.CircuitType >= 1 /*CZ_CT_MODE_OF_OPERATION_1*/ &&
        c.Circuit.CircuitType <= 4 /*CZ_CT_MODE_OF_OPERATION_EXCLUSIVE*/) {
      uint32_t id = c.Circuit.Id;

      std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Id", id},
                                   {eCZone_Circuit_SystemOnState, false, 0.0f, "SystemsOn", id},
                                   {eCZone_Circuit_ModeSystemOnState, false, 0.0f, "ModesSystemOn", id},
                                   {eCZone_Circuit_Level, false, 0.0f, "Level", id}};

      ProcessFields(fields, id, snapshot.m_modes, lastSnapshot.m_modes, m_UnitConversion, m_DataTypeIndex);
    }
  }
}

void CzoneDatabase::UpdateMonitoringACMainContactors(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                                     N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto acMains = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayACMains);
  for (auto &a : acMains) {
    for (uint32_t i = 0; i < a.ACMainsDevice.NumberOfContactors; i++) {
      uint32_t id = a.ACMainsDevice.Contactors[i].SystemStateId;

      std::vector<Field> fields = {
          {eCZone_Generic_Instance, false, 0.0f, "SystemStateId", id},
          {eCZone_Circuit_ACContactorSystemsState, false, 0.0f, "ACContactorSystemsState", id},
          {eCZone_Circuit_ACContactorSourceAvailable, false, 0.0f, "ACContactorSourceAvailable", id},
          {eCZone_Circuit_ReversePolarity, false, 0.0f, "ReversePolarity", id},
          {eCZone_Circuit_ACContactorAutoChangeOver, false, 0.0f, "ACContactorAutoChangeOver", id},
          {eCZone_Circuit_ManualOverride, false, 0.0f, "ManualOverride", id}};

      ProcessFields(fields, id, snapshot.m_acMainContactors, lastSnapshot.m_acMainContactors, m_UnitConversion,
                    m_DataTypeIndex);
    }
  }
}

void CzoneDatabase::UpdateMonitoringEngines(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                            N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  // [x] smartcraft
  // #ifdef EUROPA_SMARTCRAFT_SUPPORT
  //   auto engines = m_canService.EngineList();
  //   for (auto &e : engines) {
  //     m_canService.UpdateMonitoringData(e.first, snapshot.mutable_engines(), lastSnapshot.mutable_engines());
  //   }

  //   auto nmea2kEngines = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayEngines);
  //   for (auto &e : nmea2kEngines) {
  //     uint8_t instance = e.DynamicDevice.Instance;

  //     std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
  //                                  {eCZone_Engine_Speed, false, 0.0f, "Speed", instance},
  //                                  {eCZone_Engine_BoostPressure, false, 0.0f, "BoostPressure", instance},
  //                                  {eCZone_Engine_Trim, false, 0.0f, "Trim", instance},
  //                                  {eCZone_Engine_OilPressure, false, 0.0f, "OilPressure", instance},
  //                                  {eCZone_Engine_OilTemperature, false, 0.0f, "OilTemperature", instance},
  //                                  {eCZone_Engine_Temperature, false, 0.0f, "CoolantTemperature", instance},
  //                                  {eCZone_Engine_AlternatorPotential, false, 0.0f, "AlternatorPotential",
  //                                  instance}, {eCZone_Engine_FuelRate, false, 0.0f, "FuelRate", instance},
  //                                  {eCZone_Engine_TotalEngineHours, false, 0.0f, "TotalEngineHours", instance},
  //                                  {eCZone_Engine_EngineCoolantPressure, false, 0.0f, "CoolantPressure", instance},
  //                                  {eCZone_Engine_FuelPressure, false, 0.0f, "FuelPressure", instance},
  //                                  {eCZone_Engine_DiscreteStatus1, false, 0.0f, "DiscreteStatus1", instance},
  //                                  {eCZone_Engine_DiscreteStatus2, false, 0.0f, "DiscreteStatus2", instance},
  //                                  {eCZone_Engine_EngineLoad, false, 0.0f, "PercentEngineLoad", instance},
  //                                  {eCZone_Engine_EngineTorque, false, 0.0f, "PercentEngineTorque", instance}};

  //     ProcessFields(fields, instance, snapshot.mutable_engines(), lastSnapshot.mutable_engines(), m_UnitConversion,
  //                   m_DataTypeIndex);
  //   }
  // #endif
}

void CzoneDatabase::UpdateMonitoringACs(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                        N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto ac = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayMeteringAC);
  for (uint8_t i = 0; i < 253; i++) {
    auto parentACItem = std::make_shared<N2KMonitoring::AC>();
    parentACItem->m_instance = i;
    for (auto &a : ac) {
      uint8_t instance = a.MeteringDevice.Instance;
      auto line = a.MeteringDevice.Line;

      if (i == instance) {
        auto voltageType = a.MeteringDevice.Output ? eCZone_AC1_Out_Voltage : eCZone_AC1_In_Voltage;
        auto currentType = a.MeteringDevice.Output ? eCZone_AC1_Out_Current : eCZone_AC1_In_Current;
        auto frequencyType = a.MeteringDevice.Output ? eCZone_AC1_Out_Frequency : eCZone_AC1_In_Frequency;
        auto powerType = a.MeteringDevice.Output ? eCZone_AC1_Out_RealPower : eCZone_AC1_In_RealPower;

        if (line == 1) {
          voltageType = a.MeteringDevice.Output ? eCZone_AC2_Out_Voltage : eCZone_AC2_In_Voltage;
          currentType = a.MeteringDevice.Output ? eCZone_AC2_Out_Current : eCZone_AC2_In_Current;
          frequencyType = a.MeteringDevice.Output ? eCZone_AC2_Out_Frequency : eCZone_AC2_In_Frequency;
          powerType = a.MeteringDevice.Output ? eCZone_AC2_Out_RealPower : eCZone_AC2_In_RealPower;
        } else if (line == 2) {
          voltageType = a.MeteringDevice.Output ? eCZone_AC3_Out_Voltage : eCZone_AC3_In_Voltage;
          currentType = a.MeteringDevice.Output ? eCZone_AC3_Out_Current : eCZone_AC3_In_Current;
          frequencyType = a.MeteringDevice.Output ? eCZone_AC3_Out_Frequency : eCZone_AC3_In_Frequency;
          powerType = a.MeteringDevice.Output ? eCZone_AC3_Out_RealPower : eCZone_AC3_In_RealPower;
        }

        std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
                                     {eCZone_Generic_Instance, false, 0.0f, "Line", line},
                                     {voltageType, false, 0.0f, "Voltage", instance},
                                     {currentType, false, 0.0f, "Current", instance},
                                     {frequencyType, false, 0.0f, "Frequency", instance},
                                     {powerType, false, 0.0f, "Power", instance}};

        auto lastACItem = lastSnapshot.m_ac.find(instance);
        if (lastACItem == lastSnapshot.m_ac.end()) {
          auto emptyItem = std::make_shared<N2KMonitoring::AC>();
          emptyItem->m_instance = instance;

          lastSnapshot.m_ac[instance] = emptyItem;
          lastACItem = lastSnapshot.m_ac.find(instance);
        }

        ProcessFields(fields, line, parentACItem->m_acLines, lastACItem->second->m_acLines, m_UnitConversion,
                      m_DataTypeIndex);
      }
    }

    if (parentACItem->m_acLines.size() > 0) {
      snapshot.m_ac[parentACItem->m_instance] = parentACItem;
    }
  }
}

/**
 * @brief Updates monitoring data for DC electrical systems
 *
 * Processes DC electrical monitoring devices including batteries, DC power systems,
 * and battery management systems. This function has special handling for wake-up
 * scenarios where cached DC data should be used instead of querying live data.
 *
 * In normal operation, monitors:
 * - Voltage levels
 * - Current flow (charging/discharging)
 * - Temperature
 * - State of charge (battery percentage)
 * - Remaining capacity
 * - Time remaining until empty
 * - Time to full charge
 * - Combined time remaining/to charge
 *
 * @param snapshot Reference to current snapshot to populate with DC data
 * @param lastSnapshot Reference to previous snapshot for change detection
 */
void CzoneDatabase::UpdateMonitoringDCs(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                        N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  // Special handling for wake-up scenarios - use cached data instead of live queries
  if (m_WakeUp) {
    // If no previous DC data exists or it matches wake cache, use wake-up data
    if (lastSnapshot.m_dc.size() == 0 || lastSnapshot.m_dc == m_WakeDcMap) {
      snapshot.m_dc = m_WakeDcMap;
      lastSnapshot.m_dc = m_WakeDcMap;
    }
    return;
  }

  // Normal operation - query live DC monitoring data
  auto dc = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayMeteringDC);
  for (auto &d : dc) {
    uint8_t instance = d.MeteringDevice.Instance;

    // Define DC monitoring field mappings for comprehensive battery/DC system monitoring
    std::vector<Field> fields = {
        {eCZone_Generic_Instance, false, 0.0f, "Instance", instance},                         // DC system instance
        {eCZone_DC_Potential, false, 0.0f, "Voltage", instance},                              // Voltage level
        {eCZone_DC_Current, false, 0.0f, "Current", instance},                                // Current flow
        {eCZone_DC_Temperature, false, 0.0f, "Temperature", instance},                        // System temperature
        {eCZone_DC_StateOfCharge, false, 0.0f, "StateOfCharge", instance},                    // Battery percentage
        {eCZone_DC_CapacityRemaining, false, 0.0f, "CapacityRemaining", instance},            // Remaining capacity
        {eCZone_DC_TimeRemaining, false, 0.0f, "TimeRemaining", instance},                    // Time until empty
        {eCZone_DC_TimeToCharge, false, 0.0f, "TimeToCharge", instance},                      // Time to full charge
        {eCZone_DC_TimeRemainingOrToCharge, false, 0.0f, "TimeRemainingOrToCharge", instance} // Combined time info
    };

    // Process DC system fields using standard monitoring pipeline
    ProcessFields(fields, instance, snapshot.m_dc, lastSnapshot.m_dc, m_UnitConversion, m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringTemperatures(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                                 N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto temperatures = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayMonitoringTemperature);
  for (auto &t : temperatures) {
    uint8_t instance = t.MonitoringDevice.Instance;
    tCZoneDataType dataType = t.MonitoringDevice.HighTemperature == CZONE_TRUE ? eCZone_Environment_HighTemperature
                                                                               : eCZone_Environment_Temperature;

    std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
                                 {dataType, false, 0.0f, "Temperature", instance}};

    ProcessFields(fields, instance, snapshot.m_temperatures, lastSnapshot.m_temperatures, m_UnitConversion,
                  m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringPressures(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                              N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto pressures = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayMonitoringPressure);
  for (auto &p : pressures) {
    uint8_t instance = p.MonitoringDevice.Instance;
    tCZoneDataType dataType = p.MonitoringDevice.AtmosphericPressure == CZONE_TRUE
                                  ? eCZone_Environment_AtmosphericPressure
                                  : eCZone_Environment_Pressure;

    std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
                                 {dataType, false, 0.0f, "Pressure", instance}};

    ProcessFields(fields, instance, snapshot.m_pressures, lastSnapshot.m_pressures, m_UnitConversion, m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringHVACs(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                          N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto hvacs = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayHvac);
  for (auto &h : hvacs) {
    uint8_t instance = h.HvacDevice.HvacInstance;

    std::vector<Field> fields = {
        {eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
        {eCZone_Hvac_OperatingMode, false, 0.0f, "OperationMode", instance},
        {eCZone_Hvac_FanMode, false, 0.0f, "FanMode", instance},
        {eCZone_Hvac_FanSpeed, false, 0.0f, "Fanspeed", instance},
        {eCZone_Environment_SetTemperature, false, 0.0f, "EnvironmentSetTemperature", instance},
        {eCZone_Environment_Temperature, false, 0.0f, "EnvironmentTemperature", instance}};

    ProcessFields(fields, instance, snapshot.m_hvacs, lastSnapshot.m_hvacs, m_UnitConversion, m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringAwnings(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                            N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto awnings = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayZipdeeAwning);
  for (auto &a : awnings) {
    uint8_t instance = a.AwningDevice.Instance;

    std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
                                 {eCZone_ZipdeeAwning_State, false, 0.0f, "State", instance}};

    ProcessFields(fields, instance, snapshot.m_awnings, lastSnapshot.m_awnings, m_UnitConversion, m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringThirdPartyGenerators(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                                         N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto generators = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayThirdPartyGenerator);
  for (auto &g : generators) {
    uint8_t instance = g.ThirdPartyGeneratorDevice.SignalInstance;

    std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
                                 {eCZone_Signal_OnTime, false, 0.0f, "OnTime", instance},
                                 {eCZone_Signal_Status, false, 0.0f, "Status", instance}};

    ProcessFields(fields, instance, snapshot.m_thirdPartyGenerators, lastSnapshot.m_thirdPartyGenerators,
                  m_UnitConversion, m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringInverterChargers(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                                     N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto inverterChargers = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayInverterCharger);
  for (auto &i : inverterChargers) {
    uint32_t instance =
        static_cast<uint32_t>(i.InverterChargerDevice.InverterInstance) << 8 | i.InverterChargerDevice.ChargerInstance;

    std::vector<Field> fields = {
        {eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
        {eCZone_Inverter_Enabled, false, 0.0f, "InverterEnable", i.InverterChargerDevice.InverterInstance},
        {eCZone_Inverter_OperatingState, false, 0.0f, "InverterState", i.InverterChargerDevice.InverterInstance},
        {eCZone_Charger_Enabled, false, 0.0f, "ChargerEnable", i.InverterChargerDevice.ChargerInstance},
        {eCZone_Charger_OperatingState, false, 0.0f, "ChargerState", i.InverterChargerDevice.ChargerInstance}};

    ProcessFields(fields, instance, snapshot.m_inverterChargers, lastSnapshot.m_inverterChargers, m_UnitConversion,
                  m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringTyrepressures(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                                  N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto tyrePressures = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayTyrePressure);
  for (auto &t : tyrePressures) {
    for (int i = 0; i < t.TyrePressure.NumberTyreInstances; i++) {
      auto tyreInstance = t.TyrePressure.TyreInstances[i];
      std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", tyreInstance},
                                   {eCZone_Tyre_Pressure, false, 0.0f, "Pressure", tyreInstance},
                                   {eCZone_Tyre_Temperature, false, 0.0f, "Temperature", tyreInstance},
                                   {eCZone_Tyre_Status, false, 0.0f, "Status", tyreInstance},
                                   {eCZone_Tyre_LimitStatus, false, 0.0f, "LimitStatus", tyreInstance}};

      ProcessFields(fields, tyreInstance, snapshot.m_tyrepressures, lastSnapshot.m_tyrepressures, m_UnitConversion,
                    m_DataTypeIndex);
    }

    for (int i = 0; i < t.TyrePressure.NumberSpareInstances; i++) {
      auto tyreInstance = t.TyrePressure.TyreInstanceSpare[i];
      std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", tyreInstance},
                                   {eCZone_Tyre_Pressure, false, 0.0f, "Pressure", tyreInstance},
                                   {eCZone_Tyre_Temperature, false, 0.0f, "Temperature", tyreInstance},
                                   {eCZone_Tyre_Status, false, 0.0f, "Status", tyreInstance},
                                   {eCZone_Tyre_LimitStatus, false, 0.0f, "LimitStatus", tyreInstance}};

      ProcessFields(fields, tyreInstance, snapshot.m_tyrepressures, lastSnapshot.m_tyrepressures, m_UnitConversion,
                    m_DataTypeIndex);
    }
  }
}

void CzoneDatabase::UpdateMonitoringAudioStereos(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                                 N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto audioStereos = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayAudioStereo);
  for (auto &a : audioStereos) {
    uint8_t instance = a.AudioStereoDevice.Instance;

    std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
                                 {eCZone_AudioStereo_Power, false, 0.0f, "Power", instance},
                                 {eCZone_AudioStereo_Mute, false, 0.0f, "Mute", instance},
                                 {eCZone_AudioStereo_AudioStatus, false, 0.0f, "AudioStatus", instance},
                                 {eCZone_AudioStereo_Sourcemode, false, 0.0f, "SourceMode", instance},
                                 {eCZone_AudioStereo_Volume, false, 0.0f, "Volume", instance}};

    ProcessFields(fields, instance, snapshot.m_audioStereos, lastSnapshot.m_audioStereos, m_UnitConversion,
                  m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateMonitoringGNSS(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                         N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  // [x] GNSS
  // #ifdef EUROPA_GNSS_SUPPORT
  //   auto gnss = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayGNSS);
  //   for (auto &g : gnss) {
  //     uint8_t instance = g.DynamicDevice.Instance;

  //     std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Instance", instance},
  //                                  {eCZone_GPS_Latitude, false, 0.0f, "Latitude", instance},
  //                                  {eCZone_GPS_Longitude, false, 0.0f, "Longitude", instance},
  //                                  {eCZone_GPS_Cog, false, 0.0f, "Cog", instance},
  //                                  {eCZone_GPS_Sog, false, 0.0f, "Sog", instance},
  //                                  {eCZone_GPS_MagneticVariation, false, 0.0f, "MagneticVariation", instance},
  //                                  {eCZone_GPS_SatellitesUsed, false, 0.0f, "SatellitesInFix", instance},
  //                                  {eCZone_GPS_BestOfFourSatellitesSNR, false, 0.0f, "BestOfFourSatellitesSNR",
  //                                  instance}, {eCZone_GPS_Method, false, 0.0f, "Method", instance},
  //                                  {eCZone_GPS_FixType, false, 0.0f, "FixType", instance},
  //                                  {eCZone_GPS_HDOP, false, 0.0f, "Hdop", instance},
  //                                  {eCZone_GPS_PDOP, false, 0.0f, "Pdop", instance},
  //                                  {eCZone_GPS_VDOP, false, 0.0f, "Vdop", instance}};

  //     ProcessFields(fields, instance, snapshot.mutable_gnss(), lastSnapshot.mutable_gnss(), m_UnitConversion,
  //                   m_DataTypeIndex);

  //     std::vector<FieldS32> gpsPosFields = {{eCZone_GPS_Latitude_S32, false, 0, instance},
  //                                           {eCZone_GPS_Longitude_S32, false, 0, instance}};

  //     auto lastSnapShotGnssForInstance = lastSnapshot.gnss().find(instance);
  //     bool const lastInstanceFound = !(lastSnapShotGnssForInstance == lastSnapshot.gnss().end());
  //     N2KMonitoring::ValueDouble lastLatitudeDeg;
  //     N2KMonitoring::ValueDouble lastLongitudeDeg;
  //     if (lastInstanceFound) {
  //       lastLatitudeDeg = lastSnapShotGnssForInstance->second.latitudedeg();
  //       lastLongitudeDeg = lastSnapShotGnssForInstance->second.longitudedeg();
  //     }

  //     for (auto &gpsPosField : gpsPosFields) {
  //       bool validValue = GetValueS32ForInstanceOrId(gpsPosField, m_DataTypeIndex);
  //       int32_t const gpsPosVal32 = gpsPosField.Value;
  //       double gpsPosVal = ((double)gpsPosVal32 * 1e-7);

  //       N2KMonitoring::ValueDouble nVal;
  //       nVal.set_value(gpsPosVal);
  //       nVal.set_valid(validValue);

  //       if (gpsPosField.Type == eCZone_GPS_Latitude_S32) {
  //         if (!lastInstanceFound || !CheckIfValueDoubleAreEqual(nVal, lastLatitudeDeg)) {
  //           (*snapshot.mutable_gnss())[instance].mutable_latitudedeg()->CopyFrom(nVal);
  //           (*lastSnapshot.mutable_gnss())[instance].mutable_latitudedeg()->CopyFrom(nVal);
  //         }
  //       } else if (gpsPosField.Type == eCZone_GPS_Longitude_S32) {
  //         if (!lastInstanceFound || !CheckIfValueDoubleAreEqual(nVal, lastLongitudeDeg)) {
  //           (*snapshot.mutable_gnss())[instance].mutable_longitudedeg()->CopyFrom(nVal);
  //           (*lastSnapshot.mutable_gnss())[instance].mutable_longitudedeg()->CopyFrom(nVal);
  //         }
  //       }
  //     }

  //     if (snapshot.gnss_size() > 0) {
  //       if ((*snapshot.mutable_gnss())[instance].has_latitude() &&
  //           !(*snapshot.mutable_gnss())[instance].has_longitude()) {
  //         (*snapshot.mutable_gnss())[instance].mutable_longitude()->CopyFrom(
  //             (*lastSnapshot.mutable_gnss())[instance].longitude());
  //       } else if (!(*snapshot.mutable_gnss())[instance].has_latitude() &&
  //                  (*snapshot.mutable_gnss())[instance].has_longitude()) {
  //         (*snapshot.mutable_gnss())[instance].mutable_latitude()->CopyFrom(
  //             (*lastSnapshot.mutable_gnss())[instance].latitude());
  //       }

  //       if ((*snapshot.mutable_gnss())[instance].has_latitudedeg() &&
  //           !(*snapshot.mutable_gnss())[instance].has_longitudedeg()) {
  //         (*snapshot.mutable_gnss())[instance].mutable_longitudedeg()->CopyFrom(
  //             (*lastSnapshot.mutable_gnss())[instance].longitudedeg());
  //       } else if (!(*snapshot.mutable_gnss())[instance].has_latitudedeg() &&
  //                  (*snapshot.mutable_gnss())[instance].has_longitudedeg()) {
  //         (*snapshot.mutable_gnss())[instance].mutable_latitudedeg()->CopyFrom(
  //             (*lastSnapshot.mutable_gnss())[instance].latitudedeg());
  //       }
  //     }

  //     std::vector<Field> timeFields = {
  //         {eCZone_DateTime_UTCDate, false, 0.0f, "UTCDate", instance},
  //         {eCZone_DateTime_UTCTime, false, 0.0f, "UTCTime", instance},
  //         {eCZone_DateTime_TimeLocalOffset, false, 0.0f, "TimeLocalOffset", instance},
  //     };

  //     std::unordered_map<uint32_t, struct MonitoringValue> valueMap;
  //     bool validValue = GetValuesForInstanceOrId(timeFields, m_UnitConversion, m_DataTypeIndex, valueMap);
  //     if (timeFields.at(0).Valid && timeFields.at(1).Valid && timeFields.at(2).Valid) {
  //       timespec tmSpec;
  //       tmSpec.tv_sec =
  //           static_cast<time_t>(timeFields.at(0).Value) * 24 * 60 * 60 +
  //           static_cast<time_t>(timeFields.at(1).Value);
  //       tmSpec.tv_nsec = 0;
  //       std::string iso8601 = GNSSInterface::TimespecToIso8601(tmSpec);

  //       auto lastSnapShotEntry = lastSnapshot.mutable_gnss()->find(instance);
  //       if (lastSnapShotEntry == lastSnapshot.mutable_gnss()->end() ||
  //           iso8601 != lastSnapShotEntry->second.utcdatetime()) {
  //         (*snapshot.mutable_gnss())[instance].set_utcdatetime(iso8601);
  //         (*lastSnapshot.mutable_gnss())[instance].set_utcdatetime(iso8601);

  //         auto offset = new N2KMonitoring::ValueU32();
  //         offset->set_value(static_cast<uint32_t>(timeFields.at(2).Value));
  //         offset->set_valid(timeFields.at(2).Valid);
  //         (*snapshot.mutable_gnss())[instance].set_allocated_timeoffset(offset);
  //       }
  //     }
  //   }
  // #endif
}

void CzoneDatabase::UpdateMonitoringBinaryLogicStates(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                                      N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  auto bls = m_canService.Interface()->displayListNoLock(eCZoneStructDisplayBinaryLogicState);

  for (auto &b : bls) {
    uint32_t const address = b.BinaryLogicState.Address;
    uint32_t const dipswitch = (address >> 8) & 0xFF;
    uint32_t const data_type_offset = ((address >> 5) & 0x7);
    tCZoneDataType dataType = static_cast<tCZoneDataType>(eCZone_Logic_BinaryStateInstance0 + data_type_offset);

    // Based on function "void tCZoneNmea2kDataDevice::BEPPGN65308CallBack(const tCZoneNetworkMsg* msg)"
    // BinaryLogicStates uses dipswitch as instance, and data type is 0-7
    uint32_t instance = dipswitch;

    std::vector<Field> fields = {{eCZone_Generic_Instance, false, 0.0f, "Dipswitch", instance},
                                 {eCZone_Generic_Instance, false, 0.0f, "Instance", data_type_offset},
                                 {dataType, false, 0.0f, "States", instance}};

    ProcessFields(fields, instance, snapshot.m_binaryLogicState, lastSnapshot.m_binaryLogicState, m_UnitConversion,
                  m_DataTypeIndex);
  }
}

void CzoneDatabase::UpdateNetworkStatus(N2KMonitoring::SnapshotInstanceIdMap &snapshot,
                                        N2KMonitoring::SnapshotInstanceIdMap &lastSnapshot) {
  const std::lock_guard<std::mutex> lock(m_NetworkStatusMutex);
  if (m_NetworkStatus.m_ethernetStatus.length() == 0) {
    BOOST_LOG_TRIVIAL(error) << "UpdateNetworkStatus: No NetworkStatus received yet";
    return;
  }

  if (lastSnapshot.m_networkStatus == nullptr) {
    lastSnapshot.m_networkStatus = std::make_shared<N2KMonitoring::NetworkStatus>(m_NetworkStatus);
    snapshot.m_networkStatus = std::make_shared<N2KMonitoring::NetworkStatus>(m_NetworkStatus);
  } else {
    if (*lastSnapshot.m_networkStatus != m_NetworkStatus) {
      lastSnapshot.m_networkStatus = std::make_shared<N2KMonitoring::NetworkStatus>(m_NetworkStatus);
      snapshot.m_networkStatus = std::make_shared<N2KMonitoring::NetworkStatus>(m_NetworkStatus);
    }
  }
}

void CzoneDatabase::registerDbus(std::shared_ptr<DbusService> dbusService) {
  dbusService->registerService("SingleSnapshot", "czone",
                               [ptr = this]() -> std::string { return ptr->m_LastSnapshot.tojson().dump(); });

  dbusService->registerSignal("Snapshot", "czone");

  auto task = [this, &dbusService]() {
    while (!this->m_workerpool.isShutdown()) {
      try {
        {
          const std::lock_guard<std::mutex> lock(m_SnapshotMutex);
          auto delta = this->Snapshot();
          if (delta) {
            BOOST_LOG_TRIVIAL(debug) << "CzoneDatabase::registerDbus::Task delta detected.";
            dbusService->emitSignal("Snapshot", "czone", this->m_Snapshot.tojson().dump());
          }
        }
        std::this_thread::sleep_for(std::chrono::seconds(10));
      } catch (const std::exception &e) {
        BOOST_LOG_TRIVIAL(error) << "CzoneDatabase::registerDbus::Task snapshot scan exception: " << e.what();
      }
    }
  };
  m_workerpool.addTask(std::move(task));
}