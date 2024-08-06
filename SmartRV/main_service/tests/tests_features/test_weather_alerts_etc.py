import os
import sys
import logging
from datetime import datetime
import subprocess
import asyncio

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
import pytest

from main_service.wgo_main_service import app

from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import INTERIOR_HOT, INTERIOR_COLD
from common_libs.models.common import RVEvents, EventValues


BASE_URL = '/api/features/wx/'

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def client():
    with TestClient(app) as c:
        # Get current floorplan and options and save
        current_floorplan = c.get(
            '/api/system/floorplan'
        ).json()
        current_optioncodes = c.get(
            '/api/system/optioncodes'
        ).json()
        current_optioncodes = ','.join(current_optioncodes)
        print('PyTest Client Current Floorplan', current_floorplan, current_optioncodes)
        # Put floorplan
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,52N,33F,31P,33F,29J'
            }
        )
        yield c
        # Reset floorplan and options
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': current_floorplan,
                'optionCodes': current_optioncodes
            }
        )


def test_wx_defaults(client):
    # msg = {
    #     "Instance": "1",
    #     "Position": "10",
    #     "Motion": "No motion",
    #     "name": "Awning_Status"
    # }

    # response = send_a_can_event(client, msg)

    response = client.get(BASE_URL + '1/state')
    assert response.status_code == 200

    print('RESPONSE WX', response.json())

    assert response.json().get("onOff") is not None
    assert response.json().get("inMtnTimer") == 15
    assert response.json().get("trvlDist") == 60
    assert response.json().get("process") == 0


CH_URL = '/api/vehicle/ch/'


def test_get_ch(client):
    '''Test for position'''

    response = client.get(CH_URL + '2/state')
    assert response.status_code == 200

    print('RESPONSE CH', response.json())

    assert response.json().get("pos") is not None


def test_alerts_process(client):

    response = client.put('/api/features/wx/1/alerts/process')
    assert response.status_code == 200


in_dev = pytest.mark.skip(
    reason="Refactor needed to pass tests on any platform"
)

@in_dev
@pytest.mark.asyncio
async def test_alerts_expire(client):

    # Insert Weather Alert
    wx_alert = {
        "event": "High Wind Warning",
        "startTime": "2023-12-11T14:38:00+00:00",
        "endTime": "2023-12-11T22:45:00+00:00",
        "headline": "High Wind Warning issued December 11 at 9:38AM EST until December 11 at 7:00PM EST by NWS Caribou ME",
        "description": "* WHAT...Southwest winds 15 to 25 mph with gusts up to 60 mph.\n\n* WHERE...Central Washington, Coastal Hancock and Coastal\nWashington Counties.\n\n* WHEN...Until 7 PM EST this evening.\n\n* IMPACTS...Damaging winds will blow down trees and power lines.\nWidespread power outages are expected. Travel will be\ndifficult, especially for high profile vehicles.",
        "instruction": "People should avoid being outside in forested areas and around\ntrees and branches. If possible, remain in the lower levels of\nyour home during the windstorm, and avoid windows. Use caution if\nyou must drive.",
        "area": "Central Washington; Coastal Hancock; Coastal Washington",
        "severity": "Severe",
        "certainty": "Likely",
        "urgency": "Expected",
        "issuer": {
            "name": "NWS Caribou ME",
            "email": "w-nws.webmaster@noaa.gov"
        }
    }

    response = client.put('/api/features/wx/1/alert',
                          json=wx_alert)
    assert response.status_code == 200
    await asyncio.sleep(1)

    # check for alert

    response = client.get('/ui/notifications',)
    assert response.status_code == 200

    print(f"\n\n\nWeather Test {response.json()} \n\n\n")

    found_HWW = False
    for item in response.json():
        if item.get('ecode') == 'HIGH_WIND_WARNING':
            found_HWW = True
    assert found_HWW is True
    # run check function - alert should be stale

    response = client.put('/api/features/wx/1/alerts/checktimeout',
                          json={})
    assert response.status_code == 200

    # check alert not present

    response = client.get('/ui/notifications',)
    assert response.status_code == 200

    print(f"\n\n\nWeather Test {response.json()} \n\n\n")

    found_HWW = False
    for item in response.json():
        if item.get('ecode') == 'HIGH_WIND_WARNING':
            found_HWW = True
    assert found_HWW is False
