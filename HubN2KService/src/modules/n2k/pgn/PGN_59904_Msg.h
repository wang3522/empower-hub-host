#ifndef PGN_59904_MSG_H
#define PGN_59904_MSG_H

#include <stdint.h>
#include <Nmea2kLib/tNetworkInterface.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    uint32_t PGN;
} tNmea2kPGN59904Data;

void Unpack59904PGN(const tCZoneNetworkMsg* msg, void* data);

#ifdef __cplusplus
}
#endif

#endif
