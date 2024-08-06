import os

from fastapi import APIRouter, Request

from common_libs.models.gui import InfoLabel
from main_service.modules.system_helper import (
    get_iot_status,
    get_ip,
    get_os_release,
)

BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/manufacturing',
    tags=['MANUFACTURING', ]
)


@router.get('', response_model_exclude_none=True)
async def gui_manufacturing(request: Request):
    print('[UI][API] MANUFACTURING')

    # Get IoT status
    get_iot_status(request.app)
    iot_status = request.app.iot_status
    navigation_lock = True
    hide_sidebar = True
    floorplan = request.app.hal.floorPlan
    current_vin = request.app.hal.vehicle.handler.state.get('vin')
    if current_vin is None:
        current_vin = ''

    enable_config = False
    if len(current_vin) == 17:
        enable_config = True

    print('IOT status', iot_status)
    if floorplan != 'VANILLA':      # iot_status.get('status') == 'CONNECTED' and floorplan != 'VANILLA':
        # We are on a floorplan
        hide_sidebar = False
        navigation_lock = False

    os_data = get_os_release()
    ip_data = get_ip()

    response = {
        'overview': {
            'title': 'Manufacturing',
            'name': 'ManufacturingOverview',
            'settings': {
                'href': f'{BASE_URL}/ui/manufacturing/settings',
                'type': 'GET'
            }
        },
        'options': [
            InfoLabel(
                category='system',
                title='OS Version',
                # subtext='ALPHA',
                text=os_data.get('version_id', 'NA')
            ),
            InfoLabel(
                category='system',
                title='WinnConnect Software Version',
                # subtext='ALPHA',
                text=request.app.__version__.get(
                    'version',
                    'NA'
                )
            ),
            InfoLabel(
                category='system',
                title='Connection State',
                text=iot_status.get('status', 'STATUS RETRIEVAL ERROR')
            ),
            InfoLabel(
                category='system',
                title='IP Address',
                subtext=None,
                text=str(get_ip())
            ),
            InfoLabel(
                category='system',
                title='Floorplan',
                text=floorplan
            ),
            # Add VIN entry
            {
                'title': 'VIN',
                'type': 'KeyboardEntry',
                'config': {
                    'title': 'Enter VIN',
                    'minLength': 17,
                    'maxLength': 17,
                    'onlyUpper': True,
                    'hintText': '17 character VIN'
                },
                'active': True,     # Cannot edit when false
                'value_param': 'vin',
                'state': {
                    'vin': current_vin       # Get VIN that is currently set
                },
                'actions': {
                    'ENTER': {
                        'type': 'api_call',
                        'actions': {
                            'href': f'{BASE_URL}/api/vehicle/vin',
                            'type': 'PUT',
                            'params': {
                                '$vin': 'str'
                            }
                        }
                    }
                }
            },

            # Add Download Config Button
            {
                'title': 'Get Config',
                'type': 'WIDGET_BUTTON',
                'enabled': enable_config,   # Only enable if VIN is entered
                'actions': {
                    'TAP': {
                        'type': 'api_call',
                        'actions': {
                            'href': f'{BASE_URL}/api/system/reconfigure',
                            'type': 'PUT',
                        }
                    }
                }
            },
            # Add Reboot System Button
            {
                'title': 'Restart',
                'type': 'WIDGET_BUTTON',
                'actions': {
                    'TAP': {
                        'type': 'api_call',
                        'actions': {
                            'href': f'{BASE_URL}/api/system/reboot',
                            'type': 'PUT',
                        }
                    }
                }
            },
            # Add Reboot System Button
            # {
            #     'title': 'All Lights ON',
            #     'type': 'WIDGET_BUTTON',
            #     'actions': {
            #         'TAP': {
            #             'type': 'api_call',
            #             'actions': {
            #                 'href': f'{BASE_URL}/api/lighting/manufacturing/reset',
            #                 'type': 'PUT',
            #             }
            #         }
            #     }
            # },
            # {
            #     'title': 'Disable Manufacturing',
            #     'type': 'WIDGET_BUTTON',
            #     'actions': {
            #         'TAP': {
            #             'type': 'api_call',
            #             'actions': {
            #                 'href': f'{BASE_URL}/api/system/manufacturing/mode',
            #                 'type': 'PUT',
            #                 'params': {
            #                     'onOff': 0
            #                 }
            #             }
            #         }
            #     }
            # }
        ],
        'navigationLock': navigation_lock,      # We go to this page automatically when in vanilla, manufacturing user cannot leave this nor enter this manually
        'hideSidebar': hide_sidebar         # There shall be no sidebar when this is True
    }

    return response


@router.get('/settings')
async def get_settings(request: Request) -> dict:
    '''Setting for manufacturing.
    TBD'''
    settings = {}
    return settings
