
import os

from fastapi import APIRouter, Request, BackgroundTasks
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pydantic import BaseModel
from datetime import datetime, timedelta

from common_libs.models.common import RVEvents, EventValues
from .ui_lighting import LIGHTING_SIMPLEDIM_PARAMS, light_text_from_state
from .helper import (
    get_tank_level_text,
    create_ui_lockout
)

BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/movable',      # temp setting to movable, should be movables
    tags=['UI']
)


@router.put("/so/understand")
# Temp add before we transition to movables being called by ui
@router.put("s/so/understand")
async def set_slideout_understand(request: Request):
    try:
        current_date = datetime.now().date()
        request.app.config['slideOut']['lastSignedDate'] = current_date
    except Exception as err:
        print(err, 'Could not store signed date')
    return request.app.config['slideOut']['lastSignedDate']


@router.get("/so/settings")
@router.get("s/so/settings")
async def get_slideout_settings(request: Request):
    SLIDEOUT_INSTANCE = 1
    slideout_meta = request.app.hal.movables.handler.slideout[SLIDEOUT_INSTANCE].meta
    try:
        response = {
            'title': 'Slide-Outs',
            'type': 'SECTIONS_LIST',
            'data': [
                {
                    'title': 'MANUFACTURER INFORMATION',
                    'type': 'LIST_ITEM',
                    'configuration': [
                        {
                            'title': 'Slide-Outs',
                            'type': 'LIST_ITEM_NAV',
                            'data': [
                                {
                                    'type': 'SETTINGS_SECTIONS_LIST',
                                    'title': 'MANUFACTURER INFORMATION',
                                    'data': [
                                        {
                                            'type': 'SECTIONS_LIST_ITEM',
                                            'title': 'Manufacturer',
                                            'value': slideout_meta.get("manufacturer")
                                        },
                                        {
                                                'type': 'SECTIONS_LIST_ITEM',
                                                'title': 'Product Model',
                                                'value': slideout_meta.get("model")
                                        },
                                        {
                                                'type': 'SECTIONS_LIST_ITEM',
                                                'title': 'Part#',
                                                'value': slideout_meta.get("part")
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                # NOTE: Legal Disclaimer removed as not needed, left in here if that changes
                # {
                #     'title': 'MANUFACTURER INFORMATION',
                #     'type': 'LIST_ITEM',
                #     'configuration': [
                #         {
                #             'title': 'Legal Disclaimer',
                #             'type': 'SECTIONS_LIST',
                #             'title': 'Legal Disclaimer',
                #             'data':  [
                #                 {
                #                     'title': 'Legal Disclaimer',
                #                     'subtext': 'Effective March 31, 2020',
                #                     'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut laborem ipsum dolor sit amet, consectetur adipscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliq.'
                #                 }
                #             ]
                #         }
                #     ]
                # }
            ]

        }
    except Exception as err:
        print(err, 'Could not fetch settings.')
    return response


@router.get("/so/warning")
@router.get("s/so/warning")
async def get_slideout_warning(request: Request):

    current_date = datetime.now().date()
    last_signed_date = request.app.config['slideOut']['lastSignedDate']

    if isinstance(last_signed_date, str):
        last_signed_date = datetime.strptime(
            last_signed_date, '%Y-%m-%d').date()

    time_difference = current_date - last_signed_date
    time_limit = request.app.config['slideOut']['timeLimit']
    understand_flag = time_difference >= timedelta(days=time_limit)

    response = {
        'title': 'Slide-Outs Safety',
        'type': 'SECTIONS_LIST',
        'data': [
            {
                'title': 'Warning',
                'type': 'SECTIONS_LIST_ITEM',
                'body': 'Always make sure that the slide-out room path is clear of people and objects before and during operation of the slide-out. Always keep away from the gear racks when the room is being operated.'
            },
            {
                'title': 'Warning',
                'type': 'SECTIONS_LIST_ITEM',
                'body': 'Do not work on your slide-out system unless the battery is disconnected. Failure to act in accordance with this warning may result in death, serious injury or damage to the trailer.',
            },
            {
                'title': 'Warning',
                'type': 'SECTIONS_LIST_ITEM',
                'body': 'The In-Wall Slide-out System is intended for the sole purpose of extending and retracting the slide-out room. It should not be used for any other purpose other than to actuate the slide-out room. To use the system for any other reason other than what it is designed for may result in death, serious injury or damage to the trailer.'
            },
            {
                'title': 'Caution',
                'type': 'SECTIONS_LIST_ITEM',
                'body': 'Moving parts can pinch, crush or cut. Keep clear and use caution.'
            },
            {
                'title': 'I Understand',
                'type': 'button',
                'subtext': 'By clicking "I Understand" you agree that Winnebago is not liable to any damages or harm while interacting with Winnebago product.',
                'value': understand_flag,
                'actions': {
                    'POP_UP': {
                        'type': 'api_call',
                        'action': {
                            'href': f'/ui/movables/so/understand',
                            'type': 'PUT',
                        }
                    }
                }
            }
        ]
    }

    return response


@router.get("/so/screen")
@router.get("s/so/screen")
async def get_slideout_screen(request: Request):
    '''UI endpoint to assemble slideout screen'''
    # Get slideouts from HAL
    # TODO: Get list of slideouts from HAL
    SLIDEOUT_INSTANCE = 1
    slideouts = request.app.hal.movables.handler.slideout
    slideout_list = []

    slideout = slideouts[SLIDEOUT_INSTANCE]

    slideout_enabled = True
    # Update the lockouts
    slideout.check_lockouts()

    # Disable the slideout UI when lockouts apply
    if slideout.state.lockouts:
        slideout_enabled = False

    chassis_on = True
    if slideout.state.warnings:
        for warning in slideout.state.warnings:
            print('Warning', warning)
            if warning == EventValues.IGNITION_ON:
                chassis_on = False
    lockouts_ui = []
    for lock_out in slideout.state.lockouts:
        lock = request.app.hal.system.handler.lockouts[lock_out]
        lockouts_ui.append(
            create_ui_lockout(
                slideout,
                lock,
                lock_out
            )
        )

    for instance, slideout in slideouts.items():
        # Might need to massage the actual string that is shown
        # TODO: Put the above lockout check into the loop here

        if slideout.state.mode in (EventValues.EXTENDING, EventValues.RETRACTING):
            slideout_state_text = slideout.state.mode.name.capitalize()
        else:
            slideout_state_text = 'Off'

        # NOTE: External switch could move this and our state does not account this yet
        # slideout_state_text = slideout.state.mode.name

        slideout_list.append(
            {
                'title': slideout.attributes.get('name', 'ATTR_NAME_MISSING'),
                'subtext': slideout_state_text,
                'name': f'slideOut{instance}',
                'type': 'DEADMAN',
                'intervalMs': 200,      # DOM to confirm
                'holdDelayMs': 1000,    # DOM to confirm
                # Dom to review if this can be moved to lockouts in state
                'enabled': slideout_enabled,
                'state': slideout.state,
                'lockouts': lockouts_ui,
                'option_param': 'mode',
                'switches': {},
                'actions': {
                    'PRESS': None,
                    'HOLD': {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/movables/so/{instance}/state',
                            'type': 'PUT',
                            'param': {
                                '$mode': 'int',
                            }
                        }
                    },
                    # TODO: How can we place this better ? Should not be in the action itself, but no immediate better way (DOM)
                    'subtext': 'Stop',
                    'RELEASE': {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/movables/so/{instance}/state',
                            'type': 'PUT',
                            'param': {
                                'mode': EventValues.OFF,
                            }
                        }
                    }
                },
                'options': [
                    {
                        'key': '-',
                        'subtext': 'Retract',
                        'value': EventValues.RETRACTING,
                        # TODO: Attach the appropriate state to this when lockout condition appears
                        'enabled': slideout_enabled,

                    },
                    {
                        'key': '+',
                        'subtext': 'Extend',
                        'value': EventValues.EXTENDING,
                        # TODO: Attach the appropriate state to this when lockout condition appears
                        'enabled': slideout_enabled,

                    },

                ]
            }
        )
    # Get
    response = {
        'overview': {
            'title': 'Slide-Outs',
            'type': 'SECTIONS_LIST',
            'warnings': [
                {
                    'title': 'Danger',
                    'type': 'ALERT',
                    'subtext': 'Make sure the slide-out area is free from people and objects.',
                    'footer': {
                        'title': 'See All Safety Messages',
                        'actions': {
                            'TAP': {
                                'type': 'NAVIGATE',
                                'action': {
                                    'href': f'{BASE_URL}/ui/movables/so/warning',
                                    'type': 'GET',
                                }
                            }
                        }
                    }
                }
            ],
            'lockouts': lockouts_ui,
            'settings': {
                'href': f'{BASE_URL}/ui/movables/so/settings',
                'type': 'GET'
            },
        },
        'twoStepReq': request.app.config['slideOut']['twoStepReq'],
        'slideOuts': slideout_list
    }
    if chassis_on is False:
        response['overview']['warnings'].append(
            {
                'title': 'Helpful Tip!',
                'type': 'INFO',
                'subtext': '''It's recommended to have the chassis engine running while using the slide-outs.'''
                # TODO: What should happen on the X
                # Could be a dismiss for the ignition off state to be ignored

            }
        )

    return response


# awning
@router.put("/aw/understand")
# Temp add before we transition to movables being called by ui
@router.put("s/aw/understand")
async def set_awning_understand(request: Request):
    try:
        current_date = datetime.now().date()
        request.app.config['awning']['lastSignedDate'] = current_date
    except Exception as err:
        print(err, 'Could not store signed date')

    return request.app.config['awning']['lastSignedDate']


@router.get("/aw/warning")
@router.get("s/aw/warning")
async def get_awning_warning(request: Request):

    current_date = datetime.now().date()
    last_signed_date = request.app.config['awning']['lastSignedDate']

    if isinstance(last_signed_date, str):
        last_signed_date = datetime.strptime(
            last_signed_date, '%Y-%m-%d').date()

    time_difference = current_date - last_signed_date
    time_limit = request.app.config['awning']['timeLimit']
    understand_flag = time_difference >= timedelta(days=time_limit)

    response = {
        'title': 'Awning Safety',
        'type': 'SECTIONS_LIST',
        'data': [
            {
                'title': 'Caution',
                'type': 'SECTIONS_LIST_ITEM',
                'body': 'Always make sure that the Awning path is clear of people and objects before and during operation of the Awning. Always keep away from the moving parts when the Awning is being operated.'
            },
            {
                'title': 'I Understand',
                'type': 'button',
                'subtext': 'By clicking "I Understand" you agree that Winnebago is not liable to any damages or harm while interacting with Winnebago product.',
                'value': understand_flag,
                'actions': {
                    'POP_UP': {
                        'type': 'api_call',
                        'action': {
                            'href': '/ui/movables/aw/understand',
                            'type': 'PUT',
                        }
                    }
                }
            }
        ]
    }

    return response


@router.get("/aw/screen")
@router.get("s/aw/screen")
async def get_awning_screen(request: Request):
    '''UI endpoint to assemble awning screen'''
    # Get slideouts from HAL
    # TODO: Get list of slideouts from HAL

    # might need an else
    if not hasattr(request.app.hal.movables.handler, 'awning'):
        return {}

    awning_list = []
    awnings = request.app.hal.movables.handler.awning

    for instance, awning in awnings.items():
        awning_lights = []
        awning_light = None
        for component in awning.relatedComponents:
            if 'lighting' in component.get("componentTypeId"):
                AWNING_LIGHT_INSTANCE = component.get("instance")
                awning_light = request.app.hal.lighting.handler.lighting_zone[AWNING_LIGHT_INSTANCE]
                awning_light_onoff = 'On' if awning_light.state.onOff == EventValues.ON else 'Off'
                awning_lights.append({
                    'title': awning_light.attributes.get("name"),
                    'type': 'dimmable',
                    'subtext': f'{awning_light_onoff}: {awning_light.state.brt}%' if awning_light_onoff == 'On' else awning_light_onoff,
                    'state': awning_light.state,
                    'widget': {
                        'step': 5,
                        'min': 5,      # TODO: What is the minimum?
                        'max': 100
                    },
                    'actions': ['action_default', ],
                    'action_default': {
                        'type': 'api_call',
                        'action': {
                            'href': f'/api/lighting/lz/{AWNING_LIGHT_INSTANCE}/state',
                            'type': 'PUT',
                            'params': LIGHTING_SIMPLEDIM_PARAMS,
                        }
                    }
                })
        # TODO: update for multiple lights on a single awning

        # Disable the awning UI when lockouts apply

        awning.check_lockouts()
        awning_enabled = True
        # Update the lockouts

        if awning.state.lockouts:
            awning_enabled = False

        chassis_on = True
        if awning.state.warnings:
            for warning in awning.state.warnings:
                print('Warning', warning)
                if warning == EventValues.IGNITION_ON:
                    chassis_on = False
        lockouts_ui = []
        for lock_out in awning.state.lockouts:
            lock = request.app.hal.system.handler.lockouts[lock_out]
            lockouts_ui.append(
                create_ui_lockout(
                    awning,
                    lock,
                    lock_out
                )
            )

        switches = []

        auto_extend = {
            'title': 'Auto Extend',
            # 'subtext': '',
            'type': 'DEADMAN',
            'name': 'AwningAutoExtend',
            'intervalMs': None,        # DOM to confirm
            'holdDelayMs': 1000,       # DOM to confirm
            'enabled': awning_enabled,
            'actions': {
                'PRESS': None,
                'HOLD': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/movables/aw/{instance}/state',
                        'type': 'PUT',
                        'param': {
                            'mode': EventValues.EXTENDING,
                            'setPctExt': 100,
                        }
                    }
                },
                'RELEASE': None,
            }
        }

        auto_retract = {
            'title': 'Auto Retract',
            # 'subtext': '',
            'type': 'DEADMAN',
            'name': 'AwningAutoRetract',
            'intervalMs': None,        # DOM to confirm
            'holdDelayMs': 1000,       # DOM to confirm
            'enabled': awning_enabled,
            'actions': {
                'PRESS': None,
                'HOLD': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/movables/aw/{instance}/state',
                        'type': 'PUT',
                        'param': {
                            'mode': EventValues.RETRACTING,
                            'setPctExt': 0,
                        }
                    }
                    },
                'RELEASE': None,
            }
        }
        manual_extend = {
            'title': '+',
            # 'subtext': 'Extend',
            'type': 'DEADMAN',
            'name': 'AwningManualExtend',
            'intervalMs': 100,        # DOM to confirm
            'holdDelayMs': 1000,       # DOM to confirm
            'enabled': awning_enabled,
            'actions': {
                'PRESS': None,
                'HOLD': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/movables/aw/{instance}/state',
                        'type': 'PUT',
                        'param': {
                            'mode': EventValues.EXTENDING,
                        }
                    }
                },
                'RELEASE': {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/movables/aw/{instance}/state',
                            'type': 'PUT',
                            'param': {
                                'mode': EventValues.OFF,
                            }
                        }
                    },
            }
        }
        manual_retract = {
            'title': '-',
            # 'subtext': 'Retract',
            'type': 'DEADMAN',
            'name': 'AwningManualRetract',
            'intervalMs': 100,        # DOM to confirm
            'holdDelayMs': 1000,       # DOM to confirm
            'enabled': awning_enabled,
            'actions': {
                'PRESS': None,
                'HOLD': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/movables/aw/{instance}/state',
                        'type': 'PUT',
                        'param': {
                            'mode': EventValues.RETRACTING,
                        }
                    }
                },
                'RELEASE': {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/movables/aw/{instance}/state',
                            'type': 'PUT',
                            'param': {
                                'mode': EventValues.OFF,
                            }
                        }
                    },
            }
        }
        stop = {
            'title': 'Stop',
            'type': 'DEADMAN',
            'intervalMs': None,        # DOM to confirm
            'holdDelayMs': None,       # DOM to confirm
            # Dom to review if this can be moved to lockouts in state
            'enabled': awning_enabled,
            'actions': {
                    'PRESS': {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/movables/aw/{instance}/state',
                            'type': 'PUT',
                            'param': {
                                'mode': EventValues.OFF,
                            }
                        }
                    },
            },
            'HOLD': None,
            'RELEASE': None,
        }

        if awning.state.mode in [EventValues.RETRACTING, EventValues.EXTENDING]:
            if awning.state.setPctExt == 100 or awning.state.setPctExt == 0:   # setPctExt could be 0
                switches.append(stop)
            else:
                switches.extend(
                    [
                        auto_retract,
                        auto_extend,
                        # manual_retract,
                        # manual_extend
                    ]
                )

        elif awning.state.mode in [
                        None,
                        EventValues.OFF,
                        EventValues.RETRACTED,
                        EventValues.EXTENDED]:
            switches.extend(
                [
                    auto_retract,
                    auto_extend,
                    # manual_retract,
                    # manual_extend
                ]
            )

        # Might need to massage the actual string that is shown
        pct_ext = '--'
        if awning.state.pctExt is not None:
            pct_ext = awning.state.pctExt

        awning_mode = awning.state.mode
        if awning_mode is None:
            if pct_ext == '--':
                awning_state_text = 'Status Unavailable'
            else:
                awning_state_text = f'NA · {pct_ext}%'
        else:
            awning_state_text = f'{awning.state.mode.name.capitalize()} · {pct_ext}%'
        # print('related-components-', awning.relatedComponents)
        awning_list.append(
            {
                'title': awning.attributes.get('name', 'ATTR_NAME_MISSING'),
                'subtext': awning_state_text,
                'name': f'awning{instance}',
                # Dom to review if this can be moved to lockouts in state
                'enabled': awning_enabled,
                'state': awning.state,
                'lockouts': lockouts_ui,
                'switches': switches,
                'awningLights': awning_lights
            }
        )

    response = {
        'overview': {
            'title': 'Awning',
            'type': 'SECTIONS_LIST',
            'warnings': [
                {
                    'title': 'Caution',
                    'type': 'ALERT',
                    'subtext': 'Make sure people and objects are away from the awning path and any moving parts.',
                    'footer': {
                        'title': 'See All Safety Messages',
                        'actions': {
                            'TAP': {
                                'type': 'NAVIGATE',
                                'action': {
                                    'href': '/ui/movables/aw/warning',
                                    'type': 'GET',
                                }
                            }
                        }
                    }
                }
            ],
            'lockouts': lockouts_ui,
            'settings': {
                'href': f'{BASE_URL}/ui/movables/aw/settings',
                'type': 'GET'
            },
        },
        'twoStepReq': request.app.config['awning']['twoStepReq'],
        'awnings': awning_list,
    }
    if chassis_on is False:
        response['overview']['warnings'].append(
            {
                'title': 'Helpful Tip!',
                'type': 'INFO',
                'subtext': '''It's recommended to have your parking brake engaged while using your awning.'''
                # TODO: What should happen on the X
                # Could be a dismiss for the ignition off state to be ignored

            }
        )

    return response


@router.get("s/aw/settings")
@router.get("/aw/settings")
async def get_awning_settings(request: Request):

    if not hasattr(request.app.hal.movables.handler, 'awning'):
        return {}
    AWNING_INSTANCE = 1
    awning = request.app.hal.movables.handler.awning[AWNING_INSTANCE]
    wind_sensor_onoff = 'On' if awning.state.mtnSenseOnOff == EventValues.ON else 'Off'
    wind_sensor_sensitivity = awning.state.mtnSense
    awning_meta = awning.meta

    if wind_sensor_sensitivity in (1, 2):
        wind_type = 'High Winds can trigger the awning to auto-retract.'
    elif wind_sensor_sensitivity == 3:
        wind_type = 'Medium Winds can trigger the awning to auto-retract.'
    elif wind_sensor_sensitivity in (4, 5):
        wind_type = 'Low Winds can trigger the awning to auto-retract.'
    else:
        wind_type = 'Unknown state of the motion sensor.'

    if awning.state.mtnSenseOnOff == EventValues.ON:
        footer_text = 'The awning will auto-retract when there is inclement weather.'
    else:
        footer_text = 'The motion sensor will not auto-retract the awning.'

    response = {
        'title': 'Awning',
        'data': [
            {
                'title': 'Motion Sensor',
                'type': 'LIST_ITEM_NAV',
                'value': wind_sensor_onoff,
                'data': [
                    {
                        'title': None,
                        'type': 'SECTIONS_LIST',
                        'data': [
                            {
                                'title': 'Motion Sensor',
                                'value': wind_sensor_onoff,
                                'state': {
                                    'onOff': awning.state.mtnSenseOnOff,
                                },
                                'actions': {
                                    'TOGGLE': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'/api/movables/aw/{AWNING_INSTANCE}/state',
                                            'type': 'PUT',
                                            'params': {
                                                '$mtnSenseOnOff': 'int',
                                            }
                                        }
                                    }
                                },
                            }
                        ],
                        'footer': footer_text,
                    },
                    {
                        'title': 'SENSITIVITY',
                        'type': 'simpleSlider',
                        'state': {
                            'mtnSenseOnOff': awning.state.mtnSenseOnOff,
                            'mtnSense': awning.state.mtnSense,
                        },
                        'widget': {
                            'step': 1,
                            'min': 1,
                            'max': 5
                        },
                        'actions': {
                            'SLIDE': {
                                'type': 'api_call',
                                'action': {
                                    'type': 'PUT',
                                    'href': f'/api/movables/aw/{AWNING_INSTANCE}/state',
                                    'params': {
                                        '$mtnSense': 'int'
                                    }
                                }
                            }
                        },
                        'footer': f'Sensitivity {wind_sensor_sensitivity}: {wind_type} ',
                    },
                    # {
                    #     'title': 'Restore Default',
                    #     'type': 'BUTTON',
                    #     'actions': {
                    #         'TAP': {
                    #             'type': 'api_call',
                    #             'action': {
                    #                 'href': f'/api/movables/aw/{AWNING_INSTANCE}/mtnsense/default',
                    #                 'type': 'PUT',
                    #             },
                    #         },
                    #     }
                    # }
                ],
            },
            {
                'title': 'MANUFACTURER INFORMATION',
                'type':  'LIST_ITEM',
                'data': [
                    {
                        'title': 'Awning',
                        'type': 'LIST_ITEM_NAV',
                        'data': [
                            {
                                'title': 'Awning',
                                'information': [
                                    {
                                        'title': 'MANUFACTURER INFORMATION',
                                        'type': 'SECTIONS_LIST',
                                        'items': [
                                            {
                                                'key': 'Manufacturer',
                                                # TODO: Where to get from ?
                                                'value': awning_meta.get("manufacturer")
                                            },
                                            {
                                                'key': 'Product Model',
                                                'value': awning_meta.get("model")
                                            },
                                            {
                                                'key': 'Details',
                                                'value': awning_meta.get("part")
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]

            },
            {
                'title': 'LEGAL DISCLAIMER',
                'type':  'SECTIONS_LIST',
                'data': [
                    {
                        'title': 'Legal Disclaimer',
                        'data':  [
                            {
                                'title': 'Legal Disclaimer',
                                'subtext': 'Effective March 31, 2020',
                                'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut laborem ipsum dolor sit amet, consectetur adipscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliq.'
                            }
                        ]
                    }
                ]
            }
        ],
    }
    return response
