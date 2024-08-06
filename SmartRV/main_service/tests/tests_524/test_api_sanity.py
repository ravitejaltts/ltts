'''Tests the API call sanity checks like 404 responses when requesting unknown instances etc.'''
import logging
logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

import pytest


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


def test_catch_all_api_sanity(client):
    # Test unknown system supersystems
    response = client.get('/api/supersystems/wc/1/state')
    assert response.status_code == 404

    # Test unknown code xx for existing system watersystems
    response = client.get('/api/watersystems/xx/1/state')
    assert response.status_code == 404


def test_watersystems_api_sanity(client):
    # Tanks
    # Get not present instance 999
    response = client.get('/api/watersystems/wt/999/state')
    assert response.status_code == 404
    # Water tanks do not have a put, but they could to harmoize it
    response = client.put('/api/watersystems/wt/999/state', json={})
    # TODO: Change this to 404 to test that the put would reject the instance
    assert response.status_code == 404
    # Pumps
    response = client.get('/api/watersystems/wp/999/state')
    assert response.status_code == 404
    response = client.put('/api/watersystems/wp/999/state', json={})
    assert response.status_code == 404
    # Heaters
    response = client.get('/api/watersystems/wh/999/state')
    assert response.status_code == 404
    response = client.put('/api/watersystems/wh/999/state', json={})
    assert response.status_code == 404
    # Toilet Circuit
    # NOTE: Not the same code fails if we have a tc 1 ion the R, so a specific test is required
    response = client.get('/api/watersystems/tc/999/state')
    assert response.status_code == 404


def test_lighting_api_sanity(client):
    response = client.get('/api/lighting/lz/999/state')
    assert response.status_code == 404


def test_features_petminder_api_sanity(client):
    response = client.get('/api/features/pm/999/state')
    assert response.status_code == 404


def test_features_weather_api_sanity(client):
    pass


def test_climate_api_sanity(client):
    # Thermostat
    # Air Conditioner
    # Heater
    #
    pass
