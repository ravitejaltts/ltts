import datetime

from typing import Optional, List

from logging import Logger

from fastapi import (
    APIRouter,
    HTTPException,
    Request
)
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel, Field

from .common import ResultLevel, not_implemented, BaseResponse
from main_service.modules.system_helper import (
    get_display_brightness,
    set_display_brightness,
    set_display_on,
    set_display_off,
    get_system_processes
)

# from main_service.modules.hardware.hal import hw_layer


class SystemResponse(BaseResponse):
    '''Response model for all System calls'''
    system_key: str
    system_value: str


class Brightness(BaseModel):
    '''Request Model for display brightness'''
    value: int = Field(
        ...,
        ge=0,
        le=100,
        description='The value for brightness must be => 0 and <= 100, where 0 is off and 100 is 100% brightness'
    )


class SimpleSwitch(BaseModel):
    onOff: int

class SimpleDim(BaseModel):
    onOff: Optional[int]
    power: Optional[int]
    mode: Optional[int]

router = APIRouter(
    prefix='/electrical',
    tags=['ACDC',]
)


@router.get('/state')
async def get_electrical_state(request: Request) -> dict:
    '''Respond available AC/DC outlets and sensors.'''
    try:
        electrical_state = request.app.hal.electrical.handler.state

        return electrical_state

    except Exception as err:
        raise HTTPException(
            500, f'Ligting state failure: {err}')


@router.get('/ac')
async def get_ac() -> dict:
    '''Get all controllable AC endpoints'''
    return not_implemented()


@router.get('/ac/{ac_id}')
async def get_ac_id(ac_id) -> dict:
    '''Get specific AC endpoint details'''
    return not_implemented()


@router.put('/ac/{ac_id}')
async def set_ac_id(ac_id) -> dict:
    '''Set specific AC endpoint state'''
    return not_implemented()


@router.get('/dc')
async def get_dc() -> dict:
    '''Get all controllable DC endpoints'''
    return not_implemented


@router.put('/dc/{dc_id}')
async def set_dc_id(request: Request, dc_id: int, body: SimpleDim) -> dict:
    '''Set specific DC endpoint details'''
    # This is for now a test endpoint, but could be used for RV-C compatible outputs
    # Set default
    output = 100
    if hasattr(body, 'power'):
        if body.power:
            output = body.power

    direction = None

    if hasattr(body, 'mode'):
        if body.mode == 0:
            body.onOff = 0
        elif body.mode == 1:
            body.onOff = 1
            direction = 'FORWARD'
        elif body.mode == -1:
            body.onOff = 1
            direction = 'BACKWARD'

    if direction is None:
        result = request.app.hal.electrical.handler.dc_switch(dc_id, body.onOff, output=output)
    else:
        result = request.app.hal.electrical.handler.dc_switch(dc_id, body.onOff, output=output, direction=direction)

    # Check downstream effect
    return {
        'result': result,
        'msg': result['msg']
    }


@router.get('/dc/{dc_id}')
async def get_dc_id(request: Request, dc_id: int) -> dict:
    '''Get specific DC endpoint state'''
    current_state = request.app.hal.electrical.handler.get_state('dc', dc_id)
    if current_state is None:
        return {}
    response = {**current_state}
    response['id'] = dc_id
    response['system'] = 'dc'
    return response


@router.get('/config')
async def get_config(request: Request):
    return request.app.hal.electrical.handler.cfgMapping
