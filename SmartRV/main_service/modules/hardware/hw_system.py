# What controls does the water system need
# Who is providing this control

from copy import deepcopy
from multiprocessing.sharedctypes import Value
import subprocess
import time
import sys
import struct

if __name__ == '__main__':
    # adding to test this file as main
    import sys
    sys.path.append("main_service")
    sys.path.append(".")

from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.logger import prefix_log
from main_service.modules.data_helper import byte_flip

from common_libs.models.common import RVEvents, EventValues
from main_service.components.energy import (
    BatteryManagement, BatteryMgmtState,
    GeneratorPropane, GeneratorDiesel, GeneratorState,

)
from common_libs.system.schedule_manager import ScheduledFunctionManager

from main_service.components.catalog import component_catalog
from main_service.components.energy import(
    BatteryMgmtState,
    BatteryManagement,

    EnergyConsumer,
    EnergyConsumerState,

    PowerSourceSolar,
    PowerSourceShore,

    PowerSourceAlternator,
    PowerSourceState,

    FuelTankState,
    FuelTank,

    InverterAdvancedState,
    InverterAdvanced,
)

import logging

wgo_logger = logging.getLogger('uvicorn.error')


# TODO: Review and delete if not purpose
INIT_SCRIPT = {}
SHUTDOWN_SCRIPT = {}


# CONSTANTS used in this hw layer

# TODO: Modify this to read from file on start
# Refer to e.g. energy for details
CONFIG_DEFAULTS = {}

# Handled wholistically in HAL Baseclase
# CODE_TO_ATTR = {}


RVC_DSA_LIST = {
    68: 'Control Panel',
    88: 'Main Thermostat',
    90: 'Thermostat #3',
    91: 'Thermostat #4',
    92: 'Thermostat #5',
    93: 'Thermostat #6',
    94: 'Main Furnace (Conventional)',
    101: 'Water Heater #1',
    102: 'Water Heater #2',
}


class System(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        for key, value in config.items():
            self.state[key] = value
        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')
        self.configBaseKey = 'system'
        self.init_components(components, self.configBaseKey)

        lockouts = getattr(self, self.CODE_TO_ATTR['lk'])
        for key, lockout in lockouts.items():
            print(key, lockout, '----', lockout.attributes)
            if 'defaultActive' in lockout.attributes:
                lockout.state.active = lockout.attributes['defaultActive']

        self.state = {'CAN': {}}

        self.WINNCONNECT_DGNS = {
            65260: {},    # VIN
            61252: {     # WC Status
                'func': self.emit_system_status,
                'args': (),
                'kwargs': {}
            },

        }

    def run_dgn_func(self, dgn):
        dgn_handle = self.WINNCONNECT_DGNS.get(dgn)
        if dgn_handle is None:
            print('[SYSTEM] DGN not support', dgn)
            return

        func = dgn_handle.get('func')
        args = dgn_handle.get('args', ())
        kwargs = dgn_handle.get('kwargs', {})

        return func(*args, **kwargs)

    def emit_system_status(self):
        self.HAL.app.can_sender.can_send_raw(
            '18FE4444',
            '0001020304050607'
        )

    # Update Can state
    def update_can_state(self, msg_name, can_msg):
        updated, state = False, None

        if msg_name == 'dm_rv':
            # RV-C diagnostics message
            # Fine the source address
            try:
                dsa = int(can_msg.get('DSA'))
            except ValueError as err:
                print('Cannot convert DSA to int', err)
                dsa = -1

            fmi = can_msg.get('FMI')
            red_lamp = int(can_msg.get('Red_Lamp_Status'))
            yellow_lamp = int(can_msg.get('Yellow_Lamp_Status'))
            spn_lsb = can_msg.get('SPN_LSB')
            source_address = can_msg.get('source_address')

            self.state['CAN'][f'{source_address}__{dsa}'] = can_msg

            if red_lamp == EventValues.ON:
                self.event_logger.add_event(
                    RVEvents.WINNCONNECT_SYSTEM_CAN_BUS_RVC_RED_LAMP_CHANGE,
                    dsa,
                    red_lamp
                )

            if yellow_lamp == EventValues.ON:
                self.event_logger.add_event(
                    RVEvents.WINNCONNECT_SYSTEM_CAN_BUS_RVC_RED_LAMP_CHANGE,
                    dsa,
                    yellow_lamp
                )

            # Get the related details from can system
            # Get related component
            # Trow generic error first

        elif msg_name == 'request_for_dgn':
            # Check if requests are coming in
            desired_pgn = int(can_msg.get('Desired_DGN'))
            print('[SYSTEM][CAN] Received request for DGN', desired_pgn)
            print('[SYSTEM][CAN] Received request for DGN', self.run_dgn_func(desired_pgn))




        # super().update_can_state(can_msg)

        # PSM inputs
        # Voltage readings
        #

        return state


module_init = (
    System,
    'system_mapping',
    'components'
)

if __name__ == '__main__':
    pass
