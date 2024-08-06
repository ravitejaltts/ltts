from main_service.tests.can_messages import (
    INVALID_TEMP,
    INTERIOR_HOT,
    UNKOWN_TEMP,
    FRIDGE_IN_RANGE,
    FRIDGE_ROUND_DOWN_TEMP,
    FRIDGE_ROUND_UP_TEMP,
    INTERIOR_INVALID,
)
from main_service.tests.utils import send_a_can_event
from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)
from main_service.wgo_main_service import app
from fastapi.testclient import TestClient
import os
import sys
import logging
import pytest
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)


# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print("Changing Floorplan to WM524T")
#     logger.debug("Changing Floorplan to WM524T")
#     subprocess.call(["sed -i -e 's/848EC/WM524T/g' /storage/UI_config.ini"], shell=True)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_get_climate_th1(client):
    instance = 1
    response = client.get(f"api/climate/th/{instance}/state")
    assert response.status_code == 200


# # climate related api's
# def test_get_climate_response(client):
#     # Set floorplan to 524T
#     client.put('/api/system/floorplan',
#                json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,29J'})
#     response = client.get("api/climate")
#     assert response.status_code == 200


def test_set_thermostat_state(client):
    instance = 1
    response = client.put(
        f"api/climate/zones/{instance}/thermostat/state",
        json={
            "mode": 519,
            "onOff": 1,
            "unit": "F",
            "setTempCool": 72,
            "setTempHeat": 67,
        },
    )
    assert response.status_code == 200
    state = response.json()
    assert state.get("unit") == "F"


def test_set_th1_state(client):
    instance = 1

    response = client.put(
        f"api/climate/th/{instance}/state",
        json={
            "mode": EventValues.AUTO,
            "onOff": 1,
            "unit": "C",
            "setTempCool": 30,
            "setTempHeat": 25,
        },
    )
    assert response.status_code == 200
    state = response.json()
    assert state.get("unit") == "C"
    assert state.get("setTempCool") == 30

    response = client.get(
        f"api/climate/th/{instance}/state?unit=F"
    )
    assert response.status_code == 200
    state = response.json()
    assert state.get("unit") == "F"
    assert state.get("setTempCool") == 86

    response = client.put(
        f"api/climate/th/{instance}/state",
        json={
            "mode": EventValues.AUTO,
            "onOff": 1,
            "unit": "C",
            "setTempCool": 30,
            "setTempHeat": 25,
        },
    )
    assert response.status_code == 200
    state = response.json()
    assert state.get("unit") == "C"
    assert state.get("setTempCool") == 30


    response = client.get(
        f"api/climate/th/{instance}/state?unit=F"
    )
    assert response.status_code == 200
    state = response.json()
    assert state.get("unit") == "F"
    assert state.get("setTempCool") == 86


@pytest.mark.skip(reason='Test needs refactoring due to the change to "C" as the default unit if not unit is given')
def test_th_unit_pref(client):
    instance = 1
    response = client.put(
        f"api/climate/settings",
        json={
            "value": "C",
            "item": "TempUnitPreference"}
    )
    assert response.status_code == 200

    response = client.get(
        f"api/climate/th/{instance}/state"
    )
    assert response.status_code == 200
    state = response.json()
    assert state.get("unit") == "C"

    response = client.put(
        f"api/climate/settings",
        json={
            "value": "F",
            "item": "TempUnitPreference"
        }

    )
    assert response.status_code == 200

    response = client.get(
        f"api/climate/th/{instance}/state"
    )
    assert response.status_code == 200
    state = response.json()
    assert state.get("unit") == "F"


def test_set_zone_temp(client):
    instance = 1
    response = client.put(
        f"api/climate/zones/{instance}/temp", json={"mode": "HEAT", "setTemp": 74, "unit": "F"}
    )
    assert response.status_code == 200




def test_set_zone_schedule(client):
    return
    zone_id = 1
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put(
            f"api/climate/zones/{zone_id}/schedule/onoff", json={"onOff": onOff}
        )
        assert response.status_code == 200


def test_set_clear_zone(client):
    return
    zone_id = 1
    response = client.put(f"api/climate/zones/{zone_id}/schedule/clear")
    assert response.status_code == 200


def test_get_rooffan_zone_state(client):
    zone_id = 1
    fan_id = 1
    response = client.get(f"api/climate/rv/{fan_id}/state")
    assert response.status_code == 200


def test_non_existing_thermostat(client):
    '''Test a non existing thermostat being handled properly as 404.'''
    instance = 789
    response = client.put(
        f'/api/climate/th/{instance}/state',
        json={}
    )
    assert response.status_code == 404


@pytest.mark.skip(reason='No longer a valid test/bug as behavior was changed to support heating when temp actually is 0F and below')
def test_bug_10268_safety_check_fails_to_turn_off(client):
    '''
    Tests
    https://dev.azure.com/WGO-Web-Development/SmartRV/_workitems/edit/10268
    '''
    # Set floorplan to 524T
    client.put('/api/system/floorplan',
               json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,291'})

    # Set Thermostat to on and mode to AUTO
    # TODO: This was blocking before adding unit etc.
    response = client.put(
        '/api/climate/th/1/state',
        json={
            "setMode": EventValues.AUTO,
            "onOff": EventValues.ON,
            "unit": "F",
            "setTempCool": 72,
            "setTempHeat": 67,
        }
    )
    assert response.status_code == 200
    assert response.json().get('setMode') == EventValues.AUTO

    # Set hot interior temp
    send_a_can_event(client, INTERIOR_HOT)
    response = client.get(
        '/api/climate/he/1/state'
    )
    print('Response', response.json())
    assert response.status_code == 200
    assert response.json().get('onOff') == 0

    response = client.get(
        '/api/climate/ac/1/state'
    )
    print('Response', response.json())
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('comp') == 1

    # Inject error / None temp

    INVALID_TEMP["Instance"] = "2"  # 500 series interior temp module
    send_a_can_event(client, INVALID_TEMP)

    response = client.get(
        '/api/climate/he/1/state'
    )
    print('Response', response.json())
    assert response.status_code == 200
    assert response.json().get('onOff') == 1

    response = client.get(
        '/api/climate/ac/1/state'
    )
    print('Response', response.json())
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('comp') == 0


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_bug_12088_refrigerator_invalid_data_handled_as_number(client):
    # Send data invalid
    send_a_can_event(client, UNKOWN_TEMP)
    # Test fridge temp is None
    response = client.get(
        '/api/climate/rf/1/state'
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('temp') is None

    send_a_can_event(client, FRIDGE_IN_RANGE)
    response = client.get(
        '/api/climate/rf/1/state'
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('temp') == float(FRIDGE_IN_RANGE.get('Ambient_Temp'))

    send_a_can_event(client, UNKOWN_TEMP)
    # Test fridge temp is None
    response = client.get(
        '/api/climate/rf/1/state'
    )

    assert response.status_code == 200
    print(response.json())
    assert response.json().get('temp') is None


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_new_rounding_on_fridge(client):
    # Send data invalid
    send_a_can_event(client, FRIDGE_ROUND_UP_TEMP)
    # Test fridge temp is None
    response = client.get(
        '/api/climate/rf/1/state'
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('temp') == 2.5

    send_a_can_event(client, FRIDGE_ROUND_DOWN_TEMP)
    response = client.get(
        '/api/climate/rf/1/state'
    )
    assert response.status_code == 200
    print('New 2.4 response', response.json())
    print(app.hal.climate.handler.refrigerator[1])
    # This consideres that the lwoer level rounds to halb celsius numbers
    assert response.json().get('temp') == 2.5


def test_data_invalid_thermostat(client):
    '''
    Test that thermostat does not turn off on a Data Invalid from dometic gateway
    '''
    # Set floorplan to 524T
    client.put('/api/system/floorplan',
               json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,291'})

    # Set Thermostat to on and mode to AUTO
    response = client.put(
        '/api/climate/th/1/state',
        json={
            "setMode": EventValues.AUTO,
            "onOff": EventValues.ON,
            "unit": "F",
            "setTempCool": 72,
            "setTempHeat": 67,
        }
    )
    assert response.status_code == 200
    assert response.json().get('setMode') == EventValues.AUTO

    # Set hot interior temp
    send_a_can_event(client, INTERIOR_INVALID)

    response = client.get(
        '/api/climate/th/1/state'
    )
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.ON




def test_cool_increment_thermostat(client):
    '''
    Test that thermostat incrementing cool does not raise heat setting
    '''
    # Set floorplan to 524T
    client.put('/api/system/floorplan',
               json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,291'})

    # Set Thermostat to on and mode to AUTO
    response = client.put(
        '/api/climate/th/1/state',
        json={
            "setMode": EventValues.AUTO,
            "onOff": EventValues.ON,
            "unit": "C",
            "setTempCool": 34,
            "setTempHeat": 25,
        }
    )
    assert response.status_code == 200
    assert response.json().get('setMode') == EventValues.AUTO

    # Set hot interior temp
    send_a_can_event(client, INTERIOR_INVALID)

    response = client.get(
        '/api/climate/th/1/state'
    )
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.ON
    assert response.json().get('setTempCool') == 34
    assert response.json().get('setTempHeat') == 25

     # Set Thermostat to on and mode to AUTO
    response = client.put(
        '/api/climate/th/1/state',
        json={
            "unit": "C",
            "setTempCool": 35,
        }
    )
    assert response.status_code == 200


    response = client.get(
        '/api/climate/th/1/state'
    )
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.ON
    assert response.json().get('setTempCool') == 35
    # The ticket falure where the heat setting was raised should pass now
    assert response.json().get('setTempHeat') == 25
