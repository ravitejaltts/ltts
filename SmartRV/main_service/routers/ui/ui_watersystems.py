import os
from typing import List

from copy import deepcopy

from fastapi import APIRouter, Request

from pydantic import BaseModel

from main_service.modules.constants import (
    GALLONS_2_LITER,
    WATER_UNIT_GALLONS,
    WATER_UNIT_LITER,
    WATER_UNITS,
    _celcius_2_fahrenheit,
    fahrenheit_2_celcius
)
from common_libs.models.common import EventValues

from .helper import get_tank_level_text
from .helper import get_pump_text
from .helper import get_heater_text
from .helper import create_ui_lockout
from .helper import get_heating_pad_text
from .helper import get_watersystems_settings


class WaterPump(BaseModel):
    name: str
    title: str
    subtext: str
    type: str
    state: dict
    widget: str = 'SIMPLE_TOGGLE'
    actions: List[str]
    action_default: dict


BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/watersystems',
    tags=['WATER SYSTEMS',]
)


@router.get('/', response_model_exclude_none=True)
async def gui_water(request: Request):
    current_water_unit = request.app.config['watersystems'].get(
        'VolumeUnitPreference',
        WATER_UNIT_GALLONS
    )

    temp_preference = request.app.config.get('climate', {}).get('TempUnitPreference')

    switches = []

    heating_pad_features_present = False
    heating_pad_ids = []

    # hidden_ids = []
    for heat_id, heater in request.app.hal.watersystems.handler.water_heater.items():
        print('HEATER TYPE', heater.attributes.get('type'))
        print(heater.attributes)
        print(heater.componentId)
        print(heater.type)

        if 'tankpad' in heater.componentId:
            heating_pad_features_present = True
            heating_pad_ids.append(heat_id)
            # Skip adding this individually
            continue

        lockouts_ui = []
        # Check this from the Lockoutcomponent
        heater.check_lockouts()
        for lock_out in heater.state.lockouts:
            lock = request.app.hal.system.handler.lockouts[lock_out]

            # Lockout needs to be added
            lockouts_ui.append(
                create_ui_lockout(
                    heater,
                    lock,
                    lock_out
                )
            )
        enabled = True
        if heater.state.lockouts:
            enabled = False

        ui_heater = {
            'name': 'WaterHeaterToggle',
            'title': heater.attributes.get('name', 'Water Heater'),
            'subtext': get_heater_text(heater.state, unit=temp_preference),
            'type': 'SIMPLE_WATER_HEATER',
            'widget': 'TOGGLE_WITH_EXTRAS_AND_INFO',
            'state': heater.state,
            'lockouts': lockouts_ui,
            'enabled': enabled,
            'actions': {
                'TAP': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/watersystems/wh/{heat_id}/state',
                        'type': 'PUT',
                        'params': {
                            '$onOff': 'int',
                            '$mode': 'int'
                        }
                    }
                }
            },
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/watersystems/wh/{heat_id}/state',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$mode': 'int'
                    }
                }
            }
        }

        if heater.type == 'rvc':
            # Get propane tank status
            propane_state = None
            if hasattr(request.app.hal.energy.handler, 'fuel_tank'):
                for tank_id, tank in request.app.hal.energy.handler.fuel_tank.items():
                    if tank.attributes.get('type') == 'LP':
                        propane_state = tank.state
                        break

            if propane_state is not None:
                if propane_state.lvl is None:
                    lvl = '--'
                else:
                    lvl = propane_state.lvl

                ui_heater['subtext'] += f' · Propane Tank {lvl}%'

            # TODO: Get the data from the component as initialized (componentGroup might need to define)
            ECO_TEMP = 41
            COMFORT_TEMP = 102

            if temp_preference == 'C':
                ECO_TEMP = fahrenheit_2_celcius(ECO_TEMP)
                COMFORT_TEMP = fahrenheit_2_celcius(COMFORT_TEMP)

            # Advanced heater with suboptions
            options = [
                {
                    'key': 'Comfort',
                    'value': EventValues.COMFORT,
                    'selected': heater.state.mode == EventValues.COMFORT
                },
                {
                    'key': 'Eco',
                    'value': EventValues.ECO,
                    'selected': heater.state.mode == EventValues.ECO
                }
            ]
            ui_heater['extras'] = {
                'mode': {
                    "text": "Mode",
                    # "subtext": f"Select a setting for your fan",
                    # "footerText": 'Fan will run only when the thermostat is heating or cooling',
                    "options": options,
                    'information': {
                        'title': 'Water Heater Modes',
                        'items': [
                            {
                                'title': '{Eco Mode} saves energy and prevents freezing.',
                                'items': [
                                    f'The temperature in the appliance is automatically kept above {ECO_TEMP}° {temp_preference}',
                                ]
                            },
                            {
                                'title': '{Comfort Mode} maintains stand-by heat for rapid availability of hot water.',
                                'items': [
                                    f'The temperature in the appliance is automatically kept above {COMFORT_TEMP}° {temp_preference}',
                                ]
                            }
                        ]
                    }
                }
            }

        switches.append(
            ui_heater
        )

    # Pumps
    pump_list = []
    for instance, pump in request.app.hal.watersystems.handler.water_pump.items():
        uiclass = '{}WaterPumpToggle'.format(
            pump.attributes.get('type', 'FRESH').capitalize()
        )

        pump_name = pump.attributes.get('name', 'NA')

        pump_state = pump.state.onOff

        p_feature = WaterPump(
            name=uiclass,
            title=pump_name,
            subtext=get_pump_text(pump_state),
            type='SIMPLE_PUMP',
            state={
                'onOff': pump_state
            },
            actions=['action_default',],
            action_default={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/watersystems/wp/{instance}/state',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            }
        )
        pump_list.append(p_feature)

    switches.extend(pump_list)

    # Finalize with heating pads
    if heating_pad_features_present is True:
        heater = request.app.hal.watersystems.handler.water_heater[heating_pad_ids[0]]
        print('Heating Pad 1', heater)
        triggerTemp = 41    # Get from config and then convert to user setting first
        if temp_preference == 'C':
            triggerTemp = fahrenheit_2_celcius(triggerTemp)

        if heater.state.onOff == EventValues.ON:
            subtext = f'Enabled: Pads will heat up when it is below {triggerTemp}°{temp_preference} outside'
        else:
            subtext = 'Disabled'

        pad_feature = {
            'name': 'TankPadToggle',
            'title': 'Tank Heating Pads',
            'subtext': subtext,
            'type': heater.type.upper(),
            'widget': 'SIMPLE_TOGGLE',
            'state': {
                'onOff': heater.state.onOff
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/watersystems/wh/{heater.instance}/state',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            }
        }
        switches.append(pad_feature)

    # Check if we have a toilet circuit
    if hasattr(request.app.hal.watersystems.handler, 'toilet_circuit'):
        # Add Toilet circuits
        for instance, toilet in request.app.hal.watersystems.handler.toilet_circuit.items():
            toilet_switch = {
                'name': 'ToiletOverride',
                'title': 'Toilet Shutoff',
                'subtext': 'TBD',
                'type': 'TBD',
                'widget': 'SIMPLE_TOGGLE',
                'state': {
                    'onOff': toilet.state.onOff
                },
                'actions': ['action_default',],
                'action_default': {
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/watersystems/tc/{instance}/state',
                        'type': 'PUT',
                        'params': {
                            '$onOff': 'int'
                        }
                    }
                }
            }
            switches.append(toilet_switch)

    # else:
    #     # Testing only on 524T floorplan
    #     toilet_circuit = {
    #         'name': 'ToiletToggle',
    #         'title': 'Macerator Toilet',
    #         'subtext': 'Auto: Toilet will turn off when black tank level reaches 95%',
    #         'type': 'SIMPLE_WATER_HEATER',
    #         'widget': 'TOGGLE_WITH_EXTRAS_AND_INFO',
    #         'state': {'onOff': 1},
    #         'lockouts': lockouts_ui,
    #         'enabled': True,
    #         'actions': {
    #             'TAP': {
    #                 'type': 'api_call',
    #                 'action': {
    #                     'href': f'{BASE_URL}/api/watersystems/tc/1/state',
    #                     'type': 'PUT',
    #                     'params': {
    #                         '$onOff': 'int',
    #                         '$mode': 'int'
    #                     }
    #                 }
    #             }
    #         },
    #         'action_default': {
    #             'type': 'api_call',
    #             'action': {
    #                 'href': f'{BASE_URL}/api/watersystems/tc/1/state',
    #                 'type': 'PUT',
    #                 'params': {
    #                     '$onOff': 'int',
    #                     '$mode': 'int'
    #                 }
    #             }
    #         }
    #     }
    #     options = [
    #         {
    #             'key': 'On',
    #             'value': EventValues.ON,
    #             'selected': False
    #         },
    #         {
    #             'key': 'Auto',
    #             'value': EventValues.AUTO,
    #             'selected': True
    #         }
    #     ]
    #     toilet_circuit['extras'] = {
    #         'mode': {
    #             "text": "Mode",
    #             # "subtext": f"Select a setting for your fan",
    #             # "footerText": 'Fan will run only when the thermostat is heating or cooling',
    #             "options": options,
    #             'information': {
    #                 'title': 'Toilet Mode',
    #                 'items': [
    #                     {
    #                         'title': 'Auto mode will turn off and on the toilet power based on tank levels.',
    #                         'items': [
    #                             f'The temperature in the appliance is automatically kept above {ECO_TEMP}° {temp_preference}',
    #                         ]
    #                     },
    #                     {
    #                         'title': 'On will keep the toilet enabled even if black tank is full.',
    #                         'items': [
    #                             f'The temperature in the appliance is automatically kept above {COMFORT_TEMP}° {temp_preference}',
    #                         ]
    #                     }
    #                 ]
    #             }
    #         }
    #     }

    #     switches.append(
    #         toilet_circuit
    #     )

    levels = []
    tanks = request.app.hal.watersystems.handler.get_tanks()
    for instance, tank in tanks.items():
        tank_state = request.app.hal.watersystems.tank_readout(
            tank,
            current_water_unit
        )
        fill = tank_state.get('fill')
        tank_fill_str = '--' if fill is None else f"{fill:.1f}"
        if tank_state.get('level_raw') == -1:
            tank_subtext = f"NA {tank_state.get('unit')}"
        else:
            tank_subtext = f"{tank_fill_str} {tank_state.get('unit')}"

        uiclass = '{}TankLevel'.format(
            tank.attributes.get('type', 'NA').capitalize()
        )

        tank_name = tank.attributes.get('name')

        levels.append(
            {
                "title": tank_name,
                "subtext": tank_subtext,
                "name": uiclass,
                "type": "simpleLevel",  # TODO: Remove after confirming widget being used instead
                'widget': 'SIMPLE_LEVEL',
                "simpleLevel": {
                    "max": 100,
                    "min": 0,
                    "current_value": tank_state.get('level_raw', 0.0),
                    "unit": "%",
                    "level_text": get_tank_level_text(tank)
                },
                'state': {
                    "max": 100,
                    "min": 0,
                    "current_value": tank_state.get('level_raw', 0.0),
                    "unit": "%",
                    "level_text": get_tank_level_text(tank)
                }
            }
        )

    response = {
        'overview': {
            'title': 'Water Systems',
            'name': 'WaterSystemsOverview',
            'settings': {
                'href': f'{BASE_URL}/ui/watersystems/settings',
                'type': 'GET'
            }
        },
        'switches': switches,
        'levels': levels,
    }

    return response


@router.get('/settings')
async def get_settings(request: Request) -> dict:
    # Get settings from the right place of HW, SW and State for element water systems
    # Probably central place
    return get_watersystems_settings(request.app)
