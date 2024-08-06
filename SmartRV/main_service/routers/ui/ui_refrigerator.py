from datetime import datetime
import os
from typing import Optional, List
from common_libs.models.common import EventValues, RVEvents, LogEvent
from main_service.routers.api_climate import refrigerator_freezer_history
from fastapi import APIRouter, HTTPException, Request, Body

from pydantic import BaseModel

from main_service.modules.constants import (
    TEMP_UNITS,
    TEMP_UNIT_PREFERENCE_KEY,
    TEMP_UNIT_FAHRENHEIT,
    _celcius_2_fahrenheit,
)


class SimpleSwitch(BaseModel):
    onOff: int


class SimpleLevel(BaseModel):
    max: int
    min: int
    current_value: float
    unit: str
    level_text: str


class WaterPump(BaseModel):
    name: str
    title: str
    subtext: str
    type: str
    Simple: Optional[SimpleSwitch]
    actions: List[str]
    action_default: dict


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
    prefix='/refrigerator',
    tags=['REFRIGERATOR', ]
)


def get_outOrIn(alert_onoff, sorted_list):
    # TODO: Could this be cleared up ?
    out_or_in = '--'
    if alert_onoff != 0:
        if sorted_list and sorted_list[0].get('alert'):
            out_or_in = 'Outside Range'
        elif sorted_list and not sorted_list[0].get('alert'):
            out_or_in = 'Inside Range'
    return out_or_in


@router.get('/', response_model_exclude_none=True)
async def gui_refrigerator(request: Request):
    FRIDGE_ID = 1
    FREEZER_ID = 2

    FRIDGE_ID_INDEX = 0
    FREEZER_ID_INDEX = 1

    instance_ids = [FRIDGE_ID, FREEZER_ID]
    current_date = datetime.now().strftime("%A, %Y-%m-%d")
    start_time, end_time = '12:00:00 AM', '11:59:59 PM'
    limit = 50
    # BUG: We cannot send an empty string without causing the default to be used
    current_date = datetime.now().strftime("%Y-%m-%d")
    instance_data = []
    for instance_id in instance_ids:
        sorted_list, current_temp, current_temp_short = refrigerator_freezer_history(
            request,
            instance_id,
            start_time,
            end_time,
            current_date
        )
        if instance_id == FRIDGE_ID:
            alert_onoff = request.app.config['refrigerator']['AlertOnOff']
        if instance_id == FREEZER_ID:
            alert_onoff = request.app.config['freezer']['AlertOnOff']
        outOrIn = get_outOrIn(alert_onoff, sorted_list)
        finalize_data = sorted_list[:min(len(sorted_list), limit)]
        sub_list = [sorted_list, current_temp, current_temp_short, outOrIn, finalize_data]
        instance_data.append(sub_list)

    response = {
        'overview': {
            'title': 'Refrigeration',
            'settings': {
                'href': f'{BASE_URL}/ui/refrigerator/settings',
                'type': 'GET'
            },
            'bottom_widget_refrigerator': {
                'title': 'FRIDGE',
                'text': instance_data[FRIDGE_ID_INDEX][1],
                'sidetext': '°' + instance_data[FRIDGE_ID_INDEX][2],
                'subtext': instance_data[FRIDGE_ID_INDEX][3],
                'alert': False
            },
            'bottom_widget_freezer': {
                'title': 'FREEZER',
                'text': instance_data[FREEZER_ID_INDEX][1],
                'sidetext': '°' + instance_data[FREEZER_ID_INDEX][2],
                'subtext': instance_data[FREEZER_ID_INDEX][3],
                'alert': False
            },
        },
        # TODO: Fix the path to be pre-parameterized
        # TODO: Fix instances being used
        # TODO: Drop applianceType from params
        'controls': {
            'refrigerator_current_history': {
                'title': 'Refrigerator Temperature History',
                'subtext': datetime.now().strftime("%A, %B %d"),
                'refrigerator_data': instance_data[FRIDGE_ID_INDEX][4],
                'refrigerator_full_history': {
                    'title': 'See Refrigerator History',
                    'type': 'button',
                    'PRESS': {
                        'type': 'navigate',
                        'action': {
                            'href': f'{BASE_URL}/ui/refrigerator/freezer/fullhistory',
                            'type': 'PUT',
                                'params': {
                                    'applianceType': 'refrigerator',
                                    'date': current_date,
                                }
                        },
                    },
                },
            },
            'freezer_current_history': {
                'title': 'Freezer Temperature History',
                'subtext': datetime.now().strftime("%A, %B %d"),
                'freezer_data': instance_data[FREEZER_ID_INDEX][4],
                'freezer_full_history': {
                    'title': 'See Freezer History',
                    'type': 'button',
                    'PRESS': {
                        'type': 'navigate',
                        'action': {
                            'href': f'{BASE_URL}/ui/refrigerator/freezer/fullhistory',
                            'type': 'PUT',
                                'params': {
                                    'applianceType': 'freezer',
                                    'date': current_date,
                                }
                        },
                    },
                },
            }
        }
    }

    return response


@router.put('/fullhistory', response_model_exclude_none=True)
@router.put('/freezer/fullhistory', response_model_exclude_none=True)
async def pull_fullhistory(request: Request, data: dict = Body(...)):
    '''Use format {"date": "2023-23-10", "applianceType": "refrigerator"}'''
    current_date = datetime.now().strftime("%Y-%m-%d")
    date = data.get("date", current_date)
    appliance_type = data.get("applianceType")

    try:
        bool(datetime.strptime(date, "%Y-%m-%d"))
    except ValueError as err:
        raise HTTPException(status_code=400, detail="Invalid date format")

    instance_id = 1
    if appliance_type == 'freezer':
        instance_id = 2

    sorted_list, current_fridge_temp, current_temp_short = refrigerator_freezer_history(
        request, instance_id, '12:00:00 AM', '11:59:59 PM', date)

    response = {
        'controls': {
            'fullhistory': {
                'data': sorted_list,
                'actions': ['action_default', 'get_refrigerator_prev_next_history', 'get_freezer_prev_next_history'],
                'action_default': {
                    'text': 'See Full History',
                    'type': 'navigate',
                    'action': {
                        'href': '/home/refrigerator/history',
                    }
                },
                'get_refrigerator_prev_next_history': {
                    'type': 'api_call',
                    'type': 'PUT',
                    'description': 'YYYY-MM-DD should be in string format',
                    'action': {
                        'href': f'{BASE_URL}/ui/refrigerator/fullhistory',
                                'type': 'PUT',
                                'params': {
                                    '$date': 'str',
                                    'date': date,
                                    '$applianceType': 'str',
                                }
                    }
                },
                'get_freezer_prev_next_history': {
                    'type': 'api_call',
                    'type': 'PUT',
                    'description': 'YYYY-MM-DD should be in string format',
                    'action': {
                        'href': f'{BASE_URL}/ui/refrigerator/freezer/fullhistory',
                                'type': 'PUT',
                                'params': {
                                    '$date': 'str',
                                    'date': date,
                                    '$applianceType': 'str',
                                }
                    }
                }
            }
        },
    }
    return response


@router.get('/settings')
async def get_settings(request: Request) -> dict:
    # Get settings from the right place of HW, SW and State for element water systems

    refrigerator_alertonoff = request.app.config['refrigerator']['AlertOnOff']
    refrigerator_notification_key = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
    fridge_note = request.app.event_notifications[refrigerator_notification_key]
    fridge_meta = request.app.hal.climate.handler.refrigerator[1].meta

    freezer_alertonoff = request.app.config['freezer']['AlertOnOff']
    freezer_notification_key = RVEvents.FREEZER_OUT_OF_RANGE.value
    freezer_note = request.app.event_notifications[freezer_notification_key]
    freezer_meta = request.app.hal.climate.handler.refrigerator[2].meta

    refrigerator_index = 0
    freezer_index = 1
    appliances_note = [fridge_note, freezer_note]
    # taking into account all negative celsius values
    # fridge
    appliances_data = []
    for appliance_note in appliances_note:
        # get the triiger list and make floating point
        appliance_triggers = appliance_note.trigger_value.split(',')
        appliances_data.append(float(appliance_triggers[0]))
        appliances_data.append(float(appliance_triggers[1]))

    settings = {
        'title': 'Refrigerator-Freezer Settings',
        'configuration': [
            {
                'title': 'Refrigerator Temp Alert',
                'items': [
                    {
                        'title': 'Refrigerator Temp Alert',
                        'selected_text': 'on',
                        'type': 'Simple',
                        'Simple': {
                            'onOff': refrigerator_alertonoff,
                        },
                        'actions': ['action_default'],
                        'action_default': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/alert',
                                'type': 'PUT',
                                'params': {
                                    '$onOff': 'int',
                                    'applianceType': 'refrigerator'
                                }
                            }
                        }
                    },
                    {
                        'title': 'Refrigerator Temp Range',
                        'items': [
                            {
                                'title': 'upper limit',
                                'value': _celcius_2_fahrenheit(appliances_data[1]),
                                'type': 'Upper_Limit',
                                'actions': ['change_upper_limit'],
                                'change_upper_limit': {
                                    'type': 'api_call',
                                    'action': {
                                        'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/temprange',
                                        'type': 'PUT',
                                        'params': {
                                            '$upper_limit': 'float',
                                            '$lower_limit': 'float',
                                            'applianceType': 'refrigerator'
                                        }
                                    }
                                },
                            },
                            {
                                'title': 'lower limit',
                                'value': _celcius_2_fahrenheit(appliances_data[0]),
                                'type': 'Lower_Limit',
                                'actions': ['change_lower_limit'],
                                'change_lower_limit': {
                                    'type': 'api_call',
                                    'action': {
                                        'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/temprange',
                                        'type': 'PUT',
                                        'params': {
                                            '$upper_limit': 'float',
                                            '$lower_limit': 'float',
                                            'applianceType': 'refrigerator'
                                        }
                                    }
                                },
                            }
                        ]

                    },
                    {
                        'title': 'restore default',
                        'actions': ['action_default'],
                        'action_default': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/restoredefault',
                                'type': 'PUT',
                                'params': {
                                    'applianceType': 'refrigerator'
                                }
                            }
                        }
                    }
                ]
            },
            {
                'title': 'Freezer Temp Alert',
                'items': [
                    {
                        'title': 'Freezer Temp Alert',
                        'selected_text': 'on',
                        'type': 'Simple',
                        'Simple': {
                            'onOff': freezer_alertonoff,
                        },
                        'actions': ['action_default'],
                        'action_default': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/alert',
                                'type': 'PUT',
                                'params': {
                                    '$onOff': 'int',
                                    'applianceType': 'freezer'
                                }
                            }
                        }
                    },
                    {
                        'title': 'Temp Range',
                        'items': [
                            {
                                'title': 'upper limit',
                                'value': _celcius_2_fahrenheit(appliances_data[3]),
                                'type': 'Upper_Limit',
                                'actions': ['change_upper_limit'],
                                'change_upper_limit': {
                                    'type': 'api_call',
                                    'action': {
                                        'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/temprange',
                                        'type': 'PUT',
                                        'params': {
                                            '$upper_limit': 'float',
                                            '$lower_limit': 'float',
                                            'applianceType': 'freezer'
                                        }
                                    }
                                },
                            },
                            {
                                'title': 'lower limit',
                                'value': _celcius_2_fahrenheit(appliances_data[2]),
                                'type': 'Lower_Limit',
                                'actions': ['change_lower_limit'],
                                'change_lower_limit': {
                                    'type': 'api_call',
                                    'action': {
                                        'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/temprange',
                                        'type': 'PUT',
                                        'params': {
                                            '$upper_limit': 'float',
                                            '$lower_limit': 'float',
                                            'applianceType': 'freezer'
                                        }
                                    }
                                },
                            }
                        ]

                    },
                    {
                        'title': 'restore default',
                        'actions': ['action_default'],
                        'action_default': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/climate/refrigerator/freezer/settings/restoredefault',
                                'type': 'PUT',
                                'params': {
                                    'applianceType': 'freezer'
                                }
                            }
                        }
                    }
                ]
            }
        ],
        'information': [
            {
                'title': 'MANUFACTURER INFORMATION',
                'items': [
                    {
                        'title': 'Refrigerator',
                        'sections': [
                            {
                                'title': 'FRIDGE',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': fridge_meta.get("manufacturer")
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': fridge_meta.get("model")
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': fridge_meta.get("part")
                                    }
                                ]
                            },
                            {
                                'title': 'SENSOR',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'KiB'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'Some Model'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Refrigerator',
                        'sections': [
                            {
                                'title': 'FRIDGE',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': freezer_meta.get("manufacturer")
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': freezer_meta.get("model")
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': freezer_meta.get("part")
                                    }
                                ]
                            },
                            {
                                'title': 'SENSOR',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'KiB'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'Some Model'
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


@router.get('/settings/alerts')
async def get_alerts() -> dict:
    # Get settings from the right place of HW, SW and State
    # Probably central place
    alerts = {
        'title': 'Water Systems Settings',
        'configuration': [
            {
                'title': None,
                'items': [
                    {
                        'title': 'Unit Preference',
                        'selected_text': 'Gallons',
                        'options': [
                            {
                                'key': 'Gallons (gal.)',
                                'value': 0,
                                'selected': True
                            },
                            {
                                'key': 'Liters (L)',
                                'value': 1,
                                'selected': False
                            },
                        ],
                        'actions': ['action_default', ],
                        'action_default': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/watersystems/settings',
                                'type': 'PUT',
                                'params': {
                                    '$value': 'int',
                                    'item': 'VolumeUnitPreference'
                                }
                            }
                        }
                    }
                ]
            }
        ],
        'information': [
            {
                'title': 'MANUFACTURER INFORMATION',
                'items': [
                    {
                        'title': 'Water Pump',
                        'sections': [
                            {
                                'title': None,
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'Shurflo'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'ABC123'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Water Heater',
                        'sections': [
                            {
                                'title': None,
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'GE'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'ABC123'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Fresh Tank',
                        'sections': [
                            {
                                'title': 'TANK',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'Some OEM'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'Some Model'
                                    },
                                    {
                                        'key': 'Tank Volume',
                                        # Convert this to the selected unit before reporting out
                                        'value': '21 gal.'
                                    }
                                ]
                            },
                            {
                                'title': 'SENSOR',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'Maretron'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'TLM100 - M002201'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Gray Tank',
                        'sections': [
                            {
                                'title': 'TANK',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'Some OEM'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'Some Model'
                                    },
                                    {
                                        'key': 'Tank Volume',
                                        # Convert this to the selected unit before reporting out
                                        'value': '21 gal.'
                                    }
                                ]
                            },
                            {
                                'title': 'SENSOR',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'Maretron'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'TLM100 - M002201'
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
    return alerts
