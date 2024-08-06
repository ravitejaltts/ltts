import os
from typing import Optional, List

import math
import time

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from common_libs.models.common import RVEvents, EventValues
from pydantic import BaseModel

from main_service.modules.constants import (
    WATER_UNIT_GALLONS,
)

# from main_service.modules.hardware.hal import hw_layer

from .helper import (
    get_tank_level_text,
    create_ui_lockout
)

BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/generator',
    tags=['GENERATOR', ]
)


@router.get('/', response_model_exclude_none=True)
async def gui_generator(request: Request) -> dict:
    print('hit ui_generator')
    # Settings
    # Battery SoC as a level widget
    BATTERY_INSTANCE = 1
    # INVERTER_INSTANCE = 1
    GENERATOR_INSTANCE = 1
    LP_INSTANCE = 1
    bms = request.app.hal.energy.handler.battery_management[BATTERY_INSTANCE]
    bms_battery_level = bms.state.soc
    house_battery_subtext = '--'
    house_battery_soc = bms_battery_level
    house_battery_soc_text = get_tank_level_text({'lvl': bms_battery_level})

    current_water_unit = request.app.config['watersystems'].get(
        'VolumeUnitPreference',
        WATER_UNIT_GALLONS
    )

    # Get LP level and text
    propane = request.app.hal.energy.handler.fuel_tank[1]
    propane_name = propane.attributes.get('name')

    tank_state = request.app.hal.watersystems.tank_readout(
            propane,
            current_water_unit
        )
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

    # Get generator state
    generator = request.app.hal.energy.handler.generator[GENERATOR_INSTANCE]
    generator.check_lockouts()

    # Detect power source
    generator_power = None
    for _, source in request.app.hal.energy.handler.energy_source.items():
        if source.attributes.get('type') == 'GENERATOR':
            generator_power = source
            break

    lockouts_ui = []
    # Check this from the Lockoutcomponent
    for lock_out in generator.state.lockouts:
        lock = request.app.hal.system.handler.lockouts[lock_out]

        # Lockout needs to be added
        lockouts_ui.append(
            create_ui_lockout(
                generator,
                lock,
                lock_out
            )
        )

    enabled = True
    if generator.state.lockouts:
        enabled = False

    generator_button = 'Start'
    param_mode = EventValues.RUN

    generator_active = EventValues.FALSE
    gen_wattage = '--'

    if generator.state.mode == EventValues.STARTING or generator.state.mode == EventValues.RUN:
        generator_button = 'Stop'
        param_mode = EventValues.OFF
        generator_active = EventValues.TRUE

        if generator_power.state.watts is not None:
            gen_wattage = round(generator_power.state.watts, 0)

    switches = [
        {
            'title': generator_button,
            'type': 'DEADMAN',
            'intervalMs': None,        # DOM to confirm
            'holdDelayMs': 1000,       # DOM to confirm
            'enabled': enabled,        # Dom to review if this can be moved to lockouts in state
            'option_param': 'mode',
            'actions': {
                'PRESS': None,
                'HOLD': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/energy/ge/{GENERATOR_INSTANCE}/state',
                        'type': 'PUT',
                        'param': {
                            'mode': param_mode,
                        }
                    }
                },
                'RELEASE': None,
            }
        }
    ]
    energy_source = vars(generator_power.state)
    energy_source.pop('onOff', None)
    currentRuntime = 0
    if generator.state.lastStartTime is not None and generator.state.mode == EventValues.RUN:
        currentRuntime = (time.time() - generator.state.lastStartTime) / 60

    response = {
        'overview': {
            'title': 'Generator',
            'settings': {
                'href': f'{BASE_URL}/ui/generator/settings',
                'type': 'GET'
            },
            'name': 'AppFeaturePageGenerator',
            'runTime': {
                # TODO: Get Energy Source Generator state
                'hours': "{:.2f}".format(currentRuntime),
                'active': generator_active,
                'subtext': 'Hours'
            },
            'powerStatus': {
                # TODO: Get Energy Source Generator state
                'watts': gen_wattage,
                'active': generator_active,
                'subtext': 'Watts'
            },
            'levels': [
                {
                    "name": "PropaneTankLevel",
                    # "type": propane.componentId,
                    # TODO: Fix holistically to use component ID
                    "type": 'simpleLevel',
                    "state": {
                        "max": 100,
                        "min": 0,
                        "current_value": propane.state.lvl,
                        "unit": "%",
                        "level_text": get_tank_level_text(propane)
                    },
                    "title": propane_name,
                    "subtext": tank_subtext
                }
            ]
        },
        'generators': [
            {
                'title': 'Generator Status',
                'subtext': generator.state.mode.name.capitalize() if hasattr(generator.state.mode, 'name') else 'UNKNOWN',   # Convert the enum value to a localized string at some point
                'type': 'energy.ge_basic',              # Type could be dropping the _basic to associate generally with a ge component ?
                'active': generator_active,
                'state': generator.state,
                'energy': energy_source,
                'lockouts': lockouts_ui,
                'switches': switches
            }
        ],
        'levels': [
            {
                "name": "PropaneTankLevel",
                # "type": propane.componentId,
                # TODO: Fix holistically to use component ID
                "type": 'SimpleLevel',
                "state": {
                    "max": 100,
                    "min": 0,
                    "current_value": propane.state.lvl,
                    "unit": "%",
                    "level_text": get_tank_level_text(propane)
                },
                "title": propane_name,
                "subtext": tank_subtext,
                # "actions": None
            }
        ]
    }

    # TODO: clarify lockouts / timers on API response to show prime lockout animation with mobile team


    return response


@router.get('/settings')
async def get_settings(request: Request) -> dict:
    # Get settings from the right place of HW, SW and State for element water systems
    # Probably central place
    GENERATOR_INSTANCE = 1
    generator_meta = request.app.hal.energy.handler.generator[GENERATOR_INSTANCE].meta
    print('generator-meta', generator_meta)
    settings = {
        'title': 'Generator Information',
        'information': [
            {
                'title': 'MANUFACTURER INFORMATION',
                'items': [
                    {
                        'title': 'Generator',
                        'sections': [
                            {
                                'title': None,
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': generator_meta.get("manufacturer")   # TODO: Where to get from ?
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': generator_meta.get("model")
                                    },
                                    {
                                        'key': 'Details',
                                        'value': generator_meta.get("part")
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
        'notification': []
    }
    return settings
