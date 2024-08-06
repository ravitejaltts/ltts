'''Model definition for the WM524NP/IM524NP'''

from copy import deepcopy

from common_libs.models.common import EventValues, RVEvents

from main_service.components.catalog import component_catalog as catalog
from main_service.components.catalog import component_class_library as class_library

from main_service.components.climate import *
from main_service.components.energy import *
from main_service.components.vehicle import *
from main_service.components.movables import *
from main_service.components.lighting import *
from main_service.components.watersystems import *
from main_service.components.system import *
from main_service.components.connectivity import *

from main_service.components.features import get_base_features

from main_service.components.inputs.alerts import ALERTS

from main_service.components.vehicles.can_mappings import _500_BASE
from main_service.components.vehicles.config_500 import HAL_CATEGORIES_500

# TODO: Figure out how to auto get schema for state
# print(dir(FuelTank))
# print(FuelTank.schema())
# state_schema_ref = FuelTank.schema().get('properties', {}).get('state', {}).get('$ref')
# print(state_schema_ref)
# state_schema = FuelTank.schema().get('definitions', {}).get(state_schema_ref.split('/')[-1])

# print(state_schema)

model_definition = {
    # $schema is a helper file, if present will validate the schema as per platform design
    "$schema": "./$schema.json",
    # id: TODO: This should be auto generated
    # "id": "s500.7054042.WM524T",
    # type is static to identify it as a componentGroup which defines a vehicle including all its options
    "type": "componentGroup",
    # description is static for the type
    "description": "component groups allow us to piece together rv components based on its device type, model, floorplan starting with lowest to greatest specificity",
    # deviceType identifies it as a group of vehicles that are similar
    "deviceType": "s500",
    # seriesModel is the numerical ID for the specific model
    "seriesModel": "1054742",   # TODO: Confirm with Rick
    # floorPlan is the specific flooplan, a floorplan separates variants of the same vehicle
    "floorPlan": "WM524NP",
    # attributes can be used as Meta information that can be propagated to the UI as needed
    "attributes": {
        "name": "????",
        "seriesName": "VIEW",
        "seriesCode": "500",
        "version": "1.0.0",          # TODO: Increment this version automatically upon generation
    },
    # optionCodes (dict)
    # are just a list of all possible options, nothing specifically happens here just a at a glance check what options do apply
    # optioncodes will be handled in filters further down in relatedComponents
    "optionCodes": [
        "52D",
        "33F",
        "52N",
        "29J",
        "291",
        "31T",
        "31P"
    ],
    # filters (dict)
    # that help query broader picture data and help to which modelYears and other meta info this plan applies to
    "filters": {
        "modelYears": ["2024", "2025"]
    },
    # components (list)
    # List of components that make up this model including options, instances etc.
    # This will drive which schemas/models get associated with this over APIs
    # Components in this case are a glue item between physical hardware abstraction and the
    # features they drive, a physical component could be split up in multiple
    # virtual components here
    "components": [
        VehicleSprinter(
            # The Sprinter chassis could provide a cetain base functionality
            # around the PSM outputs and how they are handled
            # PSM outputs ignition, park brake, transmission not in park, door lock state
            instance=1,
            attributes={
                'name': 'Mercedes Sprinter',
                'controllable': 'N'
            },
            state=VehicleSprinterState(),
            meta={
                'manufacturer': 'TBDMercedes Benz - TrucksX',
                'model': 'Sprinter',
                'part': 'TBD'
            }
        ),
        Thermostat(
            instance=1,
            state=ThermostatState(),
            attributes={
                'name': 'Thermostat'
            },
            meta={
                'manufacturer': 'Winnebago',
                'model': 'WinnConnect Virtual Thermostat',
                'part': 'WC-TH-VIRTUAL'
            }
        ),
        HouseDoorLock(
            instance=1,
            attributes={
                "name": "Door Lock / Unlock",
                'description': 'Handles the door lock/unlock state of the house vs. the chassis'
            },
            state=HouseDoorLockState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        HeaterBasic(
            instance=1,
            attributes={
                "name": "Heater (LP Furnace)",
                'description': 'Dometic LP Furnace'
            },
            state=HeaterState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }

        ),
        RefrigeratorBasic(
            instance=1,
            attributes={
                'name': 'Refrigerator',
                'description': 'Dometic fridge ?'
            },
            state=RefrigeratorState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        RefrigeratorBasic(
            instance=2,
            attributes={
                'name': 'Freezer',
                'description': 'Freezer compartment'
            },
            state=RefrigeratorState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        RoofFanAdvanced(
            instance=1,
            attributes={
                'name': 'Roof Vent',
                'description': 'Main Roof Fan'
            },
            state=RoofFanAdvancedState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        RoofFanAdvanced(
            instance=2,
            attributes={
                'name': 'Bathroom Vent',
                'description': 'Bath Roof Fan'
            },
            state=RoofFanAdvancedState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        AcRvcTruma(
            instance=1,
            attributes={
                "name": "Truma - Air Conditioning",
                "description": "Air conditioner option 291 - Truma"
            },
            state=AcRvcTrumaState(),
            # optionCodes='291',
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        AcRvcGe(
            instance=1,
            attributes={
                "name": "GE - Air Conditioning",
                "description": "Air conditioner option 29J - GE with Heatpump"
            },
            state=AcRvcGeState(),
            # optionCodes='29J',
            relatedComponents=[
                {
                    "componentTypeId": HeaterACHeatPump().componentId,
                    "instance": 2
                }
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        # {
        #     "componentTypeId": "climate.ac_rvc_ge",
        #     "instance": 1,
        #     "attributes": {
        #         "name": "GE - Air Conditioning",
        #         "description": "Air conditioner option 29J - GE with Heatpump"
        #     },
        #     "filters": {
        #         "optionCode": "29J"
        #     }
        # },
        HeaterACHeatPump(
            instance=2,
            attributes={
                'name': 'GE AC Heatpump'
            },
            state=HeaterSourceState(),
            optionCodes='29J',
            relatedComponents=[
                {
                    "componentTypeId": AcRvcGe().componentId,
                    "instance": 1
                },
                {
                    "componentTypeId": FuelTank().componentId,
                    "instance": 1
                },
                {
                    "componentTypeId": BatteryManagement().componentId,
                    "instance": 1
                }
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        ThermostatOutdoor(
            instance=2,
            attributes={
                'name': 'Outdoor'
            },
            state=ThermostatOutdoorState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        # {
        #     "componentTypeId": "connectivity.ce_basic",
        #     "instance": 1,
        #     "attributes": {
        #         "name": "Cellular Services"
        #     }
        # },
        BatteryManagement(
            instance=1,
            attributes={
                'name': 'battery management',
                'type': 'LITHIONICS',
                # 'batCnt': 1,
                'nominalVoltage': '12.8V',
                # 'maxCurrent': '',
                'minSoc': 10
            },
            state=BatteryMgmtState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            },
            relatedComponents=[
                {
                    "componentTypeId": BatteryPack().componentId,
                    "instance": 1
                },
            ],

        ),
        BatteryPack(
            instance=1,
            attributes={
                'name': 'LITHIONICS IONGEN',    # TODO: Get the right name
                'type': 'LITHIONICS',
                'description': 'Default battery pack',
                'cap': '320AH'
            },
            state=BatteryState(),
            relatedComponents=[
                {
                    "componentTypeId": BatteryManagement().componentId,
                    "instance": 1
                },
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        BatteryPack(
            instance=1,
            attributes={
                'name': 'LITHIONICS IONGEN',    # TODO: Get the right name
                'type': 'LITHIONICS',
                'description': 'Defaul battery pack',
                'cap': '640AH'                       # TODO: Get the capacity and possible options
            },
            state=BatteryState(),
            relatedComponents=[
                {
                    "componentTypeId": BatteryManagement(
                        state=BatteryMgmtState()).componentId,
                    "instance": 1
                }
            ],
            # optionCodes="XXDOMTBD",
            optionCodes="33W"
        ),
        BatteryPack(
            instance=2,
            attributes={
                'name': 'LITHIONICS IONGEN',    # TODO: Get the right name
                'type': 'LITHIONICS',
                'description': 'Defaul battery pack',
                'cap': '320AH'                       # TODO: Get the capacity and possible options
            },
            state=BatteryState(),
            relatedComponents=[
                {
                    "componentTypeId": BatteryManagement(
                        state=BatteryMgmtState()).componentId,
                    "instance": 1
                }
            ],
            optionCodes="33W"
        ),
        InverterAdvanced(
            instance=1,
            attributes={
                "name": "Inverter Xantrex",
                "type": "RVC",      # Still needed ?
                "state.maxLoad": 2000
            },
            state=InverterAdvancedState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        EnergyConsumer(
            instance=1,
            attributes={
                'name': 'AC - Total',
                'type': 'AC',
                'acc': 'MEASURED'
            },
            state=EnergyConsumerState()
        ),
        # TODO: Add all consumers that are known
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 3,
        #     "attributes": {
        #         "name": "Water Heater",
        #         "type": "AC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 4,
        #     "attributes": {
        #         "name": "Other AC",
        #         "type": "AC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 5,
        #     "attributes": {
        #         "name": "Inverter Output",
        #         "type": "AC",
        #         "acc": "MEASURED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 10,
        #     "attributes": {
        #         "name": "Lights",
        #         "type": "DC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 11,
        #     "attributes": {
        #         "name": "Refrigerator",
        #         "type": "DC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 12,
        #     "attributes": {
        #         "name": "Fresh Water Pump",
        #         "type": "DC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 13,
        #     "attributes": {
        #         "name": "Gray Water Pump",
        #         "type": "DC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 14,
        #     "attributes": {
        #         "name": "Air Conditioner",
        #         "type": "AC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 15,
        #     "attributes": {
        #         "name": "Roof Fan",
        #         "type": "DC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 16,
        #     "attributes": {
        #         "name": "DC - Total",
        #         "type": "DC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        # {
        #     "componentTypeId": "energy.ec_basic",
        #     "instance": 17,
        #     "attributes": {
        #         "name": "DC - Other",
        #         "type": "DC",
        #         "acc": "ESTIMATED"
        #     }
        # },
        PowerSourceSolar(
            instance=1,
            attributes={
                'name': 'Solar'
            },
            state=PowerSourceState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        PowerSourceShore(
            instance=2,
            attributes={
                'name': 'Shore'
            },
            state=PowerSourceState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        PowerSourceAlternator(
            instance=3,
            attributes={
                'name': 'Alternator',
                'type': 'wakespeed',
                'volts': '48'
            },
            state=PowerSourceState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        PowerSourceGenerator(
            instance=4,
            attributes={
                'name': 'Generator'
            },
            state=PowerSourceState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            },
            relatedComponents=[
                {
                    "componentTypeId": GeneratorPropane().componentId,
                    "instance": 1
                }
            ]
        ),
        FuelTank(
            instance=1,
            state=FuelTankState(),
            attributes={
                'name': 'Liquid Propane',
                'type': 'LP',
                'description': 'Liquid Propane',
                'cap': 30,      # TODO Check capacity
                'unit': 'G',
                'controllable': 'N'
            },
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        GeneratorPropane(
            instance=1,
            attributes={
                'name': 'LP Generator',
                'description': '4,000 WATT, RVMP, LP/GAS'
            },
            state=GeneratorState(),
            optionCodes='52D',
            meta={
                'manufacturer': 'RVMP',
                'model': '4,000 WATT, LP/GAS ',
                'part': 'TBD'
            },
            relatedComponents=[
                {
                    "componentTypeId": FuelTank().componentId,
                    "instance": 1
                },
                {
                    "componentTypeId": PowerSourceGenerator().componentId,
                    "instance": 4
                }
            ]
        ),
        GeneratorDiesel(
            instance=1,
            attributes={
                'name': 'Diesel Generator',
                'description': 'Onan Diesel Generator'
            },
            state=GeneratorState(),
            optionCodes='33F',
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=1,
            attributes={
                'name': 'Front Bunk R',
                'description': 'Dimmable Light Zone',
                'type': 'DIM__ITC_CHANNEL',

            },
            optionCodes='31T',
            state=LightDimmableState()
        ),
        LightDimmable(
            instance=2,
            attributes={
                'name': 'Front Bunk R',
                'description': 'Dimmable Light Zone',
                'type': 'DIM__ITC_CHANNEL',

            },
            optionCodes='31T',
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=2,
            attributes={
                'name': 'Bed 1 OVHD',
                'description': 'Dimmable Light Zone',
                'type': 'DIM__ITC_CHANNEL',

            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=3,
            attributes={
                'name': 'Bed 2 OVHD',
                'description': 'Dimmable Light Zone',
                'type': 'DIM__ITC_CHANNEL',

            },
            state=LightDimmableState()
        ),
        LightDimmable(
            instance=4,
            attributes={
                "name": "Bed Accent",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=5,
            attributes={
                "name": "Front Bunk L",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            optionCodes='31T',
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=6,
            attributes={
                "name": "Service",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState()
        ),
        LightDimmable(
            instance=7,
            attributes={
                "name": "Porch",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=8,
            attributes={
               "name": "Lounge",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=9,
            attributes={
                "name": "Dining OVHD",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=10,
            attributes={
                "name": "Galley",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState()
        ),
        LightDimmable(
            instance=11,
            attributes={
                "name": "Galley OVHD",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=12,
            attributes={
                "name": "Wardrobe",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=13,
            attributes={
                "name": "Bath Light",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=14,
            attributes={
                "name": "Bed Accent",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=15,
            attributes={
                "name": "Compartment",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=16,
            attributes={
                "name": "Drawer and Front OVHD",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            state=LightDimmableState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightDimmable(
            instance=17,
            attributes={
                "name": "Awning Light",
                "description": "Awning light",
                "type": "RVC__DC_DIMMER"
            },
            state=LightDimmableState(),
            # This light belongs to Awning instance 1
            relatedComponents=[
                {
                    "componentTypeId": AwningRvc().componentId,
                    "instance": 1
                }
            ],        # ['movables.aw1', ],
            optionCodes='52N',
            meta={
                'manufacturer': 'CareFree',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LightGroup(
            instance=0,
            attributes={
                "name": "Master",
                'description': 'Master light group',
                "type": "LG_MASTER"
            },
            state=LightGroupState()
        ),
        LightGroup(
            instance=1,
            attributes={
                "name": "Preset 1",
                'description': 'User Preset 1',
                "type": "LG_PRESET"
            },
            state=LightGroupState()
        ),
        LightGroup(
            instance=2,
            attributes={
                "name": "Preset 2",
                'description': 'User Preset 2',
                "type": "LG_PRESET"
            },
            state=LightGroupState()
        ),
        LightGroup(
            instance=3,
            attributes={
                "name": "Preset 3",
                'description': 'User Preset 3',
                "type": "LG_PRESET"
            },
            state=LightGroupState()
        ),
        AwningRvc(
            instance=1,
            attributes={
                "name": "Awning",
                "description": "Awning - RVC"
            },
            state=AwningRvcState(),
            optionCodes='52N',
            # Lighting for this awning is handled in lz17
            relatedComponents=[
                {
                    "componentTypeId": LightDimmable().componentId,
                    "instance": 17
                }
            ],
            meta={
                'manufacturer': 'Carefree',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        # Awning light not handled as its own component
        # {
        #     "componentTypeId": "movables.al_rvc",
        #     "instance": 1,
        #     "attributes": {
        #         "name": "Awning Light",
        #         "description": "",
        #         "type": "RVC"
        #     },
        #     "filters": {
        #         "optionCode": "52N"
        #     }
        # },
        LevelJacksRvc(
            instance=1,
            attributes={
                "name": "Leveling Jacks",
                "description": "Leveling Jacks - RVC"
            },
            state=JackState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        # TODO: Figure out if we want to list the murphy bed at all and possible introduce an attribute
        # To say it is not controlled by WinnConnect
        # {
        #     "componentTypeId": "movable.mb_simple",
        #     "instance": 1,
        #     "attributes": {
        #         "name": "Murphy Bed - Powered",
        #         "description": ""
        #     }
        # },
        SlideoutBasic(
            instance=1,
            attributes={
                'name': 'Living Room',
                'description': 'Main Slideout'
            },
            state=SlideoutBasicState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),

        # TODO: Fix water tanks
        WaterTankDefault(
            instance=1,
            attributes={
                "name": "Fresh Water",
                "description": "Fresh Water",
                "type": "FRESH",
                "cap": 60,
                "unit": "G",
                "uiclass": "FreshTankLevel"
            },
            state=WaterTankState(),
            relatedComponents=[
                {
                    "componentTypeId": WaterPumpDefault(state=WaterPumpState()).componentId,
                    "instance": 1
                }
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        WaterTankDefault(
            instance=2,
            attributes={
                "name": "Gray Water",
                "description": "Gray Water",
                "type": "GREY",
                "cap": 60,
                "unit": "G",
                "uiclass": "GreyTankLevel"
            },
            state=WaterTankState(),
            relatedComponents=[
                {
                    "componentTypeId": TankHeatingPad(state=TankHeatingPadState()).componentId,
                    "instance": 2
                }
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        WaterTankDefault(
            instance=3,
            attributes={
                "name": "Black Water",
                "description": "Black Water",
                "type": "BLACK",
                "cap": 60,
                "unit": "G",
                "uiclass": "BlackTankLevel"
            },
            state=WaterTankState(),
            relatedComponents=[
                {
                    "componentTypeId": TankHeatingPad(state=TankHeatingPadState()).componentId,
                    "instance": 3
                }
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        WaterPumpDefault(
            instance=1,
            attributes={
                "name": "Fresh Water Pump",
                "description": "Fresh Water Pump",
                "type": "FRESH"
            },
            # Pump is related to Fresh water tank, instance 1 of wt in this case
            relatedComponents=[
                {
                    "componentTypeId": WaterTankDefault(state=WaterTankState()).componentId,
                    "instance": 1
                }
            ],
            state=WaterPumpState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        WaterHeaterRvc(
            instance=1,
            attributes={
                "name": "Water Heater",
                "description": "Water Heater - RVC"
            },
            # state=WaterHeaterRvcState(),
            meta={
                'manufacturer': 'Truma',
                'model': 'AquaGo',
                'part': ''
            },
            relatedComponents=[
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": 1
                }
            ]
        ),
        TankHeatingPad(
            instance=2,
            attributes={
                "name": "Tank Heating Pad - Gray",
                "description": "Water Tank Heating Pad",
                "type": "GREY"
            },
            # state=TankHeatingPadState(),
            # This heats the gray tank
            relatedComponents=[
                {
                    "componentTypeId": WaterTankDefault(state=WaterTankState()).componentId,
                    "instance": 2
                }
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        TankHeatingPad(
            instance=3,
            attributes={
                "name": "Tank Heating Pad - Black",
                "description": "Water Tank Heating Pad",
                "type": "BLACK"
            },
            # state=TankHeatingPadState(),
            # This heats the black tank
            relatedComponents=[
                {
                    "componentTypeId": WaterTankDefault(state=WaterTankState()).componentId,
                    "instance": 3
                }
            ],
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        ),
        LockoutBasic(
            instance=EventValues.PARK_BRAKE_APPLIED,
            attributes={
                'name': "Park Brake Appleid",
                'description': 'Is the park brake currently released',
                'controllable': 'N'
            },
            state=LockoutState()
        ),
        LockoutBasic(
            instance=EventValues.IGNITION_ON,
            attributes={
                'name': "Ignition On State",
                'description': 'Is the ignition on',
                'controllable': 'N'
            },
            state=LockoutState()
        ),
        LockoutBasic(
            instance=EventValues.LOW_VOLTAGE,
            attributes={
                'name': "Low voltage on house battery ?????",
                'description': 'Might cause warnings or lockouts based on low voltage',
            },
            # state=LockoutState(),
            relatedComponents=[
                {
                    "componentTypeId": SlideoutBasic().componentId,
                    "instance": 1
                }
            ],
        ),
        LockoutBasic(
            instance=EventValues.NOT_IN_PARK,
            attributes={
                'name': "Vehicle Not in Park",
                'description': 'The indicator if the vehicle gear is currently park or anything else, might be drive, neutral etc.',
                'controllable': 'N'
            },
            state=LockoutState()
        ),
        LockoutBasic(
            instance=EventValues.LOAD_SHED_ACTIVE,
            attributes={
                'name': 'System in Load shedding',
                'description': 'System is currently applying load shedding. Generic status if anything is being shed.',
            },
            state=LockoutState()
        ),
        LockoutBasic(
            instance=EventValues.DECALC_WATERHEATER_LOCKOUT,
            attributes={
                'name': 'DeCalc status received from RCV WH',
                'description': 'The User is running a manual decalcification, we should not attempt to conrtrol the water heater',
            },
            state=LockoutState()
        )
    ]
}

model_definition['id'] = '{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan')
)

# Copy and override for the few changes to the Navion
alternate_model_definition = deepcopy(model_definition)
alternate_model_definition['seriesModel'] = '7054742'
alternate_model_definition['floorPlan'] = 'IM524NP'
alternate_model_definition['attributes']['seriesName'] = 'NAVION'

alternate_model_definition['id'] = '{}.{}.{}'.format(
    alternate_model_definition.get('deviceType'),
    alternate_model_definition.get('seriesModel'),
    alternate_model_definition.get('floorPlan')
)


config_definition = {
    "floorPlan": "",
    "componentGroup": "",
    "hal_options": [
        "52D",
        "31T",
        "52N",
        "29J"
    ],
    "climate_components": {
        "rf1": {
            "componentTypeId": "climate.rf_basic",
            "instance": 1,
            "attributes": {
                "name": "Refrigerator ",
                "description": "Refrigerator Temp"
            }
        },
        "rf2": {
            "componentTypeId": "climate.rf_basic",
            "instance": 2,
            "attributes": {
                "name": "Freezer ",
                "description": "Freezer Temp"
            }
        },

        "he1":{
            "componentTypeId": "climate.he_basic",
            "instance": 1,
            "attributes": {
                "name": "Heater (LP Furnace)"
            }
        },
        "he2": {
            "componentTypeId": "climate.he_heatpump",
            "instance": 2,
            "attributes": {
                "name": "GE AC Heatpump"
            },
            "filters": {
                "optionCodes": [
                    "29J"
                ],
                "relatedComponents": [
                    "ac1"
                ]
            }
        },
        "th1": {
            "componentTypeId": "climate.th_virtual",
            "instance": 1,
            "attributes": {
                "name": "Thermostat",
                "description": "Indoor HVAC control Thermostat"
            }
        },
        "th2": {
            "componentTypeId": "climate.th_outdoor",
            "instance": 2,
            "attributes": {
                "name": "Outdoor",
                "description": "Outdoor Thermostat"
            }
        }
    },
    "climate_defaults": {
        "zone_1__ac_1": {
            "onOff": 0,
            "fanSpd": 0
        },
        "fan_mapping": {
            "1": 4,
            "2": 4,
            "3": 3,
            "4": 4
        },
        "he1": {
            "onOff": 0
        },
        "initial_state": {
            "zone_1__fan_1": {
                "compressor": 0,
                "fanSpd": 0
            },
            "zone_1__fan_2": {
                "direction": 529,
                "dome": 0,
                "onOff": 0,
                "fanSpd": 0
            },
            "zone_1__fan_3": {
                "direction": 529,
                "dome": 0,
                "onOff": 0,
                "fanSpd": 0
            },
            "he1": {
                "onOff": 0
            },
            "zone_1__onOff": 1,
            "zone_1_climate_mode": 519
        },
        "max_temp_set": 35.0,
        "min_temp_set": 15.6,
        "num_zones": 1,
        "zone_1": {
            "hvac_mode": 519,
            "set_temperature": 22.8,
            "set_temperature_AUTO": 21.1,
            "set_temperature_COOL": 25.6,
            "set_temperature_HEAT": 20.0
        },
        "climate_algo_enabled": 1
    },
    "energy_mapping": {
        "generator": {
            "operating": 0
        },
        "battery__1__soc": None,
        "battery__1__soh": None,
        "battery__1__capacity_remaining": None,
        "battery__1__voltage": None,
        "battery__1__current": None,
        "battery__1__charging": None,
        "battery__1__remaining_runtime_minutes": None,
        "bms__1__charge_lvl": 0,
        "bms__1__temp": None,
        "is_charging": None,
        "solar_active": None,

        "charger__1__voltage": None,

        "ei1": {
            "onOff": None,
            "load": None,
            "continuous_max_load": 2000,
            "overld": False,
            "overload_timer": 0
        },

        "solar__1__input_voltage": None,
        "solar__1__input_current": None,
        "solar__1__input_watts": None,

        "shore__1__lvl": None,
        "shore__1__lock": False
    },
    "movable_components": {
        "so1": {
            "componentTypeId": "movables.so_basic",
            "instance": 1,
            "attributes": {
                "name": "Bedroom",
                "description": "Make room for the Murphy Bed"
            }
        },
        "aw1": {
            "componentTypeId": "movables.aw_rvc",
            "instance": 1,
            "attributes": {
                "name": "Awning",
                "description": "Adjustable cover for the entance side."
            }
        },
        "al1": {
            "componentTypeId": "movables.al_light_rvc",
            "instance": 1,
            "attributes": {
                "name": "Awning light",
                "description": "Adjustable cover light."
            }
        },
        "lj1": {
            "componentTypeId": "movables.lj_rvc",
            "instance": 1,
            "attributes": {
                "name": "Leveling Jacks",
                "description": "For leveling the RV."
            }
        }
    },
    "movable_mapping": {
        "awning": {
            "mode": 526,
            "pctExt": None,
            "light": {
                "onOff": 0,
                "brt": 75
            },
            "awning__1__motion": "Data Invalid",
            "awning__1__position": "Data Invalid"
        },
        "jacks": {
            "mode": 564
        }
    },
    "lighting_mapping": {
        "default_on_lighting_zones": [7,11,16],
        "zones": [
            {
                "id": 2,
                "type": "SIMPLE_DIM",
                "name": "Bed 1 OVHD",
                "description": "",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 3,
                "type": "SIMPLE_DIM",
                "name": "Bed 2 OVHD",
                "description": "",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 4,
                "type": "SIMPLE_DIM",
                "name": "Bed Accent",
                "description": "",
                "code": "lz",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 6,
                "type": "SIMPLE_DIM",
                "name": "Service",
                "description": "",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 7,
                "type": "SIMPLE_DIM",
                "name": " Porch",
                "description": "",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 8,
                "type": "SIMPLE_DIM",
                "name": "Lounge",
                "description": "",
                "code": "lz",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 9,
                "type": "SIMPLE_DIM",
                "name": "Dining OVHD",
                "description": "Main ceiling lights",
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 10,
                "type": "SIMPLE_DIM",
                "name": "Galley ",
                "description": "",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 11,
                "type": "SIMPLE_DIM",
                "name": "Galley OVHD",
                "description": "",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 12,
                "type": "SIMPLE_DIM",
                "name": "Wardrobe",
                "description": "",
                "code": "lz",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 13,
                "type": "SIMPLE_DIM",
                "name": "Bath light",
                "description": "Main ceiling lights",
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 14,
                "type": "SIMPLE_DIM",
                "name": "Bath Accent",
                "description": "",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 15,
                "type": "SIMPLE_DIM",
                "name": " Compartment Lights",
                "description": "",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 16,
                "type": "SIMPLE_DIM",
                "name": "Drawer and Front OVHD",
                "description": "",
                "code": "lz",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 17,
                "type": "SIMPLE_DIM",
                "name": "Awning",
                "description": "Awning light associated with Awning instance 1",
                "code": "lz",
                "channel": 1,
                "controller_type": "RVC",
                "controller": "CAN",
                "state": {"brt": 100, "onOff": 0}
            }
        ]
    },
    "energy_components": {
        "bm1": {
            "componentTypeId": "energy.bm_basic",
            "instance": 1,
            "attributes": {
                "name": "Battery Management",
                "description": "Status for the Battery"
            }
        }
    },
    "features_components": {
        "pm1": {
            "componentTypeId": "features.pm_basic",
            "instance": 1,
            "attributes": {
                "name": "Pet Minder",
                "description": "Petminder State Reporting"
            }
        }
    },
    "communication_components": {
        "ce1": {
            "componentTypeId": "communication.ce_cradlepoint",
            "instance": 1,
            "attributes": {
                "name": "Network Router",
                "description": "Router State Reporting"
            }
        }
    },
    "electrical_mapping": {
        "ac": {},
        "dc": {
            "5": {
                "description": "Controls power to the Theater Seat",
                "id": 5,
                "long": "C6.5-7 Theater Seat",
                "rvOutputId": 5,
                "short": "TheaterSeat",
                "category": "electrical"
            },
            "6": {
                "description": "Controls power to ITC lighting controller 1 20DC",
                "id": 6,
                "long": "C6.1-4 Lighting controller 1 (Z1 - Z16)",
                "rvOutputId": 1,
                "short": "LightController",
                "category": "electrical"
            },
            "7": {
                "description": "Door Lock/Unlock",
                "id": 7,
                "long": "C2.9/1 Door Lock/Unlock",
                "rvOutputId": 161,
                "short": "DoorLockUnlock",
                "category": "vehicle",
                "circuitType": "H-BRIDGE",
                "widget": "deadman",
                "backText": "Lock",
                "forwardText": "Unlock"
            },
            "8": {
                "description": "Provides power to the furnace.",
                "id": 8,
                "long": "C13.4 Furnace",
                "rvOutputId": 130,
                "short": "Furnace",
                "category": "climate"
            },
            "9": {
                "description": "Provides power to the gray tank heater",
                "id": 9,
                "long": "C13.2 Gray Water Tank Heater",
                "rvOutputId": 104,
                "short": "GreyTankHeater",
                "category": "watersystems"
            },
            "10": {
                "description": "Provides power to the black water tank heater.",
                "id": 10,
                "long": "C13.3 Black Water tank heater.",
                "rvOutputId": 129,
                "short": "BlackTankHeater",
                "category": "watersystems"
            },
            "11": {
                "description": "Turns power to Water Pump on/off",
                "id": 11,
                "long": "C13.1 Water Pump Power on/off",
                "rvOutputId": 103,
                "short": "Water Pump",
                "category": "watersystems",
                "code": "wp",
                "instance": 1
            },
            "12": {
                "description": "Provides power to the RooFFan.",
                "id": 12,
                "long": "C13.5 Power to both Roof Fans",
                "rvOutputId": 131,
                "short": "RooFFan",
                "category": "climate"
            },
            "13": {
                "description": "H - Bridge 01 Provides power to the Murphy Bed",
                "id": 13,
                "long": "Power to the Murphy Bed",
                "rvOutputId": 165,
                "short": "MurphyBed",
                "category": "movables",
                "circuitType": "H-BRIDGE",
                "widget": "deadman",
                "backText": "Down",
                "forwardText": "Up"
            },
            "14": {
                "description": "Provides Power to Water Heater",
                "id": 14,
                "long": "C6.8-10 Water Heater",
                "rvOutputId": 14,
                "short": "WaterHeater",
                "category": "watersystems",
                "code": "wh",
                "instance": 1
            },
            "15": {
                "description": "Controls Furnace Trigger, that allows burn off cycke to conclude",
                "id": 15,
                "long": "C12.1 Furnace Trigger",
                "rvOutputId": 15,
                "short": "FurnaceTrigger",
                "category": "climate"
            },
            "16": {
                "description": "Sets General Power JJT",
                "id": 16,
                "long": "Gen Power JJT",
                "rvOutputId": 65,
                "short": "GenPowerJJT",
                "category": "electrical"
            },
            "17": {
                "description": "Sets Refrigerator Power",
                "id": 17,
                "long": "Refrigerator Power",
                "rvOutputId": 8,
                "short": "Refrigerator",
                "category": "electrical"
            },
            "18": {
            "description": "Run Slideout Retract",
            "id": 18,
            "long":"C12.7 Run Slideout Retract",
                "rvOutputId": 100,
                "short": "SlideoutRetract",
                "category": "movables",
                "widget": "button",
                "code": "so",
                "instance": 1
            },
            "19": {
                "description": "Sets General Power JE",
                "id": 19,
                "long": "General Power JE",
                "rvOutputId": 35,
                "short": "GenPowerJE",
                "category": "electrical"
            },
            "20": {
                "description": "Run Slideout Extend",
                "id": 20,
                "long": "C12.8 Run Slideout Extend",
                "rvOutputId": 99,
                "short": "SlideoutExtend",
                "category": "movables",
                "widget": "button",
                "code": "so",
                "instance": 1
            },
            "22": {
                "description": "HMI - Display",
                "id": 22,
                "long": "HMI - Display",
                "rvOutputId": 68,
                "short": "HMIPower",
                "category": "electrical"
            },
            "23": {
                "description": "Microwave Load Shed Relay",
                "id": 23,
                "long": "C12.4 Microwave Load Shed Relay",
                "rvOutputId": 72,
                "short": "LoadShedMW",
                "category": "electrical"
            },
            "24": {
                "description": "Range Load Shed Relay",
                "id": 24,
                "long": "C12.5 Range Load Shed Relay",
                "rvOutputId": 97,
                "short": "LoadShedRng",
                "category": "electrical"
            },
            "25": {
                "description": "Sets General Power JD",
                "id": 25,
                "long": "General Power JD",
                "rvOutputId": 38,
                "short": "GenPowerJD",
                "category": "electrical"
            },
             "26": {
                "description": "Parking Brake Ground to Slide Controller CFS",
                "id": 26,
                "long":"C14.6 Parking Brake Signal CFS",
                "rvOutputId": 164,
                "short": "ParkingCFS",
                "category": "movable"
            },
            "27": {
                "description": "LP Generator Start",
                "id": 27,
                "long":"C2.10/2 LP Gen Start",
                "rvOutputId": 162,
                "short": "LPGenStart",
                "category": "energy"
            },
            "28": {
                "description": "LP Generator Stop",
                "id": 28,
                "long":"C2.13/5 LP Gen Stop",
                "rvOutputId": 163,
                "short": "LPGenStop",
                "category": "energy"
            }
        },
        "switches": {
            "bank_4": {
                "1": {
                    "last_modified": None,
                    "onOff": None
                },
                "2": {
                    "last_modified": None,
                    "onOff": None
                },
                "3": {
                    "last_modified": None,
                    "onOff": None
                },
                "4": {
                    "last_modified": None,
                    "onOff": None
                },
                "5": {
                    "last_modified": None,
                    "onOff": None
                },
                "6": {
                    "last_modified": None,
                    "onOff": None
                },
                "7": {
                    "last_modified": None,
                    "onOff": None
                },
                "8": {
                    "last_modified": None,
                    "onOff": None
                }
            }
        },

        "KEYPAD_CONTROLS": {
            "5": {
                "Name": "Porch",
                "zone_id": "7"
            },
            "6": {
                "Name": "Awning On",
                "zone_id": "17"
            },
            "7": {
                "Name": "Lounge",
                "zone_id": "8"
            },
            "8": {
                "Name": "Compartment",
                "zone_id": "15"
            },
            "9": {
                "Name": "All On",
                "action": "hal_action",
                "category": "lighting",
                "function": "all_on",
                "params": {"onOff": 1}
            },
            "10": {
                "Name": "All Off",
                "action": "hal_action",
                "category": "lighting",
                "function": "all_off",
                "params": {"onOff": 0}
            }
        },
        "SI_CONTROLS": {
            "4": {
                "Name": "Front Bed OVHD",
                "Comment": "Input 2 # Momentary",
                "zone_id": 2,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/2",
                "params": {"$onOff": "int"}
            },
            "6": {    "Name": "Input 3",
                "Comment": "READ_BED OVHD - Momentary",
                "zone_id": 3,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/2",
                "params": {"$onOff": "int"}
            },
            "8": {    "Name": "Input 4",
                "Comment": "ACCENT_COACH - Momentary",
                "zone_id": 4,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/2",
                "params": {"$onOff": "int"}
            },
            "10": {   "Name": "Input 5",
                "Comment": "BED_LIGHT Accent - Momentary",
                "zone_id": 4,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/2",
                "params": {"$onOff": "int"}
            },
            "12": {   "Name": "Input 6",
                "Comment": "SERVICE_LIGHT - Latching",
                "zone_id": 6,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/2",
                "params": {"$onOff": "int"}
            }
        },

        "RV1_CONTROLS": {
            "14": {  "Name": "Input 14",
                "Comment": "Galley Light - Momentary",
                "zone_id": 10,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/4",
                "params": {"$onOff": "int"}
            },
            "16": {  "Name": "Input 14",
                "Comment": "Galley OVHD Light - Latching",
                "zone_id": 11,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/4",
                "params": {"$onOff": "int"}
            },
            "12": {  "Name": "Input 12",
                "Comment": "Dining OVHD Light - Momentary",
                "zone_id": 9,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/3",
                "params": {"$onOff": "int"}
            },
            "20": { "Name": "Input 20",
                "Comment": "Bath Accent Light - Momentary",
                "zone_id": 14,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/3",
                "params": {"$onOff": "int"}
            },
            "22": {  "Name": "Input 22",
                "Comment": "Wardrobe Light - Momentary",
                "zone_id": 12,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/3",
                "params": {"$onOff": "int"}
            },
            "10": {  "Name": "Input 10",
                "Comment": "Bath  Light - Momentary",
                "zone_id": 13,
                "action": "api_call",
                "type": "PUT",
                "href": "http://127.0.0.1:8000/api/lighting/zone/4",
                "params": {"$onOff": "int"}
            }
        },
        "TOGGLE_ZONES": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17"]
    },
    "alert_items": ALERTS,
    "hal_categories": {
        "climate": "modules.hardware._500.hw_climate",
        "electrical": "modules.hardware._500.hw_electrical",
        "energy": "modules.hardware._500.hw_energy",
        "lighting": "modules.hardware._500.hw_lighting",
        "vehicle": "modules.hardware._500.hw_vehicle",
        "watersystems": "modules.hardware._500.hw_watersystems",
        "communication": "modules.hardware.wineguard.hw_wineguard",
        "movables": "modules.hardware.hw_movables",
        "system": "modules.hardware.hw_system",
        "features": "modules.sw_features"
    },
    "can_mapping": {
        "fluid_level": "watersystems",
        "lighting_broadcast": "lighting",

        "heartbeat": "electrical",
        "rvswitch": "electrical",
        "rvoutput": "electrical",

        "roof_fan_status_1": "climate",
        "ambient_temperature": "climate",
        "thermostat_ambient_status": "climate",

        "dc_source_status_1": "energy",
        "dc_source_status_2": "energy",
        "dc_source_status_3": "energy",
        "battery_status": "energy",
        "prop_bms_status_6": "energy",
        "prop_module_status_1": "energy",

        "inverter_ac_status_1": "energy",
        "inverter_status": "energy",
        "charger_ac_status_1": "energy",
        "charger_ac_status_2": "energy",
        "charger_status": "energy",
        "charger_status_2": "energy",
        "solar_controller_status": "energy",

        "vehicle_status_1": "vehicle",
        "vehicle_status_2": "vehicle",
        "state_of_charge": "vehicle",
        "dc_charging_state": "vehicle",
        "pb_park_brake": "vehicle",
        "tr_transmission_range": "vehicle",
        "odo_odometer": "vehicle",
        "aat_ambient_air_temperature": "vehicle",
        "vin_response": "vehicle",

        "dc_dimmer_command_2": "electrical",

        "waterheater_status": "watersystems",
        "waterheater_status_2": "watersystems"
    }
}


config_definition['componentGroup'] = '{}.{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan'),
    "componentGroup"
)
config_definition['floorPlan'] = model_definition.get('floorPlan')


# Copy and override for the few changes to the Navion
alternate_config_definition = deepcopy(config_definition)
alternate_config_definition['componentGroup'] = '{}.{}.{}.{}'.format(
    alternate_model_definition.get('deviceType'),
    alternate_model_definition.get('seriesModel'),
    alternate_model_definition.get('floorPlan'),
    "componentGroup"
)
alternate_config_definition['floorPlan'] = alternate_model_definition.get('floorPlan')
