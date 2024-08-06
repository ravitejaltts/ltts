from main_service.components.climate import (
    ThermostatState,
    Thermostat,
    RoofFanAdvancedState,
    RoofFanAdvanced,
    ACBasicState,
    ACBasic,
    HeaterState,
    HeaterSourceState,
    HeaterBasic,
    HeaterACHeatPump,
    TemperatureConverter,
    RefrigeratorBasic,
    AmbientTempSensor,
    ACFanSpeedEnum,
)
import logging
import sqlite3
import time
import json
from datetime import datetime
from enum import Enum, IntEnum
from typing import Collection, Optional, List, Union
from common_libs.models.common import EventValues, LogEvent, RVEvents
from common_libs.models.notifications import request_to_iot, request_to_iot_handler
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from main_service.modules import db_helper as database
from main_service.modules.constants import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODES,
    TEMP_UNIT_CELCIUS,
    TEMP_UNIT_FAHRENHEIT,
    TEMP_UNIT_PREFERENCE_KEY,
    TEMP_UNITS,
    _celcius_2_fahrenheit,
    fahrenheit_2_celcius,
)

from main_service.modules.logger import prefix_log
from pydantic import BaseModel, Field, validator, ValidationError

from .common import APIItem, BaseAPIModel, BaseAPIResponse
from common_libs import environment

from main_service.modules.api_helper import validate_wc_api_call, validate_wc_state


wgo_logger = logging.getLogger("main_service")
_env = environment()

TEMP_PROTECTIVE_RANGE = 3  # Degrees


class ClimateResponse(BaseAPIResponse):
    climate: list
    # features: Optional[List[ClimateFeature]]
    # schemas: dict


def thermostat_check(hal, zone_id):
    thermostat_onoff = hal.climate.handler.thermostat[zone_id].state.onOff

    if thermostat_onoff == 0:
        raise HTTPException(400, "Thermostat is off, not accepting commands")
    return False


def refrigerator_freezer_history(request, instance_id, start_time, end_time, date):

    timezone = request.app.config.get("timezone").get("TimeZonePreference")
    current_temp_unit = request.app.config.get("climate", {}).get(
        TEMP_UNIT_PREFERENCE_KEY, TEMP_UNIT_FAHRENHEIT
    )
    current_temp_short = TEMP_UNITS.get(current_temp_unit, {}).get("short")

    current_fridge_temp = request.app.hal.climate.handler.refrigerator[instance_id].get_temperature(
        current_temp_unit
    )
    refrigerator_freezer_events = []

    # timestamp specific queries
    end_timestamp = f"{date} {end_time}"
    end_datetime_object = datetime.strptime(end_timestamp, "%Y-%m-%d %I:%M:%S %p")
    end_time_stamp = end_datetime_object.timestamp()

    start_timestamp = f"{date} {start_time}"
    start_datetime_object = datetime.strptime(start_timestamp, "%Y-%m-%d %I:%M:%S %p")
    start_time_stamp = start_datetime_object.timestamp()

    sql = request.app.user_db.get_coach_event_refrigerator_freezer_query(start_time_stamp, end_time_stamp, instance_id)

    data = request.app.user_db.execute_refrigerator_freezer_query(sql=sql, current_temp_short=current_temp_short, timezone=timezone)
    refrigerator_freezer_events.extend(data)

    # refrigerator_freezer_events = sorted(
    #     refrigerator_freezer_events, key=lambda x: x["timestamp"], reverse=True)
    refrigerator_freezer_events = sorted(data[0], key=lambda x: x.get('timestamp', 0), reverse=True)
    sorted_list = []
    event_count = 0
    while event_count < len(refrigerator_freezer_events):
        if (
            event_count + 1 < len(refrigerator_freezer_events)
            and refrigerator_freezer_events[event_count]["value"] == refrigerator_freezer_events[event_count + 1]["value"]
        ):
            if refrigerator_freezer_events[event_count]["alert"]:
                sorted_list.append(refrigerator_freezer_events[event_count])
            else:
                sorted_list.append(
                    refrigerator_freezer_events[event_count + 1])
            event_count += 2
        else:
            sorted_list.append(refrigerator_freezer_events[event_count])
            event_count += 1
    return sorted_list, current_fridge_temp, current_temp_short


PREFIX = "climate"


router = APIRouter(
    prefix=f"/{PREFIX}",
    tags=["CLIMATE"],
)


@router.get("/state")
async def get_climate_state(request: Request) -> dict:
    """Report state json from the hw_layer"""
    c_state = {}
    climate_state = request.app.hal.get_state().get('climate')

    print('Climate State', climate_state)

    for instance, comp in climate_state.items():
        c_state[instance] = comp.dict()

    return c_state


class QuickSettings(object):
    """Helper for pydantic model inputs.

    Add attributes as needed"""

    def __init__(self):
        pass


@router.get("/zones/{instance}/thermostat/state")
@router.get("/th/{instance}/state")
async def get_thermostat_state(request: Request, instance: int, unit: str = None):
    thermostat = await validate_wc_api_call(request, PREFIX, 'th', instance)

    if unit is None:
        unit = 'C'

    return thermostat.get_converted_state(unit)


@router.put("/zones/{instance}/thermostat/state")
@router.put("/th/{instance}/state")
async def set_thermostat_state(request: Request, instance: int, ac_mode: dict) -> dict:
    """Sets the full state Request Body"""
    print("Climate Zone control", instance, ac_mode)
    thermostat = await validate_wc_api_call(request, PREFIX, 'th', instance)

    onOff = ac_mode.get("onOff")
    new_mode = ac_mode.get("setMode")
    if new_mode is not None:
        # TODO: Clean this up to use eventvalues everywhere
        # This test  for mode as an int lets us use 'AUTO' or 519
        # on the state input and the state result is always the code - 519
        # trying not to break the UI
        if type(new_mode) is str:
            result = request.app.hal.climate.handler.thermostat[instance].state.setMode = EventValues(
                new_mode)

        else:
            result = request.app.hal.climate.handler.thermostat[instance].state.setMode = new_mode

        # # This test  for mode as an int lets us use 'AUTO' or 519
        # # on the state input and the state result is always the code - 519
        # # trying not to break the UI
        # if type(new_mode) is int:
        #     result = request.app.hal.climate.handler.set_zone_ac_mode(
        #         instance, EventValues(new_mode).name
        #     )
        # else:
        #     result = request.app.hal.climate.handler.set_zone_ac_mode(instance, new_mode
    if onOff is not None:
        setting = QuickSettings()
        setting.onOff = ac_mode["onOff"]
        if ac_mode["onOff"] == 0 or ac_mode["onOff"] == 1:
            result = request.app.hal.climate.handler.thermostat[instance].state.onOff = ac_mode["onOff"]

    current_temp_unit = request.app.config.get("climate", {}).get(
        "TempUnitPreference", TEMP_UNIT_FAHRENHEIT
    )

    unit = ac_mode.get('unit')
    if unit is None:
        # unit = request.app.config.get('climate', {}).get('TempUnitPreference')
        unit = 'C'

    # TODO: Check if setTempHeat is > setTempCool - protective band
    # TODO: If yes, check if setTempCool can be adjusted
    # TODO: If not reject and stay at given temps
    # TODO: Get previous set temps to figure out which changed to assess which direction to check
    # If Cool changes we need to do the check in reverse

    temp_value = ac_mode.get("setTempCool")
    if temp_value is not None:
        request.app.hal.climate.handler.thermostat[instance].set_tempCool(
            temp_value, unit)

    temp_value = ac_mode.get("setTempHeat")
    if temp_value is not None:
        request.app.hal.climate.handler.thermostat[instance].set_tempHeat(
            temp_value, unit)

    thermostat.save_db_state()
    thermostat = await get_thermostat_state(request, instance=instance, unit=unit)

    # try:
    #     request.app.hal.climate.handler.run_climate_controls()
    # except ValueError as err:
    #     print('Error running climate algo from API', err)

    # Add the request to the IOT queue

    await request_to_iot_handler(request, ac_mode)
    # emit the events using the base component
    request.app.hal.climate.handler.thermostat[instance].update_state()

    return thermostat


@router.put("/zones/{zone_id}/mode")
async def set_zone_mode(request: Request, zone_id: int, ac_mode: dict) -> dict:
    """Sets the zone on or off In Request Body use this format: {"item": "ClimateMode", "value": "COOL"}"""
    result = "Error"  # prepare for exception
    print(f"><><><> PUT climate {ac_mode}")
    try:
        thermostat_check(request.app.hal, zone_id)
        if ac_mode.get("item") == "ClimateMode":
            current_hvac_mode = request.app.config.get(
                "climate", {}).get("HVACMode", EventValues.AUTO)
            print(f"><><><> current_hvac_mode {current_hvac_mode}")
            print(f"><><><>  ac_mode.get('value') { ac_mode.get('value')}")
            request.app.config["climate"]["HVACMode"] = ac_mode.get("value")
            result = request.app.hal.climate.handler.set_zone_ac_mode(
                zone_id, EventValues(ac_mode.get("value")).name
            )
        else:
            result = "ClimateMode not found."
    except ValueError as err:
        print(err)
        raise HTTPException(422, "Cannot set the zone to desired state 4")

    try:
        request.app.hal.climate.handler.run_climate_controls()
    except ValueError as err:
        print('Error running climate algo from API', err)

    # Add the request to the IOT queue
    await request_to_iot_handler(request, ac_mode)

    return request.app.hal.climate.handler.thermostat[zone_id].state


# Set AC temp in a partiuclar ZONE
@router.put("/zones/{zone_id}/temp")
async def set_zone_temp(request: Request, zone_id: int, zone_temp: dict) -> dict:
    '''Sets the zone on or off, In Request Body use this format: {"mode": "HEAT", "setTemp": 74, "unit": "F"}'''
    #current_temp_unit = request.app.config.get("climate", {}).get("TempUnitPreference", TEMP_UNIT_FAHRENHEIT)
    # TODO: Get this fixed below, the $ should be gone, what code is still using the $ sign?

    temp_value = float(zone_temp.get("setTemp"))
    if temp_value is None:
        raise HTTPException(
            422, f"Cannot set zone to None Value {zone_temp.get('setTemp')} ")

    # Set the mode which we want to control
    # TODO: TBD, question in to UX

    temp_mode = zone_temp.get("mode")
    result = False

    thermostat = request.app.hal.climate.handler.thermostat[zone_id]
    unit = zone_temp.get('unit')
    print('UNIT', unit, type(unit))
    if unit is None:
        # Unit was not provided in the request
        # Check system unit
        unit = request.app.config.get('climate', {}).get('TempUnitPreference')
        print('System Unit', unit)

    r_event = None
    if temp_mode == EventValues.COOL or temp_mode == EventValues.COOL.name:
        # Check COOL in allowed range
        result = thermostat.set_tempCool(temp_value, unit)
        r_event = RVEvents.THERMOSTAT_CURRENT_COOL_TEMPERATURE_SET_CHANGE
        # raise HTTPException(400, 'Cannot exceed temp band value')

    elif temp_mode == EventValues.HEAT or temp_mode == EventValues.HEAT.name:
        result = thermostat.set_tempHeat(temp_value, unit)
        r_event = RVEvents.THERMOSTAT_CURRENT_HEAT_TEMPERATURE_SET_CHANGE

        # raise HTTPException(400, 'Cannot exceed temp band value')

    if result is False:
        raise HTTPException(
            422, f"Cannot set zone to desired temp of : {temp_value} unit {unit} ")

    # if r_event is not None:
    #     request.app.event_logger(
    #             LogEvent(
    #                 event=r_event,
    #                 instance=zone_id,
    #                 value=temp_value
    #             ),
    #             force=True
    #         )
    # Add the request to the IOT queue
    await request_to_iot_handler(request, zone_temp)

    thermostat.save_db_state()

    return thermostat.state


@router.get("/rv/{instance}/state")
async def get_rooffan_state(request: Request, instance: int) -> dict:
    roof_vent = await validate_wc_api_call(request, PREFIX, 'rv', instance)

    return roof_vent.state


@router.put("/rv/{instance}/state")
async def set_rooffan_state(request: Request, instance: int, in_state: dict) -> dict:
    roof_vent = await validate_wc_api_call(request, PREFIX, 'rv', instance)
    try:
        _ = roof_vent.set_state(in_state)
    except ValidationError as err:
        print('[CLIMATE][API][RV] Validation Error')
        raise HTTPException(422, str(err))

    return roof_vent.state


@router.get("/ac/{instance}/state")
async def get_ac_state(request: Request, instance: int) -> dict:
    air_conditioner = await validate_wc_api_call(request, PREFIX, 'ac', instance)
    # Pull the state directly
    return air_conditioner.state


@router.put("/ac/{instance}/state")
async def put_ac_state(request: Request, instance: int, in_state: dict) -> dict:
    air_conditioner = await validate_wc_api_call(request, PREFIX, 'ac', instance)
    print('[CLIMATE] Receive AC State', in_state)
    air_conditioner.set_state(in_state)

    return air_conditioner.state


@router.get("/he/{instance}/state")
async def get_heater_state(request: Request, instance: int) -> dict:
    # Pull the state directly
    heater = await validate_wc_api_call(request, PREFIX, 'he', instance)
    return heater.state


@router.put("/he/{instance}/state")
async def put_heater_state(request: Request, instance: int, in_state: dict) -> dict:
    heater = await validate_wc_api_call(request, PREFIX, 'he', instance)
    try:
        heater.state.validate(in_state)
    except ValidationError as err:
        print(err)
        raise HTTPException(422, {'msg': str(err)})

    # TODO: Create proper component handler
    # TODO: Temp fix for hard coded UI
    for key, value in in_state.items():
        if key == 'sourceMode':
            key = 'heatSrc'
        elif key == 'onOff' and instance > 1:
            # Ignore
            continue
        setattr(heater.state, key, value)

    return request.app.hal.climate.handler.heater[instance].state


@router.get("/zones/{zone_id}/fans/{fan_id}/state")
async def get_rooffan_zone_state(request: Request, fan_id: int, zone_id: int = 1):
    """State of Roof Fan"""
    try:
        roof_hatch_state = request.app.hal.climate.handler.get_roof_hatch_state(
            zone_id, fan_id)
        print(f"Roof Hatch state {roof_hatch_state}")

        fans = {
            "id": fan_id,
            "zone": zone_id,
            "name": "Main Roof",
            "description": "Dometic Roof Fan with RV-C gateway",
            "type": "ADVANCED_FAN",
            "state": RoofFanAdvancedState(
                onOff=roof_hatch_state.get("onOff", 0),
                fanSpd=roof_hatch_state.get("fanSpd", 0),
                direction=roof_hatch_state.get("direction", 529),
                dome=roof_hatch_state.get("dome", 525),
            ),
        }
        return fans["state"]

    except:
        raise HTTPException(
            404, f"Fan ID: {fan_id} with " f"Zone ID: {zone_id} not found")


@router.get("/zones/{zone_id}/acfan/{fan_id}/state")
async def get_ac_zone_state(request: Request, zone_id: int, fan_id: int):
    fan_speed = request.app.hal.climate.handler.air_conditioner[zone_id].state.fanSpd
    if fan_speed == EventValues.MEDIUM:
        fan_speed = EventValues.LOW
    # try:
    acfan = {
        "id": 1,
        "zone": 1,
        "type": "SIMPLE_AC",
        "name": "Main AC",
        "description": "Premier AC, simple controlled, hi/lo and compressor onOff",
        "state": ACBasicState(
            onOFF=request.app.hal.climate.handler.air_conditioner[zone_id].state.comp,
            fanSpd=fan_speed,
        ),
    }

    if zone_id == acfan["id"] and zone_id == acfan["zone"]:
        return acfan["state"]
    else:
        raise HTTPException(
            404, f"Fan ID: {fan_id} with " f"Zone ID: {zone_id} not found")


# Set AC FAN speed in ZONE


@router.put("/zones/{zone_id}/acfan/{fan_id}/state")
async def set_ac_zone_fan(request: Request, zone_id: int, fan_id: int, setting: ACBasicState) -> dict:
    """Set FAN speed for a fan in a specific zone, In Request Body use this format:  {"fanSpd":"EventValues.HIGH"}"""
    try:
        thermostat_check(request.app.hal, zone_id)
        try:
            fan_speed = ACFanSpeedEnum(setting.fanSpd)
            new_settings = ACBasicState(fanSpd=fan_speed)
            # This function only worked for GE
            air_conditioner = request.app.hal.climate.handler.air_conditioner[zone_id]  # work for either
            result = air_conditioner.set_state(new_settings)
            print("API result", result)
            #     zone_id, new_settings)
            await request_to_iot_handler(
                {
                    "hdrs": dict(request.headers),
                    "url": f"/api/climate/zones/{zone_id}/acfan/{fan_id}/state",
                    "body": setting.dict(exclude_none=True),
                }
            )
            return result
        except:
            raise ValueError(f"{setting.fanSpd} not supported")

    except Exception as err:
        raise HTTPException(404, f"Zone ID: {zone_id} set error - {err}")

    # #TODO Why is this a Duplicate Quick Action error ????

    # @router.put("/zones/{zone_id}/fans/{fan_id}/quickaction")
    # async def set_zone_fan_quick_action(
    #     request: Request, zone_id: int, fan_id: int, fan_setting: dict
    # ) -> dict:
    #     """Set FAN speed for a fan in a specific zone"""
    #     prefix_log(wgo_logger, __name__, f"{zone_id} / {fan_id}")
    #     prefix_log(wgo_logger, __name__, fan_setting)

    #     onOff = fan_setting.get("onOff")

    #     # Get current state
    #     current_fan_state = request.app.hal.climate.handler.get_fan_state(zone_id, fan_id)
    #     print("Current FAN State", current_fan_state)
    #     # Update onOff
    #     # Send
    #     speed = current_fan_state.get("fanSpd")
    #     direction = current_fan_state.get("direction")
    #     dome = onOff
    #     rain_sensor = current_fan_state.get("rain", 0)

    #     result = request.app.hal.climate.handler.fan_control(
    #         zone_id, fan_id, onOff, speed, direction, dome, rain_sensor
    #     )

    # # Add the request to the IOT queue
    # request_to_iot(
    #     {
    #         "hdrs": dict(request.headers),
    #         # TODO: Get this from the function to make it generic
    #         "url": f'/api/climate/zones/{zone_id}/fans/{fan_id}/state',
    #         "body": fan_setting.dict(exclude_none=True)
    #     }
    # )
    return result


@router.put("/zones/{zone_id}/fans/{fan_id}/state")
async def set_zone_fan(
    request: Request, zone_id: int, fan_id: int, fan_setting: RoofFanAdvancedState
) -> dict:
    """Set FAN speed for a fan in a specific zone"""
    prefix_log(wgo_logger, __name__, f"{zone_id} / {fan_id}")
    prefix_log(wgo_logger, __name__, fan_setting)

    onOff = fan_setting.onOff
    speed = fan_setting.fanSpd
    if speed == EventValues.OFF:
        onOff = 0
    else:
        onOff = 1

    direction = fan_setting.direction
    dome = fan_setting.dome
    rain_sensor = 0
    result = request.app.hal.climate.handler.fan_control(
        zone_id, fan_id, onOff, speed, direction, dome, rain_sensor)

    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            # TODO: Get this from the function to make it generic
            "url": f"/api/climate/zones/{zone_id}/fans/{fan_id}/state",
            "body": fan_setting.dict(exclude_none=True),
        }
    )
    return result


# TODO: Evaluate Queueing and most resilient approach
# TODO: Create decorator @Dom
@router.put("/rv/{fan_id}/quickaction")
async def run_zone_fan_quickaction(request: Request, fan_id: int, onOff: dict):
    # This is not hardware agnostic
    print('Incoming onOff', onOff)
    result = request.app.hal.climate.handler.fan_control(
        fan_id,
        onOff.get("onOff"),
        EventValues.MEDIUM,
        EventValues.FAN_OUT,
        EventValues.OPEN,
        EventValues.OFF
    )
    print('Fan control result', result)
    quick_action_id = 1
    request.app.hal.climate.handler.state[f"quickaction_fan_{fan_id}_{quick_action_id}"] = onOff.get(
        "onOff")
    # Add the request to the IOT queue
    # request_to_iot(
    #     {
    #         "hdrs": dict(request.headers),
    #         "url": f"/api/climate/zones/{zone_id}/fans/{fan_id}/quickaction",
    #         "body": onOff,
    #     }
    # )
    return result


# Update settings


@router.put("/rainsensor")
async def push_notification(request: Request, body: dict = {"onOff": 0}):
    onOff = body["onOff"]
    rain_sensor = request.app.config.get("climate", {}).get("rainSensor")
    if rain_sensor is None:
        raise ValueError("Rain Sensor not part of the config")

    request.app.config["climate"]["rainSensor"] = onOff

    return request.app.config["climate"]


@router.put("/heatcoolmindelta")
async def heat_cool_delta(request: Request, body: dict = {"setTemp": 5}):
    temp = body["setTemp"]
    current_temp = request.app.config.get(
        "climate", {}).get("heatCoolMin", {}).get("setTemp")
    if current_temp is None:
        raise ValueError("Cool differential temp not part of the config")

    request.app.config["climate"]["heatCoolMin"]["setTemp"] = temp

    return {"setTemp": temp}


@router.put("/heatcoolmindelta/restoredefault")
async def heat_cool_restore_delta(request: Request):
    try:
        request.app.config["climate"]["heatCoolMin"]["setTemp"] = 5
        print(request.app.config["climate"]["heatCoolMin"]["setTemp"])
    except Exception as err:
        print("could not restore default Heat Cool Min Delta", err)


@router.put("/cooldifferential")
async def cool_differential_temp(request: Request, body: dict = {"setTemp": 0.5}):
    temp = body["setTemp"]
    current_temp = request.app.config.get("climate", {}).get(
        "coolDifferential", {}).get("setTemp")
    if current_temp is None:
        raise ValueError("Cool differential temp not part of the config")

    request.app.config["climate"]["coolDifferential"]["setTemp"] = temp

    return {"setTemp": temp}


@router.put("/cooldifferential/restoredefault")
async def cool_differential_restore_default(request: Request):
    try:
        request.app.config["climate"]["coolDifferential"]["setTemp"] = 0.5
    except Exception as err:
        print("could not restore default Cool Differential Temperature", err)


@router.put("/minoutdoor")
async def min_out_door(request: Request, body: dict = {"setTemp": 0.5}):
    temp = body["setTemp"]
    current_temp = request.app.config.get(
        "climate", {}).get("minOutDoor", {}).get("setTemp")
    if current_temp is None:
        raise ValueError("Minimum outdoor temp not part of the config")

    request.app.config["climate"]["minOutDoor"]["setTemp"] = temp

    return {"setTemp": temp}


@router.put("/minoutdoor/restoredefault")
async def min_out_door_restore_default(request: Request):
    try:
        request.app.config["climate"]["minOutDoor"]["setTemp"] = 60
    except Exception as err:
        print("could not restore default Cool Differential Temperature", err)


# TODO: what should the range be? where are we showing the alerts?
@router.put("/indoortempalert")
async def indoor_temp_alert(request: Request, body: dict = {"onOff": 0}):
    onOff = body["onOff"]
    indoor_temp_alert = request.app.config.get("climate", {}).get("indoorTempAlert")

    if indoor_temp_alert is None:
        raise ValueError("Indoor temperature alert not part of the config")

    request.app.config["climate"]["indoorTempAlert"] = onOff

    return request.app.config["climate"]


@router.put("/settings")
async def update_climate_settings(request: Request, settings: dict):
    '''Update settings for climate.'''
    item = settings['item']
    value = settings['value']

    if value in TEMP_UNITS:
        # Get the current unit
        request.app.config['climate'][item] = value
        # Save in the settings DB
        setting_key = f'climate.{item}'
        request.app.save_config(setting_key, value)
        # TODO: What is this needed for ?
        # if value == TEMP_UNIT_CELCIUS:
        #     # Round values when coming from Fahrenheit
        #     request.app.hal.climate.handler.temp_unit_switch(TEMP_UNIT_CELCIUS)
    else:
        raise ValueError(f'{item} value: {value} not supported')

    response = {
        'settings': request.app.config.get('climate')
    }
    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": f'/api/climate/settings',
            "body": settings,
            "result": response
        }
    )
    return response

@router.put("/refrigerator/freezer/settings/alert")
async def set_fridge_freezer_alert_control(request: Request, body: dict) -> dict:
    """Sets the alerts on or off"""
    onoff = body.get("onOff")
    appliance_type = body.get("applianceType")
    prefix_log(wgo_logger, __name__, str(onoff))

    if appliance_type not in ["refrigerator", "freezer"]:
        raise HTTPException(422, "Appliance type is not valid.")

    if appliance_type == "refrigerator":
        APPLIANCE_ID = 1
        notification_id = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
    else:
        APPLIANCE_ID = 2
        notification_id = RVEvents.FREEZER_OUT_OF_RANGE.value

    user_selected = False if onoff == 0 else True

    try:
        request.app.config[appliance_type]["AlertOnOff"] = onoff
        request.app.event_notifications[notification_id].user_selected = user_selected
        request.app.user_db.update_notification(request.app.event_notifications[notification_id])

    except ValueError as err:
        raise HTTPException(
            422,
            detail={
                'msg': 'Cannot set alerts to desired state',
                'err': str(err)
            }
        )
    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": 'api/climate/refrigerator/freezer/settings/alert',
            "body": {"Onoff": onoff},
        }
    )


# api to restore default
@router.put("/refrigerator/freezer/settings/restoredefault")
async def set_default_range(request: Request, body: dict):

    appliance_type = body.get("applianceType")

    if appliance_type not in ["refrigerator", "freezer"]:
        raise HTTPException(422, "Appliance type is not valid.")

    if appliance_type == "refrigerator":
        APPLIANCE_ID = 1
        notification_key = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
        range = str(1.11) + "," + str(3.33)
    else:
        APPLIANCE_ID = 2
        notification_key = RVEvents.FREEZER_OUT_OF_RANGE.value
        range = str(-4) + "," + str(0)

    appliance = request.app.hal.climate.handler.refrigerator[APPLIANCE_ID]

    try:
        appliance_note = request.app.event_notifications[notification_key]
        appliance_note.trigger_value = f"{range}"
        request.app.user_db.update_notification_trigger_value(appliance_note)

    except Exception as err:
        print("could not restore default temp range", err)

    current_appliance_temp = appliance.state.temp

    # Emit if not None, on None not much will happen
    if current_appliance_temp is not None:
        # Emit a temperature event to clear/set alerts/notifications
        request.app.event_logger(
            LogEvent(
                event=RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
                instance=APPLIANCE_ID,
                value=current_appliance_temp
            ),
            force=True
        )
    return 'Updated'


@router.put("/refrigerator/freezer/settings/temprange")
async def set_temp_range(request: Request, temp_range: dict):
    """Sets upper and lower limit temp of refrigerator"""

    appliance_type = temp_range.get("applianceType")
    if appliance_type not in ["refrigerator", "freezer"]:
        raise HTTPException(422, "Appliance type is not valid.")

    if appliance_type == "freezer":
        notification_key = RVEvents.FREEZER_OUT_OF_RANGE.value
        APPLIANCE_ID = 2
        if not temp_range:
            temp_range["upper_limit"] = 32
            temp_range["lower_limit"] = 24.8

    else:
        notification_key = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
        APPLIANCE_ID = 1
        if not temp_range:
            temp_range["upper_limit"] = 38
            temp_range["lower_limit"] = 34

    upper_limit = fahrenheit_2_celcius(temp_range.get("upper_limit"))
    lower_limit = fahrenheit_2_celcius(temp_range.get("lower_limit"))

    if upper_limit <= lower_limit:
        raise HTTPException(422, 'Lower limit must be less than upper limit')

    range = str(lower_limit) + "," + str(upper_limit)

    try:
        appliance_note = request.app.event_notifications[notification_key]
        appliance_note.trigger_value = f"{range}"
        request.app.user_db.update_notification_trigger_value(appliance_note)
    except Exception as err:
        print("could not set temp range", err)

    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": "/api/climate/refrigerator/freezer/settings/temprange",
            "body": {
                "lower_limit": lower_limit,
                "upper_limit": upper_limit,
            },
        }
    )

    appliance_data = request.app.hal.climate.handler.refrigerator[APPLIANCE_ID]
    current_appliance_temp = appliance_data.state.temp

    # Emit if not None, on None not much will happen anyway
    if current_appliance_temp is not None:
        # Emit a current temperature event to clear/set alerts/notifications
        request.app.event_logger(
            LogEvent(
                event=RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
                instance=APPLIANCE_ID,
                value=current_appliance_temp
            ),
            force=True
        )

    return {
        "upper_limit": upper_limit,
        "lower_limit": lower_limit
    }


@router.put("/refrigerator/temprange")
async def get_temp_range(request: Request, appliance: dict):
    """Sets upper and lower limit temp of refrigerator"""

    appliance_type = appliance.get("applianceType")
    if appliance_type not in ["refrigerator", "freezer"]:
        raise HTTPException(422, "Appliance type is not valid.")

    try:
        if appliance_type == "refrigerator":
            notification_key = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
            fridge_note = request.app.event_notifications[notification_key]
            trigger_value = fridge_note.trigger_value.split(',')

            return {"lower_limit": trigger_value[0], "upper_limit": trigger_value[1]}

        elif appliance_type == "freezer":
            notification_key = RVEvents.REFRIGERATOR_OUT_OF_RANGE.value
            fridge_note = request.app.event_notifications[notification_key]
            trigger_value = fridge_note.trigger_value.split(',')

            return {"lower_limit": trigger_value[0], "upper_limit": trigger_value[1]}

    except:
        raise HTTPException(400, "Failed to get values from DB")


@router.get('/rf/{instance}/state')
async def get_rf_state(request: Request, instance: int):
    refrigerator = await validate_wc_api_call(request, PREFIX, 'rf', instance)
    return refrigerator.state


@router.get("/schemas")
async def get_schemas(request: Request, include=None):
    # TODO:
    # Get list of climate components from HW layer
    # Get schemas into model file
    # TODO: Decide if that needs to be separate per vehicle modle/ floorplan
    # request.app.hal.climate.handler.whoami() ?
    # Inject mapping for twin short keys and otehr data needs to describe the

    all_schemas = {
        "BASIC_HEATER": BasicHeater.schema(),
        "AMBIENT_TEMP": AmbientTempSensor.schema(),
        "ADVANCED_FAN": RoofFanAdvancedState.schema(),  # roof fan
        "SIMPLE_AC": PremierAC.schema(),  # climate fan
        "CLIMATE_ZONE": None,
        "ZONE_THERMOSTAT": ThermostatState.schema(),
    }

    schemas = {}

    if include is not None:
        include_list = include.split(",")
        for s in include_list:
            schemas[s.upper()] = all_schemas.get(s.upper())
        return schemas

    return all_schemas
