import os
import sys
import logging
from datetime import datetime, timedelta
import subprocess
import json
import asyncio
from copy import deepcopy

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import *
import time

import pytest
from common_libs.models.common import EventValues


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,29J'
            }
        )
        yield c


# Load Shedding Step 1 - Shed first
# Load Shedding Step 2 - Shed Second
# Load Sh

COOKTOP_CIRCUIT = 24
MICROWAVE_CIRCUIT = 23


def test_loadshedding_basics(client):
    '''Test the shedding of the AC via turning thermostat off.'''
    # Set desired thermostat mode
    tstat = {
        "onOff": 1,
        "setTempHeat": 65,
        "setTempCool": 75,
        "setMode": EventValues.COOL,
        "unit": "F"
    }

    response = client.put("/api/climate/th/1/state", json=tstat)


    assert response.status_code == 200
    # Set Load to ~1000 watts
    msg = deepcopy(ENERGY_INVERTER_OVERLOAD)
    msg['RMS_Current'] = "9.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 1080
    assert response.json().get('overld') == EventValues.FALSE

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.FALSE

    # Set load to 2400
    msg['RMS_Current'] = "20.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 2400
    assert response.json().get('overld') == EventValues.TRUE

    time.sleep(6)
    # send overload again
    send_can_response = send_a_can_event(client, msg)
    assert send_can_response.status_code == 200

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.TRUE

    # Send temperature to see that thermostat is off
    _ = send_a_can_event(client, INTERIOR_HOT)
    th_response = client.get('/api/climate/th/1/state')
    assert th_response.json().get('onOff') == EventValues.OFF

    # Set below 2000
    msg['RMS_Current'] = "5.0"

    send_can_response = send_a_can_event(client, msg)
    assert send_can_response.status_code == 200

    # Get inverter load and check it is not in overld anymore
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 600
    assert response.json().get('overld') == EventValues.FALSE

    assert send_a_can_event(client, msg).status_code == 200

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.TRUE

    # Resend to test second cycle clears locks
    msg['RMS_Current'] = "5.0"
    time.sleep(10)
    # send clear again
    assert send_a_can_event(client, msg).status_code == 200

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.FALSE

    # Check that thermostat is back on
    # Send temperature to see that thermostat is off
    assert send_a_can_event(client, INTERIOR_HOT).status_code == 200

    th_response = client.get('/api/climate/th/1/state')
    assert th_response.json().get('onOff') == tstat.get('onOff')

    tstat = {
        "onOff": 1,
        "setTempHeat": 65,
        "setTempCool": 75,
        "setMode": EventValues.COOL,
        "unit": "F"
    }

    response = client.get("/api/climate/th/1/state")

    assert response.status_code == 200

    response = client.put("/api/climate/th/1/state", json=tstat)

    assert response.status_code == 200

    response = client.get(
        "/api/climate/th/1/state", params={"unit": "F"}
    )

    print(f"TSTAT State Response {response.json()}")
    assert response.status_code == 200
    assert response.json().get("setTempHeat") == 65


def ac_helper_set_to_cool(client):

    tstat = {
        "onOff": 1,
        "setTempHeat": 65,
        "setTempCool": 75,
        "setMode": EventValues.COOL,
        "unit": "F"
    }

    response = client.get("/api/climate/th/1/state")

    assert response.status_code == 200

    response = client.put("/api/climate/th/1/state", json=tstat)

    assert response.status_code == 200

    # Indoor
    tempurature_msg = {
        "Instance": "2",
        "Ambient_Temp": "30",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, tempurature_msg)
    response = client.get(
        "/api/climate/th/1/state", params={"unit": "F"}
    )
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 86
    assert response.json().get("mode") == EventValues.COOL


def test_loadshedding_ac(client):
    '''Test the shedding of the AC via turning thermostat off.'''

    # enable AC
    ac_helper_set_to_cool(client)

    # Set Load to ~1000 watts
    msg = deepcopy(ENERGY_INVERTER_OVERLOAD)
    msg['RMS_Current'] = "9.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 1080
    assert response.json().get('overld') == EventValues.FALSE

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.FALSE

    # Set load to 2400
    msg['RMS_Current'] = "20.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    time.sleep(6)
    # send overload again
    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 2400
    assert response.json().get('overld') == EventValues.TRUE

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.TRUE
    #assert 'climate.ac1' in response.json().get('shedComps')

    # Trigger thermostat to run
    # Indoor
    temperature_msg = {
        "Instance": "2",
        "Ambient_Temp": "30",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, temperature_msg)
    response = send_a_can_event(client, temperature_msg)

    # Verify AC in standby
    response = client.get(
        "/api/climate/th/1/state", params={"unit": "F"}
    )
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 86
    assert response.json().get("mode") == EventValues.STANDBY
    # Set below 2000
    msg['RMS_Current'] = "5.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load and check it is not in overld anymore
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 600
    assert response.json().get('overld') == EventValues.FALSE

    # Resend to test second cycle clears locks
    msg['RMS_Current'] = "5.0"
    time.sleep(10)

    response = send_a_can_event(client, msg)
    assert response.status_code == 200
    response = send_a_can_event(client, temperature_msg)

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.FALSE

    response = send_a_can_event(client, temperature_msg)
    response = send_a_can_event(client, temperature_msg)

    # Verify AC stays in Standby
    response = client.get(
        "/api/climate/th/1/state", params={"unit": "F"}
    )
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 86
    assert response.json().get("mode") == EventValues.COOL
    assert response.json().get("onOff") == EventValues.ON


def test_loadshedding_cooktop(client):
    '''Test the shedding of the AC via turning thermostat off.'''

    # enable AC
    ac_helper_set_to_cool(client)

    # Set Load to ~1000 watts
    msg = deepcopy(ENERGY_INVERTER_OVERLOAD)
    msg['RMS_Current'] = "9.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 1080
    assert response.json().get('overld') == EventValues.FALSE

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.FALSE

    # Set load to 2400
    msg['RMS_Current'] = "20.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    time.sleep(6)
    # send overload again
    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 2400
    assert response.json().get('overld') == EventValues.TRUE

    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.TRUE

    # TODO: Figure out how
    # time.sleep(2)
    # # Check circuit state as well
    # response = client.get(f'/api/electrical/dc/{COOKTOP_CIRCUIT}')
    # print(response.json())
    # assert response.status_code == 200
    # assert response.json().get('onOff') == 1

    # Trigger thermostat to run
    # Indoor
    temperature_msg = {
        "Instance": "2",
        "Ambient_Temp": "30",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, temperature_msg)
    response = send_a_can_event(client, temperature_msg)

    # Verify AC in standby
    response = client.get(
        "/api/climate/th/1/state", params={"unit": "F"}
    )
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 86
    assert response.json().get("mode") == EventValues.STANDBY

    # overload for cooktop now

    time.sleep(6)
    # send overload again
    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Check load shedding state
    response = client.get('/api/energy/ls/2/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.TRUE


    time.sleep(10)

    # Set below 2000
    msg['RMS_Current'] = "5.0"

    response = send_a_can_event(client, msg)
    assert response.status_code == 200

    # Get inverter load and check it is not in overld anymore
    response = client.get('/api/energy/ei/1/state')
    assert response.status_code == 200
    assert response.json().get('load') == 600
    assert response.json().get('overld') == EventValues.FALSE

    # Resend to test second cycle clears locks
    msg['RMS_Current'] = "5.0"
    time.sleep(10)

    response = send_a_can_event(client, msg)
    assert response.status_code == 200
    response = send_a_can_event(client, temperature_msg)

    msg['RMS_Current'] = "5.0"
    time.sleep(10)

    response = send_a_can_event(client, msg)
    assert response.status_code == 200
    # Check load shedding state
    response = client.get('/api/energy/ls/1/state')
    assert response.status_code == 200
    assert response.json().get('active') == EventValues.FALSE

    response = send_a_can_event(client, temperature_msg)
    response = send_a_can_event(client, temperature_msg)

    # Verify AC stays in Standby
    response = client.get(
        "/api/climate/th/1/state", params={"unit": "F"}
    )
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 86
    assert response.json().get("mode") == EventValues.COOL
    assert response.json().get("onOff") == EventValues.ON
