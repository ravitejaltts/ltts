from optparse import Option
from typing import Optional, List, Union
from enum import Enum, IntEnum

from pydantic import BaseModel, Field

try:
    from common import BaseComponent, ComponentTypeEnum
except ImportError as err:
    from .common import (
        BaseComponent,
        ComponentTypeEnum
    )

try:
    from common_libs.models.common import RVEvents, EventValues
except ImportError as err:
    import sys
    import os
    abs_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
    add_path = os.path.join(abs_path, '../')
    sys.path.append(
        add_path
    )
    from  common_libs.models.common import RVEvents, EventValues


CATEGORY = 'climate'

HEATER_CODE = 'he'
THERMOSTAT_CODE = 'th'
REFRIGERATOR_CODE = 'rf'
ROOFFAN_CODE = 'rv'


# Virtual Thermostat (temp, setTempHeat, setTempCool)
# Roof Fan Dometic (dome, speed, onOff, direction, rain)
# AC Unit (compressor, fan)
# Heater (onOff)
# Heater Elwell / Truma ?


class ThermostatState(BaseModel):
    onOff: Optional[int] = Field(
        EventValues.OFF,
        values=[
            EventValues.OFF,
            EventValues.ON
        ],
        description='Thermostat overall state, if off all climate functionality in this zone is off'
    )
    temp: Optional[float] = Field(
        None,
        ge=-273,
        le=1700,    # TODO: Fix that to the right value
        description='Interior temperature for that zone',
        eventId=RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE,
        setting=False
    )
    setTempHeat: Optional[float] = Field(
        None,
        ge=-273,    # TODO: Get this from business rules
        le=1700,    # TODO: Get this from business rules,
        description='Temperature the heating system shall maintain if in auto or heat mode',
        eventId=RVEvents.THERMOSTAT_CURRENT_HEAT_TEMPERATURE_SET_CHANGE,
        setting=True
    )
    setTempCool: Optional[float] = Field(
        None,
        ge=-273,    # TODO: Get this from business rules
        le=1700,    # TODO: Get this from business rules,
        description='Temperature the cooling system shall maintain if in auto or cool mode',
        eventId=RVEvents.THERMOSTAT_CURRENT_COOL_TEMPERATURE_SET_CHANGE,
        setting=True
    )
    # Mode is what the user sets in the UI
    setMode: Optional[int] = Field(
        EventValues.OFF,
        description='Mode the climate system is set to by user',
        values=[
            EventValues.OFF,
            EventValues.AUTO,
            EventValues.HEAT,
            EventValues.COOL,
            EventValues.FAN_ONLY
        ],
        eventId=RVEvents.THERMOSTAT_OPERATING_MODE_CHANGE,
        setting=True
    )
    # mode is new to indicate the current system mode
    # TODO: Can this work in the twin using desired and reported being somewhat not aligned
    mode: Optional[int] = Field(
        EventValues.OFF,
        description='The mode the system is currently operating in',
        values=[
            EventValues.OFF,        # System is off and not doing anything
            EventValues.HEAT,       # System is currently heating
            EventValues.COOL,       # System is currently cooling
            EventValues.FAN_ONLY,   # Fan only mode, do we need this ?
            EventValues.STANDBY     # System is in standby, should that be called idle ?
        ],
        eventId=RVEvents.THERMOSTAT_CURRENT_OPERATING_MODE_CHANGE,
        setting=False
    )
    unit: Optional[str] = Field(
        'F',
        values=[
            'F',
            'C'
        ],
        description='Unit of temperature',
        setting=True
    )
    # Other stuff


class Thermostat(BaseComponent):
    '''Basic virtual Thermostat.'''
    category: str = CATEGORY
    code: str = THERMOSTAT_CODE
    # subType: str = None
    componentId: str = f'{THERMOSTAT_CODE}_virtual'
    state: ThermostatState
    attributes: dict = {}


class HeaterState(BaseModel):
    onOff: int = Field(
        None,
        ge=0,
        le=1,
        description='Heater On Off state as int',
        eventId=RVEvents.ELECTRIC_HEATER_OPERATING_MODE_CHANGE
    )


class HeaterBasic(BaseComponent):
    '''Basic heater that supports on off and is driven by the virtual thermostat.'''
    category: str = CATEGORY
    code: str = HEATER_CODE
    # subType: str=None
    componentId: str = f'{HEATER_CODE}_basic'
    state: HeaterState


class HeaterSourceState(BaseModel):
    '''Virtual component to drive heat source settings.
    Elwell would provide additional attributes to refer fuel, furnace/heatpump use LP and Electric.
    '''
    src: int = Field(
        EventValues.ELECTRIC,
        description='Source of heat energy in case multiple sources are available',
        values=[
            EventValues.ELECTRIC,
            EventValues.COMBUSTION,
            EventValues.AUTO
        ],
        eventId=RVEvents.HEATER_ENERGY_SOURCE_CHANGE
    )


class HeaterACHeatPump(BaseComponent):
    '''Virtual component to drive heatpump settings.'''
    category: str = CATEGORY
    code: str = HEATER_CODE
    # subType: str=None
    componentId: str = f'{HEATER_CODE}_heatpump'
    state: HeaterSourceState


class RoofFanAdvancedState(BaseModel):
    '''State for Dometic or similar fans based on RV-C'''
    onOff: Optional[int] = Field(
        EventValues.OFF,
        values=[
            EventValues.ON,
            EventValues.OFF
        ],
        description='Overall system mode onOff for the Roof fan',
        eventId=RVEvents.ROOF_VENT_OPERATING_MODE_CHANGE,
    )
    dome: Optional[int]  = Field(
        EventValues.CLOSED,
        values=[
            EventValues.OPENED,
            EventValues.CLOSED
        ],
        description='Dome status for RV-C, Opened, CLosed',
        eventId=RVEvents.ROOF_VENT_DOME_POSITION_CHANGE
    )
    direction: Optional[int] = Field(
        EventValues.FAN_OUT,
        values=[
            EventValues.FAN_IN,
            EventValues.FAN_OUT],
        example=EventValues.FAN_OUT,
        description='Fan wind direction, IN/OUT',
        eventId=RVEvents.ROOF_VENT_FAN_DIRECTION_CHANGE
    )
    fanSpd: Optional[int] = Field(
        EventValues.MEDIUM,
        values=[
            EventValues.OFF,
            EventValues.LOW,
            EventValues.MEDIUM,
            EventValues.HIGH
        ],
        description='Speed of the fan in ',
        eventId=RVEvents.ROOF_VENT_FAN_SPEED_CHANGE
    )
    rain: Optional[int] = Field(
        EventValues.OFF,
        values=[
            EventValues.OFF,
            EventValues.ON
        ],
        description='State of the rain sensor, not available on all fans',
        eventId=RVEvents.ROOF_VENT_RAIN_SENSOR_CHANGE
    )


class RoofFanAdvanced(BaseComponent):
    '''Model for somewhat advanced roof fan, Dometic and other RV-C compatible fans.'''
    category: str = CATEGORY
    code: str = ROOFFAN_CODE
    # subType: str = None
    componentId: str = f'{ROOFFAN_CODE}_advanced'
    state: RoofFanAdvancedState


class ACBasicState(BaseModel):
    '''State for Air Conditioner Only'''
    onOff: Optional[int] = Field(
        EventValues.OFF,
        values=[
            EventValues.OFF,
            EventValues.ON
        ],
        description='Command the AC to Run for Cooling',
        eventId=RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE
    )
    # Fan Speed
    fanSpd: Optional[int] = Field(
        EventValues.MEDIUM,
        values=[
            EventValues.OFF,
            EventValues.LOW,
            EventValues.MEDIUM,
            EventValues.HIGH
        ],
        description='Speed of the fan in the AC Unit',
        eventId=RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE
    )


class ACBasic(BaseComponent):
    pass


class RefrigeratorState(BaseModel):
    temp: Optional[float] = Field(
        None,
        ge=-273,
        le=1700,    # TODO: Fix that to the right value
        description='Refrigerator/Freezer Temp',
        eventId=RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
        setting=False
    )


class RefrigeratorBasic(BaseComponent):
    '''Model for basic refrigerator.'''
    category: str = CATEGORY
    code: str = REFRIGERATOR_CODE
    # subType: str = None
    componentId: str = f'{REFRIGERATOR_CODE}_basic'
    state: RefrigeratorState


if __name__ == '__main__':
    pass
