from abc import abstractmethod
from copy import deepcopy
import time
import subprocess

from common_libs.models.common import (
    EventValues,
    RVEvents,
    LogEvent,
    CODE_TO_ATTR,
    ATTR_TO_CODE
)

from main_service.components.catalog import component_catalog


SMARTTOGGLE_LAST_TRIGGERED_KEY = 'lighting__smarttoggle__last_trigger_time'


def shell_cmd(cmd: str, print_it=0):
    if print_it != 0:
        print('Shell cmd =', cmd)

    success = False
    try:
        result = subprocess.run(
            cmd.split(' '),
            capture_output=True
        )
        if result.returncode == 0:
            success = True
    except FileNotFoundError as err:
        print('FileNotFound', err)

    return success


# TODO: We need a base component type to help with common functions
# We could start with the common functions helping to read the input
# json and creating the keys in the appropriate systems

# class RVComponent(object):
#     def __init__(self, config={}):
#         self.attributes = config.get('attributes', {})
#         self.properties = config.get('properties', {})

#     def get_meta(self):
#         return self.attributes

#     def get_state(self):
#         return self.properties

#     def set_property(self, property: str, value):
#         self.properties[property] = value

#     def get_property(self, property: str):
#         return self.properties[property]

#     def get_atribute(self, atribute: str):
#         return self.atributes[atribute]


class HALBaseClass(object):
    def __init__(self, config={}, components=[], HAL=None, app=None):
        self.state = {}
        self.savedState = {}
        self.config = config
        self.components = components
        self.loaded_components = {}
        self.COMP_INSTANCES = []
        self.hw_config = {}
        self.HAL = HAL
        self.app = app
        self.meta = {}
        self.CODE_TO_ATTR = CODE_TO_ATTR
        self.ATTR_TO_CODE = ATTR_TO_CODE
        # self.set_initial_state()

    def init_components(self, components, category=None):
        if category is not None:
            components = [
                c for c in components if c.get('componentTypeId').startswith(category)
            ]

        for component in components:
            attributes = component.get('attributes', {})
            component_type_id = component.get('componentTypeId')

            # Get the dataclass from __init__ in components
            component_class = component_catalog.get(component_type_id)

            if component_class is None:
                print('>' * 30, 'Cannot get component for', component_type_id)
                # print(component_catalog.keys())
                continue

            # Create the object
            obj = component_class.component(
                instance=component.get('instance'),
                name=attributes.get('name'),
                description=component.get('description', 'No description'),
                state=component_class.state(),
                relatedComponents=component.get('relatedComponents'),
                hal=self,
                meta=component.get('meta')
            )
            # Try to load state from database
            # try:
            #     setattr(obj.state, 'hal', self)
            # except ValueError as err:
            #     print('Cannot set HAL for', obj)

            self.COMP_INSTANCES.append(obj)

            # Iterate over state properties and get the evenId out of the schema
            state_schema = obj.state.schema()

            # {'title': 'WaterTankState', 'type': 'object', 'properties': {'lvl': {'title': 'Lvl', 'description': 'Level of the given tank in % between 0 - 100%', 'default': 0, 'minimum': 0, 'maximum': 100, 'eventId': <RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE: 8600>, 'type': 'integer'}}}
            for item in obj.state:
                event_id = state_schema["properties"].get(item[0], {}).get("eventId")
                obj.eventIds[item[0]] = event_id

            # Inject additional attributes from the model definition (componentGroup) to the the defaults in the component
            # NOTE: We could just use dict.update instead of iterating
            for attr_key, attr_value in attributes.items():
                obj.attributes[attr_key] = attr_value

            # look up the desired internal name for the attribute
            # The short code could have some benefits as it could use the same method of getattr from the API
            long_code = self.CODE_TO_ATTR.get(component_class.code)
            if long_code is None:
                raise ValueError(f'Cannot find {component_class.code}')

            # Check if the attribute is present and of the type dict
            # (otherwise we migth overwrite internal attributes based on faulty parsing)
            # This is not fully secure as a pre-existing attribute of the type dict would still be overwritten
            # Could possibly check if the first result in the dict is a component
            if hasattr(self, long_code):
                handle = getattr(self, long_code)
                if isinstance(handle, type({})):
                    handle[obj.instance] = obj
                else:
                    raise AttributeError(f'Cannot overwrite existing attribute: {long_code}')
            else:
                handle = {
                    obj.instance: obj
                }
                setattr(self, long_code, handle)

            if long_code in self.loaded_components:
                self.loaded_components[long_code][obj.instance] = obj
            else:
                self.loaded_components[long_code] = {
                    obj.instance: obj
                }

    def set_initial_state(self):
        initial_state = self.config.get('initial_state')
        if initial_state is None:
            return

        # print('Initial State', initial_state)

        for key, value in initial_state.items():
            self.state[key] = value

        return self.state

    def setHAL(self, hal_obj):
        '''Sets the hal object for central use and provides a reference to each component.
        Also triggers reading from the DB where it is applicable.'''
        self.HAL = hal_obj
        for cat_component in self.COMP_INSTANCES:
            cat_component.set_hal(self.HAL)
            cat_component.set_state_initial()
            cat_component.set_attribute_defaults()
            cat_component.get_db_state()

    def updateStates(self):
        for cat_component in self.COMP_INSTANCES:
            cat_component.update_state()

    def setEventLogger(self, handler=None):
        if handler is None:
            # Can be used to overwrite the logger for testing individual HW layers
            handler = self.HAL.app.event_logger
        self.event_logger = EventLogger(handler)
        print('Setting event logger', __name__)

    def set_state(self, system, system_id, new_state):
        system_key = f'{system}__{system_id}'
        self.state[system_key] = new_state

        return self.state[system_key]

    def get_state(self, system=None, system_id=None):
        '''Return state of corresponding system.'''
        if system is None:
            return self.state
        else:
            system_key = f'{system}__{system_id}'
            return self.state.get(system_key, {})

    def get_systems(self, system=None):
        if system is None:
            # Get them all
            # TODO: Implement
            return []

        response = []
        for key, value in self.state.items():
            # print(key)
            if system in key:
                # print('System', system, key, value)
                # result = {k: v for k, v in value.items()}
                result = {}
                result['system_key'] = key
                result['meta'] = self.meta.get(key, {})
                result['state'] = self.state.get(key, {})
                response.append(result)

        return response

    def emit_event(self, obj, properties):
        '''Emit the associated event if present.'''
        for event_prop in properties:
            # Get the eventId
            event_id = obj.eventIds.get(event_prop)
            if event_id is None:
                print('NOT GOOD')
            else:
                self.event_logger.add_event(
                    event_id,
                    obj.instance,  # Report instance '1' for the platform,
                    getattr(obj.state, event_prop)
                )

    def update_can_state(self, system, body) -> dict:
        raise NotImplementedError('Base Class does not handle update_can_state')


class EventLogger(object):
    def __init__(self, log_handle):
        self.logger = log_handle

    def add_event(self, event, instance, value, meta=None):
        # print('Received Event:', event, instance, value)
        try:
            return self.logger(
                LogEvent(
                    timestamp=time.time(),
                    event=event,
                    instance=instance,
                    value=value,
                    meta=meta
                )
            )
        except Exception as err:
            print('Exception', err)
            print('event', event)
            print('instance', instance)
            print('value', value)


class BaseWaterSystems(HALBaseClass):
    '''Provides all methods and attributes that are required for a watersystems class.'''
    def __init__(self, config={}, components=[], app=None):
        HALBaseClass.__init__(self, config=config, components=components, app=app)

    def get_pump_state(self, pump_id: int):
        pump_key = f'wp{pump_id}'
        # TODO: Add defaults for states to be returned and maybe emit an event for tracking
        # That a given state was not initialized
        return self.state.get(pump_key)

    def set_pump_state(self, pump_id: int):
        raise NotImplementedError('Method not implemented')

    def get_heater_state(self, heater_id: int):
        heater_key = f'wh{heater_id}'
        # TODO: Add defaults for states to be returned and maybe emit an event for tracking
        # That a given state was not initialized
        return self.state.get(heater_key)

    def set_heater_state(self, heater_id: int):
        raise NotImplementedError('Method not implemented')

    def get_tank_state(self, tank_id: int):
        tank_key = f'wt{tank_id}'
        # TODO: Add defaults for states to be returned and maybe emit an event for tracking
        # That a given state was not initialized
        return self.state.get(tank_key)


class BaseEnergy(HALBaseClass):
    '''Provides all methods and attributes that are required for a watersystems class.'''

    def __init__(self, config={}, hal=None):
        HALBaseClass.__init__(self, config=config)


class BaseVehicle(HALBaseClass):
    '''Provides all methods and attributes that are required for a watersystems class.'''

    def __init__(self, config={}, hal=None):
        HALBaseClass.__init__(self, config=config)


class BaseClimate(HALBaseClass):
    '''Provides all methods and attributes that are required for a watersystems class.'''

    def __init__(self, config={}, hal=None):
        HALBaseClass.__init__(self, config=config)

    def get_thermostat_state(self, zone_id: int):
        thermostat_key = f'thermostat__{zone_id}'
        return self.state.get(thermostat_key)

    def set_thermostat_state(self, zone_id: int, state: dict):
        raise NotImplementedError('Method not implemented')

    def get_rooffan_state(self, fan_id: int):
        raise NotImplementedError('Method not implemented')

    def set_rooffan_state(self, fan_id: int, state: dict):
        raise NotImplementedError('Method not implemented')

    def get_ac_state(self, zone_id: int):
        raise NotImplementedError('Method not implemented')

    def set_ac_state(self, zone_id: int, state: dict):
        raise NotImplementedError('Method not implemented')

    def get_heater_state(self, zone_id: int):
        raise NotImplementedError('Method not implemented')

    def set_heater_state(self, zone_id: int, state: dict):
        raise NotImplementedError('Method not implemented')

    def get_temp_state(self, sensor_id: int):
        '''Get individual sensor data for outdoor, refrigerator.'''
        # TODO: Create mapping that would allow asking for 'OUTDOOR', 'FRIDGE', 'FREEZER' rather than a number
        raise NotImplementedError('Method not implemented')


class BaseLighting(HALBaseClass):
    '''Provides all methods and attributes that are required for a lightings class.'''
    LG_MASTER = 0       # ID for the master lighting group
    LG_ALL = 101        # ID for all lights
    ALL_ON_INTERVAL = 2     # Second(s)

    def __init__(self, config={}, components=[], app=None):
        HALBaseClass.__init__(self, config=config, app=app)
        self.state['smarttoggle'] = None
        # self.lighting_zones = None

    def get_zone_state(self, zone_id: int):
        zone_key = f'lz__{zone_id}'
        return self.state.get(zone_key)

    def set_zone_state(self, zone_id: int, state: dict):
        raise NotImplementedError('Method not implemented')

    def get_group_state(self, group_id: int):
        group_key = f'lg__{group_id}'
        return self.state.get(group_key)

    def save_lightingGroup(self, group_id: int, state: dict):
        raise NotImplementedError('Method not implemented')

    def activate_lightingGroup(self, group_id: int):
        raise NotImplementedError('Method not implemented')

    def zone_switch(self):
        '''Switch zones on/off'''
        raise NotImplementedError('Method not implemented')

    def zone_rgbw(self):
        '''Adjust zone RGB-W color.'''
        raise NotImplementedError('Method not implemented')

    def zone_brightness(self):
        '''Adjust zone brightness.'''
        raise NotImplementedError('Method not implemented')

    def zone_colortemp(self):
        raise NotImplementedError('Method not implemented')

    def toggle_zone_switch(self, zone_id, on_off):
        '''Method to toggle state of a zone'''
        raise NotImplementedError('Method not implemented')

    def notification(self, level):
        '''Method to provide light notifications.'''
        raise NotImplementedError('Method not implemented')

    def allLights(self, state):
        '''Handles settings to all lights.'''
        onOff = state.get('onOff')
        brt = state.get('brt')

        brt_set = False
        if onOff == EventValues.OFF:
            # Turn all off
            for i, lz in self.HAL.lighting.handler.lighting_zone.items():
                if lz.attributes.get('hidden', False) is False:
                    self.zone_switch(i, onOff)
                    brt_set = True  # We do not want to set brightness if we turned off

        elif onOff == EventValues.ON:
            # Turn ALL on
            for i, lz in self.HAL.lighting.handler.lighting_zone.items():
                if lz.attributes.get('hidden', False) is False:
                    if brt is not None:
                        self.zone_brightness(i, brt)
                        brt_set = True  # We do not want to set brightness if we turned off
                    self.zone_switch(i, onOff)

        if brt_set is False and brt is not None:
            for i, lz in self.HAL.lighting.handler.lighting_zone.items():
                if lz.attributes.get('hidden', False) is False:
                    self.zone_brightness(i, brt)

        return

    def smartToggle(self, state, instance=0, attr_filter={}):
        '''Toggles all lights off, memorizes setting to bring back.'''
        # Convert to dict if we get a state obj
        if hasattr(state, 'onOff'):
            state = state.dict()

        if instance == self.LG_ALL:
            print('[LIGHTING] Received LG ALL')
            # Handle this in all lightgs
            _ = self.allLights(state)
            self.lighting_group[instance].state

        elif instance != self.LG_MASTER:
            raise ValueError(f'Smarttoggle does not support this lighting group id: {instance}')

        onOff = state.get('onOff')
        brt = state.get('brt')

        light_group = self.lighting_group.get(instance)
        print('Smarttoggle received', onOff)

        if onOff == EventValues.OFF:
            # Reset Time for double press of 6-way switch
            self.HAL.system.handler.state[SMARTTOGGLE_LAST_TRIGGERED_KEY] = None

            if self.state['smarttoggle'] == EventValues.OFF:
                print('Smarttoggle: Received same state that we already have, ignore ?')

                # return light_group.state

            current_state = deepcopy(self.state)

            for k, v in current_state.items():
                print('key:', k, 'value:', v)
                self.savedState[k] = v

            print('Saved state as', self.savedState)

            # print('LZs', self.lighting_zones)

            for zone_id, zone in self.lighting_zone.items():
                if zone.attributes.get('hidden', False) is False:
                    self.zone_switch(zone_id, 0)

            self.state['smarttoggle'] = EventValues.OFF
            light_group.state.onOff = onOff

            self.event_logger.add_event(
                RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_OPERATING_MODE_CHANGE,
                self.LG_MASTER,
                onOff
            )

        elif onOff == EventValues.ON:
            # Check when the last on request was sent
            if self.state.get('smarttoggle') == EventValues.ON:
                last_trigger_time = self.HAL.system.handler.state.get(SMARTTOGGLE_LAST_TRIGGERED_KEY)
                if last_trigger_time is not None and time.time() - last_trigger_time < self.ALL_ON_INTERVAL:
                    print('Need ALL on')
                    self.HAL.system.handler.state[SMARTTOGGLE_LAST_TRIGGERED_KEY] = None
                    if hasattr(self, 'all_on'):
                        print('Setting all lights on')
                        self.all_on()
                        self.state['last_smarttoggle_action'] = 'ALL_ON'
                else:
                    self.HAL.system.handler.state[SMARTTOGGLE_LAST_TRIGGERED_KEY] = time.time()
            else:
                if self.state['smarttoggle'] == EventValues.ON:
                    # We are already on, ignore ?
                    return light_group.state

                at_least_one_light = False
                for k, v in self.savedState.items():
                    # TODO: Change this iteration to something useful
                    print('key:', k, 'value:', v)
                    if k in ('preset_1', 'preset_2', 'preset_3', 'smarttoggle', '0', 0, 'last_smarttoggle_action'):
                        continue

                    try:
                        self.zone_switch(k, v.get('onOff', 0))
                        if brt is not None:
                            self.zone_brightness(zone_id, brt)
                        if v.get('onOff') == 1:
                            at_least_one_light = True
                    except AttributeError as err:
                        print('[ERROR]', err)
                        continue

                if at_least_one_light is False:
                    try:
                        for lz in self.HAL.lighting.DEFAULT_LIGHTS:
                            self.zone_switch(lz, 1)
                    except AttributeError as err:
                        print('Cannot set DEFAULT_LIGHTS', err)

                self.state['last_smarttoggle_action'] = 'SMART'

            self.state['smarttoggle'] = EventValues.ON
            light_group.state.onOff = onOff

            self.event_logger.add_event(
                RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_OPERATING_MODE_CHANGE,
                self.LG_MASTER,
                onOff
            )

        elif brt is not None:
            for zone_id, zone in self.lighting_zone.items():
                if zone.attributes.get('hidden', False) is False:
                    if zone.state.onOff == EventValues.ON:
                        self.zone_brightness(zone_id, brt)
        else:
            self.state['smarttoggle'] = None
            raise ValueError(f'Cannot handle value of {state}')

        # Disable presets on change of smarttoggle
        try:
            light_group.override_light_groups()
        except KeyError:
            pass

        if brt is not None:
            light_group.state.brt = brt

        return light_group.state


if __name__ == '__main__':
    handler = HALBaseClass()
    print(handler)

    def test_logger(event):
        print(event)

    logger = EventLogger(test_logger)
    print(logger.add_event(1000, 1, 1))
