'''
Winnebago CAN Service

Reads CAN messages, decodes, keeps state of all messages and their changes as well reporting
thus changes to the main service for applying business logic.
'''

__author__ = 'Dominique Parolin'

# Version for the service is in the main py file.
__version__ = "1.0.3"

import asyncio
import json
import os
import threading
import time
import logging
import platform
from collections import deque
# TODO: We should check if we want to replace with built in urllib ?
import requests
import uvicorn
from common_libs import environment
from common_libs.system.scheduled_function import ScheduledFunction
from common_libs.system.schedule_manager import ScheduledFunctionManager
from common_libs.clients import CAN_CLIENT

from fastapi import (
    FastAPI,
    Request
)
from fastapi.middleware.cors import CORSMiddleware

from can_service.routers import (
    testing,
)

from can_service.can_helper import CanHandler

try:
    from setproctitle import setproctitle
    setproctitle('WGO-CAN-Service')
except ImportError:
    pass


LOG_MAX_FILE_SIZE = 20000
LOG_BACKUP_FILE_CNT = 1

_env = environment()

logger = logging.getLogger(__name__)
from logging.handlers import RotatingFileHandler

logger.setLevel(logging.DEBUG)
bulk_handler = RotatingFileHandler(
      _env.log_file_path('can_service.log'),
      'a+',
      maxBytes=LOG_MAX_FILE_SIZE,
      backupCount=LOG_BACKUP_FILE_CNT
    )
# logHandler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# logHandler.setFormatter(formatter)
bulk_handler.setFormatter(formatter)
logger.addHandler(bulk_handler)
# logger.addHandler(logHandler)


origins = [
    "https://localhost",
    "https://localhost:8000",
    "https://localhost:3000",
    "https://127.0.0.1:8000",
    "*"
]

MAIN_SERVICE_PORT = _env.main_service_port
CAN_SERVICE_PORT = _env.can_service_port
WGO_MAIN_HOST = _env.main_host_uri
BIND_ADDRESS = _env.bind_address


__version__ = os.environ.get('WGO_CAN_VERSION', 'NOT_SET')

# TODO: Move to config file ?
CAN_CONFIG = {
    'bitrate': 250000,
    'channel': 'canb0s0',
    'logger': logger
}

API_CONFIG = {

}


DEFAULT_SUPPORTED_MSG = {
    "fluid_level": "watersystems",
    "lighting_broadcast": "lighting",
    "heartbeat": "electrical",
    "rvswitch": "electrical",
    "rvoutput": "electrical",
    "roof_fan_status_1": "climate",
    "ambient_temperature": "climate",
    "thermostat_ambient_status": "climate",
    "dc_source_status_1": "energy",
    "dc_source_status_2": "energy",
    "dc_source_status_3": "energy",
    "battery_status": "energy",
    "prop_bms_status_6": "energy",
    "prop_module_status_1": "energy",
    "inverter_ac_status_1": "energy",
    "inverter_status": "energy",
    "charger_ac_status_1": "energy",
    "charger_ac_status_2": "energy",
    "charger_status": "energy",
    "charger_status_2": "energy",
    "charger_configuration_status": "energy",
    "charger_configuration_status_2": "energy",
    "solar_controller_status": "energy",
    "vehicle_status_1": "vehicle",
    "vehicle_status_2": "vehicle",
    "state_of_charge": "vehicle",
    "dc_charging_state": "vehicle",
    "pb_park_brake": "vehicle",
    "tr_transmission_range": "vehicle",
    "odo_odometer": "vehicle",
    "aat_ambient_air_temperature": "vehicle",
    "vin_response": "vehicle",
    "dc_dimmer_command_2": "electrical",
    "waterheater_status": "watersystems",
    "waterheater_status_2": "watersystems",
    "prop_tm620_config_status":"watersystems",
    "awning_status": "movables"
}


async def emit_can_stale_report(report):
    '''Send CAN staleness report to UI/State Service.'''
    # TODO: Can we request the HAL overview/mapping from the MAIN Service ?
    # Map events to a subsystem and hit a more specific endpoint
    # e.g. Lighting, Watersystems etc.
    # Remove non serializable data as applicable, might happen in the decoded messages
    # to_str = {k: str(v) for (k, v) in report.items()}
    # Null out the raw message, not desired

    # print('REPORT', json.dumps(report, indent=4))

    try:
        response = await CAN_CLIENT.put(
            f'{_env.main_host_uri}:{MAIN_SERVICE_PORT}/api/can/stale',
            json=report,
            timeout=2.0,
        )
    except requests.exceptions.ConnectionError as err:
        # print(err)
        return {
            'result': 'ERROR',
            'message': err
        }
    except requests.exceptions.ReadTimeout as err:
        # print(err)
        return {
            'result': 'ERROR',
            'message': err
        }
    except Exception as err:
        print('ERROR sending stale report', err)
        raise

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as err:
        print('!'*80)
        print('ERROR', err)
        print(response)
        print('!'*80)

        return {
            'result': 'ERROR',
            'message': err
        }


async def stale_can_checker():
    '''Execute stale checker from app scope.'''
    print('Running stale_can_checker')
    _ = await runner.handler.stale_msg_check()
    # We will always emit this report for updates to main
    await emit_can_stale_report(runner.handler.inventory)
    # else:
    #     print('Result OK')


def emit_can_event(result):
    '''Send CAN event to UI/State Service.'''
    # TODO: Can we request the HAL overview/mapping from the MAIN Service ?
    # Map events to a subsystem and hit a more specific endpoint
    # e.g. Lighting, Watersystems etc.
    # Remove non serializable data as applicable, might happen in the decoded messages
    to_str = {k: str(v) for (k, v) in result.items()}
    # Null out the raw message, not desired
    result['msg'] = None

    system = to_str.get("msg_name", "default").lower()

    try:
        response = requests.put(
            f'{_env.main_host_uri}:{MAIN_SERVICE_PORT}/api/can/event/{system}',
            json=to_str,
            timeout=1.0,
        )
    except requests.exceptions.ConnectionError as err:
        # print(err)
        return {
            'result': 'ERROR',
            'message': err
        }
    except requests.exceptions.ReadTimeout as err:
        # print(err)
        return {
            'result': 'ERROR',
            'message': err
        }

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as err:
        print('!'*80)
        print('ERROR', err)
        print(response)
        print('!'*80)

        return {
            'result': 'ERROR',
            'message': err
        }


api_can_queue = deque()


def queue_can_result(result, func=emit_can_event):
    '''Intermediate function to add a new message to the emit queue.

    This will receive the message and will allow the API sender thread to pick these up and send them out.'''
    global api_can_queue

    # Could we check the priority of the message and appendleft ?

    api_can_queue.append((func, result))
    print('Queue length', len(api_can_queue))
    return len(api_can_queue)


class CANBackgroundRunner:
    def __init__(self, can_cfg: dict):
        self.config = can_cfg
        # TODO: Check if it helps to pass the app
        # Would need to create the runner on Start the rather than globally
        self.handler = CanHandler(self.config, )
        self.api_sender = APIHandler(self.config, )
        # self.th = threading.Thread(target=self.handler.read_loop, args=[emit_can_event,])
        self.th = threading.Thread(
            target=self.handler.read_loop,
            args=[queue_can_result,]
        )
        self.sender_thread = threading.Thread(
            target=self.api_sender.run_api_send_loop,
            args=[]
        )

    async def run_main(self):
        self.th.start()
        self.sender_thread.start()
        print('CAN Reading Loop started')

    async def stop(self):
        self.handler.running = False
        self.api_sender.running = False
        self.th.join()
        self.sender_thread.join()


class APIHandler:
    def __init__(self, cfg, queue=None):
        global api_can_queue
        if queue is None:
            self.queue = api_can_queue
        else:
            self.queue = queue

        self.running = True
        print('[CAN][API] API Handler initialized')

    def run_api_send_loop(self):
        while self.running is True:
            try:
                next_msg = self.queue.popleft()
            except IndexError:
                time.sleep(0.1)
                continue

            print(next_msg)
            # Format is function and args
            result = next_msg[0](next_msg[1])
            if result.get('result') == 'ERROR':
                # Null out the state to retry
                print('Error, ignoring CAN state', result)


class APIBackgroundSender:
    def __init__(self, cfg: dict):
        self.config = cfg
        # TODO: Check if it helps to pass the app
        # Would need to create the runner on Start the rather than globally
        self.api_queue = deque()
        self.handler = APIHandler(self.config, self.api_queue)
        self.th = threading.Thread(target=self.handler.run_api_send_loop)

    async def run_main(self):
        self.th.start()
        print('API Sending Loop started')

    async def stop(self):
        self.handler.running = False
        self.th.join()


api_sender = APIBackgroundSender(API_CONFIG)
runner = CANBackgroundRunner(CAN_CONFIG)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.taskScheduler = ScheduledFunctionManager()  # Holder for ScheduleManager Class object


if os.getenv('UI_TEST_HARNESS', 'True') == 'True':
    app.include_router(testing.router)
    app.state = json.load(open('can_test_state.json', 'r'))
else:
    app.state = {}


@app.get('/status')
async def status():
    return {
        'Status': 'OK',
        'Version': 'NA',
        'Modules': [],
        'ProcId': 'NA',
        'SystemTime': time.time()
    }


@app.get('/state')
async def get_state():
    return app.state


@app.put('/state/reset')
async def reset_state():
    '''Reset the state, e.g. when UI service restarts to send all data again regardless of change.'''
    runner.handler.reset_state()


@app.get('/stats')
async def get_stats():
    return runner.handler.msg_statistics


@app.get('/filter')
async def get_can_filter(request: Request):
    '''Get the current CAN filter.'''
    result = [hex(x) for x in runner.handler.MSG_NEEDED]
    return result


@app.put('/filter')
@app.put('/can/filter')
async def set_can_filter(request: Request, canfilter: dict):
    '''Set a filter to the given messages, so we do not decode them all
    if no one is consuming them.'''
    runner.handler.set_filter(canfilter)
    result = [hex(x) for x in runner.handler.MSG_NEEDED]
    return result


@app.get("/can_ui")
@app.get("/can/ui")
async def can_ui():
    myKeys = list(runner.handler.state.keys())  # Is keys() not already a list ?
    myKeys.sort(reverse=True)
    sorted_dict = {i: runner.handler.state[i] for i in myKeys}  # There is a sorted dict we could use right away
    # Why not return an object and iterate over the keys in the frontend ? There are no duplicate messages, right ?
    can_array = [
        {
            'name': str(k),
            'instances': list(v.keys()), k: v,
        } for k, v in sorted_dict.items()
    ]

    return can_array


@app.get("/can/inventory")
async def can_inventory():
    result = {}
    for source, details in runner.handler.inventory.items():
        source_key = f'{source:02X}'
        result[source_key] = {}
        for key, value in details.items():
            if key == 'msgs':
                result[source_key][key] = {}
                # Iterate
                for pgn, msg in value.items():
                    pgn_key = f'{pgn:05X}'
                    result[source_key][key][pgn_key] = msg
            else:
                result[source_key][key] = value

    return result


@app.on_event("startup")
async def startup_event():
    global scheduletask

    asyncio.create_task(runner.run_main())
    # Fetch CAN list form main service
    CAN_LIST_URL = f'{WGO_MAIN_HOST}:{MAIN_SERVICE_PORT}/api/system/can/filter'
    print('[CANINIT] CAN LIST URL', CAN_LIST_URL)
    retries = 0
    can_filter = None
    while True:
        try:
            can_filter = await CAN_CLIENT.get(CAN_LIST_URL, timeout=5)
        except Exception as err:
            print('[CANINIT] Error fetching CAN filter list', retries, err)
            retries += 1
            await asyncio.sleep(5)
            continue

        break

    # if can_filter is None:
    #     print('[CANINIT] Cannot set can filter, using default')
    #     can_filter = DEFAULT_SUPPORTED_MSG
    # else:
    can_filter = can_filter.json()

    print('[CANINIT] CAN_FILTER', can_filter)

    runner.handler.set_filter(can_filter)

    scheduletask = asyncio.create_task(app.taskScheduler.check_run())
    # Let system be the holder for the (ScheduleManager) object

    staleChecker = ScheduledFunction(
        function=stale_can_checker,
        args=(),
        wait_seconds=10,  # Perodic rate, allows DM_RV to be used
        oneshot=False
    )
    print('Adding CAN stale checker to Tasks')
    app.taskScheduler.add_timed_function(staleChecker)


@app.on_event('shutdown')
async def shutdown_event():
    global scheduletask
    scheduletask.cancel()
    await runner.stop()

    try:
        await scheduletask
    except asyncio.CancelledError:
        print("Schedule Task cancellation was confirmed")


if __name__ == '__main__':
    uvicorn.run(
        'wgo_can_service:app',
        host=BIND_ADDRESS,
        port=int(CAN_SERVICE_PORT),
        log_level='debug',
        # reload=True,
        workers=1
    )
