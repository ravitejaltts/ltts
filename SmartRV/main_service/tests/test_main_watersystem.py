
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from common_libs.models.common import EventValues
from main_service.tests.utils import send_a_can_event

import pytest


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
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,291'
            }
        )
        yield c


def test_get_watersystems_settings(client):
    response = client.get(f'/api/watersystems/settings')
    assert response.status_code == 200


def test_put_watersystems_settings(client):
    return
    response = client.put('/api/watersystems/settings', json ={"item": 0, "value": "VolumeUnitPreference"} )
    assert response.status_code == 200


# def test_get_watersystem_schema(client):
#     response = client.get('/api/watersystems/schemas')
#     assert response.status_code == 200


def test_bug_14232_water_heater_no_turning_off(client):
    # Set to 524T
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': '52D,33F,31P,33F,29J'
        }
    )

    # Set mode to COMFORT
    can_msg = {
        "name": "waterheater_status_2",
        "Instance": "1",
        "Heat_Level": "High level (COMFORT)"
    }
    result = send_a_can_event(client, can_msg)
    # Get current wh state
    response = client.get('/api/watersystems/wh/1/state')
    assert response.status_code == 200
    # TODO: Send another mock message for water heater status 1 for on
    # assert response.json().get('onOff') == EventValues.OFF

    assert response.json().get('mode') == EventValues.COMFORT

    del response

    response = client.put(
        '/api/watersystems/wh/1/state',
        json={
            'onOff': EventValues.ON
        }
    )
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data.get('onOff') == EventValues.ON
    assert data.get('mode') == EventValues.COMFORT

    # TODO: Add check to the can log, latest sent message shall be
    # cansend canb0s0 19FFF644#0100FFFF00000F00
