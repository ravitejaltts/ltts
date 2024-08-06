import datetime

from typing import Optional, List
from enum import Enum

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel, Field

from common_libs.models.system import Proximity
from .common import ResultLevel, not_implemented, BaseResponse


# from main_service.modules.hardware.hal import hw_layer


TEMP_TYPES = (
    'fridge',
    'freezer',
    'internal',
    'outside'
)

FLUID_TYPES = (
    'black',
    'grey',
    'fresh',
    'fuel'
)


router = APIRouter(
    prefix='/sensors',
    tags=['SENSORS']
)


GALLONS_2_LITER = 3.785


# Proximity
@router.get('/proximity', response_model=Proximity)
async def proximity(request: Request) -> dict:
    response = request.app.state.get(
        'proximity_state',
        {
            'proximity_state': 'NO_CHANGE'
        }
    )
    return response


# Fluids
@router.get('/fluids', tags=['FLUIDS',])
async def fluid_list() -> dict:
    # Get list of fluid sensors
    # Report states of each
    return not_implemented()


@router.get('/fluids/by-type/{fluid_type}', tags=['FLUIDS',])
async def fluid_by_type(fluid_type) -> dict:
    return not_implemented()


@router.get('/fluids/{tank_id}', tags=['FLUIDS',])
async def fluid_by_id(tank_id: int):
    tank_state = request.app.hal.watersystems.handler.get_state(f'wt{tank_id}')

    # Get conversion rule
    capacity = float(tank_state.get('cap', 0))
    fill_level = float(tank_state.get('lvl', 0))
    current_gallons = (fill_level / 100) * ((capacity * 1000) / GALLONS_2_LITER)

    return {
        'id': tank_id,
        'state': tank_state,
        'current_absolute': current_gallons,
        'current_absolute_unit': 'gal.'
    }

# Temperature
@router.get('/temperature/{temp_id}', tags=['TEMPERATURE',])
async def temp_by_id(temp_id: int):
    temp_state = request.app.hal.sensors.handler.get_state(f'temp_{temp_id}')
    return {
        'id': temp_id,
        'state': temp_state
    }


@router.get('/temperature/{temp_type}', tags=['TEMPERATURE',])
async def temp_by_type(temp_type):
    if temp_type not in TEMP_TYPES:
        raise HTTPException('Temp Type unknown: ' + temp_type)

    return not_implemented()
