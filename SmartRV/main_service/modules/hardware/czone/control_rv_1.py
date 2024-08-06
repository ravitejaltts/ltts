'''Module for CZone controls.'''

import subprocess
import time

# TODO: Provide HMI / Main handler to issue CAN commands
# TODO: Common interface for can inputs for CAN enabled devices

SWITCH_BANK = bin(0xffffffffffffff)


RV1 = 16
SI = 8
KEYPAD_6 = 4
CONTROL_X_PLUS = 2
SCI = 1

DEVICE_TYPES = {
    RV1: {
        'id': RV1,
        'short': 'RV1',
        'name': 'CZone RV1'
    },
    SI: {
        'id': SI,
        'short': 'SI',
        'name': 'CZone Signal Interface',
    },
    KEYPAD_6: {
        'id': KEYPAD_6,
        'short': 'KEY_6',
        'name': 'CZone 6-Way Keypad'
    },
    CONTROL_X_PLUS: {
        'id': CONTROL_X_PLUS,
        'short': 'CX+',
        'name': 'CZone Control X Plus'
    },
    SCI: {
        'id': SCI,
        'short': 'SCI',
        'name': 'CZone Switch Control Interface'
    }
}


class CZone(object):
    def __init__(self, cfg=None, load_from='NA'):
        print('[CZONE][INIT][Initializing RV1 Class]', cfg, load_from)
        if cfg is None:
            cfg = {}

        self.cfg = cfg
        self.HAL = None
        self.state = {
            i: {'onOff': 0, 'power': 0} for i in range(1, 29)
        }
        self.SOURCE_ADDRESS = 0x44
        self.alerts = {}

    def set_hal(self, hal_obj):
        if hal_obj is None:
            print('[HAL][CZONE][INIT]', 'Ignoring setting to None')
            return
        print('[HAL][CZONE][INIT] Setting HAL for CZONE RV1 handler', hal_obj)
        self.HAL = hal_obj
        print('[HAL][CZONE][INIT] Setting HAL for CZONE RV1 handler', dir(self.HAL))

    def decode_dipswitch(self, dip_value: int):
        '''Take a diswitch value and decode according to WGO mapping for dipswitches.'''
        instance = dip_value & 0b00000111
        device = dip_value >> 3
        device_type = DEVICE_TYPES.get(device)
        if device_type is None:
            raise KeyError(f'Unknown or misconfigured device: {device}/{instance}')

        return device_type, instance

    def bank_to_bits(self, bank_id, on_off):
        '''Convert an id to the bit needed to set in NMEA2K'''
        i = bank_id
        if on_off == 1:
            fill = '01'
        elif on_off == 0:
            fill = '00'
        else:
            fill = '11'

        bits = '0b' + SWITCH_BANK[2:i*2+2] + fill + SWITCH_BANK[i*2+4:]
        return int(bits, 2)

    def circuit_control(self, circuit_id, on_off, output, inverted=False, direction='FORWARD'):
        '''Proprietary circuit control for CZone.'''
        # TODO: Add power logic to CZone code, remove from high level 'electrical'
        # Check if inverted circuit
        if inverted is True or inverted == 1:
            result_on_off = 0 if on_off == 1 else 1
            # print(f'Circuit is inverted {circuit_id}')
        else:
            result_on_off = on_off

        if result_on_off == 0:
            # Overwrite output to 0
            output = 0

        # We use this to decide if the circuit has a specific type
        circuit = self.cfg.get('mapping', {}).get('dc', {}).get(str(circuit_id), {})
        # print('Mappings', self.cfg.get('mapping'))
        # print(f'Selected CZone Circuit: {circuit_id} {circuit}')
        circuit_type = circuit.get('circuitType', 'DEFAULT')

        if circuit_type == 'DEFAULT':
            cmd = f'2799{circuit_id:02X}00{output:02X}FF7C0F'

        elif circuit_type == 'H-BRIDGE':
            if on_off == 1:
                # Forward 0xF1
                # Backwards 0xF4
                # control = 0xF1
                if direction is None or direction == 'FORWARD':
                    control = 0x84
                elif direction == 'BACKWARD':
                    control = 0x74
                else:
                    raise ValueError(f'Unknown direction: {direction}')
            else:
                # Turn off
                control = 0x00

            # Using the same message as regular circuit
            # TOOD: Check
            cmd = f'2799{circuit_id:02X}00{control:02X}FF7C0F'
            # cmd = f'cansend canb0s0 1CFF00{self.SOURCE_ADDRESS}#2799{circuit_id:02X}000008{control:02X}00'
        else:
            raise ValueError(f'Unsupported circuit type: {circuit_type}')

        # # Check what type of circuit we use
        # if circuit_id in range (1, 11 ): # or circuit_id in [18,20]:
        #     if circuit_id == 4:
        #         # special case Murphy bed Reverse
        #         if on_off == 1:
        #             output = 0xf4
        #         else:
        #             output = 0x42
        #         cmd = f'cansend canb0s0 1CFF00{self.SOURCE_ADDRESS}#27990D000008{output:02X}00'
        #     else:
        #         output = 0xf2 - on_off
        #         cmd = f'cansend canb0s0 1CFF00{self.SOURCE_ADDRESS}#2799{circuit_id:02X}000008{output:02X}00'
        # else:

        print(f'######################  Command {cmd}')
        print('[CZONE][INIT]', dir(self))
        print('[CZONE][INIT]', self.HAL)
        self.HAL.app.can_sender.can_send_raw(
            f'1CFF00{self.SOURCE_ADDRESS:02X}',
            cmd
        )

        # Set circuit state
        self.state[circuit_id] = {
            'onOff': result_on_off,
            'power': output
        }

        return {
            'onOff': on_off,
            'output': output
        }

    def switch_bank_control(self, switch_id, on_off):
        '''Control NMEA2K switchbank.
        Currently works by toggling a switch, makes maintaining state more important.
        Might be overwritten by state received from Bank broadcast'''
        # Check if on or off
        # If off and off is desired, do nothing, same for on/on
        # If on and off toggle, same for off and it is on
        current_state = self.state.get(switch_id)
        changed = True
        if current_state == on_off:
            changed = False
        else:
            cmd = '00{:02X}'.format(self.bank_to_bits(switch_id, 1))

            self.HAL.app.can_sender.can_send_raw(
                f'19F20E{self.SOURCE_ADDRESS:02X}',
                cmd
            )
            time.sleep(0.125)
            # Flip bit for quicker action
            cmd = '00{:02X}'.format(self.bank_to_bits(switch_id, 0))

            self.HAL.app.can_sender.can_send_raw(
                f'19F20E{self.SOURCE_ADDRESS:02X}',
                cmd
            )

        self.state[switch_id] = on_off

        # Return status
        return {
            'onOff': on_off,
            'changed': changed
        }

    def switch_input_trigger(self, switch_id, state):
        '''React to a momentary switch'''
        pass

    def alarm_received(self, level, body):
        '''Receive and handle CZone alarm'''
        pass

    def configure(self, cfg):
        '''Configre CZone module.'''
        pass

    def handle_can_input(self, can_msg):
        '''Handle CAN messages.'''
        pass


if __name__ == '__main__':
    handler = CZone()
    print(handler.state)

    print('{:02X}'.format(handler.bank_to_bits(10, 1)))
    print(handler.switch_bank_control(10, 0))
    print(handler.switch_bank_control(10, 1))
    print(handler.switch_bank_control(10, 1))
    print(handler.switch_bank_control(10, 0))
    print(handler.switch_bank_control(10, 0))
    # print(handler.switch_bank_control(10, 0))
    # assert handler.switch_bank_control(10, 0).get('changed') is False
    # assert handler.switch_bank_control(10, 0).get('changed') is False
    # print(handler.switch_bank_control(10, 1))
    # print(handler.switch_bank_control(10, 1))
