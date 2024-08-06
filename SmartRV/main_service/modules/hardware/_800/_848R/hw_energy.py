# What controls does the water system need
# Who is providing this control

from copy import deepcopy
from multiprocessing.sharedctypes import Value
import subprocess
import time
import struct
import os
from main_service.modules.hardware._800.hw_energy import (
    EnergyControlBaseCLass,
    INVERTER_CONTINUOUS_MAX,
    CHARGE_LVL_INITIAL,
    SHORE_POWER_ID,
    PRO_POWER_ID,
    BATTERY_ID,
    AVC_CIRCUIT,
    PRO_POWER_CIRCUIT,
    SOC_RANGE_LOW,      # Do not increase charge level when below this
    SOC_RANGE_HIGH,
    LVL_DETECT_PROTECTION_TIMER,
    SOLAR_ACTIVE_THRESHOLD,
    CHARGE_LVL_PRO_POWER,
    CHARGE_LVL_L2,
    DEFAULT_INVERTER_ID,
    L1_LOW,
    L1_HIGH,
    L2_LOW,
    L2_HIGH,
    SOLAR_SOURCE_ID
)
from main_service.modules.logger import prefix_log
from main_service.modules.data_helper import byte_flip
from main_service.modules.hardware.victron.cerbogx import CerboGxControl

from main_service.modules.constants import (
    CHARGE_LVL_1_STR,
    CHARGE_LVL_1_5_STR,
    CHARGE_LVL_2_STR,
    CHARGE_LVL_PRO_POWER_STR,
    celcius_2_fahrenheit,
    fahrenheit_2_celcius
)
from common_libs.models.common import RVEvents, EventValues

import logging

wgo_logger = logging.getLogger('main_service')

# 800 is using CZone to switch the heater on/off
# 800 is using CZone oto switch AC compressor on and AC fan lo/hi
try:
    from main_service.modules.hardware.czone.control_x_plus import CZone
except ModuleNotFoundError:
    from czone.control_x_plus import CZone


czone = CZone(
    cfg={}
)

INIT_SCRIPT = {
    # Should a real script go here for init
    # 'bms': [
    #     # Set to 1300 watts charge level
    #     'cansend canb0s0 18EF4644#5501024692040000',
    # ]
}

BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

shutdown_script = {}

# # BMS inverter FR min is 9.0.02 for load adjustment
# # Charge level will remain the same regardless of load


# INVERTER_CONTINUOUS_MAX = 2400
# DEFAULT_INVERTER_ID = 1

# CHARGE_LVL_INITIAL = 1300           # Watts
# # Latest Pro Power change as per Neng 2022/12/15
# CHARGE_LVL_PRO_POWER = 1900         # Watts
# CHARGE_LVL_L1_5 = 2650              # Watts
# CHARGE_LVL_L2 = 5350                # Watts
# VEHICLE_SOC_PRO_POWER_CUTOFF = 33   # %
# LVL_DETECT_PROTECTION_TIMER = 60    # Seconds

# SOC_RANGE_LOW = 10      # Do not increase charge level when below this
# SOC_RANGE_HIGH = 90     # Possibly reduce charge lvl when above this

# L2_LOW = 179
# L2_HIGH = 250

# L1_LOW = 105
# L1_HIGH = 130


# AVC_CIRCUIT = 35
# PRO_POWER_CIRCUIT = 0x0d
# # WHY is it 4?
# # UI agnostic to HW circuit, but why 4 ?
# SHORE_POWER_ID = 1

# PRO_POWER_ID = 2

# BATTERY_ID = 1

# SOLAR_SOURCE_ID = 4

# # TODO: Clarify threshold if any
# SOLAR_ACTIVE_THRESHOLD = 20     # Watts


# TODO: Modify this to read from file on start
CONFIG_DEFAULTS = {
    'battery__1__soc': None,
    'battery__1__voltage': None,
    'battery__1__current': None,
    'battery__1__charging': None,
    'battery___1__remaining_runtime_minutes': None,
    'bms__1__charge_lvl': 0,
    'bms__1__temp': None,

    'charger__1__voltage': None,

   'ei1': {
        'current_load': None,
        'continuous_max_load': INVERTER_CONTINUOUS_MAX,
        'overld': False,
        'overload_timer': 0,
    },

    'solar__4__input_voltage': None,
    'solar__4__input_current': None,

    'shore__1__lvl': None,
    'shore__1__lock': False,

    # This updates from vehicle hw layer
    'pro_power__2__enabled': None,

    # Global override for testing
    'lvl2_algo_enabled': 1,

    'chargerAcVoltage': None,
    'chargerAcCurrent': None,
    'inverterCurrent': None,
}

# SOURCE Mapping
SOURCE_MAPPING = {
    1: {
        'type': 'SOURCE_EV_SHORE',
        'controls': {
            'setChargeLevel': 'int'
        }
    },
    # 2: {
    #     'type': 'SOURCE_PRO_POWER',
    #     'controls': {
    #         'onOff': 'int'
    #     }
    # },
    4: {
        'type': 'SIMPLE_INPUT_SOLAR'
    }
}

# AVC Circuit


#CZone instance IDs for NMEA2K fluid level
AC_CURRENT_SENSOR_ID = 14
AC_CHARGER_SENSOR_ID = 15
AC_MAX_AMPS = 50

# Copntrols the charge levels supported by Lithionics chargers
MIN_CHARGE_LEVEL = 0        # Max charging, not restricted
MAX_CHARGE_LEVEL = 7200     # Max desired for LVL2 charging (240/30 amps)

# Solar

# Solar default voltage, we cannot read the voltage so assume a value in the range of the solar charger
SOLAR_DEFAULT_VOLTAGE = 53.0
SOLAR_SHUNT_AMPS = 50       #
SOLAR_SHUNT_MV = 50        # TODO: Change this to 50 when we have the shunt confirmed
SOLAR_CZONE_SHUNT_MV = 50   # Default shunt millivolt assumed is 50
SOLAR_SHUNT_FACTOR = 450 / SOLAR_SHUNT_AMPS * (SOLAR_SHUNT_MV / 50)
SOLAR_SHUNT_OFFSET = 0.8


class EnergyControl(EnergyControlBaseCLass):
    def __init__(self, config={}, init_script={}):
        super().__init__(config, init_script)
        self.init_script = init_script
        self.run_init_script()

    def run_init_script(self):
        prefix_log(wgo_logger, __name__, f'Initializing for 848R floorplan')
        for key, value in self.init_script.items():
            # Iterate over list of commands
            prefix_log(wgo_logger, __name__, f'Initializing: {key}')
            for cmd in value:
                result = subprocess.run(cmd, shell=True)
                if result != 0:
                    prefix_log(wgo_logger, __name__, f'cmd: {cmd} failed', lvl='error')
        self.set_charger_lvl(CHARGE_LVL_INITIAL)
        self.cerbogx = CerboGxControl()


    def update_can_state(self, msg_name, can_msg):
        '''Receive updates to energy modules.  Adds Cerbo GX'''

        updated, state = super().update_can_state(msg_name, can_msg)

        if not updated:
            if msg_name in self.cerbogx.msg_names :
                print('Cerbo GX ************************************')
                updated, state = self.cerbogx.update_can_state(msg_name, can_msg)
                #self.state |= state
                print('Cerbo GX returned: ',state)
                # Map cerbo gx to UI
                if 'inverterCurrent' in state:
                    self.state['ei1']['current_load'] = state.get('inverterCurrent')
                    if self.state['ei1']['current_load'] is not None:
                        self.event_logger.add_event(
                            RVEvents.INVERTER_CHARGER_CURRENT_METER_AFTER_INVERTER_CHANGE, #TODO Verify this the right current meter here
                            1,  # Report instance '1' for the platform  AC_CURRENT_SENSOR_ID,
                            self.state['ei1']['current_load'])
                        # check load shedding
                        self.run_load_shedding()

                if 'chargerAcCurrent' in state:
                    self.state['shore__1__current_amps'] = state.get('chargerAcCurrent')
                    if self.state['shore__1__current_amps']  is not None:
                        self.event_logger.add_event(
                                RVEvents.ENERGY_MANAGEMENT_AC_CURRENT_METER_CHANGE, #TODO Verify this the right current meter here
                                1,  # Report instance '1' for the platform  AC_CHARGER_SENSOR_ID,
                                self.state['shore__1__current_amps'])

                    self.state['charger__1__voltage'] = state.get('chargerAcVoltage')

        return updated, state

    def is_power_incoming(self):
        '''Checks the given systems, if power is flowing in.'''
        # Check solar value positive
        power_incoming = 0
        solar_input = self.get_solar_input(solar_id=4)
        if solar_input.get('active') is True:
            power_incoming = 1

        #shore_power = self.power_source_active(SHORE_POWER_ID)
        #if shore_power == 1:

        if self.state['charger__1__voltage'] is not None:
            if self.state['charger__1__voltage'] > 0:
                power_incoming = 1

        # Check BMS value positive
        # Check if chargers have a positive charging current

        return power_incoming

    # def set_source(self, source_id):
    #     self.state['']
    # TODO: Create code to trigger AVC switch event

    def power_source_active(self, source_id):
        source_state = None
        if source_id == 1:
            source_state = 0
            if self.state[f'charger__{source_id}__voltage'] is not None:
                if self.state[f'charger__{source_id}__voltage'] > 0:
                    source_state = 1

            self.event_logger.add_event(
                    RVEvents.ENERGY_MANAGEMENT_AVC2_MODE_CHANGE,
                    1,  # TODO: Get instance from some place in config
                    source_state
                ) # This should report 0 or 1
        return source_state

    def get_state_of_charge(self, battery_id):
        return self.state.get(f'battery__{battery_id}__soc')

    def get_remaining_runtime(self, battery_id):
        minutes_remaining = self.state.get(f'battery___{battery_id}__remaining_runtime_minutes')
        if minutes_remaining is None:
            return None

        return self.calculate_days(minutes_remaining)

    def get_state_of_health(self, battery_id):
        return self.state.get(f'battery__{battery_id}__soh')

    def get_capacity_remaining(self, battery_id):
        return self.state.get(f'battery__{battery_id}__capacity_remaining')

    def get_battery_voltage(self, battery_id):
        return self.state.get(f'battery__{battery_id}__voltage')

    def get_battery_current(self, battery_id):
        return self.state.get(f'battery__{battery_id}__current')

    def get_battery_state(self, battery_id):
        # Get Voltage
        # Get Current
        # Calculate Wattage
        current = self.get_battery_current(battery_id)
        voltage = self.get_battery_voltage(battery_id)
        watts = None
        if current is not None and voltage is not None:
            watts = round(current * voltage, 3)
            voltage = round(voltage, 3)
            current = round(current, 3)

        remainingRuntime = self.get_remaining_runtime(battery_id)
        charging = None
        minutes = None

        if remainingRuntime is not None:
            charging = remainingRuntime.get('isCharging')
            minutes = remainingRuntime.get('original_minutes')

        bms_temp = self.state.get(f'bms__{battery_id}__temp')
        # TODO: Check unit
        if bms_temp is not None:
            try:
                bms_temp_rd = round(float(bms_temp),1)
                bms_temp_out = celcius_2_fahrenheit(bms_temp_rd)

                self.event_logger.add_event(
                    # Need to verify this is was is wanted in battery - or event in state needs updating
                    RVEvents.BATTERY_TEMP_CHANGE,
                    1,  # Report instance '1' for the platform
                    round(bms_temp,3) # report battery temp to IOT in celcius
                )
            except TypeError:
                bms_temp_out = bms_temp
        else:
            bms_temp_out = bms_temp


        return {
            'isCharging': charging,
            'remainingRuntime': minutes,
            'stateOfCharge': self.get_state_of_charge(battery_id),
            'stateOfHealt': self.get_state_of_health(battery_id),
            'capacityRemaining': self.get_capacity_remaining(battery_id),
            'voltage': voltage,
            'current': current,
            'watts': watts,
            'bmsTemp': bms_temp_out
        }

    def get_charger_voltage(self, charger_id):
        return self.state.get(f'charger__{charger_id}__voltage')

    def get_active_consumers(self):
        '''List all consumers the system is aware of.'''
        # Overall usage
        # All sources + bms_wattage
        # Inverter Overall Usage
        consumers = []
        ac_total_usage = self.get_inverter_load(inverter_id=DEFAULT_INVERTER_ID)
        if ac_total_usage is not None:
            # AC Circuits enabled and having a known wattage
            pass
            # AC Delta to be reported

        # DC Circuits on
        # DC Load per circuit
        #
        return consumers

    def get_inverter_load(self, inverter_id):
        base_voltage = 120
        amps = self.state.get(f'ei{inverter_id}')['current_load']
        if amps is None:
            return None

        return int(base_voltage * amps)

    def get_inverter_continuous_max(self, inverter_id):
        '''Get max continuous load.'''
        # TODO: Consider temperature
        return self.state.get(f'ei{inverter_id}')['continuous_max_load']

    def get_inverter_overld(self, inverter_id):
        current_load = self.get_inverter_load(inverter_id)


        in_overload = False
        if current_load and (current_load > self.get_inverter_continuous_max(inverter_id)):
            in_overload = True

        state = {
            'overload': in_overload
        }
        return state

     #TODO: We can remove this function and possibly others -- the base class implements the same code
    # def get_inverter_state(self, zone_id=1, inverter_id=1):
    #     # Get Circuit state, is it on/off
    #     # get
    #     return {
    #         'onOff': self.state.get(f'ei{inverter_id}']['onOff')
    #     }

    #TODO: Remove code - it is a duplication of the base class
    # def get_total_input(self):
    #     # Get solar
    #     solar = self.get_solar_input()
    #     charger = self.get_charger_input()

    #     solar_watts = solar.get('watts')
    #     if solar_watts is None:
    #         solar_watts = 0

    #     # TODO: Check if that is desirable
    #     # Report -10% on charger as this is the power arriving at the BMS
    #     # total = solar.get('watts') + (charger.get('watts') * 0.9)
    #     total = solar_watts + (charger.get('watts'))

    #     return {
    #         'watts': total,
    #         'kilowatts': round(total / 1000, 1)
    #     }

    def get_charger_input(self, charger_id=1):
        # TODO: Implement power readout
        # TODO: Figure out issues between inverter circuit and sensor
        IGNORE_THRESHOLD = 0.9
        # Measurement error ?
        # Ignore that data
        current = self.state.get(f'shore__{charger_id}__current_amps')
        if current is None or current == 0 or current < IGNORE_THRESHOLD:
            return {
                'watts': 0,
                'voltage': 0,
                'current': 0
            }

        # Get the current charge limit
        #charge_lvl = self.state.get('bms__1__charge_lvl', 0)
        # Divide the charge limit by the measured current and get the voltage
        voltage = self.state.get(f'charger__1__voltage')
        return {
            'watts': voltage * current,
            'voltage': voltage,
            'current': current
        }

    def get_shore_power_state(self, shore_id=1):
        '''Get state for shore power.'''
        # Get Voltage, Current, Wattage
        # Get Current Charge level
        current = self.state.get(f'shore__{shore_id}__current_amps')
        charge_lvl = self.state.get('bms__1__charge_lvl', 0)
        if current is None or current == 0:
            voltage = None
            watts = None
        else:
            voltage = charge_lvl / current
            watts = voltage * current

        # Get Set charge level
        return {
            'watts': watts,
            'current': current,
            'voltage': voltage,
            'active': self.power_source_active(shore_id),
            # 'currentChargeLevel': self.state.get('shore__{shore_id}__lvl'),
            'setChargeLevel': self.state.get(f'shore__{shore_id}__lvl')
        }

    def get_vehicle_power_state(self, source_id=2):
        '''Get state of the available vehicle charging source(s).

        Could be Pro Power, or Wkaespeed alternator, technically could be multiple.'''
        # Is it currently active ?
        # Check AVC state
        # Chack if Pro Power is enabled
        # If yes, for Pro Power use the same wattage calculation as for shore
        active = None
        enabled = None
        watts = None
        voltage = None
        current = None

        pro_power_enabled = self.state.get(f'pro_power__{source_id}__enabled')

        return {
            'watts': watts,
            'active': active,
            'current': current,
            'voltage': voltage,
            'onOff': pro_power_enabled
        }

    def get_energy_sources(self, zone_id=1):
        '''Get full list of energy sources.'''
        # Solar
        # Shore
        # Vehicle / Pro-Power
        sources = []

        solar = self.get_solar_input(SOLAR_SOURCE_ID)
        sources.append(
            {
                'id': SOLAR_SOURCE_ID,
                'type': 'SIMPLE_INPUT_SOLAR',
                'name': 'Solar Input',
                'description': 'Solar input from multiple chargers through Shunt sensor',
                'state': solar
            }
        )

        shore = self.get_shore_power_state(SHORE_POWER_ID)
        sources.append(
            {
                'id': SHORE_POWER_ID,
                'type': 'SOURCE_EV_SHORE',
                'name': 'Shore Power',
                'description': '',
                'state': shore
            }
        )


        return sources


    def set_source_state(self, zone_id, source_id, state):
        ''''''
        # Check the source exists
        source = SOURCE_MAPPING.get(source_id)
        source_type = source.get('type')
        if source is None:
            raise IndexError(f'Cannot get {source_id}, from zone: {zone_id}')

        controls = source.get('controls')
        if controls is None:
            raise KeyError(f'Cannot control anny properties of source: {source_id} in zone: {zone_id}')

        new_state = {}

        # Check if controllable keys are available
        for key, value in controls.items():
            if key in state:
                new_state[key] = state[key]

        if new_state:
            # if source_type == 'SOURCE_PRO_POWER':
            #     self.HAL.electrical.handler.dc_switch(PRO_POWER_CIRCUIT, new_state.get('onOff'), 100)
            #     self.event_logger.add_event(
            #         RVEvents.PROPOWER_PRO_POWER_RELAY_CHANGE,
            #         1,  # TODO: Get instance from some place in config
            #         new_state.get('onOff')) # This should report 0 or 1
            # elif
            if source_type == 'SOURCE_EV_SHORE':
                self.set_charger_lvl(new_state.get('setChargeLevel'), source_id)
                self.event_logger.add_event(
                    RVEvents.SHORE_POWER_CONNECTED,
                    1,  # TODO: Get instance from some place in config
                    1) # This should report 0 or 1
            else:
                 self.event_logger.add_event(
                    RVEvents.SHORE_POWER_DISCONNECTED,
                    1,  # TODO: Get instance from some place in config
                    1) # This should report 0 or 1

        return new_state

    def get_ui_response(self):
        response = super().get_ui_response()

        if self.is_power_incoming():
            total_input_text = 'Power On'
        else:
            total_input_text = 'Not Charging'

        #Fill in the values that the base class can not do
        response['items'][0]['subtext'] = total_input_text
        response['items'][0]['active'] = self.is_power_incoming()
        SHORE_SOURCE_ID = 1
        ems_shore_source_active = self.power_source_active(SHORE_SOURCE_ID)
        ems_shore_input = self.get_charger_input(SHORE_SOURCE_ID)

        #Kilowatts
        if ems_shore_source_active:
            ems_shore_power_subtext = round(ems_shore_input.get('watts') / 1000, 1)
        else:
            ems_shore_power_subtext = '--'

        response['items'][0]['widgets'][1] = {
                        'name': 'EmsShoreWidget',
                        'title': 'SHORE',
                        'subtext': ems_shore_power_subtext,
                        'subtext_unit': ' kW',

                        'type': 'Info',
                        'state': {
                            'onOff': ems_shore_source_active
                        },

                        'actions': None,
                        # Shows the bolt state
                        'active': ems_shore_source_active
                    }

        #TODO better identify the WAKESPEED here
        ems_propower_source_onOff = self.state.get('pro_power__1__enabled', 0)
        ems_propower_source_active = 0
        response['items'][0]['widgets'][2] = {
                        'name': 'EmsWakePowerWidget',
                        'title': 'Wake',
                        'subtext': '--',
                        'subtext_unit': ' kW',
                        'type': 'Simple',
                        # New style using state for the specific type
                        'state': {
                            'onOff': ems_propower_source_onOff
                        },
                        # 'actions': ['action_default',],
                        # 'action_default': {
                        #     'type': 'api_call',
                        #     'action': {
                        #         # TODO: Abstract in HAL away from UI and also run required algorithms
                        #         # Adding a number to allow for multiple ac inputs
                        #         'href': f'{BASE_URL}/api/electrical/dc/13',
                        #         'type': 'PUT'
                        #     }
                        # },
                        # Shows the bolt state
                        'active': ems_propower_source_active
                    }
        return response

handler = EnergyControl(config=CONFIG_DEFAULTS, init_script=INIT_SCRIPT)


if __name__ == '__main__':
    print(handler)
    print(handler.config)
