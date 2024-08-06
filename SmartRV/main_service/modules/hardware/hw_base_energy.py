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

from main_service.modules.constants import (
    CHARGE_LVL_1_STR,
    CHARGE_LVL_1_5_STR,
    CHARGE_LVL_2_STR,
    CHARGE_LVL_PRO_POWER_STR,
    _celcius_2_fahrenheit,
    # fahrenheit_2_celcius
)

from common_libs.models.common import RVEvents, EventValues
from main_service.components.energy import (
    BatteryManagement, BatteryMgmtState,
    GeneratorPropane, GeneratorDiesel, GeneratorState,
)

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

INIT_SCRIPT = {
    # Should a real script go here for init
    # 'bms': [
    #     # Set to 1300 watts charge level
    #     ('can', '18EF4644', '5501024692040000'),
    # ]
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
LVL_DETECT_PROTECTION_TIMER = 60    # Seconds

SOC_RANGE_LOW = 10      # Do not increase charge level when below this
SOC_RANGE_HIGH = 90     # Possibly reduce charge lvl when above this

L2_LOW = 179
L2_HIGH = 250

L1_LOW = 105
L1_HIGH = 130


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

INVERTER_BASE_VOLTAGE = 120     # Volts


# TODO: Modify this to read from file on start
CONFIG_DEFAULTS = {
    'battery__1__soc': None,
    'battery__1__soh': None,
    'battery__1__capacity_remaining': None,
    'battery__1__voltage': None,
    'battery__1__current': None,
    'battery__1__charging': None,
    'battery___1__remaining_runtime_minutes': None,
    'bms__1__charge_lvl': 0,
    'bms__1__temp': None,
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


CODE_TO_ATTR = {
    'es': 'energy_source',
    'ei': 'inverter',
    'bm': 'battery_management',
    'ft': 'fuel_tank',
    'ec': 'energy_consumer',
    'ge': 'generator',
    'ba': 'battery',
}


class EnergyControlBaseClass(HALBaseClass):
    state = {}

    def __init__(self, config={}, components=[], app=None):
        # Given by base class
        # .state / .savedState / .config
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        for key, value in config.items():
            self.state[key] = value
        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')
        self.configBaseKey = 'energy'
        self.init_components(components, self.configBaseKey)

        if hasattr(self, 'load_shedding'):
            LOAD_SHED_MAIN_ID = 0
            load_shed = self.load_shedding[LOAD_SHED_MAIN_ID]
            init_result = load_shed.initialize_component()
            if init_result is None:
                print('[ENERGY][LOADSHEDDING] initialize component not implemented')

    def run_init_script(self):
        ''' Required in Child class'''
        # TODO: Check if this should be standardized and only overridden if something special needs to happen

        # This could run during init in super

        raise ValueError('HW Energy is not configured correctly - using base class!')

    def init_energysystems(self, mapping, tanks):
        # initialize systems
        # TODO: Make a generic init function - copied from watersystems
        # TODO: and it looks like it might need to move to run_init_script
        # Tanks
        for tank_id in tanks:
            tank_key = f'ft{tank_id}'
            tank = mapping.get(tank_key, {})
            # tank['system_key'] = tank_key
            self.state[tank_key] = tank.get('state', {})
            self.meta[tank_key] = tank

    # ######## New State handlers ############
    def set_energy_source_state(self, instance: int, state: dict):
        '''Update the state of an energy source if supported.'''
        # TODO: Handle KeyErrors properly
        energy_source = self.energy_source[instance]
        # Check if source can be controlled (use onOff as an attribute being present)
        if hasattr(energy_source.state, 'onOff'):
            # TODO: Perform action if applicable, currently only ProPower has this
            pass
        else:
            # Fail out properly ?
            raise ValueError(f'Energy Source: {instance} does not support setting state onOff')

        return energy_source.state

    def get_tank_state(self, tank_id: int):
        tank_key = f'ft{tank_id}'
        # TODO: Add defaults for states to be returned and maybe emit an event for tracking
        # That a given state was not initialized
        return self.state.get(tank_key)


    def get_floor_plan(self):
        '''Return the floorplan set in the HALL layer'''
        return self.HAL.floorPlan

    ############################################################################

    # TODO: The below methods might actuall work from the base class when looking up current data by key in the state
    def get_power_inputs(self) -> list:
        '''Returns the list of power inputs available in their categories.'''
        raise NotImplementedError('get_power_inputs needs to be overwritten in the implementing class, hitting base class')

    def get_batteries(self) -> list:
        '''Returns the list of batteries and their current details.'''
        raise NotImplementedError('get_batteries needs to be overwritten in the implementing class, hitting base class')

    def get_power_consumers(self) -> list:
        '''Returns the list of power consumers and their current details.'''
        raise NotImplementedError('get_batteries needs to be overwritten in the implementing class, hitting base class')

    ############################################################################

    def calculate_days(self, minutes):
        '''Calculate the days and hours remaining for an amount of minutes.'''

        if minutes == 0:
            self.state['is_charging'] = None
        elif minutes < 0:
            # Negative means charging as per CAN message implementation below
            self.state['is_charging'] = True
        elif minutes > 0:
            self.state['is_charging'] = False

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
            'isCharging': self.state['is_charging']
        }


    # set_state
    # get_state
    def run_load_shedding(self, inverter_id=1):
        '''Overload function in the EnergyControl Class . Required in loadshed class'''
        raise NotImplementedError('run_load_shedding needs to be overwritten in the top class, hitting base class')

        # if self.state.get('load_shedding_enabled') == 0:
        #     self.HAL.climate.handler.set_heater_lock(0)
        #     return

        # # current_load = self.state.get(f'ei{inverter_id}']['current_load')
        # current_load = self.get_inverter_load(inverter_id)
        # inverter_max = self.get_inverter_continuous_max(inverter_id)

        # # Check If we are in overload
        # if current_load > inverter_max:
        #     self.state[f'ei{inverter_id}']['overld'] = True
        #     in_overload = True
        #     if self.state.get(f'ei{inverter_id}')['overload_timer'] is None:
        #         self.state[f'ei{inverter_id}']['overload_timer'] = time.time()
        # else:
        #     self.state[f'ei{inverter_id}']['overld'] = False
        #     self.state[f'ei{inverter_id}']['overload_timer'] = None
        #     in_overload = False
        #     self.HAL.climate.handler.set_heater_lock(0)

        # INITIAL_SHED_TIMER = 5          # Seconds
        # SECOND_STAGE_TIMER = 30         # Seconds

        # if in_overload is True:
        #     if time.time() - self.state.get(f'ei{inverter_id}')['overload_timer'] > INITIAL_SHED_TIMER:
        #         # Water heater might actually not actively drawing power at this point
        #         self.HAL.watersystems.handler.heater_control(1, 0)
        #     if time.time() - self.state.get(f'ei{inverter_id}')['overload_timer'] > SECOND_STAGE_TIMER:
        #         self.HAL.climate.handler.set_heater_lock(1)
        #         self.HAL.climate.handler.auto_heater_off()

        #     self.event_logger.add_event(
        #         RVEvents.ENERGY_MANAGEMENT_SYSTEM_OVERLOAD_TRIGGER_CHANGE, #TODO Verify this the right current meter here
        #         1,  # TODO: Get from some place in config
        #         EventValues.TRUE
        #     )

        # # TODO: Put int he right place when the proper decision is made to stop shedding
        # self.event_logger.add_event(
        #     RVEvents.ENERGY_MANAGEMENT_SYSTEM_OVERLOAD_TRIGGER_CHANGE, #TODO Verify this the right current meter here
        #     1,  # TODO: Get from some place in config
        #     EventValues.FALSE
        # )

        # # If yes
        #     # Can we shed circuits ?
        #     # Yes
        #         # Select circuit next in line
        #         # Still in overload ?
        #         # Yes
        #             #Repeat
        #         # No
        #             #Exit
        #     # No
        #         # Show error to user
        #         # Warn


        # # If no
        #     # Check if we did shed a circuit before
        #     # If yes
        #         # Check if we have the wiggle room
        #         # Yes
        #             # Turn circuit back on
        #         # No
        #             # Keep shed
        #     # No
        #         # exit


    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''Receive updates to energy modules. Required in Child class'''
        '''Receive updates to energy modules.
        BMS
        AVC2 / VSIM inputs'''

        updated = False
        state = None

        # if msg_name == 'dc_source_status_1':
        #     instance = can_msg.get('DC_Instance', 1)

        #     voltage = can_msg.get('DC_Voltage')
        #     current = can_msg.get('DC_Current')

        #     if voltage is not None:
        #         try:
        #             voltage = float(voltage)
        #         except ValueError as err:
        #             voltage = None

        #     if current is not None:
        #         try:
        #             current = float(current)
        #         except ValueError as err:
        #             current = None

        #     self.state[f'battery__{instance}__voltage'] = voltage
        #     self.state[f'battery__{instance}__current'] = current

        #     state = {
        #         'voltage': self.state[f'battery__{instance}__voltage'],
        #         'current': self.state[f'battery__{instance}__current']
        #     }

        #     updated = True

        # if msg_name == 'dc_source_status_2':
        #     instance = can_msg.get('DC_Instance', 1)
        #     if instance == 'Main House Battery Bank':
        #         instance = 1    # This is the actual value on the bus
        #     elif instance == 1:
        #         pass
        #     elif instance == 'Data Invalid':
        #         # Should not happen, but who knows.
        #         raise ValueError(f'Instance reported as invalid: {can_msg}')
        #     else:
        #         return updated, state

        #     self.state[f'battery__{instance}__soc'] = float(can_msg.get('State_Of_Charge'))

        #     time_remaining = int(can_msg.get('Time_Remaining'))
        #     if time_remaining == 65535:
        #         self.state[f'battery___{instance}__remaining_runtime_minutes'] = None
        #     else:
        #         if can_msg.get('Time_Remaining_Interpretation') != 'Time to Empty':
        #             # Turn negative as time to full charge
        #             time_remaining *= -1

        #     self.state[f'battery___{instance}__remaining_runtime_minutes'] = time_remaining

        #     battery_temp = float(can_msg.get('Source_Temperature'))
        #     # BMS temp comes as C
        #     self.state[f'bms__{instance}__temp'] = battery_temp


        #     self.event_logger.add_event(
        #         RVEvents.LITHIUM_ION_BATTERY_STATE_OF_CHARGE_CHANGE,
        #         instance,  # Report instance '1' for the platform  ,
        #         self.state[f'battery__{instance}__soc']
        #     )

        #     self.event_logger.add_event(
        #         RVEvents.LITHIUM_ION_BATTERY_TEMPERATURE_CHANGE,
        #         instance,  # Report instance '1' for the platform  AC_CURRENT_SENSOR_ID,
        #         self.state[f'battery__{instance}__temp']
        #     )

        #     state = self.state
        #     updated = True

        # elif msg_name == 'dc_source_status_3':
        #     instance = can_msg.get('DC_Instance', 1)
        #     self.state[f'battery__{instance}__soh'] = float(can_msg.get('State_Of_Health'))
        #     self.state[f'battery__{instance}__dschCap'] = int(can_msg.get('Capacity_Remaining'))
        #     self.event_logger.add_event(
        #         RVEvents.LITHIUM_ION_BATTERY_STATE_OF_HEALTH_CHANGE,
        #         instance,  # Report instance '1' for the platform  AC_CURRENT_SENSOR_ID,
        #         self.state[f'battery__{instance}__soh']
        #     )
        #     self.event_logger.add_event(
        #         RVEvents.LITHIUM_ION_BATTERY_REMAINING_DISCHARGE_CAPACITY_CHANGE,
        #         instance,  # Report instance '1' for the platform  AC_CURRENT_SENSOR_ID,
        #         self.state[f'battery__{instance}__dschCap']
        #     )
        #     updated = True

        if msg_name == 'battery_status':
            # F214
            instance = int(can_msg.get('Instance'))
            if instance == 1:
                print(f"Fresh Tank Volts {can_msg.get('Battery_Voltage')}")
            elif instance == 2:
                print(f"Gray Tank Volts {can_msg.get('Battery_Voltage')}")
            elif instance == 3:
                print(f"Black Tank Volts {can_msg.get('Battery_Voltage')}")
            elif instance == 4:
                print(f"LP Sensor Reading {can_msg.get('Battery_Voltage')}")
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
                print('@@@@ Solar Measured Current', measured_current)
                actual_current = (measured_current - SOLAR_SHUNT_OFFSET) / SOLAR_SHUNT_FACTOR
                print('@@@@ Actual Solar Current', actual_current)
                if actual_current < 0.0:
                    actual_current *= -1
                    print('@@@@ Actual Solar Current', actual_current)

                self.state[f'solar__{instance}__input_current'] = actual_current
                self.event_logger.add_event(
                    RVEvents.SOLAR_CHARGER_SHUNT_DC_CURRENT_CHANGE,
                    1,  # Report instance '1' for the platform  instance,
                    actual_current
                )

        return state

    def is_power_incoming(self):
        '''Checks the given systems, if power is flowing in. Required in Child class'''
        raise ValueError('HW Energy is not configured correctly - using base class!')

    def power_source_active(self, source_id):
        '''Required in Child class'''
        raise ValueError('HW Energy is not configured correctly - using base class!')

    def get_state_of_charge(self, battery_id):
        '''Get state of charge for the given battery.'''
        return self.state.get(f'battery__{battery_id}__soc')

    def get_remaining_runtime(self, battery_id):
        bms = self.battery_management[battery_id]
        if bms.state.tte == EventValues.TIME_TO_EMPTY:
            minutes_remaining = bms.state.minsTillEmpty
        elif bms.state.tte == EventValues.TIME_TO_FULL:
            minutes_remaining = bms.state.minsTillFull
        else:
            print('get_remaining_runtime is ELSE !', bms.state.tte)

        print('Remaining Battery runtime', minutes_remaining, 'baseclass')
        if minutes_remaining is None:
            return None

        return self.calculate_days(minutes_remaining)

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

        # IS this ba temp or bm temp or both?
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
        '''Get the current load in watts the inverter outputs.

        This supports simple inverters as well as the ones that provide the voltage.
        if voltage is unknown (due to not being measured) we use a static value.'''

        voltage = self.state.get(f'ei{inverter_id}')['voltage']
        # TODO: Make sure updates are reported as current not load
        amps = self.state.get(f'ei{inverter_id}')['current']

        if amps is None:
            return None

        if voltage is None:
            voltage = INVERTER_BASE_VOLTAGE

        return int(voltage * amps)

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

    def set_inverter_state(self, state, inverter_id=1):
        '''Change the state of the inverter.'''
        # TODO: Add some abstraction here maybe ? The ability to work with different inverters and just needing a config file
        # e.g. type simpleInverter needs a circuit ID
        # RV-C might need a feature list
        # Anything else might need something else

        raise NotImplementedError('set_inverter_state needs to be implemented in model specific class for now')

    def get_inverter_state(self, inverter_id=1):
        inverter_key = f'ei{inverter_id}'
        return self.state.get(inverter_key)


    def get_inverter_state(self, zone_id=1, inverter_id=1):
        # Get Circuit state, is it on/off
        # get
        return {
            'onOff': self.state[f'ei{inverter_id}']['onOff']
        }

    def get_solar_input(self, solar_id=4):
        voltage = self.state.get(f'solar__{solar_id}__input_voltage')
        current = self.state.get(f'solar__{solar_id}__input_current')
        watts = None # fill in below if other values are present
        #active = None
        if voltage is None or current is None:
            self.state['solar_active'] = False
            prefix_log(wgo_logger, __name__, f'Solar Voltage: {voltage}, Solar Current: {current}')
        else:
            watts = int(voltage * current)
            prefix_log(wgo_logger, __name__, f'Solar Watts: {watts}')
            if watts > SOLAR_ACTIVE_THRESHOLD:
                self.state['solar_active'] = True
            else:
                self.state['solar_active'] = False

        return {
            'voltage': voltage,
            'current': current,
            'watts': watts,
            'active': self.state['solar_active']
        }

    def get_total_input(self):
        # Get solar
        solar = self.get_solar_input()
        charger = self.get_charger_input()

        solar_watts = solar.get('watts')
        if solar_watts is None:
            solar_watts = 0

        # TODO: Check if that is desirable
        # Report -10% on charger as this is the power arriving at the BMS
        # total = solar.get('watts') + (charger.get('watts') * 0.9)
        total = solar_watts + (charger.get('watts'))

        return {
            'watts': total,
            'kilowatts': round(total / 1000, 1)
        }

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
        '''Get full list of energy sources. Can be added to in the Descendants'''
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
        '''Required in Child class'''
        raise ValueError('HW Energy is not configured correctly - using base class!')

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

        cmd = f'55{instance:02X}02{bms_cmd:02X}{charge_setting:04X}0000'
        self.HAL.app.can_sender.can_send_raw(
            '18EF4644',
            cmd
        )

        self.state[f'bms__{instance}__charge_lvl'] = charge_lvl
        return self.get_state(f'bms__{instance}__charge_lvl')

    def get_consumers(self):
        count = 0
        systems = []

        # Check Water Pumps / Water Heater / water heater
        # TODO: Retrieve from proper HW list with names
        for key in ('wp1', 'wp2', 'wh1'):
            if self.HAL.watersystems.handler.get_state(key).get('onOff', 0) == 1:
                count += 1
                systems.append(key)

        # Check Heating / Cooling
        current_hvac_mode = self.HAL.climate.handler.thermostat[1].state.mode
        if current_hvac_mode == EventValues.HEAT:
            count += 1
            systems.append('Heater')
        elif current_hvac_mode == EventValues.COOL:
            count += 1
            systems.append('AC')
        elif current_hvac_mode != EventValues.STANDBY:
            count += 1
            systems.append('FAN')

        # Check Other Circuits
        # Lighting Controllers
        # Fridge
        # Lighting Zone 9 / 10
        # Tech Cab Fan
        # Other

        return count, systems

    def set_battery_management_state(self, instance: int, in_state: BatteryMgmtState):
        '''Do some work to setup the desired state'''
        # TODO: Make sure nothing gets set that cannot be set

        # Check if there is any setting available for the management system
        # Apply setting
        print('IN state', in_state)
        in_state = BatteryMgmtState(**in_state)
        battery_mgr = self.battery_management[instance]
        battery_mgr.state = in_state

        return battery_mgr.state

    def set_generator_controls(self, instance: int):
        '''Set the generator state.'''
        # TODO:  We could adapt this this for the ONAN and RVMP
        # Get Generator instance and component
        # Peform the action to put the generator into this already approved new state

        generator = self.generator[instance]
        # Move to componet perform transition and then call this action
        # Let component perform transition
        # generator.set_generator_state(in_state)
        # With returned state perform actions towards the real HW
        # Check the modes and associated actions required
        # TODO: Get this from some better place
        # LP Start = 27
        # LP Stop/Prime = 28
        lp_start_id = 27  # 0x1B
        lp_stop_id = 28  # 0x1C
        start_onoff = None
        stop_onoff = None
        switch_id = '13'

        if generator.state.mode == EventValues.OFF:
            # Check that it is running
            # Will be None if nothing is updating it
            if self.HAL.electrical.handler.get_switch_state(switch_id).get('onOff') == EventValues.ON:
                # Special handling here - if we are asking the generator to turn off -
                #  THEN let the incoming RV1 actually turn it off - since we know it is running
                generator.internal_state.mode = EventValues.RUN
                start_onoff = 1
                generator.internal_state.lastStartTime = time.time()
                generator.super().save_db_state()

        elif generator.state.mode == EventValues.RUN or \
             generator.state.mode == EventValues.STARTING:
            # Check that it is not running
            if self.HAL.electrical.handler.get_switch_state(switch_id).get('onOff') == EventValues.OFF:
                # Set start circuit to ON - it is a toggle for OFF or ON
                start_onoff = 1

        else:
            print('Unhandled state', generator.state.mode)

        # New gen will be on it's a toggle
        if start_onoff == 1:
            output = 100
        else:
            output = 0

        if start_onoff is not None:
            # NOTE: Changed H-BRIDGE to move BACKWARD instead of FORWARD
            # Pending decision of the team 2024/02/02 DOM
            direction = 'FORWARD'
            result = self.HAL.electrical.handler.dc_switch(
                lp_start_id,
                start_onoff,
                output=output,
                direction=direction
            )
        # should not be needed for two line gen

        # if stop_onoff == 1:
        #     output = 100
        # else:
        #     output = 0

        # result = self.HAL.electrical.handler.dc_switch(
        #     lp_stop_id,
        #     stop_onoff,
        #     output=output,
        #     direction=direction
        # )

        return generator.state


# handler = EnergyControlBaseClass(
#     config=CONFIG_DEFAULTS,
#     components=read_default_config_json_file().get("energy_components", {}),)


if __name__ == '__main__':
    print(handler)
    print(handler.config)
