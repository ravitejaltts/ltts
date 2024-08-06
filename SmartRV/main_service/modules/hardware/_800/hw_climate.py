import logging
import subprocess
from typing import Union


wgo_logger = logging.getLogger('main_service')

if __name__ == '__main__':
    # adding to test this file as main
    import sys
    sys.path.append("main_service")
    sys.path.append(".")

from common_libs.models.common import EventValues, LogEvent, RVEvents

#from main_service.modules.storage_helper import read_default_config_json_file
from main_service.modules.constants import *
from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.logger import prefix_log

# from  common_libs.models.common import (
#      LogEvent,
#      RVEvents,
#      EventValues
# )


# 800 is using CZone to switch the heater on/off
# 800 is using CZone oto switch AC compressor on and AC fan lo/hi
try:
    from main_service.modules.hardware.czone.control_x_plus import CZone
except ModuleNotFoundError:
    from czone.control_x_plus import CZone


# try:
#     from main_service.modules.hardware.dometic import RoofFan
# except ModuleNotFoundError:
#     from dometic import RoofFan

THIS_SYSTEM = "CLIMATE"

AC_FAN_LOW = 16
AC_FAN_HIGH = 17
AC_COMPRESSOR = 34

CLIMATE_LOW_HIGH_THRESHOLD = 2  # Degrees

HEATER = 19

ROOF_FAN_CZONE_POWER = 9

# RV-C speed is in 0.5% increments, so 2 = 1%, the lowest speed supported
# By dometic
FAN_DEFAULT_SPEED = EventValues.OFF.value
FAN_DEFAULT_DIRECTION = EventValues.FAN_OUT.value
FAN_DEFAULT_SYSTEM_STATE = 0    # 0 = Off
FAN_HOOD_DEFAULT_OPEN = EventValues.OPEN.value
FAN_DEFAULT_STATE = {
    'onOff': FAN_DEFAULT_SYSTEM_STATE,
    'direction': FAN_DEFAULT_DIRECTION,
    'fanSpd': FAN_DEFAULT_SPEED,
    'hood': FAN_HOOD_DEFAULT_OPEN
}

RVC_FRIDGE_INSTANCE = 55
RVC_THERMISTOR_INSTANCE = 1
INSTANCE_TO_ZONE = {
    1: 1,       # Elwell System on 848R
    2: 1,
    4: 1,       # Thermistor on Dometic
    6: 6,       # Exterior
    55: 99,     # Fridge
    '?': 100   # Exterior
}
EXTERIOR_TEMP_ZONE = 6

CLIMATE_ZONES = [1,]

DATA_INVALID = 'Data invalid'

class QuickSettings(object):
    '''Helper for pydantic model inputs.

    Add attributes as needed'''
    def __init__(self):
        pass


czone = CZone(
    cfg={}
)

init_script = {
    # Should a real script go here for init
    # Set Roof Fan default
    # Set AC default mode (Auto ?)
}

shutdown_script = {}

# CONFIG_DEFAULTS -> Moved to file Climate_Defaults.json in the data dir
# Under tools use default helper to adjust the file as needed

class ClimateControl(HALBaseClass):
    def __init__(self, config={}, components=[]):
        # Given by base class
        # .state / .savedState / .config
        HALBaseClass.__init__(self, config=config)
        #self.event_logger = None
        self.configBaseKey = 'climate'

        for key, value in config.items():
            self.state[key] = value

    def run_init_script(self, script):
        for func, args in script.items():
            func(*args)

    # set_state
    def get_state(self):
        twin_state = {'th1': '800'}
        return twin_state
    # update_can_state

    def _check_temperature(self, temp_desired, temp_unit):
        if temp_unit == TEMP_UNIT_FAHRENHEIT:
            temp_desired = fahrenheit_2_celcius(temp_desired)

        # prefix_log(wgo_logger, f'{__name__} - [CLIMATE][TEMPCHECK]', f'{temp_desired} {temp_unit}')
        if temp_desired > self.config['max_temp_set'] or temp_desired < self.config['min_temp_set']:
            return True
        return False

    def _init_config(self):
        # Get climate settings
        for zone_id in CLIMATE_ZONES:
            base_key = f'{self.configBaseKey}.zone.{zone_id}'

            # Fans
            fan_speed_key = f'{base_key}.fan.1.fanSpd'
            fan_speed = self.HAL.app.get_config(fan_speed_key)

            if fan_speed is not None:
                settings = QuickSettings()
                settings.fan_speed = fan_speed.get('value')
                settings.compressor = None
                # TODO: Do we even need this or, shouldn't that be done the first time the Climate algo executed ?
                self.set_ac_setting(zone_id, settings)

            # Climate Mode
            climate_mode_key = f'{base_key}.climate_mode'
            climate_mode = self.HAL.app.get_config(climate_mode_key)
            if climate_mode is None:
                # TODO: Set defaults or just ignore ?
                pass
            else:
                try:
                    self.set_zone_ac_mode(zone_id, climate_mode.get('value'))
                except ValueError as err:
                    # Happens sometimes reading older values from a DB
                    self.set_zone_ac_mode(zone_id, '519')
                # Set Temps
                set_temp_cool = self.HAL.app.get_config(f'{base_key}_set_temperature_COOL')
                set_temp_heat = self.HAL.app.get_config(f'{base_key}_set_temperature_HEAT')
                if set_temp_cool is not None:
                    self.set_temperature(zone_id, set_temp_cool.get('value'), EventValues.COOL.name, temp_unit=TEMP_UNIT_CELCIUS)

                if set_temp_heat is not None:
                    self.set_temperature(zone_id, set_temp_heat.get('value'), EventValues.HEAT.name, temp_unit=TEMP_UNIT_CELCIUS)

            # Thermostat
            on_off_key = f'{base_key}.onOff'
            thermostat_onoff = self.HAL.app.get_config(on_off_key)
            if thermostat_onoff is not None:
                settings = QuickSettings()
                # Defaults to off for now
                settings.onOff = thermostat_onoff.get('value')
                # settings.onOff = 0
                self.set_zone(zone_id, settings)

    def get_zone(self, zone_id: int):
        '''Get the zones current state.'''
        return self.state.get(f'zone_{zone_id}__onOff')

    def set_zone(self, zone_id: int, control: dict):
        '''Set the zone control.
        Turning a Zone off will turn off the AC and heating elements.'''
        result = self.state[f'zone_{zone_id}__onOff'] = control.onOff

        self.HAL.app.save_config(
            f'climate.zone.{zone_id}.onOff',
            {'value': control.onOff}
        )

        return {
            'zone_id': zone_id,
            'onOff': control.onOff
        }

    def set_zone_ac_mode(self, zone_id: int, mode: str):
        '''Sets the given zone to mode AUTO / HEAT / COOL / FAN_ONLY.'''
        if zone_id not in CLIMATE_ZONES:
            raise ValueError(f'Climate zone: {zone_id} unknown')

        ac_key = f'zone_{zone_id}_climate_mode'

        previous_mode = self.state.get(ac_key)
        if previous_mode is None:
            raise KeyError(f'Cannot read climate_mode for {ac_key}')
        #else:
        #    previous_mode = previous_mode[:]

        self.state[ac_key] =  EventValues[mode]

        # TODO: Fix below code, currently fails on first attempt to switch to auto mode from heat/cool
        if mode == EventValues.AUTO.name:
            # prefix_log(wgo_logger, '>>>>>>>>>>>>>>>>>', f'{previous_mode} - {mode}')
            # Check from which mode we come to avoid temperature clashes
            # Heat might be higher than cooling and vice versa
            current_heat_temp = self.thermostat[zone_id].state.setTempHeat.get_temperature()
            current_cool_temp = self.thermostat[zone_id].state.setTempCool.get_temperature()

            if previous_mode == EventValues.HEAT:
                # Update Cool to adhere to the limits
                if (current_heat_temp + TEMP_PROTECTIVE_RANGE) > current_cool_temp:
                    # Need to update
                    # prefix_log(wgo_logger, '>>>>>>>>>>>>>>>>>', f'TEMP HEAT: {current_heat_temp}')
                    # TODO: Below can fail if we exceed max temp, then we need to adjust both
                    try:
                        self.set_temperature(
                            zone_id,
                            (current_heat_temp + TEMP_PROTECTIVE_RANGE),
                            EventValues.COOL.name,
                            TEMP_UNIT_CELCIUS
                        )
                    except ValueError as err:
                        # Set max value
                        self.set_temperature(
                            zone_id,
                            self.config['max_temp_set'],
                            EventValues.COOL.name,
                            TEMP_UNIT_CELCIUS
                        )
                        self.set_temperature(
                            zone_id,
                            self.config['max_temp_set'] - TEMP_PROTECTIVE_RANGE,
                            EventValues.HEAT.name,
                            TEMP_UNIT_CELCIUS
                        )
            elif previous_mode == EventValues.COOL:
                # Update heat to adhere to the limits
                if (current_cool_temp - TEMP_PROTECTIVE_RANGE) < current_heat_temp:
                    # prefix_log(wgo_logger, '>>>>>>>>>>>>>>>>>', f'TEMP COOL: {current_cool_temp}')
                    # TODO: The below can fail, see above
                    try:
                        self.set_temperature(
                            zone_id,
                            (current_cool_temp - TEMP_PROTECTIVE_RANGE),
                            EventValues.HEAT.name,
                            TEMP_UNIT_CELCIUS
                        )
                    except ValueError as err:
                        # Set min value
                        self.set_temperature(
                            zone_id,
                            self.config['min_temp_set'],
                            EventValues.HEAT.name,
                            TEMP_UNIT_CELCIUS
                        )
                        self.set_temperature(
                            zone_id,
                            self.config['min_temp_set'] + TEMP_PROTECTIVE_RANGE,
                            EventValues.COOL.name,
                            TEMP_UNIT_CELCIUS
                        )
            else:
                # Do nothing for FAN_ONLY or error states if applicable
                pass

        self.event_logger.add_event(
            RVEvents.THERMOSTAT_OPERATING_MODE_CHANGE,
            zone_id,
            EventValues[mode]
        )

        config_key = f'{self.configBaseKey}.zone.{zone_id}.climate_mode'
        self.HAL.app.save_config(config_key, {'value': mode})

        return self.state.get(ac_key)

    # def get_zone_ac_mode(self, zone_id: int):
    #     ac_key = f'zone_{zone_id}_climate_mode'
    #     return self.state.get(ac_key)

    def get_zone_schedule(self, zone_id):
        '''Read current schedule ob off state for given zone.'''
        return self.get_state('zone_schedule', zone_id)

    def set_zone_schedule(self, zone_id, control):
        '''Turns schedule on or off for a given zone.'''
        self.set_state(f'zone_schedule', zone_id, control.onOff)

    def clear_zone_schedule(self, zone_id):
        '''Clear hold from schedule.'''
        # Check which schedule applies to the given time
        # Set schedule
        schedule_id = 1
        self.set_state(f'zone_schedule', zone_id, schedule_id)

    def get_climate_zone_temp_config(self, zone_id, temp_unit=TEMP_UNIT_FAHRENHEIT):
        result = {}
        for mode in [EventValues.COOL.name, EventValues.HEAT.name]:
            set_temp = self.config[f'zone_{zone_id}'].get(f'set_temperature_{mode}')
            if set_temp is None:
                raise ValueError

            if temp_unit == TEMP_UNIT_FAHRENHEIT:
                value = celcius_2_fahrenheit(set_temp)
            else:
                # value = round(internal_temp * 2) / 2
                value = round(set_temp, 0)

            result[mode] = value

        return result

    def set_temperature(self, zone_id: int, zone_temp, zone_mode: str, temp_unit=TEMP_UNIT_FAHRENHEIT):
        '''Set the desired temperature of a specific zone.'''
        # Get current temp
        set_temp_key = f'set_temperature_{zone_mode}'
        try:
            current_set_temp = self.config[f'zone_{zone_id}'].get(set_temp_key)
        except KeyError as err:
            print(f'Zone: {zone_id} not defined in climate HW settings')
            print(err)
            raise

        if current_set_temp is None:
            raise ValueError('Current set temp should never be none')

        # Check if temp is within allowed ranges
        if self._check_temperature(zone_temp, temp_unit=temp_unit):
            raise ValueError(f'HW does not allow setting this value: {zone_temp}')

        if temp_unit == TEMP_UNIT_FAHRENHEIT:
            zone_temp_set = fahrenheit_2_celcius(zone_temp)
            current_set_temp = celcius_2_fahrenheit(current_set_temp)
        else:
            zone_temp_set = zone_temp

        self.config[f'zone_{zone_id}'][f'set_temperature_{zone_mode}'] = zone_temp_set

        if zone_mode == EventValues.COOL.name:
            event_type = RVEvents.THERMOSTAT_CURRENT_COOL_TEMPERATURE_SET_CHANGE
        elif zone_mode == EventValues.HEAT.name:
            event_type = RVEvents.THERMOSTAT_CURRENT_HEAT_TEMPERATURE_SET_CHANGE
        else:
            raise ValueError(f'Unsupported Mode: {zone_mode}')

        self.event_logger.add_event(
            event_type,
            zone_id,
            zone_temp_set
        )

        config_key = f'{self.configBaseKey}.zone.{zone_id}_set_temperature_{zone_mode}'
        self.HAL.app.save_config(config_key, {'value': zone_temp_set})

        return {
            'setpoint_temperature': zone_temp,
            'previous_set_temperature': current_set_temp,
            'mode': zone_mode
        }

    def auto_ac_on(self, zone_id=1, fan_circuit=AC_FAN_HIGH):
        self.auto_heater_off(zone_id=zone_id)

        # prefix_log(wgo_logger, __name__, '[CLIMATE] Turning CLIMATE ON')
        czone.circuit_control(fan_circuit, 1, 100)
        self.event_logger.add_event(
            RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
            1,
            EventValues.HIGH
        )

        czone.circuit_control(AC_COMPRESSOR, 1, 100)
        self.event_logger.add_event(
            RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
            1,
            EventValues.ON
        )

    def auto_heater_on(self, zone_id=1):
        # prefix_log(wgo_logger, '[CLIMATE]', 'Turning HEATER ON')
        self.auto_ac_off(zone_id)

        if self.state.get('heater_1_lock') == 1:
            prefix_log(wgo_logger, '[CLIMATE]', 'Heater is locked from turning on (load shedding)')
            return

        czone.circuit_control(HEATER, 1, 100)
        self.event_logger.add_event(
            RVEvents.FURNACE_OPERATING_MODE_CHANGE_CHANGE,
            1,
            EventValues.ON
        )

    def auto_ac_off(self, zone_id=1):
        # prefix_log(wgo_logger, __name__, '[CLIMATE] Turning AC OFF')
        czone.circuit_control(AC_FAN_LOW, 0, 0)
        czone.circuit_control(AC_FAN_HIGH, 0, 0)
        czone.circuit_control(AC_COMPRESSOR, 0, 0)
        self.event_logger.add_event(
            RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
            1,
            EventValues.OFF
        )

        self.event_logger.add_event(
            RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
            1,
            EventValues.OFF
        )

    def auto_heater_off(self, zone_id=1):
        # prefix_log(wgo_logger, '[CLIMATE]', 'Turning HEATER OFF')
        czone.circuit_control(HEATER, 0, 0)
        # TODO: Fix even name below
        self.event_logger.add_event(
            RVEvents.FURNACE_OPERATING_MODE_CHANGE_CHANGE,
            zone_id,
            EventValues.OFF
        )

    def safety_shutoff(self, zone_id):
        self.auto_ac_off(zone_id)
        self.auto_heater_off(zone_id)

    def set_heater_lock(self, onoff, heater_id=1):
        '''Set lock mode on heater, so it cannot be enganged, either due to load shedding or user function.'''
        self.state[f'heater_{heater_id}_lock'] = onoff
        value = EventValues.ON if onoff == 1 else EventValues.OFF
        self.event_logger.add_event(
            RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_HEATER_LOCK,
            heater_id,
            value
        )

    def get_set_ac_fan_speed(self, zone_id: int):
        base_key = f'{self.configBaseKey}.zone.{zone_id}'
        fan_speed_key = f'{base_key}.fan.1.fanSpd'
        fan_speed = self.HAL.app.get_config(fan_speed_key)
        return fan_speed['value']

    def get_ac_fan_state(self, zone_id: int, fan_id: int):
        fan_key = f'zone_{zone_id}__fan_{fan_id}'
        ac_fan_state = self.state.get(fan_key, {})
        #compressor = self.state.get(fan_key, {}).get('compressor', 0)
        return ac_fan_state

    def get_ac_state(self, zone_id: int):
        '''Read the current state of the AC in given zone_id.'''
        fan_key = f'zone_{zone_id}__ac_1'
        # print('FAN', fan_key)
        state = self.state.get(fan_key)

        #print('AC state', state)

        result = {
            'onOff': state.get('onOff'),
            'fanSpd': state.get('fanSpd'),
        }
        return result

    def get_roof_hatch_state(self, zone_id: int, fan_id: int):
        fan_key = f'zone_{zone_id}__fan_{fan_id}'
        roof_hatch_state = self.state.get(fan_key, {})
        return roof_hatch_state


        return current_set_temp

    def get_actual_temperature(self, zone_id: int, unit: str = 'C'):
        zone_temp = self.state.get(f'currenttemp__{zone_id}')
        if zone_temp is None:
            return None
        else:
            temp = self.state.get(f'currenttemp__{zone_id}')
        if unit == 'F':
            temp = celcius_2_fahrenheit(temp_in_c=temp)
        return temp

    def get_outdoor_temperature(self, unit: str = 'C'):
        global EXTERIOR_TEMP_ZONE
        return self.get_actual_temperature(EXTERIOR_TEMP_ZONE, unit=unit)

    def get_hvac_mode(self, zone_id: int):
        '''Get the current HVAC status for zone_id.'''
        # Check if Thermostat is off
        if self.thermostat[zone_id].state.onOff == 0:
            # TODO: Use the enum
            return EventValues.OFF
        try:
            hvac_mode = self.state.get(f'zone_{zone_id}_climate_mode', HVAC_MODE_AUTO)
        except KeyError as err:
            print(f'Zone: {zone_id} not defined in climate HW settings or "hvac_mode" not found')
            print(err)
            raise

        return hvac_mode

    def get_current_hvac_mode(self, zone_id: int):
        '''Within the currently set mode we have active modes such as cooling/heating while in auto mode.

        This implements all the checks around it to present the current system mode to the API/UI'''
        # TODO: Implement
        current_mode = self.state.get(f'zone_{zone_id}_climate_mode_current', EventValues.STANDBY)
        # Check if fan is currently on
        if current_mode == EventValues.FAN_ONLY:
            # Get FAN speed and override response with speed
            fan_key = f'zone_{zone_id}__fan_1'
            fan_speed = self.state.get(fan_key, {}).get('fanSpd', EventValues.AUTO_OFF)
            current_mode = fan_speed

        # Check if there are any errors
        # If nothing on, mode is standby
        return current_mode

    def set_ac_setting(self, zone_id: int, settings: dict):
        '''Set the AC to the specific setting of fan, compressor and future possibilities.'''
        fan_key = f'zone_{zone_id}__ac_1'

        fan_speed = settings.fanSpd

        if fan_speed == EventValues.OFF:
            # Turn both CZone circuits off
            czone.circuit_control(AC_FAN_LOW, 0, 0)
            czone.circuit_control(AC_FAN_HIGH, 0, 0)
            czone.circuit_control(AC_COMPRESSOR, 0, 0)
        elif fan_speed == EventValues.LOW:
            czone.circuit_control(AC_FAN_LOW, 1, 100)
            czone.circuit_control(AC_FAN_HIGH, 0, 0)
        elif fan_speed == EventValues.HIGH:
            czone.circuit_control(AC_FAN_HIGH, 1, 100)
            czone.circuit_control(AC_FAN_LOW, 0, 0)
        elif fan_speed is None:
            # Set FAN speed for response to unchanged
            fan_speed = self.state.get(fan_key, {}).get('fanSpd', EventValues.OFF)
        else:
            raise ValueError(f'fanSpd {settings.fanSpd} not supported')

        self.HAL.app.save_config(f'climate.zone.{zone_id}.fan.1.fanSpd', {'value': fan_speed})

        compressor = settings.onOff
        if compressor == 0:
            czone.circuit_control(AC_COMPRESSOR, 0, 0)
        elif compressor == 1:
            # Check if fan is running ???
            czone.circuit_control(AC_COMPRESSOR, 1, 100)
        elif compressor is None:
            # Leave untouched and climate algo with handle
            compressor = self.state.get(fan_key, {}).get('onOff', 0)
        else:
            raise ValueError(f'Compressor Setting {settings.compressor} not supported')

        self.state[fan_key] = {
            'fanSpd': settings.fanSpd,
            'onOff': settings.onOff
        }

        self.event_logger.add_event(
            RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
            zone_id,
            fan_speed
        )

        self.event_logger.add_event(
            RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
            zone_id,
            compressor
        )

        self.state[fan_key]

    def get_fan_state(self, zone_id: int, fan_id: int):
        '''Read the current state of the fan.'''
        fan_key = f'zone_{zone_id}__fan_{fan_id}'
        state = self.state.get(fan_key)
        if state is None:
            raise ValueError(f'Key {fan_key} not present in state: {self.state}')
        return state

    def get_fan_state_by_key(self, fan_key: str):
        '''Read the current state of the fan.'''
        state = self.state.get(fan_key)
        if state is None:
            raise ValueError(f'Key not present in state: {self.state}')
        return state

    # FAN specific implementation
    def fan_control(self, zone_id: int, fan_id: int, on_off:  int, speed: Union[str, int], direction: Union[str, int], dome: int, rain_sensor: int):
        '''Switch Fan {id} controls'''

        print('fan_control onOff', on_off, type(on_off))
        print('fan_control direction', direction, type(direction))
        print('fan_control speed', speed, type(speed))
        print('fan_control dome', dome, type(dome))


        # Test to see if we can use both words or integers in the same functions
        # And return to the user what they expect - integers or words -
        using_int = False  # if any integer is in the input then the response will be integers

        fan_key = f'zone_{zone_id}__fan_{fan_id}'
        #fan_instance = self.config.get('fan_mapping', {}).get(fan_id, 4)
        fan_instance = 4 # TODO: until this changes is fan_id = 1  int(fan_id)
        print('fan_instance ', fan_instance, type(fan_instance))

        current_fan_state = self.state.get(fan_key)
        if current_fan_state is None:
            current_fan_state = FAN_DEFAULT_STATE

        # Dometic fan
        # CAN speed is 0.5% increments

        if speed is None:
            speed = current_fan_state.get('fanSpd', FAN_DEFAULT_SPEED)

        if on_off == EventValues.OFF:
            on_off = 0
        elif on_off == 'ON':
            on_off = 1

        if speed == EventValues.OFF:
            # Used to turn off
            set_speed = 2
            on_off = 0
        elif speed == EventValues.LOW:
            set_speed = 20 * 2
        elif speed == EventValues.MEDIUM:
            set_speed = 60 * 2
        elif speed == EventValues.HIGH:
            set_speed = 100 * 2
        else:
            raise ValueError(f'Cannot set speed based on: {speed} type {type(speed)}')

        if set_speed is None:
            # prefix_log(wgo_logger, __name__, 'Default mismatch, speed is none')
            set_speed = 2

        if direction is None:
            direction = current_fan_state.get('direction', FAN_DEFAULT_DIRECTION)

        if direction == EventValues.FAN_OUT:
            direction_set = 0
        else:
            direction_set = 1

        current_on_off = current_fan_state.get('onOff', FAN_DEFAULT_SYSTEM_STATE)
        current_dome_state = current_fan_state.get('dome', 0)

        if current_dome_state != dome:
            # A change in Dome
            pass
        else:
            # No change in dome
            if on_off == 1:
                dome = 1
            elif on_off == 0:
                dome = 0

        if on_off is None:
            on_off = current_on_off

        if dome == 1 or dome == 525: # 525 == OPENED
            dome_set = 4
        else:
            dome_set = 0

        print('direction_set', direction_set, 'dome_set', dome_set)

        byte3 = direction_set | (dome_set << 2)

        print('onOff', on_off, type(on_off))
        print('byte3', byte3, type(byte3))
        print('fanSpd', speed, type(speed), speed)
        print('set_speed', set_speed, type(set_speed))

        cmd = f'cansend canb0s0 19FEA644#{fan_instance:02X}{on_off:02X}{set_speed:02X}{byte3:02X}FFFFFFFF'

        print(f'Fan set can msg :  {cmd}')
        # prefix_log(wgo_logger, None, 'Sending: ' + str(cmd))
        # TODO: Move this to a CAN handling class in HAL / Main Service
        result = subprocess.run(cmd, shell=True, capture_output=True)
        print(f'Fan set can msg result:  {result}')

        try:
            self.event_logger.add_event(
                RVEvents.ROOF_VENT_OPERATING_MODE_CHANGE,
                1,  # One roof dome  -> check fan_instance,
                on_off,
            )
            self.event_logger.add_event(
                RVEvents.ROOF_VENT_FAN_SPEED_CHANGE,
                1,  # One roof dome  -> check fan_instance,
                speed
            )

            self.event_logger.add_event(
                RVEvents.ROOF_VENT_FAN_DIRECTION_CHANGE,
                1,  # One roof dome  -> check fan_instance,
                direction
            )
        except Exception as err:
            print(f'Failed adding events {err}')

        # TODO: Migrate to set_state
        self.state[fan_key] = {
            'dome': dome,
            'onOff': on_off,
            'fanSpd': speed,
            'direction': direction
        }

        result = self.state[fan_key]
        print('Fan State result returned', result)

        return result

    def heater_control(self, heater_id: int, on_off: int, temp_set: int):
        pass

    def ac_control(self, on_off: int, temp_set: int):
        pass

    def temp_unit_switch(self, unit):
        '''Makes sure units are switched properly.
        Coming from Fahrenheit the system temp is celcius and might be fractions of Celsius

        Need to round them to the nearest full number.'''
        # TODO: Get list of zones from config/template
        if unit == TEMP_UNIT_CELCIUS:
            for zone_id in [1,]:
                current_heat_temp = self.thermostat[zone_id].state.setTempHeat.get_temperature()
                current_cool_temp = self.thermostat[zone_id].state.setTempCool.get_temperature()
                new_temp_heat = round(current_heat_temp, 0)
                new_temp_cool = round(current_cool_temp, 0)
                self.set_temperature(
                    zone_id,
                    new_temp_heat,
                    EventValues.HEAT.name,
                    temp_unit=TEMP_UNIT_CELCIUS
                )
                self.set_temperature(
                    zone_id,
                    new_temp_cool,
                    EventValues.COOL.name,
                    temp_unit=TEMP_UNIT_CELCIUS
                )


    def run_climate_controls(self, zone_id=1):
        '''Check based on updated values if any action is required for climate.'''
        # Check interior temp
        if self.state.get('climate_algo_enabled') == 0:
            prefix_log(wgo_logger, __name__, f'[CLIMATE] Skipping Climate Algorithm for testing')
            return

        # prefix_log(wgo_logger, __name__, f'[CLIMATE] Running Climate Loop for zone {zone_id}')
        current_temp = self.get_actual_temperature(instance= zone_id)
        # prefix_log(wgo_logger, __name__, f'[CLIMATE] Current Temp in Zone {zone_id}: {current_temp}')
        # Check Thermostat on
        zone_state = self.thermostat[zone_id].state.onOff
        if zone_state == 0 or zone_state is None:
            # prefix_log(wgo_logger, __name__, '[CLIMATE] Zone is off, do nothing, turn everything off')
            self.safety_shutoff(zone_id)
            self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.STANDBY
            return

        # Check Mode
        current_mode = self.thermostat[zone_id].state.mode
        # prefix_log(wgo_logger, __name__, f'[CLIMATE] HVAC mode Zone {zone_id}: {current_mode}')

        # Check if current temp is none, then go to failure mode
        if current_temp is None:
            prefix_log(
                wgo_logger,
                __name__,
                f'[CLIMATE] Internal Temp erroneous/unknown, enabling fail safe shutoff in zone: {zone_id}',
                lvl='error'
            )
            self.safety_shutoff(zone_id)
            # Disable Thermostat
            self.state[f'zone_{zone_id}__onOff'] = 0
            self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.STANDBY
            raise ValueError('Do not know temperature')

        if current_mode == HVAC_MODE_AUTO:
            # Check low and hi temp
            desired_temp_heat = self.thermostat[zone_id].state.setTempHeat.get_temperature()
            desired_temp_cool = self.thermostat[zone_id].state.setTempCool.get_temperature()

            # prefix_log(wgo_logger, __name__, f'[CLIMATE] Desired Temp Heat: {desired_temp_heat}')
            # prefix_log(wgo_logger, __name__, f'[CLIMATE] Desired Temp Cool: {desired_temp_cool}')

            if current_temp < desired_temp_heat:
                self.auto_heater_on()
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.HEAT
            elif current_temp > (desired_temp_cool + CLIMATE_LOW_HIGH_THRESHOLD):
                self.auto_ac_on(fan_circuit=AC_FAN_HIGH)
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.COOL
            elif current_temp > desired_temp_cool:
                self.auto_ac_on(fan_circuit=AC_FAN_LOW)
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.COOL
            else:
                self.auto_heater_off()
                self.auto_ac_off()
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.STANDBY

        elif current_mode == HVAC_MODE_COOL:
            self.auto_heater_off(zone_id)
            desired_temp = self.thermostat[zone_id].state.setTempCool.get_temperature()
            # Check if temperature is higher than target temp
            # TODO: Check when the FAN should be high vs. low
            if current_temp > (desired_temp + CLIMATE_LOW_HIGH_THRESHOLD):
                self.auto_ac_on()
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.COOL
            elif current_temp > desired_temp:
                self.auto_ac_on()
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.COOL
            else:
                self.auto_ac_off()
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.STANDBY
        elif current_mode == HVAC_MODE_HEAT:
            self.auto_ac_off(zone_id)
            # Check lo
            desired_temp = self.thermostat[zone_id].state.setTempHeat.get_temperature()
            if current_temp < desired_temp:
                self.auto_heater_on()
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.HEAT
            else:
                self.auto_heater_off()
                self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.STANDBY
        elif current_mode == HVAC_MODE_FAN_ONLY:
            # Turn Heater off
            self.auto_heater_off()
            # Turn Compressor off
            czone.circuit_control(AC_COMPRESSOR, 0, 0)
            # Confirm fan speed
            # Not implemented
            #
            self.state[f'zone_{zone_id}_climate_mode_current'] = EventValues.STANDBY


    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''Receive updates to climate module.

        Those include internal temperature etc.
        Also contain fridge due to the nature of the message reveiced until further notice.'''
        updated = False
        state = None
        # return updated, state  # Messing with DOmetic
        # print('MSG_Name', msg_name)
        # print('MSG', can_msg)

        # TODO: Remove 'ambient_temperature' when confirmed not used anywhere else
        if msg_name == 'thermostat_ambient_status':
            # Check instance
            instance = int(can_msg.get('Instance', -1))
            zone_id = INSTANCE_TO_ZONE.get(instance)

            if zone_id is None:
                return {}

            temp_key = f'currenttemp__{zone_id}'

            current_temp_celcius = self.state.get(temp_key)
            new_temp_celcius = can_msg.get('Ambient_Temp')
            print(f'New temp for instance: {instance}: {new_temp_celcius}')

            if new_temp_celcius == '-17.78125':
                # This likely is thermistor failing for Dometic FAN gateway
                new_temp_celcius = None
            else:
                try:
                    new_temp_celcius = round(float(new_temp_celcius), 1)
                except ValueError:
                    if new_temp_celcius == DATA_INVALID:
                        # TODO: Bring back reporting None if needed or raise nother event/error
                        print(f'{instance}: Data Invalid')
                        return state
                    else:
                        raise

            self.state[temp_key] = new_temp_celcius
            updated = True
            state = self.state[temp_key]

            # TODO: Move this into a shared module that is receiving the HW specific handler ?
            if instance == 1:
                try:
                    self.run_climate_controls()
                except ValueError as err:
                    prefix_log(wgo_logger, __name__, 'TEMP ERROR: '+ str(err), lvl='error')

                # TODO: What to report if the temp is NONE
                if new_temp_celcius is None:
                    pass
                else:
                    self.event_logger.add_event(
                        RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE,
                        INSTANCE_TO_ZONE.get(instance, 1),
                        new_temp_celcius
                    )

            elif instance == 55:
                self.event_logger.add_event(
                    RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
                    1, # report refrigerator as 1 to platform
                    new_temp_celcius
                )

        return state


#handler = ClimateControl(config=read_default_config_json_file().get('climate_defaults'))
module_init = (
    ClimateControl,
    'climate_defaults',
    'components'
)


if __name__ == '__main__':
    print(handler)
    print(handler.config)
