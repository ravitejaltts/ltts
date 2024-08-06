import os
import sys
import logging
import time

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

import pytest
from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event

from common_libs.models.common import EventValues



PROPANE_FULL = {
    "title": 'Fuel Tank - LP - 100 %',
    "Instance": 4,
    "Fluid_Type": "PROPANE",
    "Fluid_Level": str(100),
    # "Tank_Capacity": "0.1136",
    # "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}

PROPANE_EMPTY = {
    "title": 'Fuel Tank - LP - 0 %',
    "Instance": 4,
    "Fluid_Type": "PROPANE",
    "Fluid_Level": str(0),
    # "Tank_Capacity": "0.1136",
    # "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}

PROPANE_HALF = {
    "title": 'Fuel Tank - LP - 50 %',
    "Instance": 4,
    "Fluid_Type": "PROPANE",
    "Fluid_Level": str(50),
    # "Tank_Capacity": "0.1136",
    # "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}


# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     return
#     logger.debug("Changing Floorplan to 848EC")
#     subprocess.call(["sed -i -e 's/WM524T/848EC/g' /storage/UI_config.ini"], shell=True)


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,52N,29J'
            }
        )
        yield c


#subprocess.run(["sed -i -e 's/848EC/WM524T/g' /storage/UI_config.ini"], shell=True, check=True)
#time.sleep(5)

# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print("Changing Floorplan to WM524T")
#     logger.debug("Changing Floorplan to WM524T")
#     subprocess.run(["sed -i -e 's/848EC/WM524T/g' /storage/UI_config.ini"], shell=True, check=True)


# def test_bm_for_WM524T(client):
#     # TODO send a Battery temp
#     # This is the wrong message to test BMS
#     msg = {
#         "Instance": "1",
#         "Battery_Voltage": "13.780000000000001",
#         "Battery_Current": "160.0",
#         "Sequence_ID": "0",
#         "name": "Battery_Status",
#     }

#     response = send_a_can_event(client, msg)

#     response = client.get("/api/energy/bm/1/state")
#     assert response.status_code == 200
#     print(f"Full State Response {response.json()}")

#     assert response.json().get("vltg") is not None
#     assert response.json().get("vltg") == 13.780000000000001

#     assert response.json().get("dcCur") is not None
#     assert response.json().get("dcCur") == 160.0


def test_bm_voltage_for_WM524T(client):
    # TODO send a Battery temp
    # This is the wrong message to test BMS
    # DC_Instance here is a strong based on the rvc.dbc value definition
    # VAL_ 2181037312 DC_Instance
    # 0 "Invalid"
    # 1 "Main House Battery Bank"
    # 2 "Chassis Start Battery"
    # 3 "Secondary House Battery Bank"
    # 4 "Generator Starter Battery"
    # 5 "Arbitrary";

    msg = {
        "Instance": "1",
        "DC_Voltage": "13.780000000000001",
        "DC_Current": "160.0",
        "name": "DC_SOURCE_STATUS_1",
    }

    response = send_a_can_event(client, msg)

    response = client.get("/api/energy/bm/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("vltg") == 13.780000000000001
    assert response.json().get("dcCur") == 160.0

    # Setting voltage to exceed limit to test validation
    msg['DC_Voltage'] = str(1001.1)
    response = send_a_can_event(client, msg)

    response = client.get("/api/energy/bm/1/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get("vltg") is not None
    # Value should remain the same as set above
    assert response.json().get("vltg") == 13.780000000000001


def test_get_energy_source_solar_state(client):
    SOLAR_ID = 1
    response = client.get(f"api/energy/es/{SOLAR_ID}/state")
    assert response.status_code == 200


def test_get_energy_source_shore_state(client):
    SHORE_ID = 2
    response = client.get(f"api/energy/es/{SHORE_ID}/state")
    assert response.status_code == 200


def test_get_energy_source_vehicle_state(client):
    VEHICLE_ID = 3
    response = client.get(f"api/energy/es/{VEHICLE_ID}/state")
    assert response.status_code == 200


def test_get_energy_consumer_states(client):
    CONSUMER_COUNT = 1

    for i in range(1, 1 + CONSUMER_COUNT):
        response = client.get(f"/api/energy/ec/{i}/state")
        assert response.status_code == 200


def test_get_generator_state(client):
    response = client.get(f"/api/energy/ge/1/state")
    assert response.status_code == 200


@pytest.mark.skip('Need to define if the default lockouts are set or not, or create preconditions for this lockout')
def test_generator_default_lockout_states(client):
    response = client.get(f"/api/energy/ge/1/state")
    assert response.status_code == 200
    # Test default lockouts being engaged
    response = client.put(
        "/api/energy/ge/1/state",
        json={
            'mode': EventValues.RUN
        }
    )
    assert response.status_code == 423


@pytest.mark.skip(reason='New RVMP LP generator has no PRIME circuit we support')
def test_generator_no_lockout_state_priming(client):
    '''Test to ensure transition from OFF to PRIME to OFF works.'''
    headers = {'source': 'hmi'}
    response = client.get(f"/api/energy/ge/1/state")
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.OFF

    # Report fuel level OK
    response = send_a_can_event(client, PROPANE_FULL)

    response = client.put(
        'api/energy/ge/1/state',
        json={
            'mode': EventValues.PRIME
        },
        headers=headers
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.PRIME

    # Resend prime as dead man switch would do
    response = client.put(
        'api/energy/ge/1/state',
        json={
            'mode': EventValues.PRIME
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.PRIME

    # Set to off
    response = client.put(
        'api/energy/ge/1/state',
        json={
            'mode': EventValues.OFF
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.OFF


@pytest.mark.skip(reason='Revamp logic for this based on new requirements')
def test_generator_no_lockout_state_starting(client):
    response = client.get(f"/api/energy/ge/1/state")
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.OFF

    # Report fuel level OK
    response = send_a_can_event(client, PROPANE_FULL)

    response = client.put(
        'api/energy/ge/1/state',
        json={
            'mode': EventValues.RUN
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.STARTING

    msg = {
        "Manufacturer_Code": "BEP Marine",
        "Dipswitch": "128",
        "Instance": "4",
        "Output13": '1',
        "name": "RvSwitch",
    }

    response = client.get('/api/energy/ge/1/state')
    assert response.status_code == 200
    print("Generator", response.json())
    assert response.json().get('mode') == EventValues.STARTING

    time.sleep(5)  # Might want to skip this text for speed after confirming it works
    response = send_a_can_event(client, msg)

    response = client.get('/api/energy/ge/1/state')
    assert response.status_code == 200
    print("Generator II", response.json())
    assert response.json().get('mode') == EventValues.RUN

    response = client.put(
        'api/energy/ge/1/state',
        json={
            'mode': EventValues.OFF
        }
    )
    print(response.json())
    assert response.status_code == 200


@pytest.mark.skip(reason='Generator start/stop is permitted remote/far field')
def test_generator_farfield_state_starting(client):
    response = client.get('/api/energy/ge/1/state')
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.OFF

    # Report fuel level OK
    response = send_a_can_event(client, PROPANE_FULL)

    response = client.put(
        'api/energy/ge/1/state',
        json={
            'mode': EventValues.RUN
        },
        headers={"source": "platform"}
    )
    print(response.json())
    assert response.status_code == 403


@pytest.mark.skip(reason='Revamp logic for this based on new requirements')
def test_generator_no_lockout_state_stop(client):
    '''Also check we can stop farfield'''
    response = client.get(f"/api/energy/ge/1/state")
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.OFF

    # Report fuel level OK
    response = send_a_can_event(client, PROPANE_FULL)

    response = client.put(
        'api/energy/ge/1/state',
        json={
            'mode': EventValues.OFF
        },
        headers={"source": "platform"}
    )
    print(response.json())
    assert response.json().get('mode') == EventValues.OFF
    assert response.status_code == 200


def test_inverter_state(client):
    response = client.get(f"api/energy/ei/1/state")
    print('Initial GET state', response.json())
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.OFF

    response = client.put(
        f"api/energy/ei/1/state",
        json={
            'onOff': EventValues.ON
        }
    )
    print('PUT response state', response.json())
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.ON

    response = client.put(
        f"api/energy/ei/1/state",
        json={
            'onOff': EventValues.OFF
        }
    )
    print('PUT response state', response.json())
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.OFF


def test_inverter_overload(client):
    # Check that it is not in overload
    response = client.get(f"/api/energy/ei/1/state")
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.OFF
    # NOTE: Initial load changed to None, no inital value set to differentiate
    # between nothing received yet and actual 0
    assert response.json().get('load') is None
    assert response.json().get('overld') == EventValues.FALSE
    # NOTE: Initial load changed to None, no inital value set to differentiate
    # between nothing received yet and actual 0
    assert response.json().get('overldTimer') is None

    # Set a state to show it is in overload
    msg = {
        "Instance": "65",
        "RMS_Voltage": "120",
        "RMS_Current": "20",
        "Frequency": "60",
        "name": "INVERTER_AC_STATUS_1",
    }

    response = send_a_can_event(client, msg)

    # Check that it reports overload
    # Check that a timer is provided
    response = client.get(f"api/energy/ei/1/state")
    print('Overload STATE', response.json())
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.OFF
    assert response.json().get('load') == 2400
    assert response.json().get('overld') == EventValues.TRUE
    overload_timer = response.json().get('overldTimer')
    assert overload_timer != 0

    send_a_can_event(client, msg)
    response = client.get(f"api/energy/ei/1/state")
    assert overload_timer == response.json().get('overldTimer')

    # Check that load shedding applies
    # Get affected components and check if lockout it report
    # Set it to be under overload

    msg['RMS_Current'] = 10
    send_a_can_event(client, msg)
    response = client.get(f"api/energy/ei/1/state")
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.OFF
    assert response.json().get('load') == 1200
    assert response.json().get('overld') == EventValues.FALSE
    assert response.json().get('overldTimer') == 0


def test_get_inverter_state(client):
    response = client.get(f"api/energy/ei/1/state")
    assert response.status_code == 200


def test_get_fuel_tank_state(client):
    response = client.get(f"api/energy/ft/1/state")
    assert response.status_code == 200


def test_get_energy_state(client):
    response = client.get(f"api/energy/state")

    assert response.status_code == 200

    assert response.json().get('bm1') is not None
    assert response.json().get('ei1') is not None
    assert response.json().get('es1') is not None
    assert response.json().get('es2') is not None
    assert response.json().get('es3') is not None
    assert response.json().get('ge1') is not None
    assert response.json().get('ec1') is not None



def test_battery_temp(client):
    msg = {
        'Instance': '1',
        'Cells_Temp': '30',
        'name': 'PROP_MODULE_STATUS_1',
        }

    response = send_a_can_event(client, msg)

    response = client.get(f"/api/energy/ba/1/state")

    assert response.status_code == 200
    assert response.json().get('temp') == 30


# def test_setup_for_848EC(client):


#     return

#     print("Changing Floorplan to 848EC")
#     logger.debug("Changing Floorplan to 848EC")
#     subprocess.call(["sed -i -e 's/WM524T/848EC/g' /storage/UI_config.ini"], shell=True)


# #ENERGYMANAGEMENT
