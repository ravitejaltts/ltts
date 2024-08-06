from asyncio import base_futures
import datetime
import time
import json
import os
import pytz
from typing import Optional, List
from common_libs.models.common import (
    RVEvents,
    convert_utc_to_local,
    EventValues,
    FLOORPLAN_TO_INFO
)

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel
from main_service.modules.constants import (
    GALLONS_2_LITER,
    WATER_UNIT_GALLONS,
    WATER_UNIT_LITER,
    WATER_UNITS,
    TEMP_UNITS,
    TEMP_UNIT_PREFERENCE_KEY,
    TEMP_UNIT_FAHRENHEIT,
    _celcius_2_fahrenheit,
    fahrenheit_2_celcius,
    TIME_ZONE_PREFERENCE,
    DISTANCE_UNIT_MILES,
    DISTANCE_UNIT_KILOMETERS,
    TIME_MODE_AM,
    DISTANCE_UNITS_PREFERENCE
)
from main_service.modules.ui_helper import (
    get_temp_unit_preferences
)
from main_service.modules.system_helper import (
    read_about_from_bld_directory
)

from main_service.modules.system_helper import (
    get_ip,
    get_iot_status,
    get_bt_status,
    get_bt_mac,
)

from .helper import get_watersystems_features_settings


BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/settings',
    tags=['SETTINGS', ]
)


def get_general_about_settings():
    return [
        {
            'title': 'My RV',
            'data': []
        }
    ]


def get_sw_update_settings():
    return []


def get_general_settings():
    return {
        'title': 'General',
        'configuration': [
            {
                'data': [
                    {
                        'title': 'About My RV',
                        'data': get_general_about_settings()
                    },
                    {
                        'title': 'Software Updates',
                        'data': get_sw_update_settings()
                    }
                ]
            }
        ]
    }


def get_bt_settings():
    return []


async def get_cellular_settings(app):
    # Check IoT Status
    app.iot_status = get_iot_status(app)
    print('[IOTSTATUS]', app.iot_status)
    subscription_status = {}
    # Check cellular status
    # Assemble Text and options
    # TODO: Get connection status from Cradlepoint
    topText_value = 'NA'        # Should be the type of connection, like LTE, No Connection, 5G etc.

    iot_connected = app.iot_status.get('status', 'NA')
    # iot_msg = iot_status.get('msg', 'NA')
    if iot_connected == 'ERROR':
        topText_value = 'Disconnected'

    # Could be
    # Winnebago Connect Premium
    # Winnebago Connect Premium + Wi-Fi
    #

    # TODO: Implement the subscription level
    # Where does that live ? IoT coming from Platform ?
    winnconnect_string = subscription_status.get('subscription', 'Winnebago Connect Premium')

    cellular_status = await app.hal.connectivity.handler.get_connection_status()
    print('[CELLULAR][STATUS]', cellular_status)
    # {'eth-wan': 'disconnected', 'sim1': 'connecting', 'sim1_signal': 'unknown', 'sim2': 'disconnected', 'sim2_signal': 'unknown'}
    cellular_strength = 0
    # TODO: Add that to the connection status
    connection_state = 'Disconnected'
    cellular_network_str = ''
    if cellular_status.get('eth-wan') == 'connected':
        cellular_network_str = 'UPLINK'
        connection_state = 'Connected'
    else:
        cellular_network_str = 'LTE'

        for key, value in cellular_status.items():
            if key == 'sim1' and value == 'connected':
                connection_state = 'Connected'
                cellular_strength = cellular_status.get(f'{key}_signal')

            elif key == 'sim1' and value == 'connecting':
                connection_state = 'Connecting...'

            elif key == 'sim2' and value == 'connected':
                connection_state = 'Connected'
                cellular_strength = cellular_status.get(f'{key}_signal')

            elif key == 'sim2' and value == 'connecting':
                connection_state = 'Connecting...'

    if cellular_network_str:
        connection_status_str = connection_state + ' - ' + cellular_network_str
    else:
        connection_status_str = connection_state

    # TODO: Get from component settings
    cellular_data_enabled = app.config['cellular'].get('onOff', 1)
    cellular_response = {
        'title': 'Cellular',
        'type': 'SETTINGS_LIST_ITEM_NAV',
        'value': connection_state,
        'data': [
            {
                'title': 'Cellular',
                'data': [
                    {
                        'title': 'CELLULAR INFO / SUBSCRIPTION',
                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                        'data': [
                            # {
                            #     'title': 'Cellular Data',
                            #     'type': 'SIMPLE_ONOFF',
                            #     'value': 'On' if cellular_data_enabled == 1 else 'Off',
                            #     'state': {
                            #             'onOff': cellular_data_enabled,
                            #     },
                            #     'actions': {
                            #         'TOGGLE': {
                            #             'type': 'api_call',
                            #             'action': {
                            #                     # TODO: Move this to a state update in the cellular component
                            #                     'href': f'{BASE_URL}/api/connectivity/cellular/onoff',
                            #                     'type': 'PUT',
                            #                     'params': {
                            #                         '$onOff': 'int',
                            #                         'item': 'CellularEnabled',
                            #                     }
                            #             }
                            #         }
                            #     },
                            # },
                            {
                                'title': winnconnect_string,
                                'type': 'CELLULAR_INFO_LABEL',
                                'value': connection_status_str,
                                'state': {
                                    'strength': cellular_strength,
                                    'network': cellular_network_str
                                },
                                'actions': {
                                    'DISPLAY': {
                                        'type': 'api_call',
                                        'action': {
                                                'href': f'{BASE_URL}/api/connectivity/cellular',
                                                'type': 'GET',
                                        }
                                    }
                                },
                            },
                        ]
                    }
                ]
            }
        ]
    }
    if cellular_network_str == 'UPLINK':
        cellular_response['data'][0]['data'][0]['data'].append(
            {
                'type': 'SUPPORT_TEXT',
                'text': 'System detected a wired WAN connection. Connectivity and general far field functionality of Winnebago Connect depends on that external connection.'
            }
        )

    return cellular_response


def nested_get(obj, path, sep='.'):
    '''Get a nested value from a dictionary'''
    pass


@router.get('/', response_model_exclude_none=True)
async def gui_settings(request: Request):
    '''Main UI Settings API endpoint.'''
    bt_enabled = request.app.config.get(
        'BluetoothSettings', {}).get('BluetoothControlEnabled')
    print('BluetoothEnabled', bt_enabled)
    backup_enabled = request.app.config.get(
        'settings', {}).get('DataBackupEnabled')

    # TODO: Link to real data
    display_brightness = request.app.config.get(
        'settings', {}).get('DisplayBrightness', 50)

    current_timeout_value = request.app.config.get(
        'activity_settings', {}).get('lockTimeMinutes', 5)
    watersystems = request.app.config.get('watersystems')
    volume_preference = watersystems.get('VolumeUnitPreference')
    current_temp_unit = request.app.config.get('climate', {}).get(
        TEMP_UNIT_PREFERENCE_KEY, TEMP_UNIT_FAHRENHEIT)
    current_temp_text = TEMP_UNITS.get(current_temp_unit, {}).get('long')
    current_temp_short = TEMP_UNITS.get(current_temp_unit, {}).get('short')
    current_timezone_preference = request.app.config.get(
        'timezone', {}).get('TimeZonePreference')
    time_offset = request.app.config.get('time', {}).get('time_offset')
    day_offset = request.app.config.get('date', {}).get('day_offset')
    current_utc_datetime = datetime.datetime.utcnow()
    if time_offset == 0:
        current_time = convert_utc_to_local(
            datetime.datetime.utcnow(), current_timezone_preference).strftime('%I:%M %p')
    else:
        current_time = (current_utc_datetime +
                        datetime.timedelta(seconds=time_offset)).strftime('%I:%M %p')

    if day_offset == 0:
        current_date = convert_utc_to_local(
            datetime.datetime.utcnow(), current_timezone_preference).strftime('%m-%d-%Y')
    else:
        current_date = (current_utc_datetime +
                        datetime.timedelta(days=day_offset)).strftime('%m-%d-%Y')
    adjust_sunset_onOff = request.app.config.get(
        'settings', {}).get('AutoScreenModeSunset')

    print('ADJUST SUNSET SETTING', adjust_sunset_onOff)

    push_notification_onOff = request.app.config.get('push_notification')
    rain_sensor_onoff = request.app.config.get('climate', {}).get('rainSensor')
    location_onOff = request.app.config.get('climate', {}).get('location', 0)
    try:
        gps_opt_out = request.app.hal.vehicle.handler.vehicle[2].state.usrOptIn
    except Exception as err:
        print('GPS OPT OUT ERROR', err)
        gps_opt_out = False
    location_onOff = 1 if gps_opt_out else 0

    distance_unit_preference = request.app.config.get(
        'distanceunits', {}).get('DistanceUnits')
    automatic_backup = request.app.config.get(
        'settings', {}).get('DataBackupEnabled')
    restore_previous_backup = 'restore previous backup'
    current_temp_unit = request.app.config.get('climate', {}).get(
        TEMP_UNIT_PREFERENCE_KEY, TEMP_UNIT_FAHRENHEIT)
    current_temp_short = TEMP_UNITS.get(current_temp_unit, {}).get('short')
    indoor_temp_alert = request.app.config['climate']['indoorTempAlert']
    max_indoor_temp = 90
    min_indoor_temp = 37

    if current_temp_unit == 'C':
        max_indoor_temp = fahrenheit_2_celcius(max_indoor_temp)
        min_indoor_temp = fahrenheit_2_celcius(min_indoor_temp)

    alertonoff = request.app.config['refrigerator']['AlertOnOff']

    # TODO: Re-enable upon REFRIGERATOR return
    # notification_key = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
    # fridge_note = request.app.event_notifications[notification_key]
    # trigger_value = fridge_note.trigger_value.split(',')
    # lower_limit_value = float(trigger_value[0])
    # upper_limit_value = float(trigger_value[1])
    # pass_fail_test = 0

    if hasattr(request.app.hal, 'climate'):
        if hasattr(request.app.hal.climate.handler, 'heater'):
            try:
                furnace_meta = request.app.hal.climate.handler.heater.get(1).meta
            except AttributeError:
                furnace_meta = {}
        else:
            furnace_meta = {}

        if hasattr(request.app.hal.climate.handler, 'air_conditioner'):
            try:
                ac_meta = request.app.hal.climate.handler.air_conditioner.get(1).meta
            except AttributeError:
                ac_meta = {}
        else:
            ac_meta = {}

        if hasattr(request.app.hal.climate.handler, 'roof_vent'):
            try:
                roof_fan_meta = request.app.hal.climate.handler.roof_vent.get(1).meta
            except AttributeError:
                roof_fan_meta = {}
        else:
            roof_fan_meta = {}

    inverter_meta = request.app.hal.energy.handler.inverter[1].meta

    wh_meta = request.app.hal.watersystems.handler.water_heater[1].meta
    wp_meta = request.app.hal.watersystems.handler.water_pump[1].meta

    error_list = request.app.error_log
    print('ERROR LIST', error_list)
    # TODO: Unnest this, why is this not a straight list ?
    if len(error_list) == 0:
        # We want to show at least one item, so the page does not look like it
        # is broken
        error_list.append([
                {
                    'title': 'No Errors',
                    'type': 'ERROR',
                    'topText': 'No Errors',
                    'timestamp': 'Now',
                    'body': 'No errors logged in the system.',
                }
            ]
        )
    connected_devices_list = request.app.config.get(
        'BluetoothSettings', {}).get('ConnectedDevices')

    bluetooth_connected_devices_list = []
    for device in connected_devices_list:
        new_device = {
            'title': device.get('name'),
            'value': device.get('connected'),
            'actions': {
                'DISCONNECT': {
                    'type': 'api_call',
                    'action': {
                        'type': 'PUT',
                        'href': f'{BASE_URL}/api/system/bluetooth/disconnect',
                        'params': {
                            '$value': 'int'
                        }
                    }
                },
                'FORGET_DEVICE': {
                    'type': 'api_call',
                    'action': {
                        'type': 'PUT',
                        'href': f'{BASE_URL}/api/system/bluetooth/forgetdevice',
                        'params': {
                            '$value': 'int'
                        }
                    }
                }
            }
        }
        bluetooth_connected_devices_list.append(new_device)

    cellular_connected = request.app.config['cellular']
    cool_diff_temp = request.app.config['climate']['coolDifferential']['setTemp']
    heat_cool_min = request.app.config['climate']['heatCoolMin']['setTemp']
    comp_min_out = request.app.config['climate']['minOutDoor']['setTemp']

    # today_date = '2-27-23'
    # TODO: Get list of settings from main app config
    floorplan = request.app.hal.floorPlan
    model = FLOORPLAN_TO_INFO.get(floorplan, {}).get('name', '')
    floorplan = FLOORPLAN_TO_INFO.get(floorplan, {}).get('floorplan', '')
    model = f'{model} {floorplan}'
    vin = request.app.config.get('VIN', '--')
    version = 'Current Version'     # TODO: Check if this is most current
    year = request.app.iot_status.get('model_year', '--')  # from IoT
    serial_number = request.app.iot_status.get('serial_number', '--')   # from IoT

    settings_model = {
        'title': model,
        'name': 'UiSettingAboutDetails',
        'type': "SETTINGS_SECTIONS_LIST",
        'data': [
            {
                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                'title': 'RV PROFILE',
                'items': [
                    #     'title': 'RV PROFILE',
                    #     'data': [
                    {
                        'type': 'SETTINGS_INFO_SIMPLE',
                        'title': 'Model',
                        'value': model
                    },
                    {
                        'type': 'SETTINGS_INFO_SIMPLE',
                        'title': 'Year',
                        'value': year

                    },
                    {
                        'type': 'SETTINGS_INFO_SIMPLE',
                        'title': 'Floor Plan',
                        'value': floorplan
                    },
                    {
                        'type': 'SETTINGS_INFO_SIMPLE',
                        'title': 'VIN',
                        'value': vin
                    },
                    {
                        'type': 'SETTINGS_INFO_SIMPLE',
                        'title': 'Serial #',
                        'value': serial_number
                    }
                ]
            },
            {
                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                'title': 'WINNCONNECT',
                'items': [
                    {
                        'type': 'SETTINGS_INFO_MULTI_NAVIGATION',
                        'title': 'Software Version',
                        'value': version,
                        'subtext': request.app.__version__,
                    },
                ],
                'actions': {
                    'value': {
                        'TAP': {
                            'type': 'navigate',
                            'action': {
                                'href': '/software/update',
                            },
                        }
                    },
                },
            }
        ]
    }

    settings_bluetooth = {
        'title': 'Bluetooth',
        'configuration': [
            {
                'title': None,
                'data': [
                    {
                        'title': 'Enable control through Bluetooth',
                        'type': 'Simple',
                        'Simple': {
                            'onOff': bt_enabled
                        },
                        'actions': ['action_default', ],
                        'action_default': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/settings/bluetooth/onoff',
                                'type': 'PUT',
                                'params': {
                                    '$onOff': 'int',
                                    'item': 'BluetoothControlEnabled'
                                }
                            }
                        }
                    },
                    # {
                    #     'title': 'Bluetooth SSID'
                    # }
                ]
            },
            {
                'title': 'Users',
                'data': []
            }
        ],
        'actions': ['pair_user', ],
        'pair_user': {
            'title': 'Pair a New User',
            'actions': ['navigate', ],
            'navigate': {
                'type': 'navigate',
                'action': {
                    'href': '/home/bluetooth/pair'
                }
            }
        }
    }

    settings_notifications = {
        'title': 'Notifications',
        'name': 'UiSettingsNotificationsDetails',
        'type': 'SETTINGS_SECTIONS_LIST',  # should it be SETTINGS_TOGGLE?
        'data': [
            {
                'title': 'Notifications',
                'items': [
                    {
                        'title': 'Allow Push Notifications',
                        'type': 'SIMPLE_ONOFF',
                        'state': {
                            'onoff': push_notification_onOff,
                        },
                        'actions': {
                            'TOGGLE': {
                                'type': 'api_call',
                                'action': {
                                    'href': f'{BASE_URL}/api/system/pushnotification',
                                    'type': 'PUT',
                                    'params': {
                                        '$onOff': 'int',
                                    },
                                },
                            },
                        },
                    }
                ],
            },

        ]
    }

    settings_wifi = {
        'title': 'Wi-Fi',
        'type': 'SETTINGS_LIST_ITEM_NAV',
        'value': 'MyWifi99',
        'data': [
            {
                'title': 'Wi-Fi',
                'data': [
                    {
                        'title': None,
                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                        'data': [
                            {
                                'title': 'Wi-Fi',
                                'type': 'SIMPLE_ONOFF',
                                'state': {
                                    'onoff': 0,
                                },
                                'actions': {
                                    'TOGGLE': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'{BASE_URL}/api/settings/wifi/onoff',
                                            'type': 'PUT',
                                            'params': {
                                                '$onoff': 'int',
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                'title': 'Wi-Fi Network',
                                'type': 'SETTINGS_LIST_ITEM_NAV',
                                'value': 'selected_wifi_network',
                                'data': [
                                    {

                                    }
                                ]
                            },
                        ]
                    },
                    {
                        'title': 'NETWORKS',
                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                        'data': [
                            {
                                'title': 'connected_wifi_name',
                                'value': 'connected_wifi_connected',
                            },
                            {
                                'title': 'Known Networks',
                                'type': 'SETTINGS_LIST_ITEM_NAV',
                                'data': [

                                ]
                            },
                            {
                                'title': 'Network',
                                'actions': {
                                    'TOGGLE': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'{BASE_URL}/api/settings/wifi/onoff',
                                            'type': 'PUT',
                                            'params': {
                                                '$onoff': 'int',
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    },
                    {
                        'title': None,
                        'type': 'SETTINGS_LIST_ITEM_NAV',
                        'data': [
                            {
                                'title': 'Ask to Join Network',
                                'value': 'ask',
                            }
                        ]
                    }
                ]
            }
        ]
    }

    settings_cellular = await get_cellular_settings(request.app)

    try:
        ignition_status = request.app.hal.system.handler.lockouts[EventValues.IGNITION_ON].state.active
    except KeyError as err:
        print(err)
        ignition_status = False

    pairing_steps = [
        {
            'numbered_item': '1',
            'instruction': 'Download the Winnebago App from the Android or Apple App Store.',
        },
    ]
    if ignition_status is False:
        pairing_steps.extend(
            [
                {
                    'numbered_item': '2',
                    'instruction': 'Turn on your RV, and make sure it\'s in park.',
                },
                {
                    'numbered_item': '3',
                    'instruction': 'In the App, create your account and when asked select "WinnConnect Enabled RV".',
                },
                {
                    'numbered_item': '4',
                    'instruction': 'When prompted, scan the QR code to the right.',
                }
            ]
        )
        qr_url = f'{BASE_URL}/api/settings/qr_code_blur'
    else:
        pairing_steps.extend([
            {
                'numbered_item': '2',
                'instruction': 'In the App, create your account and when asked select "WinnConnect Enabled RV".',
            },
            {
                'numbered_item': '3',
                'instruction': 'When prompted, scan the QR code to the right.',
            }
        ])
        qr_url = f'{BASE_URL}/api/settings/qr_code'

    settings_connectivity = {
        'title': 'Connectivity',
        'name': 'UiSettingsConnectivityDetails',
        'type': 'SETTINGS_SECTIONS_LIST',
        'data': [
            {
                'title': 'Connectivity',
                'data': [
                    {
                        'title': None,
                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                        'items': [
                            {
                                'title': 'Bluetooth',
                                'type': 'SETTINGS_LIST_ITEM_NAV',
                                'value': '--',      # TODO: Get from device list, check if a device is currently connected
                                'data': [
                                    {
                                        'title': 'Bluetooth',
                                        'data': [
                                            {
                                                'title': 'BLUETOOTH PREFERENCES',
                                                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                'data': [
                                                    {
                                                        'title': 'Bluetooth',
                                                        'subtext': 'Having trouble connecting? Try turning Bluetooth off and then back on. Then try reconnecting.',
                                                        'type': 'SIMPLE_ONOFF',
                                                        'state': {
                                                            'onOff': bt_enabled,
                                                        },
                                                        'actions': {
                                                            'TOGGLE': {
                                                                'type': 'api_call',
                                                                'action': {
                                                                    'href': f'{BASE_URL}/api/settings/bluetooth/onoff',
                                                                    'type': 'PUT',
                                                                    'params': {
                                                                        '$onOff': 'int',
                                                                        'item': 'BluetoothControlEnabled',
                                                                    }
                                                                }
                                                            }
                                                        },
                                                    },
                                                    {
                                                        'type': 'SUPPORT_TEXT',
                                                        'text': 'Having trouble connecting? Try turning Bluetooth off and then back on. Then try reconnecting.'
                                                    }
                                                    # {
                                                    #     'title': 'Reset Bluetooth',
                                                    #     'type': 'SIMPLE_ONOFF',
                                                    #     'state': {
                                                    #         'onOff': 0,
                                                    #     },
                                                    #     'actions': {
                                                    #         'TOGGLE': {
                                                    #             'type': 'api_call',
                                                    #             'action': {
                                                    #                 'href': f'{BASE_URL}/api/settings/bluetooth/reset',
                                                    #                 'type': 'PUT'
                                                    #             }
                                                    #         }
                                                    #     },
                                                    # },
                                                    # {
                                                    #     'title': 'Reset Bluetooth',
                                                    #     'type': 'BUTTON',
                                                    #     'actions': {
                                                    #         'TAP': {
                                                    #             'type': 'api_call',
                                                    #             'action': {
                                                    #                 'href': f'{BASE_URL}/api/settings/bluetooth/reset',
                                                    #                 'type': 'PUT'
                                                    #             }
                                                    #         }
                                                    #     },
                                                    # },
                                                ]
                                            },
                                            # {
                                            #     'title': 'Pair a Device',
                                            #     'type': 'BUTTON',
                                            #     'actions': {
                                            #         'TAP': {
                                            #             'type': 'api_call',
                                            #             'action': {
                                            #                 'href': f'{BASE_URL}/api/settings/bluetooth/pairing',
                                            #                 'type': 'PUT',
                                            #                 'params': {
                                            #                     '$onOff': 'int'
                                            #                 }
                                            #             }
                                            #         }
                                            #     },
                                            # },
                                            # {
                                            #     'title': 'USER DEVICES',
                                            #     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                            #     'data': connected_devices_list
                                            # },
                                        ]
                                    },
                                ]
                            },
                            # Hidden until TCU / Connectivity module is selected and integrated
                            # settings_wifi,
                            settings_cellular,
                            {
                                'title': 'Pair a Device',
                                'type': 'BUTTON',
                                'data': [
                                    {
                                        'title': 'SETUP WINNEBAGO CONNECT',
                                        'subtext': 'To use Winnebago Connect on your phone:',
                                        'data': [
                                            {
                                                'title': 'To use Winnebago Connect on your phone:',
                                                'data': pairing_steps
                                            },
                                            {
                                                'title': None,
                                                'type': 'IMAGE',
                                                'subtext': 'Use the Winnebago app to scan this code',
                                                'actions': {
                                                    'DISPLAY': {
                                                        'type': 'api_call',
                                                        'action': {
                                                                'href': qr_url,
                                                            'type': 'GET',
                                                        }
                                                    }
                                                },
                                                'footer': f'VIN: {vin}'
                                            },

                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    },
    # TODO: Refrigerator REFRIGERATOR
    # settings_features_refrigerator = {
    #     'title': 'Refrigerator',
    #     'type': 'SETTINGS_LIST_ITEM_NAV',
    #     'name': 'UiSettingsFeaturesDetailsRefrigerator',
    #     'items': [
    #         {
    #             'type': 'SETTINGS_LIST_ITEM_NAV',
    #             'title': 'Refrigerator Temp Alert',
    #             'selected_text': 'On',
    #             'item': [
    #                 {
    #                     'title': 'Refrigerator Temp Alert',
    #                     'type': 'SIMPLE_ONOFF',
    #                     'state': {
    #                         'onoff': alertonoff,
    #                     },
    #                     'actions': {
    #                         'TOGGLE': {
    #                             'type': 'api_call',
    #                             'action': {
    #                                 'href': f'{BASE_URL}/api/climate/refrigerator/settings/alert',
    #                                 'type': 'PUT',
    #                                 'params': {
    #                                     '$onOff': 'int',
    #                                 },
    #                             }
    #                         },
    #                     }
    #                 },
    #                 {
    #                     'title': None,
    #                     'items': [
    #                         {
    #                             'title': 'MAX TEMP',
    #                             'value': _celcius_2_fahrenheit(upper_limit_value),
    #                             'type': 'Upper_Limit',
    #                             'actions': {
    #                                 'TAP': {
    #                                     'type': 'api_call',
    #                                     'action': {
    #                                         'href': f'{BASE_URL}/api/climate/refrigerator/settings/temprange',
    #                                         'type': 'PUT',
    #                                         'params': {
    #                                             '$fdg_upper_limit': 'float',
    #                                             '$fdg_lower_limit': 'float',
    #                                         }
    #                                     }
    #                                 }
    #                             }
    #                         },
    #                         {
    #                             'title': 'MIN TEMP',
    #                             'value': _celcius_2_fahrenheit(lower_limit_value),
    #                             'type': 'Lower_Limit',
    #                             'actions': {
    #                                 'TAP': {
    #                                     'type': 'api_call',
    #                                     'action': {
    #                                         'href': f'{BASE_URL}/api/climate/refrigerator/settings/temprange',
    #                                         'type': 'PUT',
    #                                         'params': {
    #                                             '$fdg_upper_limit': 'float',
    #                                             '$fdg_lower_limit': 'float',
    #                                         }
    #                                     }
    #                                 }
    #                             }
    #                         },
    #                         {
    #                             'title': 'Restore Default',
    #                             'type': 'BUTTON',
    #                             'subtext': 'Receive an alert when the refrigerator is outside of the temperature range.',
    #                             'actions': {
    #                                 'TAP': {
    #                                     'type': 'api_call',
    #                                     'action': {
    #                                         'href': f'{BASE_URL}/api/climate/refrigerator/settings/restoredefault',
    #                                         'type': 'PUT'
    #                                     }
    #                                 }
    #                             }
    #                         }
    #                     ]
    #                 }
    #             ]
    #         },
    #         {
    #             'type': 'SETTINGS_SECTIONS_ITEM_LIST',
    #             'title': 'MANUFACTURER INFORMATION',
    #             'data': [
    #                 {
    #                     'title': 'Manufacturer',
    #                     'value': 'Fridges R. US'
    #                 },
    #                 {
    #                     'title': 'Product Model',
    #                     'value': 'ABC123'
    #                 }
    #             ]
    #         }
    #     ]
    # }

    has_itc = False
    for i, v in request.app.hal.lighting.handler.lighting_zone.items():
        if 'ITC' in v.attributes.get('type'):
            has_itc = True
            break

    settings_features = {
        'title': 'Features',
        'name': 'UiSettingsFeaturesDetails',
        'type': 'SETTINGS_SECTIONS_LIST',
        'configuration': [
            {
                'title': 'Climate Control',
                'type': 'SETTINGS_LIST_ITEM_NAV',
                'name': 'UiSettingsFeaturesDetailsClimate',
                'data': [
                    {
                        'title': 'Climate Control',
                        'configuration': [
                            # NOTE: Need to fix thermostat
                            # {
                            #     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                            #     'title': 'THERMOSTAT',
                            #     'items': [
                            #         # {
                            #         #     'type': 'SETTINGS_LIST_ITEM_NAV',
                            #         #     'title': 'Heat/Cool Min Delta',
                            #         #     'value': heat_cool_min,
                            #         #     'data': [
                            #         #         {
                            #         #             'title': 'Heat/Cool Min Delta',
                            #         #             'subtext': 'The minimum temperature separation between the heat and cool temperatures in Auto Mode',
                            #         #             'actions': {
                            #         #                 'TAP': {
                            #         #                     'type': 'api_call',
                            #         #                     'action': {
                            #         #                         'href': f'{BASE_URL}/api/climate/heatcoolmindelta',
                            #         #                         'type': 'PUT',
                            #         #                         'params': {
                            #         #                             '$setTemp': 'float',
                            #         #                             '$unit': 'F'
                            #         #                         },
                            #         #                     },
                            #         #                 },
                            #         #             }
                            #         #         },
                            #         #         {
                            #         #             'title': 'Restore Default',
                            #         #             'type': 'Button',
                            #         #             'actions': {
                            #         #                 'TAP': {
                            #         #                     'type': 'api_call',
                            #         #                     'action': {
                            #         #                         'href': f'{BASE_URL}/api/climate/heatcoolmindelta/restoredefault',
                            #         #                         'type': 'PUT',
                            #         #                     },
                            #         #                 },
                            #         #             }
                            #         #         }
                            #         #     ]
                            #         # },
                            #         # {
                            #         #     'type': 'SETTINGS_LIST_ITEM_NAV',
                            #         #     'title': 'Cool Differential Temp',
                            #         #     'value': cool_diff_temp,
                            #         #     'data': [
                            #         #         {
                            #         #             'title': 'Cool Differential Temp',
                            #         #             'subtext': 'The minimum temperature difference from the cool set point before the compressor starts cooling',
                            #         #             'actions': {
                            #         #                 'TAP': {
                            #         #                     'type': 'api_call',
                            #         #                     'action': {
                            #         #                         'href': f'{BASE_URL}/api/climate/cooldifferential',
                            #         #                         'type': 'PUT',
                            #         #                         'params': {
                            #         #                             '$setTemp': 'float',
                            #         #                             '$unit': 'F'
                            #         #                         },
                            #         #                     },
                            #         #                 },
                            #         #             }
                            #         #         },
                            #         #         {
                            #         #             'title': 'Restore Default',
                            #         #             'type': 'Button',
                            #         #             'actions': {
                            #         #                 'TAP': {
                            #         #                     'type': 'api_call',
                            #         #                     'action': {
                            #         #                         'href': f'{BASE_URL}/api/climate/cooldifferential/restoredefault',
                            #         #                         'type': 'PUT',
                            #         #                     },
                            #         #                 },
                            #         #             }
                            #         #         }
                            #         #     ]
                            #         # },
                            #         # {
                            #         #     'type': 'SETTINGS_LIST_ITEM_NAV',
                            #         #     'title': 'Compressor Min Outdoor Temp',
                            #         #     'value': comp_min_out,
                            #         #     'data': [
                            #         #         {
                            #         #             'title': 'Compressor Min Outdoor Temp',
                            #         #             'subtext': 'The compressor will not run below this outdoor temperature',
                            #         #             'actions': {
                            #         #                 'TAP': {
                            #         #                     'type': 'api_call',
                            #         #                     'action': {
                            #         #                         'href': f'{BASE_URL}/api/climate/minoutdoor',
                            #         #                         'type': 'PUT',
                            #         #                         'params': {
                            #         #                             '$setTemp': 'float',
                            #         #                             '$unit': 'F'
                            #         #                         },
                            #         #                     },
                            #         #                 },
                            #         #             }
                            #         #         },
                            #         #         {
                            #         #             'title': 'Restore Default',
                            #         #             'type': 'Button',
                            #         #             'actions': {
                            #         #                 'TAP': {
                            #         #                     'type': 'api_call',
                            #         #                     'action': {
                            #         #                         'href': f'{BASE_URL}/api/climate/minoutdoor/restoredefault',
                            #         #                         'type': 'PUT',
                            #         #                     },
                            #         #                 },
                            #         #             }
                            #         #         }
                            #         #     ]

                            #         # },
                            #         # {
                            #         #     'type': 'SETTINGS_LIST_ITEM_NAV',
                            #         #     'title': 'Temperature Alert',
                            #         #     'items': [
                            #         #         {
                            #         #             'title': 'Temperature Alert',
                            #         #             'type': 'SIMPLE_ONOFF',
                            #         #             'items': [
                            #         #                 {
                            #         #                     # 'title': 'Indoor Temperature Alert',
                            #         #                     # 'type': 'SIMPLE_ONOFF',
                            #         #                     'subtext': 'Receive an alert when the indoor temperature is outside of this temperature range',
                            #         #                     'state': {
                            #         #                         'onoff': indoor_temp_alert,
                            #         #                     },
                            #         #                     'actions': {
                            #         #                         'TOGGLE': {
                            #         #                             'type': 'api_call',
                            #         #                             'action': {
                            #         #                                 'href': f'{BASE_URL}/api/climate/indoortempalert',
                            #         #                                 'type': 'PUT',
                            #         #                                 'params': {
                            #         #                                     '$onOff': 'int',
                            #         #                                 },
                            #         #                             },
                            #         #                         },
                            #         #                     },
                            #         #                     'title': 'Indoor Temp Alert Range',
                            #         #                     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                            #         #                     'items': [
                            #         #                         {
                            #         #                             'title': 'MAX TEMP',
                            #         #                             'value': f'{max_indoor_temp}° {current_temp_short}',
                            #         #                         },
                            #         #                         {
                            #         #                             'title': 'MIN TEMP',
                            #         #                             'value': f'{min_indoor_temp}° {current_temp_short}',
                            #         #                         }
                            #         #                     ]
                            #         #                 }
                            #         #             ],
                            #         #         },
                            #         #     ]
                            #         # }
                            #     ]
                            # },
                            # TODO: Bring back when implemented
                            # {
                            #     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                            #     'title': 'ROOF HATCH',
                            #     'items': [
                            #         {
                            #             'title': 'Rain Sensor',
                            #             'type': 'SIMPLE_ONOFF',
                            #             'items': [
                            #                 {
                            #                     'title': 'Rain Sensor',
                            #                     'type': 'SIMPLE_ONOFF',
                            #                     'state': {
                            #                         'onoff': rain_sensor_onoff,
                            #                     },
                            #                     'actions': {
                            #                         'TOGGLE': {
                            #                             'type': 'api_call',
                            #                             'action': {
                            #                                 'href': f'{BASE_URL}/api/climate/rainsensor',
                            #                                 'type': 'PUT',
                            #                                 'params': {
                            #                                     '$onOff': 'int'
                            #                                 },
                            #                             },
                            #                         },
                            #                     },
                            #                 }
                            #             ],
                            #         },
                            #     ]
                            # },
                            {
                                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                'title': 'MANUFACTURER INFORMATION',
                                'items': [
                                    {
                                        'type': 'SETTINGS_LIST_ITEM_NAV',
                                        'title': 'Furnace',
                                        'data': [
                                            {
                                                'type': 'SETTINGS_SECTIONS_LIST',
                                                'title': 'MANUFACTURER INFORMATION',
                                                'data': [
                                                        {
                                                            'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                            'title': 'Manufacturer',
                                                            'value': furnace_meta.get("manufacturer")
                                                        },
                                                        {
                                                            'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                            'title': 'Product Model',
                                                            'value': furnace_meta.get("model")
                                                        },
                                                        {
                                                            'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                            'title': 'Part#',
                                                            'value': furnace_meta.get("part")
                                                        }
                                                ]
                                            }
                                        ]

                                    },
                                    {
                                        'type': 'SETTINGS_LIST_ITEM_NAV',
                                        'title': 'Air Conditioner',
                                        'data': [
                                            {
                                                'type': 'SETTINGS_SECTIONS_LIST',
                                                'title': 'MANUFACTURER INFORMATION',
                                                'data': [
                                                    {
                                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                        'title': 'Manufacturer',
                                                        'value': ac_meta.get("manufacturer")
                                                    },
                                                    {
                                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                        'title': 'Product Model',
                                                        'value': ac_meta.get("model")
                                                    },
                                                    {
                                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                        'title': 'Part#',
                                                        'value': ac_meta.get("part")
                                                    }

                                                ]
                                            }
                                        ]
                                    },
                                    {
                                        'type': 'SETTINGS_LIST_ITEM_NAV',
                                        'title': 'Roof Vent',
                                        'data': [
                                            {
                                                'type': 'SETTINGS_SECTIONS_LIST',
                                                'title': 'MANUFACTURER INFORMATION',
                                                'data': [
                                                    {
                                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                        'title': 'Manufacturer',
                                                        'value': roof_fan_meta.get("manufacturer")
                                                    },
                                                    {
                                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                        'title': 'Product Model',
                                                        'value': roof_fan_meta.get("model")
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            # {
            #     'title': 'Energy Management',
            #     'type': 'SETTINGS_LIST_ITEM_NAV',
            #     'name': 'UiSettingsFeaturesDetailsEnergy',
            #     'data': [
            #         {
            #             'title': 'Energy Management'
            #         }
            #     ]
            # },
            {

                'title': 'Inverter',
                'type': 'SETTINGS_LIST_ITEM_NAV',
                'name': 'UiSettingsFeaturesDetailsInverter',
                'data': [
                    {
                        'title': 'Inverter',
                        'data': [
                            {
                                'type': 'SETTINGS_SECTIONS_LIST',
                                'title': 'MANUFACTURER INFORMATION',
                                'data': [
                                    {
                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                        'title': 'Manufacturer',
                                        'value': inverter_meta.get("manufacturer")
                                    },
                                    {
                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                        'title': 'Product Model',
                                        'value': inverter_meta.get("model")
                                    },
                                    {
                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                        'title': 'Part#',
                                        'value': inverter_meta.get("part")
                                    }
                                ]
                            }
                        ]
                    },
                ]

            },
            {
                'title': 'Lights',
                'type': 'SETTINGS_LIST_ITEM_NAV',
                'name': 'UiSettingsFeaturesDetailsLights',
                'data': [
                    {
                        'title': 'Lights',
                        'configuration': [
                            {
                                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                'title': 'MANUFACTURER INFORMATION',
                                'items': [
                                    {
                                        'type': 'SETTINGS_LIST_ITEM_NAV',
                                        'title': x.attributes.get('name'),
                                        'data': [
                                            {
                                                'title': x.attributes.get('name'),
                                                'data': [
                                                    {
                                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                                        'title': 'MANUFACTURER INFORMATION',
                                                        'data': [
                                                            {
                                                                'title': 'Manufacturer Model',
                                                                'value': x.meta.get('manufacturer', '--')
                                                            },
                                                            {
                                                                'title': 'Product Model',
                                                                'value': x.meta.get('model', '--')
                                                            },
                                                            {
                                                                'title': 'Part Number',
                                                                'value': x.meta.get('part', '--')
                                                            }
                                                        ]
                                                    }
                                                ]
                                            },
                                        ]
                                    } for k, x in request.app.hal.lighting.handler.lighting_zone.items() if not x.attributes.get('name') == 'Awning Light'
                                ]
                            },
                            # TODO: Check for a component that indicates we have an ITC controller
                            # To decide to show or not
                            {
                                'title': 'LIGHTING CONTROLLER',
                                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                'data': [
                                    {
                                        'title': 'Lighting Configuration Set',
                                        'type': 'SETTINGS_LIST_ITEM_NAV',
                                        'data': [
                                            {
                                                'title': 'Refer to ITC Controller instructions in Owners Manual',
                                                'subtext': 'Upon replacement of the controller or hard reset it might be necessary to set the HW defaults through this functionality. This will momentary turn all of its lights off and turn default lights back on.',
                                            },
                                            {
                                                'title': 'RESET',
                                                'type': 'BUTTON',
                                                'actions': {
                                                    'TAP': {
                                                        'type': 'api_call',
                                                        'action': {
                                                            'href': f'{BASE_URL}/api/lighting/reset',
                                                            'type': 'PUT',
                                                            'params': {}
                                                        },
                                                    },
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            # {
            #     'title': 'Pet Monitor',
            #     'type': 'SETTINGS_LIST_ITEM_NAV',
            #     'name': 'UiSettingsFeaturesDetailsPetMonitor',
            #     'items': [
            #         {
            #             'title': 'PET MONITOR',
            #             'data': [
            #                 {
            #                     'type': 'SETTINGS_SECTIONS_LIST',
            #                     'title': 'Legal Disclaimer',
            #                     'data': [
            #                         {
            #                             'type': 'SETTINGS_LIST_ITEM_NAV',
            #                             'title': 'Legal Disclaimer',
            #                             'data':  [
            #                                 {
            #                                     'title': 'Legal Disclaimer',
            #                                     'subtext': 'Effective March 31, 2020',
            #                                     'body': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut laborem ipsum dolor sit amet, consectetur adipscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliq.'
            #                                 }
            #                             ]
            #                         }
            #                     ]
            #                 }
            #             ]
            #         }
            #     ]
            # },
            # settings_features_refrigerator,
            {
                'title': 'Water Systems',
                'type': 'SETTINGS_LIST_ITEM_NAV',
                'name': 'UiSettingsFeaturesDetailsWaterSystems',
                'configuration': [
                    {
                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                        'title': 'MANUFACTURER INFORMATION',
                        'items': get_watersystems_features_settings(
                            request.app,
                            section_key='data',
                            list_key='data'
                        )
                    }
                ]
            }
        ]
    }
    settings_display = {
        'title': None,
        'data': [
            {
                'title': 'Display',
                'data': [
                    {
                        'title': 'Brightness',
                        'type': "SETTINGS_SECTIONS_LIST",
                        'data': [
                            {
                                'title': None,
                                'type': 'SimpleSlider',
                                'name': 'SettingsDisplayBrightness',
                                'SimpleSlider': {
                                    'value': display_brightness,
                                    'step': 5,
                                    'min': 10,
                                    'max': 100
                                },
                                'actions': {
                                    'SLIDE': {
                                        'type': 'api_call',
                                        'action': {
                                                'type': 'PUT',
                                                'href': f'{BASE_URL}/api/system/display/brightness',
                                                'params': {
                                                    '$value': 'int'
                                                }
                                        }
                                    }
                                }
                            },
                        ],
                        'configuration': [
                            {
                                # 'title': 'Dim Display After',     # TODO: Temp override
                                'title': 'Turn Off Display After',
                                'type': 'SETTINGS_LIST_ITEM_NAV',
                                'data': [
                                    {
                                        # 'title': 'DIM DISPLAY AFTER',
                                        'title': 'TURN OFF DISPLAY AFTER',
                                        'type': 'SETTINGS_OPTIONS_LIST',
                                        'options': [
                                            {
                                                'key': '1 min',
                                                'value': 1,
                                                'selected': True if current_timeout_value == 1 else False
                                            },
                                            {
                                                'key': '2 mins',
                                                'value': 2,
                                                'selected': True if current_timeout_value == 2 else False
                                            },
                                            {
                                                'key': '5 mins',
                                                'value': 5,
                                                'selected': True if current_timeout_value == 5 else False
                                            },
                                            {
                                                'key': 'Never',
                                                'value': 0,
                                                'selected': True if current_timeout_value == 0 else False
                                            },
                                        ],
                                        'actions': {
                                            'TAP': {
                                                'type': 'api_call',
                                                'action': {
                                                    'type': 'PUT',
                                                    'href': f'{BASE_URL}/api/system/display/autodimming',
                                                    'params': {
                                                        '$value': 'int'
                                                    }
                                                }
                                            }
                                        }
                                    },
                                ],
                            },
                        ],
                    }
                ]
            },
            {
                'title': 'Appearance',
                'type': "SETTINGS_SECTIONS_LIST",
                'data': [
                    {
                        'title': None,
                        'type': 'CustomSelect',
                        'CustomSelect': {
                            'title': None,
                            'options': [
                                {
                                    'title': None,
                                    'name': 'SettingsAppearanceLightMode',
                                    'value': 'LIGHTMODE',
                                    'subtext': 'Light Mode'
                                },
                                {
                                    'title': None,
                                    'name': 'SettingsAppearanceDarkMode',
                                    'value': 'DARKMODE',
                                    'subtext': 'Dark Mode'
                                    # TODO: Define API calls if any
                                }
                            ]
                        },
                        'actions': {
                            'TAP': {
                                'type': 'api_call',
                                'href': f'{BASE_URL}/api/settings/browser/screenmode',
                                'params': {
                                    '$value': 'str'
                                }
                            }
                        }
                    },
                    {
                        # needs an api call to automatically change at sunset
                        'title': 'Automatically Adjust at Sunset',
                        'type': 'SIMPLE_ONOFF',
                        'Simple': {
                            'onOff': adjust_sunset_onOff,
                        },
                        'actions': {
                            'TAP': {
                                'type': 'api_call',
                                'action': {
                                        'href': f'{BASE_URL}/api/settings/browser/screenmode/autosunset',
                                        'type': 'PUT',
                                        'params': {
                                            '$onOff': 'int'
                                        }
                                }
                            }
                        }
                    },
                ]
            },
        ]
    }

    settings_unit_preferences = {
        'title': 'Unit Preferences',
        'name': 'UiSettingsUnitPreferences',
        'type': "SETTINGS_SECTIONS_LIST",
        'data': [
            {
                'title': 'DISTANCE UNITS',
                'type': 'SETTINGS_OPTIONS_LIST',
                'options': [
                    {
                        'key': 'Miles',
                        'value': 0,
                        'selected': True if distance_unit_preference == DISTANCE_UNIT_MILES else False
                    },
                    {
                        'key': 'Kilometers',
                        'value': 1,
                        'selected': True if distance_unit_preference == DISTANCE_UNIT_KILOMETERS else False
                    },
                ],
                'actions': {
                    'TAP': {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/system/distance',
                            'type': 'PUT',
                            'params': {
                                '$value': 'int',
                                'item': 'DistanceUnits',
                            }
                        }
                    }
                }
            },
            {
                'title': 'TEMPERATURE UNITS',
                'type': "SETTINGS_OPTIONS_LIST",
                # 'selected_text': current_temp_text,
                'options': get_temp_unit_preferences(TEMP_UNITS, current_temp_unit),
                'actions': {
                    'TAP': {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/climate/settings',
                            'type': 'PUT',
                            'params': {
                                '$value': 'int',
                                'item': TEMP_UNIT_PREFERENCE_KEY
                            },
                        }
                    }
                }
            },
            {
                'title': 'VOLUME UNITS',
                'type': "SETTINGS_OPTIONS_LIST",
                'options': [
                    {
                        'key': 'Gallons',
                        'value': 0,
                        'selected': True if volume_preference == WATER_UNIT_GALLONS else False
                    },
                    {
                        'key': 'Liters',
                        'value': 1,
                        'selected': True if volume_preference == WATER_UNIT_LITER else False
                    },
                ],
                'actions': {
                    'TAP': {
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
            }

        ]
    }

    # TODO: we have a function that allows to change time and date and it works, but will need to make sure all parts of the system recieve the time change, as currently it works just with timezone
    settings_system = {
        'title': 'System',
        'name': 'UiSettingsSystemsDetails',
        'type': "SETTINGS_SECTIONS_LIST",
        'data': [
            {
                'title': None,
                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                'configuration': [
                    {
                        'title': 'Date and Time',
                        'type': 'SETTINGS_LIST_ITEM_NAV',
                        'data': [
                            # {
                            #     'title': 'Date and Time',
                            #     'data': [
                            #         {
                            #             'title': 'Time Synching',
                            #             'subtext': 'Automatically Update Across Timezones',
                            #             'type': 'Simple',
                            #             'Simple': {
                            #                 'onOff': location_onOff,
                            #             },
                            #             'actions': {
                            #                 'TOGGLE': {
                            #                     'type': 'api_call',
                            #                     'action': {
                            #                         'href': f'{BASE_URL}/api/system/timezone/autosync',
                            #                         'type': 'PUT',
                            #                         'params': {
                            #                             '$onOff': 'int'
                            #                         }
                            #                     }
                            #                 }
                            #             }
                            #         }
                            #     ],
                            # },
                            {
                                'title': 'Date and Time',
                                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                'configuration': [
                                    # {
                                    #     'title': 'Date',
                                    #     'value': current_date,
                                    #     'data': [
                                    #         {
                                    #             'title': 'Set Date',
                                    #             'type': 'BUTTON',
                                    #             'actions': {
                                    #                 'TAP': {
                                    #                     'type': 'api_call',
                                    #                     'action': {
                                    #                         'href': f'{BASE_URL}/api/system/setdate',
                                    #                         'type': 'PUT',
                                    #                         'params': {
                                    #                             '$value': 'int',
                                    #                             'item': 'day_offset'
                                    #                         }
                                    #                     }
                                    #                 }
                                    #             }
                                    #         },
                                    #         {
                                    #             'title': 'Cancel',
                                    #             'type': 'BUTTON',
                                    #             'actions': {
                                    #                 'TAP': {
                                    #                     'type': 'api_call',
                                    #                     'action': {
                                    #                         'href': f'{BASE_URL}/api/system/setdate/cancel',
                                    #                         'type': 'PUT',
                                    #                     }
                                    #                 }
                                    #             }
                                    #         },
                                    #     ]
                                    # },
                                    # {
                                    #     'title': 'Time',
                                    #     'value': current_time,
                                    #     'data': [
                                    #         {
                                    #             'title': 'Set Clock',
                                    #             'type': 'BUTTON',
                                    #             'actions': {
                                    #                 'TAP': {
                                    #                     'type': 'api_call',
                                    #                     'action': {
                                    #                         'href': f'{BASE_URL}/api/system/setclock',
                                    #                         'type': 'PUT',
                                    #                         'params': {
                                    #                             '$value': 'int',
                                    #                             'item': 'time_offset',

                                    #                         }
                                    #                     }
                                    #                 }
                                    #             }
                                    #         },
                                    #         {
                                    #             'title': 'Cancel',
                                    #             'type': 'BUTTON',
                                    #             'actions': {
                                    #                 'TAP': {
                                    #                     'type': 'api_call',
                                    #                     'action': {
                                    #                         'href': f'{BASE_URL}/api/system/setclock/cancel',
                                    #                         'type': 'PUT',
                                    #                     }
                                    #                 }
                                    #             }
                                    #         },
                                    #     ]
                                    # },
                                    {
                                        'title': 'Timezone',
                                        'selected_text': current_timezone_preference,
                                        'data': [
                                            {
                                                'title': 'Timezone',
                                                'type': "SETTINGS_OPTIONS_LIST",
                                                'options': [
                                                    {
                                                        'key': 'Eastern',
                                                        'value': 'US/Eastern',
                                                        'selected': True if current_timezone_preference == 'US/Eastern' else False
                                                    },
                                                    {
                                                        'key': 'Central',
                                                        'value': 'US/Central',
                                                        'selected': True if current_timezone_preference == 'US/Central' else False
                                                    },
                                                    {
                                                        'key': 'Mountain',
                                                        'value': 'US/Mountain',
                                                        'selected': True if current_timezone_preference == 'US/Mountain' else False
                                                    },
                                                    {
                                                        'key': 'Pacific',
                                                        'value': 'US/Pacific',
                                                        'selected': True if current_timezone_preference == 'US/Pacific' else False
                                                    }
                                                ],
                                                'actions': {
                                                    'TAP': {
                                                        'type': 'api_call',
                                                        'action': {
                                                            'href': f'{BASE_URL}/api/system/timezone/settings',
                                                            'type': 'PUT',
                                                            'params': {
                                                                '$value': 'str',
                                                                'item': TIME_ZONE_PREFERENCE
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                ]
            },
            {
                'title': None,
                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                'configuration': [
                    {
                        'title': 'Location',
                        'type': 'SETTINGS_LIST_ITEM_NAV',
                        'data': [
                            {
                                'title': 'Location',
                                'data': [
                                    {
                                        'title': 'Location',
                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                        'data': [
                                            {
                                                'title': 'Allow WinnConnect to Use Location',
                                                'type': 'Simple',
                                                'belowtext': 'When Location is turned on, WinnConnect may approximate your vehicle\'s location through Wi-Fi, Bluetooth, GPS, cellular network, and network connections. When Location is turned off, location data will not be stored, which will impact some features, such as Weather reporting.',
                                                'Simple': {
                                                    'onOff': location_onOff,
                                                },
                                                'actions': {
                                                    'TOGGLE': {
                                                        'type': 'api_call',
                                                        'action': {
                                                            'href': f'{BASE_URL}/api/system/location',
                                                            'type': 'PUT',
                                                            'params': {
                                                                '$onOff': 'int'
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ]


                            }
                        ],
                    },
                ]
            },
            {
                'title': None,
                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                'configuration': [
                    {
                        'title': 'Error Log',
                        'type': 'SETTINGS_LIST_ITEM_NAV',
                        'data': [
                            {
                                'title': 'Error Log',
                                'data': error_list,
                                'actions': {
                                    'DISPLAY': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'{BASE_URL}/api/setting/errorlog',
                                            'type': 'PUT',
                                            'params': {
                                                '$onOff': 'int'
                                            }
                                        }
                                    }
                                }

                            },
                        ]
                    },
                ]
            },
            {
                'title': None,
                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                'configuration': [
                    # {
                    #     'title': 'User Configuration Backup',
                    #     'type': 'SETTINGS_LIST_ITEM_NAV',
                    #     'data': [
                    #         {
                    #             'title': 'User Configuration Backup',
                    #             'type': 'Initial Setup Screen',
                    #             'data': [
                    #                 {
                    #                     'title': None,
                    #                     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                    #                     'data': [
                    #                         {
                    #                             'title': 'Backup Your RV Settings',
                    #                             'subtext': 'Connect your RV to your phone through the Winnebago App',
                    #                             'belowtext': 'From your mobile device download the Winnebago App through Google Play or Apple App store, create your account and start pairing!',
                    #                         },
                    #                         {
                    #                             'title': 'Start Pairing',
                    #                             'type': 'BUTTON',
                    #                             'actions': {
                    #                                 'action_default': {
                    #                                     'type': 'api_call',
                    #                                     'action': {
                    #                                         'href': f'{BASE_URL}/api/setting/bluetooth',
                    #                                         'type': 'PUT',
                    #                                         'params': {
                    #                                             '$onOff': 'int'
                    #                                         }
                    #                                     }
                    #                                 }
                    #                             }
                    #                         }
                    #                     ]

                    #                 }
                    #             ]
                    #         },
                    #         {
                    #             'title': 'User Configuration Backup',
                    #             'type': 'Original Screen',
                    #             'data': [
                    #                 {
                    #                     'title': 'SYNC USER CONFIGURATION',
                    #                     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                    #                     'data': [
                    #                         {
                    #                             'title': 'Automatically Backup',
                    #                             'subtext': 'Syncs Your RV Settings to Your Winnebago Account',
                    #                             'bottomtext': f'Last backup {last_config_backup}',
                    #                             'Simple': {
                    #                                 'onOff':  automatic_backup,
                    #                             },
                    #                             'actions': {
                    #                                 'TOGGLE': {
                    #                                     'type': 'api_call',
                    #                                     'action': {
                    #                                         'href': f'{BASE_URL}/api/settings/auto/databackup',
                    #                                         'type': 'PUT',
                    #                                         'params': {
                    #                                             '$onOff': 'int',
                    #                                             'item': 'DataBackupEnabled',
                    #                                         }
                    #                                     }
                    #                                 }
                    #                             }
                    #                         },
                    #                         {
                    #                             'title': 'Manually Backup Now',
                    #                             'type': 'BUTTON',
                    #                             'data': [
                    #                                 {
                    #                                     'title': None,
                    #                                     'type': 'Loading Screen',
                    #                                     'subtext': 'Backing Up Configuration Data...'
                    #                                 },
                    #                                 {
                    #                                     'title': 'Backup Failed',
                    #                                     'type': 'Failed Screen',
                    #                                     'subtext': 'Could not complete your configuration data backup, please check your connection and try again.',
                    #                                     'data': [
                    #                                         {
                    #                                             'title': 'Okay',
                    #                                             'type': 'BUTTON',
                    #                                             'actions': {
                    #                                                 'TAP': {
                    #                                                     'type': 'navigate',
                    #                                                     'actions': {
                    #                                                         'TAP': {
                    #                                                             'href': '/databackup',
                    #                                                             'type': 'PUT',
                    #                                                             'params': {
                    #                                                                 '$onOff': 'int'
                    #                                                             }
                    #                                                         }
                    #                                                     }
                    #                                                 }
                    #                                             }
                    #                                         }
                    #                                     ]
                    #                                 },
                    #                             ],
                    #                             'actions': {
                    #                                 'TAP': {
                    #                                     'type': 'api_call',
                    #                                     'action': {
                    #                                         'href': f'{BASE_URL}/api/settings/databackup',
                    #                                         'type': 'PUT',
                    #                                         'params': {
                    #                                             '$onOff': 'int',
                    #                                             'item': 'DataBackupEnabled',
                    #                                         }
                    #                                     }
                    #                                 }
                    #                             }

                    #                         }
                    #                     ]
                    #                 },
                    #                 {
                    #                     'title': 'RESTORE SYSTEM SETTINGS',
                    #                     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                    #                     'bottomtext': 'Restore previously saved settings for Features, Smart BUTTONs, GPS, Cellular settings, custom Home Screen widget order, Display, Date & Time, and Unit Preferences.',
                    #                     'data': [
                    #                         {
                    #                             'title': 'Restore from Backup',
                    #                             'value': restore_previous_backup,
                    #                         }
                    #                     ]
                    #                 }
                    #             ]
                    #         },


                    #     ]
                    # },

                    # better idea to allow loading screens to be made by Uday and not come from backend
                    {
                        'title': 'Master Reset',
                        'type': 'SETTINGS_LIST_ITEM_NAV',
                        'configuration': [
                            {
                                'title': 'Factory Reset',
                                'data': [
                                    {
                                        'title': None,
                                        'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                                        'data': [
                                            {
                                                'title': 'Resetting WinnConnect',
                                                'subtext': 'Resetting your WinnConnect system clears all locally stored data and restores your system to factory defaults.',
                                                # f'Last Backup {last_config_backup}',
                                                'bottomtext': '',
                                                'data': [
                                                    {
                                                        'title': 'Reset',
                                                        'type': 'BUTTON',
                                                        'data': [
                                                            {
                                                                'title': 'Wipe and Reset WinnConnect?',
                                                                'type': 'Initial Screen',
                                                                'subtext': 'All data will be wiped. Do you want to continue?',
                                                                'data': [
                                                                    {
                                                                        'title': 'Cancel',
                                                                        'type': 'BUTTON',
                                                                        'actions': {
                                                                            'TAP': {
                                                                                'type': 'navigate',
                                                                                'action': {
                                                                                    'href': '/factoryreset',
                                                                                    'type': 'PUT',
                                                                                }
                                                                            }
                                                                        }
                                                                    },
                                                                    {
                                                                        'title': 'Yes, Reset',
                                                                        'type': 'BUTTON',
                                                                        'data': [
                                                                            {
                                                                                'title': None,
                                                                                'type': 'Loading Screen',
                                                                                'subtext': 'Resetting WinnConnect...',
                                                                                'actions': {
                                                                                    'TAP': {
                                                                                        'type': 'api_call',
                                                                                        'action': {
                                                                                            'href': f'{BASE_URL}/api/system/reset/loading',
                                                                                            'type': 'GET',
                                                                                            'params': {
                                                                                                '$onOff': 'int',
                                                                                                'item': 'DataBackupEnabled',
                                                                                            }
                                                                                        },
                                                                                    }
                                                                                }
                                                                            }
                                                                        ],
                                                                        'actions': {
                                                                            'TAP': {
                                                                                'type': 'api_call',
                                                                                'action': {
                                                                                    'href': f'{BASE_URL}/api/system/datareset',
                                                                                    'type': 'PUT',
                                                                                    'params': {
                                                                                        '$onOff': 'int',
                                                                                        'item': 'DataBackupEnabled',
                                                                                    }
                                                                                },
                                                                            }
                                                                        }
                                                                    },
                                                                    {
                                                                        'title': 'Do you want to restart your device now?',
                                                                        'subtext': 'Restarting can be helpful if you are experiencing technical issues. Your display will be off for a few moments, but all systems will continue to run during the restart.',
                                                                        'data': [
                                                                            {
                                                                                'title': 'Cancel',
                                                                                'type': 'BUTTON',
                                                                                'actions': {
                                                                                    'TAP': {
                                                                                        'type': 'navigate',
                                                                                        'action': {
                                                                                            'href': '/home',
                                                                                            'type': 'PUT',
                                                                                        }
                                                                                    }
                                                                                }
                                                                            },
                                                                            {
                                                                                'title': 'Restart',
                                                                                'type': 'BUTTON',
                                                                                'actions': {
                                                                                    'TAP': {
                                                                                        'type': 'api_call',
                                                                                        'actions': {
                                                                                            'href': f'{BASE_URL}/api/system/reboot',
                                                                                            'type': 'PUT',

                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },

                                                        ],
                                                        # 'actions': {
                                                        #     'TAP': {
                                                        #         'type': 'api_call',
                                                        #         'action': {
                                                        #             'href': f'{BASE_URL}/api/settings/databackup/now',
                                                        #             'type': 'PUT',
                                                        #             'params': {
                                                        #                 '$onOff': 'int'
                                                        #             },
                                                        #         },
                                                        #         'action': {
                                                        #             'href': f'{BASE_URL}/api/system/factoryreset',
                                                        #             'type': 'PUT',
                                                        #             'params': {
                                                        #                 '$onOff': 'int'
                                                        #             }
                                                        #         }
                                                        #     }
                                                        # }
                                                    }
                                                ]
                                            },
                                            {
                                                'title': 'Yes, Reset',
                                                'type': 'BUTTON',
                                                'actions': {
                                                    'TAP': {
                                                        'type': 'api_call',
                                                        'action': {
                                                            'href': f'{BASE_URL}/api/system/datareset',
                                                            'type': 'PUT',
                                                            'params': {
                                                                '$onOff': 'int'
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                ]
            },
            # {
            #     'title': None,
            #     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
            #     'data': [
            #         {
            #             'title': 'Component Check',
            #             'type': 'SETTINGS_LIST_ITEM_NAV',
            #             'data': [
            #                 {
            #                     'title': 'Troubleshoot System Connections',
            #                     'type': 'Original Screen',
            #                     'data': [
            #                         {
            #                             'title': None,
            #                             'type': 'SETTINGS_SECTIONS_LIST_ITEM',
            #                             'data': [
            #                                 {
            #                                     'title': 'System Connections Test',
            #                                     'subtext': 'The system connections test checks for a status message from your RV appliances to troubleshoot system issues.',
            #                                     'data': [
            #                                         {
            #                                             'title': 'Run Test',
            #                                             'type': 'BUTTON',
            #                                             'actions': {
            #                                                 'TAP': {
            #                                                     'type': 'api_call',
            #                                                     'action': {
            #                                                         'href': f'{BASE_URL}/api/system/appliancetest',
            #                                                         'type': 'PUT',
            #                                                         'params': {
            #                                                             '$onOff': 'int'
            #                                                         }
            #                                                     }
            #                                                 }
            #                                             }
            #                                         }
            #                                     ]
            #                                 }
            #                             ]
            #                         },
            #                     ]
            #                 },
            #                 {
            #                     'title': 'System Connections Test',
            #                     'type': 'Testing Screen',
            #                     'items': [
            #                         {
            #                             'title': 'Lighting',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Refrigerator Sensors',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Current Sensors',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Air Conditioner',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Furnace',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Solar Controller',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Roof Vent',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Multiplex Device',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Lithium Battery BMS',
            #                             'value': pass_fail_test,
            #                         },
            #                         {
            #                             'title': 'Stop Test',
            #                             'type': 'BUTTON',
            #                             'actions': {
            #                                 'TAP': {
            #                                     'type': 'api_call',
            #                                             'action': {
            #                                                 'href': f'{BASE_URL}/api/system/appliancetest',
            #                                                 'type': 'PUT',
            #                                                 'params': {
            #                                                     '$onOff': 'int'
            #                                                 }
            #                                             }
            #                                 }
            #                             }
            #                         }

            #                     ]

            #                 }
            #             ]
            #         }
            #     ]
            # },
            # {
            #     'title': 'Restart',
            #     'type': 'BUTTON',
            #     'actions': {
            #         'TAP': {
            #             'type': 'api_call',
            #                     'action': {
            #                         'href': f'{BASE_URL}/api/system/reboot',
            #                         'type': 'PUT',
            #                         'params': {
            #                             '$onOff': 'int'
            #                         }
            #                     }
            #         }
            #     }
            # }
            {
                'title': None,
                'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                'configuration': [
                    {
                        'title': 'System Diagnostics',
                        'name': 'SettingsSystemDiagnostics',
                        'type': 'SETTINGS_LIST_ITEM_NAV',
                        'data': [
                            {
                                'title': 'System Diagnostics',
                                'data': gui_settings_diagnostics(request),
                            },
                        ]
                    },
                ]
            },
            # {
            #     'title': None,
            #     'type': 'SETTINGS_SECTIONS_LIST_ITEM',
            #     'configuration': [
            #         {
            #             'title': 'Functional Control Panel',
            #             'name': 'SettingsFCP',
            #             'type': 'SETTINGS_LIST_ITEM_NAV_REDIRECT',
            #             'actions': {
            #                 'TAP': {
            #                     'type': 'navigate',
            #                     'action': {
            #                         'href': '/home/functionaltests'
            #                     }
            #                 }
            #             }
            #         }
            #     ]
            # },
        ]
    }
    SYSTEM_SETTING_INSTANCE = 1
    service_settings = request.app.hal.system.handler.setting.get(SYSTEM_SETTING_INSTANCE)

    if service_settings is not None:
        if service_settings.state.fcpEnabled == EventValues.ON:
            settings_system['data'].append(
                {
                    'title': None,
                    'type': 'SETTINGS_SECTIONS_LIST_ITEM',
                    'configuration': [
                        {
                            'title': 'Functional Control Panel',
                            'name': 'SettingsFCP',
                            'type': 'SETTINGS_LIST_ITEM_NAV_REDIRECT',
                            'actions': {
                                'TAP': {
                                    'type': 'navigate',
                                    'action': {
                                        'href': '/home/functionaltests'
                                    }
                                }
                            }
                        }
                    ]
                }
            )
    running_version = request.app.__version__.get('version', 'NA')
    # running_date = request.app.__version__.get("date", "NA")
    running_update = request.app.__version__.get('date', 'NA.123456')[:-7]
    waiting_user_approval = bool(request.app.ota_state.get('waiting', "False") == "True")
    waiting_user_version = request.app.ota_state.get('version', "NA")
    last_checked = request.app.ota_state.get('checked', "--")
    request.app.update_notes = read_about_from_bld_directory()

    version_waiting = "Next Version"
    multi_plus_title = "Your RV is Up to Date"
    multi_plus_subtitle = f'Last Checked {last_checked}'
    no_update_avaliable = True
    can_update = False
    update_blocked = False

    if waiting_user_approval is True:
        multi_plus_title = "Your RV has an Update Available"
        multi_plus_subtitle = f'Software Version {waiting_user_version}'
        no_update_avaliable = False
        can_update = True
        update_blocked = request.app.check_ota_lockout()
        if update_blocked is True:
            can_update = False

    print(f'no_update_avaliable {no_update_avaliable} \n waiting_user_approval {waiting_user_approval} \n update_blocked {update_blocked}  ')

    # TODO: Figure out if an up
    # date is available, what version it is etc.
    settings_software_update = {'data': [
            {
                'type': 'MULTI_NAVIGATION_BUTTON',
                'title': f'Software Version {running_version}',
                'subtitle': f'Last Updated {running_update}',
                'button':  {
                    'title': "Check for Updates",
                    'enable': no_update_avaliable,
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/system/otacheck',
                        'type': 'GET'
                    }
                }
            },
            {
                'type': 'MULTI_NAVIGATION_BUTTON_PLUS',
                'data': [
                    {
                        'type': 'MULTI_NAVIGATION_BUTTON',
                        'title': multi_plus_title,
                        'subtitle': multi_plus_subtitle,
                        # 'button':  {
                        #     'title': "About this Update",
                        #     'enable': waiting_user_approval,
                        #     # Hidden until About this Update is pressed
                        #     'type': 'notes_page',
                        #     'notes':
                        #         {
                        #             'title':  multi_plus_subtitle,
                        #             'text_page': request.app.update_notes
                        #         }
                        #     }
                    },
                    {
                        'type': 'PURE_INFO',
                        'title': 'To update your software your battery must be charged to at least 50%.',  # Till we see shore power , or 25% if plugged into shore power.',
                        'enable': update_blocked,
                    },
                    {
                        'type': 'BUTTON',
                        'title': 'UPDATE NOW',
                        'enable': can_update,
                        # Travel to a new page after call results
                        'api_call': {
                            'href': f'{BASE_URL}/api/system/otastart',
                            'type': 'PUT',
                            'params': {
                                '$onOff': 'int'
                            }
                        }
                    }
                ]
            },
        ]
    }


    # Menu on the left
    response = {
        'title': 'Close',
        "type": "SETTINGS_MAIN",
        'actions': {
            'TAP': {
                'type': 'navigate',
                'action': {
                    'href': '/home'
                }
            }
        },
        'tabs': [
            {
                'title': model,
                'type': 'SETTINGS_ABOUT_TAB',
                'name': 'UiSettingAboutTab',
                'details': settings_model,
                'EOS': True,
            },
            {
                'title': 'Connectivity',
                'type': 'SETTINGS_CONNECTIVITY_TAB',
                'name': 'UiSettingsConnectivity',
                'details': settings_connectivity,
                'EOS': True,
            },
            {
                'title': 'Features',
                'type': 'SETTINGS_FEATURES_TAB',
                'name': 'UiSettingsFeatures',
                'details': settings_features,
                'EOS': False,
            },
            # {
            #     'title': 'Notifications',
            #     'type': 'SETTINGS_NOTIFICATIONS_TAB',
            #     'name': 'UiSettingsNotifications',
            #     'details': settings_notifications,
            #     'EOS': False,
            # },
            {
                'title': 'Unit Preferences',
                'type': 'SETTINGS_UNITPREFERENCES_TAB',
                'name': 'UiSettingsUnitPreferences',
                'details': settings_unit_preferences,
                'EOS': True,
            },
            {
                'title': 'System',
                'type': 'SETTINGS_SYSTEM_TAB',
                'name': 'UiSettingsSystem',
                'details': settings_system,
                'EOS': False,
            },
            {
                'title': 'Software Update',
                'type':'SETTINGS_SOFTWAREUPDATE_TAB',
                'name': 'UiSettingsSoftwareUpdate',
                'details': settings_software_update,
                'EOS': False,
            },
            {
                'title': 'Display',
                'type': 'SETTINGS_DISPLAY_TAB',
                'name': 'UiSettingsDisplay',
                'details': settings_display,
                'EOS': True,
            },
        ],
    },
    return response


def gui_settings_diagnostics(request):
    '''Provides list of diagnostics output per device.'''
    CATEGORY_TO_FEATURES = {
        'energy': 'Energy Management',
        'climate': 'Climate Control',
        'watersystems': 'Water Systems',
        'lighting': 'Lighting',
        'electrical': 'Electrical',
        'awning': 'Awning',
        'petminder': 'Pet Minder',
        'awning': 'Awning',
        'movables': 'Slideout/Awning',
        'slideout': 'Slide-Out',
        'connectivity': 'Connectivity',
        # 'UNHANDLED': 'UNHANDLED'
    }
    diagnostics = request.app.can_diagnostics
    system_diagnostics = request.app.system_diagnostics

    # Inject some things when called
    iot_status = get_iot_status(request.app)
    print('IoT status', iot_status)

    if iot_status == {}:
        stale = True
        last_seen = time.time()
    else:
        stale = False
        last_seen = None

    system_diagnostics['devices']['WinnConnect IoT'] = {
        'stale': stale,
        'category': 'connectivity',
        'last_seen': last_seen
    }

    combo_diagnostics = {k: v for k, v in diagnostics.items()}
    for k, v in system_diagnostics.get('devices', {}).items():
        combo_diagnostics['devices'][k] = v

    last_ran = combo_diagnostics.get('last_ran')
    stale_count = combo_diagnostics.get('stale_count')
    if last_ran is None:
        last_ran = 'Last Ran: Never'
        run_text = 'Not Run'
    else:
        last_ran = f'Last Ran: {time.time() - last_ran:.2f} seconds ago'
        if stale_count > 0:
            run_text = f'{stale_count} FAIL'
        else:
            run_text = 'All Passed'

        # NOTE: We temporarily remove the text to avoid confusion
        # TODO: Get the count right, only on the things that are visible
        run_text = ''

    top = {
        'text': 'Check for system issues by verifying communication with feature components.',
        'subtext': last_ran,
        'actions': {
            'TAP': {
                'type': 'BUTTON',
                'title': 'Run System Diagnostics',
                'enable': True,
                # Travel to a new page after call results
                'api_call': {
                    'href': f'{BASE_URL}/api/system/rundiagnostics',
                    'type': 'PUT',
                    'params': {}
                }
            },
        }
    }

    # TODO: Iterate over inventory received from can service
    categories = {}
    for dev_name, device in combo_diagnostics.get('devices', {}).items():
        raw_category = device.get('category', 'NA')

        category = CATEGORY_TO_FEATURES.get(
            raw_category,
        )

        if raw_category not in CATEGORY_TO_FEATURES:
            appfeatures_name = 'Generic'
        else:
            appfeatures_name = raw_category.capitalize()

        if raw_category == 'NA':
            continue
            category_name = 'UNSORTED'
        else:
            category_name = category

        if category not in categories:
            categories[category] = {
                'name': f'AppFeature{appfeatures_name}',
                'title': category_name,
                'status': None,
                'devices': []
            }

        status = 'FAIL'
        result = 'Result: Lost communication with this component.'

        if dev_name == 'Wakespeed WS500':
            # Special case, the wakespeed only shows when engine is running
            # Get Engine running lockout
            vehicle = request.app.hal.vehicle.handler.vehicle.get(1)
            if vehicle is None:
                status = 'FAIL'
                result = 'Result: No updates to vehicle data available.'
            else:
                if vehicle.state.engRun == EventValues.TRUE:
                    stale = device.get('stale')
                    if stale is False:
                        status = 'PASS'
                        result = 'Result: Maintained communication with component.'
                else:
                    status = 'PENDING'
                    result = 'Result: Component only communicates when engine is running.'

        else:
            stale = device.get('stale')
            if stale is False:
                status = 'PASS'
                result = 'Result: Maintained communication with component.'
            else:
                # This is only stale or None
                categories[category]['status'] = status

        categories[category]['devices'].append(
            {
                'title': dev_name,
                # Use same naming convention for AppView / Features
                # Add a single generic icon for things that do not apply to features
                # 'name': f'AppFeature{appfeatures_name}',
                'text': result,
                'status': status,
                'details': [
                    {
                        'title': dev_name,    # ITC Controller, TM-1010 etc.
                        'status': status,               # PASS / FAIL
                        'status_text': status,          # PASS/FAIL as a string
                        'collapsed_caption': None,      # Shown even when collapsed
                        'expanded_text': result,
                    }
                ]
            }
        )

    categories = [v for k, v in categories.items()]

    middle = {
        'left': f'Results: {run_text}',
        'right': {
            # TODO: Figure out how to own this a data driven way, for now
            # UI hard codes what each means
            'options': [
                'Expand All Features',
                'Collapse All Features'
            ]
        }
    }

    return {
        'top': top,
        'middle': middle,
        'categories': categories
    }
