from typing import Optional, List
import os
import math
import logging
import math

from copy import deepcopy

wgo_logger = logging.getLogger("main_service")

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from main_service.components.climate import ACBasicState

from pydantic import BaseModel


# from main_service.modules.hardware.hal import hw_layer

from main_service.modules.constants import (
    TEMP_UNITS,
    TEMP_UNIT_PREFERENCE_KEY,
    TEMP_UNIT_FAHRENHEIT,
    HVAC_MODE_AUTO,
    HVAC_MODES,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    _celcius_2_fahrenheit,
)

from main_service.modules.logger import prefix_log

from main_service.modules.ui_helper import (
    get_temp_unit_preferences,
    get_ac_modes,
    get_fan_options,
)

from common_libs.models.common import (
    EventValues,
    UIStyles
)
from common_libs.models.notifications import request_to_iot

# UI Business logic
MINIMUM_BATTERY_WARNING = 20    # %
MINIMUM_PROPANE_TANK_LVL_WARNING = 20   # %


BASE_URL = os.environ.get("WGO_MAIN_API_BASE_URL", "")

router = APIRouter(prefix="/climate", tags=["CLIMATE", "HVAC"])


def get_schedules(app):
    """Get schedules from main app config."""
    schedules = app.config.get(
        "climate_schedules",
        # Default settings if no config is present
        [
            {
                "id": 0,
                "name": "scheduleWake",
                "title": "Wake",
                "startHour": None,
                "startMinute": None,
                # Options for startTimeMode: 'AM, 'PM', '24H', None
                "startTimeMode": None,
                "setTempHeat": None,
                "setTempCool": None,
            },
            {
                "id": 1,
                "name": "scheduleAway",
                "title": "Away",
                "startHour": None,
                "startMinute": None,
                "startTimeMode": None,
                "setTempHeat": None,
                "setTempCool": None,
            },
            {
                "id": 2,
                "name": "scheduleAtcamp",
                "title": "At Camp",
                "startHour": None,
                "startMinute": None,
                "startTimeMode": None,
                "setTempHeat": None,
                "setTempCool": None,
            },
            {
                "id": 3,
                "name": "scheduleSleep",
                "title": "Sleep",
                "startHour": None,
                "startMinute": None,
                "startTimeMode": None,
                "setTempHeat": None,
                "setTempCool": None,
            },
        ],
    )

    return schedules


# def get_temp_unit_preferences(units, selected):
#     '''Assemble list for UI of possible options and their value.
#     [
#         {
#             'key': 'Fahrenheit / F',
#             'value': 0,
#             'selected': True
#         },
#         {
#             'key': 'Celsius / C',
#             'value': 1,
#             'selected': False
#         }
#     ]
#     '''
#     ui_result = []
#     for key_value, names in units.items():
#         result = {
#             'key': f'{names["long"]} / {names["short"]}',
#             'value': key_value,
#             'selected': True if key_value == selected else False
#         }
#         ui_result.append(result)

#     return ui_result


# def get_ac_modes(modes, selected):
#     '''
#     'options': [
#         {
#             'key': EventValues.AUTO,
#             'value': 0,
#             'selected': True
#         },
#         {
#             'key': EventValues.HEAT,
#             'value': 1,
#             'selected': False
#         },
#         {
#             'key': 'Cool',
#             'value': 2,
#             'selected': False
#         }
#     ],
#     '''
#     ui_result = []
#     for key_value, names in modes.items():
#         result = {
#             'key': f'{names["short"]}',
#             'value': key_value,
#             'selected': True if key_value == selected else False
#         }
#         ui_result.append(result)

#     return ui_result


@router.get("/")
@router.get("")
async def gui_climate(request: Request, http_response: Response):
    http_response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    http_response.headers["Pragma"] = "no-cache"
    http_response.headers["Expires"] = "0"
    current_temp_unit = request.app.config.get("climate", {}).get(
        "TempUnitPreference", TEMP_UNIT_FAHRENHEIT
    )
    # runClimate = request.app.hal.climate.handler.state['climate_algo_enabled']

    climate_zones = [
        {
            "id": 1,
            "fans": [
                {
                    "id": 1, "name": "Dometic Roof Fan"
                },
            ],
        },
    ]

    # Temp helper
    climate_zone = climate_zones[0]
    climate_zone_id = climate_zone.get("id")
    # climate_zone_onOff = request.app.hal.climate.handler.get_zone(1)
    # climate_zone_onOff = 1 if climate_zone_onOff == None else climate_zone_onOff
    climate_zone_onOff = request.app.hal.climate.handler.thermostat[1].state.onOff
    climate_fan_id = 1
    he_id = 1
    # get house battery level
    house_battery_soc = request.app.hal.energy.handler.battery_management[1].state.soc

    if house_battery_soc is None:
        house_battery_hexcode = UIStyles.BAD
        house_battery_soc_text = '--'
    else:
        if house_battery_soc <= MINIMUM_BATTERY_WARNING:
            house_battery_hexcode = UIStyles.BAD
        else:
            house_battery_hexcode = UIStyles.GOOD
        house_battery_soc = math.floor(house_battery_soc)
        house_battery_soc_text = house_battery_soc

    # Get LP level
    if hasattr(request.app.hal.energy.handler, 'fuel_tank'):
        propane = request.app.hal.energy.handler.fuel_tank[1]

        if propane.state.lvl is None:
            propane_lvl = None
            propane_hexcode = UIStyles.BAD
            propane_lvl_text = '--'
        else:
            propane_lvl = math.floor(propane.state.lvl)
            if propane_lvl <= MINIMUM_PROPANE_TANK_LVL_WARNING:
                propane_hexcode = UIStyles.BAD
            else:
                propane_hexcode = UIStyles.GOOD

            propane_lvl_text = propane_lvl
    else:
        propane = None
        propane_lvl = None
        propane_hexcode = None
        propane_lvl_text = '--'

    if not hasattr(request.app.hal.climate.handler, 'air_conditioner'):
        ac_status = {}
    else:
        ac_status = request.app.hal.climate.handler.air_conditioner[1].state.dict()

    heat_source_status = request.app.hal.climate.handler.heater[1].state.dict()

    climate_zone_temp_settings = request.app.hal.climate.handler.get_climate_zone_temp_config(
        climate_zone_id, temp_unit=current_temp_unit
    )

    thermostat = request.app.hal.climate.handler.thermostat[1]

    internal_temp = request.app.hal.climate.handler.thermostat[1].get_temperature(
        current_temp_unit
    )
    if internal_temp is None:
        internal_temp = '--'

    # TODO: Get a standard way of retrieving outdoor temp
    try:
        outdoor_temp = request.app.hal.climate.handler.thermostat[2].get_temperature(
            unit=current_temp_unit
        )
    except Exception as err:
        print(err)
        # Execute the old way
        outdoor_temp = request.app.hal.climate.handler.get_actual_temperature(
            instance=2,
            unit=current_temp_unit
        )

    if outdoor_temp is None:
        outdoor_temp = '--'

    outdoor_temp_text = (
        f"Current Outdoor Temp: {outdoor_temp}°"
        + TEMP_UNITS[current_temp_unit]["short"]
    )

    try:
        current_hvac_mode = request.app.hal.climate.handler.thermostat[1].state.mode
        hvac_mode_text = HVAC_MODES[EventValues(current_hvac_mode)].get("short")
    except Exception as err:
        print("b>" * 35, f"climate curMode mode test {current_hvac_mode}", err)
        hvac_mode_text = "OFF"

    try:
        current_tstat_mode = request.app.hal.climate.handler.thermostat[1].state.setMode
        cur_tstat_text = HVAC_MODES[EventValues(current_tstat_mode)].get("long")

    except Exception as err:
        print("b>" * 35, "climate tstat mode test ", err)
        hvac_mode_text = "OFF"
        cur_tstat_text = "OFF"

    thermostat_text = (
        f"On - {cur_tstat_text} - {hvac_mode_text}"
        if climate_zone_onOff == 1
        else EventValues.OFF.name
    )

    ac_fan_off_option = (
        "Off"
        if current_tstat_mode in (EventValues.FAN_ONLY, EventValues.HEAT)
        else "Auto"
    )

    roof_fans = []
    for fan_id, fan in request.app.hal.climate.handler.roof_vent.items():
        roof_fans.append(
            {
                "title": fan.attributes.get('name'),
                # TODO: Not hardcode the status
                "subtext": "",
                # "subtext": "Closed" if fan.state.dome == EventValues.CLOSED else "Open",
                "type": "AdvancedFan",
                "state": fan.state,
                # TODO: Move this to state
                "AdvancedFan": {
                    # TODO: Change model to not have onOff, but use speed 0 for off, and implicit on if speed is > 0
                    "dome": {
                        "title": '{} Hatch'.format(fan.attributes.get('name', '')),
                        "options": [
                            {
                                "key": "Open",
                                "value": EventValues.OPENED,
                                "selected": False,
                            },
                            {
                                "key": "Close",
                                "value": EventValues.CLOSED,
                                "selected": False,
                            }
                        ]
                    },
                    "fanSpd": {
                        "title": "Fan Speed",
                        "options": [
                            # {
                            #     "key": "Off",
                            #     "value": EventValues.OFF,
                            #     # "selected": fan.state.fanSpd == EventValues.OFF,
                            #     "selected": False,
                            # },
                            {
                                "key": "Low",
                                "value": EventValues.LOW,
                                # "selected": fan.state.fanSpd == EventValues.LOW,
                                "selected": False,
                            },
                            {
                                "key": "Medium",
                                "value": EventValues.MEDIUM,
                                # "selected": fan.state.fanSpd == EventValues.MEDIUM,
                                "selected": False,
                            },
                            {
                                "key": "High",
                                "value": EventValues.HIGH,
                                # "selected": fan.state.fanSpd == EventValues.HIGH,
                                "selected": False,
                            },
                        ]
                    }
                },
                "actions": [
                    "action_default",
                ],
                "action_default": {
                    "type": "api_call",
                    "action": {
                        "href": f"{BASE_URL}/api/climate/rv/{fan_id}/state",
                        "type": "PUT",
                        "params": {
                            "$fanSpd": "int",
                            "$direction": "int",
                            "$dome": "int"
                        },
                    },
                },
            }
        )

    try:
        # Optional heat source
        GE_HE_ID = 2
        ac_heat_component = request.app.hal.climate.handler.heater[GE_HE_ID]
        options = [
            # NOTE: EventValues.AUTO removed due to challenges, need more work
            # EventValues.AUTO,
            EventValues.ELECTRIC,
            EventValues.COMBUSTION
        ]
        # TODO: Make this a high level thing, this is an experiment
        # We provide a string if the name of the event is not what we want
        # If it is OK, then we capitalize it below
        str_dict = {
            EventValues.COMBUSTION: 'Propane'
        }

        heat_source = {
            "text": "Heat Source",
            "type": "ToggleModal",
            'state': {
                'heatSrc': ac_heat_component.state.heatSrc
            },
            "ToggleModal": {
                "active": True,
                "option_param": 'heatSrc',
                "options": [
                    {
                        "key": str_dict.get(x, x.name.lower().capitalize()),
                        "value": x,
                        # TODO: Use the current state rather than the selected
                        # attribute
                        "selected": ac_heat_component.state.heatSrc == x,
                    } for x in options
                ],
                'action_default': {
                    "type": "api_call",
                    "action": {
                        "href": f"{BASE_URL}/api/climate/he/2/state",
                        "type": "PUT",
                        # TODO: add source mode when available
                        "params": {
                            "$heatSrc": "int"
                        },
                    }
                },
                'actions': ['action_default', ],
                # "actions": {
                #     'PRESS': {
                #         "type": "api_call",
                #         "action": {
                #             "href": f"{BASE_URL}/api/climate/he/2/state",
                #             "type": "PUT",
                #             # TODO: add source mode when available
                #             "params": {
                #                 "$heatSrc": "int"
                #             },
                #         }
                #     }
                # },
                "footerText1": f"House Battery {house_battery_soc_text}%",
                "footerColor1": house_battery_hexcode,
                "footerText2": f"Propane Tank {propane_lvl_text}%",
                "footerColor2": propane_hexcode
            }
        }
    except KeyError as err:  # TODO: find a better way to handle options not present
       heat_source = None

    if not hasattr(request.app.hal.climate.handler, 'air_conditioner'):
        ac_fan_extra = None
    else:
        ac_component = request.app.hal.climate.handler.air_conditioner[1]
        if ac_component.type == 'rvc_truma':
            # We have multiple options available
            # TODO: Get this from the schema options rather
            options = [
                {
                    # This alternatively is off in heat mode ??
                    "key": ac_fan_off_option,  # Defines text based on the current mode
                    "value": EventValues.AUTO_OFF,
                    "selected": ac_component.state.fanMode == EventValues.AUTO_OFF
                },
                {
                    "key": "Low",
                    "value": EventValues.LOW,
                    "selected": ac_component.state.fanMode == EventValues.LOW
                },
                {
                    'key': 'Medium',
                    'value': EventValues.MEDIUM,
                    'selected': ac_component.state.fanMode == EventValues.MEDIUM
                },
                {
                    "key": "High",
                    "value": EventValues.HIGH,
                    "selected": ac_component.state.fanMode == EventValues.HIGH
                }
            ]
        else:
            options = [
                {
                    # This alternatively is off in heat mode ??
                    "key": ac_fan_off_option,  # Defines text based on the current mode
                    "value": EventValues.AUTO_OFF,
                    "selected": ac_component.state.fanMode == EventValues.AUTO_OFF
                },
                {
                    "key": "Low",
                    "value": EventValues.LOW,
                    "selected": ac_component.state.fanMode == EventValues.LOW
                },
                {
                    "key": "High",
                    "value": EventValues.HIGH,
                    "selected": ac_component.state.fanMode == EventValues.HIGH
                }
            ]

        if ac_component.state.fanMode == EventValues.AUTO_OFF:
            if thermostat.state.setMode == EventValues.FAN_ONLY:
                footer_text = 'Fan remains off'
            else:
                footer_text = 'Fan will run only when the thermostat is heating or cooling'
        else:
            fan_mode = ac_component.state.fanMode
            if fan_mode is None:
                footer_text = 'Fan will run continuously on the selected speed'
            else:
                print('FAN speed', fan_mode)
                fan_text = EventValues(fan_mode).name.lower()
                footer_text = f'Fan will run continuously on {fan_text}'

        ac_fan_extra = {
            "text": "Fan",
            # TODO: Remove hardcoding
            "subtext": "Select a setting for your fan",
            "footerText": footer_text,
            "type": "ToggleModal",
            "ToggleModal": {
                "active": True,
                "options": options,
                "actions": [
                    "action_default",
                ],
                "action_default": {
                    "type": "api_call",
                    "action": {
                        "href": f"{BASE_URL}/api/climate/ac/{climate_fan_id}/state",
                        "type": "PUT",
                        "params": {
                            "$fanMode": "int"
                        },
                    },
                },
            },
        }

    response = {
        "overview": {
            "title": "Climate Control",
            "subtext": outdoor_temp_text,
            "settings": {"href": f"{BASE_URL}/ui/climate/settings", "type": "GET"},
            "bottom_widget": {
                "text": internal_temp,
                "sidetext": "°" + TEMP_UNITS[current_temp_unit]["short"],
                "subtext": "Current Indoor Temp",
            },
        },
        "climateZones": [
            {
                "thermostat": {
                    "master": {
                        "title": thermostat.attributes.get('name', 'Thermostat'),
                        "subtext": thermostat_text,
                        "type": "Simple",
                        "Simple": {"onOff": climate_zone_onOff},
                        "actions": [
                            "action_default",
                        ],
                        "action_default": {
                            "type": "api_call",
                            "action": {
                                "href": f"{BASE_URL}/api/climate/th/{climate_zone_id}/state",
                                "type": "PUT",
                                "params": {"$onOff": "int"},
                            },
                        },
                    },
                    "climateMode": {
                        "type": "ToggleButton",
                        "ToggleButton": {
                            "options": get_ac_modes(
                                HVAC_MODES, EventValues(current_tstat_mode)
                            ),
                            "actions": [
                                "action_default",
                            ],
                            "action_default": {
                                "type": "api_call",
                                "action": {
                                    "href": f"{BASE_URL}/api/climate/zones/{climate_zone_id}/mode",
                                    "type": "PUT",
                                    "params": {"$value": "int", "item": "ClimateMode"},
                                },
                            },
                        },
                    },
                    "tempBand": {
                        "setTempHeat": climate_zone_temp_settings.get(
                            EventValues.HEAT.name
                        ),
                        "setTempHeatTitle": climate_zone_temp_settings.get(
                            EventValues.HEAT.name
                        ),
                        "setTempHeatText": "°" + TEMP_UNITS[current_temp_unit]["short"],
                        "setTempCool": climate_zone_temp_settings.get(
                            EventValues.COOL.name
                        ),
                        "setTempCoolTitle": climate_zone_temp_settings.get(
                            EventValues.COOL.name
                        ),
                        "setTempCoolText": "°" + TEMP_UNITS[current_temp_unit]["short"],
                        "actions": ["increase_temp", "decrease_temp"],
                        "increase_temp": {
                            "type": "api_call",
                            "action": {
                                "href": f"{BASE_URL}/api/climate/zones/{climate_zone_id}/temp",
                                "type": "PUT",
                                "params": {
                                    # mode 1 / 2 Cool or Heat
                                    "$mode": "str",
                                    "$setTemp": "int",
                                    "unit": "F",
                                },
                            },
                        },
                        "decrease_temp": {
                            "type": "api_call",
                            "action": {
                                "href": f"{BASE_URL}/api/climate/zones/{climate_zone_id}/temp",
                                "type": "PUT",
                                "params": {
                                    # mode 1 / 2 Cool or Heat
                                    "$mode": "str",
                                    "$setTemp": "int",
                                    "unit": "F",
                                },
                            },
                        },
                    },
                    "extras": [
                        heat_source,
                        ac_fan_extra
                    ],
                    "heatSource": heat_source,
                    "acFanSpeed": ac_fan_extra
                }
            }
        ],
        "roofFans": roof_fans,
        "notifications": [],
    }
    if heat_source is None:
        # Remove from thermostat
        # TODO: Rather add and not remove
        try:
            del response['climateZones'][0]['thermostat']['heatSource']
        except KeyError as err:
            print(err)

    return response


@router.get("/AC")
async def get_ac(request: Request) -> dict:
    awe = request.app.hal.climate.handler.get_ac_state()
    return awe


@router.put("/AC")
async def set_ac(request: Request, state: ACBasicState) -> dict:
    print("climate setting ac", state)
    # This function only worked for GE
    air_conditioner = request.app.hal.climate.handler.air_conditioner[1]  # work for either
    result = air_conditioner.set_state(state.dict())

    # result = request.app.hal.climate.handler.set_ac_state(state.dict())

    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": f"/api/climate/ac",
            "body": result
        }
    )

    return result


@router.get("/settings")
async def get_settings(request: Request):
    current_temp_unit = request.app.config.get("climate", {}).get(
        TEMP_UNIT_PREFERENCE_KEY, TEMP_UNIT_FAHRENHEIT
    )
    current_temp_text = TEMP_UNITS.get(current_temp_unit, {}).get("long")
    current_temp_short = TEMP_UNITS.get(current_temp_unit, {}).get("short")
    runClimate = request.app.hal.climate.handler.state['climate_algo_enabled']
    ac_meta = request.app.hal.climate.handler.air_conditioner[1].meta
    heater_meta = request.app.hal.climate.handler.heater[1].meta
    roof_fan_meta = request.app.hal.climate.handler.roof_vent[1].meta
    return {
        "title": "Climate Control Settings",
        "configuration": [
            {
                "title": None,
                "items": [
                    {
                        "title": "Unit Preference",
                        "selected_text": current_temp_text,
                        "options": get_temp_unit_preferences(
                            TEMP_UNITS, current_temp_unit
                        ),
                        "actions": [
                            "action_default",
                        ],
                        "action_default": {
                            "type": "api_call",
                            "action": {
                                "href": f"{BASE_URL}/api/climate/settings",
                                "type": "PUT",
                                "params": {
                                    "$value": "int",
                                    "item": TEMP_UNIT_PREFERENCE_KEY,
                                },
                            },
                        },
                    }
                ],
            }
        ],
        "information": [
            {
                "title": "MANUFACTURER INFORMATION",
                "items": [
                    {
                        "title": "Air Conditioner",
                        "sections": [
                            {
                                "title": None,
                                "items": [
                                    {"key": "Manufacturer", "value": ac_meta.get("manufacturer")},
                                    {"key": "Model", "value": ac_meta.get("model")},
                                    {"key": "Part#", "value": ac_meta.get("part")}
                                ],
                            }
                        ],
                    },
                    {
                        "title": "Heater",
                        "sections": [
                            {
                                "title": None,
                                "items": [
                                    {"key": "Manufacturer", "value": heater_meta.get("manufacturer")},
                                    {"key": "Model", "value": heater_meta.get("model")},
                                    {"key": "Part#", "value": heater_meta.get("part")}
                                ],
                            }
                        ],
                    },
                    {
                        "title": "Roof Fan",
                        "sections": [
                            {
                                "title": None,
                                "items": [
                                    {"key": "Manufacturer", "value": roof_fan_meta.get("manufacturer")},
                                    {"key": "Model", "value": roof_fan_meta.get("model")},
                                    {"key": "Part#", "value": roof_fan_meta.get("part")}
                                ],
                            }
                        ],
                    },
                ],
            }
        ],
        "climate_algo_enabled": runClimate
    }


@router.get("/schedule")
async def get_schedule(request: Request):
    return {
        "title": "Schedule",
        "type": "Simple",
        "Simple": {"onOff": 1},
        "items": get_schedules(request.app),
        "actions": ["action_default", "action_set"],
        "action_default": {
            "type": "api_call",
            "action": {
                "href": f"{BASE_URL}/api/climate/1/schedule/onoff",
                "type": "PUT",
                "params": {"$onOff": "int"},
            },
        },
        "action_set": {
            "type": "api_call",
            "action": {
                "href": f"{BASE_URL}/api/climate/schedule/",
                "type": "PUT",
                "params": {
                    "$id": "int",
                    "$startHour": "int",
                    "$startMinute": "int",
                    "$startTimeMode": "str",  # AM, PM, 24H
                    "$setTempHeat": "int",
                    "$setTempHeat": "int",
                },
            },
        },
    }
