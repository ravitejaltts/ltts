
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


from common_libs.models.common import EventValues

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

import pytest

@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put('/api/system/floorplan', json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,291'})
        yield c

# ##VEHICLE

def test_get_ignition(client):
    response = client.get('api/vehicle/ignition_key')
    assert response.status_code == 200


def test_get_vehicle_vin(client):
    response = client.get('api/vehicle/vin')
    assert response.status_code == 200


def test_set_vehicle_vin(client):
    response = client.get('api/vehicle/vin')
    assert response.status_code == 200


def test_get_vehicle_soc(client):
    response = client.get('api/vehicle/soc')
    assert response.status_code == 200


def test_doorlock_default_state(client):
    result = client.get('/api/vehicle/dl/1/state')
    assert result.status_code == 200
    assert result.json().get('lock') == EventValues.UNLOCKED


def test_doorlock_lock(client):
    result = client.put(
        '/api/vehicle/dl/1/state',
        json={
            'lock': EventValues.LOCK
        }
    )
    assert result.status_code == 200
    assert result.json().get('lock') == EventValues.LOCKED


def test_doorlock_unlock(client):
    result = client.put(
        '/api/vehicle/dl/1/state',
        json={
            'lock': EventValues.LOCK
        }
    )
    assert result.status_code == 200
    assert result.json().get('lock') == EventValues.LOCKED

    result = client.put(
        '/api/vehicle/dl/1/state',
        json={
            'lock': EventValues.UNLOCK
        }
    )
    assert result.status_code == 200
    assert result.json().get('lock') == EventValues.UNLOCKED


def test_doorlock_invalid_state(client):
    result = client.put(
        '/api/vehicle/dl/1/state',
        json={
            'lock': EventValues.UNLOCK
        }
    )
    assert result.status_code == 200
    assert result.json().get('lock') == EventValues.UNLOCKED

    # Send invalid state
    result = client.put(
        '/api/vehicle/dl/1/state',
        json={
            'lock': 123
        }
    )
    print(result)
    assert result.status_code == 400

    result = client.get('/api/vehicle/dl/1/state')
    assert result.status_code == 200
    assert result.json().get('lock') == EventValues.UNLOCKED
