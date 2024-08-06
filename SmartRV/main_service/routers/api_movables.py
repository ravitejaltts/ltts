import json

from fastapi import APIRouter, Request, HTTPException
from pydantic import ValidationError

from common_libs.models.notifications import (
    request_to_iot,
    request_to_iot_handler
)
from common_libs.system.state_helpers import check_special_states
from main_service.modules.api_helper import validate_wc_api_call

from main_service.components.movables import (
    SlideoutBasicState,
    AwningRvcState,
    # AwningLightState,
    JackState,
    EventValues
)

PREFIX = 'movables'

router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['MOVABLES', ]
)


# TODO: Add to central place
LOCKOUT_ERROR_CODE = 423
DEFAULT_MTNSENSE = 5

# CONSTANTS for API validation
SYSTEM_STR = 'movables'


@router.get("/aw/{awning_id}/state")
async def get_awning_state(request: Request, awning_id: int) -> dict:
    awning = await validate_wc_api_call(request, SYSTEM_STR, 'aw', awning_id)

    awning.check_lockouts()

    return awning.state


# Update FCP to use new format if possible
# TODO: Do not apply a State OBJ as it might be different across awnings
@router.put("/aw/{awning_id}/state")
async def set_awning_state(request: Request, awning_id: int, state: dict) -> dict:
    awning = await validate_wc_api_call(request, SYSTEM_STR, 'aw', awning_id)

    if request.state.check_special_state is True:
        result = check_special_states(component=awning, in_state=state)
        if result is not None:
            return result

    awning.check_lockouts()
    if awning.state.lockouts:
        response = {
            'msg': 'Lockout conditions not met',
            'lockouts': awning.state.lockouts
        }
        # TODO: If request comes from UI inject UI related info
        raise HTTPException(
            LOCKOUT_ERROR_CODE,
            response
        )

    # TODO: Move the state transition to the component
    if 'onOff' in state:
        state['mtnSenseOnOff'] = state['onOff']
        del state['onOff']

    result = awning.set_state(state)
    # result = request.app.hal.movables.handler.move_awning(state.dict())

    await request_to_iot_handler(
        request,
        result
    )

    return result


@router.put("/aw/{instance}/mtnsense/default")
async def set_mtnsense_default(request: Request, instance: int):
    awning = await validate_wc_api_call(request, SYSTEM_STR, 'aw', instance)
    awning.set_state(
        {
            "mtnSense": DEFAULT_MTNSENSE,
            "mtnSenseOnOff": EventValues.ON
        }
    )

    return awning.state


# # Update FCP to use new format if possible
# @router.put("/jacks")
# async def change_jacks(request: Request, state: JackState) -> dict:
#     jacks = await validate_wc_api_call(request, SYSTEM_STR, 'lj', awning_id)
#     print("movable router jacks", state)
#     result = request.app.hal.movables.handler.move_jacks(state)

#     # Add the request to the IOT queue
#     request_to_iot_handler(
#         request,
#         result.dict(exclude_none=True)
#     )

#     return result


# NEW APIS

@router.get("/so/{instance}/state")
async def slideout_state(request: Request, instance: int):
    '''Component driven GET endpoint for slideout.'''
    slideout = await validate_wc_api_call(request, SYSTEM_STR, 'so', instance)
    slideout.check_lockouts()
    return slideout.state


@router.put("/so/{instance}/state")
# SlideoutBasicState
async def set_slideout_state(request: Request, instance: int, state: dict):
    # TODO: Move this to middleware to apply on each PUT request that is in the component pattern
    # Such as /api/{category}/{code}/{instance}/state
    # Might be as simple as matching .endswith("/state")
    # We also need to ensure that it matches the allowed properties for sending only, something that is hidden
    # in the generated schema, not available int he property directly
    # Currently we can handle this by not handling any of those properties, such as lockouts when they come in
    # NEVER simply set the state to what is received even for a valid schema
    slideout = await validate_wc_api_call(request, SYSTEM_STR, 'so', instance)
    try:
        slideout.state.validate(state)
    except ValidationError as err:
        print(err)
        raise HTTPException(422, {'msg': str(err)})

    slideout.check_lockouts()
    # This is checking the stte that comes in, not the state that we currently have
    # Check if the lockout condition is met (lockout = 540)
    if slideout.state.lockouts:
        response = {
            'msg': 'Lockout conditions not met',
            'lockouts': slideout.state.lockouts
        }
        # Auto Set OFF ?
        # slideout.set_state(
        #     {
        #         'mode': EventValues.OFF
        #     }
        # )
        # TODO: If request comes from UI inject UI related info
        raise HTTPException(
            LOCKOUT_ERROR_CODE,
            response
        )

    # TODO: Need to allow safe values to pass for lockouts, such as OFF ?
    # Maybe handle this on the backend. But it would be odd to receive an error when trying to stop
    # Not all component might have a safe value

    # Warnings are not sent, nor do they need to be checked before executing.
    # A warning might turn into a lockout between receiving this API call and trying to execute

    # TODO: Get the lockouts for this instance of a component and check if any is active
    # Get lockouts that apply to this component from attributes for now
    # Eventually this can be from relationships to a lockoutComponent
    # result = request.app.hal.movables.handler.move_slideout(state, instance)
    result = slideout.set_state(state)

    return result


# @router.get("/aw/{instance}/state")
# async def awning_state(request: Request, instance: int):
#     '''Component driven GET endpoint for awning.'''
#     result = request.app.hal.movables.handler.awning[instance].state.dict()
#     return result


# @router.put("/aw/{instance}/state")
# async def change_awning_state(request: Request, instance: int, state: dict):
#     # Validate schema here
#     # AwningRvcState
#     validate_state = request.app.hal.movables.handler.awning[instance].state.validate(state)
#     print(f'aw {instance} {state}')
#     result = request.app.hal.movables.handler.change_awning(state, instance)
#     return result




# Remove unused endpoint


@router.get("/jacks")
@router.get("/lj/{instance}/state")
async def leveling_jacks_state(request: Request, instance: int = 1):
    '''Component driven GET endpoint for slideout.'''
    jacks = await validate_wc_api_call(request, SYSTEM_STR, 'lj', instance)
    result = jacks.state.dict()
    return result


@router.put("/lj/{instance}/state")
async def change_leveling_jacks_state(request: Request, instance: int, state: dict):
    # Validate schema here
    jacks = await validate_wc_api_call(request, SYSTEM_STR, 'lj', instance)
    validate_state = jacks.state.validate(
        state)
    # JackState
    result = request.app.hal.movables.handler.move_jacks(state, instance)
    return result
