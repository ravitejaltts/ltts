import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app

import pytest


@pytest.fixture
def client():
    with TestClient(app) as c:

        yield c


# #SETTINGS:


def test_api_main_settings(client):
    response = client.get("/api/settings")
    assert response.status_code == 200


def test_bluetooth_pairing(client):
    response = client.get("/api/settings/bluetooth/pairing")
    assert response.status_code == 200


def test_bluetooth_onoff(client):
    return
    response = client.put("/api/settings/bluetooth/onoff", json={"onOff": 0})
    assert response.status_code == 200


def test_bluetooth_pairdevice(client):
    return
    response = client.put(
        "/api/settings/bluetooth/pairdevice",
        json={"name": "Iphone12", "connected": True, "macAddress": "44:01:BB:E0:90:9B"},
    )
    assert response.status_code == 200


def test_bluetooth_disconnect(client):
    return
    response = client.put(
        "/api/settings/bluetooth/disconnect",
        json={"name": "Iphone12", "connected": True, "macAddress": "44:01:BB:E0:90:9B"},
    )
    assert response.status_code == 200


def test_bluetooth_forgetdevice(client):
    return
    response = client.put(
        "/api/settings/bluetooth/forgetdevice",
        json={"name": "Iphone12", "connected": True, "macAddress": "44:01:BB:E0:90:9B"},
    )
    assert response.status_code == 200


def test_screenmode(client):
    values = ["LIGHT", "DARK"]
    for value in values:
        response = client.put("api/settings/browser/screenmode", json={"value": value})
        assert response.status_code == 200


def test_autosunset(client):
    return
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put(
            "/api/settings/browser/screenmode/autosunset", json={"onOff": onOff}
        )
        assert response.status_code == 200


def test_qr_code(client):
    response = client.get("/api/settings/qr_code")
    print(response.json())
    assert response.status_code == 200


def test_qr_code_envs(client):
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': '52D,33F,31P,33F,29J'
        }
    )
    for env in (
            'https://apim.ownersapp.winnebago.com/',
            'https://tst-apim.ownersapp.winnebago.com',
            'https://dev-apim.ownersapp.winnebago.com'):
        app.config['environment'] = 'https://dev-apim.ownersapp.winnebago.com'
        # print('ENV', app.config.get('environment'))
        response = client.get("/api/settings/qr_code")
        # print('ENV', app.config.get('environment'))
        # print(response.json())
        assert 'https://dev-apim.ownersapp.winnebago.com/API/vehicle/ownersAppRedirect?vin=' in response.json().get('url')
        assert response.status_code == 200
