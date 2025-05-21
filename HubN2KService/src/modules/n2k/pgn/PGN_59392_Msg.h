#ifndef PGN_59392_MSG_H
#define PGN_59392_MSG_H

#include <stdint.h>
#include <Nmea2kLib/tNetworkInterface.h>

#ifdef __cplusplus
extern "C" {
#endif

#define ISO_ACKNOWLEDGE_NOTSUPPORTED 1
#define ISO_ACKNOWLEDGE_ACCESS_DENIED 2

typedef struct
{
    uint8_t DestinationAddress;
    uint32_t PGN;
    uint8_t Acknowledgement;
} tNmea2kPGN59392Data;

void Pack59392PGN(tCZoneNetworkMsg* msg, const void* data);

#ifdef __cplusplus
}
#endif

#endif
