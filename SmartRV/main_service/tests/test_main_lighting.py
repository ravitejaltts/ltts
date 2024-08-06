
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath('./..'))
sys.path.append(os.path.abspath('.'))

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
import subprocess

import pytest

# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print("Changing Floorplan to WM524T")
#     logger.debug("Changing Floorplan to WM524T")
#     subprocess.call(["sed -i -e 's/848EC/WM524T/g' /storage/UI_config.ini"], shell=True)

# TODO: Review endpoints if they could require a NotImplementError handler on success
# as some endpoints might not apply to a particular model


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.skip(reason="New pytest error - on NotImplementedError")
def test_lighting_overview(client):
    # TODO: Fix test once properly implemented
    with pytest.raises(NotImplementedError):
        response = client.get('/api/lighting')


def test_lighting_state(client):
    response = client.get('/api/lighting/state')
    assert response.status_code == 200


# def test_lighting_zone(client):
#     response = client.get('/api/lighting/lz')
#     assert response.status_code == 200

def test_get_lighting_zone(client):
    zone_id = 2
    endpoint = f'/api/lighting/lz/{zone_id}/state'
    response = client.get(endpoint)
    assert response.status_code == 200


def test_set_lighting_zone(client):
    zone_id = 2
    response = client.put(
        f'/api/lighting/lz/{zone_id}/state',
        json={
            "brt": 100,
            "onOff": 1,
            "rgb": "string",        # Not required for 500 series, but should not break
            "clrTmp": 10000
        }
    )
    assert response.status_code == 200


def test_lighting_group_defaults(client):
    for lg in (0, 1, 2, 3):
        response = client.get(f'/api/lighting/lg/{lg}/state')
        assert response.status_code == 200


def test_activate_lighting_group_defaults(client):
    # Need to be sure we have saved the lg before we ask it to activate
    for lg in (1, 2, 3):
        response = client.put(
            f'/api/lighting/lg/{lg}/state',
            json={
                'save': 1
            })
        assert response.status_code == 200
    for lg in (0, 1, 2, 3):
        response = client.put(
            f'/api/lighting/lg/{lg}/state',
            json={
                'onOff': 1
            })
        assert response.status_code == 200


def test_set_lighting_group_defaults(client):
    for lg in (1, 2, 3):
        response = client.put(
            f'/api/lighting/lg/{lg}/state',
            json={
                'save': 1
            })
        assert response.status_code == 200


def test_get_lighting_settings(client):
    response = client.get(f'/api/lighting/settings')
    assert response.status_code == 200


def test_get_lighting_reset(client):
    response = client.put(f'/api/lighting/reset')
    assert response.status_code == 200


def test_get_non_existing_lz(client):
    response = client.get('/api/lighting/lz/-1/state')
    assert response.status_code == 404


def test_set_non_positive_lz(client):
    response = client.put('/api/lighting/lz/-1/state')
    assert response.status_code == 422


def test_set_non_existing_lz(client):
    response = client.put('/api/lighting/lz/999/state', json={'onOff': 1})
    assert response.status_code == 404


def test_get_non_existing_lg(client):
    response = client.get('/api/lighting/lg/-1/state')
    assert response.status_code == 404


def test_set_non_existing_lg(client):
    response = client.put('/api/lighting/lg/-1/state', json={'onOff': 1})
    assert response.status_code == 404


def test_smart_lg_settings(client):
    LG = 0

    response = client.get(f'/api/lighting/lg/{LG}/state')
    assert response.status_code == 200

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'brt': 50
        }
    )
    assert response.status_code == 200
    assert response.json().get('brt') == 50
