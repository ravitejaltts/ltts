"""WGO Notification Module.

Notification module to work closely with the DB model and Events to provide
notifications to the user and allow for user configurable actions.

"""
import ast
import json
import re
import sys
import time
from datetime import datetime
from enum import Enum, IntEnum
from typing import List, Union

import requests
from pydantic import BaseModel, Field, validator

from common_libs.clients import BT_BASE_URL, IOT_BASE_URL, MAIN_CLIENT
from common_libs.models.common import EventValues, RVEvents
from iot_service.models.telemetry_msg import AlertMsg, RequestMsg


class NotificationTrigger(IntEnum):
    '''ENUM of Notification triggers.'''
    OFF = 0
    ON = 1
    ONOFF = 3
    HIGH = 4
    LOW = 5             #
    STRING = 6          # Does it match a given string
    STRING_LIST = 7     # This value helps catch the AC 'modes'
    RANGE = 8
    TIME = 9


class NotificationPriority(IntEnum):
    ''''''
    # Updates Mar 2024 for inclusion of Weather Service Alerts and Pet Monitor Critical
    # Critical Levels
    Weather_Warning = 0
    Pet_Minder_Critical = 1
    System_Critical = 2
    # Warning Levels
    Weather_Advisory = 3
    Weather_Watch = 4
    Weather_Alert = 5  # (requiremnts to move to Weather Watch - level)
    System_Warning = 6
    Pet_Minder_Warning = 7
    # Notice or Info Level
    Pet_Minder_Notice = 8
    System_Notice = 9
    Notice = 10  # Using all specfied priorities (#15969) for ordering in display

    # TODO: The following are not yet in the source of truth spreadsheet but were created initially
    # https://winnebagoind.sharepoint.com/:x:/s/CustomerDigitalStrategy/EdHDFZCAyhhFq-OvfirQlMkBfoStOBUAG0R9xI6nduX28A?e=pUEv9u
    # Authentication = 3
    # Acknowledgement = 4
    Resolved = 11   # 11 Currently only used on pet monitoring to relay the level that all is good
    Good = 11


class NotificationLevel(IntEnum):
    ''''''
    # level  value  Color in display
    # Values per Home Screen Variation Doc
    Critical = 0    # f15f31
    Warning = 1     # f7a300
    Info = 4        # 419bf9


def priority_to_level(priority: NotificationPriority):
    '''Convert a priority to a level.'''
    result = NotificationLevel.Critical
    if priority >= NotificationPriority.Pet_Minder_Notice:
        result = NotificationLevel.Info
    elif priority >= priority >= NotificationPriority.Weather_Advisory:
        result = NotificationLevel.Warning
    return result


# Notification Type Asked for by the platform
class NotificationType(IntEnum):
    Status = 0
    Event = 1

    # Notification system designed to trigger Alerts
    # DEFAULT_NOTIFICATIONS moved to Default_Config.json as alert_items


class Notification(BaseModel):
    ts_id: float  # time stamp for the twin reporting
    notification_id: RVEvents  # Is unique and Primary Key
    instance: int
    ts_active: float     # Timestamp the Notification last activated
    ts_dismissed: float  # Timestamp the user dismissed the notification
    ts_cleared: float    # Timestamp the notification last cleared
    priority: int
    code: str  # For platform
    active: bool
    user_selected: bool
    user_cleared: bool
    mobile_push: bool
    trigger_events: List[RVEvents]
    trigger_type: NotificationTrigger
    trigger_value: Union[int, EventValues, str, float, bool, List[str]]
    header: str
    msg: str  # Msg to display to user
    type: NotificationType  # From the source of truth spreadsheet
    meta: Union[str, dict] = Field(default_factory=dict)

    @validator('meta', pre=True, always=True)
    def validate_meta(cls, value):
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            # Try to parse as JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

            # Try to parse as a Python dictionary literal
            try:
                parsed_value = ast.literal_eval(value)
                if isinstance(parsed_value, dict):
                    return parsed_value
                else:
                    raise ValueError("String does not represent a dictionary.")
            except (ValueError, SyntaxError):
                pass

            # If both parsing attempts fail, print an error and default to empty dictionary
            print("Error: Incoming data was a string but failed to convert to a dictionary. Defaulting to an empty dictionary.")
            return {}
        else:
            print("Error: Invalid value type. Expected a string or a dictionary. Defaulting to an empty dictionary.")
            return {}



def check_new_note(nNote: Notification) -> Notification:
    '''First check that level triggers are a list now
    or make them into a list.'''
    # TODO: Clarify if this does anything to the list, as it is not assigned, how does nVal get used ?
    if nNote.trigger_type == NotificationTrigger.LOW:
        if isinstance(nNote.trigger_value, type([])) is False:
            nVal = []
            nVal[0] = nNote.trigger_value
            nVal[1] = nNote.trigger_value + 10  # arbitray increase
            nNote.trigger_value = nVal
    elif nNote.trigger_type == NotificationTrigger.HIGH:
        if isinstance(nNote.trigger_value, type([])) is False:
            nVal = []
            nVal[0] = nNote.trigger_value
            nVal[1] = nNote.trigger_value - 10  # arbitray decrease
            nNote.trigger_value = nVal
    elif nNote.trigger_type == NotificationTrigger.RANGE:
        if isinstance(nNote.trigger_value, type([])) is False:
            nNote.trigger_value = nNote.trigger_value.split(',')
    return nNote


def update_notification_from_csv_row(_row, up_Note: Notification) -> Notification:
    '''DB Now returns only updates to the notification'''

    # print(f'[update_notification_from_csv_row]  row = {_row}')

    # NOTE: Experiment to drop reading DB state of active and dismissed etc.
    # up_Note.ts_active=_row[2]
    # up_Note.ts_dismissed=_row[3]  # we DO keep the user notifications list after reboot
    # up_Note.ts_cleared=_row[4]
    # up_Note.active=_row[7]
    # up_Note.user_selected=_row[8]
    # up_Note.user_cleared=_row[9]
    # print('NOTIFICATION Updated', up_Note.code)
    return up_Note


def notification_from_dict(x) -> Notification:
    # print(f'[notification_from_dict] {x}')

    # NOTE: Check when this is called and how the data is passed in
    new_note = Notification(
        ts_id=0.0,
        notification_id=x["notification_id"],
        instance=x["instance"],
        ts_active=0.0,
        ts_dismissed=0.0,
        ts_cleared=0.0,
        priority=x["priority"],
        code=str(x["code"]),
        active=False,
        user_selected=True,
        user_cleared=False,
        mobile_push=True,
        trigger_events=x["trigger_events"],
        trigger_type=NotificationTrigger(x["trigger_type"]),
        trigger_value=x["trigger_value"],
        header=x["header"],
        msg=x["msg"],
        type=x.get("type", 0),
        meta=x.get("meta", "{}")
    )

    return check_new_note(new_note)


# def update_note_from_telemetry(_note, _tel) -> Notification:
#     _note.instance = _tel["instance"]
#     _note.priority = _tel["priority"]
#     # _note.user_selected = _tel['user_selected']  Not used by platform
#     _note.code = _tel["code"]
#     _note.trigger_type = NotificationTrigger(_tel["trigger_type"])
#     _note.trigger_value = _tel["trigger_value"]
#     _note.header = _tel["header"]
#     _note.msg = _tel["msg"]
#     _note.type = _tel["type"]
#     _meta = _tel.get("meta", {})

#     return check_new_note(_note)


def prepare_display_note(_note):
    '''function to return the display ready notification

    Example of what is in the display note
    d_note_format = {
        'id': RVEvents.FRESH_WATER_TANK_BELOW.value,
        't': '',
        'ecode': RVEvents(RVEvents.FRESH_WATER_TANK_BELOW).name,
        'header': 'Fresh water tank low',
        'body': DEFAULT_NOTIFICATIONS[ RVEvents.FRESH_WATER_TANK_BELOW.value].msg,
        'level': NotificationPriority.Warning
    }'''

    # Do NOT display the notification if the user has asked not to see it
    if not _note.user_selected:
        return None

    new_body = _note.msg[:95]
    if "When..." in new_body:
        new_body = new_body[9:].split('\n\n', 1)[0]

    # d_note = display_notes[_note.notification_id]
    d_note = {
        "id": _note.notification_id.value,
        "t": "",
        "ecode": _note.notification_id.name,
        "header": _note.header,
        "body": new_body,
        "level": priority_to_level(_note.priority),
        # Standard Footer
        "footer": {
            # NOTE: Ideally we have an independent text that we can provide per notifcation
            "actions": ["dismiss",],
            "action_dismiss": {
                "type": "dismiss",
                "action": {
                    "text": "Dismiss",
                    "event_href": f"/notifications/{_note.notification_id.value}/dismiss",
                },
            }
        },
    }
    print('NOTEACTIONS META', _note.meta)
    note_actions = _note.meta.get('actions')
    print('NOTEACTIONS', note_actions)
    if note_actions is not None:
        navigate = note_actions.get('navigate')
        api_call = note_actions.get('api_call')

        if navigate is not None:
            print('NOTEACTIONS', 'Found navigate', navigate)
            action = navigate.get('action')
            if action is not None:
                d_note['footer']['actions'].append('navigate')
                d_note['footer']['action_navigate'] = {
                    "type": "navigate",
                    'action': action
                }

        if api_call is not None:
            print('NOTEACTIONS', 'Found api_call', api_call)
            action = api_call.get('action')
            if action is not None:
                d_note['footer']['actions'].append('api_call')
                d_note['footer']['action_api_call'] = {
                    "type": "api_call",
                    "action": action
                }

    if (
        _note.trigger_type == NotificationTrigger.LOW
        or _note.trigger_type == NotificationTrigger.HIGH
    ):
        level = float(_note.trigger_value[0])  # level setting that triggered the event
        d_note["body"] = d_note["body"].format(
            level
        )  # Customize the message with the level

    # TODO Footer additions for other actions, special notifications

    return d_note


MINIMUM_TIMEOUT = 0.1  # secs


def event_to_iot(_event, report: bool = False):
    # print("IOT found", json.dumps(_event, default=vars))
    try:
        apiResponse = requests.put(
            IOT_BASE_URL + "/telemetry/event",
            data=json.dumps(_event, default=vars),
            timeout=MINIMUM_TIMEOUT,
        )
        # events = json.loads(apiResponse.text)
        events = apiResponse.json()
        if report is True:
            return events
    except Exception as err:
        print("check iot err:", err)
    return


def alert_to_iot(_alert, report: bool = False):
    """Helper function to queue an alert to be reported to the twin"""
    try:
        _op = str(int(time.time() * 1000))
        category = code = ""
        cc = _alert.code.split(':')
        if len(cc) >= 2:
            category = cc[0]
            code = cc[1]

        oAlert = AlertMsg(
            id=_op,
            type=_alert.type.name,
            code=code,
            category=category,
            instance=_alert.instance,
            header=_alert.header,
            message=_alert.msg,
            priority=_alert.priority,
            active=_alert.active,
            opened=_op,
            dismissed=str(int(_alert.ts_dismissed * 1000)),
        )

        apiResponse = requests.put(
            IOT_BASE_URL + "/telemetry/alert",
            data=json.dumps(oAlert, default=vars),
            timeout=MINIMUM_TIMEOUT,
        )
        events = json.loads(apiResponse.text)
        if report is True:
            return events

    except Exception as err:
        print("alert to iot err:", err)



def event_to_bt(_event, report: bool = False):
    """Check if the event needs to be sent to BT."""
    # TODO: This likely should be replaced by a trigger that there is an update
    # or emit the changes of the state
    print("BT found", json.dumps(_event, default=vars))
    try:
        apiResponse = requests.put(
            BT_BASE_URL + "/updates/event",
            data=json.dumps(_event, default=vars),
            timeout=MINIMUM_TIMEOUT,
        )
        events = json.loads(apiResponse.text)
        if report is True:
            return events
    except Exception as err:
        print("check bt err:", err)

    return


async def request_to_iot_handler(request, body):
    await request_to_iot(
        {
            'hdrs': dict(request.headers),
            'url': request.url.path,
            'body': body
        }
    )


async def request_to_iot(_fields_needed, report: bool = False):
    """Helper function to queue a request to be reported to the twin"""
    # print("Request recording to IOT fields needed",json.dumps(_fields_needed))

    _src = _fields_needed.get("hdrs", {}).get("source", 'HMI')
    _id = _fields_needed.get("hdrs", {}).get("id", str(int(time.time() * 1000)))
    _url = _fields_needed.get("url", "")
    _body = _fields_needed.get("body", "")
    _requested = _fields_needed.get("hdrs", {}).get(
        "req_ts",
        str(int(time.time() * 1000))
    )

    try:
        oRequest = RequestMsg(
            id=_id,
            source=_src,
            name="deviceRequest",
            requested=_requested,
            completed=_requested,
            url=_url,
            body=_body,
            result="success",
        )
    except Exception as err:
        print('[ERROR] Cannot create RequestMsg object', err)
        return

    try:
        apiResponse = await MAIN_CLIENT.put(
            IOT_BASE_URL + "/telemetry/request",
            data=json.dumps(oRequest, default=vars),
            timeout=MINIMUM_TIMEOUT,
        )
        if report is True:
            return apiResponse.json()
    except Exception as err:
        print("request to iot err:", err, " body ", _body)

def dismiss_note(_app, _note, user_dissmissed=True):
    """Remove the notification from the HMI display list"""
    # check was it user dismissed?
    if _note.ts_dismissed == 0:
        with _app.n_lock:
            try:
                notification_index = [
                    i
                    for i, x in enumerate(_app.notifications)
                    if x["id"] == _note.notification_id
                ][0]
                _app.notifications.pop(notification_index)
                if user_dissmissed:
                    # report the alert with dismissed time
                    print("Adding dismissed stamp to alert", _note)
                    _note.ts_dismissed = time.time()
                    _app.user_db.update_notification(_note)
                alert_to_iot(_note)

            except Exception as err:
                print("Error with notifications?", err)
    else:
        print('Notification user already dismissed!')
        # Force pop again
        with _app.n_lock:
            try:
                notification_index = [
                    i
                    for i, x in enumerate(_app.notifications)
                    if x["id"] == _note.notification_id
                ][0]
                _app.notifications.pop(notification_index)

            except Exception as err:
                print("Error with notifications?", err)


def compare_phrases(phrase1, phrase2):
    import re

    # Function to clean and prepare a phrase
    def prepare_phrase(phrase):
        # Remove non-letter characters and convert to upper case
        return re.sub(r'[^A-Za-z]', '', phrase).upper()

    # Prepare both phrases
    prepared_phrase1 = prepare_phrase(phrase1)
    prepared_phrase2 = prepare_phrase(phrase2)

    # Compare the prepared phrases
    return prepared_phrase1 == prepared_phrase2

# Function to convert a phrase to uppercase and underscores
def convert_to_uppercase_underscore(phrase):
    # Replace non-letter characters with underscores and convert to uppercase
    return re.sub(r'[^A-Za-z]', '_', phrase).upper()

# Function to find the matching enum value using direct access
def phrase_to_RVEvents(input_phrase):
    converted_input = convert_to_uppercase_underscore(input_phrase)
    try:
        return RVEvents[converted_input]
    except KeyError:
        return None


def extract_between_issued_by(text):
    # Define the regex pattern to capture everything between 'issued' and 'by'
    pattern = r'issued(.*?)by'

    # Search the text for the pattern
    match = re.search(pattern, text)

    # If a match is found, return the captured group, otherwise return None
    if match:
        return match.group(1).strip()  # .strip() removes leading/trailing whitespace
    else:
        return None


class weatherCodeEnum(Enum):
    AIR_QUALITY_ALERT = "AQA"
    AVALANCHE_WARNING = "AVW"
    AVALANCHE_WATCH = "AVA"
    BLIZZARD_WARNING = "BZW"
    BLIZZARD_WATCH = "BZA"
    COASTAL_FLOOD_WARNING = "CFW"
    DENSE_FOG_ADVISORY = "DFV"
    EXCESSIVE_HEAT_WARNING = "EHW"
    EXTREME_COLD_WARNING = "ECW"
    EXTREME_FIRE_DANGER = "FRW"
    EXTREME_WIND_WARNING = "HWW"
    FIRE_WARNING = "FRW"
    FLASH_FLOOD_WARNING = "FFW"
    FLASH_FLOOD_WATCH = "FFA"
    FLOOD_WARNING = "FLW"
    FLOOD_WATCH = "FLA"
    FREEZE_WARNING = "FZW"
    FREEZING_RAIN_ADVISORY = "FRA"
    HIGH_WIND_WARNING = "EWW"
    HURRICANE_FORCE_WIND_WARNING = "HUW"
    HURRICANE_FORCE_WIND_WATCH = "HUA"
    HURRICANE_WARNING = "HUW"
    HURRICANE_WATCH = "HUA"
    SEVERE_THUNDERSTORM_WARNING = "SVR"
    SEVERE_THUNDERSTORM_WATCH = "SVA"
    STORM_WARNING = "SSW"
    STORM_WATCH = "SSA"
    TORNADO_WARNING = "TOR"
    TORNADO_WATCH = "TOA"
    TROPICAL_STORM_WARNING = "TRW"
    TROPICAL_STORM_WATCH = "TRA"
    WIND_ADVISORY = "WND"
    WINTER_STORM_WARNING = "WSW"

    # FROM WIKI
# Air Quality Alert - AQA **
# Avalanche Warning - AVW
# Avalanche Watch - AVA
# Blizzard Warning - BZW
# Blizzard Watch - BZA
# Coastal Flood Warning - CFW
# Dense Fog Advisory - DFV **
# Excessive Heat Warning - EHW **
# Extreme Cold Warning - ECW **
# Extreme Fire Danger - FRW
# Extreme Wind Warning - HWW
# Fire Warning - FRW
# Flash Flood Warning - FFW
# Flash Flood Watch - FFA
# Flood Warning - FLW
# Flood Watch - FLA
# Freeze Warning - FZW
# Freezing Rain Advisory - FRA
# High Wind Warning - EWW
# Hurricane Force Wind Warning - HUW
# Hurricane Force Wind Watch - HUA
# Hurricane Warning - HUW
# Hurricane Watch - HUA
# Severe Thunderstorm Warning - SVR
# Severe Thunderstorm Watch - SVA
# Storm Warning - SSW
# Storm Watch - SSA
# Tornado Warning - TOR
# Tornado Watch - TOA
# Tropical Storm Warning - TRW
# Tropical Storm Watch - TRA
# Wind Advisory - WND **
# Winter Storm Warning - WSW

def notifcation_from_weather_alert(wx):
    try:
        wx_id = phrase_to_RVEvents(wx.get('event'))
        instance = 1  # All weather for now

    except Exception as err:
        print(f'Weather alert conversion: {err}')
        return None

    wx_event = wx.get('event')

    # Match priorities to HMI scheme
    if 'warning' in wx_event.lower():
        priority = NotificationPriority.Weather_Warning.value
    elif 'advisory' in wx_event.lower():
        priority = NotificationPriority.Weather_Advisory.value
    else: # Now Weather Watch and Alert at same priority in HMI
        priority = NotificationPriority.Weather_Watch.value

    expiry_str = wx.get('endTime')
    if expiry_str is None:
        print("Why is alert endTime = None?")
        expiry = datetime.now().timestamp()
    else:
        expiry = datetime.fromisoformat(expiry_str).timestamp()

    extracted_text = extract_between_issued_by(wx.get('headline'))

    new_msg = f"* When...{extracted_text}\n\n" + wx.get('description')

    wx_note = Notification(
        ts_id=0.0,
        notification_id=wx_id,
        instance=instance,
        ts_active=time.time(),
        ts_dismissed=0.0,
        ts_cleared=0.0,
        priority=priority,
        code=weatherCodeEnum.__members__[wx_id.name].value,
        active=False,  # This will be set active during insertion.
        user_selected=True,    #TODO: Need to get these from settings eventually?
        user_cleared=False,
        mobile_push=True,
        trigger_events=[wx_id,],   # Intresting case - wx alerts trigger themselves
        trigger_type=NotificationTrigger.TIME,
        trigger_value=expiry,
        header=wx_event,
        msg=new_msg,
        type=NotificationType.Event,
        meta="{}"

    )

    return wx_note


if __name__ == "__main__":
    # Test twin_alerts builds
    import configparser
    import os

    sys.path.append("./main_service/")
    #from main_service.modules.storage_helper import read_default_config_json_file

    t_configParser = configparser.ConfigParser()
    # try:
    t_configParser.read_dict(
        {
            "Device": {
                "assigned_hub": "",
                "cert_pp": "Winn23",
                "provisioning_host": "global.azure-devices-provisioning.net",
                "id_scope": "One0075D1E7",
                "device_id": "",
            },
            "States": {
                "configured": "False",
                "chatty_mode": "False",
                "connected": "False",
                "provisioned": "False",
            },
        }
    )
    wx_alerts = [
        {
            "event": "Flood Warning",
            "startTime": "2023-12-11T15:25:00+00:00",
            "endTime": "2023-12-11T19:00:00+00:00",
            "headline": "Flood Warning issued December 11 at 10:25AM EST until December 11 at 2:00PM EST by NWS Caribou ME",
            "description": "* WHAT...Urban area and small stream flooding caused by rain and\nsnowmelt continues.\n\n* WHERE...Portions of DownEast and East Central Maine, including the\nfollowing counties, in DownEast Maine, Hancock and Washington. In\nEast Central Maine, Penobscot.\n\n* WHEN...Until 200 PM EST.\n\n* IMPACTS...Streams continue to run high due to excess runoff from\nongoing rainfall.",
            "instruction": "Turn around, don't drown when encountering flooded roads. Most flood\ndeaths occur in vehicles.\n\nIn hilly terrain there are hundreds of low water crossings which are\npotentially dangerous in heavy rain. Do not attempt to cross flooded\nroads. Find an alternate route.",
            "area": "Hancock, ME; Penobscot, ME; Washington, ME",
            "severity": "Severe",
            "certainty": "Likely",
            "urgency": "Expected",
            "issuer": {
                "name": "NWS Caribou ME",
                "email": "w-nws.webmaster@noaa.gov"
            }
        },
        {
            "event": "High Wind Warning",
            "startTime": "2023-12-11T14:38:00+00:00",
            "endTime": "2023-12-11T22:45:00+00:00",
            "headline": "High Wind Warning issued December 11 at 9:38AM EST until December 11 at 7:00PM EST by NWS Caribou ME",
            "description": "* WHAT...Southwest winds 15 to 25 mph with gusts up to 60 mph.\n\n* WHERE...Central Washington, Coastal Hancock and Coastal\nWashington Counties.\n\n* WHEN...Until 7 PM EST this evening.\n\n* IMPACTS...Damaging winds will blow down trees and power lines.\nWidespread power outages are expected. Travel will be\ndifficult, especially for high profile vehicles.",
            "instruction": "People should avoid being outside in forested areas and around\ntrees and branches. If possible, remain in the lower levels of\nyour home during the windstorm, and avoid windows. Use caution if\nyou must drive.",
            "area": "Central Washington; Coastal Hancock; Coastal Washington",
            "severity": "Severe",
            "certainty": "Likely",
            "urgency": "Expected",
            "issuer": {
                "name": "NWS Caribou ME",
                "email": "w-nws.webmaster@noaa.gov"
            }
        }
    ]

    sys.path.append("./iot_service/")
    t_cfg = json.load(open("../data/Config_VANILLA.json", "r"))
    # from telemetry import control_telemetry  # , get telemetry control object

    # m_telemetry = control_telemetry(t_configParser, t_cfg, "Test run")

    x = RVEvents.GREY_WATER_TANK_FULL
    print(x)
    print(dir(x))
    print(x.value)
    print(x.name)
    y = NotificationTrigger.STRING_LIST
    print(y.value)
    print(y.name)

    z = NotificationPriority.System_Notice
    print(z.value)
    print(z.name)

    #print(RVEvents)
    # print(dir(RVEvents))
    notification_list = [{"name": x.name, "value": x.value} for x in RVEvents]
    #print(json.dumps(notification_list, indent=4))

    # test_event = RVEvents.CLIMATE_ZONE_MODE
    test_event = RVEvents.GREY_WATER_TANK_ABOVE

    # for xn in t_cfg["alerts"]["items"]:
    #     test_note = notification_from_dict(xn)
    #     print(json.dumps(test_note, indent=4))

    TEST_NOTIFICATIONS = {
        "50009": {
            "notification_id": 50009,
            "instance": 1,
            "priority": 4,
            "user_selected": 1,
            "code": "wt50009",
            "trigger_events": [
                8600
            ],
            "trigger_type": 4,
            "trigger_value": [99, 80],   # level trigger list , trigger on,  trigger off high or low direction hysterisis
            "header": "Fresh water tank full",
            "msg": "Fresh water tank is full",
            "type": 0,
            "meta": "{}"
        },
        "50034": {
            "notification_id": 50034,
            "instance": 1,
            "priority": 4,
            "user_selected": 1,
            "code": "wt50034",
            "trigger_events": [
                8600
            ],
            "trigger_type": 5,
            "trigger_value": [25, 40],
            "header": "Fresh water tank getting low",
            "msg": "Fresh water tank is below {}%",
            "type": 0,
            "meta": "{}"
        },
        "50035": {
            "notification_id": 50035,
            "instance": 2,
            "priority": 4,
            "user_selected": 1,
            "code": "wt:50035",
            "trigger_events": [
                8600
            ],
            "trigger_type": 4,
            "trigger_value": [75,60],
            "header": "Gray water approaching high",
            "msg": "Gray water tank is filling up!",
            "type": 0,
            "meta": "{'precedence' :{'over': [], 'under': [50011]}}"
        },
        "50011": {
            "notification_id": 50011,
            "instance": 2,
            "priority": 1,
            "user_selected": 1,
            "code": "wt:50011",
            "trigger_events": [
                8600
            ],
            "trigger_type": 4,
            "trigger_value": [90, 80],
            "header": "Gray water tank High",
            "msg": "Gray water tank is above {}%",
            "type": 0,
            "meta": "{'precedence' :{'over': [ 50035], 'under': []}}"
        }
    }

    test_notification = notification_from_dict(TEST_NOTIFICATIONS[str(test_event.value)])
    print("\n\n")
    print(test_notification)
    print("Check when ", test_event, " event happens.")

    print(
        "Display notification to UI",
        json.dumps(prepare_display_note(test_notification), indent=4),
    )

    # m_telemetry.queue_alert(test_notification)

    phrase1 = "Flood Warning"
    phrase2 = "FLOOD_WARNING"
    result = compare_phrases(phrase1, phrase2)
    print("Phrase compare result: ", result)

    result = phrase_to_RVEvents(phrase1)
    print("RVEvents: ", result)

    for wxal in wx_alerts:
        new_note = notifcation_from_weather_alert(wxal)
        print(
            f"Weather notification to UI, code: {new_note.code}",
            json.dumps(prepare_display_note(new_note), indent=4),
        )

    test_event = RVEvents.FRESH_WATER_TANK_NOTICE
    test_notification = notification_from_dict(TEST_NOTIFICATIONS[str(test_event.value)])

    # m_telemetry.queue_alert(test_notification)
    request_to_iot(
        {
            "hdrs": {"source": "HMI", "id": "33"},
            "url": "/api/climate/zones/1",
            "body": {},
        }
    )

    # twin = m_telemetry.build_twin_telemetry()

    # print(json.dumps(twin, indent=4))

    # Modifying the function to include a test for 'has_item_over' as well

    def has_item_over_under(note):
        # Checking if 'precedence' exists and then checking for items in 'over' and 'under'
        over = bool(note.meta).get("precedence", {}).get("over", [])
        under = bool(note.meta).get("precedence", {}).get("under", [])
        return over, under

    for test_id  in TEST_NOTIFICATIONS:
        print(test_id)
        test_notification = notification_from_dict(TEST_NOTIFICATIONS[str(test_id)])
        o, v = has_item_over_under(test_notification)
        print("Over", o)
        print("Under", v)
