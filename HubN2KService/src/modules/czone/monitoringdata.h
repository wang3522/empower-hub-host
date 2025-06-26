#pragma once

#include <memory>
#include <string>
#include <unordered_map>

#include "modules/czone/configdata.h"

namespace N2KMonitoring {

enum class eSystemOnState { StateOff = 0, StateOn = 1, StateOnTimer = 2 };
enum eFaultState {
  None = 0,
  ConfigurationConflict = 1,
  DipswitchConflict = 2,
  EepromFailure = 3,
  NoCZoneNetwork = 4,
  LowRunCurrent = 5,
  OverCurrent = 6,
  ShortCircuit = 7,
  MissingCommander = 8,
  MissingModeCommander = 9,
  ReverseCurrent = 10,
  CurrentCalibration = 11,
};
enum class eSourceAvailable {
  SourceInvalid = 0,
  SourceUnAvailable = 1,
  SourceAvailable = 2,
};
enum eEngineState {
  Dead = 0,
  Stall = 1,
  Crank = 2,
  Run = 3,
  PowerOff = 4,
};
enum EngineInstance {
  StarboardEngine = 0,
  Port = 1,
  StarboardInnerEngine = 2,
  PortInnerEngine = 3,
  EngineCount = 4,
};
enum eHVACOperatingMode {
  NoChange = 0,
  Off = 1,
  Moisture = 2,
  Auto = 3,
  Heat = 4,
  Cool = 5,
  AutoAux = 6,
  Aux = 7,
  FanOnly = 8,
  Pet = 10,
};
enum eAwningState {
  AwningNoPower = 0,
  AwningParked = 1,
  AwningTiltedLeft = 2,
  AwningTiltedLeftRight = 3,
  AwningTiltedRight = 4,
  AwningOpenUnknown = 5,
  AwningOpenFull = 6,
  AwningMoving = 7,
};
enum eGeneratorState {
  GeneratorOff = 0,
  GeneratorOn = 1,
  GeneratorUnknown = 2,
};
enum eInverterChargerEnabled {
  Off = 0,
  On = 1,
  Error = 2,
  Unavailable = 3,
};
enum eInverterState {
  Inverting = 0,
  ACPassthru = 1,
  LoadSense = 2,
  Fault = 3,
  Disabled = 4,
  Charging = 5,
  EnergySaving = 6,
  Supporting = 7,
  EnergySaving2 = 12,
  Supporting2 = 13,
  Error = 14,
  DataNotAvailable = 15,
};
enum eChargerState {
  NotCharging = 0,
  Bulk = 1,
  Absorption = 2,
  Overcharge = 3,
  Equalize = 4,
  Float = 5,
  NoFloat = 6,
  ConstantVI = 7,
  Disabled = 8,
  Fault = 9,
};
enum eTyreStatus {
  Ok = 0,
  Leak = 1,
  Error = 2,
};
enum eTyreLimitStatus {
  ExtremeOverPressure = 0,
  OverPressure = 1,
  NoAlarm = 2,
  LowPressure = 3,
  ExtremeLowPressure = 4,
  NA = 5,
  Error = 6,
};
enum eAudioStatus {
  AudioStatusInitialising = 0,
  AudioStatusReady = 1,
  AudioStatusUnknown = 2,
};
enum eAudioSource {
  VesselAlarm = 0,
  AM = 1,
  FM = 2,
  Weather = 3,
  DAB = 4,
  AUX = 5,
  USB = 6,
  CD = 7,
  MP3 = 8,
  AppleiOS = 9,
  Android = 10,
  Bluetooth = 11,
  SiriusXM = 12,
  Pandora = 13,
  Spotify = 14,
  Slacker = 15,
  Songza = 16,
  AppleRadio = 17,
  LastFM = 18,
  Ethernet = 19,
  VideoMP4 = 20,
  VideoDVD = 21,
  VideoBlueRay = 22,
  HDMI = 23,
  Video = 24,
  NoSource = 25,
};
enum eContactorOnState {
  ContactorOff = 0x0,
  ContactorOn = 0x01,
  ContactorAvailable = 0x02,
  ContactorUnAvailable = 0x04,
  ContactorFault = 0x08,
  ContactorOverride = 0x10,
  ContactorStarting = 0x20,
};
enum eGNSSMethod {
  NoFix = 0,
  StandardFix = 1,
  DifferentialFix = 2,
  PreciseFix = 3,
  RtkInt = 4,
  RtkFloat = 5,
  Estimated = 6,
  Manual = 7,
  Simulator = 8,
  Error = 14,
  Null = 15,
};
enum eGNSSFixType {
  FixNA = 0,
  Fix2D = 2,
  Fix3D = 3,
};
enum eDiscreteStatus1Mask {
  None1 = 0,
  CheckEngine = 1,
  OverTemperature = 2,
  LowOilPressure = 4,
  LowOilLevel = 8,
  LowFuelPressure = 16,
  LowSystemVoltage = 32,
  LowCoolantLevel = 64,
  WaterFlow = 128,
  WaterInFuel = 256,
  ChargeIndicator = 512,
  PreheatIndicator = 1024,
  HighBoostPressure = 2048,
  RevLimitExceeded = 4096,
  EGRSystem = 8192,
  ThrottlePositionSensor = 16384,
  EngineEmergencyStopMode = 32768,
};
enum eHealth {
  HealthOk = 0x0,
  HealthBad = 0x02,
  HealthNone = 0x03,
};

template <typename T>
using IdMap = std::unordered_map<uint32_t, std::shared_ptr<T>>;

template <typename T>
class Value {
public:
  bool m_valid;
  T m_value;

  bool operator==(const Value<T> &other) const { return m_valid == other.m_valid && m_value == other.m_value; }
};

using ValueSystemOnState = Value<eSystemOnState>;
using ValueU32 = Value<uint32_t>;
using ValueS32 = Value<int32_t>;
using ValueF = Value<float>;
using ValueBool = Value<bool>;
using ValueDouble = Value<double>;
using ValueTankType = Value<MonitoringType::eTankType>;
using ValueFaultState = Value<eFaultState>;
using ValueSourceAvailable = Value<eSourceAvailable>;
using ValueEngineState = Value<eEngineState>;
using ValueHVACOperatingMode = Value<eHVACOperatingMode>;
using ValueAwningState = Value<eAwningState>;
using ValueGeneratorState = Value<eGeneratorState>;
using ValueInverterChargerEnabled = Value<eInverterChargerEnabled>;
using ValueInverterState = Value<eInverterState>;
using ValueChargerState = Value<eChargerState>;
using ValueTyreStatus = Value<eTyreStatus>;
using ValueTyreLimitStatus = Value<eTyreLimitStatus>;
using ValueAudioStatus = Value<eAudioStatus>;
using ValueAudioSource = Value<eAudioSource>;
using ValueContactorOnState = Value<eContactorOnState>;
using ValueGNSSMethod = Value<eGNSSMethod>;
using ValueGNSSFixType = Value<eGNSSFixType>;

class Circuit {
public:
  int m_id;
  ValueSystemOnState m_systemsOn;
  ValueU32 m_level;
  ValueF m_current;
  ValueFaultState m_fault;
  ValueU32 m_onCount;
  ValueU32 m_onTime;
  ValueU32 m_sequentialState;
  ValueU32 m_modesSystemOn;
  ValueSourceAvailable m_aCSourceAvailable;
  ValueBool m_isOffline;

  bool operator==(const Circuit &other) const = default;
};

class Tank {
public:
  uint32_t m_instance;
  ValueU32 m_levelPercent;
  ValueU32 m_level;
  ValueU32 m_capacity;
  ValueTankType m_tankType;

  bool operator==(const Tank &other) const = default;
};

class Engine {
public:
  uint32_t m_instance;
  ValueU32 m_speed; // SC <unit: RPM, gain: 1> --> DP <unit: RPM, gain: 1> i.e. value: 1000 means 1000RPM * 1 = 1000RPM
  ValueF m_boostPressure;  // SC <unit: kPa, gain: 0.01> --> DP <unit: kPa, gain: 0.01> i.e. value: 8836 means 8836 *
                           // 0.01 = 88.36kPa = 12.82PSI
  ValueS32 m_trim;         // Not implemented
  ValueU32 m_oilPressure;  // SC <unit: kPa, gain: 0.01> --> DP <unit: kPa, gain: 0.01> i.e. value: 34172 means 34712 *
                           // 0.01 = 341.72kPa = 49.56PSI
  ValueF m_oilTemperature; // SC <unit:degrees C, gain: 1> --> DP <unit:degrees C, gain: 1> i.e. value:100 means 100
                           // degress C = 212 degress F
  ValueF m_temperature;    // SC <unit:degrees C, gain: 1> --> DP <unit:degrees C, gain: 1> (Sea water temperature) i.e.
                           // value:-50 means -50 degress C
  ValueF m_alternatorPotential; // SC <unit: volts, gain: 0.001> --> DP <unit: volts, gain: 0.001> i.e. value: 13461
                                // means 13461 * 0.001 = 13.461V
  ValueF m_fuelRate;            // Not implemented
  ValueU32 m_totalEngineHours;  // SC <unit: minutes, gain: 1> --> DP <unit: minutes, gain: 1> i.e. value: 586828 means
                                // 586828 minutes = 9780 hours
  ValueF m_coolantPressure; // SC <unit: kPa, gain: 0.01> --> DP <unit: kPa, gain: 0.01> i.e. value: 8836 means 8836 *
                            // 0.01 = 88.36kPa = 12.82PSI
  ValueF m_coolantTemperature;  // SC <unit:degrees C, gain: 1> --> DP <unit:degrees C, gain: 1> i.e. value:63 means 63
                                // degress C
  ValueF m_fuelPressure;        // Not implemented
  ValueU32 m_discreteStatus1;   // Not implemented
  ValueU32 m_discreteStatus2;   // Not implemented
  ValueS32 m_percentEngineLoad; // Not implemented
  ValueS32 m_percentEngineTorque; // Not implemented
  ValueEngineState m_engineState; // SC <unit:enum 0-5, gain: 1> --> DP <unit:enum eEngineState>
  ValueU32 m_activeEnginesId;

  bool operator==(const Engine &other) const = default;
};

class ACLine {
public:
  uint32_t m_instance;
  MeteringDevice::eACLine m_line;
  ValueF m_voltage;
  ValueF m_current;
  ValueF m_frequency;
  ValueF m_power;

  bool operator==(const ACLine &other) const = default;
};

class AC {
public:
  uint32_t m_instance;
  std::unordered_map<uint32_t, std::shared_ptr<ACLine>> m_acLines;

  bool operator==(const AC &other) const;
};

class DC {
public:
  uint32_t m_instance;
  ValueF m_voltage;
  ValueF m_current;
  ValueF m_temperature;
  ValueS32 m_stateOfCharge;
  ValueF m_capacityRemaining;
  ValueU32 m_timeRemaining;
  ValueU32 m_timeToCharge;
  ValueU32 m_timeRemainingOrToCharge;

  bool operator==(const DC &other) const = default;
};

class Temperature {
public:
  uint32_t m_instance;
  ValueF m_temperature;

  bool operator==(const Temperature &other) const = default;
};

class Pressure {
public:
  uint32_t m_instance;
  ValueF m_pressure;

  bool operator==(const Pressure &other) const = default;
};

class HVAC {
public:
  uint32_t m_instance = 1;
  ValueHVACOperatingMode m_operationMode;
  ValueU32 m_fanMode;                 // tbc
  ValueU32 m_fanSpeed;                // Values from 1 to 125 = 1% to 125%. Auto 126
  ValueF m_environmentSetTemperature; // Celcius
  ValueF m_environmentTemperature;    // Celcius

  bool operator==(const HVAC &other) const = default;
};

class ZipdeeAwning {
public:
  uint32_t m_instance;
  ValueAwningState m_state;

  bool operator==(const ZipdeeAwning &other) const = default;
};

class ThirdPartyGenerator {
public:
  uint32_t m_instance;
  ValueU32 m_onTime; // seconds
  ValueGeneratorState m_status;

  bool operator==(const ThirdPartyGenerator &other) const = default;
};

class InverterCharger {
public:
  uint32_t m_instance; // Note in InverterInstance << 8 | ChargerInstance
  ValueU32 m_inverterInstance;
  ValueU32 m_chargerInstance;
  ValueInverterChargerEnabled m_inverterEnable;
  ValueInverterState m_inverterState;
  ValueInverterChargerEnabled m_chargerEnable;
  ValueChargerState m_chargerState;

  bool operator==(const InverterCharger &other) const = default;
};

class TyrePressure {
public:
  uint32_t m_instance;
  ValueF m_pressure;
  ValueF m_temperature;
  ValueTyreStatus m_status;
  ValueTyreLimitStatus m_limitStatus;

  bool operator==(const TyrePressure &other) const = default;
};

class AudioStereo {
public:
  uint32_t m_instance;
  ValueBool m_power;
  ValueBool m_mute;
  ValueAudioStatus m_audioStatus;
  ValueAudioSource m_sourceMode;
  ValueU32 m_volume;

  bool operator==(const AudioStereo &other) const = default;
};

class ACMainContactor {
public:
  uint32_t m_systemStateId;
  ValueContactorOnState m_acContactorSystemsState;
  ValueBool m_acContactorSourceAvailable;
  ValueBool m_reversePolarity;
  ValueBool m_acContactorAutoChangeOver;
  ValueBool m_manualOverride;

  bool operator==(const ACMainContactor &other) const = default;
};

class GNSS {
public:
  uint32_t m_instance;
  ValueF m_latitude;          // Radians, +/- North/South
  ValueF m_longitude;         // Radians, +/- East/West
  ValueF m_cog;               // Radians, True
  ValueF m_sog;               // m/s
  ValueF m_magneticVariation; // Radians
  std::string m_utcDateTime;  // ISO 8601 - YYYY-MM-DDThh:mm:ss.s
  ValueU32 m_timeOffset;      // Offset minutes
  ValueU32 m_satellitesInFix;
  ValueS32 m_bestOfFourSatellitesSNR; // dB
  ValueGNSSMethod m_method;
  ValueGNSSFixType m_fixType;
  ValueF m_hdop;              // unitless, lower is better
  ValueF m_pdop;              // unitless, lower is better
  ValueF m_vdop;              // unitless, lower is better
  ValueDouble m_latitudeDeg;  // Degrees
  ValueDouble m_longitudeDeg; // Degrees

  bool operator==(const GNSS &other) const = default;
};

class MonitoringKeyValue {
public:
  bool m_valid;
  float m_value;
  bool m_limitValid;
  float m_min;
  float m_max;
  float m_warnLow;
  float m_warnHigh;

  bool operator==(const MonitoringKeyValue &other) const = default;
};

class BinaryLogicState {
public:
  uint32_t m_dipswitch;
  uint32_t m_instance;
  ValueU32 m_states;

  bool operator==(const BinaryLogicState &other) const = default;
};

class NetworkStatus {
public:
  std::string m_ethernetStatus;
  bool m_ethernetInternetConnectivity;
  std::string m_ethernetIp;
  std::string m_ethernetId;
  std::string m_wifiStatus;
  bool m_wifiInternetConnectivity;
  std::string m_wifiIp;
  std::string m_wifiSsid;
  std::string m_wifiSecurity;
  std::string m_wifiType;
  int32_t m_wifiChannel;
  int32_t m_wifiSignalStrengthDbm;
  std::string m_hotspotStatus;
  std::string m_hotspotIp;
  std::string m_hotspotSsid;
  std::string m_hotspotPassword;
  std::string m_hotspotSecurity;
  std::string m_hotspotType;
  int32_t m_hotspotChannel;
  std::string m_cellularStatus;
  bool m_celllularInternetConnectivity;
  std::string m_cellularIp;
  std::string m_cellularOperator;
  std::string m_cellularType;
  int32_t m_cellularSignalStrengthDbm;
  std::string m_cellularSimIccid;
  std::string m_cellularSimEid;
  std::string m_cellularSimImsi;

  bool operator==(const NetworkStatus &other) const;
  void clear();
};

class SnapshotInstanceIdMap {
public:
  SnapshotInstanceIdMap() = default;
  ~SnapshotInstanceIdMap() = default;

  std::unordered_map<uint32_t, std::shared_ptr<Circuit>> m_circuits;
  std::unordered_map<uint32_t, std::shared_ptr<Circuit>> m_modes;
  std::unordered_map<uint32_t, std::shared_ptr<Tank>> m_tanks;
  std::unordered_map<uint32_t, std::shared_ptr<Engine>> m_engines;
  std::unordered_map<uint32_t, std::shared_ptr<AC>> m_ac;
  std::unordered_map<uint32_t, std::shared_ptr<DC>> m_dc;
  std::unordered_map<uint32_t, std::shared_ptr<Temperature>> m_temperatures;
  std::unordered_map<uint32_t, std::shared_ptr<Pressure>> m_pressures;
  std::unordered_map<uint32_t, std::shared_ptr<HVAC>> m_hvacs;
  std::unordered_map<uint32_t, std::shared_ptr<ZipdeeAwning>> m_awnings;
  std::unordered_map<uint32_t, std::shared_ptr<ThirdPartyGenerator>> m_thirdPartyGenerators;
  std::unordered_map<uint32_t, std::shared_ptr<InverterCharger>> m_inverterChargers;
  std::unordered_map<uint32_t, std::shared_ptr<TyrePressure>> m_tyrepressures;
  std::unordered_map<uint32_t, std::shared_ptr<AudioStereo>> m_audioStereos;
  std::unordered_map<uint32_t, std::shared_ptr<ACMainContactor>> m_acMainContactors;
  std::unordered_map<uint32_t, std::shared_ptr<GNSS>> m_gnss;
  std::unordered_map<uint32_t, std::shared_ptr<MonitoringKeyValue>> m_monitoringKeyValue;
  std::unordered_map<uint32_t, std::shared_ptr<BinaryLogicState>> m_binaryLogicState;
  NetworkStatus m_networkStatus;
  std::string m_timeStamp;

  void Clear();
};

class HealthStatus {
public:
  eHealth m_serviceThread;
  eHealth m_networkThread;
  eHealth m_scThread;
  eHealth m_gnssThread;
  eHealth m_gnssLatLon;
  eHealth m_gnssFix;
};

class MonitoringKeyValueMap {
public:
  std::unordered_map<uint32_t, std::shared_ptr<MonitoringKeyValue>> m_keyValueMap;

  void Clear();
};

}; // namespace N2KMonitoring