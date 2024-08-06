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
        c.put('/api/system/floorplan', json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,29J'})
        yield c

# ACDC

def test_get_dc_status(client):
    response = client.get("api/electrical/dc/status")
    assert response.status_code == 200


def test_get_dc_status(client):
    dc_id = 0
    response = client.get(f"api/electrical/dc/{dc_id}")
    assert response.status_code == 200


def test_set_dc_status(client):
    return
    dc_id = 0
    response = client.put(
        f"api/electrical/dc/{dc_id}", json={"onOff": 1, "power": 0, "mode": 0}
    )
    assert response.status_code == 200
