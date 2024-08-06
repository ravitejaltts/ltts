from copy import deepcopy
import datetime
import logging

from typing import Optional, List

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel, Field, ValidationError
from enum import Enum

from .common import (
    APIItem,
    not_implemented,
    BaseResponse,
    BaseAPIResponse,
    BaseAPIModel,
)

from common_libs.models.notifications import (
    request_to_iot,
    request_to_iot_handler
)

# from common_libs.models.watersystems import (
#     SIMPLE_WATER_HEATER,
#     SIMPLE_PUMP,
#     SIMPLE_TANK,
#     SIMPLE_PUMP_STATE,
#     SIMPLE_TANK_STATE,
#     SIMPLE_WATER_HEATER_STATE,
#     TRUMA_WATER_HEATER_STATE
# )

from common_libs.models.common import RVEvents, EventValues
from common_libs.models.common import LogEvent

from main_service.modules.api_helper import validate_wc_api_call
from main_service.modules.constants import fahrenheit_2_celcius

from main_service.modules.constants import (
    WATER_UNITS
)

LOCKOUT_ERROR_CODE = 423

# CONSTANTS for API validation
WATER_HEATER_CODE = 'wh'        # TODO: Figure out what source this should come from
TOILET_CIRCUIT_CODE = 'tc'
WATER_TANK_CODE = 'wt'
WATER_PUMP_CODE = 'wp'
SYSTEM_STR = 'watersystems'

# Get from central settings file
BASE_URL = ''

class ModelEnum(Enum):
    SIMPLE_WATER_HEATER = 1
    SIMPLE_PUMP = 2
    SIMPLE_TANK = 3
    SIMPLE_PUMP_STATE = 4
    SIMPLE_TANK_STATE = 5
    SIMPLE_WATER_HEATER_STATE= 6
    TRUMA_WATER_HEATER_STATE= 7


class SimpleSwitch(BaseModel):
    onOff: int


class HeaterStatus(BaseModel):
    '''Model for the heater status.'''
    state: str = Field(
        ...,
        description='On,Off,Standby'
    )
    active_runtime: datetime.timedelta = Field(
        ...,
        description='If on, how long has it been on for in seconds. Off shall be 0 seconds'
    )


class HeaterStatusResponse(BaseResponse):
    heaters: List[HeaterStatus]


class HeaterCommandResponse(BaseResponse):
    heater: HeaterStatus


class PumpStatus(BaseModel):
    pump_id: int
    state: str = Field(
        ...,
        description='On,Off,Standby',
    )
    pump_on_timer: Optional[datetime.timedelta] = Field(
        ...,
        description='If on, how long has it been on for in seconds. Off shall be 0 seconds'
    )


class PumpStatusResponse(BaseResponse):
    water_pumps: List[PumpStatus]


class PumpCommandResponse(BaseResponse):
    water_pump: PumpStatus


class WaterSystem(BaseAPIModel):
    type: str = Field(
        'SIMPLE_PUMP|SIMPLE_WATER_HEATER|SIMPLE_LEVEL',
        description='Water system types supported are SIMPLE_PUMP, SIMPLE_HEATER, SIMPLE_LEVEL'
    )
    subType: Optional[str]


class WaterResponse(BaseAPIResponse):
    watersystems: List[WaterSystem]
    schemas: Optional[dict]


class HeaterControl(BaseModel):
    '''Dom new model for heater control.'''
    # TODO: Retire/remove unused models
    onOff: int = Field(
        default=0,
        ge=0,
        le=1,
        description=''
    )
    mode: Optional[int]
    temp: Optional[int]


PREFIX = 'watersystems'

router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['WATER SYSTEMS',]
)


wgo_logger = logging.getLogger('main_service')


def get_pump_overview(hal):
    '''Assemble the list of pumps in the vehicle.'''
    # TODO: Get list of pumps from hw layer
    # TODO: Move model to hw layer
    result = []
    pump_ids = [1, 2]
    for pump_id in pump_ids:
        pump_details = hal.watersystems.handler.get_pump_details(pump_id)
        result.append(
            {
                'id': pump_id,
                'name': pump_details.get('name', '--'),
                'description': '',
                'type': pump_details.get('type'),
                'subType': pump_details.get('subType'),
                'state': pump_details.get('state'),
                'information': {
                    'runtime': pump_details.get('runtime')
                },
                'settings': None
            }
        )
    return result


def get_tank_overview(hal):
    '''Assemble the list of tanks in the vehicle.'''
    result = []
    tank_ids = [1, 2]
    for tank_id in tank_ids:
        tank_details = hal.watersystems.handler.water_tank[tank_id].state.dict()

        #print(f'\nwup {5}\n')
        wgo_logger.debug(f'Tank_Details: {tank_details}')
        result.append(tank_details)

    return result


def get_heater_overview(hal):
    '''Assemble the list of heaters in the vehicle.'''
    result = []
    heater_ids = [1,]
    for heater_id in heater_ids:
        heater_details = hal.watersystems.handler.get_heater_details(heater_id)
        result.append(heater_details)

    return result


@router.get('', tags=['ROOT_API'])
async def get_watersystems_overview():
    raise NotImplementedError()


@router.get('/state')
async def get_watersystems_state(request: Request) -> dict:
    watersystems_state = request.app.hal.get_state().get('watersystems')
    return watersystems_state


@router.get('/wt/{instance}/state')
async def get_water_tank_state(request: Request, instance: int):
    '''Get the state of water tanks.'''
    water_tank = await validate_wc_api_call(request, SYSTEM_STR, WATER_TANK_CODE, instance)
    return water_tank.state


@router.put('/wt/{instance}/state')
async def set_water_tank_calibration(request: Request, instance: int, state: dict):
    '''Set the calibration values of water tanks.'''
    water_tank = await validate_wc_api_call(request, SYSTEM_STR, WATER_TANK_CODE, instance)
    water_tank.state.validate(state)

    updated = None
    # We use if else to only handle one, other values should be none
    if 'vltgMin' in state:
        vltgMin = state.get('vltgMin')
        if vltgMin is not None:
            water_tank.state.vltgMin = vltgMin
            updated = 'vltgMin'
    elif 'vltgMax' in state:
        vltgMax = state.get('vltgMax')
        if vltgMax is not None:
            water_tank.state.vltgMax = vltgMax
            updated = 'vltgMax'
    elif 'cap' in state:
        cap = state.get('cap')
        if cap is not None:
            water_tank.state.cap = cap
            updated = 'cap'
    else:
        print('[WATERSYSTEMS][API] Water Tank calibration had not relevant key', state)

    if updated is not None:
        # We only update that one property at a time
        water_tank.save_db_state()

    return water_tank.state


@router.get('/wp/{instance}/state')
async def get_water_pump_state(request: Request, instance: int):
    '''Get the state of water pumps.'''
    water_pump = await validate_wc_api_call(request, SYSTEM_STR, WATER_PUMP_CODE, instance)
    return water_pump.state


@router.put('/wp/{instance}/state')
async def set_water_pump_state(request: Request, instance: int, state: dict):
    '''Set the desired state of water pumps.'''
    # TODO: Figure out best way to validate the model per instance
    water_pump = await validate_wc_api_call(request, SYSTEM_STR, WATER_PUMP_CODE, instance)
    result = water_pump.set_state(state)

    await request_to_iot_handler(
        request,
        result.dict(exclude_none=True)
    )
    return result


@router.get('/wh/{instance}/state', tags=['WATER HEATER', ])
async def get_water_heater_state(request: Request, instance: int):
    '''Get state of water heaters.'''
    water_heater = await validate_wc_api_call(request, SYSTEM_STR, WATER_HEATER_CODE, instance)
    return water_heater.state


@router.put('/wh/{instance}/state', tags=['WATER HEATER', ])
async def set_water_heater_state(request: Request, instance: int, in_state: dict):
    '''Set desired state of water heaters.'''
    # TODO: Figure out best way to validate the model per instance
    water_heater = await validate_wc_api_call(
        request,
        SYSTEM_STR,
        WATER_HEATER_CODE,
        instance
    )
    # If unit provided, convert
    set_temp_in = in_state.get('setTemp')
    if set_temp_in is not None and in_state.get('unit', 'C') == 'F':
        set_temp_in = fahrenheit_2_celcius(set_temp_in)
        in_state['setTemp'] = set_temp_in

    try:
        water_heater.state.validate(in_state)
    except ValidationError as err:
        print(err)
        raise HTTPException(
            422,
            str(err)
        )

    try:
        water_heater.set_state(
            in_state
        )
    except ValueError as err:
        print(err)
        raise HTTPException(
            423,
            {
                'result': 'FAIL',
                'msg': 'Lockouts not met.'
            }
        )

    return water_heater.state


@router.put('/wh/{instance}/settings/restoredefault', tags=['WATER HEATER', ])
async def reset_water_heater_settings(request: Request, instance: int):
    '''Reset water heater to its defaults.'''
    # TODO: Figure out best way to validate the model per instance
    water_heater = await validate_wc_api_call(request, SYSTEM_STR, WATER_HEATER_CODE, instance)
    # TODO: Set defaults for the water heater
    WH_DEFAULT_SET_TEMP = 45.0
    DEFAULT_WH_STATE = {
        'setTemp': WH_DEFAULT_SET_TEMP,
        'mode': EventValues.COMFORT
    }
    water_heater.set_state(DEFAULT_WH_STATE)
    # TODO: Should that be done in the component as a default method like set_defaults ?
    return water_heater.state


@router.get('/tc/{instance}/state')
async def get_toilet_circuit_state(request: Request, instance: int):
    '''Get the state of toilet power.'''
    toilet_circuit = await validate_wc_api_call(request, SYSTEM_STR, TOILET_CIRCUIT_CODE, instance)
    return toilet_circuit.state


@router.put('/tc/{instance}/state', tags=['WATER HEATER',])
async def set_toilet_circuit_state(request: Request, instance: int, state: dict):
    '''Set desired state of toilet power.'''
    # TODO: Figure out best way to validate the model per instance
    toilet_circuit = await validate_wc_api_call(request, SYSTEM_STR, TOILET_CIRCUIT_CODE, instance)
    result = request.app.hal.watersystems.handler.set_toilet_circuit_state(
        instance,
        state
    )
    await request_to_iot_handler(
        request,
        result.dict(exclude_none=True)
    )
    return result


# ###########
# # Settings
# ###########
# Getting settings lives in ui/watersystems as it is mainly used to visualize state and provide list of options

@router.get('/settings')
async def get_settings(request: Request):
    '''Get settings from main app and inject units.'''
    water_systems = request.app.config.get('watersystems')
    mapped_values = {
        k: {
            'value': v,
            'unit': WATER_UNITS.get(v)
        } for (k, v) in water_systems.items()
    }
    response = {
        'config': water_systems,
        'units': mapped_values
    }
    return response


@router.put('/settings')
async def set_settings(request: Request, body: dict):
    '''Update the given settings.'''

    item = body.get('item')
    value = body.get('value')

    watersystems = request.app.config.get('watersystems')
    print(watersystems)

    # print(f'\nwup {13}\n')
    if watersystems is None:
        raise ValueError('Watersystems not part of the config')

    updated = False
    if item in watersystems:
        # Compare
        if watersystems[item] != value:
            watersystems[item] = value
            updated = True

    # Get the settings that are updated
    # Update them in the appropriate system (mapping to HW, SW or State logic)
    # Return OK / NOK result

    response = {
        'updated': updated,
        'item': item,
        'value': watersystems[item]
    }
    # request_to_iot_handler(
    #     request,
    #     body
    # )
    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": '/api/watersystems/settings',
            "body": body
        }
    )

    return response


@router.get('/schemas')
async def get_schemas(include=None):
    all_schemas = {
        # These came from model - not components currently TODO: DO we need to change?
    #     'SIMPLE_PUMP': SIMPLE_PUMP_STATE.schema(),
    #     'SIMPLE_WATER_HEATER': SIMPLE_WATER_HEATER_STATE.schema(),
    #     'TRUMA_WATER_HEATER': TRUMA_WATER_HEATER_STATE.schema(),
    #     'SIMPLE_TANK': SIMPLE_TANK_STATE.schema()
    }

    schemas = {}

    if include is not None:
        include_list = include.split(',')
        for s in include_list:
            schemas[s.upper()] = all_schemas.get(s.upper())
        return schemas

    return all_schemas
