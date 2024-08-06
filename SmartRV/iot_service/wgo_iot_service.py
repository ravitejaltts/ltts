# -------------------------------------------------------------------------
# Copyright (c) Winnebago Industries. All rights reserved.
# --------------------------------------------------------------------------
"""
Winnebago IOT Service

Provide API control over IOT system, become an Azure Device Client to provide
remote data and control
"""

# Version for the IOT service is in the main py file.
__version__ = "1.0.8"

import asyncio
import json
import os
import time
from datetime import  datetime, timedelta
import uuid
import logging
from common_libs import environment
import signal
from threading import Thread, Timer, Lock
# from six.moves import input
from fastapi import FastAPI

import uvicorn
import requests

from enum import Enum, auto

from iot_service.utils import (
    Iot_Status,
    StateLog,
    read_data_after_version_id
)
from urllib.parse import urlparse


from azure.iot.device import X509
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import IoTHubDeviceClient
from azure.iot.device import Message
from azure.iot.device import MethodResponse
from azure.iot.device.common.transport_exceptions import ConnectionFailedError
from azure.iot.device.exceptions import (
    ConnectionFailedError as InitialConnectionFailedError,
)
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient

import configparser
from iotConfig import IotConfig
#from enum import IntEnum, auto
from iot_service.provisioning import Provisioning
from logging.handlers import RotatingFileHandler
from iot_service.iot_bulk import (
    m1_bulk_store,
    m2_bulk_store,
    retrieve_m1_bulk_messages,
    retrieve_m2_bulk_messages,
)
from iot_service.ota_control import ota_control, OTAStatus

#from typing import Optional, List, Union
#from pydantic import BaseModel
from iot_service.utils import Utils, MIN_LENGTH  # , InMemoryX509

from iot_service.routers import root
from iot_service.routers import notifications

# from common_libs.models.notifications import TelemetryMsg
from iot_service.telemetry import control_telemetry  # , get telemetry control object

# TODO: Dom to decide a good 'common' path -
# sys.path.append("../main_service/models/")
from common_libs.models.common import LogEvent, RVEvents, EventValues
from common_libs.system.system_storage_helper import get_telemetry_file

#from common_libs.system.scheduled_function import ScheduledFunction
from common_libs.system.schedule_manager import ScheduledFunctionManager
from common_libs.data_helper import remove_empty_elements

_env = environment()


class APIMethods(Enum):
    '''API Types for sending over BLE'''
    GET = 1
    HEAD = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()
    CONNECT = auto()
    OPTIONS = auto()
    TRACE = auto()
    PATCH = auto()


# sys.path.append('./SmartRv/can_service/bt_service/')
# sys.path.append("../bt_service/")

try:
    from setproctitle import setproctitle

    setproctitle("WGO-IoT-Service")
except ImportError:
    pass

BaseUrl = f"http://{_env.bind_address}:{_env.main_service_port}"
uvicorn_logger = logging.getLogger(__name__)
LOG_MAX_FILE_SIZE = 40000
LOG_BACKUP_FILE_CNT = 3

RETRY_WAIT_INTERVAL = 12  # Hours
CONNECT_RETRY_INTERVAL = timedelta(hours=RETRY_WAIT_INTERVAL)   # Attempt to retry if disconnected due to failed to connect - ( not internet missing )

from enum import Enum

uvicorn_logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
fileLogHandler = RotatingFileHandler(
    _env.log_file_path("iot_service.log"),
    "a+",
    maxBytes=LOG_MAX_FILE_SIZE,
    backupCount=LOG_BACKUP_FILE_CNT,
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fileLogHandler.setFormatter(formatter)
uvicorn_logger.addHandler(fileLogHandler)
# logHandler.setFormatter(formatter)
# uvicorn_logger.addHandler(logHandler)

Utils.setLogger(uvicorn_logger)

# TODO the machine endpoint, which will be an API call...
# TODO  send the VIN, and get back deviceId, deviceType, attributes (like Floorplan, model, etc), DPS and certs

MINUTES = 60

MESSAGE_TYPE_TELEMETRY = "1"
MESSAGE_TYPE_CRITICAL = "2"

ALLOWED_METHODS = (
    "getStatus",
    "enableChatty",
    "disableChatty",
    "setConfig",
)
SYSTEM_URLS = [
    "https://apim.ownersapp.winnebago.com/api/devices",
    "https://tst-apim.ownersapp.winnebago.com/api/devices",
    "https://dev-apim.ownersapp.winnebago.com/api/devices"
]


# TODO The next level of fallback as part of provisioning

def clean_twin_patch(patch):
    """Removes meta information from a twin patch."""
    return {k: v for k, v in patch.items() if k.startswith("$") is False}

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
    print('IOError', err)
    try:
        VERSION = json.load(
            open('../version.json', 'r')
        )
    except IOError as err:
        print('IOError', err)
        VERSION = {
            'version': __version__,
        }

# Inject more data
VERSION['debug'] = True

class IoTHandler(object):
    """Handles all IoT callbacks, methods and interactions."""

    file_version = __version__
    tcu_update = False
    m1_bundle_cnt = 0  #
    m2_bundle_cnt = 0  #
    m1_lock = Lock()
    m2_lock = Lock()
    send_m1_to_platform_check_flag = True
    send_m2_to_platform_check_flag = True
    send_m2_to_main_needed_flag = True
    dpsFailCnt = 0
    logger = uvicorn_logger
    clearTwin = False  # set for hand clearing now on startup
    t_data_sent = {}  # Don't resend data already sent
    cfg = {}
    run = True
    connectedLast = datetime.now() - timedelta(days=1)
    device_id = None
    #platform_env = None
    deviceClient = None
    deviceClientisCreated = False
    iot_telemetry = None
    ota_control = None
    error = None
    ONLINE_CHANGE_FLAG = False
    not_connected_cnt = 0  # After x passes clear the assigned hub and fall back next connect to provisioning
    M1_TELEMETRY_TIME = time.time() - 580
    M2_TELEMETRY_TIME = time.time()
    TWIN_TELEMETRY_TIME = time.time()
    cfg = {}
    iotStatus = Iot_Status.FRESH_BOOT
    iotStatusLock = Lock()
    iotStateLock = Lock()
    state_check_is_running = False
    iotStatusMsg = "Just finished Init."
    twin_update_needed = False
    twin_high_interval = False  # set true if twin fast data is added
    vinreset = False
    process_new_vin_needed = False
    t_data_sent = {}
    cert_path = None
    provisioner = None
    once = True
    remoteDeviceTwin = {}
    X509 = None
    bulk_timer = None
    registration_success = False
    check_counter = 0
    client_fail_counter = 0
    cert_update_in_progress = False
    use_bak_certs = False
    last_connect_retry_fail = datetime.now() - timedelta(days=1)
    mainLoopCounter = 0
    want_cert = False
    os_host_name = ""
    configCheck = None

    def platform_env(self):
        parsed_url = urlparse(self.get_active_env_api_url())
        self.configCheck.set_key("Device","platform_env", parsed_url.hostname.split('.')[0])
        return self.configCheck.get_key("Device","platform_env")

    def __init__(self, connect_on_create=True):
        #have_ini = False
        #self.configParser = configparser.ConfigParser()
        self.configCheck = IotConfig(self, VERSION)

        self.configParser = self.configCheck.configParser

        # No need to start chatty
        self.disableChatty()

        self.ota_control = ota_control(self)

        self.iot_telemetry = control_telemetry(
            self.configCheck, self
        )
        self.os_host_name = read_data_after_version_id('/etc/os-release')

        time.sleep(2) # Give time back to uvicorn before running Init

        self.Provisioned_Init()


    def state_check(self):
        try:
            if self.state_check_is_running is True:
                time.sleep(.1)
                print("Running??")
                return
            with self.iotStateLock:
                self.state_check_is_running = True
                if Utils.have_internet() is False:
                    if self.deviceClient.connected is True:
                        self.log("State: No internet but device not yet timedout.")
                    else:
                        self.update_status(Iot_Status.CHECKING_FOR_INTERNET, f"No Internet detected.")
                # Determnine the next step based on status
                elif self.iotStatus == Iot_Status.FRESH_BOOT or  \
                    self.iotStatus == Iot_Status.CONFIG_NEEDED or \
                    self.iotStatus == Iot_Status.CHECKING_FOR_INTERNET:
                    if self.check_vin() is not None and Utils.have_internet():
                        self.update_status(Iot_Status.GETTING_VEHICLE_RECORDS, f'Checking registration: {self.vin()}')
                    elif self.check_vin() is None:
                        self.iotStatus = Iot_Status.VIN_NEEDED

                elif self.iotStatus == Iot_Status.VIN_NEEDED:
                    # Waiting for VIN
                    time.sleep(5)  # Nothing to do without VIN
                elif self.iotStatus == Iot_Status.VIN_ENTERED or \
                    self.iotStatus == Iot_Status.GETTING_VEHICLE_RECORDS:
                    if self.deviceClient is not None:
                        try:
                            self.deviceClient.disconnect()
                            time.sleep(.1)  # Pause a moment for the system : - )
                        except Exception as err:
                            self.log(f'GETTING_VEHICLE_RECORDS dissconect: {err}')
                    # Begin VIN processing
                    self.check_env_GET()

                elif self.iotStatus == Iot_Status.VEHICLE_RECORDS_LOADED:
                    # Do we have certs?
                    self.registration_success = True
                    if self.want_cert is True or self.configCheck.get_key("States", "configured", "False") == "False":
                        self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, f"Prepare to call patch: {datetime.now()}")
                    else:
                        print(f'Check self.configCheck.get_key("States","configured") {self.configCheck.get_key("States","configured")}')
                        self.update_status(Iot_Status.DPS_PROVISIONING, "Records found.")

                elif self.iotStatus == Iot_Status.DPS_PROVISIONING:
                    self.dps_provision()

                elif self.iotStatus == Iot_Status.CONNECT_START:
                    # Determine is we are ready to go to IOT or setting up Certs
                    if self.configCheck.get_key("States", "configured", "False") != "True":
                        if self.deviceClient is not None:
                            self.log("STate: Remove OLD Client")
                            del self.deviceClient
                            self.deviceClient = None
                            time.sleep(.1)  # Pause a moment for the system : - )
                        self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, f"TRYING to get certs for: {self.get_active_env_api_url()}")
                    else:
                        self.update_status(Iot_Status.DPS_CERTS_OK, f"Using previous certs for: {self.get_active_env_api_url()}")

                elif self.iotStatus == Iot_Status.REGISTATIONS_PATCH_CALL:
                    if self.dpsFailCnt > 1:
                        self.update_status(Iot_Status.REGISTRATIONS_FAIL, f"TRYING twice to get certs for: {self.get_active_env_api_url()} ")
                        self.last_connect_retry_fail = datetime.now()
                    else:
                        self.patch_call()

                elif self.iotStatus == Iot_Status.DPS_CERTS_OK:
                    self.create_device_client()
                elif self.iotStatus == Iot_Status.CONNECTING:
                    self.connect()

                elif self.iotStatus == Iot_Status.DPS_CERTS_MISSING or \
                    self.iotStatus == Iot_Status.FALLBACK_PREP or \
                    self.iotStatus == Iot_Status.CLIENT_FAIL:
                    Utils.checkCerts()
                    if self.client_fail_counter < 3:
                        if self.working_in_temp() > 0:
                            # Reset to come back - TODO: Will we loop trying to go back - maybe set timestamp
                            self.configCheck.set_key('Platform', 'transfer_failed', str(datetime.now().timestamp()))
                            if self.configCheck.get_key("Device", "fallback_api_url") != "":
                                self.configCheck.set_key("Device", "api_url", self.configCheck.get_key("Device", "fallback_api_url"))
                                self.configCheck.set_key("Device", "assigned_hub", "")
                                self.update_status(Iot_Status.FALLBACK_PREP, f"Retrying to get certs for: {self.get_active_env_api_url()}")
                            else:
                                # Go back around
                                self.update_status(Iot_Status.GETTING_VEHICLE_RECORDS, f"TRYING to get certs for: {self.get_active_env_api_url()}")
                            self.saveConfig()
                        else:
                            self.update_status(Iot_Status.GETTING_VEHICLE_RECORDS, f"TRYING to get certs for: {self.get_active_env_api_url()}")
                    else:
                        self.update_status(Iot_Status.CLIENT_FAIL, f"Will not retry for {RETRY_WAIT_INTERVAL} hours.")
                        self.last_connect_retry_fail = datetime.now()

                elif self.iotStatus == Iot_Status.CONFIG_OK:
                    self.Provisioned_Init()
                    self.connect()

                elif self.iotStatus == Iot_Status.OFFLINE:
                    if (self.not_connected_cnt % 10) == 0:
                        self.update_status(Iot_Status.CHECKING_FOR_INTERNET, "OFFLINE - checking if we can reconnect")

                elif self.iotStatus ==  Iot_Status.VEHICLE_RECORDS_NOT_RECEIVED or \
                    self.iotStatus == Iot_Status.REGISTRATIONS_FAIL or \
                    self.iotStatus == Iot_Status.CLIENT_FAIL:
                    # This is a failure state - Parked here
                    time.sleep(5)
                    # make sure time interval is up
                    if self.last_connect_retry_fail + CONNECT_RETRY_INTERVAL < datetime.now():
                        self.iotStatus = Iot_Status.GETTING_VEHICLE_RECORDS
                elif  self.iotStatus ==  Iot_Status.CONNECTED:
                    if self.tcu_update is True:
                        # Disconnect to register again and report
                        if self.deviceClient is not None:
                            try:
                                self.deviceClient.disconnect()
                                # Same as requesting certs
                                self.configCheck.set_key("States", "provisioned", "False")
                                self.configCheck.set_key("States", "configured", "False")
                                self.configCheck.set_key("Device", "assigned_hub", "")
                                self.want_cert = True
                                self.saveConfig()
                                self.update_status(Iot_Status.GETTING_VEHICLE_RECORDS, "IMEI data to register now.")
                                time.sleep(.1)  # Pause a moment for the system : - )
                            except Exception as err:
                                self.log(f'TCU_UPDATED disconect: {err}')

                self.state_check_is_running = False
        except Exception as err:
            self.log(f'state_check: {err}')
            if self.iotStatus == Iot_Status.CONNECTING:
                # If we exception in connecting state
                self.update_status(Iot_Status.CLIENT_FAIL, f'State exception: {err}  ts: {datetime.now()}')
            self.state_check_is_running = False


    def update_status(self, status: Iot_Status, msg: str ):
        with self.iotStatusLock:
            self.iotStatus = status
            self.iotStatusMsg = msg
        logmsg = f"IOT Status change: {status.name} {msg}"
        Utils.pushLog(logmsg)
        StateLog.append(logmsg)
        if status == Iot_Status.CONNECTED:
            try:
                if self.use_bak_certs is True:
                    # Check if we used the backup Cert restore it
                    Utils.restore_backup_cert(f'{self.get_working_pem_name()}.pem')
                    Utils.restore_backup_cert(f'{self.get_working_pem_name()}.chain.pem')
                    self.use_bak_certs = False
                else:
                    # Check if we need to store anything
                    Utils.check_backup_cert(f'{self.get_working_pem_name()}.pem')
                    Utils.check_backup_cert(f'{self.get_working_pem_name()}.chain.pem')
                self.cert_update_in_progress = False
                self.configCheck.set_key("Device","api_url", self.get_active_env_api_url())
                if self.working_in_temp() == 2:
                    if self.configCheck.get_key('Platform', 'temp_api_url') == self.get_active_env_api_url():
                        self.configCheck.set_key("Device","fallback_api_url", self.get_active_env_api_url())
                        self.configCheck.set_key("Platform", "temp_api_url", "")
                # Make sure OTA has the environment
                self.ota_control.re_init()
                self.not_connected_cnt = 0
                if self.bulk_timer is not None:
                    self.bulk_timer.cancel()
                    self.bulk_timer = None
                # Only start OTA if we are not trying to transfer
                if self.working_in_temp() == 0:
                    self.ota_control.set_ota_allowed(True)
                else:
                    self.ota_control.set_ota_allowed(False)
            except Exception as err:
                Utils.pushLog(f"update_status ERROR: {err}")


    def check_vin(self, vin: str = None):
        Utils.pushLog(f"Check VIN called with vin: {vin}")
        # if we already have vin
        if self.vin() is not None:
            if self.iotStatus == Iot_Status.VEHICLE_RECORDS_NOT_RECEIVED:
                if self.vinreset is True:
                    self.configCheck.set_key("Device","vin", vin)
                    self.saveConfig()
                    self.update_status(Iot_Status.VIN_ENTERED, "Trying adjusted VIN.")
                    self.vinreset = False
                else:
                    Utils.pushLog(f"Already failed GETTING_VEHICLE_RECORDS {self.vin()}")
                    return None
            else:
                Utils.pushLog(f"Check VIN already have vin: {self.vin()}")
                return self.vin()
        else:
            try:
                vn = self.configCheck.get_key("Device", "vin")
            except:
                vn = "NA"
            if len(vn) == 17:
                return self.vin()

        def check_length(vn):
            if len(vn) == 17:
                Utils.pushLog(f"Found VIN {vn}")
                # Save new VIN
                self.configCheck.set_key("Device","vin", vn)
                self.saveConfig()
                return vn
            else:
                Utils.pushLog(f"Found improper VIN {vn}")
                return None

        # If Vin was passed in
        if vin is not None:
            self.configCheck.set_key("Device","vin", check_length(vin))
        else:  # Fall Back try to read the file
            vin_file = _env.vin_file_path()
            try:
                with open(vin_file, "r") as vfile:
                    vin = vfile.read().replace("\n", "")
                    self.configCheck.set_key("Device","vin", check_length(vin))
            except IOError as err:
                Utils.pushLog(f"IOError: {err}, {vin_file}", 'error')
                self.configCheck.set_key("Device","vin", "")
            except FileNotFoundError as err:
                Utils.pushLog(f"FileNotFoundError: {err}, {vin_file}", 'error')
                self.configCheck.set_key("Device","vin", "")
            # We must have the vin to proceed with IOT
            Utils.pushLog(f"Vin at this point: {self.vin()}")
        self.saveConfig()
        return self.vin()

    def load_telemetry(self):
        # Decide what telemetry file to load
        self.log("\n\nload_telemetry starting")
        telemetryOk = False
        try:
            # gt the last OTA file deleivered
            msg = f'Using Telemetry from {self.configCheck.get_key("OTA", "telemetry_file")}'
            print(f"\n\nTELEMETRY ******************* {msg}\n\n")

            self.log(msg)
            self.cfg = get_telemetry_file(self.configCheck.get_key("OTA", "telemetry_file"))
            telemetryOk, msg = self.iot_telemetry.set_cfg(self.cfg)
        except Exception as err:
            self.log(f'Load Telemetry ini Fail {err} ',"error")
            try:    # load Vanilla if not found
                self.log(f"Loading Telemetry VANILLA_ota_template.json {err} ","error")
                self.cfg = get_telemetry_file("VANILLA_ota_template.json")
                telemetryOk, msg = self.iot_telemetry.set_cfg(self.cfg)
            except Exception as err:
                self.log(f"Load Telemetry Vanilla Fail {err} ","error")

        if telemetryOk is False:
            self.update_status(Iot_Status.CONFIG_ERROR, f"Load telemetry file failed {msg}.")
        else:
            self.log(msg)


    def find_environment(self):
        """Check for the enviroment the device belongs to"""
        result = False
        if self.vin() is None:
            return result

        for item in SYSTEM_URLS:
            print("Check get_registrations", item)
            result = self.get_registrations(api_url=item)
            if result is True:
                break

        return result

    def transfer_failed(self):
        # return True #test without transfers
        '''Check if we tried to tranfer in the last hour'''
        return (self.configCheck.get_key("Platform", 'temp_api_url') != ""  and
            datetime.fromtimestamp(float(self.configCheck.get_key("Platform", "transfer_failed", "0"))) + timedelta(hours=1.0) >
            datetime.now())

    def working_in_temp(self):
        ''''Determine if we are trying to work in a temp environment'''
        result = 0
        if self.configCheck.get_key('Platform', 'temp_api_url') != "" and not self.transfer_failed():
            if self.configCheck.get_key('Platform', 'expiration_time') != "0.0":
                # check is expired
                if datetime.fromtimestamp(float(self.configCheck.get_key('Platform', 'expiration_time', "0.0"))) > datetime.now():
                    # Temporary environment OK - ACTIVE
                    result = 1
                else:
                    # It has expired - clear request
                    self.log(f"Transfer request expired - clearing {self.configCheck.get_key('Platform', 'temp_api_url')}")
                    self.configCheck.set_key('Platform', 'temp_api_url', "")
                    if self.configCheck.get_key("Device","fallback_api_url") != "":
                        self.configCheck.set_key("Device","api_url", self.configCheck.get_key("Device","fallback_api_url"))
                        # Might need to clear the hub other places
                        self.configCheck.set_key("Device","assigned_hub", "")
                    self.saveConfig()
            else:
                # Transfer in progress
                result = 2
        return result

    def get_active_env_api_url(self):
        result = self.configCheck.get_key("Device","api_url")
        if self.working_in_temp() > 0:
            result = self.configCheck.get_key('Platform', 'temp_api_url')
        return result

    def get_registrations(self, api_url: str = None):
        print('Enter get_registrations')
        if self.provisioner is None:
            self.provisioner = Provisioning(
                    api_url, self)
        if api_url is not None:
            self.provisioner.api.set_api(api_url)
            self.configCheck.set_key("Device","api_url", api_url)
            self.platform_env()

        if self.get_active_env_api_url() == "":
            self.configCheck.set_key("Device","api_url", api_url)
            self.platform_env()
        self.log(f"Trying get_registrations: {self.provisioner.api}")
        result = False
        try:
            #self.log(f"Trying get_device_info: {self.device_id}")
            device_info = self.provisioner.api.get_device_info(self.vin())
            self.log(f"get_registrations {self.vin()} device info {device_info.__dict__()}")
            if device_info is not None and device_info.success is True:
                try:
                    self.log(f"\n Device Info {device_info.__dict__()}")
                    # Store the results if not a temp change or a test

                    #self.configCheck.set_key("Device","api_url"] = self.provisioner.api.api_url
                    self.configCheck.set_key("Device","device_id", device_info.device_id)
                    #parsed_url = urlparse(self.provisioner.api.api_url)
                    #self.configCheck.set_key("Device","platform_env"] = parsed_url.hostname.split('.')[0]
                    self.configCheck.set_key("Device", "id_scope", device_info.dps_scope)
                    self.configCheck.set_key("Device", "serial_number", device_info.serial_number)
                    self.configCheck.set_key("Device", "model_year", device_info.model_year)
                    self.configCheck.set_key("Device", "device_type", device_info.device_type)
                    self.configCheck.set_key("Device", "provisioning_host", device_info.dps_host)
                    self.configCheck.set_key("Device", "csr_required", str(device_info.csr_required))
                    if device_info.series_model is not None:
                        if device_info.series_model != "":
                            self.configCheck.set_key("Device", "seriesmodel", device_info.series_model)
                    if device_info.floor_plan is not None:
                        if device_info.floor_plan != "":
                            self.configCheck.set_key("Device", "floor_plan", device_info.floor_plan)
                    if device_info.option_codes is not None:
                        if device_info.option_codes != "":
                            self.configCheck.set_key("Device", "option_codes", device_info.option_codes)
                    if device_info.model_year is not None:
                        if device_info.model_year != "":
                            self.configCheck.set_key("Device", "model_year", device_info.model_year)
                    if device_info.attributes is not None:
                        if device_info.attributes != "":
                            self.configCheck.set_key("Device", "attributes", str(device_info.attributes))
                    self.log(f'Found environment {self.platform_env()} VIN {self.vin()} device given {device_info.device_type}')
                    #  Now let's check if we are being asked to transfer - but not while we are trying to transfer
                    print("Checking transfer stuff")
                    if device_info.transfer_path != "" and self.iotStatus != Iot_Status.VEHICLE_RECORD_MOVE and \
                        device_info.installation_cert is not None:
                        # Check if we are going back to default
                        print("Checking transfer direction")
                        if device_info.transfer_path == self.configCheck.get_key("Device", "fallback_api_url"):
                            print("Fallback transfer")
                            self.configCheck.set_key('Platform', 'expiration_time', "0.0")
                            self.configCheck.set_key('Platform', 'temp_api_url', "")
                            self.configCheck.set_key('Device', 'api_url', self.configCheck.get_key("Device", "fallback_api_url"))
                            self.configCheck.set_key("Device", "assigned_hub", "")
                            self.platform_env()
                            self.update_status(Iot_Status.VEHICLE_RECORD_MOVE, "Fallback Transfer requested.")
                            self.get_registrations(device_info.transfer_path)
                        else:
                            print(f"New transfer to {device_info.transfer_path} ")
                            self.configCheck.set_key("Device","fallback_api_url", self.configCheck.get_key("Device","api_url"))

                            # Check have we tried this before recently?
                            if not self.transfer_failed():
                                self.configCheck.set_key("Platform", "transfer_failed", "0")  #Reset to be easy to spot attempt
                                self.configCheck.set_key('Platform', 'temp_api_url', device_info.transfer_path)
                                # prepare and move the cert for the env
                                self.configCheck.set_key("Device","assigned_hub", "")
                                self.configCheck.set_key("States", "configured", "False")
                                parsed_url = urlparse(device_info.transfer_path)
                                tmp_platform_env = parsed_url.hostname.split('.')[0]
                                Utils.put_secret(f"for_check.pem", device_info.installation_cert)
                                self.provisioner.api.move_pfx(device_info.installation_cert, tmp_platform_env, self.vin(), device_info.device_id, device_env=True)
                                if device_info.transfer_expires is not None:
                                    self.configCheck.set_key('Platform', 'expiration_time', str(device_info.transfer_expires))
                                    self.log(f'Platform expiration_time: {str(device_info.transfer_expires)}')
                                    if datetime.fromtimestamp(device_info.transfer_expires) < datetime.now():
                                        self.update_status(Iot_Status.VEHICLE_RECORDS_LOADED, "Expired Transfer Request in response!")
                                        print(f"Transfer expired already.")
                                    else:
                                        self.update_status(Iot_Status.VEHICLE_RECORD_MOVE, "Transfer Requested")
                                        print(f"Transfer active till:  {device_info.transfer_expires}")
                                else:
                                    self.configCheck.set_key('Platform', 'expiration_time', "0.0")
                                    self.update_status(Iot_Status.VEHICLE_RECORD_MOVE, "Environment Transfer Requested")
                                # Recurse into this function for move
                                self.get_registrations(device_info.transfer_path)
                            else:
                                self.update_status(Iot_Status.VEHICLE_RECORDS_LOADED, "Transfer requested but has already failed within last hour.")
                                self.send_floorplan_to_main()
                                self.iot_telemetry.send_events_to_main_service()  # Be sure to send options
                    elif device_info.installation_cert is not None:
                        print(f"get_registrations VIN {self.vin()} path Has installation Cert!")
                        self.log(f"get_registrations VIN {self.vin()} path Has installation Cert!")
                        parsed_url = urlparse(device_info.transfer_path)
                        tmp_platform_env = parsed_url.hostname.split('.')[0]
                        Utils.put_secret(f"reg_check.pem", device_info.installation_cert)
                        self.provisioner.api.move_pfx(device_info.installation_cert, tmp_platform_env, self.vin(), device_info.device_id, device_env=True)
                        self.update_status(Iot_Status.VEHICLE_RECORDS_LOADED, "init 1")
                        self.send_floorplan_to_main()
                        self.iot_telemetry.send_events_to_main_service()  # Be sure to send options
                    else:
                        print("REcords Loaded....")
                        self.update_status(Iot_Status.VEHICLE_RECORDS_LOADED, "init 2")
                        self.send_floorplan_to_main()
                        self.iot_telemetry.send_events_to_main_service()  # Be sure to send options

                    self.configCheck.set_key("Device", "api_url", self.provisioner.api.api_url)
                    self.saveConfig()
                except Exception as err:
                    self.log(f"get_registrations config save Error: {err}")
                    print(f"get_registrations config save Error: {err}")
                self.twin_update_needed = True
                result = True
        except Exception as err:
            self.log(f"get_registrations Fail VIN {self.vin()} path {api_url} Error: {err}")

        print("get_registrations Exit....")
        return result

    def check_env_GET(self):
        result = False
        attempts = 0

        have_env = (self.get_active_env_api_url() != "")

        if self.provisioner is None:
            self.provisioner = Provisioning(
                self.get_active_env_api_url(), self)
        else:
            self.provisioner.api.set_api(self.get_active_env_api_url())

        # Find Environment - if we don't already have one - must clear it to retry
        while attempts < 4 and not have_env:
            #self.update_status(Iot_Status.GETTING_VEHICLE_RECORDS, f"find_environment attempt {attempts}.")
            have_env = self.find_environment()
            attempts += 1

        if have_env is False:
            self.update_status(Iot_Status.VEHICLE_RECORDS_NOT_RECEIVED, f"No environment for VIN {self.vin()} after: {attempts-1} attempts.")
            self.configCheck.set_key("Device", "api_url", "")
            self.configCheck.set_key("Device", "fallback_api_url", "")
        else:
            result = self.get_registrations(api_url=self.get_active_env_api_url())

            if result is False:   # Check our info():
                Utils.pushLog(f"get_registrations Fail?")
                if self.working_in_temp() > 0:
                    # Reset to come back -
                    self.configCheck.set_key('Platform', 'transfer_failed', str(datetime.now().timestamp()))
                    if self.configCheck.get_key("Device","fallback_api_url") != "":
                        self.configCheck.set_key("Platform", "temp_api_url", "")
                        self.configCheck.set_key("Device","api_url", self.configCheck.get_key("Device","fallback_api_url"))
                        self.configCheck.set_key("Device","assigned_hub", "")
                    self.saveConfig()
                    # self.run = False
                else:
                    self.update_status(Iot_Status.VEHICLE_RECORDS_NOT_RECEIVED, f"Get registration failed! IOT using VIN {self.vin()}")
            else:
                self.update_status(Iot_Status.VEHICLE_RECORDS_LOADED, 'Registration OK.')
        return  # Results in an updated status


    # def GetCert(self):
    #     pass

    def patch_call(self):
        self.tcu_update = False  # Reset the TCU flag we have sent the information
        if self.provisioner.provision_device(self.vin(),
                                            self.configCheck.get_key("Device","device_id")
                                        ):
            self.log("The device was given a cert!")
            self.configCheck.set_key("States", "configured", "True")
            self.want_cert = False
            self.saveConfig()
            # self.update_status(Iot_Status.DPS_CERTS_OK, "The device was able to get pfx and certs!")
            self.dpsFailCnt = 0  # resert retries
        else:
            # Check for fallback
            if self.working_in_temp() > 0:
                # Reset to come back - TODO: Will we loop trying to go back - maybe set timestamp
                self.configCheck.set_key('Platform', 'transfer_failed', str(datetime.now().timestamp()))
                if self.configCheck.get_key("Device","fallback_api_url") != "":
                    self.configCheck.set_key("Device","api_url", self.configCheck.get_key("Device","fallback_api_url"))
                    self.configCheck.set_key("Device","assigned_hub", "")
                self.saveConfig()
                self.update_status(Iot_Status.FALLBACK_PREP, f"NOT able to get pfx certs for:{self.get_active_env_api_url()}")
            else:
                self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, f"NOT able to get pfx certs for:{self.get_active_env_api_url()}")
                self.dpsFailCnt += 1  # This will retry once

    def Provisioned_Init(self):
     # BAW111   print(self.configParser.items())
        # self.m2Queue = Queue(maxsize=100) # for passing the calls from the API
        # timer for the class
        self.bulk_timer = None
        self.version_data = VERSION.get('version')
        if self.version_data != self.configCheck.get_key("Device",'software_version'):
            self.configCheck.set_key("Device",'software_version', self.version_data)
            self.saveConfig()
        self.load_telemetry()
        # TODO Check if OTA is finished from all updates
        try:
            # NOTE: This is overwritten in so many places now, ideally read from one source, and then fall back to a default in the same place
            self.cfg["TELEMETRY_INTERVAL"] = 600  # default M1 Interval
            self.cfg["TWIN_INTERVAL"] = 600  # default Twin Interval without chatty
            self.cfg["HIGH_TWIN_INTERVAL"] = 5  # default Twin Interval  chatty
            self.cfg["EVENT_INTERVAL"] = 5  # default M2 Interval
            self.cfg["FULL_TELEMETRY_INTERVAL"] = 86400  # Fetch from template
            self.cfg["FULL_EVENT_INTERVAL"] = 86400  # Fetch from template
            self.cfg["CHATTY_TWIN_INTERVAL"] = 5
            # We can bundle messages that don't need to be sent immediately
            self.cfg["bundle_messages"] = 1  # Combine messages if more than 1

            # NOTE: The use of a list in the template seems not efficient to use
            # To soften the iteration a little we can break the for loop if we only try to find the one item 'standard'
            for interval in self.iot_telemetry.cfg["targets"]:
                if interval["id"] == "standard":
                    self.cfg["TELEMETRY_INTERVAL"] = interval["intervalSeconds"]
                    self.cfg["FULL_TELEMETRY_INTERVAL"] = interval.get("intervalSecondsFull", 86400)
                elif interval["id"] == "event":
                    self.cfg["FULL_EVENT_INTERVAL"] = interval["intervalSeconds"]
                    self.cfg["FULL_EVENT_INTERVAL"] = interval.get("intervalSecondsFull", 86400)
                elif interval["id"] == "$twin":
                    self.cfg["TWIN_INTERVAL"] = interval["intervalSeconds"]
                    self.cfg["HIGH_TWIN_INTERVAL"] = interval.get("intervalSecondsFull", 86400)
                    self.cfg["CHATTY_TWIN_INTERVAL"] = interval.get("intervalSecondsChatty", 2)
            # Override time for test
            # self.cfg['TELEMETRY_INTERVAL'] = 60
            print("Interval M1 =", self.cfg["TELEMETRY_INTERVAL"])
            print("Interval M2 =", self.cfg["EVENT_INTERVAL"])
            self.log("IoTHandler Init ")
        except Exception as err:
            self.log(f"IoTHandler Init without proper config probable. {err}")

    def saveConfig(self):
        """Used to store config and provisioning etc between service restarts"""
        self.configCheck.saveConfig()

    def check_cert(self, check):
        result = False
        if not Utils.has_secret(check):
            certPath = _env.certs_path(check)
            if os.path.isfile(certPath):
                with open(certPath) as cert_file:
                    cert_str = cert_file.read()
                    Utils.put_secret(name=check, value=cert_str)
                    # We found the cert and loaded to the vault
                    result = True
            else:
                self.log(f"Certificate not found: {check}")
                self.configCheck.set_key("States", "provisioned", "False")
                self.configCheck.set_key("States", "configured", "False")
                self.dpsFailCnt = 0  # resert retries
                self.saveConfig()
        else: # We have the cert in vault
            result = True
        return result

    def dps_provision(self):
        key_file_name = f'{self.vin()}.key'
        if os.getenv("VAULT") is not None:
            key_file_name = f'{os.getenv("VAULT")}{key_file_name}'
        if not self.check_cert(key_file_name):
            self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, f"create_device_client: {key_file_name}")
            print("DPS A return")
            return # Don't start this if no cert

        cert_file_name = f'{self.platform_env()}-{self.vin()}.pem'

        if not self.check_cert(cert_file_name):
            self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, f"create_device_client: {cert_file_name}")
            print("DPS B return")
            return  # Don't start this if no cert

        chain_file_name = f'{self.platform_env()}-{self.vin()}.chain.pem'
        if not self.check_cert(chain_file_name):
            self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, f"create_device_client: {chain_file_name}")
            print("DPS C return")
            return # Don't start this if no cert

        self.error = None
        try:
            print(f"Key2.5 {self.platform_env()}")
            if self.use_bak_certs is True:
                cert_file_name = f'{self.platform_env()}-{self.vin()}.chain.pem.bak'
                if os.getenv("VAULT") is not None:
                    cert_file_name = f'{os.getenv("VAULT")}{cert_file_name}'
            else:
                cert_file_name = f'{self.platform_env()}-{self.vin()}.chain.pem'
                if os.getenv("VAULT") is not None:
                    cert_file_name = f'{os.getenv("VAULT")}{cert_file_name}'

            self.x509_provision = X509(
                                        cert_file_name,
                                        key_file_name,
                                        )
            msg = (f"DPS PROVISIONING  self.x509_provision {self.platform_env()}")
            self.log(msg,'debug')

            print(f"Key3 {self.platform_env()}  NAMES {key_file_name}  {cert_file_name}")
            provisioning_device_client = (
                ProvisioningDeviceClient.create_from_x509_certificate(
                    provisioning_host=self.configCheck.get_key("Device",
                        "provisioning_host"
                    ),
                    registration_id=self.configCheck.get_key("Device","device_id"),
                    id_scope=self.configCheck.get_key("Device","id_scope"),
                    x509=self.x509_provision,
                    #x509=self.x509_provision,
                    websockets=False
                )
            )

        except Exception as err:
            msg = f"Error in creating provisioning client {err}"
            self.log(msg,'debug')
            self.dpsFailCnt += 1
            self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, msg)
            raise
        print(f"Key4 {self.platform_env()}")

        try:
            self.update_status(Iot_Status.DPS_PROVISIONING, f"Run Client ts: {datetime.now()}")
            registration_result = asyncio.run(
                provisioning_device_client.register()
            )

            self.log(f"The complete registration result is: {registration_result.registration_state}")
            if registration_result.status == "assigned":
                self.configCheck.set_key("Device", "assigned_hub", registration_result.registration_state.assigned_hub)
                self.configCheck.set_key("Device", "device_id", registration_result.registration_state.device_id)
                self.log(
                    f'Will send telemetry from the provisioned device {self.configCheck.get_key("Device","assigned_hub")}'
                )
                self.configCheck.set_key("States", "provisioned", "True")
                ##self.cert_path = _env.certs_path(
                #   f'{self.configCheck.set_key("Device","platform_env"]}-{self.vin()}.pem'
                #)
                self.cert_path = f'{self.platform_env()}-{self.vin()}.pem'
                #)
                self.saveConfig()
                self.update_status(Iot_Status.DPS_CERTS_OK, "Run Client")
                print("register DPS")

            else:
                self.error = "Provisioning Call Failed"
                self.update_status(Iot_Status.DPS_FAIL, "Provisioning Call Failed.")
                print("FAIL DPS!")
                # raise("Provisioning Call Failed")

        except Exception as err:
            print(f'DPS : {err}')
            if self.cert_update_in_progress is True:
                self.update_status(Iot_Status.GETTING_VEHICLE_RECORDS, f'Setup Error DPS_PROVISIONING new cert: {err} ts: {datetime.now()}')
                self.log('Falling back to .bak certs')
                self.use_bak_certs = True
            else:
                self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, f'Setup exception: during DPS_PROVISIONING {err} ts: {datetime.now()}')


            # else:
            #     self.update_status(Iot_Status.DPS_CERTS_OK, "Already provisioned.")
            #     pass

    def assign_callbacks(self):
        try:
            self.deviceClient.on_message_received = (
                self.on_message_received )

            #print(f'Key3 on message ok {self.configCheck.set_key("Device","assigned_hub"]}')
            self.deviceClient.on_twin_desired_properties_patch_received = (
                self.on_twin_patch )

            #print(f'Key3 on twin ok {self.configCheck.set_key("Device","assigned_hub"]}')
            self.deviceClient.on_method_request_received = (
                self.on_method_received )

            #print(f'Key3 on method ok {self.configCheck.set_key("Device","assigned_hub"]}')
            self.deviceClient.on_connection_state_change = (
                self.on_connection_state_change )

            #print(f'Key3 on connection ok {self.configCheck.set_key("Device","assigned_hub"]}')
        except Exception as err:
            self.log(f"assign_callbacks: {err}")
            raise err

    def create_device_client(self):
        # iot client create
        print(f"KeyR {self.platform_env()}")
        if self.deviceClient is not None:
            try:
                self.log("setup:Remove OLD Client")
                self.deviceClient.shutdown()
                self.deviceClient = None
                time.sleep(.1)  # Pause a moment for the system : - )
            except Exception as err:
                self.log(f"Error in client shutdown: {err}")
                self.deviceClient = None

        self.log("setup: check certs")
        if self.use_bak_certs is True:
            cert_file_name = f'{self.platform_env()}-{self.vin()}.pem.bak'
            if os.getenv("VAULT") is not None:
                cert_file_name = f'{os.getenv("VAULT")}{cert_file_name}'
        else:
            cert_file_name = f'{self.platform_env()}-{self.vin()}.pem'
            if os.getenv("VAULT") is not None:
                cert_file_name = f'{os.getenv("VAULT")}{cert_file_name}'

        if not self.check_cert(cert_file_name):
            self.update_status(Iot_Status.DPS_PROVISIONING, f"create_device_client: {cert_file_name}")
            return  # Don't start this if no cert\

        key_file_name = f'{self.vin()}.key'
        if os.getenv("VAULT") is not None:
            key_file_name = f'{os.getenv("VAULT")}{key_file_name}'
        if not self.check_cert(key_file_name):
            self.update_status(Iot_Status.DPS_PROVISIONING, f"create_device_client: {key_file_name}")
            return # Don't start this if no cert

        try:
            # TODO Call the machine api endpoint
            # For now use an assinged Registration ID "vdt000000003-0000"
            try:
                print(f"Key1 - x509  {self.platform_env()}")
                #dpem =f'{self.configCheck.set_key("Device","platform_env"]}-{self.vin()}.pem'
                #dkey = key_file_name
                #self.X509 = X509(
                #    cert_file=_env.certs_path(cert_file_name),
                #    key_file=_env.certs_path(key_file_name),
                #)
                self.X509T = X509(
                    cert_file_name,
                    key_file_name,
                )
                print(f"Key2 {self.platform_env()}")
                msg = (f"setup  certs  {cert_file_name} {key_file_name}")
                self.log(msg, 'debug')

            except Exception as err:
                print("Error in setup: X509", err)
                self.dpsFailCnt += 1
                raise

            print(f"Key3 {self.platform_env()}")
            self.log(f"Create IoTHubDeviceClient ts: {datetime.now()}")
            self.deviceClient = IoTHubDeviceClient.create_from_x509_certificate(
                #x509=self.X509,
                x509=self.X509T,
                hostname=self.configCheck.get_key("Device","assigned_hub"),
                device_id=self.configCheck.get_key("Device","device_id"),
                keep_alive=180 # keep-alive timeout - 3 minutes MQTT update
            )
            self.update_status(Iot_Status.CONNECTING, f"Client created: ts: {datetime.now()}")
        except Exception as err:
            self.update_status(Iot_Status.CLIENT_FAIL, f'Setup exception: {err}  ts: {datetime.now()}')
            Utils.checkCerts()
            self.use_bak_certs = True
            self.dpsFailCnt += 1  # Increment here also
            self.client_fail_counter += 1
            if self.dpsFailCnt > 1:
                if self.configCheck.get_key("Device","fallback_api_url") != "":
                    self.configCheck.set_key("Device","api_url", self.configCheck.get_key("Device","fallback_api_url"))
                    self.configCheck.set_key("Device","assigned_hub", "")
                    #self.run = False
            msg = f"IOT configure error  {err}"
            self.log(msg,'debug')
            self.configCheck.set_key("States", "provisioned", "False")
            self.saveConfig()
            # raise

    def vin(self):
        try:
            result = f'{self.configCheck.get_key("Device","vin")}'
            if result == "":
                result = None
        except:
            # VIN not recorded
            result = None
        return result


    def get_working_pem_name(self):
        env = self.platform_env()
        vin = self.configCheck.get_key("Device","vin")
        return f"{env}-{vin}"

    def connect(self, retry=False, retry_counter=5):
        try:
            self.log("Device checking client.")
            result = self.deviceClient.connect()
        except ConnectionFailedError as err:
            self.log(f'ConnectionFailedError {print(err)}')
            if retry is True and retry_counter > 0:
                time.sleep(5)
                print("Retrying", retry_counter)
                return self.connect(retry=retry, retry_counter=retry_counter - 1)
            else:
                self.log("Connect retires exceeded!",'error')
                self.client_fail_counter += 1 # Increment the fail counter for the client
                raise
        except InitialConnectionFailedError as err:
            self.deviceClient.disconnect()
            self.log(f"Connect retry {retry_counter}")
            if retry is True and retry_counter > 0:
                time.sleep(5)
                print("Retrying", retry_counter)
                return self.connect(retry=retry, retry_counter=retry_counter - 1)
            else:
                self.log("Connect retires exceeded! B",'error')
                self.client_fail_counter += 1 # Increment the fail counter for the client
                raise
        except Exception as err:
            self.log(f"\n Connect ERROR  {retry_counter}")
            print(f"iot state: {self.iotStatus.name}")
            if self.working_in_temp() > 0:
                # Fallback connection failing
                self.client_fail_counter += 1
                self.update_status(Iot_Status.FALLBACK_PREP, "Try to go back connect failed.")
            else:
                self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, "See if we need new certs.")

        # Tested - incoming twin works TODO:  how to use the twin
        try:
            if self.clearTwin:
                self.log("Clearing Twin")
                self.clear_twin_on_platform()

            self.remoteDeviceTwin = self.deviceClient.get_twin()
            self.update_status(Iot_Status.CONNECTED, "Connect Immediate!")
            self.checkTwinIn()  # check is we need info the platform saved

            twice = 0
            # loop for platform - wants us to retry once if fails
            while twice < 2 :
                try:
                    # Check Twin for desired OTA
                    self.on_twin_patch(self.remoteDeviceTwin.pop('desired', {}))
                    twice = 2  # Exit loop
                    self.assign_callbacks()
                except Exception as err:
                    self.log(f"Twin OTA at startup err {err}", 'error')
                    twice += 1
        except ConnectionFailedError as err:
            self.log(f"connect:  {err}")
            self.remoteDeviceTwin = {}
            self.want_cert = True  # Note: check test this
            print(f"iot state: {self.iotStatus.name}")
            if self.working_in_temp() > 0:
                # Fallback connection failing
                self.client_fail_counter += 1
                self.update_status(Iot_Status.FALLBACK_PREP, "Try to go back twin recieve failed.")
            else:
                self.update_status(Iot_Status.REGISTATIONS_PATCH_CALL, "will try new certs.")

        except Exception as err:
            self.log(f"Get twin failed. {err}")
            self.remoteDeviceTwin = {}

    def checkTwinIn(self):
        print("\n\nDevice Twin received! @@@ ", self.remoteDeviceTwin, "\n\n")
        reports = self.remoteDeviceTwin.pop('request', {})
        if reports != {}:
            print("\n\nPATCH Local twin:  @@@ ", reports, "\n\n")
            self.log(f"PATCH Local twin: {reports}")
            self.iot_telemetry.add_other_twin_data('request', reports)

    def disconnect(self):
        self.deviceClient.disconnect()
        self.log("Device disconnect COMMANDED")

    def send_telemetry(self, body, bulk_flag=False, msg_type=MESSAGE_TYPE_TELEMETRY):
        if (
            self.iotStatus is Iot_Status.CONNECTED
        ):
            telemetry_message = Message(body.rstrip())

            telemetry_message.custom_properties[
                "mver"
            ] = "1"  # Changed to only need mver in custom proterties 1/19/23
            if not bulk_flag:  # Changed to custom proterties 1/20/23
                telemetry_message.content_encoding = "utf-8"
                telemetry_message.content_type = "application/json"

            # print('Telemetry_msg = ',telemetry_message)
            result = {}
            result = self.deviceClient.send_message(telemetry_message)

            if result == None:
                print("Telemetry send SUCCESS", telemetry_message)
                return True
            else:
                print("Telemetry send failed? ", result)
                return False
        return False  # not connected or locked - either way - the caller should store the message for later

    def send_m1_bulk_telemetry(self):
        """Send bulk messages could be after coming back Online or other use case"""
        print("Bulk M1 Start")
        if not Utils.have_internet:
            # do nothing with bulk if no internet, they will continue to accumulate
            print("Bulk not sent - no internet")
            self.log("Bulk not sent - no internet")
            return False

        self.log("Checking for M1 bulk files")
        result = "Unknown"
        # Get the storage info for the blob
        blob_file = retrieve_m1_bulk_messages()
        while blob_file != None:
            blob_name = os.path.basename(blob_file)
            storage_info = self.deviceClient.get_storage_info_for_blob(blob_name)
            try:
                sas_url = "https://{}/{}/{}{}".format(
                    storage_info["hostName"],
                    storage_info["containerName"],
                    storage_info["blobName"],
                    storage_info["sasToken"],
                )

                print(
                    "\nM1 Uploading file: {} to Azure Storage as blob: {} in container {}\n".format(
                        blob_file,
                        storage_info["blobName"],
                        storage_info["containerName"],
                    )
                )
                self.log(
                    "M1 Uploading file: {} to Azure Storage as blob: {} in container {}".format(
                        blob_file,
                        storage_info["blobName"],
                        storage_info["containerName"],
                    )
                )
                # Upload the specified file
                with BlobClient.from_blob_url(sas_url) as blob_client:
                    with open(blob_file, "rb") as f:
                        result = blob_client.upload_blob(f, overwrite=True)

                self.log(f"M1 Bulk Result {result}")
                os.remove(blob_file)
                blob_file = retrieve_m1_bulk_messages()

            except FileNotFoundError as ex:
                # catch file not found and add an HTTP status code to return in notification to IoT Hub
                ex.status_code = 404
                self.log("Bulk FileNotFoundError {ex}",'error')
                blob_file = None
                return False

            except AzureError as ex:
                # catch Azure errors that might result from the upload operation
                self.log("Bulk AzureError {ex}",'error')
                blob_file = None
                return False

        self.send_m1_to_platform_check_flag = False
        self.log("Done Checking for M1 bulk files")
        return True

    def send_m2_bulk_telemetry(self):
        """Send bulk messages could be after coming back Online or other usecase"""
        if self.iotStatus is not Iot_Status.CONNECTED:
            # do nothing with bulk if no internet, they will continue to accumulate
            self.log(f"Bulk data not sent {self.iotStatus}")
            return False
        # retrieve_bulk_messages from a logfile removes each file in rotation as it is read
        # it should be called until it return None
        print("Bulk M2 Start")
        # Get the storage info for the blob
        blob_file = retrieve_m2_bulk_messages()
        result = "Unknown"
        while blob_file != None:
            blob_name = os.path.basename(blob_file)
            self.log(f"Bulk M2 blob_name {blob_name}")
            try:
                storage_info = self.deviceClient.get_storage_info_for_blob(blob_name)
            except Exception as err:
                self.log(f"Bulk M2 get_storage_info_for_blob {err}", 'error')
                try:
                    os.remove(blob_file)
                    blob_file = None
                except FileNotFoundError as ex:
                    # catch file not found and add an HTTP status code to return in notification to IoT Hub
                    ex.status_code = 404
                    self.log(f"Bulk FileNotFoundError {ex}",'error')
                    blob_file = None
                    return False
            try:
                sas_url = "https://{}/{}/{}{}".format(
                    storage_info["hostName"],
                    storage_info["containerName"],
                    storage_info["blobName"],
                    storage_info["sasToken"],
                )
                print(
                    "\nM2 Uploading file: {} to Azure Storage as blob: {} in container {}\n".format(
                        blob_file,
                        storage_info["blobName"],
                        storage_info["containerName"],
                    )
                )
                self.log(
                    "M2 Uploading file: {} to Azure Storage as blob: {} in container {}".format(
                        blob_file,
                        storage_info["blobName"],
                        storage_info["containerName"],
                    )
                )
                # Upload the specified file
                with BlobClient.from_blob_url(sas_url) as blob_client:
                    with open(blob_file, "rb") as f:
                        result = blob_client.upload_blob(f, overwrite=True)

                self.log(f"M2 Bulk Result {result}")
                os.remove(blob_file)
                time.sleep(3)
                blob_file = retrieve_m2_bulk_messages()

            except FileNotFoundError as ex:
                # catch file not found and add an HTTP status code to return in notification to IoT Hub
                ex.status_code = 404
                self.log(f"Bulk FileNotFoundError {ex}",'error')
                blob_file = None
                return False

            except AzureError as ex:
                # catch Azure errors that might result from the upload operation
                self.log(f"Bulk AzureError {ex}",'error')
                blob_file = None
                return False

        self.send_m2_to_platform_check_flag = False
        print("Bulk M2 End")
        return True

    def send_critical_message(self, body, props={}, msg_type=MESSAGE_TYPE_CRITICAL):
        pass

    def on_connect(self, message):
        if self.iotStatus is Iot_Status.CONNECTED:
            self.log("on_connect hit while connected")
            #self.ota_control.set_ota_allowed(True)
            time.sleep(5)
            return
        self.update_status(Iot_Status.CONNECTED, "on_connect OK")

    def on_disconnect(self, message):
        if Utils.have_internet() is True:
            self.update_status(Iot_Status.OFFLINE, message)
            time.sleep(5)
        else:
            self.update_status(Iot_Status.CHECKING_FOR_INTERNET, message)

    def check_telemetry(self):
        if self.iotStatus is not Iot_Status.CONNECTED:
            # waiting to connect
            t_data = self.iot_telemetry.get_m1_telemetry()
            # save bulk message
            if t_data.get("data", {}) == {}:
                # Ignore this message
                print("Ignoring empty telemetry - check")
            else:
                self.store_telemetry(t_data)
                print("storing by timer", self.iotStatus, t_data)
            self.bulk_timer = Timer(
                self.cfg["EVENT_INTERVAL"], self.check_telemetry, [], {}
            )
            self.bulk_timer.start()

    def on_connection_state_change(self):
        self.log(f"on_connection_state_change callback = {self.deviceClient.connected}")
        currentConnection = self.deviceClient.connected
        if currentConnection is True:
            self.on_connect("ONLINE")
        else:
            self.on_disconnect("OFFLINE")
        # Slow down the main loop on a mode change
        self.ONLINE_CHANGE_FLAG = True


    def on_twin_patch(self, patch):
        print(dir(patch))
        print(patch)
        self.log(f"Twin Patch Received {patch}")
        self.twin_update_needed = True
        we_should_restart = False
        pltfrm_request = patch.pop("request", False)
        if pltfrm_request is not False:
            self.log(f"\n\n\n -> Plaftform request: {pltfrm_request}")
            reports = {}
            reported_requests = self.iot_telemetry.get_twin_data('request')
            for key in pltfrm_request.keys():
                try:
                    twin_key = int(reported_requests[key]['id'])
                except Exception as err:
                    self.log(f"New reset patch error {err}")
                    twin_key = 0
                # CHeck ID to only perfrom once
                if int(pltfrm_request[key]['id']) > twin_key:
                    self.log(f"New reset patch {pltfrm_request}")
                    print(f"New reset patch {pltfrm_request}")
                    #time.sleep(5)
                    self.configParser['Platform']['last_id'] = pltfrm_request[key]['id']
                    self.saveConfig
                    command = pltfrm_request[key].get('command', False)
                    if command is not False:
                        # print(f"Will RESTART IOT {key} Command: ", command)
                        param = command.get('parameters', False)
                        command_name = command.get('name', False)
                        if command_name is not False and param is not False:
                            self.run_remote_method(command_name, param)
                        # we_should_restart = True
                        reports['request'] = pltfrm_request
                else:
                    self.log(f"Previously handled reset patch detected {self.configCheck.get_key('Platform', 'last_id')}")

            if reports != {}:
                self.log(f"PATCH Remote twin: {reports}")
                self.iot_telemetry.add_other_twin_data('request', pltfrm_request)
                self.deviceClient.patch_twin_reported_properties(reports)
            if we_should_restart is True:
                self.log(f"RUN FALSE -> on_twin_patch: {reports}")
                self.run = False
                return # Do no additional processing is restarting

        ota_cmd = patch.pop("ota", False)
        if ota_cmd is not False:
            desired = patch.pop("$version", "z")
            self.ota_control.check_patch(ota_cmd, desired)

    def fetch_vin(self):
        """Get the vin from the main api or return none."""
        result = self.vin()
        if result == None:
            apiResponse = requests.get(BaseUrl + "/api/vehicle/vin")
            vin_data = apiResponse.json()
            vdata = vin_data.get("vin")
            if len(vdata) == 17:
                Utils.pushLog(f"VIN received {vdata}")
                result = vdata
            else:
                Utils.pushLog(f"Invalid VIN received {vdata}")
        else:
            Utils.pushLog(f"Using VIN {result}")

        return result

    def vin_received(self, vin: str):
        Utils.pushLog(f"Processing VIN {vin}")
        result = f"Success - Processing VIN {vin}"
        self.vinreset = False
        if self.iotStatus == Iot_Status.VEHICLE_RECORDS_NOT_RECEIVED:
            # Is the user trying to enter a corrected VIN?
            if vin != self.vin():
                # clear old vin
                self.failed_vin = self.vin()
            self.vinreset = True

        # Set status so we start processing in other thread.
        if self.check_vin(vin) is not None:
            self.update_status(Iot_Status.VIN_ENTERED, "VIN processing.")
            self.process_new_vin_needed = True
        else:
            result = f"Failure - Exisiting VIN {self.vin}"
        return result

    def tcu_received(self, tcu: dict):
        Utils.pushLog(f"Processing TCU {tcu}")
        result = f"Success - Processing TCU {tcu}"
        # Populate the ConfigParser with data from the dictionary
        if self.configParser.__contains__("TCU") is False:
            self.configParser["TCU"] = {}
        for key, value in tcu.items():
            self.configParser.set("TCU", key, value)
        self.saveConfig()
        # set flag register needed to send needed
        self.tcu_update = True
        return result


    def tcu(self) -> dict:
        """Not just the imei, but all related data set by main"""
        try:
            result = self.configParser["TCU"]
            if result == {}:
                result = None
        except:
            # TCU not recorded
            self.configParser["TCU"] = {}
            result = None
        return result

    def enableChatty(self, payload):
        print("enableChatty", payload)
        response = {}

        if payload is None:
            payload = {}

        if self.configCheck.get_key("States", "chatty_mode", "False") == "True":
            # Check if timer is different
            self.cfg["chatty_expires"] = payload.get("expires", time.time() + 200)  # 4 minutes
            response["result"] = f"{self.cfg['chatty_expires']}"
        else:
            self.configCheck.set_key("States", "chatty_mode", "True")
            self.cfg["chatty_expires"] = payload.get("expires", time.time() + 200)
            response["result"] = f"{self.cfg['chatty_expires']}"
        print(response)
        return response

    def disableChatty(self, payload=None):
        """payload is so can be called as a remote method"""
        response = {}
        try:
            if self.configCheck.get_key("States", "chatty_mode", "False") == "True":
                self.configCheck.get_key("States", "chatty_mode", "False")
                self.saveConfig()
                self.cfg["chatty_expires"] = None
                response["result"] = "Chatty disabled"
            else:
                response["result"] = "Chatty already disabled"

            return response
        except Exception as err:
            print("disableChatty err", err)

    def run_remote_method(self, method_name, payload):
        if payload is None:
            payload = {}
        try:
            msg = f"run_remote_method start {method_name} {payload}"
            print(msg)
            self.log(msg)
            response_code = 500
            response_message = "Standard Response"
            if method_name in ALLOWED_METHODS:
                try:
                    if hasattr(self, method_name):
                        # Run local methods
                        result = getattr(self, method_name)(payload)
                        response = {
                            "remoteStatus": 200,
                            "command": method_name,
                            "response": result,
                        }
                        response_code = 200
                    else:
                        # Do something else
                        response = {
                            "remoteStatus": 404,
                            "command": method_name
                        }
                        response_code = 404
                    return response_code, response
                except Exception as err:
                    self.log("run_remote_method err", 'error')

            elif method_name.lower() == "apirequest":
                print('Enter apirequest')
                request_method = {}
                request_body = {}
                request_url = ""
                HEADER = {}
                try:
                    print("api request", method_name, payload)
                    request_method = APIMethods(payload["method"])
                    request_url = payload["url"]
                    request_body = payload["body"]
                    print("request", request_method.name.lower())
                    print("url", request_url)
                    print("body", request_body)
                    HEADER = {
                        "source": "platform",
                        "id": str(payload.get("id", 1)),
                        "req_ts": str(int(time.time() * 1000)),
                    }
                # except Exception as err:
                #     Utils.pushLog(f"apirequest 1 err: {err}")
                # try:
                    response = getattr(requests, request_method.name.lower())(
                        "http://127.0.0.1:8000" + request_url,
                        json=request_body,
                        headers=HEADER,
                        timeout=3000,
                    )

                    response_code = 200
                    c_response = {
                        "remoteStatus": response.status_code,
                        "response": response.json(),
                    }
                except Exception as err:
                    Utils.pushLog(f"apirequest 2 err: {err}")
                    response_code = (
                            200  # Still ok to platfrom but remoteStatus is timeout
                        )
                    c_response = {"remoteStatus": 408, "response": "Request Timeout"}
                print("####  run_remote_method response", c_response)
                self.TWIN_TELEMETRY_TIME = (
                    time.time() - self.cfg.get("TWIN_INTERVAL", 600) + 0.6
                )
                self.enableChatty({})
                return response_code, c_response

            elif method_name.lower() == "devicereset":
                Utils.pushLog("@@ reset {method_name} {payload}")
                print(f"Will RESTART IOT {method_name} Command: ")
                # Any reset clears a transfer failure
                self.configCheck.set_key('Platform', 'transfer_failed', '0')
                incl = payload.get('include', False)
                # incl = False  # TESTING
                if incl is not False:
                    self.log(f"Reset patch parameters included {incl}")
                    if 'cert' in incl:
                        # self.get_registrations()
                        self.configCheck.set_key("States", "provisioned", "False")
                        self.configCheck.set_key("States", "configured", "False")
                        self.configCheck.set_key("Device", "assigned_hub", "")
                        self.want_cert = True
                        self.saveConfig()
                        self.update_status(Iot_Status.GETTING_VEHICLE_RECORDS, "Pass though the start procedures.")
                        print("Heading back to Get Registrations")
                    if 'data' in incl:
                        self.clear_twin_on_platform()
                        api = BaseUrl + "/api/system/datareset?are_you_sure=true"
                        response = requests.put(api)
                        self.log(response.json())
                        if response.status_code != 200:
                            self.logger.error(f"ERROR in DATA RESET {response.status_code}")
                            response_message = Message(
                                json.dumps({"message": "ERROR in DATA RESET", "level": "CRITICAL"})
                            )
                        else:
                            response_message = Message(
                                json.dumps({"message": "DATA RESET success", "level": "INFO"})
                            )
                Utils.pushLog(f"####  run_remote_method response {response_message}")
                return response_code, response_message

            elif method_name.lower() == "checkinsecurity":
                Utils.pushLog("@@ checkinsecurity {method_name} {payload}")
                response_code = (
                        400  # Still ok to platfrom but remoteStatus is timeout
                    )
                c_response = {"response": "CheckInSecurity Not Implemeted"}
                Utils.pushLog(f"####  run_remote_method response {c_response}")
                return response_code, c_response

            else:
                Utils.pushLog(f"Action {method_name} {payload}")
                response_code = (
                        400  # Still ok to platfrom but remoteStatus is timeout
                    )
                c_response = {"response": f"{method_name} Not Implemeted {method_name.lower()}"}
                Utils.pushLog(f"####  run_remote_method response {c_response}")
                return response_code, c_response
        except Exception as err:
            print("err - run_remote_method: ", err)
            return 200, {"remoteStatus": 500, "response": err}

    def on_message_received(self, message):
        self.log(f"on_message_received: {message}",'debug')

        # BAW111   print(dir(message))
        # BAW111   print("the data in the message received was ")
        # BAW111   print(message.data)
        # BAW111   print(type(message.data))
        # BAW111   print("custom properties are")
        # BAW111   print(message.custom_properties)
        # BAW111   print(type(message.custom_properties))
        # BAW111   print("content Type: {0}".format(message.content_type))

        payload = json.loads(message.data)
        print("Message received @@@ Payload = ", payload)
        # Check if it is a command
        if "command" in payload:
            command = payload.get("command")
            print("Command: ", command)
            method_name = command.get("name", "NA")
            method_payload = command.get("parameters", {}) # BAW
            print("STart Message based command:", method_name, method_payload)

            response_code, payload = self.run_remote_method(method_name, method_payload)
            print("Result Message based command:", response_code, payload)

        else:
            # Regular message ?
            response_code = "Other messages, not handled yet!"
        self.deviceClient.send_method_response(response_code)
        #else:
        #    print("Can not respond due to Locked device!")


    def on_method_received(self, method_request):
        try:
            self.log(f"on_method_received: {method_request}", 'debug')
            try:
                print("on_method_received Method Request:", method_request)
                print("on_method_received dir", dir(method_request))
                print("on_method_received name", method_request.name)
                print("on_method_received request id", method_request.request_id)
                print("on_method_received payload", method_request.payload)

                method_name = method_request.name
                pok = True
                try:
                    parameters = method_request.payload["parameters"]
                    parameters["id"] = method_request.request_id
                    self.log(f"parameters: {parameters}")
                except:
                    msg = f"on_method_received parameters request failed"
                    self.log(msg)
                    method_response = MethodResponse.create_from_method_request(
                    method_request, 409, msg)
                    pok = False

                # Check if it is a command
                if "command" in method_name and pok is True:
                    command = method_request.payload.get("name")
                    print("Command: ", command)
                    print("Payload: ", method_request.payload)
                    method_payload = method_request.payload.get("parameters", {})
                    print("STart Method based command:", command, method_payload)

                    response_code, payload = self.run_remote_method(command, method_payload)
                    print("Result Method based command:", response_code, payload)
                    method_response = MethodResponse.create_from_method_request(
                        method_request, response_code, payload
                )
                else:
                    # Regular message ?
                    msg = "Other messages, not handled yet!"
                    method_response = MethodResponse.create_from_method_request(
                        method_request, 409, msg
                    )
                    self.log(msg, 'error')

            except Exception as err:
                msg = f"err - on_method_received: {err}"
                method_response = MethodResponse.create_from_method_request(
                    method_request, 409, msg
                )
                self.log(msg, 'error')
            self.deviceClient.send_method_response(method_response)

        except Exception as err:
            msg = f"on_method_received error: {err}"
            self.log(msg, 'error')

    def checkChatty(self):
        if self.configCheck.get_key("States", "chatty_mode", "False") == "True":
            expires = self.cfg.get("chatty_expires", None)

            if expires == '' or expires is None or time.time() > expires:
                self.configCheck.set_key("States", "chatty_mode", "False")
                self.saveConfig()
                self.cfg["chatty_expires"] = None
                self.twin_high_interval = False  # if expired
                Utils.pushLog("chatty expired")

    def store_telemetry(self, data_line):
        """Save for a bulk message"""
        line = json.dumps(data_line)
        print("self.m1_bundle_cnt = ", self.m1_bundle_cnt, "Storing bulk", line)
        self.m1_lock.acquire()
        try:
            m1_bulk_store.critical(line)  # Using logging to rotate files
        except Exception as err:
            Utils.pushLog(f"check_m1_for_new_data err: {err}")
        self.m1_lock.release()
        self.m1_bundle_cnt += 1

    def check_m1_for_new_data(self):
        if self.check_counter >= 30:
            # Check telemetry timer
            print("checking M1 while ", self.iotStatus)
            self.check_counter = 0
        else:
            self.check_counter += 1
        if (
            self.M1_TELEMETRY_TIME + self.cfg.get("TELEMETRY_INTERVAL", 600)
            < time.time()
        ):
            # See if gps is avaliable
            self.iot_telemetry.get_fresh_gps()

            # Get telemetry data
            t_data = self.iot_telemetry.get_m1_telemetry()

            # Check if data is empty
            if t_data.get("data", {}) != {}:
                try:
                    print(t_data)
                    if self.iotStatus is Iot_Status.CONNECTED:
                        # Send telemetry - or bulk if it is built up already
                        if self.send_m1_to_platform_check_flag:
                            # Startup check
                            self.m1_lock.acquire()
                            try:
                                self.send_m1_bulk_telemetry()
                            except Exception as err:
                                Utils.pushLog(f"check_m1_for_new_data 1 err: {err}")
                            self.m1_lock.release()

                        if self.m1_bundle_cnt >= 1:  # if we have been storing bulk
                            print("Found BULK data to send")
                            # Store the current message to go with the bulk
                            self.store_telemetry(t_data)
                            self.m1_lock.acquire()
                            try:
                                # Send the bundled messages
                                if self.send_m1_bulk_telemetry():
                                    # if sent then reset the count so next message will be individual
                                    self.m1_bundle_cnt = 0
                            except Exception as err:
                                Utils.pushLog(f"check_m1_for_new_data 2 err: {err}")
                            self.m1_lock.release()
                        elif not self.send_telemetry(json.dumps(t_data)):
                            # the individual message send failed
                            # start saving this as a bulk message
                            self.store_telemetry(t_data)
                    else:
                        # not connected - save to bulk message
                        self.store_telemetry(t_data)

                    self.M1_TELEMETRY_TIME = time.time()
                except Exception as err:
                    Utils.pushLog(f"check_m1_for_new_data 3 err: {err}")

                # Uncomment the else to see the loop ignoring empty set
            # else:
            #      # Ignore this message
            #     print("Ignoring empty telemetry Main")


    def check_twin_for_new_data(self):
        '''Check if new twin data has to be patched to the TWIN.'''

        # Check telemetry timer
        if self.iotStatus == Iot_Status.CONNECTED:
            # Get telemetry data
            # try:
            t_data = self.iot_telemetry.build_twin_telemetry()

            if t_data != {'requests': []}:
                Utils.pushLog(f'check_twin_for_new_data: {json.dumps(t_data, indent=4)}')

                # TODO: Check if this is needed anywhere else
                # TODO: Can we prevent null values being sent from main
                # TODO: Can we only send the changed stuff for the request
                # TODO: Make sure all requests get emitted

                # TODO: Check when this fails and handle failure
                self.deviceClient.patch_twin_reported_properties(
                    remove_empty_elements(t_data)
                )

                Utils.pushLog('check_twin_for_new_data: twin patch successful')

                self.TWIN_TELEMETRY_TIME = time.time()
                self.twin_high_interval = False # if there was data forcing faster upload
                self.t_data_sent = t_data  # update so we don't resend.
                self.twin_update_needed = False

            # except Exception as err:
            #     Utils.pushLog(f"build_twin_telemetry {err}")
            #     self.checkChatty()
            #     t_data = {}

        else:
            print("No Twin Patching while ", self.iotStatus)

    def store_m2_event(self, data_line):
        """Store M2 in it's own set of rotating files."""
        line = json.dumps(data_line)
        print("self.m2_bundle_cnt = ", self.m2_bundle_cnt, "Storing M2 bulk", line)
        m2_bulk_store.critical(line)  # Using logging to rotate files
        self.m2_bundle_cnt += 1

    def check_m2_event(self, i_event):
        """Check and react to the m2 event - including startup"""
        if i_event.event == RVEvents.SERVICE_START:
            # the ui has told us it just restarted
            # Note that we need to send the desired M2 events from the main loop
            self.send_m2_to_main_needed_flag = True
        try:  # we never want this call from main service to lock and not release
            # Put data into telemtery for next send ~5 sec
            self.iot_telemetry.check_twin(
                i_event.event, i_event.instance, i_event.value
            )
            self.iot_telemetry.check_m2(i_event.event, i_event.instance, i_event.value)
            # Handle Bulk store Here if offline
            if self.iotStatus is not Iot_Status.CONNECTED:
                # If time expired
                if (
                    self.M2_TELEMETRY_TIME + self.cfg.get("M2_TELEMETRY_INTERVAL", 5)
                    < time.time()
                ):
                    if self.iot_telemetry.m2toBeReported != {}:
                        m2_msg = self.iot_telemetry.build_m2_telemetry()
                        self.store_m2_event(m2_msg)
                        self.M2_TELEMETRY_TIME = time.time()
        except Exception as err:
            Utils.pushLog(f"Checking m2 error {err}")

    def send_floorplan_to_main(self):
        flr_plan = self.configCheck.get_key("Device","floor_plan")
        if flr_plan is not None and flr_plan != "VANILLA":
            #  TODO Build up the data to send - not recreate
            try:
                # see if we have option codes
                optionCodes = self.configCheck.get_key("Device", "option_codes")
                if optionCodes != "" and optionCodes != None:
                    datatosend = json.dumps({"floorPlan": flr_plan,
                                            "optionCodes": optionCodes})
                else:
                    datatosend = json.dumps({"floorPlan": flr_plan})
                try:
                    t_filename = self.configCheck.get_key("OTA", "telemetry_file")
                    if t_filename is not None:
                        if optionCodes != "" and optionCodes != None:
                            datatosend = json.dumps({"floorPlan": flr_plan,
                                        "optionCodes": optionCodes,
                                        "telemetryFile": t_filename})
                        else:
                            datatosend = json.dumps({"floorPlan": flr_plan,
                                         "telemetryFile": t_filename})
                except Exception as err:
                    Utils.pushLog(f"floorplan send request err {err}")
                    return

                Utils.pushLog(f"floorplan sending to flooplan {datatosend}")
                apiResponse = requests.put(
                    BaseUrl + "/api/system/floorplan",
                    data=datatosend
                )
                Utils.pushLog(f"floorplan sent to main {apiResponse}")
            except Exception as err:
                # logger.error(repr(err))
                # Utils.pushLog(f'floorplan fail to main {flr_plan}, {repr(err)}')
                Utils.pushLog(f'floorplan to main failed: {flr_plan}  {err}')
        else:
            Utils.pushLog(f"floorplan not sent to main {flr_plan}")

    def log(self, msg: str, level: str = 'info'):
        Utils.pushLog(msg, level)

    def exit_log(self, msg):
        # Create or open file in append mode
        with open(_env.log_file_path("iot_main_exit.log"), "a") as f:
            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Append the timestamped message to the file
            f.write(f"[{timestamp}] {msg}\n")

    def main_loop(self):
        self.enableChatty(payload={})  # Start the chatty timer - report at startup
        while (self.vin() is None or self.ota_control is None or self.iot_telemetry is None)  and self.run is True :
            try:
                # Nothing to do until we have the VIN
                Utils.writeLogs()
                self.state_check()  # Move to VIN needed if new
                time.sleep(5)
            except KeyboardInterrupt:  # Still need to break out
                    print("Exiting...")
                    self.log(f"RUN FALSE -> Mini MainLoop Exiting KeyboardInterrupt")
                    self.run = False
            #self.check_m2_event(event_vin)
            self.latest_events()  # Get the latest
            self.iot_telemetry.last_reported_daily = time.time()  # 24hr
            self.check_counter = 30  # Helper cnt
            self.mainLoopCounter = 600
            # self.bundle_cnt= 0  # We can bundle messages that don't need to be sent immediately
        Utils.writeLogs()
        try:
            while self.run is True:
                #print("Looping??")
                self.mainLoopCounter += 1
                if self.iotStatus is not Iot_Status.CONNECTED:
                    print("Not connected - loop1")
                    self.not_connected_cnt += 1
                self.state_check()  # New

                if self.configCheck.get_key("States", "configured", "False") == "True":
                    try: # Catch exceptions that are killing us
                        #print('Main1')
                        try:
                            if self.mainLoopCounter > 60:
                                self.mainLoopCounter = 0
                                self.log(f"MainLoop Marker: {self.iotStatus.name}")  #

                            #print('Main2')
                            if self.send_m2_to_main_needed_flag and self.iot_telemetry is not None:
                                self.send_floorplan_to_main()
                                self.iot_telemetry.send_events_to_main_service()
                                #self.ota_control.re_init() # get these new setting from config
                                self.send_m2_to_main_needed_flag = False
                            # Slow down the main loop on a mode change
                            if self.ONLINE_CHANGE_FLAG:
                                time.sleep(10)
                                self.ONLINE_CHANGE_FLAG = False
                            self.check_m1_for_new_data()
                        except Exception as err:
                            Utils.pushLog(f'Main Loop M1 err: {err}')
                            Utils.writeLogs()

                        #print('Main4')
                        if self.iot_telemetry is not None:
                            if self.iotStatus is Iot_Status.CONNECTED:
                                # CHeck daily
                                #print('Main5')
                                try:
                                    if self.iot_telemetry.last_reported_daily + int(self.cfg.get("FULL_EVENT_INTERVAL", 86400)) <= time.time():
                                        #print('Main5a')
                                        self.iot_telemetry.m1LastReported = {}  # Clear old data so new will be sent
                                        self.latest_events()  # Get the latest
                                        self.iot_telemetry.last_reported_daily = time.time()
                                except Exception as err:
                                    Utils.pushLog(f'Main Loop daily err: {err}')
                                    Utils.writeLogs()
                                # If there is new M2 data

                                #print('Main6')
                                try:
                                    if (
                                        self.M2_TELEMETRY_TIME + self.cfg.get("TELEMETRY_INTERVAL", 5)
                                        < time.time()
                                    ):
                                        if self.iot_telemetry.m2toBeReported != {}:
                                            m2_msg = self.iot_telemetry.build_m2_telemetry()
                                            if self.send_telemetry(
                                                body=json.dumps(m2_msg),
                                                bulk_flag=False,
                                                msg_type=MESSAGE_TYPE_CRITICAL,
                                            ):
                                                self.M2_TELEMETRY_TIME = time.time()
                                except Exception as err:
                                    Utils.pushLog(f'Main Loop M2 report err: {err}')
                                    Utils.writeLogs()
                                # if we have been storing M2 bulk
                                #print('Main7')
                                if self.m2_bundle_cnt > 1 or self.send_m2_to_platform_check_flag:
                                    # Send the bundled messages - they are not sent in bulk anywhere else
                                    if self.send_m2_bulk_telemetry():
                                        # if sent then reset the count for the M2 bundled
                                        self.m2_bundle_cnt = 0
                                # Check if there are updates to the twin related data

                                #print('Main7a')
                                if self.iot_telemetry.update_active_alerts() is True:
                                    self.twin_update_needed = True # This stuff sends quicker

                            # if self.twin_update_needed is True and self.configCheck.get_key("States", "chatty_mode", "False") == "True":
                            #     self.twin_update_needed = False
                            #     # check and send twin if needed
                            #     #print('Main8')
                            #     try:
                            #         self.check_twin_for_new_data()
                            #         self.checkChatty()
                            #     except Exception as err:
                            #         Utils.pushLog(f'Main Loop twin 1 err: {err}')
                            #         Utils.writeLogs()
                            # else:
                                # Single timeout test
                            try:
                                if (
                                    self.TWIN_TELEMETRY_TIME
                                    + self.cfg.get("TWIN_INTERVAL", 600)
                                    <= time.time()
                                ) or \
                                ((
                                    self.TWIN_TELEMETRY_TIME
                                    + self.cfg.get("CHATTY_TWIN_INTERVAL", 2)
                                    <= time.time()
                                ) and self.configCheck.get_key("States", "chatty_mode", "False") == "True"):
                                    # check and send twin if needed
                                    self.check_twin_for_new_data()
                                    self.checkChatty()
                            except Exception as err:
                                Utils.pushLog(f'Main Loop twin 2 err: {err}')
                                Utils.writeLogs()
                        elif self.iot_telemetry is None:
                            Utils.pushLog('Main Loop iot_telemetry is NONE!')
                        # time.sleep(self.cfg['EVENT_INTERVAL'])  # increased for Initial version
                        Utils.writeLogs()
                        time.sleep(0.5)  # Need some off time - we are not the only process running.
                    except KeyboardInterrupt:
                        print("Exiting...")
                        self.log("RUN FALSE -> MainLoop Exiting KeyboardInterrupt")
                        self.run = False
                        Utils.writeLogs()
                    except Exception as err:
                        Utils.pushLog(f'Inside Main Loop err: {err}')
                        Utils.writeLogs()
                        time.sleep(3)  # This can occur rapidly if not throttled
                else:  # Not provisioned yet
                    if self.mainLoopCounter > 600:
                            self.mainLoopCounter = 0
                            self.log(f"Not Provisioned Marker: {self.iotStatus.name} {self.iotStatusMsg}")  #
                    Utils.writeLogs()
                    time.sleep(1)  # increased for Initial version

            msg = "MainLoop Exiting -> Run went false."
            self.log(msg)
            if self.deviceClient is not None:
                self.disconnect()
            Utils.writeLogs()
        except KeyboardInterrupt:
            print("Exiting...")
            msg = "MainLoop Exiting KeyboardInterrupt"
            self.log(msg)
            self.disconnect()
            Utils.writeLogs()
        except Exception as err:
            msg = f'Outside Main Loop err: {err}'
            Utils.pushLog(msg)
            Utils.writeLogs()
        self.iot_telemetry.save_twin_to_file()
        self.exit_log(msg)
        # Always exit all after main.
        signal.raise_signal(signal.SIGINT)


    def clear_twin_on_platform(self):
        # Clear our own twin too
        self.iot_telemetry.clear_twin()
        clearIt = {
            "items": None,
            "climate": None,
            "requests": None,
            "reported": None,
            "reports": None,
            "reset": None,
            "lighting": None,
            "proofToken": None,
            "alerts": None,
            "vehicle": None,
            "ota": None,
            "watersystem": None
        }
        self.log("PATCH Remote twin to clear it !")
        self.deviceClient.patch_twin_reported_properties(clearIt)
        self.clearTwin()


    def create_ini(self):
        # we know this is a new bootup and we don't have all we need
        self.update_status(Iot_Status.CONFIG_NEEDED, f"Create our INI file!")
        #
        self.version_data = VERSION.get('version')

        self.configParser.read_dict(
            {
                "Device": {
                    "vin": "",
                    "assigned_hub": "",
                    "cert_pp": "Winn23",
                    "provisioning_host": "global.azure-devices-provisioning.net",
                    "id_scope": "One0075D1E7",
                    # registration_id"": "",
                    "device_id": "",
                    "platform_env": "",
                    "far_field": "",
                    "csrrequired": "",
                    "devicetype": "",
                    "serialnumber": "",
                    "optioncodes": "",
                    "api_url": "",
                    "software_version": self.version_data,
                },
                "States": {
                    "configured": "False",
                    "chattymode": "False",
                    "chattyexpires": "",
                    "connected": "False",
                    "provisioned": "False",
                },
                "Platform": {
                    "last_id": "",
                    "transfer_failed": "0"
                },
                "OTA": {
                    "allow_auto": "False",
                    "state": "7",
                    "desired": "N",
                    "error_count": "0",
                    "waiting": '',
                    "waiting_ts": '',
                    "telemetry_file": "VANILLA_ota_template.json"
                },
            }
        )
        self.saveConfig()

    def check_api_url(self):
        '''This function checks to see if we are in a temporary environment'''
        result = self.api_url
        if self.configCheck.get_key('Platform', 'temp_api_url') != "":
            expireTime = self.configCheck.get_key('Platform', 'expiration_time', "0.0")
            if expireTime <= datetime.now():
                self.configCheck.set_key('Platform', 'temp_api_url', "")
            else:
                result = self.configCheck.get_key('Platform', 'temp_api_url', "")
        return result

    def proof_token(self):
        if self.check_vin() is None:
            return "No Vin"
        try:
            print(
                f"Exisiting key {self.configCheck.get_key('Device', 'far_field')}"
            )
            ff_ts = int(self.configCheck.get_key("Device","far_field_ts", 0))
            print(
                f"Exisiting key {ff_ts}"
            )
        except Exception as err:
            self.log(f"proof_token getting existing key: {err}")
            self.configCheck.set_key("Device","far_field", "")
            self.configCheck.set_key("Device","far_field_ts", str(
                int(time.time()) - 1200
            ))
            self.saveConfig()

        try:
            # We can only hand this out if the key is in the ignition
            apiResponse = requests.get(BaseUrl + '/api/system/lk/{}/state'.format(
                EventValues.IGNITION_ON
            ), timeout=2)
            if apiResponse.status_code == 200:
                if apiResponse.json().get('active') is False:
                    return EventValues.FAR_FIELD_LOCK
            else:
                return EventValues.FAR_FIELD_LOCK
        except Exception as err:
            self.log(f"proof_token getting ignition: {err}")
            return EventValues.FAR_FIELD_LOCK


        if int(
            self.configCheck.get_key("Device","far_field_ts", 0)
        ) + 900 < int(time.time()):
            self.configCheck.set_key("Device","far_field", str(
                uuid.uuid1())
            )
            self.configCheck.set_key("Device","far_field_ts", str(
                int(time.time()))
            )
            self.saveConfig()
            # make a UUID based on the host ID and current time
            print(
                f"Guid created = {self.configCheck.get_key('Device','far_field')}"
            )
        # send token to the platform twin
        self.iot_telemetry.add_other_twin_data(
            "proofToken", self.configCheck.get_key("Device","far_field")
        )
        self.twin_update_needed = True  # tell it so update twin soon
        # Make sure this update goes soon
        self.configCheck.set_key("States", "chatty_mode", "True")

        return self.configCheck.get_key("Device","far_field")

    def ota_restart(self):
        # Check before we do it?
        self.exit_log("OTA endpoint hit!")
        result  = {'result': 'OTA not ready.'}  # We can't do this if we are not ready
        with self.ota_control.stateLock:  # Let's ensure the OTA thread is not running
            if self.ota_control.status == OTAStatus.USER_APPROVAL:
                # Check if build is waiting
                if os.path.isfile(_env.storage_file_path("latest_bld")):
                    # Now to write the OTA is OK file
                    with open(_env.storage_file_path('OK'), 'w') as f:
                        f.write('Ok OTA')
                    # self.run = False  Don't quit with cron job service.
                    result  = {'result': 'OTA preparing to start.'}
                    self.ota_control.update_ota_state(OTAStatus.OTA_INSTALLING, "OTA service file written.")
            else:
                self.log(f"ota_restart denied for OTA_STATUS: {self.ota_control.status}")
            self.log(f"ota_restart -> {result}")
        return result

    def iot_restart(self):
        self.log("RUN FALSE -> iot_restart api call")
        self.run = False
        result  = {'result': 'IOT preparing to start.'}
        return result

    def latest_events(self):
        # Call Main for the events
        filtered = []
        try:
            apiResponse = requests.get(BaseUrl + "/coach_events")
            event_data = apiResponse.json()
            #print("Coach Events received", event_data)
            for event in event_data:
                if event['event'] in self.iot_telemetry.m2List:
                    print(f"{RVEvents(event['event']).name} {event['instance']} {event['value']}")
                    self.iot_telemetry.check_m2(event['event'],event['instance'],event['value'])
                    filtered.append(event)
        except:
            Utils.pushLog("Main service did not return latest events.")
        return filtered


# Set up FastAPI and read
app = FastAPI(
    title="WinnConnect Coach IOT API",
    description="API with connections to and messgaes for the IOT HUB",
    version="1.0",
)

# app.test = {}
app.iot_device_client = None  # Initialize in the startup event

app.include_router(root.router)
app.include_router(notifications.router)
app.taskScheduler = ScheduledFunctionManager(1)  # Holder for ScheduleManager Class object


@app.on_event("startup")
async def startup_event():
    print("Startup")
    # TODO: Review if the approach would be the same as for CAN or Bluetooth to create a Runner

    # Addiition config items now in config parser and save in Iot_config.ini
    app.iot_device_client = IoTHandler()
    app.main_thread = Thread(target=app.iot_device_client.main_loop)
    app.main_thread.start()
    global scheduletask
    scheduletask = asyncio.create_task(app.taskScheduler.check_run())



@app.on_event("shutdown")
async def shutdown_event():
    print("Shutdown")
    # Perform cleanup
    app.iot_device_client.run = False  # End main loop
    time.sleep(2)  # Allow Shutdown
    if app.main_thread.is_alive():
        app.main_thread.join()


if __name__ == "__main__":
    # import cProfile

    # print(f"Have internet {Utils.have_internet()}")

    # profiler = cProfile.Profile()
    # profiler.enable()

    uvicorn.run(
        "wgo_iot_service:app",
        host=_env.bind_address,
        port=_env.iot_service_port,
        # reload=True,
        log_level="error",
        workers=1,
        # limit_concurrency=5
    )
    # profiler.disable()
    # profiler.print_stats(sort='time')
