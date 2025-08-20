#include <tuple>

#include "modules/czone/monitoringdata.h"

namespace {
template <typename MapType>
bool deepCompareMap(const MapType &a, const MapType &b) {
  if (a.size() != b.size())
    return false;
  for (const auto &[key, value] : a) {
    auto it = b.find(key);
    if (it == b.end() || ((value == nullptr) != (it->second == nullptr)))
      return false;
    if (value && it->second && *value != *(it->second))
      return false;
  }
  return true;
}
} // namespace

N2KMonitoring::SnapshotInstanceIdMap::SnapshotInstanceIdMap() {
  m_circuits.clear();
  m_modes.clear();
  m_tanks.clear();
  m_engines.clear();
  m_ac.clear();
  m_dc.clear();
  m_temperatures.clear();
  m_pressures.clear();
  m_hvacs.clear();
  m_awnings.clear();
  m_thirdPartyGenerators.clear();
  m_inverterChargers.clear();
  m_tyrepressures.clear();
  m_audioStereos.clear();
  m_acMainContactors.clear();
  m_gnss.clear();
  m_monitoringKeyValue.clear();
  m_binaryLogicState.clear();

  // m_networkStatus = nullptr;
  m_timeStamp = "";
}

N2KMonitoring::SnapshotInstanceIdMap::~SnapshotInstanceIdMap() { clear(); }

void N2KMonitoring::SnapshotInstanceIdMap::clear() {
  m_circuits.clear();
  m_modes.clear();
  m_tanks.clear();
  m_engines.clear();
  m_ac.clear();
  m_dc.clear();
  m_temperatures.clear();
  m_pressures.clear();
  m_hvacs.clear();
  m_awnings.clear();
  m_thirdPartyGenerators.clear();
  m_inverterChargers.clear();
  m_tyrepressures.clear();
  m_audioStereos.clear();
  m_acMainContactors.clear();
  m_gnss.clear();
  m_monitoringKeyValue.clear();
  m_binaryLogicState.clear();

  // if (m_networkStatus != nullptr) {
  //   m_networkStatus->clear();
  // }
  // m_networkStatus = nullptr;
  m_timeStamp = "";
}

void N2KMonitoring::NetworkStatus::clear() {
  m_ethernetStatus = "";
  m_ethernetInternetConnectivity = false;
  m_ethernetIp = "";
  m_ethernetId = "";
  m_wifiStatus = "";
  m_wifiInternetConnectivity = false;
  m_wifiIp = "";
  m_wifiSsid = "";
  m_wifiSecurity = "";
  m_wifiType = "";
  m_wifiChannel = 0;
  m_wifiSignalStrengthDbm = 0;
  m_hotspotStatus = "";
  m_hotspotIp = "";
  m_hotspotSsid = "";
  m_hotspotPassword = "";
  m_hotspotSecurity = "";
  m_hotspotType = "";
  m_hotspotChannel = 0;
  m_cellularStatus = "";
  m_cellularInternetConnectivity = false;
  m_cellularIp = "";
  m_cellularOperator = "";
  m_cellularType = "";
  m_cellularSignalStrengthDbm = 0;
  m_cellularSimIccid = "";
  m_cellularSimEid = "";
  m_cellularSimImsi = "";
}

void N2KMonitoring::MonitoringKeyValueMap::clear() { m_keyValueMap.clear(); }

bool N2KMonitoring::AC::operator==(const N2KMonitoring::AC &other) const {
  return deepCompareMap(m_acLines, other.m_acLines) && std::tie(m_instance) == std::tie(other.m_instance);
}

bool N2KMonitoring::SnapshotInstanceIdMap::operator==(const N2KMonitoring::SnapshotInstanceIdMap &other) const {
  return deepCompareMap(m_circuits, other.m_circuits) && deepCompareMap(m_modes, other.m_modes) &&
         deepCompareMap(m_tanks, other.m_tanks) && deepCompareMap(m_engines, other.m_engines) &&
         deepCompareMap(m_ac, other.m_ac) && deepCompareMap(m_dc, other.m_dc) &&
         deepCompareMap(m_temperatures, other.m_temperatures) && deepCompareMap(m_pressures, other.m_pressures) &&
         deepCompareMap(m_hvacs, other.m_hvacs) && deepCompareMap(m_awnings, other.m_awnings) &&
         deepCompareMap(m_thirdPartyGenerators, other.m_thirdPartyGenerators) &&
         deepCompareMap(m_inverterChargers, other.m_inverterChargers) &&
         deepCompareMap(m_tyrepressures, other.m_tyrepressures) &&
         deepCompareMap(m_audioStereos, other.m_audioStereos) &&
         deepCompareMap(m_acMainContactors, other.m_acMainContactors) && deepCompareMap(m_gnss, other.m_gnss) &&
         deepCompareMap(m_monitoringKeyValue, other.m_monitoringKeyValue) &&
         deepCompareMap(m_binaryLogicState, other.m_binaryLogicState);
}

bool N2KMonitoring::MonitoringKeyValueMap::operator==(const MonitoringKeyValueMap &other) const {
  return deepCompareMap(m_keyValueMap, other.m_keyValueMap);
}

auto N2KMonitoring::Circuit::get(const std::string &memberName) -> N2KMonitoring::Circuit::CircuitValue {
  if (memberName == "Id")
    return &m_id;
  if (memberName == "SystemsOn")
    return &m_systemsOn;
  if (memberName == "Level")
    return &m_level;
  if (memberName == "OnCount")
    return &m_onCount;
  if (memberName == "OnTime")
    return &m_onTime;
  if (memberName == "SequentialState")
    return &m_sequentialState;
  if (memberName == "ModesSystemOn")
    return &m_modesSystemOn;
  if (memberName == "Current")
    return &m_current;
  if (memberName == "Fault")
    return &m_fault;
  if (memberName == "ACSourceAvailable")
    return &m_aCSourceAvailable;
  if (memberName == "IsOffline")
    return &m_isOffline;
  throw std::invalid_argument("Invalid member name (Circuit): " + memberName);
}

auto N2KMonitoring::Circuit::get(const std::string &memberName) const -> N2KMonitoring::Circuit::CircuitValueConst {
  if (memberName == "Id")
    return &m_id;
  if (memberName == "SystemsOn")
    return &m_systemsOn;
  if (memberName == "Level")
    return &m_level;
  if (memberName == "OnCount")
    return &m_onCount;
  if (memberName == "OnTime")
    return &m_onTime;
  if (memberName == "SequentialState")
    return &m_sequentialState;
  if (memberName == "ModesSystemOn")
    return &m_modesSystemOn;
  if (memberName == "Current")
    return &m_current;
  if (memberName == "Fault")
    return &m_fault;
  if (memberName == "ACSourceAvailable")
    return &m_aCSourceAvailable;
  if (memberName == "IsOffline")
    return &m_isOffline;
  throw std::invalid_argument("Invalid member name (Circuit): " + memberName);
}

auto N2KMonitoring::Tank::get(const std::string &memberName) -> N2KMonitoring::Tank::TankValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "LevelPercent") {
    return &m_levelPercent;
  }
  if (memberName == "Level") {
    return &m_level;
  }
  if (memberName == "Capacity") {
    return &m_capacity;
  }
  if (memberName == "TankType") {
    return &m_tankType;
  }
  throw std::invalid_argument("Invalid member name (Tank): " + memberName);
}

auto N2KMonitoring::Tank::get(const std::string &memberName) const -> N2KMonitoring::Tank::TankValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "LevelPercent") {
    return &m_levelPercent;
  }
  if (memberName == "Level") {
    return &m_level;
  }
  if (memberName == "Capacity") {
    return &m_capacity;
  }
  if (memberName == "TankType") {
    return &m_tankType;
  }
  throw std::invalid_argument("Invalid member name (Tank): " + memberName);
}

auto N2KMonitoring::Engine::get(const std::string &memberName) -> N2KMonitoring::Engine::EngineValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Speed") {
    return &m_speed;
  }
  if (memberName == "BoostPressure") {
    return &m_boostPressure;
  }
  if (memberName == "Trim") {
    return &m_trim;
  }
  if (memberName == "OilPressure") {
    return &m_oilPressure;
  }
  if (memberName == "OilTemperature") {
    return &m_oilTemperature;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }
  if (memberName == "AlternatorPotential") {
    return &m_alternatorPotential;
  }
  if (memberName == "FuelRate") {
    return &m_fuelRate;
  }
  if (memberName == "TotalEngineHours") {
    return &m_totalEngineHours;
  }
  if (memberName == "CoolantPressure") {
    return &m_coolantPressure;
  }
  if (memberName == "CoolantTemperature") {
    return &m_coolantTemperature;
  }
  if (memberName == "FuelPressure") {
    return &m_fuelPressure;
  }
  if (memberName == "DiscreteStatus1") {
    return &m_discreteStatus1;
  }
  if (memberName == "DiscreteStatus2") {
    return &m_discreteStatus2;
  }
  if (memberName == "PercentEngineLoad") {
    return &m_percentEngineLoad;
  }
  if (memberName == "PercentEngineTorque") {
    return &m_percentEngineTorque;
  }
  if (memberName == "EngineState") {
    return &m_engineState;
  }
  if (memberName == "ActiveEnginesId") {
    return &m_activeEnginesId;
  }
  throw std::invalid_argument("Invalid member name (Engine): " + memberName);
}

auto N2KMonitoring::Engine::get(const std::string &memberName) const -> N2KMonitoring::Engine::EngineValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Speed") {
    return &m_speed;
  }
  if (memberName == "BoostPressure") {
    return &m_boostPressure;
  }
  if (memberName == "Trim") {
    return &m_trim;
  }
  if (memberName == "OilPressure") {
    return &m_oilPressure;
  }
  if (memberName == "OilTemperature") {
    return &m_oilTemperature;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }
  if (memberName == "AlternatorPotential") {
    return &m_alternatorPotential;
  }
  if (memberName == "FuelRate") {
    return &m_fuelRate;
  }
  if (memberName == "TotalEngineHours") {
    return &m_totalEngineHours;
  }
  if (memberName == "CoolantPressure") {
    return &m_coolantPressure;
  }
  if (memberName == "CoolantTemperature") {
    return &m_coolantTemperature;
  }
  if (memberName == "FuelPressure") {
    return &m_fuelPressure;
  }
  if (memberName == "DiscreteStatus1") {
    return &m_discreteStatus1;
  }
  if (memberName == "DiscreteStatus2") {
    return &m_discreteStatus2;
  }
  if (memberName == "PercentEngineLoad") {
    return &m_percentEngineLoad;
  }
  if (memberName == "PercentEngineTorque") {
    return &m_percentEngineTorque;
  }
  if (memberName == "EngineState") {
    return &m_engineState;
  }
  if (memberName == "ActiveEnginesId") {
    return &m_activeEnginesId;
  }
  throw std::invalid_argument("Invalid member name (Engine): " + memberName);
}

auto N2KMonitoring::ACLine::get(const std::string &memberName) -> N2KMonitoring::ACLine::ACLineValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Line") {
    return &m_line;
  }
  if (memberName == "Voltage") {
    return &m_voltage;
  }
  if (memberName == "Current") {
    return &m_current;
  }
  if (memberName == "Frequency") {
    return &m_frequency;
  }
  if (memberName == "Power") {
    return &m_power;
  }

  throw std::invalid_argument("Invalid member name (ACLine): " + memberName);
}

auto N2KMonitoring::ACLine::get(const std::string &memberName) const -> N2KMonitoring::ACLine::ACLineValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Line") {
    return &m_line;
  }
  if (memberName == "Voltage") {
    return &m_voltage;
  }
  if (memberName == "Current") {
    return &m_current;
  }
  if (memberName == "Frequency") {
    return &m_frequency;
  }
  if (memberName == "Power") {
    return &m_power;
  }

  throw std::invalid_argument("Invalid member name (ACLine): " + memberName);
}

auto N2KMonitoring::AC::get(const std::string &memberName) -> N2KMonitoring::AC::ACValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "AClines") {
    return &m_acLines;
  }
  throw std::invalid_argument("Invalid member name (AC): " + memberName);
}

auto N2KMonitoring::AC::get(const std::string &memberName) const -> N2KMonitoring::AC::ACValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "AClines") {
    return &m_acLines;
  }
  throw std::invalid_argument("Invalid member name (AC): " + memberName);
}

auto N2KMonitoring::DC::get(const std::string &memberName) -> N2KMonitoring::DC::DCValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Voltage") {
    return &m_voltage;
  }
  if (memberName == "Current") {
    return &m_current;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }
  if (memberName == "StateOfCharge") {
    return &m_stateOfCharge;
  }
  if (memberName == "CapacityRemaining") {
    return &m_capacityRemaining;
  }
  if (memberName == "TimeRemaining") {
    return &m_timeRemaining;
  }
  if (memberName == "TimeToCharge") {
    return &m_timeToCharge;
  }
  if (memberName == "TimeRemainingOrToCharge") {
    return &m_timeRemainingOrToCharge;
  }

  throw std::invalid_argument("Invalid member name (DC): " + memberName);
}

auto N2KMonitoring::DC::get(const std::string &memberName) const -> N2KMonitoring::DC::DCValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Voltage") {
    return &m_voltage;
  }
  if (memberName == "Current") {
    return &m_current;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }
  if (memberName == "StateOfCharge") {
    return &m_stateOfCharge;
  }
  if (memberName == "CapacityRemaining") {
    return &m_capacityRemaining;
  }
  if (memberName == "TimeRemaining") {
    return &m_timeRemaining;
  }
  if (memberName == "TimeToCharge") {
    return &m_timeToCharge;
  }
  if (memberName == "TimeRemainingOrToCharge") {
    return &m_timeRemainingOrToCharge;
  }

  throw std::invalid_argument("Invalid member name (DC): " + memberName);
}

auto N2KMonitoring::Temperature::get(const std::string &memberName) -> N2KMonitoring::Temperature::TemperatureValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }

  throw std::invalid_argument("Invalid member name (Temperature): " + memberName);
}

auto N2KMonitoring::Temperature::get(const std::string &memberName) const
    -> N2KMonitoring::Temperature::TemperatureValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }

  throw std::invalid_argument("Invalid member name (Temperature): " + memberName);
}

auto N2KMonitoring::Pressure::get(const std::string &memberName) -> N2KMonitoring::Pressure::PressureValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Pressure") {
    return &m_pressure;
  }

  throw std::invalid_argument("Invalid member name (Pressure): " + memberName);
}

auto N2KMonitoring::Pressure::get(const std::string &memberName) const -> N2KMonitoring::Pressure::PressureValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Pressure") {
    return &m_pressure;
  }

  throw std::invalid_argument("Invalid member name (Pressure): " + memberName);
}

auto N2KMonitoring::HVAC::get(const std::string &memberName) -> N2KMonitoring::HVAC::HVACValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "OperationMode") {
    return &m_operationMode;
  }
  if (memberName == "FanMode") {
    return &m_fanMode;
  }
  if (memberName == "FanSpeed") {
    return &m_fanSpeed;
  }
  if (memberName == "EnvironmentSetTemperature") {
    return &m_environmentSetTemperature;
  }
  if (memberName == "EnvironmentTemperature") {
    return &m_environmentTemperature;
  }

  throw std::invalid_argument("Invalid member name (HVAC): " + memberName);
}

auto N2KMonitoring::HVAC::get(const std::string &memberName) const -> N2KMonitoring::HVAC::HVACValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "OperationMode") {
    return &m_operationMode;
  }
  if (memberName == "FanMode") {
    return &m_fanMode;
  }
  if (memberName == "FanSpeed") {
    return &m_fanSpeed;
  }
  if (memberName == "EnvironmentSetTemperature") {
    return &m_environmentSetTemperature;
  }
  if (memberName == "EnvironmentTemperature") {
    return &m_environmentTemperature;
  }

  throw std::invalid_argument("Invalid member name (HVAC): " + memberName);
}

auto N2KMonitoring::ZipdeeAwning::get(const std::string &memberName) -> N2KMonitoring::ZipdeeAwning::ZipdeeAwningValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "State") {
    return &m_state;
  }

  throw std::invalid_argument("Invalid member name (ZipdeeAwning): " + memberName);
}

auto N2KMonitoring::ZipdeeAwning::get(const std::string &memberName) const
    -> N2KMonitoring::ZipdeeAwning::ZipdeeAwningValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "State") {
    return &m_state;
  }

  throw std::invalid_argument("Invalid member name (ZipdeeAwning): " + memberName);
}

auto N2KMonitoring::ThirdPartyGenerator::get(const std::string &memberName)
    -> N2KMonitoring::ThirdPartyGenerator::ThirdPartyGeneratorValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "OnTime") {
    return &m_onTime;
  }
  if (memberName == "Status") {
    return &m_status;
  }

  throw std::invalid_argument("Invalid member name (ThirdPartyGenerator): " + memberName);
}

auto N2KMonitoring::ThirdPartyGenerator::get(const std::string &memberName) const
    -> N2KMonitoring::ThirdPartyGenerator::ThirdPartyGeneratorValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "OnTime") {
    return &m_onTime;
  }
  if (memberName == "Status") {
    return &m_status;
  }

  throw std::invalid_argument("Invalid member name (ThirdPartyGenerator): " + memberName);
}

auto N2KMonitoring::InverterCharger::get(const std::string &memberName)
    -> N2KMonitoring::InverterCharger::InverterChargerValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "InverterInstance") {
    return &m_inverterInstance;
  }
  if (memberName == "ChargerInstance") {
    return &m_chargerInstance;
  }
  if (memberName == "InverterEnable") {
    return &m_inverterEnable;
  }
  if (memberName == "InverterState") {
    return &m_inverterState;
  }
  if (memberName == "ChargerEnable") {
    return &m_chargerEnable;
  }
  if (memberName == "ChargerState") {
    return &m_chargerState;
  }
  throw std::invalid_argument("Invalid member name (InverterCharger): " + memberName);
}

auto N2KMonitoring::InverterCharger::get(const std::string &memberName) const
    -> N2KMonitoring::InverterCharger::InverterChargerValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "InverterInstance") {
    return &m_inverterInstance;
  }
  if (memberName == "ChargerInstance") {
    return &m_chargerInstance;
  }
  if (memberName == "InverterEnable") {
    return &m_inverterEnable;
  }
  if (memberName == "InverterState") {
    return &m_inverterState;
  }
  if (memberName == "ChargerEnable") {
    return &m_chargerEnable;
  }
  if (memberName == "ChargerState") {
    return &m_chargerState;
  }
  throw std::invalid_argument("Invalid member name (InverterCharger): " + memberName);
}

auto N2KMonitoring::TyrePressure::get(const std::string &memberName) -> N2KMonitoring::TyrePressure::TyrePressureValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Pressure") {
    return &m_pressure;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }
  if (memberName == "Status") {
    return &m_status;
  }
  if (memberName == "LimitStatus") {
    return &m_limitStatus;
  }

  throw std::invalid_argument("Invalid member name (TyrePressure): " + memberName);
}

auto N2KMonitoring::TyrePressure::get(const std::string &memberName) const
    -> N2KMonitoring::TyrePressure::TyrePressureValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Pressure") {
    return &m_pressure;
  }
  if (memberName == "Temperature") {
    return &m_temperature;
  }
  if (memberName == "Status") {
    return &m_status;
  }
  if (memberName == "LimitStatus") {
    return &m_limitStatus;
  }

  throw std::invalid_argument("Invalid member name (TyrePressure): " + memberName);
}

auto N2KMonitoring::AudioStereo::get(const std::string &memberName) -> N2KMonitoring::AudioStereo::AudioStereoValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Power") {
    return &m_power;
  }
  if (memberName == "Mute") {
    return &m_mute;
  }
  if (memberName == "AudioStatus") {
    return &m_audioStatus;
  }
  if (memberName == "SourceMode") {
    return &m_sourceMode;
  }
  if (memberName == "Volume") {
    return &m_volume;
  }

  throw std::invalid_argument("Invalid member name (AudioStereo): " + memberName);
}

auto N2KMonitoring::AudioStereo::get(const std::string &memberName) const
    -> N2KMonitoring::AudioStereo::AudioStereoValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Power") {
    return &m_power;
  }
  if (memberName == "Mute") {
    return &m_mute;
  }
  if (memberName == "AudioStatus") {
    return &m_audioStatus;
  }
  if (memberName == "SourceMode") {
    return &m_sourceMode;
  }
  if (memberName == "Volume") {
    return &m_volume;
  }

  throw std::invalid_argument("Invalid member name (AudioStereo): " + memberName);
}

auto N2KMonitoring::ACMainContactor::get(const std::string &memberName)
    -> N2KMonitoring::ACMainContactor::ACMainContactorValue {
  if (memberName == "SystemStateId") {
    return &m_systemStateId;
  }
  if (memberName == "ACContactorSystemsState") {
    return &m_acContactorSystemsState;
  }
  if (memberName == "ACContactorSourceAvailable") {
    return &m_acContactorSourceAvailable;
  }
  if (memberName == "ReversePolarity") {
    return &m_reversePolarity;
  }
  if (memberName == "ACContactorAutoChangeOver") {
    return &m_acContactorAutoChangeOver;
  }
  if (memberName == "ManualOverride") {
    return &m_manualOverride;
  }

  throw std::invalid_argument("Invalid member name (ACMainContactor): " + memberName);
}

auto N2KMonitoring::ACMainContactor::get(const std::string &memberName) const
    -> N2KMonitoring::ACMainContactor::ACMainContactorValueConst {
  if (memberName == "SystemStateId") {
    return &m_systemStateId;
  }
  if (memberName == "ACContactorSystemsState") {
    return &m_acContactorSystemsState;
  }
  if (memberName == "ACContactorSourceAvailable") {
    return &m_acContactorSourceAvailable;
  }
  if (memberName == "ReversePolarity") {
    return &m_reversePolarity;
  }
  if (memberName == "ACContactorAutoChangeOver") {
    return &m_acContactorAutoChangeOver;
  }
  if (memberName == "ManualOverride") {
    return &m_manualOverride;
  }

  throw std::invalid_argument("Invalid member name (ACMainContactor): " + memberName);
}

auto N2KMonitoring::GNSS::get(const std::string &memberName) -> N2KMonitoring::GNSS::GNSSValue {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Latitude") {
    return &m_latitude;
  }
  if (memberName == "Longitude") {
    return &m_longitude;
  }
  if (memberName == "Cog") {
    return &m_cog;
  }
  if (memberName == "Sog") {
    return &m_sog;
  }
  if (memberName == "MagneticVariation") {
    return &m_magneticVariation;
  }
  if (memberName == "UTCDateTime") {
    return &m_utcDateTime;
  }
  if (memberName == "TimeOffset") {
    return &m_timeOffset;
  }
  if (memberName == "SatellitesInFix") {
    return &m_satellitesInFix;
  }
  if (memberName == "BestOfFourSatellitesSNR") {
    return &m_bestOfFourSatellitesSNR;
  }
  if (memberName == "Method") {
    return &m_method;
  }
  if (memberName == "FixType") {
    return &m_fixType;
  }
  if (memberName == "Hdop") {
    return &m_hdop;
  }
  if (memberName == "Pdop") {
    return &m_pdop;
  }
  if (memberName == "Vdop") {
    return &m_vdop;
  }
  if (memberName == "LatitudeDeg") {
    return &m_latitudeDeg;
  }
  if (memberName == "LongitudeDeg") {
    return &m_longitudeDeg;
  }
  throw std::invalid_argument("Invalid member name (GNSS): " + memberName);
}

auto N2KMonitoring::GNSS::get(const std::string &memberName) const -> N2KMonitoring::GNSS::GNSSValueConst {
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "Latitude") {
    return &m_latitude;
  }
  if (memberName == "Longitude") {
    return &m_longitude;
  }
  if (memberName == "Cog") {
    return &m_cog;
  }
  if (memberName == "Sog") {
    return &m_sog;
  }
  if (memberName == "MagneticVariation") {
    return &m_magneticVariation;
  }
  if (memberName == "UTCDateTime") {
    return &m_utcDateTime;
  }
  if (memberName == "TimeOffset") {
    return &m_timeOffset;
  }
  if (memberName == "SatellitesInFix") {
    return &m_satellitesInFix;
  }
  if (memberName == "BestOfFourSatellitesSNR") {
    return &m_bestOfFourSatellitesSNR;
  }
  if (memberName == "Method") {
    return &m_method;
  }
  if (memberName == "FixType") {
    return &m_fixType;
  }
  if (memberName == "Hdop") {
    return &m_hdop;
  }
  if (memberName == "Pdop") {
    return &m_pdop;
  }
  if (memberName == "Vdop") {
    return &m_vdop;
  }
  if (memberName == "LatitudeDeg") {
    return &m_latitudeDeg;
  }
  if (memberName == "LongitudeDeg") {
    return &m_longitudeDeg;
  }
  throw std::invalid_argument("Invalid member name (GNSS): " + memberName);
}

auto N2KMonitoring::MonitoringKeyValue::get(const std::string &memberName)
    -> N2KMonitoring::MonitoringKeyValue::MonitoringKeyValueValue {
  if (memberName == "Valid") {
    return &m_valid;
  }
  if (memberName == "Value") {
    return &m_value;
  }
  if (memberName == "LimitValid") {
    return &m_limitValid;
  }
  if (memberName == "Min") {
    return &m_min;
  }
  if (memberName == "Max") {
    return &m_max;
  }
  if (memberName == "WarnLow") {
    return &m_warnLow;
  }
  if (memberName == "WarnHigh") {
    return &m_warnHigh;
  }
  throw std::invalid_argument("Invalid member name (MonitoringKeyValue): " + memberName);
}

auto N2KMonitoring::MonitoringKeyValue::get(const std::string &memberName) const
    -> N2KMonitoring::MonitoringKeyValue::MonitoringKeyValueValueConst {
  if (memberName == "Valid") {
    return &m_valid;
  }
  if (memberName == "Value") {
    return &m_value;
  }
  if (memberName == "LimitValid") {
    return &m_limitValid;
  }
  if (memberName == "Min") {
    return &m_min;
  }
  if (memberName == "Max") {
    return &m_max;
  }
  if (memberName == "WarnLow") {
    return &m_warnLow;
  }
  if (memberName == "WarnHigh") {
    return &m_warnHigh;
  }
  throw std::invalid_argument("Invalid member name (MonitoringKeyValue): " + memberName);
}

auto N2KMonitoring::BinaryLogicState::get(const std::string &memberName)
    -> N2KMonitoring::BinaryLogicState::BinaryLogicStateValue {
  if (memberName == "Dipswitch") {
    return &m_dipswitch;
  }
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "States") {
    return &m_states;
  }
  throw std::invalid_argument("Invalid member name (BinaryLogicState): " + memberName);
}

auto N2KMonitoring::BinaryLogicState::get(const std::string &memberName) const
    -> N2KMonitoring::BinaryLogicState::BinaryLogicStateValueConst {
  if (memberName == "Dipswitch") {
    return &m_dipswitch;
  }
  if (memberName == "Instance") {
    return &m_instance;
  }
  if (memberName == "States") {
    return &m_states;
  }
  throw std::invalid_argument("Invalid member name (BinaryLogicState): " + memberName);
}

// JSON conversion implementations

// Helper function implementations for enum to string conversion
namespace N2KMonitoring::JsonHelpers {
std::string toString(eSystemOnState value) {
  switch (value) {
  case eSystemOnState::StateOff: return "StateOff";
  case eSystemOnState::StateOn: return "StateOn";
  case eSystemOnState::StateOnTimer: return "StateOnTimer";
  default: return "Unknown";
  }
}

std::string toString(eFaultState value) {
  switch (value) {
  case eFaultState::None: return "None";
  case eFaultState::ConfigurationConflict: return "ConfigurationConflict";
  case eFaultState::DipswitchConflict: return "DipswitchConflict";
  case eFaultState::EepromFailure: return "EepromFailure";
  case eFaultState::NoCZoneNetwork: return "NoCZoneNetwork";
  case eFaultState::LowRunCurrent: return "LowRunCurrent";
  case eFaultState::OverCurrent: return "OverCurrent";
  case eFaultState::ShortCircuit: return "ShortCircuit";
  case eFaultState::MissingCommander: return "MissingCommander";
  case eFaultState::MissingModeCommander: return "MissingModeCommander";
  case eFaultState::ReverseCurrent: return "ReverseCurrent";
  case eFaultState::CurrentCalibration: return "CurrentCalibration";
  default: return "Unknown";
  }
}

std::string toString(eSourceAvailable value) {
  switch (value) {
  case eSourceAvailable::SourceInvalid: return "SourceInvalid";
  case eSourceAvailable::SourceUnAvailable: return "SourceUnAvailable";
  case eSourceAvailable::SourceAvailable: return "SourceAvailable";
  default: return "Unknown";
  }
}

std::string toString(eEngineState value) {
  switch (value) {
  case eEngineState::Dead: return "Dead";
  case eEngineState::Stall: return "Stall";
  case eEngineState::Crank: return "Crank";
  case eEngineState::Run: return "Run";
  case eEngineState::PowerOff: return "PowerOff";
  default: return "Unknown";
  }
}

std::string toString(eHVACOperatingMode value) {
  switch (value) {
  case eHVACOperatingMode::NoChange: return "NoChange";
  case eHVACOperatingMode::Off: return "Off";
  case eHVACOperatingMode::Moisture: return "Moisture";
  case eHVACOperatingMode::Auto: return "Auto";
  case eHVACOperatingMode::Heat: return "Heat";
  case eHVACOperatingMode::Cool: return "Cool";
  case eHVACOperatingMode::AutoAux: return "AutoAux";
  case eHVACOperatingMode::Aux: return "Aux";
  case eHVACOperatingMode::FanOnly: return "FanOnly";
  case eHVACOperatingMode::Pet: return "Pet";
  default: return "Unknown";
  }
}

std::string toString(eAwningState value) {
  switch (value) {
  case eAwningState::AwningNoPower: return "AwningNoPower";
  case eAwningState::AwningParked: return "AwningParked";
  case eAwningState::AwningTiltedLeft: return "AwningTiltedLeft";
  case eAwningState::AwningTiltedLeftRight: return "AwningTiltedLeftRight";
  case eAwningState::AwningTiltedRight: return "AwningTiltedRight";
  case eAwningState::AwningOpenUnknown: return "AwningOpenUnknown";
  case eAwningState::AwningOpenFull: return "AwningOpenFull";
  case eAwningState::AwningMoving: return "AwningMoving";
  default: return "Unknown";
  }
}

std::string toString(eGeneratorState value) {
  switch (value) {
  case eGeneratorState::GeneratorOff: return "GeneratorOff";
  case eGeneratorState::GeneratorOn: return "GeneratorOn";
  case eGeneratorState::GeneratorUnknown: return "GeneratorUnknown";
  default: return "Unknown";
  }
}

std::string toString(eInverterChargerEnabled value) {
  switch (value) {
  case eInverterChargerEnabled::Off: return "Off";
  case eInverterChargerEnabled::On: return "On";
  case eInverterChargerEnabled::Error: return "Error";
  case eInverterChargerEnabled::Unavailable: return "Unavailable";
  default: return "Unknown";
  }
}

std::string toString(eInverterState value) {
  switch (value) {
  case eInverterState::Inverting: return "Inverting";
  case eInverterState::ACPassthru: return "ACPassthru";
  case eInverterState::LoadSense: return "LoadSense";
  case eInverterState::Fault: return "Fault";
  case eInverterState::Disabled: return "Disabled";
  case eInverterState::Charging: return "Charging";
  case eInverterState::EnergySaving: return "EnergySaving";
  case eInverterState::Supporting: return "Supporting";
  case eInverterState::EnergySaving2: return "EnergySaving2";
  case eInverterState::Supporting2: return "Supporting2";
  case eInverterState::Error: return "Error";
  case eInverterState::DataNotAvailable: return "DataNotAvailable";
  default: return "Unknown";
  }
}

std::string toString(eChargerState value) {
  switch (value) {
  case eChargerState::NotCharging: return "NotCharging";
  case eChargerState::Bulk: return "Bulk";
  case eChargerState::Absorption: return "Absorption";
  case eChargerState::Overcharge: return "Overcharge";
  case eChargerState::Equalize: return "Equalize";
  case eChargerState::Float: return "Float";
  case eChargerState::NoFloat: return "NoFloat";
  case eChargerState::ConstantVI: return "ConstantVI";
  case eChargerState::Disabled: return "Disabled";
  case eChargerState::Fault: return "Fault";
  default: return "Unknown";
  }
}

std::string toString(eTyreStatus value) {
  switch (value) {
  case eTyreStatus::Ok: return "Ok";
  case eTyreStatus::Leak: return "Leak";
  case eTyreStatus::Error: return "Error";
  default: return "Unknown";
  }
}

std::string toString(eTyreLimitStatus value) {
  switch (value) {
  case eTyreLimitStatus::ExtremeOverPressure: return "ExtremeOverPressure";
  case eTyreLimitStatus::OverPressure: return "OverPressure";
  case eTyreLimitStatus::NoAlarm: return "NoAlarm";
  case eTyreLimitStatus::LowPressure: return "LowPressure";
  case eTyreLimitStatus::ExtremeLowPressure: return "ExtremeLowPressure";
  case eTyreLimitStatus::NA: return "NA";
  case eTyreLimitStatus::Error: return "Error";
  default: return "Unknown";
  }
}

std::string toString(eAudioStatus value) {
  switch (value) {
  case eAudioStatus::AudioStatusInitialising: return "AudioStatusInitialising";
  case eAudioStatus::AudioStatusReady: return "AudioStatusReady";
  case eAudioStatus::AudioStatusUnknown: return "AudioStatusUnknown";
  default: return "Unknown";
  }
}

std::string toString(eAudioSource value) {
  switch (value) {
  case eAudioSource::VesselAlarm: return "VesselAlarm";
  case eAudioSource::AM: return "AM";
  case eAudioSource::FM: return "FM";
  case eAudioSource::Weather: return "Weather";
  case eAudioSource::DAB: return "DAB";
  case eAudioSource::AUX: return "AUX";
  case eAudioSource::USB: return "USB";
  case eAudioSource::CD: return "CD";
  case eAudioSource::MP3: return "MP3";
  case eAudioSource::AppleiOS: return "AppleiOS";
  case eAudioSource::Android: return "Android";
  case eAudioSource::Bluetooth: return "Bluetooth";
  case eAudioSource::SiriusXM: return "SiriusXM";
  case eAudioSource::Pandora: return "Pandora";
  case eAudioSource::Spotify: return "Spotify";
  case eAudioSource::Slacker: return "Slacker";
  case eAudioSource::Songza: return "Songza";
  case eAudioSource::AppleRadio: return "AppleRadio";
  case eAudioSource::LastFM: return "LastFM";
  case eAudioSource::Ethernet: return "Ethernet";
  case eAudioSource::VideoMP4: return "VideoMP4";
  case eAudioSource::VideoDVD: return "VideoDVD";
  case eAudioSource::VideoBlueRay: return "VideoBlueRay";
  case eAudioSource::HDMI: return "HDMI";
  case eAudioSource::Video: return "Video";
  case eAudioSource::NoSource: return "NoSource";
  default: return "Unknown";
  }
}

std::string toString(eContactorOnState value) {
  switch (value) {
  case eContactorOnState::ContactorOff: return "ContactorOff";
  case eContactorOnState::ContactorOn: return "ContactorOn";
  case eContactorOnState::ContactorAvailable: return "ContactorAvailable";
  case eContactorOnState::ContactorUnAvailable: return "ContactorUnAvailable";
  case eContactorOnState::ContactorFault: return "ContactorFault";
  case eContactorOnState::ContactorOverride: return "ContactorOverride";
  case eContactorOnState::ContactorStarting: return "ContactorStarting";
  default: return "Unknown";
  }
}

std::string toString(eGNSSMethod value) {
  switch (value) {
  case eGNSSMethod::NoFix: return "NoFix";
  case eGNSSMethod::StandardFix: return "StandardFix";
  case eGNSSMethod::DifferentialFix: return "DifferentialFix";
  case eGNSSMethod::PreciseFix: return "PreciseFix";
  case eGNSSMethod::RtkInt: return "RtkInt";
  case eGNSSMethod::RtkFloat: return "RtkFloat";
  case eGNSSMethod::Estimated: return "Estimated";
  case eGNSSMethod::Manual: return "Manual";
  case eGNSSMethod::Simulator: return "Simulator";
  case eGNSSMethod::Error: return "Error";
  case eGNSSMethod::Null: return "Null";
  default: return "Unknown";
  }
}

std::string toString(eGNSSFixType value) {
  switch (value) {
  case eGNSSFixType::FixNA: return "FixNA";
  case eGNSSFixType::Fix2D: return "Fix2D";
  case eGNSSFixType::Fix3D: return "Fix3D";
  default: return "Unknown";
  }
}

std::string toString(eHealth value) {
  switch (value) {
  case eHealth::HealthOk: return "HealthOk";
  case eHealth::HealthBad: return "HealthBad";
  case eHealth::HealthNone: return "HealthNone";
  default: return "Unknown";
  }
}

std::string toString(MonitoringType::eTankType value) { return MonitoringType::to_string(value); }

std::string toString(MeteringDevice::eACLine value) { return MeteringDevice::to_string(value); }
} // namespace N2KMonitoring::JsonHelpers

json N2KMonitoring::Circuit::tojson() const {
  json result;
  result["id"] = m_id;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "SystemsOn", m_systemsOn);
  JsonHelpers::valueToJson(result, "Level", m_level);
  JsonHelpers::valueToJson(result, "Current", m_current);
  JsonHelpers::valueToJson(result, "Fault", m_fault);
  JsonHelpers::valueToJson(result, "OnCount", m_onCount);
  JsonHelpers::valueToJson(result, "OnTime", m_onTime);
  JsonHelpers::valueToJson(result, "SequentialState", m_sequentialState);
  JsonHelpers::valueToJson(result, "ModesSystemOn", m_modesSystemOn);
  JsonHelpers::valueToJson(result, "ACSourceAvailable", m_aCSourceAvailable);
  JsonHelpers::valueToJson(result, "IsOffline", m_isOffline);
  return result;
}

json N2KMonitoring::Tank::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "LevelPercent", m_levelPercent);
  JsonHelpers::valueToJson(result, "Level", m_level);
  JsonHelpers::valueToJson(result, "Capacity", m_capacity);
  JsonHelpers::valueToJson(result, "TankType", m_tankType);
  return result;
}

json N2KMonitoring::Engine::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "Speed", m_speed);
  JsonHelpers::valueToJson(result, "BoostPressure", m_boostPressure);
  JsonHelpers::valueToJson(result, "Trim", m_trim);
  JsonHelpers::valueToJson(result, "OilPressure", m_oilPressure);
  JsonHelpers::valueToJson(result, "OilTemperature", m_oilTemperature);
  JsonHelpers::valueToJson(result, "Temperature", m_temperature);
  JsonHelpers::valueToJson(result, "AlternatorPotential", m_alternatorPotential);
  JsonHelpers::valueToJson(result, "FuelRate", m_fuelRate);
  JsonHelpers::valueToJson(result, "TotalEngineHours", m_totalEngineHours);
  JsonHelpers::valueToJson(result, "CoolantPressure", m_coolantPressure);
  JsonHelpers::valueToJson(result, "CoolantTemperature", m_coolantTemperature);
  JsonHelpers::valueToJson(result, "FuelPressure", m_fuelPressure);
  JsonHelpers::valueToJson(result, "DiscreteStatus1", m_discreteStatus1);
  JsonHelpers::valueToJson(result, "DiscreteStatus2", m_discreteStatus2);
  JsonHelpers::valueToJson(result, "PercentEngineLoad", m_percentEngineLoad);
  JsonHelpers::valueToJson(result, "PercentEngineTorque", m_percentEngineTorque);
  JsonHelpers::valueToJson(result, "EngineState", m_engineState);
  JsonHelpers::valueToJson(result, "ActiveEnginesId", m_activeEnginesId);
  return result;
}

json N2KMonitoring::ACLine::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  result["Line"] = static_cast<int>(m_line);
  JsonHelpers::valueToJson(result, "Voltage", m_voltage);
  JsonHelpers::valueToJson(result, "Current", m_current);
  JsonHelpers::valueToJson(result, "Frequency", m_frequency);
  JsonHelpers::valueToJson(result, "Power", m_power);
  return result;
}

json N2KMonitoring::AC::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["AClines"] = JsonHelpers::idMapToJson(m_acLines);
  return result;
}

json N2KMonitoring::DC::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "Voltage", m_voltage);
  JsonHelpers::valueToJson(result, "Current", m_current);
  JsonHelpers::valueToJson(result, "Temperature", m_temperature);
  JsonHelpers::valueToJson(result, "StateOfCharge", m_stateOfCharge);
  JsonHelpers::valueToJson(result, "CapacityRemaining", m_capacityRemaining);
  JsonHelpers::valueToJson(result, "TimeRemaining", m_timeRemaining);
  JsonHelpers::valueToJson(result, "TimeToCharge", m_timeToCharge);
  JsonHelpers::valueToJson(result, "TimeRemainingOrToCharge", m_timeRemainingOrToCharge);
  return result;
}

json N2KMonitoring::Temperature::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "Temperature", m_temperature);
  return result;
}

json N2KMonitoring::Pressure::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "Pressure", m_pressure);
  return result;
}

json N2KMonitoring::HVAC::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "OperationMode", m_operationMode);
  JsonHelpers::valueToJson(result, "FanMode", m_fanMode);
  JsonHelpers::valueToJson(result, "FanSpeed", m_fanSpeed);
  JsonHelpers::valueToJson(result, "EnvironmentSetTemperature", m_environmentSetTemperature);
  JsonHelpers::valueToJson(result, "EnvironmentTemperature", m_environmentTemperature);
  return result;
}

json N2KMonitoring::ZipdeeAwning::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "State", m_state);
  return result;
}

json N2KMonitoring::ThirdPartyGenerator::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "OnTime", m_onTime);
  JsonHelpers::valueToJson(result, "State", m_status);
  return result;
}

json N2KMonitoring::InverterCharger::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "InverterInstance", m_inverterInstance);
  JsonHelpers::valueToJson(result, "ChargerInstance", m_chargerInstance);
  JsonHelpers::valueToJson(result, "InverterEnable", m_inverterEnable);
  JsonHelpers::valueToJson(result, "InverterState", m_inverterState);
  JsonHelpers::valueToJson(result, "ChargerEnable", m_chargerEnable);
  JsonHelpers::valueToJson(result, "ChargerState", m_chargerState);
  return result;
}

json N2KMonitoring::TyrePressure::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "Pressure", m_pressure);
  JsonHelpers::valueToJson(result, "Temperature", m_temperature);
  JsonHelpers::valueToJson(result, "Status", m_status);
  JsonHelpers::valueToJson(result, "LimitStatus", m_limitStatus);
  return result;
}

json N2KMonitoring::AudioStereo::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "Power", m_power);
  JsonHelpers::valueToJson(result, "Mute", m_mute);
  JsonHelpers::valueToJson(result, "AudioStatus", m_audioStatus);
  JsonHelpers::valueToJson(result, "SourceMode", m_sourceMode);
  JsonHelpers::valueToJson(result, "Volume", m_volume);
  return result;
}

json N2KMonitoring::ACMainContactor::tojson() const {
  json result;
  result["SystemStateId"] = m_systemStateId;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "ACContactorSystemsState", m_acContactorSystemsState);
  JsonHelpers::valueToJson(result, "ACContactorSourceAvailable", m_acContactorSourceAvailable);
  JsonHelpers::valueToJson(result, "ReversePolarity", m_reversePolarity);
  JsonHelpers::valueToJson(result, "ACContactorAutoChangeOver", m_acContactorAutoChangeOver);
  JsonHelpers::valueToJson(result, "ManualOverride", m_manualOverride);
  return result;
}

json N2KMonitoring::GNSS::tojson() const {
  json result;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  result["UTCDateTime"] = m_utcDateTime;
  JsonHelpers::valueToJson(result, "Latitude", m_latitude);
  JsonHelpers::valueToJson(result, "Longitude", m_longitude);
  JsonHelpers::valueToJson(result, "Cog", m_cog);
  JsonHelpers::valueToJson(result, "Sog", m_sog);
  JsonHelpers::valueToJson(result, "MagneticVariation", m_magneticVariation);
  JsonHelpers::valueToJson(result, "TimeOffset", m_timeOffset);
  JsonHelpers::valueToJson(result, "SatellitesInFix", m_satellitesInFix);
  JsonHelpers::valueToJson(result, "BestOfFourSatellitesSNR", m_bestOfFourSatellitesSNR);
  JsonHelpers::valueToJson(result, "Method", m_method);
  JsonHelpers::valueToJson(result, "FixType", m_fixType);
  JsonHelpers::valueToJson(result, "Hdop", m_hdop);
  JsonHelpers::valueToJson(result, "Pdop", m_pdop);
  JsonHelpers::valueToJson(result, "Vdop", m_vdop);
  JsonHelpers::valueToJson(result, "LatitudeDeg", m_latitudeDeg);
  JsonHelpers::valueToJson(result, "LongitudeDeg", m_longitudeDeg);
  return result;
}

json N2KMonitoring::MonitoringKeyValue::tojson() const {
  json result;
  result["Valid"] = m_valid;
  result["Value"] = m_value;
  result["LimitValid"] = m_limitValid;
  result["Min"] = m_min;
  result["Max"] = m_max;
  result["WarnLow"] = m_warnLow;
  result["WarnHigh"] = m_warnHigh;
  return result;
}

json N2KMonitoring::BinaryLogicState::tojson() const {
  json result;
  result["Dipswitch"] = m_dipswitch;
  result["Instance"] = m_instance;
  result["ComponentStatus"] = "Disconnected";
  JsonHelpers::valueToJson(result, "States", m_states);
  return result;
}

json N2KMonitoring::NetworkStatus::tojson() const {
  json result;
  result["EthernetStatus"] = m_ethernetStatus;
  result["EthernetInternetConnectivity"] = m_ethernetInternetConnectivity;
  result["EthernetIp"] = m_ethernetIp;
  result["EthernetId"] = m_ethernetId;
  result["WifiStatus"] = m_wifiStatus;
  result["WifiInternetConnectivity"] = m_wifiInternetConnectivity;
  result["WifiIp"] = m_wifiIp;
  result["WifiSsid"] = m_wifiSsid;
  result["WifiSecurity"] = m_wifiSecurity;
  result["WifiType"] = m_wifiType;
  result["WifiChannel"] = m_wifiChannel;
  result["WifiSignalStrengthDbm"] = m_wifiSignalStrengthDbm;
  result["HotspotStatus"] = m_hotspotStatus;
  result["HotspotIp"] = m_hotspotIp;
  result["HotspotSsid"] = m_hotspotSsid;
  result["HotspotPassword"] = m_hotspotPassword;
  result["HotspotSecurity"] = m_hotspotSecurity;
  result["HotspotType"] = m_hotspotType;
  result["HotspotChannel"] = m_hotspotChannel;
  result["CellularStatus"] = m_cellularStatus;
  result["CellularInternetConnectivity"] = m_cellularInternetConnectivity;
  result["CellularIp"] = m_cellularIp;
  result["CellularOperator"] = m_cellularOperator;
  result["CellularType"] = m_cellularType;
  result["CellularSignalStrengthDbm"] = m_cellularSignalStrengthDbm;
  result["CellularSimIccid"] = m_cellularSimIccid;
  result["CellularSimEid"] = m_cellularSimEid;
  result["CellularSimImsi"] = m_cellularSimImsi;
  return result;
}

json N2KMonitoring::SnapshotInstanceIdMap::tojson() const {
  json result;

  if (m_circuits.size() > 0)
    JsonHelpers::idMapToJson(result, "Circuits", m_circuits);
  if (m_modes.size() > 0)
    JsonHelpers::idMapToJson(result, "Modes", m_modes);
  if (m_tanks.size() > 0)
    JsonHelpers::idMapToJson(result, "Tanks", m_tanks);
  if (m_engines.size() > 0)
    JsonHelpers::idMapToJson(result, "Engines", m_engines);
  if (m_ac.size() > 0)
    JsonHelpers::idMapToJson(result, "AC", m_ac);
  if (m_dc.size() > 0)
    JsonHelpers::idMapToJson(result, "DC", m_dc);
  if (m_temperatures.size() > 0)
    JsonHelpers::idMapToJson(result, "Temperatures", m_temperatures);
  if (m_pressures.size() > 0)
    JsonHelpers::idMapToJson(result, "Pressures", m_pressures);
  if (m_hvacs.size() > 0)
    JsonHelpers::idMapToJson(result, "Hvacs", m_hvacs);
  if (m_awnings.size() > 0)
    JsonHelpers::idMapToJson(result, "Awnings", m_awnings);
  if (m_thirdPartyGenerators.size() > 0)
    JsonHelpers::idMapToJson(result, "ThirdPartyGenerators", m_thirdPartyGenerators);
  if (m_inverterChargers.size() > 0)
    JsonHelpers::idMapToJson(result, "InverterChargers", m_inverterChargers);
  if (m_tyrepressures.size() > 0)
    JsonHelpers::idMapToJson(result, "Tyrepressures", m_tyrepressures);
  if (m_audioStereos.size() > 0)
    JsonHelpers::idMapToJson(result, "AudioStereos", m_audioStereos);
  if (m_acMainContactors.size() > 0)
    JsonHelpers::idMapToJson(result, "ACMainContactors", m_acMainContactors);
  if (m_gnss.size() > 0)
    JsonHelpers::idMapToJson(result, "GNSS", m_gnss);
  if (m_monitoringKeyValue.size() > 0)
    JsonHelpers::idMapToJson(result, "MonitoringKeyValue", m_monitoringKeyValue);
  if (m_binaryLogicState.size() > 0)
    JsonHelpers::idMapToJson(result, "BinaryLogicState", m_binaryLogicState);

  // if (m_networkStatus) {
  //   result["NetworkStatus"] = m_networkStatus->tojson();
  // }
  result["TimeStamp"] = m_timeStamp;
  return result;
}

json N2KMonitoring::HealthStatus::tojson() const {
  json result;
  result["ServiceThread"] = static_cast<int>(m_serviceThread);
  result["NetworkThread"] = static_cast<int>(m_networkThread);
  result["SCThread"] = static_cast<int>(m_scThread);
  result["GNSSThread"] = static_cast<int>(m_gnssThread);
  result["GNSSLatLon"] = static_cast<int>(m_gnssLatLon);
  result["GNSSFix"] = static_cast<int>(m_gnssFix);
  return result;
}

json N2KMonitoring::MonitoringKeyValueMap::tojson() const {
  json result;
  result["KeyValueMap"] = JsonHelpers::idMapToJson(m_keyValueMap);
  return result;
}

// Global to_json function implementations
void N2KMonitoring::to_json(nlohmann::json &j, const Circuit &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const Tank &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const Engine &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const ACLine &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const AC &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const DC &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const Temperature &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const Pressure &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const HVAC &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const ZipdeeAwning &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const ThirdPartyGenerator &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const InverterCharger &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const TyrePressure &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const AudioStereo &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const ACMainContactor &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const GNSS &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const MonitoringKeyValue &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const BinaryLogicState &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const NetworkStatus &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const SnapshotInstanceIdMap &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const HealthStatus &c) { j = c.tojson(); }
void N2KMonitoring::to_json(nlohmann::json &j, const MonitoringKeyValueMap &c) { j = c.tojson(); }
