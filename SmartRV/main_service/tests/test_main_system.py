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
        yield c


def test_get_system_status(client):
    return

    response = client.get("api/system/status")
    assert response.status_code == 200


def test_get_cpu_details(client):
    return
    response = client.get("api/system/cpu")
    assert response.status_code == 200


def test_get_system_memory_details(client):
    return
    response = client.get("api/system/memory")
    assert response.status_code == 200


def test_get_system_process_details(client):
    return
    response = client.get("api/system/processes")
    assert response.status_code == 200


def test_get_system_process_details(client):
    return
    proc_id = 1
    response = client.get("api/system/process/{proc_id}")
    assert response.status_code == 200


def test_set_display_brightness(client):
    return
    response = client.put("api/system/display/brightness", json={"value": 100})
    assert response.status_code == 200


def test_door_lock(client):
    return
    onOff_values = [0, 1]
    for value in onOff_values:
        response = client.put("api/system/doorLock", json={"onOff": value})
        assert response.status_code == 200


def test_display_on(client):
    return
    response = client.put("api/system/display/on")
    assert response.status_code == 200


def test_display_off(client):
    return
    response = client.put("api/system/display/off")
    assert response.status_code == 200


def test_display_autodimming(client):
    return
    values = [0, 1, 2, 5]
    for value in values:
        response = client.put("api/system/display/autodimming", json={"value": value})
        assert response.status_code == 200


# what goes into this api?
def test_service_restart(client):
    return
    response = client.put("api/system/service/{service}/restart")
    assert response.status_code == 200


def test_set_screen_inactive(client):
    return
    response = client.put("api/system/activity/off")
    assert response.status_code == 200


def test_system_shutdown(client):
    return
    response = client.put("api/system/shutdown")
    assert response.status_code == 200


def test_system_reboot(client):
    return
    response = client.put("api/system/reboot")
    assert response.status_code == 200


def test_system_floorplan(client):
    response = client.get("/api/system/floorplan")
    assert response.status_code == 200


def test_get_system_floorplans_available(client):
    response = client.get("/api/system/floorplans_available")
    assert response.status_code == 200


def test_system_ifconfig(client):
    return
    response = client.get("api/system/ifconfig")
    assert response.status_code == 200


def test_system_check_passcode(client):
    return
    response = client.put("api/system/passcode", json={"passcode": 0})
    assert response.status_code == 200


def test_system_configure_passcode(client):
    return
    response = client.put(
        "api/system/passcode/setting", json={"passcode": 1234, "isProtected": True}
    )
    assert response.status_code == 200


def test_set_date(client):
    return
    response = client.put("api/system/setdate", json={"value": "06-28-2023"})
    assert response.status_code == 200


def test_set_clock(client):
    return
    response = client.put("api/system/setclock", json={"value": "05:21", "item": "pm"})
    assert response.status_code == 200


def test_set_autosync(client):
    return
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put("api/system/timezone/autosync", json={"onOff": onOff})
        assert response.status_code == 200


def test_set_location_on(client):
    return
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put("api/system/location", json={"onOff": onOff})
        assert response.status_code == 200


def test_set_location_on(client):
    return
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put("api/system/location", json={"onOff": onOff})
        assert response.status_code == 200


def test_set_distance_unit(client):
    response = client.put(
        "api/system/distance", json={"value": 1, "item": "DistanceUnits"}
    )
    assert response.status_code == 200


def test_set_distance_unit(client):
    response = client.put(
        "api/system/distance", json={"value": 0, "item": "DistanceUnits"}
    )
    assert response.status_code == 200


def test_set_appearance_onoff(client):
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put("api/system/appearance", json={"onOff": onOff})
        assert response.status_code == 200


def test_set_appearance_onoff(client):
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put("api/system/appearance", json={"onOff": onOff})
        assert response.status_code == 200


def test_pushnotification_onoff(client):
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put("api/system/pushnotification", json={"onOff": onOff})
        assert response.status_code == 200


def test_set_manual_timezone(client):
    response = client.put(
        "api/system/timezone/settings",
        json={"value": "Central", "item": "TimeZonePreference"},
    )
    assert response.status_code == 200

def test_datareset(client):
    bool_values = [True, False]
    for bool in bool_values:
        response = client.put("api/system/datareset", json = {"are_you_sure": bool})
        assert response.status_code == 200
