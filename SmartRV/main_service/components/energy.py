from typing import Optional, List, Literal
import time

from pydantic import BaseModel, Field

from main_service.components.common import (
    BaseComponent,
    ComponentTypeEnum,
    LockoutListItem,
    LockoutTimer,
    inject_parent_attr,
)

from main_service.components.system import (
    ActionTracker
)

from common_libs.models.common import RVEvents, EventValues
from datetime import datetime, timedelta
from common_libs.system.scheduled_function import ScheduledFunction

CATEGORY = "energy"
COMP_TYPE_ENERGY_MANAGE = "em"
COMP_TYPE_BATTERY_MANAGE = "bm"
COMP_TYPE_ENERGY_SOURCE = 'es'
COMP_TYPE_ENERGY_CONSUMER = 'ec'
COMP_TYPE_GENERATOR = 'ge'
COMP_TYPE_BATTERY = 'ba'
COMP_TYPE_INVERTER = 'ei'
COMP_TYPE_CHARGER = 'ic'
COMP_TYPE_FUEL_TANK = 'ft'
COMP_TYPE_LOAD_SHEDDING = 'ls'

DATA_INVALID = 'Data Invalid'   # As set in the NMEA2K / Other DBC files
# Sources/Chargers
# - Shore
# - Vehicle
# - Solar

# Consumers
# AC / DC (Combine and use subType ?)
# AC
# DC

# Batteries
# Inverter

# Load Shedding State


class InverterBasicState(BaseModel):
    '''State for simple inverter that can only be turned on/off.'''
    onOff: int = Field(
        None,
        ge=0,
        le=1,
        description="Inverter on/off state",
        eventId=RVEvents.INVERTER_CHARGER_INVERTER_MODE_CHANGE,
        setting=True,
        store_db=True
    )


class InverterBasic(BaseComponent):
    """Inverter model for basic inverter such as Victron without CerboGX."""

    category: str = CATEGORY
    code: str = "ei"
    type: str = 'basic'
    # componentId: str = "ei_basic"
    state: InverterBasicState = InverterBasicState()


class InverterAdvancedState(BaseModel):
    '''State for advanced inverters with more control.

    Applies to:
        - Victron with CerboGX
        - XANTREX
    '''
    onOff: Literal[
            EventValues.OFF,
            EventValues.ON] = Field(
        EventValues.OFF,
        description="Inverter on/off state",
        eventId=RVEvents.INVERTER_CHARGER_INVERTER_MODE_CHANGE,
        setting=True,
        store_db=True
    )
    load: int = Field(
        None,
        ge=0,
        description='Load in watts on the output of the inverter.',
        eventId=RVEvents.INVERTER_LOAD_CHANGE,
        setting=False
    )
    overld: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.FALSE,
        description='Is the inverter currently in overload.',
        eventId=RVEvents.INVERTER_OVERLOAD_CHANGE,
        setting=False
    )
    overldTimer: float = Field(
        None,
        description='Seconds since entering overload state',
        eventId=None,
        setting=False
    )
    rmsVoltage: float = Field(
        None,
        description='AC Voltage reported by the inverter',
        eventId=None,
        setting=False
    )
    rmsCurrent: float = Field(
        None,
        description='AC Current reported by the inverter',
        eventId=None,
        setting=False
    )
    frequency: float = Field(
        None,
        description='AC Frequency reported by the inverter',
        eventId=None,
        setting=False
    )
    maxLoad: int = Field(
        None,       # This should be set from the template
        # during initialization it should read state.maxLoad from the attributes
        description='Max Duty WATTS allowed for the inverter',
        # Set a valid range for the max load
        ge=0,           # TODO: Check this value
        le=5000,        # TODO: Check this value
        eventId=None,   # eventId=RVEvents.INVERTER_MAX_LOAD_CHANGE,
        setting=False   # This may change depending on the power source
    )
    # TDDO: Would a temperature compensation work here for MaxLoad ?

    # TODO: Check if the EcoFlow system fits


class InverterAdvanced(BaseComponent):
    """Inverter model for basic inverter such as Victron without CerboGX."""

    category: str = CATEGORY
    code: str = COMP_TYPE_INVERTER
    type: str = 'rvc'
    # componentId: str = f'{CATEGORY}.{COMP_TYPE_INVERTER}_rvc'
    state: InverterAdvancedState = InverterAdvancedState()
    # Attributes need to define continous max load here
\
    def update_can_state(self, msg_name, can_msg) -> dict:
        '''Update the state based on the CAN message received.'''

        print('>' * 40, "InverterAdvanced", msg_name, can_msg)
        if msg_name == 'inverter_ac_status_1':
            try:
                self.state.rmsVoltage = float(can_msg.get('RMS_Voltage'))
            except ValueError as e:
                self.state.rmsVoltage = None
                print('Inverter RMS_Voltage ValueError', e)
            except TypeError as e:
                self.state.rmsVoltage = None
                print('Inverter RMS_Voltage TypeError', e)

            try:
                self.state.rmsCurrent = float(can_msg.get('RMS_Current'))
            except ValueError as e:
                self.state.rmsCurrent = None
                print('Inverter RMS_Current ValueError', e)
            except TypeError as e:
                self.state.rmsCurrent = None
                print('Inverter RMS_Current TypeError', e)

            try:
                self.state.frequency = float(can_msg.get('Frequency'))
            except ValueError as e:
                self.state.frequency = None
                print('Inverter Frequency ValueError', e)
            except TypeError as e:
                self.state.frequency = None
                print('Inverter Frequency TypeError', e)

            if self.state.rmsVoltage is not None and self.state.rmsCurrent is not None:
                self.state.load = int(self.state.rmsVoltage * self.state.rmsCurrent)
                if self.state.load > self.state.maxLoad:
                    self.state.overld = EventValues.TRUE
                    if self.state.overldTimer == 0:
                        self.state.overldTimer = time.time()
                else:
                    self.state.overld = EventValues.FALSE
                    self.state.overldTimer = 0

            print(
                '$' * 30, 'voltage',
                self.state.rmsVoltage,
                type(self.state.rmsVoltage),
                'current',
                self.state.rmsCurrent,
                type(self.state.rmsCurrent)
            )
            print('<' * 40)
            self.update_state()
            return self.state

        else:
            print(f'[InverterAdvanced] Unknown message {msg_name} received')
            return None



class ChargerAdvancedState(BaseModel):
    '''State for advanced inverter/charger with more control.

    Applies to:
        - XANTREX
    '''
    # onOff: Literal[
    #         EventValues.OFF,
    #         EventValues.ON] = Field(
    #     EventValues.OFF,
    #     description="Inverter on/off state",
    #     eventId=RVEvents.INVERTER_CHARGER_INVERTER_MODE_CHANGE,
    #     setting=True
    # )
    # load: int = Field(
    #     0,
    #     ge=0,
    #     description='Load in watts on the output of the inverter.',
    #     eventId=RVEvents.INVERTER_LOAD_CHANGE,
    #     setting=False
    # )
    # overld: bool = Field(
    #     False,
    #     description='Is the inverter currently in overload.',
    #     eventId=RVEvents.INVERTER_OVERLOAD_CHANGE,
    #     setting=False
    # )
    # overldTimer: float = Field(
    #     0,
    #     description='Seconds since entering overload state',
    #     eventId=None,
    #     setting=False
    # )
    brkSize: Optional[int] = Field(
        None,
        ge=5,
        le=30,
        description='Breaker Size for charger, does not impact the load that can be drawn on pass-thru',
        initial=15,
        setting=True,
        store_db=True
    )


class ChargerAdvanced(BaseComponent):
    """Charger for Xantrex."""

    category: str = CATEGORY
    code: str = COMP_TYPE_CHARGER
    type: str = 'rvc'
    state: ChargerAdvancedState = ChargerAdvancedState()
    # Attributes need to define continous max load here

    def set_state(self, state: dict):
        new_state = ChargerAdvancedState(**state)
        print('[COMPONENT][CHARGER] Set State', new_state)
        if new_state.brkSize is not None:
            self.set_charger_state(new_state)

        super().set_state(None)
        return self.state

    def set_charger_state(self, state):
        if state.brkSize is None:
            # Nothing else to set for now
            return

        cmd = f'{self.instance:02X}FFFF{state.brkSize:02X}FFFFFFFF'
        self.hal.app.can_sender.can_send_raw(
            '19FF9544',
            cmd
        )

        self.state.brkSize = state.brkSize


class EnergyConsumerState(BaseModel):
    """State for power consumers"""

    watts: int = Field(
        None,
        ge=0,
        description="Consumption in watts",
        eventId=RVEvents.ENERGY_CONSUMER_WATTS_CHANGE,
        setting=False
    )
    current: int = Field(
        None,
        description="Current in Amps",
        eventId=RVEvents.ENERGY_CONSUMER_CURRENT_CHANGE,
        setting=False
    )
    active: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.FALSE,
        description='Is this power consumer currently active, this should drive if it is shown or not',
        eventId=RVEvents.ENERGY_CONSUMER_ACTIVE_CHANGE,
        setting=False
    )
    shed: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.FALSE,
        description='Is this consumer currently being shed',
        eventId=RVEvents.ENERGY_CONSUMER_SHED_CHANGE,
        setting=False
    )


class EnergyConsumer(BaseComponent):
    """Inverter model for basic inverter such as Victron without CerboGX."""
    category: str = CATEGORY
    code: str = COMP_TYPE_ENERGY_CONSUMER
    type: str = 'basic'
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_ENERGY_CONSUMER}_basic"
    state: EnergyConsumerState = EnergyConsumerState()

    def set_state(self, state):
        new_state = EnergyConsumer(**state)
        for key, value in state.items():
            if hasattr(self.state, key):
                setattr(
                    self.state,
                    key,
                    getattr(new_state, key)
                )

        super().set_state(None)
        return self.state


class BatteryMgmtState(BaseModel):
    temp: Optional[int] = Field(
        None,
        ge=-273,       # Theoretical min as per CAN
        le=1735,       # Theoretical max as per CAN
        description='BMS Temperature in celcius',
        eventId=RVEvents.BMS_TEMPERATURE_CHANGE,
        setting=False
    )
    soc: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="State of Charge in the Battery",
        eventId=RVEvents.BMS_STATE_OF_CHARGE_CHANGE,
        setting=False
    )
    vltg: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Voltage in Volts",
        eventId=RVEvents.BMS_VOLTAGE_STATUS_CHANGE,
        setting=False
    )
    dcCur: Optional[int] = Field(
        None,
        description="DC current in Amps",
        eventId=RVEvents.BMS_DC_CURRENT_CHANGE,
        setting=False
    )
    dcPwr: Optional[int] = Field(
        None,
        description="Net power watts - negative if draw - positive if gain",
        eventId=RVEvents.BMS_DC_POWER_CHANGE,
        setting=False
    )
    tte: Literal[
            EventValues.TIME_TO_EMPTY,
            EventValues.TIME_TO_FULL
        ] = Field(
            EventValues.TIME_TO_EMPTY,
            description="Time to event Minutes, if charging time till full, if discharging time till empty",
            eventId=RVEvents.BMS_TIME_REMAINING_INTERPRETATION_CHANGE,
            setting=False
    )
    minsTillFull: Optional[int] = Field(
        None,
        description='Actual minutes remaining to charge',
        setting=False,
        # TODO: Resolve this
        eventId=RVEvents.BMS_TIME_REMAINING_TO_FULL_CHARGE_CHANGE
    )
    minsTillEmpty: Optional[int] = Field(
        None,
        description='Actual minutes remaining to charge',
        setting=False,
        # TODO: Resolve this
        eventId=RVEvents.BMS_TIME_REMAINING_TO_EMPTY_CHANGE
    )


# class EnergyManagementState(BaseModel):
#     avc2: int = Field(
#         EventValues.OFF,
#         values=[
#             EventValues.OFF,
#             EventValues.SHORE,
#             EventValues.PROPOWER,
#         ],
#         eventId=RVEvents.ENERGY_MANAGEMENT_AVC2_MODE_CHANGE ,
#         description="Current/Desired source for power",
#     )


# class EnergyManagement(BaseComponent):
#     """State for Slideout without limiter switches or percent extended knowledge."""

#     category: str = CATEGORY
#     code: str = COMP_TYPE_ENERGY_MANAGE
#     type: str = "basic"
#     componentId: str = f"{COMP_TYPE_ENERGY_MANAGE}_basic"
#     state: EnergyManagementState

#     attributes: dict = {
#         "name": "Energy Management",
#         "description": ""
#     }


class PowerSourceState(BaseModel):
    onOff: Literal[
            EventValues.OFF,
            EventValues.ON
        ] = Field(
            EventValues.OFF,
            description='Is the power source enabled. Not many energy sources can be disabled',
            eventId=RVEvents.ENERGY_SOURCE_MODE_CHANGE,
            setting=True,
            store_db=True
    )
    active: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.FALSE,
        description="Is the power source avtively providing power",
        eventId=RVEvents.ENERGY_SOURCE_ACTIVE_CHANGE,
        setting=False
    )
    watts: Optional[int] = Field(
        None,
        ge=0,
        description="Power in watts provided to the system",
        eventId=RVEvents.ENERGY_SOURCE_POWER_CHANGE,
        setting=False
    )
    vltg: Optional[int] = Field(
        None,
        description='Voltage of the input source if known',
        eventId=RVEvents.ENERGY_SOURCE_VOLTAGE_CHANGE,
        setting=False
    )
    # TODO: Need to review naming
    cur: Optional[int] = Field(
        None,
        description='Current of the input source if known',
        eventId=RVEvents.ENERGY_SOURCE_CURRENT_CHANGE,
        setting=False
    )
    # frquency may load from the inverter/ charger messages
    freq: Optional[float] = Field(
        None,
        description='AC Frequency reported by the inverter',
        eventId=None,
        setting=False
    )


class PowerSourceSolar(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_ENERGY_SOURCE
    type: str = "solar_rvc"
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_ENERGY_SOURCE}_solar_rvc"
    state: PowerSourceState = PowerSourceState()
    attributes: dict = {
        'type': 'SOLAR'
    }

    def set_state(self, state):
        new_state = PowerSourceState(**state)

        self.state.watts = new_state.watts
        # TODO: Add a threshold for active
        if new_state.watts > 0:
            self.state.active = True
        else:
            self.state.active = False

        # Emit state events
        super().set_state(None)


class PowerSourceShore(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_ENERGY_SOURCE
    type: str = "shore_rvc"
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_ENERGY_SOURCE}_shore_rvc"
    state: PowerSourceState = PowerSourceState()
    attributes: dict = { 'type': 'SHORE' }


class PowerSourceAlternator(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_ENERGY_SOURCE
    type: str = "alternator_rvc"
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_ENERGY_SOURCE}_alternator_rvc"
    state: PowerSourceState = PowerSourceState()
    attributes: dict = { 'type': 'WAKESPEED' }


class PowerSourceProPower(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_ENERGY_SOURCE
    type: str = "vehicle"
    # componentId: str = f'{CATEGORY}.{COMP_TYPE_ENERGY_SOURCE}_propower_ford'
    state: PowerSourceState = PowerSourceState()


class PowerSourceGenerator(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_ENERGY_SOURCE
    type: str = "generator_src"
    state: PowerSourceState = PowerSourceState()
    attributes: dict = inject_parent_attr({
        'type': 'GENERATOR',
        # NOTE: Requirements allow full far field control
        # 'controllable': "NS",   # controlable attribute - N Nearfield, F Farfield, S Special
        # 'special-states': [{'mode': EventValues.OFF},]   # controlable Special Farfield Operations allowed to be stopped
        })


class GeneratorState(BaseModel):
    """State for generators"""
    # Removed onOff as it serves no specific purpose yet. Schedules and auto-on need a new component
    mode: Optional[Literal[
                EventValues.OFF,                    # Set and current mode
                EventValues.CRANK,                  # Set and current mode while cranking (or while external buttons causes cranking)
                # EventValues.PRIME,                  # Set and current mode while priming
                EventValues.RUN,                    # Set and current mode
                EventValues.RESET,                  # Sent to set neither run nor stop (DEADMAN release)
                EventValues.STARTING,               # Intermediate state while no other state is identified
                EventValues.GENERIC_ERROR,          # This mode cannot be set
        ]] = Field(
            None,
            description="Stop, crank, prime or run the Generator",
            eventId=RVEvents.GENERATOR_OPERATING_MODE_CHANGE,
            setting=True
    )
    lockouts: Optional[List[int]] = Field(
        [],
        description='List of lockouts present'
    )
    warnings: Optional[List[int]] = Field(
        [],
        description='List of warnings present, such as Low Fuel'
    )
    lastStartTime: float = Field(
        None,
        description='Last time we did transitioned into RUN as seconds from epoch. Used to compute current running time if still in RUN.',
        setting=False,
        eventId=None,
        store_db=True
    )

class GeneratorBasic(BaseComponent):
    '''Base model shared for all generators.'''
    category: str = CATEGORY
    code: str = COMP_TYPE_GENERATOR
    type: str = "basic"
    _startTracker: ActionTracker = ActionTracker()
    # Cummins propane specific  TODO: should we move this?
    # If we have 5 unsuccessful starts in a row, check the 5th last unsuccessful and if it's within 200 seconds of the current time,
    # display a message to the user - "Please check your generator for any errors" and lockout for 5 minutes
    # If we have a successful start, reset the unsuccessful counter to 0
    _startTracker.expiry = 50  # Should have started in 45 ish seconds per
    # Trying to use this startingTracker to stay in the starting state for 30 seconds - not the same as the start tracker
    _startingTracker: ActionTracker = ActionTracker()
    # stateChecker will hold the scheduled Function callback to check state after starting
    # stateChecker: ScheduledFunction = None
    _runTracker: ActionTracker = ActionTracker()
    # Tracker starts when the sensor circuit goes high
    # If the circuit is still high after 5 seconds it is running
    _runTracker.expiry = 5
    _primeTracker: ActionTracker = ActionTracker()
    internal_state: GeneratorState = GeneratorState()

    attributes: dict = inject_parent_attr(
        {
            'lockoutStates': [
                {
                    'eventValue': EventValues.GENERATOR_COOLDOWN,
                    'triggerValue': True,
                    'timerBased': True,
                    'timerDefaultSecs': 300,
                    'default': False
                },
            ],
            'warningStates': [
                {
                    'eventValue': EventValues.FUEL_LOW,
                    'triggerValue': True
                }
            ],
            # NOTE: Requirements allow full far field control
            # 'controllable': "NS",   # controlable attribute - N Nearfield, F Farfield, S Special
            # 'special-states': [{'mode': EventValues.OFF},],   # controlable Special Farfield Operations allowed to be stopped
            # 'cooldown-monitor': {'attempts': 1,  # start attemps - cleared when running or ignored if first attemp > ? seconds
            #                     'first-attemp-ts': 0,      # when did the user begin trying to start the generator?
            #                     'most-recent-ts': 0}        # timestamp of last attempt
        }
    )

    def get_db_state(self):
        saved_state = super().get_db_state()
        if saved_state is not None:
            self.internal_state.lastStartTime = saved_state.get('lastStartTime')
        return self.internal_state

    @property
    def state(self):
        '''Runs on getting the state to ensure that the state transition is available on the API.'''
        # print(f"\nR E A D I N G GeneratorBasic state")
        # This method will be called whenever you access the 'state' attribute
        # Check timers here to see if we need to transition before returning the current state
        if self.internal_state.mode == EventValues.STARTING:
            # if self._startingTracker.is_expired():
            #     # Check if we are running
                try:
                    # ...
                    # 'circuitId': '4-13'
                    # ...
                    switch_bank, switch_id = self.attributes.get('circuitId').split('-')
                    # Will be None if nothing is updating it
                    switch_state = self.hal.electrical.handler.get_switch_state(
                        switch_id,
                        switch_bank=switch_bank
                    )
                    if switch_state.get('onOff') == EventValues.ON and self._runTracker.is_expired():
                        self.internal_state.mode = EventValues.RUN
                        self.internal_state.lastStartTime = time.time()
                    else:
                        if self._startingTracker.is_expired():
                            self.internal_state.mode = EventValues.OFF

                except Exception as err:
                    print(f"{err}")

        # print(f"R E A D I N G GenretorBasic state ^^^^^^^^^^^^^^^^^^^^^^^^^^^^{self._state.mode.name} \n")
        # if self.hal is not None:
        #    print(f"\n\nHELP  {self.hal.electrical.handler.get_switch_state('13').get('onOff','WHERE IS Switch')}")

        return self.internal_state

    @state.setter
    def state(self, value):
        # This method will be called whenever you assign a new value to 'state'
        # TODO: see if we want to replace set_state with this type of idea
        self.set_state(value)

    async def get_state_async(self):
        '''Used in scheduled functions which have to support async.'''
        return self.state

    def set_state(self, in_state: dict) -> GeneratorState:
        '''Set the generator state.'''
        # What generator am I ?
        # if hal is not None:
        #     self.check_lockouts(hal)

        desired_mode = in_state.get('mode')
        print(f'Generator set_state desire mode" {desired_mode}')

        # Check the mode, is it applicable, locked out etc.

        current_mode = self.internal_state.mode
        # Adding a 'STARTING' state - which when it 'expires' the generator should be set to running or have a 5 sec lockout

        # If we are running we cannot PRIME
        # Start timers when priming starts, check timers if they exceed and set lockout state and reject state transition
        if desired_mode == EventValues.PRIME:
            # Not with this generator
            return self.internal_state

        elif desired_mode == EventValues.RUN:
            if current_mode == EventValues.RUN or current_mode == EventValues.STARTING:
                return self.internal_state
            else:
                lock = self.hal.system.handler.lockouts[EventValues.TIME_BASED_LOCKOUT_15_SECS]
                lock.state.active = True
                lock.state.expiry = datetime.now() + timedelta(seconds=15)
                lock.state.durationSeconds = 15
                print('INCREMENTING TRACKER', self._startTracker)
                if self._startTracker.increment() > 3:
                    # Do we need additional checking or component for multiple retries

                    # Start not allowed - cool down?
                    lock = self.hal.system.handler.lockouts[EventValues.GENERATOR_COOLDOWN]
                    lock.state.active = True
                    lock.state.expiry = datetime.now() + timedelta(seconds=300)
                    lock.state.durationSeconds = 300
                    self.internal_state.mode = EventValues.OFF

                    # TODO: We need to raise and error so we report the 423 lockout activated
                    raise ValueError("To many attempts to start. Allow cooldown.")
                else:
                    self.internal_state.mode = EventValues.STARTING
                    self._startingTracker.increment()
                    print("Before adding stateChecker")
                    stateChecker = ScheduledFunction(
                        function=GeneratorBasic.get_state_async,
                        args=(self,),
                        wait_seconds=13,
                        oneshot=True
                    )
                    self.hal.app.taskScheduler.add_timed_function(stateChecker)
                    stateChecker = ScheduledFunction(
                        function=GeneratorBasic.get_state_async,
                        args=(self,),
                        wait_seconds=60,
                        oneshot=True
                    )
                    self.hal.app.taskScheduler.add_timed_function(stateChecker)
                    print("\n\nSHould see new task\n\n")

                print('TRACKER AFTER INCREMENTING', self._startTracker)

        elif desired_mode == EventValues.OFF:
            print('WANT TO SET OFF', 'current', current_mode)
            if current_mode == EventValues.PRIME:
                self.internal_state.mode = EventValues.OFF
            elif current_mode == EventValues.RUN or current_mode == EventValues.STARTING:
                self.internal_state.mode = EventValues.OFF
                lock = self.hal.system.handler.lockouts[EventValues.TIME_BASED_LOCKOUT_15_SECS]
                lock.state.active = True
                lock.state.expiry = datetime.now() + timedelta(seconds=15)
                lock.state.durationSeconds = 15
            else:
                print('HIT ELSE in desired_mode', desired_mode)

        # Set state to operate the generator
        self.hal.energy.handler.set_generator_controls(self.instance)

        # Emit state events
        super().set_state(None)

        return self.internal_state

    # async def check_hours(self):
    #     '''Function to be called every 36 seconds to track run hours to 100th of an hour.'''
    #     # Passing in hal - scheduled function seems to be using the wring generator ( is the floorplan init more than once? )
    #     if self.internal_state.mode == EventValues.RUN:
    #         # Note: will we accumulate error over time?
    #         self.internal_state.hours += 0.01
    #         self.internal_state.curRunTime += 0.01
    #         self.save_db_state()

        # DEBUG statements below
        #         print("Generator hours : ", self.internal_state.hours, "\n")
        #     except Exception as err:
        #         print(f"Hour update err: {err}")
        # else:
        #     print(f"Generator hours not running wha? {self.internal_state.mode} \n\n")

    def update_generator_run(self, onOff):
        # TODO: Change to EventValues in the template
        if onOff is True:
            if self.state.mode == EventValues.RUN:
                # We do not do anything as the generator is already running
                pass
            else:
                # RVMP genertor run hours need incrementing ( another function )
                self.internal_state.mode = EventValues.RUN
                # also record the start time - user started from outside
                self.internal_state.lastStartTime = time.time()
        else:
            # Check if it is in mode starting
            if self.state.mode == EventValues.STARTING:
                # Check timer is done when state is read run state
                pass
            else:
                self.internal_state.mode = EventValues.OFF

        # Update the state / save db

        # TODO: Should this really increment at all times or only on starting ? How does it reliably
        self._runTracker.increment()
        super().save_db_state()


class GeneratorPropane(GeneratorBasic):
    '''Thin wrapper around Generator Basic.
    This might be necessary to differentiate the cranking mode etc. and might
    allow state transitions to be handled in this model/class.'''
    type: str = 'propane'
    attributes: dict = inject_parent_attr(
        {
            'fuelSource': 'PROPANE',
            'lockoutStates': [
                # Removed per user will frequently have aux tank for longer stays.
                # {
                #     "componentTypeId": LockoutBasic().componentId,
                #     "instance": EventValues.FUEL_EMPTY
                # },
                {  # Per  MFG  delay after changing state
                    'eventValue': EventValues.TIME_BASED_LOCKOUT_15_SECS,
                    'triggerValue': True
                },
                {
                    'eventValue': EventValues.GENERATOR_COOLDOWN,
                    'triggerValue': True,
                    'timerBased': True,
                    'timerDefaultSecs': 300,
                    'default': False
                },
            ],
            'warningStates': [
                {
                    'eventValue': EventValues.FUEL_LOW,
                    'triggerValue': True
                }
            ],
            # NOTE: Requirements allow full far field control
            # 'controllable': "NF",   # controllable attribute - N Nearfield, F Farfield, S Special
            # 'special-states': [{'mode': EventValues.OFF},]   # controllable Special Farfield Operations allowed to be stopped
        }
    )


class GeneratorDiesel(GeneratorBasic):
    '''Thin wrapper around Generator Basic.
    This might be necessary to differentiate the cranking mode etc. and might allow state transitions
    to be handled in this model/class.'''
    type: str = 'diesel'
    # componentId: str = f'{CATEGORY}.{COMP_TYPE_GENERATOR}_diesel'
    attributes: dict = {
        'fuelSource': 'DIESEL',
        'lockoutStates': [
            {
                'eventValue': EventValues.GENERATOR_OVERCRANKED,
                'triggerValue': True
            },
            {
                'eventValue': EventValues.GENERATOR_COOLDOWN,
                'triggerValue': True
            },
            {
                'eventValue': EventValues.EMPTY,
                'triggerValue': True
            },
        ],
        'warningStates': [
            {
                'eventValue': EventValues.LOW,
                'triggerValue': True
            },
        ],
        # NOTE: Requirements allow full far field control
        # 'controllable': "NS",   # controlable attribute - N Nearfield, F Farfield, S Special
        # 'special-states': [
        #     {
        #         'mode': EventValues.OFF
        #     },
        # ]   # controlable Special Farfield Operations allowed to be stopped
    }


class BatteryManagement(BaseComponent):
    instance: int = 1
    description: str = "BMS Lithionics battery - Basic"
    category: str = CATEGORY
    code: str = COMP_TYPE_BATTERY_MANAGE
    type: str = "basic"
    state: BatteryMgmtState = BatteryMgmtState()

    attributes: dict = inject_parent_attr(
        {
            "type": {
                "description": "Type of BMS in use",
                "propertyType": "string",
                "values": [
                    "LITHIONICS",
                    "ECOFLOW"
                ]
            }
        }
    )

    def set_stale(self):
        # Just set default
        self.state = BatteryMgmtState()


class BatteryState(BaseModel):
    # TODO: What are the properties for a battery ?
    # Temp ?
    temp: Optional[int] = Field(
        None,
        description='Module/Cells temperature for the given battery pack, as received by PROP_MODULE_STATUS_1',
        eventId=RVEvents.BATTERY_TEMP_CHANGE,
        setting=False
    )


class BatteryPack(BaseComponent):
    description: str = "Battery Pack Lithionics - Basic"
    category: str = CATEGORY
    code: str = COMP_TYPE_BATTERY
    type: str = "basic"
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_BATTERY}_basic"
    state: BatteryState = BatteryState()
    # Override attributes to also have capacity
    # Needs a related BMS instance

    # TODO: Add get / set temperature from climate (don't need the setter)


class BaseState(BaseModel):
    # TODO: See if a basic state that holds a handle to hal or the app (or both) is useful
    # Also check if that might be better suited on the component level not the state
    # _hal: Optional[object] = PrivateAttr()
    pass


class FuelTankState(BaseState, validate_assignment=True):
    lvl: int = Field(
        None,
        description='Level of the tank in percent',
        eventId=RVEvents.FUEL_TANK_LEVEL_CHANGE,
        setting=False
    )
    disabled: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.FALSE,
        description='Disables the tank readout. Main use LP tank if external tank is provided',
        eventId=RVEvents.FUEL_TANK_DISABLED_CHANGE,
        setting=True,
        store_db=True
    )
    mode: Literal[EventValues.TANK_FILLING, EventValues.TANK_STEADY, EventValues.TANK_DRAINING] = Field(
        None,
        description='Current state of the tank, calculated from changes to previous level reading.',
        setting=False,
        eventId=None
    )
    minLvl: float = Field(
        0,
        description='Value we consider 0%, so the user can calibrate without the need to change CZone configs',
        setting=True,
        save_db=True
    )
    maxLvl: float = Field(
        93,
        description='Value we consider 100%, so the user can calibrate without the need to change CZone configs',
        setting=True,
        save_db=True
    )


class FuelTank(BaseComponent):
    description: str = "Fuel Tanks - Basic"
    category: str = CATEGORY
    code: str = COMP_TYPE_FUEL_TANK
    type: str = "basic"
    state: FuelTankState = FuelTankState()

    FUEL_EMPTY_THRESHOLD = 2  # %

    def set_state(self, state):
        new_state = FuelTankState(**state)

        # Check if the previous is same, higher or lower
        previous_lvl = self.state.dict().get('lvl')
        if new_state.lvl is not None:
            self.state.lvl = new_state.lvl
            # TODO: Improve this check to consider longer times and put it into runtime data
            if previous_lvl is not None:
                if previous_lvl > self.state.lvl:
                    self.state.mode = EventValues.TANK_FILLING
                elif previous_lvl < self.state.lvl:
                    self.state.mode = EventValues.TANK_DRAINING
                else:
                    self.state.mode = EventValues.TANK_STEADY

        if new_state.disabled is not None:
            self.state.disabled = new_state.disabled

        super().set_state(None)

        return self.state

    def update_can_state(self, msg_name, can_msg) -> dict:
        '''Read fluid level for fuel tank and scale as needed.'''
        can_level = can_level = can_msg['Fluid_Level']
        if can_level == DATA_INVALID:
            print('[TANK] Got Data invalid reported')
            self.state.lvl = None
            new_level = None
        else:
            new_level = float(can_level)

        # Scale the reading
        if new_level is None:
            return False, self.state

        print('TANK LEVEL RAW', new_level)
        lvl = self.scale_reading(new_level)
        print('TANK LEVEL SCALED', lvl)

        # Set the state here
        _ = self.set_state(
            {
                'lvl': lvl
            }
        )

        # Handle related components
        related_comps = self.get_related_components()
        if related_comps:
            # Do something
            for comp in related_comps:
                if comp.__class__.__name__.startswith('Lockout'):
                    # Handle lockouts for now
                    if comp.instance == EventValues.FUEL_EMPTY:
                        if self.state.lvl is not None and \
                                self.state.lvl <= self.FUEL_EMPTY_THRESHOLD:
                            comp.state.active = True
                        else:
                            comp.state.active = False

        return self.state

    def scale_reading(self, hw_read_value):
        '''Takes a HW reading that might need scaling.'''
        # We need to take the incoming value, scale it for the shape and size of the cylinder
        scale = self.state.maxLvl - self.state.minLvl
        value = (100 / scale) * hw_read_value
        if value > 100.0:
            value = 100.0

        return value


class LoadSheddingState(BaseModel):
    '''State for load shedding.'''
    enabled: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.TRUE,       # We default load shedding to be enabled
        description='Is load shedding algorithm enabled',
        setting=False,       # Not an API setting, but could be done in a test override situation,
        eventID=None         # Need an event if this gets turned off
    )
    active: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.FALSE,
        description='are we currently actively shedding',
        setting=False,      # Not settable but the outcome of the algorithm,
        eventId=None,       # Need event for active/inactive
    )
    lastShedTime: float = Field(
        None,
        description='Last time we did shed as seconds from epoch. Used to decide if the load is considered adjusted to the latest shed event.',
        setting=False,
        eventId=None,
    )
    shedComps: list = Field(
        [],
        description='Which components are shed at this time.',
        setting=False,      # Outcome of the algorithm
        eventId=None,
    )


class LoadShedding500(BaseComponent):
    '''Load Shedding component for the 500 series.'''
    description: str = "Load Shedding - Virtual Component"
    category: str = CATEGORY
    code: str = COMP_TYPE_LOAD_SHEDDING
    type: str = "XM524"     # This is a hard coded variant for 524 series
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_FUEL_TANK}_{self.type}"
    state: LoadSheddingState = LoadSheddingState()

    # Override attributes to also have capacity and default unit communicated on API

    # def set_state(self, in_state):
    #     '''Update the state of load shedding.'''
    #     pass

    def initialize_component(self):
        self.runtimeData['relatedComponent'] = {}
        self.runtimeData['priority'] = []
        # print('[ENERGY][LOADSHEDDING] Initializing Components')
        # print('HAL', self.hal)
        # TODO: Why does hal hold a reference to to energy ?
        for instance, component in self.hal.load_shedding.items():
            if component.type not in ('component', 'circuit'):
                # Skip over main and implicit types
                continue

            # print('[ENERGY][LOADSHEDDING] Instance, Component', instance, component)
            self.runtimeData['priority'].append(component)

        self.runtimeData['priority'] = sorted(
            self.runtimeData['priority'], key=lambda x: x.attributes.get('priority', 100)
        )

        # print('[ENERGY][LOADSHEDDING] Shedding priority', self.runtimeData['priority'])

    def run_load_shedding(self, load: int, max_load: int):
        '''Check load shedding flow and set locks accordingly.
        load: current load of the inverter
        maxLoad: What is the continuous max load of the inverter.'''
        # TODO: Move this to the attributes for this component
        SHED_COOLDOWN = self.attributes.get('SHED_COOLDOWN', 5.0)     # Seconds
        # Which components are affected by load shedding
        # 524
        # AC unit first
        # Cooktop then
        # Microwave last
        # What is the current load
        # TODO: Figure out how we can avoid checking for None at all times, unless None is a good way to reset load shedding
        if self.state.lastShedTime is None:
            self.state.lastShedTime = time.time()

        if self.state.lastShedTime > time.time() - SHED_COOLDOWN:
            print('[ENERGY][LOADSHEDDING] Shedding cooldown not expired')
            return

        if load is None or max_load is None:
            print('[ENERGY][LOADSHEDDING] Cannot compare None values for load and/or max_load')
            return

        delta = load - max_load
        print('[ENERGY][LOADSHEDDING] DELTA', delta)
        # Check if we need to shed or can bring stuff back
        shed_component = None
        if delta > 0:
            # Check last time we shed
            for comp in self.runtimeData.get('priority'):
                print('[ENERGY][LOADSHEDDING] Component', comp)
                print('[ENERGY][LOADSHEDDING] STATE', comp.state)

                if comp.state.active == EventValues.TRUE:
                    # Step over to next
                    print('[ENERGY][LOADSHEDDING] Already shed, continue to next')
                    continue
                else:
                    print('[ENERGY][LOADSHEDDING] Shedding', comp.instance)
                    comp.set_state(
                        {
                            'active': EventValues.TRUE
                        }
                    )
                    shed_component = comp
                    # Update time of last shed event
                    self.state.lastShedTime = time.time()
                    # We only shed one at a time
                    print('[ENERGY][LOADSHEDDING] Exit out of shedding until next run')
                    break

            if shed_component is None:
                print('[ENERGY][LOADSHEDDING] No more components to shed.')
                # Throw event for out of relief
                self.hal.event_logger.add_event(
                    RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value,
                    4,  # Report instance '4' for out of components,
                    EventValues.TRUE
                )
            else:
                self.state.shedComps.append(shed_component)

            # Overload situation
            # Are we shedding ?
            # need to shed more ?
            # Timers / counter passed ?
            # self.state.shedComps = ['climate.ac1',]
            # self.state.active = True
        else:
            # SHED recovery needs to be a bit long than COOL DOWN I think
            SHED_RECOVERY = self.attributes.get('SHED_RECOVERY', 10.0)     # Seconds

            if not self.state.shedComps:
                # Nothing is shed
                return

            if self.state.lastShedTime > time.time() - SHED_RECOVERY:
                print('[ENERGY][LOADSHEDDING] Shedding recovery not expired')
                return

            # We can clear the all shed if it was set
            self.hal.event_logger.add_event(
                    RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value,
                    4,  # Report instance '4' for out of components,
                    0
                )

            # The component that is recovering is removed from the list of shed components.
            shed_component_recovering = None

            for comp in reversed(self.runtimeData.get('priority')):
                print('[ENERGY][LOADSHEDDING] RECOVER Component', comp)
                print('[ENERGY][LOADSHEDDING] STATE', comp.state)

                if comp.state.active == EventValues.FALSE:
                    # Step over to next
                    print('[ENERGY][LOADSHEDDING] Is NOT shed, continue to next')
                    continue
                else:
                    print('[ENERGY][LOADSHEDDING] Trying to recover:', comp.instance)
                    if comp.attributes.get('pwrRatingWatts', 800) <= abs(delta):  # Set some minimum if no power rating
                        comp.set_state(
                            {
                                'active': EventValues.FALSE,
                                'lastClearTime': time.time()
                            }
                        )
                        shed_component_recovering = comp
                        # Update time of last shed event
                        self.state.lastShedTime = time.time()
                        # We only shed one at a time
                        print('[ENERGY][LOADSHEDDING] Exit out of shedding until next run')
                        break

            if shed_component_recovering is None:
                print('[ENERGY][LOADSHEDDING] We can not Recover at this time.')
                # TODO: Throw event for that
            else:
                # The component that is recovering is removed from the list of shed components.
                self.state.shedComps.remove(shed_component_recovering)

                # Loop to fire the event again to reset the alert that was overridden.
                for comp in reversed(self.runtimeData.get('priority')):
                    if comp.state.active == EventValues.FALSE:
                        # Step over to next
                        print('[ENERGY][LOADSHEDDING] Is NOT shed, continue to next')
                        continue
                    else:
                        # Refire the event  TODO: This needs to be better, should not have to clear
                        self.hal.event_logger.add_event(
                            RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value,
                            comp.instance,
                            0
                        )
                        self.hal.event_logger.add_event(
                            RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value,
                            comp.instance,
                            1
                        )
                        break

            # Not in overload
            # Are we shedding components ?
            # Can we bring something back ?
            # Are we still shedding ?
        if self.state.shedComps:
            self.state.active = EventValues.TRUE
        else:
            self.state.active = EventValues.FALSE
            self.state.lastShedTime = None

        print('[LOADSHEDDING] Ran component based load shed algorithm.', self.state.shedComps)


class LoadShedderState(BaseModel):
    '''State for load shedder components/circuit.'''
    active: Literal[EventValues.FALSE, EventValues.TRUE] = Field(
        EventValues.FALSE,
        description='are we currently actively shedding',
        setting=False,      # Not settable but the outcome of the algorithm,
        eventId=RVEvents.ENERGY_CONSUMER_SHED_CHANGE,
    )
    lastShedTime: float = Field(
        None,
        description='Last time we did shed as seconds from epoch. Used to decide if the load is considered adjusted to the latest shed event.',
        setting=False,
        eventId=None,
    )
    # TODO: Figure out if saving the clear time is useful
    lastClearTime: float = Field(
        None,
        description='Last time we cleared shedding.',
        setting=False,
        eventId=None,
    )
    # activeSince:
    # shedCnt:


class LoadShedderComponent(BaseComponent):
    '''Wrapper around load shedding functionality.
    Keeps the state of shedding, timestamps and counters.
    Dispatches common functional call(s) to the supported component.'''
    description: str = "Load Shedding - Wrapper"
    category: str = CATEGORY
    code: str = COMP_TYPE_LOAD_SHEDDING
    type: str = "component"     # COMPONENT needs related component
    state: LoadShedderState = LoadShedderState()

    def set_state(self, in_state: dict):
        '''Perform required action.'''
        state = self.state.validate(in_state)
        if state.active == EventValues.TRUE:
            # Perform the required action
            self.state.active = EventValues.TRUE
            # TODO: Add timestamp set
            self.state.lastShedTime = time.time()
            self.state.lastClearTime = None
            # TODO: Clear timestamp released
        elif state.active == EventValues.FALSE:
            # Anything to roll back ?
            self.state.active = EventValues.FALSE
            self.state.lastShedTime = None
            self.state.lastClearTime = time.time()
            # TODO: Clear timestamp set
            # TODO: Set timestamp cleared
        # Send the event
        super().set_state(None)


class LoadShedderCircuit(BaseComponent):
    '''Wrapper around load shedding functionality.
    Keeps the state of shedding, timestamps and counters.
    Dispatches common functional call(s) to the supported component.'''
    description: str = "Load Shedding - Wrapper"
    category: str = CATEGORY
    code: str = COMP_TYPE_LOAD_SHEDDING
    type: str = "circuit"     # CIRCUIT needs circuit knowledge
    state: LoadShedderState = LoadShedderState()

    def set_state(self, in_state: dict):
        '''Perform required action.'''
        state = self.state.validate(in_state)
        if state.active == EventValues.TRUE:
            # Perform the required action
            self.state.active = EventValues.TRUE
            self.state.lastShedTime = time.time()
            # TODO: Add timestamp set
            # TODO: Clear timestamp released
        elif state.active == EventValues.FALSE:
            # Anything to roll back ?
            self.state.active = EventValues.FALSE
            self.state.lastShedTime = None
            # TODO: Clear timestamp set
            # TODO: Set timestamp cleared

        circuit_id = self.attributes.get('circuitId')
        print('[LOADSHEDDING][LoadShedderCircuit] Circuit ID', circuit_id)
        try:
            #  BMAPPING TO THE CIRCUIT
            # Note: This will only work for circuits that shed on being active
            onOff = 1 if self.state.active == EventValues.TRUE else 0
            print('[LoadShedderCircuit] OnOff', onOff)
            result = self.hal.electrical.handler.dc_switch(
                circuit_id,
                onOff,
                100
            )
            print('[LOADSHEDDING][LoadShedderCircuit] CircuitControl', result)
        except Exception as err:
            print('[LOADSHEDDING][LoadShedderCircuit] Componenterror:', circuit_id, err)

        # Send the event
        super().set_state(None)


if __name__ == "__main__":
    import pprint
    propane = GeneratorPropane()
    print(propane)
    print('SCHEMA', pprint.pprint(propane.schema()))
