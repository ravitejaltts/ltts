from enum import Enum
import json

from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError
from datetime import datetime

from common_libs.models.common import CODE_TO_ATTR


COMPONENT_SEPARATOR = '.'

DEFAULT_ATTRIBUTES = {
    'description': {
        'default': '',
        'description': 'Describes the component for internal use',
        'propertyType': 'string'
    },
    'name': {
        'default': '',
        'description': 'Name of the Component',
        'propertyType': 'string'
    },
    'controllable': 'NF'
    # 'controllable': {
    #     'default': 'NF',
    #     'description': ' N Nearfield, F Farfield, S Special - One allowed state',
    #     'propertyType': 'string'
    # }
}


class CategoryEnum(str, Enum):
    lighting = 'lighting'
    watersystems = 'watersystems'
    vehicle = 'vehicle'
    energy = 'energy'
    climate = 'climate'
    system = 'system'
    connectivity = 'connectivity'
    movables = 'movables'
    features = 'features'


# TODO: Change this to also hold the event ID ranges for checks
class ComponentTypeEnum(str, Enum):
    ac = 'Air Conditioner'
    at = 'Alternator'
    aw = 'Awning'
    ba = 'Battery'
    bl = 'Bluetooth'
    bm = 'Battery Management'
    cc = 'Circuits'
    ce = 'Cellular'
    ch = 'Chassis'
    dl = 'Door Lock'
    dx = 'Diagnostics'
    ec = 'Energy Consumer'
    ei = 'Inverter'
    em = 'Energy Management'
    es = 'Energy Source'
    ft = 'Fuel Tank'
    fu = 'Heater'       # Deprecated
    ge = 'Generator'
    he = 'Heater'       # Combined with furnace
    hm = 'WinnConnect HMI Hardware'
    ic = 'Charger'
    lf = 'Lighting Feature'
    lg = 'Lighting Group'
    lj = 'Leveling Jacks'
    lk = 'Lockouts'     # Lockouts are a virtual component under system that get translated into lockouts and warning per component
    lo = 'Location'
    ls = 'Load Shedding'
    lz = 'Lighting Zone'
    ot = 'OTA'
    pc = 'Power Consumer'
    pm = 'Pet Monitoring'
    pr = 'ProPower'
    rf = 'Refrigerator'
    rv = 'Roof Vent'
    sc = 'Solar Charger'
    sm = 'Smart Buttons - feature will be implemented in the future, just a placeholder'
    so = 'Slide Out'
    tc = 'Toilet Circuit'  # Power for macerator
    th = 'Thermostat'
    us = 'User Setting'
    wf = 'WiFi'
    wh = 'Water Heater'
    wi = 'WinnConnect System'
    wp = 'Water Pump'
    wt = 'Water Tank'
    wx = 'Weather'

    XXXX = 'FAILURE_TEST'


class BaseAttributes(BaseModel):
    name: Optional[str]
    description: Optional[str]


class BaseComponent(BaseModel):
    instance: int = Field(
        1,
        ge=0,
        description="Instance of this component, starts at 1 for each "
                    "component that shares a code and increments regardless"
                    " of subtypes",
    )
    category: CategoryEnum
    meta: Optional[dict]      # Holds the as build manufacturing info to be show in settings, eventually can be overwritten via OTA if the as built info changes
    code: str  # wt, wh, lz     # TODO: Rename to componentType ?
    type: str   # componentId: str    #lz_rgb
    properties: Optional[List[dict]]
    attributes: dict = DEFAULT_ATTRIBUTES

    # optionCodes is a regex string to indicate under which option conditions this component is in the floorplan / as built coach
    optionCodes: Optional[str]
    relatedComponents: Optional[List[dict]]

    componentId: str = ''       # Needs to be set during init

    # Internal Use in HAL Code
    # Holds the event ids for each property that the state could have
    eventIds: Optional[dict] = {}

    hal: Optional[object] = Field(
        None,
        exclude=True
    )

    runtimeData: Optional[dict] = {}     # Holds runtime data that can be retrieved/used

    def __getattribute__(self, __name: str):
        if __name == 'componentId':
            # retrieve value from lockouts
            return f'{self.category}.{self.code}_{self.type}'
        elif __name == 'config_key':
            return f'{self.category}.{self.code}.{self.instance}'
        else:
            return object.__getattribute__(self, __name)

    class Config:
         exclude = {"hal"}

    def set_attribute_defaults(self):
        # Filter attributes that start with 'state.'
        state_attributes = {k: v for k, v in self.attributes.items() if k.startswith('state.')}

        # Iterate over the filtered attributes
        for state_key, value in state_attributes.items():
            # Extract the property name from the state_key
            prop = state_key.split('.', 1)[1]
            if hasattr(self.state, prop):
                setattr(self.state, prop, value)

    def set_state_defaults(self):
        '''Re-init the state defaults when needed, can be used to reset each state to its
        default model -> attributes.

        Can be used to set the defaults, and overwrite the user DB entries for
        each property.'''
        self.set_state_initial()
        self.set_attribute_defaults()
        self.save_db_state()

    def set_hal(self, hal_obj):
        '''Set a reference to the initialized HAL.'''
        self.hal = hal_obj

    def set_component_id(self):
        '''Instead of generating it in realtime, set it during catalog creation.'''
        # TODO: Move to single catalog instead of __init__
        self.componentId = f'{self.category}.{self.code}_{self.type}'

    def check_lockouts(self):
        component_lockouts = self.attributes.get('lockoutStates', [])
        lockouts = []
        for lock_out in component_lockouts:
            event_id = lock_out['eventValue']
            try:
                lock = self.hal.system.handler.lockouts[event_id]
                print(component_lockouts, 'Lock check', lock)
                if lock.state.active is lock_out['triggerValue']:
                    if hasattr(lock.state, "expiry"):
                        print(f"Check Timer lockout for expired.")
                        if lock.state.expiry > datetime.now():
                            # Timer has not expired, Lockout needs to be added
                            lockouts.append(event_id)
                        else:
                            # clear lockout
                            lock.state.active = False
                            lock.state.expiry = None
                    else:
                        # Lockout needs to be added
                        lockouts.append(event_id)
            except KeyError as err:
                print("check_lockouts lockouts ", err)
        warnings = []
        for warning in self.attributes.get('warningStates', []):
            try:
                event_id = warning['eventValue']
                lock = self.hal.system.handler.lockouts[event_id]
                if lock.state.active is warning['triggerValue']:
                    # Lockout needs to be added
                    warnings.append(event_id)
            except KeyError as err:
                print("check_lockouts warnings ", err)

        if hasattr(self.state, "lockouts"):
            print('Adding lockouts to state', lockouts)
            self.state.lockouts = lockouts
        if hasattr(self.state, "warnings"):
            print('Adding warnings to state', warnings)
            self.state.warnings = warnings

        print(self)

    def get_related_components(self):
        print('RELATED1: Related Components', self.relatedComponents)
        # Might have to handle none
        related_components = []
        for component in self.relatedComponents:
            # print('Comp', component)
            category, code = component.get('componentTypeId').split('.')
            # print(category, code)
            instance = component.get('instance')
            # print(instance)
            handler = getattr(self.hal, category).handler
            # print(handler)
            long_code = CODE_TO_ATTR.get(code.split('_', maxsplit=1)[0])
            try:
                comp_handle = getattr(handler, long_code)
            except AttributeError as err:
                print('[BASECOMPONENT] Cannot get handle for related component, might not exit', err, category, long_code)
                continue
            # print(comp_handle)
            comp_instance = comp_handle[instance]
            related_components.append(comp_instance)

        return related_components

    def save_db_state(self):
        '''Save DB config for this component state.'''
        state = self.state.dict()
        saved_state = {}
        if hasattr(self, 'internal_state'):
            schema = self.internal_state.schema()
        else:
            schema = self.state.schema()

        for prop, _ in state.items():
            save_to_db = schema.get(
                    'properties', {}
                ).get(
                    prop, {}
                ).get('store_db')

            if save_to_db is True:
                value = state.get(prop)
                if value is not None:
                    saved_state[prop] = value

        # We do not want to save anything when no values provided
        print('SAVE_DB_STATE Result', saved_state)
        if not saved_state:
            return {}

        return self.hal.app.save_config(self.config_key, saved_state)

    def get_db_state(self):
        '''Retrieve DB config for this component state.'''
        db_state = self.hal.app.get_config(self.config_key)

        if db_state is not None:
            # Check which filter applies
            for prop, _ in self.state.dict().items():
                get_from_db = self.state.schema().get(
                        'properties', {}
                    ).get(
                        prop, {}
                    ).get('store_db')

                if get_from_db is not True and prop in db_state:
                    del db_state[prop]

            self.set_state_props(db_state)

        try:
            self.hal.emit_state_events(self)  # Added to push out events to IOT
        except Exception as err:
            # Why does this error hit: AttributeError: 'ClimateControl' object has no attribute 'emit_state_events'
            print(f"hal emit_state_events: {err}", self.hal)

        return db_state

    def set_state(self, in_state):
        '''BaseComponent set_state. Currently only
        emits the events.'''
        # print('Received state in BaseComponent for', self.instance, self.componentId, state)
        # Emit state events
        self.hal.emit_state_events(self)
        self.save_db_state()
        return None

    def update_state(self):
        '''Emit all state properties.'''
        self.hal.emit_state_events(self)
        return None

    def set_state_initial(self):
        '''Iterate over state properties and check if
        they need an initial value as per schema.'''
        # print('[set_state_inital] Checking', self.componentId, self.state)
        for prop, _ in self.state.dict().items():
            # print('[set_state_inital] Checking value for', self.componentId, prop)
            initial_value = self.get_state_initial(prop)
            if initial_value is not None:
                # print('[set_state_inital] Setting value for', prop, initial_value, type(initial_value))
                # TODO: Check if we can convert the type of the property and conversion is needed
                setattr(self.state, prop, initial_value)

        return self.state

    def get_state_initial(self, property, default=None):
        '''Try to get the value set for 'initial' of the given property or return
        default / None.'''
        return self.state.schema().get('properties', {}).get(property, {}).get('initial', default)

    def validate_state(self, in_state):
        '''Validate the provided in_state for our state model.'''
        try:
            self.state.validate(in_state)
            return False
        except ValidationError as err:
            # return err.json()
            return json.loads(err.json())

    def set_state_props(self, properties, set_none_only=False):
        '''Set values in the state from list of properties.'''
        for key, value in properties.items():
            if hasattr(self.state, key) and value is not None:
                # We do not want to set None values as these would not be properties that are desirable
                if set_none_only is True:
                    if getattr(self.state, key) is None:
                        setattr(self.state, key, value)
                else:
                    setattr(self.state, key, value)

    def set_stale(self):
        '''Let the component decide what needs to happen
        when a device communication is lost.
        Set the list of properties to the default values (usually None).'''
        pass

    def initialize_component(self):
        '''Signature for the must overwrite initialize_component.'''
        return None
        # raise NotImplementedError('Inititalize component not implemented in the instance of the BaseComponent.')

    def update_can_state(self, msg_name, can_msg) -> dict:
        '''Method to update state as received from the CAN bus.'''
        print('[CAN] BaseComponent received: ', msg_name, can_msg)
        print('[CAN] Need to overide in specific component')
        raise NotImplementedError('Update from CAN not implemented in the instance of the BaseComponent.')

    # class Config:
    #     exclude = {"hal"}


class BaseState(BaseModel, validate_assignment=True):
    pass


class SimpleOnOff(BaseModel):
    onOff: int = Field(
        None,
        ge=0,
        le=254,
        description="Instances of the equipment, everything has an instance even if there is only one. Instances should start at 1 for each type of component",
    )
    deviceType: str = "core"
    type: Optional[ComponentTypeEnum]
    name: Optional[str]  # "ei - Inverter - Basic Metered"
    meta: Optional[dict]  # Random dictionary, needs more definition (name, ... ?)


class LockoutListItem(BaseModel):
    value: int = Field(
        None,
        description='The linked EventValue enum entry by int value'
    )


class LockoutTimer(BaseModel):
    eventValue: int = Field(
        None,
        description='ID this timer relates to'
    )
    secsRemaining: int = Field(
        None,
        description='Seconds remaining in this timer'
    )


def inject_parent_attr(attributes):
    '''This injects the parent attributes into the child model.'''
    # TODO: Figure out if there is a proper object based way to get the parent attributes first from inheritance
    # That should not be so hard

    global BaseComponent
    parent_attributes = BaseComponent(code='NONE', type='NONE', category='lighting').attributes
    for attr, value in parent_attributes.items():
        print(attr)
        if attr not in attributes:
            attributes[attr] = value

    return attributes


if __name__ == '__main__':
    component = BaseComponent(
        category='lighting',
        code='dt'
    )
    print(component)
    print(component.componentId)
