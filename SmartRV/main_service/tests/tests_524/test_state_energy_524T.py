import os
import sys
import logging
from datetime import datetime
import subprocess
import asyncio

from pydantic import ValidationError

import time
import random

from fastapi.testclient import TestClient
import pytest

from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import (
    CZONE_MAIN_STUD_MEDIUM_LOAD,
    CZONE_MAIN_STUD_NO_LOAD,
    ENERGY_INVERTER_NO_LOAD,
    ENERGY_INVERTER_1200W_LOAD,
    SHORE_1200W,
    SOLAR_16W
)
from common_libs.models.common import EventValues


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,29J'
            }
        )
        yield c


# # @pytest.hookimpl()
# # def pytest_sessionstart(session):
# #     print("hello")


# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_sessionstart(session):
#     with TestClient(app) as c:
#         c.put(
#             '/api/system/floorplan',
#             json={
#                 'floorPlan': 'WM524T',
#                 'optionCodes': '52D,33F,31P,33F,29J'
#             }
#         )
#         yield
#     print('Pytest Cleanup')
#     c.put(
#         '/api/system/floorplan',
#         json={
#             'floorPlan': 'VANILLA',
#             'optionCodes': ''
#         }
#     )


def test_ec_rounding_WM524T(client):
    # Indoor
    MAIN_POWER_STUD_INSTANCE = 2
    CAN_INSTANCE = 252
    msg = {
        'Instance': f'{CAN_INSTANCE}',
        'Battery_Voltage': '13.13',
        'Battery_Current': '-0.2',
        'Sequence_Id': '0',
        'msg': 'Timestamp: 1708498737.525601    ID: 19f21497    X Rx                DL:  8    fc 21 05 fe ff ff ff 00     Channel: canb0s0',
        'msg_name': 'Battery_Status',
        # 'name': 'battery_status',
        'source_address': '97',
        'instance_key': '19F21497__0__252'
    }
    # 2.626 Watts expect 3

    response = send_a_can_event(client, msg)

    response = client.get(f"/api/energy/ec/{MAIN_POWER_STUD_INSTANCE}/state")
    assert response.status_code == 200
    assert response.json().get("watts") == 3
    assert response.json().get("active") == EventValues.TRUE


def test_ec_inactive_WM524T(client):
    # Indoor
    MAIN_POWER_STUD_INSTANCE = 2
    CAN_INSTANCE = 252
    # Set to non active
    msg = {
        'Instance': f'{CAN_INSTANCE}',
        'Battery_Voltage': '13.13',
        'Battery_Current': '0.0',
        'Sequence_Id': '0',
        'msg': 'Timestamp: 1708498737.525601    ID: 19f21497    X Rx                DL:  8    fc 21 05 fe ff ff ff 00     Channel: canb0s0',
        'msg_name': 'Battery_Status',
        # 'name': 'battery_status',
        'source_address': '97',
        'instance_key': '19F21497__0__252'
    }

    response = send_a_can_event(client, msg)

    response = client.get(f"/api/energy/ec/{MAIN_POWER_STUD_INSTANCE}/state")
    assert response.status_code == 200
    assert response.json().get("watts") == 0
    assert response.json().get("active") == EventValues.FALSE


def test_ec_invalid_data_WM524T(client):
    # Indoor
    MAIN_POWER_STUD_INSTANCE = 2
    CAN_INSTANCE = 252

    # Set to invalid data
    msg = {
        'Instance': f'{CAN_INSTANCE}',
        'Battery_Voltage': 'Data Invalid',
        'Battery_Current': 'Data Invalid',
        'Sequence_Id': '0',
        'msg': 'Timestamp: 1708498737.525601    ID: 19f21497    X Rx                DL:  8    fc 21 05 fe ff ff ff 00     Channel: canb0s0',
        'msg_name': 'Battery_Status',
        # 'name': 'battery_status',
        'source_address': '97',
        'instance_key': '19F21497__0__252'
    }

    response = send_a_can_event(client, msg)

    response = client.get(f"/api/energy/ec/{MAIN_POWER_STUD_INSTANCE}/state")
    assert response.status_code == 200
    assert response.json().get("watts") is None
    assert response.json().get("active") is None


def test_ic_set_brk_sizes(client):
    '''Test to set different charger breaker sizes for Xantrex Inverter/Charger'''
    CHARGER_ID = 1
    # Set defaults
    response = client.put(f'/api/energy/ic/{CHARGER_ID}/defaults')

    response = client.get(f'/api/energy/ic/{CHARGER_ID}/state')

    assert response.status_code == 200
    assert response.json().get('brkSize') == 15

    response = client.put(
        f'/api/energy/ic/{CHARGER_ID}/state',
        json={
            'brkSize': 20
        }
    )
    assert response.status_code == 200
    assert response.json().get('brkSize') == 20

    response = client.get(f'/api/energy/ic/{CHARGER_ID}/state')
    assert response.status_code == 200
    assert response.json().get('brkSize') == 20

    # TODO: Find out why validation error is not the one handled
    # with pytest.raises(ValidationError):
    with pytest.raises(Exception):
        # Exceed the models max brkSize
        response = client.put(
            f'/api/energy/ic/{CHARGER_ID}/state',
            json={
                'brkSize': 200
            }
        )

    # with pytest.raises(ValidationError):
    with pytest.raises(Exception):
        # Below the models min brkSize
        response = client.put(
            f'/api/energy/ic/{CHARGER_ID}/state',
            json={
                'brkSize': 0
            }
        )

    response = client.get(f'/api/energy/ic/{CHARGER_ID}/state')

    assert response.status_code == 200
    assert response.json().get('brkSize') == 20

    response = client.put(f'/api/energy/ic/{CHARGER_ID}/defaults')


def test_energy_consumers_basic(client):
    '''Test that energy consumer components update properly.'''
    # Check that neither DC or AC are reporting
    AC_ID = 1
    DC_ID = 2

    # Check all defaults for the instances
    for instance in (AC_ID, DC_ID):
        response = client.get(f'/api/energy/ec/{instance}/state')
        assert response.json().get('active') == EventValues.FALSE
        assert response.json().get('watts') is None

    _ = send_a_can_event(client, ENERGY_INVERTER_NO_LOAD)

    ac_response = client.get(f'/api/energy/ec/{AC_ID}/state')
    assert ac_response.json().get('active') == EventValues.OFF
    assert ac_response.json().get('watts') == 0

    # Set an AC Load
    _ = send_a_can_event(client, ENERGY_INVERTER_1200W_LOAD)

    ac_response = client.get(f'/api/energy/ec/{AC_ID}/state')
    assert ac_response.json().get('active') == EventValues.ON
    assert ac_response.json().get('watts') == 1200

    # Clear AC Load Again
    _ = send_a_can_event(client, ENERGY_INVERTER_NO_LOAD)

    ac_response = client.get(f'/api/energy/ec/{AC_ID}/state')
    assert ac_response.json().get('active') == EventValues.OFF
    assert ac_response.json().get('watts') == 0

    # DC
    _ = send_a_can_event(client, CZONE_MAIN_STUD_NO_LOAD)

    dc_response = client.get(f'/api/energy/ec/{DC_ID}/state')
    assert dc_response.json().get('active') == EventValues.OFF
    assert dc_response.json().get('watts') == 0

    # DC Set Load
    _ = send_a_can_event(client, CZONE_MAIN_STUD_MEDIUM_LOAD)

    dc_response = client.get(f'/api/energy/ec/{DC_ID}/state')
    assert dc_response.json().get('active') == EventValues.ON
    assert dc_response.json().get('watts') == 260

# # Removed from UI
# def test_energy_shore_ui(client):
#     '''Test that energy source ui providers properly.'''

#     _ = send_a_can_event(client, SHORE_1200W)

#     ui_response = client.get('/ui/shore/')
#     assert ui_response.status_code == 200
#     grp = ui_response.json().get('group')
#     state = grp.get('state')
#     assert state.get('active') == EventValues.ON
#     pwr = grp.get('tiles')[0].get('value')
#     assert pwr == '1200'


# def test_energy_solar_ui(client):
#     '''Test that energy source ui providers properly.'''

#     _ = send_a_can_event(client, SOLAR_16W)

#     ui_response = client.get('/ui/solar/')
#     assert ui_response.status_code == 200
#     grp = ui_response.json().get('group')
#     state = grp.get('state')
#     assert state.get('active') == EventValues.ON
#     pwr = grp.get('tiles')[0].get('value')
#     assert pwr == '16'
