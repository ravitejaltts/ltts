from optparse import Option
from typing import Any, Optional, List, Union, Literal
from enum import Enum, IntEnum

from pydantic import BaseModel, Field

try:
    from common import (
        BaseComponent,
        ComponentTypeEnum,
    )
except ImportError:
    from .common import (
        BaseComponent,
        ComponentTypeEnum,
    )

try:
    from common_libs.models.common import RVEvents, EventValues
except ImportError as err:
    import sys
    import os

    abs_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
    add_path = os.path.join(abs_path, "../")
    sys.path.append(add_path)
    from common_libs.models.common import RVEvents, EventValues

from datetime import datetime, timedelta

CATEGORY = "system"
COMP_TYPE_LOCKOUTS = "lk"
COMP_TYPE_CIRCUIT = 'cc'
COMP_TYPE_SETTING = 'us'

class ActionTracker(BaseModel):
    """User action monitor"""
    lastAction: datetime = Field(
        None,
        description='Action epoch time in UTC in ms',
        setting=False
    )
    count: int = Field(
        0,
        description='Action Count, of actions more frequent than expiry.',
        setting=False
    )
    expiry: int = Field(
        30,  # 30 seconds deault may need to be adjusted
        description='Expiry seconds, where diference from lastAction resets Action Count',
        setting=False
    )
    # Do we need to know if the action is active ( like holding a key ?) - how to determine
    # Do we need a duration?  how to incremnt if they are holding a key down?

    def __init__(self):
        super().__init__()
        self.lastAction = datetime.now() - timedelta(days=1)

    def is_expired(self):
        return self.lastAction + timedelta(seconds=self.expiry) <= datetime.now()

    def increment(self) -> int:
        """Count increment and time stamp"""
        currentTime = datetime.now()
        if self.is_expired():
            self.count = 1
        else:
            self.count += 1
        self.lastAction = currentTime
        return self.count


class LockoutState(BaseModel):
    """Basic Lockout state."""
    # TODO: Remove the lockout state default
    active: bool = Field(
        None,
        description="Lockout state is active or inactive",
        eventId=RVEvents.LOCKOUT_STATE_CHANGE,
        setting=False
    )


class LockoutStaticState(LockoutState):
    """Static Timer Based Lockout state."""
    expiry: int = Field(
        None,
        description='Expiry epoch time in UTC in ms',
        setting=False
    )


class LockoutDynamicState(LockoutStaticState):
    """Dynamic Timer Based Lockout state."""
    durationSeconds: int = Field(
        None,
        description='Remaining seconds until this expires as caluclated by the coach.',
        setting=False
    )


class LockoutBasic(BaseComponent):
    """State for Slideout without limiter switches or percent extended knowledge."""
    category: str = CATEGORY
    code: str = COMP_TYPE_LOCKOUTS
    type: str = "basic"
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_LOCKOUTS}_basic"
    state: LockoutState = LockoutState()

    # Testing not ready to implement
    # internal_state: LockoutState = LockoutState()

    # @property
    # def state(self):
    #     return self.internal_state

    # @state.setter
    # def state(self, value):
    #     # This method will be called whenever you assign a new value to 'state'
    #     self.set_state(value)

    # def set_state(self, state):
    #     new_state = LockoutState(**state)
    #     self.internal_state = new_state
    #     super().set_state(None)
    #     return self.internal_state


class LockoutDynamic(BaseComponent):
    '''Component definition for a Dynamic Timer based lockout.'''
    category: str = CATEGORY
    code: str = COMP_TYPE_LOCKOUTS
    type: str = "timebased_dynamic"
    state: LockoutDynamicState = LockoutDynamicState()


class LockoutStatic(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_LOCKOUTS
    type: str = "timebased_static"
    state: LockoutDynamicState = LockoutDynamicState()


class CircuitState(BaseModel):
    onOff: Literal[
            EventValues.OFF,
            EventValues.ON] = Field(
        EventValues.OFF,
        description='Current Circuit State',
        setting=False
    )


class Circuit(BaseComponent):
    category: str = CATEGORY        # Temporary place for it as it is electrical
    code: str = COMP_TYPE_CIRCUIT
    type: str = "czone"
    state: CircuitState = CircuitState()
    # Attributes shall contain all info that is needed to drive this circuit
    # And related information back to the system
    # It also needs to be related to a specific component
    attributes: dict = {
        'circuitId': None,
        'circuitType': None,
        'stateProperty': None,
        'valueOn': None,
        'valueOff': None
    }
    # Overwrite this with the single related object for this circuit
    # TODO: Might add this to the Basecomponent
    relatedComponentHandle: Optional[object]

    def execute_state_update(self):
        '''When onOff changes get the relevant info and toggle the change.'''
        # Get attributes
        # Get which component is associated with it
        # Modify this component state, specific property to the value it
        # should switch to
        if self.relatedComponentHandle is None:
            raise ValueError('Cannot access related component, as it is not SET')
        else:
            property = self.attributes.get('stateProperty')
            if property is None:
                raise ValueError('Cannot set None property, property not set')

            value_to_set = None
            if self.state.onOff == EventValues.OFF:
                value_to_set = self.attributes.get('valueOff')
            elif self.state.onOff == EventValues.ON:
                value_to_set = self.attributes.get('valueOn')

            if value_to_set is None:
                raise ValueError('No value to set in property for state: {self.state.onOff}')

            try:
                setattr(self.relatedComponentHandle.state, property, value_to_set)
            except Exception as e:
                print(e)
                raise


class ServiceSettingsState(BaseModel):
    '''State model for service options.
    serviceModeonOff'''
    serviceModeOnOff: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.OFF,
        description='Defines if service mode is currently on or not',
        setting=True,
        eventId=RVEvents.WINNCONNECT_SYSTEM_SETTINGS_SERVICE_MODE_CHANGE
    )
    fcpEnabled: Literal[EventValues.OFF, EventValues.ON] = Field(
        EventValues.OFF,
        description='Setting to enabled/disabled FCP (Functional Control Panel).',
        setting=True,
        eventId=None
    )
    systemMode: Literal[
            EventValues.SYSTEM_MODE_USER,
            EventValues.SYSTEM_MODE_MANUFACTURING,
            EventValues.SYSTEM_MODE_DEALER
        ] = Field(
            EventValues.SYSTEM_MODE_USER,
            description='Overall System Mode the system is in.',
            setting=False,
            eventId=RVEvents.WINNCONNECT_SYSTEM_MODE_CHANGE
        )


class ServiceSettings(BaseComponent):
    '''Model to hold component for service settings.
    This is hard coding instance 1 for now.'''
    category: str = CATEGORY
    code: str = COMP_TYPE_SETTING
    type: str = 'service'
    state: ServiceSettingsState = ServiceSettingsState()
    attributes: dict = {
        'name': 'Service Settings',
        'description': 'Service Settings component',
        'type': 'SETTINGS_SERVICE'
    }
    instance: int = 1

    def set_state(self, state):
        print('[SETTING] Running set_state in component', state)
        new_state = ServiceSettingsState(**state)

        if new_state.serviceModeOnOff is not None:
            self.state.serviceModeOnOff = new_state.serviceModeOnOff

            if hasattr(self.hal.system.handler, 'lockouts'):
                service_mode_lockout = self.hal.system.handler.lockouts.get(
                    EventValues.SERVICE_MODE_LOCKOUT
                )
                if service_mode_lockout is not None:
                    service_mode_lockout.state.active = True if self.state.serviceModeOnOff == EventValues.ON else False

        if new_state.fcpEnabled is not None:
            self.state.fcpEnabled = new_state.fcpEnabled

        super().set_state(None)
        return self.state


class FAILURECOMPONENTSTATE(BaseModel):
    pass


class FAILURE_TEST_COMPONENT(BaseComponent):
    category: str = CATEGORY
    code: str = 'XXXX'
    type: str = 'failthis'
    state: FAILURECOMPONENTSTATE = FAILURECOMPONENTSTATE()


if __name__ == "__main__":
    lockout = LockoutBasic(
        instance=EventValues.LOW_VOLTAGE,
        attributes={
            'name': 'Dom'
        }
    )
    print(lockout.componentId)

    circuit = Circuit(
        attributes={
            'circuitId': None,
            'circuitType': None,
            'stateProperty': 'onOff',
            'valueOn': EventValues.ON,
            'valueOff': EventValues.OFF
        },
        relatedComponentHandle=lockout
    )
    print(circuit)
    circuit.state.onOff = EventValues.ON
    print(circuit)
    circuit.execute_state_update()
    print(lockout)
