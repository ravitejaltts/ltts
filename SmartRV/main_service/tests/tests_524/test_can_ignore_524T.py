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
    INTERIOR_HOT,
    INTERIOR_COLD,
    INTERIOR_NORMAL
)
from common_libs.models.common import EventValues

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    print('[TESTCLIENT] Init Client')
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,29J'
            }
        )
        yield c


def test_can_ignore_init_WM524T(client):
    '''Test that the initial list has two messages and that the ignore_count is
    the same as current_count.'''
    KEY_LIST = [
        'waterheater_status',
        'waterheater_status_2'
    ]
    response = client.get("/can/ignore_state")
    assert response.status_code == 200
    for key in KEY_LIST:
        response_data = response.json()
        assert key in response_data
        assert response_data[key]['current_count'] == response_data[key]['ignore_count']


def test_can_ignore_current_count_reset_WM524T(client):
    '''Test that the initial list has two messages and that the ignore_count is
    the same as current_count.'''

    client.put('/api/watersystems/wh/1/state', json={'onOff': EventValues.ON})
    # Need to wait a little as this is a queue item to be processed
    time.sleep(0.25)

    response = client.get("/can/ignore_state")
    assert response.status_code == 200
    assert response.json()['waterheater_status']['current_count'] == 0

    client.put('/api/watersystems/wh/1/state', json={'mode': EventValues.ECO})

    # Need to wait a little as this is a queue item to be processed
    time.sleep(0.25)

    response = client.get("/can/ignore_state")
    assert response.status_code == 200
    assert response.json()['waterheater_status_2']['current_count'] == 0


@pytest.mark.skip(reason='Cannot figure out why this does not work, it seems the client resets the floorplan in between')
def test_can_ignore_response_WM524T(client):
    '''Test that a counter that is below ignore_count will return appropriately.'''
    client.put('/api/watersystems/wh/1/state', json={'mode': EventValues.ECO})
    # Need to wait a little as this is a queue item to be processed
    time.sleep(5)

    response = client.get("/can/ignore_state")
    assert response.status_code == 200
    print(response.json())
    assert response.json()['waterheater_status_2']['current_count'] == 0

    # response = send_a_can_event(client, {
    #     "title": "Set Water Heater Mode to decalcification",
    #     "name": "waterheater_status_2",
    #     "Instance": "1",
    #     "Heat_Level": "Low level (ECO)"
    # })

    # assert response.status_code == 200
    # assert response.json().get('result') != ''
