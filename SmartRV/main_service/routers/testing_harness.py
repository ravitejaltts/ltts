import datetime

from typing import Optional, List
from enum import Enum
import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel

from .common import ResultLevel, not_implemented

from common_libs.models.system import Proximity

from main_service.modules.test_helper import weston_debug, weston_screenshot

from common_libs.models.common import (
    CODE_TO_ATTR,
    ATTR_TO_CODE
)

from main_service.modules.sw_features import Features


class Temperature(BaseModel):
    '''Temperature message for setting and getting.'''
    temp_set: float
    temp_current: float


class TimeInterval(BaseModel):
    '''.'''
    start_time: datetime.datetime
    end_time: datetime.datetime
    temp_desired: float
    fanSpd: int


class Schedule(BaseModel):
    '''Schedule setting for a specific Zone.'''
    name: str
    time_intervals: List[TimeInterval]
    active: bool


class QuickAction(BaseModel):
    '''Individual Quick Action item.'''
    icon: str
    header: str
    tooltip: str
    sub_header: str
    action_type: str


class RawCAN(BaseModel):
    '''Raw CAN messags to send via cansend command'''
    can_interface: str
    cansend: str

    # priority: int
    # dgn: str
    # source_address: str
    # data: str


class AlgoSetting(BaseModel):
    onOff: int


router = APIRouter(
    prefix='/testharness',
    tags=['TESTING', ]
)


@router.put('/{category}/{code}/{instance}/state/override')
async def override_generic_state(request: Request, category: str, code: str, instance: int, partialState: dict, validate_state: bool = False):
    '''Allows sending a desired state to the component state properties.

    It can accept one or more properties.

    It will ignore additional properties that are not present in the component
    state.'''

    if not hasattr(request.app.hal, category):
        raise HTTPException(404, {'msg': f'Cannot find category {category}'})

    handler = getattr(request.app.hal, category).handler

    attr_code = CODE_TO_ATTR.get(code)
    if attr_code is None:
        raise HTTPException(
            404,
            {
                'msg': f'Cannot find code {code} in CODE_TO_ATTR'
            }
        )

    if not hasattr(handler, attr_code):
        raise HTTPException(
            404,
            {
                'msg': f'Cannot find code {code} ({CODE_TO_ATTR.get(code)})'
            }
        )

    componentType = getattr(handler, CODE_TO_ATTR.get(code))
    if instance not in componentType:
        raise HTTPException(
            404,
            {
                'msg': f'Cannot find instance {instance} in {category} {code}'
            }
        )

    component = getattr(handler, CODE_TO_ATTR.get(code))[instance]

    if validate_state is False:
        # Iterate over incoming values and apply as is
        for key, value in partialState.items():
            if hasattr(component.state, key):
                setattr(component.state, key, value)
    else:
        # Validate the state
        validation_result = component.validate_state(partialState)
        if validation_result:
            raise HTTPException(422, validation_result)

    return component.state


@router.get('/status')
async def status() -> dict:
    '''Respond with details of the test harness enabled'''
    return {'Status': 'OK'}


@router.get('/quick_actions', response_model=List[QuickAction])
async def get_quickactions() -> list:
    '''Get list of quick actions for testing.'''
    actions = [
        QuickAction(
            icon="mfi-test-someicon",
            header="Test",
            sub_header="Button",
            tooltip="Some tooltip",
            action_type="Button"
        ),
        QuickAction(
            icon="mfi-test-someicon2",
            header="Test2",
            sub_header="Button",
            tooltip="Some tooltip2",
            action_type="Button"
        ),
    ]
    return actions


@router.put('/notifications')
async def put_notifications(value: dict) -> dict:
    '''Send a notification to the UI'''
    print(value)
    return {}


@router.put('/state')
async def put_state(request: Request, value: dict) -> dict:
    '''Set state values externally.'''
    request.app.state = value
    return request.app.state


@router.put('/state_value')
async def put_state_sub_value(request: Request, value: dict) -> dict:
    '''Set the value for a given state key.'''
    print(value)
    key = value.get('sub_system')
    items = value.get('value')
    print(key, items)
    request.app.state[key] = items
    return request.app.state


@router.put('/proximity')
async def put_proximity_status(request: Request, proxy: Proximity) -> dict:
    '''Sets proximity value for testing.'''
    request.app.state['proximity'] = proxy
    print(proxy.proximity_state)
    print(dir(proxy.proximity_state))
    print(proxy.proximity_state.value)
    print(proxy.proximity_state.name)
    return request.app.state['proximity']


# @router.put('/raw_can')
# async def put_raw_can(request: Request, msg: RawCAN) -> dict:
#     '''Send a raw can message for testing.'''
#     if not msg.can_interface in ('canb0s0', 'canb1s0', 'can0', 'can1', 'vcan'):
#         raise HTTPException(401, f'Cannot access interface: {msg.can_interface}')

#     request.app.can_sender.can_send_raw(

#     )

#     cmd = f'cansend {msg.can_interface} {msg.cansend.replace(" ", "")}'
#     print(cmd)

#     return {
#         'status': 'OK'
#     }


@router.get('/stats')
async def get_stats(request: Request) -> dict:
    '''Get statistics for various things. TBD'''
    return request.app.state.get('stats', {})


@router.put('/ui_debug')
async def enable_ui_debug(request: Request) -> dict:
    # Restart Weston with debug enabled
    # Restart Kiosk browser to ensure it is visible
    proc = weston_debug(1, request.app)
    print(proc)
    return str(proc)


@router.get('/screenshot')
async def get_screenshot(request: Request) -> dict:
    screenshot = weston_screenshot()
    if screenshot is None:
        return {
            'detail': 'cannot get screenshot from weston'
        }
    else:
        return {}


@router.put('/algo/{algo_name}')
async def put_algo_enabled(request: Request, algo_name, data: AlgoSetting):
    '''Update given algorithms to be enabled/disabled for testing.'''
    print('algorithm', algo_name, data.onOff)
    if algo_name == 'lvl2':
        request.app.hal.energy.handler.state['lvl2_algo_enabled'] = data.onOff
    elif algo_name == 'climate':
        request.app.hal.climate.handler.state['climate_algo_enabled'] = data.onOff
    elif algo_name == 'loadshedding':
        request.app.hal.energy.handler.state['load_shedding_enabled'] = data.onOff
    else:
        return {'msg': 'Unkown algorithm'}
    return {'msg': f'{algo_name} state: {data.onOff}'}


@router.get('/algo/{algo_name}')
async def get_algo_enabled(request: Request, algo_name):
    print('algorithm', algo_name)
    if algo_name == 'lvl2':
        on_off = request.app.hal.energy.handler.state.get('lvl2_algo_enabled')
    elif algo_name == 'climate':
        on_off = request.app.hal.climate.handler.state.get('climate_algo_enabled')
    elif algo_name == 'loadshedding':
        on_off = request.app.hal.energy.handler.state.get('load_shedding_enabled')
    else:
        return {'msg': 'Unknown algorithm'}
    return {
        algo_name: on_off
    }


@router.get('/config')
async def get_config(request: Request):
    return request.app.config


@router.put('/config')
async def set_config_value(request: Request, config: dict):
    cfg = request.app.config
    # NOTE: There is no check if that config exists
    # if '.' in config.get('cfg_key'):
    #     # TODO: Unpack as nested dict
    #     raise NotImplementedError('Cannot unpack nested config, yet')

    cfg_key = config.get('cfg_key')
    cfg_value = config.get('cfg_value')

    if cfg_key is None:
        raise HTTPException(400, {'msg': 'No config key provided'})

    if cfg_value is None:
        raise HTTPException(400, {'msg': 'No config value provided'})

    if cfg_key in ('settings.debugEnabled', ):
        request.app.config['settings']['debugEnabled'] = cfg_value
    else:
        if '.' in cfg_key:
            raise NotImplementedError('Cannot unpack nested config for generic items, yet')

        request.app.config[config['cfg_key']] = cfg_value

    return request.app.config


@router.get('/component/{category}/{compType}/{instance}')
async def get_hal_component(request: Request, category, compType, instance: int):
    hal = getattr(request.app.hal, category).handler
    print(hal)
    try:
        comps = getattr(hal, compType)
    except AttributeError as err:
        print(err, dir(hal))
        raise HTTPException(422, detail={'err': str(err)})

    print('Components', comps)
    # TODO: serialize HAL into some relevant info if we do nto want to keep exluding it

    return comps[instance]


@router.get('/run_gps_task')
async def run_gps_task(request: Request):
    return await Features.check_gps_task(request.app.hal)


@router.put('/deadman/test/{trigger}/', tags=['TEST', ])
async def test_deadman(request: Request, trigger: str = 'NONE', body: dict = {}):
    '''Test Endpoint to view deadman state.'''
    print('DEADMAN', trigger, body)
    deadman = request.app.config.get(
        'deadmaneatingdeadbeef',
        {'count': 0, 'start': time.time(), 'released': False, 'holdtime': 0}
    )
    if trigger == 'RELEASE':
        print('Button released after: ', time.time() - deadman['start'])
        deadman['released'] = True
    elif trigger == 'HOLD':
        deadman['count'] += 1
        print('Button held for {x} interations', deadman['count'])
        deadman['released'] = False
        deadman['holdtime'] = time.time() - deadman['start']
    elif trigger == 'PRESS':
        deadman['start'] = time.time()
        deadman['released'] = False
        deadman['holdtime'] = 0
        deadman['count'] = 0

    request.app.config['deadmaneatingdeadbeef'] = deadman

    return deadman


@router.put('/db/config/delete')
async def delete_db_config_table(request: Request):
    return request.app.user_db.reset_config_table()
