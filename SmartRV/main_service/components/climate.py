from typing import Optional, Literal
from enum import Enum
from math import floor
import logging

from pydantic import BaseModel, constr, validator, Field, root_validator

from main_service.components.common import (
    BaseComponent,
    inject_parent_attr,
)

from common_libs.models.common import RVEvents, EventValues


wgo_logger = logging.getLogger('main_service')

CATEGORY = "climate"

HEATER_CODE = "he"
THERMOSTAT_CODE = "th"
REFRIGERATOR_CODE = "rf"
ROOFFAN_CODE = "rv"
HVAC_CODE = "ac"


# Virtual Thermostat (temp, setTempHeat, setTempCool)
# Roof Fan Dometic (dome, speed, onOff, direction, rain)
# AC Unit (compressor, fan)
# Heater (onOff)
# Heater Elwell / Truma ?


class TemperatureConverter(BaseModel):
    """This is a temperature field class, stored always in Celsius - get and set can specify the Unit if F is needed."""

    def __init__(self, temp: float = -273, unit: str = "C", **kwargs):
        super().__init__(**kwargs)
        temp_celsius = self._convert_to_celsius(temp, unit)
        self.temp = temp_celsius
        # print('Init TempConverter with temp', temp, self.temp)

    temp: float = Field(-273, description="Temperature in Celsius or None")

    @root_validator(pre=True)
    def check_temp_bounds(cls, values):
        temp = values.get("temp")

        if temp is not None:
            temp_celsius = cls._convert_to_celsius(temp)
            if not (-273 <= temp_celsius <= 1700):
                raise ValueError(
                    'Temperature out of range. Must be between -273°C and 1700°C or None.'
                )

        return values

    @classmethod
    def _convert_to_celsius(cls, temp: float, unit="C") -> float:
        if unit == 0 or unit == 1:
            raise ValueError('INT unit no longer supproted, send F or C')

        if unit.upper() == 'C':
            # print('Returning temp as is', temp)
            return temp
        elif unit.upper() == 'F':
            return (temp - 32) * 5 / 9
        else:
            # print("_to_celsius RAISE")
            raise ValueError("Invalid unit. Use 'C' or 'F'.")

    def get_temperature(self, unit='C'):
        if unit == 0 or unit == 1:
            raise ValueError('INT unit no longer supproted, send F or C')

        if unit.upper() == 'C':
            return round(self.temp * 2) / 2
        elif unit.upper() == 'F':
            return int(
                floor(
                    self._convert_to_fahrenheit(self.temp) + 0.5
                )
            )
        else:
            raise ValueError("Invalid unit. Use 'C' or 'F'.")

    def set_temperature(self, temp, unit="C"):
        # print('set_temperature: ', temp)
        temp_celsius = self._convert_to_celsius(temp, unit)
        # print(f"Type temp = {type(temp_celsius)} , {temp_celsius}")
        if -273 <= temp_celsius <= 1700:
            self.temp = temp_celsius
            return self.temp
        else:
            raise ValueError("Temperature out of range. Must be between -273°C and 1700°C or None.")

    def _convert_to_fahrenheit(self, temp_celsius):
        return temp_celsius * 9 / 5 + 32


THERMOSTAT_HEAT_DEFAULT = 17.7      # 64 F
THERMOSTAT_COOL_DEFAULT = 23.3      # 74 F

# THERMOSTAT_MINIMUM = 15.5
THERMOSTAT_MINIMUM = 4
THERMOSTAT_MAXIMUM = 35

THERMOSTAT_HEAT_MINIMUM = 4
THERMOSTAT_HEAT_MAXIMUM = 29.5

THERMOSTAT_COOL_MINIMUM = 15
THERMOSTAT_COOL_MAXIMUM = 35


class ThermostatState(BaseModel):
    """Virtual Thermostat state"""

    # Here in the init gives us the change to set the defaults
    def __init__(self, state_dict: dict = dict(), **kwargs):
        super().__init__(**kwargs)
        print('State dict in Thermostat State', state_dict)
        self.onOff = state_dict.get("onOff", EventValues.OFF)
        if state_dict.get("unit", "C") == "F":
            self.unit = "F"
        else:
            self.unit = "C"

        if state_dict.get("setTempHeat") is not None:
            state_dict["setTempHeat"] = TemperatureConverter(state_dict["setTempHeat"], self.unit).temp
        if state_dict.get("setTempCool") is not None:
            state_dict["setTempCool"] = TemperatureConverter(state_dict["setTempCool"], self.unit).temp
        if state_dict.get("temp") is not None:
            state_dict["temp"] = TemperatureConverter(float(state_dict["temp"]), "F").temp

        self.temp = state_dict.get("temp")
        self.setTempHeat = state_dict.get("setTempHeat", THERMOSTAT_HEAT_DEFAULT)
        self.setTempCool = state_dict.get("setTempCool", THERMOSTAT_COOL_DEFAULT)
        self.setMode = state_dict.get("setMode", EventValues.AUTO)
        self.mode = EventValues.OFF  # Keep units off until run_climate executes.

        print('Initial Temp state', self.temp)

    onOff: Literal[
            EventValues.OFF,
            EventValues.ON] = Field(
        EventValues.OFF,
        description="Thermostat overall state, if off all climate functionality in this zone is off",
        eventId=RVEvents.THERMOSTAT_GENERAL_ONOFF_CHANGE,
        setting=True
    )
    temp: Optional[float] = Field(
        None,
        description="Interior temperature for that zone",
        eventId=RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE,
        setting=False,
    )
    setTempHeat: Optional[float] = Field(
        THERMOSTAT_HEAT_DEFAULT,
        description="Temperature the heating system shall maintain if in auto or heat mode",
        eventId=RVEvents.THERMOSTAT_CURRENT_HEAT_TEMPERATURE_SET_CHANGE,
        setting=True,
        multiple_of=0.5,
        ge=THERMOSTAT_HEAT_MINIMUM,
        le=THERMOSTAT_HEAT_MAXIMUM,
        store_db=True
    )
    setTempCool: Optional[float] = Field(
        THERMOSTAT_COOL_DEFAULT,
        description="Temperature the cooling system shall maintain if in auto or cool mode",
        eventId=RVEvents.THERMOSTAT_CURRENT_COOL_TEMPERATURE_SET_CHANGE,
        setting=True,
        multiple_of=0.5,
        ge=THERMOSTAT_COOL_MINIMUM,
        le=THERMOSTAT_COOL_MAXIMUM,
        store_db=True
    )
    # Mode
    setMode: Literal[
            EventValues.OFF,
            EventValues.AUTO,
            EventValues.HEAT,
            EventValues.COOL,
            EventValues.FAN_ONLY] = Field(
        EventValues.AUTO,
        description='Desired mode the climate system is set to by user',
        eventId=RVEvents.THERMOSTAT_OPERATING_MODE_CHANGE,
        setting=True,
        store_db=True
    )
    # mode is new to indicate the current system mode
    mode: Literal[
        EventValues.OFF,
        EventValues.AUTO,
        EventValues.HEAT,
        EventValues.COOL,
        EventValues.FAN_ONLY,
        EventValues.STANDBY,
    ] = Field(
        EventValues.OFF,
        description="The current mode of the system is operating in.",
        eventId=RVEvents.THERMOSTAT_CURRENT_OPERATING_MODE_CHANGE,
        setting=False,
    )
    unit: Literal["F", "C"] = Field(
        "C", description="Unit of temperature",
        eventId=None,  # Always C in the twin
        setting=True
    )


class Thermostat(BaseComponent):
    """Basic virtual Thermostat."""

    band: float = 3

    category: str = CATEGORY
    code: str = THERMOSTAT_CODE
    type: str = 'virtual'
    state: ThermostatState = ThermostatState()
    attributes: dict = inject_parent_attr({
        'controllable': "NF"  # Near and Far field controlable
        })

    # Get the Temp converted to the unit
    def get_converted_state(self, in_unit: str = "C"):
        # Return the temperatures in the specified unit
        result = {
            "onOff": self.state.onOff,
            "temp": self.get_temperature(in_unit),
            "setTempHeat": self.get_tempHeat(in_unit),
            "setTempCool": self.get_tempCool(in_unit),
            "setMode": self.state.setMode,
            "mode": self.state.mode,
            "unit": in_unit,
        }
        return result

    def get_temperature(self, unit: str = "C"):
        """Return the temperature in the specified unit."""
        if self.state.temp is None:
            return None
        return TemperatureConverter(self.state.temp).get_temperature(unit)

    def set_temperature(self, temp, unit: str = "C"):
        """Return the temperature in the specified unit."""
        tt = TemperatureConverter(temp, unit).get_temperature(unit)
        self.state.temp = tt
        self.update_state()

    def set_temp_to_none(self):
        self.state.temp = None

    def set_tempCool(self, temp, unit: str = "C"):
        result = False  # default to not allowed
        if temp is None:
            return result

        # TODO: Make sure the band is considered properly and does not push
        # temp out of allowed range

        inTemp = TemperatureConverter(temp, unit).temp
        if inTemp < THERMOSTAT_COOL_MAXIMUM:
            if inTemp >= THERMOSTAT_COOL_MINIMUM + self.band:
                self.state.setTempCool = inTemp
                if inTemp < self.state.setTempHeat + self.band:
                    self.state.setTempHeat = inTemp - self.band
                result = True
        else:
            self.state.setTempCool = THERMOSTAT_COOL_MAXIMUM
            result = True

        return result

    def set_tempHeat(self, temp, unit: str = "C"):
        result = False  # default to not allowed
        if temp is None:
            return result
        inTemp = TemperatureConverter(temp, unit).temp
        if inTemp < THERMOSTAT_HEAT_MAXIMUM + self.band:
            if inTemp >= THERMOSTAT_HEAT_MINIMUM:
                self.state.setTempHeat = inTemp
                if inTemp > self.state.setTempCool - self.band:
                    self.state.setTempCool = inTemp + self.band
                result = True
        return result

    def get_tempCool(self, unit="C"):
        return TemperatureConverter(self.state.setTempCool).get_temperature(unit)

    def get_tempHeat(self, unit="C"):
        return TemperatureConverter(self.state.setTempHeat).get_temperature(unit)


class ThermostatOutdoorState(BaseModel):
    temp: float = Field(
        None,
        description="Outdoor temperature",
        eventId=RVEvents.THERMOSTAT_OUTDOOR_TEMPERATURE_CHANGE,
        setting=False,
    )


class ThermostatOutdoor(BaseComponent):
    """Outdoor temp sensor."""

    category: str = CATEGORY
    code: str = THERMOSTAT_CODE
    type: str = 'outdoor'
    # componentId: str = f"{CATEGORY}.{THERMOSTAT_CODE}_outdoor"
    state: ThermostatOutdoorState = ThermostatOutdoorState()
    attributes: dict = inject_parent_attr({
        'controllable': "NF"  # Near and Far field controlable
        })

    def get_temperature(self, unit: str = "C"):
        """Return the temperature in the specified unit."""
        if self.state.temp is None:
            return None
        return TemperatureConverter(self.state.temp).get_temperature(unit)

    def set_temperature(self, temp, unit: str = "C"):
        """Return the temperature in the specified unit."""
        tt = TemperatureConverter(temp, unit).get_temperature(unit)
        self.state.temp = tt
        self.update_state()

    def get_converted_state(self, in_unit: str = "C"):
        # Return the temperatures in the specified unit
        result = {
            "temp": self.get_temperature(unit=in_unit),
            "unit": in_unit,
        }
        return result

    def set_temp_to_none(self):
        self.state.temp = None


class HeaterState(BaseModel):
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.OFF,
        description="Heater On Off state from event values",
        eventId=RVEvents.ELECTRIC_HEATER_OPERATING_MODE_CHANGE,
        setting=False
    )


class HeaterBasic(BaseComponent):
    '''Basic heater that supports on off and is driven by the virtual thermostat.'''
    category: str = CATEGORY
    code: str = HEATER_CODE
    type: str = 'basic'
    # componentId: str = f"{CATEGORY}.{HEATER_CODE}_basic"
    state: HeaterState = HeaterState()


class HeaterSourceState(BaseModel):
    '''Virtual component to drive heat source settings.
    Elwell would provide additional attributes to refer fuel, furnace/heatpump use LP and Electric.
    '''
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.OFF,
        description="Current state of this heat source/pump",
        eventId=RVEvents.HEATER_MODE_CHANGE,
        setting=False
    )
    # NOTE: Removed EventValues.AUTO as per Marc F. on 05/14/24
    heatSrc: Literal[EventValues.ELECTRIC, EventValues.COMBUSTION] = Field(
        EventValues.ELECTRIC,
        description="Source of heat energy in case multiple sources are available",
        eventId=RVEvents.HEATER_ENERGY_SOURCE_CHANGE,
        setting=True,
        store_db=True
    )


class HeaterACHeatPump(BaseComponent):
    '''Virtual component to drive heatpump settings.'''
    category: str = CATEGORY
    code: str = HEATER_CODE
    type: str = 'heatpump'
    # componentId: str = f"{CATEGORY}.{HEATER_CODE}_heatpump"
    state: HeaterSourceState = HeaterSourceState()
    attributes: dict = inject_parent_attr({})


class RoofFanAdvancedState(BaseModel):
    '''State for Dometic or similar fans based on RV-C'''
    onOff: Optional[Literal[
            EventValues.OFF,
            EventValues.ON]] = Field(
        None,
        description="Overall system mode onOff for the Roof fan",
        eventId=RVEvents.ROOF_VENT_OPERATING_MODE_CHANGE,
        setting=True,
        # TODO: Figure out if an initial value is possible
        # initial=TBD,
        # store_db=True
    )
    dome: Optional[Literal[
        # supporting legacy UI for the HMI until that has been
        # updated with the new event values
        # TODO: Delete ON/OFF after
        # - HMI OK
        # - APP OK
        # EventValues.OFF,
        # EventValues.ON,
        EventValues.CLOSED,
        EventValues.OPENED
    ]] = Field(
        None,
        description="Dome status for RV-C, Opened, Closed",
        eventId=RVEvents.ROOF_VENT_DOME_POSITION_CHANGE,
        setting=True,
        # TODO: Figure out if an initial value is possible
        # initial=TBD,
        # store_db=True
    )
    direction: Optional[Literal[
        EventValues.FAN_OUT,
        EventValues.FAN_IN
    ]] = Field(
        None,
        description="Fan wind direction, IN/OUT",
        eventId=RVEvents.ROOF_VENT_FAN_DIRECTION_CHANGE,
        # TODO: Figure out if an initial value is possible
        # initial=TBD,
        setting=False
    )
    fanSpd: Optional[Literal[
        # EventValues.OFF,
        EventValues.LOW,
        EventValues.MEDIUM,
        EventValues.HIGH
    ]] = Field(
        None,
        description="Speed of the fan in ",
        eventId=RVEvents.ROOF_VENT_FAN_SPEED_CHANGE,
        # TODO: Figure out if an initial value is possible
        # initial=TBD,
        setting=True,
        # store_db=True
    )
    rain: Optional[Literal[
        EventValues.OFF,
        EventValues.ON
    ]] = Field(
        None,
        description="State of the rain sensor, not available on all fans",
        eventId=RVEvents.ROOF_VENT_RAIN_SENSOR_CHANGE,
        setting=True,
        # TODO: Figure out if an initial value is possible
        # initial=TBD,
        # store_db=True
    )


class RoofFanAdvanced(BaseComponent):
    '''Model for somewhat advanced roof fan, Dometic and other RV-C compatible fans.'''
    category: str = CATEGORY
    code: str = ROOFFAN_CODE
    type: str = 'advanced'
    # componentId: str = f"{CATEGORY}.{ROOFFAN_CODE}_advanced"
    state: RoofFanAdvancedState = RoofFanAdvancedState()

    def set_state(self, state):
        new_state = RoofFanAdvancedState(**state)
        print('SET STATE FAN', new_state)
        _ = self.hal.climate.handler.new_fan_control(
            self.instance,
            new_state
        )
        # _ = self.hal.climate.handler.fan_control(
        #     self.instance,
        #     new_state.onOff,
        #     new_state.fanSpd,
        #     new_state.direction,
        #     new_state.dome,
        #     new_state.rain,
        # )
        # Emit state events
        super().set_state(None)

        return self.state


class ACBasicState(BaseModel):
    """State for Air Conditioner Only"""
    # NOTE: Used for W44R and ERV2, needs proper implementation to support wired ACs
    comp: Optional[Literal[EventValues.OFF, EventValues.ON]] = Field(
        EventValues.OFF,
        description="Command the AC compressor to Run for Cooling",
        eventId=RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
        setting=False
    )
    # Fan Speed is the actual speed, while mode is the desired speed that informs the algo
    fanSpd: Optional[Literal[EventValues.OFF, EventValues.LOW, EventValues.MEDIUM, EventValues.HIGH]] = Field(
        None,
        description="Actual speed of the fan in the AC Unit",
        eventId=RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
        setting=False,
        store_db=False
    )
    fanMode: Optional[
                Literal[
                    # Conditional, if in FAN ONLY thermostat mode, we turn it off, otherwise we run AUTO
                    EventValues.AUTO_OFF,
                    EventValues.LOW,
                    EventValues.HIGH]] = Field(
        None,
        description="Desired Fan Speed mode",
        initial=EventValues.AUTO_OFF,
        eventId=RVEvents.AIR_CONDITIONER_FAN_MODE_CHANGE,
        setting=True,
        store_db=True
    )


class ACBasic(BaseComponent):
    '''Model to support wire based AC units such Premier and Coleman-Mach.'''
    category: str = CATEGORY
    code: str = HVAC_CODE
    type: str = 'wired'
    state: ACBasicState = ACBasicState()

    def set_state(self, state):
        new_state = ACBasicState(**state)

        if new_state.fanMode is not None:
            # Set the mode in the HAL
            # On successful return set the state and return it
            pass

        return self.state


class RefrigeratorState(BaseModel):
    temp: float = Field(
        None,
        description="Refrigerator temperature",
        eventId=RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
        setting=False,
    )


class RefrigeratorBasic(BaseComponent):
    '''Model for basic refrigerator.'''
    category: str = CATEGORY
    code: str = REFRIGERATOR_CODE
    type: str = 'basic'
    # componentId: str = f"{CATEGORY}.{REFRIGERATOR_CODE}_basic"
    state: RefrigeratorState = RefrigeratorState()

    def get_temperature(self, unit: str = "C"):
        """Return the temperature in the specified unit."""
        if self.state.temp is None:
            return None
        return TemperatureConverter(self.state.temp).get_temperature(unit)

    def set_temperature(self, temp, unit: str = "C"):
        """Return the temperature in the specified unit."""
        print('Setting fridge temp', temp, type(temp))
        tt = TemperatureConverter(temp, unit).get_temperature(unit)
        print('Conversion result fridge', tt)
        self.state.temp = tt

    def get_converted_state(self, in_unit: str = "C"):
        # Return the temperatures in the specified unit
        result = {
            "temp": self.get_temperature(unit=in_unit),
            "unit": in_unit,
        }
        return result


class AmbientTempSensor(BaseModel):
    temperature: Optional[float]
    temp: Optional[float]
    unit: str


class FanSpeedEnum(int, Enum):
    off = EventValues.OFF.value
    low = EventValues.LOW.value
    med = EventValues.MEDIUM.value
    high = EventValues.HIGH.value


class ACFanSpeedEnum(int, Enum):
    auto_off = EventValues.AUTO_OFF.value
    low = EventValues.LOW.value
    high = EventValues.HIGH.value


# class TempUnitEnum(str, Enum):
#     fahrenheit = "F"
#     celcius = "C"
#     # kelvin = 'K'


# TODO: Enum is used in api_home.py, do we really need this ? And is this the right place ?

class HVACModeEnum(int, Enum):
    AUTO = EventValues.AUTO.value
    HEAT = EventValues.HEAT.value
    COOL = EventValues.COOL.value
    FAN_ONLY = EventValues.FAN_ONLY.value
    OFF = EventValues.OFF.value
    STANDBY = EventValues.STANDBY.value
    ERROR = EventValues.FAULT.value


# class FanDirectionEnum(int, Enum):
#     fan_out = EventValues.FAN_OUT.value
#     fan_in = EventValues.FAN_IN.value


class Temperature(BaseModel):
    """Temperature message for setting and getting."""

    temp_set: Optional[float]
    temp_current: Optional[float]


# TODO: See how literal could be beneficial
class AcRvcGeState(BaseModel):
    comp: Optional[Literal[EventValues.OFF, EventValues.ON]] = Field(
        EventValues.OFF,
        description="Is the compressor on or off",
        eventId=RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
        setting=False,
    )
    fanMode: Optional[
                Literal[
                    # Conditional, if in FAN ONLY thermostat mode, we turn it off, otherwise we run AUTO
                    EventValues.AUTO_OFF,
                    EventValues.LOW,
                    EventValues.HIGH]] = Field(
        None,
        description="Desired Fan Speed mode",
        initial=EventValues.AUTO_OFF,
        eventId=RVEvents.AIR_CONDITIONER_FAN_MODE_CHANGE,
        setting=True,
        store_db=True
    )
    fanSpd: Optional[
                Literal[
                    EventValues.OFF,
                    EventValues.LOW,
                    EventValues.HIGH]] = Field(
        None,
        description="Actual current Fan Speed",
        # TODO: Check that we do not need an initial value
        initial=EventValues.OFF,
        eventId=RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
        setting=False,
    )


class AcRvcGe(BaseComponent):
    """Model for GE RVC AC."""
    category: str = CATEGORY
    code: str = HVAC_CODE
    type: str = 'rvc_ge'
    # componentId: str = f"{CATEGORY}.{HVAC_CODE}_rvc_ge"
    state: AcRvcGeState = AcRvcGeState()
    optionCodes: str = '29J'

    def set_state(self, state):
        new_state = AcRvcGeState(**state)

        wgo_logger.debug(f'CLIMATE AC Setting new state: {new_state}')
        # Apply the mode as a setting
        if state.get('fanMode') is not None:
            # We need to check the incoming dict if mode is there or not
            # Otherwise it will use the default, which is OFF
            self.state.fanMode = new_state.fanMode

        self.hal.climate.handler.set_ac_state(new_state)

        super().set_state(None)
        self.save_db_state()

        return self.state


class AcRvcTrumaState(BaseModel):
    '''State for Truma RVC AC.'''
    comp: Literal[
        EventValues.OFF,
        EventValues.ON
    ] = Field(
        None,
        description="Is the compressor on or off",
        eventId=RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
        setting=False,
    )
    fanMode: Literal[
        EventValues.AUTO_OFF,
        EventValues.LOW,
        EventValues.MEDIUM,
        EventValues.HIGH,
    ] = Field(
        EventValues.AUTO_OFF,
        description="Desired Fan Speed mode",
        eventId=RVEvents.AIR_CONDITIONER_FAN_MODE_CHANGE,
        setting=True,
        store_db=True
    )
    fanSpd: Literal[
        EventValues.OFF,
        EventValues.LOW,
        EventValues.MEDIUM,
        EventValues.HIGH
    ] = Field(
        None,
        description="Actual current Fan Speed",
        eventId=RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
        setting=False
    )


class AcRvcTruma(BaseComponent):
    """Model for Truma RVC AC."""
    category: str = CATEGORY
    code: str = HVAC_CODE
    type: str = 'rvc_truma'
    # componentId: str = f"{CATEGORY}.{HVAC_CODE}_rvc_truma"
    state: AcRvcTrumaState = AcRvcTrumaState()
    optionCodes: str = '291'    # Specific component, so define optioncode here

    def set_state(self, state):
        print('Setting TRUMA AC STATE', state)
        new_state = AcRvcTrumaState(**state)

        print('Setting new state', new_state)
        # Apply the mode as a setting
        if state.get('fanMode') is not None:
            self.state.fanMode = new_state.fanMode
        # else:
        #     self.state.fanMode = EventValues.AUTO_OFF

        print('State', self.state)

        # Using thermostat based setting
        self.hal.climate.handler.set_ac_state_thermostat(new_state)

        # Emit state events
        super().set_state(None)

        self.save_db_state()

        return self.state


class ThermostatWiredState(ThermostatState):
    """Virtual Thermostat state for wired (non RV-C/CAN) AC units"""
    # Wired Thermostat State is the same for now, but we will override methods here when needed

class ThermostatWired(Thermostat):
    """Wire Virtual Thermostat."""
    # Wired Thermostat State is the same for now, but we will override methods here when needed

    # override the state to use the wired state in preperation for the chages
    state: ThermostatWiredState = ThermostatWiredState()


if __name__ == "__main__":
    # Create a Temperature instance with an initial value of 25 degrees Celsius
    # Create a Temperature instance with an initial value of 25 degrees Celsius
    temp = TemperatureConverter()

    temp.set_temperature(25)

    # Get the temperature in Celsius and Fahrenheit
    print(temp.get_temperature())  # Output: 25
    print(temp.get_temperature("F"))  # Output: 77.0

    temp.set_temperature(30)
    # Set the temperature to 32 degrees Fahrenheit
    temp.set_temperature(32, "F")
    print(temp.get_temperature())  # Output: 0.0

    tstat = Thermostat(instance=1, name="name", description="No description", state=ThermostatState({}))

    tstat.set_temperature(30)

    print(tstat, "\n\n")
    tstat.set_tempCool(78, "F")

    if tstat.set_tempHeat(74, "F"):
        print("\ndict \n\n", tstat.state.__dict__)
    else:
        print("Fail")
