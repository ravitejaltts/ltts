import os
import sys
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

from fastapi.testclient import TestClient
from iot_service.wgo_iot_service import app
from common_libs.models.common import LogEvent

from common_libs.models.common import KeyValue, RVEvents, EventValues
import pytest

import signal

from conftest import client


# Combine api calls to save startup times
def test_get_endpoints(client):
    print("IOT /status")
    response = client.get("/status", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}

    print("IOT get /vin")
    response = client.get("/vin", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}

    print("IOT get /far_field_token")
    # Skip Requires main to run
    response = client.get("/far_field_token", headers={})
    assert response.status_code == 503
    print(response.json(), "\n")
    assert response.json() != {}

    print("IOT get /device_id")
    response = client.get("/device_id", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}

    print("IOT get /telemetry/twin_data")
    response = client.get("/telemetry/twin_data", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    #assert response.json() != {}

    print("IOT get /telemetry/new_twin_data")
    response = client.get("/telemetry/new_twin_data", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    #assert response.json() != {}

    print("IOT get /telemetry/alert_data")
    response = client.get("/telemetry/alert_data", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    #assert response.json() != {}

    print("IOT get /latest_events")
    response = client.get("/latest_events", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}

    print("IOT get /telemetry/header")
    response = client.get("/telemetry/header", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}

    assert response.json().get('mdl') == ''
    assert response.json().get('flr') == ''

