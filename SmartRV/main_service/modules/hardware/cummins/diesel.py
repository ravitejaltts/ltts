'''Module for Cummins diesel generator controls.'''

import subprocess
import time

from main_service.modules.hardware.common import HALBaseClass, shell_cmd
from main_service.modules.logger import prefix_log
from  common_libs.models.common import RVEvents, EventValues

import logging

wgo_logger = logging.getLogger('main_service')


class CGenerator(HALBaseClass):
    state = {}

    def __init__(self, config={}, init_script={}):
        # Given by base class
        # .state / .savedState / .config
        HALBaseClass.__init__(self, config=config)
        self.state = {'generator': {'operating': 0}}
        for key, value in config.items():
            self.state[key] = value
        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')


    def request_change(self, in_state:dict) -> dict:
        for key, value in in_state:
            if value != None:
                if key == 'operating':
                    if value == EventValues.OFF:
                        #Send all shutdown command
                        result = shell_cmd('cansend canb0s0 19FFDA44#00FFFFFFFFFFFFFF',print_it=1)
                    elif value == EventValues.RUN:
                        #Start and run the genertor
                        result = shell_cmd('cansend canb0s0 19FFDA44#01FFFFFFFFFFFFFF',print_it=1)

                    # STORE THE NEW STATE
                    self.state['generator'][key] = value
        return self.state['generator']
