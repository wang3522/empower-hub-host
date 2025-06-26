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
  uint32_t Instance;
  ValueU32 LevelPercent;
  ValueU32 Level;
  ValueU32 Capacity;
  ValueTankType TankType;

  bool operator==(const Tank &other) const = default;
};

class Engine {
public:
  uint32_t Instance;
  ValueU32 Speed; // SC <unit: RPM, gain: 1> --> DP <unit: RPM, gain: 1> i.e. value: 1000 means 1000RPM * 1 = 1000RPM
  ValueF BoostPressure;  // SC <unit: kPa, gain: 0.01> --> DP <unit: kPa, gain: 0.01> i.e. value: 8836 means 8836 * 0.01
                         // = 88.36kPa = 12.82PSI
  ValueS32 Trim;         // Not implemented
  ValueU32 OilPressure;  // SC <unit: kPa, gain: 0.01> --> DP <unit: kPa, gain: 0.01> i.e. value: 34172 means 34712 *
                         // 0.01 = 341.72kPa = 49.56PSI
  ValueF OilTemperature; // SC <unit:degrees C, gain: 1> --> DP <unit:degrees C, gain: 1> i.e. value:100 means 100
                         // degress C = 212 degress F
  ValueF Temperature;    // SC <unit:degrees C, gain: 1> --> DP <unit:degrees C, gain: 1> (Sea water temperature) i.e.
                         // value:-50 means -50 degress C
  ValueF AlternatorPotential; // SC <unit: volts, gain: 0.001> --> DP <unit: volts, gain: 0.001> i.e. value: 13461 means
                              // 13461 * 0.001 = 13.461V
  ValueF FuelRate;            // Not implemented
  ValueU32 TotalEngineHours;  // SC <unit: minutes, gain: 1> --> DP <unit: minutes, gain: 1> i.e. value: 586828 means
                              // 586828 minutes = 9780 hours
  ValueF CoolantPressure;     // SC <unit: kPa, gain: 0.01> --> DP <unit: kPa, gain: 0.01> i.e. value: 8836 means 8836 *
                              // 0.01 = 88.36kPa = 12.82PSI
  ValueF CoolantTemperature;  // SC <unit:degrees C, gain: 1> --> DP <unit:degrees C, gain: 1> i.e. value:63 means 63
                              // degress C
  ValueF FuelPressure;        // Not implemented
  ValueU32 DiscreteStatus1;   // Not implemented
  ValueU32 DiscreteStatus2;   // Not implemented
  ValueS32 PercentEngineLoad; // Not implemented
  ValueS32 PercentEngineTorque; // Not implemented
  ValueEngineState EngineState; // SC <unit:enum 0-5, gain: 1> --> DP <unit:enum eEngineState>
  ValueU32 ActiveEnginesId;

  bool operator==(const Engine &other) const = default;
};

class ACLine {
public:
  uint32_t Instance;
  MeteringDevice::eACLine Line;
  ValueF Voltage;
  ValueF Current;
  ValueF Frequency;
  ValueF Power;

  bool operator==(const ACLine &other) const = default;
};

class AC {
public:
  uint32_t Instance;
  std::unordered_map<uint32_t, std::shared_ptr<ACLine>> AClines;

  bool operator==(const AC &other) const;
};

class DC {
public:
  uint32_t Instance;
  ValueF Voltage;
  ValueF Current;
  ValueF Temperature;
  ValueS32 StateOfCharge;
  ValueF CapacityRemaining;
  ValueU32 TimeRemaining; // minutes, current <= 0.0A
  ValueU32 TimeToCharge;  // minutes, current > 0.0A
  ValueU32 TimeRemainingOrToCharge;

  bool operator==(const DC &other) const = default;
};

class Temperature {
public:
  uint32_t Instance;
  ValueF Temperature;

  bool operator==(const Temperature &other) const = default;
};

class Pressure {
public:
  uint32_t Instance;
  ValueF Pressure;

  bool operator==(const Pressure &other) const = default;
};

class HVAC {
public:
  uint32_t Instance = 1;
  ValueHVACOperatingMode OperationMode;
  ValueU32 FanMode;                 // tbc
  ValueU32 FanSpeed;                // Values from 1 to 125 = 1% to 125%. Auto 126
  ValueF EnvironmentSetTemperature; // Celcius
  ValueF EnvironmentTemperature;    // Celcius

  bool operator==(const HVAC &other) const = default;
};

class ZipdeeAwning {
public:
  uint32_t Instance;
  ValueAwningState State;

  bool operator==(const ZipdeeAwning &other) const = default;
};

class ThirdPartyGenerator {
public:
  uint32_t Instance;
  ValueU32 OnTime; // seconds
  ValueGeneratorState Status;

  bool operator==(const ThirdPartyGenerator &other) const = default;
};

class InverterCharger {
public:
  uint32_t Instance; // Note in InverterInstance << 8 | ChargerInstance
  ValueU32 InverterInstance;
  ValueU32 ChargerInstance;
  ValueInverterChargerEnabled InverterEnable;
  ValueInverterState InverterState;
  ValueInverterChargerEnabled ChargerEnable;
  ValueChargerState ChargerState;

  bool operator==(const InverterCharger &other) const = default;
};

class TyrePressure {
public:
  uint32_t Instance;
  ValueF Pressure;
  ValueF Temperature;
  ValueTyreStatus Status;
  ValueTyreLimitStatus LimitStatus;

  bool operator==(const TyrePressure &other) const = default;
};

class AudioStereo {
public:
  uint32_t Instance;
  ValueBool Power;
  ValueBool Mute;
  ValueAudioStatus AudioStatus;
  ValueAudioSource SourceMode;
  ValueU32 Volume;

  bool operator==(const AudioStereo &other) const = default;
};

class ACMainContactor {
public:
  uint32_t SystemStateId;
  ValueContactorOnState ACContactorSystemsState;
  ValueBool ACContactorSourceAvailable;
  ValueBool ReversePolarity;
  ValueBool ACContactorAutoChangeOver;
  ValueBool ManualOverride;

  bool operator==(const ACMainContactor &other) const = default;
};

class GNSS {
public:
  uint32_t Instance;
  ValueF Latitude;          // Radians, +/- North/South
  ValueF Longitude;         // Radians, +/- East/West
  ValueF Cog;               // Radians, True
  ValueF Sog;               // m/s
  ValueF MagneticVariation; // Radians
  std::string UTCDateTime;  // ISO 8601 - YYYY-MM-DDThh:mm:ss.s
  ValueU32 TimeOffset;      // Offset minutes
  ValueU32 SatellitesInFix;
  ValueS32 BestOfFourSatellitesSNR; // dB
  ValueGNSSMethod Method;
  ValueGNSSFixType FixType;
  ValueF Hdop;              // unitless, lower is better
  ValueF Pdop;              // unitless, lower is better
  ValueF Vdop;              // unitless, lower is better
  ValueDouble LatitudeDeg;  // Degrees
  ValueDouble LongitudeDeg; // Degrees

  bool operator==(const GNSS &other) const = default;
};

class MonitoringKeyValue {
public:
  bool m_valid;
  float m_value;
  bool LimitValid;
  float Min;
  float Max;
  float WarnLow;
  float WarnHigh;

  bool operator==(const MonitoringKeyValue &other) const = default;
};

class BinaryLogicState {
public:
  uint32_t Dipswitch;
  uint32_t Instance;
  ValueU32 States;

  bool operator==(const BinaryLogicState &other) const = default;
};

class NetworkStatus {
public:
  std::string EthernetStatus;
  bool EthernetInternetConnectivity;
  std::string EthernetIp;
  std::string EthernetId;
  std::string WifiStatus;
  bool WifiInternetConnectivity;
  std::string WifiIp;
  std::string WifiSsid;
  std::string WifiSecurity;
  std::string WifiType;
  int32_t WifiChannel;
  int32_t WifiSignalStrengthDbm;
  std::string HotspotStatus;
  std::string HotspotIp;
  std::string HotspotSsid;
  std::string HotspotPassword;
  std::string HotspotSecurity;
  std::string HotspotType;
  int32_t HotspotChannel;
  std::string CellularStatus;
  bool CelllularInternetConnectivity;
  std::string CellularIp;
  std::string CellularOperator;
  std::string CellularType;
  int32_t CellularSignalStrengthDbm;
  std::string CellularSimIccid;
  std::string CellularSimEid;
  std::string CellularSimImsi;

  bool operator==(const NetworkStatus &other) const;
  void clear();
};

class SnapshotInstanceIdMap {
public:
  SnapshotInstanceIdMap() = default;
  ~SnapshotInstanceIdMap() = default;

  std::unordered_map<uint32_t, std::shared_ptr<Circuit>> m_Circuits;
  std::unordered_map<uint32_t, std::shared_ptr<Circuit>> m_Modes;
  std::unordered_map<uint32_t, std::shared_ptr<Tank>> m_Tanks;
  std::unordered_map<uint32_t, std::shared_ptr<Engine>> m_Engines;
  std::unordered_map<uint32_t, std::shared_ptr<AC>> m_AC;
  std::unordered_map<uint32_t, std::shared_ptr<DC>> m_DC;
  std::unordered_map<uint32_t, std::shared_ptr<Temperature>> m_Temperatures;
  std::unordered_map<uint32_t, std::shared_ptr<Pressure>> m_Pressures;
  std::unordered_map<uint32_t, std::shared_ptr<HVAC>> m_Hvacs;
  std::unordered_map<uint32_t, std::shared_ptr<ZipdeeAwning>> m_Awnings;
  std::unordered_map<uint32_t, std::shared_ptr<ThirdPartyGenerator>> m_ThirdPartyGenerators;
  std::unordered_map<uint32_t, std::shared_ptr<InverterCharger>> m_InverterChargers;
  std::unordered_map<uint32_t, std::shared_ptr<TyrePressure>> m_Tyrepressures;
  std::unordered_map<uint32_t, std::shared_ptr<AudioStereo>> m_AudioStereos;
  std::unordered_map<uint32_t, std::shared_ptr<ACMainContactor>> m_ACMainContactors;
  std::unordered_map<uint32_t, std::shared_ptr<GNSS>> m_GNSS;
  std::unordered_map<uint32_t, std::shared_ptr<MonitoringKeyValue>> m_MonitoringKeyValue;
  std::unordered_map<uint32_t, std::shared_ptr<BinaryLogicState>> m_BinaryLogicState;
  NetworkStatus m_NetworkStatus;
  std::string m_TimeStamp;

  void Clear();
};

class HealthStatus {
public:
  eHealth ServiceThread;
  eHealth NetworkThread;
  eHealth SCThread;
  eHealth GNSSThread;
  eHealth GNSSLatLon;
  eHealth GNSSFix;
};

class MonitoringKeyValueMap {
public:
  std::unordered_map<uint32_t, std::shared_ptr<MonitoringKeyValue>> KeyValueMap;

  void Clear();
};

}; // namespace N2KMonitoring