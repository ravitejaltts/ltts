import json

from fastapi import APIRouter, Request, HTTPException
from pydantic import ValidationError

from common_libs.models.notifications import (
    request_to_iot,
    request_to_iot_handler
)
from common_libs.system.state_helpers import check_special_states
from common_libs.system.scheduled_function import ScheduledFunction

from main_service.components.movables import (
    SlideoutBasicState,
    AwningRvcState,
    # AwningLightState,
    JackState,
    EventValues
)
from main_service.modules.sw_features import Features
from datetime import datetime

from main_service.modules.api_helper import validate_wc_api_call

PREFIX = 'features'

router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['FEATURES', ]
)

# TODO: Add to central place
LOCKOUT_ERROR_CODE = 423


@router.get("/pm/{instance}/state")
async def get_pet_monitor(request: Request, instance: int) -> dict:
    # Get from the right place
    try:
        pet_monitor = request.app.hal.features.handler.pet_monitoring[instance]
    except KeyError as err:
        print(err)
        raise HTTPException(404, {'msg': f'Cannot find instance {instance}'})

    return pet_monitor.state


@router.put('/pm/{instance}/state')
async def set_pet_monitor(request: Request, instance: int, in_state: dict) -> dict:
    try:
        pet_monitor = request.app.hal.features.handler.pet_monitoring[instance]
    except KeyError as err:
        print(err)
        raise HTTPException(404, {'msg': f'Cannot find instance {instance}'})

    try:
        pet_monitor.set_state(in_state)
    except ValidationError as err:
        print(err)
        raise HTTPException(422, {'msg': f'Cannot set temp to desired value'})
    except ValueError as err:
        print(err)
        raise HTTPException(422, {'msg': f'Cannot set temp range to desired value'})

    # Run the algorithm
    request.app.hal.features.handler.run_pet_monitoring_algorithm()
    # Handle errors
    return pet_monitor.state


@router.get('/wx/{instance}/state')
async def get_alert_status(request: Request, instance: int) -> dict:
    # Get from the right place
    try:
        weather = request.app.hal.features.handler.weather[instance]
    except KeyError as err:
        print(err)
        raise HTTPException(404, {'msg': f'Cannot find instance {instance}'})

    return weather.state


@router.put('/wx/{instance}/state')
async def set_weather_alert_settings(request: Request, instance: int, in_state: dict) -> dict:
    try:
        weather = request.app.hal.features.handler.weather[instance]
    except KeyError as err:
        print(err)
        raise HTTPException(404, {'msg': f'Cannot find instance {instance}'})

    weather.set_state(in_state)
    # Handle errors
    return weather.state


@router.put('/wx/{instance}/alert')
async def set_weather_alert(request: Request, instance: int, in_alert: dict) -> dict:
    try:
        weather = request.app.hal.features.handler.weather[instance]
        weather.input_alert(request.app.hal.app, in_alert)
    except KeyError as err:
        print(err)
        raise HTTPException(404, {'msg': f'Cannot find instance {instance}'})

    # Handle errors
    return weather.state


@router.put('/wx/{instance}/report')
async def put_weather_alerts(request: Request, instance: int, in_report: dict) -> dict:
    """The IOT calls with platform data when it arrives."""
    try:
        await Features.receive_and_process_weather(request, in_report)
        msg = "WX data processed"
    except Exception as err:
        print(err)
        msg = err

    # Handle errors
    return 200, msg


@router.put('/wx/{instance}/alerts/checktimeout')
async def check_weather_alerts(request: Request, instance: int) -> dict:
    try:
        await request.app.check_time_notifications_expired(request.app)
        return 200, "Checked."

    # Handle errors
    except Exception as err:
        print(err)
        raise HTTPException(404, {'msg': f"/alerts/checktimeout {err}"})



@router.put('/wx/{instance}/alerts/process')
async def get_weather_alerts(request: Request, instance: int) -> dict:
    try:
        # Kickoff a one shot to fetch weather
        print("Scheduling Weather Check for 10 seonds from now!")
        wxChecker = ScheduledFunction(function=Features.check_weather_task,
                                                        args=(request.app.hal.app,),
                                                        wait_seconds=10,  # 10 second wait
                                                        oneshot=True)

        request.app.taskScheduler.add_timed_function(wxChecker)

        return 200, f"Processing {datetime.now()}"

    # Handle errors
    except Exception as err:
        print(err)
        raise HTTPException(404, {'msg': f"/alerts/process {err}"})


@router.get('/dx/{instance}/state')
async def get_system_overview(request: Request, instance: int):
    '''Diagnostics Endpoints.'''
    diag = await validate_wc_api_call(request, PREFIX, 'dx', instance)
    return diag.state
