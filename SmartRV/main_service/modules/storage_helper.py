"""Module to support data storage."""

from configparser import ConfigParser

import json
import logging
import os
import platform
import sys
import re

from common_libs.system.system_logger import prefix_log

from main_service.modules.system_helper import (
    check_partitions,
)

from common_libs import environment
_env = environment()

class MyException(Exception):
    pass

sys_platform = platform.system()
wgo_logger = logging.getLogger('main_service')

DEFAULT_FLOORPLAN = 'VANILLA'
DEFAULT_OPTIONS = ''


def set_floorplan(floorplan: str, optioncodes: str = "") -> bool:
    if floorplan in get_floorplans_available():
        ini_file = ConfigParser()
        filereadresult = ini_file.read(
            _env.storage_file_path('UI_config.ini')
        )
        if optioncodes is None:
            optioncodes = ""  # Must be string for ini

        ini_file['Vehicle'] = {
            'floorplan': floorplan,
            'optioncodes': optioncodes
        }

        with open(_env.storage_file_path('UI_config.ini'), 'w') as configfile:
            ini_file.write(configfile)

        result = {
            'status': 'OK',
            'msg': 'HAL will be reloaded.'
        }
    else:
        raise ValueError(f'Floorplan not available: {floorplan}')

    return result


def read_ui_config_file(path='UI_config.ini'):
    '''Read floorplan of config.'''
    cfg_path = _env.storage_file_path(path)
    have_ini = os.path.isfile(cfg_path)

    write_default = False

    if have_ini is False:
        floorplan = DEFAULT_FLOORPLAN
        options = DEFAULT_OPTIONS
        write_default = True
    else:
        ini_file = ConfigParser()
        ini_file.read(cfg_path)
        try:
            floorplan = ini_file['Vehicle']['floorplan']
        except KeyError as err:
            prefix_log(wgo_logger, "read_ui_config_file", f"floorplan {err}")
            floorplan = DEFAULT_FLOORPLAN
            write_default = True

        # Keep options separate for older ini's
        # older ini should be corrected by registations
        try:
            options = ini_file['Vehicle']['optioncodes']
        except KeyError as err:
            prefix_log(wgo_logger, "read_ui_config_file", f"optionCodes {err}")
            options = DEFAULT_OPTIONS

    if write_default is True:
        # We need to write the file for next read and update
        ini_file = ConfigParser()
        ini_file['Vehicle'] = {
            'floorplan': floorplan,
            'optioncodes': options
        }
        with open(_env.storage_file_path(path), 'w') as configfile:
            ini_file.write(configfile)

    return floorplan, options


def read_floorplan_config_json_file(floorplan='VANILLA', input_options: list = None):
    '''Read config for given floorplan.'''
    config_data = None
    ini_file = ConfigParser()

    # TODO: Change filename to all lowercase
    cfg_path = _env.storage_file_path('UI_config.ini')
    have_ini = os.path.isfile(cfg_path)
    # print('Have UI INI?', have_ini)

    if have_ini is False:
        # USE DEFAULT
        set_floorplan("VANILLA")
        prefix_log(wgo_logger, "read_floorplan_config_json_file", "VANILLA")

    ini_file.read(cfg_path)
    json_config_file = _env.data_file_path(f'Config_{ini_file["Vehicle"]["floorPlan"]}.json')

    try:
        config_data = json.load(open(json_config_file, 'r'))
    except IOError as err:
        prefix_log(wgo_logger, "read_floorplan_config_json_file", f"load {err}")
        raise
    except FileNotFoundError as err:
        wgo_logger.error(f'FileNotFoundError: {err}, {json_config_file}')
        raise

    # Get components
    component_group_filename = config_data.get('componentGroup', 'vanilla')
    component_group_filename = _env.data_file_path(f'{component_group_filename}.json')

    with open(component_group_filename, 'r') as component_file:
        component_group = json.load(component_file)

    # Temporary get the configured options until we get the unique instanced template from platform
    option_codes = config_data.get('hal_options', [])
    # Override if we got options from the platform
    if input_options is not None:
        option_codes = input_options

    # print('\nHal Options', option_codes)
    components = []
    for comp in component_group.get('components', []):
        # print(comp)
        component_option_codes = comp.get('filters', {}).get('optionCodes')
        # print(component_option_codes)
        # TODO BAW111 - we see Front bunk option loaded - why is lighitng not using it?
        if component_option_codes is None:
            components.append(comp)
            # print(f"Adding component {comp}")
        else:
            m = re.search(component_option_codes, str(option_codes))
            if m is None:
                # Did not match either positive nor negative
                continue
            else:
                prefix_log(wgo_logger, "read_floorplan_config_json_file", f"adding {comp}")
                components.append(comp)

    config_data['components'] = components
    config_data['optionCodes'] = option_codes

    return config_data


def get_floorplans_available() -> list:
    '''Check if the desired floorplan is available as a config.'''
    file_list = os.listdir(_env.data_file_path())
    file_list = [x for x in file_list if x.startswith('Config_')]
    floorplans = [os.path.splitext(x)[0].replace('Config_', '') for x in file_list]

    return floorplans
