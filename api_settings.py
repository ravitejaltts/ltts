import asyncio
import base64
import datetime
import os
import pyqrcode
import pytz

import httpx

from typing import List
from enum import Enum

import requests

from common_libs import environment
from common_libs.models.common import EventValues
from common_libs.clients import MAIN_CLIENT

# from logging import Logger

from fastapi import APIRouter, HTTPException, Request

from pydantic import BaseModel, Field

from .common import (
    BaseAPIModel,
    BaseAPIResponse
)

from main_service.modules.system_helper import (
    get_display_brightness,
    set_display_brightness,
    set_display_on,
    set_display_off,
    get_system_processes,
    restart_service,
    shutdown_system,
    reboot_system,
    ok_ota_system,
    ifconfig,
    get_iot_status,
)

from main_service.modules.sw_features import Features

_env = environment()

BT_SERVICE_PORT = _env.bluetooth_service_port

# Get env URL from IoT
# Prod: https://apim.ownersapp.winnebago.com/API/vehicle/ownersAppRedirect?vin={vin}
# Tst: https://tst-apim.ownersapp.winnebago.com/API/vehicle/ownersAppRedirect?vin={vin}
# Dev: https://dev-apim.ownersapp.winnebago.com/API/vehicle/ownersAppRedirect?vin={vin}
# https://apim.ownersapp.winnebago.com/

ENV = 'https://apim.ownersapp.winnebago.com/'
PAIRING_BASE_URL = '{env}/API/vehicle/ownersAppRedirect?vin={vin}'


class SimpleSwitch(BaseModel):
    onOff: int


class Setting(BaseAPIModel):
    type: str = Field(
        'SYSTEM_BRIGHTNESS|VOLUME_UNIT|TEMPERATURE_UNIT|???',
        description='Type of setting to apply to the overall system.'
    )


class SettingsResponse(BaseAPIResponse):
    systemSettings: List[Setting] = Field(
        description='List of system wide settings, like volume units, temp unit, display brightness etc.'
    )
    # schemas: dict


class ScreenModeEnum(str, Enum):
    light = 'LIGHT'
    dark = 'DARK'


class ScreenMode(BaseModel):
    screenMode: ScreenModeEnum


router = APIRouter(
    prefix='/settings',
    tags=['SETTINGS', ]
)


@router.get('', response_model=SettingsResponse, tags=['ROOT_API',])
async def get_settings_main(request: Request):
    '''Get list of available settings and their current state.'''
    settings = []
    return {
        'count': len(settings),
        'key': 'systemSettings',
        'hwSystemSettings': None,
        'systemSettings': settings,
        'schemas': {}
    }


@router.put('/bluetooth/reset')
async def set_bluetooth_reset(request: Request, ) -> dict:
    '''Accept call to reset Bluetooth.

    Mainly used to re-advertise.'''
    url = f'http://localhost:{BT_SERVICE_PORT}/reset'
    try:
        result = await MAIN_CLIENT.put(
            url,
            timeout=5
        )
    except httpx.ConnectError as err:
        print('Error connecting to BT', err)
        result = {'msg': str(err)}
    except httpx.Timeout as err:
        print('Timeout connecting to BT', err)
        result = {'msg': str(err)}

    print('BT Reset Result:', result)

    return result


@router.get('/bluetooth/pairing')
async def get_bluetooth_onoff(request: Request) -> dict:
    '''Respond with full details of the bluetooth.

    Includes onOff, current paired used etc.'''

    bluetooth_settings = request.app.config.get('settings', {}).get('BluetoothControlEnabled')
    return {
        'BluetoothControlEnabled': bluetooth_settings
    }


def generate_qr_code(vin, app, recreate=False):
    '''Generate QR code required to link into the app.'''
    filepath = _env.storage_file_path(f'{vin}_pairing_qr_code.png')
    env = app.config.get('environment')
    if env is None:
        # Get the environment from iot service
        get_iot_status(app)  # check if new
        env_url = app.iot_status.get('env_url')
        print('ENV URL', env_url)
        if env_url:
            env = env_url.lower().split('/api/')[0]
            app.config['environment'] = env
            print('Updated environment')
            # Must recreate
            recreate = True
        else:
            env = ''

    if os.path.exists(filepath) and recreate is False:
        url = PAIRING_BASE_URL.format(
            env=env, vin=vin
        )
    else:
        url = pyqrcode.create(PAIRING_BASE_URL.format(
            env=env, vin=vin)
        )
        # TODO: Test error scenarios like storage folder not writable
        url.png(filepath, scale=6)

    return filepath, url


def encode_image_to_base64(filepath):
    # Read the PNG image from the file and encode it to Base64
    with open(filepath, "rb") as file:
        qr_bytes = file.read()
        qr_base64 = base64.b64encode(qr_bytes).decode('utf-8')

    return qr_base64


@router.get('/qr_code_blur')
async def blurred_qr_code(request: Request) -> dict:
    '''Respond with a static blurred QR code to indicate missing precondition.'''
    filepath = '../data/blur.png'
    # Encode the QR code image to Base64
    qr_code_base64 = encode_image_to_base64(filepath)

    response = {
        'qr_value': qr_code_base64,
        'title': 'Device status',
        'status': 0,
        'timestamp': 0
    }

    return response


@router.get('/qr_code')
async def qr_code(request: Request) -> dict:
    vin = request.app.config.get('VIN', 'VINNOTFOUND')

    # TODO: Fix UI to use the url given in action and not hard code it to this endpoint
    # Check lockouts
    if request.app.hal.system.handler.lockouts[EventValues.IGNITION_ON].state.active is False:
        # Return a blurred QR code
        filepath, url = '../data/blur.png', ''
    else:
        # Generate the QR code and get the file path
        filepath, url = generate_qr_code(vin, request.app)

    # Encode the QR code image to Base64
    qr_code_base64 = encode_image_to_base64(filepath)

    response = {
        'qr_value': qr_code_base64,
        'title': 'Device status',
        'status': request.app.config['BluetoothSettings']['PairingStatus']['state'],
        'timestamp': request.app.config['BluetoothSettings']['PairingStatus']['timeStamp'],
        'url': url
    }

    return response


@router.put('/bluetooth/state')
async def update_bt_setting_state(request: Request, state: dict) -> dict:
    '''Update the state of bluetooth settings.'''
    onOff = state.get('onOff')
    if onOff is None:
        raise ValueError('onOff is the only setting supported')

    url = f'http://localhost:{BT_SERVICE_PORT}/onoff'

    try:
        result = await MAIN_CLIENT.put(
            url,
            json={
                'onOff': onOff
            },
            timeout=5
        )
    except httpx.ConnectError as err:
        result = {'msg': str(err)}
        raise HTTPException(503, result)

    except httpx.Timeout as err:
        result = {'msg': str(err)}
        raise HTTPException(408, result)

    print('BT OnOff Result:', result)
    request.app.config['BluetoothSettings']['BluetoothControlEnabled'] = state['onOff']

    return state



@router.put('/bluetooth/onoff')
async def update_bt_enabled(request: Request, data: SimpleSwitch) -> dict:
    '''Update BT enabled settings.'''
    print('BT ONOFF', data)

    try:
        request.app.config['BluetoothSettings']['BluetoothControlEnabled'] = data.onOff
    except KeyError:
        raise KeyError('settings key missing in app config')

    # Set advertising to off in BT service
    url = f'http://localhost:{BT_SERVICE_PORT}/onoff'
    # try:
    #     result = requests.put(
    #         url,
    #         json={
    #             'onOff': data.onOff
    #         },
    #         timeout=5
    #     )
    # except requests.exceptions.ConnectionError as err:
    #     print('Error connecting to BT', err)
    #     result = {'msg': str(err)}
    #     raise HTTPException(503, result)
    # except requests.exceptions.Timeout as err:
    #     print('Timeout connecting to BT', err)
    #     result = {'msg': str(err)}
    #     raise HTTPException(408, result)

    try:
        result = await MAIN_CLIENT.put(
            url,
            json={
                'onOff': data.onOff
            },
            timeout=5
        )
    except httpx.ConnectError as err:
        result = {'msg': str(err)}
        raise HTTPException(503, result)

    except httpx.Timeout as err:
        result = {'msg': str(err)}
        raise HTTPException(408, result)

    print('BT OnOff Result:', result)
    bluetooth_enabled = request.app.config.get('BluetoothSettings', {}).get(
        'BluetoothControlEnabled'
    )

    return {
        'item': 'BluetoothControlEnabled',
        'onOff': bluetooth_enabled
    }


@router.put('/bluetooth/pairdevice')
async def pair_device(request: Request, body: dict) -> list:
    '''pair bluetooth device'''

    name = body.get('name')
    connected = body.get('connected')
    mac_address = body.get('macAddress')

    device = {
        'name': name,
        'connected': connected,
        'macAddress': mac_address,
    }
    request.app.config['BluetoothSettings']['ConnectedDevices'].append(device)
    connected_devices_list = request.app.config['BluetoothSettings']['ConnectedDevices']

    return connected_devices_list


@router.put('/bluetooth/disconnect')
async def disconnect_paired_devices(request: Request, body: dict) -> list:
    '''disconnect bluetooth device'''

    name = body.get('name').lower()
    connected = body.get('connected')
    mac_address = body.get('macAddress')

    connected_devices_list = request.app.config.get('BluetoothSettings', {}).get('ConnectedDevices')
    if connected_devices_list is None:
        raise ValueError('There are no devices connected')

    device = {
        'name': name,
        'connected': connected,
        'macAddress': mac_address,
    }
    for index, device in enumerate(connected_devices_list):
        if device['name'].lower() == name and device['macAddress'] == mac_address:
            request.app.config['BluetoothSettings']['ConnectedDevices'][index]['connected'] = False
            break
    connected_devices_list = request.app.config.get('BluetoothSettings', {}).get('ConnectedDevices')
    return connected_devices_list


@router.put('/bluetooth/forgetdevice')
async def forget_bt_device(request: Request, body: dict) -> list:
    '''forget bluetooth device'''
    name = body.get('name').lower()
    mac_address = body.get('macAddress')
    connected_devices_list = request.app.config.get('BluetoothSettings', {}).get('ConnectedDevices')
    if connected_devices_list is None:
        raise ValueError('There are no devices connected')
    for index, device in enumerate(connected_devices_list):
        if device['name'].lower() == name or device['macAddress'] == mac_address:
            request.app.config.get('BluetoothSettings', {}).get('ConnectedDevices').pop(index)
            break
    connected_devices_list = request.app.config.get('BluetoothSettings', {}).get('ConnectedDevices')

    return connected_devices_list


@router.put('/databackup')
async def update_databackup(request: Request, data: dict) -> dict:
    '''Update data backup settings.'''

    item = data.get('item')

    try:
        request.app.config['settings'][item] = data.onOff
    except KeyError:
        raise KeyError('settings key missing in app config')

    databackup_settings = request.app.config.get('settings', {}).get(item)

    return {
        'item': item,
        'onOff': databackup_settings
    }


@router.put('/browser/screenmode')
async def update_browser_mode(request: Request, body: dict = {'value': 'LIGHT'}):
    mode = body['value']
    current_mode = request.app.config.get('settings', {}).get('UIScreenMode')
    if current_mode is None:
        raise ValueError('Mode not part of the config')

    request.app.config['settings']['UIScreenMode'] = mode


@router.put('/browser/screenmode/autosunset')
async def auto_adjust_sunset(request: Request, body: dict):
    onOff = body['onOff']
    auto_sunset = request.app.config.get('settings', {}).get('AutoScreenModeSunset')

    if auto_sunset is None:
        raise ValueError('Auto Adjust Sunset not part of the config')

    request.app.config['settings']['AutoScreenModeSunset'] = onOff
    request.app.save_config('settings.AutoScreenModeSunset', onOff)

    print(Features.check_sunset(request.app))

    return {
        'AutoScreenModeSunset': request.app.config['settings']['AutoScreenModeSunset']
    }
    # WTF ?
    # if onOff == 1:
    #     while True:
    #         tz = pytz.timezone(preferred_timezone)
    #         current_time_preferred_timezone = datetime.datetime.now(tz).strftime('%I:%M %p')
    #         # Check if the current time matches the sunrise time (e.g. 6:30 AM)
    #         if datetime.datetime.strptime(current_time_preferred_timezone, '%I:%M %p').time() >= datetime.time(6, 30):
    #             # Change the appearance mode to light
    #             request.app.config['settings']['UIScreenMode'] = 'LIGHT'
    #             print(request.app.config['settings']['UIScreenMode'])
    #             break
    #         # Check if the current time matches the sunset time (e.g. 6:30 PM)
    #         elif datetime.datetime.strptime(current_time_preferred_timezone, '%I:%M %p').time() >= datetime.time(18, 30):
    #             # Change the appearance mode to dark
    #             request.app.config['settings']['UIScreenMode'] = 'DARK'
    #             break

    #         # Wait 1 minute before checking the time again
    #         await asyncio.sleep(60)
