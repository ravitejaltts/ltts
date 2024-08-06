from optparse import Option
from typing import Optional, List, Union, Literal
from enum import Enum, IntEnum
from copy import deepcopy

from pydantic import BaseModel, Field

from common_libs.models.common import RVEvents, EventValues
from .common import BaseComponent


CATEGORY = 'lighting'
COMP_TYPE_LIGHT_ZONE = 'lz'
COMP_TYPE_LIGHT_GROUP = 'lg'

DEFAULT_BRIGHTNESS = 80
MIN_LIGHTING_BRIGHTNESS = 5     # %
MAX_LIGHTING_BRIGHTNESS = 100   # %


class LightSimpleState(BaseModel):
    '''Component state model for a simple light that can only be turned on/off.'''
    onOff: Literal[
            EventValues.OFF,
            EventValues.ON] = Field(
        None,
        description='Schema for a simple on off state, currently allows None as the initial value',
        eventId=RVEvents.LIGHTING_ZONE_MODE_CHANGE,
        setting=True,
        store_db=False      # We do not save this, calling it out here for information, we read the lighting state from the HW on bootup
    )


class LightDimmableState(BaseModel):
    '''Component state model for a light that can
        - turned on/off
        - Dimmed between 5-100% as set in the min and max brightness.'''
    # TODO: We could inherit from SimpleLightState
    # inherits onOff
    onOff: Optional[Literal[EventValues.OFF, EventValues.ON]] = Field(
        None,
        description='Schema for a simple on off state, currently allows None as the initial value',
        eventId=RVEvents.LIGHTING_ZONE_MODE_CHANGE,
        setting=True
    )

    brt: Optional[int] = Field(
        None,
        ge=MIN_LIGHTING_BRIGHTNESS,
        le=MAX_LIGHTING_BRIGHTNESS,
        description='Brightness level for the simple dimmable light',
        eventId=RVEvents.LIGHTING_ZONE_BRIGHTNESS_LEVEL_CHANGE,
        store_db=True,
        initial=DEFAULT_BRIGHTNESS
    )

    dim: Optional[int] = Field(
        None,
        description='Change in brightness level while switch is held',
        eventId=None
    )


class LightRGBWState(BaseModel):
    '''Component state model for a light that can support on/off,
    brightness, RGBW and color temp.

    This was introduced for ITC controllers that have RGBW, so there might
    be the need for an RGB light if upcoming lights don't have the separate
    white channel.'''
    onOff: Literal[
            EventValues.OFF,
            EventValues.ON] = Field(
        None,
        description='Schema for a simple on off state, currently allows None as the initial value',
        eventId=RVEvents.LIGHTING_ZONE_MODE_CHANGE,
        setting=True
    )
    brt: int = Field(
        None,
        ge=MIN_LIGHTING_BRIGHTNESS,
        le=MAX_LIGHTING_BRIGHTNESS,
        description='Brightness level for the simple dimmable light',
        eventId=RVEvents.LIGHTING_ZONE_BRIGHTNESS_LEVEL_CHANGE,
        store_db=True,
        setting=True,
        initial=DEFAULT_BRIGHTNESS
    )
    rgb: str = Field(
        None,
        description='RGB values as a string, accepts #FFFFFF or FFFFFF in the HTML format for RRGGBB',
        eventId=RVEvents.LIGHTING_ZONE_RGBW_COLOR_CHANGE,
        setting=True,
        store_db=True
    )
    clrTmp: int = Field(
        None,
        ge=3000,
        le=10000,
        description='Color temperature in Kelvin',
        eventId=RVEvents.LIGHTING_ZONE_COLOR_TEMP_CHANGE,
        setting=True,
        store_db=True
    )
    dim: Optional[int] = Field(
        None,
        description='Change in brightness level while switch is held',
        eventId=None
    )


class LightSimple(BaseComponent):
    '''Component for a simple light'''
    category: str = CATEGORY
    code: str = COMP_TYPE_LIGHT_ZONE
    type: str = 'simple'
    state: LightSimpleState = LightSimpleState()

    # TODO: Put common lighting stuff into a base lighting class
    def override_light_groups(self):
        '''Similar to the light groups method but this does not save.
        Acts upon any changes to any given non hidden light zone.'''
        for group_id, group in self.hal.lighting.handler.lighting_group.items():
            # We do not update special group 0 which is master/smarttoggle
            # Range of regular presents is between 1 - 99
            if group_id > 0 and group_id <= 50:
                group.state.onOff = EventValues.OFF

    def set_state(self, state):
        new_state = LightSimpleState(**state)

        if new_state.onOff is None:
            new_state.onOff = self.state.onOff

        self.hal.lighting.handler.set_zone_state(self.instance, new_state)
        self.override_light_groups()
        super().set_state(None)
        return self.state

    # def get_db_state(self):
    #     '''Override basic get db state.
    #     Additionally check on brt value to be not NONE.'''
    #     loaded_state = self.hal.app.get_config(self.config_key)
    #     if loaded_state is None:
    #         print(f'No config found for {self.config_key}')
    #         # TODO: Load default
    #         self.state = LightDimmableState()
    #     else:
    #         self.state = LightDimmableState(**loaded_state)

    #     # Perform extra check that brt is not NONE
    #     if self.state.brt is None:
    #         self.state.brt = DEFAULT_BRIGHTNESS

    #     return self.state


class LightDimmable(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_LIGHT_ZONE
    type: str = "dimmable"
    state: LightDimmableState = LightDimmableState()

    def override_light_groups(self):
        '''Similar to the light groups method but this does not save.
        Acts upon any changes to any given non hidden light zone.'''
        for group_id, group in self.hal.lighting.handler.lighting_group.items():
            # We do not update special group 0 which is master/smarttoggle
            # Range of regular presents is between 1 - 99
            if group_id > 0 and group_id <= 50:
                group.state.onOff = EventValues.OFF

    def set_state(self, state):
        new_state = LightDimmableState(**state)

        if new_state.brt is None:
            new_state.brt = self.state.brt

        if new_state.onOff is None:
            new_state.onOff = self.state.onOff

        self.hal.lighting.handler.set_zone_state(self.instance, new_state)
        self.override_light_groups()
        super().set_state(None)
        return self.state


class LightRGBW(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_LIGHT_ZONE
    type: str = 'rgbw'
    # componentId: str = f'{CATEGORY}.{COMP_TYPE_LIGHT_ZONE}_rgbw'
    state: LightRGBWState = LightRGBWState()


class LightGroupState(BaseModel):
    onOff: Optional[Literal[EventValues.OFF, EventValues.ON]] = Field(
        EventValues.OFF,
        description='Lighting Group / Preset onOff state, OFF is a state, not settable',
        eventId=RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_OPERATING_MODE_CHANGE,
        setting=True
    )
    save: Optional[Literal[EventValues.TRUE, ]] = Field(
        None,
        description='If set to True we save the current lighting settings to the light_map',
        setting=True,
        exclude=True        # TODO: What does it do ?
    )
    light_map: Optional[List[dict]] = Field(
        [],
        description='Light state to be achieved when this preset is activated, will need to be loaded by the user DB',
        setting=False,
        store_db=True
    )


class LightGroupSmartState(BaseModel):
    '''Class for the Smart Toggle lighting group.'''
    onOff: Optional[Literal[EventValues.OFF, EventValues.ON]] = Field(
        EventValues.OFF,
        description='Lighting Group onOff state',
        eventId=RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_OPERATING_MODE_CHANGE,
        setting=True
    )
    brt: Optional[int] = Field(
        None,
        ge=MIN_LIGHTING_BRIGHTNESS,
        le=MAX_LIGHTING_BRIGHTNESS,
        description='Brightness level for the lights of this lighting group (when on)',
        eventId=RVEvents.LIGHTING_GROUP_BRIGHTNESS_LEVEL_CHANGE,
        setting=True,
        store_db=True,
        initial=DEFAULT_BRIGHTNESS
    )
    light_map: Optional[List[dict]] = Field(
        [],
        description='Light state to be achieved when this preset is activated, will need to be loaded by the user DB',
        setting=False,
        store_db=True
    )

class LightGroup(BaseComponent):
    category: str = CATEGORY
    code: str = COMP_TYPE_LIGHT_GROUP
    type: str = 'basic'
    # componentId: str = f'{CATEGORY}.{COMP_TYPE_LIGHT_GROUP}_basic'
    state: LightGroupState = LightGroupState()

    def set_state(self, state):
        # TODO: Implement this properly
        super().set_state(None)

    def override_light_groups(self):
        for group_id, group in self.hal.lighting.handler.lighting_group.items():
            # We do not update special group 0 which is master/smarttoggle
            if group_id > 0 and group_id <= 50:
                group.state.onOff = EventValues.OFF
                group.save_db_state()
                group.set_state(None)

    def save(self):
        '''Save the current lighting map to this preset.'''
        # Get all current light zones states except hidden
        new_map = []
        for zone_id, light_zone in self.hal.lighting.handler.lighting_zone.items():
            # We do not store hidden lighting zones in presets
            if light_zone.attributes.get('hidden') is True:
                continue

            if light_zone.state.onOff is None:
                light_zone.state.onOff = EventValues.OFF

            new_map.append(
                {
                    'instance': zone_id,
                    'state': deepcopy(light_zone.state.dict())
                }
            )
        self.state.light_map = new_map

        self.override_light_groups()

        self.state.onOff = EventValues.ON

        return self.state

    def activate(self):
        '''Activate the mapped lights of this preset.'''
        # Check if there are stored lights in the map
        if not self.state.light_map:
            raise ValueError('Light Group has no mapped lights yet.')

        for light in self.state.light_map:
            instance = light['instance']
            state = light['state']
            try:
                light_zone = self.hal.lighting.handler.lighting_zone[instance]
            except KeyError as e:
                print(
                    'Cannot find lighting zone, likely previous floorplan issue on lighting zone',
                    instance,
                    e
                )
                continue
            light_zone.set_state(state)

        self.override_light_groups()

        # Now we set our own instance state to on
        self.state.onOff = EventValues.ON

        self.save_db_state()

        # Emit events
        super().set_state(None)

        return self.state

    def check_group(self, attribute: str, skip_if_True: bool = True):
        # Check the zone - skip lights accordingly
        new_map = []
        temp_state = EventValues.OFF  # chane to ON if we find and lit
        for zone_id, light_zone in self.hal.lighting.handler.lighting_zone.items():
            # We do not store hidden lighting zones in presets
            if light_zone.attributes.get(attribute) is True:
                if skip_if_True is True:
                    continue
            elif light_zone.attributes.get(attribute) is None:
                if skip_if_True is False:
                    continue
            if light_zone.attributes.get('hidden') is True:
                continue

            if light_zone.state.onOff is None:
                light_zone.state.onOff = EventValues.OFF
            elif light_zone.state.onOff == EventValues.ON:
                temp_state = EventValues.ON

            new_map.append(
                {
                    'instance': zone_id,
                    'state': deepcopy(light_zone.state.dict())
                }
            )
        self.state.light_map = new_map
        self.state.onOff = temp_state  # We just recomputed our state
        result = {
            "onOff": self.state.onOff,
            "light_map": new_map
        }
        return result

    # def get_db_state(self):
    #     loaded_state = self.hal.app.get_config(self.config_key)
    #     if loaded_state is None:
    #         print(f'No config found for {self.config_key}')
    #         # TODO: Load default
    #         self.state = LightGroupState()
    #     else:
    #         self.state = LightGroupState(**loaded_state)

    #     return self.state


class SmartLightGroup(BaseComponent):
    '''Component for Smart Toggle lighting group.'''
    category: str = CATEGORY
    code: str = COMP_TYPE_LIGHT_GROUP
    type: str = 'smart'

    state: LightGroupSmartState = LightGroupSmartState()

    def set_state(self, state):
        # TODO: Implement this properly
        super().set_state(None)

    def override_light_groups(self):
        for group_id, group in self.hal.lighting.handler.lighting_group.items():
            # We do not update special group 0 which is master/smarttoggle
            if group_id > 0 and group_id <= 50:
                group.state.onOff = EventValues.OFF
                group.save_db_state()


    def check_group(self, attribute: str, skip_if_True: bool=True):
        # Check the zone - skip lights accordingly
        new_map = []
        temp_state = EventValues.OFF  # chane to ON if we find and lit
        for zone_id, light_zone in self.hal.lighting.handler.lighting_zone.items():
            # We do not store hidden lighting zones in presets
            if light_zone.attributes.get(attribute) is True:
                if skip_if_True is True:
                    continue
            elif light_zone.attributes.get(attribute) is None:
                if skip_if_True is False:
                    continue
            if light_zone.attributes.get('hidden') is True:
                continue

            if light_zone.state.onOff is None:
                light_zone.state.onOff = EventValues.OFF
            elif light_zone.state.onOff == EventValues.ON:
                temp_state = EventValues.ON

            new_map.append(
                {
                    'instance': zone_id,
                    'state': deepcopy(light_zone.state.dict())
                }
            )
        self.state.light_map = new_map
        self.state.onOff = temp_state  # We just recomputed our state
        result = {
            "onOff": self.state.onOff,
            "light_map": new_map
        }
        return result

if __name__ == '__main__':
    import json

    # from helper import generate_component

    # for component in (LightSimple, LightDimmable, LightRGBW, LightGroup):
    #     print(json.dumps(generate_component(component), indent=4))
    x = LightSimple(
        state=LightSimpleState(
            onOff=EventValues.DATA_INVALID
        )
    )

    print(x)
    print(x.schema_json())
