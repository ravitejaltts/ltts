import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
import pytest

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from common_libs.models.common import EventValues


@pytest.fixture
def client():
    with TestClient(app) as c:
        print('Creating new instance of app')
        print('Test Client Response', c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,29J'
            }
        ))
        yield c


def test_get_state_session(client):
    '''Test that the state endpoint handles a new session with a full state.'''
    response = client.get("/api/state", headers={})
    assert response.status_code == 200
    print(response.json())
    result = response.json()
    session = result.get('sessionId')
    assert session is not None

    # Call again and see nothing
    response = client.get(f"/api/state?session_id={session}", headers={})
    assert response.status_code == 200
    assert response.json() == {}

    # Make a change
    response = client.put('/api/climate/th/1/state', json={'onOff': EventValues.ON})
    assert response.status_code == 200

    response = client.get(f"/api/state?session_id={session}", headers={})
    assert response.status_code == 200
    assert response.json() != {}
    assert response.json().get('climate', {}).get('th1').get('onOff') == EventValues.ON

    response = client.get(f"/api/state?session_id={session}", headers={})
    assert response.status_code == 200
    assert response.json() == {}
