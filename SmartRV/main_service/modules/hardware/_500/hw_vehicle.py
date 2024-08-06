# What controls does the water system need
# Who is providing this control

import logging

from common_libs import environment
from common_libs.models.common import EventValues, RVEvents
from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.logger import prefix_log

wgo_logger = logging.getLogger('uvicorn.error')
_env = environment()


# Intermotive chassis interface
vehicle_interface = None


INIT_SCRIPT = {
    # # Should a real script go here for init
    # 'vin': [
    #     # Set to 1300 watts charge level
    #     ('can', '18EF4644', '5501024692040000'),
    # ]
}

shutdown_script = {}


# TODO: Modify this to read from file on start
CONFIG_DEFAULTS = {
    'propulsion_battery__1__soc': None,
    'park_brake_status': None,
    'current_odo_reading': None,
    'vin_buffer': {},
    'vin': None
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


def active_to_eventvalue(active):
    '''HAL action come in as True/False but the models expect an EventValue.'''
    if active is True:
        return EventValues.TRUE
    elif active is False:
        return EventValues.FALSE
    else:
        return None


class VehicleInterface(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        # Given by base class
        # .state / .savedState / .config
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        print('*' * 80)
        print('[VEHICLE] Config', config)
        print('*' * 80)
        for key, value in config.items():
            self.state[key] = value
        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')

        self.configBaseKey = 'vehicle'
        self.init_components(components, self.configBaseKey)

        self.state['vin_buffer'] = {}

        # # Init defaults for vehicle
        # if hasattr(self, 'vehicle'):
        #     for ch_id, ch in self.vehicle.items():
        #         ch.get_db_state()

    # set_state
    # get_state
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
        # NOTE: Removed as it interfered with a unit test
        # # TODO: Move this to a better place on init and retry until VIN is known
        # Bring back to have the option to populate the VIN with a module
        # cmd = 'ECFE00'
        # self.HAL.app.can_sender.can_send_raw(
        #     '18EA0044',
        #     cmd
        # )
        try:
            self.vehicle[1].state.vin = vin
            self.vehicle[1].update_state()  # emit event
        except Exception as err:
            print(f"Unable to set component vin: {err}")


        return vin

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''500 Series currently does not support any CAN updates other than VIN during manufactuing.
        PSM outputs come from CZone, so shall be queried there from a mapping.'''

        updated = False
        state = None

        if msg_name == 'vin_response':
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
            print('[VIN] Adding fragment to VIN buffer', list_num, vin_fragment)
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
                        stored_vin = vin_file.read().strip()
                except FileNotFoundError as err:
                    stored_vin = None

                if stored_vin is None:
                    write_vin(vin)
                elif stored_vin != vin:
                    # Mismatch
                    self.event_logger.add_event(
                        RVEvents.CHASSIS_VIN_CHANGE,
                        CHASSIS_ID,
                        vin
                    )
                    write_vin(vin)
                else:
                    # Do nothing
                    pass

                self.state['vin_complete'] = True

        # TODO: See where to put VIN requesting, 500 has no module the above code is not triggered
        # unless we feed it in.
        # if self.state.get('vin_complete') is not True:
        #     self.get_vin()

        return state

    def get_state_of_charge(self, battery_id):
        ''' Read data from propulsion_battery__X__soc.'''
        raise IndexError('Vehicle does not have a propulsion battery')

    def update_pb_ign_combo(self, state):
        '''Update internal state of the park brake as well as update related lockout.'''
        active = active_to_eventvalue(state.get('active'))

        self.vehicle[1].state.pbIgnCombo = active
        self.vehicle[1].update_state()
        lockout = self.HAL.system.handler.lockouts[EventValues.PSM_PB_IGN_COMBO]
        print('PSM_PB_IGN_COMBO Lockout', lockout)
        lockout.state.active = state.get('active')

    def update_park_brake(self, state):
        '''Update internal state of the park brake as well as update related lockout.'''
        active = active_to_eventvalue(state.get('active'))

        self.vehicle[1].state.parkBrk = active
        self.vehicle[1].update_state()
        lockout = self.HAL.system.handler.lockouts[EventValues.PARK_BRAKE_APPLIED]
        print('PARK Brake Lockout', lockout)
        lockout.state.active = state.get('active')

    def update_ignition(self, state):
        '''Update internal state of the ignition as well as update related lockout.'''
        print('Received update_ignition', state)
        active = active_to_eventvalue(state.get('active'))

        self.vehicle[1].state.ign = active
        self.vehicle[1].update_state()
        lockout = self.HAL.system.handler.lockouts[EventValues.IGNITION_ON]
        print('Ignition Lockout', lockout)
        lockout.state.active = state.get('active')

    def update_engine(self, state):
        '''Update internal state of the engine running state as well as update related lockout.'''
        print('Received update_running', state)
        active = active_to_eventvalue(state.get('active'))

        self.vehicle[1].state.engRun = active
        self.vehicle[1].update_state()
        lockout = self.HAL.system.handler.lockouts[EventValues.ENGINE_RUNNING]
        print('Engine Lockout', lockout)
        lockout.state.active = state.get('active')

    def update_transmission(self, state):
        '''Update internal state of the transmission as well as update related lockout.'''
        active = active_to_eventvalue(state.get('active'))

        self.vehicle[1].state.notInPark = active
        self.vehicle[1].update_state()
        lockout = self.HAL.system.handler.lockouts[EventValues.NOT_IN_PARK]
        print('Transmission not in park Lockout', lockout)
        lockout.state.active = state.get('active')

    def set_door_lock(self, instance, state):
        '''Set the door lock for this vehicle.

        Doorlock is realized in the 500 series with an H-Bridge on the RV1 CZone controller
        and requires the circuit ID to be known and direction to move for LOCK/UNLOCK
        '''
        # TODO: Get circuit that maps to the door lock and not hard code
        DL_CIRCUIT = 7

        direction = None
        if state.lock == EventValues.LOCK:
            # Figure direction of the command if applicable
            # Send lock command
            direction = 'FORWARD'
        elif state.lock == EventValues.UNLOCK:
            # Get circuit that maps to the door lock
            # Figure direction of the command if applicable
            # Send unlock command
            direction = 'BACKWARD'
        else:
            raise ValueError(f'Unsupported lock state: {state}')

        try:
            _ = self.HAL.electrical.handler.dc_switch(
                DL_CIRCUIT,
                1,
                output=100,
                direction=direction
            )
        except Exception as err:
            print('[ERROR] Error setting dc switch', err)
            raise

        self.event_logger.add_event(
            RVEvents.CHASSIS_DOOR_LOCK_CHANGE,
            instance,
            state.lock
        )

        # TODO: Any errors we can capture here and push up ?
        return state


module_init = (
    VehicleInterface,
    None,
    'components'
)


if __name__ == '__main__':
    pass
