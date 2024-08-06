import logging
import time
from copy import deepcopy

from common_libs.models.common import EventValues, RVEvents
from main_service.components.climate import (
    TemperatureConverter,
    ThermostatState,
)
from main_service.modules.constants import *
from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.hardware.czone.control_rv_1 import CZone
from main_service.modules.logger import prefix_log

wgo_logger = logging.getLogger("main_service")
# try:
#     from main_service.modules.hardware.dometic import RoofFan
# except ModuleNotFoundError:
#     from dometic import RoofFan

THIS_SYSTEM = "CLIMATE"

CODE_TO_ATTR = {
    "he": "heater",
    "rf": "refrigerator",
    "rv": "roof_vent",
    "th": "thermostat",
    "ac": "air_conditioner",
}

# AC_FAN_LOW = 16
# AC_FAN_HIGH = 17
# AC_COMPRESSOR = 34

CLIMATE_LOW_HIGH_THRESHOLD = 2  # Degrees


# TODO: where bst to place this always on circuit and check it has not been disabled?
# ANd how to disable in settings?

HEATER_POWER_ALWAYS = 5     # Furnace Power
HEATER = 15  # CZone circuit ID, HEATER constant power is 5, 15 is the trigger wire

ROOF_FAN_CZONE_POWER = 9

# RV-C speed is in 0.5% increments, so 2 = 1%, the lowest speed supported
# By dometic
FAN_DEFAULT_SPEED = EventValues.OFF
FAN_DEFAULT_DIRECTION = EventValues.FAN_OUT
FAN_DEFAULT_SYSTEM_STATE = 0  # 0 = Off
FAN_HOOD_DEFAULT_OPEN = 0
FAN_DEFAULT_STATE = {
    "onOff": FAN_DEFAULT_SYSTEM_STATE,
    "direction": FAN_DEFAULT_DIRECTION,
    "fanSpd": FAN_DEFAULT_SPEED,
    "hood": FAN_HOOD_DEFAULT_OPEN,
}


RVC_THERMISTOR_INSTANCE = 1
INSTANCE_TO_ZONE = {
    1: 4,  # Elwell System on 848R / Truma AC  - also outdoor temp??
    2: 1,  # Dometic 524T Bath, main
    3: 3,  # Aux temp from Lounge fan, thermistor currently not connected
    # 4: 1,  # Dometic
    55: 55,  # No need to change as it will be looked for in REFRIGERATOR_MAPPING below
    56: 56,  # No need to change as it will be looked for in REFRIGERATOR_MAPPING below
    0xF9: 2,  # Exterior TM-1010 sens 1
    0xFA: 55,  # sens 2
    0xF8: 56,  # sens 3
}

FAN_INSTANCES = {
    "2": 2,     # Bath room
    "3": 1      # Lounge
}

# Turn the dict around for reverse index
INSTANCE_TO_CAN = {v: int(k) for k, v in FAN_INSTANCES.items()}


RVC_FRIDGE_INSTANCE = 55
RVC_FREEZER_INSTANCE = 56

REFRIGERATOR_MAPPING = {
    RVC_FRIDGE_INSTANCE: 1,
    RVC_FREEZER_INSTANCE: 2
}

EXTERIOR_TEMP_ZONE = 2
TANK_PADS_INSTANCE = 2

CLIMATE_ZONES = [
    1,
]

DATA_INVALID = 'Data Invalid'

DOMETIC_DEAD_TEMP_READING = "-17.78125"
OUTSIDE_COLD_THRESHOLD = -4.0
OUTSIDE_TEMP_ID = 2


class QuickSettings(object):
    """Helper for pydantic model inputs.

    Add attributes as needed"""

    def __init__(self):
        pass


czone = CZone(load_from='hw_climate')

init_script = {
    # Should a real script go here for init
    # Set Roof Fan default
    # Set AC default mode (Auto ?)
}

shutdown_script = {}


# CONFIG_DEFAULTS -> Moved to file Climate_Defaults.json in the data dir
# Under tools use default helper to adjust the file as needed


class ClimateControl(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        # Given by base class
        # .state / .savedState / .config
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        self.configBaseKey = "climate"
        # TODO: currently saving the tstat state - on or OFF
        # Should that not be somewhere else, like the load shedding component ?
        self.loadshed_saved_state = None


        for key, value in config.items():
            self.state[key] = value
            print(f"ClimateControl key {key} value {value}")

        self.init_components(components, self.configBaseKey)

        # # Add HAL to czone
        # TODO: Where can we put this ? Might be in the AGS branch
        czone.set_hal(self.HAL)


    def run_init_script(self, script):
        for func, args in script.items():
            func(*args)

    def _check_temperature(self, temp_desired):     # MUST BE Celsius temp_unit='C'):
        # if temp_unit == TEMP_UNIT_FAHRENHEIT:
        #     temp_desired = fahrenheit_2_celcius(temp_desired)

        # prefix_log(wgo_logger, f'{__name__} - [CLIMATE][TEMPCHECK]', f'{temp_desired} {temp_unit}')
        if (
            temp_desired > self.config["max_temp_set"]
            or temp_desired < self.config["min_temp_set"]
        ):
            return True
        return False

    def _init_config(self):
        '''Initialize climate specific configurations.'''
        # Initialize Thermostat settings
        for instance, thermostat in self.thermostat.items():
            print(thermostat)
            saved_state = thermostat.get_db_state()
            if saved_state is not None:
                print(f"\n #x#x#x#x \n Loading Saved ThermostatState {saved_state} \n")
                # Drop current temp from saved state
                # TODO: Remove once 100% that temp is not saved anymore
                if 'temp' in saved_state:
                    try:
                        del saved_state['temp']
                    except KeyError as err:
                        print(err)

                new_state = ThermostatState(saved_state)
                # Update new_state to set onOff to off as per
                # https://dev.azure.com/WGO-Web-Development/SmartRV/_workitems/edit/4023
                # FIX:14022
                new_state.onOff = EventValues.OFF
                thermostat.state = new_state

        return

    def set_zone_ac_mode(self, zone_id: int, mode: int):
        """Sets the given zone to mode AUTO / HEAT / COOL / FAN_ONLY."""

        # if mode not in [EventValues.OFF, EventValues.AUTO, EventValues.HEAT, EventValues.COOL, EventValues.FAN_ONLY]:
        #     raise "Need to use Event Values for AC mode!!"

        if zone_id not in CLIMATE_ZONES:
            raise ValueError(f"Climate zone: {zone_id} unknown")

        # TODO: Remove after UI handles properly
        if type(mode) == str:
            mode = EventValues[mode]
            if mode not in [
                EventValues.OFF,
                EventValues.AUTO,
                EventValues.HEAT,
                EventValues.COOL,
                EventValues.FAN_ONLY,
            ]:
                raise "Not a valid  AC mode!!"

        thermostat = self.thermostat[zone_id]

        previous_mode = thermostat.state.setMode

        if previous_mode != mode:
            thermostat.state.setMode = mode
            self.event_logger.add_event(
                RVEvents.THERMOSTAT_OPERATING_MODE_CHANGE, zone_id, mode
            )
            thermostat.state.setMode = mode
            thermostat.save_db_state()

        return self.thermostat[zone_id].state.setMode

    def get_zone_schedule(self, zone_id):
        """Read current schedule ob off state for given zone."""
        return self.get_state("zone_schedule", zone_id)

    def set_zone_schedule(self, zone_id, control):
        """Turns schedule on or off for a given zone."""
        self.set_state(f"zone_schedule", zone_id, control.onOff)

    def clear_zone_schedule(self, zone_id):
        """Clear hold from schedule."""
        # Check which schedule applies to the given time
        # Set schedule
        schedule_id = 1
        self.set_state(f"zone_schedule", zone_id, schedule_id)

    def get_climate_zone_temp_config(self, zone_id, temp_unit=TEMP_UNIT_FAHRENHEIT):
        result = {}
        result["HEAT"] = self.thermostat[zone_id].get_tempHeat(temp_unit)
        result["COOL"] = self.thermostat[zone_id].get_tempCool(temp_unit)

        return result

    def set_temperature(
        self, zone_id: int, zone_temp, zone_mode: str, temp_unit=TEMP_UNIT_FAHRENHEIT
    ):
        """Set the desired temperature of a specific zone."""
        print(f"\n  hw_climate.py set_temperature {zone_mode} {zone_id} {zone_temp} \n")


        # TODO: APPARENTLY NOT USED ANYMORE

        ztemp = TemperatureConverter(zone_temp, temp_unit).temp

        # self.config[f"zone_{zone_id}"][f"set_temperature_{zone_mode}"] = zone_temp_set
        if zone_mode == "HEAT" or zone_mode == EventValues.HEAT:
            self.thermostat[zone_id].set_tempHeat(ztemp, temp_unit)
            current_set_temp = self.thermostat[zone_id].get_tempHeat(temp_unit)
        elif zone_mode == "COOL" or zone_mode == EventValues.COOL:
            self.thermostat[zone_id].set_tempCool(ztemp, temp_unit)
            current_set_temp = self.thermostat[zone_id].get_tempCool(temp_unit)

        if zone_mode == EventValues.COOL.name or zone_mode == EventValues.COOL:
            event_type = RVEvents.THERMOSTAT_CURRENT_COOL_TEMPERATURE_SET_CHANGE
        elif zone_mode == EventValues.HEAT.name or zone_mode == EventValues.HEAT:
            event_type = RVEvents.THERMOSTAT_CURRENT_HEAT_TEMPERATURE_SET_CHANGE
        else:
            raise ValueError(f"Unsupported Mode: {zone_mode}")

        self.event_logger.add_event(event_type, zone_id, zone_temp)

        return {
            "setpoint_temperature": zone_temp,
            "previous_set_temperature": current_set_temp,
            "mode": zone_mode,
        }

    def auto_ac_on(self, zone_id: int = 1, fan_speed: EventValues = EventValues.HIGH):
        self.auto_heater_off(zone_id=zone_id)

        ac_state = {
            "comp": EventValues.ON,
            "fanSpd": fan_speed
        }

        air_conditioner = self.air_conditioner[zone_id]
        air_conditioner.set_state(ac_state)

    def auto_heater_on(self, zone_id=1):
        global HEATER
        self.auto_ac_off(zone_id)

        HEAT_PUMP_ID = 2
        heat_pump = self.heater.get(HEAT_PUMP_ID)
        if heat_pump is not None:
            source = heat_pump.state.heatSrc
            combustion = False
            electric = False
            auto = False
            if source == EventValues.COMBUSTION:
                combustion = True
            elif source == EventValues.ELECTRIC:
                electric = True
            elif source == EventValues.AUTO:
                auto = True
            else:
                # Default to combustions
                print('[CLIMATE][HEATSOURCE] Default to combustion as heatSrc is None')
        else:
            combustion = True
            electric = False
            auto = False

        # TODO: Check that this does not apply, is not a 120V heater that can be shed, but it might be out of LP
        # if self.state.get('heater_1_lock') == 1:
        #     prefix_log(wgo_logger, '[CLIMATE]', 'Heater is locked from turning on (load shedding)')
        #     return

        # TODO: Remove hardcoding the HEATER ID and discover it in component init
        # Set internal attributes accordingly

        if combustion is True:
            self.HAL.electrical.handler.dc_switch(
                HEATER,
                1,
                100
            )
            self.heater[zone_id].state.onOff = EventValues.ON
        else:
            self.HAL.electrical.handler.dc_switch(
                HEATER,
                0,
                100
            )
            self.heater[zone_id].state.onOff = EventValues.OFF

        self.event_logger.add_event(
            RVEvents.HEATER_OPERATING_MODE_CHANGE,
            zone_id,
            self.heater[zone_id].state.onOff
        )

        if electric is True:
            self.auto_heatpump_on(zone_id=zone_id)
        else:
            self.auto_heatpump_off(zone_id=zone_id)

        if auto is True:
            print('[CLIMATE] AUTO Heat setting, to be refined.')
            shore_power = self.HAL.energy.handler.energy_source.get(2)
            shore_power_active = shore_power.state.active
            battery = self.HAL.energy.handler.battery_management.get(1)
            battery_soc = battery.state.soc
            propane = self.HAL.energy.handler.fuel_tank.get(1)
            propane_lvl = propane.state.lvl
            if shore_power_active:
                self.auto_heatpump_on(zone_id=zone_id)
                # TODO: What should we do for heat pump AND propane
                # Temp differential needed for both or using the furnace
            else:
                if propane_lvl > 10.0:
                    self.HAL.electrical.handler.dc_switch(
                        HEATER,
                        1,
                        100
                    )
                    # czone.circuit_control(HEATER, 1, 100)
                    self.heater[zone_id].state.onOff = EventValues.ON
                elif battery_soc > 15.0:
                    self.auto_heatpump_on(zone_id=zone_id)

    def auto_ac_off(self, zone_id=1, fanSpd=None):
        prefix_log(wgo_logger, __name__, "[CLIMATE] Turning AC OFF")
        # TODO: Add 500 series Alpha implementation
        # Send CAN message to ac unit

        if fanSpd is None:
            fanSpd = self.air_conditioner[zone_id].state.fanMode

        ac_state = {
            "comp": EventValues.OFF,
            "fanSpd": fanSpd
        }

        air_conditioner = self.air_conditioner[zone_id]
        air_conditioner.set_state(ac_state)

    def ac_fan_off(self, zone_id=1):
        prefix_log(wgo_logger, __name__, "[CLIMATE] Turning AC FAN off")
        # TODO: Add 500 series Alpha implementation
        # Send CAN message to ac unit

        ac_state = {
            "comp": EventValues.OFF,
            "fanSpd": EventValues.OFF
        }

        air_conditioner = self.air_conditioner[zone_id]
        air_conditioner.set_state(ac_state)

    def auto_heater_off(self, zone_id=1):
        prefix_log(wgo_logger, "[CLIMATE]", "Turning HEATER OFF")
        self.HAL.electrical.handler.dc_switch(
            HEATER,
            0,
            0
        )
        # czone.circuit_control(HEATER, 0, 0)
        # self.state[f"he{zone_id}"] = {"onOff": 0}
        self.heater[zone_id].state.onOff = 0
        # TODO: Fix even name below
        self.event_logger.add_event(
            RVEvents.HEATER_OPERATING_MODE_CHANGE, zone_id, EventValues.OFF
        )

    def auto_heatpump_off(self, zone_id=1):
        '''Turn Heatpump off if present.'''
        HEATPUMP_HEATER_ID = 2      # Hard coded for now
        # TODO: Get this on init and store as a flag for zone 1
        # This should avoid the need to check over and over for heat pump presence
        if hasattr(self, 'heater'):
            heat_pump = self.heater.get(HEATPUMP_HEATER_ID)
            if heat_pump is None:
                return
            else:
                heat_lvl = 0
                self.HAL.app.can_sender.can_send_raw('19FF9A44', f'{zone_id:02X}01FF{heat_lvl:02X}FFFFFFFF')

            self.heater[HEATPUMP_HEATER_ID].state.onOff = EventValues.OFF
            self.event_logger.add_event(
                RVEvents.HEATER_OPERATING_MODE_CHANGE,
                HEATPUMP_HEATER_ID,
                self.heater[HEATPUMP_HEATER_ID].state.onOff
            )

    def auto_heatpump_on(self, zone_id=1):
        '''Turn Heatpump off if present.'''
        HEATPUMP_HEATER_ID = 2      # Hard coded for now
        # TODO: Get this on init and store as a flag for zone 1
        # This should avoid the need to check over and over for heat pump presence
        if hasattr(self, 'heater'):
            heat_pump = self.heater.get(HEATPUMP_HEATER_ID)
            air_conditioner = self.air_conditioner.get(zone_id)
            if air_conditioner is not None:
                fan_mode = air_conditioner.state.fanMode
                if fan_mode == EventValues.AUTO_OFF:
                    # TODO: Auto set speed
                    fan_spd = 50 * 2
                elif fan_mode == EventValues.LOW:
                    fan_spd = 50 * 2
                elif fan_mode == EventValues.HIGH:
                    fan_spd = 100 * 2
                else:
                    fan_spd = 0xFF
            else:
                # This should be irrelevant as we return if we have no heat pump
                fan_spd = 50 * 2

            if heat_pump is None:
                return
            else:
                heat_lvl = 100 * 2

                self.HAL.app.can_sender.can_send_raw(
                    '19FF9A44',
                    f'{zone_id:02X}01FF{heat_lvl:02X}FFFF{fan_spd:02X}FF'
                )

            self.heater[HEATPUMP_HEATER_ID].state.onOff = EventValues.ON
            self.event_logger.add_event(
                RVEvents.HEATER_OPERATING_MODE_CHANGE,
                HEATPUMP_HEATER_ID,
                self.heater[HEATPUMP_HEATER_ID].state.onOff
            )

    def safety_shutoff(self, zone_id):
        # Turn AC off and keep fan off too
        self.auto_ac_off(zone_id, fanSpd=EventValues.OFF)
        self.auto_heater_off(zone_id)
        # TODO: Check fan speed here for heatpump too
        self.auto_heatpump_off(zone_id)
        # self.ac_fan_off(zone_id)

    # TODO: Remove for 500 ? OR Add to heater lockouts??
    # TODO: - Should now become a lockout if not already
    def set_heater_lock(self, onoff, heater_id=1):
        """Set lock mode on heater, so it cannot be enganged, either due to load shedding or user function."""
        self.state[f"heater_{heater_id}_lock"] = onoff
        value = EventValues.ON if onoff == 1 else EventValues.OFF
        self.event_logger.add_event(
            RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_HEATER_LOCK, heater_id, value
        )

    def get_roof_hatch_state(self, zone_id: int, fan_id: int):
        return self.roof_vent[zone_id].state.dict()

    # def get_actual_temperature(self, instance: int, unit: str = "C"):
    #     return self.thermostat[instance].state.temp.get_temperature(unit)

    def get_fridge_temperature(self, instance: int, unit: str = "C"):
        return self.refrigerator[instance].get_temperature(unit)

    def get_outdoor_temperature(self, unit: str = "C"):
        global EXTERIOR_TEMP_ZONE
        return self.thermostat[2].state.temp.get_temperature(unit)

    def get_hvac_mode(self, zone_id: int):
        """Get the current HVAC status for zone_id."""
        # Check if Thermostat is off
        if self.thermostat[zone_id].state.onOff == 0:
            return EventValues.OFF

        hvac_mode = self.thermostat[zone_id].state.setMode
        if hvac_mode is None:
            hvac_mode = EventValues.OFF

        return hvac_mode

    def get_fan_state(self, zone_id: int, fan_id: int):
        """Read the current state of the fan."""
        fan_key = f"zone_{zone_id}__fan_{fan_id}"
        state = self.state.get(fan_key)
        if state is None:
            raise ValueError(f"Key {fan_key} not present in state: {self.state}")

        return state

    def get_fan_state_by_key(self, fan_key: str):
        """Read the current state of the fan."""
        state = self.state.get(fan_key)
        if state is None:
            raise ValueError(f"Key not present in state: {self.state}")
        return state

    # FAN specific implementation

    def new_fan_control(self, fan_id, desired_state):
        '''Simpler controls with single message per state.'''
        print('[CLIMATE][FAN] - New State', desired_state)

        roof_vent = self.roof_vent[fan_id]

        pgn = '19FEA644'
        cmd = None
        onoff = 0

        can_instance = INSTANCE_TO_CAN.get(fan_id)

        if desired_state.fanSpd is not None:
            if desired_state.fanSpd == EventValues.OFF:
                cmd = f'{can_instance:02X}0100FFFFFFFFFF'
                onoff = 0
            elif desired_state.fanSpd == EventValues.LOW:
                cmd = f'{can_instance:02X}012810FFFFFFFF'
                onoff = 1
            elif desired_state.fanSpd == EventValues.MEDIUM:
                cmd = f'{can_instance:02X}017810FFFFFFFF'
                onoff = 1
            elif desired_state.fanSpd == EventValues.HIGH:
                cmd = f'{can_instance:02X}01C810FFFFFFFF'
                onoff = 1
            else:
                print('[CLIMATE][FAN] Not a valid speed', desired_state.fanSpd)
            roof_vent.state.fanSpd = desired_state.fanSpd

        if desired_state.dome is not None:
            if desired_state.dome == EventValues.OPENED:
                cmd = f'{can_instance:02X}010010FFFFFFFF'
                roof_vent.state.dome = EventValues.OPENED
                onoff = 1
            elif desired_state.dome == EventValues.CLOSED:
                cmd = f'{can_instance:02X}010000FFFFFFFF'
                roof_vent.state.dome = EventValues.CLOSED
                onoff = 0
            else:
                print('[CLIMATE][FAN] Not a valid dome', desired_state.dome)
            roof_vent.state.dome = desired_state.dome


        roof_vent.state.onOff = onoff
        self.HAL.app.can_sender.can_send_raw(
            pgn,
            cmd
        )

        return roof_vent.state

    def fan_control(
                self,
                fan_id: int,
                on_off: int,
                speed: int,
                direction: int,
                dome: int,
                rain_sensor: int
            ):
        """Switch Fan {id} controls"""

        print("[CLIMATE}[FAN] fan_control onOff", on_off, type(on_off))
        print("[CLIMATE}[FAN] fan_control direction", direction, type(direction))
        print("[CLIMATE}[FAN] fan_control speed", speed, type(speed))
        print("[CLIMATE}[FAN] fan_control dome", dome, type(dome))

        roof_vent = self.roof_vent[fan_id]

        # Dometic fan
        # CAN speed is 0.5% increments
        if speed == EventValues.OFF or speed is None:
            on_off = 0
            set_speed = 2
        else:
            on_off = 1

            if speed == EventValues.LOW:
                set_speed = 20 * 2
            elif speed == EventValues.MEDIUM:
                set_speed = 60 * 2
            elif speed == EventValues.HIGH:
                set_speed = 100 * 2
            else:
                raise ValueError(f"Cannot set speed based on: {speed} type {type(speed)}")

        # NOTE: Perma set to OUT
        direction = EventValues.FAN_OUT

        if direction == EventValues.FAN_OUT:
            direction_set = 0
        else:
            direction_set = 1

        print("[CLIMATE}[FAN] dome", dome)
        print('[CLIMATE}[FAN] onoff', on_off)
        if dome == EventValues.OPENED:  # 525 == OPENED
            dome_set = 4
        elif dome == EventValues.CLOSED:
            dome_set = 0
        else:
            if speed == EventValues.OFF:
                # We should set the dome to closed as it will do so on off
                dome_set = 0
            else:
                dome_set = 7    # No change

        print("[CLIMATE}[FAN] direction_set", direction_set, "dome_set", dome_set)

        byte3 = direction_set | (dome_set << 2)

        print("[CLIMATE}[FAN] onOff", on_off, type(on_off))
        print("[CLIMATE}[FAN] byte3", byte3, type(byte3))
        print("[CLIMATE}[FAN] fanSpd", speed, type(speed), speed)
        print("[CLIMATE}[FAN] set_speed", set_speed, type(set_speed))
        can_instance = INSTANCE_TO_CAN.get(fan_id)

        # Check if dome has changed
        if dome is not None and dome != roof_vent.state.dome:
            # Set the opposite state for a moment
            if dome == EventValues.CLOSED:
                domeset = 243
            else:
                domeset = 227

            self.HAL.app.can_sender.can_send_raw(
                '19FEA644',
                f'{can_instance:02X}FFFF{domeset:02X}FFFFFFFF'
            )
            time.sleep(0.3)

        self.HAL.app.can_sender.can_send_raw(
            '19FEA644',
            f'{can_instance:02X}{on_off:02X}{set_speed:02X}{byte3:02X}FFFFFFFF'
        )

        # NOTE: Removing updating the state
        # if dome == EventValues.ON:
        #     roof_vent.state.dome = EventValues.OPENED
        # elif dome == EventValues.OFF:
        #     roof_vent.state.dome = EventValues.CLOSED
        # else:
        #     print('Taking dome as is', dome)
        #     roof_vent.state.dome = dome

        # roof_vent.state.onOff = on_off
        # roof_vent.state.fanSpd = speed
        # roof_vent.state.direction = direction

        # roof_vent.state.onOff = None
        # roof_vent.state.fanSpd = None
        # roof_vent.state.direction = None
        roof_vent.state.dome = dome

        return roof_vent.state

    def run_climate_controls(self, zone_id=1):
        """Check based on updated values if any action is required for climate."""
        if self.state.get("climate_algo_enabled", 1) == 0:
            prefix_log(
                wgo_logger,
                __name__,
                f"[CLIMATE] Skipping Climate Algorithm for testing",
            )
            print("\nSkipping CLIMATE algo" * 4, f" zone_id {zone_id}")
            current_mode = self.thermostat[zone_id].state.mode = EventValues.STANDBY
            return

        # Check load shedding present
        ac_load_shed = EventValues.FALSE
        # NOTE: Heater not sheddable in 500 series
        # heat_load_shed = False
        if hasattr(self.HAL.energy.handler, 'load_shedding'):
            AC_LOAD_SHED_INSTANCE = 1
            shed_comp = self.HAL.energy.handler.load_shedding[AC_LOAD_SHED_INSTANCE]
            ac_load_shed = shed_comp.state.active

        # TODO: Ensure power is on in the CZone config always, otherwise we have to retain
        # this here for now

        new_mode = None
        # TODO: Change this to the appropriate circuit after Jon D makes the change to the current Theatre Seat Circuit
        self.HAL.electrical.handler.dc_switch(
            HEATER_POWER_ALWAYS,
            1,
            100
        )
        # czone.circuit_control(HEATER_POWER_ALWAYS, 1, 100)

        thermostat = self.thermostat[zone_id]

        # prefix_log(wgo_logger, __name__, f'[CLIMATE] Running Climate Loop for zone {zone_id}')
        current_temp = thermostat.get_temperature()
        # prefix_log(wgo_logger, __name__, f'[CLIMATE] Current Temp in Zone {zone_id}: {current_temp}')
        # Check Thermostat on
        tstat_state = thermostat.state.onOff
        print("[CLIMATE] Current Thermostat state", tstat_state)

        # ONLY LOAD SHEDDING FOR ZONE 1 Thermostat
        if ac_load_shed == EventValues.TRUE:
            print("[CLIMATE][LOADSHED] ACTIVE!")
            # We just need to save the state - when we see it once
            if self.loadshed_saved_state is None:
                self.loadshed_saved_state = deepcopy(self.thermostat[AC_LOAD_SHED_INSTANCE].state)
                print(f"[CLIMATE][LOADSHED] Save: {self.loadshed_saved_state}")

            # Is this needed ? STANDBY
            thermostat.state.mode = EventValues.STANDBY
            thermostat.state.onOff = EventValues.OFF

            self.safety_shutoff(zone_id)
            return
        else:
            print(f"[CLIMATE][LOADSHED] *** INACTIVE!  {self.loadshed_saved_state}")
            # had we load shed?
            if self.loadshed_saved_state is not None:
                # restore the onOff mode
                print(f"[CLIMATE][LOADSHED] Restore: {self.loadshed_saved_state}")
                self.thermostat[AC_LOAD_SHED_INSTANCE].state = deepcopy(self.loadshed_saved_state)
                self.loadshed_saved_state = None

        if tstat_state == EventValues.OFF or tstat_state is None:
            # prefix_log(wgo_logger, __name__, '[CLIMATE] Zone is off, do nothing, turn everything off')
            # TODO need rules - to be able to run heater or ac without thermostat
            self.safety_shutoff(zone_id)
            thermostat.state.mode = EventValues.STANDBY
            print(f"[CLIMATE][ALGO] Thermostat Disabled for Zone: {zone_id}")
            return

        # Check desired Mode
        commanded_mode = thermostat.state.setMode
        print(f'[CLIMATE][ALGO] Climate controls zone {zone_id} mode {commanded_mode} at temp {current_temp}')
        air_conditioner = self.air_conditioner[zone_id]
        # Check if current temp is none, then go to failure mode
        # TODO: Figure out how to handle this better
        # On None temp the thermostat shuts off, that would happen on daata invalid
        # as well
        if current_temp is None:
            prefix_log(
                wgo_logger,
                __name__,
                f"[CLIMATE] Internal Temp erroneous/unknown, enabling fail safe shutoff in zone: {zone_id}",
                lvl="error",
            )
            return

        #     self.safety_shutoff(zone_id)
        #     # Disable Thermostat NOTE: Why ?
        #     # self.thermostat[zone_id].state.onOff = 0
        #     thermostat.state.mode = EventValues.STANDBY
        #     print('[CLIMATE][ALGO] Do not know interior temperature, exiting climate')
        #     return

        if commanded_mode == HVAC_MODE_AUTO:
            # Check low and hi temp
            desired_temp_heat = thermostat.get_tempHeat()
            desired_temp_cool = thermostat.get_tempCool()

            if current_temp < desired_temp_heat:
                # Too cold, need heat
                self.auto_heater_on()
                new_mode = EventValues.HEAT
            elif current_temp > (desired_temp_cool + CLIMATE_LOW_HIGH_THRESHOLD):
                if air_conditioner.state.fanMode == EventValues.AUTO_OFF:
                    # Very hot, need max cool if in AUTO - otherwise leave fan as user set it
                    self.auto_ac_on(fan_speed=EventValues.HIGH)
                else:
                    self.auto_ac_on(fan_speed=air_conditioner.state.fanMode)
                new_mode = EventValues.COOL
            elif current_temp > desired_temp_cool:
                if air_conditioner.state.fanMode == EventValues.AUTO_OFF:
                    # Hot, need low cool if in AUTO - otherwise leave fan as user set it
                    self.auto_ac_on(fan_speed=EventValues.LOW)
                else:
                    self.auto_ac_on(fan_speed=air_conditioner.state.fanMode)
                new_mode = EventValues.COOL
            else:
                self.auto_heater_off()
                self.auto_heatpump_off(zone_id)
                if air_conditioner.state.fanMode != EventValues.AUTO_OFF:
                    ac_state = {
                        "comp": EventValues.OFF,
                        "fanSpd": air_conditioner.state.fanMode
                    }

                    returned_state = air_conditioner.set_state(ac_state)
                    new_mode = EventValues.FAN_ONLY
                else:
                    self.auto_ac_off(zone_id)
                    new_mode = EventValues.STANDBY

        elif commanded_mode == HVAC_MODE_COOL:
            self.auto_heater_off(zone_id)
            self.auto_heatpump_off(zone_id)
            desired_temp = self.thermostat[zone_id].get_tempCool()
            new_mode = None
            # Check if temperature is higher than target temp
            # TODO: Check when the FAN should be high vs. low
            if current_temp > (desired_temp + CLIMATE_LOW_HIGH_THRESHOLD) and air_conditioner.state.fanMode == EventValues.AUTO_OFF:
                self.auto_ac_on(fan_speed=EventValues.HIGH)
                new_mode = EventValues.COOL

            elif current_temp > desired_temp and air_conditioner.state.fanMode == EventValues.AUTO_OFF:
                self.auto_ac_on(fan_speed=EventValues.LOW)
                new_mode = EventValues.COOL

            elif current_temp > desired_temp:
                print('Need cooling, but fanMode is not AUTO')
                self.auto_ac_on(fan_speed=air_conditioner.state.fanMode)
                new_mode = EventValues.COOL
            else:
                if air_conditioner.state.fanMode != EventValues.AUTO_OFF:
                    ac_state = {
                        "comp": EventValues.OFF,
                        "fanSpd": air_conditioner.state.fanMode
                    }

                    returned_state = air_conditioner.set_state(ac_state)
                    new_mode = EventValues.FAN_ONLY
                else:
                    self.auto_ac_off(zone_id)
                    new_mode = EventValues.STANDBY

            thermostat.state.mode = new_mode

        elif commanded_mode == HVAC_MODE_HEAT:
            self.auto_ac_off(zone_id)
            # Check lo
            desired_temp = thermostat.get_tempHeat()
            if current_temp < desired_temp:
                self.auto_heater_on()
                new_mode = EventValues.HEAT
            else:
                self.auto_heater_off()
                self.auto_heatpump_off(zone_id)
                new_mode = EventValues.STANDBY

        elif commanded_mode == HVAC_MODE_FAN_ONLY:
            # Turn Heater off
            self.auto_heater_off()
            self.auto_heatpump_off(zone_id)
            # Create AC state
            new_mode = EventValues.FAN_ONLY
            # Where is fan Speed?
            ac_state = {
                "comp": EventValues.OFF,
                "fanSpd": air_conditioner.state.fanMode
            }

            returned_state = air_conditioner.set_state(ac_state)

        thermostat.state.mode = new_mode
        thermostat.update_state()

        print(f"[CLIMATE][ALGO] END of Climate Algorithm for zone {zone_id}")

    def update_can_state(self, msg_name, can_msg) -> dict:
        """Receive updates to climate module.

        Those include internal temperature etc.
        Also contain fridge due to the nature of the message reveiced until further notice.
        """
        updated = False
        state = None
        # return updated, state  # Messing with Dometic
        # print('MSG_Name', msg_name)
        # print('MSG', can_msg)

        # print(f" Running Climate update_can_state {msg_name} {can_msg}")
        # 1FF9C
        if msg_name == "thermostat_ambient_status":
            # Check instance
            instance = int(can_msg.get("Instance", -1))

            zone_id = INSTANCE_TO_ZONE.get(instance)
            print(f'[CLIMATE][TEMP] New temp for instance: {instance} zone {zone_id} received')

            if zone_id is None:
                print(f"[CLIMATE][TEMP] {zone_id}: Invalid Zone")
                # Return an empty updated dict
                return False, {}

            new_temp_celcius = can_msg.get("Ambient_Temp")
            print(
                '[CLIMATE][TEMP] New temp celsius',
                new_temp_celcius,
                type(new_temp_celcius)
            )
            if new_temp_celcius == DATA_INVALID:
                print(
                    f"{instance}: %%%%%%%%%%%%%%%%%%%% Data Invalid"
                )
                # Do not do this, this is the gateway either initializing from power off
                # Or due to electrical issues
                new_temp_celcius = None

            # NOTE: We don't want to do that as it could really be that cold, and that is the lowest the dometic GW supports
            elif new_temp_celcius == DOMETIC_DEAD_TEMP_READING:
                print('[CLIMATE][TEMP][DOMETIC] 0 degree F reading', new_temp_celcius)
                # TODO: Also check the exterior temp as a safeguard
                if OUTSIDE_TEMP_ID in self.thermostat:
                    outside_temp = self.thermostat[OUTSIDE_TEMP_ID].state.temp
                    if outside_temp is not None:
                        if self.thermostat[OUTSIDE_TEMP_ID].state.temp > OUTSIDE_COLD_THRESHOLD:
                            print(f"[CLIMATE][TEMP][DOMETIC] Dometic GW reported 0F, but exterior temp is {outside_temp}, considering failure")
                            # TODO: Raise an alert and invalide temp ? Allow manual operation of climate ?
                            # This likely is thermistor failing for Dometic FAN gateway

            if new_temp_celcius is not None:
                try:
                    new_temp_celcius = round(float(new_temp_celcius), 1)
                except ValueError as err:
                    print('Error converting value to float', new_temp_celcius, err)
                    raise

            if zone_id in self.thermostat:
                if new_temp_celcius is not None:
                    try:
                        self.thermostat[zone_id].set_temperature(new_temp_celcius)
                        updated = True
                    except Exception as err:
                        print(f"Climate Update {new_temp_celcius} Can err: {err}")
                        raise err
                else:
                    # print(f"None temp for zone: {zone_id}")
                    self.thermostat[zone_id].set_temp_to_none()

            # TODO: Move this into a shared module that is receiving the HW specific handler ?
            if zone_id == 1:  # MAIN zone
                # TODO: Make this work after FCP / Alpha
                try:
                    self.run_climate_controls(zone_id)
                except ValueError as err:
                    prefix_log(
                        wgo_logger, __name__, "TEMP ERROR: " + str(err), lvl="error"
                    )
                except Exception as err:
                    print('[CLIMATE] Algorithm error', err)

                # If pet monitoring is enabled, run the algorithm
                if hasattr(self.HAL.features.handler, 'pet_monitoring'):
                    self.HAL.features.handler.run_pet_monitoring_algorithm()

                self.thermostat[zone_id].update_state()
                updated = True
                state = self.thermostat[zone_id].state

            elif zone_id in REFRIGERATOR_MAPPING:
                # Single gatewway solution "instance_key" always 55
                rf_inst = REFRIGERATOR_MAPPING.get(zone_id)
                if hasattr(self, 'refrigerator'):
                    fridge = self.refrigerator.get(rf_inst)
                    if fridge is not None:

                        if new_temp_celcius is None:
                            # Set temp to None
                            fridge.state.temp = None
                        else:
                            current_fridge_temp = fridge.get_temperature()
                            fridge.set_temperature(new_temp_celcius)
                            self.event_logger.add_event(
                                RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
                                rf_inst,  # report refrigerator as 1 to platform
                                new_temp_celcius,
                            )

            elif zone_id == EXTERIOR_TEMP_ZONE:  # TM-1010
                thermostat = self.thermostat[EXTERIOR_TEMP_ZONE]
                thermostat.update_state()
                state = thermostat.state
                # print("\n%%%%%%%%%%% BEFORE CHECK TANK &&&&&&&&&&&\n")
                self.HAL.watersystems.handler.check_tank_pad_state(
                    TANK_PADS_INSTANCE
                )

        elif msg_name == 'roof_fan_status_1':
            # Handle status for dometic and other fans ?
            print('ROOF FAN STATUS', msg_name, can_msg)
            # {'Instance': '2', 'System_Status': 'Off', 'Fan_Mode': 'Auto', 'Speed_Mode': 'Auto (Variable)', 'Light': 'Off', 'Fan_Speed_Setting': '60.0', 'Wind_Direction_Switch': 'Air Out', 'Dome_Position': 'Open', 'Deprecated': '0', 'Ambient_Temperature': '-273.0', 'Setpoint': '-273.0', 'msg': 'Timestamp: 1697840958.111073    ID: 19fea7ce    X Rx                DL:  8    02 00 78 10 00 00 00 00     Channel: canb0s0', 'msg_name': 'ROOF_FAN_STATUS_1', 'instance_key': '19FEA7CE__0__2'}
            instance = can_msg.get('Instance')
            fan_instance = FAN_INSTANCES.get(instance)
            try:
                fan = self.roof_vent[fan_instance]
            except KeyError as err:
                print('Unknown FAN instance', err)
                return updated, state

            dome = can_msg.get('Dome_Position')
            speed = can_msg.get('Fan_Speed_Setting')
            onOff = can_msg.get('System_Status')

            if dome == 'Open':
                fan.state.dome = EventValues.OPENED
            elif dome == 'Closed':
                fan.state.dome = EventValues.CLOSED

            if speed == '20.0':
                fan.state.fanSpd = EventValues.LOW
            elif speed == '60.0':
                fan.state.fanSpd = EventValues.MEDIUM
            elif speed == '100.0':
                fan.state.fanSpd = EventValues.HIGH

            if onOff == 'Off':
                fan.state.fanSpd = EventValues.OFF

            updated = True
            state = fan.state

        return updated, state

    def get_ac_state(self, zone_id: int = 1):
        """Read the current state of the fan."""
        ac_key = f"zone_{zone_id}__ac_1"
        # print('FAN', fan_key)
        state = self.state.get(ac_key)

        # print('XX>'*5,'AC state', state)
        result = state
        return result

    # Climate Controls
    def set_ac_state(self, in_state, ac_id: int = 1):
        """Set the GE AC using a can msg via AIR_CONDITIONER_COMMANF"""
        print(f"hw_climate GE air conditioner zone {ac_id} change {in_state}")

        # TODO: align order of parameters to start with index/instance/id
        air_conditioner = self.air_conditioner[ac_id]

        print('Set AC state', in_state)

        # Set AC thermostat into schedule disabled mode to assert control

        op_mode = 1         # Manual
        cool_level = 0
        fan_speed = 0
        max_fan = 0xC8      # 100%
        max_cool = 0xC8     # 100%
        dead_band = 0xFF    # No data
        second_dead_band = 0xFF     # No data

        if in_state.fanSpd == EventValues.OFF:
            air_conditioner.state.comp = EventValues.OFF
            fan_speed = 0   # Turn off
            cool_level = 0  # Turn off
        else:
            if in_state.fanSpd == EventValues.LOW:  # LOW
                fan_speed = 0x64    # GE does not support less than 50%
            # NOTE: This MEDIUM speed should never come in
            elif in_state.fanSpd == EventValues.MEDIUM:  # MED
                fan_speed = 0x64    # 100*0.5 = 50 %
            elif in_state.fanSpd == EventValues.HIGH:  # HIGH
                fan_speed = 0xC8    # 200*0.5 = 100 %
            else:
                print('[CLIMATE] Invalid FAN speed', in_state.fanSpd)
                fan_speed = 0xFF    # No data

            if in_state.comp == EventValues.ON:
                self.air_conditioner[ac_id].state.comp = EventValues.ON
                cool_level = 100 * 2
            else:
                cool_level = 0

        self.HAL.app.can_sender.can_send_raw(
            '19FFE044',
            f'{ac_id:02X}{op_mode:02X}{max_fan:02X}{max_cool:02X}{fan_speed:02X}{cool_level:02X}{dead_band:02X}{second_dead_band:02X}'
        )

        air_conditioner.state.fanSpd = in_state.fanSpd
        air_conditioner.state.comp = in_state.comp

        # TODO Save to DB

        return air_conditioner.state

    def set_ac_state_thermostat(self, in_state, ac_id: int = 1):
        """Set the Truma AC using a can msg"""
        print(f"hw_climate air conditioner zone {ac_id} change {in_state}")

        # TODO: align order of parameters to start with index/instance/id
        air_conditioner = self.air_conditioner[ac_id]

        print('Set AC state', in_state)

        # Set AC thermostat into schedule disabled mode to assert control

        instance = ac_id
        op_mode = 0
        fan_mode = 0
        schedule_mode = 0
        fan_speed = 0
        heat_temp = 100     # TODO: Get this from the values below
        cool_temp = 0

        if in_state.fanSpd == EventValues.OFF:
            # and (in_state.fanMode == EventValues.OFF or in_state.onOff == EventValues.OFF)):
            # id fan is off turn off and compressor should follow
            op_mode = 0
            fan_speed = 0
            fan_mode = 0
            schedule_mode = 0
            self.air_conditioner[ac_id].state.comp = EventValues.OFF
            self.air_conditioner[ac_id].state.fanSpd = EventValues.OFF
        else:
            if in_state.comp == EventValues.ON:
                self.air_conditioner[ac_id].state.comp = EventValues.ON
                op_mode = 1     # Cool
                fan_mode = 1
                # set the fan accordingly for compressor
                if in_state.fanSpd == EventValues.LOW:  # LOW
                    fan_speed = 0x32    # 50*0.5 = 25 %
                    self.air_conditioner[ac_id].state.fanSpd = EventValues.LOW
                elif in_state.fanSpd == EventValues.MEDIUM:  # MED
                    fan_speed = 0x64    # 100*0.5 = 50 %
                    self.air_conditioner[ac_id].state.fanSpd = EventValues.MEDIUM
                elif in_state.fanSpd == EventValues.HIGH:  # HIGH
                    fan_speed = 0xC8    # 200*0.5 = 100 %
                    self.air_conditioner[ac_id].state.fanSpd = EventValues.HIGH
            else:
                air_conditioner.state.comp = EventValues.OFF
                op_mode = 0     # Fan only
                fan_mode = 1    # Manual
                schedule_mode = 3   # No Data

                if in_state.fanSpd == EventValues.LOW:  # LOW
                    fan_speed = 0x32    # 50*0.5 = 25 %
                    self.air_conditioner[ac_id].state.fanSpd = EventValues.LOW
                elif in_state.fanSpd == EventValues.MEDIUM:  # MED
                    fan_speed = 0x64    # 100*0.5 = 50 %
                    self.air_conditioner[ac_id].state.fanSpd = EventValues.MEDIUM
                elif in_state.fanSpd == EventValues.HIGH:  # HIGH
                    fan_speed = 0xC8    # 200*0.5 = 100 %
                    self.air_conditioner[ac_id].state.fanSpd = EventValues.HIGH

        byte2 = op_mode + (fan_mode << 4) + (schedule_mode << 6)
        heat_temp = "FFFF"
        cool_temp = "2024"
        print('Byte 2', hex(byte2), op_mode, fan_mode, schedule_mode)
        print('Set the Truma AC using a can msg')

        self.HAL.app.can_sender.can_send_raw(
            '19FEF944',
            f'{instance:02X}{byte2:02X}{fan_speed:02X}{heat_temp}{cool_temp}FF'
        )

        return air_conditioner.state


# config_data = read_default_config_json_file()
module_init = (
    ClimateControl,
    'climate_defaults',
    'components'
)
