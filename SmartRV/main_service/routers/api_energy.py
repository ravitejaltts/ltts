import datetime

from typing import Optional, List

import logging

import json

from .common import BaseAPIModel, BaseAPIResponse

from main_service.components.common import SimpleOnOff, BaseComponent
from main_service.components.energy import BatteryMgmtState, BatteryManagement
from main_service.components.energy import GeneratorState

wgo_logger = logging.getLogger("main_service")

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from enum import Enum, IntEnum
from pydantic import BaseModel, Field, ValidationError

from main_service.modules.logger import prefix_log
from .ui.ui_inverter import gui_inverter

from common_libs.models.notifications import (
    request_to_iot,
    request_to_iot_handler
)
from common_libs.system.state_helpers import check_special_states

from common_libs.models.common import RVEvents, EventValues
from common_libs.models.common import LogEvent
from common_libs.models.common import CODE_TO_ATTR, ATTR_TO_CODE

from main_service.modules.api_helper import validate_wc_api_call, validate_wc_state


class ChargeLvl(BaseModel):
    watts: int


class EnergySystem(BaseAPIModel):
    type: str = Field(
        "SOLAR|BMS|BMS_LITHIONICS|BATTERY|SOURCE|CONSUMER_AC|CONSUMER_DC",
        description="Energy related system for power input, output etc.",
    )


class EnergySensor(BaseModel):
    id: int
    type: str
    name: str
    state: dict


class EnergyZoneState(BaseModel):
    onOff: int = Field(0, description="")


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
    accuracy: str = Field(
        "FIXED", description="Values can be FIXED, MEASURED and ESTIMATED"
    )


def get_circuit_states(hal):
    INVERTER_CIRCUIT_ID = 0x15
    circuit_states = hal.electrical.handler.get_state()
    inverter_state = circuit_states.get(f"dc_{INVERTER_CIRCUIT_ID}", {"onOff": 1})
    inverter_onOff = inverter_state.get("onOff")
    return {"inverter": inverter_onOff}


# This lists the types of sources the API supports
SOURCES_SUPPORTED = (
    "SOURCE_EV_SHORE",  # 848EC introduced multi level shore input
    "SOURCE_PRO_POWER",  # Ford chassis power supply
    "SIMPLE_INPUT_SOLAR",  # CZone Shunt based Solar reading
)

LOCKOUT_ERROR_CODE = 423


def inverter_overview_list(hal, zone_id=1):
    # TODO: Push this to HW layer
    inverter_ids = [
        1,
    ]
    result = []

    for inverter_id in inverter_ids:
        load_shedding_active = False
        result.append(
            {
                "id": 1,
                "type": "SIMPLE_INVERTER_METERED",
                "name": "Inverter",
                "description": "Victron Inverter",
                "state": {
                    "onOff": get_circuit_states(hal).get("inverter"),
                    "maxContinuousPowerWatts": hal.energy.handler.get_inverter_continuous_max(
                        inverter_id
                    ),
                    "currentLoad": hal.energy.handler.get_inverter_load(
                        inverter_id
                    ),
                    "overld": None,  # TODO: Get this from HW layer
                    "shed": load_shedding_active,
                },
                "information": None,
                "api": {
                    "path": f"/api/{PREFIX}/zones/{zone_id}/inverters/{inverter_id}/state",
                    "GET": {"req": None, "res": "SIMPLE_INVERTER_METERED"},
                    "PUT": {"req": "SIMPLE_ONOFF", "res": "SIMPLE_INVERTER_METERED"},
                },
            }
        )
    return result


def solar_overview_list(hal):
    # TODO: Get this from HW layer
    result = []
    solar_ids = [
        1,
    ]
    for solar_id in solar_ids:
        current_charge_watts = hal.energy.handler.get_solar_input(solar_id)
        result.append(
            {
                "id": solar_id,
                "type": "SIMPLE_INPUT_SOLAR",
                "name": "Solar Input",
                "description": "Solar input from multiple chargers through Shunt sensor",
                "state": {
                    "watts": current_charge_watts.get("watts"),
                    "voltage": current_charge_watts.get("voltage"),
                    "current": current_charge_watts.get("current"),
                    "active": current_charge_watts.get("active"),
                },
                "information": None,
            }
        )

    return result


def battery_overview_list(zone_id=1):
    """To be implemented"""
    # Get BMS and Battery details from HW Layer
    # Get Battery details from HW Layer

    battery_list = [
        {
            "id": 1,
            "type": "LITHIONICS_LI_ION",
            "name": "",
            "description": "",
            "cellCount": 16,
            "state": None,
        },
        {
            "id": 2,
            "type": "LITHIONICS_LI_ION",
            "name": "",
            "description": "",
            "cellCount": 16,
            "state": None,
        },
    ]

    return battery_list


def charger_overview_list(zone_id=1):
    """Get list of chargers in the system.
    Usually used within a BMS object"""
    return [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]


def consumer_overview_list(sort_field="watts", order_reverse=True, zone_id=1):
    # Get list of consumers from HAL
    # Get Inverter Circuits on
    # Get Inverter Load
    result = [
        {
            "id": 99,
            "name": "DC Circuits",
            "description": "Test",
            "type": "DC_CONSUMER",
            "systemType": None,
            "systemSubType": None,
            "state": {
                "watts": 150,
                "voltage": 13.4,
                "current": 11.2,
                "runtimeMinutes": 120,
                "accuracy": "MEASURED",
            },
        },
        {
            "id": 100,
            "name": "AC Circuit",
            "description": "Test",
            "type": "AC_CONSUMER",
            "systemType": None,
            "systemSubType": None,
            "state": {
                "voltage": 120,
                "current": 2.0,
                "watts": 250,
                "runtimeMinutes": 10,
                "accuracy": "ESTIMATED",
            },
        },
        {
            "id": 101,
            "name": "Water Heater",
            "description": "Test",
            "type": "AC_CONSUMER",
            "systemType": "watersystems",
            "systemSubType": "SIMPLE_WATER_HEATER",
            "state": {
                "watts": 1200,
                "voltage": 120,
                "current": 10,
                "runtimeMinutes": 4,
                "accuracy": "FIXED",
            },
        },
    ]

    sorted_result = sorted(
        result, key=lambda x: x["state"]["watts"], reverse=order_reverse
    )

    return sorted_result


def source_overview_list(hal, zone_id=1):
    """Get list of sources."""
    result = []

    energy_sources = hal.energy.handler.get_energy_sources(zone_id)
    for source in energy_sources:
        source_id = source.get("id")
        source_type = source.get("type")
        path = f"/api/{PREFIX}/zones/{zone_id}/sources/{source_id}/state"

        if source_type == "SIMPLE_INPUT_SOLAR":
            api = {
                "path": path,
                "GET": {"req": None, "res": "SIMPLE_INPUT_SOLAR"},
                "PUT": None,
            }

        elif source_type == "SOURCE_EV_SHORE":
            api = {
                "path": path,
                "GET": {"req": None, "res": "SOURCE_EV_SHORE"},
                "PUT": {"req": "SOURCE_EV_SHORE", "res": "SOURCE_EV_SHORE"},
            }

        elif source_type == "SOURCE_PRO_POWER":
            api = {
                "path": path,
                "GET": {"req": None, "res": "SOURCE_PRO_POWER"},
                "PUT": {"req": "SOURCE_PRO_POWER", "res": "SOURCE_PRO_POWER"},
            }

        result.append(
            {
                "id": source_id,
                "type": source_type,
                "name": source.get("name"),
                "description": source.get("description"),
                "state": source.get("state"),
                "api": api,
            }
        )

    return result


def get_single_source(zone_id, source_id):
    sources = source_overview_list(zone_id)
    source = None

    for s in sources:
        if s.get("id") == source_id:
            source = s
            break

    if source is None:
        raise HTTPException(
            404, {"msg": f"Cannot find source {source_id} in zone {zone_id}"}
        )

    return source


def sensor_overview_list(zone_id=1):
    result = []

    # AC Sensor Inverter
    # AC Sensor Charging

    return result


def bms_overview(hal, zone_id=1, battery_id=1):
    battery_state = hal.energy.handler.get_battery_state(battery_id)
    bms = {
        "id": battery_id,
        "type": "BMS_LITHIONICS",
        "name": "House Battery",
        "state": {
            # Current Battery charge
            "stateOfCharge": battery_state.get("stateOfCharge"),
            # Charging or discharging
            "isCharging": battery_state.get("isCharging"),
            # Net incoming watts, could be negative
            "netPowerWatts": battery_state.get("watts"),
            # Remaining charge time or runtime
            "timeTillMinutes": battery_state.get("remainingRuntime"),
            # Volts of the system
            "voltage": battery_state.get("voltage"),
            "current": battery_state.get("current"),
            "bmsTemp": battery_state.get("bmsTemp"),
        },
        "controls": None,
        "description": "Lithionics",
        "batteries": battery_overview_list(),
        # TODO: Add details that are available per charger to the system
        "chargers": charger_overview_list(),
        "api": {
            "path": f"/api/{PREFIX}/zones/{zone_id}/bms/state",
            "GET": {"res": "BMS_LITHIONICS"},
        },
    }
    return bms


def energy_zone_overview(hal, zone_id):
    energy_zone = {
        "id": zone_id,
        "name": "Main",
        "type": "ENERGY_ZONE",
        "state": {
            # This is static for now, could act as a masterswitch with PUT request
            "onOff": 1
        },
        "controls": None,
        "bms": bms_overview(hal, zone_id=zone_id),
        "sources": source_overview_list(hal,zone_id),
        "inverters": inverter_overview_list(hal, zone_id),
        "consumers": consumer_overview_list(zone_id),
        "generators": None,
        "sensors": sensor_overview_list(zone_id),
    }
    return energy_zone


PREFIX = "energy"

router = APIRouter(
    prefix=f"/{PREFIX}",
    tags=[
        "ENERGYMANAGEMENT",
    ],
)


# Overview
@router.get(
        "",
        response_model=EnergyResponse,
        tags=["ROOT_API"],
        response_model_exclude_none=False)
async def get_energy_overview(request: Request):
    energy_zones = []

    # TODO: Get the energy zones from HW later, for now that might be hardcoded
    energy_zone_id = 1
    battery_id = 1

    energy_zone = energy_zone_overview(request.app.hal, energy_zone_id)
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
        key="energy",
        settings={},
        energy=energy_zones,
    )
    return result


@router.get("/state")
async def get_energy_state(request: Request) -> dict:
    energy_state = request.app.hal.get_state().get('energy')
    result = {}

    # systems = {
    #     'energy_source': 'es',
    #     'inverter': 'ei',
    #     'battery_management': 'bm',
    #     'fuel_tank': 'ft',
    #     'energy_consumer': 'ec',
    #     'generator': 'ge'
    # }
    for instance, comp in energy_state.items():
        result[instance] = comp.dict()
        # for k, obj in getattr(request.app.hal.energy.handler, system).items():
        #     energy_state[f'{code}{obj.instance}'] = obj.state.dict()

    return result


@router.get('/{code}/{instance}/state/{key}')
async def get_generic_state(request: Request, code: str, instance: int, key: str):
    '''Get a generic state attribute'''
    component = await validate_wc_api_call(request, PREFIX, code, instance)

    if hasattr(component.state, key):
        return getattr(component.state, key)


# Battery Management    ######################
@router.get("/bm/{instance}/state")
async def get_battery_management_state(request: Request, instance: int):
    bms = await validate_wc_api_call(request, PREFIX, 'bm', instance)
    return bms.state


# NOTE: Modified to use set_state, need to review set state
# TODO: Check if this API is needed/desired and make sure the set_state exists and works
@router.put("/bm/{instance}/state")
async def set_battery_management_state(
        request: Request,
        instance: int,
        state: dict
):
    bms = await validate_wc_api_call(request, PREFIX, 'bm', instance)
    bms.set_state(state)

    await request_to_iot_handler(
        request,
        bms.state.dict(exclude_none=True)
    )

    return bms.state


# Inverter ##################
@router.get("/ei/{instance}/state")
async def get_inverter_state(request: Request, instance: int):
    inverter = await validate_wc_api_call(request, PREFIX, 'ei', instance)
    return inverter.state


@router.put("/ei/{instance}/state")
async def set_inverter_state(request: Request, instance: int, state: dict):
    inverter = await validate_wc_api_call(request, PREFIX, 'ei', instance)

    # TODO: Move this to inverter set_state
    result = request.app.hal.energy.handler.set_inverter_state(
        instance,
        state
    )
    # Removed emit events and now will come from state emitter

    # Add the request to the IOT queue
    await request_to_iot_handler(
        request,
        result.dict(exclude_none=True)
    )
    return result


# Charger ##################
@router.get("/ic/{instance}/state")
async def get_charger_state(request: Request, instance: int):
    charger = await validate_wc_api_call(request, PREFIX, 'ic', instance)
    return charger.state


@router.put("/ic/{instance}/state")
async def set_charger_state(request: Request, instance: int, state: dict):
    charger = await validate_wc_api_call(request, PREFIX, 'ic', instance)

    result = charger.set_state(state)
    print('[ENERGY][CHARGER] Result', result)

    # Add the request to the IOT queue
    await request_to_iot_handler(
        request,
        result.dict(exclude_none=True)
    )
    return result


# Energy Sources    #################
@router.get("/es/{instance}/state")
async def get_energy_source_state(request: Request, instance: int):
    energy_source = await validate_wc_api_call(request, PREFIX, 'es', instance)
    return energy_source.state


@router.put("/es/{instance}/state")
async def set_energy_source_state(request: Request, instance: int, state: dict):
    energy_source = await validate_wc_api_call(request, PREFIX, 'es', instance)

    result = request.app.hal.energy.handler.set_energy_source_state(
        instance,
        state
    )
    await request_to_iot_handler(
        request,
        result.dict(exclude_none=True)
    )
    return result


# Energy Consumers  #################
@router.get("/ec/{instance}/state")
async def get_energy_consumer_state(request: Request, instance: int):
    energy_consumer = await validate_wc_api_call(request, PREFIX, 'ec', instance)
    return energy_consumer.state

# No SET state available for energy consumer (yet)

# Fuel Tanks    ###############
@router.get("/ft/{instance}/state")
async def get_fuel_tank_state(request: Request, instance: int):
    fuel_tank = await validate_wc_api_call(request, PREFIX, 'ft', instance)

    # TODO: Compare the current output with what state would provide

    result = request.app.hal.energy.handler.fuel_tank[instance].state
    result_dict = result.dict()
    response = {}

    for key, value in result_dict.items():
        if key.endswith('_'):
            computed_key = key.replace('_', '')
            response[computed_key] = getattr(result, computed_key)
        else:
            response[key] = value
    return response

# No SET state available for fuel tank (yet)

# Generator #############
@router.get("/ge/{instance}/state")
async def get_generator_state(request: Request, instance: int):
    generator = await validate_wc_api_call(request, PREFIX, 'ge', instance)
    # Update the lockouts
    generator.check_lockouts()
    # return the state
    return generator.state


@router.put("/ge/{instance}/state")
async def set_generator_state(request: Request, instance: int, state: dict):
    print(f"set_generator_state {state}")
    generator = await validate_wc_api_call(request, PREFIX, 'ge', instance)

    # Validate the state and fail with proper 422
    _ = await validate_wc_state(request, generator.internal_state, state)

    # TODO: create a generic helper for this
    if request.state.check_special_state is True:
        result = check_special_states(component=generator, in_state=state)
        if result is not None:
            return result

    # Update lockouts
    generator.check_lockouts()
    print('AFTER LOCKOUT CHECK', generator.internal_state)
    cur_state = generator.state
    if cur_state.lockouts and state.get('mode') != EventValues.OFF:
        response = {
            'msg': 'Lockout conditions not met',
            'lockouts': cur_state.lockouts
        }
        # TODO: If request comes from UI inject UI related info

        raise HTTPException(
            LOCKOUT_ERROR_CODE,
            response
        )

    # Else we try to set the state
    # TODO: Need to allow safe values to pass for lockouts, such as OFF ?
    # Maybe handle this on the backend. But it would be odd to receive an error when trying to stop
    # Not all component might have a safe value

    # Warnings are not sent, nor do they need to be checked before executing.
    # A warning might turn into a lockout between receiving this API call and trying to execute

    # TODO: Get the lockouts for this instance of a component and check if any is active
    # Get lockouts that apply to this component from attributes for now
    # Eventually this can be from relationships to a lockoutComponent
    # TODO: Set try/except for lockout validation failure
    # TODO: Get lockouts applicable first and send them into the state transition
    try:
        result = generator.set_state(state)
    except ValueError as err:
        response = {
            'V msg': str(err)
        }
        # TODO: If request comes from UI inject UI related info
        print('VALUEERROR', err)
        raise HTTPException(
            LOCKOUT_ERROR_CODE,
            response
        )

    return result


# Battery
@router.get("/ba/{instance}/state")
async def get_battery_state(request: Request, instance: int):
    battery = await validate_wc_api_call(request, PREFIX, 'ba', instance)
    return battery.state


# Load Shedding
@router.get("/ls/{instance}/state")
async def get_load_shedding_state(request: Request, instance: int = 1):
    load_shedding = await validate_wc_api_call(request, PREFIX, 'ls', instance)
    return load_shedding.state


# NOTE: Setting not needed right now
# @router.put("/ls/{instance}/state")
# async def set_load_shedding_state(request: Request, instance: int):
#     load_shedding = await validate_wc_api_call(request, PREFIX, 'ls', instance)
#     return load_shedding.state


@router.get("/schemas")
async def get_schemas(include=None):
    all_schemas = {
        "SIMPLE_ONOFF": SimpleOnOff.schema(),
        "BMS_LITHIONICS": BMSLithionics.schema(),
        "SIMPLE_INVERTER_METERED": SimpleInverterMeteredState.schema(),
        # 'SIMPLE_INVERTER_METERED_CONTROL': SimpleOnOff.schema(),
        "SIMPLE_INPUT_SOLAR": SimplePowerState.schema(),
        "SOURCE_PRO_POWER": SimplePowerState.schema(),
        # 'SOURCE_PRO_POWER_CONTROL': ProPowerControl.schema(),
        "SOURCE_EV_SHORE": EVShoreState.schema(),
        # 'SOURCE_EV_SHORE_CONTROL': EVShoreControl.schema(),
        "DC_CONSUMER": Consumer.schema(),
        "AC_CONSUMER": Consumer.schema(),
        "ENERGY_ZONE": None,
        "LITHIONICS_LI_ION": None,
    }

    schemas = {}

    if include is not None:
        include_list = include.split(",")
        for s in include_list:
            schemas[s.upper()] = all_schemas.get(s.upper())
        return schemas

    return all_schemas
