
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

# from main_service.tests.can_messages import *
from main_service.tests.utils import send_a_can_event

from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

import pytest


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# ##VEHICLE

VIN = ''


def test_get_ignition(client):
    response = client.get('/api/vehicle/ignition_key')
    assert response.status_code == 200


def test_get_vehicle_vin(client):
    response = client.get('/api/vehicle/vin')
    assert response.status_code == 200


def test_set_vehicle_vin(client):
    response = client.get('/api/vehicle/vin')
    assert response.status_code == 200


def test_get_vehicle_soc(client):
    response = client.get('/api/vehicle/soc')
    assert response.status_code == 200


def test_get_vin(client):
    global VIN
    response = client.get('/api/vehicle/vin')
    assert response.status_code == 200
    VIN = response.json().get('vin', VIN)


def test_set_vin(client):
    global VIN
    response = client.get('/api/vehicle/vin')
    print('Vin response', response.json())
    assert response.status_code == 200
    VIN = response.json().get('vin', VIN)

    response = client.put(
        '/api/vehicle/vin',
        json={
            'vin': 'FEDCBAG0123456789'
        }
    )
    print('Failure in setting VIN')
    print(response.json())
    assert response.status_code == 200
    assert response.json().get('vin') == 'FEDCBAG0123456789'

    if not VIN:
        # If test starts with empty VIN we need to set a new one
        VIN = 'ABCDEFG0123456789'

    response = client.put(
        '/api/vehicle/vin',
        json={
            'vin': VIN
        }
    )
    assert response.status_code == 200
    assert response.json().get('vin') == VIN


def test_set_vin_sanitize(client):
    global VIN
    response = client.get('/api/vehicle/vin')
    assert response.status_code == 200
    VIN = response.json().get('vin', VIN)

    response = client.put(
        '/api/vehicle/vin',
        json={
            'vin': 'abcdEFG0123456789'
        }
    )
    assert response.status_code == 200
    assert response.json().get('vin') == 'ABCDEFG0123456789'

    response = client.put(
        '/api/vehicle/vin',
        json={
            'vin': '!@#!@#!@#!@#!@#!@'
        }
    )
    assert response.status_code == 422

    response = client.put(
        '/api/vehicle/vin',
        json={
            'vin': 'BCDEFG0123456789'
        }
    )
    assert response.status_code == 422

    response = client.get('/api/vehicle/vin')
    assert response.status_code == 200
    assert response.json().get('vin') == 'ABCDEFG0123456789'

    response = client.put(
        '/api/vehicle/vin',
        json={
            'vin': VIN
        }
    )
    assert response.status_code == 200
    assert response.json().get('vin') == VIN


def test_vanilla_vin_from_can(client):
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'VANILLA',
            'optionCodes': ''
        }
    )
    vin_1 = {
        "name": 'VIN_RESPONSE',
        "msg_name": "VIN_RESPONSE",
        "Vin_List_Num": "1",
        "Hex_Ascii_1": 0x31,
        "Hex_Ascii_2": 0x32,
        "Hex_Ascii_3": 0x33,
        "Hex_Ascii_4": 0x34,
        "Hex_Ascii_5": 0x35,
        "Hex_Ascii_6": 0x36,
        "Hex_Ascii_7": 0x37
    }
    vin_2 = {
        "name": 'VIN_RESPONSE',
        "msg_name": "VIN_RESPONSE",
        "Vin_List_Num": "2",
        "Hex_Ascii_1": 0x38,
        "Hex_Ascii_2": 0x39,
        "Hex_Ascii_3": 0x30,
        "Hex_Ascii_4": 0x31,
        "Hex_Ascii_5": 0x32,
        "Hex_Ascii_6": 0x33,
        "Hex_Ascii_7": 0x34
    }
    vin_3 = {
        "name": 'VIN_RESPONSE',
        "msg_name": "VIN_RESPONSE",
        "Vin_List_Num": "3",
        "Hex_Ascii_1": 65,
        "Hex_Ascii_2": 66,
        "Hex_Ascii_3": 67,
        "Hex_Ascii_4": "Data Invalid",
        "Hex_Ascii_5": "Data Invalid",
        "Hex_Ascii_6": "Data Invalid",
        "Hex_Ascii_7": "Data Invalid"
    }
    send_a_can_event(client, vin_1)
    send_a_can_event(client, vin_2)
    send_a_can_event(client, vin_3)

    response = client.get('/api/vehicle/vin')
    assert response.status_code == 200
    assert response.json().get('vin') == '12345678901234ABC'
