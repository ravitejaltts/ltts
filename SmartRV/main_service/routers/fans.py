import datetime

from typing import Optional, List
from typing_extensions import Annotated

from logging import Logger
from xmlrpc.client import Boolean

from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from main_service.components.climate import RoofFanAdvancedState

from pydantic import BaseModel, Field

from .common import ResultLevel, not_implemented, BaseResponse

try:
    from  common_libs.models.common import RVEvents, EventValues
except ImportError as err:
    import sys
    import os
    abs_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
    add_path = os.path.join(abs_path, '../')
    sys.path.append(
        add_path
    )
    from  common_libs.models.common import RVEvents, EventValues

from main_service.modules.system_helper import (
    get_display_brightness,
    set_display_brightness,
    set_display_on,
    set_display_off,
    get_system_processes
)

# from main_service.modules.hardware.hal import hw_layer

from common_libs.models.notifications import request_to_iot

class SystemResponse(BaseResponse):
    '''Response model for all System calls'''
    system_key: str
    system_value: str


# class FanSettings(BaseModel):
#     '''Request Model for display brightness'''
#     onOff: int
#     speed: int = Field(
#         ...,
#         ge=0,
#         le=100,
#         description='Speed setting of the fan'
#     )
#     direction: int


router = APIRouter(
    prefix='/fans',
    tags=['FANS', ]
)


@router.get('/status')
async def status(request: Request) -> dict:
    '''Respond with full details of the fans in the coach.'''
    fans = {}
    try:
        for i in range(1,4):
            key = f"zone_1__fan_{i}"
            fans[key] = request.app.hal.climate.handler.get_fan_state_by_key(key)

    except Exception as err:
        print(f'Fan {key} state err: {err}')

    return fans


@router.put('/fan/{fan_id}')
async def set_fanid_on(request: Request, fan_id: int, fan_settings: RoofFanAdvancedState):
# async def set_fanid_on(request: Request, fan_id: int, fan_settings:  Annotated[
#         RoofFanBasicState,
#         Body(
#             example={
#                         "direction": 1,
#                         "dome": 1,
#                         "onOff": EventValues.OFF.value,
#                         "fanSpdfanSpd": EventValues.OFF.value
#                 },
#             ),
#     ],  ):
    '''Set state of fan with fan_id.'''
    # On / Off
    # Direction
    # Speed
    #print(f"Fans speed type is {type(fan_settings.fanSpd)} {fan_settings.fanSpd}")
    #Default Fan speed not zero is need to turn dome on
    if fan_settings.fanSpd != 0:
        fan_settings.onOff = 1
    fan_response = request.app.hal.climate.handler.fan_control(
        zone_id=1,
        fan_id=fan_id,
        on_off=fan_settings.onOff,
        speed=fan_settings.fanSpd,
        direction=fan_settings.direction,
        dome=fan_settings.dome,
        rain_sensor=fan_settings.rain,
    )
    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers), "url": f'/api/climate/settings', "body": fan_settings.dict(exclude_none=True)
        }
    )

    return fan_response

@router.get('/fan/{fan_id}')
async def get_fanid_on(request: Request, fan_id) -> dict:
    '''Get state of fan with fan_id.'''
    fan = {}
    try:
        fan = request.app.hal.climate.handler.get_fan_state(zone_id=1,fan_id=fan_id)
    except Exception as err:
        print(f'Fan {fan_id} state err: {err}')

    return fan
