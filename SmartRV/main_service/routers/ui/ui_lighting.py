from fastapi import APIRouter, HTTPException, Request, Response
# from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from common_libs.models.lighting import *
from common_libs.models.common import EventValues

from .helper import get_lighting_settings


BASE_URL = ''


PREFIX = 'lighting'
router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['UI', ]
)


LIGHTING_RGBW_PARAMS = {
    '$onOff': 'int',
    '$rgb': 'hex',
    '$clrTmp': 'int',
    '$brt': 'int'
}

LIGHTING_SIMPLEDIM_PARAMS = {
    '$onOff': 'int',
    '$brt': 'int'
}

LIGHTING_SIMPLE_PARAMS = {
    '$onOff': 'int'
}

LIGHTING_SIMPLE_ONOFF_TEXT = {
    0: 'Off',
    1: 'On',
    None: ''
}


def light_text_from_state(state, zone):
    '''Get text definitions for certain states'''
    # print('Current Zone State', state)

    light_type = zone.type
    response = {
        'title': zone.attributes.get('name')
    }
    # If we have a state get the subtext for the off case
    if state:
        if state.onOff == EventValues.OFF:
            response['subtext'] = 'Off'
        # NOTE: Need this currently for simple lights
        elif state.onOff == EventValues.ON:
            response['subtext'] = 'On'
        else:
            # NOTE: Not sure yet why this is needed
            response['subtext'] = 'Off'
    else:
        response['subtext'] = 'Off'

    if light_type == 'RGBW':
        response['params'] = LIGHTING_RGBW_PARAMS
        if state is None:
            response['subtext'] = ''
            state = {
                'onOff': 0,
                'rgb': '#EEEEEE',
                'brt': 60,
                'clrTmp': 5000,
            }
        else:
            # onOff = 0 handled above
            if state.onOff == 1:
                response['subtext'] = f'{state.get("brt", "NA")}%'

        if state.brt is None:
            state.brt = 60

        if state.rgb is None:
            # print('rgb is none setting now')
            state.rgb = '#F0000000'

    elif light_type == 'dimmable':
        response['params'] = LIGHTING_SIMPLEDIM_PARAMS

        if state.brt is None:
            state.brt = 60

        if state.onOff == 1:
            response['subtext'] = f'{state.brt}%'
        else:
            response['subtext'] = f'Off'

    elif light_type == 'simple':
        print('[LIGHTING] simple light', zone)
    #     if state is None:
    #         response['subtext'] = ''
    #         state = {
    #             'onOff': 0
    #         }
    #     else:
    #         state['clrTemp'] = None
    #         state['rgb'] = None
    #         state['brt'] = None
    #         response['subtext'] = LIGHTING_SIMPLE_ONOFF_TEXT[state.get('onOff')]

        response['params'] = LIGHTING_SIMPLE_PARAMS

    else:
        raise ValueError(f'Unkown light type: {light_type}')

    response['state'] = state

    return response


# Lighting
@router.get('', response_model_exclude_none=True)
async def gui_lighting(request: Request) -> dict:
    # print(request.client)
    # print(dir(request.client))
    # print(f'HOST: {request.client.host}, Port: {request.client.port}')
    # Get Presets
    # Get Settings
    # Get Zones from HW
    # Iterate and add actions for the light
    zones = [v for k, v in request.app.hal.lighting.handler.lighting_zone.items()]
    # print('Zones')
    # [print(x) for x in zones]

    light_status = request.app.hal.lighting.handler.light_status()

    lights_on = light_status.get('on')
    master_sub_text = f'{lights_on} Light{"s" if lights_on > 1 else ""} On'
    if lights_on == 0:
        master_sub_text = 'All lights off'

    MASTER_ZONE = 0
    # Get mast light switch state
    light_master = request.app.hal.lighting.handler.state.get(MASTER_ZONE, {})
    # Get what zones are supported
    zone_types = [x.type for x in zones]
    if 'RGBW' in zone_types:
        most_complex_lz_type = 'RGBW'
    elif 'dimmable' in zone_types:
        most_complex_lz_type = 'SIMPLE_DIM'
    else:
        most_complex_lz_type = 'SIMPLE_ONOFF'

    # Get defined presets
    lighting_presets = []
    for group_id, group in request.app.hal.lighting.handler.lighting_group.items():
        # We only care for presets here no other light groups
        if group.attributes.get('type') != 'LG_PRESET':
            continue

        lighting_presets.append(
            {
                'title': str(group_id),
                'name': f'LightingPreset{group_id}',
                'subtext': 'Light Preset',
                'type': 'Simple',
                'Simple': {
                    'onOff': group.state.onOff
                },
                'state': group.state,
                'actions': ['action', 'action_longpress'],
                'action': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/lighting/lg/{group_id}/state',
                        'type': 'PUT',
                        'params': {
                            'onOff': EventValues.ON
                        }
                    }
                },
                'action_longpress': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/lighting/lg/{group_id}/state',
                        'type': 'PUT',
                        'params': {
                            'save': EventValues.TRUE
                        }
                    }
                }
            }
        )

    lights = {
        'master': {
            'title': 'Light Master',
            'name': 'LightingMasterSwitch',
            'type': 'SIMPLE_ONOFF',
            'SIMPLE_ONOFF': {
                # Get state here
                'onOff': 1 if lights_on > 0 else 0
            },
            'state': {
                'onOff': 1 if lights_on > 0 else 0
            },
            'widget': {
                'step': 5,
                'min': 5,
                'max': 100
            },
            'subtext': master_sub_text,
            'actions': ['action_default', 'action_all'],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/lighting/lg/0/state',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            },
            'action_all': {
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/lighting/lz/0/state',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'str',
                        '$brt': 'int',
                        '$clrTmp': 'int'
                    }
                }
            },
            # TODO: Get from lighting system, if at least one is RGBW set RGBW
            'masterType': most_complex_lz_type,
            'masterState': {
                'onOff': 1 if lights_on > 0 else 0,
                # TODO: Figure out what to show when affecting all lights
                'brt': light_master.get('brt', 50)
            }
        },
        'lights': []
    }

    for zone in zones:
        # print(zone)
        zone_id = zone.instance
        # Check if hidden
        hidden = zone.attributes.get('hidden')
        if hidden is True:
            continue

        zone_state = zone.state

        # print('Zone State', zone_id, zone_state)
        zone_type = zone.type
        light_attributes = light_text_from_state(
            zone_state,
            zone
        )

        state = zone.state.dict()
        # NOTE: Set default brightness, do we really need this ?
        try:
            brightness = zone.state.brt
        except AttributeError:
            brightness = None

        if brightness is None:
            state['brt'] = 80

        onOff = zone.state.onOff
        if onOff is None:
            state['onOff'] = 0

        light = {
            'zone_id': zone_id,
            'name': f'LightingZone{zone_id}',
            'title': zone.attributes.get('name'),
            'subtext': light_attributes.get('subtext'),
            'type': zone_type,
            zone_type: state,
            'state': state,
            'widget': {
                'step': 5,
                'min': 5,
                'max': 100
            },
            'actions': ['action_default', ],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/lighting/lz/{zone_id}/state',
                    'type': 'PUT',
                    'params': light_attributes.get('params')
                }
            }
        }
        lights['lights'].append(light)

    settings = None
    if get_lighting_settings(request.app) != {}:
        settings = {
            'type': 'navigate',
            # 'href': '/ui/lighting/settings',
            'href': '/setting/UiSettingsFeaturesDetailsLights'
        }

    # Todo read from language file and state where applicable
    overview = {
        'title': 'Lighting',
        'name': 'LightingOverview',
        'settings': settings,
        # {
        #     'href': '/ui/lighting/settings'
        # },
        'colorPreferences': [
            {
                'id': 1,
                'type': 'ValuePreset',
                'ValuePreset': {
                    'rgb': '#FFEEFF'
                },
                'actions': ['action_default', 'action_longpress', ],
                'action_default': {
                    'type': 'setValue',
                    'item': 'rgb'
                },
                'action_longpress': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/lighting/color-rgb-preset',
                        'type': 'PUT',
                        'params': {
                            '$id': 'int',
                            '$rgb': 'str'
                        }
                    }
                }
            },
        ],
        'colorTempPreferences': [
            {
                'id': 1,
                'type': 'ValuePreset',
                'ValuePreset': {
                    'clrTmp': '6000'
                },
                'actions': ['action_default', 'action_longpress',],
                'action_default': {
                    'type': 'setValue',
                    'item': 'clrTmp'
                },
                'action_longpress': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/lighting/color-temp-preset',
                        'type': 'PUT',
                        'params': {
                            '$id': 'int',
                            '$clrTmp': 'str'
                        }
                    }
                }
            },
        ],
        'switches': lighting_presets
    }

    #  = get_presets()
    # settings = get_settings()
    response = {
        'overview': overview,
        'lights': lights
    }
    # print('RESPONSE:\n\n', json.dumps(response))
    return response


@router.get('/settings')
async def get_settings(request: Request, http_response: Response) -> dict:
    # Get settings from the right place of HW, SW and State for element water systems
    # Probably central place
    return get_lighting_settings(request.app)
    # lighting = request.app.config.get('lighting')

    # settings = request.app.hal.lighting.handler.get_hw_info()
    # settings['notifications'] = []
    # settings['bottom'] = {
    #     'title': 'Reset Lighting',
    #     'name': 'LightingResetButton',
    #     'type': 'SIMPLE',
    #     'actions': ['DEFAULT',],
    #     'DEFAULT': {
    #         'type': 'api_call',
    #         'action': {
    #             'href': f'{BASE_URL}/api/lighting/reset',
    #             'type': 'PUT',
    #             'params': {}
    #         }
    #     }
    # }

    # return settings
