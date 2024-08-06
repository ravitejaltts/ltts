import pytest
from common_libs.models.common import RVEvents, EventValues
from main_service.wgo_main_service import app
from fastapi.testclient import TestClient
import main_service.wgo_main_service
import importlib

import os
import sys
import logging
from datetime import datetime
from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import RV1_IGNITION_ON, RV1_IGNITION_OFF
from common_libs import environment

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    with TestClient(main_service.wgo_main_service.app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52N,33F,31P,33F,29J,52D'
            }
        )
        yield c


def test_get_movable_awning(client):
    response = client.get("/api/movables/aw/1/state")
    assert response.status_code == 200


def test_set_movable_change_awning(client):
    msg = {
        "Instance": "1",
        "Position": "10",
        "Motion": "No motion",
        "name": "Awning_Status"
    }
    response = send_a_can_event(client, msg)

    msg = RV1_IGNITION_OFF
    response = send_a_can_event(client, msg)


    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.EXTENDING,
            "setPctExt": 100
        }
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 200

    msg = {
        "Instance": "1",
        "Position": "55",
        "Motion": "Extending",
        "name": "Awning_Status"
    }
    response = send_a_can_event(client, msg)


    result = client.get("/api/movables/aw/1/state")
    print(f"set movable result {result.json()}")
    assert result.json().get('pctExt') == 55
    assert result.json().get('mode') == EventValues.EXTENDING

    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.RETRACTING,
            "setPctExt": 0
        }
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 200

    result = client.get("/api/movables/aw/1/state")
    print(f"set movable result {result.json()}")
    # assert result.json().get('setPctExt') == 55
    assert result.json().get('mode') == EventValues.RETRACTING

    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.OFF,
            # "setPctExt": 50
        }
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 200

    result = client.get("/api/movables/aw/1/state")
    print(f"set movable result {result.json()}")
    # assert result.json().get('setPctExt') == 55
    assert result.json().get('mode') == EventValues.OFF

    # Add setPctExt only extend test
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "setPctExt": 100
        }
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 200

    result = client.get("/api/movables/aw/1/state")
    print(f"set movable result {result.json()}")
    # assert result.json().get('setPctExt') == 55
    assert result.json().get('mode') == EventValues.EXTENDING
    msg = {
            "Instance": "1",
            "Position": "99",
            "Motion": "No motion",
            "name": "Awning_Status"
        }
    response = send_a_can_event(client, msg)

    # Add setPctExt only retract test
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "setPctExt": 5
        }
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 200

    result = client.get("/api/movables/aw/1/state")
    print(f"set movable result {result.json()}")
    # assert result.json().get('setPctExt') == 55
    assert result.json().get('mode') == EventValues.RETRACTING


def test_set_movable_change_awning_farfield(client):

    msg = RV1_IGNITION_OFF
    response = send_a_can_event(client, msg)

    headers = {
        'source': 'platform'
    }
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.EXTENDING,
            "setPctExt": 100
        },
        headers=headers
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 403

    headers={'source': 'platform'}
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.EXTENDING,
            "setPctExt": 50
        },
        headers=headers
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 403

    headers={'source': 'platform'}
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.RETRACTING,
            "setPctExt": 50
        },
        headers=headers
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 403

    # Test Allowed to retract
    response = client.put(
        "/api/movables/aw/1/state",
        json={
            "mode": EventValues.RETRACTING,
            "setPctExt": 0
        },
        headers=headers
    )
    print(f"set movable response {response.json}")
    assert response.status_code == 200


@pytest.mark.skip(reason='No CAN enabled leveling jack available at this time')
def test_get_movable_jacks(client):
    response = client.get("/api/movables/lj/1/state")
    print(response)
    assert response.status_code == 200


@pytest.mark.skip(reason='No CAN enabled leveling jack available at this time')
def test_put_movable_jacks(client):
    response = client.put("/api/movables/lj/1/state",
                          json={"mode": EventValues.LEVELING_BIAX_RIGHT_EXTENDING})

    print(f"get jack result {response.json()}")
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.LEVELING_BIAX_RIGHT_EXTENDING

    response = client.put("/api/movables/lj/1/state",
                          json={"mode": EventValues.OFF})

    print(f"get jack result {response.json()}")
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.OFF


@pytest.mark.skip(reason='No CAN enabled leveling jack available at this time')
def test_put_movable_jacks_farfield(client):
    headers={'source': 'platform'}
    response = client.put("/api/movables/lj/1/state",
                          json={"mode": EventValues.LEVELING_BIAX_RIGHT_EXTENDING}, headers=headers)

    print(f"get jack result {response.json()}")
    assert response.status_code == 403
    assert 'Farfield commanding not allowed for this component.' in response.json().get('detail')


def test_slideout_get_state_default_lockouts(client):
    # Default should report at least one lockout
    response = client.get("/api/movables/so/1/state")
    print(response)
    assert response.status_code == 200
    # TODO: What should the default state be for lockouts that apply
    # to the slideout
    # assert len(response.json().get('lockouts')) > 0


def test_slideout_set_state_retracting(client):
    '''Test RETACTING then OFF'''
    response = client.put(
        f"/api/system/lk/{EventValues.PARK_BRAKE_APPLIED}/state",
        json={
            'active': True
        }
    )
    print(response.json())
    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.RETRACTING
        }
    )
    print(response.json())
    # NOTE: The signal changed to Combo Signal, so this test was modified to ensure PARK brake by itself does not allow movement
    assert response.status_code == 423

    response = client.put(
        f"/api/system/lk/{EventValues.PSM_PB_IGN_COMBO}/state",
        json={
            'active': True
        }
    )
    print(response.json())

    # response = client.put(
    #     "/api/movables/so/1/state",
    #     json={
    #         'mode': EventValues.OFF
    #     }
    # )
    # print(response.json())
    # assert response.status_code == 200
    # assert response.json().get('mode') == EventValues.OFF

    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.RETRACTING
        }
    )
    print(response.json())
    assert response.status_code == 200


def test_put_movable_slideout_farfield(client):
    headers={'source': 'platform'}
    response = client.put("/api/movables/so/1/state",
                          json={"mode": EventValues.EXTENDING}, headers=headers)

    print(f"get jack result {response.json()}")
    assert response.status_code == 403
    assert 'Farfield commanding not allowed for this component.' in response.json().get('detail')


def test_slideout_set_state_extending(client):
    # Remove all lockouts from state
    response = client.put(
        f"/api/system/lk/{EventValues.PSM_PB_IGN_COMBO}/state",
        json={
            'active': True
        }
    )
    print(response.json())
    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.EXTENDING
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.EXTENDING

    print(response.json())
    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.OFF
        }
    )
    print(response.json())
    assert response.status_code == 200
    # As this is not being overwritten in this test, the state shall be EXTENDING
    # TODO: Change this test to send a CAN message that uses the right ciruit and state update
    # from electrical. Also state should then NOT update anymore based on the request
    # Might be debatable, as we could also rely on this status while we do not know nay better and assume it is working
    assert response.json().get('mode') == EventValues.EXTENDED


@pytest.mark.skip('Not clear yet what state changes would result in off other that from RETRACTING to OFF, which is covered.')
def test_slideout_set_state_off(client):
    # Remove all lockouts from state
    response = client.put(
        f"/api/system/lk/{EventValues.PARK_BRAKE_APPLIED}/state",
        json={
            'active': True
        }
    )
    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.OFF
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.OFF


def test_slideout_set_state_extending_lockout(client):
    '''Test that with applicable lockouts extending fails.'''
    response = client.put(
        f"/api/system/lk/{EventValues.PSM_PB_IGN_COMBO}/state",
        json={
            'active': False
        }
    )
    print(response)
    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.EXTENDING
        }
    )
    print(response.json())
    assert response.status_code == 423
    assert len(response.json().get('detail', {}).get('lockouts', [])) > 0


def test_slideout_set_state_retracting_lockout(client):
    '''Test that with applicable lockouts retracting fails.'''
    response = client.put(
        f"/api/system/lk/{EventValues.PSM_PB_IGN_COMBO}/state",
        json={
            'active': False
        }
    )
    print(response)

    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.RETRACTING
        }
    )
    print(response.json())
    assert len(response.json().get('detail', {}).get('lockouts', [])) > 0
    assert response.status_code == 423


@pytest.mark.skip(reason='Not yet implemented as of 08/12/2023')
def test_slideout_set_state_off_no_lockout_applied(client):
    '''This test is to validate that OFF is not blocked by a lockout.
    08/12/2023 DOM: Not implemented as a feature yet.'''
    response = client.put(
        f"/api/system/lk/{EventValues.PARK_BRAKE_APPLIED}/state",
        json={
            'active': False
        }
    )

    response = client.put(
        "/api/movables/so/1/state",
        json={
            'mode': EventValues.OFF
        }
    )
    print(response.json())
    assert response.status_code == 200


def test_set_mtnsense_default(client):
    instance = 1
    response = client.put(f"/api/movables/aw/{instance}/mtnsense/default")
    assert response.status_code == 200
    assert response.json().get('mtnSense') == 5
    assert response.json().get('mtnSenseOnOff') == EventValues.ON


def test_set_mtnsense_user_turns_off(client):
    '''The default should just be 5 and on for motion'''
    instance = 1
    response = client.get(f"/api/movables/aw/{instance}/state")
    assert response.status_code == 200
    # assert response.json().get('mtnSense') == 5
    assert response.json().get('mtnSense') == 5
    assert response.json().get('mtnSenseOnOff') == EventValues.ON

    response = client.put(
        f"/api/system/lk/{EventValues.IGNITION_ON}/state",
        json={
            'active': False
        }
    )

    response = client.put(
        "/api/movables/aw/1/state",
        json={
            'mtnSenseOnOff': EventValues.OFF
        }
    )

    response = client.get(f"/api/movables/aw/{instance}/state")
    assert response.status_code == 200
    assert response.json().get('mtnSense') == 5
    assert response.json().get('mtnSenseOnOff') == EventValues.OFF

    response = client.put(
        "/api/movables/aw/1/state",
        json={
            'mode': EventValues.EXTENDING
        }
    )
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('mode') == EventValues.EXTENDING
