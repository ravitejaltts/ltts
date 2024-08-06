'''Model definition for the WM524R/IM524R'''


from copy import deepcopy

from ._500_XM524T import model_definition as base_500
from main_service.components.helper import replace_component, ReplaceComp
# from common_libs.models.common import RVEvents, EventValues

from main_service.components.lighting import LightSimple, LightDimmable
from main_service.components.watersystems import (
    ToiletCircuitDefault,
    ToiletCircuitState,
    WaterTankDefault,
    WaterTankState,
    TankHeatingPad,
    TankHeatingPadState,
    WaterPumpDefault,
)

from main_service.components.watersystems import *

from main_service.components.movables import *

from main_service.components.inputs.alerts import ALERTS

from main_service.components.vehicles.can_mappings import _500_BASE
from main_service.components.vehicles.config_500 import HAL_CATEGORIES_500

base_components = deepcopy(base_500['components'])


# TODO: Figure out how to auto get schema for state
# print(dir(FuelTank))
# print(FuelTank.schema())
# state_schema_ref = FuelTank.schema().get('properties', {}).get('state', {}).get('$ref')
# print(state_schema_ref)
# state_schema = FuelTank.schema().get('definitions', {}).get(state_schema_ref.split('/')[-1])

# print(state_schema)

[print(x) for x in base_components if x.category == 'lighting']
# Update components that do not apply
# Remove
for zone_id in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17):
    base_components = replace_component(
        base_components,
        ReplaceComp(category='lighting', instance=zone_id),
        delete=True
    )

for tank_id in (1, 2, 3):
    base_components = replace_component(
        base_components,
        ReplaceComp(category='watersystems', instance=tank_id),
        delete=True
    )
# Rename LZ5, LZ10
new_light_zones = [
    LightDimmable(
        instance=1,
        attributes={
            'name': 'Front Bunk',
            'description': 'Dimmable Light Zone',
            'type': 'DIM__ITC_CHANNEL',
            'hidden': False
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
            'name': 'Bed OVHD - Driver Side',
            'description': 'Dimmable Light Zone',
            'type': 'DIM__ITC_CHANNEL',
            'hidden': False
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
            'name': 'Bed OVHD - Passenger Side',
            'description': 'Dimmable Light Zone',
            'type': 'DIM__ITC_CHANNEL',
            'hidden': False
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
            "name": "Main Accent",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
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
            "name": "Lounge Rear OVHD",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
        },
        optionCodes='31T',
        meta={
            'manufacturer': 'ITC',
            'model': 'VariLight',
            'part': '12345123123'
        }
    ),
    LightDimmable(
        instance=6,
        attributes={
            "name": "Service Light",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            'exterior': True,
            "hidden": False,
            "autoOn": True
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
            "name": "Porch And Step Light",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            'exterior': True,
            "hidden": False,
            "autoOn": True
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
            "name": "Lounge Ceiling",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            "hidden": False,
            "autoOn": True
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
            "name": "Bed Ceiling",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
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
            "name": "Lounge front OVHD",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
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
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
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
            "name": "Hallway Ceiling",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
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
            "name": "Bath Light",
            "description": "Dimmable Light Zone",
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
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
            "type": "DIM__ITC_CHANNEL",
            "hidden": False
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
            "hidden": True,  # Hidden hides them from main lighting view
            "autoOn": True  # Future to be used when first init of the HW controllers
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
            "type": "RVC__DC_DIMMER",
            "canInstance": 1,
            'exterior': True,
            'state.brt': 80
        },
        # This light belongs to Awning instance 1
        relatedComponents=[
            {
                "componentTypeId": AwningRvc().componentId,
                "instance": 1
            }
        ],  # ['movables.aw1', ],
        optionCodes='52N',
        meta={
            'manufacturer': 'CareFree',
            'model': 'DRCMoLED',
            'part': ''
        }
    ),
    LightSimple(
        instance=31,
        attributes={
            "name": "Bed Step Light",
            "description": "czone light For Step Light in Bedroom",
            "type": "Czone__Circuit",
            "hidden": False,
        },
        # This light belongs to Awning instance 1
        meta={
            'manufacturer': '',
            'model': '',
            'part': ''
        }
    )
]

base_components.extend(
    new_light_zones
)


r_tanks = [
    WaterTankDefault(
        instance=1,
        attributes={
            "name": "Fresh Water",
            "description": "Fresh Water",
            "type": "FRESH",
            "cap": 35,
            "unit": 'G',
            "uiclass": "FreshTankLevel",
            "vltgMin": "0.5",
            "vltgMax": "1.29"
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
            "vltgMin": "0.5",
            "vltgMax": "1.346"
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
            "vltgMin": "0.5",
            "vltgMax": "1.068"
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
    )
]

base_components.extend(r_tanks)


# TODO: Add R specific alerts here
# TODO: Pull out or update any alerts that are different for the R
# ALERTS["1234"] = {}

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
    "seriesModel": "1054142",   # TODO: Confirm with Rick
    # floorPlan is the specific flooplan, a floorplan separates variants of the same vehicle
    "floorPlan": "WM524R",
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
        "29J",
        "291",
        "31P",
        "31T",
        "52D",
        "52N",
        "33W"
    ],
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
    "components": base_components
}

# Get R specific components in
model_definition['components'].extend(
    [
        ToiletCircuitDefault(
            instance=1,
            attributes={
                "name": "Toilet Macerator Circuit",
                'description': 'TBD toilet',
                'circuitId': 30  # 0x1E
            },
            state=ToiletCircuitState(),
            meta={
                'manufacturer': 'TBD',
                'model': 'TBD',
                'part': 'TBD'
            }
        )
    ],
)

# Replace R components, such as lights


model_definition['id'] = '{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan')
)

# Copy and override for the few changes to the Navion
alternate_model_definition = deepcopy(model_definition)
alternate_model_definition['seriesModel'] = '7054142'
alternate_model_definition['floorPlan'] = 'IM524R'
alternate_model_definition['attributes']['seriesName'] = 'NAVION'

alternate_model_definition['id'] = '{}.{}.{}'.format(
    alternate_model_definition.get('deviceType'),
    alternate_model_definition.get('seriesModel'),
    alternate_model_definition.get('floorPlan')
)

config_definition = {
    "hal_options": [
        "29J",
        "291",
        "31P",
        "31T",
        "52D",
        "52N",
        "33W"
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
        "default_on_lighting_zones": [6, 7, 8, 15, 16],
        "zones": [
            {
                "id": 1,
                "type": "SIMPLE_DIM",
                "name": "Zone 1 Red",
                "description": "Front Bunk",
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 2,
                "type": "SIMPLE_DIM",
                "name": "Zone 1 Green",
                "description": "Front Bed OVHD",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 3,
                "type": "SIMPLE_DIM",
                "name": "Zone 1 Blue",
                "description": "Rear Bed OVHD",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 4,
                "type": "SIMPLE_DIM",
                "name": "Zone 1 White",
                "description": "Galley Accent 1,2,3,4 (General)",
                "code": "lz",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 5,
                "type": "SIMPLE_DIM",
                "name": "Zone 2 Red",
                "description": "Lounge Rear Overhead",
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 6,
                "type": "SIMPLE_DIM",
                "name": "zone 2 green",
                "description": "Service Light",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 7,
                "type": "SIMPLE_DIM",
                "name": "Zone 2 Blue",
                "description": "Step Light, Porch Light",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 8,
                "type": "SIMPLE_DIM",
                "name": "Zone 2 White",
                "description": "Lounge 1,2,3,4",
                "code": "lz",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 9,
                "type": "SIMPLE_DIM",
                "name": "Zone 3 Red",
                "description": "BED 1 and 2",
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 10,
                "type": "SIMPLE_DIM",
                "name": "Zone 3 Green",
                "description": "Lounge front overhead",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 11,
                "type": "SIMPLE_DIM",
                "name": "Zone 3 Blue",
                "description": "Galley Overhead",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 12,
                "type": "SIMPLE_DIM",
                "name": "zone 3 white",
                "description": "HAllway",
                "channel": "W",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 13,
                "type": "SIMPLE_DIM",
                "name": "Zone 4 Red",
                "description": "Bath Light",
                "code": "lz",
                "channel": "R",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 0}
            },
            {
                "id": 14,
                "type": "SIMPLE_DIM",
                "name": "Zone 4 Green",
                "description": "Bath Accent Light",
                "code": "lz",
                "channel": "G",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 15,
                "type": "SIMPLE_DIM",
                "name": "Zone 4 Blue",
                "description": "Compartment Light",
                "code": "lz",
                "channel": "B",
                "controller_type": "ITC 227X-RGBW",
                "controller": "itc_1",
                "state": {"_rgb": "#00000000", "brt": 100, "onOff": 1}
            },
            {
                "id": 16,
                "type": "SIMPLE_DIM",
                "name": "Zone 4 White",
                "description": "Drawer Lights",
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
            "componentTypeId": "feature.pm_basic",
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
                "description": "Provides power to the galley/lounge vent fan.",
                "id": 12,
                "long": "C13.5 Power to galley vent fan",
                "rvOutputId": 131,
                "short": "RooFFan",
                "category": "climate"
            },
            # Not in the R
            # "13": {
            #     "description": "H - Bridge 01 Provides power to the Murphy Bed",
            #     "id": 13,
            #     "long": "Power to the Murphy Bed",
            #     "rvOutputId": 165,
            #     "short": "MurphyBed",
            #     "category": "movables",
            #     "circuitType": "H-BRIDGE",
            #     "widget": "deadman",
            #     "backText": "Down",
            #     "forwardText": "Up"
            # },
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
                "long": "C6.18-20 Gen Power JJT",
                "rvOutputId": 65,
                "short": "GenPowerJJT",
                "category": "electrical"
            },
            "17": {
                "description": "Sets Refrigerator Power",
                "id": 17,
                "long": "C6.8-10 Refrigerator Power",
                "rvOutputId": 8,
                "short": "Refrigerator",
                "category": "electrical"
            },
            "18": {
                # TODO: Figure this out
                # ????? How is this different from the T
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
                "long": "C6.12-14 General Power JE",
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
                "id": 25,
                "long": "C6.15-17 General Power JD",
                "rvOutputId": 38,
                "short": "GenPowerJD",
                "category": "electrical"
            },
            "27": {
                "description": "LP Generator Start/Stop",
                "id": 27,
                "long": "C2.10/2 LP Gen Start/Stop",
                "rvOutputId": 162,
                "short": "LPGenStartStop",
                "category": "energy",
                "circuitType": "H-BRIDGE"
            },
            "29": {
                "description": "Water Heater Status LED",
                "id": 0x1D,
                "long": "C12.2 Water Heater LED",
                "rvOutputId": 998,
                "short": "WaterHeaterLED",
                "category": "watersystems"
            },
            "30": {
                "description": "H - Bridge 02 c3.4/3 Toilet",
                "id": 30,
                "long": "C3.4/3 Power To Toilet",
                "rvOutputId": 166,
                "short": "Toilet",
                "category": "watersystems"
            },
            "31": {
                "description": "Bed Room Step Light",
                "id": 0x1F,
                "long": "C12.3 Bedroom Step Light",
                "rvOutputId": 997,
                "short": "Bedroom Step",
                "category": "lighting"
            },
            "32": {
                "description": "Bed Room Step light ",
                "id": 31,
                "long": "CZone Step Light C12.3",
                "rvOutputId": 71,
                "short": "Bed step light",
                "category": "lighting",
                "code": "lz",
                "instance": 31,
            },
            "33": {
                "description": "Theater Seat Power",
                "id": 30,
                "long": "C3.6/5 Theater Seat",
                "rvOutputId": 999,
                "short": "TheaterSeat",
                "category": "electrical"
            }
        },

        "switches": {},

        "KEYPAD_CONTROLS": {
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
                    "onOff": 1
                }
            },
            "10": {
                "Name": "All Off",
                "action": "hal_action",
                "category": "lighting",
                "function": "smartToggle",
                "params": {
                    "onOff": 0
                }
            }
        },
        "SI_CONTROLS": {
            "13-2": {
                "Name": "Front Bunk",
                "Comment": "Input 2 # Momentary",
                "zone_id": 1
            },
            "13-4": {
                "Name": "Rear Lounge",
                "Comment": "Input 2 # Momentary",
                "zone_id": 5
            },
            "13-6": {
                "Name": "Lounge Front",
                "Comment": "Input 3 # Momentary",
                "zone_id": 10
            },
            "13-8": {
                "Name": "Input 4",
                "Comment": "Hallway",
                "zone_id": 12
            },
            "13-10": {
                "Name": "Input 5",
                "Comment": "Bed Light",
                "zone_id": 9
            },
            "13-12": {
                "Name": "Input 6",
                "Comment": "SERVICE_LIGHT",
                "zone_id": 6
            }
        },

        "RV1_CONTROLS": {
            '4-3': {
                'bank': 4,
                'output': 3,
                'Name': 'PSM - Engine Running',
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
                'Name': 'PSM - Ignition',
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
                'Name': 'PSM - Park Brake Engaged',
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
                'Name': 'PSM - Transmission not in Park',
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
                'Name': 'PSM - AEY signal',
                'Comment': 'C2.5 AEY combined status as received by Sprinter PSM',
                "action": "hal_action_component",
                "category": "vehicle",
                "function": "update_pb_ign_combo",
                "params": {
                    "$active": 'bool'
                }
            },
            "6-4": {
                'bank': 6,
                'output': 4,
                "Name": "Input 12",
                "Comment": "Bath",
                "zone_id": 12
            },
            "6-6": {
                'bank': 6,
                'output': 6,
                "Name": "Input 20",
                "Comment": "Bath Accent",
                "zone_id": 8
            },
            "6-10": {
                'bank': 6,
                'output': 10,
                "Name": "Input 10",
                "Comment": "Bath",
                "zone_id": 13
            },
            "6-12": {
                'bank': 6,
                'output': 12,
                "Name": "Input 22",
                "Comment": "Bed 1 and 2",
                "zone_id": 4
            },
            "6-14": {
                'bank': 6,
                'output': 14,
                "Name": "Input 10",
                "Comment": "Galley",
                "zone_id": 11
            },
            "6-16": {
                'bank': 6,
                'output': 16,
                "Name": "Input 10",
                "Comment": "lounge ceiling",
                "zone_id": 8
            },
            "6-18": {
                'bank': 6,
                'output': 18,
                "Name": "Input 10",
                "Comment": "main accent",
                "zone_id": 4
            },
            "6-20": {
                'bank': 6,
                'output': 20,
                "Name": "Input 10",
                "Comment": "Accent",
                "zone_id": 14
            },
            "6-22": {
                'bank': 6,
                'output': 22,
                "Name": "Input 14",
                "Comment": "Bed room ceiling",
                "zone_id": 31
            },
            '6-30': {
                'bank': 6,
                'output': 30,
                'Name': 'Bank 6 - Input 30',
                'Comment': 'Rear Bed OVHD',
                'zone_id': 3
            },
            "6-32": {
                'bank': 6,
                'output': 10,
                "Name": "Input 14",
                "Comment": "Front Bed OVHD",
                "zone_id": 2
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
            }
        },

        "TOGGLE_ZONES": [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "31"
        ]
    },
    "alert_items": ALERTS,
    "hal_categories": HAL_CATEGORIES_500,
    "can_mapping": _500_BASE,

    'componentGroup': '{}.{}.{}.{}'.format(
        model_definition.get('deviceType'),
        model_definition.get('seriesModel'),
        model_definition.get('floorPlan'),
        "componentGroup"
    ),
    'floorPlan': model_definition.get('floorPlan')
}

# Copy and override for the few changes to the Navion
alternate_config_definition = deepcopy(config_definition)
alternate_config_definition['componentGroup'] = '{}.{}.{}.{}'.format(
    alternate_model_definition.get('deviceType'),
    alternate_model_definition.get('seriesModel'),
    alternate_model_definition.get('floorPlan'),
    "componentGroup"
)
alternate_config_definition['floorPlan'] = alternate_model_definition.get('floorPlan')
