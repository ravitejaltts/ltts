import asyncio
import csv
import json
import logging
import os
import signal
import sqlite3
import threading
import time
from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from io import StringIO
from logging.handlers import RotatingFileHandler
from threading import Lock
from typing import List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import JSONResponse, StreamingResponse
from starlette.types import Receive, Scope

from common_libs import environment
from common_libs.models.common import FLOORPLAN_TO_INFO
from common_libs.system.schedule_manager import ScheduledFunctionManager
from common_libs.system.scheduled_function import ScheduledFunction
from common_libs.system.system_storage_helper import get_telemetry_file
from common_libs.clients import MAIN_CLIENT
from common_libs.models.common import BtStateChange, EventValues, LogEvent, RVEvents
from common_libs.models.gui import Motd
from common_libs.models.notifications import (
    Notification,
    NotificationTrigger,
    alert_to_iot,
    dismiss_note,
    event_to_bt,
    event_to_iot,
    update_notification_from_csv_row,
    notification_from_dict,
    prepare_display_note
)

from main_service.components.energy import GeneratorBasic
from main_service.components.system import (
    ActionTracker,
)
from main_service.modules.can_helper import (
    CAN_IGNORE_MAP,
    CANAPIForwardBackgroundRunner,
    CANSendBackgroundRunner,
)
from main_service.modules.sw_features import Features
from main_service.modules.system_helper import (
    check_partitions,
    clear_caches,
    get_iot_status,
    read_about_from_bld_directory,
    read_current_version_about,
    set_display_brightness,
    set_display_on,
    shutdown_main_system,
)
from main_service.modules import db_helper as database
from main_service.modules.constants import (
    # TIME_MODE_AM,
    # TIME_MODE_PM,
    DISTANCE_UNIT_MILES,
    # TEMP_UNIT_CELCIUS,
    # HVAC_MODES,
    # TEMP_UNITS,
    # TEMP_UNIT_PREFERENCE_KEY,
    HVAC_MODE_AUTO,
    TEMP_UNIT_FAHRENHEIT,
    TIME_ZONE_EASTERN,
    # WATER_UNITS,
    WATER_UNIT_GALLONS,
)
from main_service.modules.hardware.hal import init_hw_layer
from main_service.modules.storage_helper import (
    read_ui_config_file,
)
from main_service.routers import api, api_home, testing_harness

# Version for the service is in the main py file.
__version__ = "1.1.12"
__author__ = 'Dominique Parolin and others'


try:
    from setproctitle import setproctitle
    setproctitle('WGO-MAIN-Service')
except ImportError:
    pass

_env = environment()

# Check partitions are available, function does not do anything right now
check_partitions()

LIGHTING_PRESET_COUNT = 3
CAN_RESET_URL = 'http://localhost:8001/state/reset'
CAN_FILTER_URL = 'http://localhost:8001/filter'

OTA_BATTERY_SOC_LOW_THRESHOLD = 50         # % SoC
OTA_BATTERY_SHORE_SOC_LOW_THRESHOLD = 25    # % SoC
OTA_BATTERY_VOLTAGE_LOW_THRESHOLD = 12.8    # V


def get_motd_handler(app):
    '''Creates Motd.'''
    try:
        _ = app.hal
    except AttributeError as e:
        print(e)
        return {}

    try:
        floorplan = app.hal.floorPlan
        model = FLOORPLAN_TO_INFO.get(floorplan, {}).get('name', '')
        floorplan = FLOORPLAN_TO_INFO.get(floorplan, {}).get('floorplan', '')
        model = f'{model} {floorplan}'
    except AttributeError as e:
        print(e)
        model = '--'

    try:
        motd = app.config.get('motd')
    except AttributeError:
        # Happens when config is not yet added to app
        motd = None

    # NOTE: No spaces between punctuation EVER!

    if motd is None:
        motd = {
            'iconType': 'ASSET',
            'icon': 'WGO',
            'title': f'Winnebago {model}',
            'text': 'Welcome Home!',
            # NOTE: Emojis not supported without adding a heavy emoji font
            # 'text': 'Good Morning ! 🚙🚙🚙🚙',
            'actions': None,
            'name': 'HomeMotdMessage'
        }
    return motd


def save_config(config_key, config_value):
    ''' Receive config and hw setting updates.

    config_key: 'lighting.zone.1' / 'watersystems.pump.1' / 'climate.zone.1.set_temp_cool'
    config_value: {
        'onOff': 1,
        }
    '''
    # TODO: Check type of config_value and convert as needed to fit into json
    stored_config_value = user_db.set_config(
        config_key,
        config_value
    )

    return stored_config_value


def get_config(config_key, default=None, partial=False):
    '''Retrieve a specific config key.

    config_key: 'lighting.zone.1'
    '''
    # TODO: What do we do if that value does not exist ?
    # If not exist return None
    # Next layer will handle this
    # Check template / hw defaults in calling function
    config_value = None

    if partial is False:
        config_value = user_db.get_config(config_key)
    else:
        raise NotImplementedError('Soon!')

    # TODO: Check config_value and convert back if in 'value'
    if config_value is None:
        config_value = default

    return config_value


def init_floorplan(cur_app, floorplan, options: list = None):
    '''Initialized the floor plan, including alerts etc.'''
    if options is None:
        options = []
    # TODO: Add a check that looks for the most crucial given options like
    # air_conditioner, battery
    hal, cfg, sanity = init_hw_layer(cur_app, floorplan, options)
    if sanity is False:
        # We identified crucial missing components, cannot proceed
        event_logger(
            LogEvent(
                timestamp=time.time(),
                event=RVEvents.FLOORPLAN_ERROR,
                instance=0,
                value=EventValues.MAIN_SERVICE,
                meta={
                    'floorplan': floorplan,
                    'options': str(options)
                }
            )
        )
        hal, cfg, _ = init_hw_layer(cur_app, 'VANILLA', [])

    cur_app.hal = hal

    #init_notifications(cur_app, cfg)  # Init the List of Notifications
    print("APPLY STUFF HERE")
    apply_notification_changes(cur_app)

    init_system(cur_app)

    # TODO: Need to know where to put this - new function maybe?
    if floorplan != "VANILLA":

        # Fetch the iot status for serial number etc
        get_iot_status(cur_app)
        # Clean out previous functions
        cur_app.taskScheduler.dump_all_scheduled_functions()

        # Start to check for gps every X seconds
        gpsChecker = ScheduledFunction(
            function=Features.check_gps_task,
            args=(cur_app.hal,),
            wait_seconds=60,  # 1 min Determine rate after testing
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(gpsChecker)

        # Register for 24 hours functions -
        once_task = ScheduledFunction(
            function=Features.register_for_weather_task,
            args=(cur_app,),
            wait_seconds=(900),  # once to start as one shot - wait 15 min to see if gps lock arrives
            oneshot=True
        )
        cur_app.taskScheduler.add_timed_function(once_task)

        daily_task = ScheduledFunction(
            function=Features.register_for_weather_task,
            args=(cur_app,),
            wait_seconds=86400,  # once a day or when loations move
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(daily_task)

        once_task = ScheduledFunction(
            function=Features.report_all_events_task,
            args=(cur_app,),
            wait_seconds=(600),  # once to start as one shot - wait 10 min to report all events
            oneshot=True
        )
        cur_app.taskScheduler.add_timed_function(once_task)

        daily_task = ScheduledFunction(
            function=Features.report_all_events_task,
            args=(cur_app,),
            wait_seconds=86400,  # once a day report all events
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(daily_task)

        time_notes_task = ScheduledFunction(
            function=check_time_notifications_expired,
            args=(cur_app,),
            wait_seconds=900,   # Clear every 15 min
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(time_notes_task)

        sunset_checker = ScheduledFunction(
            function=Features.check_sunset,
            args=(cur_app,),
            wait_seconds=60,    # 1 min Determine rate after testing
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(sunset_checker)

        tcu_checker = ScheduledFunction(
            function=cur_app.hal.features.handler.check_tcu_information,
            args=(),
            wait_seconds=45,    # 45 secs Determine rate after testing
            oneshot=True
        )
        cur_app.taskScheduler.add_timed_function(tcu_checker)

        connectivity_checker = ScheduledFunction(
            function=cur_app.hal.features.handler.check_connectivity,
            args=(),
            wait_seconds=60,    # 1 min Determine rate after testing
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(connectivity_checker)

        # periodic_can_requests found in sw_featues.py
        periodic_can_send = ScheduledFunction(
            function=cur_app.hal.features.handler.periodic_can_requests,
            args=(),
            wait_seconds=10,    # 1 min Determine rate after testing
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(periodic_can_send)

        periodic_system_overview = ScheduledFunction(
            function=cur_app.hal.features.handler.periodic_system_overview,
            args=(),
            wait_seconds=10,
            oneshot=False
        )
        cur_app.taskScheduler.add_timed_function(periodic_system_overview)

        # # NOTE: MODEL / OPTIONCODE specific init
        # # IF we have a generator - check when to increment hour meter
        # # TODO: is there a better test for a generator component?
        # if hasattr(cur_app.hal.energy.handler, 'generator'):
        #     # Check if we have first instance
        #     generator = cur_app.hal.energy.handler.generator.get(1)
        #     if generator is not None:
        #         # We have a generator instance 1
        #         run_meter = ScheduledFunction(
        #             function=GeneratorBasic.check_hours,
        #             args=(generator,),
        #             wait_seconds=36,  # 100th on an hour
        #             oneshot=False
        #         )

        #         cur_app.taskScheduler.add_timed_function(run_meter)
                # print(f"Generator found with  {generator.get_db_state().hours} hours")
        # else:
        #     print('No Generator found')

        if hasattr(cur_app.hal.features.handler, 'diagnostics'):
            SYS_OVERVIEW_INSTANCE = 3
            system_overview = cur_app.hal.features.handler.diagnostics.get(
                SYS_OVERVIEW_INSTANCE
            )
            if system_overview is not None:
                system_overview.state.startTime = time.time()
                print('PERIODIC SYSTEM OVERVIEW: Set Starttime')

    event_logger(
        LogEvent(
            timestamp=time.time(),
            event=RVEvents.FLOORPLAN_LOADED,
            instance=0,
            value=EventValues.MAIN_SERVICE,
            meta={
                'host': '',
                'port': ''
            }
        )
    )


# def init_telemetry(cur_app, telemetry_path):
#     '''Initialize the telemetry items'''
#     print('TELEMETRY', 'Trying to load path', telemetry_path)
#     # if os.path.exists(telemetry_path):
#         # TODO: Check SNYK recommendation for abspath and preventing relative path to be passed in
#     try:
#         t_cfg = get_telemetry_file(telemetry_path)
#     except Exception as e:
#         print(e)
#         return True
#     try:
#         apply_notification_changes(cur_app)
#     except Exception as e:
#         print('TELEMETRY ERROR', e)
#         # print("No telemetry alert_items", e)

#     # else:
#     #     # TODO: Find the proper way to handle this downstream.
#     #     print('TELEMETRY', 'Path does not exist', telemetry_path)
#     #     return True


def init_system(app):
    '''Initialize system as required to get back to where user was.
    Considerations for cold/warm boot.'''
    # Set display on
    check_partitions()
    set_display_on()

    # Get display brightness
    stored_brightness = app.get_config('settings.DisplayBrightness')
    if stored_brightness is None or stored_brightness == 0:
        user_brightness = 75    # TODO: create a default variable
    else:
        user_brightness = stored_brightness

    _ = set_display_brightness(user_brightness)

    # Get user selected timezone
    timezone = app.get_config('settings.timezone.UserTimeZonePreference')
    print('[SYSTEM][INIT][Timezone]', timezone)
    if timezone is not None:
        app.config['timezone']['TimeZonePreference'] = timezone

    sunset_setting = app.get_config('settings.AutoScreenModeSunset')
    if sunset_setting is not None:
        app.config['settings']['AutoScreenModeSunset'] = sunset_setting

    clear_caches()


def get_lighting_presets():
    # TODO: Remove hardcoding, read amount of presets from feature template
    presets = {}
    for i in range(LIGHTING_PRESET_COUNT):
        j = i + 1
        config_value = get_config(f'lighting.preset.{j}')
        presets[j] = config_value
    return presets


HOME_DIR = os.environ.get("WGO_HOME_DIR", '.')

try:
    VERSION = json.load(
        open(
            os.path.join(
                HOME_DIR,
                'version.json'
            ),
            'r'
        )
    )
except IOError as err:
    try:
        VERSION = json.load(
            open('../version.json', 'r')
        )
    except IOError as err:
        VERSION = {
            'version': __version__,
        }

# Inject more data
VERSION['debug'] = True

MAIN_SERVICE_PORT = _env.main_service_port
DEBUG = int(os.environ.get('WGO_MAIN_DEBUG', 0))
FCP_DEBUG = int(os.environ.get('WGO_FCP_DEBUG', 0))
DEBUG = (DEBUG == 1)
# NOTE: Temp fix for frontend failing to update
# FRONTEND_DIR = os.environ.get('WGO_FRONTEND_DIR')
FRONTEND_DIR = '/opt/smartrv/smartrv-frontend'
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = os.environ.get('WGO_FRONTEND_DIR', '.')
    if FRONTEND_DIR is None:
        raise ValueError(
            'Please set ENV variable WGO_FRONTEND_DIR properly to frontend directory to serve'
        )
print(f'[INIT] Frontend Dir: {FRONTEND_DIR}')

BIND_ADDRESS = _env.bind_address

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    # Remove * in prod but allow in dev
    "*",
]

db_config = {
    'path': _env.storage_file_path('wgo_user.db')
}

try:
    user_db = database.DBHandler(db_config)
except sqlite3.OperationalError as err:
    # Fallback for local non linux testing (or whereever else there is not such path)
    # user_db = database.DBHandler({'path': 'wgo_user.db'})
    print('Database error', err)
    raise


def restart():
    '''Kill the current process, and handle it gracefully in the shutdow procedure.'''
    os.kill(os.getpid(), signal.SIGTERM)


app = FastAPI(
    title='WinnConnect Coach MAIN API',
    description='Main APIs to control all aspects of the Coach SW.',
    version=VERSION.get('version')
)

app.restart_service = restart
app.init_floorplan = init_floorplan
#app.init_telemetry = init_telemetry
app.get_motd = get_motd_handler
# Operation Modes allow certin pages to be shown or hidden and can change behavior as needed
app.operation_modes = []

# Event will be set trying gracefull end the scheduler task
stop_event = asyncio.Event()

# Schema validator
# async def set_body(request: Request):
#     receive_ = await request._receive()

#     async def receive():
#         return receive_

#     request._receive = receive

# TODO: Remove later when decided what the middleware structure should be
# @app.middleware("http")
# async def validate_source(request: Request, call_next):
#     '''Validate headers for source.
#     Using 'host'
#     Could also use origin
#     'origin': 'http://localhost:3000'
#     '''
#     ALLOWED_ORIGINS = [
#         'http://localhost:3000',
#         'http://localhost:8000'
#         # What is another service hitting ?
#     ]
#     source = request.headers.get('source')
#     if source is None:
#         source = 'UNKNOWN'
#         if request.headers.get('origin') in ALLOWED_ORIGINS:
#             # Localhost, HMI
#             source == 'HMI'
#         else:
#             source == 'UNKNOWN'

#     if source == 'HMI':
#         # An HMI request can perform all actions
#         pass
#     elif source == 'BLUETOOTH':
#         # Bluetooth might have restrictions
#         # TODO: This validate_source is not called?
#         if request.app.config['system']['serviceModeEnabled'] is True:
#             raise HTTPException(423, json={'lockout': [EventValues.SERVICE_MODE_LOCKOUT,]})

#     elif source == 'platform':
#         # IOT cannot perform all functions far-field
#         # Check if allowed - add to the validate schema calls
#         # TODO: This validate_source is not called?
#         if request.app.config['system']['serviceModeEnabled'] is True:
#             raise HTTPException(423, json={'lockout': [EventValues.SERVICE_MODE_LOCKOUT,]})

#     elif source == 'UNKNOWN':
#         # Source not set, try to get from need to get rid of this
#         # Could restrict the APIs to the minumum set, at least to what far field
#         # is allowed to do
#         pass
#     elif source == 'INTERNAL_ALGO':
#         # This is a source as a last resort if a functionality can
#         # only be achieved with API calls
#         pass
#     elif source == 'UNIT_TEST':
#         # Source coming from unit testing an API, should be handled as HMI unless otherwise required for testing
#         pass
#     else:
#         raise (ValueError(f'Unknown source: {source}'))

#     response = await call_next(request)

#     return response


async def validate_schema(request: Request, call_next):
    path = request.url.path
    validated = False
    wrong_apis = [
        'zones',    # Lighting state which aneds in state
    ]

    if path.startswith('/api/') and request.method.upper() == 'PUT' and path.endswith('state'):
        # Check if this is a known component path
        # If yes get body as json and validate the correct schema
        print('>>>>>>>>>>>MIDDLEWARE\n' * 5)
        print(path)
        url_parts = path.split('/')
        print(url_parts)
        category, component, instance = url_parts[2:5]
        print(
            category,
            component,
            instance
        )

        # TODO: Find exceptions and handle
        # Instance is an integer
        try:
            instance = int(instance)
        except ValueError as err:
            print('Error converting instance', err)
            instance = None

        if instance is not None:
            # General HW handler for this category
            hw_handler = getattr(request.app.hal, category).handler
            # Get instance
            try:
                comp_instance = getattr(
                    hw_handler, hw_handler.CODE_TO_ATTR[component])[instance]
            except KeyError as err:
                print(path, 'KeyError', err)
                print('Ignoring request fior schema validation')
                return await call_next(request)

            print(comp_instance)

            # body = await request.json()
            # print(body)
            print('NEED TO VALIDATE')
            validated = True
            print('<<<<<<<<<<<<MIDDLEWARE\n' * 5)

            print('Await call_next')
            response = await call_next(request)
            print('Done with call Next')
            if validated is True:
                response.headers['X-STATE-SCHEMA-VALIDATED'] = str(True)
        else:
            print('No instance provided')
            response = await call_next(request)

    else:
        response = await call_next(request)

    return response


class BodyResetRequest(Request):
    def __init__(self, scope: Scope, receive: Receive, body: bytes):
        super().__init__(scope, receive)
        self._cached_body = body

    async def body(self) -> bytes:
        return self._cached_body

    async def json(self):
        return json.loads(self._cached_body.decode("utf-8"))


@app.middleware("http")
async def validate_farfield(request: Request, call_next):
    '''Check if the incoming call is allowed under current conditions,
    lockouts etc.'''
    source = request.headers.get('source')
    request.state.check_special_state = False
    # print("TOP source ", source)
    method = request.method.upper()
    service_mode = False
    if hasattr(request.app.hal, 'system'):
        # NOTE: At import time hal won't have the system handler yet, so it
        # would throw an attribute error
        if hasattr(request.app.hal.system.handler, 'setting'):
            service_settings = request.app.hal.system.handler.setting.get(1)
            # print('[SETTINGS] Service Settings', service_settings)
            if service_settings is not None:
                service_mode = True if service_settings.state.serviceModeOnOff == EventValues.ON else False
                # print('[SETTINGS] Service Mode', service_mode, service_settings.state, method)

    if source == "platform":
        if method == 'PUT' and service_mode is True:
            # NOTE: We do not allow PUT requests while service mode is enabled
            return JSONResponse(
                status_code=423,
                content={
                    "detail":
                        "Farfield commanding not allowed."
                        " The HMI is in service mode.",
                    'lockouts': [EventValues.SERVICE_MODE_LOCKOUT,]
                }
            )
        path = request.url.path
        if path.startswith('/api/') and method == 'PUT' \
                and path.endswith('state'):
            url_parts = path.split('/')
            category, component, instance = url_parts[2:5]
            # Instance is an integer
            try:
                instance = int(instance)
            except ValueError as e:
                print('Error converting instance', e)
                instance = None

            if instance is not None:
                # General HW handler for this category
                hw_handler = getattr(request.app.hal, category).handler

                # Get instance
                comp_instance = getattr(
                    hw_handler,
                    hw_handler.CODE_TO_ATTR[component]
                ).get(instance)
                # TODO: Figure out when this would happen
                if comp_instance is None:
                    print('Ignoring request for schema validation')
                    return await call_next(request)

                source = request.headers.get('source')
                if source == 'platform' and 'F' not in comp_instance.attributes.get('controllable'):
                    # TODO: Check if we can see inside request body and keep going - at this time we can not - waiting on the FastAPI guys
                    if 'S' not in comp_instance.attributes.get('controllable') or comp_instance.attributes.get('special-states') is None:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": "Farfield commanding not allowed for this component."
                            }
                        )
                    else:
                        special_states = comp_instance.attributes.get('special-states')
                        # print('special-states=', special_states)
                        # print('state=', comp_instance.state)
                        # print('\n\n',request.__dict__)
                        request.state.check_special_state = True
                        response = await call_next(request)
                else:
                    print('FAR FIELD PERMITTED')
                    response = await call_next(request)
            else:
                print('No Instance provided')
                response = await call_next(request)
        else:  # Not for state
            print('Not for /state')
            response = await call_next(request)
    else:
        if source == "BLE" and method == 'PUT':
            if service_mode is True:
                return JSONResponse(
                    status_code=423,
                    content={
                        "detail": "Nearfield commanding not allowed. The HMI is in service mode.",
                        'lockouts': [EventValues.SERVICE_MODE_LOCKOUT,]
                    }
                )

        response = await call_next(request)

    return response

LOG_MAX_FILE_SIZE = 20000
LOG_BACKUP_FILE_CNT = 1

# TODO: Check if this is initialized too many times for the same logger
logger = logging.getLogger('main_service')

logger.setLevel(logging.DEBUG)
# logHandler = logging.StreamHandler()
fileLogHandler = RotatingFileHandler(
    _env.log_file_path('main_service.log'),
    'a+',
    maxBytes=LOG_MAX_FILE_SIZE,
    backupCount=LOG_BACKUP_FILE_CNT
)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fileLogHandler.setFormatter(formatter)
logger.addHandler(fileLogHandler)
# logHandler.setFormatter(formatter)
# logger.addHandler(logHandler)

app.wgo_logger = logger
app.user_db = user_db

# TODO: Read from config file or provider
app.config = {
    'activity_settings': {
        # Interval the current page shall use when polling for an update
        'activePollingInterval': 1,
        # When no touches occured for the inactiveTimeout, set the screen to inactive (usually reduces brightness)
        'inactiveTimeout': 280,
        # After hitting inactive, after an additional offTimeout send off which will turn the screen off (brightness 0)
        # offTimeout is more or less a constant that is a timedelta
        'offTimeout': 0,        # TEMP set to 0
        'lockTimeMinutes': 5,
        # Time the current page shall be polling when in off
        # 0 - Never
        'offPollingInterval': 60,
        # Page to navigate to after waking up / returning from lock screen
        # If none remain on current page
        'navigateTo': '/home',
        'activityAPIs': {
            'type': 'PUT',
            'inactive': '/api/system/activity/idle',
            'active': '/api/system/activity/on',
            'off': '/api/system/activity/off'
        },
        # TODO: Get from user settings
        'isProtected': False
    },
    'settings': {
        'BluetoothControlEnabled': 1,
        'VolumeUnitPreference': WATER_UNIT_GALLONS,
        'TempUnitPreference': TEMP_UNIT_FAHRENHEIT,
        'DataBackupEnabled': 1,
        'UIScreenMode': 'LIGHT',
        'AutoScreenModeSunset': 0,
        # Backlight intensity between 0 and 100%
        # TODO: Get this from the DB and only use default then
        # TODO: Add the defaults to a config file and then fall back to code default
        'DisplayBrightness': 75,
        # Passcode Settings
        'passcode': '0eed0213db0062b1672f0f9cd10c262e7016416f38f792a28b6b213acc03abba',
        'passcodeTriesRemaining': 10,
        'passcodeLockoutTimer': 0,
        'debugEnabled': DEBUG
    },
    'BluetoothSettings': {
        'BluetoothControlEnabled': 1,
        'ConnectedDevices': [
            # {
            #     'name': 'Iphone12',
            #     'connected': True,
            #     'macAddress': '44:01:BB:E0:90:9B'

            # },
            # {
            #     'name': 'Samsung Galaxy s22',
            #     'connected': False,
            #     'macAddress': '44:01:BB:E0:90:9C'
            # }
        ],
        'PairingStatus': {
            'state': 0,
            'timeStamp': '2023-08-21 15:30:45',
        },
    },
    'cellular': {
        'onOff': 1,
        'band': '5G',
        'signalStrength': 52,
        'status': 'Connected',
    },
    'watersystems': {
        'VolumeUnitPreference': WATER_UNIT_GALLONS,
    },
    'distanceunits': {
        'DistanceUnits': DISTANCE_UNIT_MILES,
    },
    'refrigerator': {
        'TempAlertThreshold': None,
        'AlertOnOff': 1,
    },
    'freezer':{
        'AlertOnOff': 1,
    },
    'climate': {
        'TempUnitPreference': get_config('climate.TempUnitPreference', TEMP_UNIT_FAHRENHEIT),
        'HVACMode': HVAC_MODE_AUTO,
        'rainSensor': 0,
        'heatCoolMin': {
            'setTemp': 5,
        },
        'coolDifferential': {
            'setTemp': 0.5,
        },
        'minOutDoor': {
            'setTemp': 60,
        },
        'indoorTempAlert': 0,
        'location': 1,
    },
    'timezone': {
        'TimeZonePreference': TIME_ZONE_EASTERN,
    },
    'date': {
        'day_offset': 0,
    },
    'time': {
        'time_offset': 0,
    },
    'slideOut': {
        'lastSignedDate': '2023-10-15',
        'timeLimit': 1,
        'twoStepReq': True,
    },
    'awning': {
        'lastSignedDate': '2023-10-15',
        'timeLimit': 1,
        'twoStepReq': True,

    },
    'time_auto_sync': 0,
    'push_notification': 0,
    'auto_adjust_sunset': 0,
    'climate_schedules': [
        {
            'id': 0,
            'name': 'scheduleWake',
            'title': 'Wake',
            'startHour': 7,
            'startMinute': 30,
            # Options for startTimeMode: 'AM, 'PM', '24H'
            'startTimeMode': 'AM',
            'setTempHeat': 68,
            'setTempCool': 75
        },
        {
            'id': 1,
            'name': 'scheduleAway',
            'title': 'Away',

            'startHour': 10,
            'startMinute': 0,
            'startTimeMode': 'AM',

            'setTempHeat': 60,
            'setTempCool': 80
        },
        {
            'id': 2,
            'name': 'scheduleAtcamp',
            'title': 'At Camp',

            'startHour': None,
            'startMinute': None,
            'startTimeMode': None,

            'setTempHeat': None,
            'setTempCool': None
        },
        {
            'id': 3,
            'name': 'scheduleSleep',
            'title': 'Sleep',

            'startHour': 7,
            'startMinute': 30,
            'startTimeMode': 'AM',

            'setTempHeat': 68,
            'setTempCool': 75
        }
    ],
    'lighting': {
        'itcConfigTimer': 0,
    },
    'electrical': {},
    'lighting_presets': get_lighting_presets(),

    # TODO: Move to another place
    'CHARGE_LVL_DEFAULT': 1300,
    'CHARGE_LVL_L2': 5350,
    'CHARGE_LVL_L1_5': 1400,
    'CHARGE_LVL_L2_MAX': 7200,

    # TODO: Read from model/floorplan
    # 'motd': get_motd_handler(app),
    'VIN': None,
    # TODO: Define how quick actions are made available and prioritized to be shown
    'quickactions': [],
    'features': {
        'petmonitoring': {
            'title': 'Pet Minder Initializing',
            'subtitle': 'Gathering Data',
            'body': 'Have a Good Day!',
            'level': 4,     # Default Info level, should be blue
            'footer': None
        }
    },
    'system': {
        # API to enable this needed
        'fcpEnabled': False,
        'serviceModeEnabled': False,
        'fcpEnabledCounter': 0,     # Used to do Android like tapping
    }
}
app.hal = None
# Sessions are used to send delta states
app.sessions = {}
app.ota_state = {'waiting': 'False',
                 'version': '',
                 'checked': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
app.iot_status = {}  # Filled with iot fetch

# TODO: Should this be a deque with max length ?
# Should we recover this from database ?
# Error log as shown
MAX_ERROR_LOG_LENGTH = 50
app.error_log = deque(maxlen=MAX_ERROR_LOG_LENGTH)

# Test only
# app.error_log.append(
#     [
#         {
#             'title': 'Serious Error Dude!',
#             'type': 'ERROR',
#             'topText': 'No Errors',
#             'timestamp': 'Now',
#             'body': 'No errors logged in the system.',
#         }
#     ]
# )

# TODO: BRUCE What is this ?  Looks like something Niha added - I don't see it being accessed but maybe part of a plan to reset to new user?
global default_config_dict
default_config_dict = deepcopy(app.config)

app.notifications = []

app.n_lock = Lock()

app.event_notifications = {}

app.updateNow = ActionTracker()  # Force IOT updates by incrementing the tracker
app.updateNow.increment()  # Starts an update cycle for 30 seconds


# def init_notifications(app, config_items):
#     # print(f"%^%^%^%^%^%^%^^%^   init_notifications {config_items}")
#     # check the default notificaitions are all included
#     # config_items = read_default_config_json_file()

#     app.wgo_logger.debug('Read Default_config notifications before DB update')
#     for i in config_items['alert_items']:
#         # app.wgo_logger.debug( f'Alert item check {i} DB')
#         # new_notification = notification_from_dict(DEFAULT_NOTIFICATIONS[i])
#         new_notification = notification_from_dict(
#             config_items['alert_items'][i])
#         try:
#             notification_key = new_notification.notification_id
#             app.event_notifications[notification_key] = new_notification  # First recording of the notification
#             # now if the notifications is in the db read out current changes
#             db_note = user_db.get_notification(notification_key)
#             if  db_note is not None:
#                 app.event_notifications[notification_key] = update_notification_from_csv_row(db_note, new_notification)
#                 app.wgo_logger.debug(f'Notifications {notification_key} updateed from DB')
#             else:
#                 user_db.add_notification(new_notification)
#                 app.wgo_logger.debug(f'Notifications {notification_key} added to DB')

#         except Exception as err:
#             app.wgo_logger.debug(f'init_notifications err {err}  are in DB')


# TODO: Make sure not to use app as a parameter name to avoid implicit
# handling of global vs. function scope
def apply_notification_changes(application):
    #print(f'[apply_telemetry_notification_changes] Notes {i_tel_notes} ')
    i_tel_notes = application.hal.cfg['alert_items']
    for x in i_tel_notes:
        with application.n_lock:
            try:
                new_notification = notification_from_dict(i_tel_notes[x])
                notification_key = new_notification.notification_id
                # application.wgo_logger.debug(f'apply_notification_changes key {notification_key} ')
                application.event_notifications[notification_key] = new_notification  # First recording of the notification

                # now if the notifications is in the db read out current changes
                db_note = user_db.get_notification(notification_key)
                # application.wgo_logger.debug(f'[apply_notification_changes] {db_note} before update from DB')

                if db_note is not None:
                    application.event_notifications[notification_key] = update_notification_from_csv_row(db_note, new_notification)
                    # application.wgo_logger.debug(f'Notifications {notification_key} updated from Telemetry')
                else:
                    user_db.add_notification(new_notification)
                    # application.wgo_logger.debug(f'Notifications {notification_key} Telemetry added to DB')

            except Exception as err:
                application.wgo_logger.debug(f'[apply_telemetry_notification_changes] exception: {err}')


def is_over(i_note: Notification) -> tuple:
    # Check if this notifications has precedence over any others
    print('IN IS OVER', i_note)
    if 'precedence' in i_note.meta:
        print('IN OVER META', i_note.meta, type(i_note.meta))
        o_list = i_note.meta.get("precedence", {}).get("over", [])
        # NOTE: Checking that we have an item in the list
        over = bool(o_list)
        # if over is True:
        #     print(f"\n{i_note.header} HAS OVER {o_list}  \n")
        return over, o_list
    else:
        return False, []


def is_under(i_note: Notification) -> tuple:
    # Check if this notifications has precedence over any others
    print('[NOTIFICATION] Checking meta for presedence', i_note.meta)
    if 'precedence' in i_note.meta:
        u_list = i_note.meta.get("precedence", {}).get("under", [])
        under = bool(u_list)
        # if under is True:
        #     print(f"\n{i_note.header} HAS UNDER {u_list} \n")
        return under, u_list
    else:
        return False, []


# TODO: pass in App here
def check_note_active(i_note: Notification, i_current_value, i_condition_met):
    # TODO: Added global to be explicit
    global app
    _over = False
    o_list = []
    over_ridden = False

    print('[NOTIFICATION] Check_note_active run for ', i_current_value, i_condition_met)

    if i_condition_met is True:
        _over, o_list = is_under(i_note)
        if _over is True:
            # Check if the over riding event is active
            for temp in o_list:
                t_note = app.event_notifications[temp]
                # print(t_note)
                if t_note.active is True:
                    # Over ride the condition
                    i_condition_met = False
                    over_ridden = True
                    # print("Setting CONDITION over_ridden ")
                    break

    if i_condition_met is True:
        if i_note.active is True:
            app.wgo_logger.debug(
                f'{RVEvents(i_note.notification_id).name} notification is already active! {o_list}'
            )
            if i_note.notification_id in [RVEvents.REFRIGERATOR_OUT_OF_RANGE, RVEvents.FREEZER_OUT_OF_RANGE]:
                event = LogEvent(
                    timestamp=time.time(),
                    event=i_note.notification_id,
                    instance=i_note.instance,
                    value=i_current_value,
                    meta={
                        'active': i_note.active
                    }
                )
                user_db.add_event(event)
        else:
            app.wgo_logger.debug(
                f'Setting {RVEvents(i_note.notification_id).name} notification active!'
            )
            # TODO: Push the notification Here
            i_note.active = True
            i_note.ts_active = time.time()
            i_note.ts_dismissed = 0.0   # fresh notification clear the user dismissed time
            event = LogEvent(
                timestamp=time.time(),
                event=i_note.notification_id,
                instance=i_note.instance,
                value=i_current_value,
                meta={
                    'active':  i_note.active
                }
            )
            user_db.add_event(event)
            display_note = prepare_display_note(i_note)
            user_db.update_notification(i_note)
            alert_to_iot(i_note)
            if display_note is not None and display_note != {}:
                try:
                    with app.n_lock:
                        # Adding this check to only keep one copy of a message in the list.
                        is_present = any(item['id'] == i_note.notification_id for item in app.notifications)
                        # TODO: What is the actual error we want to handle ?
                        if is_present is False:
                            app.notifications.append(display_note)
                        else:
                            print(f"Notification {i_note.notification_id} already in the list.")
                except Exception as err:
                    print(err)
                    print('Check notifications exception:', display_note)
    else:
        print('WE ARE IN ELSE')
        if i_note.active is True:
            print('NOTE IS ACTIVE')
            i_note.active = False
            if over_ridden is False:
                event = LogEvent(
                    timestamp=time.time(),
                    event=i_note.notification_id,
                    instance=i_note.instance,
                    value=i_current_value,
                    meta={
                        'active': i_note.active
                    }
                )
                app.wgo_logger.debug(
                    f'{RVEvents( i_note.notification_id).name}  notification is active -> Now clearing!')
            else:
                app.wgo_logger.debug(
                    f'{RVEvents( i_note.notification_id).name}  notification is OVERRIDDEN -> Now clearing!')

            i_note.ts_cleared = time.time()
            user_db.update_notification(i_note)
            dismiss_note(app, i_note, user_dissmissed=False)

    # Now check conditions of under precedence items
    _under, u_list = is_over(i_note)
    if _under is True and i_note.active is True:
        for _id in u_list:
            t_note = app.event_notifications[_id]
            if t_note.active is True:
                t_note.active = False
                user_db.update_notification(t_note)
                dismiss_note(app, t_note, user_dissmissed=False)
                print(f"\n Note {RVEvents( i_note.notification_id).name}  DISMISSED over_ridden ")


async def check_time_notifications_expired(app):
    """Check any time based notfifications to see if they are expired."""
    # TODO: Check if the below needs to be awaitable
    for x in app.event_notifications:
        event_note = app.event_notifications[x]

        if not event_note.user_selected:
            continue

        if event_note.trigger_type == NotificationTrigger.TIME:
                check_note_active(
                    i_note=event_note,
                    i_current_value=EventValues.ON,
                    i_condition_met=bool(
                        event_note.trigger_value > datetime.now().timestamp())
                )


def check_all_notifications(i_event):
    '''
        EVENT timestamp=1676953401.0004811 event=<RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE: 8600> instance=2 value=99 meta=None
        ['Config', '__abstractmethods__', '__annotations__', '__class__', '__class_vars__', '__config__', '__custom_root_type__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__exclude_fields__', '__fields__', '__fields_set__', '__format__', '__ge__', '__get_validators__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__include_fields__', '__init__', '__init_subclass__', '__iter__', '__json_encoder__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__post_root_validators__', '__pre_root_validators__', '__pretty__', '__private_attributes__', '__reduce__', '__reduce_ex__', '__repr__', '__repr_args__', '__repr_name__', '__repr_str__', '__schema_cache__', '__setattr__', '__setstate__', '__signature__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__try_update_forward_refs__', '__validators__', '_abc_impl', '_calculate_keys', '_copy_and_set_values', '_decompose_class', '_enforce_dict_if_root', '_get_value', '_init_private_attributes', '_iter', 'construct', 'copy', 'dict', 'event', 'from_orm', 'instance', 'json', 'meta', 'parse_file', 'parse_obj', 'parse_raw', 'schema', 'schema_json', 'timestamp', 'update_forward_refs', 'validate', 'value']
        RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ['__class__', '__doc__', '__module__', 'as_integer_ratio', 'bit_length', 'conjugate', 'denominator', 'from_bytes', 'imag', 'name', 'numerator', 'real', 'to_bytes', 'value']
        Name WATER_TANK_FLUID_LEVEL_CHANGE
    '''
    # TODO: Added global to be explicit
    global app
    # Check if the Notification generates a Notification
    # And if the notifcation needs to be pushed or already has
    # TODO: Why do we iterate here ?
    for x in app.event_notifications:
        event_note = app.event_notifications[x]

        if not event_note.user_selected:
            continue
        else:
            check_notification(event_note, i_event)


def check_notification(event_note: Notification, i_event):
    '''Check notification.'''
    #print('[NOTIFICATION] Checking Notification', event_note)
    if i_event.event.value in event_note.trigger_events and \
            i_event.instance == event_note.instance:
        print('Its a hit, ', i_event.event.name , i_event)
        if event_note.trigger_type == NotificationTrigger.ONOFF:
            check_note_active(
                i_note=event_note,
                i_current_value=i_event.value,
                i_condition_met=True
            )  # ONOFF we want to see the toggle
        elif event_note.trigger_type == NotificationTrigger.ON:
            check_note_active(
                i_note=event_note,
                i_current_value=i_event.value,
                i_condition_met=bool(i_event.value == 1)
            )
        elif event_note.trigger_type == NotificationTrigger.OFF:
            check_note_active(
                i_note=event_note,
                i_current_value=i_event.value,
                i_condition_met=bool(i_event.value == 0)
            )
        elif event_note.trigger_type == NotificationTrigger.STRING_LIST:
            event_note.trigger_type(
                i_note=event_note,
                i_currentValue=i_event.value,
                i_condition_met=bool(
                    i_event.value in event_note.trigger_value)
            )
        elif event_note.trigger_type == NotificationTrigger.LOW:
            condition_met = bool(
                float(i_event.value) <= float(event_note.trigger_value[0]))
            if event_note.active is True:
                condition_met = bool(
                    float(i_event.value) <= float(event_note.trigger_value[1]))
            print('PRE CHECK NOTE ACTIVE')
            check_note_active(
                i_note=event_note,
                i_current_value=i_event.value,
                i_condition_met=condition_met
            )
            print('POST CHECK NOTE ACTIVE')
        elif event_note.trigger_type == NotificationTrigger.HIGH:
            condition_met = bool(
                float(i_event.value) >= float(event_note.trigger_value[0]))
            if event_note.active is True:
                condition_met = bool(
                    float(i_event.value) >= float(event_note.trigger_value[1]))
            check_note_active(
                i_note=event_note,
                i_current_value=i_event.value,
                i_condition_met=condition_met
            )
        elif event_note.trigger_type == NotificationTrigger.RANGE:
            # NOTE: Is this still current ?
            range = event_note.trigger_value
            check_note_active(
                i_note=event_note,
                i_current_value=i_event.value,
                i_condition_met=bool(float(i_event.value) < float(
                    range[0]) or float(i_event.value) > float(range[1]))
            )
        elif event_note.trigger_type == NotificationTrigger.TIME:
            check_note_active(
                i_note=event_note,
                i_current_value=i_event.value,
                i_condition_met=bool(
                    event_note.trigger_value > datetime.now().timestamp())
            )


# to set config to default
def reset_config_default():
    try:
        # not changing vin value
        vin_num = app.config["VIN"]
        default_config_dict["VIN"] = vin_num
        # setting all values to default
        app.config.update(default_config_dict)
    except Exception as err:
        print(err, 'Could not reset config to default values')
    return 'Default config values restored'


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(api_home.router)
app.taskScheduler = ScheduledFunctionManager(1)  # Holder for ScheduleManager Class object

started = False


@app.on_event("startup")
async def startup_event():
    '''Handle startup tasks.
    TODO: migrate to the new way of yielding after startup.'''
    global started, scheduletask
    app.wgo_logger.info('WGO Logger initialized - app startup')
    app.wgo_logger.setLevel(logging.DEBUG)
    app.wgo_logger.debug('Set logger to DEBUG')
    # Load config databases
    # Load previous state from storage

    # Add config handlers to the app for use in HAL
    app.save_config = save_config
    app.get_config = get_config
    app.reset_config_default = reset_config_default

    # Read Config
    floorplan, options = read_ui_config_file()
    print('FLOORPLAN:', floorplan)
    print('OPTIONCODES:', options, type(options))
    # Convert the string to a list
    options = options.split(',')

    init_floorplan(app, floorplan, options)

    # OTA updates will change the DB indirectly by calling
    # the init_telemetry with a new file, file does not need to be
    # specifically retained.
    # TODO: Still retain which was the last set telemetry in the future
    # S
    # Reset CAN service
    # TODO: Make this HTTPX

    try:
        await MAIN_CLIENT.put(CAN_RESET_URL, timeout=3)
    except Exception as e:
        print('[ERROR]', e)

    # Trigger VIN retrieval

    # Handler to send CAN messages in a central queue (Async hopefully)
    app.can_ignore_state = {}
    for key, value in CAN_IGNORE_MAP.items():
        app.can_ignore_state[key] = value
        if isinstance(value, type({})):
            # Set the value to be accepting incoming messages upon init
            app.can_ignore_state[key]['current_count'] = app.can_ignore_state[key]['ignore_count']

    app.can_send_runner = CANSendBackgroundRunner(
        {},
        app.can_ignore_state
    )
    await asyncio.create_task(app.can_send_runner.run_main())
    app.can_sender = app.can_send_runner.handler

    # Handler to perform HAL updates in a queue (async hopefully)
    app.can_hal_runner = CANAPIForwardBackgroundRunner({})
    await asyncio.create_task(app.can_hal_runner.run_main())
    app.hal_updater = app.can_hal_runner.handler

    app.hal.vehicle.handler.get_vin()

    if started is not True:
        started = True
        scheduletask = asyncio.create_task(app.taskScheduler.check_run())

        # Let system be the holder for the (ScheduleManager) object
    else:
        print("[ERROR] Startup event hit twice!")

    # NOTE: The below fails in several unit tests, bring that back and see if that is because of the option codes and floor plan not loading an electrical layer at all
    # print('[APP][INIT] CZONE HAL', app.hal.electrical.handler.czone.HAL)
    # print('[APP][INIT] CZONE HAL HAL loaded', hasattr(app.hal.electrical.handler.czone, 'HAL'))
    # print('[APP][INIT] CZONE HAL App loaded', hasattr(app.hal.electrical.handler.czone.HAL, 'app'))
    event_logger(
        LogEvent(
            timestamp=time.time(),
            event=RVEvents.SERVICE_START,
            instance=0,
            value=EventValues.MAIN_SERVICE,
            meta={
                'host': '',
                'port': ''
            }
        )
    )


@app.on_event('shutdown')
async def shutdown_event():
    # TODO: Save configs
    # Are there valid reasons to shut this down but not everything ?
    # Maybe a hot swap update ?
    print('Shutting down MAIN service')
    app.taskScheduler.running = False
    global scheduletask
    scheduletask.cancel()
    app.can_send_runner.stop()
    app.can_hal_runner.stop()

    try:
        await scheduletask
    except asyncio.CancelledError:
        print("Schedule Task cancellation was confirmed")

    try:
        event_logger(
            LogEvent(
                event=RVEvents.SERVICE_STOP,
                instance=0,
                value=EventValues.MAIN_SERVICE
            )
        )
    except:
        pass # maybe we removed the db
    shutdown_main_system()


# Only load test harness code if set
# TODO: Remove 'True' assignment if env variable does not exist
if os.getenv('UI_TEST_HARNESS', 'True') == 'True':
    app.include_router(testing_harness.router)
    # app.state = json.load(open('test_state.json', 'r'))
    app.state = {}
else:
    app.state = {}


def fake_logger(event):
    pass


# def get_config_safe(key, sep='.'):
#     '''Get config items.
#     Try local app config first, then hit DB, then return default if available.

#     Raise KeyError with details if none of these succeeded'''
#     # Check if sep in key
#     # If yes
#         #
#     pass


# def set_config_safe(key, value, sep='.'):
#     '''Sets a config item and stores to the config database table.'''
#     pass
#     # Check if sep in key
#     # If so

IotBaseUrl = "http://localhost:" + str(_env.iot_service_port)


def check_iot(i_event):
    '''Check an event needs to be emitted to IoT for twin and telemetry.'''
    with app.iot_events_lock:
        with app.twin_events_lock:
            if i_event.event.value in app.iot_events or i_event.event.value in app.twin_events :
                print(f'[IOT] IOT found {json.dumps(i_event, default=vars)}')
                event_to_iot(i_event)
            # Enable this else print to look for missing twin data
            else:
                print(f'[IOT] Event not configured to send to IOT: {i_event}')
    return


def check_bt_twin(i_event):
    '''Checkif we need to send the event to blueooth devices'''
    with app.twin_events_lock:
        if i_event.event.value in app.twin_events:
            # print('BT twin found', json.dumps(i_event, default=vars))
            # app.wgo_logger.debug(
            #    f'BT twin found {json.dumps(i_event, default=vars)}')
            event_to_bt(i_event)
        else:
            app.wgo_logger.debug(f'Bluetooth event not reported: {json.dumps(i_event, default=vars)}')
    return


def event_logger_raw(i_timestamp, i_event, i_instance, i_value, i_log_extra=None):
    '''Used for raw external events coming in via API.'''
    n_event = LogEvent(
        timestamp=i_timestamp,
        event=RVEvents(i_event),
        instance=i_instance,
        value=i_value
    )
    event_logger(event=n_event, log_extra=i_log_extra)


def event_logger(event, log_extra=None, force=False):
    '''This is the main Event emitter for all property changes etc.'''
    # Write to event database
    THRESHOLDS = {
        # 'CLIMATE_ZONE_SET_TEMP_HEAT_CHANGE': 2,
    }
    update = not app.updateNow.is_expired()  # False unless we want all to go through
    if update is True:
        force = True

    # Lock to ensure thread safe function
    # print('Running Event Logger in app for', event)
    with app.eventLock:
        event_key = f'{event.event.name}_{event.instance}'
        # print('---> Event Key: ', event_key, event.value)
        if event_key in app.event_states:
            previous_value = app.event_states.get(event_key).value
            if (event.value == previous_value) and (force is False):
                # Ignore
                pass
            else:
                # TODO: Check against a table if this is an item for threshold checking
                threshold = THRESHOLDS.get(event.event.name)
                if threshold is None:
                    update = True
                else:
                    if event.value >= (previous_value + threshold) or event.value < (previous_value - threshold):
                        update = True
                    else:
                        print(f'Ignoring Event as not in threshold: {threshold}', event, previous_value)
                        pass
        else:
            update = True

        if update is True:
            if force is False:
                # We only want to add an event if it is different,
                # force is used to review notifications in the same manner as on change
                user_db.add_event(event)
                # print('[EVENTLOG] UPDATED Event Value', event)
            try:
                # print('Notification check for event', event)
                check_all_notifications(i_event=event)
            except Exception as e:
                print(event)
                print("[ERROR] ^^^^^^^%%%%%%%%%%%%%^^^^^^^^ EXCEPTION:", e, "\n\n")

            app.event_states[event_key] = event

            check_iot(event)
            # check_bt_twin(event)  # Currently not doing anything

            if log_extra is not None:
                print(f"log_extra: {log_extra}")

    # print('Event logger done', update)


def get_coach_events(event_key=None):
    '''Get the latest from the event database'''
    result = user_db.get_coach_events(event_key)

    # Convert results to a list of dictionaries
    columns = [desc[0] for desc in result.description]
    data = [dict(zip(columns, row)) for row in result]

    return data


def check_ota_lockout():
    '''Check battery is high enough etc'''
    result = False  # False is not locked out
    battery = app.hal.energy.handler.battery_management[1]
    # TODO: Yes, we need standard handling for all missing components reading
    # TODO: Should we handle missing voltages here or somewhere else ?
    # TODO: Should the default for bm values be None
    if battery.state.soc is not None: # or battery.state.vltg is not None:
        soc_low = float(battery.state.soc) < float(OTA_BATTERY_SOC_LOW_THRESHOLD)
        # voltage_low = battery.state.vltg < OTA_BATTERY_VOLTAGE_LOW_THRESHOLD
        # check is shore power connected then lower battery threshhold

        # TODO: verify how we determine shore power the function below not working
        #if app.hal.energy.handler.get_shore_power_state()
    else:
        soc_low = EventValues.OFF
        voltage_low = EventValues.OFF

    if soc_low is True:
        result = True

    print(f"****   Battery SOC {battery.state.soc} Voltage { battery.state.vltg}")
    return result

# Define the time here so the function can update its
app.update_version = "6.22."  # TODO: Fill from iot
app.update_available = False  # TODO: Fill from IOT


app.previous_state = app.state
app.can_states = {}
app.can_counter = {
    # Nred to put a starting point to update duration
    'log_start': time.time(),
    'log_duration': 0.0,
    'total_msg_counter': 0
}
# can_diagnostics shall hold data receveived from ther can bus
app.can_diagnostics = {
    'last_ran': None,
    'status': None,
    'devices': {}
}
app.system_diagnostics = {
    'last_ran': None,
    'status': None,
    'devices': {}
}
app.event_states = {}
# Let the IOT know startup happened so it can load other m2 events
app.iot_events = [RVEvents.SERVICE_START, ]
app.twin_events = []
app.iot_events_lock = Lock()
app.twin_events_lock = Lock()
app.eventLock = Lock()
# app.event_logger = fake_logger
app.event_logger = event_logger
app.__version__ = VERSION
app.__build_time__ = '1979/10/11 04:22 AM'
app.get_coach_events = get_coach_events
app.check_ota_lockout = check_ota_lockout
app.about_notes = read_current_version_about()
app.update_notes = read_about_from_bld_directory()
app.check_note_active = check_note_active
app.check_time_notifications_expired = check_time_notifications_expired


@app.get('/version')
async def get_version(request: Request):
    return app.__version__


@app.get('/config')
async def get_all_config(request: Request):
    return app.config


@app.get('/api')
async def get_api(request: Request):
    return {
        "lighting": "/api/lighting",
        "watersystems": "/api/watersystems",
        'electrical': "/api/electrical",
        'climate': "/api/climate",
        'energy': "/api/energy",
        'vehicle': "/api/vehicle",
        'system': '/api/system'
    }


@app.put('/event_log')
async def put_logging_event(request: Request, i_event: LogEvent):
    ''' External API to log an event to DB.'''
    # TODO: Perform a basic sanity check
    # TODO: Check if comes from an allowed service
    # Expecting
    # CAN Service
    # IOT Service - OTA etc
    # System Service
    # - Memory / CPU / Procs running
    # run in a thread to not stop caller

    print(f"[MAIN][EVENT_LOG] Received Logged out side event {i_event}\n\n")

    # TODO: Check for other methods - this could create many threads.
    threading.Thread(
        target=event_logger_raw,
        args=(
            i_event.timestamp,
            i_event.event.value,
            i_event.instance,
            i_event.value)
    ).start()
    print(f'[MAIN][EVENT_LOG] Logged out side event')
    return {'result': 'Success'}


@app.get('/snapshot')
async def get_state_snapshot(request: Request):
    '''Test endpoint to query the current state to monitor for changes or
    validate current internal state.'''
    states = deepcopy(request.app.event_states)
    result = {}

    for key in sorted(states.keys()):
        state = states.get(key)
        if isinstance(state.value, EventValues):
            # Add the representation for better readability of the number
            state.value = state.value.name
        # Else the value is accepted as is and not converted
        state.event = state.event.name
        result[key] = state

    return result


@app.get('/snapshot2')
async def get_state_snapshot_new(request: Request):
    '''Test endpoint to query the current state to monitor for changes or
    validate current internal state.'''
    states = deepcopy(request.app.event_states)
    result = {}

    for key in sorted(states.keys()):
        state = states.get(key)
        if isinstance(state.value, EventValues):
            # Add the representation for better readability of the number
            state.value = f'{state.value} ({state.value.name})'
        # Else the value is accepted as is and not converted
        state.event = state.event.name
        result[key] = state

    return result


@app.get('/event_count')
async def get_event_total():
    count_result = user_db.event_count()
    return count_result


class TimeRange(BaseModel):
    start_ts: Optional[float]
    end_ts: Optional[float]


@app.get('/all_notifications')
async def get_all_notifications():
    all_notifications = []
    # print(app.event_notifications)
    try:
        global app
        all_notifications = list(app.event_notifications.values())
        all_notifications = sorted(
            all_notifications[:],
            key=lambda x: x.priority
        )
    except Exception as err:
        print('Get all notifications exception', err)
    return all_notifications


# TODO: Consider comment in https://github.com/tiangolo/fastapi/issues/1277
# TODO: Use a generator that uses the cursor to yield a row towards downloading
@app.get('/event_dump')
async def get_event_dump(format='csv', time_range: TimeRange = Depends()):

    # return user_db.fetch_many(100,0)
    start_time = 0.0
    end_time = 0.0
    if time_range.start_ts != None:
        start_time = time_range.start_ts
    if time_range.end_ts != None:
        end_time = time_range.end_ts

    app.wgo_logger.debug('Start ' + str(start_time) + ' End ' + str(end_time))
    # return user_db.get_events(start_time, end_time).fetchone()

    if format == 'csv':
        header = ('id', 'timestamp', 'event', 'event_name',
                  'instance', 'value', 'value_type', 'meta')
        new_csvfile = StringIO()
        wr = csv.DictWriter(new_csvfile, fieldnames=header)
        wr.writeheader()

        cur = user_db.get_events(start_time, end_time)

        while True:
            row = cur.fetchone()
            if not row:
                break

            value = row[5]
            if row[4] == 1:
                value_type = EventValues(row[5])
            elif row[4] == 2:
                value_type = str(type(value))
            else:
                value_type = 'unspecified'

            full_row = {
                'id': row[0],
                'timestamp': row[1],
                'event': row[2],
                'event_name': RVEvents(row[2]),
                'instance': row[3],
                'value': value,
                'value_type': value_type,
                'meta': row[6]
            }
            wr.writerow(full_row)

        new_csvfile.seek(0)

        return StreamingResponse(
            new_csvfile,
            media_type="text/csv",
            headers={'Content-Disposition': 'filename=event_download.csv'}
        )
    elif format == 'json':
        cur = user_db.get_events(start_time, end_time)

        result = []
        cnt = 0
        while True:
            row = cur.fetchone()
            if not row:
                break
            cnt = cnt + 1
            value = row[5]
            if row[4] == 1:
                value_type = EventValues(row[5])
            elif row[4] == 2:
                value_type = str(type(value))
            else:
                value_type = 'unspecified'

            event_row = {
                'id': row[0],
                'timestamp': row[1],
                'event': row[2],
                'event_name': RVEvents(row[2]),
                'instance': row[3],
                'value': value,
                'value_type': value_type
            }
            print('Row', cnt, event_row)
            result.append(event_row)
        # id,timestamp,event,event_name,instance,value,value_type  dropped for now ->,meta
        return result

    else:
        raise HTTPException(422, f'Unknown data format: {format}')


@app.put('/drop_events')
async def put_drop_older(request: Request, time_stamp: float):
    '''Drop events that are older than X. None or 0 will drop older than 2 weeks.'''
    if time_stamp is None or time_stamp == 0.0:
        '''Drop older than two weeks events.'''
        time_stamp = datetime.now() - timedelta(weeks=2)
    user_db.drop_events(time_stamp)
    return {"result": "success"}


@app.get('/')
async def host_index():
    '''Responds with index for basepath of /'''
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))


@app.get('/iot_events')
async def get_iot_list(request: Request):
    '''Return list of IoT events already configured.'''
    return request.app.iot_events


@app.put('/iot_events')
async def put_iot_list(request: Request, i_items: List[int]):
    '''Add IoT Telemetry events that need to be reported.'''
    with request.app.iot_events_lock:
        request.app.iot_events = i_items
    print("[IOT] Updated IOT list received.", i_items)
    return {"result": "success"}


@app.put('/all_iot_events')
async def send_all_iot_events(request: Request):
    '''Trigger a send of all configured IoT events ???'''
    # TODO: Check if this function is called
    # TODO: Check if this is needed at all
    request.app.updateNow.increment()
    request.app.hal.updateStates()
    return {"result": "success"}


@app.put('/twin_events')
async def put_twin_list(request: Request, i_items: List[int]):
    '''Add IoT Twin events that need to be reported.'''
    with request.app.twin_events_lock:
        request.app.twin_events = i_items

    # print("Updated Twin list received.")
    # app.wgo_logger.debug(f'Updated Twin list received. {i_items}')
    return {"result": "success"}


@app.put('/ota_status')
async def set_ota_status(request: Request, ota_state: dict):
    '''Receive OTA status from IoT.'''
    request.app.ota_state = ota_state
    print(f'ota_status received: {ota_state}')
    return {"result": "success"}


@app.get('/ota_status')
async def get_ota_status(request: Request):
    '''Show OTA status as received from IoT.'''
    return request.app.ota_state


@app.put('/device_id')
async def put_device_id(request: Request, _id: str):
    '''Receive device ID from IoT.'''
    # TODO: Review if this is actively used and needed or folded into the bigger API call(s).
    request.app.__version__['device_id'] = _id
    # print("Updated device_id received.")
    return {"result": "success"}


@app.put('/motd')
async def update_motd(request: Request, motd: Motd):
    '''Allows receipts of a device specific
    Message of the day, which display if no other
    alerts supersede it.'''
    request.app.config['motd'] = motd
    return request.app.config['motd']


# TODO: Refine logic to also check which request is coming in
# TODO: Check if this could be useful in the future or otherwise remove

# async def verify_source(request: Request):
#     source = request.headers.get('source')
#     # Convert url to feature and decide if OK or not
#     if source.lower() != 'ui':
#         raise HTTPException(status_code=400, detail="Invalid source")
#     return source


@app.get('/cfg/{cfg_key}')
async def get_cfg(request: Request, cfg_key):
    '''Endpoint to retrieve a specific config item from DB.'''
    return get_config(cfg_key)


@app.put('/cfg/{cfg_key}')
async def set_cfg(request: Request, cfg_key, cfg_value):
    '''Endpoint to set a specific config item to the DB.'''
    return save_config(cfg_key, cfg_value)


@app.get('/coach_events')
async def get_coach_event_list(request: Request):
    '''Endpoint to retrieve list of all coach events from the DB'''
    # TODO: Check if this should be moved to e.g. test harness or a debug router.
    return request.app.get_coach_events()


@app.put('/pair_device_status', response_model=BtStateChange)
async def put_pair_device(request: Request, state: int):
    '''Not sure what this does.'''
    # TODO: Figure out if this is useful for anything
    try:
        request.app.config[
            'BluetoothSettings']['PairingStatus']['state'] = state
        request.app.config[
            'BluetoothSettings']['PairingStatus']['timeStamp'] = datetime.now(
        ).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print('Connection status unkown', e)

    return state


@app.get('/ota_lockout')
async def get_ota_lockout(request: Request):
    '''Check if OTA is locked out to be performed.
    Used to prevent updates from happening while on low battery power or other
    unsafe conditions.'''
    return request.app.check_ota_lockout()


@app.get('/can/ignore_state')
async def get_can_ignore_state(request: Request):
    '''Get the list of message we currently ignore when they come in.
    Ignoring a can state is used to prevent flip-flopping when an old
    state is received while a new desired one is being sent out.'''
    return request.app.can_ignore_state


app.mount(
    '/',
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="base_static"
)


if __name__ == '__main__':
    import sys
    try:
        MAIN_SERVICE_PORT = int(sys.argv[1])
    except IndexError:
        # User default defined on top
        pass

    uvicorn.run(
        'wgo_main_service:app',
        host=BIND_ADDRESS,
        port=int(MAIN_SERVICE_PORT),
        reload=DEBUG == 1,
        # reload=1,
        log_level="error",
        workers=1,
        # limit_concurrency=5
    )
