import os
import sys
import logging
import time

logger = logging.getLogger(__name__)

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


def test_service_settings(client):
    '''Tests the effectiveness of service mode when set.'''
    response = client.get('/api/system/us/1/state')
    assert response.json().get('fcpEnabled') == EventValues.OFF
    assert response.json().get('serviceModeOnOff') == EventValues.OFF
    assert response.json().get('systemMode') == EventValues.SYSTEM_MODE_USER

    set_response = client.put(
        '/api/system/us/1/state',
        json={
            'serviceModeOnOff': EventValues.ON
        }
    )

    assert set_response.status_code == 200
    assert set_response.json().get('serviceModeOnOff') == EventValues.ON

    # Perform a GET and a PUT as BLE and platform each
    get_response = client.get('/api/watersystems/wp/1/state', headers={'source': 'platform'})
    assert get_response.status_code == 200

    put_response = client.put(
        '/api/watersystems/wp/1/state',
        json={
            'onOff': EventValues.ON
        },
        headers={
            'source': 'BLE'
        }
    )
    assert put_response.status_code == 423

    put_response = client.put(
        '/api/watersystems/wp/1/state',
        json={
            'onOff': EventValues.ON
        },
        headers={
            'source': 'platform'
        }
    )
    assert put_response.status_code == 423

    set_response = client.put(
        '/api/system/us/1/state',
        json={
            'serviceModeOnOff': EventValues.OFF
        }
    )

    assert set_response.status_code == 200
    assert set_response.json().get('serviceModeOnOff') == EventValues.OFF

    put_response = client.put(
        '/api/watersystems/wp/1/state',
        json={
            'onOff': EventValues.ON
        },
        headers={
            'source': 'BLE'
        }
    )
    assert put_response.status_code == 200

    put_response = client.put(
        '/api/watersystems/wp/1/state',
        json={
            'onOff': EventValues.OFF
        },
        headers={
            'source': 'platform'
        }
    )
    assert put_response.status_code == 200
