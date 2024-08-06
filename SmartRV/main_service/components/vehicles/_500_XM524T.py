'''Model definition for the WM524T/IM524T'''

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
    "seriesModel": "1054042",   # TODO: Confirm with Rick
    # floorPlan is the specific flooplan, a floorplan separates variants of the same vehicle
    "floorPlan": "WM524T",
    # attributes can be used as Meta information that can be propagated to the UI as needed
    "attributes": {
        "name": 'VIEW',
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
    # generator_ prefixed keys shall be dropped after generation
    'generator_fields': {
        # Model years will generate a dedicated componentGroup for an unchanged floorplan for
        # each year and revision combination
        'modelYears': {
            '2024': {
                'revisions': [2,]
            },
            '2025': {
                'revisions': [0, 1]
            }
        }
    },
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
                'description': 'Mercedes Sprinter Chassis with PSM module',
                'controllable': 'N'
            },
            state=VehicleSprinterState(),
            meta={
                'manufacturer': 'Mercedes Benz - TrucksX',
                'model': 'Sprinter',
                'part': ''
            }
        ),
        Thermostat(
            instance=1,
            state=ThermostatState(),
            attributes={
                'name': 'Thermostat',
                'description': 'Virtual Thermostat',
                'type': 'MAIN'
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
            meta={
                'manufacturer': 'TriMark',
                'model': '36517-01',
                'part': 'N/A'
            }
        ),
        HeaterBasic(
            instance=1,
            attributes={
                "name": "Heater (LP Furnace)",
                'description': 'Dometic LP Furnace'
            },
            meta={
                'manufacturer': 'Dometic Corporation',
                'model': '20298',
                'part': 'DFMD25'
            }

        ),
        # RefrigeratorBasic(
        #     instance=1,
        #     attributes={
        #         'name': 'Refrigerator',
        #         'description': 'Dometic fridge ?',
        #         'type': 'REFRIGERATOR'
        #     },
        #     meta={
        #         'manufacturer': '',
        #         'model': '',
        #         'part': ''
        #     }
        # ),
        # RefrigeratorBasic(
        #     instance=2,
        #     attributes={
        #         'name': 'Freezer',
        #         'description': 'Freezer compartment',
        #         'type': 'FREEZER'
        #     },
        #     meta={
        #         'manufacturer': '',
        #         'model': '',
        #         'part': ''
        #     }
        # ),
        RoofFanAdvanced(
            instance=1,
            attributes={
                'name': 'Galley Vent',
                'description': 'Main Roof Fan'
            },
            meta={
                'manufacturer': 'Dometic',
                'model': 'FanTastic 5300',
                'part': 'FV5300HWUWD81-SP'
            }
        ),
        RoofFanAdvanced(
            instance=2,
            attributes={
                'name': 'Bathroom Vent',
                'description': 'Bath Roof Fan'
            },
            meta={
                'manufacturer': 'Dometic',
                'model': 'FanTastic 5300',
                'part': 'FV5300HWUWD81-SP'
            }
        ),
        AcRvcTruma(
            instance=1,
            attributes={
                "name": "Truma - Air Conditioning",
                "description": "Air conditioner option 291 - Truma"
            },
            optionCodes='291',
            meta={
                'manufacturer': 'Truma',
                'model': 'Aventa Comfort',
                'part': '000265395'
            },
            relatedComponents=[
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.LOAD_SHEDDING_AIR_CONDITIONER_ACTIVE
                },
            ]
        ),
        AcRvcGe(
            instance=1,
            attributes={
                "name": "GE - Air Conditioning",
                "description": "Air conditioner option 29J - GE with Heatpump"
            },
            optionCodes='29J',
            relatedComponents=[
                {
                    "componentTypeId": HeaterACHeatPump().componentId,
                    "instance": 2
                },
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.LOAD_SHEDDING_AIR_CONDITIONER_ACTIVE
                },
            ],
            meta={
                'manufacturer': 'GE Appliances',
                'model': 'ARH15AAC',
                'part': ''
            }
        ),
        HeaterACHeatPump(
            instance=2,
            attributes={
                'name': 'GE AC Heatpump',
                'description': 'GE AC Heatpump Component'
            },
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
                },
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.LOAD_SHEDDING_AIR_CONDITIONER_ACTIVE
                },
            ],
            meta={
                'manufacturer': 'GE Appliances',
                'model': 'ARH15AAC',
                'part': ''
            }
        ),
        ThermostatOutdoor(
            instance=2,
            attributes={
                'name': 'Outdoor',
                'description': 'Outdoor Temp Sensor',
                'type': 'OUTDOOR'
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        NetworkRouter(
            instance=1,
            state=RouterState(),
            attributes={
                "name": "Cradlepoint - S700",
                'description': 'Connectivity Unit',
                'type': 'CRADLEPOINT-S700'
            },
            meta={
                'manufacturer': 'Cradlepoint',
                'model': 'S700',
                'part': ''
            }
        ),
        BatteryManagement(
            instance=1,
            attributes={
                'name': 'Battery Management',
                'description': 'BMS',
                'type': 'LITHIONICS',
                # 'batCnt': 1,
                'nominalVoltage': '12.8V',
                # 'maxCurrent': '',
                'minSoc': 10
            },
            meta={
                'manufacturer': 'Lithionics',
                'model': '74-221-UL',
                'part': ''
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
            relatedComponents=[
                {
                    "componentTypeId": BatteryManagement().componentId,
                    "instance": 1
                },
            ],
            meta={
                'manufacturer': 'Lithionics',
                'model': '74-221-UL',
                'part': ''
            }
        ),
        # BatteryPack(
        #     instance=1,
        #     attributes={
        #         'name': 'LITHIONICS IONGEN',    # TODO: Get the right name
        #         'type': 'LITHIONICS',
        #         'description': 'Defaul battery pack',
        #         'cap': '640AH'                       # TODO: Get the capacity and possible options
        #     },
        #     state=BatteryState(),
        #     relatedComponents=[
        #         {
        #             "componentTypeId": BatteryManagement(
        #                 state=BatteryMgmtState()).componentId,
        #             "instance": 1
        #         }
        #     ],
        #     # optionCodes="XXDOM",
        #     optionCodes="33W"
        # ),
        # BatteryPack(
        #     instance=2,
        #     attributes={
        #         'name': 'LITHIONICS IONGEN',    # TODO: Get the right name
        #         'type': 'LITHIONICS',
        #         'description': 'Defaul battery pack',
        #         'cap': '320AH'                       # TODO: Get the capacity and possible options
        #     },
        #     state=BatteryState(),
        #     relatedComponents=[
        #         {
        #             "componentTypeId": BatteryManagement(
        #                 state=BatteryMgmtState()).componentId,
        #             "instance": 1
        #         }
        #     ],
        #     optionCodes="33W"
        # ),
        InverterAdvanced(
            instance=1,
            attributes={
                "name": "Inverter",
                'description': 'Inverter Component',
                "type": "RVC",      # Still needed ?
                "state.maxLoad": 2000
            },
            meta={
                'manufacturer': 'XANTREX',
                'model': 'Freedom XC Pro 2000',
                'part': ''
            }
        ),
        ChargerAdvanced(
            instance=1,
            attributes={
                'name': 'Charger',
                'description': 'Charger in XANTREX',
                'defaultBreakerSizeA': 15,   # Amps for break size,
                'defaultChargeCurrentA': 100    # Amps for charger
            }
        ),
        EnergyConsumer(
            instance=1,
            attributes={
                'name': 'AC - Total',
                'description': 'Energy Consumer for AC',
                'type': 'AC',
                'acc': 'MEASURED'
            }
        ),
        EnergyConsumer(
            instance=2,
            attributes={
                'name': 'DC - Total',
                'description': 'Energy Consumer for DC',
                'type': 'DC',
                'acc': 'MEASURED'
            }
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
                'name': 'Solar',
                'description': 'Solar Controller Source',
                'type': 'SOLAR'
            },
            meta={
                'manufacturer': 'XANTREX',
                'model': '710-3024-01',
                'part': ''
            }
        ),
        PowerSourceShore(
            instance=2,
            attributes={
                'name': 'Shore',
                'description': 'Shore Power Source',
                'type': 'SHORE'
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            },
            relatedComponents=[
                {
                    "componentTypeId": PowerSourceGenerator().componentId,
                    "instance": 4
                },
            ]
        ),
        PowerSourceAlternator(
            instance=3,
            attributes={
                'name': 'Alternator',
                'description': 'Alternator Power Source',
                'type': 'ALTERNATOR'
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        PowerSourceGenerator(
            instance=4,
            attributes={
                'name': 'Generator',
                'description': 'Generator Power Source'
            },
            meta={
                'manufacturer': 'RVMP',
                'model': '4000K LP/GAS',
                'part': 'N/A'
            },
            optionCodes='52D',
            relatedComponents=[
                {
                    "componentTypeId": GeneratorPropane().componentId,
                    "instance": 1
                },
                {
                    "componentTypeId": PowerSourceShore().componentId,
                    "instance": 1
                },
            ]
        ),
        FuelTank(
            instance=1,
            state=FuelTankState(),
            attributes={
                'name': 'Liquid Propane',
                'type': 'LP',
                'description': 'Liquid Propane',
                'cap': 12.2 * 0.8,
                'unit': 'G',
                'controllable': 'N',
                'state.minLvl': 0.0,
                'state.maxLvl': 100.0
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            },
            relatedComponents=[
                # Removed per user will frequently have aux tank for longer stays.
                # Property disabled was introduced that can be used to allow this lockout.
                # TODO: Get UX for this
                # {
                #     "componentTypeId": LockoutBasic().componentId,
                #     "instance": EventValues.FUEL_EMPTY
                # },
                {
                    "componentTypeId": GeneratorPropane().componentId,
                    "instance": 1
                }
            ],
        ),
        GeneratorPropane(
            instance=1,
            attributes={
                'name': 'Generator',
                'description': 'RVMP LP Generator',
                'circuitId': '4-13'
            },
            optionCodes='52D',
            meta={
                'manufacturer': 'RVMP',
                'model': '4000K LP/GAS',
                'part': ''
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
        # GeneratorDiesel(
        #     instance=1,
        #     attributes={
        #         'name': 'Generator',
        #         'description': 'Onan Diesel Generator'
        #     },
        #     optionCodes='33F',
        #     meta={
        #         'manufacturer': '',
        #         'model': '',
        #         'part': ''
        #     }
        # ),
        LightDimmable(
            instance=1,
            attributes={
                'name': 'Front Bunk',
                'description': 'Dimmable Light Zone',
                'type': 'DIM__ITC_CHANNEL',

            },
            optionCodes='31T',
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=2,
            attributes={
                'name': 'Front Bed OVHD',
                'description': 'Dimmable Light Zone',
                'type': 'DIM__ITC_CHANNEL',

            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=3,
            attributes={
                'name': 'Rear Bed OVHD',
                'description': 'Dimmable Light Zone',
                'type': 'DIM__ITC_CHANNEL',

            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=4,
            attributes={
                "name": "Accent",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=5,
            attributes={
                "name": "Bed",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            optionCodes='-31T',
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=5,
            attributes={
                "name": "Couch",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            optionCodes='31T',
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=6,
            attributes={
                "name": "Service",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=7,
            attributes={
                "name": "Porch",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL",
                'exterior': True,
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=8,
            attributes={
               "name": "Lounge",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=9,
            attributes={
                "name": "Dining",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=10,
            attributes={
                "name": "Galley",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=11,
            attributes={
                "name": "Galley OVHD",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=12,
            attributes={
                "name": "Wardrobe",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=13,
            attributes={
                "name": "Bath",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=14,
            attributes={
                "name": "Bath Accent",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL"
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=15,
            attributes={
                "name": "Compartment",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL",
                "hidden": False,         # Hidden hides them from main lighting view
                "autoOn": True          # Future to be used when first init of the HW controllers
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=16,
            attributes={
                "name": "Drawer and Front OVHD",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL",
                "hidden": True,
                "autoOn": True
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightDimmable(
            instance=17,
            attributes={
                "name": "Awning Light",
                "description": "Awning light",
                'exterior': True,
                "type": "RVC__DC_DIMMER",
                "canInstance": 1,
                'state.brt': 100
            },
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
                'model': 'DRCMoLed',
                'part': ''
            }
        ),
        SmartLightGroup(
            instance=0,
            attributes={
                "name": "Smarttoggle",
                'description': 'Smart light group',
                "type": "LG_SMART"
            }
        ),
        SmartLightGroup(
            instance=101,
            attributes={
                "name": "All Lights",
                'description': 'Smart lighting group for all lights',
                "type": "LG_ALL"
            }
        ),
        LightGroup(
            instance=1,
            attributes={
                "name": "Preset 1",
                'description': 'User Preset 1',
                "type": "LG_PRESET"
            }
        ),
        LightGroup(
            instance=2,
            attributes={
                "name": "Preset 2",
                'description': 'User Preset 2',
                "type": "LG_PRESET"
            }
        ),
        LightGroup(
            instance=3,
            attributes={
                "name": "Preset 3",
                'description': 'User Preset 3',
                "type": "LG_PRESET"
            }
        ),
        LightGroup(
            instance=99,
            attributes={
                "name": "Interior",
                'description': 'Interior light group',
                "type": "LG_INTERIOR"
            }
        ),
        LightGroup(
            instance=100,
            attributes={
                "name": "Exterior",
                'description': 'Exterior light group',
                "type": "LG_EXTERIOR"
            }
        ),
        AwningRvc(
            instance=1,
            attributes={
                "name": "Awning",
                "description": "Awning - RVC"
            },
            optionCodes='52N',
            # Lighting for this awning is handled in lz17
            relatedComponents=[
                {
                    "componentTypeId": LightDimmable().componentId,
                    "instance": 17
                },
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.IGNITION_ON
                }
            ],
            meta={
                'manufacturer': 'CareFree of Colorado',
                # 'model': 'DRCHub',
                # 'part': 'R002039'
                'model': 'DRCHub / Awning',
                'part': 'R002039 / IJ1926EJV8LL'
            }
        ),
        # No level jacks that are CAN controllable present
        # LevelJacksRvc(
        #     instance=1,
        #     attributes={
        #         "name": "Leveling Jack",
        #         "description": "Leveling Jackss - RVC"
        #     },
        #     meta={
        #         'manufacturer': '',
        #         'model': '',
        #         'part': ''
        #     }
        # ),
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
            meta={
                'manufacturer': 'Lippert',
                'model': '700156',
                'part': '000235616'
            },
            relatedComponents=[
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.PSM_PB_IGN_COMBO
                },
            ]
        ),

        # TODO: Fix water tanks
        WaterTankDefault(
            instance=1,
            attributes={
                "name": "Fresh Water",
                "description": "Fresh Water",
                "type": "FRESH",
                "cap": 30,
                "unit": 'G',
                "uiclass": "FreshTankLevel",

                'state.vltgMin': 0.5,
                'state.vltgMax': 1.29
            },
            relatedComponents=[
                {
                    "componentTypeId": WaterPumpDefault().componentId,
                    "instance": 1
                }
            ],
            meta={
                'manufacturer': 'Winnebago',
                'model': '',
                'part': ''
            }
        ),
        WaterTankDefault(
            instance=2,
            attributes={
                "name": "Gray Water",
                "description": "Gray Water",
                "type": "GREY",
                "cap": 46,
                "unit": 'G',
                "uiclass": "GreyTankLevel",

                'state.vltgMin': 0.5,
                'state.vltgMax': 1.346
            },
            relatedComponents=[
                {
                    "componentTypeId": TankHeatingPad().componentId,
                    "instance": 2
                }
            ],
            meta={
                'manufacturer': 'Winnebago',
                'model': '',
                'part': ''
            }
        ),
        WaterTankDefault(
            instance=3,
            attributes={
                "name": "Black Water",
                "description": "Black Water",
                "type": "BLACK",
                "cap": 47,
                "unit": 'G',
                "uiclass": "BlackTankLevel",

                'state.vltgMin': 0.5,
                'state.vltgMax': 1.068
            },
            relatedComponents=[
                {
                    "componentTypeId": TankHeatingPad().componentId,
                    "instance": 3
                }
            ],
            meta={
                'manufacturer': 'Winnebago',
                'model': '',
                'part': ''
            }
        ),
        WaterPumpDefault(
            instance=1,
            attributes={
                "name": "Water Pump",
                "description": "Fresh Water Pump",
                "type": "FRESH",
                'controller': 'CZONE',
                'circuits': [11, ]
            },
            # Pump is related to Fresh water tank, instance 1 of wt in this case
            relatedComponents=[
                {
                    "componentTypeId": WaterTankDefault().componentId,
                    "instance": 1
                }
            ],
            meta={
                'manufacturer': 'SHURFLO',
                'model': '4008-101-F65',
                'part': 'N/A'  # No partnumber given
            }
        ),
        WaterHeaterRvc(
            instance=1,
            attributes={
                "name": "Water Heater",
                "description": "Water Heater - RVC"
            },
            relatedComponents=[
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.DECALC_WATERHEATER_LOCKOUT
                }
            ],
            meta={
                'manufacturer': 'TRUMA CORP (23351)',
                'model': '36022-81',
                'part': '000027742',
                'logo': 'Truma'
            }
        ),
        TankHeatingPad(
            instance=2,
            attributes={
                "name": "Tank Heating Pads",
                "description": "Water Tank Heating Pads",
                "type": "COMBO",
                "controller": "CZONE",
                "circuits": [9, 10]
            },
            # This heats the gray tank
            relatedComponents=[
                {
                    "componentTypeId": WaterTankDefault().componentId,
                    "instance": 2
                }
            ],
            meta={
                'manufacturer': 'Therma Heat',
                'model': 'SL-ST725G-16G',
                'part': '00167187'
            }
        ),
        # TankHeatingPad(
        #     instance=3,
        #     attributes={
        #         "name": "Tank Heating Pad - Black",
        #         "description": "Water Tank Heating Pad",
        #         "type": "BLACK",
        #         "controller": "CZONE",
        #         "circuit": 9
        #     },
        #     # This heats the black tank
        #     relatedComponents=[
        #         {
        #             "componentTypeId": WaterTankDefault().componentId,
        #             "instance": 3
        #         }
        #     ],
        #     meta={
        #         'manufacturer': 'Therma Heat',
        #         'model': 'SL-ST725G-16G',
        #         'part': '00167187'
        #     }
        # ),
        LockoutBasic(
            instance=EventValues.PARK_BRAKE_APPLIED,
            attributes={
                'name': "Park Brake Applied",
                'description': 'Is the park brake currently released',
                'defaultActive': False,
            },
            relatedComponents=[
                {
                    "componentTypeId": SlideoutBasic().componentId,
                    "instance": 1
                },
            ]
        ),
        LockoutBasic(
            instance=EventValues.IGNITION_ON,
            attributes={
                'name': "Ignition On State",
                'description': 'Is the ignition on',
                'defaultActive': True
            },
            relatedComponents=[
                {
                    "componentTypeId": SlideoutBasic().componentId,
                    "instance": 1
                },
            ]
        ),
        LockoutBasic(
            instance=EventValues.PSM_PB_IGN_COMBO,
            attributes={
                'name': "Ignition ON and Park Brake Applied",
                'description': 'Direct enabler line to the controller.',
                'defaultActive': False,
            },
            relatedComponents=[
                {
                    "componentTypeId": SlideoutBasic().componentId,
                    "instance": 1
                },
            ]
        ),
        LockoutBasic(
            instance=EventValues.LOW_VOLTAGE,
            attributes={
                'name': "Low voltage on house battery.",
                'description': 'Might cause warnings or lockouts based on low voltage'
            },
            relatedComponents=[
                {
                    "componentTypeId": SlideoutBasic().componentId,
                    "instance": 1
                },
                {
                    "componentTypeId": InverterAdvanced().componentId,
                    'instance': 1
                }
            ],
        ),
        LockoutBasic(
            instance=EventValues.NOT_IN_PARK,
            attributes={
                'name': "Vehicle Not in Park",
                'description': 'The indicator if the vehicle gear is currently park or anything else, might be drive, neutral etc.'
            }
        ),
        LockoutBasic(
            instance=EventValues.LOAD_SHED_ACTIVE,
            attributes={
                'name': 'System in Load shedding',
                'description': 'System is currently applying load shedding. Generic status if anything is being shed.',
                'defaultActive': False,
            }
        ),
        LockoutDynamic(
            instance=EventValues.GENERATOR_COOLDOWN,
            attributes={
                'name': 'Generator Cool Down Required',
                'description': 'Generator cannot be used currently as it is cooling down.',
                'uiMsgSubtext': 'Generator cool down, try again in {timer} seconds',
                'timerUnit': 'SECONDS',
                'defaultActive': False
            },
            state=LockoutDynamicState(
                active=False
            )
        ),
        LockoutDynamic(
            instance=EventValues.TIME_BASED_LOCKOUT_15_SECS,
            attributes={
                'name': 'Generator Wait Required',
                'description': 'Generator just changed state, wait 15 seconds to change again.',
                'uiMsgSubtext': 'Generator wait period, try again in {timer} seconds',
                'timerUnit': 'SECONDS',
                'defaultActive': False
            },
            state=LockoutDynamicState(
                active=False
            )
        ),
        LockoutBasic(
            instance=EventValues.FUEL_EMPTY,
            attributes={
                'name': 'Fuel Source is Empty',
                'description': 'Generator cannot be used as fuel source is empty.',
                'defaultActive': False
            },
            relatedComponents=[
                {
                    "componentTypeId": FuelTank().componentId,
                    "instance": 1
                }
            ],
        ),
        LockoutBasic(
            instance=EventValues.FUEL_LOW,
            attributes={
                'name': 'Fuel Source is low',
                'description': 'Generic lockout if fuel is below TBD threshold.',
                'defaultActive': False
            },
            relatedComponents=[
                {
                    "componentTypeId": FuelTank().componentId,
                    "instance": 1
                }
            ],
        ),
        LockoutBasic(
            instance=EventValues.DECALC_WATERHEATER_LOCKOUT,
            attributes={
                'name': 'Water heater currently in decalcification mode',
                'description': 'The User is running a manual decalcification, we should not attempt to conrtrol the water heater',
                'defaultActive': False,
            },
            relatedComponents=[
                {
                    "componentTypeId": WaterHeaterRvc().componentId,
                    "instance": 1
                }
            ]
        ),
        LockoutBasic(
            instance=EventValues.ENGINE_RUNNING,
            attributes={
                'name': "Engine Running State",
                'description': 'Is the engine running'
            }
        ),
        LockoutBasic(
            instance=EventValues.LOAD_SHEDDING_AIR_CONDITIONER_ACTIVE,
            attributes={
                'name': "Load Shedding State for Air Condition",
                'description': 'Is the Air Conditioner currently shed'
            }
        ),
        LockoutBasic(
            instance=EventValues.LOAD_SHEDDING_COOKTOP_ACTIVE,
            attributes={
                'name': "Load Shedding State for Cooktop",
                'description': 'Is the Cooktop is currently shed'
            }
        ),
        LockoutBasic(
            instance=EventValues.LOAD_SHEDDING_MICROWAVE_ACTIVE,
            attributes={
                'name': "Load Shedding State for Microwave",
                'description': 'Is the Microwave currently shed'
            }
        ),
        LockoutBasic(
            instance=EventValues.SERVICE_MODE_LOCKOUT,
            attributes={
                'name': "Service Mode Lockout",
                'description': 'Active if we are in service mode',
                'defaultActive': False
            }
        ),
        VehicleLocation(
            instance=2,
            attributes={
                'name': 'Vehicle Location',
                'description': 'Vehicle location and settings'
            },
            relatedComponents=[
                # Communication Component
            ]
        ),
        LoadShedding500(
            instance=0,
            attributes={
                'name': 'Load Shedding - Main',
                'description': 'Load Shedding Virtual Component for 524 series',
                'sheddableDevices': 'ac1, '
            },
            relatedComponents=[]
        ),
        LoadShedderComponent(
            instance=1,
            attributes={
                'name': 'Load Shedder - AC1',
                'description': 'Load Shedding for Air Conditioner',
                'priority': 10,
                'pwrRatingWatts': 1300
            },
            relatedComponents=[
                {
                    "componentTypeId": AcRvcGe().componentId,
                    "instance": 1
                },
                {
                    "componentTypeId": AcRvcTruma().componentId,
                    "instance": 1
                },
                {
                    "componentTypeId": HeaterACHeatPump().componentId,
                    "instance": 2
                },
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.LOAD_SHEDDING_AIR_CONDITIONER_ACTIVE
                }
            ]
        ),
        LoadShedderCircuit(
            instance=2,
            attributes={
                'name': 'Load Shedder - Cooktop',
                'description': 'Load Shedding for Cooktop Relay / Relay NC',
                'circuitId': 24,
                'priority': 20,
                'pwrRatingWatts': 1100
            },
            relatedComponents=[
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.LOAD_SHEDDING_COOKTOP_ACTIVE
                }
            ]
        ),
        LoadShedderCircuit(
            instance=3,
            attributes={
                'name': 'Load Shedder - Microwave',
                'description': 'Load Shedding for Microwave Relay',
                'circuitId': 23,
                'priority': 30,
                'pwrRatingWatts': 800
            },
            relatedComponents=[
                {
                    "componentTypeId": LockoutBasic().componentId,
                    "instance": EventValues.LOAD_SHEDDING_MICROWAVE_ACTIVE
                }
            ]
        ),
        ServiceSettings()
    ]
}

model_definition['components'].extend(
    get_base_features(model_definition)
)

model_definition['id'] = '{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan')
)

# Copy and override for the few changes to the Navion
alternate_model_definition = deepcopy(model_definition)
alternate_model_definition['seriesModel'] = '7054042'
alternate_model_definition['floorPlan'] = 'IM524T'
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
        "291"
    ],
    # "climate_components": {
    #     "rf1": {
    #         "componentTypeId": "climate.rf_basic",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Refrigerator ",
    #             "description": "Refrigerator Temp"
    #         }
    #     },
    #     "rf2": {
    #         "componentTypeId": "climate.rf_basic",
    #         "instance": 2,
    #         "attributes": {
    #             "name": "Freezer ",
    #             "description": "Freezer Temp"
    #         }
    #     },

    #     "he1": {
    #         "componentTypeId": "climate.he_basic",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Heater (LP Furnace)"
    #         }
    #     },
    #     "he2": {
    #         "componentTypeId": "climate.he_heatpump",
    #         "instance": 2,
    #         "attributes": {
    #             "name": "GE AC Heatpump"
    #         },
    #         "filters": {
    #             "optionCodes": [
    #                 "29J"
    #             ],
    #             "relatedComponents": [
    #                 "ac1"
    #             ]
    #         }
    #     },
    #     "th1": {
    #         "componentTypeId": "climate.th_virtual",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Thermostat",
    #             "description": "Indoor HVAC control Thermostat"
    #         }
    #     },
    #     "th2": {
    #         "componentTypeId": "climate.th_outdoor",
    #         "instance": 2,
    #         "attributes": {
    #             "name": "Outdoor",
    #             "description": "Outdoor Thermostat"
    #         }
    #     }
    # },
    # TODO: Review what can be used to initialize runtime data and use that instead of state
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
    # "energy_mapping": {
    #     "generator": {
    #         "operating": 0
    #     },
    #     "battery__1__soc": None,
    #     "battery__1__soh": None,
    #     "battery__1__capacity_remaining": None,
    #     "battery__1__voltage": None,
    #     "battery__1__current": None,
    #     "battery__1__charging": None,
    #     "battery__1__remaining_runtime_minutes": None,
    #     "bms__1__charge_lvl": 0,
    #     "bms__1__temp": None,
    #     "is_charging": None,
    #     "solar_active": None,

    #     "charger__1__voltage": None,

    #     "ei1": {
    #         "onOff": None,
    #         "load": None,
    #         "continuous_max_load": 2000,
    #         "overld": False,
    #         "overload_timer": 0
    #     },

    #     "solar__1__input_voltage": None,
    #     "solar__1__input_current": None,
    #     "solar__1__input_watts": None,

    #     "shore__1__lvl": None,
    #     "shore__1__lock": False
    # },
    # "movable_components": {
    #     "so1": {
    #         "componentTypeId": "movables.so_basic",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Bedroom",
    #             "description": "Make room for the Murphy Bed"
    #         }
    #     },
    #     "aw1": {
    #         "componentTypeId": "movables.aw_rvc",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Awning",
    #             "description": "Adjustable cover for the entance side."
    #         }
    #     },
    #     "al1": {
    #         "componentTypeId": "movables.al_light_rvc",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Awning light",
    #             "description": "Adjustable cover light."
    #         }
    #     },
    #     "lj1": {
    #         "componentTypeId": "movables.lj_rvc",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Leveling Jacks",
    #             "description": "For leveling the RV."
    #         }
    #     }
    # },
    # TODO: Is this specific config still needed ?
    "movable_mapping": {
        # "awning": {
        #     "mode": 526,
        #     "pctExt": None,
        #     "light": {
        #         "onOff": 0,
        #         "brt": 75
        #     },
        #     "awning__1__motion": "Data Invalid",
        #     "awning__1__position": "Data Invalid"
        # },
        # "jacks": {
        #     "mode": 564
        # }
    },

    "lighting_mapping": {
        "default_on_lighting_zones": [6, 7, 10, 11, 15, 16],        # TODO: Move that to the individual light that it should be default
        "zones": [
            {
                "id": 1,
                "type": "SIMPLE_DIM",
                # TODO: Get the name from the attribute, not from the config
                "name": "Zone1-R",
                # TODO: Get a description from the attribute, not from the config
                "description": "",
                # TODO: Verify code from config is not used anywhere
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
            },
            {
                "id": 2,
                "type": "SIMPLE_DIM",
                # TODO: Get the name from the attribute, not from the config
                "name": "Bed 1 OVHD",
                # TODO: Get a description from the attribute, not from the config
                "description": "",
                # TODO: Verify code from config is not used anywhere
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 1,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
            },
            {
                "id": 5,
                "type": "SIMPLE_DIM",
                "name": "Zone2-Channel-R",
                "description": "",
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 1,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 1,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 1,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 1,
                }
            },
            {
                "id": 15,
                "type": "SIMPLE_DIM",
                "hidden": True,
                "name": " Compartment Lights",
                "description": "",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 1,
                }
            },
            {
                "id": 16,
                "hidden": True,
                "type": "SIMPLE_DIM",
                "name": "Drawer and Front OVHD",
                "description": "",
                "code": "lz",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {
                    "_rgb": "#00000000",
                    "brt": 100,
                    "onOff": 0,
                }
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
                "state": {
                    "brt": 100,
                    "onOff": 0,
                }
            }
        ]
    },
    # "energy_components": {
    #     "bm1": {
    #         "componentTypeId": "energy.bm_basic",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Battery Management",
    #             "description": "Status for the Battery"
    #         }
    #     }
    # },
    # "features_components": {
    #     "pm1": {
    #         "componentTypeId": "features.pm_basic",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Pet Minder",
    #             "description": "Petminder State Reporting"
    #         }
    #     }
    # },
    # "communication_components": {
    #    "ce1": {
    #         "componentTypeId": "communication.ce_cradlepoint",
    #         "instance": 1,
    #         "attributes": {
    #             "name": "Network Router",
    #             "description": "Router State Reporting"
    #         }
    #     }
    # },
    # This provides information how a circuit can be controlled and how a status message could update the state of a circuit
    # Circuit currently is a lower level concept that is abstracted in the component, but without that extra detail an mapping
    # we could not properly control e.g. a water pump.
    # TODO: Improve how we communicate this and use relatedComponents for it, e.g. a lower level CZone component could be related to
    # components and provide the extra details it needs as from below to make it work
    "electrical_mapping": {
        "ac": {},
        "dc": {
            "5": {
                "description": "Controls power to the Furnace",
                "id": 5,
                "long": "C6.5-7 Furnace",
                "rvOutputId": 5,
                "short": "Furnace",
                "category": "climate"
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
                "backText": "Unlock",
                "forwardText": "Lock"
            },
            "8": {
                "description": "Power to the bath vent fan",
                "id": 8,
                "long": "C13.4 Bath Vent Fan Power",
                "rvOutputId": 130,
                "short": "Bath Vent",
                "category": 'electrical'
            },
            "9": {
                "description": "Provides power to the gray tank heater",
                "id": 9,
                "long": "C13.2 Gray Water Tank Heater",
                "rvOutputId": 104,
                "short": "GrayTankHeater",
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
                "description": "Provides power to the galley/lounge vent fan.",
                "id": 12,
                "long": "C13.5 Power to galley vent fan",
                "rvOutputId": 131,
                "short": "RooFFan",
                "category": "climate"
            },
            "13": {
                "description": "H - Bridge 01 Provides power to the Murphy Bed",
                "id": 13,
                "long": "C3.2/1 Power to the Murphy Bed",
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
                "long": "C13.6 Water Heater",
                "rvOutputId": 132,
                "bank": 0x80,   # Instance
                'output': 4,
                "short": "WaterHeater",
                "category": "watersystems",
                # TODO: Fix the incorrect update of state onOff
                "code": "wh",
                "instance": 1
            },
            "15": {
                "description": "Controls Furnace Trigger, that allows burn off cycle to conclude",
                "id": 15,
                "long": "C12.1 Furnace Trigger",
                "rvOutputId": 15,
                "short": "FurnaceTrigger",
                "category": "climate"
            },
            "16": {
                "description": "Sets General Power JJT",
                "id": 16,
                "long": "C6.18-20 Gen Power JJT",
                "rvOutputId": 65,
                "short": "GenPowerJJT",
                "category": "electrical"
            },
            "17": {
                "description": "Sets Refrigerator Power",
                "id": 0x11,
                "long": "C6.8-10 Refrigerator Power",
                "rvOutputId": 8,
                "short": "Refrigerator",
                "category": "electrical"
            },
            "18": {
                "description": "Run Slideout Extend",
                "id": 0x12,
                "long": "C12.8 Run Slideout Extend",
                "bank": 0x60,
                "output_id": 0x3,
                "rvOutputId": 99,
                "short": "SlideoutExtend",
                "category": "movables",
                "widget": "button",
                "code": "so",
                "instance": 1,
                # Which property of the state is modified on circuit updates ?
                "property": "mode",
                # What values map to 1 / 0, these will be read as strings
                "values": {
                    EventValues.OFF: EventValues.OFF,
                    EventValues.ON: EventValues.EXTENDING,
                }
            },
            "19": {
                "description": "Sets General Power JE",
                "id": 0x13,
                "long": "C6.12-14 General Power JE",
                "rvOutputId": 35,
                "short": "GenPowerJE",
                "category": "electrical"
            },
            "20": {
                "description": "Run Slideout Retract",
                "id": 0x14,
                "long": "C12.7 Run Slideout Retract",
                "bank": 0x60,
                "output_id": 0x4,
                "rvOutputId": 100,
                "short": "SlideoutRetract",
                "category": "movables",
                "widget": "button",
                "code": "so",
                "instance": 1,

                # Which property of the state is modified on circuit updates ?
                "property": "mode",
                # What values map to 1 / 0, these will be read as strings
                "values": {
                    EventValues.OFF: EventValues.OFF,
                    EventValues.ON: EventValues.RETRACTING,
                }
            },
            "22": {
                "description": "HMI - Display",
                "id": 0x16,
                "long": "C6.22 HMI - Display",
                "rvOutputId": 68,
                "short": "HMIPower",
                "category": "electrical",
                "hidden": True      # Hide from FCP
            },
            "23": {
                "description": "Microwave Load Shed Relay",
                "id": 0x17,
                "long": "C12.4 Microwave Load Shed Relay",
                "bank": 0x40,
                "output_id": 0x8,
                "rvOutputId": 72,
                "short": "LoadShedMW",
                "category": "electrical"
            },
            "24": {
                "description": "Range Load Shed Relay",
                "id": 0x18,
                "long": "C12.5 Range Load Shed Relay",
                "bank": 0x60,
                "output_id": 0x1,
                "rvOutputId": 97,
                "short": "LoadShedRng",
                "category": "electrical"
            },
            "25": {
                "description": "Sets General Power JD",
                "id": 0x19,
                "long": "C6.15-17 General Power JD",
                "rvOutputId": 38,
                "short": "GenPowerJD",
                "category": "electrical"
            },
            "26": {
                "description": "Parking Brake Ground to Slide Controller CFS",
                "id": 0x1A,
                "long": "C14.6 Parking Brake Signal CFS",
                "rvOutputId": 164,
                "short": "ParkingCFS",
                "category": "movable"
            },
            "27": {
                "description": "LP Generator Start/Stop",
                "id": 0x1B,
                "long": "C2.10/2 LP Gen Start/Stop",
                "rvOutputId": 162,
                "short": "LPGenStartStop",
                "category": "energy",
                "circuitType": "H-BRIDGE"
            },
            # NOTE: Gen Stop removed for the RVMP Generator
            # "28": {
            #     "description": "LP Generator Stop",
            #     "id": 28,
            #     "long": "C2.13/5 LP Gen Stop",
            #     "rvOutputId": 163,
            #     "short": "LPGenStop",
            #     "category": "energy",
            #     "circuitType": "H-BRIDGE"
            # },
            "29": {
                "description": "Water Heater Status LED",
                "id": 0x1D,
                "long": "C12.2 Water Heater LED",
                "rvOutputId": 998,
                "short": "WaterHeaterLED",
                "category": "watersystems"
            },
            "33": {
                "description": "Theater Seat Power",
                "id": 0x21,
                "long": "C3.6/5 Theater Seat",
                "rvOutputId": 999,
                "short": "TheaterSeat",
                "category": "electrical"
            },
        },
        "switches": {},

        "KEYPAD_CONTROLS": {
            # TODO: Test if the right messages go out
            # TODO: Be explicit about the lighting action
            #
            "5": {
                "Name": "Porch",
                "zone_id": 7
            },
            "6": {
                "Name": "Awning On",
                "zone_id": 17
            },
            "7": {
                "Name": "Lounge",
                "zone_id": 8
            },
            "8": {
                "Name": "Compartment",
                "zone_id": 15
            },
            "9": {
                "Name": "All On",
                "action": "hal_action",
                "category": "lighting",
                "function": "smartToggle",
                "params": {
                    'onOff': 1
                }
            },
            "10": {
                "Name": "All Off",
                "action": "hal_action",
                "category": "lighting",
                "function": "smartToggle",
                "params": {
                    'onOff': 0
                }
            }
        },
        'SI_CONTROLS': {   # This is using the heartbeat message FF04 with instance 0x0D / 13
            '13-2': {
                'Name': 'Bunk Light',
                'Comment': 'Input 1 # Momentary',
                'zone_id': 1    # TODO: Get the right zone id
            },
            '13-4': {
                'Name': 'Front Bed OVHD',
                'Comment': 'Input 2 # Momentary',
                'zone_id': 2
            },
            '13-6': {
                'Name': 'Input 3',
                'Comment': 'REAR_BED OVHD - Momentary',
                'zone_id': 3
            },
            '13-8': {
                'Name': 'Input 4',
                'Comment': 'BED_LIGHT - Momentary',
                'zone_id': 4        # TODO: Find out if two switches should act upon the same zone or not.
            },
            '13-10': {
                'Name': 'Input 5',
                'Comment': 'BED_LIGHT Accent - Momentary',
                'zone_id': 5
            },
            '13-12': {
                'Name': 'Input 6',
                'Comment': 'SERVICE_LIGHT - Latching',
                'zone_id': 6
            }
        },
        'RV1_CONTROLS': {
            '4-3': {
                'bank': 4,
                'output': 3,
                'Name': 'C5.12 PSM - Engine Running',
                'Comment': 'C5.12 Engine Running status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_engine",
                "params": {
                    "$active": 'bool'
                }
            },
            '4-5': {
                'bank': 4,
                'output': 5,
                'Name': 'C5.14 PSM - Ignition',
                'Comment': 'C5.13 Ignition status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_ignition",
                "params": {
                    "$active": 'bool'
                }
            },
            '4-7': {
                'bank': 4,
                'output': 7,
                'Name': 'C5.14 PSM - Park Brake Engaged',
                'Comment': 'C5.14 Park Brake status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_park_brake",
                "params": {
                    "$active": 'bool'
                }
            },
            '6-1': {
                'bank': 6,
                'output': 1,
                'Name': 'C5.1 PSM - Transmission not in Park',
                'Comment': 'C5.1 Transmission status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_transmission",
                "params": {
                    "$active": 'bool'
                }
            },
            '6-3': {
                'bank': 6,
                'output': 3,
                'Name': 'C2.5 (AEY) PSM_PB_IGN_COMBO',
                'Comment': 'C2.5 AEY combined status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_pb_ign_combo",
                "params": {
                    "$active": 'bool'
                }
            },
            '6-10': {
                'bank': 6,
                'output': 10,
                'Name': 'C5.6 - Bath Light Switch',
                'Comment': 'C5.6 RV1 Bath Light Switch Input',
                'zone_id': 13       # Bath light
                # "action": "hal_action_component",
                # "category": "lighting",
                # "function": "",
                # "params": {
                #     "$active": 'bool'
                # }
            },
            '6-12': {
                'bank': 6,
                'output': 12,
                'Name': 'C5.7 - Dining OVHD Light Switch',
                'Comment': 'C5.7 RV1 Dining OVHD Light Switch Input',
                'zone_id': 9       # Bath light
                # "action": "hal_action_component",
                # "category": "lighting",
                # "function": "",
                # "params": {
                #     "$active": 'bool'
                # }
            },
            '6-14': {
                'bank': 6,
                'output': 14,
                'Name': 'C5.8 - Galley Light Switch',
                'Comment': 'C5.8 RV1 Galley Light Switch Input',
                'zone_id': 10       # Bath light
                # "action": "hal_action_component",
                # "category": "lighting",
                # "function": "",
                # "params": {
                #     "$active": 'bool'
                # }
            },
            '6-16': {
                'bank': 6,
                'output': 16,
                'Name': 'C5.9 - Galley OVHD Light Switch',
                'Comment': 'C5.9 RV1 Galley OVHD Light Switch Input',
                'zone_id': 11       # Bath light
                # "action": "hal_action_component",
                # "category": "lighting",
                # "function": "",
                # "params": {
                #     "$active": 'bool'
                # }
            },
            '6-20': {
                'Name': 'C11.2 Bath Accent Light',
                'Comment': 'C11.2 Bath Accent Light - Momentary',
                'zone_id': 14,
                # 'action': 'api_call',
                # 'type': 'PUT',
                # 'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
                # 'params': {'$onOff': 'int'}
            },
            '6-22': {
                'Name': 'C11.3 Wardrobe Light',
                'Comment': 'C11.3 Wardrobe Light - Momentary',
                'zone_id': 12,
                # 'action': 'api_call',
                # 'type': 'PUT',
                # 'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
                # 'params': {'$onOff': 'int'}
            },
            '4-26': {
                'bank': 4,
                'output': 26,
                'Name': 'WaterHeaterON',
                'Comment': 'C11.16',
                "action": "hal_action_component",
                "category": "watersystems",
                "function": "set_wh_switch_state",
                "params": {
                    "onOff": 1,
                    "instance": 1
                }
            },
            '4-28': {
                'bank': 4,
                'output': 28,
                'Name': 'WaterHeaterOff',
                'Comment': 'C11.17',
                "action": "hal_action_component",
                "category": "watersystems",
                "function": "set_wh_switch_state",
                "params": {
                    "onOff": 0,
                    "instance": 1
                }
            },
            '4-13': {
                'bank': 4,
                'output': 13,
                'Name': 'Generator - Generator Run',
                'Comment': 'C5.18 Generator Run Status',
                "action": "hal_action_component",
                "category": "energy",
                "function": "update_generator_run",
                "params": {
                    "$active": 'bool',
                    "instance": 1
                }
            },
        },

        'TOGGLE_ZONES': [
            '1', '2', '3', '4', '5',
            '6', '7', '8', '9',
            '10', '11', '12', '13',
            '14', '15', '17'
        ]
    },
    "alert_items": ALERTS,
    # hal categories define which HW modules are loaded, re-use where possible,
    # inherit where possible
    "hal_categories": HAL_CATEGORIES_500,
    # This dispatches CAN messages by name to the appropriate HW handler and its 'update_can_state' method
    # If a message applies to multiple handlers based on instance, we have prepped for by name, instance and source combination
    # Used in 848EC for fluid levels as we use it for energy measurements
    "can_mapping": _500_BASE
}

# Create the componentGroup field based on several data fields
config_definition['componentGroup'] = '{}.{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan'),
    "componentGroup"
)
config_definition['floorPlan'] = model_definition.get('floorPlan')


# Copy and override for the few changes to the NAVION as a twin to the VIEW
alternate_config_definition = deepcopy(config_definition)
alternate_config_definition['componentGroup'] = '{}.{}.{}.{}'.format(
    alternate_model_definition.get('deviceType'),
    alternate_model_definition.get('seriesModel'),
    alternate_model_definition.get('floorPlan'),
    "componentGroup"
)
alternate_config_definition['floorPlan'] = alternate_model_definition.get('floorPlan')



if __name__ == '__main__':
    print(catalog)
    import csv
    with open('export.csv', 'w') as csv_out_handle:
        headers = (
            'floorplan',
            'category',
            'componentId',
            'instance',
            'meta.manufacturer',
            'meta.model',
            'meta.part',
            'attr.name',
            'attr.description'
        )
        csv_file = csv.DictWriter(csv_out_handle, fieldnames=headers)
        csv_file.writeheader()
        for component in model_definition['components']:
            if component.meta is not None:
                meta = component.meta
            else:
                meta = {}

            csv_row = {
                'floorplan': 'WM524T',
                'category': component.category,
                'componentId': component.componentId,
                'instance': component.instance,
                'meta.manufacturer': meta.get('manufacturer'),
                'meta.model': meta.get('model'),
                'meta.part': meta.get('part'),
                'attr.name': component.attributes.get('name'),
                'attr.description': component.attributes.get('description')
            }
            csv_file.writerow(csv_row)
