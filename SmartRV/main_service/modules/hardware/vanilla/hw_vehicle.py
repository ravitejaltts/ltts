# What controls does the water system need
# Who is providing this control

from copy import deepcopy
from multiprocessing.sharedctypes import Value
import subprocess
import time
import struct

import requests

from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.logger import prefix_log
from main_service.modules.data_helper import byte_flip
from common_libs import environment

import logging

wgo_logger = logging.getLogger('main_service')
_env = environment()

from  common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

# Intermotive chassis interface
vehicle_interface = None


INIT_SCRIPT = {
    # # Should a real script go here for init
    # 'vin': [
    #     # Set to 1300 watts charge level
    #     'cansend canb0s0 18EF4644#5501024692040000',
    # ]
}

shutdown_script = {}


# TODO: Modify this to read from file on start
CONFIG_DEFAULTS = {
    'propulsion_battery__1__soc': None,
    'park_brake_status': None,
    'current_odo_reading': None,
    'vin_buffer': {},
    'vin': None,
    'key_position': None
}

METER_TO_MILES = 0.0006213712

CHASSIS_ID = 1

ODO_THRESHOLD = 1

PRO_POWER_ID = 2

# Required for string matching dbc values for invalid data
DATA_INVALID = 'Data Invalid'

def write_vin(vin):
    try:
        with open(_env.vin_file_path(), 'w') as vin_file:
            vin_file.write(vin)
    except FileNotFoundError as err:
        # On dev with path not available ?
        with open('./vin.txt', 'w') as vin_file:
            vin_file.write(vin)


class VehicleInterface(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        # Given by base class
        # .state / .savedState / .config
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        for key, value in config.items():
            self.state[key] = value

        self.state['vin_buffer'] = {}

    # TODO: Create a single shared can sending method on the HW layer maybe ?
    def get_vin(self):
        '''This will request the VIN from the vehicle.
        This is an async call, the assembly of the VIN happens in update_can_state'''
        print('Reqeuesting VIN')
        # Read from file if present
        vin = ''
        try:
            with open(_env.vin_file_path(), 'r') as vin_file:
                vin = vin_file.read().strip()
        except FileNotFoundError as err:
            # On dev with path not available ?
            try:
                with open('./vin.txt', 'r') as vin_file:
                    vin = vin_file.read().strip()
            except FileNotFoundError as err:
                pass

        self.HAL.app.config['VIN'] = vin
        self.state['vin'] = vin

        # Request VIN and handle if different upon receipt
        self.HAL.app.can_sender.can_send_raw(
            '18EA0044',
            'ECFE00'
        )

        return vin

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''Receive updates to energy modules.

        BMS
        AVC2 / VSIM inputs'''
        state = None

        prefix_log(wgo_logger, __name__, f'CAN Msg Name: {msg_name}', lvl='debug')
        prefix_log(wgo_logger, __name__, f'CAN Msg : {can_msg}', lvl='debug')

        if msg_name == 'state_of_charge':
            # FCC2
            # {
            #     "Charge_Percent": "82.80000000000001",
            #     "name": "STATE_OF_CHARGE"
            # }
            if can_msg.get('Charge_Percent') == DATA_INVALID:
                soc_value = None
            else:
                try:
                    soc_value = float(can_msg['Charge_Percent'])
                    soc_value = round(soc_value, 1)
                except ValueError as err:
                    soc_value = None

            self.state['propulsion_battery__1__soc'] = soc_value

            # TODO: Reintroduce SoC when clear why this fails
            self.event_logger.add_event(
                RVEvents.CHASSIS_SOC_CHANGE,
                CHASSIS_ID,
                soc_value
            )
        elif msg_name == 'aat_ambient_air_temperature':
            # {
            #     "name": "AAT_AMBIENT_AIR_TEMPERATURE",
            #     "Temperature": "16"
            # }
            # Update climate instance
            outside_instance = 6
            new_temp_celcius = can_msg.get('Temperature')
            if new_temp_celcius is None:
                raise ValueError('Temperature reading None')

            if new_temp_celcius == 'Data Invalid':
                exterior_temp = None
            else:
                try:
                    exterior_temp = round(float(new_temp_celcius), 1)
                except ValueError as err:
                    # TODO: Check if this error happens with the check for 'Data Invalid'
                    exterior_temp = None

            self.HAL.climate.handler.state[f'currenttemp__{outside_instance}'] = exterior_temp

            self.event_logger.add_event(
                RVEvents.CHASSIS_OUTSIDE_TEMPERATURE_CHANGE,
                CHASSIS_ID,  # just one instance of outside temperature to report to the platform
                exterior_temp
            )
        elif msg_name == 'pg_park_brake':
            # {
            #     'name': 'PB_PARK_BRAKE',
            #     'Park_Break_Status': 'applied'
            # }
            park_brake_status = can_msg.get('Park_Brake_Status')
            value = EventValues.PARK_BRAKE_APPLIED if park_brake_status == 'applied' else EventValues.PARK_BRAKE_RELEASED
            self.state[f'park_brake_status'] = can_msg.get('Park_Brake_Status')
            print(f'Park_Brake_Status {value}')
            self.event_logger.add_event(
                RVEvents.CHASSIS_PARK_BRAKE_CHANGE,
                CHASSIS_ID,
                value
            )
        elif msg_name == 'vehicle_status_2':
            # {
            #     'name': 'VEHICLE_STATUS_2',
            #     'On': 1
            # }
            ignition_switch_status = can_msg.get("Key_Position")
            value = EventValues.ON if ignition_switch_status == 'Run' else EventValues.OFF
            self.state[f'key_position'] = can_msg.get('Key_Position')
            print(f'Ignition Key {value}')
            self.event_logger.add_event(
                RVEvents.CHASSIS_IGNITION_STATUS_CHANGE,
                CHASSIS_ID,
                value
            )
        elif msg_name == 'vehicle_status_1':
            # Get Pro Power and other data
            wgo_logger.debug(str(can_msg))
            pro_power_state = can_msg.get('Pro_Power_Status')
            wgo_logger.debug(f'Pro Power State: {pro_power_state} {type(pro_power_state)}')
            PRO_POWER_CIRCUIT = 13
            if pro_power_state == 'Front & Rear On':
                self.HAL.energy.handler.state['pro_power__1__enabled'] = 1
            elif pro_power_state == 'Data Invalid':
                # TODO: Add lockout to Pro Power control if vehicle is off
                self.HAL.energy.handler.state['pro_power__1__enabled'] = None
            else:
                self.HAL.energy.handler.state['pro_power__1__enabled'] = 0

            self.HAL.electrical.handler.state[f'dc__{PRO_POWER_CIRCUIT}'] = {
                'onOff': self.HAL.energy.handler.state.get('pro_power__1__enabled')
            }

            self.event_logger.add_event(
                RVEvents.CHASSIS_PRO_POWER_STATUS_CHANGE,
                CHASSIS_ID,
                self.HAL.energy.handler.state.get('pro_power__1__enabled', 0)
            )

        elif msg_name == 'vin_response':
            # Check the VIN fragments
            vin_fragment = []
            for i in range(7):
                index = i + 1
                try:
                    char_int = int(can_msg.get(f'Hex_Ascii_{index}'))
                except ValueError as err:
                    # Happens as 255 is decoded as data invalid
                    # TODO: Update DBC file to not consider this invalid, if the resulting VIN is all FF, it will be empty and can
                    # be considered invalid then
                    continue

                # This might not happen due to above, but once DBC is fixed it will ignore FF
                if char_int == 255:
                    continue

                vin_fragment.append(chr(char_int))

            list_num = can_msg.get('Vin_List_Num')
            vin_fragment = "".join(vin_fragment)
            print('[VIN] Adding VIN fragement', list_num, vin_fragment)
            self.state['vin_buffer'][list_num] = vin_fragment

            # Check complete
            is_complete = True
            for indx in ('1', '2', '3'):
                if not indx in self.state['vin_buffer']:
                    is_complete = False

            if is_complete is True:
                vin = self.state['vin_buffer']['1'] + self.state['vin_buffer']['2'] + self.state['vin_buffer']['3']
                self.state['vin'] = vin

                print('[VIN] Result:', vin)
                self.HAL.app.config['VIN'] = vin

                # Read the vin from the file

                try:
                    with open(_env.vin_file_path(), 'r') as vin_file:
                        stored_vin = vin_file.read()
                except FileNotFoundError as err:
                    stored_vin = None

                if stored_vin is None:
                    write_vin(vin)
                elif stored_vin != vin:
                    # Mismatch
                    write_vin(vin)
                else:
                    # Do nothing
                    pass
                # Maybe it didn't change but we need more vin reporting and this will keep it in the twin data
                self.event_logger.add_event(
                    RVEvents.CHASSIS_VIN_CHANGE,
                    CHASSIS_ID,
                    vin
                )
                try:
                    self.vehicle[1].state.vin = vin
                    self.vehicle[1].update_state()  # emit event
                except Exception as err:
                    print(f"Unable to set component vin: {err}")

                self.state['vin_complete'] = True

        elif msg_name == 'odo_odometer':
            latest_odo_reading = can_msg.get('Distance_Traveled')
            if latest_odo_reading == DATA_INVALID:
                latest_odo_reading = None
            if latest_odo_reading is not None:
                # Distance is in meters
                odo_in_miles = int(latest_odo_reading) * METER_TO_MILES
                # Currently rounding to the next full digit, every mile will report
                odo_in_miles = round(odo_in_miles, 0)
                if odo_in_miles != self.state.get('current_odo_reading'):
                    # TODO: Add thottling and rounding ? We do not want to write every increase
                    self.state['current_odo_reading'] = odo_in_miles
                    self.event_logger.add_event(
                        RVEvents.CHASSIS_ODOMETER_READING_CHANGE,
                        CHASSIS_ID,
                        odo_in_miles
                    )

        # TODO: Feature to light up, need to refine and emit an event that can be
        # handled centrally
        # elif msg_name == 'tr_transmission_range':
        #     # Emit event if transmission range changes to reverse or drive
        #     current_tr_mode = can_msg.get('Transmission_Status')
        #     if current_tr_mode == 'drive' or current_tr_mode == 'reverse':
        #         # TODO: Add precondition check
        #         self.HAL.lighting.handler.notification('error')
        #     else:
        #         pass

        if self.state.get('vin_complete') is not True:
            self.get_vin()



        return state

    def get_state_of_charge(self, battery_id):
        ''' Read data from propulsion_battery__X__soc.'''
        return self.state.get(f'propulsion_battery__{battery_id}__soc')


module_init = (
    VehicleInterface,
    None,
    None
)
# handler = VehicleInterface(config=CONFIG_DEFAULTS, init_script=INIT_SCRIPT)


if __name__ == '__main__':
    print(handler)
    print(handler.config)
