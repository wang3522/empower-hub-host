#ifndef UNIT_UTILS_H
#define UNIT_UTILS_H

#include <DevelopmentLib/Utils/tUnitTypes.h>
#include <Monitoring/tCZoneDataTypes.h>

namespace Utils::Units
{
    tUnitTypes UnitsFromDataType(const tCZoneDataType dataType);
};

#endif