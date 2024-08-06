from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from common_libs.models.common import EventValues, RVEvents
from main_service.components.common import (
    BaseComponent,
    BaseState,
    inject_parent_attr,
)

CATEGORY = "movables"
COMP_TYPE_SLIDEOUT = "so"
COMP_TYPE_AWNING = "aw"
COMP_TYPE_JACKS = "lj"

# Awning
# SlideOut
# Jacks

# TODO: Should we combine these data points in one or more  Status' ?


class SlideoutBasicState(BaseState):
    """Basic Slideout controller for Lippert SlimRack/FAST Slideout
    Controller.
    """
    mode: Literal[
        EventValues.RETRACTING,     # Command and also current status
        EventValues.OFF,            # Command and status if RETRACTING was last command or status
        EventValues.EXTENDING,      # Command and current status
        EventValues.EXTENDED,       # Status if last action was EXTENDING
        ] = Field(
            EventValues.OFF,
            eventId=RVEvents.SLIDEOUT_MODE_CHANGE,
            description="Current/ Desired mode for slideout",
    )

    lockouts: Optional[List[int]] = Field(
        [],
        description='List of lockouts present',
        setting=False
    )
    warnings: Optional[List[int]] = Field(
        [],
        description='List of warnings present, such as Low Fuel',
        setting=False
    )
    twoStepReq: Optional[bool] = Field(
        True,
        description='Does using this API require a two step validation by the user',
        setting=False,
    )


class SlideoutBasic(BaseComponent):
    """State for Slideout without limiter switches or percent extended knowledge."""

    category: str = CATEGORY
    code: str = COMP_TYPE_SLIDEOUT
    type: str = 'basic'
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_SLIDEOUT}_basic"
    state: SlideoutBasicState = SlideoutBasicState()
    # attributes: list = ...
    attributes: dict = inject_parent_attr({
        'deadmanSwitch': 1,
        'deadmanInitialPauseMs': 1000,
        'deadmanSendIntervalMs': 100,
        'deadmanProperty': 'mode',
        'deadmanReleaseValue': EventValues.OFF,
        'controllable': "N",  # controlable attribute - N Nearfield F Farfield S SpecialTBD for some Farfield Operations

        # "twoStepPres": {
        #     "propertyType": "integer",
        #     "default": 1,  # A two step validation process in present for this component/feature
        # },
        # "twoStepKey": {
        #     "propertyType": "string",
        #     "default": "so",
        # },  # The key where we store this is a dedicated API endpoint is created, not BETA
        # TODO: Clarify if we want to commnuicate the possible values in attributes or not
        # Does this component have lockouts that have to be considered
        "lockoutStates": [
            {
                'eventValue': EventValues.PSM_PB_IGN_COMBO,
                'triggerValue': False
            },
            # {
            #     'eventValue': EventValues.PARK_BRAKE_APPLIED,
            #     'triggerValue': False
            # }
        ],
        "warningStates": [
            # {
            #     'eventValue': EventValues.IGNITION_ON,
            #     'triggerValue': False
            # },
            {
                'eventValue': EventValues.LOW_VOLTAGE,
                'triggerValue': True
            }
        ]

    })

    def set_state(self, state: dict):
        # Validate the incoming state
        new_state = SlideoutBasicState(**state)

        self.hal.movables.handler.move_slideout(new_state, id=self.instance)

        # Transition the state
        if new_state.mode == EventValues.OFF:
            # Put code to stop movement here
            if self.state.mode == EventValues.EXTENDING:
                self.state.mode = EventValues.EXTENDED
            elif self.state.mode == EventValues.RETRACTING:
                self.state.mode = EventValues.OFF
        elif new_state.mode == EventValues.RETRACTING:
            # TODO Assumption
            # Locks are supposed to have been met - NOT checked here!!
            self.state.mode = EventValues.RETRACTING
        elif new_state.mode == EventValues.EXTENDING:
            # TODO Assumption
            # Locks are supposed to have been met - NOT checked here!!
            self.state.mode = EventValues.EXTENDING

        super().set_state(None)
        return self.state


class AwningRvcState(BaseModel):
    '''State for Awning that is RVC enabled.'''
    mode: Optional[Literal[
        EventValues.RETRACTED,
        EventValues.RETRACTING,
        EventValues.OFF,
        EventValues.EXTENDING,
        EventValues.EXTENDED,
    ]] = Field(
        None,  # Using OFF as it has to be overwritten by HW
        description="Moving mode for the awning, OFF is an unknown state and a command.",
        eventId=RVEvents.AWNING_MODE_CHANGE,
        setting=True
    )
    pctExt: Optional[int] = Field(
        None,       # TODO: Using None as it has to be overwritten by HW
        description="Position of the awning reported by hardware.",
        eventId=RVEvents.AWNING_PERCENT_EXTENDED_CHANGE,
        setting=False,  # Only set for False, otherwise assume True in conversion to JSON
    )
    setPctExt: Optional[int] = Field(
        None,
        description="Percentage desired to set, currently only want 0 and 100% - IF NULL then deadman switch  mode",
        setting=True,
    )
    mtnSense: Optional[int] = Field(
        None,  # default to 5 if new
        description="Motion / Wind sensor.",
        ge=0,
        le=5,
        initial=5,  # Need a different field to not use default for the model
        eventId=RVEvents.AWNING_MOTION_SENSE_SENSITIVITY_CHANGE,
        setting=True,
        # store_db isa used to determine if a property value shall be saved/loaded to/from DB
        store_db=True
    )
    # mtnSenseOnOff added as per request by Taylor to retain the motion sensitivity setting
    mtnSenseOnOff: Optional[Literal[EventValues.OFF, EventValues.ON]] = Field(
        None,     # Default to on
        description="Motion / Wind sensor On Off mode.",
        eventId=RVEvents.AWNING_MOTION_SENSE_MODE_CHANGE,
        setting=True,
        initial=EventValues.ON,      # Default
        store_db=True
    )
    # Motion triggered is currently no in the design
    lockouts: Optional[List[int]] = Field(
        description='Lockouts that currently apply to the awning.',
        setting=False
    )
    warnings: Optional[List[int]] = Field(
        description='Warnings that currently apply to the awning.',
        setting=False
    )


class AwningRvc(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_AWNING
    type: str = 'rvc'
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_AWNING}_rvc"
    state: AwningRvcState = AwningRvcState()
    attributes: dict = inject_parent_attr({
        # "twoStepPres": 1,
        'deadmanSwitch': 1,
        'deadmanInitialPauseMs': 1000,
        'deadmanSendIntervalMs': 100,
        'deadmanProperty': 'mode',
        'deadmanReleaseValue': EventValues.OFF,
        # Does this component have lockouts that have to be considered
        'controllable': "NS",   # controlable attribute - N Nearfield, F Farfield, S Special
        'special-states': [{'mode': EventValues.RETRACTING, 'setPctExt': 0}, {'setPctExt': 0}],
        # controlable Special Farfield Operations allowed - retraction
        # NOTE: Added lockouts to align with the physical controller
        # Left PARK brake signal in as it might be used for physical lockout
        # so it can be brought in easily
        "lockoutStates": [
            {
                'eventValue': EventValues.IGNITION_ON,
                'triggerValue': True
            },
        ],
        "warningStates": [
            {
                'eventValue': EventValues.LOW_VOLTAGE,
                'triggerValue': True
            },
            {
                'eventValue': EventValues.PARK_BRAKE_APPLIED,
                'triggerValue': False
            }
        ]
    })

    # def __init__(self, **data):
    #     # TODO: Review this URGS
    #     # Let Pydantic do its initialization and validation first
    #     super().__init__(**data)
    #     # Now, Pydantic has already validated and assigned the fields
    #     # TODO add derived class to BaseComponent to use this new 'initial' field as below
    #     # then change the basecomponent to use the new class to any object with 'initial' defined
    #     # These initial state values will be overridden by a call to get_db_state is previously saved
    #     # Access the field description
    #     mtnSenseOnOff_info = AwningRvcState.schema()["properties"]["mtnSenseOnOff"]
    #     self.state.mtnSenseOnOff = mtnSenseOnOff_info.get("initial", EventValues.ON)
    #     mtnSense_info = AwningRvcState.schema()["properties"]["mtnSense"]
    #     self.state.mtnSense = mtnSense_info.get("initial", 5)
    #     print('[AWNING][MOTIONSENSE]', self.state.dict())

    def set_state(self, state: dict):
        # Validate the state obj
        # TODO: How to handle the failure below ? Do it in API ?
        new_state = AwningRvcState(**state)
        print('[AWNING][STATE]', new_state)
        save_keys = []
        if new_state.setPctExt is not None and self.state.pctExt is not None:
            if self.state.pctExt > new_state.setPctExt:
                new_state.mode = EventValues.RETRACTING
            elif self.state.pctExt < new_state.setPctExt:
                new_state.mode = EventValues.EXTENDING

        # Validating None values and desired behavior
        if new_state.mode is not None:
            if new_state.mode != self.state.mode:
                if new_state.mode == EventValues.OFF:
                    # Stop awning
                    pass
                elif new_state.mode == EventValues.EXTENDING:
                    # Check if we can extend then extend or reject
                    pass
                elif new_state.mode == EventValues.RETRACTING:
                    # Check if we can retract
                    pass

            self.hal.movables.handler.move_awning(new_state)

        # else:
        #     # No mode change required, in this case should we stop ?
        #     new_state.mode = EventValues.OFF
        #     # Might conflict with a simple update to motion sensitivity ?
        #     # Can we extend while changing the sensitivity ?
        #     # Could happen if someone does mobile extend
        #     # while HMI modifies settings

        if new_state.mtnSense is not None:
            print('[AWNING][MTNSENSE]', 'Incoming MtnSense', new_state.mtnSense)
            # store state and set the setting
            # Send the proper command
            self.hal.movables.handler.set_motion_sense(
                self.instance,
                new_state
            )
            self.state.mtnSense = new_state.mtnSense
            save_keys.append('mtnSense')

        if new_state.mtnSenseOnOff is not None:
            print('[AWNING][MTNSENSE]', 'Incoming MtnSense onOFF', new_state.mtnSenseOnOff)
            self.state.mtnSenseOnOff = new_state.mtnSenseOnOff
            self.hal.movables.handler.set_motion_sense(
                self.instance,
                new_state
            )
            save_keys.append('mtnSenseOnOff')

        if new_state.pctExt is not None:
            self.state.pctExt = new_state.pctExt

        # Emit state events
        super().set_state(None)
        self.save_db_state()

        return self.state


class JackState(BaseModel):
    """State for leveling Jacks"""

    mode: Optional[Literal[
            EventValues.RETRACTED,  # Jacks are fully retracted
            EventValues.RETRACTING,  # Jacks are currently retracting or command to retract
            EventValues.LEVELING,  # Jacks are currently auto levelling
            EventValues.AUTO,  # Command to auto level
            EventValues.OFF,  # Only sent as command and used as default
            EventValues.EXTENDING,  # Jacks are currently extending or command to extend
            EventValues.EXTENDED,  # Jacks are fully extended / How does this align with AUTO ?
            EventValues.LEVELING_BIAX_FRONT_EXTENDING,
            EventValues.LEVELING_BIAX_FRONT_RETRACTING,
            EventValues.LEVELING_BIAX_BACK_EXTENDING,
            EventValues.LEVELING_BIAX_BACK_RETRACTING,
            EventValues.LEVELING_BIAX_LEFT_EXTENDING,
            EventValues.LEVELING_BIAX_LEFT_RETRACTING,
            EventValues.LEVELING_BIAX_RIGHT_EXTENDING,
            EventValues.LEVELING_BIAX_RIGHT_RETRACTING,
    ]] = Field(
        EventValues.OFF,
        description="Mode for the leveling jacks",
        eventId=RVEvents.LEVELING_JACKS_MODE_CHANGE,
    )
    lockouts: Optional[List[int]] = Field(
        description='Lockouts that currently apply to the Jacks',
        setting=False
    )
    warnings: Optional[List[int]] = Field(
        description='Warnings that currently apply to the Jacks',
        setting=False
    )


class LevelJacksRvc(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_JACKS
    type: str = 'rvc'
    # componentId: str = f"{CATEGORY}.{COMP_TYPE_JACKS}_rvc"
    state: JackState = JackState()
    # attributes: list = ...
    attributes: dict = inject_parent_attr({
        # "twoStepPres": 1,S
        # Does this component have lockouts that have to be considered
        'controllable': "N",   # controlable attribute - N Nearfield F Farfield  SpecialTBD for some Farfield Operations
        "lockoutStates": [
            {
                'eventValue': EventValues.PARK_BRAKE_APPLIED,
                'triggerValue': False       # Cannot operate the jacks when park brake is not applied
            },
            {
                'eventValue': EventValues.IGNITION_ON,
                'triggerValue': False       # Cannot operate the jacks when ignition is off ? # TODO: Confirm, should be recommended to be on
            },
            {
                'eventValue': EventValues.NOT_IN_PARK,
                'triggerValue': True        # Jacks auto-retract if vehicle is not in park
            }
        ]
    })


if __name__ == "__main__":
    pass
