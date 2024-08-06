import os
import sys
import logging
from datetime import datetime
import subprocess
import json


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
from common_libs.models.common import EventValues, RVEvents, LogEvent

logger = logging.getLogger(__name__)


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



def test_battery_blocks_ota_WM524T(client):
    # Indoor
    MAIN_POWER_STUD_INSTANCE = 2
    CAN_INSTANCE = 252
    msg = {
            'Instance': f'{CAN_INSTANCE}',
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            # "State_Of_Charge": "10.1",
            "State_Of_Charge": str(random.randint(0, 49)),
            "Time_Remaining": "604",
            "Time_Remaining_Interpretation": "Time to Full",
            # "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            "instance_key": "",
        }
    # 2.626 Watts expect 3

    response = send_a_can_event(client, msg)

    response = client.get(f"/api/energy/ec/{MAIN_POWER_STUD_INSTANCE}/state")
    assert response.status_code == 200

    event = LogEvent(
                timestamp=time.time(),
                event=RVEvents.OTA_UPDATE_RECEIVED,
                instance=1,
                value=1,
            )
    response = client.put("/event_log", json=event.dict())
    assert response.status_code == 200


    response = client.get(f"/ota_lockout")
    assert response.status_code == 200
    assert response.json() is True
