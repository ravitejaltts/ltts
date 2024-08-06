import subprocess
import datetime
import pytz
import asyncio
import os
import signal
import time
import random
from typing import Optional, List
# from astral.sun import sun
# from astral import LocationInfo
from logging import Logger
# from main_service.modules.hardware.hal import hw_layer
from hashlib import sha256

import json

import requests

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel, Field, ValidationError

from .common import ResultLevel, not_implemented, BaseResponse
from  common_libs.models.common import RVEvents, EventValues, convert_utc_to_local
from main_service.modules.storage_helper import get_floorplans_available, set_floorplan
from main_service.modules.system_helper import (
    get_display_brightness,
    set_display_brightness,
    save_display_config,
    set_display_on,
    set_display_off,
    get_system_processes,
    restart_service,
    shutdown_system,
    reboot_system,
    ok_ota_system,
    ifconfig,
    get_ip,
    shutdown_main_system,
    get_iot_status
)

from common_libs.models.notifications import (
    request_to_iot)

from main_service.modules.api_helper import validate_wc_api_call


CHASSIS_ID = 1


# from main_service.modules.hardware.hal import hw_layer as hal
# from main_service.modules.hardware.hal import hw_layer
BRIGHTNESS_MIN = 10
BRIGHTNESS_MAX = 100
BRIGHTNESS_IDLE = 30
OFFTIME_OFFSET = 0  # TEMP set to 0

current_time = datetime.datetime.now()

from main_service.modules.constants import (
    WATER_UNIT_GALLONS,
    TEMP_UNIT_FAHRENHEIT,
)
tests = {}

def hash_passcode(passcode):
    p_hash = sha256()
    p_code = bytes(passcode)
    p_hash.update(p_code)
    return p_hash.hexdigest()


class SystemResponse(BaseResponse):
    '''Response model for all System calls'''
    system_key: str
    system_value: str


class Brightness(BaseModel):
    '''Request Model for display brightness'''
    value: int = Field(
        ...,
        ge=BRIGHTNESS_MIN,
        le=BRIGHTNESS_MAX,
        description=f'The value for brightness must be => {BRIGHTNESS_MIN} and <= {BRIGHTNESS_MAX}, where 0 is off and 100 is 100% brightness'
    )

class PasscodeBody(BaseModel):
    '''Model for passcode checking.'''
    passcode: int


class PasscodeResponse(BaseModel):
    '''Model for the response to the pass code check.'''
    passcodeTriesRemaining: int
    passcodeLockoutTimer: int


class PasscodeSetting(PasscodeBody):
    '''Model to configure passcode.'''
    # Inherited
    # passcode: int

    # If true passcode is enabled
    isProtected: bool


class FloorPlan(BaseModel):
    floorPlan: str = Field(
        'VANILLA',
        description='Floorplan name that correlates to an existing config file.'
    )
    telemetryFile: Optional[str] = Field(
        None,
        description='The telemetry file to use as received by IoT, defaults to VANILLA in the main code'
    )
    optionCodes: Optional[str] = Field(
        '',
        description='String of , separated option codes'
    )


PREFIX = 'system'

router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['SYSTEM', ]
)


@router.get('/status')
async def status() -> dict:
    '''Respond with full details of the HMI system.

    Includes CPU, Memory, Processes, etc.'''
    return not_implemented()


@router.get('/cpu')
async def get_cpu_details() -> dict:
    '''Get overview of CPU details.'''
    # Get CPU details
    # Get Current CPU Load
    return not_implemented()


@router.get('/memory')
async def get_memory_details() -> dict:
    '''Get overview of memory details.'''
    # Get Memory consumption
    return not_implemented()


@router.get('/processes')
async def get_process_details() -> dict:
    '''Get overview of running processes.'''
    # Get Processes running details
    processes = get_system_processes()
    return BaseResponse(
        result_code=0,
        result_level='OK',
        result_message=processes.stdout
    )


@router.get('/process/{proc_id}')
async def get_process_id_details() -> dict:
    '''Get specific process detail.'''
    # Get Process info for proc_id
    return not_implemented()


@router.put('/doorLock', response_model=BaseResponse)
async def door_lock(request: Request, body:dict) -> dict:
    '''Set door lock open or locked'''
    # TODO: Move to vehicle and hw_vehicle ?
    print(f'doorLock called with: {body}')

    if body['onOff'] == 'ON' or body['onOff'] == 1:
        cmd = '2799070084FF7C0F'
        msg = 'Locked'
    else:
        cmd = '2799070074FF7C0F'
        msg = 'Unlocked'

    request.app.can_sender.can_send_raw(
        '1CFF0044',
        cmd
    )

    if body['onOff'] == 'ON' or body['onOff'] == 1:
        request.app.hal.electrical.handler.set_state(
            system='chassis',
            system_id='doorLock',
            new_state={
                'onOff': 1
            }
        )
    else:
        request.app.hal.electrical.handler.set_state(
            system='chassis',
            system_id='doorLock',
            new_state={
                'onOff': 0
            }
        )

    return BaseResponse(
        result_code=0,
        result_level='OK',
        result_message=msg
    )


@router.put('/display/on', response_model=BaseResponse)
async def display_on(request: Request) -> dict:
    '''Set display on'''
    set_display_on()

    return BaseResponse(
        result_code=0,
        result_level='OK',
        result_message='Turned display ON'
    )


@router.put('/display/off')
async def display_off() -> dict:
    '''Set display off'''
    set_display_off()

    return BaseResponse(
        result_code=0,
        result_level='OK',
        result_message='Turned display OFF'
    )


@router.get('/display/brightness')
async def get_screen_brightness(request: Request) -> dict:
    return {
        'brightness': request.app.config['settings']['DisplayBrightness']
    }


@router.put('/display/brightness')
async def set_brightness(request: Request, brightness: Brightness) -> dict:
    '''Set brightness of display'''
    # Constraints in Brightness definition
    brightness_result = set_display_brightness(
        brightness.value
    )
    request.app.config['settings']['DisplayBrightness'] = brightness_result
    request.app.save_config('settings.DisplayBrightness', brightness_result)

    settings = request.app.config['activity_settings']
    settings['brightness'] = request.app.config['settings']['DisplayBrightness']

    save_display_config(settings)

    # Write to new file
    return {
        'brightness': brightness_result
    }


@router.put('/display/autodimming')
async def display_dimming(request: Request, body: dict) -> dict:
    '''Set display timeout'''
    value = body.get('value')
    # TODO: the value shoul dbe enforced by the same source of truth as providing the options in the UI
    # might need a constant somewhere SCREEN_TIMEOUT_OPTIONS
    if value in [0, 1, 2, 5]:
        if value == 0:
            inactive_timeout = 0
        else:
            inactive_timeout = (value * 60) - OFFTIME_OFFSET

        request.app.config['activity_settings']['inactiveTimeout'] = inactive_timeout
        request.app.config['activity_settings']['lockTimeMinutes'] = value
    else:
        raise HTTPException(400, f'Value error: {value}')

    settings = request.app.config['activity_settings']
    settings['brightness'] = request.app.config.get('settings', {}).get('DisplayBrightness')

    save_display_config(settings)

    return request.app.config['activity_settings']



@router.put('/service/{service}/restart')
async def service_restart(request: Request, service: str) -> dict:
    '''Restart given service'''
    service = service.lower()
    try:
        result = restart_service(service)
        # TODO: Add event
    except ValueError as err:
        raise HTTPException(404, f'Service not available/controllable: "{service}"')

    return result


# Activity
@router.put('/activity/idle', response_model=BaseResponse)
async def set_screen_inactive(request: Request):
    # Get configured brightness setting for inactivity
    # Set brightness to inactivity brightness
    # TODO: Make this an offset from the user preference unless user preference is < X (TBD)
    user_brightness = request.app.config.get('settings', {}).get('DisplayBrightness')
    if user_brightness > BRIGHTNESS_IDLE:
        brightness_result = set_display_brightness(BRIGHTNESS_IDLE)
    else:
        brightness_result = 'NA'

    request.app.hal.lighting.handler.event_logger.add_event(
        RVEvents.SYSTEM_ACTIVITY_STATE_CHANGE,
        0,
        EventValues.ACTIVITY_IDLE
    )

    return BaseResponse(
        result_code=0,
        result_level='OK',
        result_message='Set brightness to {}'.format(brightness_result)
    )


@router.put('/activity/on', response_model=BaseResponse)
async def set_screen_active(request: Request):
    # Get configured user brightness
    # Set brightness to user set level

    # TODO: Get from user preference
    user_brightness = request.app.config.get('settings', {}).get('DisplayBrightness')
    if user_brightness is None:
        print('User brightness KeyError')
        user_brightness = 75

    brightness_result = set_display_brightness(user_brightness)

    request.app.hal.lighting.handler.event_logger.add_event(
        RVEvents.SYSTEM_ACTIVITY_STATE_CHANGE,
        0,
        EventValues.ACTIVITY_WAKE
    )

    return BaseResponse(
        result_code=0,
        result_level='OK',
        result_message='Set brightness to {}'.format(brightness_result)
    )


@router.put('/activity/off', response_model=BaseResponse)
async def set_screen_off(request: Request):
    # Set brightness to 0 for now
    brightness_result = set_display_brightness(0)

    request.app.hal.lighting.handler.event_logger.add_event(
        RVEvents.SYSTEM_ACTIVITY_STATE_CHANGE,
        0,
        EventValues.ACTIVITY_SLEEP
    )

    return BaseResponse(
        result_code=0,
        result_level='OK',
        result_message='Set brightness to {}'.format(brightness_result)
    )


@router.put('/shutdown')
async def system_shutdown():
    return {
        'status': 'OK',
        'msg': str(shutdown_system())
    }


@router.put('/reboot')
async def system_reboot():
    return {
        'status': 'OK',
        'msg': str(reboot_system())
    }


@router.put('/otastart')
async def system_start_ota(request: Request):
    result = await ok_ota_system(request.app)
    if result == {}:
        response = {
            'status': 'FAIL',
            'msg': 'Unable to start Update.'
        }
    else:
        response = {
            'status': 'OK',
            'msg': 'Update processing.'
        }
    print(f'//otastart {response}')
    return response


@router.get('/otacheck')
async def check_ota(request: Request):
    '''Check is anything new?'''
    get_iot_status(request.app)
    request.app.ota_state['waiting'] = 'False'
    if request.app.iot_status.get('ota_status') == 'USER_APPROVAL':
        request.app.ota_state['waiting'] = 'True'
    request.app.ota_state['version'] = request.app.iot_status.get('releaseVersionWaiting')
    request.app.ota_state['checked'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = {
        'Status': 'OK'
        }
    return response


@router.get('/otaabout')
async def about_ota():
    '''Fetch and return the update information'''
    response = {
        'page': 'Determine the format for this about information.'
        }
    return response


@router.get('/floorplan')
async def get_floorplan_string(request: Request) -> str:
    '''Get the loaded floorplan string.'''
    return request.app.hal.floorPlan


@router.get('/optioncodes')
async def get_optioncodes_string(request: Request) -> str:
    '''Get the loaded option codes string.'''
    return request.app.hal.optionCodes


@router.get('/floorplans_available')
async def get_floorplans_supported() -> list:
    '''Get the floorplan supported list.'''
    return get_floorplans_available()


@router.put('/floorplan')
async def assign_floorplan(request: Request, data: FloorPlan):
    '''IoT informs main service of a change or initial setting of
    a floorplan and option codes.'''

    request.app.wgo_logger.info(f"[SYSTEM] Current Floorplan and options: {request.app.hal.optionCodes} / {request.app.hal.floorPlan}")
    # TODO: work these into the componect loading below
    optioncodes_updated = False
    compare_codes = data.optionCodes.split(',')
    if compare_codes != request.app.hal.optionCodes:
        request.app.hal.optionCodes = data.optionCodes
        optioncodes_updated = True
        request.app.wgo_logger.info(f"[SYSTEM] Floorplan options updated: {data.optionCodes}")

    # Get the current floorplan
    floorplan_updated = False
    if data.floorPlan != request.app.hal.floorPlan or optioncodes_updated is True:
        try:
            request.app.hal.floorPlan = data.floorPlan
            result = set_floorplan(data.floorPlan, data.optionCodes)
            floorplan_updated = True
        except ValueError as err:
            print(err)
            msg = f'[SYSTEM] Floorplan: {data.floorPlan} not found, check configs.'
            request.app.wgo_logger.error(msg)
            raise HTTPException(404, msg)
    else:
        request.app.wgo_logger.info(f"[SYSTEM]Floorplan and options unchanged")
        result = {
            'status': 'UNCHANGED',
            'msg': 'Floorplan same as before'
        }

        request.app.wgo_logger.info(result)

    # NOTE: PIN IN HERE
    # if data.telemetryFile is not None:
    #     # Check if we need to reload OTA template, do it during runtime
    #     request.app.init_telemetry(request.app, data.telemetryFile)
    #     result['msg'] += f', telemetry template applied {data.telemetryFile}'

    if floorplan_updated is True or optioncodes_updated is True:
        # TODO: Send the trigger to the app
        request.app.wgo_logger.info(f'[SYSTEM] Updating FloorPlan: {data.floorPlan}')
        if data.optionCodes is None:
            request.app.init_floorplan(
                request.app,
                data.floorPlan
            )
        else:
            request.app.init_floorplan(
                request.app,
                data.floorPlan,
                data.optionCodes.split(',')
            )

        await reconfig_iot(request)  # call the following function

    return result


@router.put('/reconfigure')
async def reconfig_iot(request: Request):
    '''Send VIN to IoT service to kick off personalization.'''
    # Check if VIN is not None and adheres to the rules
    # 17 chars etc.
    # TODO: Put in _env variables
    IOT_URL = 'http://localhost:8002/vin'
    # Get VIN
    request.app.hal.vehicle.handler.get_vin()
    vin = request.app.hal.vehicle.handler.state.get('vin')
    if vin is None:
        vin = request.app.config.get('VIN')

    print('Current App VIN:', vin)
    try:
        result = requests.put(
            IOT_URL,
            json={
                'vin': vin
            },
            timeout=5
        )
        print(result)
    except requests.exceptions.ConnectionError as err:
        print(err)
        return HTTPException(400, detail=f'IOT connection error: {err}')

    return {
        'status': 'OK'
    }


@router.get('/ifconfig')
async def get_ifconfig():
    response = ifconfig()
    ifconfig_data = response.stdout
    interfaces = {}
    iface_name = ''
    iface_details = []

    for line in ifconfig_data.decode('utf-8').split('\n'):
        if not line.startswith('\t'):
            # New interface
            interfaces[iface_name] = iface_details
            iface_name = line.split(':', maxsplit=1)[0]
            iface_details = []
        else:
            if 'inet' in line:
                iface_details.append(line)
        # print(line)

    return interfaces


@router.put('/passcode')
async def check_passcode(request: Request, body: PasscodeBody):
    '''Check if a given passcode is correct.'''
    passcode = hash_passcode(body.passcode)

    # TODO: Check type here
    settings = request.app.config.get('settings', {})
    # TODO: Check if this needs to be disabled
    # Disable for Tampa
    # if settings.get('passcodeTriesRemaining', 1) <= 0:
    #     raise HTTPException(
    #         403,
    #         {
    #             'result': 'BLOCKED',
    #             'msg': 'No more tries left, please contact customer service.'
    #         }
    #     )
    return {
            'result': 'ALLOWED'
        }
    if passcode == settings.get('passcode'):
        settings['passcodeTriesRemaining'] = 10
        return {
            'result': 'ALLOWED'
        }
    else:
        settings['passcodeTriesRemaining'] -= 1
        raise HTTPException(
            403,
            {
                'result': 'FAIL',
                'passcodeTriesRemaining': settings['passcodeTriesRemaining'],
                'msg': 'Entered incorrect, passcode.'
            }
        )


@router.get('/passcode/setting')
async def get_lock_config(request: Request):
    settings = request.app.config.get('settings', {})
    return {
        'isProtected': request.app.config.get('activity_settings', {}).get('isProtected', False),
        'passcodeTriesTRemaning': settings.get('passcodeTriesRemaining'),
        'passcodeLockoutTimer': settings.get('passcodeLockoutTimer')
    }


@router.put('/passcode/setting')
async def configure_passcode(request: Request, body: PasscodeSetting):
    '''Vonfigure passcode, required existing passcode to be sent,
    if no passcode is set it will set one at that time.'''
    passcode = body.passcode
    passcode = hash_passcode(passcode)
    settings = request.app.config.get('settings', {})
    if settings.get('passcode') != passcode:
        raise HTTPException(
            403,
            {
                'result': 'FAIL',
                'msg': 'Entered passcode incorrectly',
                'passcodeTriesTRemaning': settings.get('passcodeTriesRemaining'),
                'passcodeLockoutTimer': settings.get('passcodeLockoutTimer')
            }
        )
    else:
        isProtected = body.isProtected
        if isProtected is not None:
            request.app.config.get('activity_settings', {})['isProtected'] = isProtected

    return {
        'isProtected': request.app.config.get('activity_settings', {}).get('isProtected')
    }


@router.put('/setdate')
def set_date(request: Request, body: dict):
    '''Use format {"value":"06-28-2023"}'''
    value = body.get('value')
    month, day, year = value.split('-')

    date_str = f'{month}/{day}/{year}'
    new_datetime = datetime.datetime.strptime(date_str, '%m/%d/%Y')
    current_datetime = datetime.datetime.utcnow()
    day_offset = (new_datetime.date() - current_datetime.date()).days

    request.app.config["date"]["day_offset"] = day_offset
    new_datetime2 = (current_datetime + datetime.timedelta(days=day_offset)).date()
    print(new_datetime)
    return {
        'offset': day_offset,
        'new_date': new_datetime2,
    }


@router.put('/setclock')
def set_time(request: Request, body: dict):
    '''Use format {"value":"05:21", "item":"pm"}'''
    value = body.get('value')
    item = body.get('item')
    hour, minute = value.split(':')
    hour, minute = int(hour), int(minute)

    am_pm = item
    time_str = f'{hour}:{minute} {am_pm}'

    if am_pm.lower() == 'pm' and int(hour) != 12:
        hour += 12
    elif am_pm.lower() == 'am' and hour == '12':
        hour = 0
    current_time = datetime.datetime.utcnow()
    new_time = datetime.datetime.strptime(time_str, '%I:%M %p')
    time_offset = new_time - current_time
    print(time_offset)
    request.app.config['time']['time_offset'] = time_offset.seconds

    new_time = (current_time + datetime.timedelta(seconds=time_offset.seconds)).time()

    return {
        # 'current_time': current_time.strftime('%H:%M:%S'),
        'new_time': new_time.strftime('%I:%M %p'),
        'time_offset': time_offset.seconds,
    }


@router.put('/timezone/autosync')
async def set_autosync(request: Request, body: dict):
    '''Use format {"onOff": 1}'''
    onoff = body.get('onOff')
    request.app.config['auto_sync'] = onoff
    if onoff == 1:
        while True:
            try:
                geoloc = await request.app.hal.communication.handler.get_sys_gps(
                    {
                        'usrOptIn': True
                    }
                )
                lat, lon = geoloc['position']['latitude'], geoloc['position']['longitude']
                try:
                    timezone_name = pytz.timezone(pytz.all_timezones[int((lat + 90) * 4)])
                    request.app.config['timezone']['TimeZonePreference'] = timezone_name.zone
                except Exception as err:
                    pass
                await asyncio.sleep(60)  # wait for 60 seconds before checking location again
            except Exception as err:
                print('Auto Sync not available')
                await asyncio.sleep(60)  # wait for 60 seconds before checking location again
    return request.app.config['time_auto_sync']


@router.put('/location')
async def set_location(request: Request, body: dict):
    onoff = body.get('onOff', None)
    if onoff is not None:
        request.app.hal.vehicle.handler.vehicle[2].state.usrOptIn = True if onoff == 1 else False
        request.app.hal.vehicle.handler.vehicle[2].save_db_state()
    return request.app.hal.vehicle.handler.vehicle[2].state


@router.put('/distance')
async def update_distance_unit(request: Request, body: dict):

    value = body.get('value')
    item = body.get('item')

    distance_unit = request.app.config.get('distanceunits')
    if distance_unit is None:
        raise ValueError('Distance Unit not part of the config')

    updated = False
    if item in distance_unit:
        if distance_unit[item] != value:
            distance_unit[item] = value
            updated = True

    response = {
        'updated': updated,
        'item': item,
        'value': distance_unit[item]
    }

    return response


@router.put('/appearance')
async def auto_adjust_sunset(request: Request, body: dict = {'onOff': 1}):

    onOff = body['onOff']
    auto_sunset = request.app.config.get('auto_adjust_sunset')
    if auto_sunset is None:
        raise ValueError('Auto Adjust Sunset not part of the config')

    request.app.config['auto_adjust_sunset'] = onOff

    return request.app.config['auto_adjust_sunset']


@router.put('/pushnotification')
async def push_notification(request: Request, body: dict = {'onOff': 0}):

    onOff = body['onOff']
    push_notification = request.app.config.get('push_notification')
    if push_notification is None:
        raise ValueError('Push notification not part of the config')

    request.app.config['push_notification'] = onOff

    return request.app.config['push_notification']


@router.put('/timezone/settings')
async def set_timezone(request: Request, body: dict):
    '''Update the timezone settings.'''
    value = body.get('value')
    item = body.get('item')
    timezone_preference = request.app.config.get('timezone')
    timezone_name = f'US/{value}'
    tz = pytz.timezone(timezone_name)
    current_time_tz = datetime.datetime.now(tz=tz)
    is_dst = tz.localize(datetime.datetime.now(), is_dst=None).dst() != datetime.timedelta(0)
    # Adjust the time for daylight saving time, if necessary
    if not is_dst:
        current_time_tz -= datetime.timedelta(hours=1)

    if timezone_preference is None:
        raise ValueError('Time zone not part of the config')

    updated = False
    if item in timezone_preference:
        # Compare
        if timezone_preference[item] != timezone_name:
            timezone_preference[item] = timezone_name
            updated = True

    if updated is True:
        # Save in database
        request.app.save_config('settings.timezone.UserTimeZonePreference', timezone_name)
    return {
        'updated': updated,
        'timezone': timezone_preference,
    }


@router.put('/datareset')
async def reset_data(request: Request, are_you_sure: bool = False):

    if are_you_sure is False:
        return
    else:
        try:
            #delete db
            print('Data Reset Request!')
            request.app.user_db.delete_database()
            request.app.wgo_logger.info(f"User db tables dropped!")
        except Exception as err:
            print('Could not reset data', err)
            return

        # Send VIN back to IOT
        request.app.hal.lighting.handler.event_logger.add_event(
                        RVEvents.CHASSIS_VIN_CHANGE,
                        CHASSIS_ID,
                        request.app.hal.vehicle.handler.state.get('vin')
                    )
        # reboot system
        # try:
        #     # exit and restart main?
        #     shutdown_main_system()
        # except Exception as err:
        #     print('Could not reboot', err)
        #     return

    # Add the request to the IOT queue
    # request_to_iot({"hdrs": dict(request.headers), "url": f'/api/system/datareset', "body": _body})

    return {'Data has been reset'}


@router.get('/reset/loading')
async def reset_loading(request: Request, progress: int):
    progress = 100
    # for time in range(1, 11):
    #     progress = time * 10
    #     await asyncio.sleep(5)
    return progress


@router.get('/ipaddress')
async def get_ip_address(request: Request):
    return get_ip()


@router.get('/lk/{instance}/state')
async def get_lockout_state(request: Request, instance: int):
    lockout = await validate_wc_api_call(request, PREFIX, 'lk', instance)
    return lockout.state


@router.put('/lk/{instance}/state')
async def test_set_lockout_state(request: Request, instance: int, state: dict):
    lockout = await validate_wc_api_call(request, PREFIX, 'lk', instance)

    try:
        lockout.state.validate(state)
    except ValidationError as err:
        raise HTTPException(
            422,
            detail=str(err)
        )

    lockout.state.active = state.get('active', False)
    return lockout.state


@router.get('/lk/{instance}/name')
async def get_lockout_name(request: Request, instance: int):
    event = EventValues(instance)
    return {
        'id': instance,
        'name': event.name
    }


@router.get('/lk/state')
async def get_all_lockout_state(request: Request):
    result = {}
    for instance, lockout in request.app.hal.system.handler.lockouts.items():
        result[f'lk{instance}'] = lockout.state

    return result


@router.get('/motd')
async def get_message_of_the_day(request: Request):
    return request.app.config.get('motd')


@router.put('/motd')
async def set_motd(request: Request, motd: dict):
    random_facts = (
        'Random Fact 1',
        'Random Fact 2',
        'Random Fact 3'
    )
    msg_of_the_day = {
        'iconType': 'ASSET',
        'icon': 'WGO',
        'title': motd.get('title', 'Random Fact'),
        'text': motd.get('text', random.choice(random_facts)),
        'actions': None,
        'name': 'HomeMotdMessage'
    }
    request.app.config['motd'] = msg_of_the_day
    return request.app.config.get('motd')


@router.get('/can/filter')
async def get_can_filter(request: Request):
    '''Get current CAN filter.'''
    print('FETCHING CAN Filter')
    can_mapping = request.app.hal.cfg.get('can_mapping', {})
    return {
        k: '' for k, _ in can_mapping.items()
    }


@router.get('/state')
async def get_system_state(request: Request):
    system_state = request.app.hal.get_state().get('system')

    return system_state


@router.get('/can/state/rvc')
async def get_can_rvc_errors(request: Request):
    return request.app.hal.system.handler.state.get('CAN', {})


@router.put('/rundiagnostics')
async def run_can_diagnostics(request: Request):
    '''Perform diagnostics on request.'''
    # TODO: Figure out which tests to run
    return {'msg': 'OK'}


@router.put('/manufacturing/mode')
async def set_manufacturing_mode(request: Request, mode: dict):
    '''Set manufacturing mode.'''
    MODE_MANUFACTURING = 'MANUFACTURING'
    on_off = mode.get('onOff')
    app_modes = list(request.app.operation_modes)
    # This assumes the set below will always ensure that there is a single
    # occurrence only
    if on_off == EventValues.ON:
        app_modes.remove(MODE_MANUFACTURING)
    elif on_off == EventValues.OFF:
        app_modes.append(MODE_MANUFACTURING)

    request.app.operation_modes = set(app_modes)


@router.put('/features/settings/fcp')
async def enable_fcp(request: Request, _body: dict):
    '''Enables the FCP under System UI as a hidden button.'''
    service_stettings = request.app.hal.system.handler.setting.get(1)

    request.app.config['system']['fcpEnabledCounter'] += 1
    print('[FCP] Counter', request.app.config['system']['fcpEnabledCounter'])
    if request.app.config['system']['fcpEnabledCounter'] >= 10:
        service_stettings.state.fcpEnabled = EventValues.ON
    else:
        service_stettings.state.fcpEnabled = EventValues.OFF

    remaining_taps = 10 - request.app.config['system']['fcpEnabledCounter']

    if service_stettings.state.fcpEnabled == EventValues.OFF:
        if remaining_taps < 5:
            return {
                'msg': f'Keep pressing {remaining_taps} more times to enable debugging menu',
                'fcpEnabled': service_stettings.state.fcpEnabled
            }

    return {
        'fcpEnabled': service_stettings.state.fcpEnabled
    }


@router.get('/us/{instance}/state')
async def get_settings_component(request: Request, instance: int):
    '''Get state of the given setting instance.'''
    setting = await validate_wc_api_call(request, PREFIX, 'us', instance)
    return setting.state


@router.put('/us/{instance}/state')
async def set_settings_component(request: Request, instance: int, state: dict):
    '''Update settings for the given settings.'''
    setting = await validate_wc_api_call(request, PREFIX, 'us', instance)
    return setting.set_state(state)


@router.put('/features/settings/serviceMode')
async def enable_service_mode(request: Request, _body: dict):
    '''Old endpoint to set from FCP.'''
    if _body.get('onOff') == EventValues.ON:
        request.app.config['system']['serviceModeEnabled'] = True
        mode = EventValues.ON
    else:
        request.app.config['system']['serviceModeEnabled'] = False
        mode = EventValues.OFF

    setting = await validate_wc_api_call(request, PREFIX, 'us', 1)
    setting.set_state({
        'serviceModeOnOff': mode
    })

    return setting.state
