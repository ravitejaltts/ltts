'''
Winnebago BT Service

Provide API control over BT system, bring up GATT interface and dispatch messages to and from the main service
'''

__author__ = 'Dominique Parolin and others'

# Version for the service is in the main py file.
__version__ = "1.0.0"

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
import platform
import sys
import threading
import time
import signal

from fastapi import (
    FastAPI,
    Request
)
import uvicorn

from common_libs import environment
from common_libs.clients import BT_CLIENT
# TODO: Check if we want to replace with built in urllib ?

from bt_service.routers import (
    testing,
    ble_api
)

from bt_service.gatt.app import GATTHandler

try:
    from setproctitle import setproctitle
    setproctitle('WGO-BT-Service')
except ImportError:
    pass

LOG_MAX_FILE_SIZE = 20000
LOG_BACKUP_FILE_CNT = 1
uvicorn_logger = logging.getLogger("uvicorn")

_env = environment()

uvicorn_logger.setLevel(logging.DEBUG)
bulk_handler = RotatingFileHandler(
      _env.log_file_path('bt_service.log'),
      'a+',
      maxBytes=LOG_MAX_FILE_SIZE,
      backupCount=LOG_BACKUP_FILE_CNT
    )
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
bulk_handler.setFormatter(formatter)
uvicorn_logger.addHandler(bulk_handler)

MAIN_SERVICE_PORT = _env.main_service_port
WGO_MAIN_HOST = _env.main_host_uri

BT_SERVICE_PORT = _env.bluetooth_service_port
IOT_SERVICE_PORT = _env.iot_service_port
BIND_ADDRESS = _env.bind_address

VIN_API = f'{_env.main_host_uri}:{_env.main_service_port}/api/vehicle/vin'
VERSION_API = f'{_env.main_host_uri}:{_env.main_service_port}/version'
SERVICE_RESTART_API = f'{_env.main_host_uri}:{_env.main_service_port}/api/system/service/bluetooth/restart'
DEVICEID_API = f'{_env.main_host_uri}:{_env.iot_service_port}/device_id'

# TODO: Move to config file ?
BT_CONFIG = {}


class BTBackgroundRunner:
    logger = uvicorn_logger

    def __init__(self, cfg: dict):
        self.config = cfg
        print(f"BTbackground config {self.config}")
        self.logger.debug(f"BTbackground config {self.config}")
        # TODO: Check if it helps to pass the app
        # Would need to create the runner on Start the rather than globally
        self.handler = GATTHandler(config=self.config, logger=self.logger)
        self.th = threading.Thread(target=self.handler.main_loop, args=[])

    async def run_main(self):
        self.th.start()
        # self.logger.debug('VIN Response run main', self.config['VIN'])
        # time.sleep(5)
        if self.handler.is_advertising is False:
            self.logger.debug('error in advertising - not set yet')

    async def stop(self):
        self.handler.running = False
        try:
            self.logger.debug('BT Background Stop Called')
            self.handler.unregister_advertisement()
        except AttributeError as err:
            self.logger.debug(f'Continue shutdown: {err}')

        self.handler.mainloop.quit()

        # self.queue_thread.join()
        self.th.join()

        try:
            await BT_CLIENT.put(SERVICE_RESTART_API, timeout=5)
        except Exception as err:
            self.logger.error(f'Cannot restart service: {err}')


# Setting global runner variable
runner = None

app = FastAPI()
app.include_router(ble_api.router)

if os.getenv('UI_TEST_HARNESS', 'True') == 'True':
    # app.include_router(testing.router)
    app.state = {}
else:
    app.state = {}


app.state['VIN'] = None
app.runner = None


@app.get('/status')
async def status(request: Request):
    global BT_CONFIG, runner
    advertising = runner.handler.is_advertising
    print('[BLUETOOTH][STATUS]', runner.handler.app.services)
    last_pairing_status = None
    for service in runner.handler.app.services:
        if 'BleSecurityService' in service.__str__():
            print('[BLUETOOTH][STATUS][SECURITY]', service)
            last_pairing_status = str(service.last_pairing_status)

    return {
        'Name': 'BT Service',
        'Status': 'OK',     # TODO: Do not hardcode
        'advertising': advertising,
        'Version': __version__,
        'Modules': [],
        'ProcId': 'NA',
        'SystemTime': time.time(),
        'DeviceId': BT_CONFIG.get('DEVICE_ID'),
        'connectedDevices': [],     # Currently connected devices
        'knownDevice': [],          # Known and approved devices
        'blockedDevices': [],       # Blocked through failure of authentication
        'lastPairingStatus': last_pairing_status
    }


@app.get('/restart')
async def restart_service(request: Request):
    await runner.stop()
    os.kill(os.getpid(), signal.SIGTERM)


@app.get('/state')
async def get_state():
    return app.state


@app.put('/vin')
async def set_vin(request: Request, vin: str):
    current_vin = request.app.state.get('VIN')
    # TODO: Check VIN for sanity
    # Check if VIN is different (other than None)
    request.app.state['VIN'] = vin
    # Change vin in BTHandler for use in advertising
    return {
        'status': 'OK',
        'msg': 'VIN updated'
    }


@app.get('/vin')
async def get_vin(request: Request):
    return request.app.state.get('VIN')


@app.put('/reset')
async def reset_bt(request: Request):
    '''Reset BT service.'''
    await restart_service(request)
    return


@app.get('/advertise')
async def get_advertisement(request: Request):
    # request.app.runner.handler.
    bt_runner = request.app.runner
    return {
        'is_advertising': bt_runner.handler.advertisement.is_advertising
    }


@app.put('/advertise')
async def set_advertisement(request: Request, body: dict):
    # request.app.runner.handler.
    onOff = body.get('onOff')
    bt_runner = request.app.runner
    if onOff == 0:
        result = bt_runner.handler.unregister_advertisement()
    elif onOff == 1:
        result = bt_runner.handler.register_advertisement()

    return result


@app.put('/onoff')
async def set_bt_onoff(request: Request, body: dict):
    return await set_advertisement(request, body)


@app.on_event("startup")
async def startup_event():
    global runner
    config = None
    while config is None:
        try:
            version_response = await BT_CLIENT.get(VERSION_API, timeout=5)
        except Exception as err:
            print(err)
            time.sleep(2)
            continue

        config = version_response.json()
        print('Version_response', config)
        uvicorn_logger.debug(f'Version_response {config}')
        break

    # Get VIN
    vin = None
    while vin is None or vin == "":
        try:
            print('Query VIN')
            vin_response = await BT_CLIENT.get(VIN_API, timeout=5)
        except Exception as err:
            print(err)
            time.sleep(2)
            continue

        vin = vin_response.json().get('vin')
        break

    # Get DEVICE_ID
    device_id = None
    retry_counter = 0
    RETRY_ATTEMPTS = 10
    RETRY_WAIT_TIMER_INCREMENT = 3
    # device_id = '12BW111TEST001'
    while device_id is None:
        try:
            print('Getting IoT Data, incl. Device ID')
            id_response = await BT_CLIENT.get(DEVICEID_API, timeout=5)
            print(id_response)
            iot_response = id_response.json()
        except Exception as err:
            print(err)
            retry_counter += 1
            if retry_counter == RETRY_ATTEMPTS:
                iot_response = {}
                device_id = 'NOTSET'
                uvicorn_logger.error('Cannot retrieve DEVICE ID, setting unknown.')
                break

            time.sleep(RETRY_WAIT_TIMER_INCREMENT * retry_counter)
            continue

        device_id = iot_response.get('device_id', 'NOTSET')
        # break

    for key, value in config.items():
        BT_CONFIG[key] = value

    BT_CONFIG['VIN'] = vin
    app.state['VIN'] = vin
    BT_CONFIG['DEVICE_ID'] = device_id
    # TODO: Temp Hard coded
    # BT_CONFIG['DEVICE_ID'] = os.environ.get('WGO_IOT_DEVICE_ID', '7054042BB005-0000')

    uvicorn_logger.debug(f'IoT response {iot_response}')

    uvicorn_logger.debug(f'VIN response {vin}')
    uvicorn_logger.debug(f'Device ID: {device_id}')
    uvicorn_logger.debug(f'Device config: {BT_CONFIG}')
    runner = BTBackgroundRunner(BT_CONFIG)

    app.runner = runner

    # Get VIN from main service
    asyncio.create_task(runner.run_main())


@app.on_event('shutdown')
async def shutdown_event():
    await runner.stop()


if __name__ == '__main__':
    uvicorn.run(
        'wgo_bt_service:app',
        host=BIND_ADDRESS,
        port=int(BT_SERVICE_PORT),
        workers=1
    )
