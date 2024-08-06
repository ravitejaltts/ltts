
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


from common_libs.models.common import EventValues

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

import pytest


BASE_URL = '/api'
TEST_HARNESS_API = '/testharness'


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


def test_set_lighting_state(client):
    for i, _ in app.hal.lighting.handler.lighting_zone.items():
        _ = client.put(f'/api/lighting/lz/{i}/defaults')

    result = client.get(
        BASE_URL + '/lighting/lz/2/state'
    )
    assert result.status_code == 200
    data = result.json()
    assert data.get('onOff') is None
    assert data.get('brt') == 80

    result = client.put(
        TEST_HARNESS_API + '/lighting/lz/2/state/override',
        json={
            'onOff': 0,
            'brt': 100
        }
    )

    assert result.status_code == 200
    data = result.json()
    assert data.get('onOff') == 0
    assert data.get('brt') == 100

    result = client.put(
        TEST_HARNESS_API + '/lighting/lz/2/state/override',
        json={
            'onOff': 1,
            'brt': 40
        }
    )

    assert result.status_code == 200
    data = result.json()
    assert data.get('onOff') == 1
    assert data.get('brt') == 40


def test_set_incorrect_parameters(client):
    # Send wrong/unknown category
    result = client.put(
        TEST_HARNESS_API + '/domscategory/lz/2/state/override',
        json={
            'onOff': 0,
            'brt': 100
        }
    )

    assert result.status_code == 404

    # Test that a not existing code in a valid category return 404
    result = client.put(
        TEST_HARNESS_API + '/lighting/domscode/2/state/override',
        json={
            'onOff': 1,
            'brt': 40
        }
    )

    assert result.status_code == 404

    # Test that a non existing instance returns 404
    result = client.put(
        TEST_HARNESS_API + '/lighting/lz/9999/state/override',
        json={
            'onOff': 1,
            'brt': 40
        }
    )

    assert result.status_code == 404

    # Test that a non integer returns 422 as that is set in the API
    result = client.put(
        TEST_HARNESS_API + '/lighting/lz/domsinstance/state/override',
        json={
            'onOff': 1,
            'brt': 40
        }
    )

    assert result.status_code == 422
