import logging
from ...models.n2k_configuration.n2k_configuation import N2kConfiguration
from ...models.empower_system.empower_system import EmpowerSystem
from ...models.empower_system.thing import Thing
from ...models.n2k_configuration.device import DeviceType

from ...models.empower_system.hub import Hub

from .config_processor_helpers import (
    get_category_list,
    get_associated_circuit,
    get_primary_dc_meter,
    get_fallback_dc_meter,
    get_ac_meter_associated_bls,
    create_link,
    get_circuit_associated_bls,
    is_in_category,
    get_child_circuits,
    calculate_inverter_charger_instance,
    get_associated_tank,
)

from ...models.n2k_configuration.ui_relationship_msg import ItemType

from ...models.n2k_configuration.inverter_charger import InverterChargerDevice

from ...models.empower_system.inverter import CombiInverter
from ...models.n2k_configuration.tank import TankType
from ...models.empower_system.charger import CombiCharger, ACMeterCharger
from ...models.n2k_configuration.category_item import CategoryItem
from ...models.empower_system.battery import Battery
from ...models.empower_system.gnss import GNSS
from ...models.n2k_configuration.ac import ACType
from ...models.empower_system.shore_power import ShorePower
from ...models.empower_system.inverter import AcMeterInverter
from ...models.empower_system.tank import (
    FuelTank,
    BlackWaterTank,
    FreshWaterTank,
    WasteWaterTank,
)
from ...models.common_enums import ThingType
from ...models.empower_system.climate import Climate
from ...models.constants import Constants
from ...models.empower_system.light import CircuitLight
from ...models.empower_system.bilge_pump import CircuitBilgePump
from ...models.empower_system.pump import CircuitWaterPump
from ...models.empower_system.circuit_power_switch import CircuitPowerSwitch
from ...models.empower_system.engine_list import EngineList
from ...models.n2k_configuration.engine_configuration import EngineConfiguration
from ...models.empower_system.marine_engines import MarineEngine
from ...models.devices import N2kDevices
from .config_processor_helpers import (
    calculate_inverter_charger_instance,
)


class ConfigProcessor:
    _things: list[Thing]

    # Keep ACMeters associated with Inverters and DCMeters associated with chargers.
    # When creating ACMeters, DCMeters, check that they are not already part of a COMBI
    _acMeter_inverter_instances: list[str]
    _dcMeter_charger_instances: list[str]

    # Keep track of IC Status. Shorepower Component Status for Combi Shorepower is same as Combi Component Status.
    # Shorepower connected logic changes for shorepower depending on if it is associated with Combi
    _ic_component_status: dict

    # Mark associated circuits whose status is tracked by other component
    # i.e. shorepower circuit, so that these are not created as duplicate, independant circuits
    # when we create all circuit things
    _associated_circuit_instances: list[str]

    def __init__(self):
        self._things = []
        self._acMeter_inverter_instances = []
        self._dcMeter_charger_instances = []
        self._ic_component_status = {}
        self._associated_circuit_instances = []

    # ###################################################
    #     Devices
    # ###################################################
    def process_devices(
        self, config: N2kConfiguration, n2k_devices: N2kDevices
    ) -> None:
        for device in config.device.values():
            if device.device_type == DeviceType.Europa:
                hub = Hub(device, n2k_devices)
                self._things.append(hub)

    # ###################################################
    #     Inverter/Chargers
    # ###################################################
    def process_inverter_circuit(
        self,
        inverter_charger: InverterChargerDevice,
        config: N2kConfiguration,
    ):
        inverter_visible_circuit = None
        if (
            inverter_charger.inverter_circuit_id.enabled
            and inverter_charger.inverter_circuit_id.id in config.hidden_circuit
        ):
            inverter_hidden_circuit = config.hidden_circuit[
                inverter_charger.inverter_circuit_id.id
            ]

            if (
                inverter_hidden_circuit is not None
                and inverter_hidden_circuit.control_id in config.circuit
            ):
                self._associated_circuit_instances.append(
                    inverter_hidden_circuit.control_id
                )

                inverter_visible_circuit = config.circuit[
                    inverter_hidden_circuit.control_id
                ]

                self._associated_circuit_instances.append(
                    inverter_visible_circuit.control_id
                )
                return inverter_visible_circuit

    def process_charger_circuit(
        self, inverter_charger: InverterChargerDevice, config: N2kConfiguration
    ):
        charger_visible_circuit = None
        if (
            inverter_charger.charger_circuit_id.enabled
            and inverter_charger.charger_circuit_id.id in config.hidden_circuit
        ):
            charger_hidden_circuit = config.hidden_circuit[
                inverter_charger.charger_circuit_id.id
            ]

            if (
                charger_hidden_circuit is not None
                and charger_hidden_circuit.control_id in config.circuit
            ):
                self._associated_circuit_instances.append(
                    charger_hidden_circuit.control_id
                )

                charger_visible_circuit = config.circuit[
                    charger_hidden_circuit.control_id
                ]

                self._associated_circuit_instances.append(
                    charger_visible_circuit.control_id
                )
                return charger_visible_circuit

    def process_inverters(
        self,
        config: N2kConfiguration,
        inverter_charger: InverterChargerDevice,
        categories: list[CategoryItem],
        n2k_devices: N2kDevices,
        instance: int,
    ) -> None:

        ac_meter = None
        inverter_associated_ac_line = None

        inverter_visible_circuit = self.process_inverter_circuit(
            inverter_charger, config
        )

        if inverter_charger.inverter_ac_id is not None:
            ac_meter, inverter_associated_ac_line = next(
                (
                    (meter, key)
                    for meter in config.ac.values()
                    for key, value in meter.line.items()
                    if value.id == inverter_charger.inverter_ac_id.id
                    and inverter_charger.inverter_ac_id.enabled
                ),
                (None, None),
            )

        if ac_meter is not None:
            categories = next(
                (
                    categories
                    for line in ac_meter.line.values()
                    if (
                        categories := get_category_list(
                            ItemType.AcMeter,
                            line.id,
                            config,
                        )
                    )
                    != []
                ),
                [],
            )
        inverter_thing = CombiInverter(
            inverter_charger=inverter_charger,
            ac_line1=ac_meter.line[1] if ac_meter and 1 in ac_meter.line else None,
            ac_line2=ac_meter.line[2] if ac_meter and 2 in ac_meter.line else None,
            ac_line3=ac_meter.line[3] if ac_meter and 3 in ac_meter.line else None,
            categories=categories,
            instance=instance,
            inverter_circuit=inverter_visible_circuit,
            status_ac_line=inverter_associated_ac_line,
            n2k_devices=n2k_devices,
        )
        self._things.append(inverter_thing)
        if ac_meter is not None:
            self._acMeter_inverter_instances.append(ac_meter.line[1].instance.instance)

    def process_chargers(
        self,
        inverter_charger: InverterChargerDevice,
        config: N2kConfiguration,
        categories: list[CategoryItem],
        n2k_devices: N2kDevices,
        instance: int,
    ) -> None:
        charger_visible_circuit = self.process_charger_circuit(inverter_charger, config)

        dc_meter1 = None
        if inverter_charger.battery_bank_1_id.enabled is not None:
            dc_meter1 = next(
                (
                    meter
                    for meter in config.dc.values()
                    if meter.id == inverter_charger.battery_bank_1_id.id
                ),
                None,
            )
            if dc_meter1 is not None:
                self._dcMeter_charger_instances.append(dc_meter1.instance.instance)

        dc_meter2 = None
        if inverter_charger.battery_bank_2_id.enabled is not None:
            dc_meter2 = next(
                (
                    meter
                    for meter in config.dc.values()
                    if meter.id == inverter_charger.battery_bank_2_id.id
                ),
                None,
            )
            if dc_meter2 is not None:
                self._dcMeter_charger_instances.append(dc_meter2.instance.instance)

        dc_meter3 = None
        if inverter_charger.battery_bank_3_id.enabled is not None:
            dc_meter3 = next(
                (
                    meter
                    for meter in config.dc.values()
                    if meter.id == inverter_charger.battery_bank_3_id.id
                ),
                None,
            )
            if dc_meter3 is not None:
                self._dcMeter_charger_instances.append(dc_meter3.instance.instance)
        charger_thing = CombiCharger(
            inverter_charger=inverter_charger,
            dc1=dc_meter1 if dc_meter1 is not None else None,
            dc2=dc_meter2 if dc_meter2 is not None else None,
            dc3=dc_meter3 if dc_meter3 is not None else None,
            categories=categories,
            charger_circuit=charger_visible_circuit,
            instance=instance,
            n2k_devices=n2k_devices,
        )

        shorepower = None
        if inverter_charger.charger_ac_id.enabled:
            shorepower, shore_key = next(
                (
                    (meter, key)
                    for meter in config.ac.values()
                    for key, value in meter.line.items()
                    if value.id == inverter_charger.charger_ac_id.id
                ),
                (None, None),
            )

        if shorepower is not None:
            self._ic_component_status[shorepower.line[1].instance.instance] = (
                # charger_thing.component_status
                charger_thing.component_status,
                shore_key,
            )

        self._things.append(charger_thing)

    def process_inverter_chargers(
        self, config: N2kConfiguration, n2k_devices: N2kDevices
    ) -> None:
        # For each inverter/charger we will create both an inverter and
        # charger thing.
        for id, inverter_charger in config.inverter_charger.items():
            categories = get_category_list(
                ItemType.InverterCharger,
                inverter_charger.id,
                config,
            )
            instance = calculate_inverter_charger_instance(inverter_charger)
            self.process_inverters(
                config, inverter_charger, categories, n2k_devices, instance
            )
            self.process_chargers(
                inverter_charger, config, categories, n2k_devices, instance
            )

    # ###################################################
    #     DC Meters
    # ###################################################
    def process_dc_meters(
        self, config: N2kConfiguration, n2k_devices: N2kDevices
    ) -> None:
        for dc_meter in config.dc.values():
            circuit = None
            if dc_meter.instance.instance in self._dcMeter_charger_instances:
                continue
            categories = get_category_list(
                ItemType.DcMeter,
                dc_meter.id,
                config,
            )
            circuit = get_associated_circuit(
                ItemType.DcMeter,
                dc_meter.id,
                config,
            )
            primary_dc = get_primary_dc_meter(dc_meter.id, config)
            secondary_dc = get_fallback_dc_meter(dc_meter.id, config)
            if circuit is not None:
                self._associated_circuit_instances.append(circuit.control_id)

            dc_thing = Battery(
                battery=dc_meter,
                categories=categories,
                battery_circuit=circuit,
                primary_battery=primary_dc,
                fallback_battery=secondary_dc,
                n2k_devices=n2k_devices,
            )
            self._things.append(dc_thing)

    # ###################################################
    #     GNSS
    # ###################################################
    def process_gnss(self, config: N2kConfiguration, n2k_devices: N2kDevices) -> None:
        for gnss in config.gnss.values():
            gnss_thing = GNSS(gnss, n2k_devices)
            self._things.append(gnss_thing)

    # ###################################################
    #     AC Meters
    # ###################################################
    def process_ac_meters(
        self, config: N2kConfiguration, n2k_devices: N2kDevices
    ) -> None:
        for ac_meter in config.ac.values():
            if ac_meter.line[1].instance.instance in self._acMeter_inverter_instances:
                continue

            ic_associated_line = None
            component_status = None
            if ac_meter.line[1].instance.instance in self._ic_component_status:
                component_status, ic_associated_line = self._ic_component_status[
                    ac_meter.line[1].instance.instance
                ]

            circuit = next(
                (
                    circuit
                    for line in ac_meter.line.values()
                    if (
                        circuit := get_associated_circuit(
                            ItemType.AcMeter,
                            line.id,
                            config,
                        )
                    )
                    is not None
                ),
                None,
            )

            if circuit is not None:
                self._associated_circuit_instances.append(circuit.control_id)

            ac_type = next(
                (
                    ac_type
                    for line in ac_meter.line.values()
                    if (ac_type := line.ac_type)
                    not in [
                        ACType.Unknown,
                        ACType.Parallel,
                        ACType.Outlet,
                        ACType.Generator,
                    ]
                ),
                None,
            )

            if ac_type is None:
                continue

            categories = next(
                (
                    categories
                    for line in ac_meter.line.values()
                    if (
                        categories := get_category_list(
                            ItemType.AcMeter,
                            line.id,
                            config,
                        )
                    )
                    != []
                ),
                [],
            )

            ac_bls = get_ac_meter_associated_bls(ac_meter=ac_meter, config=config)

            if ac_type == ACType.ShorePower:
                thing = ShorePower(
                    ac_meter.line[1] if 1 in ac_meter.line else None,
                    ac_meter.line[2] if 2 in ac_meter.line else None,
                    ac_meter.line[3] if 3 in ac_meter.line else None,
                    n2k_devices=n2k_devices,
                    categories=categories,
                    circuit=circuit,
                    ic_associated_line=ic_associated_line,
                    bls=ac_bls,
                    component_status=component_status,
                )

            if ac_type == ACType.Inverter:
                thing = AcMeterInverter(
                    ac_meter.line[1] if 1 in ac_meter.line else None,
                    ac_meter.line[2] if 2 in ac_meter.line else None,
                    ac_meter.line[3] if 3 in ac_meter.line else None,
                    n2k_devices=n2k_devices,
                    categories=categories,
                    circuit=circuit,
                )
            if ac_type == ACType.Charger:
                thing = ACMeterCharger(
                    ac_meter.line[1] if 1 in ac_meter.line else None,
                    ac_meter.line[2] if 2 in ac_meter.line else None,
                    ac_meter.line[3] if 3 in ac_meter.line else None,
                    n2k_devices=n2k_devices,
                    categories=categories,
                    circuit=circuit,
                )
            self._things.append(thing)

    # ###################################################
    #     Tanks
    # ###################################################
    def process_tanks(self, config: N2kConfiguration, n2k_devices: N2kDevices) -> None:
        for tank in config.tank.values():
            links = []
            # Fuel tanks
            if tank.tank_type == TankType.Fuel or tank.tank_type == TankType.Oil:
                tank_thing = FuelTank(tank=tank)
                self._things.append(tank_thing)
            # Water tanks (have associated circuits (pumps))
            else:
                circuit = get_associated_circuit(
                    ItemType.FluidLevel,
                    tank.id,
                    config,
                )

                if circuit is not None:
                    link = create_link(
                        ThingType.PUMP, ThingType.WATER_TANK, circuit.control_id
                    )
                    links.append(link)
                    # Ensure duplicate power circuit is not created
                    self._associated_circuit_instances.append(circuit.control_id)

                if tank.tank_type == TankType.FreshWater:
                    tank_thing = FreshWaterTank(
                        tank=tank,
                        links=links,
                        n2k_devices=n2k_devices,
                    )
                    self._things.append(tank_thing)

                if tank.tank_type == TankType.WasteWater:
                    tank_thing = WasteWaterTank(
                        tank=tank,
                        links=links,
                        n2k_devices=n2k_devices,
                    )
                    self._things.append(tank_thing)

                if tank.tank_type == TankType.BlackWater:
                    tank_thing = BlackWaterTank(
                        tank=tank,
                        links=links,
                        n2k_devices=n2k_devices,
                    )
                    self._things.append(tank_thing)

    # ###################################################
    #     Hvac
    # ###################################################
    def process_hvac(self, config: N2kConfiguration, n2k_devices: N2kDevices) -> None:
        for hvac in config.hvac.values():
            categories = get_category_list(ItemType.Temperature, hvac.id, config)
            climate_thing = Climate(
                hvac=hvac,
                categories=categories,
                n2k_devices=n2k_devices,
            )
            self._things.append(climate_thing)

    # ###################################################
    #     Circuits
    # ###################################################
    def process_circuits(
        self, config: N2kConfiguration, n2k_devices: N2kDevices
    ) -> None:
        for circuit in config.circuit.values():
            links = []
            # 1 - LocalAndRemove, 2 - RemoteOnly
            if circuit.remote_visibility != 1 and circuit.remote_visibility != 2:
                continue

            bls = get_circuit_associated_bls(circuit, config)
            if is_in_category(circuit.categories, Constants.Lighting):
                child_circuit = get_child_circuits(circuit.id, config)
                for child in child_circuit:
                    link = create_link(
                        ThingType.LIGHT, ThingType.LIGHT, child.control_id
                    )
                    links.append(link)
                circuit_thing = CircuitLight(
                    circuit=circuit,
                    links=links,
                    bls=bls,
                    n2k_devices=n2k_devices,
                )
                self._things.append(circuit_thing)

            if is_in_category(circuit.categories, Constants.BilgePumps):
                # If circuit is associated with a combi inverter/charger, skip it
                if circuit.control_id in self._associated_circuit_instances:
                    continue

                circuit_thing = CircuitBilgePump(circuit, links, n2k_devices, bls)
                circuit_thing.circuit = circuit
                self._things.append(circuit_thing)

            if is_in_category(circuit.categories, Constants.Pumps):
                associated_tank = get_associated_tank(circuit.control_id, config)
                if associated_tank is not None:
                    link = create_link(
                        ThingType.WATER_TANK,
                        ThingType.PUMP,
                        associated_tank.instance.instance,
                    )
                    links.append(link)
                circuit_thing = CircuitWaterPump(circuit, links, n2k_devices, bls)
                self._things.append(circuit_thing)
            if (
                is_in_category(circuit.categories, Constants.Power)
                and circuit.control_id not in self._associated_circuit_instances
            ):
                circuit_thing = CircuitPowerSwitch(circuit, links, n2k_devices, bls)
                self._things.append(circuit_thing)

    def build_empower_system(
        self, config: N2kConfiguration, devices: N2kDevices
    ) -> EmpowerSystem:
        logger = logging.getLogger("Config Processor")
        self._things.clear()
        try:
            self.process_devices(config, devices)
            self.process_inverter_chargers(config, devices)
            self.process_dc_meters(config, devices)
            self.process_gnss(config, devices)
            self.process_ac_meters(config, devices)
            self.process_tanks(config, devices)
            self.process_hvac(config, devices)
            self.process_circuits(config, devices)

            # Config metadata?
            system = EmpowerSystem(config.config_metadata)
            [system.add_thing(thing) for thing in self._things]

            return system

        except Exception as error:
            logger.error(error, exc_info=True)
            raise

    def build_engine_list(
        self, config: EngineConfiguration, devices: N2kDevices
    ) -> EngineList:
        logger = logging.getLogger("Engine Config Processor")
        engines: list[Thing] = []
        try:
            for device in config.devices.values():
                thing = MarineEngine(device, devices)
                engines.append(thing)

        except Exception as error:
            logger.error(error)
            raise
        engine_list = EngineList(should_reset=config.should_reset)
        [engine_list.add_engine(engine) for engine in engines]

        return engine_list
