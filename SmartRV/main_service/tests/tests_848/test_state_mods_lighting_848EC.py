import os
import sys
import logging
from datetime import datetime
import subprocess
import time

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

from main_service.wgo_main_service import app
from fastapi.testclient import TestClient
#from main_service.wgo_main_service import app
from importlib import reload

from main_service.tests.utils import (
    send_a_can_event,
    preset_helper,
    lighting_zone_helper
)

import pytest


# subprocess.call(["sed -i -e 's/WM524T/848EC/g' /storage/UI_config.ini"], shell=True)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_get_put_lz_many_lighting(client):
    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")
    logger.debug(f"Response {response.json()}")
    for zone in [2,6]:
        lighting_zone_helper(client, zone)


def test_get_put_lz_state_lighting(client):
    zone = 2
    lighting_zone_helper(client, zone)


def test_get_put_lz_many_lighting_848EC(client):
    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")
    logger.debug(f"Response {response.json()}")

    for zone in [3, 6]:
        lighting_zone_helper(client, zone)


@pytest.mark.skip(reason='Need to figure out desired default state to save a fresh lighting zone in a preset')
def test_preset_848EC(client):
    preset_helper(client)


def test_switch_event_848EC(client):
    return #TODO fist this floorplan switch
    zone_id = 3

    msg = {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "11",
            "Instance": 0x0b,
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "1",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "0",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        }
    msg2 =  {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "11",
            "Instance": 0x0b,
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "0",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "0",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        }
    # 848EC Ignores the first can bus heartbeat - just once
    print('weowowowwo')
    response = send_a_can_event(client, data=msg)

    response = send_a_can_event(client, data=msg2)

    response = client.put(f"api/lighting/lz/{zone_id}/state", json={"onOff": 0})
    assert response.status_code == 200
    print(f"Put Response 1 \n {response.json()}")

    assert response.json().get("onOff") == 0

    response = send_a_can_event(client, data=msg)
    time.sleep(1)
    # Async needs time to complete ??
    response = send_a_can_event(client, msg)

    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response 2 \n {response.json()}")

    assert response.json().get(f"lz{zone_id}").get("onOff") == 1
    msg2 =  {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "11",
            "Instance": 0x0b,
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "0",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "0",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        }
    response = send_a_can_event(client, msg2)

    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response 3 \n {response.json()}")
    assert response.json().get(f"lz{zone_id}").get("onOff") == 0



def test_get_put_lz_state_lighting_848EC(client):
    zone = 2
    lighting_zone_helper(client, zone)
