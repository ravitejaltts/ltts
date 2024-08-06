import datetime
from typing import Optional, List, Literal

import time
from copy import deepcopy

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks

from pydantic import BaseModel, Field

from common_libs.models.common import (
    EventValues,
)

from main_service.components.common import (
    SimpleOnOff,
)
from main_service.components.lighting import LightGroupState

# TODO: Remove this below, no need to follow a baseresponse
from .common import (
    BaseAPIResponse,
)

from common_libs.models.notifications import (
    request_to_iot_handler,
)
from common_libs.models.common import RVEvents, EventValues
from common_libs.models.common import LogEvent

from main_service.modules.api_helper import validate_wc_api_call


ALL_GROUP_LZ = 0
SMARTTOGGLE_GROUPS = [0, 101]   # TODO: Get from config which one is of type MASTER
INTERIOR_GROUP = 99
EXTERIOR_GROUP = 100


def control_lighting_zone(hal, zone_id, light_control, preset=False):
    '''Function to control lighting zones.'''
    brightness_result = None
    rgb_result = None
    color_temp_result = None
    onoff_result = None

    if zone_id == ALL_GROUP_LZ:
        # We update the state of the master light state one key at a time
        master_state = hal.lighting.handler.state.get(zone_id, {})
        # TODO: Check if deepcopy is needed
        if light_control.onOff is not None:
            master_state['onOff'] = light_control.onOff
        if light_control.brt is not None:
            master_state['brt'] = light_control.brt
        if light_control.rgb is not None:
            master_state['rgb'] = light_control.rgb
        if light_control.clrTmp is not None:
            master_state['clrTmp'] = light_control.clrTmp
        hal.lighting.handler.state[zone_id] = master_state
        for z_id, zone in hal.lighting.handler.lighting_zone.items():
            control_lighting_zone(hal, z_id, light_control, preset=True)

        return master_state

    # TODO: Push the default state logic to get_state
    current_state = hal.lighting.handler.lighting_zone[zone_id].state

    # zone = hal.lighting.handler.zones_by_id.get(zone_id)
    try:
        zone = hal.lighting.handler.lighting_zone[zone_id]
    except KeyError as err:
        if preset is True:
            return
        else:
            print(err)
            raise

    zone_type = zone.type

    if zone_type == 'simple':
        # Overwrite whatever we receive
        # Handle edge cases like ITC controller based brightness
        # Czone in HW layer
        light_control.brt = None
        try:
            light_control.clrTmp = None
            light_control.rgb = None
        except Exception as err:
            print(f"Minor bug? {err}")

    elif zone_type == 'dimmable':
        try:
            light_control.clrTmp = None
            light_control.rgb = None
        except Exception as err:
            print(f"Minor bug? {err}")

    elif zone_type == 'RGBW':
        raise TypeError(f'Unsupported zone type: {zone_type}')

    else:
        raise TypeError(f'Unsupported zone type: {zone_type}')

    if light_control.brt is not None:
        # We send brightness always as received, no state check to avoid unexpected user feedback
        brightness = light_control.brt

        # Check if desired brightness is different (for combo requests)
        if current_state.brt != brightness:
            b_res = hal.lighting.handler.zone_brightness(zone_id, brightness)
            print(f'Zone {zone_id} Brightness changed {brightness}')

    if light_control.onOff is not None:
        # We send onOff always as received, no state check to avoid unexpected user feedback
        onOff = light_control.onOff
        onoff_result = hal.lighting.handler.zone_switch(zone_id, onOff)

        # TODO - HERE WAS THE KILLER
        # setting the lights on when a brightness is applied but onOFF is OFF

        if onOff:
            if light_control.clrTmp is not None and light_control.clrTmp != current_state.get('clrTmp'):
                # Temp should only be emitted on change as it otherwise conflicts with rgb
                color_temp = light_control.clrTmp
                _ = hal.lighting.handler.zone_colortemp(zone_id, color_temp, rgb=light_control.rgb)
                if current_state.get('onOff') == 0:
                    # Turn on as well if not coming from a preset
                    onoff_result = hal.lighting.handler.zone_switch(zone_id, 1)

    else:
        if light_control.rgb is not None and light_control.rgb != current_state.get('rgb'):

            # rgb should only be emitted on change as it otherwise conflicts with temp
            # if light_control.rgb is None:
            #     light_control.rgb = "#000000"

            if not light_control.rgb.startswith('#'):
                light_control.rgb = f'#{light_control.rgb}'
                # raise HTTPException('RGB needs to prefix # to align with HTML color setting')

            rgb = light_control.rgb
            rgb_result = hal.lighting.handler.zone_rgb(zone_id, rgb)

            if current_state.get('onOff') == 0 and preset is False:
                # Turn on as well if not coming from a preset
                onoff_result = hal.lighting.handler.zone_switch(zone_id, 1)

    zone_state = zone.state
    result = zone_state

    if zone_id != 0:
        zone.override_light_groups()

    return result


# class RgbStatus(BaseModel):
#     ''''''
#     r: int = Field(
#         ...,
#         description='Value of Red',
#         ge=0,
#         le=255
#     )
#     g: int = Field(
#         ...,
#         description='Value of Green',
#         ge=0,
#         le=255
#     )
#     b: int = Field(
#         ...,
#         description='Value of Blue',
#         ge=0,
#         le=255
#     )


# class LightBase(BaseModel):
#     onOff: int


# class Light(BaseModel):
#     '''Light message for a specific group or light'''
#     light_id: Optional[int] = 0
#     zone_id: Optional[int] = 0
#     brt: Optional[int] = Field(
#         ...,
#         description='Value of brightness in %',
#         le=0,
#         ge=100
#     )
#     rgb: Optional[RgbStatus]


class SimpleDim(BaseModel):
    onOff: Optional[int] = Field(
        None,
        ge=-1,
        le=1,
        description='Sets a Zone off or on 0=Off, 1=On, for state responses a third type of -1 is possible for Unknown states e.g during init. A state of 2 might be used for future cases.'
    )
    brt: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description='The value for brightness between 0 and 100%'
    )


class RGBW(BaseModel):
    onOff: Optional[int] = Field(
        None,
        ge=-1,
        le=1,
        description='Sets a Zone off or on 0=Off, 1=On, for state responses a third type of -1 is possible for Unknown states e.g during init. A state of 2 might be used for future cases.'
    )
    brt: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description='The value for brightness between 0 and 100%'
    )
    rgb: Optional[str] = Field(
        None,
        description='RGB HTML string prefixed #, #RRGGBB'
    )
    colorTemp: Optional[int] = Field(
        None,
        ge=2000,
        le=10000,
        description='Color temp in Kelvin'
    )

    # TODO: Removed until frontend bug is fixed
    # @validator('rgb')
    # def rgb_startswith_hash(cls, v):
    #     assert v.startswith('#'), 'must start with # and follow #RRGGBB format'
    #     return v


# class LightSchedule(BaseModel):
#     '''Schedule object for Lighting'''
#     light_id: Optional[int] = 0
#     zone_id: Optional[int] = 0
#     auto_off_time: datetime.datetime


# class LightStatus(BaseModel):
#     '''Status Response Message'''
#     lights: List[Light]
#     schedules: List[LightSchedule]


class APIItem(BaseModel):
    path: str
    PUT: Optional[dict]
    GET: Optional[dict]


class LightZone(BaseModel):
    '''Describes a zone of lights'''
    id: Optional[int]
    type: Optional[str] = Field(
        'RGBW',
        description='Light types that are supported such as Simple, SimpleDim, RGBW'
    )
    name: Optional[str]
    description: Optional[str]
    # TODO: Confirm not needed in API
    # controller_type: str
    state: Optional[dict]
    api: Optional[APIItem]


# class Brightness(BaseModel):
#     '''Request Model for zone/light brightness'''
#     value: int = Field(
#         ...,
#         ge=0,
#         le=100,
#         description='The value for brightness must be => 0 and <= 100, where 0 is off and 100 is 100% brightness'
#     )


class LightControl(BaseModel):
    '''Request model for controls to a lighting zone.'''
    brt: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description='The value for brightness between 0 and 100%'
    )
    onOff: Optional[Literal[EventValues.OFF, EventValues.ON]] = Field(
        None,
        description='Sets a Zone off or on 0=Off, 1=On, for state responses a third type of -1 is possible for Unknown states e.g during init. A state of 2 might be used for future cases.'
    )
    rgb: Optional[str] = Field(
        None,
        description='RGB HTML string prefixed #, #RRGGBB'
    )
    clrTmp: Optional[int] = Field(
        None,
        ge=2000,
        le=10000,
        description='Color temp in Kelvin'
    )

    # @validator('rgb')
    # def rgb_startswith_hash(cls, v):
    #     assert v.startswith('#'), 'must start with # and follow #RRGGBB format'
    #     return v


class LightResponse(BaseAPIResponse):
    '''General action response to Light commands'''
    lighting: List[LightZone]
    # api_overview: List[APIItem]
    features: list
    schemas: Optional[dict]


# class LightConfig(BaseModel):
#     '''Configurable items in the lighting system.'''
#     fadein: bool = Field(
#         ...,
#         description='If the lighting system supports fade-in, this will be to change the setting'
#     )
#     fadeout: bool = Field(
#         ...,
#         description='If the lighting system supports fade-out, this will be to change the setting'
#     )
#     fade_timer: int


# class GenericKeyValue(BaseModel):
#     data: dict


# class LightingPresetStore(BaseModel):
#     name: Optional[str] = Field(
#         'Preset Switch',
#         description='Update the name of the preset switch',
#         max_length=15
#     )


# class LightingPresetState(BaseModel):
#     active: bool = Field(
#         False,
#         description='If active is True, this is currently the selected preset, used to show on UI'
#     )
#     name: str = Field(
#         'Preset Switch',
#         description='Name of the switch',
#         max_length=10
#     )


# class LightingGroupState(BaseModel):
#     # instance: int = Field(
#     #     None,
#     #     description='Instance of lighting group, 0 is used for master switch / smart toggle, rest for presets'
#     # )
#     onOff: int = Field(
#         0,
#         description='Lighting Group defines a permanent or temporary set of lights taht act together for presets, master toggles etc.',
#         ge=0,
#         le=1
#     )
#     name: str = Field(
#         None,
#         description='Name this group has, such as Preset 1, Master, Smart Light, etc. might be changed by the user'
#     )
#     # map: str = Field(
#     #     None,
#     #     description='Stores the changed light zones ???'
#     # )


# class LightingPresetFull(BaseModel):
#     id: int
#     state: LightingPresetState
#     zones: List[LightZone]


PREFIX = 'lighting'

router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['Lighting', ]
)


schema_mapping = {
    'SIMPLE_DIM': SimpleDim,
    'SIMPLE_ONOFF': SimpleOnOff,
    'RGBW': RGBW,
    'LIGHT_RESPONSE': LightResponse
}


@router.get('', response_model=LightResponse, response_model_exclude_none=True, tags=['ZONE', 'ROOT_API'])
async def get_lighting_overview(request: Request):
    '''Root API for Lighting systems.

    Lighting systems consist out of lighting zones of various supported types:

    - RGBW (onOff, Brightness, colorTemp, RGB)
    - SIMPLE_ONOFF (onOff)
    - SIMPLE_DIM (onOff, Brightness)
    '''
    raise NotImplementedError('Reworking the purpose of this endpoint')


@router.get('/state')
async def get_lighting_state_overview(request: Request):
    '''Twin like response for lighting system.'''
    # Get lightzones from HW Layer

    lighting_state = request.app.hal.get_state().get('lighting')

    # Keys to not put into the twin state for lighting group
    ignore_list = (
        'light_map',
        'save'
    )

    # TODO: Find a way to handle this based on being a setting or not in the
    # component state
    response = {}
    for instance, comp in lighting_state.items():
        comp = comp.dict()
        print('instance', instance, 'comp', comp)
        if instance.startswith('lg'):
            comp = await get_lighting_group_state(request, int(instance[2:]))
            comp = comp.dict()
            for key in ignore_list:
                print(key, comp, type(comp))
                if key in comp:
                    print(key, 'found')
                    del comp[key]
        response[instance] = comp

    return response


# Test code below - state above is what is desired
@router.get('/states')
async def get_lighting_state(request: Request) -> dict:
    try:
        lighting_state = request.app.hal.lighting.handler.state

        return lighting_state

    except Exception as err:
        raise HTTPException(
            500, f'Lighting state failure: {err}')


@router.get('/lz/{zone_id}/state', tags=['ZONE'])
async def get_lighting_zone_state(request: Request, zone_id: int) -> dict:
    '''Control the given lighting zone zone_id based on the type of light.

    Simple: Supports onOff
    SimepleDim: Supports onOff and brightness
    RGBW: Supports onOff, brightness, rgb, colorTemp

    zone_id 0 controls all zones at once, however there is a smarttoggle functionality
        defined that is to be used to keep the previous state before turning off.
    '''
    # START = time.time()
    light_zone = await validate_wc_api_call(request, PREFIX, 'lz', zone_id)
    # print('PROFILING validate_wc_api_call', int((time.time() - START) * 1000), 'MS', 'LZ', zone_id)

    return light_zone.state


@router.put('/zones/{zone_id}/state', tags=['ZONE'])
@router.put('/lz/{zone_id}/state', tags=['ZONE'])
async def set_zone(request: Request, zone_id: int, state: dict):
    if zone_id == 0:
        # All zones
        control_lighting_zone(request.app.hal, 0, LightControl(**state))
        response = request.app.hal.lighting.handler.lighting_group[0].state
    else:
        light_zone = await validate_wc_api_call(request, PREFIX, 'lz', zone_id)

        response = light_zone.set_state(state)

    try:
        await request_to_iot_handler(request, response.dict(exclude_none=True))
    except AttributeError as e:
        print(e, response)

    return response


@router.put('/lz/{zone_id}/defaults', tags=['ZONE'])
async def set_zone_defaults(request: Request, zone_id: int):
    light_zone = await validate_wc_api_call(request, PREFIX, 'lz', zone_id)
    response = light_zone.set_state_defaults()

    try:
        await request_to_iot_handler(request, response.dict(exclude_none=True))
    except AttributeError as e:
        print(e, response)

    return response


# TODO: Convert to background task
@router.put('/notification')
async def light_notification(request: Request, level: str = 'WARNING'):
    '''If triggered lights up a configured pattern and color to visual
    notifications to the user. Initial application is load shedding.'''
    level = level.lower()
    if level == 'error':
        pass
    elif level == 'warning':
        pass
    elif level == 'info':
        pass
    else:
        pass

    request.app.hal.lighting.handler.notification(level)

    await request_to_iot_handler(request, {"level": level})

    return {'level': level}


@router.get('/lg/{group_id}/state')
async def get_lighting_group_state(request: Request, group_id: int):
    # We can use a specific model here as groups are not instance dependent
    # Master might be handled separately, but all other ids act the same

    light_group = await validate_wc_api_call(request, 'lighting', 'lg', group_id)

    if group_id == EXTERIOR_GROUP:
        light_group.check_group(attribute='exterior', skip_if_True=False)

    elif group_id == INTERIOR_GROUP:
        light_group.check_group(attribute='exterior', skip_if_True=True)
    elif group_id == 0:
        # use the check group function for 0 by using a none existant attribute.
        light_group.check_group(attribute='ALL', skip_if_True=True)

    response = light_group.state

    return response


@router.put('/group/{group_id}/set')
async def set_lighting_group_old(request: Request, group_id: int):
    light_group = await validate_wc_api_call(request, 'lighting', 'lg', group_id)

    response = light_group.save()
    return response


@router.put('/group/{group_id}/activate')
async def activate_lighting_group_old(request: Request, group_id: int):
    light_group = await validate_wc_api_call(request, 'lighting', 'lg', group_id)

    response = light_group.activate()
    return response


@router.put('/master/state')
@router.put('/lg/{instance}/state')
async def set_lighting_group_state(request: Request, state: dict, instance: int=0):
    # We can use a specific model here as groups are not instance dependent
    # Master might be handled separately, but all other ids act the same
    light_group = await validate_wc_api_call(
        request,
        'lighting',
        'lg',
        instance
    )

    print('[LIGHTING][GROUP] Received', instance, light_group)

    if instance in SMARTTOGGLE_GROUPS:
        # Perform smarttoggle / master
        # Handle non int
        if 'brt' in state:
            state['brt'] = int(round(float(state['brt']), 0))

        response = request.app.hal.lighting.handler.smartToggle(state)
        print('Smarttoggle Response', response)

    elif instance == EXTERIOR_GROUP:
        for instance, light in request.app.hal.lighting.handler.lighting_zone.items():
            if light.attributes.get('exterior') is True:
                # Turn off / on
                light.set_state(
                    {
                        'onOff': state.get('onOff')
                    }
                )

        light_group.state.onOff = state.get('onOff')
        response = light_group.state

    elif instance == INTERIOR_GROUP:
        for instance, light in request.app.hal.lighting.handler.lighting_zone.items():
            if light.attributes.get('hidden', False) is False:
                if light.attributes.get('exterior', False) is False:
                    light.set_state(
                            {
                                'onOff': state.get('onOff')
                            }
                        )
            else:
                light.set_state(
                            {
                                'onOff': EventValues.ON
                            }
                        )
        light_group.state.onOff = state.get('onOff')
        response = light_group.state
        # raise NotImplementedError('Internal Light Group not yet implemented')
    else:
        print('[LIGHTING][GROUP] STATE', state)
        if state.get('save') == EventValues.TRUE:
            response = light_group.save()
            print('[LIGHTING][GROUP] Save triggered', response)

        elif state.get('onOff') == EventValues.ON:
            try:
                response = light_group.activate()
            except ValueError as err:
                print('[LIGHTING][GROUP] No saved lights, exit')
                light_group.override_light_groups()
                raise HTTPException(400, {'msg':str(err)})

            print('[LIGHTING][GROUP] Activate triggered', response)

        else:
            response = light_group.state
            print('[LIGHTING][GROUP] Preset Else', response)

    # TODO: This may nver turn them off - which we need to check in another location
    request.app.event_logger(
            LogEvent(
                event=RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_OPERATING_MODE_CHANGE,
                instance=instance,
                value=state.get('onOff')
            ),
            force=True
        )

    await request_to_iot_handler(
        request,
        state
    )

    return response


@router.get('/settings')
async def set_settings(request: Request):
    '''Update settings related to lighting in the main app/state.'''
    # TODO: Make this a reusable function across all settings for all modules/routers

    lighting = request.app.config.get('lighting')
    if lighting is None:
        raise ValueError('Lighting not part of app config')

    return lighting


@router.get('/schemas')
async def get_schemas(request: Request, include=None):
    '''Get lighting schemas.'''
    schemas = {}

    for _id, zone in request.app.hal.lighting.handler.lighting_zone.items():
        print(zone.state.schema())
        schemas[zone.state.schema().__name.upper()] = zone.state.schema()

    if include is not None:
        include_list = include.split(',')
        for s in include_list:
            schemas[s.upper()] = all_schemas.get(s.upper())
        return schemas

    return schemas


@router.put('/reset')
async def reset_lighting(request: Request):
    '''Perform a reset of the lighting system to avoid 'disco mode' and other
    anomalies blocking the user'''
    result = request.app.hal.lighting.handler.perform_reset()

    await request_to_iot_handler(
        request,
        None
    )
    return {
        'result': result
    }


@router.put('/manufacturing/reset')
async def reset_lighting_for_manufacturing(request: Request):
    '''Perform a reset of the lighting system to avoid 'disco mode'
    and turn all lights on for maunfacturing.'''
    # Lighting hal does not exist in Vanilla
    if request.app.hal.floorPlan == 'VANILLA':
        # Only handles ITC right now
        # Perform raw can messages here
        # Open EEPROM
        request.app.can_sender.can_send_raw('0CFC0044', 'FFFF6E01FFFFFFFF')
        request.app.can_sender.can_send_raw('0CFC0044', 'FFFF02FF00FFFFFF')
        request.app.can_sender.can_send_raw('0CFC0044', 'FFFF06FF0100FFFF')
        request.app.can_sender.can_send_raw('0CFC0044', 'FFFF01FFFFFFFFFF')
        # Close EEPROM
        request.app.can_sender.can_send_raw('0CFC0044', 'FFFF6E00FFFFFFFF')
        result = 'OK'

    else:
        result = request.app.hal.lighting.handler.perform_reset(
            set_all_on=True
        )

    await request_to_iot_handler(
        request,
        None
    )
    return {
        'result': result
    }


@router.put('/disco')
async def disco_mode(request: Request):
    '''Enable Disco for lighting testing'''
    result = request.app.hal.lighting.handler.enable_disco()

    await request_to_iot_handler(
        request,
        None
    )

    return {
        'result': result
    }


@router.put('/all')
async def all_mode(request: Request, light_control: LightControl):
    '''Turn On or Off   - ALL  lighting'''
    if light_control.onOff == 1:
        result = request.app.hal.lighting.handler.all_on()
    elif light_control.onOff == 0:
        result = request.app.hal.lighting.handler.all_off()
    else:
        result = 'Bad Request'

    return {
        'result': result
    }
