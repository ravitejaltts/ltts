import os
import sys
import logging
from datetime import datetime, timedelta
import subprocess
import json
import asyncio
from copy import deepcopy

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import *
import time

import pytest
from common_libs.models.common import EventValues


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52N,31T,29J,52D'
            }
        )
        yield c


def test_lockout_not_found_404(client):
    response = client.get(
        '/api/system/lk/{}/state'.format(
            -1
        )
    )
    print(response.json())
    assert response.status_code == 404
    assert 'detail' in response.json()
    # TODO: Check if we want to test for content, if not one uses it actively that might be a waste

    response = client.put(
        '/api/system/lk/{}/state'.format(
            -1
        ),
        json={}
    )
    print(response.json())
    assert response.status_code == 404
    assert 'detail' in response.json()

    response = client.get(
        '/api/system/lk/{}/state'.format(
            999999999999999
        )
    )
    print(response.json())
    assert response.status_code == 404
    assert 'detail' in response.json()

    response = client.put(
        '/api/system/lk/{}/state'.format(
            999999999999999
        ),
        json={}
    )
    print(response.json())
    assert response.status_code == 404
    assert 'detail' in response.json()


def test_lockout_non_integer_422(client):
    response = client.get(
        '/api/system/lk/{}/state'.format(
            "DOM"
        )
    )
    print(response.json())
    assert response.status_code == 422
    assert 'detail' in response.json()


def test_lockout_wrong_schema_422(client):
    response = client.put(
        '/api/system/lk/{}/state'.format(
            EventValues.FUEL_EMPTY
        ),
        json={
            'active': 'DOM'
        }
    )
    assert response.status_code == 422
    assert 'detail' in response.json()


@pytest.mark.skip(reason="Requirement changes for Fuel lockout - user supplied external tanks.")
def test_lockout_fuel_empty_generator_524T(client):
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': '52N,31T,29J,52D'
        }
    )
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.FUEL_EMPTY
        )
    )
    assert response.status_code == 200
    print('Initial Lockout Response', response.json())
    assert response.json().get('active') is False
    # Send Fuel Empty CAN message
    response = send_a_can_event(client, LP_LEVEL_FULL)
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.FUEL_EMPTY
        )
    )
    assert response.status_code == 200
    assert response.json().get('active') is False
    # assert response.json().get('')
    # Fluid Level instance 4
    response = send_a_can_event(client, LP_LEVEL_EMPTY)
    # Get Fuel Level
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.FUEL_EMPTY
        )
    )
    assert response.status_code == 200
    assert response.json().get('active') is True


@pytest.mark.skip(reason="Requirement changes for Fuel lockout - user supplied external tanks.")
def test_lockout_empty_generator_524T(client):
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': '52N,31T,29J,52D'
        }
    )
    # Send Fuel Empty CAN message
    response = send_a_can_event(client, LP_LEVEL_FULL)
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.FUEL_EMPTY
        )
    )
    assert response.status_code == 200
    assert response.json().get('active') is False
    # assert response.json().get('')
    # Fluid Level instance 4
    response = send_a_can_event(client, LP_LEVEL_EMPTY)
    # Get Fuel Level
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.FUEL_EMPTY
        )
    )
    print('FUEL IS EMPTY', response)
    print('FUEL IS EMPTY', response.json())
    assert response.status_code == 200
    assert response.json().get('active') is True


@pytest.mark.skip(reason="Working through generator lockouts")
def test_lockout_will_expire(client):
    # We only have one time lockout currently so we will use it to test
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.GENERATOR_COOLDOWN
        )
    )
    assert response.status_code == 200

    # This could be order dependant -
    # the test test_lockout_cooldown_generator_524T will check it
    # assert response.json().get('active') is False

    # TODO: Check with DOM about lockout get_state
    # which would be needed for clearing on lockout state read only

    # set the lockout
    # wait for it
    # check  it is no longer active

@pytest.mark.skip(reason="Working through generator lockouts - occasional pytest error")
def test_lockout_cooldown_generator_524T(client):
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': '52N,31T,29J,52D'
        }
    )
    # Send Fuel Empty CAN message
    response = send_a_can_event(client, LP_LEVEL_FULL)

    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.GENERATOR_COOLDOWN
        )
    )
    assert response.status_code == 200
    assert response.json().get('active') is False
    # assert response.json().get('')

    for i in range(5):
        response = client.put(
            f'/api/energy/ge/1/state',
            json={
                'mode': EventValues.RUN
            }
        )
        assert response.status_code == 200

        msg = {"Manufacturer_Code": "BEP Marine",
                    "Dipswitch": "128",
                    "Instance": "4",
                    "Output13": '1',
                    "name": "RvSwitch",
            }

        response = send_a_can_event(client, msg)

        response = client.put(
            f'/api/energy/ge/1/state',
            json={
                'mode': EventValues.OFF
            }
        )
        assert response.status_code == 200

    response = client.put(
        f'/api/energy/ge/1/state',
        json={
            'mode': EventValues.RUN
        }
    )
    # Should fail on the fourth to fast quick attempt
    assert response.status_code == 423

    # CHeck - now lockout is set
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.GENERATOR_COOLDOWN
        )
    )
    print('FUEL IS EMPTY', response)
    print('FUEL IS EMPTY', response.json())
    assert response.status_code == 200
    assert response.json().get('active') is True

    response = client.put(
        f'/api/energy/ge/1/state',
        json={
            'mode': EventValues.OFF
        }
    )
    assert response.status_code == 200


# Skip this in normal mode - it takes minutes to run
@pytest.mark.skip('Skip this in normal mode - it takes minutes to run')
def test_full_lockout_cooldown_generator_524T(client):
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': '52N,31T,29J,52D'
        }
    )
    # Send Fuel Empty CAN message
    response = send_a_can_event(client, LP_LEVEL_FULL)

    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.GENERATOR_COOLDOWN
        )
    )
    assert response.status_code == 200
    assert response.json().get('active') is False
    # assert response.json().get('')

    response = client.put(
        f'/api/energy/ge/1/state',
        json={
            'mode': EventValues.RUN
        }
    )
    assert response.status_code == 200

    # Get Fuel Level
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.GENERATOR_COOLDOWN
        )
    )
    print('FUEL IS EMPTY', response)
    print('FUEL IS EMPTY', response.json())
    assert response.status_code == 200
    assert response.json().get('active') is True

    cnt = 1
    while cnt < 11:
        cnt += 1
        ts1 = datetime.now() + timedelta(seconds=40)

        while response.json().get('active') is True and ts1 > datetime.now():
            # query the state to check lock expirations
            response = client.get('/api/energy/ge/1/state')
            assert response.status_code == 200
            response = client.get(
                '/api/system/lk/{}/state'.format(
                    EventValues.GENERATOR_COOLDOWN
                )
            )
            assert response.status_code == 200

        if response.json().get('active') is None:
            assert cnt % 5 == 0
        else:
            assert response.json().get('active') is False
        # Fake a restart
        response = client.put(
            f'/api/energy/ge/1/state',
            json={
                'mode': EventValues.RUN
            }
        )
        assert response.status_code == 200


def test_lockout_parkbrake_slideout_awning_524T(client):
    '''Test Park Brake lockouts and its application to Slideout.'''
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524T',
            'optionCodes': '52N,31T,29J,52D'
        }
    )

    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.PARK_BRAKE_APPLIED
        )
    )
    print('Initial lockout status', response.json())
    # Lockouts are currently all active, in case of a positive
    # state like PARK BRAKE ENGAGED will be True, as such no
    # lockout might be present until states change
    assert response.status_code == 200
    assert response.json().get('active') is False

    response = send_a_can_event(
        client,
        RV1_PARK_BRAKE_RELEASED
    )

    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.PARK_BRAKE_APPLIED
        )
    )
    print('Lockout Status', response.json())
    assert response.status_code == 200
    assert response.json().get('active') is False

    # Check that lockout appears in awning state
    response = client.get(
        '/api/movables/aw/1/state'
    )
    print('Awning State - test', response.json())
    assert response.status_code == 200
    assert response.json().get('state', {}).get('warnings') != []

    # Check that lockout appears in slideout state
    response = client.get(
        '/api/movables/so/1/state'
    )
    print('Slideout State', response.json())
    assert response.status_code == 200
    assert response.json().get('state', {}).get('lockouts') != []

    response = send_a_can_event(
        client,
        RV1_PARK_BRAKE_ENGAGED
    )

    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.PARK_BRAKE_APPLIED
        )
    )
    print('Lockout Status', response.json())
    assert response.status_code == 200
    assert response.json().get('active') is True

    response = client.get(
        '/api/movables/so/1/state'
    )
    print('Slideout State', response.json())
    assert response.status_code == 200
    assert response.json().get('state', {}).get('lockouts') is None


def test_lockout_ignition_slideout_524T(client):
    '''Test ignition warning and its application to Slideout.'''
    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.IGNITION_ON
        )
    )
    print('Initial lockout status', response.json())
    # Lockouts are currently all active, in case of a positive
    # state like PARK BRAKE ENGAGED will be True, as such no
    # lockout might be present until states change
    assert response.status_code == 200
    assert response.json().get('active') is True

    response = send_a_can_event(
        client,
        RV1_IGNITION_OFF
    )

    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.IGNITION_ON
        )
    )
    print('Lockout Status', response.json())
    assert response.status_code == 200
    assert response.json().get('active') is False

    # Check that lockout appears in slideout state
    response = client.get(
        '/api/movables/so/1/state'
    )
    print('Slideout State', response.json())
    assert response.status_code == 200
    assert response.json().get('state', {}).get('warnings') != []

    response = send_a_can_event(
        client,
        RV1_IGNITION_ON
    )

    response = client.get(
        '/api/system/lk/{}/state'.format(
            EventValues.IGNITION_ON
        )
    )
    print('Lockout Status', response.json())
    assert response.status_code == 200
    assert response.json().get('active') is True

    response = client.get(
        '/api/movables/so/1/state'
    )
    print('Slideout State', response.json())
    assert response.status_code == 200
    assert response.json().get('state', {}).get('warnings') is None
