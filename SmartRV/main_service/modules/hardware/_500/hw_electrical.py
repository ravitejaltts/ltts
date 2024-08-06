import logging
import time

from common_libs.models.common import EventValues, RVEvents
from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.hardware.czone.control_rv_1 import CZone
from main_service.modules.logger import prefix_log

wgo_logger = logging.getLogger('main_service')

init_script = {
    # Should a real script go here for init
}

shutdown_script = {}

# A downstream impact is somethign that will impact other circuits or features
# as this is very specific to the
# electrical architecture, this lives here for now, including the copy it
# needs, but the copy shall soon be drawn from a central file anyway for
# language and copy

DOWNSTREAM_IMPACT = {
    # 0x15: {
    #     0: {
    #         'msg': 'AC systems unavailable',
    #         'level': 1
    #     }
    # }
}

CZONE_RV1 = 'RV1'
CZONE_SI = 'SI'
CZONE_SCI = 'SCI'
CZONE_KEYPAD = 'KEYPAD'

CZONE_DIPSWITCHES = {
    0x80: CZONE_RV1,
    0x40: CZONE_SI,
    0x20: CZONE_KEYPAD,
    0x10: CZONE_SCI
}


class DataHelper(object):
    def __init__(self):
        pass


class ElectricalSystems(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        self.HEARTBEAT_INGORE_LIMIT = 1
        self.HEARTBEAT_COUNT = 0
        self.keypad_controls = config.get("KEYPAD_CONTROLS")
        self.si_controls = config.get("SI_CONTROLS")
        self.rv1_controls = config.get("RV1_CONTROLS")
        self.toggle_zones = config.get("TOGGLE_ZONES")

        # TODO: Create a common set / get state for this in HALBaseClass
        self.savedState = {}
        self.HAL = None
        # was a mapping 'global' now it is config in the ElectricalSystems class object
        # Convert logical czone mapping to output mapping and add as 'outputs
        self.cfgMapping = config
        outputs = {}
        for key, value in self.cfgMapping['dc'].items():
            outputs[value.get('rvOutputId')] = key
            instance_key = str(value.get('bank')) + '-' + str(value.get('output_id'))
            if 'None' in instance_key:
                print('No proper instance key found for ', key, value)
            else:
                outputs[instance_key] = key

        self.cfgMapping['outputs'] = outputs

        # Initialize lighting controllers used in the 800
        self.czone = CZone(
            cfg={
                'mapping': self.cfgMapping
            },
            load_from='hw_electrical'
        )
        self.czone_source_addresses = {}
        self.czone_devices = {}

    def setHAL(self, hal_obj):
        print('Setting HAL in electrical')
        super().setHAL(hal_obj)
        self.czone.set_hal(hal_obj)

    def perform_hal_lighting_action(self, hal, switch_id, params, controls):
        switch_action = controls.get(switch_id, controls.get(str(switch_id)))
        if switch_action is None:
            prefix_log(wgo_logger, __name__, f'No HAL switch action defined for id: {switch_id}')
            return

        zone_id = switch_action.get('zone_id')
        # zone = self.HAL.lighting.handler.lighting_zone[zone_id]

        if str(zone_id) in self.toggle_zones:
            prefix_log(wgo_logger, __name__, f'{switch_id} is a toggle zone')
            hal.lighting.handler.toggle_zone_switch(
                zone_id,
                params.get('onOff')
            )
        else:
            # TODO: Allow for zone toggle as well to make latching switch both ways
            prefix_log(wgo_logger, __name__, f'{switch_id} is not a toggle zone')
            hal.lighting.handler.zone_switch(
                zone_id,
                params.get('onOff')
            )

    def dc_switch(self, dc_id: int, on_off: int, output: int, direction: str = None):
        '''Switch DC System on/off, if output provided set output level.
        CZone uses PWM value'''
        if on_off not in [EventValues.OFF, EventValues.ON]:
            raise ValueError('[ELECTRICAL][DC] DC SWITCHING onoff can only be 0 or 1')

        # TODO: Feature likely not needed, 'dangerous' to turn all circuits off
        if dc_id == 0:
            raise ValueError('Setting all circuits at once currently disabled')
            # for k, v in self.cfgMapping.get('dc').items():
            #     result = self.czone.circuit_control(
            #         k,
            #         on_off,
            #         output,
            #         inverted=v.get('inverted', False)
            #     )
            #     self.set_state(dc_id, {'onOff', on_off})
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

            if direction == 'BACKWARD':
                on_off = 1
                output = 100

            result = self.czone.circuit_control(
                circuit.get('id'),
                on_off,
                output,
                inverted=circuit.get('inverted', False),
                direction=direction
            )

            self.set_state(
                'dc',
                dc_id,
                {
                    'onOff': result.get('onOff', on_off),
                    'output': result.get('output', output),
                    'direction': direction
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

    def get_switch_state(self, switch_id, switch_bank=4):
        return self.get_state(
            'switches',
            f'bank_{switch_bank}_{switch_id}'
        )

    def set_switch_state(self, switch_id, switch_state, switch_bank=4):
        prefix_log(wgo_logger, f'{__name__}.HW__CAN_SWITCH_HELPER', f'Received switch state for {switch_bank}, {switch_id} with state: {switch_state}')
        if isinstance(switch_state, type({})):
            switch_state = switch_state.get('onOff')

        if self.get_switch_state(switch_id, switch_bank=switch_bank).get('onOff') != switch_state:
            switch_state = {
                'onOff': switch_state,
                'last_modified': time.time()
            }
            self.set_state(
                'switches',
                f'bank_{switch_bank}_{switch_id}',
                switch_state
            )

            prefix_log(wgo_logger, f'{__name__}.HW__CAN_SWITCH_HELPER', f'Updated switch state for {switch_bank}, {switch_id} with state: {switch_state}')

        return self.get_switch_state(switch_id, switch_bank=switch_bank)

    def circuit_check(self):
        '''Check if circuits changed state that should not.
        Happens when a CZone circuit turns off due to a fuse.'''
        # Check list of circuits and expected state
        # TODO: Figure out if this needs to go to a different layer, as it should likely be handled
        # by logic above the circuit, rather in e.g. Refrigerator is off although it should be on
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

    def can_switch_helper(self, index, can_msg, controls_schema):
        '''Check if switch needs to be performed.'''
        switch_bank = int(can_msg.get('Instance'))
        prefix_log(wgo_logger, f'{__name__}.HW__CAN_SWITCH_HELPER', f'Instance: {switch_bank} Checking {index} / {type(index)}')
        if '-' in index:
            template_bank, instance = index.split('-')
        else:
            template_bank = switch_bank
            instance = index

        instance = int(instance)
        template_bank = int(template_bank)

        # prefix_log(wgo_logger, f'{__name__}.HW__CAN_SWITCH_HELPER', f'instance {instance} / Bank: {template_bank}')

        if switch_bank != template_bank:
            # prefix_log(wgo_logger, f'{__name__}.HW__MAPPING', f'{switch_bank} does not match template bank {template_bank}')
            # This switch does not apply to this CAN message
            return

        # Get previous state of the switch in the given switch bank
        prev_sub_state = self.get_switch_state(
            instance,
            switch_bank=switch_bank
        )

        switch_state = int(can_msg.get(f'Output{instance}', -1))

        if switch_state is None:
            raise ValueError(f'[ELECTRICAL][ERROR] Cannot get switch state for circuit {index}')
        elif switch_state == -1:
            prefix_log(wgo_logger, f'{__name__}.HW__CAN_SWITCH_HELPER', f'Switch state not found')
            pass

        # print('[ERROR] PREV SUB STATE', prev_sub_state)
        if switch_state == prev_sub_state.get('onOff', None):
            # prefix_log(wgo_logger, f'{__name__}.HW__CAN_SWITCH_HELPER', f'Ignoring as no state change detected: {instance}')
            # return
            pass

        self.set_switch_state(
            instance,
            switch_state,
            switch_bank=switch_bank
        )

        # print('[ERROR] Controls Schema', controls_schema)
        # Check mapped input HAL action
        switch_action = controls_schema.get(str(index))
        if switch_action is None:
            raise IndexError(f'Cannot find an action for {index}')

        action = switch_action.get('action')
        # print('[ERROR] Action', action)

        if action == 'hal_action_component':
            # Perform component lookup in hal and run function in handler
            func = getattr(
                getattr(
                    self.HAL,
                    switch_action.get('category')
                ).handler,
                switch_action.get('function')
            )
            params = {
                'active': switch_state == 1
            }
            prefix_log(wgo_logger, f'{__name__}.HW__ACTION', f'Performing HAL ACTION COMPONENT: {index} {params}')
            # Execute function
            result = func(params)
            prefix_log(wgo_logger, f'{__name__}.HW__MAPPING', f'Function returned: {result}')

        elif action == 'hal_action':
            if switch_state != 1:
                # We only siwtch hal_actions on switch set to 1, but not 0
                return
            params = switch_action.get('params')

            prefix_log(wgo_logger, f'{__name__}.HW__ACTION', f'Performing HAL ACTION: {index} {params}')

            func = getattr(
                getattr(
                    self.HAL,
                    switch_action.get('category')
                ).handler,
                switch_action.get('function')
            )

            result = None
            try:
                if params is None:
                    result = func()
                else:
                    result = func(params)
            except Exception as err:
                print('HAL ACTION ERROR', func, err)

            prefix_log(wgo_logger, f'{__name__}.HW__MAPPING', f'Function returned: {result}')

        else:
            params = {
                'onOff': switch_state
            }
            prefix_log(wgo_logger, f'{__name__}.HW__ACTION', f'Performing HAL LIGHTING ACTION: {index} {params}')
            self.perform_hal_lighting_action(
                self.HAL,
                index,
                params,
                controls_schema
            )

    def switch_helper(self, switch_bank, switch_id, switch_action, switch_state):
        '''Perform the appropriate action.'''
        prev_sub_state = self.get_switch_state(
            switch_id,
            switch_bank=switch_bank
        )
        print('Previous/Current RvSwitch State', prev_sub_state, switch_state)

        if prev_sub_state is None or prev_sub_state == {}:
            # Set to current state
            prev_sub_state = self.set_switch_state(
                switch_id,
                {
                    'onOff': switch_state
                },
                switch_bank=switch_bank
            )

        if switch_state == prev_sub_state.get('onOff', None):
            # Ignore non state changes
            print('Did not change, still executing for now')

        self.set_switch_state(
            switch_id,
            switch_state,
            switch_bank=switch_bank
        )

        # Perform Action
        if switch_action.get('action') == 'hal_action_component':
            # Perform component lookup in hal and run function in handler
            try:
                func = getattr(
                    getattr(
                        self.HAL,
                        switch_action.get('category')
                    ).handler,
                    switch_action.get('function')
                )
            except AttributeError as err:
                print('Cannot find function', err, switch_action)
                return

            print('Function', func)
            params = {
                'active': switch_state == 1
            }
            parameter = switch_action.get('params')
            for p, val in parameter.items():
                if not p.startswith('$'):
                    # Static parameter
                    params[p] = val

            # Execute function
            print('Function return', func(params))

        else:
            print('Performing HAL lighting action for', switch_id)
            params = {
                'onOff': switch_state
            }
            self.perform_hal_lighting_action(
                self.HAL,
                switch_id,
                params,
                {
                    switch_id: switch_action
                }
            )

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''Receive Electrical related can messages and update state
        accordingly.'''
        # New way to identify the device is using the DIPswitch field for now (until we read this even better)
        dipswitch = int(can_msg.get('Dipswitch', 0x00))
        try:
            device = self.czone.decode_dipswitch(dipswitch)
        except KeyError as err:
            device = None
            print('KeyError', err)
            # Need to raise once properly implemented

        # If device is available use that to separate below, later we want to parse all the messages and compare a unique ID and map to an internal circuit
        # e.g. FF15 dipswitch 0x80 and instance 0x60 output 1 could be
        # 0xFF15806001    This is a big number, so might be able to condense this, but this would uniquely identify the specific output/input this relates to
        #   2 byte DGN 1 byte dipswitch 1 bytes instance and then the output between 1-32
        # Need to see more messages

        CXPLUS  = 54    # 0x36
        SCI     = 11    # 0x0B
        SI      = 13    # 0x0D
        KEYPAD  = 0x1D  # 29
        RV1     = 48    # 0x30
        RV1_C13 = 0x80  # Not sure what the 80 means here, is it an indicator for one of the RV1 submodules ?

        # We need to reliably associate each of the OutputX values from the similarly structured CAN messages to a component and the related property to update
        # We only receive 0 / 1 on this, so this needs to map to e.g. EventValues.EXTENDING for the slideout cicruit for extending and OFF /Extended as per rules in the state
        # when seeing the circuit go back to 0

        updated = False
        state = None
        if msg_name == 'heartbeat':     # FF04
            heartbeat_start = time.time()
            source_address = can_msg.get('source_address')
            dipswitch = int(can_msg.get('Dipswitch'))
            instance = int(can_msg.get('Instance'))
            device_name = CZONE_DIPSWITCHES.get(dipswitch)
            print(
                '[ELECTRICAL][CZONE] Received Heartbeat from',
                device_name,
                source_address,
                dipswitch,
                instance
            )

            # Check if we know the source address already
            if source_address not in self.czone_source_addresses:
                # Add it for the specific device
                if device_name is None:
                    # Not a known / supported device
                    print(
                        '[ELECTRICAL][CZONE] Unidentified device dip-switch',
                        dipswitch
                    )

                self.czone_source_addresses[source_address] = device_name
                self.czone_devices[device_name] = {
                    'source_address': source_address,
                    'dipswitch': dipswitch,
                    'instance': instance
                }

            print(f'[PROFILING] Heartbeat so far: {time.time() - heartbeat_start} seconds')

            # TODO: Handle only changes from previous state
            # if instance == CXPLUS:
            #     # Parse source and status of each circuit
            #     for i in range(24):
            #         index = i+1
            #         try:
            #             circuit_state = int(can_msg.get(f'Output{index}'))
            #             # if czone light we need to check and set the light state
            #         except TypeError:
            #             prefix_log(wgo_logger, f'{__name__}.TESTING', f'Ignoring error of output circuits Output{index}')
            #             continue

            #         if circuit_state is None:
            #             raise ValueError(f'Cannot get circuit state for circuit {index}')

            #         mapped_output = self.cfgMapping['outputs'].get(index)
            #         state = self.set_state('dc', mapped_output, {'onOff': circuit_state})
            #         # print(f' CXPLUS State {state}')

            #         # if index == 22:
            #         #     prefix_log(wgo_logger, f'{__name__}.CIRCUITS_AVC_MAP', f'{self.cfgMapping["outputs"]}')
            #         #     prefix_log(wgo_logger, f'{__name__}.CIRCUITS_AVC_CIRCUIT_STATE', f'{i} - {circuit_state}')
            #         #     prefix_log(wgo_logger, f'{__name__}.CIRCUITS_AVC_OUTPUT', f'{mapped_output}')
            #         #     prefix_log(wgo_logger, f'{__name__}.CIRCUITS_AVC_STATE', f'{state}')

            #     updated = True
            #     self.circuit_check()
            if instance == KEYPAD:
                prefix_log(wgo_logger, f'{__name__}.HW__CZONE__SI', f'KEYPAD Detected: {can_msg}')
                for index in self.keypad_controls.keys():
                    sub_start = time.time()
                    self.can_switch_helper(
                        index,
                        can_msg=can_msg,
                        controls_schema=self.keypad_controls
                    )
                    print(f'[PROFILING] KEYPAD: Time taken for {index}: CAN SWITCH HELPER: {time.time() - sub_start}')

            elif instance == SI:
                prefix_log(wgo_logger, f'{__name__}.HW__CZONE__SI', f'SI Detected: {can_msg}')
                for index in self.si_controls.keys():
                    sub_start = time.time()
                    self.can_switch_helper(
                        index,
                        can_msg=can_msg,
                        controls_schema=self.si_controls
                    )
                    print(f'[PROFILING] SI: Time taken for {index}: CAN SWITCH HELPER: {time.time() - sub_start}')
            elif instance == RV1:
                # Heartbeat not used for RV1, but might use for source address
                # identification
                pass
            else:
                print('[CZONE] Received unknown Instance', instance)
                print(can_msg)

            print(f'[PROFILING] Heartbeat END: {time.time() - heartbeat_start} seconds')

            self.HEARTBEAT_COUNT += 1

        elif msg_name == 'rvswitch':    # FF1C
            dipswitch = int(can_msg['Dipswitch'])
            device = CZONE_DIPSWITCHES.get(dipswitch)

            print('FOUND rvswitch', device)
            # Get the bank
            # Check what the previous state was
            # If changed. emit the correct HAL action
            if device == CZONE_RV1:
                # RV 1 Dipswitch banks
                instance = int(can_msg.get('Instance'))
                for i in range(32):
                    index = i + 1
                    switch_key = f'{instance}-{index}'
                    if switch_key in self.rv1_controls:
                        switch = self.rv1_controls.get(switch_key)
                        print('Found', switch_key, switch)
                        state = can_msg.get(f'Output{index}')
                        if state is None:
                            # This happens for testing only to keep changes concise in set_state
                            # raise ValueError('Config Error on:', switch_key)
                            continue
                        else:
                            state = int(state)

                        print('Setting', switch_key, state)
                        try:
                            # Check previous state
                            print(
                                'SwitchHelper',
                                self.switch_helper(
                                    instance,
                                    index,
                                    self.rv1_controls.get(switch_key),
                                    state
                                )
                            )
                        except Exception as err:
                            print('Error setting switch', err)
                    else:
                        print('Not Found', switch_key)
            else:
                print('Unhandled device', device)

        elif msg_name == 'rvoutput':    # FF15
            dipswitch = int(can_msg['Dipswitch'])
            device = CZONE_DIPSWITCHES.get(dipswitch)
            # print('RVOUTPUT', can_msg)
            # Used by RV1 to provide updates to Circuits
            instance = int(can_msg.get('Instance'))
            # print('RV1 - Circuit Change')
            # Check DIP switch
            # Take instance * output number and try to find matching circuit and toggle accordingly
            for i in range(32):
                index = i + 1
                try:
                    circuit_state = int(can_msg.get(f'Output{index}'))
                except TypeError:
                    prefix_log(
                        wgo_logger,
                        f'{__name__}.TESTING',
                        'Ignoring error of output circuits'
                    )
                    continue

                output_id = index + instance
                # print('ELECTRICAL OUTPUT_ID', output_id, index, instance)
                # print(self.cfgMapping['outputs'])
                if output_id in self.cfgMapping['outputs']:
                    # #print('Found output_id', output_id, self.cfgMapping['outputs'][output_id])
                    output = self.cfgMapping['outputs'][output_id]
                    # print('OUTPUT', output)
                    circuit_mapped_output = self.cfgMapping['dc'].get(output)
                    self.set_state('dc', output, {'onOff': circuit_state})
                    print(
                        '[CAN][ELECTRICAL][RV1][STATE][RVOUTPUT]',
                        output,
                        circuit_mapped_output,
                        self.get_state('dc', output),
                        output_id,
                        circuit_state
                    )

                    if circuit_mapped_output.get('code') is not None:
                        # print('CODE FOUND', circuit_mapped_output.get('code'))
                        # Try to update the given property in state
                        hal_handle = getattr(
                            self.HAL, circuit_mapped_output.get('category')
                        )
                        # print('HAL: HANDLE', hal_handle, circuit_mapped_output.get('code'))
                        component_handle = self.CODE_TO_ATTR.get(
                            circuit_mapped_output.get('code')
                        )
                        # print('COMPONENT HANDLE', component_handle)
                        try:
                            component = getattr(
                                hal_handle.handler,
                                component_handle
                            )
                            # print('COMPONENT', component)
                            # print('Circuit state', circuit_state)
                            # Get the property if available
                            circuit_instance = circuit_mapped_output.get('instance')
                            property = circuit_mapped_output.get('property', 'onOff')
                            values = circuit_mapped_output.get('values', {})
                            # TODO: Put the conversion to int into init
                            values = {int(key): value for key, value in values.items()}
                            value = values.get(
                                circuit_state,
                                # We default to the circuit state as a value
                                circuit_state
                            )
                            print(
                                '[CAN][ELECTRICAL][RV1][STATE]',
                                output,
                                circuit_mapped_output,

                                component_handle,
                                component[circuit_instance].state,
                                property,
                                value
                            )
                            if output == "14":
                                print('[SKIPPING][WH] found water heater mystery toggle, WOW !!')
                            else:
                                setattr(
                                    component[circuit_instance].state,
                                    property,
                                    value
                                )
                            # component[instance].state.onOff = circuit_state
                        except Exception as err:
                            print(component)
                            print(circuit_mapped_output)
                            print('YYYYY' * 16, err)
                else:
                    pass
                    # print('OUTPUT not found')

        elif msg_name == 'dc_dimmer_command_2':
            # RV-C 1FEDBh
            instance = int(can_msg.get('Instance'))
            command = can_msg.get('Command')
            # print('Command received', command, 'Instance', instance)

            if command == 'ON - 100% direct':
                on_off = 1
                output = 100
            elif command == 'OFF':
                on_off = 0
                output = 0

            if instance <= 100:
                # Regular Circuits
                print(self.dc_switch(instance, on_off, output))

            elif instance > 100 and instance <= 150:
                # Lighting mapping 101 = 1, 102 = 2 etc.
                instance = instance - 100
                # print('Lighting Instance', instance)
                # if instance in TOGGLE_ZONES:
                #     self.HAL.lighting.handler.toggle_zone_switch(instance, on_off)
                # else:
                # Homekit / RV-Bridge buttons are not momentary
                self.HAL.lighting.handler.zone_switch(instance, on_off)

            elif instance == 200:
                smart = DataHelper()
                smart.onOff = on_off

                self.HAL.lighting.handler.smartToggle(smart)
            else:
                print('Instance not mapped', instance)

        # TODO: Rework for efficiency, if we know this alert already, do not ask
        # again. Need to parse the fast data we request so we can
        elif msg_name == 'czone_alerts':
            # Handle CZone alerts
            print('[CZONE][ALERT] CZone alert received', can_msg)
            item_address_a1 = int(can_msg.get('Alarming_Item_Address_A1'))
            item_address_a2 = int(can_msg.get('Alarming_Item_Address_A2'))

            alarm_id_b1 = int(can_msg.get('Alarming_Id_B1'))
            alarm_id_b2 = int(can_msg.get('Alarming_Id_B2'))

            sequence = 1
            dipswitch = 0x80

            alert_key = f'{item_address_a1}{item_address_a2}__{alarm_id_b1}{alarm_id_b2}'
            if alert_key not in self.czone.alerts:
                cmd = (
                    '2799'
                    f'{dipswitch:02X}'
                    f'{item_address_a2:02X}{item_address_a1:02X}'
                    f'{sequence:02X}'
                    f'{alarm_id_b1:02X}{alarm_id_b2:02X}'
                )
                print('[CZONE] Send Alarm String CMD', cmd)
                # Issue a string request
                self.HAL.app.can_sender.can_send_raw(
                    '1CFF1344',
                    cmd
                )
                # Add to list and augment later so we do not send this all the time
                self.czone.alerts[alert_key] = {}
            else:
                print('[CZONE] Ignoring known alert')

        elif msg_name == 'czone_fast_data':
            print('[CZONE] Fast Data Received', can_msg)

        return state


module_init = (
    ElectricalSystems,
    'electrical_mapping',
    'components'
)
# handler = ElectricalSystems(
#     # config=read_default_config_json_file('Default_Config.json').get('electrical_mapping')
#     config=read_default_config_json_file().get('electrical_mapping')
# )


if __name__ == '__main__':
    pass
