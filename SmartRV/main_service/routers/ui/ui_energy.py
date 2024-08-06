import datetime
import json
import os
import logging
from typing import Optional, List
from urllib import response


from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel

from common_libs.models.common import EventValues

from .helper import get_tank_level_text

from main_service.modules.logger import prefix_log

wgo_logger = logging.getLogger('uvicorn.error')

# TODO: Figure out which one to use
BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/ems',
    tags=['EMS', 'ENERGY MANAGEMENT']
)


@router.get('/', response_model_exclude_none=True)
async def gui_ems(request: Request):
    # # TODO: Get inputs
    power_inputs = request.app.hal.energy.handler.get_power_inputs()
    # # TODO: Get Batteries
    BATTERY_INSTANCE = 1
    bms = request.app.hal.energy.handler.battery_management[BATTERY_INSTANCE]
    # batteries = request.app.hal.energy.handler.get_batteries()
    # # TODO: Get Consumers
    # consumers = request.app.hal.energy.get_power_consumers()

    # Get Energy Sources
    energy_sources = request.app.hal.energy.handler.energy_source
    source_combined_watts = 0
    # TODO: Get from type attribute
    solar_power = energy_sources[1]
    shore_power = energy_sources[2]
    vehicle_power = energy_sources[3]

    # TODO: Bring back Pro-Power support
    vehicle_input = power_inputs.get('vehicle', {})
    vehicle_input_type = vehicle_input.get('type')

    # ems_propower_source_onOff = request.app.hal.energy.handler.state.get('pro_power__1__enabled', 0)
    # ems_propower_source_active = 0

    veh_action = None
    veh_actions = None

    vehicle_widget = None
    if hasattr(request.app.hal.energy.handler, 'energy_source'):
        for es_id, source in request.app.hal.energy.handler.energy_source.items():
            print('Source', es_id, source)
            if source.componentId == 'energy.es_vehicle':
                if source.attributes.get('type') == 'PROPOWER':
                    print('Found PRO POWER')
                    # Add control
                    veh_action = {
                        'type': 'api_call',
                        'action': {
                            # TODO: Abstract in HAL away from UI and also run required algorithms
                            # Adding a number to allow for multiple ac inputs
                            'href': f'{BASE_URL}/api/electrical/dc/13',
                            'type': 'PUT'
                        }
                    }
                    veh_actions = ['action_default',]

                vehicle_widget = {
                    'name': 'EmsProPowerWidget',
                    'title': vehicle_power.attributes.get('name', 'N/A').upper(),
                    'subtext': '--',    # TODO: Add data
                    'subtext_unit': 'W',
                    'type': 'Simple',
                    # New style using state for the specific type
                    'state': {
                        'onOff': vehicle_power.state.onOff
                    },
                    'actions': veh_actions,
                    'action_default': veh_action,
                    # Shows the bolt state
                    'active': vehicle_power.state.active
                }
                break

    generators = []
    # generator_running = False
    if hasattr(request.app.hal.energy.handler, 'generator'):
        generator_power = energy_sources[4]
        for gen_id, generator in request.app.hal.energy.handler.generator.items():
            # TODO: hook up to real sensor
            generator.check_lockouts()
            generator_button = 'Start'
            param_mode = EventValues.RUN

            if generator.state.mode == EventValues.STARTING or generator.state.mode == EventValues.RUN:
                generator_button = 'Stop'
                param_mode = EventValues.OFF

            enabled = True
            if generator.state.lockouts:
                enabled = False

            # TODO: Get wattage of generator from power source that is linked via relatedComponent
            # Also update wattage from sensor that is not tested yet

            # Get the generator power wattage
            if generator.state.mode == EventValues.RUN:
                # generator_running = True

                gen_wattage = '--'
                if generator_power.state.watts is not None:
                    gen_wattage = round(generator_power.state.watts, 0)
                    source_combined_watts += gen_wattage
            else:
                # generator_running = False
                gen_wattage = '--'

            generator_widget = {
                'name': 'EmsGeneratorWidget',
                'title': generator.attributes.get('name', 'GENERATOR').upper(),
                'subtext': gen_wattage,    # TODO: Add data
                'subtext_unit': 'W',
                'type': 'Simple',
                # New style using state for the specific type
                'state': {
                    'onOff': generator_power.state.active
                },
                'actions': ['action_default', ],
                'action_default': {
                    'type': 'navigate',
                    'action': {
                        'href': '/home/generator'
                    }
                },
                'switches': [
                    {
                        'title': generator_button,
                        'type': 'DEADMAN',
                        'intervalMs': None,      # DOM to confirm
                        'holdDelayMs': 1000,    # DOM to confirm
                        'enabled': enabled,   # Dom to review if this can be moved to lockouts in state
                        'option_param': 'mode',
                        'actions': {
                            'PRESS': None,
                            'HOLD': {
                                'type': 'api_call',
                                'action': {
                                    'href': f'{BASE_URL}/api/energy/ge/{gen_id}/state',
                                    'type': 'PUT',
                                    'param': {
                                        '$mode': param_mode,
                                    }
                                }
                            },
                            'RELEASE': None,
                        }
                    },
                ],
                # Shows the bolt state
                'active': generator_power.state.active
            }
            generators.append(generator_widget)

    # TODO: Get list of inverters and iterate
    print('INVERTERS', request.app.hal.energy.handler.inverter)
    inverter_widgets = []
    for instance, inverter in request.app.hal.energy.handler.inverter.items():
        inverter_state = inverter.state

        # Inverter AC Current Reading
        inverter_wattage = inverter_state.load
        if inverter_wattage is None:
            inverter_wattage = '--'

        inverter_state = inverter.state.dict()
        # Inject max load from attributes - during initization - this is a default value
        # inverter_state['maxLoad'] = inverter.attributes.get('defaultMaxLoad', 0)

        inverter_widget = {
            'name': 'EmsInverterWidget',
            'title': inverter.attributes.get('name', 'INVERTER').upper(),
            'subtext': '',
            # 'subtext_unit': 'W',
            'type': 'InverterEMSWidget',
            # New style using state for the specific type
            'state': inverter_state,
            'actions': [
                'action_default',
            ],
            'action_default': {
                'type': 'api_call',
                'action': {
                    "href": f"/api/energy/ei/{instance}/state",
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            },
            # Shows the bolt state
            'active': inverter.state.onOff,
            'inverterLoadText': '{load}W',
            'inverterCapacityText': 'of {maxLoad}W'
        }
        inverter_widgets.append(inverter_widget)

    # Batteries
    # Get SoC
    # Get net power
    # Get time till
    # Create subtext

    # Consumers
    # List by usage

    # list of columns (Source, Battery, Usage)

    solar_watts = solar_power.state.watts
    if solar_watts is None:
        solar_watts = 0
        ems_solar_subtext = '--'    # We do not know as it is None
    else:
        solar_watts = round(solar_watts, 0)
        ems_solar_subtext = solar_watts

    prefix_log(wgo_logger, __name__, solar_watts)

    if solar_watts > 0:
        ems_solar_source_active = 1
    else:
        ems_solar_source_active = 0

    source_combined_watts += solar_watts

    shore_power_watts = 0
    if shore_power.state.watts is None:
        ems_shore_power_subtext = '--'
    else:
        ems_shore_power_subtext = round(shore_power.state.watts, 0)
        shore_power_watts = shore_power.state.watts

    source_combined_watts += shore_power_watts

    ems_battery_level = bms.state.soc
    if ems_battery_level is None:
        ems_battery_level = 0
    else:
        ems_battery_level = round(ems_battery_level, 0)

    print(bms.state)
    ems_time_remaining = request.app.hal.energy.handler.get_remaining_runtime(BATTERY_INSTANCE)

    if ems_time_remaining is None:
        ems_time_remaining = None
        ems_time_remaining_hi = '-- '
        ems_time_remaining_lo = '-- '
        ems_days_text = 'h'
        ems_hours_text = 'm'
        ems_is_charging = None
    else:
        ems_time_remaining_days = ems_time_remaining.get('days')
        ems_time_remaining_hours = ems_time_remaining.get('hours')
        ems_time_remaining_minutes = ems_time_remaining.get('minutes')

        ems_days_text = 'd'
        ems_hours_text = 'h'

        if ems_time_remaining_days < 1:
            ems_days_text = 'h'
            ems_hours_text = 'm'
            ems_time_remaining_hi = ems_time_remaining_hours
            ems_time_remaining_lo = ems_time_remaining_minutes
        else:
            ems_time_remaining_hi = ems_time_remaining_days
            ems_time_remaining_lo = ems_time_remaining_hours

        if bms.state.tte == EventValues.TIME_TO_FULL:
            ems_is_charging = True
        elif bms.state.tte == EventValues.TIME_TO_EMPTY:
            ems_is_charging = False
        else:
            ems_is_charging = None

    if ems_is_charging is None:
        ems_battery_charging_state_text = '--'
        ems_battery_charging_time_text = '--'
    elif ems_is_charging is True:
        ems_battery_charging_state_text = 'Charging'
        ems_battery_charging_time_text = 'till full'
    else:
        ems_battery_charging_state_text = 'Discharging'
        ems_battery_charging_time_text = 'till empty'

    ems_battery_low = True if ems_battery_level <= 10 else False
    ems_battery_warning = True if (
        ems_battery_level > 10 and ems_battery_level < 25) else False

    # Get from HW layer
    # Check each load circuit on the CZone
    # Check each AC load
        # Water heater
        # Heater
    # TODO: Make UI agnostic to HW by reading the config with mappings
    # inverter id is set as 1 here, but should be read from template for this model
    current_ac_load = request.app.hal.energy.handler.get_inverter_load(1)
    print('Inverter Load', current_ac_load)
    ac_load_text = '--' if current_ac_load == 0 or current_ac_load is None else current_ac_load / 1000

    energy_consumers = request.app.hal.energy.handler.get_active_consumers()

    active_systems = [x for x in energy_consumers if x.state.active is True]
    active_system_count = len(active_systems)

    ems_usage_systems_text = f'{active_system_count} System(s) Active'
    # TODO: Read real values
    ems_usage_level = 0
    ems_charge_level = 0

    total_energy_input = request.app.hal.energy.handler.get_total_input()['kilowatts']
    if total_energy_input > 0.02:
        total_input_text = f'Total {total_energy_input} kW'
    elif request.app.hal.energy.handler.is_power_incoming() is True:
        total_input_text = 'Power On'
    else:
        total_input_text = 'Not Charging'

    # Get Inverter load, maybe add % overhead
    # Get DC circuits from CZone (if wattage not known show them based on their assumed load if on)

    consumer_watts = 0
    current_energy_consumer = []
    if hasattr(request.app.hal.energy.handler, 'energy_consumer'):
        for ec_instance, consumer in request.app.hal.energy.handler.energy_consumer.items():
            if consumer.state.active:
                current_energy_consumer.append(
                    {
                        'name': f'EmsUsageConsumer{ec_instance}',
                        'title': consumer.attributes.get('name'),
                        'type': consumer.attributes.get('type'),
                        'subtext': f'{consumer.state.watts} W'
                    }
                )
                # NOTE: Watts should not be None if it is passing the active check above
                consumer_watts += consumer.state.watts

    # TODO: Sum up all defined input sorces
    sources = [
        {
            # Internal name for QA and matching with UI styles etc.
            'name': 'EmsSolarWidget',
            'title': 'SOLAR',
            'subtext': ems_solar_subtext,
            'subtext_unit': 'W',

            'type': 'Info',
            'state': {
                'onOff': ems_solar_source_active
            },

            'actions': None,
            # Shows the bolt state
            'active': ems_solar_source_active,
            'details': {
                'title': 'Solar',
                'tiles': [
                    {
                        'title': 'Yield',
                        'value': '00',
                        'subtext': 'Watts'
                    },
                    {
                        'title': 'Power Max',
                        'value': '00',
                        'subtext': 'Amps'
                    },
                    {
                        'title': 'BMS Voltage Max',
                        'value': '00',
                        'subtext': 'Volts'
                    },
                    {
                        'title': 'Battery Max',
                        'value': '00',
                        'subtext': 'Volts'
                    },
                    {
                        'title': 'Battery Min',
                        'value': '00',
                        'subtext': 'Volts'
                    }
                ]
            }
        },
        {
            'name': 'EmsShoreWidget',
            'title': 'SHORE',
            'subtext': ems_shore_power_subtext,
            'subtext_unit': 'W',

            'type': 'Info',
            'state': {
                'onOff': shore_power.state.active
            },

            'actions': None,
            # Shows the bolt state
            'active': shore_power.state.active
        },
        # inverter_widget
    ]
    if vehicle_widget:
        sources.append(vehicle_widget)

    sources.extend(generators)

    response = {
        'title': 'Energy Management',
        'items': [
            # 1 - Source
            {
                'title': 'Source',
                'name': 'EnergySourceColumn',
                'subtext': '{watts}W',
                # '{watts}W'
                'actions': ['action_default', ],
                'action_default': {
                    'type': 'navigate',
                    'action': {
                        'href': '/home/ems/sources'
                    }
                },
                'state': {
                    'watts': source_combined_watts
                },
                # active would help identify if energy is flowing on the input side
                # 0 -> off
                # 1 -> on
                'active': source_combined_watts > 0,
                'widgets': sources
            },
            # 2 - Battery
            {
                'title': 'Battery',
                'name': 'EnergyBatteryColumn',
                'subtext': '{soc} Charge Left',
                'actions': ['action_default', ],
                'action_default': {
                    'type': 'navigate',
                    'action': {
                        'href': '/home/ems/battery'
                    }
                },
                'state': {
                    'soc': f'{ems_battery_level}%'
                },
                # active would help identify if energy is flowing
                # 0 -> off
                # 1 -> on
                # TODO: Read from system if power actually is drawn
                'active': 1,
                'widgets': [
                    {
                        'name': 'EmsBatteryMainWidget',
                        'title': None,
                        'type': 'BatteryMain',
                        'BatteryMain': {
                            'value': ems_battery_level,
                            'value_unit': '%',

                            # TODO: Need to review this !
                            'battery_low': ems_battery_low,
                            'battery_warning': ems_battery_warning,

                            'remaining_high': ems_time_remaining_hi,
                            'remaining_low': ems_time_remaining_lo,
                            'remaining_title': 'Remaining',

                            'text_high': ems_days_text,
                            'text_low': ems_hours_text,
                            'subtext': ems_battery_charging_time_text,
                            'toptext': ems_battery_charging_state_text
                        },
                        # New style
                        'state': {
                            'value': ems_battery_level,
                            'value_unit': '%',

                            # TODO: Need to review this !
                            'battery_low': ems_battery_low,
                            'battery_warning': ems_battery_warning,

                            'remaining_high': ems_time_remaining_hi,
                            'remaining_low': ems_time_remaining_lo,
                            'text_high': ems_days_text,
                            'text_low': ems_hours_text,
                            'remaining_title': 'Remaining',

                            'subtext': ems_battery_charging_time_text,
                            'toptext': ems_battery_charging_state_text
                        },
                    },
                    # TODO: Fix and create clean assembly of the individual widget groups
                    inverter_widgets[0]
                ],
                'details': {
                    'title': 'Battery',
                    'tiles': [
                        {
                            'title': 'Voltage',
                            'value': bms.state.vltg,
                            'subtext': 'Volts'
                        },
                        {
                            'title': 'Current',
                            'value': bms.state.dcCur,
                            'subtext': 'Amps'
                        },
                        {
                            'title': 'Battery Temp',
                            'value': '00',
                            'subtext': 'Celsius'     # TODO: Get system unit here
                        },
                        {
                            'title': 'Power',
                            'value': '00',
                            'subtext': 'Watts'
                        },
                        {
                            'title': 'Capacity',
                            'value': '00',
                            'subtext': 'Amp hours'
                        },
                        {
                            'title': 'BMS Temp',
                            'value': bms.state.temp,
                            'subtext': 'Celsius'     # TODO: Get system unit here
                        }
                    ]
                }
            },
            # 3 - Usage
            {
                'title': 'Usage',
                'name': 'EnergyUsageColumn',
                'subtext': '~ {watts}W',
                'actions': ['action_default', ],
                'action_default': {
                    'type': 'navigate',
                    'action': {
                        'href': '/home/ems/usage'
                    }
                },
                'state': {
                    'watts': consumer_watts
                },
                # active would help identify if energy is flowing
                # 0 -> off
                # 1 -> on
                'active': None,
                'widgets': [
                    {
                        'name': 'EmsUsageWidget',
                        'title': 'USAGE',
                        'type': 'UsageMain',
                        'UsageMain': {
                            'usage_level': ems_usage_level,
                            'usage_unit': 'kW',
                            'charge_level': ems_charge_level,
                            'charge_unit': 'kW',
                            # Remove charge line if not active (0)
                            'active': 0
                        }
                    },
                    {
                        'name': 'EmsConsumerWidget',
                        'title': None,
                        'type': 'Consumers',
                        'Consumers': current_energy_consumer
                    }
                ]
            },
        ]
    }

    return response


@router.get('/settings')
async def get_settings(request:Request) -> dict:
    # Get settings from the right place of HW, SW and State for element water systems
    # Probably central place
    WP_INSTANCE = 1
    WH_INSTANCE = 1
    WT_INSTANCE = 1

    wp_meta = request.app.hal.watersystems.handler.water_pump[WP_INSTANCE].meta
    wh_meta = request.app.hal.watersystems.handler.water_heater[WH_INSTANCE].meta
    wt_meta = request.app.hal.watersystems.handler.water_tank[WT_INSTANCE].meta


    settings = {
        'title': 'Water Systems Settings',
        'configuration': [
            {
                'title': None,
                'items': [
                    {
                        'title': 'Unit Preference',
                        'selected_text': 'Gallons',
                        'options': [
                            {
                                'key': 'Gallons (gal.)',
                                'value': 0,
                                'selected': True
                            },
                            {
                                'key': 'Liters (L)',
                                'value': 1,
                                'selected': False
                            },
                        ],
                        'actions': ['action_default',],
                        'action_default': {
                            'type': 'api_call',
                            'action': {
                                'href': f'{BASE_URL}/api/watersystems/settings',
                                'type': 'PUT',
                                'params': {
                                    '$value': 'int',
                                    'item': 'VolumeUnitPreference'
                                }
                            }
                        }
                    }
                ]
            }
        ],
        'information': [
            {
                'title': 'MANUFACTURER INFORMATION',
                'items': [
                    {
                        'title': 'Water Pump',
                        'sections': [
                            {
                                'title': None,
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': wp_meta.get("manufacturer")
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': wp_meta.get("model")
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': wp_meta.get("part")
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Water Heater',
                        'sections': [
                            {
                                'title': None,
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': wh_meta.get("manufacturer")
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': wh_meta.get("model")
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': wh_meta.get("part")
                                    }
                                ]
                            }
                        ]
                    },
                    #fresh tank and gray tank black tank etc manufacturer the same?
                    {
                        'title': 'Fresh Tank',
                        'sections': [
                            {
                                'title': 'TANK',
                                'items': [
                                     {
                                        'key': 'Manufacturer',
                                        'value': wt_meta.get("manufacturer")
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': wt_meta.get("model")
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': wt_meta.get("part")
                                    }
                                ]
                            },
                            {
                                'title': 'SENSOR',
                                'items': [
                                     {
                                        'key': 'Manufacturer',
                                        'value': 'KIB'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'PSI-G-3PSI'
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': 'N/A'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Gray Tank',
                        'sections': [
                            {
                                'title': 'TANK',
                                'items': [
                                    {
                                        'key': 'Manufacturer',
                                        'value': 'Some OEM'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'Some Model'
                                    },
                                    {
                                        'key': 'Tank Volume',
                                        # Convert this to the selected unit before reporting out
                                        'value': '21 gal.'
                                    }
                                ]
                            },
                            {
                                'title': 'SENSOR',
                                'items': [
                                     {
                                        'key': 'Manufacturer',
                                        'value': 'KIB'
                                    },
                                    {
                                        'key': 'Product Model',
                                        'value': 'PSI-G-3PSI'
                                    },
                                    {
                                        'key': 'Part#',
                                        'value': 'N/A'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
        'notification': []
    }
    return settings
