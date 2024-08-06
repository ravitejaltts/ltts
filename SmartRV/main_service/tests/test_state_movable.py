import os
import sys
import logging
import asyncio


logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import RV1_IGNITION_ON, RV1_IGNITION_OFF
from common_libs.models.common import RVEvents, EventValues
import random
import pytest
from main_service.components.movables import (
    SlideoutBasicState,
    AwningRvcState,
    JackState,
)

CAN_HISTORY_WAIT_TIMER = 2

@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,52N,33F,31P,33F,29J'
            }
        )
        yield c


# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print("Changing Floorplan to WM524T")
#     logger.debug("Changing Floorplan to WM524T")
#     subprocess.call("sed -i -e 's/848EC/WM524T/g' /storage/UI_config.ini", shell=True)

in_dev = pytest.mark.skipif(True,
                          reason="Refactor needed to pass tests on any platform"
                         )


@in_dev
@pytest.mark.asyncio
async def test_aw_for_WM524T(client):

    msg_ign_off = RV1_IGNITION_OFF
    response = send_a_can_event(client, msg_ign_off)
    await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)

    msg = {
        "Instance": "1",
        "Position": "10",
        "Motion": "No motion",
        "name": "Awning_Status"
    }
    response = send_a_can_event(client, msg)
    await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)

    response = client.get("/api/movables/aw/1/state")
    assert response.status_code == 200
    print(f"Full Awning Response {response.json()}")
    assert response.json().get("mode") is not None
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.RETRACTING
        }
    )
    assert response.status_code == 200
    assert response.json().get("mode") == EventValues.RETRACTING

    await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)
    last_message = app.can_sender.get_can_history().get('history_sent').pop()
    print(last_message)
    print('[AWNING] queue history', app.can_sender.get_can_history())
    while '19FEF244#01FF02FFFFFFFFFF' not in last_message['cmd']:
        await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)
        last_message = app.can_sender.get_can_history().get('history_sent').pop()
    # db remove could be affecting - passes stand alone
    assert '19FEF244#01FF02FFFFFFFFFF' in last_message['cmd']

    # Turn off
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.OFF
        }
    )
    assert response.status_code == 200
    assert response.json().get("mode") == EventValues.OFF

    await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)
    last_message = app.can_sender.get_can_history().get('history_sent').pop()
    while '19FEF244#01FF00FFFFFFFFFF' not in last_message['cmd']:
        await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)
        last_message = app.can_sender.get_can_history().get('history_sent').pop()
    print(last_message)
    assert '19FEF244#01FF00FFFFFFFFFF' in last_message['cmd']

    # Extend
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.EXTENDING
        }
    )
    assert response.status_code == 200
    assert response.json().get("mode") == EventValues.EXTENDING

    await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)
    last_message = app.can_sender.get_can_history().get('history_sent').pop()
    print(last_message)
    while '19FEF244#01FF01FFFFFFFFFF' not in last_message['cmd']:
        await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)
        last_message = app.can_sender.get_can_history().get('history_sent').pop()
    assert '19FEF244#01FF01FFFFFFFFFF' in last_message['cmd']


# def test_so_get_for_WM524T(client):
#     response = client.get("/api/movables/so/1/state")
#     assert response.status_code == 200
#     print(f"Full SLideout Response {response.json()}")
#     assert response.json().get("mode") is not None

# def test_so_put_for_WM524T(client):
#     response = client.put("/api/movables/so/1/state", json={"mode": EventValues.RETRACTING})
#     assert response.status_code == 200
#     print(f"Full SLideout Response {response.json()}")
#     assert response.json().get("mode") is not None

#     response = client.get("/api/movables/so/1/state")
#     assert response.status_code == 200
#     print(f"Full SLideout Response {response.json()}")
#     assert response.json().get("mode") == EventValues.RETRACTING


##MOVABLE


def test_get_movable_awning(client):
    response = client.get("/api/movables/aw/1/state")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_awning_ignition_lockout(client):
    msg = RV1_IGNITION_ON
    response = send_a_can_event(client, msg)
    await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)

    response = client.put(
        "api/movables/aw/1/state",
        json={"light": {"onOff": 1, "brt": 100}, "onOff": 0, "pctExt": 563},
    )
    assert response.status_code == 423


@pytest.mark.asyncio
async def test_set_movable_change_awning(client):
    msg = RV1_IGNITION_OFF
    response = send_a_can_event(client, msg)
    await asyncio.sleep(CAN_HISTORY_WAIT_TIMER)

    response = client.put(
        "api/movables/aw/1/state",
        json={"light": {"onOff": 1, "brt": 100}, "onOff": 0, "pctExt": 563},
    )
    assert response.status_code == 200


@pytest.mark.skip(reason='No CAN enabled leveling jack available at this time')
def test_get_movable_jacks(client):
    response = client.get("api/movables/jacks")
    assert response.status_code == 200


@pytest.mark.skip(reason='No CAN enabled leveling jack available at this time')
def test_put_movable_jacks(client):
    response = client.put(
        "api/movables/lj/1/state", json={"mode": EventValues.LEVELING_BIAX_FRONT_EXTENDING}
    )
    assert response.status_code == 200
    response = client.get("api/movables/lj/1/state")
    assert response.json().get('mode') == EventValues.LEVELING_BIAX_FRONT_EXTENDING


# def test_setup_for_848EC(client):
#     print("Changing Floorplan to 848EC")
#     logger.debug("Changing Floorplan to 848EC")
#     subprocess.call(["sed -i -e 's/WM524T/848EC/g' /storage/UI_config.ini"], shell=True)


# def test_bm_for_848EC(client):

#     msg =  {
#             "title": "Setting cold",
#             "Instance": "55",
#             "Ambient_Temp": "3",
#             "name": "thermostat_ambient_status"
#         }

#     response = send_a_can_event(client, 'thermostat_ambient_status', msg)

#     response = client.get("/api/energy/bm/1/state")
#     assert response.status_code == 200
#     print(f"Full State Response {response.json()}")
#     assert(response.json().get("temp") is not None)
