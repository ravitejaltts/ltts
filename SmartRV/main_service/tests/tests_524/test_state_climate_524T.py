import os
import sys
import logging
from datetime import datetime
import subprocess
import asyncio


import time
import random

from fastapi.testclient import TestClient
import pytest

from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import (
    INTERIOR_HOT,
    INTERIOR_COLD,
    INTERIOR_NORMAL
)
from common_libs.models.common import EventValues

logger = logging.getLogger(__name__)

# with open(os.environ.get('WGO_USER_STORAGE') + 'UI_Config.ini', 'w') as ini_file:
#         ini_file.write(
#             '''[Vehicle]
# floorplan = WM524T'''
#         )

# NOTE: We need to dynamically change these for Truma vs. GE
OPTION_CODES = '52D,33F,31P,33F,29J'
TRUMA_OPTION_CODES = '52D,33F,31P,33F,291'


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': OPTION_CODES
            }
        )
        yield c

# # @pytest.hookimpl()
# # def pytest_sessionstart(session):
# #     print("hello")


# # Plugin 1
@pytest.hookimpl(hookwrapper=True)
def pytest_sessionstart(session):
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': OPTION_CODES
            }
        )
        yield
    print('Pytest Cleanup')
    c.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'VANILLA',
            'optionCodes': ''
        }
    )


def test_th_for_WM524T(client):
    # Indoor
    msg = {
        "Instance": "2",        # Dometic FAN GW dipswitched to 2
        "Ambient_Temp": str(30),    # Celsius
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/th/1/state")
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 30

    # Outdoor
    msg = {
        "Instance": str(0xF9),      # TM-1010 sensor
        "Ambient_Temp": "0",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/th/2/state")
    assert response.status_code == 200
    print(f"Outdoor State Response {response.json()}")

    assert response.json().get("temp") == 0


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_rf_for_WM524T(client):
    msg = {
        "Instance": "55",
        "Ambient_Temp": str(random.randint(1, 4)),
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("rf1").get("temp") is not None


@pytest.mark.skip(reason='Fans currently are stateless until we can figure it out correctly')
def test_rv_for_WM524T(client):
    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("fanSpd") is not None

    response = client.put(
        "/api/climate/rv/1/state",
        json={
            "fanSpd": EventValues.HIGH,
            "dome": EventValues.OPENED,
            "onOff": EventValues.ON
        },
    )
    assert response.status_code == 200

    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("fanSpd") == EventValues.HIGH
    assert response.json().get("dome") == EventValues.OPENED

    response = client.put(
        "/api/climate/rv/1/state",
        json={
            "fanSpd": EventValues.HIGH,
            "dome": EventValues.CLOSED,
            "onOff": EventValues.ON
        },
    )
    assert response.status_code == 200

    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("fanSpd") == EventValues.HIGH
    assert response.json().get("dome") == EventValues.CLOSED

    # Test second roof vent
    response = client.put(
        "/api/climate/rv/2/state",
        json={"fanSpd": EventValues.MEDIUM, "direction": EventValues.FAN_OUT},
    )
    assert response.status_code == 200

    time.sleep(0.25)

    response = client.get('/api/can/history/sent')
    assert response.status_code == 200
    last_request = response.json().get('history_sent', [])
    assert '19FEA644#02' in last_request[-1].get('cmd')[0]

    response = client.get("/api/climate/rv/2/state")
    assert response.status_code == 200
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("fanSpd") == EventValues.MEDIUM
    assert response.json().get("direction") == EventValues.FAN_OUT


def test_rv_for_basic_WM524T(client):
    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("fanSpd") is None
    assert response.json().get("onOff") is None

    response = client.put(
        "/api/climate/rv/1/state",
        json={
            "fanSpd": EventValues.HIGH,
            "onOff": EventValues.ON
        }
    )
    assert response.status_code == 200

    time.sleep(0.25)

    # response = client.get('/api/can/history/sent')
    # assert response.status_code == 200
    # last_request = response.json().get('history_sent')
    # assert '19FEA644#03' in last_request[-1].get('cmd')[0]

    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("fanSpd") == EventValues.HIGH
    assert response.json().get("onOff") == EventValues.ON

    response = client.put(
        "/api/climate/rv/1/state",
        json={
            "dome": EventValues.CLOSED
        }
    )
    assert response.status_code == 200
    assert response.json().get("fanSpd") == EventValues.HIGH
    assert response.json().get("onOff") == EventValues.OFF
    assert response.json().get("dome") == EventValues.CLOSED

    response = client.put(
        "/api/climate/rv/1/state",
        json={
            "dome": EventValues.OPENED
        }
    )
    assert response.status_code == 200
    assert response.json().get("fanSpd") == EventValues.HIGH
    assert response.json().get("onOff") == EventValues.ON
    assert response.json().get("dome") == EventValues.OPENED


def test_rv_can_updates_524(client):
    response = send_a_can_event(
        client,
        {
            'title': 'Set Main FAN- LOW',
            'Instance': '3',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '20.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__3'
        }
    )

    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # System state off mandates 0 speed
    assert response.json().get("fanSpd") == EventValues.OFF
    assert response.json().get("dome") == EventValues.OPENED

    response = send_a_can_event(
        client,
        {
            'title': 'Set Main FAN- LOW',
            'Instance': '3',
            'System_Status': 'On',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '20.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__3'
        }
    )

    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # System state off mandates 0 speed
    assert response.json().get("fanSpd") == EventValues.LOW
    assert response.json().get("dome") == EventValues.OPENED

    response = send_a_can_event(
        client,
        {
            'title': 'Set Main FAN- LOW',
            'Instance': '3',
            'System_Status': 'On',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '100.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Closed',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        }
    )

    response = client.get("/api/climate/rv/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # System state on with dome closed can retain speed ?
    assert response.json().get("fanSpd") == EventValues.HIGH
    assert response.json().get("dome") == EventValues.CLOSED

    response = send_a_can_event(
        client,
        {
            'title': 'Set Main FAN- LOW',
            'Instance': '2',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '20.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__3'
        }
    )

    response = client.get("/api/climate/rv/2/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # System state off mandates 0 speed
    assert response.json().get("fanSpd") == EventValues.OFF
    assert response.json().get("dome") == EventValues.OPENED

    response = send_a_can_event(
        client,
        {
            'title': 'Set Main FAN- LOW',
            'Instance': '2',
            'System_Status': 'On',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '20.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__3'
        }
    )

    response = client.get("/api/climate/rv/2/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # System state off mandates 0 speed
    assert response.json().get("fanSpd") == EventValues.LOW
    assert response.json().get("dome") == EventValues.OPENED

    response = send_a_can_event(
        client,
        {
            'title': 'Set Main FAN- LOW',
            'Instance': '2',
            'System_Status': 'On',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '100.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Closed',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        }
    )

    response = client.get("/api/climate/rv/2/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # System state on with dome closed can retain speed ?
    assert response.json().get("fanSpd") == EventValues.HIGH
    assert response.json().get("dome") == EventValues.CLOSED


def test_ac_for_WM524T(client):
    response = client.get("/api/climate/ac/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # TODO: Fix when clear how to set defaults
    # assert response.json().get("fanSpd") == EventValues.OFF
    assert response.json().get("fanMode") is not None

    response = client.put("/api/climate/ac/1/state", json={
        "fanMode": 52
    })
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # assert response.json().get("fanSpd") == 0
    assert response.json().get("fanMode") == 52

    response = client.get("/api/climate/ac/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    # assert response.json().get("fanSpd") == 0
    assert response.json().get("fanMode") == 52


def test_he_for_WM524T(client):
    response = client.get("/api/climate/he/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("onOff") is not None

    response = client.put("/api/climate/he/1/state", json={"onOff": 1})
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("onOff") == 1

    response = client.get("/api/climate/he/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("onOff") == 1


def test_th_works_for_WM524T(client):

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

    # Indoor
    msg = {
        "Instance": "2",
        "Ambient_Temp": "30",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/th/1/state", params={"unit": "F"})
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 86
    assert response.json().get("mode") == EventValues.COOL


def test_th_failure_handling_WM524T(client):
    tstat = {
        "onOff": EventValues.ON,
        "setTempHeat": 65,
        "setTempCool": 75,
        "setMode": EventValues.AUTO,
        "unit": "F"
    }

    response = client.get("/api/climate/th/1/state")

    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.OFF
    assert response.json().get('mode') == EventValues.OFF

    response = client.put(
        "/api/climate/ac/1/state",
        json={
            'fanMode': EventValues.AUTO_OFF
        }
    )

    response = client.put("/api/climate/th/1/state", json=tstat)


    assert response.status_code == 200
    # Remains off until first reading of a temp
    assert response.json().get('mode') == EventValues.OFF

    response = client.get(
        "/api/climate/th/1/state", params={"unit": "F"}
    )

    assert response.status_code == 200
    assert response.json().get("setTempHeat") == 65

    # Indoor
    msg = {
        "Instance": "2",
        "Ambient_Temp": "30.0",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/th/1/state", params={"unit": "F"})

    print(response.json())
    assert response.status_code == 200
    assert response.json().get("temp") == 86
    assert response.json().get("mode") == EventValues.COOL

    msg = {
        "Instance": "2",
        "Ambient_Temp": "Data Invalid",
        "name": "thermostat_ambient_status",
    }

    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/th/1/state", params={"unit": "F"})
    assert response.status_code == 200
    assert response.json().get("temp") is None
    assert response.json().get("mode") == EventValues.COOL

    msg = {
        "Instance": "2",
        "Ambient_Temp": "-19.4",
        "name": "thermostat_ambient_status",
    }

    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/th/1/state", params={"unit": "F"})
    assert response.status_code == 200
    assert response.json().get("temp") == -3
    assert response.json().get("mode") == EventValues.HEAT


def test_th_ge_ac_source_WM524T(client):
    tstat = {
        "onOff": EventValues.ON,
        "setTempHeat": 65,
        "setTempCool": 75,
        "setMode": EventValues.AUTO,
        "unit": "F"
    }

    response = client.put("/api/climate/th/1/state", json=tstat)

    assert response.status_code == 200

    # Indoor
    msg = {
        "Instance": "2",
        "Ambient_Temp": "0",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, msg)

    # Expect to heat
    response = client.get("/api/climate/th/1/state", params={"unit": "F"})
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 32
    assert response.json().get("mode") == EventValues.HEAT

    heater_2 = client.get('/api/climate/he/2/state')
    assert heater_2.status_code == 200
    assert heater_2.json().get('onOff') == EventValues.ON
    assert heater_2.json().get('heatSrc') == EventValues.ELECTRIC

    heater_1 = client.get('/api/climate/he/1/state')
    assert heater_1.status_code == 200
    assert heater_1.json().get('onOff') == EventValues.OFF

    # Set Heating Source to Propane
    heater_2 = client.put(
        '/api/climate/he/2/state',
        json={
            'heatSrc': EventValues.COMBUSTION
        }
    )
    assert heater_2.status_code == 200
    assert heater_2.json().get('onOff') == EventValues.ON
    assert heater_2.json().get('heatSrc') == EventValues.COMBUSTION

    msg = {
        "Instance": "2",
        "Ambient_Temp": "0",
        "name": "thermostat_ambient_status",
    }
    response = send_a_can_event(client, msg)

    heater_1 = client.get('/api/climate/he/1/state')
    assert heater_1.status_code == 200
    assert heater_1.json().get('onOff') == EventValues.ON

    # NOTE: Auto has been temporarily removed until properly implemented
    # # Set to AUTO
    # heater_2 = client.put(
    #     '/api/climate/he/2/state',
    #     json={
    #         'heatSrc': EventValues.AUTO
    #     }
    # )
    # # assert heater_2.json().get('onOff') == EventValues.ON   ????
    # assert heater_2.json().get('heatSrc') == EventValues.AUTO

    # msg = {
    #     "Instance": "2",
    #     "Ambient_Temp": "0",
    #     "name": "thermostat_ambient_status",
    # }
    # response = send_a_can_event(client, msg)

    # # There is no Propane available if not set, we expect this to be off
    # heater_1 = client.get('/api/climate/he/1/state')
    # assert heater_1.status_code == 200
    # assert heater_1.json().get('onOff') == EventValues.OFF

    # # Set propane available
    # msg = {
    #     "title": "Set Propane to full",
    #     "Instance": "4",
    #     "Fluid_Type": "PROPANE",
    #     "Fluid_Level": "100",
    #     "Tank_Capacity": "0.0795",
    #     "NMEA_Reserved": "255",
    #     "name": "FLUID_LEVEL"
    # }
    # response = send_a_can_event(client, msg)

    # msg = {
    #     "Instance": "2",
    #     "Ambient_Temp": "0",
    #     "name": "thermostat_ambient_status",
    # }
    # response = send_a_can_event(client, msg)

    # heater_1 = client.get('/api/climate/he/1/state')
    # assert heater_1.status_code == 200
    # assert heater_1.json().get('onOff') == EventValues.ON


def test_th_truma_WM524T(client):
    # Set TRUMA optioncodes
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': TRUMA_OPTION_CODES
        }
    )

    # time.sleep(5)

    tstat = {
        "onOff": EventValues.ON,
        "setTempHeat": 65,
        "setTempCool": 75,
        "setMode": EventValues.AUTO,
        "unit": "F"
    }

    response = client.put("/api/climate/th/1/state", json=tstat)

    assert response.status_code == 200

    # Indoor Cold
    msg = {
        "Instance": "2",
        "Ambient_Temp": "0",
        "name": "thermostat_ambient_status"
    }
    response = send_a_can_event(client, msg)

    # Expect to heat
    response = client.get("/api/climate/th/1/state", params={"unit": "F"})
    assert response.status_code == 200
    print(f"Indoor State Response {response.json()}")

    assert response.json().get("temp") == 32
    assert response.json().get("mode") == EventValues.HEAT

    heater_1 = client.get('/api/climate/he/1/state')
    assert heater_1.status_code == 200
    assert heater_1.json().get('onOff') == EventValues.ON

    # Check that AC fan is off
    ac_1 = client.get('/api/climate/ac/1/state')
    assert ac_1.status_code == 200
    assert ac_1.json().get('fanSpd') == EventValues.OFF

    msg = {
        "Instance": "2",
        "Ambient_Temp": "40",
        "name": "thermostat_ambient_status"
    }
    response = send_a_can_event(client, msg)

    heater_1 = client.get('/api/climate/he/1/state')
    assert heater_1.status_code == 200
    assert heater_1.json().get('onOff') == EventValues.OFF

    thermostat = client.get("/api/climate/th/1/state", params={"unit": "F"})
    assert thermostat.status_code == 200
    print(f"Indoor Thermostat State Response {thermostat.json()}")

    assert thermostat.status_code == 200
    assert thermostat.json().get('onOff') == EventValues.ON
    assert thermostat.json().get("mode") == EventValues.COOL

    # Check that AC fan is on HIGH
    ac_1 = client.get('/api/climate/ac/1/state')
    assert ac_1.status_code == 200
    assert ac_1.json().get('fanSpd') == EventValues.HIGH

    # Indoor OK
    msg = {
        "Instance": "2",
        "Ambient_Temp": "20",
        "name": "thermostat_ambient_status"
    }
    response = send_a_can_event(client, msg)

    heater_1 = client.get('/api/climate/he/1/state')
    assert heater_1.status_code == 200
    assert heater_1.json().get('onOff') == EventValues.OFF

    thermostat = client.get("/api/climate/th/1/state", params={"unit": "F"})
    assert thermostat.status_code == 200
    print(f"Indoor Thermostat State Response {thermostat.json()}")

    assert thermostat.status_code == 200
    assert thermostat.json().get('onOff') == EventValues.ON
    assert thermostat.json().get("mode") == EventValues.STANDBY

    # Check that AC fan is OFF
    ac_1 = client.get('/api/climate/ac/1/state')
    assert ac_1.status_code == 200
    assert ac_1.json().get('fanSpd') == EventValues.AUTO_OFF
