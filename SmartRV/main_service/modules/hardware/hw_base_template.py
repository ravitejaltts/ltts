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

from  common_libs.models.common import RVEvents, EventValues
from main_service.components.energy import (
    BatteryManagement, BatteryMgmtState,
    GeneratorPropane, GeneratorDiesel, GeneratorState,

)
#from main_service.modules.storage_helper import read_default_config_json_file
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


class HalTempalte(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        for key, value in config.items():
            self.state[key] = value
        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')
        self.configBaseKey = 'nameofthelayercategory'
        self.init_components(components, self.configBaseKey)

    # Add specific init if needed
    # def init_energysystems(self, mapping, tanks):
    #     # initialize systems
    #     # TODO: Make a generic init function - copied from watersystems
    #     # TODO: and it looks like it might need to move to run_init_script
    #     # Tanks
    #     for tank_id in tanks:
    #         tank_key = f'ft{tank_id}'
    #         tank = mapping.get(tank_key, {})
    #         # tank['system_key'] = tank_key
    #         self.state[tank_key] = tank.get('state', {})
    #         self.meta[tank_key] = tank

    # ######## New State handlers ############
    # HAL should have a set_{componentType}_state method
    def set_compType_state(self, instance: int, state: dict):
        '''Update the state of the given compType.'''
        # TODO: Handle KeyErrors properly
        # energy_source = self.energy_source[instance]
        # # Check if source can be controlled (use onOff as an attribute being present)
        # if hasattr(energy_source.state, 'onOff'):
        #     # TODO: Perform action if applicable, currently only ProPower has this
        #     pass
        # else:
        #     # Fail out properly ?
        #     raise ValueError(f'Energy Source: {instance} does not support setting state onOff')

        # return energy_source.state
        pass

    # Get state not required as it is handled by addressing the state of the component instance


if __name__ == '__main__':
    pass
