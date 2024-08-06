
import os
import sys
import logging
logger = logging.getLogger(__name__)

import pytest

from fastapi.testclient import TestClient

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))


from main_service.wgo_main_service import app


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


def test_connectivity_geo(client):
    '''Test to retrieve the geo position.'''
    response = client.get('/api/connectivity/geo')
    assert response.status_code == 200
    # TODO: Add check for content


def test_connectivity_cellular(client):
    response = client.get('/api/connectivity/cellular')
    # NOTE: We cannot test for 200 in the cloud yet, so timeout would return 408
    # On setup with Cradlepoint on NW it passes
    assert response.status_code in [200, 408]
    # TODO: Add check for content


def test_connectivity_wifi(client):
    response = client.get('/api/connectivity/wifi')
    assert response.status_code == 200
    # TODO: Add check for content


def test_connectivity_timezone(client):
    response = client.get('/api/connectivity/timezone')
    assert response.status_code == 200
    # TODO: Add check for content
