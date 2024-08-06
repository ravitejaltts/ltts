import os
import time

from fastapi import APIRouter, Request

from common_libs.models.common import EventValues
from common_libs.models.gui import (
    ButtonWidget,
    FCPDeadMan,
    FCPLevelWidget,
    InfoLabel,
    OptionWidget,
    SliderWidget,
    ToggleWidget,
)

# from main_service.modules.hardware.hal import hw_layer
from main_service.modules.constants import WATER_UNIT_GALLONS
from main_service.modules.system_helper import (
    get_bt_mac,
    get_bt_status,
    get_free_storage,
    get_iot_status,
    get_ip,
    get_os_release,
)

from .helper import (
    get_onoff_text,
)

BASE_URL = os.environ.get('WGO_MAIN_API_BASE_URL', '')

router = APIRouter(
    prefix='/functionaltests',
    tags=['TESTING', ]
)


def get_diagnostics(app):
    '''Get diagnostics info from the app.'''
    result = []
    if hasattr(app, 'can_diagnostics'):
        diagnostics = app.can_diagnostics
        for dev_name, device in diagnostics.get('devices', {}).items():
            result.append({
                'name': dev_name,
                'stale': device.get('stale'),
                'time': '',
                'category': 'can'
            })
        # Transform here

    if hasattr(app, 'system_diagnostics'):
        system_diag = app.system_diagnostics
        for dev_name, device in system_diag.get('devices', {}).items():
            result.append({
                'name': dev_name,
                'stale': device.get('stale'),
                'time': '',
                'category': 'system'
            })

    return result


@router.get('/', response_model_exclude_none=True)
async def gui_functional(request: Request):
    # Get IOT Status
    get_iot_status(request.app)
    print('iot_status', request.app.iot_status)
    bt_status = await get_bt_status()
    print('BT status', bt_status)
    try:
        bt_mac_address = get_bt_mac()
    except Exception as err:
        print(err)
        bt_mac_address = 'NA'
    # Getting OS Data
    os_data = get_os_release()

    print('calling get_diagnostics')

    diagnostics = get_diagnostics(request.app)

    # Free storage
    storage = get_free_storage()

    current_water_unit = request.app.config['watersystems'].get('VolumeUnitPreference', WATER_UNIT_GALLONS)
    # NOTE: Let the scheduled task update GPS
    # TODO: Add a button that allows to test the retrieval immediately
    # try:
    #     comm_status = request.app.hal.connectivity.handler.get_sys_gps()
    # except IOError as err:
    #     comm_status = 'ERROR'
    # Check which model is needed
    # vehicle_model = request.app.config.get('model')
    # fcp_ui = FCP.get(vehicle_model, 'GENERIC')

    print('hit ui_functionaltests')

    # Get All circuits listed in electrical
    # Get all levels from watersystems
    # Get all levels from energy
    # - AC / DC meters / Shunt etc.
    # Get Lighting Zones
    #

    # Get all CZone circuits
    circuit_states = request.app.hal.electrical.handler.get_state()
    # TODO FINDOUT where/what has circuits RV1?
    czone_mapping = request.app.hal.electrical.handler.czone.cfg.get('mapping', {}).get('dc')
    # print('Circuit states', circuit_states)
    # print('Czone Mapping', czone_mapping)

    circuits = [
        value for (key, value) in czone_mapping.items()
    ]

    switches = []

    # Get list of tanks
    tanks = request.app.hal.watersystems.handler.get_tanks()

    tanks_meta = request.app.hal.watersystems.handler.get_systems(
        system='wt'
    )
    tanks_meta = {
        v['system_key']: v.get('meta', {}) for v in tanks_meta
    }
    # print('Tanks META', tanks_meta)

    for key, tank in tanks.items():
        tank_state = request.app.hal.watersystems.tank_readout(tank, current_water_unit)
        fill = tank_state.get('fill')
        tank_fill_str = '--' if fill is None else f"{fill:.1f}"

        if tank.state.lvl == -1:
            tank_subtext = f"NA {tank_state.get('unit')}"
        else:
            tank_subtext = f"{tank_fill_str} {tank_state.get('unit')}"

        switches.append(
            FCPLevelWidget(
                category='watersystems',
                title=tank.attributes.get('name', "No Name"),
                subtext=tank_subtext,
                state={
                    'level': None if tank_state.get('level_raw') is None else (int(tank_state.get('level_raw')) if tank_state.get('level_raw') != '--' else None)
                },
                min=0.0,
                max=100.0,
                unit=tank_state.get('unit')
            )
        )
        print('[VOLTAGE]', tank.state.vltg)
        switches.append(
            InfoLabel(
                category='watersystems',
                title=tank.attributes.get('name', "No Name") + ' Sensor Voltage',
                text=f'{tank.state.vltg} Volts'
            )
        )
        switches.append(
            ButtonWidget(
                category='watersystems',
                title=tank.attributes.get('name', "No Name") + ' -> Set empty',
                action={
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/watersystems/wt/{tank.instance}/state',
                        'type': 'PUT',
                        'params': {
                            'vltgMin': tank.state.vltg
                        }
                    }
                }
            )
        )
        switches.append(
            ButtonWidget(
                category='watersystems',
                title=tank.attributes.get('name', "No Name") + ' -> Set full',
                action={
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/watersystems/wt/{tank.instance}/state',
                        'type': 'PUT',
                        'params': {
                            'vltgMax': tank.state.vltg
                        }
                    }
                }
            )
        )

    # lock_state = request.app.hal.electrical.handler.get_state(system='chassis',system_id='doorLock').get('onOff', 0)

    # switch = ToggleWidget(
    #     category='vehicle',  # Placeholder until we can read from the circuits
    #     title="Door Lock/Unlock",
    #     state={
    #         'onOff': lock_state
    #     },
    #     action={
    #         'type': 'api_call',
    #         'action': {
    #             'href': f'{BASE_URL}/api/system/doorLock',
    #             'type': 'PUT',
    #             'params': {
    #                 '$onOff': 'int'
    #             }
    #         }
    #     }
    # )
    # switches.append(switch)

    # # LP
    # try:
    #     lp_state = tanks['wt4']
    # except KeyError as err:
    #     print(err)
    #     lp_state = False

    # if lp_state is not False:
    #     lp_tank = request.app.hal.watersystems.tank_readout(lp_state)
    #     #print('!!!!!!', lp_tank)
    #     lp_fill = lp_tank.get('fill')
    #     lp_tank_fill_str = '--' if lp_fill is None else f"{lp_fill:.1f}"

    #     if lp_tank.get('level_raw') == -1:
    #         lp_tank_subtext = f"NA {lp_tank.get('unit')}"
    #     else:
    #         lp_tank_subtext = f"{lp_tank_fill_str} {lp_tank.get('unit')}"

    #     switches.append(
    #         FCPLevelWidget(
    #             category='energy',
    #             title='LPG',
    #             subtext=lp_tank_subtext,
    #             state={
    #                 'level': None if lp_tank.get('level_raw') is None else (int(lp_tank.get('level_raw')) if lp_tank.get('level_raw') != '--' else None)
    #             },
    #             min=0.0,
    #             max=100.0,
    #             unit=lp_tank.get('unit')
    #         )
    #     )

    house_battery = request.app.hal.energy.handler.battery_management[1]
    house_battery_soc = house_battery.state.soc

    switches.append(
        FCPLevelWidget(
            category='energy',
            title='House Battery',
            subtext='SoC',
            state={
                'level': house_battery_soc
            },
            min=0.0,
            max=100.0,
            unit='%'
        )
    )

    if house_battery.state.minsTillEmpty is not None:
        house_runtime_subtext = 'Discharging - Till Empty'
        house_runtime = house_battery.state.minsTillEmpty
    else:
        house_runtime_subtext = 'Charging - Till Full'
        house_runtime = house_battery.state.minsTillFull

    switches.append(
        InfoLabel(
            category='energy',
            title='House Battery - Runtime',
            subtext=house_runtime_subtext,
            text=f'{house_runtime} Minutes'
        )
    )

    house_voltage = house_battery.state.vltg
    house_current = house_battery.state.dcCur
    if house_current is not None and house_voltage is not None:
        house_current = round(house_current, 1)
        house_voltage = round(house_voltage, 1)

    if house_voltage is None or house_current is None:
        net_power = 'NA'
    else:
        house_current = round(house_current, 1)
        house_voltage = round(house_voltage, 1)
        net_power = int(house_voltage * house_current)

    switches.append(
        InfoLabel(
            category='energy',
            title='House Battery - Status',
            subtext=f'{house_voltage} V / {house_current} A',
            text=f'{net_power} Watts'
        )
    )

    # Check if BMS has runtime_meta in attributes
    if 'runtime_meta' in house_battery.attributes:
        for meta, value in house_battery.attributes['runtime_meta'].items():
            switches.append(
                InfoLabel(
                    category='energy',
                    title=f'House Battery - BMS {meta}',
                    # subtext=f'{house_voltage} V / {house_current} A',
                    text=value
                )
            )

    vehicle_battery_voltage = request.app.hal.vehicle.handler.vehicle[1].state.batVltg
    if vehicle_battery_voltage is None:
        vehicle_battery_voltage = 'NA'
    else:
        vehicle_battery_voltage = round(vehicle_battery_voltage, 1)

    switches.append(
        InfoLabel(
            category='vehicle',
            title='Vehicle Battery',
            subtext='Voltage',
            text=f'{vehicle_battery_voltage} V'
        )
    )

    wh1 = request.app.hal.watersystems.handler.water_heater[1].state.dict()
    wh_mode = wh1.get('mode')
    switches.append(
        OptionWidget(
            category='watersystems',
            title='Truma Water Heater Mode',
            option_param='mode',
            options=[
                {
                    'key': EventValues.OFF.name,
                    'value': EventValues.OFF
                },
                {
                    'key': 'ECO',
                    'value': EventValues.ECO
                },
                {
                    'key': 'COMFORT',
                    'value': EventValues.COMFORT
                }
            ],
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/watersystems/wh/1/state',
                    'type': 'PUT',
                    'params': {
                        '$mode': 'int'
                    }
                }
            },
            state={
                'mode': wh_mode
            }
        )
    )

    wh_temp = wh1.get('temp')
    switches.append(
            OptionWidget(
                category='watersystems',
                title=f'Truma Water Temp',
                option_param='temp',
                options=[
                    {
                        'key': EventValues.LOW.name,
                        'value': 35
                    },
                    {
                        'key': 'MED',
                        'value': 42
                    },
                    {
                        'key': 'HOT',
                        'value': 49
                    }
                ],
                action={
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/watersystems/wh/1/state',
                        'type': 'PUT',
                        'params': {
                            '$temp': 'int'
                        }
                    }
                },
                state={
                    'temp': wh_temp
                }
            )
        )

    if hasattr(request.app.hal.movables.handler, 'awning'):
        awning = request.app.hal.movables.handler.awning.get(1)
        if awning is not None:
            switches.append(
                OptionWidget(
                    category="movables",
                    title=f'Awning',
                    subtext='Position',
                    option_param='extension',
                    options=[
                        {
                            'key': 'Close',
                            'value': EventValues.CLOSED
                        },
                        {
                            'key': 'Halfway',
                            'value': EventValues.HALF
                        },
                        {
                            'key': 'Full',
                            'value': EventValues.FULL
                        }
                    ],
                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/movables/aw/1/state',
                            'type': 'PUT',
                            'params': {
                                '$extension': 'int'
                            }
                        }
                    },
                    state={
                        'pctExt': awning.state.pctExt
                    }
                )
            )

            switches.append(
                InfoLabel(
                    category="movables",
                    title='Awning Status',
                    text=f'Position: {awning.state.pctExt} / Motion: {awning.state.mtnSense}'
                )
            )

    if hasattr(request.app.hal.movables.handler, 'leveling_jack'):
        for jack_id, jack in request.app.hal.movables.handler.leveling_jack.items():
            jack_state = jack.state
            jacks = jack_state.mode

            switches.append(
                OptionWidget(
                    category="movables",
                    title='Leveling Jacks',
                    subtext='Position',
                    option_param='extension',
                    options=[
                        {
                            'key': 'RETRACT',
                            'value': EventValues.RETRACTED
                        },
                        {
                            'key': 'AUTO LEVEL',
                            'value': EventValues.LEVELING
                        }
                    ],
                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/movables/lj/1/state',
                            'type': 'PUT',
                            'params': {
                                '$extension': 'int'
                            }
                        }
                    },
                    state={
                        'extension': jacks
                    }
                )
            )

    if hasattr(request.app.hal.energy.handler, 'generator'):
        for gen_id, generator in request.app.hal.energy.handler.generator.items():
            switches.append(
                OptionWidget(
                    category='energy',
                    title='Generator',
                    subtext='Operation',
                    option_param='mode',
                    options=[
                        {
                            'key': EventValues.OFF.name,
                            'value': EventValues.OFF
                        },
                        {
                            'key': 'RUN',
                            'value': EventValues.RUN
                        },
                        {
                            'key': 'PRIME',
                            'value': EventValues.PRIME
                        },

                    ],
                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/energy/ge/1/state',
                            'type': 'PUT',
                            'params': {
                                '$mode': 'int'
                            }
                        }
                    },
                    state={
                        'mode': generator.state.mode
                    }
                )
            )

    print(f"\nrunClimate: {request.app.hal.climate.handler.state.get('climate_algo_enabled', 1)}\n")
    try:
        runClimate = request.app.hal.climate.handler.state.get('climate_algo_enabled', 1)
    except Exception as err:
        runClimate = 1

    switches.append(
        OptionWidget(
            category='climate',
            title='Auto Climate Control',
            subtext='Thermostat',
            option_param='onOff',
            options=[
                {
                    'key': "Enabled",
                    'value': 1,
                    'selected': runClimate == 1
                },
                {
                    'key': 'Disabled',
                    'value': 0,
                    'selected': runClimate == 0
                }
            ],
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/testharness/algo/climate',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            },
            state={
                'onOff': runClimate
            }
        )
    )

    if hasattr(request.app.hal.climate.handler, 'air_conditioner'):
        try:
            ac_state = request.app.hal.climate.handler.air_conditioner[1].state.dict()

            ac_onOff = ac_state['comp']
            ac_speed = ac_state['fanSpd']
        except Exception as err:
            print('Ouch ' * 5, f' AC Problem {err}')
            ac_onOff = 0
            ac_speed = 0

        switches.append(
            OptionWidget(
                category='climate',
                title='Air Conditioner',
                subtext='Compressor',
                option_param='comp',
                options=[
                    {
                        'key': "OFF",
                        'value': 0,
                        'selected': ac_onOff == 0
                    },
                    {
                        'key': 'ON',
                        'value': 1,
                        'selected': ac_onOff == 1
                    }
                ],
                action={
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/climate/ac/1/state',
                        'type': 'PUT',
                        'params': {
                            '$comp': 'int'
                        }
                    }
                },
                state={
                    'comp': ac_onOff
                }
            )
        )

        switches.append(
            OptionWidget(
                category='climate',
                title='AC Fan Speed',
                subtext='Blower',
                option_param='fanMode',
                options=[
                    {
                        'key': EventValues.OFF.name,
                        'value': 0,
                        'selected': ac_speed == EventValues.OFF
                    },
                    {
                        'key': EventValues.LOW.name,
                        'value': 53,
                        'selected': ac_speed == EventValues.LOW
                    },
                    {
                        'key': 'MED',
                        'value': 106,
                        'selected': ac_speed == EventValues.MEDIUM
                    },
                    {
                        'key': 'HIGH',
                        'value': 52,
                        'selected': ac_speed == EventValues.HIGH
                    }
                ],
                action={
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}api/climate/ac/1/state',
                        'type': 'PUT',
                        'params': {
                            '$fanMode': 'int'
                        }
                    }
                },
                state={
                    'fanMode': ac_speed
                }
            )
        )

    # Harcoding the fan ids as per instances on the CAN bus for now rather than logical enumeration
    for fan_id, fan in request.app.hal.climate.handler.roof_vent.items():
        fname = fan.attributes.get('name', 'NA')
        switches.append(
            OptionWidget(
                category='climate',
                title=f'{fname} Roof Fan - Hood',
                subtext='Dome',
                option_param='dome',
                options=[
                    {
                        'key': 'Open',
                        'value': EventValues.OPENED,
                        'selected': fan.state.dome == EventValues.ON
                    },
                    {
                        'key': 'Close',
                        'value': EventValues.CLOSED,
                        'selected': fan.state.dome == EventValues.OFF
                    }
                ],
                action={
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/climate/rv/{fan_id}/state',
                        'type': 'PUT',
                        'params': {
                            '$dome': 'int'
                        }
                    }
                },
                state=fan.state
            )
        )

        switches.append(
            OptionWidget(
                category='climate',
                title=f'{fname} Roof Fan - Speed',
                subtext='Speed',
                option_param='fanSpd',
                options=[
                    {
                        'key': EventValues.OFF.name,
                        'value': 0,
                        'selected': fan.state.fanSpd == EventValues.OFF
                    },
                    {
                        'key': EventValues.LOW.name,
                        'value': EventValues.LOW,
                        'selected': fan.state.fanSpd == EventValues.LOW
                    },
                    {
                        'key': 'MED',
                        'value': EventValues.MEDIUM,
                        'selected': fan.state.fanSpd == EventValues.MEDIUM
                    },
                    {
                        'key': 'HIGH',
                        'value': EventValues.HIGH,
                        'selected': fan.state.fanSpd == EventValues.HIGH
                    }
                ],
                action={
                    'type': 'api_call',
                    'action': {
                        'href': f'{BASE_URL}/api/climate/rv/{fan_id}/state',
                        'type': 'PUT',
                        'params': {
                            '$fanSpd': 'int'
                        }
                    }
                },
                state=fan.state
            )
        )

    system_reboot = ButtonWidget(
        category='system',
        title='Reboot HMI',
        action={
            'type': 'api_call',
            'action': {
                'href': f'{BASE_URL}/api/system/reboot',
                'type': 'PUT',
                'params': {}
            }
        }
    )

    switches.append(system_reboot)

    try:
        service_settings = request.app.hal.system.handler.setting.get(1)
    except AttributeError as e:
        print('[FCP] Error getting Setting 1 - Service Settings', e)
        raise

    serviceMode = service_settings.state.serviceModeOnOff

    switches.append(
        ToggleWidget(
            category='system',
            title='Service Mode',
            subtext='Enable/Disable Service Mode',
            state={
                'onOff': serviceMode
            },
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/system/features/settings/serviceMode',
                    'type': 'PUT',
                    'params': {
                        '$onOff': "int"
                    }
                }
            }
        )
    )

    # system_shutdown = ButtonWidget(
    #     category='system',
    #     title='Shutdown HMI',
    #     action={
    #         'type': 'api_call',
    #         'action': {
    #             'href': f'{BASE_URL}/api/system/shutdown',
    #             'type': 'PUT',
    #             'params': {}
    #         }
    #     }
    # )

    # switches.append(system_shutdown)

    switches.append(
        InfoLabel(
            category='system',
            title='Software Version',
            # subtext='ALPHA',
            text=request.app.__version__.get(
                'version',
                'NA'
            )
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='OS Release',
            subtext='',
            text=os_data.get('version_id', 'NA')
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='IP Address',
            subtext=None,
            text=str(get_ip())
        )
    )

    network_login_state = request.app.hal.connectivity.handler.login_state
    if network_login_state.get('success') is False:
        cradlepoint_status = 'Failure'
    elif network_login_state.get('success') is True:
        cradlepoint_status = 'Success'
    elif network_login_state.get('success') is None:
        cradlepoint_status = 'Pending'

    switches.append(
        InfoLabel(
            category='system',
            title='Cradlepoint Login',
            subtext='',
            # text=str(request.app.config.get('last_position'))
            text=cradlepoint_status
        )
    )

    cradlepoint_login_state = (
        f'{network_login_state.get("last_failed_reason", "NA")}'
    )

    switches.append(
        InfoLabel(
            category='system',
            title='Cradlepoint Login Last Error State',
            subtext='',
            text=cradlepoint_login_state
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='GPS Location',
            subtext='',
            # text=str(request.app.config.get('last_position'))
            text=request.app.hal.connectivity.handler.last_full_gps.get('position', 'Pending')
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='Option Codes',
            subtext='',
            text=', '.join(request.app.hal.optionCodes)
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='IoT Service Status',
            subtext='',
            text=request.app.iot_status.get('status', 'NA')
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='IoT Status Msg',
            subtext='',
            text=request.app.iot_status.get('msg', 'NA')
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='Device Environment',
            subtext='',
            text=request.app.iot_status.get('env_url', 'NA')
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='Bluetooth Status',
            subtext='',
            text=bt_status.get('Status', 'NA')
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='Bluetooth Last Pairing Response',
            subtext='',
            text=bt_status.get('lastPairingStatus', 'NA')
        )
    )

    switches.append(
        ButtonWidget(
            category='system',
            title='Reset Bluetooth',
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/settings/bluetooth/reset',
                    'type': 'PUT',
                    'params': {}
                }
            }
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='Bluetooth MAC',
            subtext='',
            text=bt_mac_address
        )
    )

    switches.append(
        InfoLabel(
            category='system',
            title='Bluetooth Device ID',
            subtext='',
            text=bt_status.get('DeviceId', 'NA')
        )
    )

    if hasattr(request.app.hal.features.handler, 'diagnostics'):
        if 3 in request.app.hal.features.handler.diagnostics:
            switches.append(
                InfoLabel(
                    category='system',
                    title='Free Storage Space',
                    subtext='',
                    text='{} MiB'.format(
                        request.app.hal.features.handler.diagnostics[3].state.userStorage
                    )
                )
            )

            switches.append(
                InfoLabel(
                    category='system',
                    title='Free Root Space',
                    subtext='',
                    text='{} MiB'.format(
                        request.app.hal.features.handler.diagnostics[3].state.systemStorage
                    )
                )
            )

            switches.append(
                InfoLabel(
                    category='system',
                    title='Current CPU Load',
                    subtext='',
                    text='{} %'.format(
                        request.app.hal.features.handler.diagnostics[3].state.cpuLoad
                    )
                )
            )

            switches.append(
                InfoLabel(
                    category='system',
                    title='Current Memory Usage',
                    subtext='',
                    text='{} MiB'.format(
                        request.app.hal.features.handler.diagnostics[3].state.memory
                    )
                )
            )

            if request.app.hal.features.handler.diagnostics[3].state.startTime is None:
                uptime = -1
            else:
                uptime = time.time() - request.app.hal.features.handler.diagnostics[3].state.startTime

            switches.append(
                InfoLabel(
                    category='system',
                    title='System Uptime',
                    subtext='',
                    text=f'{round(uptime, 1)} seconds'
                )
            )

    # Energy Info
    solar_input_power = request.app.hal.energy.handler.energy_source[1].state
    switches.append(
        InfoLabel(
            category='energy',
            title='Solar Input',
            subtext='Xantrex MPTT30',
            text=f'''{solar_input_power.watts} Watts'''
        )
    )

    # TODO Get Inverter state
    inverter_id = 1
    inverter_state = request.app.hal.energy.handler.inverter[inverter_id].state

    switches.append(
        ToggleWidget(
            category='energy',
            title='Inverter',
            subtext='Xantrex 2000W',
            state={
                'onOff': inverter_state
            },
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/energy/ei/{inverter_id}/state',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            }
        )
    )

    switches.append(
        OptionWidget(
            category='energy',
            title=f'Inverter',
            subtext='Xantrex 2000W',
            option_param='onOff',
            options=[
                {
                    'key': EventValues.OFF.name,
                    'value': EventValues.OFF
                },
                {
                    'key': 'ON',
                    'value': EventValues.ON
                }
            ],
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/energy/ei/{inverter_id}/state',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int'
                    }
                }
            },
            state={
                'onOff': inverter_state
            }
        )
    )

    inverter_load = request.app.hal.energy.handler.get_inverter_load(inverter_id=1)
    #print('Getting inverter load', inverter_load)

    try:
        switches.append(
            InfoLabel(
                category='energy',
                title='Inverter Output (Watts)',
                subtext='Overload: ' + str(inverter_load.get('in_overload')),
                text=f'{inverter_load.get("watts")} Watts'
            )
        )

        inverter_voltage = inverter_load.get("voltage")
        if inverter_voltage is None:
            inverter_voltage = 'NA'
        else:
            inverter_voltage = round(inverter_voltage, 1)

        switches.append(
            InfoLabel(
                category='energy',
                title='Inverter Output (Volts)',
                # subtext='Volts',
                text=f'{inverter_voltage} Volts'
            )
        )

        inverter_amps = inverter_load.get("current")
        if inverter_amps is None:
            inverter_amps = 'NA'
        else:
            inverter_amps = round(inverter_amps, 1)

        switches.append(
            InfoLabel(
                category='energy',
                title='Inverter Output (Current)',
                # subtext='Volts',
                text=f'{inverter_amps} Amps'
            )
        )

        # Being verbose here as an example of how this can be done without a specific function in the HW layer
        # Probably better to have a function per type of EQ (inverter, charger, etc.)
        charger_id = 1
        charger_key = f'charger__{charger_id}__'
        charger_voltage = request.app.hal.energy.handler.state.get(charger_key + 'voltage')
        charger_current = request.app.hal.energy.handler.state.get(charger_key + 'current')

        if charger_voltage is None or charger_current is None:
            charger_watts = 'NA'
            if charger_voltage is None:
                charger_voltage = 0
            if charger_current is None:
                charger_current = 0
        else:
            charger_watts = int(charger_voltage * charger_current)

        switches.append(
            InfoLabel(
                category='energy',
                title='Shore Input',
                subtext=f'{charger_voltage:0.0f} V / {charger_current:0.0f} A',
                text=f'{charger_watts} Watts'
            )
        )
    except:
        pass

    try:
        switches.append(
            SliderWidget(
                    category='system',
                    title='HMI Display Brightness',
                    subtext='Current %',       # Add the brightness currently set

                    min=10,
                    max=100,
                    step=5,
                    unit='%',

                    state={
                        'value': 75     # Get from system data
                    },

                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/system/display/brightness',
                            'type': 'PUT',
                            'params': {
                                '$value': 'int'
                            }
                        }
                    }
                )
        )
    except Exception as err:
        print('[FCP] Error when handlding Display Brightness', err)

    # # Lights, get them from lighting
    switches.append(
        ButtonWidget(
            category='lighting',
            title='Set all lights on',
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/lighting/manufacturing/reset',
                    'type': 'PUT',
                    'params': {}
                }
            }
        )
    )
    switches.append(
        ButtonWidget(
            category='lighting',
            title='Set default lights on',
            action={
                'type': 'api_call',
                'action': {
                    'href': f'{BASE_URL}/api/lighting/reset',
                    'type': 'PUT',
                    'params': {}
                }
            }
        )
    )
    for zone_id, zone in request.app.hal.lighting.handler.lighting_zone.items():
        try:
            switches.append(
                ToggleWidget(
                    category='lighting',
                    title=f'LZ {zone_id} ({zone.attributes.get("name")})',
                    subtext=f'Light Zone {zone_id}',
                    state=zone.state,
                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/lighting/lz/{zone_id}/state',
                            'type': 'PUT',
                            'params': {
                                '$onOff': 'int'
                            }
                        }
                    }
                )
            )
            switches.append(
                SliderWidget(
                    category='lighting',
                    title=f'LZ {zone_id} Brightness',
                    subtext=f'Light Zone {zone_id} Brightness',

                    min=10,
                    max=100,
                    step=5,
                    unit='%',

                    state=zone.state,
                    action = {
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/lighting/lz/{zone_id}/state',
                            'type': 'PUT',
                            'params': {
                                '$onOff': 'int',
                                '$brt': 'int'
                            }
                        }
                    }
                )
            )
        except Exception as err:
            print('Error in lighting', err)
            break

    # Climate addons
    main_temp = request.app.hal.climate.handler.state.get('currenttemp__1')
    if main_temp is None:
        main_temp = 'NA'
    else:
        main_temp = round(main_temp, 1)

    switches.append(
        InfoLabel(
            category='climate',
            title='Temperature MAIN (DOMETIC)',
            subtext='Celsius',
            text=f'{main_temp} °C'
        )
    )

    aux_temp = request.app.hal.climate.handler.state.get('currenttemp__2')
    if aux_temp is None:
        aux_temp = 'NA'
    else:
        aux_temp = round(aux_temp, 1)

    switches.append(
        InfoLabel(
            category='climate',
            title='Temperature Bath FAN (DOMETIC)',
            subtext='Celsius',
            text=f'{aux_temp} °C'
        )
    )

    ac_temp = request.app.hal.climate.handler.state.get('currenttemp__4')
    if ac_temp is None:
        ac_temp = 'NA'
    else:
        ac_temp = round(ac_temp, 1)

    switches.append(
        InfoLabel(
            category='climate',
            title='Temperature Truma AC',
            subtext='Celsius',
            text=f'{ac_temp} °C'
        )
    )

    outside_temp = request.app.hal.climate.handler.thermostat[2].get_temperature()
    if outside_temp is None:
        outside_temp = 'NA'
    else:
        outside_temp = round(outside_temp, 1)

    switches.append(
        InfoLabel(
            category='climate',
            title='Temperature Outside',
            subtext='Celsius',
            text=f'{outside_temp} °C'
        )
    )
    # TODO where will we keep user settings?

    if hasattr(request.app.hal.climate.handler, 'refrigerator'):
        for instance, fridge in request.app.hal.climate.handler.refrigerator.items():
            fridge_temp = fridge.get_temperature('F')
            if fridge_temp is None:
                fridge_temp = 'NA'
            else:
                fridge_temp = round(fridge_temp, 1)

            fridge_type = fridge.attributes.get('type', 'NA').capitalize()

            switches.append(
                InfoLabel(
                    category='climate',
                    title=f'Temperature {fridge_type}',
                    subtext='Fahrenheit',
                    text=f'{fridge_temp} °F'
                )
            )

    # DEADMAN Switch Tester
    switches.append(
        FCPDeadMan(
            category='electrical',
            title="DUMMY DEADMAN",
            name="DummyDead",
            option_param="mode",
            options=[
                {
                    'key': 'OFF',
                    'value': EventValues.OFF
                },
                {
                    'key': 'ON',
                    'value': EventValues.ON,
                    'enabled': False
                }
            ],
            state={
                'mode': EventValues.OFF
            },
            holdDelayMs=500,
            actions={
                'PRESS': {
                    'type': 'api_call',
                    'action': {
                        'href': '/deadman/test/PRESS',
                        'type': 'PUT',
                        'params': {
                            '$mode': 'int'
                        }
                    }
                },
                'HOLD': {
                    'type': 'api_call',
                    'action': {
                        'href': '/deadman/test/HOLD',
                        'type': 'PUT',
                        'params': {
                            '$mode': 'int'
                        }
                    }
                },
                'RELEASE': {
                    'type': 'api_call',
                    'action': {
                        'href': '/deadman/test/RELEASE',
                        'type': 'PUT',
                        'params': {
                            '$mode': 'int'
                        }
                    }
                }
            }
        )
    )

    for circuit in circuits:
        if circuit.get('short'):
            circuit_id = circuit.get('id')
            state = circuit_states.get(f'dc__{circuit_id}', {'onOff': 0})
            print(circuit_id, state, circuit_states)
            widget = circuit.get('widget', 'toggle')

            if widget == 'button':
                switch = ButtonWidget(
                    category=circuit.get('category', 'electrical'),  # Placeholder until we can read from the circuits
                    title=circuit.get('long', 'Undefined'),
                    subtext=get_onoff_text(state.get('onOff')),
                    text=circuit.get('buttonText', 'SEND'),
                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/electrical/dc/{circuit_id}',
                            'type': 'PUT',
                            'params': {
                                'onOff': 1
                            }
                        }
                    }
                )
            elif widget == 'deadman':
                switch = OptionWidget(
                    category=circuit.get('category', 'electrical'),
                    title=circuit.get('long', 'Undefined'),
                    subtext=get_onoff_text(state.get('onOff')),
                    option_param='mode',
                    options=[
                        {
                            'key': circuit.get('backText', 'Backward'),
                            'value': -1,
                            'selected': False
                        },
                        {
                            'key': EventValues.OFF.name,
                            'value': 0,
                            'selected': False
                        },
                        {
                            'key': circuit.get('forwardText', 'Forward'),
                            'value': 1,
                            'selected': False
                        }
                    ],
                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/electrical/dc/{circuit_id}',
                            'type': 'PUT',
                            'params': {
                                '$mode': 'int'
                            }
                        }
                    },
                    state={
                        'mode': state.get('mode', -99)
                    }
                )
            else:
                # switch = OptionWidget(
                #     category=circuit.get('category', 'electrical'),
                #     title=circuit.get('long', 'Undefined'),
                #     subtext='',
                #     option_param='onOff',
                #     options=[
                #         {
                #             'key': EventValues.OFF,
                #             'value': EventValues.OFF
                #         },
                #         {
                #             'key': 'ON',
                #             'value': EventValues.RUN
                #         }
                #     ],
                #     action={
                #         'type': 'api_call',
                #         'action': {
                #             'href': f'{BASE_URL}/api/electrical/dc/{circuit.get("id")}',
                #             'type': 'PUT',
                #             'params': {
                #                 '$onOff': 'int'
                #             }
                #         }
                #     },
                #     state={
                #         'onOff': state.get('onOff')
                #     }
                # )

                switch = ToggleWidget(
                    category=circuit.get('category', 'electrical'),  # Placeholder until we can read from the circuits
                    title=circuit.get('long', 'Undefined'),
                    subtext=get_onoff_text(state.get('onOff')),
                    state={
                        'onOff': state.get('onOff')
                    },
                    action={
                        'type': 'api_call',
                        'action': {
                            'href': f'{BASE_URL}/api/electrical/dc/{circuit.get("id")}',
                            'type': 'PUT',
                            'params': {
                                '$onOff': 'int'
                            }
                        }
                    }
                )
            switches.append(switch)

    diag_present = False
    sys_diag_present = False

    for device in diagnostics:
        can_name = device.get('name', 'NA')
        error = device.get('stale')
        if error is None:
            stale_text = 'ERROR NEVER'
        elif error is True:
            stale_text = 'ERROR'
        else:
            stale_text = 'OK'

        dev_category = device.get('category')

        if dev_category == 'can':
            switches.append(
                InfoLabel(
                    category='can',
                    title=f'CAN Status: {can_name}',
                    subtext='',
                    text=stale_text
                )
            )
            diag_present = True
        elif dev_category == 'system':
            switches.append(
                InfoLabel(
                    category='system',
                    title=f'System Status: {can_name}',
                    subtext='',
                    text=stale_text
                )
            )
            sys_diag_present = True

    if diag_present is False:
        switches.append(
            InfoLabel(
                category='can',
                title='No CAN status received yet',
                subtext='',
                text=''
            )
        )

    if sys_diag_present is False:
        switches.append(
            InfoLabel(
                category='system',
                title='No system diagnostics status received yet',
                subtext='',
                text=''
            )
        )

    electrical_state = request.app.hal.electrical.handler.state
    print('Electrical State', electrical_state)
    input_mapping = request.app.hal.electrical.handler.config.get('RV1_CONTROLS', {})
    input_mapping.update(request.app.hal.electrical.handler.config.get('SI_CONTROLS', {}))
    input_mapping.update(request.app.hal.electrical.handler.config.get('KEYPAD_CONTROLS', {}))

    for key, value in request.app.hal.electrical.handler.state.items():
        if key.startswith('switches'):
            print('[KEY]', key)
            bank, c_id = key.split('bank_')[1].split('_')
            map_key = f'{bank}-{c_id}'
            name = input_mapping.get(map_key, {}).get('Name', '')
            # request.app.hal.electrical.handler.rv1_controls.get()
            switches.append(
                InfoLabel(
                    category='electrical',
                    title='Switch State',
                    subtext=f'Bank: {bank}, Switch: {c_id}, ({name})',
                    text='On' if value.get('onOff') == 1 else 'Off'
                )
            )


    # Add more system

    categories = [
        {
            'title': 'All',
            'name': 'fcpCategoryAll',
            'category': None
        },
        {
            'title': 'Lighting',
            'name': 'fcpCategoryLighting',
            'category': 'lighting'
        },
        {
            'title': 'Climate',
            'name': 'fcpCategoryClimate',
            'category': 'climate'
        },
        {
            'title': "Movables",
            'name': 'fcpCategoryMovable',
            'category': "movables"
        },
        {
            'title': 'Water',
            'name': 'fcpCategoryWater',
            'category': 'watersystems'
        },
        {
            'title': 'Vehicle',
            'name': 'fcpCategoryVehicle',
            'category': 'vehicle'
        },
        {
            'title': 'Energy',
            'name': 'fcpCategoryEnergy',
            'category': 'energy'
        },
        {
            'title': 'Electrical',
            'name': 'fcpCategoryElectrical',
            'category': 'electrical'
        },
        {
            'title': 'System',
            'name': 'fcpCategorySystem',
            'category': 'system'
        },
        {
            'title': 'CAN Bus',
            'name': 'fcpCategoryCAN',
            'category': 'can'
        }
    ]

    response = {
        'overview': {
            'title': 'Test Panel',
            'name': 'FCPOverview',
            'categories': categories
        },
        # 'switches': sorted(switches, key=lambda k: (k.category, k.title))
        'switches': switches
    }

    return response
