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

import signal
import pytest
import os
from common_libs import environment

_env = environment()

from conftest import client #, main_client

# # Combine api calls to save startup times
def test_run_both(client):  #, main_client):

    print("IOT get /vin")
    response = client.get("/vin", headers={})
    assert response.status_code == 200
    print(response.json(), "\n")
    assert response.json() != {}


    # print("Main get /vin")
    # response = main_client.get("/api/vehicle/vin", headers={})
    # assert response.status_code == 200
    # print(response.json(), "\n")
    # assert response.json() != {}


def test_check_OK_OTA(client):
    # create a simulated build version
    with open(_env.storage_file_path('latest_bld'), 'w') as f:
                f.write('fake build #')

    response = client.put("/ota_start")
    assert response.json().get('result') == 'OTA not ready.'

    # assert os.path.isfile(_env.storage_file_path("OK"))

