from typing import Optional

from N2KClient.models.constants import Constants
from .thing import Thing
from N2KClient.models.common_enums import ThingType
from N2KClient.models.n2k_configuration.gnss import GNSSDevice


class GNSS(Thing):
    def __init__(
        self,
        gnss: GNSSDevice,
        categories: list[str] = [],
    ):
        Thing.__init__(
            self,
            ThingType.GNSS,
            gnss.instance.instance,
            gnss.name_utf8,
            categories,
        )

        self.metadata[
            f"{Constants.empower}:{Constants.location}.{Constants.external}"
        ] = gnss.is_external
