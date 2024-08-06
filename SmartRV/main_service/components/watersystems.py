from optparse import Option
from typing import Optional, List, Union, Literal
from enum import Enum, IntEnum

from pydantic import BaseModel, Field

from main_service.components.common import (
    BaseComponent,
    inject_parent_attr,
)

from common_libs.models.common import RVEvents, EventValues


CATEGORY = 'watersystems'


class BaseWaterSystem(BaseModel):
    id: int
    name: str
    description: str
    type: str
    subType: Optional[str]
    state: Optional[dict]


class SIMPLE_WATER_HEATER_STATE(BaseModel):
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.OFF,  # Circuit defaults to off
        description='Current state of the water heater, 0 off, 1 on, 2 future use for auto mode'
    )


class ToiletCircuitState(BaseModel):
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.ON,  # Circuit defaults to on - off if Black tank is full
        description='Toilet Circuit onOff state'
    )


class ToiletCircuitDefault(BaseComponent):
    category: str = CATEGORY
    code: str = 'tc'
    type: str = 'default'
    # componentId: str = f"{CATEGORY}.wp_default"
    state: ToiletCircuitState = ToiletCircuitState()


class SIMPLE_TANK_STATE(BaseModel):
    lvl: float = Field(
        0,
        description='Level in %',
        minimum=0,
        maximum=100
    )
    # cap: Optional[float] = Field(
    #     description='Capacity in the given unit'
    # )
    unit: Optional[str] = Field(
        'G',
        description='Capacity unit'
    )


class WaterTankState(BaseModel):
    lvl: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description='Level of the given tank in % between 0 - 100%',
        eventId=RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE,
        setting=False
    )
    # cap: Optional[float] = Field(
    #     None,
    #     ge=0.0,
    #     description='Capacity of the tank',
    #     setting=False
    # )
    vltg: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description='Current voltage value',
        setting=False
    )
    vltgMin: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description='Voltage level for empty',
        setting=True,
        save_db=True
    )
    vltgMax: Optional[float] = Field(
        None,
        ge=0.0,
        le=5.0,
        description='Voltage level for full',
        setting=True,
        save_db=True
    )
    mode: Literal[EventValues.TANK_FILLING, EventValues.TANK_STEADY, EventValues.TANK_DRAINING] = Field(
        None,
        description='Current state of the tank, calculated from changes to previous level reading.',
        setting=False,
        eventId=None
    )
    # fill: Optional[float] = Field()   # New field, to avoid conversion issues, this is the fill level in the users unit
    # # _fill_eventId:
    # unit: str = Field(
    #     'GALLONS',
    #     description='Units of measurement',
    #     values=[
    #         'GALLONS',
    #         'LITERS'
    #     ]
    # )
    # cap: int=Field(
    #     None,
    #     ge=0,
    #     eventId=8601
    # )   # capacity In the user unit
    # type: str = Field(
    #         'FRESH|GREY|BLACK|PROPANE|?',
    #         description='Type of water always stored in the tank'
    #     )


class WaterTankDefault(BaseComponent):
    category: str = CATEGORY
    code: str = 'wt'
    type: str = 'default'
    state: WaterTankState = WaterTankState()

    def set_state(self, state):
        new_state = WaterTankState(**state)

        if new_state.lvl is not None:
            previous_lvl = self.state.dict().get('lvl')
            self.state.lvl = new_state.lvl

            # TODO: Improve this check to consider longer times and put it into runtime data
            if previous_lvl is not None:
                if previous_lvl > self.state.lvl:
                    self.state.mode = EventValues.TANK_FILLING
                elif previous_lvl < self.state.lvl:
                    self.state.mode = EventValues.TANK_DRAINING
                else:
                    self.state.mode = EventValues.TANK_STEADY

        if new_state.vltgMin is not None:
            self.state.vltgMin = new_state.vltgMin

        if new_state.vltgMax is not None:
            self.state.vltgMax = new_state.vltgMax

        super().set_state(None)

        # TODO: Add save DB state when merged with latest develop

        return self.state

    def update_can_state(self, msg_name, can_msg) -> dict:
        '''Read fluid level for fuel tank and scale as needed.'''
        raise NotImplementedError('Component update can state not implemented for Water Tank')



class WaterPumpState(BaseModel):
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.OFF,
        description='Water pump onOff state',
        eventId=RVEvents.WATER_PUMP_OPERATING_MODE_CHANGE
    )


class WaterPumpDefault(BaseComponent):
    category: str = CATEGORY
    code: str = 'wp'
    type: str = 'default'
    # componentId: str = f"{CATEGORY}.wp_default"
    state: WaterPumpState = WaterPumpState()

    def set_state(self, state):
        new_state = WaterPumpState(**state)

        if new_state.onOff is not None:
            self.hal.watersystems.handler.pump_switch(self, new_state)
            self.state.onOff = new_state.onOff

        self.update_state()
        return self.state


class WaterHeaterSimpleState(BaseModel):
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.OFF,
        description='Simple Heater on/off state',
        eventId=RVEvents.WATER_HEATER_ONOFF_CHANGE,
        setting=True
    )
    lockouts: Optional[List[int]] = Field(
        [],
        description='List of lockouts present',
        setting=False
    )


class WaterHeaterSimple(BaseComponent):
    '''Component used for a simple water heater that can only be turned on/off.'''
    category: str = CATEGORY
    code: str = 'wh'
    type: str = 'simple'
    state: WaterHeaterSimpleState = WaterHeaterSimpleState()


class WaterHeaterRvcState(BaseModel):
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        None,
        description='Overall On/Off state',
        eventId=RVEvents.WATER_HEATER_ONOFF_CHANGE,
        setting=True
    )
    mode: Literal[
            EventValues.OFF,
            EventValues.COMFORT,
            EventValues.ANTI_FREEZE,
            EventValues.DECALCIFICATION,
            EventValues.ECO] = Field(
        None,
        eventId=RVEvents.WATER_HEATER_OPERATING_MODE_CHANGE,
        description='RVC (Truma) settings for mode, such as comfort and eco',
        setting=True,
        initial=EventValues.COMFORT
    )
    op_mode: Literal[
            EventValues.OFF,
            EventValues.COMFORT,
            EventValues.ANTI_FREEZE,
            EventValues.DECALCIFICATION,
            EventValues.ECO] = Field(
        None,
        description='Reported when it is operating (toggles in COMFORT as it heats)',
        setting=False
    )
    temp: float = Field(
        None,
        eventId=RVEvents.WATER_HEATER_WATER_TEMPERATURE_CHANGE,
        description='The current temperature as given by the water heater',
        setting=False
    )
    setTemp: Optional[float] = Field(
        None,        # TODO: What is the desired default set temp ?
        ge=35.0,
        le=49.0,
        initial=45.0,   # Used for defaults that cannot be in the standard place above
        description='Temperature set to achieve when water heater is on',
        eventId=RVEvents.WATER_HEATER_WATER_SET_TEMPERATURE_CHANGE,
        setting=True
    )
    unit: Optional[str] = Field(
        'C',
        description='The unit the API is currently reporting on',
        values=[
            'F',
            'C'
        ],
        setting=True        # Don't like it !
    )
    lockouts: Optional[List[int]] = Field(
        [],
        description='List of lockouts present',
        setting=False
    )


class WaterHeaterRvc(BaseComponent):
    category: str = CATEGORY
    code: str = 'wh'
    type: str = 'rvc'
    # componentId: str = f'{CATEGORY}.wh_rvc'
    # TODO: Update to
    state: WaterHeaterRvcState = WaterHeaterRvcState()
    # attributes: list = ...
    attributes: dict = inject_parent_attr({
        "lockoutStates": [
            {
                'eventValue': EventValues.DECALC_WATERHEATER_LOCKOUT,
                'triggerValue': True
            }
        ]
    })

    def set_state(self, state):
        new_state = WaterHeaterRvcState(**state)

        self.check_lockouts()

        if self.state.lockouts:
            raise ValueError(f'Lockouts prevent setting state: {self.state.lockouts}')

        if new_state.setTemp is not None:
            print(f'Water Heater temp request {new_state.setTemp}')

            set_temp_prop = self.state.schema().get('properties', {}).get('setTemp')

            if new_state.setTemp < set_temp_prop['minimum'] or new_state.setTemp > set_temp_prop['maximum']:
                print(f'Must be between: {set_temp_prop["minimum"]} and {set_temp_prop["maximum"]}')
                return self.state
            else:
                self.state.setTemp = new_state.setTemp

        if new_state.onOff is not None:
            self.state.onOff = new_state.onOff
            if new_state.onOff == EventValues.OFF:
                new_state.mode = EventValues.OFF

        if new_state.mode is not None and new_state.mode != EventValues.OFF:
            self.state.mode = new_state.mode
        elif new_state.mode == EventValues.OFF:
            self.state.onOff = EventValues.OFF

        self.hal.watersystems.handler.set_water_heater_state(
            self.instance
        )
        # Emit state events
        super().set_state(None)
        return self.state

    def update_can_state(self, msg_name, can_msg) -> dict:
        '''Handle CAN updates for Water Tanks.'''
        # TODO: WIP
        updated = False
        state = None

        raise NotImplementedError('Water heater update state not implemented')

        # Get the voltage for battery readings
        # Get the lvl for fluid level readings


class TankHeatingPadState(BaseModel):
    # User enabled needed so set state logic actually only applies power when temp is below 40 F
    onOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.ON,
        description='User setting to enable the circuit.',
        eventId=RVEvents.WATER_HEATER_ONOFF_CHANGE,  # Must use onOff here MODE change here breaks event code reporting
        setting=True,
        save_db=True
    )
    cirOnOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.ON,
        #eventId=RVEvents.WATER_HEATER_XXX_CHANGE,  # PROPOSED change to report circuit state ( keep onOFF for that name only)
        description='Auto enganged tank heating pad with built in thermal sensor',
        setting=False
    )


class TankHeatingPad(BaseComponent):
    category: str = CATEGORY
    code: str = 'wh'
    type: str = 'tankpad'
    # componentId: str = f'{CATEGORY}.wh_tankpad'
    state: TankHeatingPadState = TankHeatingPadState()

    def set_state(self, in_state: dict) -> TankHeatingPadState:
        new_state = TankHeatingPadState(**in_state)

        # This method will be called whenever you assign a new value to 'state'
        self.state.onOff = new_state.onOff

        self.hal.watersystems.handler.check_tank_pad_state(
            self.instance
        )

        super().set_state(None)  # emit the events
        return self.state


if __name__ == '__main__':
    import json

    from helper import generate_component

    tank = WaterTankDefault(
        instance=1,
        meta={
            'name': 'Test'
        },
        # TODO can this become part of the state as below - example capacity is another 'state' item that would not change
        type='FRESH',
        state=WaterTankState(
            type='FRESH',
            lvl=40,
            fill=12.4,
            unit="GALLONS",
            cap=31.0
        )
    )

    # schema_list(
    #     (WaterTankDefault, WaterPumpDefault, WaterHeaterSimple)
    # )

    for component in (WaterTankDefault, WaterPumpDefault, WaterHeaterSimple):
        print(json.dumps(generate_component(component), indent=4))

    heater_state = WaterHeaterRvcState()
    print(heater_state.schema_json())
    print(heater_state.schema().get('properties', {}).get('setTemp'))
