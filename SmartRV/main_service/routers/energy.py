import datetime

from typing import Optional, List

import logging

import json

from .common import (
    BaseAPIModel,
    BaseAPIResponse
)

from main_service.components.energy import GeneratorState
wgo_logger = logging.getLogger('main_service')

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from enum import Enum, IntEnum
from pydantic import BaseModel, Field

from main_service.modules.hardware.hal import hw_layer

from main_service.modules.logger import prefix_log
from .ui.ui_inverter import gui_inverter

from common_libs.models.notifications import (
    request_to_iot)

class ChargeLvl(BaseModel):
    watts: int


class EnergySystem(BaseAPIModel):
    type: str = Field(
        'SOLAR|BMS|BMS_LITHIONICS|BATTERY|SOURCE|CONSUMER_AC|CONSUMER_DC',
        description='Energy related system for power input, output etc.'
    )


class EnergySensor(BaseModel):
    id: int
    type: str
    name: str
    state: dict


class EnergyZoneState(BaseModel):
    onOff: int = Field(
        0,
        description=''
    )


class EnergyZone(BaseModel):
    id: int
    type: str
    name: str
    state: dict
    sensors: Optional[List[EnergySensor]]
    inverters: Optional[List[dict]]
    sources: Optional[List[dict]]
    consumers: Optional[List[dict]]
    bms: Optional[dict]


class EnergyResponse(BaseAPIResponse):
    energy: List[EnergyZone]


class SimpleInverterMeteredState(BaseModel):
    onOff: int
    maxContinuousPowerWatts: int
    currentLoad: int
    loadSheddingActive: int


# class SimpleOnOff(BaseModel):
#     onOff: int = Field(
#         0,
#         description='Off=0, On=1',
#         min=0,
#         max=2
#     )


class ProPowerState(BaseModel):
    voltage: float
    current: float
    watts: int
    active: bool


class ProPowerControl(BaseModel):
    onOff: int


class SimplePowerState(BaseModel):
    voltage: float
    current: float
    watts: int
    active: bool


class BMSLithionics(BaseModel):
    stateOfCharge: float
    isCharging: bool
    netPowerWatts: int
    timeTilleMinutes: int
    voltage: int
    current: int


class EVShoreState(SimplePowerState):
    currentChargeLevel: str
    setChargeLevel: str


class EVShoreControl(BaseModel):
    setChargeLevel: str


class Consumer(BaseModel):
    watts: int
    voltage: int
    current: int
    runtimeMinutes: int
    accuracy: str = Field('FIXED', description='Values can be FIXED, MEASURED and ESTIMATED')


def get_circuit_states(hal):
    INVERTER_CIRCUIT_ID = 0x15
    circuit_states = hal.electrical.handler.get_state()
    inverter_state = circuit_states.get(f'dc_{INVERTER_CIRCUIT_ID}', {'onOff': 1})
    inverter_onOff = inverter_state.get('onOff')
    return {'inverter': inverter_onOff}

# This lists the types of sources the API supports
SOURCES_SUPPORTED = (
    'SOURCE_EV_SHORE',      # 848EC introduced multi level shore input
    'SOURCE_PRO_POWER',     # Ford chassis power supply
    'SIMPLE_INPUT_SOLAR'    # CZone Shunt based Solar reading
)

def inverter_overview_list(hal, zone_id=1):
    # TODO: Push this to HW layer
    inverter_ids = [1, ]
    result = []

    for inverter_id in inverter_ids:
        load_shedding_active = False
        result.append(
            {
                'id': 1,
                'type': 'SIMPLE_INVERTER_METERED',
                'name': 'Inverter',
                'description': 'Victron Inverter',
                'state': {
                    'onOff': get_circuit_states().get('inverter'),
                    'maxContinuousPowerWatts': hal.energy.handler.get_inverter_continuous_max(
                        inverter_id
                    ),
                    'currentLoad': hal.energy.handler.get_inverter_load(inverter_id),
                    'loadSheddingActive': load_shedding_active
                },
                'information': None,
                'api': {
                    'path': f'/api/{PREFIX}/zones/{zone_id}/inverters/{inverter_id}/state',
                    'GET': {
                        'req': None,
                        'res': 'SIMPLE_INVERTER_METERED'
                    },
                    'PUT': {
                        'req': 'SIMPLE_ONOFF',
                        'res': 'SIMPLE_INVERTER_METERED'
                    }
                }
            }
        )
    return result


def solar_overview_list(hal):
    # TODO: Get this from HW layer
    result = []
    solar_ids = [1,]
    for solar_id in solar_ids:
        current_charge_watts = hal.energy.handler.get_solar_input(solar_id)
        result.append(
            {
                'id': solar_id,
                'type': 'SIMPLE_INPUT_SOLAR',
                'name': 'Solar Input',
                'description': 'Solar input from multiple chargers through Shunt sensor',
                'state': {
                    'watts': current_charge_watts.get('watts'),
                    'voltage': current_charge_watts.get('voltage'),
                    'current': current_charge_watts.get('current'),
                    'active': current_charge_watts.get('active')
                },
                'information': None
            }
        )

    return result


def battery_overview_list(hal, zone_id=1):
    '''To be implemented'''
    # Get BMS and Battery details from HW Layer
    # Get Battery details from HW Layer

    battery_list = [
        {
            'id': 1,
            'type': 'LITHIONICS_LI_ION',
            'name': '',
            'description': '',
            'cellCount': 16,
            'state': None,
        },
        {
            'id': 2,
            'type': 'LITHIONICS_LI_ION',
            'name': '',
            'description': '',
            'cellCount': 16,
            'state': None,
        }
    ]

    return battery_list


def charger_overview_list(zone_id=1):
    '''Get list of chargers in the system.
    Usually used within a BMS object'''
    return [
        {
            'id': 1
        },
        {
            'id': 2
        },
        {
            'id': 3
        },
        {
            'id': 4
        }
    ]


def consumer_overview_list(sort_field='watts', order_reverse=True, zone_id=1):
    # Get list of consumers from HAL
    # Get Inverter Circuits on
    # Get Inverter Load
    result = [
        {
            'id': 99,
            'name': 'DC Circuits',
            'description': 'Test',
            'type': 'DC_CONSUMER',
            'systemType': None,
            'systemSubType': None,
            'state': {
                'watts': 150,
                'voltage': 13.4,
                'current': 11.2,
                'runtimeMinutes': 120,
                'accuracy': 'MEASURED'
            }
        },
        {
            'id': 100,
            'name': 'AC Circuit',
            'description': 'Test',
            'type': 'AC_CONSUMER',
            'systemType': None,
            'systemSubType': None,
            'state': {
                'voltage': 120,
                'current': 2.0,
                'watts': 250,
                'runtimeMinutes': 10,
                'accuracy': 'ESTIMATED'
            }
        },
        {
            'id': 101,
            'name': 'Water Heater',
            'description': 'Test',
            'type': 'AC_CONSUMER',
            'systemType': 'watersystems',
            'systemSubType': 'SIMPLE_WATER_HEATER',
            'state': {
                'watts': 1200,
                'voltage': 120,
                'current': 10,
                'runtimeMinutes': 4,
                'accuracy': 'FIXED'
            }
        }
    ]

    sorted_result = sorted(result, key=lambda x: x['state']['watts'], reverse=order_reverse)

    return sorted_result


def source_overview_list(hal, zone_id=1):
    '''Get list of sources.'''
    result = []

    energy_sources = hal.energy.handler.get_energy_sources(zone_id)
    for source in energy_sources:
        source_id = source.get('id')
        source_type = source.get('type')
        path = f'/api/{PREFIX}/zones/{zone_id}/sources/{source_id}/state'

        if source_type == 'SIMPLE_INPUT_SOLAR':
            api = {
                'path': path,
                'GET': {
                    'req': None,
                    'res': 'SIMPLE_INPUT_SOLAR'
                },
                'PUT': None
            }

        elif source_type == 'SOURCE_EV_SHORE':
            api = {
                'path': path,
                'GET': {
                    'req': None,
                    'res': 'SOURCE_EV_SHORE'
                },
                'PUT': {
                    'req': 'SOURCE_EV_SHORE',
                    'res': 'SOURCE_EV_SHORE'
                }
            }

        elif source_type == 'SOURCE_PRO_POWER':
            api = {
                'path': path,
                'GET': {
                    'req': None,
                    'res': 'SOURCE_PRO_POWER'
                },
                'PUT': {
                    'req': 'SOURCE_PRO_POWER',
                    'res': 'SOURCE_PRO_POWER'
                }
            }

        result.append(
            {
                'id': source_id,
                'type': source_type,
                'name': source.get('name'),
                'description': source.get('description'),
                'state': source.get('state'),
                'api': api
            }
        )

    return result


def get_single_source(zone_id, source_id):
    sources = source_overview_list(zone_id)
    source = None

    for s in sources:
        if s.get('id') == source_id:
            source = s
            break

    if source is None:
        raise HTTPException(404, {'msg': f'Cannot find source {source_id} in zone {zone_id}'})

    return source



def sensor_overview_list(zone_id=1):
    result = []

    # AC Sensor Inverter
    # AC Sensor Charging

    return result


def bms_overview(hal, zone_id=1, battery_id=1):
    battery_state = hal.energy.handler.get_battery_state(battery_id)
    bms = {
        'id': battery_id,
        'type': 'BMS_LITHIONICS',
        'name': 'House Battery',
        'state': {
            # Current Battery charge
            'stateOfCharge': battery_state.get('stateOfCharge'),
            # Charging or discharging
            'isCharging': battery_state.get('isCharging'),
            # Net incoming watts, could be negative
            'netPowerWatts': battery_state.get('watts'),
            # Remaining charge time or runtime
            'timeTillMinutes': battery_state.get('remainingRuntime'),
            # Volts of the system
            'voltage': battery_state.get('voltage'),
            'current': battery_state.get('current'),
            'bmsTemp': battery_state.get('bmsTemp'),

        },
        'controls': None,
        'description': 'Lithionics',
        'batteries': battery_overview_list(),
        # TODO: Add details that are available per charger to the system
        'chargers': charger_overview_list(),
        'api': {
            'path': f'/api/{PREFIX}/zones/{zone_id}/bms/state',
            'GET': {
                'res': 'BMS_LITHIONICS'
            }
        }
    }
    return bms


def energy_zone_overview(zone_id):
    energy_zone = {
        'id': zone_id,
        'name': 'Main',
        'type': 'ENERGY_ZONE',
        'state': {
            # This is static for now, could act as a masterswitch with PUT request
            'onOff': 1
        },
        'controls': None,
        'bms': bms_overview(zone_id=zone_id),
        'sources': source_overview_list(zone_id),
        'inverters': inverter_overview_list(zone_id),
        'consumers': consumer_overview_list(zone_id),
        'generators': None,
        'sensors': sensor_overview_list(zone_id),
    }
    return energy_zone


PREFIX = 'energy'

router = APIRouter(
    prefix=f'/{PREFIX}',
    tags=['ENERGYMANAGEMENT',]
)


# Overview
@router.get('', response_model=EnergyResponse, tags=['ROOT_API'], response_model_exclude_none=False)
@router.get('/zones', response_model=EnergyResponse, response_model_exclude_none=False)
async def get_energy_overview():
    energy_zones = []

    # TODO: Get the energy zones from HW later, for now that might be hardcoded
    energy_zone_id = 1
    battery_id = 1

    energy_zone = energy_zone_overview(energy_zone_id)
    # {
    #     'id': energy_zone_id,
    #     'name': 'Main',
    #     'type': 'ENERGY_ZONE',
    #     'state': {
    #         # This is static for now, could act as a masterswitch with PUT request
    #         'onOff': 1
    #     },
    #     'controls': None,
    #     'bms': bms_overview(zone_id=energy_zone_id),
    #     'sources': source_overview_list(energy_zone_id),
    #     'inverters': inverter_overview_list(energy_zone_id),
    #     'consumers': consumer_overview_list(energy_zone_id),
    #     'generators': None,
    #     'sensors': sensor_overview_list(energy_zone_id),
    # }

    energy_zones.append(energy_zone)

    result = EnergyResponse(
        count=len(energy_zones),
        key='energy',
        settings={},
        energy=energy_zones,
    )
    return result


@router.get('/zones/{zone_id}')
async def get_energy_zone(zone_id):
    return energy_zone_overview(zone_id)


@router.get('/zones/{zone_id}/bms/state')
async def get_bms_state(zone_id: int, battery_id: int=1):
    # Get BMS state
    bms = bms_overview(zone_id=zone_id)

    return bms.get('state')


@router.get('/zones/{zone_id}/sources')
async def get_zone_sources(zone_id: int):
    return source_overview_list(zone_id)


@router.get('/zones/{zone_id}/sources/{source_id}')
async def get_source_state(zone_id: int, source_id: int):
    '''Returns the full source object.'''
    source = get_single_source(zone_id, source_id)

    return source


@router.get('/zones/{zone_id}/sources/{source_id}/state')
async def get_source_state(zone_id: int, source_id: int):
    '''Returns the state of a source object.'''
    # Get source details
    source = get_single_source(zone_id, source_id)

    return source.get('state', {})


@router.put('/zones/{zone_id}/sources/{source_id}/state')
async def set_source_state(request: Request, zone_id: int, source_id: int, state: dict):
    source = get_single_source(zone_id, source_id)
    # Check if the source has controls
    if source.get('api', {}).get('PUT') is None:
        raise HTTPException(400, {'msg': f'No controls available for this source: {source_id} in zone: {zone_id}'})

    # Set state
    result = request.app.hal.energy.handler.set_source_state(zone_id, source_id, state)
    # Get state
    source = get_single_source(zone_id, source_id)

    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": f'/api/energy/zones/{zone_id}/sources/{source_id}/state',
            "body": state
        }
    )
    # return
    return source.get('state')


@router.get('/zones/{zone_id}/consumers')
async def get_zone_consumers(zone_id: int):
    return consumer_overview_list(zone_id=zone_id)


@router.get('/zones/{zone_id}/sensors')
async def get_zone_sensors(zone_id: int):
    return []


@router.get('/zones/{zone_id}/generators')
async def get_zone_generators(zone_id: int):
    return []


@router.get('/zones/{zone_id}/inverters')
async def get_zone_inverters(zone_id: int):
    return inverter_overview_list(zone_id=zone_id)


### Inverter
# Get Inverter overview
@router.get('/zones/{zone_id}/inverters/{inverter_id}/state')
async def get_zone_inverter_state(zone_id: int, inverter_id: int):
    inverters = inverter_overview_list(zone_id=zone_id)
    inverter = None
    for i in inverters:
        if i.get('id') == inverter_id:
            inverter = i
            break

    if inverter is None:
        raise HTTPException(404, {'msg': f'Inverter: {inverter_id} not found in zone: {zone_id}'})

    return inverter.get('state')


@router.get('/inverter')
async def get_inverter_overview(zone_id: int=1, inverter_id:int=1):
    result = await gui_inverter()
    return result

# PUT Control Inverter
@router.put('/inverters/{inverter_id}/state')
@router.put('/inverter/{inverter_id}')
@router.put('/zones/{zone_id}/inverters/{inverter_id}/state')
async def set_inverter_controls(request: Request, inverter_id: int, controls: dict, zone_id: int=1):
    # Change this to a hw_layer call in hw_energy
    result = request.app.hal.energy.handler.set_inverter_state(controls, inverter_id=inverter_id)

    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": f'/api/energy/zones/{zone_id}/inverters/{inverter_id}/state',
            "body": controls
        }
    )
    return result

@router.put('/inverter/{inverter_id}/set')
async def put_inverter_state(request: Request, inverter_id: int, onOff: dict):
    set_response = request.app.hal.energy.handler.set_inverter_state(onOff, inverter_id=inverter_id)
    return set_response


# GET Inverter Load
@router.get('/inverter/{inverter_id}/load')
async def get_inverter_load(inverter_id: int):
    '''Get load of inverter.'''
    inverter_load_watts = request.app.hal.energy.handler.get_inverter_load(inverter_id)

    return {
        'result': inverter_load_watts
    }


### Solar
@router.get('/sources/solar/{solar_id}/state')
async def get_solar_overview(solar_id: int):
    '''Get overview of all solar inputs from HW layer and represent'''
    # current_charge_watts = request.app.hal.energy.handler.get_solar_input(solar_id)
    solars = solar_overview_list()
    for solar in solars:
        if solar_id == solar['id']:
                result = solar['state']

        else:
           raise HTTPException(422, 'invalid solar ID')
    return result


@router.get('/consumers/{consumer_id}/state')
#putin except error
async def get_consumer_state(consumer_id: int):
    consumers = consumer_overview_list()
    for consumer in consumers:
        if consumer_id == consumer['id']:
            result = consumer
    return result


@router.put('/{battery_id}/charge_lvl')
async def set_charge_lvl(request: Request, battery_id: int, charge_lvl: ChargeLvl) -> dict:
    '''Set charge lvl in watts.'''
    current_state = request.app.hal.energy.handler.state.get(f'bms__{battery_id}__charge_lvl')
    prefix_log(wgo_logger, __name__, f'Current charge level: {current_state}')
    if current_state is None:
        prefix_log(wgo_logger, __name__, f'No current state available for bms__{battery_id}__charge_lvl')

    # Set the charge lvl
    result = request.app.hal.energy.handler.set_charger_lvl(charge_lvl.watts)

    response = {'result': result}

    # Add the request to the IOT queue
    await request_to_iot(
        {
            "hdrs": dict(request.headers),
            "url": f'/api/energy/{battery_id}/charge_lvl',
            "body": charge_lvl.dict(exclude_none=True)
        }
    )
    return response



@router.get('/battery/{battery_id}/soc')
async def get_state_of_charge(battery_id: int):
    '''Get state of charge (soc).'''
    result = request.app.hal.energy.handler.get_state_of_charge(battery_id)
    return {
        'result': str(result)
    }


@router.get('/battery/{battery_id}/remaining_runtime')
async def get_remanining_runtime(battery_id: int):
    '''Get remaining battery runtime.'''
    result = request.app.hal.energy.handler.get_remaining_runtime(battery_id)
    if result is None:
        days = None
        hours = None
        minutes = None
    else:
        days = result / 24 / 60
        hours = result / 60
        minutes = result
    return {
        'time_remaining_days': days,
        'time_remaining_hours': hours,
        'time_remaining_minutes': minutes
    }


# @router.get('/generator')
# async def get_generator(request: Request) -> dict:
#     awe = request.app.hal.energy.handler.get_generator()
#     return awe

# @router.put('/generator')
# async def change_generator(request: Request, state: GeneratorState) -> dict:
#     print('movable router generator',state)
#     result = request.app.hal.energy.handler.ctrl_generator(state)

#     # Add the request to the IOT queue
#     #request_to_iot({"hdrs":dict(request.headers),"url":f'/api/energy/generator',"body":result})

#     return result

@router.get('/schemas')
async def get_schemas(include=None):
    all_schemas = {
        'SIMPLE_ONOFF': SimpleOnOff.schema(),
        'BMS_LITHIONICS': BMSLithionics.schema(),
        'SIMPLE_INVERTER_METERED': SimpleInverterMeteredState.schema(),
        # 'SIMPLE_INVERTER_METERED_CONTROL': SimpleOnOff.schema(),
        'SIMPLE_INPUT_SOLAR': SimplePowerState.schema(),

        'SOURCE_PRO_POWER': SimplePowerState.schema(),
        # 'SOURCE_PRO_POWER_CONTROL': ProPowerControl.schema(),

        'SOURCE_EV_SHORE': EVShoreState.schema(),
        # 'SOURCE_EV_SHORE_CONTROL': EVShoreControl.schema(),
        'DC_CONSUMER': Consumer.schema(),
        'AC_CONSUMER': Consumer.schema(),
        'ENERGY_ZONE': None,
        'LITHIONICS_LI_ION': None,

    }

    schemas = {}

    if include is not None:
        include_list = include.split(',')
        for s in include_list:
            schemas[s.upper()] = all_schemas.get(s.upper())
        return schemas

    return all_schemas

# @router.get('/solar/{solar_id}/level')
# async def get_solar_level(solar_id: int):
#     '''Get input level of the solar chargers.'''
#     solar_input_level = request.app.hal.energy.handler.get_solar_input(solar_id)

#     return {
#         'result': 'OK',
#         'Instance': solar_id,
#         'Type': 'SimpleSolarInput',
#         'SimpleSolarInput': {
#             'Current_Charge_Watts': solar_input_level
#         }
#     }
