import os
import sys
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

from fastapi.testclient import TestClient
from iot_service.wgo_iot_service import app
from common_libs.models.common import LogEvent

from iot_service.models.telemetry_msg import AlertMsg, RequestMsg
from common_libs.models.common import KeyValue, RVEvents, EventValues
import pytest

import signal

from conftest import client


# Combine api calls to save startup times
def test_twin(client):
    print("IOT /twin")
    response = client.get("/telemetry/twin_data", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")

    _opened = int((time.time() - 1) * 1000)
    nAlert = AlertMsg(
        id=str(_opened),
        type='also',
        code="bt120202",
        category="somesystem",
        instance="1",
        priority="priority",
        message="Hello my test Alert",
        header="msg",
        active=True,
        opened=_opened,
        dismissed=0,

    )


    response = client.put("/telemetry/alert", json=nAlert.dict())
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}


    response = client.get("/telemetry/alert_data", headers={})
    assert response.status_code == 200
    print("/telemetry/alert_data ",response.json(), "\n")
    # TODO: Figure out how to test with VIN
    # assert response.json() != {}



