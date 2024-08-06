import importlib
import platform
import sys

from common_libs.models.common import ATTR_TO_CODE
from main_service.modules.hardware.common import EventLogger
from main_service.modules.storage_helper import (
    read_floorplan_config_json_file
)

if 'Windows' == platform.system():
    sys.path.append('./main_service/')

# TODO: Figure out if we want this to be prefixed or passed in the config
MODULE_PREFIX = 'main_service.'
# TODO: Make this work to restrict importing to hardware folder
# MODULE_PREFIX = 'main_service.modules.hardware.'


class HAL(object):
    '''Hardware Abstraction Layer object.
    Does retain access to all HW and SW features so they can talk to each other
    but remain smaller for better visibility.'''
    def __init__(self, cfg, app):
        self.cfg = cfg
        self.app = app

        self.floorPlan = cfg.get('floorPlan')
        self.optionCodes = cfg.get('optionCodes', ['NOT_SET',])
        self.can_mapping = cfg.get('can_mapping')
        self.hal_categories = cfg.get('hal_categories')
        self.hal_options = cfg.get('hal_options', [])

        self.loaded_categories = {}

        if self.hal_categories is None:
            raise ValueError(f'Config file does not provide HAL categories: {cfg}')

        for hw, module in self.hal_categories.items():
            # import the module and get a handler
            full_module = f'{MODULE_PREFIX}{module}'
            hw_mod = importlib.import_module(full_module)

            # TODO: Change this to a dataclass
            handler_class = hw_mod.module_init[0]
            handler_config_default_key = hw_mod.module_init[1]
            handler_components = hw_mod.module_init[2]

            if handler_config_default_key is None:
                hw_cfg = cfg
            else:
                hw_cfg = cfg.get(handler_config_default_key, {})

            if hw_cfg is None:
                raise ValueError('No values in hw_cfg')

            hw_instance = handler_class(
                config=hw_cfg,
                components=cfg.get("components", []),
                app=app
            )

            try:
                setattr(self, hw, hw_mod)
                setattr(getattr(self, hw), 'handler', hw_instance)
            except ModuleNotFoundError as err:
                print('Cannot import: {} / {}, error: {}'.format(hw, full_module, err))
                raise

            # Initialize all module handlers as well
            getattr(self, hw).handler.setHAL(self)

        for msg, module in self.can_mapping.items():
            # print('Can Map Alignment', msg, module)
            try:
                self.can_mapping[msg] = getattr(self, module)
            except ModuleNotFoundError as err:
                print('Cannot import: {} / {}, error: {}'.format(hw, module, err))
                raise

        self.init_app()
        self.init_categories()

    def init_app(self):
        '''Initialize the app.'''
        # TODO: Is this doing anything that has not moved to other places already ?
        print('[APP][INIT] Initialize APP pointers')
        for hw, module in self.hal_categories.items():
            print('[APP][INIT] -> ', hw, module)
            try:
                getattr(self, hw).handler.setEventLogger()
            except AttributeError as err:
                print('Failed to set event logger', err)
                sys.exit(1)

            try:
                # ONLY hw_climate does anything with this function _init_config()
                getattr(self, hw).handler._init_config()
            except AttributeError as err:
                print('Failed to init config for', hw, err)

        self.event_logger = EventLogger(self.app.event_logger)
        print('Setting event logger')

    def init_categories(self):
        '''Initialize categories so HAL can reference what has been loaded.
        Might not be actively used.'''
        for hw, modules in self.hal_categories.items():
            handler = getattr(self, hw).handler
            try:
                self.loaded_categories[hw] = handler.loaded_components
            except AttributeError as err:
                print(err)
                # Happens for Wineguard

    def get_state(self):
        '''Retrieve the full state.'''
        state = {}
        for category, components in self.loaded_categories.items():
            state[category] = {}
            for component in components:
                # print(category, component)
                handler = getattr(self, category).handler
                # print(handler)
                for instance, comp in getattr(handler, component).items():
                    # print(instance)
                    short_key = f'{ATTR_TO_CODE.get(component)}{instance}'
                    if short_key not in state[category]:
                        state[category][short_key] = {}

                    comp_state = comp.state
                    # print('KEYS', short_key, component)

                    state[category][short_key] = comp_state
        return state

    def updateStates(self):
        for hw, modules in self.hal_categories.items():
            handler = getattr(self, hw).handler
            handler.updateStates()

    def emit_state_events(self, obj):
        # print('Emitting state values for', obj, obj.state)
        for event_prop, value in obj.state.dict().items():
            # Get the eventId
            event_id = obj.eventIds.get(event_prop)
            # print('-----> Event ID', event_id, type(event_id))
            if event_id is None:
                # print(f'No event for state property {event_prop}')
                pass
            else:
                # TODO: Why are we not re-using a single event logger handle in the app ?
                if self.event_logger is not None:
                    # print('>>>>Emitting now')
                    self.event_logger.add_event(
                        event_id,
                        obj.instance,  # Report instance '1' for the platform,
                        value
                    )
                    # print('<<<<Emission success')
                else:
                    print('No event logger')


def init_hw_layer(app, floorplan, options: list = []):
    '''Read the floorplan and create the HAL object.'''
    print('Setting floorplan', floorplan)
    cfg = read_floorplan_config_json_file(floorplan, options)
    hw_layer = HAL(cfg, app)

    check_passed = True

    return hw_layer, cfg, check_passed


if __name__ == '__main__':
    pass
