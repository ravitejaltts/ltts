'''Module for CZone controls.'''

import subprocess
import time

# TODO: Provide HMI / Main handler to issue CAN commands
# TODO: Common interface for can inputs for CAN enabled devices

SWITCH_BANK = bin(0xffffffffffffff)


class CZone(object):
    def __init__(self, cfg={}):
        self.cfg = cfg
        self.state = {
            i: {'onOff': 0, 'power': 0} for i in range(1, 29)
        }

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


    def circuit_control(self, circuit_id, on_off, output, inverted=False):
        '''Proprietary circuit control for CZone.'''
        # TODO: Add power logic to CZone code, remove from high level 'electrical'
        # Check if inverted circuit
        if inverted is True:
            result_on_off = 0 if on_off == 1 else 1
        else:
            result_on_off = on_off

        if result_on_off == 0:
            # Overwrite output to 0
            output = 0

        cmd = f'cansend canb0s0 1CFF0044#2799{circuit_id:02X}00{output:02X}FF7C0F'
        print(f'######################  Command {cmd}')

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
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
            cmd = 'cansend canb0s0 19F20E44#00{:02X}'.format(self.bank_to_bits(switch_id, 1))

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True
            )
            time.sleep(0.125)
            # Flip bit for quicker action
            cmd = 'cansend canb0s0 19F20E44#00{:02X}'.format(self.bank_to_bits(switch_id, 0))

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True
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
