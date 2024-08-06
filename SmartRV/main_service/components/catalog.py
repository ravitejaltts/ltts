
# TODO Read all component files and generate catalog


from dataclasses import dataclass


from main_service.components.lighting import *
from main_service.components.movables import *
from main_service.components.climate import *
from main_service.components.energy import *
from main_service.components.watersystems import *
from main_service.components.vehicle import *
from main_service.components.system import *
from main_service.components.features import *
from main_service.components.connectivity import *


@dataclass
class CatalogItem:
    code: str
    component: object
    state: object


components = [
    # Lighting
    (LightSimple, LightSimpleState),
    (LightDimmable, LightDimmableState),
    (LightRGBW, LightRGBWState),
    (LightGroup, LightGroupState),
    (SmartLightGroup, LightGroupSmartState),

    # Movables
    (AwningRvc, AwningRvcState),
    (LevelJacksRvc, JackState),
    (SlideoutBasic, SlideoutBasicState),

    # Climate
    (Thermostat, ThermostatState),
    (ThermostatOutdoor, ThermostatOutdoorState),
    (RoofFanAdvanced, RoofFanAdvancedState),
    (HeaterBasic, HeaterState),
    (HeaterACHeatPump, HeaterSourceState),
    (RefrigeratorBasic, RefrigeratorState),
    (AcRvcGe, AcRvcGeState),
    (AcRvcTruma, AcRvcTrumaState),
    (ThermostatWired, ThermostatWiredState),
    (ACBasic, ACBasicState),

    # Energy
    (FuelTank, FuelTankState),
    (InverterBasic, InverterBasicState),
    (InverterAdvanced, InverterAdvancedState),
    (ChargerAdvanced, ChargerAdvancedState),
    (FuelTank, FuelTankState),
    (PowerSourceSolar, PowerSourceState),
    (PowerSourceShore, PowerSourceState),
    (PowerSourceAlternator, PowerSourceState),
    (PowerSourceGenerator, PowerSourceState),
    (BatteryManagement, BatteryMgmtState),
    (EnergyConsumer, EnergyConsumerState),
    (GeneratorPropane, GeneratorState),
    (GeneratorDiesel, GeneratorState),
    (BatteryPack, BatteryState),
    (PowerSourceProPower, PowerSourceState),
    (LoadShedding500, LoadSheddingState),
    (LoadShedderComponent, LoadShedderState),
    (LoadShedderCircuit, LoadShedderState),

    # Watersystems
    (WaterHeaterRvc, WaterHeaterRvcState),
    (WaterHeaterSimple, WaterHeaterSimpleState),
    (WaterPumpDefault, WaterPumpState),
    (WaterTankDefault, WaterTankState),
    (TankHeatingPad, TankHeatingPadState),
    (ToiletCircuitDefault, ToiletCircuitState),

    # Vehicle
    (VehicleSprinter, VehicleSprinterState),
    (HouseDoorLock, HouseDoorLockState),
    (VehicleId, VINState),
    (VehicleETransit, VehicleETransitState),
    (VehicleLocation, VehicleLocationState),

    # System
    (LockoutBasic, LockoutState),
    (LockoutStatic, LockoutStaticState),
    (LockoutDynamic, LockoutDynamicState),

    (FAILURE_TEST_COMPONENT, FAILURECOMPONENTSTATE),

    (ServiceSettings, ServiceSettingsState),

    # Features
    (WeatherFeature, WeatherFeatureState),
    (PetMonitorFeature, PetMonitorFeatureState),
    (Diagnostics, DiagnosticsState),
    (RemoteTest, RemoteTestState),
    (SystemOverview, SystemOverviewState),

    # Connectivity
    (NetworkRouter, RouterState),
]

component_class_library = {}
component_catalog = {}
component_schemas = {}
for comp, state in components:
    comp_instance = comp(state=state())
    comp_instance.set_component_id()
    # print(comp_instance.componentId)
    component_catalog[comp_instance.componentId] = CatalogItem(
        code=comp_instance.code,
        component=comp,
        state=state
    )
    component_schemas[comp_instance.componentId] = comp
    component_class_library[comp.__name__] = comp
