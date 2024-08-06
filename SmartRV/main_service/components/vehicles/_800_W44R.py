'''Model definition for the BF848 1.4 ???'''

from common_libs.models.common import EventValues

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

from main_service.components.vehicles.can_mappings import _800_BASE
from main_service.components.vehicles.config_800 import HAL_CATEGORIES_800

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
    "deviceType": "s800",
    # seriesModel is the numerical ID for the specific model
    "seriesModel": "123456",   # TODO: Confirm with Rick
    # floorPlan is the specific flooplan, a floorplan separates variants of the same vehicle
    "floorPlan": "W44R",
    # attributes can be used as Meta information that can be propagated to the UI as needed
    "attributes": {
        "name": '44R',
        "seriesName": "44R",
        "seriesCode": "800",
        "version": "1.0.0",          # TODO: Increment this version automatically upon generation
    },
    # optionCodes (dict)
    # are just a list of all possible options, nothing specifically happens here just a at a glance check what options do apply
    # optioncodes will be handled in filters further down in relatedComponents
    "optionCodes": [
        # NOTE: We might need an option code for EcoFlow PowerHub
    ],
    # filters (dict)
    # that help query broader picture data and help to which modelYears and other meta info this plan applies to
    "filters": {
        "modelYears": ["2025", ]
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
                'description': '',
                'controllable': 'N'
            },
            meta={
                'manufacturer': '',
                'model': '',
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
        # ThermostatOutdoor(
        #     instance=2,
        #     attributes={
        #         'name': 'Outdoor',
        #         'description': 'Outdoor Temp Sensor',
        #         'type': 'INTERMOTIVE'   # Should tell code to look for the intermotive data
        #     },
        #     meta={
        #         'manufacturer': 'Ford',
        #         'model': 'Built in sensor',
        #         'part': 'N/A'
        #     }
        # ),
        HeaterBasic(
            instance=1,
            attributes={
                "name": "Heater",
                'description': 'Electrical Space Heater',
                'circuit': 123  # TODO: Get Circuit ID
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }

        ),
        ACBasic(
            instance=1,
            attributes={
                'name': 'Air Conditioner',
                'description': 'Premier AC unit with 3 wires',
                'controller': 'CZONE',
                # circuit prefix is used to understand which circuit can be
                # associated to a state property and specific value
                'circuit.comp': 5,
                'circuit.fanSpd.HIGH': 6,
                'circuit.fanSpd.LOW': 7,
                'supportedSpeeds': [EventValues.LOW, EventValues.HIGH]
            },
            meta={
                'manufacturer': 'Premier AC',
                'model': '48V',
                'part': ''
            }
        ),
        # NOTE: Bring back when refrigeration sensing is working
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
        RoofFanAdvanced(
            instance=1,
            attributes={
                'name': 'Lounge Vent',
                'description': 'Main Roof Fan'
            },
            meta={
                'manufacturer': 'Dometic',
                'model': 'FanTastic 5300',
                'part': 'FV5300HWUWD81-SP'
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
        # AC Unit
        BatteryManagement(
            instance=1,
            attributes={
                'name': 'Battery Management',
                'description': 'BMS',
                'type': 'LITHIONICS',
                'nominalVoltage': '48.0V',
                'minSoc': 10
            },
            meta={
                'manufacturer': 'Lithionics',
                'model': '',
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
        BatteryPack(
            instance=2,
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
                'model': '',
                'part': ''
            }
        ),
        # Simple Inverter
        InverterBasic(
            instance=1,
            attributes={
                "name": "Inverter",
                'description': 'Victron Simple Inverter Component',
                "type": "CIRCUIT",      # Still needed ?
                "state.maxLoad": 2400
            },
            meta={
                'manufacturer': 'Victron',
                'model': '',
                'part': ''
            }
        ),
        # AC Current Sensor
        # AC Current Sensor for AVC2
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
        # SOLAR POWER through SHUNT
        PowerSourceSolar(
            instance=1,
            attributes={
                'name': 'Solar',
                'description': 'Solar Controller Source',
                'type': 'CZONE_SHUNT',
                'shuntRatingA': 50
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        PowerSourceShore(
            instance=2,
            attributes={
                'name': 'Shore',
                'description': 'Shore Power Source'
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        PowerSourceProPower(
            instance=3,
            attributes={
                'name': 'Pro Power',
                'description': 'Pro Power Power Source',
                'type': 'PROPOWER'
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        LightRGBW(
            instance=1,
            attributes={
                'name': 'Front Bunk R',
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
            instance=16,
            attributes={
                "name": "Drawer and Front OVHD",
                "description": "Dimmable Light Zone",
                "type": "DIM__ITC_CHANNEL",
                "hidden": True,
                "autoOn": True,
                "inAll": False
            },
            meta={
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        # Lighting
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
        # WaterSystems
        # TODO: Fix water tanks
        WaterTankDefault(
            instance=1,
            attributes={
                "name": "Fresh Water",
                "description": "Fresh Water",
                "type": "FRESH",
                "cap": 35,
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
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        WaterTankDefault(
            instance=2,
            attributes={
                "name": "Grey Water",
                "description": "Grey Water",
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
                'manufacturer': '',
                'model': '',
                'part': ''
            }
        ),
        WaterPumpDefault(
            instance=1,
            attributes={
                "name": "Fresh Water",
                "description": "Fresh Water Pump",
                "type": "FRESH",
                'controller': 'CZONE',
                'circuits': [5,]      # TODO: Confirm circuit
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
        WaterPumpDefault(
            instance=2,
            attributes={
                "name": "Shower Sump",
                "description": "Grey Water / Shower Pump",
                "type": "GREY",
                'controller': 'CZONE',
                'circuits': [6,]      # TODO: Confirm circuit
            },
            # Pump is related to Fresh water tank, instance 1 of wt in this case
            relatedComponents=[
                {
                    "componentTypeId": WaterTankDefault().componentId,
                    "instance": 2
                }
            ],
            meta={
                'manufacturer': 'SHURFLO',
                'model': '4008-101-F65',
                'part': 'N/A'  # No partnumber given
            }
        ),
        WaterHeaterSimple(
            instance=1,
            attributes={
                "name": "Water Heater",
                "description": "Electric Water Heater",
                'type': 'SIMPLE',
                'controller': 'CZONE',
                'circuits': [7,],     # TODO: Fill circuitID
            },
            meta={
                'manufacturer': 'TRUMA CORP (23351)',
                'model': '36022-81',
                'part': '000027742'
            }
        ),
        LockoutBasic(
            instance=EventValues.PARK_BRAKE_APPLIED,
            attributes={
                'name': "Park Brake Applied",
                'description': 'Is the park brake currently released'
            }
        ),
        LockoutBasic(
            instance=EventValues.IGNITION_ON,
            attributes={
                'name': "Ignition On State",
                'description': 'Is the ignition on'
            }
        ),
        LockoutBasic(
            instance=EventValues.LOW_VOLTAGE,
            attributes={
                'name': "Low voltage on house battery.",
                'description': 'Might cause warnings or lockouts based on low voltage'
            }
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
        # FAILURE_TEST_COMPONENT(
        #     instance=1,
        #     attributes={
        #         'name': 'Error component, does not exist',
        #         'description': 'Shall fail template generation as it will not be generated as a component'
        #     }
        # )
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

config_definition = {
    "floorPlan": "",
    "componentGroup": "",
    "hal_options": [],
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

        "he1": {
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
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
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
                "id": 5,
                "type": "SIMPLE_DIM",
                "name": "Zone2-Channel-R",
                "description": "",
                "code": "lz",
                "channel": "R",
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
                "hidden": True,
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
                "hidden": True,
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
    # This provides information how a circuit can be controlled and how a status message could update the state of a circuit
    # Circuit currently is a lower level concept that is abstracted in the component, but without that extra detail an mapping
    # we could not properly control e.g. a water pump.
    # TODO: Improve how we communicate this and use relatedComponents for it, e.g. a lower level CZone component could be related to
    # components and provide the extra details it needs as from below to make it work
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
                "backText": "Unlock",
                "forwardText": "Lock"
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
                "description": "Provides power to the grey tank heater",
                "id": 9,
                "long": "C13.2 Grey Water Tank Heater",
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
                "long": "C12.7 Run Slideout Retract",
                "bank": 0x60,
                "output_id": 0x4,
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
                "bank": 0x60,
                "output_id": 0x3,
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
                "long": "C14.6 Parking Brake Signal CFS",
                "rvOutputId": 164,
                "short": "ParkingCFS",
                "category": "movable"
            },
            "27": {
                "description": "LP Generator Start",
                "id": 27,
                "long": "C2.10/2 LP Gen Start",
                "rvOutputId": 162,
                "short": "LPGenStart",
                "category": "energy",
                "circuitType": "H-BRIDGE"
            },
            "28": {
                "description": "LP Generator Stop",
                "id": 28,
                "long": "C2.13/5 LP Gen Stop",
                "rvOutputId": 163,
                "short": "LPGenStop",
                "category": "energy",
                "circuitType": "H-BRIDGE"
            }
        },
        "switches": {},
        'SCI_CONTROLS': {   # This is using the heartbeat message FF04 with instance 0x0D / 13
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
            # '14': {
            #     'Name': 'Input 14',
            #     'Comment': 'Galley Light - Momentary',
            #     'zone_id': 10,
            #     # 'action': 'api_call',
            #     # 'type': 'PUT',
            #     # 'href': 'http://127.0.0.1:8000/api/lighting/zone/4',
            #     # 'params': {'$onOff': 'int'}
            # },
            # '16': {
            #     'Name': 'Input 14',
            #     'Comment': 'Galley OVHD Light - Latching',
            #     'zone_id': 11,
            #     # 'action': 'api_call',
            #     # 'type': 'PUT',
            #     # 'href': 'http://127.0.0.1:8000/api/lighting/zone/4',
            #     # 'params': {'$onOff': 'int'}
            # },
            # '12': {
            #     'Name': 'Input 12',
            #     'Comment': 'Dining OVHD Light - Momentary',
            #     'zone_id': 9,
            #     # 'action': 'api_call',
            #     # 'type': 'PUT',
            #     # 'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
            #     # 'params': {'$onOff': 'int'}
            # },
            # '20': {
            #     'Name': 'Input 20',
            #     'Comment': 'Bath Accent Light - Momentary',
            #     'zone_id': 14,
            #     # 'action': 'api_call',
            #     # 'type': 'PUT',
            #     # 'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
            #     # 'params': {'$onOff': 'int'}
            # },
            # '22': {
            #     'Name': 'Input 22',
            #     'Comment': 'Wardrobe Light - Momentary',
            #     'zone_id': 12,
            #     # 'action': 'api_call',
            #     # 'type': 'PUT',
            #     # 'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
            #     # 'params': {'$onOff': 'int'}
            # },
            # '10': {
            #     'Name': 'Input 10',
            #     'Comment': 'Bath  Light - Momentary',
            #     'zone_id': 13,
            #     # 'action': 'api_call',
            #     # 'type': 'PUT',
            #     # 'href': 'http://127.0.0.1:8000/api/lighting/zone/4',
            #     # 'params': {'$onOff': 'int'}
            # },

            '4-7': {
                'bank': 4,
                'output': 7,
                'Name': 'PSM - Park Brake Engaged',
                'Comment': 'C5.13 Park Brake status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_park_brake",
                "params": {
                    "$active": 'bool'
                }
            },
            '4-5': {
                'bank': 4,
                'output': 5,
                'Name': 'PSM - Ignition',
                'Comment': 'C5.14 Ignition status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_ignition",
                "params": {
                    "$active": 'bool'
                }
            },
            '6-1': {
                'bank': 6,
                'output': 1,
                'Name': 'PSM - Transmission not in Park',
                'Comment': 'C5.1 Transmission status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_transmission",
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
                'Name': 'Bank 6 - Input 20',
                'Comment': 'C11.2 Bath Accent Light - Momentary',
                'zone_id': 14,
                # 'action': 'api_call',
                # 'type': 'PUT',
                # 'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
                # 'params': {'$onOff': 'int'}
            },
            '6-22': {
                'Name': 'Bank 6 - Input 22',
                'Comment': 'C11.3 Wardrobe Light - Momentary',
                'zone_id': 12,
                # 'action': 'api_call',
                # 'type': 'PUT',
                # 'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
                # 'params': {'$onOff': 'int'}
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
            '1', '2', '3', '4',
            '5', '6', '7', '8',
            '9', '10'
        ]
    },
    "alert_items": {
        "50009": {
            "notification_id": 50009,
            "instance": 1,
            "priority": 4,
            "user_selected": 1,
            "code": "watersystems:wt50009",
            "trigger_events": [
                8600
            ],
            "trigger_type": 4,
            "trigger_value": 99,
            "header": "Fresh water tank full",
            "msg": "Fresh water tank is full",
            "type": 0
        },
        "50034": {
            "notification_id": 50034,
            "instance": 1,
            "priority": 4,
            "user_selected": 1,
            "code": "watersystems:wt50034",
            "trigger_events": [
                8600
            ],
            "trigger_type": 5,
            "trigger_value": 25,
            "header": "Fresh water tank getting low",
            "msg": "Fresh water tank is below {}%",
            "type": 0
        },
        "50008": {
            "notification_id": 50008,
            "instance": 1,
            "priority": 1,
            "user_selected": 1,
            "code": "watersystems:wt50008",
            "trigger_events": [
                8600
            ],
            "trigger_type": 5,
            "trigger_value": 10,
            "header": "Fresh water tank low",
            "msg": "Fresh water tank is below {}%",
            "type": 0
        },
        "50007": {
            "notification_id": 50007,
            "instance": 1,
            "priority": 0,
            "user_selected": 0,
            "code": "watersystems:wt50007",
            "trigger_events": [
                8600
            ],
            "trigger_type": 5,
            "trigger_value": 1,
            "header": "Fresh water tank empty",
            "msg": "Fresh water tank is empty!",
            "type": 0
        },
        "50010": {
            "notification_id": 50010,
            "instance": 2,
            "priority": 4,
            "user_selected": 1,
            "code": "watersystems:wt50010",
            "trigger_events": [
                8600
            ],
            "trigger_type": 5,
            "trigger_value": 1,
            "header": "Gray water tank empty",
            "msg": "Gray water tank is empty!",
            "type": 0
        },
        "50035": {
            "notification_id": 50035,
            "instance": 2,
            "priority": 4,
            "user_selected": 1,
            "code": "watersystems:wt50035",
            "trigger_events": [
                8600
            ],
            "trigger_type": 4,
            "trigger_value": 75,
            "header": "Gray water approaching high",
            "msg": "Gray water tank is filling up!",
            "type": 0
        },
        "50011": {
            "notification_id": 50011,
            "instance": 2,
            "priority": 1,
            "user_selected": 1,
            "code": "watersystems:wt50011",
            "trigger_events": [
                8600
            ],
            "trigger_type": 4,
            "trigger_value": 90,
            "header": "Gray water tank High",
            "msg": "Gray water tank is above {}%",
            "type": 0
        },
        "50012": {
            "notification_id": 50012,
            "instance": 2,
            "priority": 0,
            "user_selected": 1,
            "code": "watersystems:wt50012",
            "trigger_events": [
                8600
            ],
            "trigger_type": 4,
            "trigger_value": 99,
            "header": "Gray water tank Full",
            "msg": "Gray Water is about to overflow!",
            "type": 0
        },
        "50015": {
            "notification_id": 50015,
            "instance": 1,
            "priority": 4,
            "user_selected": 1,
            "code": "energy:ba50015",
            "trigger_events": [
                7809
            ],
            "trigger_type": 4,
            "trigger_value": 99,
            "header": "Battery charged",
            "msg": "Battery fully charged",
            "type": 1
        },
        "50016": {
            "notification_id": 50016,
            "instance": 1,
            "priority": 4,
            "user_selected": 1,
            "code": "energy:ba50021",
            "trigger_events": [
                7809
            ],
            "trigger_type": 5,
            "trigger_value": 10,
            "header": "Battery low",
            "msg": "Battery voltage very low.",
            "type": 0
        },
        "50017": {
            "notification_id": 50017,
            "instance": 1,
            "priority": 4,
            "user_selected": 1,
            "code": "energy:ba50017",
            "trigger_events": [
                7809
            ],
            "trigger_type": 5,
            "trigger_value": 1,
            "header": "Battery OFF",
            "msg": "Battery Turned OFF, out of power!",
            "type": 1
        },
        "50006": {
            "notification_id": 50006,
            "instance": 1,
            "priority": 0,
            "user_selected": 1,
            "code": "climate:rf50006",
            "trigger_events": [
                9400
            ],
            "trigger_type": 8,
            "trigger_value": "1.11,3.33",
            "header": "Refrigerator Temp",
            "msg": "Refrigerator Temp. out of range!",
            "type": 0
        },
        "50036": {
            "ts_id": 0,
            "notification_id": 50036,
            "instance": 2,
            "priority": 0,
            "user_selected": 1,
            "code": "climate:fr50036",
            "trigger_events": [
                9400
            ],
            "trigger_type": 8,
            "trigger_value": "-4,0",
            "header": "Freezer Temp",
            "msg": "Freezer Temp. out of range!",
            "type": 0
        },
        "50020": {
            "notification_id": 50020,
            "instance": 1,
            "priority": 1,
            "user_selected": 1,
            "code": "climate:th50020",
            "trigger_events": [
                6802
            ],
            "trigger_type": 5,
            "trigger_value": 0.0,
            "header": "Coach Temperature Low",
            "msg": "Coach temperature is low!",
            "type": 0
        },
        "50021": {
            "notification_id": 50021,
            "instance": 1,
            "priority": 1,
            "user_selected": 1,
            "code": "climate:th50021",
            "trigger_events": [
                6802
            ],
            "trigger_type": 4,
            "trigger_value": 35.0,
            "header": "Coach Temperature High",
            "msg": "Coach temperature is high!",
            "type": 0
        },
        "50033": {
            "notification_id": 50033,
            "instance": 1,
            "priority": 1,
            "user_selected": 1,
            "code": "system:ot50033",
            "trigger_events": [
                9201
            ],
            "trigger_type": 1,
            "trigger_value": 32.22,
            "header": "OTA Received",
            "msg": "OTA Ready to Install",
            "type": 0
        }
    },
    # hal categories define which HW modules are loaded, re-use where possible,
    # inherit where possible
    "hal_categories": HAL_CATEGORIES_800,
    # This dispatches CAN messages by name to the appropriate HW handler and its 'update_can_state' method
    # If a message applies to multiple handlers based on instance, we have prepped for by name, instance and source combination
    # Used in 848EC for fluid levels as we use it for energy measurements
    "can_mapping": _800_BASE
}

# Create the componentGroup field based on several data fields
config_definition['componentGroup'] = '{}.{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan'),
    "componentGroup"
)
config_definition['floorPlan'] = model_definition.get('floorPlan')

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
