import os
import sys
import logging
from datetime import datetime
import subprocess
import asyncio

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
import time

import random
import pytest
from common_libs.models.common import EventValues


@pytest.fixture
def client():
    with TestClient(app) as c:
        # c.put('/api/system/floorplan', json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,29J'})
        yield c


@pytest.mark.skip(reason='Cannot set brightness on non SECO displays reliably, so this test would require fakery to pass')
def test_system_display_brightness(client):
    response = client.put(
        "/api/system/display/brightness",
        json={
            'value': 100
        }
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('brightness') == 100

    response = client.put(
        "/api/system/display/brightness",
        json={
            'value': 10
        }
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('brightness') == 10

    response = client.put(
        "/api/system/display/brightness",
        json={
            'value': 51
        }
    )
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('brightness') == 51

    # Test that we cannot go lower than 10 (as set by the brightness model)
    response = client.put(
        "/api/system/display/brightness",
        json={
            'value': 0
        }
    )
    assert response.status_code == 422

    # Test that we cannot go higher than 100 (as set by the brightness model)
    response = client.put(
        "/api/system/display/brightness",
        json={
            'value': 101
        }
    )
    assert response.status_code == 422

    # Test that a non int convertable string fails properly with model validation
    response = client.put(
        "/api/system/display/brightness",
        json={
            'value': "DOM"
        }
    )
    assert response.status_code == 422
