"""Class and methods to perform most of the OTA Update work."""

import requests
import json
import filecmp
import os
import shutil
from common_libs import environment
from threading import Lock, Thread

from iot_service.utils import Utils,  MIN_LENGTH
from enum import IntEnum
import sys
import time
from iot_service.untar_service import extract_pkg
import configparser
from datetime import datetime
from common_libs.models.common import LogEvent, RVEvents

_env = environment()

MAX_OTA_ERRORS = 3

sys.path.append("../main_service/models/")

import logging


class OTAStatus(IntEnum):
    OTA_INITIALIZING = 0
    OTA_RELEASE_REQUEST = 1
    OTA_DOWNLOAD_PLAN = 2
    OTA_FILES_DOWNLOADING = 3
    OTA_VALIDATION = 4
    USER_APPROVAL = 5
    OTA_INSTALLING = 6  # Done with the service and iot service off
    OTA_COMPLETE = 7
    OTA_CHECKED_OK = 8
    OTA_UNKNOWN = 98  # At initialization tim e- till status is determined - not reported to platform
    OTA_ERROR = 99


class PKGStatus(IntEnum):
    READY = 1
    DOWNLOADING = 2
    DOWNLOADED = 3
    UNCOMPRESSING = 4
    INSTALLING = 5
    MISSING = 98
    ERROR = 99


def check_dir(i_dir):
    """Helper function to make sure a directory exixts"""
    # print(f'CWD = {os.getcwd()}')
    if not os.path.exists(i_dir):
        os.mkdir(i_dir)


class package_status(object):
    def __init__(self, i_iot, i_dict=None):
        """Tracks packages - versions running and waiting , downloaded files"""
        self.iot = i_iot
        if i_dict.get('module') is None:
            self.name = f"{i_dict['module']}_{i_dict['version']}"
        else:
            self.name = f"{i_dict['module']}-{i_dict['version']}"
        if self.name.startswith('-'):
            self.name = 'pkg' + self.name
        self.config_Parser = configparser.ConfigParser()
        filereadresult = self.config_Parser.read(_env.package_file_path(f'{self.name}.ini'))
        try:
            have_ini = filereadresult[0].find(f"{self.name}.ini") != -1
        except Exception as err:
            Utils.pushLog(f"package_status: {err}")
            have_ini = False

        print(f"OTA {_env.package_file_path(self.name)} Have INI-> {have_ini}")
        if not have_ini:
            # we know this is a new bootup and we don't have all we need
            self.config_Parser.read_dict(
                {
                    "package": {
                        "incoming_version": i_dict["version"],
                        "state": PKGStatus.MISSING,
                    }
                }
            )
            self.saveConfig()


    def unpack_to(self, to_dir):
        print(f"Unpack {self.name} to {to_dir}")
        self.config_Parser["package"]["to_dir"] = to_dir
        self.update_state(PKGStatus.UNCOMPRESSING)
        os.chdir(_env.package_file_path())
        extract_pkg(self.name, _env.package_file_path(), to_dir)

    def update_state(self, i_status: PKGStatus):
        self.config_Parser["package"]["state"] = i_status.name
        self.saveConfig()

    def saveConfig(self):
        """Used to store config and provisioning etc between restarts"""
        with open(_env.package_file_path(f'{self.name}.ini'), "w") as configfile:
            self.config_Parser.write(configfile)


class ota_control(object):
    # uri = "https://dev-apim.ownersapp.winnebago.com/api/deviceTypes"
    api_latest = ""  # Get path from the patch  f'{uri}/vdt/releases/latest'
    new_files = []
    release_dict = {"version": "Object Creation - not loaded yet"}
    noChange = True  # No need to do anything
    desired = ""  # Get path from the patch  f'{uri}/vdt/releases/latest'
    current = ""  # Get from IoT_Config ['DEVICE']['software_version']
    waiting_ts = "" # Get from IoT_Config ['OTA']['waiting_ts']
    waiting = ""  # Get from IoT_Config ['OTA']['waiting']
    ota_allowed = False
    error_count = 0
    id = None
    # platform_env = None
    status = OTAStatus.OTA_UNKNOWN
    status_msg = "Object Creation"
    stateLock = Lock()  # Let other threads know method is in use
    otastatusLock = Lock()  # Let other threads know method is in use
    check_is_running = False
    incoming_release_dict = {}

    def __init__(self, i_iot):
        """OTA tracker"""
        self.iot = i_iot
        check_dir(_env.package_file_path())
        with self.stateLock:
            self.status = OTAStatus[self.iot.configCheck.get_key("OTA", "status", OTAStatus.OTA_UNKNOWN.name)]
            if self.status == OTAStatus.OTA_ERROR:
                pass
            elif self.status == OTAStatus.OTA_INSTALLING:
                # Check for the OK file
                if os.path.exists(_env.storage_file_path('OK')) is not True:
                    self.update_ota_state(OTAStatus.OTA_COMPLETE, "After OTA_INSTALLING.")
            else:
                self.check_waiting()

    def set_ota_allowed(self, otaOk: bool = True):
        Utils.pushLog(f"Setting ota allowed: {otaOk}")
        self.ota_allowed = otaOk

    def re_init(self):
        self.id = self.iot.configCheck.get_key("Device", "vin", "Na")
        self.check_waiting()

        Utils.pushLog(f"\n OTA re_init env {self.iot.platform_env()} ")
        try:
            self.prep_cert()
            try:  # to get version from main
                full_ver = Utils.get_from_main('/version')
                self.iot.configCheck.set_key("Device", "software_version", full_ver.get('version'))
                self.iot.saveConfig()
            except Exception as err:
                Utils.pushLog(f"re_init failed to get version from main service: {err}")
            self.current = self.iot.configCheck.get_key("Device", "software_version", "NA")
            self.waiting = self.iot.configCheck.get_key("OTA", "waiting", "No OTA Waiting ")
            self.waiting_ts = self.iot.configCheck.get_key("OTA", "waiting_ts", "0")
            self.iot.iot_telemetry.add_ota_twin_data(
                                "releaseVersionCurrent", self.current)
        except Exception as err:
            Utils.pushLog(f"re_init failed to get version from main. {err}")
            self.current = "NA"
            self.waiting = "No OTA Waiting 1"
            self.waiting_ts = ""
        try:
            self.release_dict = self.load_release_dict("release_info.json")
        except Exception as err:
            Utils.pushLog(f"release_dict failed to find version:  {err}")
            self.release_dict = {"version": "Not Found"}
        try:
            self.incoming_release_dict = self.load_release_dict(
                "incoming_release_info.json"
            )
        except Exception as err:
            Utils.pushLog(f"incoming_release_dict failed to find version:  {err}")
            self.incoming_release_dict = {}

        if self.incoming_release_dict == {}:
            # TODO check if why incoming is missing - should not have been moved yet
            print(f"Using existing release_dict for incoming {self.release_dict}")
            self.incoming_release_dict = self.release_dict
        try:
            self.desired = self.iot.configCheck.get_key("OTA", "waiting", "No OTA Waiting I")
        except Exception as err:
            Utils.pushLog(f"configParser failed to find waiting:  {err}")
            self.desired = "N"
        try:
            self.current = self.iot.configCheck.get_key("Device", "software_version", "NA")
            self.iot.iot_telemetry.add_ota_twin_data(
                                "releaseVersionCurrent", self.current)
        except Exception as err:
            Utils.pushLog(f"configParser failed to find software_version:  {err}")
            self.current = "NA"
        # If packages is not present there will be no release dictionary
        try:
            self.incoming_bld_dir = (
                _env.storage_file_path(f'bld_{self.incoming_release_dict["version"]}')
            )
        except Exception as err:
            self.iot.log(f"incoming_bld_dir: {err}")
            self.incoming_bld_dir = _env.storage_file_path('bld_X') # Set to known bad
        msg = f"Setting in bld dir to {self.incoming_bld_dir}"
        try:
            self.status = OTAStatus[self.iot.configCheck.get_key("OTA", "status", "NA")]
            if self.status == OTAStatus.OTA_ERROR:
                self.ota_event(0)  # Clear the OTA Flag - we are starting fresh after an Error
                self.update_ota_state(OTAStatus.OTA_INITIALIZING, msg)
                try:
                    self.error_count = int(self.iot.configCheck.get_key("OTA", "error_count", "0"))
                except Exception as err:
                    self.iot.log(f"configParser OTA Error Count: {err}")
                    self.error_count = 0
                if self.error_count >= MAX_OTA_ERRORS:
                    # TODO Handle repeating OTA errors
                    self.iot.log(f"OTA Error Count Exceeded: {self.error_count}")
            # else:
            # Leave the status as it is during re-init
        except Exception as err:
            """Unknown should only be with a new unit."""
            msg = f"OTA init {err}"
            self.iot.configCheck.set_key("OTA", "status", OTAStatus.OTA_UNKNOWN.name)
            self.update_ota_state(OTAStatus.OTA_UNKNOWN, msg)


    def update_ota_state(self, i_status: OTAStatus, i_msg: str):
        """Method to save some steps - updating state is always reported to the twin"""
        with self.otastatusLock:
            try:
                self.status_msg = i_msg
                self.status = i_status
                self.iot.configCheck.set_key("OTA", "previous_status", self.iot.configCheck.get_key("OTA", "status"))
                if i_status == OTAStatus.OTA_ERROR:
                    if os.path.exists(_env.storage_file_path('OK')) is True:
                        os.remove(_env.storage_file_path('OK')) # Would never want this to be present
                    self.error_count += 1
                    self.iot.configCheck.set_key("OTA", "error_count", str(self.error_count))
                    # Remove and reinitiate the OTA
                    self.waiting = "No OTA Waiting Err"
                    self.iot.configCheck.set_key("OTA", "waiting", self.waiting)
                    if os.path.exists(_env.storage_file_path("latest_bld")):
                        os.remove(_env.storage_file_path("latest_bld")) # don't want to try to install a bad one
                elif i_status == OTAStatus.OTA_UNKNOWN:
                    self.iot.configCheck.set_key("OTA", "error_count", "0")
                    self.error_count = 0
                self.iot.configCheck.set_key("OTA", "status", i_status.name)
                self.iot.saveConfig()
                if self.iot.iot_telemetry is not None:
                    self.iot.iot_telemetry.add_ota_twin_data("state", self.status.value)
                    self.iot.iot_telemetry.add_ota_twin_data("message", i_msg)
                Utils.pushLog(f"OTA state: {i_status.name}, {i_msg}")
            except Exception as err:
                msg = f'update_ota_state exception {err}'
                self.status = OTAStatus.OTA_ERROR
                Utils.pushLog(msg,'error')


    def get_new_release_doc(self) -> bool:
        '''Retrieve the latest release document, report true if it is new.'''
        msg = f"OTA Download start {self.desired}"
        success = True  # Default to getting the files saying it is new
        try:
            print("get_new_release_doc 1")
            if self.prep_cert() is True:

                print("get_new_release_doc 2  {self.api_latest}")
                result = requests.get(self.api_latest, headers=self.hdr)
                print("get_new_release_doc 3")
                try:
                    if result.status_code == 200:
                        print(json.dumps(result.json(), indent=4))

                        self.incoming_release_dict = result.json()
                        self.save_release_data(
                            self.incoming_release_dict, "incoming_release_info.json"
                        )
                        incoming_version = self.incoming_release_dict.get("version", None)
                        if incoming_version is not None:
                            self.iot.iot_telemetry.add_ota_twin_data(
                                        "releaseVersionFound", incoming_version)
                            self.iot.iot_telemetry.add_ota_twin_data(
                                        "releaseVersionCurrent", self.current)
                            bldName = f'bld_{self.incoming_release_dict["version"]}'
                            self.incoming_bld_dir = (
                                _env.storage_file_path(bldName)
                            )
                            newBldFile = _env.storage_file_path("latest_bld")
                            self.iot.log(f"get_new_release_doc check: current{self.current} waiting {self.waiting} incoming {incoming_version} self.incoming_bld_dir {self.incoming_bld_dir}")
                            # Check that  everything is waiting before we say we don't need to download and  If we are not already running this version
                            if incoming_version != self.current:
                                if  incoming_version != self.waiting or \
                                    os.path.exists(self.incoming_bld_dir) is False or \
                                    os.path.isfile(newBldFile) is False:
                                    try:
                                        for file in self.incoming_release_dict["files"]:
                                            try:
                                                package_tracker = package_status(self.iot, file)
                                                package_tracker.update_state(PKGStatus.READY)
                                            except Exception as err:
                                                msg = f"OTA Package ERROR package_tracker setup {err}"
                                                self.update_ota_state(OTAStatus.OTA_ERROR, msg)
                                        success = True
                                    except Exception as err:
                                        msg = f"OTA Download Twin data ERROR {self.api_latest}, {err}"
                                        self.update_ota_state(OTAStatus.OTA_ERROR, msg)
                                else:
                                    success = False
                            else:
                                success = False
                                msg = "OTA No incoming Version found."
                                self.update_ota_state(OTAStatus.OTA_COMPLETE, msg)
                    else:
                        msg = f"OTA Download Release ERROR {result.status_code}, {result.json()}"
                        self.update_ota_state(OTAStatus.OTA_ERROR, msg)
                except Exception as err:
                    print("get_new_release_doc 3f")
                    msg = f"OTA Download ERROR {result.status_code}, { err}"
                    self.update_ota_state(OTAStatus.OTA_ERROR, msg)
            else:
                msg = "OTA CERT PREP ERROR - not ready"
                self.update_ota_state(OTAStatus.OTA_ERROR, msg)

        except Exception as err:
            print(f"get_new_release_doc url {self.api_latest}")
            msg = f"OTA Get latest ERROR {err}"
            self.update_ota_state(OTAStatus.OTA_ERROR, msg)

        self.iot.log(f"get_new_release_doc result: {success}")
        return success

    def download_file(self, url, save_path, chunk_size=128) -> bool:
        success = False
        try:
            r = requests.get(url, stream=True)
            with open(save_path, "wb") as fd:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)
            success = True
        except Exception as err:
            msg = f"OTA Download file ERROR {save_path}, {err}"
            self.update_ota_state(OTAStatus.OTA_ERROR, msg)
        return success

    def fetch_all(self) -> bool:
        success = True
        self.new_files = []
        # Adding check for disk space - TODO: we can refine this
        # Based on the size of the files to be downloaded and unpacked at this time
        if Utils.check_disk_space() is False:
            msg = "check_state Disk Space Low - returning."
            Utils.pushLog(msg)
            self.status_msg = msg
            #TODO: Push an alert to main service
            msg = f"OTA Downloads fail check disk space {Utils.get_disk_space()}"
            self.update_ota_state(OTAStatus.OTA_ERROR, msg)
            return False
        try:
            file_to_save = "No filename"
            for file in self.incoming_release_dict["files"]:
                package_tracker = package_status(self.iot, file)
                package_tracker.update_state(PKGStatus.DOWNLOADING)
                file_to_save = file.get("name")
                print(f"fetch_all adding file {file_to_save}")
                # Add Package Tracker now
                full_path = _env.package_file_path(file_to_save)
                uri_file = file.get("uri")
                print(f"fetch_all file path {uri_file}")
                if self.download_file(uri_file, full_path):
                    self.iot.log(f"OTA Download OK {file_to_save}")
                    package_tracker.update_state(PKGStatus.DOWNLOADED)
                    self.new_files.append(file_to_save)
                else:
                    # why was it not downloaded - the exception catch these
                    msg = f"OTA Download Fail {file_to_save}"
                    success = False
                    self.update_ota_state(OTAStatus.OTA_ERROR, msg)

        except Exception as err:
            success = False  # Success could have been true for one file.
            msg = f"OTA Downloads fail {file_to_save} {err}"
            self.update_ota_state(OTAStatus.OTA_ERROR, msg)

        return success

    def unpack_new(self) -> bool:
        """Unpack the new files downloaded"""
        success = False
        try:
            for file in self.incoming_release_dict["files"]:
                Utils.pushLog(f'Unpacking new {file["name"]}')
                if 'json' in file['name']:
                    os.chdir(_env.package_file_path())
                    shutil.copy(os.path.join(_env.package_file_path(), file['name']),
                            os.path.join(self.incoming_bld_dir, file['name']))
                    if len(file['name']) > len('ota_template.json'):
                        # Grab this for new telemetry data
                        self.iot.configCheck.set_key("OTA", "telemetry_file", file['name'])
                        self.iot.configCheck.set_key("OTA", "file_dir", self.incoming_bld_dir)
                        self.iot.saveConfig()
                else:
                    package_tracker = package_status(self.iot, file)
                    package_tracker.unpack_to(self.incoming_bld_dir)
            success = True
        except Exception as err:
            success = False
            msg = f"OTA Unpack fail {err}"
            self.update_ota_state(OTAStatus.OTA_ERROR, msg)
        if success is True:
            self.waiting = self.incoming_release_dict["version"]
            self.iot.configCheck.set_key("OTA", "waiting", self.waiting)
            self.iot.configCheck.set_key("OTA", "file_dir", self.incoming_bld_dir)
            self.waiting_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.iot.configCheck.set_key("OTA", "waiting_ts", self.waiting_ts)
            self.iot.saveConfig()
            self.iot.iot_telemetry.add_ota_twin_data(
                "releaseVersionDownloaded", self.incoming_release_dict["version"])
            self.iot.iot_telemetry.add_ota_twin_data(
                     "releaseVersionCurrent", self.current)
        return success

    def compare_versions(self) -> bool:
        """Compare the files - return True if identical"""
        # TODO - dig deeper to understand what changes
        result = False
        if os.path.exists(_env.package_file_path("release_info.json")) is True:
            try:
                #  Check the Version Files
                result = filecmp.cmp(
                    _env.package_file_path("release_info.json"),
                    _env.package_file_path("incoming_release_info.json"),
                )
            except Exception as err:
                self.iot.log(f"OTA compare versions fail {err}",'debug')
                result = False
        return result

    def upgrade_finialize(self):
        """Move the incoming json to the current if needed."""
        try:
            os.replace(
                _env.package_file_path("incoming_release_info.json"),
                _env.package_file_path("release_info.json"),
            )
        except FileNotFoundError:
            pass
        # Update the telemtry
        self.release_dict = self.incoming_release_dict
        # Make sure releaseVersionCurrent is running
        self.iot.iot_telemetry.add_ota_twin_data(
                         "releaseVersionCurrent", self.current)
        self.iot.saveConfig()
        self.ota_event(0)  # Clear the OTA Flag
        msg = "OTA checked after Upgrade."
        self.update_ota_state(OTAStatus.OTA_CHECKED_OK, msg)


    def check_waiting(self):
        '''Used at startup to see if there is an OTA waiting.'''
        newBldFile = _env.storage_file_path("latest_bld")
        self.incoming_bld_dir = "No Dir assigned yet."
        # print(f"\n\n\ncheck_latest_ready running {newBldFile}")
        try:
            if os.path.isfile(newBldFile):
                with open(newBldFile, 'r') as f:
                    i_dir = f.readline()
                if len(i_dir) > 4:
                    waiting = self.iot.configCheck.get_key("OTA", "waiting", "No OTA Waiting 2")
                    if waiting is not None and waiting != "" and  "No OTA Waiting" not in waiting:
                        self.incoming_bld_dir = self.iot.configCheck.get_key("OTA", "file_dir", self.incoming_bld_dir)
                        if os.path.exists(self.incoming_bld_dir) is True:
                            if self.iot.configCheck.get_key("OTA", "waiting") != i_dir[4:]:
                                self.waiting = i_dir[4:]
                                self.iot.configCheck.set_key("OTA", "waiting", self.waiting)
                                self.waiting_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                self.iot.configCheck.set_key("OTA", "waiting_ts", self.waiting_ts)
                                self.iot.saveConfig()
                                msg = "OTA ready to install Awaiting User Approval."
                            else:
                                msg = "OTA already waiting."
                            self.update_ota_state(OTAStatus.USER_APPROVAL, msg) # either way we are waiting for user approval
                            self.ota_event(1)  # Ensure Main knows it is waiting
                        else:
                            # Nothing waiting
                            self.waiting = "No OTA Waiting 5"
                            self.iot.configCheck.set_key("OTA", "waiting", self.waiting)
                            result, msg = self.ota_event(0)  # Ensure clear OTA Flag
                else:
                    # Nothing waiting
                    self.waiting = "No OTA Waiting 6"
                    self.iot.configCheck.set_key("OTA", "waiting", self.waiting)
                    result, msg = self.ota_event(0)  # Ensure clear OTA Flag
        except KeyError:
            self.waiting = "No OTA Waiting 7"
            self.iot.configCheck.set_key("OTA", "waiting", self.waiting)
            result, msg = self.ota_event(0)  # Ensure clear OTA Flag

        self.iot.log(f"OTA check_waiting dir is: {self.incoming_bld_dir} {self.waiting}")


    def check_latest_ready(self, msg: str = "OTA checked after processing."):
        '''Check if ready to install OTA'''
        newBldFile = _env.storage_file_path("latest_bld")
        # print(f"\n\n\ncheck_latest_ready running {newBldFile}")
        if os.path.isfile(newBldFile):
            self.check_waiting()
        else:
            self.upgrade_finialize()  # Move in the incoming


    def ota_event(self, active):
        Utils.pushLog(f"ota_event send to main: {active}")
        result = True
        try:
            if active == 1:
                waiting = 'True'
            else:
                waiting = 'False'
            main_ota_state = {'waiting': waiting,
                 'version': self.waiting,
                 'checked': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            apiResponse1 = Utils.put_to_main("/ota_status",
                                            data=main_ota_state
                                            )
            Utils.pushLog(f"ota_event state to main: {apiResponse1}")

            event = LogEvent(
                        timestamp=time.time(),
                        event=RVEvents.OTA_UPDATE_RECEIVED,
                        instance=1,
                        value=active,
                    )
            apiResponse = Utils.put_to_main("/event_log",
                                            data=event.dict()
                                            )
            msg = f"OTA update event {active} response {apiResponse}"
            # move on to APPROVAL after Validation
        except Exception as err:
            # TODO Need to handle IOT only running and proceed if UI service is not
            result = False
            msg = f"OTA update event fail main service timeout"
        return result, msg


    def check_state(self):

        #Utils.pushLog("OTA Disabled for testing")
        #time.sleep(30) # WHOA OTA  -  BOY
        #return
        """Check and progress through the OTA process states"""
        msg = "check_state waiting."
        self.status_msg = msg
        Utils.pushLog(msg)
        time.sleep(30) # WHOA OTA  -  BOY
        msg = "check_state starting."
        Utils.pushLog(msg)

        if self.check_is_running is True:
            msg = "check_state already running - returning."
            Utils.pushLog(msg)
            self.status_msg = msg
            return

        while self.ota_allowed is not True or self.id is None:
            msg = "check_state OTA not allowed yet - but ota called for - returning."
            Utils.pushLog(msg)
            self.status_msg = msg
            return

        with self.stateLock:
            self.check_is_running = True
            try:
                self.iot.twin_update_needed = True
                restartit = False
                done = False
                while not done:
                    if self.status == OTAStatus.OTA_RELEASE_REQUEST:
                        result, msg = self.ota_event(0)  # Reset The OTA Flag before starting the process
                        result = self.get_new_release_doc()
                        if not result and self.status != OTAStatus.OTA_ERROR:
                            self.iot.log("OTA Downloads skipping due to no new document.")
                            msg = "OTA Downloads match previous - no new document."
                            self.check_latest_ready(msg)
                            self.iot.iot_telemetry.add_ota_twin_data(
                                "releaseVersionDownloaded", self.incoming_release_dict["version"])
                        else:
                            self.update_ota_state(OTAStatus.OTA_DOWNLOAD_PLAN, msg)
                    elif self.status == OTAStatus.OTA_DOWNLOAD_PLAN:
                        result = self.compare_versions()
                        if not result:
                            self.iot.iot_telemetry.add_ota_twin_data(
                                     "releaseVersionCurrent", self.current
                                 )
                            self.iot.iot_telemetry.add_ota_twin_data(
                                    "releaseVersionFound", self.incoming_release_dict["version"]
                                )
                            self.iot.log("OTA Downloads ready to start.")
                            msg = "OTA Downloads ready to start processing."
                            self.update_ota_state(OTAStatus.OTA_FILES_DOWNLOADING, msg)
                        else:
                            self.iot.log("OTA Downloads skipping due to no changes.")
                            msg = "OTA Downloads skipping due to no change detected."
                            self.check_latest_ready(msg)
                    elif self.status == OTAStatus.OTA_FILES_DOWNLOADING:
                        result = self.fetch_all()
                        if result is True and len(self.new_files) >= 1:
                            self.iot.log(f"New Files: {self.new_files}")
                            self.update_ota_state(OTAStatus.OTA_VALIDATION, "New files downloading.")
                            result, msg = self.ota_event(0)  # Reset The OTA Flag
                            if result is not True:
                                Utils.pushLog(msg)
                                # TODO - decide if we stop becuase MAIN is not responding
                                ## self.update_ota_state(OTAStatus.OTA_ERROR, msg)
                        else:
                            if self.status != OTAStatus.OTA_ERROR:
                                self.iot.log(
                                    f"OTA Downloads skipping due to no new files found."
                                )
                                msg = "OTA Downloads skipping due to no new files found."
                                self.check_latest_ready(msg)
                    elif self.status == OTAStatus.OTA_VALIDATION:
                        bldName = f'bld_{self.incoming_release_dict["version"]}'
                        self.incoming_bld_dir = (
                            _env.storage_file_path(bldName)
                        )
                        # Remove older build dirs
                        Utils.remove_BLD_dirs(bldName)
                        check_dir(self.incoming_bld_dir) # create new build dir if not present
                        if self.unpack_new():
                            # Save the new build name in latest_bld
                            newBldFile = _env.storage_file_path("latest_bld")
                            with open(newBldFile, 'w') as f:
                                f.write(bldName)
                            self.update_ota_state(OTAStatus.USER_APPROVAL, f"New files unpacked: {bldName}")
                        else:
                            self.update_ota_state(OTAStatus.OTA_ERROR, "OTA_VALIDATION files unpacking failed.")
                            done = True  # bail
                    elif self.status == OTAStatus.USER_APPROVAL:
                        done = True  # bail
                        result, msg = self.ota_event(1)  # This should already be sent to get here
                    elif self.status == OTAStatus.OTA_INSTALLING:
                        if os.path.exists(_env.storage_file_path('OK')) is not True:
                            time.sleep(60) # We should not see this except after a reboot
                            self.update_ota_state(OTAStatus.OTA_ERROR, "We should not be here without the OK file.")
                        done = True  # We are waiting to OTA Service to check that file
                    elif self.status == OTAStatus.OTA_COMPLETE:
                        if not self.compare_versions():  # If not the same version
                            self.check_latest_ready()
                        if self.status != OTAStatus.USER_APPROVAL:
                            done = True
                    elif self.status == OTAStatus.OTA_ERROR:
                        done = True
                    elif self.status == OTAStatus.OTA_CHECKED_OK:
                        done = True
                    elif self.status == OTAStatus.OTA_UNKNOWN:
                        """Initialization usually"""
                        done = True
                    elif self.status == OTAStatus.OTA_INITIALIZING:
                        """Initialization always :-)"""
                        done = True
                    else:  # For completeness
                        self.update_ota_state(OTAStatus.OTA_ERROR, f"We should not be here! What was the status: {self.status}")
                        done = True
                self.check_is_running = False
            except Exception as err:
                self.iot.iotStatusMsg = "check_state failed - exception"
                Utils.pushLog(f"check_state exception  in {self.status.name} ! {err}")
                self.check_is_running = False
            Utils.pushLog(msg)
            self.iot.iotStatusMsg = msg
            if restartit is True:
                msg = "OTA compare version ending service!"
                print(msg)
                Utils.pushLog(msg)
                # Let the service restart us
                self.iot.run = False  # End main loop
                time.sleep(5) # See if Run will write logs while we wait
            self.iot.twin_update_needed = True

        return 0

    def prep_cert(self) -> str:
        result = False
        if len(self.id) < MIN_LENGTH:
            return result
        if len(self.iot.platform_env()) < MIN_LENGTH:
            return result
        """Get the public cert and remove linefeeds"""
        cert_name = f'{self.iot.platform_env()}-{self.id}.pem'
        print("\n\nprep_cert\n\n",cert_name)
        #cert_file = _env.certs_path(f'{self.iot.platform_env()}-{self.id}.pem')
        cert = ""
        if Utils.has_secret(cert_name):
            raw = line = Utils.get_secret(cert_name)
            if type(raw) is not str:
                raw = line.decode()
            cert = (
                raw.split("-----BEGIN CERTIFICATE-----")[1]
                .replace("\n", "")
                .split("-----END CERTIFICATE-----")[0]
            )
            result = True
            # #print(f'prep_cert {cert}')
        else:
            print(f"Cert file not found: {cert_name}")
            raise FileNotFoundError
        self.hdr = {"Device-Certificate": cert}
        return result

    def save_release_data(self, i_data, i_name):
        """Used to store config and provisioning etc between service restarts"""
        try:
            with open(_env.package_file_path(i_name), "w") as wfile:
                wfile.write(json.dumps(i_data, indent=4))
            self.iot.log(f"OTA save release file OK {_env.package_file_path(i_name)}",'debug')
        except Exception as err:
            self.iot.log(f"OTA save release file err {err}",'debug')

    def load_release_dict(self, i_name):
        """Read the saved dictionary if present"""
        try:
            with open(_env.package_file_path(i_name), "r") as rfile:
                data = json.loads(rfile.read())
        except Exception as err:
            self.iot.log(f"OTA load release file {err}",'debug')
            data = {"version": "NA"}
        return data

    def check_patch(self, ota_cmd, desired):
        self.api_latest = ota_cmd.get("path", "")
        self.desired = desired
        msg = f"OTA patch check desired: {self.desired} vs have: {self.current}"
        self.iot.log(msg)
        if (
            self.api_latest != {}
            and self.desired != self.current and self.desired != self.waiting
        ):
            try:
                # Use the lock for this check and
                with self.stateLock:
                    installing_now = self.status == OTAStatus.OTA_INSTALLING
                    if installing_now is False:
                        self.update_ota_state(OTAStatus.OTA_RELEASE_REQUEST, "Found in Twin Patch! ")
                        self.ota_event(0)  # Reset The OTA Flag before starting the process
                        self.iot.iot_telemetry.add_ota_twin_data(
                            "state", OTAStatus.OTA_RELEASE_REQUEST.value
                        )
                        Thread(target=self.check_state).start()
                        msg = "OTA thread started! Clearing OTA Ready Flag in main."
                        self.iot.log(msg)
                        self.iotStatusMsg = msg
            except Exception as err:
                self.iot.log(f"OTA patch err {err}",'error')
        else:
            self.check_latest_ready()
