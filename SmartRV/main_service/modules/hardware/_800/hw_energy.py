# What controls does the water system need
# Who is providing this control

from copy import deepcopy
from multiprocessing.sharedctypes import Value
import subprocess
import time
import struct

if __name__ == '__main__':
    # adding to test this file as main
    import sys
    sys.path.append("main_service")
    sys.path.append(".")

# from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.hardware.hw_base_energy import EnergyControlBaseClass

from main_service.modules.logger import prefix_log
from main_service.modules.data_helper import byte_flip

from main_service.modules.constants import (
    CHARGE_LVL_1_STR,
    CHARGE_LVL_1_5_STR,
    CHARGE_LVL_2_STR,
    CHARGE_LVL_PRO_POWER_STR,
    celcius_2_fahrenheit,
    fahrenheit_2_celcius
)

from  common_libs.models.common import RVEvents, EventValues

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


#TODO Move this into the BM component
INIT_SCRIPT = {
    # Should a real script go here for init
    'bms': [
        # Set to 1300 watts charge level
        'cansend canb0s0 18EF4644#5501024692040000',
    ]
}

shutdown_script = {}

# BMS inverter FR min is 9.0.02 for load adjustment
# Charge level will remain the same regardless of load


INVERTER_CONTINUOUS_MAX = 2400
DEFAULT_INVERTER_ID = 1

CHARGE_LVL_INITIAL = 1300           # Watts
# Latest Pro Power change as per Neng 2022/12/15
CHARGE_LVL_PRO_POWER = 1900         # Watts
CHARGE_LVL_L1_5 = 2650              # Watts
CHARGE_LVL_L2 = 5350                # Watts
VEHICLE_SOC_PRO_POWER_CUTOFF = 33   # %
# Reduced timer to 30 seconds
LVL_DETECT_PROTECTION_TIMER = 30    # Seconds

SOC_RANGE_LOW = 10      # Do not increase charge level when below this
# Update HIGH range due to unnecessarily preventing lvl2 charging to work
# TODO Fix with Lithionics and possibly use Voltage
SOC_RANGE_HIGH = 97     # Possibly reduce charge lvl when above this

L2_LOW = 179
L2_HIGH = 250

L1_LOW = 105
L1_HIGH = 130

# These are very specific circuits on the EV
AVC_CIRCUIT = 35
PRO_POWER_CIRCUIT = 0x0d
# WHY is it 4?
# UI agnostic to HW circuit, but why 4 ?
SHORE_POWER_ID = 1

PRO_POWER_ID = 2

BATTERY_ID = 1

SOLAR_SOURCE_ID = 4

# TODO: Clarify threshold if any
SOLAR_ACTIVE_THRESHOLD = 20     # Watts

DATA_INVALID = 'Data Invalid'


# TODO: Modify this to read from file on start
CONFIG_DEFAULTS = {
    'battery__1__soc': None,
    'battery__1__soh': None,
    'battery__1__capacity_remaining': None,
    'battery__1__voltage': None,
    'battery__1__current': None,
    'battery__1__charging': None,
    'battery___1__remaining_runtime_minutes': None,
    #'bms__1__charge_lvl': 0,
    #'bms__1__temp': None,
    'is_charging': None,
    'solar_active': None,

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
}

# SOURCE Mapping
SOURCE_MAPPING = {
    1: {
        'type': 'SOURCE_EV_SHORE',
        'controls': {
            'setChargeLevel': 'int'
        }
    },
    2: {
        'type': 'SOURCE_PRO_POWER',
        'controls': {
            'onOff': 'int'
        }
    },
    4: {
        'type': 'SIMPLE_INPUT_SOLAR'
    }
}

# AVC Circuit


#CZone instance IDs for NMEA2K fluid level
# TODO: Replace this with voltage calculation
AC_CURRENT_SENSOR_ID = 14
AC_CHARGER_SENSOR_ID = 15
AC_MAX_AMPS = 50

# Controls the charge levels supported by Lithionics chargers
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


def calculate_days(minutes):
    '''Calculate the days and hours remaining for an amounf of minutes.'''

    if minutes == 0:
        is_charging = None
    elif minutes < 0:
        # Negative means charging as per CAN message implementation below
        is_charging = True
    elif minutes > 0:
        is_charging = False

    minutes = abs(minutes)
    days = int(minutes / (24 * 60))
    remaining_minutes = minutes - (days * (24 * 60))
    hours = int(remaining_minutes / 60)
    remaining_minutes = remaining_minutes - (hours * 60)

    result = days * 24 * 60 + hours * 60 + remaining_minutes

    if result != minutes:
        raise ValueError('Mismatch in minutes')

    return {
        'days': days,
        'hours': hours,
        'minutes': remaining_minutes,
        'original_minutes': minutes,
        'isCharging': is_charging
    }


class EnergyControl(EnergyControlBaseClass):
    def __init__(self, config={}, init_script={}):
        # Given by base class
        # .state / .savedState / .config
        EnergyControlBaseClass.__init__(self, config=config, components={})
        # Initialize state
        # TODO: Should that be in the base class if it is that simple ?
        for key, value in config.items():
            self.state[key] = value

        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')

        self.init_script = init_script
        self.run_init_script()

    def run_init_script(self):
        for key, value in self.init_script.items():
            # Iterate over list of commands
            prefix_log(wgo_logger, __name__, f'Initializing: {key}')
            for cmd in value:
                result = subprocess.run(cmd, shell=True)
                if result != 0:
                    prefix_log(wgo_logger, __name__, f'cmd: {cmd} failed', lvl='error')

    # TODO: Check if load shedding is specific to the model or could run eventually in base class
    # For now leave it here and make it model specific
    # TODO: Where do we store the info on which circuits are sheddable and their order
    def _run_load_shedding(self, inverter_id=1):
        if self.state.get('load_shedding_enabled') == 0:
            self.HAL.climate.handler.set_heater_lock(0)
            return

        # current_load = self.state.get(f'ei{inverter_id}']['current_load')
        current_load = self.get_inverter_load(inverter_id)
        inverter_max = self.get_inverter_continuous_max(inverter_id)

        print('Current Load', current_load, 'Inverter Max', inverter_max)

        # Check If we are in overload
        if current_load > inverter_max:
            self.state[f'ei{inverter_id}']['overld'] = True
            in_overload = True
            if self.state.get(f'ei{inverter_id}')['overload_timer'] is None:
                self.state[f'ei{inverter_id}']['overload_timer'] = time.time()
        else:
            self.state[f'ei{inverter_id}']['overld'] = False
            self.state[f'ei{inverter_id}']['overload_timer'] = None
            in_overload = False
            self.HAL.climate.handler.set_heater_lock(0)

        INITIAL_SHED_TIMER = 5          # Seconds
        SECOND_STAGE_TIMER = 30         # Seconds

        if in_overload is True:
            if time.time() - self.state.get(f'ei{inverter_id}')['overload_timer'] > INITIAL_SHED_TIMER:
                # Water heater might actually not actively drawing power at this point
                try:
                    self.HAL.watersystems.handler.heater_switch(1, 0)
                except Exception as err:
                    #TODO: heater_swtich - not present in the system?
                    prefix_log(
                    wgo_logger,
                    f'{__name__}_run_load_shedding', err)
            if time.time() - self.state.get(f'ei{inverter_id}')['overload_timer'] > SECOND_STAGE_TIMER:
                self.HAL.climate.handler.set_heater_lock(1)
                self.HAL.climate.handler.auto_heater_off()

            self.event_logger.add_event(
                RVEvents.ENERGY_MANAGEMENT_SYSTEM_OVERLOAD_TRIGGER_CHANGE, #TODO Verify this the right current meter here
                1,  # TODO: Get from some place in config
                EventValues.TRUE
            )

        # TODO: Put int he right place when the proper decision is made to stop shedding
        self.event_logger.add_event(
            RVEvents.ENERGY_MANAGEMENT_SYSTEM_OVERLOAD_TRIGGER_CHANGE, #TODO Verify this the right current meter here
            1,  # TODO: Get from some place in config
            EventValues.FALSE
        )

        # If yes
            # Can we shed circuits ?
            # Yes
                # Select circuit next in line
                # Still in overload ?
                # Yes
                    #Repeat
                # No
                    #Exit
            # No
                # Show error to user
                # Warn


        # If no
            # Check if we did shed a circuit before
            # If yes
                # Check if we have the wiggle room
                # Yes
                    # Turn circuit back on
                # No
                    # Keep shed
            # No
                # exit


    def _run_charge_lvl_detection(self):
        '''This is an 800 EV specific algorithm.'''
        # TODO: Modify as per discussion with Lithionics
        # SOC should not be used
        # SoC due to its nature is not a good cutoff for charging
        # Voltage might be better

        if self.state.get('lvl2_algo_enabled') == 0:
            prefix_log(
                wgo_logger,
                f'{__name__}.LVL_DETECT',
                'Charge Lvl Detection Algorithm disabled for testing'
            )
            return

        # Check if SoC within protective range
        soc = self.get_state_of_charge(BATTERY_ID)
        if soc is None:
            prefix_log(
                wgo_logger,
                f'{__name__}.LVL_DETECT',
                'SoC unknown'
            )
            if self.state.get('shore__1__lvl') != CHARGE_LVL_1_STR:
                self.set_charger_lvl(CHARGE_LVL_INITIAL)
                self.state['shore__1__lvl'] = CHARGE_LVL_1_STR
        else:
            # TODO: Remove this block, do not use SoC
            # if soc < SOC_RANGE_LOW or soc > SOC_RANGE_HIGH:
            if soc < SOC_RANGE_LOW:
                prefix_log(
                    wgo_logger,
                    f'{__name__}.LVL_DETECT',
                    f'SoC {soc} is outside protective range, charge level reduced'
                )
                if self.state['shore__1__lvl'] == CHARGE_LVL_1_STR:
                    # Do nothing
                    pass
                else:
                    self.set_charger_lvl(CHARGE_LVL_INITIAL)
                    self.state['shore__1__lvl'] = CHARGE_LVL_1_STR
                return

        # Check global

        previous_avc_state = self.state.get('previous_avc_state')
        # TODO: Do proper mapping of power sources
        avc_state = self.power_source_active(SHORE_POWER_ID)
        # prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'AVC State {avc_state}')

        # Check when the last AVC change was
        # If < protective time, do not go up to lvl1
        # > protective time, verify current, calculate

        if avc_state != previous_avc_state:
            # Update last AVC change
            self.state['last_avc_change'] = time.time()
            self.state['previous_avc_state'] = avc_state
            self.state['last_valid_range_time'] = None
            self.state['shore__1__lock'] = False
            # Set lvl to be safe
            prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'AVC State Change: {previous_avc_state} {avc_state}')
            self.set_charger_lvl(CHARGE_LVL_INITIAL)
            self.state['shore__1__lvl'] = CHARGE_LVL_1_STR
            prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'SET CHARGE LVL to: {CHARGE_LVL_INITIAL}')

            # TODO: Bring back event
            # self.event_logger.add_event(
            #     RVEvents.ENERGY_SHORE_DETECTED,
            #     SHORE_POWER_ID,
            #     avc_state
            # )
        else:
            # No state change
            # Check if timer elapsed without change
            last_change = self.state.get('last_avc_change')
            if last_change is None:
                self.state['last_avc_change'] = time.time()
                prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'There is no known previous AVC state timer, setting now and exiting')
                return

            time_since_last_update = time.time() - last_change
            if time_since_last_update < LVL_DETECT_PROTECTION_TIMER:
                # We need to wait
                return

            prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Wait period passed')

            # This code shall only run if the above conditions of time since last change are matched
            prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Checking desired LVL')
            ac_current = self.get_charger_input()
            prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Shore meter value: {ac_current}')

            if avc_state == 0:
                prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Shore not connected')
                # Shore not connected
                if ac_current.get('current') > 0:
                    # TODO: Refactor this repeated check into a function
                    prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Detecting current without shore power, Pro-Power input?')
                    if self.state.get('shore__1__lvl') != CHARGE_LVL_PRO_POWER_STR:
                        self.set_charger_lvl(CHARGE_LVL_PRO_POWER)
                        self.state['shore__1__lvl'] = CHARGE_LVL_PRO_POWER_STR

                # Yes
                    # Check charge level set
                # No
                    # Revert to default charging level
            elif avc_state == 1:
                prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Shore connected')
                # Is Pro Power on
                # if True:
                #     # Yes
                #     # Blip off
                #     prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Blip Pro Power Off')
                #     self.HAL.electrical.handler.dc_switch(PRO_POWER_CIRCUIT, 1, 100)
                # else:
                #     # No
                #     # OK
                #     pass

                # Check if in feasible ranges
                current_voltage = ac_current.get('voltage')
                if ac_current.get('watts') == CHARGE_LVL_L2:
                    pass

                if current_voltage > L2_LOW and current_voltage < L2_HIGH:
                    # LEVEL 2
                    # Start new timer
                    last_valid_value_time = self.state.get('last_valid_range_time')
                    if last_valid_value_time is None:
                        self.state['last_valid_range_time'] = time.time()
                        prefix_log(
                            wgo_logger,
                            __name__ + '.LVL_DETECT',
                            f'Protection in valid range not set'
                        )
                        return
                    else:
                        valid_range_timer = time.time() - last_valid_value_time
                        if valid_range_timer > LVL_DETECT_PROTECTION_TIMER:
                            # Check if we are locked or not
                            if self.state.get('shore__1__lock') is True:
                                prefix_log(
                                    wgo_logger,
                                    __name__ + '.LVL_DETECT',
                                    f'LVL LOCK engaged, cannot switch until AVC toggled'
                                )
                                return
                            else:
                                # We can set the lvl
                                prefix_log(
                                    wgo_logger,
                                    __name__ + '.LVL_DETECT',
                                    f'LVL2 detected'
                                )
                                if self.state.get('shore__1__lvl') != CHARGE_LVL_2_STR:
                                    self.set_charger_lvl(CHARGE_LVL_L2)
                                    self.state['shore__1__lvl'] = CHARGE_LVL_2_STR
                                    self.state['shore__1__lock'] = True
                                else:
                                    prefix_log(
                                        wgo_logger,
                                        __name__ + '.LVL_DETECT',
                                        f'LVL2 already set, ignoring'
                                    )
                        else:
                            # Do nothing
                            prefix_log(
                                wgo_logger,
                                __name__ + '.LVL_DETECT',
                                f'Protection in valid range not expired: {valid_range_timer}'
                            )
                            return

                elif current_voltage > L1_LOW and current_voltage < L1_HIGH:
                    # Level 1
                    # Start new time
                    last_valid_value_time = self.state.get('last_valid_range_time')
                    if last_valid_value_time is None:
                        self.state['last_valid_range_time'] = time.time()
                        prefix_log(
                            wgo_logger,
                            __name__ + '.LVL_DETECT',
                            f'Protection in valid range not set'
                        )
                        return
                    else:
                        valid_range_timer = time.time() - last_valid_value_time
                        if valid_range_timer > LVL_DETECT_PROTECTION_TIMER:
                            # We can set the lvl
                            if self.state.get('shore__1__lock') is True:
                                prefix_log(
                                    wgo_logger,
                                    __name__ + '.LVL_DETECT',
                                    f'LVL Lockout engaged, cannot set level until AVC switch'
                                )
                            else:
                                prefix_log(
                                    wgo_logger,
                                    __name__ + '.LVL_DETECT',
                                    f'LVL1 detected'
                                )
                                self.set_charger_lvl(CHARGE_LVL_INITIAL)
                                self.state['shore__1__lvl'] = CHARGE_LVL_1_STR
                                self.state['shore__1__lock'] = True
                                prefix_log(
                                    wgo_logger,
                                    __name__ + '.LVL_DETECT',
                                    f'LVL1 SET and LOCK engaged'
                                )
                            # Set flag to allow changing to L1.5
                        else:
                            # Do nothing
                            prefix_log(
                                wgo_logger,
                                __name__ + '.LVL_DETECT',
                                f'Protection in valid range not expired: {valid_range_timer}'
                            )
                            return
                else:
                    # Reset
                    self.state['last_valid_range_time'] = None

            else:
                prefix_log(wgo_logger, __name__ + '.LVL_DETECT', f'Unknown AVC state')
                self.set_charger_lvl(CHARGE_LVL_INITIAL)
                self.state['shore__1__lvl'] = CHARGE_LVL_1_STR

        # Check Pro power enabled
        # YES

        # Check if shore 1 current is 0
        # YES
            # Turn to default charge lvl
        # No
            # Check current charge lvl
            # If charge level default
            # Yes
                # Is current LVL indicative (charge lvl / current > 190 V)
                # Yes
                    # Increase charge lvl
                # No
                    # Remain on default
            # No
                # Do nothing


    def update_can_state(self, msg_name, can_msg):
        '''Receive updates to energy modules.

        BMS
        AVC2 / VSIM inputs'''

        updated = False
        state = None


        if msg_name == 'dc_source_status_1':
            instance = can_msg.get('DC_Instance', 1)

            voltage = can_msg.get('DC_Voltage')
            current = can_msg.get('DC_Current')

            if voltage is not None and voltage != DATA_INVALID:
                voltage = float(voltage)

            if current is not None and current != DATA_INVALID:
                current = float(current)

            self.state[f'battery__1__voltage'] = voltage
            self.state[f'battery__1__current'] = current

            state = {
                'voltage': self.state[f'battery__1__voltage'],
                'current': self.state[f'battery__1__current']
            }

            updated = True
        elif msg_name == 'dc_source_status_2':
            self.state['battery__1__soc'] = float(can_msg.get('State_Of_Charge'))
            time_remaining = int(can_msg.get('Time_Remaining'))
            if time_remaining == 65535:
                self.state['battery__1__remaining_runtime_minutes'] = None
            else:
                if can_msg.get('Time_Remaining_Interpretation') != 'Time to Empty':
                    # Turn negative as time to full charge
                    time_remaining *= -1

            self.state['battery__1__remaining_runtime_minutes'] = time_remaining

            bms_temp = float(can_msg.get('Source_Temperature'))
            # BMS temp comes as C
            self.state['bms__1__temp'] = bms_temp

            state = self.state['battery__1__soc']
            updated = True

            self.event_logger.add_event(
                RVEvents.LITHIUM_ION_BATTERY_STATE_OF_CHARGE_CHANGE,
                1,  # Report instance '1' for the platform
                self.state['battery__1__soc']
            )

        elif msg_name == 'fluid_level':
            # AC Current Sensor or Charge Level
            instance = int(can_msg.get('Instance'))
            if instance == AC_CURRENT_SENSOR_ID:
                load_value = float(can_msg.get('Fluid_Level'))
                # Reading is in percent of total, total is in 'Tank_Capacity' but hardcoded here as we set 500 gallons = 50 Amps
                self.state['ei1']['current_load'] = AC_MAX_AMPS * load_value / 100
                updated = True
                self.event_logger.add_event(
                    RVEvents.INVERTER_CHARGER_CURRENT_METER_AFTER_INVERTER_CHANGE, #TODO Verify this the right current meter here
                    1,  # Report instance '1' for the platform  AC_CURRENT_SENSOR_ID,
                    self.state['ei1']['current_load']
                )
                self._run_load_shedding()
            elif instance == AC_CHARGER_SENSOR_ID:
                ac_current_value = float(can_msg.get('Fluid_Level'))
                self.state['shore__1__current_amps'] = AC_MAX_AMPS * ac_current_value / 100
                updated = True
                self.event_logger.add_event(
                    RVEvents.ENERGY_MANAGEMENT_AC_CURRENT_METER_CHANGE, #TODO Verify this the right current meter here
                    1,  # Report instance '1' for the platform  AC_CHARGER_SENSOR_ID,
                    self.state['shore__1__current_amps']
                )
                self._run_charge_lvl_detection()

        elif msg_name == 'battery_status':
            # F214
            instance = int(can_msg.get('Instance'))
            # if instance == 5:
            #     # Not being used
            #     # Mastervolt Shunt, measures solar input
            #     self.state[f'solar__{instance}__input_voltage'] = can_msg.get('Battery_Voltage')
            #     self.state[f'solar__{instance}__input_current'] = can_msg.get('Battery_Current')
            #     update = True
            # TODO: Why 4 here ? No particular reason ?!
            if instance == 4:
                #######################################
                # Shunt input for Solar
                #######################################
                # CZone Shunt, using a calculation until CZone can support
                # TODO: Add link to Wiki article explaining the issue
                self.state[f'solar__{instance}__input_voltage'] = self.state.get('battery__1__voltage', SOLAR_DEFAULT_VOLTAGE)
                measured_current = float(can_msg.get('Battery_Current'))
                # TODO: Check how to handle negative
                print('Measured Current', measured_current)
                actual_current = (measured_current - SOLAR_SHUNT_OFFSET) / SOLAR_SHUNT_FACTOR
                print('Actual Solar Current', actual_current)
                if actual_current < 0.0:
                    actual_current *= -1
                    print('Actual Solar Current', actual_current)

                self.state[f'solar__{instance}__input_current'] = actual_current
                self.event_logger.add_event(
                    RVEvents.SOLAR_CHARGER_SOLAR_SHUNT_DC_CURRENT_CHANGE,
                    1,  # Report instance '1' for the platform  instance,
                    actual_current
                )
            elif instance == 10:
                # Test AC current meter
                measured_current = float(can_msg.get('Battery_Current', 0))
                measured_voltage = float(can_msg.get('Battery_Voltage', 0))
                print('AC Meter Voltage', measured_voltage)
                print('AC Meter Current', measured_current)
                print('Current: ', measured_voltage * 10 )
                print('Wattage: ', measured_voltage * 10 * 120)

        return updated, state

    def is_power_incoming(self):
        '''Checks the given systems, if power is flowing in.'''
        # Check solar value positive
        power_incoming = 0
        solar_input = self.get_solar_input(solar_id=4)
        if solar_input.get('active') is True:
            power_incoming = 1

        shore_power = self.power_source_active(SHORE_POWER_ID)
        if shore_power == 1:
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
            avc_state = self.HAL.electrical.handler.get_state('dc', AVC_CIRCUIT)
            # prefix_log(wgo_logger, f'{__name__}.AVC_CIRCUIT', f'{avc_state} / {self.HAL.electrical.handler.state}')
            # Flip state for AVC
            # TODO: Manage in electrical handler
            if avc_state.get('onOff') == 1:
                source_state = 0
            elif avc_state.get('onOff') == 0:
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
        minutes_remaining = self.state.get(f'battery__{battery_id}__remaining_runtime_minutes')
        if minutes_remaining is None:
            return None

        return calculate_days(minutes_remaining)

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
                bms_temp_out = celcius_2_fahrenheit(bms_temp)
            except TypeError:
                bms_temp_out = bms_temp
        else:
            bms_temp_out = bms_temp

        # is ths BMS temp or ba temp here?
        self.event_logger.add_event(
                    RVEvents.LITHIUM_ION_BATTERY_TEMPERATURE_CHANGE,
                    1,  # Report instance '1' for the platform
                    bms_temp # report battery temp to IOT in celcius
                )

        return {
            'isCharging': charging,
            'remainingRuntime': minutes,
            'stateOfCharge': self.get_state_of_charge(battery_id),
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

    def get_solar_input(self, solar_id=4):
        voltage = self.state.get(f'solar__{solar_id}__input_voltage')
        current = self.state.get(f'solar__{solar_id}__input_current')
        active = None
        if voltage is None or current is None:
            watts = None
        else:
            watts = int(voltage * current)
            if watts > SOLAR_ACTIVE_THRESHOLD:
                active = True
            else:
                active = False

        return {
            'voltage': voltage,
            'current': current,
            'watts': watts,
            'active': active
        }

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
        charge_lvl = self.state.get('bms__1__charge_lvl', 0)
        # Divide the charge limit by the measured current and get the voltage
        voltage = charge_lvl / current
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

        vehicle = self.get_vehicle_power_state(PRO_POWER_ID)
        sources.append(
            {
                'id': PRO_POWER_ID,
                'type': 'SOURCE_PRO_POWER',
                'name': 'Pro Power',
                'description': '',
                'state': vehicle
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
            if source_type == 'SOURCE_PRO_POWER':
                self.HAL.electrical.handler.dc_switch(PRO_POWER_CIRCUIT, new_state.get('onOff'), 100)
                self.event_logger.add_event(
                    RVEvents.PROPOWER_PRO_POWER_RELAY_CHANGE,
                    1,  # TODO: Get instance from some place in config
                    new_state.get('onOff')) # This should report 0 or 1
            elif source_type == 'SOURCE_EV_SHORE':
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


    def set_charger_lvl(self, charge_lvl, instance=1):
        '''Control how much charge the Lithionics BMS allows.'''
        # Check ranges
        if charge_lvl < MIN_CHARGE_LEVEL:
            raise ValueError(f'Cannot set charge level below {MIN_CHARGE_LEVEL}')

        if charge_lvl > MAX_CHARGE_LEVEL:
            raise ValueError(f'Cannot set charge level above {MAX_CHARGE_LEVEL}')

        bms_cmd = 70
        # Account for 10% loss/ wiggle room (switches on the DC side)
        charge_lvl_protected = int(charge_lvl * 0.9)

        try:
            charge_setting = byte_flip(charge_lvl_protected)
        except ValueError as err:
            prefix_log(wgo_logger, __name__, str(err), lvl='error')
            raise

        cmd = f'cansend canb0s0 18EF4644#55{instance:02X}02{bms_cmd:02X}{charge_setting:04X}0000'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        if result.returncode == 127:
            prefix_log(wgo_logger, __name__, 'Command cannot be executed', lvl='error')

        # TODO: Get this event into the enum
        # self.event_logger.add_event(
        #     RVEvents.ENERGY_CHARGE_LVL_CHANGE,
        #     instance,
        #     charge_lvl
        # )

        self.state[f'bms__{instance}__charge_lvl'] = charge_lvl
        return self.get_state(f'bms__{instance}__charge_lvl')

    def get_power_inputs(self):
        return {
            'solar': {},
            'shore': {},
            'vehicle': {
                'type': 'PROPOWER',
                'state': {
                    'onOff': self.HAL.electrical.handler.get_state('dc', PRO_POWER_CIRCUIT).get('onOff', 0),
                    'active': 0,
                    'power': 0
                }
            }
        }

    def set_inverter_state(self, state, inverter_id=1):
        '''Change the state of the inverter.'''
        inverter_key = f'ei{inverter_id}'
        print('set_inverter_state', state)

        on_off = state.get('onOff', 0)
        if on_off == 0:
            output = 0
        else:
            output = 100

        set_response = self.HAL.electrical.handler.dc_switch(0x15, on_off, output)
        self.state[inverter_key] = state

        result = deepcopy(self.state.get(inverter_key, {}))
        if 'msg' in set_response:
            result['msg'] = set_response['msg']

        return result


handler = EnergyControl(config=CONFIG_DEFAULTS, init_script=INIT_SCRIPT)


if __name__ == '__main__':
    print(handler)
    print(handler.config)
