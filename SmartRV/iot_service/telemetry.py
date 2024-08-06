import json
import time
import sys
import os
from copy import deepcopy

from threading import Lock
from queue import Queue, Empty, Full
from common_libs import environment
from iot_service.utils import Utils
import requests
from common_libs.models.common import LogEvent, RVEvents

_env = environment()

sys.path.append("../main_service/models/")
sys.path.append("./SmartRV/main_service/models/")
# print('Telemetry Current Dir',os.getcwd())

from common_libs.models.common import RVEvents, EventValues

# from notifications import Notification

from iot_service.models.telemetry_msg import AlertMsg, RequestMsg

GEO_REFRESH_RATE = 60.0   # seconds
BaseUrl = f"{_env.main_host_uri}:{_env.main_service_port}"


class control_telemetry(object):
    m2_has_changed = False
    m2toBeReported = {}
    cfg = None
    baseUrl = BaseUrl
    iot = None
    m1LastReported = {}
    tzOffset = "-7.0"

    def __init__(self, cfgCheck, iot_main):
        """builds the telemetry messages"""
        self.cfgCheck = cfgCheck
        self.iot = iot_main
        try:
            self.software_version = cfgCheck.get_key('Device', 'software_version')
        except KeyError:
            Utils.pushLog(f"Version key error in Telemetry init")
            # Get from main
        try:
            self.time_of_last_gps = time.time()
            apiResponse = requests.get(self.baseUrl + "/version")
            version_data = apiResponse.json()
            Utils.pushLog(f"Version received", version_data)
            self.software_version = version_data.get("version", "0.X.0")
            cfgCheck.set_key('Device', 'software_version', self.software_version)
            self.iot.saveConfig()
        except Exception as err:
            Utils.pushLog(f"control_telemetry Version: {err}")
        # build the lists
        self.m1List = []
        self.m2List = []
        self.m2toBeReported = {}
        self.m2Lock = Lock()
        self.alertList = []
        self.alertDict = {}
        self.dailyList = []
        self.last_reported_daily = 0
        self.twinList = []
        self.iotEventsList = []  # list for the main service to notify to iot
        self.twinData = {}
        self.load_twin_from_file()
        self.twinDataNew = {}
        self.twinLock = Lock()
        self.twinAlerts = []
        self.twinAlertQueue = Queue(maxsize=50)  # for saving the current alerts -
        self.twinRequests = []
        self.twinRequestQueue = Queue(maxsize=50)  # for saving the current requests -
        self.idToCode = {}
        self.idToTwinCode = {}
        self.last_reported_gps = {"pos": "27.767,-82.640", "usrOptIn": True}
        self.gps_time = time.time() - GEO_REFRESH_RATE
        self.iot_position = self.last_reported_gps["pos"]
        self.usrOptIn = self.last_reported_gps["usrOptIn"]
        self.time_of_last_gps = time.time() - GEO_REFRESH_RATE
        self.tzOffset = "-7.0"

    def set_cfg(self, incfg):
        self.cfg = incfg
        try:
            for prop in self.cfg["properties"]:
                self.idToCode[prop["id"]] = f"{prop['componentTypeCode']}[#]{prop['code']}"
                for route in prop["routings"]:
                    if route["target"] == "standard":
                        self.m1List.append(prop["id"])
                        if prop["id"] not in self.iotEventsList:
                            self.iotEventsList.append(prop["id"])
                    elif route["target"] in {
                        "event",
                        "alert",
                        "ota",
                        "request",
                        "settings",
                    }:
                        self.m2List.append(prop["id"])
                        if prop["id"] not in self.iotEventsList:
                            self.iotEventsList.append(prop["id"])
                        if route["target"] == "alert":
                            self.alertList.append(prop["id"])
                    elif route["target"] == "daily":
                        self.dailyList.append(prop["id"])
                    elif route["target"] == "$twin":
                        self.twinList.append(prop["id"])
                        if prop["id"] not in self.iotEventsList:
                            self.iotEventsList.append(prop["id"])
                        if prop["category"] not in self.twinData:
                            self.twinData[prop["category"]] = {}
                        if (
                            f'{prop["componentTypeCode"]}1'
                            not in self.twinData[prop["category"]]
                        ):
                            self.twinData[prop["category"]][
                                f'{prop["componentTypeCode"]}1'
                            ] = {}
                        if (
                            prop["code"]
                            not in self.twinData[prop["category"]][
                                f'{prop["componentTypeCode"]}1'
                            ]
                        ):
                            self.twinData[prop["category"]][
                                f'{prop["componentTypeCode"]}1'
                            ][prop["code"]] = "Uninitialized"
                        self.idToTwinCode[
                            prop["id"]
                        ] = f"{prop['category']}.{prop['componentTypeCode']}[#].{prop['code']}"
                    else:
                        print("Unknown message type in route.", route["target"])
            msg = f'Floor Plan sent to Main {self.cfg.get("floorPlan", "VANILLA")}'
        except Exception as err:
            msg = f"Exception in telemetry config {err}"
            return False, msg
        # self.send_floorplan_to_main_service()
        self.send_events_to_main_service()
        self.get_fresh_gps()

        # print('m1 list',self.m1List,'\n')
        # print('m2 list',self.m2List,'\n')
        # print("twin list", self.twinList, "\n")
        # print("daily list", self.dailyList, "\n")
        # print('alert list',self.alertList,'\n')
        # print( self.idToCode)
        return True, msg

    def send_events_to_main_service(self):
        try:
            apiResponse = requests.put(
                self.baseUrl + "/iot_events", data=json.dumps(self.iotEventsList)
            )
            Utils.pushLog(f"iot events sent to main {apiResponse}")
            events = json.loads(apiResponse.text)
            apiResponse = requests.put(
                self.baseUrl + "/twin_events", data=json.dumps(self.twinList)
            )
            Utils.pushLog(f"twin events sent to main {apiResponse}")
            events = json.loads(apiResponse.text)
        except Exception as err:
            # logger.error(repr(err))
            # Utils.pushLog(f'send_events_to_main_service err: {repr(err)}')
            Utils.pushLog(f'send_events_to_main_service err: {str(err)}')

    def get_fresh_gps(self):
        """Fetch the gps - controlled to limit refesh times"""
        if time.time() >= self.time_of_last_gps + GEO_REFRESH_RATE:
            try:
                self.time_of_last_gps = time.time()
                apiResponse = requests.get(self.baseUrl + "/api/vehicle/ch/2/state")
                geo_data = apiResponse.json()
                print("Chassis Loc received", geo_data)
                if self.last_reported_gps != geo_data:
                    self.last_reported_gps = geo_data
                    self.iot_position = geo_data.get("pos", {})
                    self.usrOptIn = geo_data.get("usrOptIn", False)

                    Utils.pushLog(f"Current GPS pos: {self.iot_position}")

                    apiResponse = requests.get(self.baseUrl + "/api/comm/tz_offset")
                    tz_data = apiResponse.json()
                    self.tzOffset = tz_data.get("tz_offset", "-7.0")
                else:
                    Utils.pushLog("GPS data unchanged")

            except Exception as err:
                # logger.error(repr(err))
                Utils.pushLog(f"Geo fetch err")
                # Utils.pushLog(f"Geo fetch err: {repr(err)}")

    def get_m1_header(self):
        """builds the m1 type of header"""
        tel_time = time.time()
        # self.iot_position = "27.767,-82.640",   #TODO  Need to pull geo loc from ??? vehicle telemetry?
        # TODO Query the location
        # try:
        #     geo_html_page = "router-ip-winegard2/gps.htm"  # TODO determine live address
        #     apiResponse = requests.get(geo_html_page)
        #     full_page = json.loads(apiResponse.text)
        #     loc_string = some parsing needed full_page  # TODO parse data for lat lon and convert
        # except Exception as err:
        #     #logger.error(repr(err))
        #     print("Telemetry Geo Loc fetch err", repr(err))
        try:
            self.software_version = self.cfgCheck.get_key('Device', 'software_version')
        except KeyError as err:
            Utils.pushLog(f"get_m1_header error: {err}")
            self.software_version = "0.5.?"

        try:
            seriesModel = self.cfgCheck.get_key('Device', 'series_model')
        except Exception as err:
            Utils.pushLog(f"get_m1_header error: {err}")
            seriesModel = 'vanilla'

        try:
            floorPlan = self.cfgCheck.get_key('Device', 'floor_plan')
        except Exception as err:
            Utils.pushLog(f"get_m1_header error: {err}")
            floorPlan = 'VANILLA'
            #  print(f"\n\n\n{self.cfg}\n\n\n")

        try:
            telemetry_data  = {}
            telemetry_data = {
                # Device ID
                "id": self.cfgCheck.get_key("Device", "device_id"),
                # Vehicle/Device Type
                "type": self.cfgCheck.get_key("Device", "device_type"),
                # Timezone offset
                "tzo": int(float(self.tzOffset)),
                # software version
                "swv": self.software_version,
                # Hardware
                "hwv": "SECORev1",
                # model
                "mdl" : seriesModel,
                # Floorplan
                "flr": floorPlan,
                # Event type
                "evt": "0",  # EVT
                # Message Type
                # 1 = Telemetry
                # 2 = Critical Command/Request/Notification
                "mtp": "1",
                # Message Version / Schema
                "mver": "1",  # 1 for now   self.cfg['version'],
                # Timestamp
                "t": int(tel_time * 1000),
                "data": {},
            }
        except Exception as err:
            Utils.pushLog(f"get_m1_header telemetry error: {err}")
            Utils.pushLog(f"get_m1_header self.tzOffset: {self.tzOffset}")

            #  print(f"\n\n\n{self.cfg}\n\n\n")
        return telemetry_data

    def get_m1_telemetry(self):
        """builds the m1 type of message"""
        telemetry_data = self.get_m1_header()
        # Query the events for the last 10 minutes
        try:
            apiResponse = requests.get(self.baseUrl + "/snapshot")
            events = apiResponse.json()

            # Inject CHASSIS VIN change so it will always be reported
            # TODO: Move this logic to Main service to emit this better
            # to remove this business logic from here
            events['CHASSIS_VIN_CHANGE_1'] = {
                'timestamp': f"{time.time()}",
                'event': 'CHASSIS_VIN_CHANGE',
                'instance': 1,
                'value': self.iot.vin(),
                'meta': None
            }

            for key, e_value in events.items():
                # Split on last occurrence of delimiter
                res = key.rpartition("_")
                event_id = RVEvents[res[0]].value
                report_it_code = None
                if event_id in self.m1List:
                    if key not in self.m1LastReported:
                        current_event = e_value
                        print("\n M1 Found NEW event to add", key, current_event, type(current_event["value"]))
                        if type(current_event["value"]) is str:
                            try:
                                current_event["value"] = EventValues[current_event["value"]].value
                                print('\n M1 Found existing str to replace', key, current_event, type(current_event["value"]))
                            except Exception as e:
                                print(
                                    '\nOK M1 value no conversion needed.',
                                    key,
                                    current_event,
                                    type(current_event["value"]),
                                    e
                                )
                        self.m1LastReported[key] = current_event
                        report_it_code = self.idToCode[event_id].replace(
                            "[#]", str(current_event["instance"])
                        )
                    else:
                        previous_value = self.m1LastReported.get(key)["value"]
                        if events.get(key)["value"] != previous_value:
                            current_event = events.get(key)
                            print('\n M1 Found existing event to replace', key, current_event, type(current_event["value"]))
                            if type(current_event["value"]) is str and current_event:
                                try:
                                    current_event["value"] = EventValues[current_event["value"]].value
                                    print('\n M1 Found existing str to replace', key, current_event, type(current_event["value"]))
                                except Exception as e:
                                    print(
                                        '\n M1 value err',
                                        key,
                                        current_event,
                                        type(current_event["value"]),
                                        e
                                    )

                            self.m1LastReported[key] = current_event
                            report_it_code = self.idToCode[event_id].replace(
                                "[#]", str(current_event["instance"])
                            )

                    if report_it_code is not None:
                        # Add to the telemetry data
                        telemetry_data["data"][report_it_code] = events.get(key)["value"]

        except Exception as e:
            # logger.error(repr(err))
            # No need to log these when main is not up # print("M1 telemetry fetch err", e)
            time.sleep(1)  # Don't spam the service if not up
            return {}

        return telemetry_data

    def build_m2_telemetry(self):
        """builds the m2 type of message from the list to be reported"""
        telemetry_data = self.get_m1_header()
        telemetry_data["mtp"] = "2"
        # TODO: Determine which evt type the _event fall into
        # The events for the last interval
        err = ""
        with self.m2Lock:
            try:
                telemetry_data["data"] = self.m2toBeReported
                self.m2toBeReported = {}
            except Exception as err:
                Utils.pushLog(f"Error in m2 locked region {err}")

        # return json.dumps(telemetry_data) #, indent=4)
        return telemetry_data  # , indent=4)

    def update_active_alerts(self):
        result = False
        while self.twinAlertQueue.qsize() >= 1:
            # add the latest alert changes to the dictionary
            wNote = self.twinAlertQueue.get()
            self.alertDict[wNote.code] = wNote.dict(exclude_none=True)
            result = True
        return result

    def build_twin_telemetry(self):
        """return the new twin data to be reported"""
        telemetry_data = {}
        with self.twinLock:
            if self.twinDataNew:
                telemetry_data = deepcopy(self.twinDataNew)
                if len(self.alertDict) > 0:
                    Utils.pushLog(f"Twin Alert Dictionary {json.dumps(self.alertDict, indent=4)}")
                    balerts = []
                    for _, a_body in self.alertDict.items():
                        # print("Indiviual Alert", a_body)
                        if a_body["active"]:
                            wAlert = {}
                            wAlert["id"] = a_body["id"]
                            wAlert["alertType"] = a_body["type"].lower()
                            wAlert["code"] = a_body["code"]
                            wAlert["category"] = a_body["category"]
                            wAlert["instance"] = int(a_body["instance"])
                            wAlert["header"] = a_body["header"]
                            wAlert["message"] = a_body["message"]
                            wAlert["priority"] = int(a_body["priority"])
                            # wAlert["active"] = a_body["active"]  removing platform does not want
                            wAlert["opened"] = a_body["opened"]
                            if a_body["dismissed"] != 0:
                                wAlert["dismissed"] = a_body["dismissed"]

                            balerts.append(wAlert)
                    # if len(balerts) > 0:
                    telemetry_data["alerts"] = balerts

                if self.twinRequestQueue.qsize() >= 1:
                    telemetry_data["requests"] = []
                    while self.twinRequestQueue.qsize() >= 1:
                        # add the latest alert changes to the queue
                        wRequest = self.twinRequestQueue.get()
                        wReq = {}
                        wReq["id"] = wRequest.id
                        wReq["source"] = wRequest.source.lower()
                        wReq["requested"] = int(wRequest.requested)
                        wReq["completed"] = int(wRequest.completed)
                        wReq["command"] = {
                            "name": "APIRequest",
                            "parameters": {
                                "method": 4,  # Need to get this from the 'request'
                                "url": wRequest.url,
                                "body": wRequest.body,
                            },
                        }
                        wReq["result"] = wRequest.result
                        telemetry_data["requests"].append(wReq)

                self.twinData["requests"] = []  # Buildup of data remove
                self.twinData.update(self.twinDataNew)
                self.twinDataNew = {}  # reset for next send
            else:
                # print("Building twin telemetry - no requests found.")
                telemetry_data["requests"] = []

        # return json.dumps(telemetry_data) #, indent=4)
        return telemetry_data  # , indent=4)

    def check_m2(self, i_eventId, i_instance, i_data):
        """Add the incoming event to the list for the next 5 sec report."""

        if i_eventId in self.m2List and i_data is not None:
            with self.m2Lock:
                reportItCode = self.idToCode[i_eventId].replace("[#]", str(i_instance))
                try:
                    if reportItCode not in self.m2toBeReported:
                        print("Found NEW M2 event to add", reportItCode, i_data)
                        self.m2toBeReported[reportItCode] = i_data
                    else:
                        previous_value = self.m2toBeReported[reportItCode]
                        if i_data != previous_value:
                            print("Found existing M2 event to replace", reportItCode, i_data)
                            self.m2toBeReported[reportItCode] = i_data
                except Exception as err:
                    Utils.pushLog(f"Error in locked region {err}")

    def queue_alert(self, i_note):
        """Add the notification to the next to be reported queue."""
        #print("Receiving alert to  ", i_note)
        # Remove oldest if queue is full
        if self.twinAlertQueue.full():
            self.twinAlertQueue.get()
        self.twinAlertQueue.put(i_note)

    def queue_request(self, i_request):
        """Add the request to the next to be reported queue."""
        #print("Receiving request to  ", i_request)
        # Remove oldest if queue is full
        if self.twinRequestQueue.full():
            self.twinRequestQueue.get()
            if i_request.id == None:
                i_request.id = str(int(time.time() * 1000))
        self.twinRequestQueue.put(i_request)

    def add_ota_twin_data(self, i_code, i_data):
        success = False
        with self.twinLock:
            try:
                if "ota" not in self.twinDataNew:
                    self.twinDataNew["ota"] = {}
                self.twinDataNew["ota"][i_code] = i_data
                success = True
            except Exception as err:
                Utils.pushLog(f"Add ota info fail {err}")

        self.iot.twin_update_needed = True
        return success

    def add_other_twin_data(self, i_code, i_data):
        success = False
        with self.twinLock:
            try:
                self.twinDataNew[i_code] = i_data
                self.twinData[i_code] = i_data
                success = True
                self.twin_update_needed = True
            except Exception as err:
                Utils.pushLog(f"Add other twin info fail {err}")
        return success

    def get_twin_data(self, icode):
        return self.twinData.get(icode, {})

    def check_twin(self, i_eventId, i_instance, i_data):
        """Add to the list for the next twin report."""
        if i_data is None:
            return  # Don't push it.

        if i_eventId in self.twinList:
            reportItCode = None
            # key = i_eventId.name + '_' + str(i_instance)
            reportItCode = self.idToTwinCode[i_eventId].replace("[#]", str(i_instance))
            reportPath = reportItCode.split(".")
            with self.twinLock:
                if reportPath[0] not in self.twinDataNew:
                    self.twinDataNew[reportPath[0]] = {}
                if reportPath[0] not in self.twinData:
                    self.twinData[reportPath[0]] = {}
                if reportPath[1] not in self.twinDataNew[reportPath[0]]:
                    self.twinDataNew[reportPath[0]][reportPath[1]] = {}
                if reportPath[1] not in self.twinData[reportPath[0]]:
                    self.twinData[reportPath[0]][reportPath[1]] = {}
                self.twinDataNew[reportPath[0]][reportPath[1]][reportPath[2]] = i_data
                #print("Found Twin data", json.dumps(self.twinDataNew))
            #Utils.pushLog(f" Adding Twin data {reportItCode}")
            self.twin_update_needed = True


    def load_twin_from_file(self):
        try:
            with open(_env.storage_file_path('iot_twin.json'), 'r') as file:
                self.twinData = json.load(file)
        except:
            self.twinData = {}

    def clear_twin(self):
        self.twinData = {}
        self.save_twin_to_file()

    def save_twin_to_file(self):
        with open(_env.storage_file_path('iot_twin.json'), 'w') as file:
            json.dump(self.twinData, file, indent=4)

import configparser

if __name__ == "__main__":
    # CFG = json.load(open(_env.storage_file_path('Telemetry_Config.json'), 'r'))
    telemetryConfigFilePath = ( r"/home/bruce/SmartRV/data/VANILLA_ota_template.json"
    )
    CFG = json.load(open(telemetryConfigFilePath, "r"))
    # version_data = json.load(open("../version.json", "r"))

    deviceV3 = configparser.ConfigParser()
    rresult = deviceV3.read_dict(
        {
            "Device": {
                "assigned_hub": "",
                "cert_pp": "1234",
                "provisioning_host": "global.azure-devices-provisioning.net",
                "id_scope": "One0075D1E7",
                "device_id": "",
                "deviceType": "s500"
            },
            "States": {
                "configured": "False",
                "chatty_mode": "False",
                "connected": "False",
                "provisioned": "False",
            },
        }
    )

    iot_telemetry = control_telemetry(deviceV3, CFG)
    telemetryOk, msg = iot_telemetry.set_cfg(CFG)

    print(json.dumps(iot_telemetry.twinData, indent=4))

    # for i in range(10):
    for i in range(3):
        # print(get_mock_alert())
        iot_telemetry.check_m2(
            RVEvents.CHASSIS_PRO_POWER_STATUS_CHANGE, 1, EventValues.FRONT_ON.value
        )
        iot_telemetry.check_m2(
            RVEvents.LIGHTING_ZONE_MODE_CHANGE, 2, EventValues.ON.value
        )
        iot_telemetry.check_m2(
            RVEvents.ROOF_VENT_FAN_DIRECTION_CHANGE, 1, EventValues.FAN_OUT.value
        )

        iot_telemetry.check_twin(
            RVEvents.CHASSIS_PRO_POWER_STATUS_CHANGE, 1, EventValues.FRONT_ON.value
        )
        iot_telemetry.check_twin(
            RVEvents.LIGHTING_ZONE_MODE_CHANGE, 2, EventValues.ON.value
        )
        iot_telemetry.check_twin(
            RVEvents.ROOF_VENT_FAN_DIRECTION_CHANGE, 1, EventValues.FAN_OUT.value
        )

        _opened = int((time.time() - 1) * 1000)
        nAlert = AlertMsg(
            id=str(_opened),
            type='also',
            code="bt120202",
            category="somesystem",
            instance='1',
            priority="2",
            message="Hello my test Alert",
            header="msg",
            active=True,
            opened=_opened,
            dismissed=0,
        )

        iot_telemetry.queue_alert(nAlert)
        nAlert = AlertMsg(
            id=str(_opened),
            type='also',
            code="bt120202",
            category="somesystem",
            instance='1',
            priority="2",
            message="Hello my test Alert",
            header="msg",
            active=True,
            opened=_opened,
            dismissed=0,
        )
        iot_telemetry.queue_alert(nAlert)
        _opened = str(int((time.time() - 1) * 1000))

        nAlert = AlertMsg(
            id=str(_opened),
            type='also',
            code="bt120202",
            category="somesystem",
            instance='1',
            priority="3",
            message="Hello my test Alert",
            header="msg",
            active=True,
            opened=_opened,
            dismissed=0,
        )
        iot_telemetry.queue_alert(nAlert)
        iot_telemetry.update_active_alerts()

        nRequest = RequestMsg(
            id=int(time.time() * 1000),
            source="TST",
            name="testRequest",
            requested=99,
            completed=100,
            url="/api/endpoint",
            body={},
            result="success",
        )
        iot_telemetry.queue_request(nRequest)

        print(iot_telemetry.build_m2_telemetry(), "\n")
        print ("Full twin events", json.dumps(iot_telemetry.twinList), "\n")
        print("Twin data test", json.dumps(iot_telemetry.twinDataNew), "\n")
        print(
            "build_telemetry",
            json.dumps(iot_telemetry.build_twin_telemetry(), indent=4),
            "\n",
        )
        print("m1 telemetry", iot_telemetry.get_m1_telemetry(), "\n")

        time.sleep(20)
        # print("Twin data complete",json.dumps(iot_telemetry.twinData, indent=4))



    print(json.dumps(iot_telemetry.twinList, indent=4))
