import os
import sys
import logging
from datetime import datetime
import subprocess
import asyncio

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
import time

import random
import pytest
from common_libs.models.common import EventValues


CATEGORY = 'watersystems'


@pytest.fixture
def client():
    with TestClient(app) as c:
        print('Creating new instance of app')
        print('Test Client Response', c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52N,52D,33F,31P,33F,29J'
            }
        ))
        yield c


@pytest.mark.skip(reason='Failure non deterministic, need to see if timing or other reasons lead to failure')
def test_water_tank_alerts_WM524T(client):
    # Fresh = 1 , Gray = 2, Black = 3
    for instance in (1, 2, 3):
        for lvl in (0, 50, 100):
            msg = {
                "title": f'Tank {instance}',
                "Instance": str(instance),
                "Fluid_Type": "X Water",
                "Fluid_Level": str(lvl),
                # "Tank_Capacity": "0.1136",
                # "NMEA_Reserved": "255",
                "name": "FLUID_LEVEL",
                'instance_key': ''
            }
            response = send_a_can_event(client, msg)

            time.sleep(1)

            response = client.get(f'/api/{CATEGORY}/wt/{instance}/state')
            assert response.status_code == 200
            print(f"Water Tank Level {lvl} Response {response.json()}")

            assert response.json().get('lvl') == float(lvl)
    # check for alert on Gray and Black

    response = client.get('/ui/notifications')
    print(response.json())
    assert response.status_code == 200

    found_alert = False
    for item in response.json():
        print(item.get('ecode'))
        if item.get('ecode') == 'GREY_WATER_TANK_FULL':
            found_alert = True
            break

    assert found_alert is True

    found_alert = False
    for item in response.json():
        print(item.get('ecode'))
        if item.get('ecode') == 'BLACK_WATER_TANK_FULL':
            found_alert = True
            break
    assert found_alert is True
