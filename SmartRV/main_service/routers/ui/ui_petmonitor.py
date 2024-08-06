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

DEGREE_STEPS_FAHRENHEIT = 1.0
DEGREE_STEPS_CELSIUS = 0.5


BASE_URL = os.environ.get("WGO_MAIN_API_BASE_URL", "")

router = APIRouter(prefix='/petmonitoring', tags=['PETMON',])


@router.get('/')
@router.get('')
async def ui_petmonitoring(request: Request, http_response: Response):
    '''Provides UI with state of petmonitoring and features to be displayed.'''
    http_response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    http_response.headers["Pragma"] = "no-cache"
    http_response.headers["Expires"] = "0"

    # NEW
    current_temp_unit = request.app.config.get("climate", {}).get(
        "TempUnitPreference", TEMP_UNIT_FAHRENHEIT
    )

    # Feature Dependencies
    PET_MON_INSTANCE = 1
    pet_mon = request.app.hal.features.handler.pet_monitoring[PET_MON_INSTANCE]

    # Energy dependencies
    # Generator

    # Climate Dependencies

    # TODO: Fix detection of outdoor and indoor zone 1
    # TODO: How to handle multiple zones
    climate_indoor_instance = 1
    climate_outdoor_instance = 2

    for instance, thermostat in request.app.hal.climate.handler.thermostat.items():
        if thermostat.attributes.get('type') == 'MAIN':
            climate_indoor_instance = instance
        elif thermostat.attributes.get('type') == 'OUTDOOR':
            climate_outdoor_instance = instance

    climate_indoor = request.app.hal.climate.handler.thermostat[
        climate_indoor_instance
    ]
    climate_outdoor = request.app.hal.climate.handler.thermostat[
        climate_outdoor_instance
    ]

    outdoor_temp = climate_outdoor.get_temperature(
        unit=current_temp_unit
    )
    if outdoor_temp is None:
        outdoor_temp_text = (
            f'Current Outdoor Temp: --°{TEMP_UNITS[current_temp_unit]["short"]}'
        )
    else:
        outdoor_temp_text = (
            f'Current Outdoor Temp: {outdoor_temp}° {TEMP_UNITS[current_temp_unit]["short"]}'
        )

    # Assemble feature

    features_state_text = 'ERR'
    features_enabled = False
    features_text = 'ERROR: We are missing some data to enable the Pet Minder feature.'
    if pet_mon.state.onOff == EventValues.ON:
        if pet_mon.state.enabled == EventValues.ON:
            features_state_text = 'Enabled - Alerts ON'
        else:
            features_state_text = 'Enabled - Alerts OFF'

        features_enabled = True
        features_text = 'Pet Minder will appear on your dashboard. You can now turn alerts on or off from there.'
    elif pet_mon.state.onOff == EventValues.OFF:
        features_state_text = 'Disabled'
        features_enabled = False
        features_text = 'Pet Minder will not appear on your dashboard. Enable the feature here to turn alerts on or off from there.'

    max_temp = pet_mon.state.maxTemp
    min_temp = pet_mon.state.minTemp


    if current_temp_unit == 'F':
        step = DEGREE_STEPS_FAHRENHEIT
        try:
            max_temp = _celcius_2_fahrenheit(max_temp)
        except TypeError:
            pass
        # Report as None

        try:
            min_temp = _celcius_2_fahrenheit(min_temp)
        except TypeError:
            pass
    else:
        step = DEGREE_STEPS_CELSIUS
        # Report as None

    pet_comfort_range = {
        'title': 'Pet Minder',
        'subtext': features_state_text,
        'type': 'Simple',
        'state': {
            'onOff': pet_mon.state.onOff
        },
        'enabled': features_enabled,
        'actions': {
            'TAP': {
                "type": "api_call",
                "action": {
                    "href": f"{BASE_URL}/api/features/pm/{PET_MON_INSTANCE}/state",
                    "type": "PUT",
                    "params": {
                        "$onOff": "int"
                    },
                }
            }
        },
        'petMonitoring': {
            'title': 'Pet Comfort Range',
            'text': features_text,
            'name': 'PetMonComfortRangeSetting',
            'type': 'PET_MON_COMFORT_RANGE',
            'items': [
                {
                    'title': 'MAX TEMP',
                    'name': 'PetMonMaxTempSetting',
                    'type': 'TEMP_SETTING_HOT',
                    'value': max_temp,
                    'step': step,
                    'min': 0.0,     #
                    'max': 100.0,   #
                    'state': {
                        'unit': current_temp_unit,
                        'maxTemp': max_temp
                    },
                    'actions': {
                        'CHANGE': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/features/pm/{PET_MON_INSTANCE}/state',
                                'type': 'PUT',
                                'params': {
                                    '$maxTemp': 'float',
                                    'unit': current_temp_unit
                                }
                            }
                        }
                    }
                },
                {
                    'title': 'MIN TEMP',
                    'name': 'PetMonMinTempSetting',
                    'type': 'TEMP_SETTING_COLD',
                    'value': min_temp,
                    'step': step,
                    'min': 0.0,     #
                    'max': 100.0,   #
                    'state': {
                        'unit': current_temp_unit,
                        'minTemp': min_temp
                    },
                    'actions': {
                        'CHANGE': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/features/pm/{PET_MON_INSTANCE}/state',
                                'type': 'PUT',
                                'params': {
                                    '$minTemp': 'float',
                                    'unit': current_temp_unit
                                }
                            }
                        }
                    }
                }
            ]
        }
    }

    pet_mon_disclaimer = {
        'type': 'SUPPORT_TEXT',     # Support text is shown in between elements
        'text': '''Receive alerts when the RV's temperature is outside of the pet comfort range, energy resources are updated, and connection is lost.'''
    }

    indoor_temp = climate_indoor.get_temperature(current_temp_unit)
    if indoor_temp is None:
        indoor_temp = '--'

    response = {
        "overview": {
            "title": 'Pet Minder',
            "subtext": outdoor_temp_text,
            "settings": None,   # No settings in this feature
            # {
            #     "href": f"{BASE_URL}/ui/climate/settings", "type": "GET"},
            "bottom_widget": {
                "text": indoor_temp,
                "sidetext": "°" + TEMP_UNITS[current_temp_unit]["short"],
                "subtext": "Current Indoor Temp",
            },
        },
        "features": [],
        "notifications": [],
    }

    response['features'].append(
        pet_comfort_range
    )

    response['features'].append(
        pet_mon_disclaimer
    )

    # TODO: Bring in with auto generator start feature, which likely is a component
    # Check if a generator is present
    if hasattr(request.app.hal.energy.handler, 'generator'):
        # Get the generator
        GENERATOR_DEFAULT_INSTANCE = 1
        generator = request.app.hal.energy.handler.generator[
            GENERATOR_DEFAULT_INSTANCE
        ]

        show = False
        for component in generator.relatedComponents:
            # TODO: Below type ID is only made up and does not yet exist
            if component['componentTypeId'] == 'GeneratorAutoStartFeature':
                # Do something else here to identify the needed auto start feature
                show = True
                break

        if show is True:
            # Get related auto start component
            # Get the related
            auto_gen_start = {
                'title': 'Auto Generator Start',
                'subtext': 'NA',
                'type': 'Simple',
                'state': {
                    'onOff': pet_mon.state.onOff
                },
                'actions': {
                    'TAP': {
                        "type": "api_call",
                        "action": {
                            "href": f"{BASE_URL}/api/features/pm/{PET_MON_INSTANCE}/state",
                            "type": "PUT",
                            "params": {
                                "$onOff": "int"
                            },
                        }
                    }
                }
            }
            response['features'].append(
                auto_gen_start
            )

    return response


@router.get("/settings")
async def get_settings(request: Request):
    raise HTTPException(404, {'msg': 'Setting not implemented for Pet Monitoring'})
