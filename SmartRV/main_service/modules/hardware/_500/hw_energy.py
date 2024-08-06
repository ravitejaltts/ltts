# What controls does the water system need
# Who is providing this control

import logging
import time

from pydantic import ValidationError

from common_libs.models.common import EventValues, RVEvents
from main_service.modules.constants import (
    _celcius_2_fahrenheit,
)
from main_service.modules.data_helper import byte_flip
from main_service.modules.hardware.hw_base_energy import EnergyControlBaseClass
from main_service.modules.logger import prefix_log

wgo_logger = logging.getLogger('main_service')


# TODO: Do we need this concept at all now (yes ?) ?
INIT_SCRIPT = {}
shutdown_script = {}


# BMS
# MAIN_BATTERY_INSTANCE = 'Main House Battery Bank'
MAIN_BATTERY_INSTANCE = 1

# TODO: Get this from the attributes in the inverter
INVERTER_CONTINUOUS_MAX = 2000      # Xantrex 2000 TODO: Get this from attributes
DEFAULT_INVERTER_ID = 1

# Charge level not controlled Not required
# CHARGE_LVL_INITIAL = 1300           # Watts
LVL_DETECT_PROTECTION_TIMER = 60    # Seconds

SOC_RANGE_LOW = 10      # Do not increase charge level when below this
SOC_RANGE_HIGH = 90     # Possibly reduce charge lvl when above this

SHORE_POWER_ID = 1

ALTERNATOR_POWER_ID = 2

BATTERY_ID = 1

SOLAR_SOURCE_ID = 1

# TODO: Clarify threshold if any
SOLAR_ACTIVE_THRESHOLD = 1     # Watts

# This might be variable or configurable
# TODO: Get procedure how to set this
XANTREX_ID = 0x41

CAN_TIME_TO_EMPTY = 'Time to Empty'

# SOURCE Mapping
SOURCE_MAPPING = {
    1: {
        'type': 'SOURCE_EV_SHORE',
        'controls': {
            'setChargeLevel': 'int'
        }
    },
    2: {
        'type': 'SOURCE_ALTERNATOR_POWER',
        'controls': {
            'onOff': 'int'
        }
    },
    4: {
        'type': 'SIMPLE_INPUT_SOLAR'
    }
}

mapping = {
    # Propane Fuel Tank
    'ft1': {
        'id': 1,
        'tankType': 'PROPANE',
        'name': 'Propane',
        'subType': 'SIMPLE_TANK',
        'type': 'PROPANE',
        'lvl': None,
        'state': {'lvl': None},
        'cap': 20,
        'description': 'Propane fuel tank',
        'information': None,
        'uiclass': 'PropaneTankLevel'
    }
}
# Inverter output
AC_CURRENT_SENSOR_ID = 0xff     # TODO: Get the instance for DC meter for the voltage reading
AC_MAX_AMPS = 100

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

DC_METER_CHASSIS_BATTERY_INSTANCE = 1
DC_METER_CZONE_MAIN_POWER_STUD = 252        # All DC output on the RV1
TANK_SENSORS = [101, 102, 103]

AC_POWER_INSTANCE = 1   # TODO: Move this detection to component init
DC_POWER_INSTANCE = 2   # EnergyConsumer instance

# TODO: Read this on init and not everytime
# TODO: Get the solar input that matches from a mapping or type in attributes
SOLAR_SOURCE = 1
SHORE_SOURCE = 2
GENERATOR_SOURCE = 4  # Changed from GENERATOR_INSTANCE - ui_generator.py ask BAW

class EnergyControl(EnergyControlBaseClass):
    state = {}
    # generator = None

    def __init__(self, config={}, components=[], app=None):
        # Given by base class
        # .state / .savedState / .config
        EnergyControlBaseClass.__init__(self, config=config, components=components, app=None)
        for key, value in config.items():
            self.state[key] = value

        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')

        # self.init_energysystems(mapping, tanks)

    # def setHAL(self, hal_obj):
    #     self.HAL = hal_obj
    #     # 33F GENERATOR - 3,200 WATT, ONAN, DIESEL
    #     # 52G GENERATOR - 3,600 WATT, ONAN MICROQUIET, LP
    #     # if "52G" in self.HAL.hal_options:
    #     #     self.generator[1] = cummins_propane()
    #     # else:
    #     #     self.generator[1] = cummins_diesel()

    def run_init_script(self):
        ''' Required in Child class'''
        raise ValueError('HW Energy is not configured correctly - using base class!')

    # def get_floor_plan(self):
    #     '''Return the floorplan set in the HALL layer'''
    #     return self.HAL.floorPlan

    # def calculate_days(self, minutes):
    #     '''Calculate the days and hours remaining for an amount of minutes.'''

    #     if minutes == 0:
    #         self.state['is_charging'] = None
    #     elif minutes < 0:
    #         # Negative means charging as per CAN message implementation below
    #         self.state['is_charging'] = True
    #     elif minutes > 0:
    #         self.state['is_charging'] = False

    #     minutes = abs(minutes)
    #     days = int(minutes / (24 * 60))
    #     remaining_minutes = minutes - (days * (24 * 60))
    #     hours = int(remaining_minutes / 60)
    #     remaining_minutes = remaining_minutes - (hours * 60)

    #     result = days * 24 * 60 + hours * 60 + remaining_minutes

    #     if result != minutes:
    #         raise ValueError('Mismatch in minutes')

    #     return {
    #         'days': days,
    #         'hours': hours,
    #         'minutes': remaining_minutes,
    #         'original_minutes': minutes,
    #         'isCharging': self.state['is_charging']
    #     }

    # set_state
    # get_state
    def run_load_shedding(self, inverter_id=1):
        '''Layer to find the componentrs used and their relationship for shedding.'''
        MAIN_SHED_ID = 0
        if self.state.get('load_shedding_enabled') == 0:
            # Remove all locks as they apply
            # TODO: Figure out how locks are stored and discovered here
            # self.HAL.climate.handler.set_heater_lock(0)
            #
            return "Load shedding disabled"

        inverter = self.inverter.get(inverter_id)
        if inverter is None:
            print('[LOADSHED][INVERTER] Inverter not found', inverter_id)
            return "Inverter not found"

        # Run component based algorithm, not HW layer
        if hasattr(self, 'load_shedding'):
            self.load_shedding[MAIN_SHED_ID].run_load_shedding(
                inverter.state.load,
                inverter.state.maxLoad)

    def update_energy_consumers(self):
        '''Iterate over energy consumer components.'''
        # Check if we have an inverter
        if not hasattr(self, 'energy_consumer'):
            return

        # Update AC
        if AC_POWER_INSTANCE in self.energy_consumer:
            ac_consumer = self.energy_consumer[AC_POWER_INSTANCE]
            if hasattr(self, 'inverter'):
                inverter = self.inverter.get(AC_POWER_INSTANCE)
                if inverter is not None:
                    ac_total_watts = self.inverter.get(AC_POWER_INSTANCE).state.load
                    if ac_total_watts is None:
                        print('[ENERGY][INVERTER] No load available to update AC consumer')
                        return
                    ac_consumer.state.watts = ac_total_watts
                    ac_consumer.state.current = self.inverter.get(AC_POWER_INSTANCE).state.rmsCurrent
                    ac_consumer.state.active = EventValues.TRUE if ac_total_watts > 0 else EventValues.FALSE

        # NOTE: Future:
        # Deduct all known or estimated consumers from the total

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''Receive updates to energy modules. Required in Child class'''
        '''Receive updates to energy modules.
        BMS
        AVC2 / VSIM inputs'''

        updated = False
        state = None

        # 1FFFD
        if msg_name == 'dc_source_status_1':
            instance = int(can_msg.get('Instance', 1))
            # TODO: Check DBC file for the DC_Instance and this new way of handling
            if instance == MAIN_BATTERY_INSTANCE:
                print('---------------')
                print('We hit the RVC CLEAN PGN')
                print(can_msg)
                print('---------------')
                instance = 1    # This is the actual value on the bus as well

            elif instance == 'Main House Battery Bank - Lithionics':
                print('---------------')
                print('HW ENERGY: We hit the specific PGN not the cleaned one')
                print(can_msg)
                print('---------------')
                instance = 1    # This is the actual value on the bus as well

            elif instance == 'Data Invalid':
                # Should not happen, but who knows.
                raise ValueError(f'Instance reported as invalid: {can_msg}')

            else:
                return state

            validate_state = self.battery_management[instance].state.dict()

            voltage = can_msg.get('DC_Voltage')
            current = can_msg.get('DC_Current')

            # print(voltage, current)

            if voltage is not None:
                try:
                    voltage = float(voltage)
                except ValueError:
                    voltage = None

            if current is not None:
                try:
                    current = float(current)
                except ValueError as err:
                    current = None

            validate_state['vltg'] = voltage
            validate_state['dcCur'] = current

            bms = self.battery_management[instance]
            try:
                bms.state.validate(validate_state)
            except ValidationError as err:
                print(err)
                return bms.state

            bms.state.vltg = voltage
            bms.state.dcCur = current

            if voltage is not None and current is not None:
                bms.state.dcPwr = int(voltage * current)
            else:
                bms.state.dcPwr = None

            bms.update_state()

            updated = True
            state = bms.state

            if hasattr(self.HAL.features.handler, 'pet_monitoring'):
                self.HAL.features.handler.run_pet_monitoring_algorithm()

        # 1FFFC
        elif msg_name == 'dc_source_status_2':
            print('*' * 40, 'DC SOURCE STATUS 2', can_msg)
            print('In high level')

            instance = can_msg.get('DC_Instance')
            if instance == 'Main House Battery Bank':
                instance = 1    # This is the actual value on the bus
            elif instance == '1':
                instance = 1
            elif instance == 'Data Invalid':
                # Should not happen, but who knows.
                raise ValueError(f'Instance reported as invalid: {can_msg}')
            else:
                print('Found no instance known', instance)
                return state

            bms = self.battery_management[instance]

            validate_state = bms.state.dict()
            validate_state['soc'] = float(can_msg.get('State_Of_Charge'))

            time_remaining = int(can_msg.get('Time_Remaining'))
            if time_remaining == 65535:
                validate_state['minsTillFull'] = None
                validate_state['minsTillEmpty'] = None
            else:
                if can_msg.get('Time_Remaining_Interpretation') != CAN_TIME_TO_EMPTY:
                    validate_state['tte'] = EventValues.TIME_TO_FULL
                    validate_state['minsTillFull'] = time_remaining
                    validate_state['minsTillEmpty'] = None
                    # Turn negative as time to full charge
                    time_remaining *= -1
                else:
                    # Time Till Empty
                    validate_state['tte'] = EventValues.TIME_TO_EMPTY
                    validate_state['minsTillFull'] = None
                    validate_state['minsTillEmpty'] = time_remaining

            battery_temp = float(can_msg.get('Source_Temperature'))
            # BMS temp comes as C
            # self.state[f'battery__{instance}__temp'] = battery_temp
            validate_state['temp'] = battery_temp

            try:
                bms.state.validate(validate_state)
            except ValidationError as err:
                print(err)
                return bms.state

            bms.state.soc = validate_state['soc']
            bms.state.tte = validate_state['tte']
            bms.state.minsTillFull = validate_state['minsTillFull']
            bms.state.minsTillEmpty = validate_state['minsTillEmpty']
            bms.state.temp = validate_state['temp']

            # state = self.state[f'battery__{instance}__soc']
            updated = True
            bms.update_state()
            state = bms.state

            if hasattr(self.HAL.features.handler, 'pet_monitoring'):
                self.HAL.features.handler.run_pet_monitoring_algorithm()

            print('Returning', state)

        elif msg_name == 'dc_source_status_3':
            # TODO: Fix the use of proper states
            # print('[ENERGY] DC_SOURCE_STATUS_3', can_msg)
            instance = int(can_msg.get('DC_Instance', 1))

            bms = self.battery_management[instance]

            self.state[f'battery__{instance}__soh'] = float(can_msg.get('State_Of_Health'))
            self.state[f'battery__{instance}__dschCap'] = int(can_msg.get('Capacity_Remaining'))

            self.event_logger.add_event(
                RVEvents.LITHIUM_ION_BATTERY_STATE_OF_HEALTH_CHANGE,
                instance,  # Report instance '1' for the platform  AC_CURRENT_SENSOR_ID,
                self.state[f'battery__{instance}__soh']
            )
            self.event_logger.add_event(
                RVEvents.LITHIUM_ION_BATTERY_REMAINING_DISCHARGE_CAPACITY_CHANGE,
                instance,  # Report instance '1' for the platform  AC_CURRENT_SENSOR_ID,
                self.state[f'battery__{instance}__dschCap']
            )

            bms.update_state()

            updated = True
            state = bms.state

        elif msg_name == 'battery_status':
            # F214 NMEA2K
            instance = int(can_msg.get('Instance', 1))
            # # if instance == 1:
            try:
                voltage = float(can_msg.get('Battery_Voltage'))
            except ValueError as err:
                voltage = None

            # TODO: This is not correct, the voltage for BMS comes from DC_SOURCE messages, this is
            # for CZone DC Meter for the vehicle battery
            # self.battery_management[instance].state.vltg = voltage
            # TODO: Move the vehicle chassis battery voltage to a component
            if instance == DC_METER_CHASSIS_BATTERY_INSTANCE:
                self.state[f'vehicle__battery__{instance}__voltage'] = voltage
                vehicle = self.HAL.vehicle.handler.vehicle[instance]
                vehicle.state.batVltg = voltage

                vehicle.update_state()
                state = vehicle.state

            elif instance == DC_METER_CZONE_MAIN_POWER_STUD:
                # {'Instance': '252', 'Battery_Voltage': '13.13', 'Battery_Current': '-0.2', 'Sequence_Id': '0', 'msg': 'Timestamp: 1708498737.525601    ID: 19f21497    X Rx                DL:  8    fc 21 05 fe ff ff ff 00     Channel: canb0s0', 'msg_name': 'Battery_Status', 'source_address': '97', 'instance_key': '19F21497__0__252'}
                print('[ENERGY][STUD] DC output', can_msg)
                # This holds all DC power usage through the CZone RV1
                dc_consumer = self.energy_consumer.get(DC_POWER_INSTANCE)
                if dc_consumer is not None:
                    try:
                        current = float(can_msg.get('Battery_Current'))
                        voltage = float(can_msg.get('Battery_Voltage'))
                    except ValueError as e:
                        print('[ENERGY] Invalid data in battery status', can_msg, e)
                        current = None
                        voltage = None

                    if current is not None and voltage is not None:
                        # Rounding to no digit as we use watts, might change on kW
                        watts = int(round(abs(current * voltage), 0))
                        # Check if it is active when using more than 0 watts after rounding
                        active = EventValues.TRUE if watts > 0 else EventValues.FALSE
                    else:
                        # Else set wattage/active to None to handle that differently from 0 and False
                        watts = None
                        active = None

                    dc_consumer.state.watts = watts
                    dc_consumer.state.current = current
                    dc_consumer.state.active = active
                    dc_consumer.state.shed = False

                    print('[ENERGY][CONSUMER] State', instance, dc_consumer.state)
                    state = dc_consumer.state
            elif instance in TANK_SENSORS:
                print('[TANK LVL]', can_msg)
                state = self.HAL.watersystems.handler.update_can_state(
                    msg_name,
                    can_msg
                )
            else:
                print('[ENERGY][DC_METER] Unknown DC Meter', can_msg)

        elif msg_name == 'solar_controller_status':
            # 1FEB3
            print('>' * 80, '\nGot solar status')
            print(can_msg)
            # instance = 1    # TODO: Check if instance can be accepted from the CAN bus
            instance = int(can_msg.get('Instance', 1))

            voltage = can_msg.get('Charge_Voltage')
            current = can_msg.get('Charge_Current')

            if voltage == 'Data Invalid':
                measured_voltage = 0.0
            else:
                measured_voltage = float(voltage)

            if current == 'Data Invalid':
                measured_current = 0.0
            else:
                measured_current = float(current)

            print('Measured Solar', measured_current, measured_voltage)
            # TODO: Check how to handle negative
            print('@@@@ Solar Measured Current', measured_current)

            solar_source = self.energy_source[SOLAR_SOURCE]

            # This requieres the above checks to be rock solid
            solar_source.state.vltg = measured_voltage
            solar_source.state.cur = measured_current
            solar_source.state.watts = measured_current * measured_voltage
            solar_source.set_state(
                solar_source.state.dict()
            )

            self.state[f'solar__{instance}__input_current'] = measured_current
            self.state[f'solar__{instance}__input_voltage'] = measured_voltage

            update = True
            state = solar_source.state
            solar_source.update_state()

        elif msg_name == 'inverter_ac_status_1':
            # This is the measurement on the AC output side, all consumers the inverter provides with AC power
            # CM_ "1FFD7";
            # BO_ 2181027584 INVERTER_AC_STATUS_1: 8 Vector__XXX
            #     SG_ Instance:
            #         0|8@1+  (1,0)   [0|255]     ""  Vector__XXX
            #     SG_ RMS_Voltage:
            #         8|16@1+  (0.05,0)   [0|65535]     "V"  Vector__XXX
            #     SG_ RMS_Current:
            #         24|16@1+    (0.05,-1600)   [-32000|33535]   "A"     Vector__XXX
            #     SG_ Frequency:
            #         40|16@1+    (0.0078125,0)   [0|65535]   "Hz"     Vector__XXX

            instance = int(can_msg.get('Instance', 1))
            if instance == XANTREX_ID:
                # print('Received Instance', instance, 'setting to 1 for testing')
                # TODO: Figure out how to control the instance on the xantrex inverter
                instance = 1

            inverter = self.inverter[instance]
            if inverter is None:
                print('[ENERGY][update_can_state] Inverter not found', instance)
                return
            _ = inverter.update_can_state(msg_name, can_msg)

            print('LOADSHED Results', self.run_load_shedding())

            # NOTE: We need to update the AC energy consumer
            self.update_energy_consumers()

            updated = True
            state = inverter.state

        elif msg_name == 'charger_ac_status_1':
            # 1FFCA
            # RV-C Charger status
            # BO_ 2181024256 CHARGER_AC_STATUS_1: 8 Vector__XXX
            # SG_ Instance:
            #     0|8@1+  (1,0)   [0|255]     ""  Vector__XXX
            # SG_ RMS_Voltage:
            #     8|16@1+  (0.05,0)   [0|65535]     "V"  Vector__XXX
            # SG_ RMS_Current:
            #     24|16@1+    (0.05,-1600)   [-32000|33535]   "A"     Vector__XXX
            # SG_ Frequency:
            #     40|16@1+    (0.0078125,0)   [0|65535]   "Hz"     Vector__XXX

            instance = int(can_msg.get('Instance', 1))

            voltage = can_msg.get('RMS_Voltage')
            if voltage == 'Data Invalid':
                print('[ENERGY][CHARGER] Voltage Data Invalid, setting to None')
                voltage = None
            else:
                try:
                    voltage = float(voltage)
                except ValueError as err:
                    print('[ENERGY][CHARGER] Voltage conversion to float failed, setting to None', err)
                    voltage = None

            current = can_msg.get('RMS_Current')
            if current == 'Data Invalid':
                print(
                    '[ENERGY][CHARGER] current Data Invalid, setting to None'
                )
                current = None
            else:
                try:
                    current = float(current)
                except ValueError as err:
                    print('[ENERGY][CHARGER] current conversion to float failed, setting to None', err)
                    current = None

            frequency = can_msg.get('Frequency')
            if frequency == 'Data Invalid':
                print('[ENERGY][CHARGER] frequency Data Invalid, setting to None')
                frequency = None
            else:
                try:
                    frequency = float(frequency)
                except ValueError as err:
                    frequency = None
                    print('[ENERGY][CHARGER] frequency conversion to float failed, setting to None', err)

            self.state[f'charger__{instance}__voltage'] = voltage
            self.state[f'charger__{instance}__current'] = current
            self.state[f'charger__{instance}__frequency'] = frequency

            source = None  # Fill in the source below
            # Check if we are on generator or shore
            # Solar handled in a different message - NOT charger_ac_status_1
            # TODO: Check can we dynamically load the Instance at initialization??
            if hasattr(self, 'generator'):
                if self.generator[1].state.mode == EventValues.RUN:
                    # We apply the data to the generator
                    self.energy_source[SHORE_SOURCE].state.vltg = None
                    self.energy_source[SHORE_SOURCE].state.cur = None
                    self.energy_source[SHORE_SOURCE].state.watts = None
                    self.energy_source[SHORE_SOURCE].state.freq = None
                    self.energy_source[SHORE_SOURCE].state.active = EventValues.FALSE
                    # self.energy_source[SHORE_SOURCE].set_state_defaults()
                    self.energy_source[SHORE_SOURCE].update_state()
                    source = self.energy_source[GENERATOR_SOURCE]
                    print('[ENERGY][GENERATOR][UICHECK] Updating Generator source')
                else:
                    self.energy_source[GENERATOR_SOURCE].state.vltg = None
                    self.energy_source[GENERATOR_SOURCE].state.cur = None
                    self.energy_source[GENERATOR_SOURCE].state.watts = None
                    self.energy_source[GENERATOR_SOURCE].state.freq = None
                    self.energy_source[GENERATOR_SOURCE].state.active = EventValues.FALSE
                    # self.energy_source[SHORE_SOURCE].set_state_defaults()
                    self.energy_source[GENERATOR_SOURCE].update_state()
                    source = self.energy_source[SHORE_SOURCE]
            else:
                source = self.energy_source[SHORE_SOURCE]

            # NOTE: Might need refinement, as this could overwrite the active state set above
            source.state.vltg = voltage
            source.state.cur = current
            source.state.freq = frequency

            if voltage is not None and current is not None:
                source.state.watts = int(voltage * current)
                if source.state.watts > 0:
                    source.state.active = EventValues.TRUE
                else:
                    source.state.active = EventValues.FALSE
            else:
                source.state.watts = None
                source.state.active = EventValues.FALSE

            source.update_state()
            updated = True
            state = source.state

        elif msg_name == 'prop_module_status_1':
            print('PROP_MODULE_STATUS_1', can_msg)
            instance = int(can_msg.get('Instance'))
            battery = self.battery[instance]

            try:
                temp = float(can_msg.get('Cells_Temp'))
            except ValueError as err:
                print(err)
                temp = None

            battery.state.temp = temp

            self.event_logger.add_event(
                RVEvents.BATTERY_TEMP_CHANGE,
                instance,
                temp
            )

            battery.update_state()

        elif msg_name == 'prop_bms_status_6':
            # Get the revision and serial number
            instance = int(can_msg.get('Instance'))
            major = int(can_msg.get('Firmware_Major'))
            minor = int(can_msg.get('Firmware_Minor'))
            serial = int(can_msg.get('Serial'))

            if hasattr(self, 'battery_management'):
                bms = self.battery_management.get(instance)
                if bms is not None:
                    bms.attributes['runtime_meta'] = {
                        'firmware': f'{major}.{minor}',
                        'serial': serial,
                        'last_updated': time.time()
                    }

        elif msg_name == 'prop_bms_status_1':
            print("[ENERGY] PROP BMS STATUS", can_msg)
            '''
            BO_ 2566881280 PROP_BMS_STATUS_1: 8 Vector__XXX
            BO_ 2566881350 PROP_BMS_STATUS_1: 8 Vector__XXX
                SG_ DC_Instance : 0|8@1+  (1,0)   [0|255]     "NA"  Vector__XXX
                SG_ Number_Modules_Sensors : 8|8@1+  (1,0)   [0|255]     "#"  Vector__XXX
                SG_ BMS_Internal_Temp : 16|8@1+  (1,-40)   [0|255]     "deg C"  Vector__XXX
                SG_ Max_Recorded_Temp : 24|8@1+  (1,-40)   [0|255]     "deg C"  Vector__XXX
                SG_ Min_Recorded_Temp : 32|8@1+  (1,-40)   [0|255]     "deg C"  Vector__XXX
                SG_ BMS_Status_Code_1 : 40|8@1+  (1,0)   [0|255]     "BitMask"  Vector__XXX
                SG_ BMS_Status_Code_2 : 48|8@1+  (1,0)   [0|255]     "BitMask"  Vector__XXX
                SG_ BMS_Status_Code_3 : 56|8@1+  (1,0)   [0|255]     "BitMask"  Vector__XXX
            '''

            # Get BMS Status Code Flags
            byte_0_flags = int(can_msg.get('BMS_Status_Code_1'))
            high_voltage_state = (byte_0_flags & 0b00000001) > 0
            _ = (byte_0_flags & 0b00000010) > 0
            neverdie_reserve_state = (byte_0_flags & 0b00000100) > 0
            optoloop_open = (byte_0_flags & 0b00001000) > 0
            _ = (byte_0_flags & 0b00010000) > 0
            _ = (byte_0_flags & 0b00100000) > 0
            _ = (byte_0_flags & 0b01000000) > 0
            power_off_state = (byte_0_flags & 0b10000000) > 0

            if power_off_state is True:
                # TODO: !!!!!!!!
                # Shut off all write activities ASAP, battery is going down
                print('[ENERGY] Shutdown imminent !')

            if optoloop_open is True:
                print('[ENERGY] BMS OptoLoop OPEN')

            if hasattr(self, 'battery_management'):
                bms = self.battery_management.get(instance)
                if bms is not None:
                    bms.state.temp = float(can_msg.get('BMS_Internal_Temp'))


        elif msg_name == 'inverter_status':
            '''INVERTER_STATUS(
                  Instance: 1,
                  Status: AC passthru,
                  Battery_Temperature_Sensor_Present: No battery temperature sensor in use,
                  Load_Sense_Enabled: Load sense disabled
              )
              53.030  INVERTER_STATUS(
                  Instance: 1,
                  Status: Invert,
                  Battery_Temperature_Sensor_Present: No battery temperature sensor in use,
                  Load_Sense_Enabled: Load sense disabled
              )
              230.024  INVERTER_STATUS(
                  Instance: 1,
                  Status: Disabled,
                  Battery_Temperature_Sensor_Present: No battery temperature sensor in use,
                  Load_Sense_Enabled: Load sense disabled
              )
            '''
            instance = int(can_msg.get('Instance', 1))
            inverter = self.inverter.get(instance)
            if inverter is None:
                return state

            status = can_msg.get('Status')
            if status == 'AC passthru':
                # not inverting, might need to apply a different max wattage
                # TODO: Figure out from Neng
                # Pass-thru also means the inverter portion is on
                inverter.state.onOff = EventValues.ON
            elif status == 'Invert':
                # We currently invert, the max wattage of the inverter applies to load shedding
                # Also set the inverter to on ?
                inverter.state.onOff = EventValues.ON
            elif status == 'Disabled':
                inverter.state.onOff = EventValues.OFF
                # TODO: Might still be passing through data, need to check

            updated = True
            state = inverter.state

        elif msg_name == 'charger_configuration_status':
            ''' SG_ Instance:        0|8@1+  (1,0)   [0|255]     ""  Vector__XXX
                SG_ Charging_Algorithm:        8|8@1+  (1,0)   [0|255]     ""  Vector__XXX
                SG_ Charger_Mode:        16|8@1+  (1,0)   [0|255]     ""  Vector__XXX
                SG_ Battery_Sensor_Present:        24|2@1+  (1,0)   [0|1]     ""  Vector__XXX
                SG_ Charger_Installation_Line:        26|2@1+  (1,0)   [0|1]     ""  Vector__XXX
                SG_ Battery_Type:        28|4@1+  (1,0)   [0|1]     ""  Vector__XXX
                SG_ Battery_Bank_Size:        32|16@1+  (1,0)   [0|65535]     "Ah"  Vector__XXX
                SG_ Maximum_Charge_Current:        48|16@1+  (0.05,-1600)   [-1600|65535]    "A"  Vector__XXX'''
            instance = int(can_msg.get('Instance', 1))
            inverter = self.inverter.get(instance)
            if inverter is None:
                return state

            # Check if battery type is as expected
            # TODO: Move to template attributes for comparison
            battery_type = can_msg.get('Battery_Type')
            if battery_type != '3':
                print('[ENERGY][INVERTER] Battery Type Check failed', battery_type, 'instead of 3')

            max_chrg_current = can_msg.get('Maximum_Charge_Current')
            if max_chrg_current != '100.0':
                print('[ENERGY][INVERTER] Charge Current Check failed', max_chrg_current, 'A instead of 100A')

            updated = True
            state = inverter.state

        elif msg_name == 'charger_configuration_status_2':
            '''
            SG_ Instance:        0|8@1+  (1,0)   [0|255]     ""  Vector__XXX
            SG_ Maximum_Charge_Current_As_Percent:        8|8@1+  (0.5,0)   [0|255]     "%"  Vector__XXX
            SG_ Charge_Rate_Limit_As_Percent_Of_Bank_Size:        16|8@1+  (0.5,0)   [0|255]     "%"  Vector__XXX
            SG_ Shore_Breaker_Size:        24|8@1+  (1,0)   [0|255]     "A"  Vector__XXX
            SG_ Default_Battery_Temperature:        32|8@1+  (1,-40)   [-40|215]     "deg C"  Vector__XXX
            SG_ Recharge_Voltage:        40|16@1+  (0.05,0)   [0|65535]    "V"  Vector__XXX'''

            instance = int(can_msg.get('Instance', 1))
            inverter = self.inverter.get(instance)
            if inverter is None:
                return state

            shore_breaker = can_msg.get('Shore_Breaker_Size')
            # TODO: Get the desired value from attributes or wherever
            if shore_breaker != '15':
                print('[ENERGY][INVERTER] Shore Breaker Check failed', shore_breaker, 'instead of ', '15')

            state = inverter.state

        return state

    def is_power_incoming(self):
        '''Checks the given systems, if power is flowing in.'''
        # Check solar
        # Check Shore
        # Check Alternator
        # If needed do delta calculation
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

    def power_source_active(self, source_id):
        '''Checks sources that are active.'''
        source_state = None
        return source_state

    # TODO: Why was this removed - if it is being called?
    def get_state_of_charge(self, battery_id):
        return self.state.get(f'battery__{battery_id}__soc')

    # def get_remaining_runtime(self, battery_id):
    #     minutes_remaining = self.state.get(f'battery__{battery_id}__remaining_runtime_minutes')
    #     if minutes_remaining is None:
    #         return None

    #     return self.calculate_days(minutes_remaining)

    # def get_battery_voltage(self, battery_id):
    #     return self.state.get(f'battery__{battery_id}__voltage')

    # def get_battery_current(self, battery_id):
    #     return self.state.get(f'battery__{battery_id}__current')

    # TODO: Why are we emitting events when we do a get ?
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
                bms_temp_out = _celcius_2_fahrenheit(bms_temp)
            except TypeError:
                bms_temp_out = bms_temp
        else:
            bms_temp_out = bms_temp

        # self.event_logger.add_event(
        #     RVEvents.LITHIUM_ION_BATTERY_TEMPERATURE_CHANGE,
        #     1,  # Report instance '1' for the platform
        #     bms_temp # report battery temp to IOT in celcius
        # )

        return {
            'isCharging': charging,
            'remainingRuntime': minutes,
            'stateOfCharge': self.get_state_of_charge(battery_id),
            'voltage': voltage,
            'current': current,
            'watts': watts,
            'bmsTemp': bms_temp_out
        }

    # def get_charger_voltage(self, charger_id):
    #     return self.state.get(f'charger__{charger_id}__voltage')

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

        for instance, consumer in self.energy_consumer.items():
            consumers.append(
                consumer
            )
        # DC Circuits on
        # DC Load per circuit
        #
        return consumers

    def get_inverter_load(self, inverter_id=1):
        # base_key = f'ei{inverter_id}'

        # return self.state.get(base_key + 'current_load')
        return  self.inverter[inverter_id].state.load


    def get_inverter_continuous_max(self, inverter_id):
        '''Get max continuous load.'''
        # TODO: Consider temperature
        # return self.state.get(f'ei{inverter_id}')['continuous_max_load']
        return  self.inverter[inverter_id].state.maxLoad


    def get_inverter_overld(self, inverter_id):
        current_load = self.get_inverter_load(inverter_id)

        try:
            in_overload = False
            if current_load and (current_load > self.get_inverter_continuous_max(inverter_id)):
                in_overload = True
        except Exception as err:
            print(f'current_load error {err}')

        state = {
            'overload': in_overload
        }
        return state

    # TODO: We can remove this function and possibly others - the base class implements the same code
    # def get_inverter_state(self, zone_id=1, inverter_id=1):
    #     # Get Circuit state, is it on/off
    #     # get
    #     return {
    #         'onOff': self.state.get(f'ei{inverter_id}']['onOff')
    #     }

    def set_inverter_state(self, instance, state):
        # TODO: The ID for sending to XANTREX is 1 but receiving is 0x41 ??? WTF
        # TODO: Handle downstream effects and report to user
        onOff = state.get('onOff')

        if onOff == EventValues.OFF:
            cmd = f'{instance:02X}FCFFFFFFFFFFFF'
        elif onOff == EventValues.ON:
            cmd = f'{instance:02X}FDFFFFFFFFFFFF'

        self.HAL.app.can_sender.can_send_raw(
            '19FFD344',
            cmd
        )

        self.inverter[instance].state.onOff = onOff

        # Emit state events
        self.inverter[instance].set_state(None)

        return self.inverter[instance].state

    def get_solar_input(self, solar_id=1):
        voltage = self.state.get(f'solar__{solar_id}__input_voltage')
        current = self.state.get(f'solar__{solar_id}__input_current')
        #active = None
        if voltage is None or current is None:
            watts = None
            # TODO: Fix instances in solar active
            self.state['solar_active'] = False
            #prefix_log(wgo_logger, __name__, f'Solar Voltage: {voltage}, Solar Current: {current}')
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
        '''Get full list of energy sources. Can be added to in the Descendants'''
        # Solar
        # Shore
        # Vehicle / Pro-Power
        # TODO: Is there a reason generator is not listed here? - Pro-Power is EV leftover?
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

        self.HAL.app.can_sender.can_send_raw(
            '18EF4644',
            f'55{instance:02X}02{bms_cmd:02X}{charge_setting:04X}0000'
        )

        # TODO: Get this event into the enum
        # self.event_logger.add_event(
        #     RVEvents.ENERGY_CHARGE_LVL_CHANGE,
        #     instance,
        #     charge_lvl
        # )

        self.state[f'bms__{instance}__charge_lvl'] = charge_lvl
        return self.get_state(f'bms__{instance}__charge_lvl')


    def get_consumers(self):
        count = 0
        systems = []

        # Check Water Pumps / Water Heater / water heater
        # TODO: Retrieve from proper HW list with names
        for key in ('wp1', 'wp2', 'wh1'):
            if self.HAL.watersystems.handler.get_state(key).get('onOff', 0) == 1:
                count +=1
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


    # def get_generator(self, instance=1):
    #     return self.state['generator']

    # TODO: FIND out if this is still needed???
    # def ctrl_generator(self, state: dict, id = 1):
    #     print(f'hw_energy generator change {state}')
    #     self.state['generator'] = self.generator.request_change(in_state=state)
    #     return self.state['generator']


    def get_power_inputs(self):
        '''Returns all power inputs known to the HW layer for consumption on API/UI.'''
        # TODO: Check if this can go to the base class or if this is OK for now
        # This ideally shoudl build itself based on the component on type etc.
        return {
            'solar': {},
            'shore': {},
            'vehicle': {
                'type': 'ALTERNATOR',
                'state': {
                    'onOff': 0,
                    'active': 0,
                    'power': 0
                }
            }
        }

    def update_generator_run(self, params):
        '''Update the state of the generator as per circuit input.'''
        # line_state = EventValues.OFF
        instance = params.get('instance', 1)
        generator = self.generator[instance]

        # TODO: Change templates to use 0/1 to align with EventValues
        generator.update_generator_run(params.get('active'))


module_init = (
    EnergyControl,
    'energy_mapping',
    'components'
)
