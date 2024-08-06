from fastapi import APIRouter, Request, HTTPException

from pydantic import BaseModel, Field

from main_service.modules.api_helper import validate_wc_api_call

from common_libs.models.notifications import request_to_iot
from common_libs.models.common import RVEvents

from common_libs import environment


_env = environment()


class VIN(BaseModel):
    vin: str = Field(
        '',
        description='VIN temp model',
        min_length=17,
        max_length=17
    )


SYSTEM_STR = 'vehicle'


router = APIRouter(
    prefix=f'/{SYSTEM_STR}',
    tags=['VEHICLE']
)


@router.get('/ignition_key')
async def get_ignition(request: Request) -> dict:
    ignition_key = request.app.hal.vehicle.handler.state.get('key_position')
    response = {
        'ignition_key': ignition_key
    }
    return response


@router.get('/vin')
async def get_vin(request: Request) -> dict:
    vin = request.app.hal.vehicle.handler.state.get('vin')
    if vin is None:
        vin = request.app.config.get('VIN')

    response = {
        'vin': vin
    }
    return response


@router.put('/vin')
async def set_vin(request: Request, data: VIN) -> dict:
    current_vin = request.app.hal.vehicle.handler.state.get('vin')
    # Check that a vin only contains alpanumeric and make it upper case
    vin = data.vin.upper()
    if not vin.isalnum():
        raise HTTPException(422, {'msg': f'VIN is not valid: {data.vin}'})

    if current_vin is None:
        request.app.config['VIN'] = vin
        request.app.hal.vehicle.handler.state['vin'] = vin
    else:
        if vin != current_vin:
            # Need to update
            request.app.config['VIN'] = vin
            request.app.hal.vehicle.handler.state['vin'] = vin

    response = {
        'vin': vin
    }
    request.app.hal.vehicle.handler.event_logger.add_event(
        RVEvents.CHASSIS_VIN_CHANGE,
        1,
        vin
    )

    try:
        with open(_env.vin_file_path(), 'w') as vin_file:
            vin_file.write(vin.strip())
    except IOError as err:
        print('IO Error, writing: ', _env.vin_file_path(), err)
        raise

    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": f'/api/vehicle/vin',
            "body": data
        }
    )

    return response


@router.get('/soc')
async def get_soc(request: Request) -> dict:
    return {
        'soc': 100
    }


@router.get('/ch/{instance}/state')
async def get_ch_state(request: Request, instance: int):
    vehicle = await validate_wc_api_call(request, SYSTEM_STR, 'ch', instance)

    return vehicle.state


@router.put('/ch/{instance}/state')
async def set_ch_state(request: Request, instance: int, state: dict):
    vehicle = await validate_wc_api_call(request, SYSTEM_STR, 'ch', instance)
    # Validate schema
    try:
        vehicle.set_state(state)
    except ValueError as err:
        print('Error setting vehicle to', state, err)
        raise HTTPException(400, detail={'state': state, 'err': str(err)})

    return vehicle.state


@router.get('/dl/{instance}/state')
async def get_dl_state(request: Request, instance: int):
    door_lock = await validate_wc_api_call(request, SYSTEM_STR, 'dl', instance)
    return door_lock.state


@router.put('/dl/{instance}/state')
async def set_dl_state(request: Request, instance: int, state: dict):
    door_lock = await validate_wc_api_call(request, SYSTEM_STR, 'dl', instance)
    # Validate schema
    try:
        door_lock.set_state(state)
    except ValueError as err:
        print('Error setting door lock to', state, err)
        raise HTTPException(400, detail={'state': state, 'err': str(err)})

    return door_lock.state
