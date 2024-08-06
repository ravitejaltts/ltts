import time

import logging

wgo_logger = logging.getLogger('main_service')

from  common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.constants import *
from main_service.modules.logger import prefix_log

# 800 is using CZone to switch the heater on/off
# 800 is using CZone oto switch AC compressor on and AC fan lo/hi
try:
    from main_service.modules.hardware.czone.control_x_plus import CZone
except ModuleNotFoundError:
    from czone.control_x_plus import CZone


init_script = {
    # Should a real script go here for init
}

config = {
    'charger': {
        'count': 1,
        'items': []
    },
    'inverter': {
        'count': 1,
        'items': []
    }
}

mapping = {
    # Charger
    'charger_1': {
        'id': 1,
        'inverted': False,
        'name': 'Battery Charger',
        'type': 'Cerbo GX',
        'subType': 'Combination',
        'description': 'Charger with RV-C control',
        'information': 'Unified controls with inverter_1'
    },
    # Inverter
    'inverter_1': {
        'id': 1,
        'name': 'AC Inverter',
        'type': 'Cerbo GX',
        'subType': 'Combination',
        'information': 'Unified controls with charger_1'
    },
}

# TODO: Fold into the above and read from file/template
information = [
    {
        'title': 'MANUFACTURER INFORMATION',
        'items': [
            {
                'title': 'Bettery Charger and AC Inverter Controller',
                'sections': [
                    {
                        'title': None,
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'Victron Energy'
                            },
                            {
                                'key': 'Product Model',
                                'value': 'Cerbo GX'
                            }
                        ]
                    }
                ]
            },
        ]
    }
]


class CerboGxControl(object):
    #TODO Possibly this class should have the commands ans well.
    # INVERETER_COMMAND
    # CHARGER_COMMAND
    # CHARGER_CONFIGURATION_COMMAND_2

    def __init__(self, config={}, init_script={}):
        # Given by base class
        # .state / .savedState / .config

        self.state = {}
        for key, value in config.items():
            self.state[key] = value

        self.configBaseKey = 'cerbogx'
        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')

        self.init_script = init_script
        self.run_init_script()
        self.msg_names = ['inverter_ac_status_1', 'inverter_status',
                           'charger_ac_status_1', 'charger_ac_status_2',
                          'charger_status','charger_status_2']

    def run_init_script(self):
        for key, value in self.init_script.items():
            # Iterate over list of commands
            #TODO: determine default for ElWell
            prefix_log(wgo_logger, __name__, f'Initializing: {key}')

    def get_hw_info(self):
        return {}

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        ''' From the Cerbo GX
        '''

        updated = False
        state = None

        if msg_name == 'inverter_ac_status_1':
            inverter_instance = can_msg.get('Instance','65')

            voltage = can_msg.get('RMS_voltage')
            current = can_msg.get('RMS_current')
            frequency = can_msg.get('Frequency')

            if voltage is not None and 'Data Invalid' not in voltage:
                RMS_voltage = float(voltage)
            else:
                RMS_voltage = None

            if current is not None and 'Data Invalid' not in current:
                RMS_current = float(current)
                if RMS_current < 0:
                    RMS_current = 0.0
            else:
                RMS_current = None

            if inverter_instance == '65':
                '''L1 reporting'''
                self.state[f'ei1']['voltage'] = RMS_voltage
                self.state[f'ei1']['urrent'] = RMS_current
                # Record as L1 to keep all data
                self.state[f'ei1']['voltage'] = RMS_voltage
                self.state[f'ei1']['current'] = RMS_current
                self.state[f'ei1']['frequency'] = frequency

                state = {
                    'inverterVoltage': self.state[f'ei1']['voltage'],
                    'inverterCurrent': self.state[f'ei1']['current']
                }
            elif inverter_instance == '81':
                # Record as L2 to keep all data
                self.state[f'ei2']['voltage'] = RMS_voltage
                self.state[f'ei2']['current'] = RMS_current
                self.state[f'ei2']['frequency'] = frequency
                # Not reporting L2 separaetly yet
                state = {'NA':None}
            else:
                raise ValueError('Unknown Inverter instance:',inverter_instance)

            updated = True
        elif msg_name == 'charger_status_2':
            charger_instance = can_msg.get('Charger_Instance','1')

            voltage = can_msg.get('Charge_voltage')
            current = can_msg.get('Charge_current')

            temperature = can_msg.get('Charger_temperature')

            if voltage is not None and 'Data Invalid' not in voltage:
                Charger_voltage = float(voltage)
            else:
                Charger_voltage = None

            if current is not None and 'Data Invalid' not in current:
                Charger_current = float(current)
                if Charger_current < 0:
                    Charger_current = 0.0
            else:
                Charger_current = None

            if temperature is None or 'Data Invalid'  in temperature:
                temperature = None

            self.state[f'charger__1__voltage'] = Charger_voltage
            self.state[f'charger__1__current'] = Charger_current
            self.state[f'charger__1__temperature'] = temperature

            state = {
                'chargerVoltage': self.state[f'charger__1__voltage'],
                'chargerCurrent': self.state[f'charger__1__current'],
                'chargerTemperature': self.state[f'charger__1__temperature']
            }

            updated = True
        elif msg_name == 'charger_ac_status_1':
            inverter_instance = can_msg.get('Instance','1')

            voltage = can_msg.get('RMS_voltage')
            current = can_msg.get('RMS_current')
            _frequency = can_msg.get('Frequency')

            if voltage is not None and 'Data Invalid' not in voltage:
                RMS_voltage = float(voltage)
            else:
                RMS_voltage = None

            if current is not None and 'Data Invalid' not in current:
                RMS_current = float(current)
                if RMS_current < 0:
                    RMS_current = 0.0
            else:
                RMS_current = None

            if _frequency is not None and 'Data Invalid' not in _frequency:
                frequency = float(_frequency)
            else:
                frequency = None

            if inverter_instance == '1':
                self.state[f'charger__1__ac_voltage'] = RMS_voltage
                self.state[f'charger__1__ac_current'] = RMS_current
                self.state[f'charger__1__ac_frequency'] = frequency
                # To be clear about L1 - not 'instance'
                self.state[f'charger__L1__ac_voltage'] = RMS_voltage
                self.state[f'charger__L1__ac_current'] = RMS_current
                self.state[f'charger__L1__ac_frequency'] = frequency

                state = {
                    'chargerAcVoltage': self.state[f'charger__1__ac_voltage'],
                    'chargerAcCurrent': self.state[f'charger__1__ac_current'],
                    'chargerAcFrequency': self.state[f'charger__1__ac_frequency']
                }
            elif inverter_instance == '17':
                # Data from L2
                self.state[f'charger__L2__ac_voltage'] = RMS_voltage
                self.state[f'charger__L2__ac_current'] = RMS_current
                self.state[f'charger__L2__ac_frequency'] = frequency
                # Not reporting L2 separaetly yet
                state = {'NA':None}
            else:
                raise ValueError('Unknown Charger instance',inverter_instance)
            updated = True
        else:
            state = {'NA':None}
            updated = True

        return updated, state
