#ifndef PGN_126208_MSG_H
#define PGN_126208_MSG_H

#include <stdint.h>
#include <Nmea2kLib/tNetworkInterface.h>

#ifdef __cplusplus
extern "C" {
#endif

#define REQUEST_GROUP_FUNCTION 0
#define COMMAND_GROUP_FUNCTION 1
#define ACKNOWLEDGE_GROUP_FUNCTION 2
#define READ_FIELDS_GROUP_FUNCTION 3
#define READ_FIELDS_REPLY_GROUP_FUNCTION 4
#define WRITE_FIELDS_GROUP_FUNCTION 5
#define WRITE_FIELDS_REPLY_GROUP_FUNCTION 6

#define FAST_PACKET_SIZE 223

#define REQUEST_HEADER_SIZE 11
#define COMMAND_HEADER_SIZE 6
#define ACKNOWLEDGE_HEADER_SIZE 6
#define READ_FIELDS_HEADER_SIZE 4
#define READ_FIELDS_REPLY_HEADER_SIZE 4
#define WRITE_FIELDS_HEADER_SIZE 4
#define WRITE_FIELDS_REPLY_HEADER_SIZE 4

typedef struct
{
    uint8_t DestinationAddress;
    uint8_t ComplexGroupFunctionCode;
    uint32_t PGN;
    uint8_t FieldDataSize;
    unsigned char FieldData[FAST_PACKET_SIZE];
} tNmea2kPGN126208GroupFunctionData;

typedef struct
{
    tNmea2kPGN126208GroupFunctionData Base;
    uint32_t TransmissionInterval;
    uint16_t TransmissionIntervalOffset;
    uint8_t NumberOfPairs;
} tNmea2kPGN126208RequestGroupFunctionData;

typedef struct
{
    tNmea2kPGN126208GroupFunctionData Base;
    uint8_t PrioritySetting;
    uint8_t NumberOfPairs;
} tNmea2kPGN126208CommandGroupFunctionData;

typedef struct
{
    tNmea2kPGN126208GroupFunctionData Base;
    uint8_t PGNErrorCode;
    uint8_t TransmissionIntervalPriorityErrorCode;
    uint8_t NumberOfParamters;
} tNmea2kPGN126208AcknowledgeGroupFunctionData;

typedef struct
{
    tNmea2kPGN126208GroupFunctionData Base;
    uint16_t ManufacturersCode;
    uint8_t IndustryGroup;
    uint8_t UniqueId;
    uint8_t NumberOfCommandedParameters;
    uint8_t NumberOfFieldsToReadWrite;
} tNmea2kPGN126208ReadWriteFieldsGroupFunctionData;

void Unpack126208PGN(const tCZoneNetworkMsg* msg, void* data);
void Pack126208PGN(tCZoneNetworkMsg* msg, const void* data);

#ifdef __cplusplus
}
#endif

#endif
