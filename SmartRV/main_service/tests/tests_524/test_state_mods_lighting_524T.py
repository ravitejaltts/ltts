import os
import sys
import logging
from datetime import datetime
import subprocess
import time

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app

import pytest
from main_service.tests.utils import (
    send_a_can_event,
    preset_helper,
    lighting_zone_helper
)


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,52N,33F,31P,33F,291'
            }
        )
        yield c


def test_get_put_lz_many_lighting_WM524T(client):
    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")
    logger.debug(f"Response {response.json()}")
    for zone in [2, 6, 17]:
        lighting_zone_helper(client, zone)


@pytest.mark.skip(reason='Need to find a way to get options for missing lighting zones to accept 404 as a valid response')
def test_sweep_all_lightzones_WM524T(client):
    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")
    logger.debug(f"Response {response.json()}")
    for i in range(17):
        lighting_zone_helper(client, i)
