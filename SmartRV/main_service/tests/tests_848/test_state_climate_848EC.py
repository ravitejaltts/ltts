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


@pytest.fixture
def client():
    with TestClient(app) as c:
        #c.put('/api/system/floorplan', json={'floorPlan': '848EC'})
        yield c


# # Plugin 1
# @pytest.hookimpl(tryfirst=True)
# def pytest_collection_modifyitems(items):
#     return
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print("Changing Floorplan to 848EC")
#     logger.debug("Changing Floorplan to 848EC")
#     subprocess.call(["sed -i -e 's/WM524T/848EC/g' /storage/UI_config.ini"], shell=True)


@pytest.mark.skip('Flooplan for 848 not ready.')
def test_climate_for_848EC(client):
    msg = {
        "title": "Setting cold",
        "Instance": "55",
        "Ambient_Temp": "3",
        "name": "thermostat_ambient_status",
    }

    response = send_a_can_event(client, msg)

    response = client.get("/api/climate/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")
    assert response.json().get("rf1").get("temp") is not None
