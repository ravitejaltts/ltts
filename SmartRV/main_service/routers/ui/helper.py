'''Module with helper functions for UI.'''

from datetime import datetime
import os
from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

from main_service.modules.ui_helper import LOCKOUT_TEMPLATES

from main_service.modules.constants import (
    _celcius_2_fahrenheit,
    fahrenheit_2_celcius
)


BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')


def _convert_to_fahrenheit(temp_celsius):
    '''Temp copied here.'''
    return temp_celsius * 9 / 5 + 32


def get_tank_level_text(tank_details, decimals=0):
    # print('Tank details', tank_details)
    try:
        level = tank_details.get('lvl')
    except AttributeError as err:
        # print(err)
        # print(tank_details)
        # Use attribute directly as a state is passed in ?
        # TODO: Ensure the above is not called anymore and remove the try/except
        level = tank_details.state.lvl

    if level == 100:
        return 'Full'
    elif level == 0:
        return 'Empty'
    elif level == -1:
        return 'NA'
    elif level is None:
        return '--'
    elif level == '--':
        return '--'
    else:
        if decimals == 0:
            level_txt = f'{level:.0f}%'
        elif decimals == 1:
            level_txt = f'{level:.1f}%'
        elif decimals == 2:
            level_txt = f'{level:.2f}%'
        else:
            # NOTE: We do not want higher decimals but also do not
            # want to fail
            level_txt = f'{level:.2f}%'

        # Remove - if value is small negative, resulting in -0.0
        return level_txt.replace('-', '')


def get_pump_text(pump_state):
    # print('PUMP_STATE', pump_state)
    if pump_state == EventValues.ON:
        return 'On'
    elif pump_state == EventValues.OFF:
        return 'Off'
    else:
        return 'Unknown'


def get_heater_text(heater_state, unit='F'):
    if hasattr(heater_state, 'temp'):
        if heater_state.temp is None:
            temp = None
        else:
            if unit == 'F':
                temp = f'{_convert_to_fahrenheit(heater_state.temp)}'
            else:
                temp = f'{heater_state.temp}'
    else:
        temp = None

    if hasattr(heater_state, 'setTemp'):
        if heater_state.setTemp is None:
            setTemp = None
        else:
            if unit == 'F':
                setTemp = f'{_convert_to_fahrenheit(heater_state.setTemp):.0f}'
            else:
                setTemp = f'{heater_state.setTemp:.1f}'
    else:
        setTemp = None

    if hasattr(heater_state, 'onOff'):
        onOff = heater_state.onOff
    else:
        onOff = heater_state

    if temp is None and setTemp is None:
        temp_str = ' · Heating · Set point unknown'
    else:
        if setTemp == '0.0':
            temp_str = ' · Heating · Set point unknown'
        else:
            temp_str = f' · Heating to {setTemp}°{unit}'

    if onOff == EventValues.ON:
        return f'On' + temp_str
    elif onOff == EventValues.OFF:
        return 'Off'
    else:
        return 'Unknown'


def get_heating_pad_text(heater_state, unit='F'):
    if hasattr(heater_state, 'temp'):
        if unit == 'F':
            temp = f'{_convert_to_fahrenheit(heater_state.temp)}'
        else:
            temp = f'{heater_state.temp}'
    else:
        temp = None

    if hasattr(heater_state, 'setTemp'):
        if unit == 'F':
            setTemp = f'{_convert_to_fahrenheit(heater_state.setTemp)}'
        else:
            setTemp = f'{heater_state.setTemp}'
    else:
        setTemp = None

    if hasattr(heater_state, 'onOff'):
        onOff = heater_state.onOff
    else:
        onOff = heater_state

    if temp is None and setTemp is None:
        temp_str = ''
    else:
        if setTemp == '0.0':
            temp_str = ' · Heating · Set point unknown'
        else:
            temp_str = f' · Heating to {setTemp}°{unit}'

    if onOff == EventValues.ON:
        return f'On' + temp_str
    elif onOff == EventValues.OFF:
        return 'Off'
    else:
        return 'Unknown'


def get_onoff_text(onOff_state):
    if onOff_state == EventValues.ON:
        return 'On'
    elif onOff_state == EventValues.OFF:
        return 'Off'
    else:
        return f'NA ({onOff_state})'


def get_features(template, debug=False):
    '''Extract the features enabled and return the availble app features.'''
    raise NotImplementedError()


def create_ui_lockout(component, lockout, lockout_id):
    '''Takes a component, the lockout in question and provides specific
    text and schema adherance in return.'''
    # print('[LOCKOUT]', component.code, lockout, dir(lockout))
    # print('Lockout Attributes', lockout.attributes)

    template = LOCKOUT_TEMPLATES.get(component.code, {}).get(
        lockout_id,
        {
            'title': lockout.attributes.get(
                'name',
                'NOTSET'
            ),
            'subtext': lockout.attributes.get(
                'uiMsgSubtext',
                'SUBTEXT NOT SET'
            )
        }
    )
    lock = {
        'id': lockout_id,
        'level': 'WARNING',     # Check notification code to align the level
        'name': 'Lockout',
        'title': template.get('title'),
        'subtext': template.get('subtext'),
        'state': lockout.state.dict()
    }
    if lockout.attributes.get('timerUnit') == 'MINUTES':
        if lockout.state.durationSeconds is None:
            lock['state']['timer'] = '--:--'
        else:
            lock['state']['timer'] = '{}'.format(
                lockout.state.durationSeconds / 60
            )
    elif lockout.attributes.get('timerUnit') == 'SECONDS':
        if lockout.state.durationSeconds is None:
            lock['state']['timer'] = '--:--'
        else:
            lock['state']['timer'] = '{}'.format(
                round((lockout.state.expiry - datetime.now()).total_seconds()))

    return lock


def get_lighting_settings(app, list_key='items', section_key='sections'):
    lighting = app.config.get('lighting')
    # Get OEM data for each lighting zone
    # Add controller function etc.
    information = [
        {
            'title': 'MANUFACTURER INFORMATION',
            'items': []
        }
    ]
    if hasattr(app.hal.lighting.handler, 'lighting_zone'):
        for instance, lz in app.hal.lighting.handler.lighting_zone.items():
            information[0]['items'].append(
                {
                    "title": lz.attributes.get('name', "Lighting"),
                    section_key: [
                        {
                            'title': None,
                            list_key: [
                                {
                                    "key": "Manufacturer",
                                    "value": lz.meta.get('manufacturer'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    "key": "Product Model",
                                    "value": lz.meta.get('model'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    "key": "Part#",
                                    "value": lz.meta.get('part'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                }
                            ]
                        }
                    ]
                },
            )

    response = {
        'title': 'Lighting Settings',
        'configuration': [],
        'logos': {},
        'information': information,
        'notification': []
    }

    # TODO: Fix frontend and align what needs to be here
    # response = {}
    return response


def get_watersystems_settings(app, list_key='items', section_key='sections'):
    '''Pass in handle to app and build ui strucutre for settings.'''
    watersystems = app.config.get('watersystems')
    temp_preference = app.config.get('climate', {}).get('TempUnitPreference')

    water_heaters = []
    if hasattr(app.hal.watersystems.handler, 'water_heater'):
        for heat_id, heater in app.hal.watersystems.handler.water_heater.items():
            print('Heater State', heater.state, heater.attributes)
            # If it allows to set a temp it requires a setting here
            if hasattr(heater.state, 'setTemp'):
                set_temp = heater.state.setTemp
                if set_temp is None:
                    set_temp = '--'

                else:
                    if temp_preference == 'F':
                        # Convert to Fahrenheit and full number
                        set_temp = int(
                            round(
                                _celcius_2_fahrenheit(set_temp),
                                0
                            )
                        )
                    else:
                        # Check that we are on the closest 0.5 C level
                        set_temp = (round(set_temp * 2) / 2) * 1.0

                print('[SETTEMP]', set_temp)
                water_heaters.append(
                    {
                        'title': 'Water Heater',
                        list_key: [
                            {
                                'title': 'Water Heater Temperature',
                                'widget': 'TEMPERATURE_SETTING',
                                # 'selected_text': f'{set_temp}',
                                'selected_text': f'{set_temp} °{temp_preference}',
                                'options': [],
                                'state': {
                                    'setTemp': set_temp,
                                    'unit': temp_preference
                                },
                                'actions': {
                                    'TAP': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'{BASE_URL}/api/watersystems/wh/{heat_id}/state',
                                            'type': 'PUT',
                                            'params': {
                                                '$setTemp': 'int',
                                                'unit': temp_preference
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                'title': 'Restore Default',
                                'widget': 'SIMPLE_BUTTON',
                                'actions': {
                                    'PRESS': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'{BASE_URL}/api/watersystems/wh/{heat_id}/settings/restoredefault',
                                            'type': 'PUT',
                                            # 'params': {}
                                        }
                                    }
                                }
                            }
                        ]
                    }
                )

    config = [
        # NOTE: Removed until alignment what should be present here vs.
        # the feature settings section
        # {
        #     'title': 'Water Heater',
        #     'items': [
        #         {
        #             'title': 'Unit Preference',
        #             'selected_text': WATER_UNITS.get(volume_preference),
        #             'options': [
        #                 {
        #                     'key': 'Gallons (gal.)',
        #                     'value': 0,
        #                     'selected': volume_preference == WATER_UNIT_GALLONS
        #                 },
        #                 {
        #                     'key': 'Liters (L)',
        #                     'value': 1,
        #                     'selected': volume_preference == WATER_UNIT_LITER
        #                 },
        #             ],
        #             'actions': {
        #                 'TAP': {
        #                     'type': 'api_call',
        #                     'action': {
        #                         'href': f'{BASE_URL}/api/watersystems/settings',
        #                         'type': 'PUT',
        #                         'params': {
        #                             '$value': 'int',
        #                             'item': 'VolumeUnitPreference'
        #                         }
        #                     }
        #                 }
        #             },
        #             'action_default': {
        #                 'type': 'api_call',
        #                 'action': {
        #                     'href': f'{BASE_URL}/api/watersystems/settings',
        #                     'type': 'PUT',
        #                     'params': {
        #                         '$value': 'int',
        #                         'item': 'VolumeUnitPreference'
        #                     }
        #                 }
        #             }
        #         }
        #     ]
        # }
    ]
    config.extend(water_heaters)

    information = [
        {
            'title': 'MANUFACTURER INFORMATION',
            'items': []
        }
    ]
    # Heaters
    if hasattr(app.hal.watersystems.handler, 'water_heater'):
        for _, heater in app.hal.watersystems.handler.water_heater.items():
            heater_data = {
                "title": heater.attributes.get('name', "Water Heater"),
                section_key: [
                    {
                        "title": None,
                        list_key: [
                            {
                                "key": "Manufacturer",
                                "value": heater.meta.get('manufacturer'),
                                "type": "SETTINGS_SECTIONS_LIST_ITEM",
                            },
                            {
                                "key": "Product Model",
                                "value": heater.meta.get('model'),
                                "type": "SETTINGS_SECTIONS_LIST_ITEM",
                            },
                            {
                                "key": "Part#",
                                "value": heater.meta.get('part'),
                                "type": "SETTINGS_SECTIONS_LIST_ITEM",
                            }
                        ]
                    }
                ]
            }
            if heater.meta.get('logo') is not None:
                # Add logo to the meta items
                heater_data[section_key][0][list_key].append(
                    {
                        "key": "Logo",
                        "value": heater.meta.get('logo'),
                        "type": "LOGO",
                    }
                )

            information[0]['items'].append(
                heater_data
            )

    # Pumps
    if hasattr(app.hal.watersystems.handler, 'water_pump'):
        for _, pump in app.hal.watersystems.handler.water_pump.items():
            information[0]['items'].append(
                {
                    "title": pump.attributes.get('name', "Water Pump"),
                    section_key: [
                        {
                            "title": None,
                            list_key: [
                                {
                                    "key": "Manufacturer",
                                    "value": pump.meta.get('manufacturer'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    "key": "Product Model",
                                    "value": pump.meta.get('model'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    "key": "Part#",
                                    "value": pump.meta.get('part'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                }
                            ]
                        }
                    ]
                }
            )
    # Tanks
    if hasattr(app.hal.watersystems.handler, 'water_tank'):
        for _, tank in app.hal.watersystems.handler.water_tank.items():
            information[0]['items'].append(
                {
                    "title": '{} Tank'.format(tank.attributes.get('name', "Water Tank")),
                    section_key: [
                        {
                            "title": 'TANK',
                            list_key: [
                                {
                                    "key": "Manufacturer",
                                    "value": tank.meta.get('manufacturer'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    "key": "Product Model",
                                    "value": tank.meta.get('model'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",

                                },
                                {
                                    "key": "Part#",
                                    "value": tank.meta.get('part'),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    'key': 'Capacity',
                                    'value': '{} Gallons'.format(tank.attributes.get('cap', 'NA')),
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                }
                            ]
                        },
                        # TODO: Figure out how to not hard code the sensor data
                        # Currently those are not part of the templates
                        {
                            'title': 'SENSOR',
                            list_key: [
                                {
                                    "key": "Manufacturer",
                                    "value": "KIB",
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    "key": "Product Model",
                                    "value": "PSI-G-3PSI",
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                },
                                {
                                    "key": "Part#",
                                    "value": "N/A",
                                    "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                }
                            ]
                        }
                    ]
                }
            )

    settings = {
        'title': 'Water Systems Settings',
        'configuration': config,
        'logos': {},
        'information': information,
        'notification': []
    }
    return settings


def get_watersystems_features_settings(app, list_key='items', section_key='sections'):
    '''Pass in handle to app and build ui strucutre for settings.'''
    # NOTE: This has a slightly different format compared to the settings in the feature itself
    watersystems = app.config.get('watersystems')
    volume_preference = watersystems.get('VolumeUnitPreference')
    temp_preference = app.config.get('climate', {}).get('TempUnitPreference')

    water_heaters = []
    if hasattr(app.hal.watersystems.handler, 'water_heater'):
        for heat_id, heater in app.hal.watersystems.handler.water_heater.items():
            print('Heater State', heater.state, heater.attributes)
            # If it allows to set a temp it requires a setting here
            if hasattr(heater.state, 'setTemp'):
                set_temp = heater.state.setTemp
                if set_temp is None:
                    set_temp = '--'

                water_heaters.append(
                    {
                        'title': 'Water Heater',
                        list_key: [
                            {
                                'title': 'Water Heater Temperature',
                                'widget': 'TEMPERATURE_SETTING',
                                'selected_text': f'{set_temp} °{temp_preference}',
                                'options': [],
                                'state': {
                                    'setTemp': heater.state.setTemp
                                },
                                'actions': {
                                    'TAP': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'{BASE_URL}/api/watersystems/wh/{heat_id}/state',
                                            'type': 'PUT',
                                            'params': {
                                                '$setTemp': 'int',
                                                'unit': temp_preference
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                'title': 'Restore Default',
                                'widget': 'SIMPLE_BUTTON',
                                'actions': {
                                    'PRESS': {
                                        'type': 'api_call',
                                        'action': {
                                            'href': f'{BASE_URL}/api/watersystems/wh/{heat_id}/settings/restoredefault',
                                            'type': 'PUT',
                                            # 'params': {}
                                        }
                                    }
                                }
                            }
                        ]
                    }
                )

    config = []
    config.extend(water_heaters)

    information = [
        {
            'title': 'MANUFACTURER INFORMATION',
            'items': []
        }
    ]
    # Heaters
    if hasattr(app.hal.watersystems.handler, 'water_heater'):
        for _, heater in app.hal.watersystems.handler.water_heater.items():
            heater_data = {
                "title": heater.attributes.get('name', "Water Heater"),
                section_key: [
                    {
                        "title": heater.attributes.get('name', "Water Heater"),
                        list_key: [
                            {
                                "type": "SETTINGS_SECTIONS_LIST",
                                "title": "MANUFACTURER INFORMATION",
                                list_key: [
                                    {
                                        "title": "Manufacturer",
                                        "value": heater.meta.get('manufacturer'),
                                        "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                    },
                                    {
                                        "title": "Product Model",
                                        "value": heater.meta.get('model'),
                                        "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                    },
                                    {
                                        "title": "Part#",
                                        "value": heater.meta.get('part'),
                                        "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            # If logo is present we do add this of a new settings type
            if heater.meta.get('logo') is not None:
                heater_data[section_key][0][list_key][0][list_key].append(
                    {
                        "key": "Logo",
                        "value": heater.meta.get('logo'),
                        "type": "LOGO",
                    }
                )
            information[0]['items'].append(heater_data)
    # Pumps
    if hasattr(app.hal.watersystems.handler, 'water_pump'):
        for _, pump in app.hal.watersystems.handler.water_pump.items():
            information[0]['items'].append(
                {
                    "title": pump.attributes.get('name', "Water Pump"),
                    section_key: [
                        {
                            "title": pump.attributes.get('name', "Water Pump"),
                            list_key: [
                                {
                                    "type": "SETTINGS_SECTIONS_LIST",
                                    "title": "MANUFACTURER INFORMATION",
                                    list_key: [
                                        {
                                            "title": "Manufacturer",
                                            "value": pump.meta.get('manufacturer'),
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        },
                                        {
                                            "title": "Product Model",
                                            "value": pump.meta.get('model'),
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        },
                                        {
                                            "title": "Part#",
                                            "value": pump.meta.get('part'),
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            )
    # Tanks
    if hasattr(app.hal.watersystems.handler, 'water_tank'):
        for _, tank in app.hal.watersystems.handler.water_tank.items():
            information[0]['items'].append(
                {
                    "title": '{} Tank'.format(tank.attributes.get('name', "Water Tank")),
                    section_key: [
                        {
                            "title": '{} Tank'.format(tank.attributes.get('name', "Water Tank")),
                            list_key: [
                                {
                                    "type": "SETTINGS_SECTIONS_LIST",
                                    "title": "TANK",
                                    list_key: [
                                        {
                                            "title": "Manufacturer",
                                            "value": tank.meta.get('manufacturer'),
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        },
                                        {
                                            "title": "Product Model",
                                            "value": tank.meta.get('model'),
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",

                                        },
                                        {
                                            "title": "Part#",
                                            "value": tank.meta.get('part'),
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        },
                                        {
                                            'title': 'Capacity',
                                            'value': '{} Gallons'.format(tank.attributes.get('cap', 'NA')),
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        }
                                    ]
                                },
                                {
                                    "type": "SETTINGS_SECTIONS_LIST",
                                    "title": "SENSOR",
                                    list_key: [
                                        {
                                            "title": "Manufacturer",
                                            "value": "KIB",
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        },
                                        {
                                            "title": "Product Model",
                                            "value": "PSI-G-3PSI",
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        },
                                        {
                                            "title": "Part#",
                                            "value": "N/A",
                                            "type": "SETTINGS_SECTIONS_LIST_ITEM",
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            )

    settings = {
        'title': 'Water Systems Settings',
        'configuration': config,
        'logos': {},
        'information': information,
        'notification': []
    }
    return settings['information'][0]['items']
