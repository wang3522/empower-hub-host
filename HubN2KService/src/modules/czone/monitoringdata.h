#pragma once

#include <unordered_map>
#include <string>
#include <memory>

class Circuit;
class Tank;
class Engine;
class AC;
class DC;
class Temperature;
class Pressure;
class HVAC;
class ZipdeeAwning;
class ThirdPartyGenerator;
class InverterCharger;
class TyrePressure;
class AudioStereo;
class ACMainContactor;
class GNSS;
class MonitoringKeyValue;
class BinaryLogicState;
class NetworkStatus;

class SnapshotInstanceIdMap {
public:
    SnapshotInstanceIdMap() = default;
    ~SnapshotInstanceIdMap() = default;

private:
    std::unordered_map<int, std::shared_ptr<Circuit>> m_circuits;
    std::unordered_map<int, std::shared_ptr<Circuit>> m_modes;
    std::unordered_map<int, std::shared_ptr<Tank>> m_tanks;
    std::unordered_map<int, std::shared_ptr<Engine>> m_engines;
    std::unordered_map<int, std::shared_ptr<AC>> m_ac;
    std::unordered_map<int, std::shared_ptr<DC>> m_dc;
    std::unordered_map<int, std::shared_ptr<Temperature>> m_temperatures;
    std::unordered_map<int, std::shared_ptr<Pressure>> m_pressures;
    std::unordered_map<int, std::shared_ptr<HVAC>> m_hvacs;
    std::unordered_map<int, std::shared_ptr<ZipdeeAwning>> m_awnings;
    std::unordered_map<int, std::shared_ptr<ThirdPartyGenerator>> m_thirdPartyGenerators;
    std::unordered_map<int, std::shared_ptr<InverterCharger>> m_inverterChargers;
    std::unordered_map<int, std::shared_ptr<TyrePressure>> m_tyrepressures;
    std::unordered_map<int, std::shared_ptr<AudioStereo>> m_audioStereos;
    std::unordered_map<int, std::shared_ptr<ACMainContactor>> m_acMainContactors;
    std::unordered_map<int, std::shared_ptr<GNSS>> m_gnss;
    std::unordered_map<int, std::shared_ptr<MonitoringKeyValue>> m_monitoringKeyValue;
    std::unordered_map<int, std::shared_ptr<BinaryLogicState>> m_binaryLogicState;
    std::shared_ptr<NetworkStatus> m_networkStatus;
    std::string m_timeStamp;
};