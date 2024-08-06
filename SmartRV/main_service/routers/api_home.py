import json
from typing import Optional, List

import logging
import time
import math
import asyncio

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from common_libs.models.gui import (
    HeaderWidgets,
    QuickActionWidget,
    LevelWidget,
    Widget,
    Notification,
    ClimateWidget,
)

from main_service.components.climate import (
    HVACModeEnum,
)


from common_libs.models.common import EventValues
from common_libs.models.notifications import NotificationPriority
# from models.common import EventValues
# from models.notifications import NotificationPriority

from common_libs.models.lighting import *

from main_service.modules.constants import (
    GALLONS_2_LITER,
    TEMP_UNIT_FAHRENHEIT,
    _celcius_2_fahrenheit,
    HVAC_MODES,
    TEMP_UNITS,
    HVAC_MODES,
    WATER_UNIT_GALLONS,
    WATER_UNIT_LITER
)

from .mockdb.lighting import lighting as mock_lighting
from .mockdb.quick_actions import quick_actions as mock_quick_actions
from .mockdb.levels import level_states as mock_levels

from .ui import ui_home
from .ui import ui_watersystems
from .ui import ui_lighting
from .ui import ui_appview
from .ui import ui_energy
from .ui import ui_climate
from .ui import ui_functionaltests
from .ui import ui_refrigerator
from .ui import ui_inverter
from .ui import ui_settings
from .ui import ui_notifications
from .ui import ui_movables
from .ui import ui_generator
from .ui import ui_manufacturing
from .ui import ui_petmonitor

from .ui.helper import *


wgo_logger = logging.getLogger('main_service')
from main_service.modules.logger import prefix_log
from common_libs.models.notifications import dismiss_note


mock_db = {}

BASE_URL = ''

def reload_mock_db():
    global mock_db
    # TODO: Move this to an application attribute
    mock_db = json.load(open('./routers/mockdb/db.json', 'r'))


router = APIRouter(
    prefix='/ui',
    tags=['UI',]
)

router.include_router(
    ui_home.router
)

router.include_router(
    ui_watersystems.router
)

router.include_router(
    ui_lighting.router
)

router.include_router(
    ui_appview.router
)

router.include_router(
    ui_energy.router
)

router.include_router(
    ui_climate.router
)

router.include_router(
    ui_functionaltests.router
)

router.include_router(
    ui_refrigerator.router
)

router.include_router(
    ui_inverter.router
)

router.include_router(
    ui_settings.router
)

router.include_router(
    ui_notifications.router
)

router.include_router(
    ui_movables.router
)

router.include_router(
    ui_generator.router
)

router.include_router(
    ui_manufacturing.router
)

router.include_router(
    ui_petmonitor.router
)


def get_top():
    current_icons = []

    # TODO: Get this from bluetooth state
    bt_status = 'active'
    bt_connected = 'false'

    bluetooth = {
        "name": "TopBluetooth",
        "icon": "top-bt-icon",
        "status": bt_status,
        "data": [
            {
                "key": "BT_CONNECTED_DEVICE",
                "value": bt_connected
            }
        ]
    }

    current_icons.append(bluetooth)
    widgets = HeaderWidgets(
        icons=current_icons
    )
    return widgets

def get_left_bar(app):
    current_icons = []
    notifications = {
        "name": "LeftBarNotifications",
        "icon": "left-bar-notification-icon",
        "status": "active",
        "data": []
    }

    with app.n_lock:
        try:
            #notifications = app.notifications
            pet = 0
            weather = 0
            critical = 0
            warning = 0
            info = 0
            for item in app.notifications:
                level = item.get('level')
                if level == NotificationPriority.System_Critical:
                    critical += 1
                elif level == NotificationPriority.System_Warning:
                    warning += 1
                elif level == NotificationPriority.System_Notice:
                    info += 1
                elif level == NotificationPriority.Pet_Minder_Notice or level == NotificationPriority.Pet_Minder_Warning:
                    pet += 1
                else:
                    weather += 1
        except Exception as err:
            print(err)

            print('Get Top exception')

    notifications['data'] = [
        {
            "key": "NOTIFICATION_COUNT",
            "value": critical + warning + info + weather + pet
        },
        {
            "key": "NOTIFICATIONS_WEATHER",
            "value": weather
        },
        {
            "key": "NOTIFICATIONS_PET_MONITOR",
            "value": pet
        },
        {
            "key": "NOTIFICATIONS_CRITICAL",
            "value": critical
        },
        {
            "key": "NOTIFICATIONS_WARNING",
            "value": warning
        },
        {
            "key": "NOTIFICATIONS_INFO",
            "value": info
        }
    ]
    if (weather + critical + warning + info) > 0:
        notifications['status'] = 'active'
        current_icons.append(notifications)
    else:
        notifications['status'] = 'inactive'
    widgets = HeaderWidgets(
        icons=current_icons
    )
    return widgets


def get_quick_action(hal, config, debug=False):
    # Get list of things to show in quick actions
    # Get priority and sort by it high to low
    # Create quick action widgets and add to response in order
    quick_actions = []
    _500_list = [
        'WM524T', 'WM524R', 'WM524D', 'WM524NP',
        'IM524T', 'IM524R', 'IM524D', 'IM524NP'
    ]

    try:
        if hal.floorPlan == 'BF848EC':
            quick_action_options = {
                'InverterAction': {},
                'WaterpumpAction': {},
                'WaterHeaterAction': {},
                'MasterLightAction': {},
                'PlaceHolderAction': {}
            }
        elif hal.floorPlan in _500_list:
            quick_action_options = {
                'InverterAction': {},
                'WaterpumpAction': {},
                'WaterHeaterAction': {},
                'MasterLightAction': {},
                'PlaceHolderAction': {}
            }
        else:
            quick_action_options = {
                'PlaceHolderAction1': {},
                'PlaceHolderAction2': {},
                'PlaceHolderAction3': {},
                'PlaceHolderAction4': {},
                'PlaceHolderAction5': {}
            }
    except AttributeError as err:
        wgo_logger.error(f'ERROR: {err}')
        quick_action_options = {
            'PlaceHolderAction1': {},
            'PlaceHolderAction2': {},
            'PlaceHolderAction3': {},
            'PlaceHolderAction4': {},
            'PlaceHolderAction5': {}
        }


    quick_water_systems_href = '/home/watersystems'

    waterpump_id = 1
    waterpump_state = hal.watersystems.handler.water_pump[waterpump_id].state

    waterpump_onOff = waterpump_state.onOff
    waterpump_subtext = 'On' if waterpump_onOff == 1 else 'Off'

    quick_inverter_onOff = hal.energy.handler.inverter[1].state.onOff
    quick_inverter_subtext = 'On' if quick_inverter_onOff else 'Off'

    waterheater_id = 1
    waterheater_state = hal.watersystems.handler.water_heater[waterheater_id].state
    if waterheater_state is None:
        wgo_logger.error('Water heater state is None')
        waterheater_state = {}

    waterheater_onOff = waterheater_state.onOff
    waterheater_subtext = 'On' if waterheater_onOff == 1 else 'Off'

    masterlight_state = hal.lighting.handler.light_status()
    lights_on = masterlight_state.get('on')
    masterlight_onOff = 1 if lights_on > 0 else 0
    masterlight_subtext = 'On' if masterlight_onOff == 1 else 'Off'

    INT_GROUP_ID = 99
    interior_light_group = hal.lighting.handler.lighting_group.get(INT_GROUP_ID)
    interior_light_group.check_group(attribute='exterior', skip_if_True=True)
    interior_lights = 'On'if interior_light_group.state.onOff == EventValues.ON else 'Off'

    EXT_GROUP_ID = 100
    exterior_light_group = hal.lighting.handler.lighting_group.get(EXT_GROUP_ID)
    exterior_light_group.check_group(attribute='exterior',  skip_if_True=False)
    exterior_lights = 'On'if exterior_light_group.state.onOff == EventValues.ON else 'Off'

    fan_id = 1  # Use the first fan instance found
    roof_fan = hal.climate.handler.roof_vent[fan_id]
    roof_fan_onoff = roof_fan.state.dome

    if roof_fan_onoff == EventValues.CLOSED:
        roof_fan_onoff = 0
    elif roof_fan_onoff == EventValues.OPEN:
        if roof_fan.state.onOff == EventValues.OFF:
            roof_fan_onoff = 0
        else:
            roof_fan_onoff = 1

    # NOTE: We currently do not support states, so we cannot have a subtext
    # roof_fan_subtext = 'On' if roof_fan_onoff == 1 else 'Off'

    quick_actions = [
        {
            "name": "InverterAction",

            "title": "Inverter",
            "subtext": quick_inverter_subtext,

            'type': 'Simple',
            'Simple': {
                'onOff': quick_inverter_onOff
            },

            'actions': [
                'action_default',
                'action_longpress'
            ],
            "action_default": {
                "type": "api_call",
                "action": {
                    # Old
                    # "href": f"/api/energy/inverters/1/state",
                    # New
                    "href": f"/api/energy/ei/1/state",
                    "type": "PUT",
                    "params": {
                        "$onOff": 'int'
                    }
                }
            },
            "action_longpress": {
                "type": "navigate",
                "action": {
                    "href": "/home/ems"
                }
            }
        },
        {
            "name": "WaterPumpAction",

            "title": "Water Pump",
            "subtext": waterpump_subtext,

            "type": "Simple",
            'Simple': {
                'onOff': waterpump_onOff
            },

            'actions': ['action_default', 'action_longpress'],

            "action_default": {
                "type": "api_call",
                "action": {
                    "href": f"/api/watersystems/wp/{waterpump_id}/state",
                    "type": "PUT",
                    'params': {
                        '$onOff': 'int'
                    }
                }
            },

            "action_longpress": {
                "type": "navigate",
                "action": {
                    "href": quick_water_systems_href
                }
            }
        },
        {
            "name": "WaterHeaterAction",

            "title": "Water Heater",
            "subtext": waterheater_subtext,

            'type': 'Simple',
            'Simple': {
                'onOff': waterheater_onOff
            },

            'actions': [
                'action_default',
                'action_longpress'
            ],
            "action_default": {
                "type": "api_call",
                "action": {
                    "href": f"/api/watersystems/wh/{waterheater_id}/state",
                    "type": "PUT",
                    "params": {
                        "$onOff": 'int'
                    }
                }
            },
            "action_longpress": {
                "type": "navigate",
                "action": {
                    "href": quick_water_systems_href
                }
            }
        },
        {
            "name": "MasterLightAction",

            "title": "Interior Lights",
            # "subtext": masterlight_subtext,
            "subtext": interior_lights,

            'type': 'Simple',
            'Simple': {
                # 'onOff': masterlight_onOff
                'onOff': interior_light_group.state.onOff
            },

            'actions': [
                'action_default',
                'action_longpress'
            ],
            "action_default": {
                "type": "api_call",
                "action": {
                    "href": f"/api/lighting/lg/{INT_GROUP_ID}/state",
                    "type": "PUT",
                    "params": {
                        "$onOff": 'int'
                    }
                }
            },
            "action_longpress": {
                "type": "navigate",
                "action": {
                    "href": "/home/lighting"
                }
            }
        },
        {
            "name": "MasterLightAction",

            "title": "Exterior Lights",
            "subtext": exterior_lights,

            'type': 'Simple',
            'Simple': {
                'onOff': exterior_light_group.state.onOff
            },

            'actions': [
                'action_default',
                'action_longpress'
            ],
            "action_default": {
                "type": "api_call",
                "action": {
                    "href": f"/api/lighting/lg/{EXT_GROUP_ID}/state",
                    "type": "PUT",
                    "params": {
                        "$onOff": 'int'
                    }
                }
            },
            "action_longpress": {
                "type": "navigate",
                "action": {
                    "href": "/home/lighting"
                }
            }
        },
        # {
        #     # TODO: Add new asset and name
        #     "name": "RoofFanAction",

        #     "title": roof_fan.attributes.get('name', 'Roof Vent'),
        #     "subtext": roof_fan_subtext,

        #     'type': 'Simple',
        #     'Simple': {
        #         'onOff': roof_fan_onoff
        #     },

        #     'actions': [
        #         'action_default',
        #         'action_longpress'
        #     ],
        #     "action_default": {
        #         "type": "api_call",
        #         "action": {
        #             "href": f"/api/climate/rv/{fan_id}/quickaction",
        #             "type": "PUT",
        #             "params": {
        #                 "$onOff": 'int'
        #             }
        #         }
        #     },
        #     "action_longpress": {
        #         "type": "navigate",
        #         "action": {
        #             "href": "/home/climatecontrol"
        #         }
        #     }
        # }
    ]


    return quick_actions


def get_levels(request):
    # Parse configs as relevant
    current_water_unit = request.app.config['watersystems'].get(
        'VolumeUnitPreference',
        WATER_UNIT_GALLONS
    )

    levels = []
    # Get list of levels
    # Water Levels
    # Battery Levels
    # Others ?
    bms = request.app.hal.energy.handler.battery_management[1]
    house_battery_soc = bms.state.soc

    try:
        soc_text = get_tank_level_text({'lvl': house_battery_soc})
    except ValueError as err:
        print(err)
        soc_text = '--'

    # print('SOC Text', soc_text, house_battery_soc)

    bms_voltage = '-- V'

    if bms.state.vltg is not None:
        bms_voltage = f'{bms.state.vltg:.1f} V'

    levels.append(
        {
            "name": "HouseBatteryLevel",
            'type': 'simpleLevel',
            'state': {
                'max': 100,
                'min': 0,
                'current_value': house_battery_soc,
                'unit': '%',
                'level_text': soc_text
            },

            "title": "House Battery",
            "subtext": bms_voltage,

            'actions': ['action_default', ],
            "action_default": {
                "type": "navigate",
                "action": {
                    "href": "/home/ems"
                }
            }
        }
    )

    if hasattr(request.app.hal.energy.handler, 'fuel_tank'):
        propane = request.app.hal.energy.handler.fuel_tank[1]
        propane_name = propane.attributes.get('name')

        # TODO: Figure out how to handle the None values in the model itself
        tank_state = request.app.hal.watersystems.tank_readout(
            propane,
            current_water_unit
        )
        print('Tank state', tank_state)
        fill = tank_state.get('fill')
        rounded_fill = fill
        if fill is not None:
            rounded_fill = round(fill)
            print('Rounded Fill', rounded_fill)

        tank_fill_str = '--' if fill is None else f"{rounded_fill:.0f}"
        if tank_state.get('level_raw') == -1:
            tank_subtext = f"NA {tank_state.get('unit')}"
        else:
            tank_subtext = f"{tank_fill_str} {tank_state.get('unit')}"

        tank_level = tank_state.get('level_raw')
        if tank_level is None:
            tank_level = 0.0
        else:
            tank_level = math.floor(tank_level)

        levels.append(
            {
                "name": "PropaneTankLevel",
                "type": "simpleLevel",
                'state': {
                    "max": 100,
                    "min": 0,
                    "current_value": tank_level,
                    "unit": "%",
                    "level_text": get_tank_level_text(propane)
                },
                "title": propane_name,
                "subtext": tank_subtext,
                "actions": ['action_default',],
                'action_default': {
                    'type': 'navigate',
                    'action': {
                        'href': '/home/ems'
                    }
                }
            }
        )

    tanks = request.app.hal.watersystems.handler.get_tanks()

    for instance, tank in tanks.items():
        tank_state = request.app.hal.watersystems.tank_readout(
            tank,
            current_water_unit
        )
        fill = tank_state.get('fill')
        rounded_fill = fill
        # if fill is not None:
        #     rounded_fill = round(fill)
        #     print('Rounded Fill', rounded_fill)

        tank_fill_str = '--' if fill is None else f"{rounded_fill:.0f}"
        if tank_state.get('level_raw') == -1:
            tank_subtext = f"NA {tank_state.get('unit')}"
        else:
            tank_subtext = f"{tank_fill_str} {tank_state.get('unit')}"

        tank_level = tank_state.get('level_raw')
        if tank_level is None:
            tank_level = 0.0
        else:
            tank_level = math.floor(tank_level)

        uiclass = '{}TankLevel'.format(
            tank.attributes.get('type', 'NA').capitalize()
        )

        tank_name = tank.attributes.get('name')

        levels.append(
            {
                "name": uiclass,
                # "name": "FreshTankLevel",
                "type": "simpleLevel",
                'state': {
                    "max": 100,
                    "min": 0,
                    "current_value": tank_level,
                    "unit": "%",
                    "level_text": get_tank_level_text(tank)
                },
                "title": tank_name,
                "subtext": tank_subtext,
                "actions": ['action_default',],
                'action_default': {
                    'type': 'navigate',
                    'action': {
                        'href': '/home/watersystems'
                    }
                }
            }
        )

    return levels


def get_climate_control(request):
    '''Create climate control widget data.'''
    current_temp_unit = request.app.config.get('climate', {}).get('TempUnitPreference', TEMP_UNIT_FAHRENHEIT)
    ui_temp_unit = TEMP_UNITS.get(current_temp_unit, {}).get('short')
    # Get internal temperature
    # internal_temp = request.app.hal.climate.handler.get_actual_temperature(instance=1, unit=current_temp_unit)
    if hasattr(request.app.hal.climate.handler, 'thermostat'):
        thermostat = request.app.hal.climate.handler.thermostat[1]
        internal_temp = thermostat.get_temperature(
            current_temp_unit
        )
        if internal_temp == None:
            internal_temp = '--'

        # hvac_mode = request.app.hal.climate.handler.get_hvac_mode(zone_id=1)
        # print('Thermostat state', thermostat.state)

        if thermostat.state.onOff == EventValues.OFF:
            # Set a couple of flags and set it to OFF
            hvac_mode = EventValues.OFF
            climate_system_mode = EventValues.OFF
        else:
            hvac_mode = thermostat.state.setMode

        hvac_mode_short_name = HVAC_MODES.get(hvac_mode).get('short')
        cur_hvac_mode_long_name = HVAC_MODES.get(hvac_mode).get('long')

        # print(hvac_mode, hvac_mode_short_name, cur_hvac_mode_long_name)

        set_temp_cool = thermostat.get_tempCool(current_temp_unit)
        set_temp_heat = thermostat.get_tempHeat(current_temp_unit)
        set_temp = set_temp_cool

        if hvac_mode == EventValues.COOL:
            set_temp = set_temp_cool
        elif hvac_mode == EventValues.HEAT:
            set_temp = set_temp_heat

        # set_temp = get_displayed_temp(set_temp, current_temp_unit)
        # set_temp_cool = get_displayed_temp(set_temp_cool, current_temp_unit)
        # set_temp_heat = get_displayed_temp(set_temp_heat, current_temp_unit)

        if hasattr(request.app.hal.climate.handler, 'air_conditioner'):
            ac_1 = request.app.hal.climate.handler.air_conditioner[1]
            ac_status = ac_1.state
            # prefix_log(wgo_logger, 'XXXXXXX:', ac_fan_status)
            # TODO: How does fanSpd update ?
            # current_ac_fan_state = ac_status.get('fanSpd')
            current_ac_fan_state = ac_status.fanMode

            # print('CUR FAN State', current_ac_fan_state)
            if current_ac_fan_state in (EventValues.OFF, EventValues.AUTO, None):
                ac_fan_active = 0
            else:
                ac_fan_active = 1

            current_mode_text = 'Off'

            # TODO: Implement
            hvac_current_mode = thermostat.state.mode
            if thermostat.state.onOff != EventValues.OFF:
                # prefix_log(wgo_logger, f'{__name__}.[CLIMATE]', f'Climate Mode: {hvac_mode}, Current Mode: {hvac_current_mode}')
                if hvac_current_mode == EventValues.COOL:
                    current_mode_text = f'Cooling to {set_temp_cool} °{ui_temp_unit}'
                elif hvac_current_mode == EventValues.HEAT:
                    current_mode_text = f'Heating to {set_temp_heat} °{ui_temp_unit}'
                elif hvac_current_mode == EventValues.STANDBY:
                    # Check main mode
                    if hvac_mode == EventValues.HEAT:
                        current_mode_text = f'Set to {set_temp_heat} °{ui_temp_unit}'
                    elif hvac_mode == EventValues.COOL:
                        current_mode_text = f'Set to {set_temp_cool} °{ui_temp_unit}'
                    elif hvac_mode == EventValues.AUTO:
                        current_mode_text = f'Temp Range\n{set_temp_heat} ° - {set_temp_cool} °{ui_temp_unit}'
                    elif hvac_mode == EventValues.OFF:
                        # TODO: Figure out when this is supposed to be happening
                        current_mode_text = 'Off'
                    else:
                        print(f'[CLIMATE]: Current HVAC Mode: {hvac_mode}')
                        current_mode_text = 'ELSE'

        else:
            # We do not have an air condition, which is currently expected to be present
            hvac_current_mode = EventValues.STANDBY
            current_mode_text = 'NO AC'
            ac_fan_active = 'FALSE'
            hvac_mode = EventValues.OFF
            hvac_mode_short_name = 'ERR'

        climate_actions = [
            {
                'type': 'navigate',
                'action': {
                    'href': '/home/climatecontrol'
                },
                'active': True,
                'name': 'HomeClimateNavigation'
            },
        ]
        # If we are currently in not in OFF or AUTO
        # we show increment/decrement options
        if hvac_mode == EventValues.HEAT or hvac_mode == EventValues.COOL:
            climate_actions.extend(
                [
                    {
                        'type': 'api_call',
                        'action': {
                            'href': '/api/climate/zones/1/temp',
                            'type': 'PUT',
                            'params': {
                                'mode': hvac_mode,
                                '$setTemp': 'float'
                            }
                        },
                        # TODO: Check if temp can go lower  that current
                        'active': True,
                        'name': 'HomeClimateDecreaseTemp'
                    },
                    {
                        'type': 'api_call',
                        'action': {
                            'href': '/api/climate/zones/1/temp',
                            'type': 'PUT',
                            'params': {
                                'mode': hvac_mode,
                                '$setTemp': 'float'
                            }
                        },
                        # TODO: Check if temp can go lower  that current
                        'active': True,
                        'name': 'HomeClimateIncreaseTemp'
                    }
                ]
            )
        elif hvac_mode == EventValues.FAN_ONLY:
            fan_only_speed = request.app.hal.climate.handler.air_conditioner[1].state.fanMode
            # Check if FAN is off / low / high
            # TODO: Get this from the HW Layer (the ids)
            if fan_only_speed == EventValues.LOW:
                current_mode_text = 'Fan on Low'
                climate_actions.extend(
                    [
                        {
                            'type': 'api_call',
                            'action': {
                                'href': '/api/climate/ac/1/state',
                                'type': 'PUT',
                                'params': {
                                    'fanMode': EventValues.OFF
                                }
                            },
                            # TODO: Check if temp can go lower  that current
                            'active': True,
                            'name': 'HomeClimateDecreaseFanSpeed'
                        },
                        {
                            'type': 'api_call',
                            'action': {
                                'href': '/api/climate/ac/1/state',
                                'type': 'PUT',
                                'params': {
                                    'fanMode': EventValues.HIGH
                                }
                            },
                            # TODO: Check if temp can go lower  that current
                            'active': True,
                            'name': 'HomeClimateIncreaseFanSpeed'
                        }
                    ]
                )
            # TODO: Generate the steps as supported by the HW 848EC < 1.4 supports off, low, high
            # 524T supports off, low, medium, high
            # elif current_ac_fan_state == EventValues.MEDIUM:
            #     current_mode_text = 'Fan on Medium'
            #     climate_actions.extend(
            #         [
            #             {
            #                 'type': 'api_call',
            #                 'action': {
            #                     'href': '/api/climate/zones/1/acfan/1',
            #                     'type': 'PUT',
            #                     'params': {
            #                         'item': 'FanSpeed',
            #                         # TODO: Read the current speed
            #                         'value': EventValues.LOW
            #                     }
            #                 },
            #                 # TODO: Check if temp can go lower  that current
            #                 'active': True,
            #                 'name': 'HomeClimateDecreaseFanSpeed'
            #             },
            #             {
            #                 'type': 'api_call',
            #                 'action': {
            #                     'href': '/api/climate/zones/1/acfan/1',
            #                     'type': 'PUT',
            #                     'params': {
            #                         'item': 'FanSpeed',
            #                         # TODO: Read the current speed
            #                         'value': EventValues.HIGH
            #                     }
            #                 },
            #                 # TODO: Check if temp can go lower  that current
            #                 'active': True,
            #                 'name': 'HomeClimateIncreaseFanSpeed'
            #             }
            #         ]
            #     )
            elif fan_only_speed == EventValues.HIGH:
                current_mode_text = 'Fan on High'
                climate_actions.extend(
                    [
                        {
                            'type': 'api_call',
                            'action': {
                                'href': '/api/climate/ac/1/state',
                                'type': 'PUT',
                                'params': {
                                    'fanMode': EventValues.LOW
                                }
                            },
                            # TODO: Check if temp can go lower  that current
                            'active': True,
                            'name': 'HomeClimateDecreaseFanSpeed'
                        },
                        {
                            'type': 'dismiss',
                            'action': None,
                            # TODO: Check if temp can go lower  that current
                            'active': False,
                            'name': 'HomeClimateIncreaseFanSpeed'
                        }
                    ]
                )
            else:
                current_mode_text = 'Fan Off'
                climate_actions.extend(
                    [
                        {
                            'type': 'none',
                            'action': None,
                            # TODO: Check if temp can go lower  that current
                            'active': False,
                            'name': 'HomeClimateDecreaseFanSpeed'
                        },
                        {
                            'type': 'api_call',
                            'action': {
                                'href': '/api/climate/ac/1/state',
                                'type': 'PUT',
                                'params': {
                                    'fanMode': EventValues.LOW
                                }
                            },
                            # TODO: Check if temp can go lower  that current
                            'active': True,
                            'name': 'HomeClimateIncreaseFanSpeed'
                        }
                    ]
                )

        else:
            pass
            # print('HVAC MODE not set', hvac_mode)

        if hvac_mode is None:
            climate_system_mode = None
            # Set mode to AUTO
            # thermostat.state.mode = EventValues.AUTO

        else:
            climate_system_mode = HVACModeEnum(hvac_mode).name

        if hvac_current_mode is None:
            # Set to standby
            climate_current_mode = HVACModeEnum(hvac_current_mode).name
        else:
            climate_current_mode = None

        widget = ClimateWidget(
            setTemp=set_temp,
            setTempText='--',
            interiorTemp=internal_temp,
            interiorTempText=f'{internal_temp}',
            # title=f'{internal_temp}',
            unit=' °' + TEMP_UNITS.get(current_temp_unit, {}).get('short'),
            actions=climate_actions,
            climateSystemMode=climate_system_mode,
            climateCurrentMode=climate_current_mode,
            climateModeText=hvac_mode_short_name,
            climateModeSubtext=current_mode_text,
            fanState=[
                {
                    'name': 'ACFan',
                    'active': ac_fan_active
                },
            ]
        )
    else:
        widget = None

    return widget


@router.get('/')
@router.get('/home')
async def home(request: Request, http_response: Response) -> dict:
    '''Get home screen items.'''
    print('[UI][API] Home API GET called')
    http_response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    http_response.headers['Pragma'] = 'no-cache'
    http_response.headers['Expires'] = '0'

    # print('Request Headers', request.headers)

    # Check if we are vanilla or a specific floorplan
    if request.app.hal.floorPlan == 'VANILLA':
        return {
            'redirect': '/home/manufacturing',
            'motd': {
                'iconType': 'ASSET',
                'icon': 'WGO',
                'title': 'Winnebago RV - Manufacturing',
                'text': 'VANILLA Floorplan',
                'actions': None,
                'name': 'HomeMotdMessage'
            }
        }
    else:
        pass
        # print('Detected floorplan', request.app.hal.floorPlan)

    state = request.app.state.get('home', {})

    response = {}
    response['top'] = get_top()
    response['left-bar'] = get_left_bar(request.app)
    response['quickactions'] = get_quick_action(
        request.app.hal,
        request.app.config.get('quickactions', [])
    )

    response['levels'] = get_levels(request)
    climate = get_climate_control(request)

    response['climateControlNew'] = climate

    activity_settings = request.app.config.get('activity_settings')
    timezone = request.app.config.get('timezone').get("TimeZonePreference")

    polling_interval = {
        k: v for k, v in activity_settings.items() if k in [
            'activePollingInterval',
            'offPollingInterval'
        ]
    }

    # response['activity_settings'] = activity_settings
    response['settings'] = {
        'timezone': timezone,
        'activity': polling_interval,
        'screenMode': request.app.config['settings'].get('UIScreenMode', 'LIGHT'),
        'isProtected': activity_settings.get('isProtected', False),
        'passcodeAPI': {
            'type': 'PUT',
            'href': '/api/system/passcode',
            'params': {
                'passcode': 'int'
            }
        }
    }
    response['motd'] = request.app.get_motd(request.app)

    response['drawer'] = {
        'enabled': True,
    }
    # TODO:  This is a temp fix - the UI needs to show higher alerts first
    higher_alerts = any(item['level'] < NotificationPriority.Pet_Minder_Warning for item in request.app.notifications)

    if hasattr(request.app.hal.features.handler, 'pet_monitoring'):
        pet_mon = request.app.hal.features.handler.pet_monitoring[1]
        if pet_mon.state.onOff == EventValues.ON and higher_alerts is False:
            # print('Adding PETMON to home as ', pet_mon.state.enabled)
            response['petmonitoring'] = {
                'top': {
                    'title': 'ON' if pet_mon.state.enabled == EventValues.ON else 'OFF',
                    'state': {
                        'enabled': pet_mon.state.enabled,
                    },
                    'actions': {
                        'TAP': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/features/pm/1/state',
                                'type': 'PUT',
                                'params': {
                                    'enabled': EventValues.ON if pet_mon.state.enabled == EventValues.OFF else EventValues.OFF
                                }
                            }
                        }
                    }
                }
            }
            if pet_mon.state.enabled == EventValues.ON:
                response['petmonitoring']['status'] = request.app.config.get('features', {}).get('petmonitoring')


    new_state = response

    if new_state != state:
        # prefix_log(wgo_logger, __name__, 'Home UI state change detected')
        request.app.state['home'] = response

    return response


@router.get('/top', response_model=HeaderWidgets)
async def top_icons() -> dict:
    '''Get icons such as wifi, bt and their state.'''
    current_icons = mock_db.get('top-icons', [])
    # Modify mock-db entry for notifications
    index = -1
    for i, x in enumerate(current_icons):
        if x.get('name') == 'TopNotifications':
            notifications = mock_db.get('notifications')
            critical = 0
            warning = 0
            info = 0
            for item in notifications:
                level = item.get('level')
                if level == NotificationPriority.Critical:
                    critical += 1
                elif level == NotificationPriority.Warning:
                    warning += 1
                elif level == NotificationPriority.Information:
                    info += 1
                # level = item.get('level')
                # if level == 'CRITICAL':
                #     critical += 1
                # elif level == 'WARNING':
                #     warning += 1
                # else:
                #     info += 1

            current_icons[i]['data'] = [
                {
                    "key": "NOTIFICATION_COUNT",
                    "value": critical + warning + info
                },
                {
                    "key": "NOTIFICATIONS_CRITICAL",
                    "value": critical
                },
                {
                    "key": "NOTIFICATIONS_WARNING",
                    "value": warning
                },
                {
                    "key": "NOTIFICATIONS_INFO",
                    "value": info
                }
            ]

    widgets = HeaderWidgets(
        icons=current_icons
    )

    return widgets


# TODO: Retire this, after verifying it does not miss anywhere
# @router.get('/quickactions')
# async def quick_action() -> dict:
#     '''Get list of quick actions.'''
#     # quick_action_list = mock_db.get('quick-actions', [])
#     return get_quick_action()
#     # return quick_action_list


# TODO: Retire this, after verifying it does not miss anywhere
# @router.get('/levels', response_model=List[LevelWidget])
# @router.get('/levels')
# async def level() -> dict:
#     '''Get list of level details.'''
#     level_list = mock_db.get('level-states', [])
#     return level_list


# TODO: Retire this, after verifying it does not miss anywhere
# @router.get('/slider', response_model=List[Widget])
# @router.get('/slider')
# async def ui_slider() -> dict:
#     '''Get slider components.'''
#     quick_actions = mock_db.get('quick-actions', [])
#     quick_actions = [
#         {
#             'type': 'QUICK_ACTION',
#             'widget': x
#         } for x in quick_actions
#     ]

#     return quick_actions


@router.get('/motd')
async def get_message_of_the_day(request: Request, http_response: Response) -> dict:
    return RedirectResponse(url=f"/home/functionaltests/", status_code=303)

    '''Endpoint for notification retrieval.'''
    http_response.headers['cache-control'] = 'no-store'
    motd = {
        'iconType': 'ASSET',
        'icon': 'WGO',
        'title': 'Welcome to Winnebago',
        'text': 'Good Morning ! 🚙',
        'actions': None,
        'name': 'HomeMotdMessage'
    }

    return motd

# TODO: Move this to test harness
# @router.get('/test_reload_mock_db')
# async def test_reload_mock_db():
#     reload_mock_db()
