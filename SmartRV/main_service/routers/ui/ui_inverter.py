from asyncio import base_futures
import datetime
import json
import os
from typing import Optional, List
from urllib import response


from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel


# from .common import ResultLevel, not_implemented

from common_libs.models.gui import (
    HeaderWidgets,
    QuickActionWidget,
    LevelWidget,
    Widget,
    Notification
)

# from main_service.modules.hardware.hal import hw_layer

from .helper import get_tank_level_text


class SimpleSwitch(BaseModel):
    onOff: int


class SimpleLevel(BaseModel):
    max: int
    min: int
    current_value: float
    unit: str
    level_text: str


class Tank(BaseModel):
    name: str
    title: str
    subtext: str
    type: str
    SimpleLevel: Optional[SimpleLevel]
    actions: Optional[List[str]]
    action_default: dict

    color_fill: str
    color_empty: str


BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/inverter',
    tags=['INVERTER',]
)


@router.get('/', response_model_exclude_none=True)
async def gui_inverter(request: Request):
    print('hit ui_inverter')

    # Settings
    # Battery SoC as a level widget
    BATTERY_INSTANCE = 1
    INVERTER_INSTANCE = 1
    bms_battery_level = request.app.hal.energy.handler.battery_management[BATTERY_INSTANCE].state.soc
    inverter_state = request.app.hal.energy.handler.inverter[INVERTER_INSTANCE].state

    house_battery_subtext = ''
    house_battery_soc = bms_battery_level
    house_battery_soc_text = get_tank_level_text({'lvl': bms_battery_level})

    # Inverter AC Current Reading
    inverter_wattage = inverter_state.load
    if inverter_wattage is None:
        inverter_wattage = '--'

    overld = inverter_state.overld
    if overld is True:
        in_overload = ' --- OVERLOAD'
    else:
        in_overload = ''

    inverter_wattage_text = f'Total AC Output: {inverter_wattage}W'
    inverter_onOff = inverter_state.onOff

    response = {
        'overview': {
            'title': 'Inverter',
            'settings': {
                'href': f'{BASE_URL}/ui/inverter/settings',
                'type': 'GET'
            },
        },
        'main': {
            'title': 'Inverter',
            'subtext': inverter_wattage_text + in_overload,
            'type': 'Simple',
            'Simple': {
                'onOff': inverter_onOff
            },
            'actions': ['action_default', ],
            'action_default': {
                'type': 'api_call',
                'action': {
                    "href": f"/api/energy/ei/{INVERTER_INSTANCE}/state",
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            }
        },
        'state': inverter_state,
        # TODO: Check against Figma
        # Generate from AC based energy consumers
        'navList': {
            'title': 'AC Powered Appliances',
            'data': [
                {
                    'title': 'Water Heater',
                    'actions': ['action_default',],
                    'action_default': {
                        'type': 'navigate',
                        'action': {
                            'href': '/home/watersystems'
                        }
                    }
                },
                {
                    'title': 'Heater',
                    'actions': ['action_default',],
                    'action_default': {
                        'type': 'navigate',
                        'action': {
                            'href': '/home/climatecontrol'
                        }
                    }
                },
                {
                    'title': 'AC Power Outlets'
                },
                {
                    'title': 'Cook Top'
                }
            ]
        },
        'levels': [
            {
                "name": "HouseBatteryLevel2",
                "type": "simpleLevel",
                "title": "House Battery",
                "subtext": house_battery_subtext,
                "icon": "",
                "color_fill": "#0ca9da",
                "simpleLevel": {
                    "max": 100,
                    "min": 0,
                    "current_value": house_battery_soc,
                    "unit": "%",
                    "level_text": house_battery_soc_text
                },
                "actions": None
            }
        ]
    }

    return response


@router.get('/settings')
async def get_settings(request:Request) -> dict:
    # Get settings from the right place of HW, SW and State for element water systems
    # Probably central place
    INVERTER_INSTANCE = 1
    inverter_meta = request.app.hal.energy.handler.inverter[INVERTER_INSTANCE].meta
    settings = {
        'title': 'Inverter Information',
        'information': [
            {
                'title': 'MANUFACTURER INFORMATION',
                'items': [
                    {
                        'title': 'Inverter',
                        'sections': [
                            {
                                'title': None,
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': inverter_meta.get("manufacturer")
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': inverter_meta.get("model")
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': inverter_meta.get("part")
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
