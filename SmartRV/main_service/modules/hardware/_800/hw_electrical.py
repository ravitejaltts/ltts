# What controls does the water system need
# Who is providing this control

from copy import deepcopy
import json
import subprocess
import time

import logging
wgo_logger = logging.getLogger('main_service')

try:
    from main_service.modules.hardware.czone.control_x_plus import CZone
except ModuleNotFoundError:
    from czone.control_x_plus import CZone

from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.logger import prefix_log, json_logger
#from main_service.modules.storage_helper import read_default_config_json_file

from  common_libs.models.common import (
    RVEvents,
    EventValues
)

import requests

# Read from 800 config
SWITCHCONTROLS = {
    1: {
        'zone_id': 1,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/1',
        'params': {'$onOff': 'int'}
    },
    3: {
        'zone_id': 2,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/2',
        'params': {'$onOff': 'int'}
    },
    5: {
        'zone_id': 3,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/3',
        'params': {'$onOff': 'int'}
    },
    8: {
        'zone_id': 4,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/4',
        'params': {'$onOff': 'int'}
    },
    7: {
        'zone_id': 5,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/5',
        'params': {'$onOff': 'int'}
    },
    9: {
        'zone_id': 5,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/5',
        'params': {'$onOff': 'int'}
    },
    11: {
        'zone_id': 6,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/6',
        'params': {'$onOff': 'int'}
    },
    15: {
        'zone_id': 10,
        'action': 'api_call',
        'type': 'PUT',
        'href': 'http://127.0.0.1:8000/api/lighting/zone/10',
        'params': {'$onOff': 'int'}
    }
}

CIRCUIT_OVERRIDES = {
    # Pro Power is a blip, always sends on
    13: {
        'onOff': 1
    }
}

TOGGLE_ZONES = [10,]

init_script = {
    # Should a real script go here for init
}

shutdown_script = {}

# A downstream impact is somethign that will impact other circuits or featuers, as this is very specific to the
# electrical architecture, this lives here for now, including the copy it needs, but the copy shall soon be drawn
# from a central file anyway for language and copy
DOWNSTREAM_IMPACT = {
    0x15: {
        0: {
            'msg': 'AC systems unavailable',
            'lvl': 1
        }
    }
}


AVC_INPUT = 'Output22'


def perform_switch_action(switch_id, params):
    '''Perform the given switch action.'''
    switch_action = SWITCHCONTROLS.get(switch_id)
    if switch_action is None:
        prefix_log(wgo_logger, __name__, f'No switch action defined for id: {switch_id}')
        return

    if switch_action.get('action') == 'api_call':
        call_type = switch_action.get('type')
        href = switch_action.get('href')
        if call_type == 'PUT':
            call_params = {}
            for p, v in switch_action.get('params').items():
                if p.startswith('$'):
                    # Dynamic read from params provided
                    key = p.replace('$', '')
                    call_params[key] = params.get(key)
                else:
                    call_params[p] = v
            try:
                start_time = time.time()
                requests.put(href, data=json.dumps(call_params), timeout=1)
            except requests.exceptions.ReadTimeout as err:
                prefix_log(wgo_logger, __name__, str(err))



def perform_hal_lighting_action(hal, switch_id, params):
    switch_action = SWITCHCONTROLS.get(switch_id)
    if switch_action is None:
        prefix_log(wgo_logger, __name__, f'No HAL switch action defined for id: {switch_id}')
        return

    zone_id = switch_action.get('zone_id')
    if zone_id is None:
        raise IndexError(f'No zone_id mapped to switch: {switch_id}')
    if zone_id in TOGGLE_ZONES:
        hal.lighting.handler.toggle_zone_switch(zone_id, params.get('onOff'))
    else:
        # TODO: Allow for zone toggle as well to make latching switch both ways
        hal.lighting.handler.zone_switch(zone_id, params.get('onOff'))


class ElectricalSystems(HALBaseClass):
    def __init__(self, config={}):
        HALBaseClass.__init__(self, config=config)
        self.HEARTBEAT_INGORE_LIMIT = 1
        self.HEARTBEAT_COUNT = 0

    # def setHAL(self, hal_obj):
    #     self.HAL = hal_obj

    # TODO: Create a common set / get state for this in HALBaseClass
        self.state = {}
        self.savedState = {}
        self.HAL = None
        # was a mapping 'global' now it is config in the ElectricalSystems class object
        # Convert logical czone mapping to output mapping and add as 'outputs
        self.cfgMapping = config
        outputs = {}
        for key, value in self.cfgMapping['dc'].items():
            outputs[value.get('output_id')] = key
        self.cfgMapping['outputs'] = outputs

        # Initialize lighting controllers used in the 800
        self.czone = CZone(
            cfg={
                'mapping': self.cfgMapping
            }
        )
        print(self.czone.cfg['mapping'])


    def setHAL(self, hal_obj):
        self.HAL = hal_obj


    def set_state(self, system, system_id, new_state):
        system_state = self.get_state(system=system)

        # updated_keys = []

        # # Check for changes in the zone state keys
        # for key, value in new_state.items():
        #     print('Key', key, 'value', value)
        #     if key in zone_state:
        #         if value != zone_state.get(key):
        #             print('Updated key', key, value)
        #             updated_keys.append(key)
        #             zone_state[key] = value
        #         else:
        #             print('Value unchanged for', key, value)
        #     else:
        #         zone_state[key] = value
        #         print('Added Key', key)
        #         updated_keys.append(key)

        # self.state[zone] = zone_state

        # print(self.state[zone], updated_keys)

        # return updated_keys
        system_key = f'{system}__{system_id}'
        self.state[system_key] = new_state

        return self.state[system_key]


    def get_state(self, system=None, system_id=None):
        '''Return state of corresponding system.'''
        if system is None:
            return self.state
        else:
            system_key = f'{system}__{system_id}'
            return self.state.get(system_key, {})


    def dc_switch(self, dc_id:int, on_off:int, output:int):
        '''Switch DC System on/off, if output provided set output level.
        CZone uses PWM value'''
        if dc_id == 0:
            for k, v in self.cfgMapping.get('dc').items():
                result = self.czone.circuit_control(
                    k,
                    on_off,
                    output,
                    inverted=v.get('inverted', False)
                )
                self.set_state(dc_id, {'onOff', on_off})
        else:
            circuit = self.cfgMapping.get('dc', {}).get(str(dc_id))
            print('DC Circuit', circuit)
            if circuit is None:
                raise ValueError(f'No mapping for dc switch "{dc_id}"')

            # Check if this has a static value, use that instead
            # TODO: Check if that is a real feature or should be avoided here
            # Problem is on the UI for Pro Power, it is only a blip, it shall always send onoff=1,
            # but the switch cannot be hardcoded on the UI side for now using fixed "params"
            static = circuit.get('static')
            if static:
                on_off = static.get('onOff')
                output = static.get('output')

            result = self.czone.circuit_control(
                circuit.get('id'),
                on_off,
                output,
                inverted=circuit.get('inverted', False)
            )

            self.set_state(
                'dc',
                dc_id,
                {
                    'onOff': result.get('onOff', on_off),
                    'output': result.get('output', output)
                }
            )

        downstream_effect = DOWNSTREAM_IMPACT.get(dc_id, {}).get(on_off)
        msg = None
        if downstream_effect is not None:
            msg = downstream_effect

        return {
            'onOff': on_off,
            'output': output,
            'msg': msg
        }


    def ac_switch(self, ac_id:int, on_off:int):
        '''Switch AC relay systems on/off .'''
        if ac_id == 0:
            for k, v in self.cfgMapping.items():
                result = self.czone.switch_bank_control(v, on_off)
                self.set_state(ac_id, {'onOff', on_off})
        else:
            circuit = self.cfgMapping['ac'].get(str(ac_id))
            if circuit is None:
                raise ValueError(f'No mapping for dc switch "{ac_id}"')

            result = self.czone.switch_bank_control(circuit, on_off)

            self.set_state('ac', ac_id, {'onOff': on_off})

        return {'onOff': on_off}


    def get_switch_state(self, switch_id, switch_bank=4):
        return self.get_state(
            'switches',
            f'bank_{switch_bank}_{switch_id}'
        )


    def set_switch_state(self, switch_id, switch_state, switch_bank=4):
        self.set_state(
            'switches',
            f'bank_{switch_bank}_{switch_id}',
            switch_state
        )

        return self.get_switch_state(switch_id, switch_bank=switch_bank)


    def circuit_check(self):
        '''Check if circuits changed state that should not.
        Happens when a CZone circuit turns off due to a fuse.'''
        # Check list of circuits and expected state
        # TODO: Figure out if this needs to go to a different layer, as it
        # should likely be handled by logic above the circuit, rather in e.g.
        # Refrigerator is off although it should be on

        fridge_state = self.state.get('dc_22')
        if fridge_state is not None:
            if fridge_state.get('onOff') == 0:
                # Fridge tripped ?
                self.event_logger.add_event(
                    RVEvents.REFRIGERATOR_BREAKER_TRIPPED,
                    1,
                    EventValues.TRUE
                )
        else:
            # Circuit not found in the list
            # TODO: Check why this happens
            pass

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''Receive Electrical related can messages and update state accordingly.
        {
            'Manufacturer_Code': 'BEP Marine',
            'Dipswitch': '1',
            'Instance': '54',
            'Output1': '1',
            'Output2': '1',
            'Output3': '0',
            'Output4': '0',
            'Output5': '0',
            'Output6': '0',
            'Output7': '0',
            'Output8': '0',
            'Output9': '0',
            'Output10': '0',
            'Output11': '0',
            'Output12': '0',
            'Output13': '0',
            'Output14': '0',
            'Output15': '0',
            'Output16': '0',
            'Output17': '0',
            'Output18': '0',
            'Output19': '0',
            'Output20': '0',
            'Output21': '0',
            'Output22': '0',
            'Output23': '0',
            'Output24': '0',
            'Byte8': '0',
            'msg': 'Timestamp: 1654641313.850771    ID: 1cff0401    X Rx                DL:  8    27 99 01 36 03 00 00 00     Channel: canb0s0',
            'msg_name': 'Heartbeat',
            'instance_key': '1CFF0401__0'
        }
        '''
        CXPLUS = 54
        SCI = 11
        SI = 13
        KEYPAD = 0x1D
        RV1 = 48

        state = None
        if msg_name == 'heartbeat':
            # Check instance
            # Assume it maps to the CZone HW type
            # 0x0B == SCI ?
            # 54 == CZoneXPlus ?

            instance = int(can_msg.get('Instance'))
            # TODO: Handle only changes from previous state
            if instance == CXPLUS:
                # Parse source and status of each circuit
                for i in range(24):
                    index = i+1
                    try:
                        circuit_state = int(can_msg.get(f'Output{index}'))
                        # if czone light we need to check and set the light state
                    except TypeError as e:
                        prefix_log(wgo_logger, f'{__name__}.TESTING', f'Ignoring error of output circuits: {e}')
                        continue

                    if circuit_state is None:
                        raise ValueError(f'Cannot get circuit state for circuit {index}')

                    mapped_output = self.cfgMapping['outputs'].get(index)
                    state = self.set_state('dc', mapped_output, {'onOff': circuit_state})

                self.circuit_check()
            elif instance == SCI:
                    print('Received Instance ->', instance)
                    # We need to ignore the first message that the system gets (after reboot to allow for initialization)

                    # TODO: Optimize to check only for changes
                    # Map switch to action
                    for i in range(16):
                        index = i+1

                        switch_bank = can_msg.get("Dipswitch")
                        prev_sub_state = self.get_switch_state(index, switch_bank=switch_bank)

                        switch_state = int(can_msg.get(f'Output{index}'))
                        if switch_state is None:
                            raise ValueError(f'Cannot get switch state for circuit {index}')

                        if switch_state == prev_sub_state.get('onOff', None):
                            # Ignore non state changes
                            continue

                        # Get state
                        # Check if updated
                        # Set state
                        new_state = {
                            'onOff': switch_state,
                            'last_modified': time.time()
                        }
                        # print(new_state)
                        self.set_switch_state(index, new_state, switch_bank=switch_bank)
                        # TODO: HERE !!!!!
                        if self.HEARTBEAT_COUNT >= self.HEARTBEAT_INGORE_LIMIT:
                            perform_hal_lighting_action(self.HAL, index, new_state)
                        else:
                            pass
                            #prefix_log(wgo_logger, '[HW_CUSTOM_PROCEDURES]', f'Ignored CZONE Heartbeats from SCI: {self.HEARTBEAT_COUNT}')

                        # if index == 1:
                        #     self.HAL.lighting.handler.zone_switch(index, switch_state)
                        # else:
                        #     print(
                        #         perform_switch_action(index, new_state)
                        #     )

                    updated = True
                    state = self.get_state('switches', can_msg)
            elif instance == KEYPAD:
                # 500 Series Keypad
                print('KEYPAD', )
                print(can_msg)
            elif instance == SI:
                # 1: Output 2
                # 2: Output 4
                # 3: Output 6
                # 4: Output 8
                # 5: Output 10
                # 6: Output 12  # Service light is latching
                print('SI (Signal Interface)')
                print(can_msg)
            elif instance == RV1:
                print('RV1 detected')
                print(can_msg)
            else:
                print('Received unknown Instance ->', instance)
                print(can_msg)

            self.HEARTBEAT_COUNT += 1
        elif msg_name == 'rvswitch':
            instance = int(can_msg.get('Instance'))

            print('RV-1 SWITCH', instance)
            print(can_msg)
        elif msg_name == 'dc_dimmer_command_2':
            # RV-C 1FEDBh
            instance = int(can_msg.get('Instance'))
            command = can_msg.get('Command')
            print('Command received', command, 'Instance', instance)

            if command == 'ON - 100% direct':
                on_off = 1
                output = 100
            elif command == EventValues.OFF:
                on_off = 0
                output = 0

            if instance <= 100:
                # Regular Circuits
                print(self.dc_switch(instance, on_off, output))

            elif instance > 100 and instance <= 150:
                # Lighting mapping 101 = 1, 102 = 2 etc.
                instance = instance - 100
                print('Lighting Instance', instance)
                if instance in TOGGLE_ZONES:
                    self.HAL.lighting.handler.toggle_zone_switch(instance, on_off)
                else:
                    self.HAL.lighting.handler.zone_switch(instance, on_off)

        return state


#handler = ElectricalSystems(config=read_default_config_json_file().get('electrical_mapping'))
module_init = (
    ElectricalSystems,
    'electrical_mapping',
    'components'
)
if __name__ == '__main__':
    print(handler)
