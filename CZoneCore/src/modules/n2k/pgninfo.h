#ifndef PGNINFO_H
#define PGNINFO_H

#include <cstdint>

struct PGNInfo {
  enum NetworkDataSource { eNmea2k = 0, eGNSS = 1, eSmartCraft = 2 };
  uint32_t PGN;
  bool SingleFrame;
  uint32_t ProprietaryCode;
  NetworkDataSource Source;
  bool LoopBack;

  PGNInfo(uint32_t pgn, bool singleFrame, uint32_t proprietaryCode,
          NetworkDataSource source) {
    PGN = pgn;
    SingleFrame = singleFrame;
    ProprietaryCode = proprietaryCode;
    Source = source;
    LoopBack = false;
  }

  PGNInfo(uint32_t pgn, bool singleFrame, uint32_t proprietaryCode,
          const bool loopBack) {
    PGN = pgn;
    SingleFrame = singleFrame;
    ProprietaryCode = proprietaryCode;
    Source = PGNInfo::eNmea2k;
    LoopBack = loopBack;
  }

  PGNInfo(uint32_t pgn, bool singleFrame, uint32_t proprietaryCode) {
    PGN = pgn;
    SingleFrame = singleFrame;
    ProprietaryCode = proprietaryCode;
    Source = PGNInfo::eNmea2k;
    LoopBack = false;
  }
};

#endif // PGNINFO_H