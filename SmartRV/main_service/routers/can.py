import subprocess
from collections import deque

from fastapi import APIRouter, Request, HTTPException
# from main_service.modules.hardware.hal import hw_layer as hal

import logging
import json
import time
import os
from main_service.modules.logger import prefix_log

# TODO: Make this HAL mapping
# TODO: Figure out if that
instance_key_mapping = {}

# Check if there are source agnostic mappings included
for key, value in instance_key_mapping.items():
    if '**' in key:
        instance_key_mapping['has_source_agnostic'] = True
        break


DEBUG = int(os.environ.get('WGO_MAIN_DEBUG', 0))
PROC_QUEUE = deque(maxlen=30)
wgo_logger = logging.getLogger('main_service')


print('Instance Mapping', instance_key_mapping)


def get_instance_mapped_system(hal, instance_key, instance_mapping):
    '''Get the system if any mapped to a specific instance.

    This is required when using workarounds, like using fluid level for AC current metering.
    In this case the 'obvious' system is not water systems, but needs to be diverted to energy.'''
    # Check if there is a source agnostic message
    system = None
    if instance_mapping.get('has_source_agnostic') is True:
        # Check for specific instance keys
        if instance_key in instance_mapping:
            # Return that system
            system = instance_mapping.get(instance_key)
        else:
            # modify instance key to be also checked for agnostic
            agnostic_instance_key = instance_key[:6] + '**' + instance_key[8:]
            if agnostic_instance_key in instance_mapping:
                system = instance_key_mapping.get(agnostic_instance_key)

    # print('System', system, type(system))
    if system is None:
        return None
    else:
        return getattr(hal, system)


router = APIRouter(
    prefix='/can',
    tags=['CAN', ]
)


@router.get('/')
async def show_commands(request: Request):
    return {}


@router.get('/queue')
async def return_queue(request: Request):
    return str(PROC_QUEUE)


@router.put('/event/{system}')
async def can_event(request: Request, system, body: dict):
    '''Receives CAN updated from CAN service and dispatches
    them to the right HAL handler.'''
    # Instance key uniquely identifies the sender, message and instance
    instance_key = body.get('instance_key', '')
    system = system.lower()

    hal = request.app.hal

    ignore_state = request.app.can_ignore_state
    if system in ignore_state:
        print('[IGNORECOUNT]', system)
        if ignore_state[system]['current_count'] < ignore_state[system]['ignore_count']:
            ignore_state[system]['current_count'] += 1
            return {'result': f'Ignoring state update for: {system}'}
        else:
            print('[IGNORECOUNT]', ignore_state[system]['current_count'])
            # We exit now and ignore the message

    can_state_key = instance_key + '__' + system
    request.app.can_states[can_state_key] = body

    request.app.can_counter['log_duration'] = int(
        time.time() - request.app.can_counter.get('log_start', time.time())
    )
    try:
        request.app.can_counter['total_msg_counter'] += 1
    except KeyError as err:
        print('[CAN] Keyerror in updating total_msg_counter', err)

    try:
        request.app.can_counter[can_state_key] += 1
    except KeyError:
        request.app.can_counter[can_state_key] = 1
        request.app.can_counter[can_state_key] = 1

    state_updated = False
    result = None
    can_handler = 'NA'

    hal_system = get_instance_mapped_system(
        hal,
        instance_key,
        instance_key_mapping
    )

    # TODO: Get the mapped component as per source address and update it
    start_time = time.time()
    if not body:
        # We expect some body to be sent
        raise HTTPException(400, {
            'msg': 'Empty messages cannot be handled'
        })

    if hal_system is not None:
        # Execute the function
        try:
            result = hal_system.handler.update_can_state(
                system,
                body
            )
        except Exception as err:
            print(f'\n\n &&& HAL &&&&&&&&&& \n can_event ERROR: {err}')
            print(f'\n can_event ERROR hal_system was: {hal_system}')
            print(f'\n can_event ERROR system was: {system}')
            print(f'\n can_event ERROR body was: {body} \n\n\n')
            raise HTTPException(
                400,
                {
                    'msg': f'CAN message: {system} cannot be decoded',
                    'body': body
                }
            )

        can_handler = 'HAL_SYS'

        duration = (time.time() - start_time) * 1000
        print(f'[CAN][PROFILING][HAL_SYS] {instance_key} called {hal_system} with msg {system} in {duration:.3f} ms')
    elif system in hal.can_mapping:
        # Run against the HW layer for the given system as per CAN message
        handler = hal.can_mapping[system].handler
        # TODO: Test queue performance and error handling (by sending a fake
        # message and breaking code in the update can state)

        # request.app.hal_updater.api_queue.append(
        #     {
        #         'func': handler.update_can_state,
        #         'args': (system, body)
        #     }
        # )
        try:
            result = handler.update_can_state(
                system,
                body
            )
        except Exception as err:
            prefix_log(wgo_logger, __name__, f'Can event {system} error {err} {handler} MSG {body}')
            print(f'Can event system {system} error {err} {hal.can_mapping[system]}')
            print('MSG', body)

            raise HTTPException(
                400,
                {
                    'msg': f'CAN message: {system} cannot be decoded',
                    'body': body
                }
            )

        can_handler = 'CAN_MAP'

    duration = (time.time() - start_time) * 1000
    print(f'[CAN][PROFILING][{can_handler}] {instance_key} called {handler} with msg {system} in {duration:.3f} ms')

    if result is None:
        raise HTTPException(500, {'msg': 'CAN HAL did not succeed in providing a result'})

    return {'result': result}


@router.get('/states')
async def can_state(request: Request):
    return request.app.can_states


@router.get('/counters')
async def get_can_counter(request: Request):
    return request.app.can_counter


@router.put('/raw_message/{arb_id}')
async def send_raw_can(request: Request, arb_id: str, msg: dict):
    print(arb_id, msg['data'])
    data = msg.get('data')
    if data is None:
        raise ValueError()

    cmd = f'cansend canb0s0 {arb_id}#{data}'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    print(result)

    return {'msg': f'Result: {result}'}


@router.get('/history/sent')
async def get_sent_can_history(request: Request):
    return request.app.can_send_runner.handler.get_can_history()


@router.put('/stale')
async def put_stale_report(request: Request, report: dict):
    request.app.can_diagnostics['raw'] = report
    stale_count = 0
    devices_updated = {}
    for source, device in report.items():
        device['source'] = source
        device['sourceHex'] = hex(int(source))
        stale = device.get('stale')
        if stale is None:
            # Have not seen this device yet
            print(source, device, 'Not one bus yet')
            stale_count += 1
        elif stale is True:
            print(source, 'is stale', device)
            stale_count += 1
        else:
            # Device good
            pass

        devices_updated[device.get('name')] = device

    if stale_count == 0:
        status = 'OK'
    elif stale_count == 1:
        status = 'WARNING'
    else:
        status = 'ERROR'

    request.app.can_diagnostics['last_ran'] = time.time()
    request.app.can_diagnostics['status'] = status
    request.app.can_diagnostics['stale_count'] = stale_count
    request.app.can_diagnostics['devices'] = devices_updated

    return {'msg': 'OK'}


@router.get('diagnostics')
async def get_can_diagnostics(request: Request):
    '''Return full diagnostics object.'''
    response = {
        'system': request.app.system_diagnostics,
        'can': request.app.can_diagnostics
    }

    return response
