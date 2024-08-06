import logging

import pytest
from fastapi.testclient import TestClient

from main_service.tests.can_messages import DEFAULTS
from main_service.tests.utils import send_a_can_event
from main_service.wgo_main_service import app

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    '''Set up client and set floorplan and option codes.'''
    print('[TESTCLIENT] Init Client')
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,31P,33F,29J,52N'
            }
        )
        yield c


def test_can_state_success_response_524t(client):
    '''Test that each supported can message does indeed return success and
    does not have hidden failures.'''
    for msg, can_msg in DEFAULTS.items():
        print('[PYTEST][CAN] Sending', msg)
        if can_msg is None:
            can_msg = {
                'name': msg
            }
        response = send_a_can_event(
            client,
            can_msg
        )
        assert response.status_code == 200


def test_can_state_bad_request_524t(client):
    '''Test that messages return bad request when empty.
    This is now handled in can.py if no body is provided.'''
    for msg, _ in DEFAULTS.items():
        print('[PYTEST][CAN] Sending', msg)

        response = send_a_can_event(
            client,
            {},
            msg_name=msg
        )
        assert response.status_code == 400


def test_can_state_energy_charger_ac_status_1(client):
    '''Example of a specific test that tests the default message.'''
    can_msg = DEFAULTS.get('charger_ac_status_1')
    response = send_a_can_event(client, can_msg)
    assert response.status_code == 200


def test_can_state_energy_charger_ac_status_1_data_wrong(client):
    '''Example of a specific test for the catch all in can.py on faulty message that is not handled.'''
    can_msg = {
        "Instance": "1",        # Currently does not cause an error as instance is just used in state key
        "RMS_Voltage": 120,
        "RMS_Current": None,
        "Frequency": "",
        "name": "charger_ac_status_1"
    }
    response = send_a_can_event(client, can_msg)
    assert response.status_code == 400
