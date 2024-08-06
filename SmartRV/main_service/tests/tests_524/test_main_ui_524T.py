import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
import pytest

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        print('Creating new instance of app')
        print('Test Client Response', c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52N,52D,33F,31P,33F,29J'
            }
        ))
        yield c


@pytest.mark.skip(reason='Duplicate and reworked endpoint, remove this test')
def test_get_state(client):
    response = client.get("/api/state", headers={})
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {}


@pytest.mark.skip(reason='Reworking the purpose of this endpoint')
def test_get_lighting(client):
    response = client.get("/api/lighting")
    assert response.status_code == 200
    logger.debug(response.json())
    assert response.json().get("count") > 0


def test_get_ui_home(client):
    response = client.get("/ui/")
    assert response.status_code == 200


def test_get_ui_energy(client):
    response = client.get("/ui/ems/")
    assert response.status_code == 200


def test_get_ui_lighting(client):
    response = client.get("/ui/lighting")
    assert response.status_code == 200


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_get_ui_refrigerator(client):
    response = client.get("/ui/refrigerator/")
    assert response.status_code == 200


def test_get_ui_climate(client):
    response = client.get("/ui/climate")
    assert response.status_code == 200


def test_get_ui_watersystems(client):
    response = client.get("/ui/watersystems/")
    assert response.status_code == 200


# refrigerator
@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_success_fullhistory(client):
    current_date = datetime.now().strftime("%Y-%m-%d")
    response = client.put("/ui/refrigerator/freezer/fullhistory", json={"date": current_date})
    assert response.status_code == 200


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_fail_fullhistory(client):
    response = client.put("/ui/refrigerator/freezer/fullhistory", json={"date": "01-01-2023"})
    assert response.status_code == 400


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_get_ui_refrigerator(client):
    response = client.get("/ui/refrigerator/")
    print(response.content)
    assert response.status_code == 200


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_get_ui_refrigerator_settings(client):
    response = client.get("/ui/refrigerator/settings")
    assert response.status_code == 200


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_set_fridge_freezer_alert_control(client):
    response_1 = client.put(
        "/api/climate/refrigerator/freezer/settings/alert",
        json={"onOff": 1, "applianceType": "refrigerator"}
    )
    assert response_1.status_code == 200

    response_2 = client.put(
        "/api/climate/refrigerator/freezer/settings/alert",
        json={"onOff": 1, "applianceType": "freezer"}
    )
    assert response_2.status_code == 200


# TODO: put temprange and restoredefault refrigerator api's failing - to fix


# works in swagger(issues accessing DB)
@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_set_temprange(client):
    response_1 = client.put("/api/climate/refrigerator/freezer/settings/temprange",
    json={"applianceType": "refrigerator", "upper_limit": 3.33, "lower_limit": 1.11}
    )
    assert response_1.status_code == 200

    response_2 = client.put("/api/climate/refrigerator/freezer/settings/temprange",
    json={"applianceType": "freezer", "upper_limit": 0, "lower_limit": -4}
    )
    assert response_2.status_code == 200


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_put_refrigerator_temprange_restoredefault(client):
    response_1 = client.put("/api/climate/refrigerator/freezer/settings/restoredefault",
    json={"applianceType": "refrigerator"}
    )
    assert response_1.status_code == 200

    response_2 = client.put("/api/climate/refrigerator/freezer/settings/restoredefault",
    json={"applianceType": "freezer"}
    )
    assert response_2.status_code == 200


def test_set_thermostat_state(client):
    zone_id = 1
    response = client.put(
        f"/api/climate/zones/{zone_id}/thermostat/state",
        json={
            "mode": "COOL",
            "onOff": 1,
            "unit": "F",
            "setTempCool": 72,
            "setTempHeat": None,
        },
    )
    assert response.status_code == 200


@pytest.mark.skip('UI should use new state API instead of this mode change endpoint. Have an issue here')
def test_set_climate_zone_mode(client):
    zone_id = 1
    response = client.put(
        f"/api/climate/zones/{zone_id}/mode",
        json={
            "item": "ClimateMode",
            "value": 517
        }
    )
    assert response.status_code == 200


def test_set_zone_temp(client):
    zone_id = 1
    response = client.put(f'/api/climate/zones/{zone_id}/temp', json = {"mode": 517, "setTemp": 74, "unit": "F"})
    assert response.status_code == 200


def test_set_zone_schedule(client):
    return
    zone_id = 1
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put(
            f"/api/climate/zones/{zone_id}/schedule/onoff", json={"onOff": onOff}
        )
        assert response.status_code == 200


def test_run_demo_mode(client):
    return
    response = client.put("/api/lighting/demomode")
    assert response.status_code == 200


def test_get_water_settings(client):
    response = client.get("/ui/watersystems/settings")
    assert response.status_code == 200


def test_get_settings(client):
    response = client.get("/ui/lighting/settings")
    assert response.status_code == 200


def test_get_appview(client):
    response = client.get("/ui/appview")
    assert response.status_code == 200


def test_get_ems(client):
    response = client.get("/ui/ems/")
    assert response.status_code == 200


def test_get_ems_settings(client):
    response = client.get("/ui/ems/settings")
    assert response.status_code == 200


def test_get_climate_settings(client):
    response = client.get("/ui/climate/settings")
    assert response.status_code == 200


def test_get_schedule(client):
    response = client.get("/ui/climate/schedule")
    assert response.status_code == 200

@pytest.mark.skip(reason='Stalling in pytests here - possible router login?')

# works in swagger
def test_gui_functional(client):
    response = client.get("/ui/functionaltests/")
    assert response.status_code == 200


def test_gui_inverter(client):
    response = client.get("/ui/inverter/")
    assert response.status_code == 200


def test_gui_inverter(client):
    response = client.get("/ui/inverter/settings")
    assert response.status_code == 200


# works in swagger(issues accessing DB)
def test_ui_settings(client):
    response = client.get("/ui/settings/")
    assert response.status_code == 200


@pytest.mark.skip(reason="This test is redundant, see other test of the same name for separate skip reason")
def test_ui_notifications(client):
    response = client.get("/ui/notifications")
    assert response.status_code == 200


def test_ui_all_notifications(client):
    response = client.get("/ui/notifications/all")
    assert response.status_code == 200


# def test_ui_notifications_settings(client):
#     response = client.get("/ui/notifications/settings")
#     assert response.status_code == 200


def test_ui_notification_center(client):
    response = client.get("/ui/notifications/center")
    assert response.status_code == 200


def test_ui_notification_clearall(client):
    response = client.put("/ui/notifications/clearall")
    assert response.status_code == 200


def test_ui_home(client):
    response = client.get("/ui/home")
    assert response.status_code == 200


def test_ui(client):
    response = client.get("/ui/")
    assert response.status_code == 200


def test_ui_top(client):
    response = client.get("/ui/top")
    assert response.status_code == 200


def test_slider(client):
    return
    response = client.get("ui/slider")
    assert response.status_code == 200


def test_motd(client):
    return
    response = client.get("ui/motd")
    assert response.status_code == 200


def test_reload_mock_db(client):
    return
    response = client.get("ui/test_reload_mock_db")
    assert response.status_code == 200


# COMMUNICATION:


def test_geo_location(client):
    return
    response = client.get("api/connectivity/geo")
    assert response.status_code == 200


def test_cellular_on_off(client):
    return
    response = client.put("api/connectivity/cellular/onoff", json={"onOff": 1})
    assert response.status_code == 200


def test_cellular_comm(client):
    return
    response = client.get("api/connectivity/cellular")
    assert response.status_code == 200


def test_comm_wifi(client):
    return
    response = client.get("api/connectivity/wifi")
    assert response.status_code == 200


def test_comm_tz_offset(client):
    return
    response = client.get("api/connectivity/tz_offset")
    assert response.status_code == 200


# LIGHTING


@pytest.mark.skip(reason='Reworking the purpose of this endpoint')
def test_lighting_overview(client):
    response = client.get("api/lighting")
    assert response.status_code == 200


def test_lighting_state(client):
    response = client.get("api/lighting/state")
    assert response.status_code == 200


def test_set_lighting_lz(client):
    zone_id = 2
    response = client.put(
        f"api/lighting/lz/{zone_id}/state",
        json={"brt": 100, "onOff": 1, "rgb": "string", "clrTmp": 10000},
    )
    assert response.status_code == 200


def test_get_lighting_reset(client):
    response = client.put(f"api/lighting/reset")
    assert response.status_code == 200


def test_get_lighting_schemas(client):
    response = client.put(f"api/lighting/disco")
    assert response.status_code == 200

@pytest.mark.skip(reason="New pytest error - on NotImplementedError")
def test_get_watersystem_overview(client):
    with pytest.raises(NotImplementedError):
        print('Calling api/watersystems')
        response = client.get("/api/watersystems")


# WATERSYSTEMS


def test_get_watersystems_settings(client):
    response = client.get("/api/watersystems/settings")
    assert response.status_code == 200


def test_put_watersystems_settings(client):
    return
    response = client.put(
        "api/watersystems/settings", json={"item": 0, "value": "VolumeUnitPreference"}
    )
    assert response.status_code == 200


# def test_get_watersystem_schema(client):
#     response = client.get("api/watersystems/schemas")
#     assert response.status_code is not None


# SYSTEM:


def test_get_system_status(client):
    response = client.get("api/system/status")
    assert response.status_code == 501


def test_get_cpu_details(client):
    response = client.get("api/system/cpu")
    assert response.status_code == 501


def test_get_system_memory_details(client):
    response = client.get("api/system/memory")
    assert response.status_code == 501


def test_get_system_process_details(client):
    response = client.get("api/system/processes")
    assert response.status_code == 501


def test_get_system_process_details(client):
    proc_id = 1
    response = client.get("api/system/process/{proc_id}")
    assert response.status_code == 501


def test_set_display_brightness(client):
    response = client.put("api/system/display/brightness", json={"value": 100})
    assert response.status_code is not None


def test_door_lock(client):
    onOff_values = [0, 1]
    for value in onOff_values:
        response = client.put("api/system/doorLock", json={"onOff": value})
        assert response.status_code == 200


def test_display_on(client):
    response = client.put("api/system/display/on")
    assert response.status_code == 200


def test_display_off(client):
    response = client.put("api/system/display/off")
    assert response.status_code == 200


def test_display_autodimming(client):
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


def test_system_update(client):
    return
    response = client.put("api/system/otastart")
    assert response.status_code == 200

def test_system_floorplan(client):
    response = client.get("api/system/floorplan")
    assert response.status_code == 200


def test_get_system_floorplans_available(client):
    response = client.get("api/system/floorplans_available")
    assert response.status_code == 200


def test_system_ifconfig(client):
    response = client.get("api/system/ifconfig")
    assert response.status_code == 200


def test_system_check_passcode(client):
    response = client.put("api/system/passcode", json={"passcode": 0})
    assert response.status_code == 200


def test_system_configure_passcode(client):
    return
    response = client.put(
        "api/system/passcode/setting", json={"passcode": 1234, "isProtected": True}
    )
    assert response.status_code == 200


def test_set_date(client):
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


# #SETTINGS:


def test_api_main_settings(client):
    response = client.get("api/settings")
    assert response.status_code == 200


def test_bluetooth_pairing(client):
    response = client.get("api/settings/bluetooth/pairing")
    assert response.status_code == 200


def test_bluetooth_onoff(client):
    '''Test that API accepts BT on/off.'''
    response = client.put("api/settings/bluetooth/onoff", json={"onOff": 0})
    # In this test BT service is not present, as such should return Service Unavailable 503
    assert response.status_code == 503


def test_bluetooth_pairdevice(client):
    response = client.put(
        "api/settings/bluetooth/pairdevice",
        json={"name": "Iphone12", "connected": True, "macAddress": "44:01:BB:E0:90:9B"},
    )
    assert response.status_code == 200


def test_bluetooth_disconnect(client):
    response = client.put(
        "api/settings/bluetooth/disconnect",
        json={"name": "Iphone12", "connected": True, "macAddress": "44:01:BB:E0:90:9B"},
    )
    assert response.status_code == 200


def test_bluetooth_forgetdevice(client):
    response = client.put(
        "api/settings/bluetooth/forgetdevice",
        json={"name": "Iphone12", "connected": True, "macAddress": "44:01:BB:E0:90:9B"},
    )
    assert response.status_code == 200


def test_screenmode(client):
    values = ["LIGHT", "DARK"]
    for value in values:
        response = client.put("api/settings/browser/screenmode", json={"value": value})
        assert response.status_code == 200


def test_autosunset(client):
    return
    onOff_values = [0, 1]
    for onOff in onOff_values:
        response = client.put(
            "api/settings/browser/screenmode/autosunset", json={"onOff": onOff}
        )
        assert response.status_code == 200

# #FANS


def test_fan_status(client):
    response = client.get("api/fans/status")
    assert response.status_code == 200

##STATE


def test_get_full_state(client):
    response = client.get("api/state/full")
    assert response.status_code == 200


def test_get_callback_list(client):
    return
    response = client.get("api/state/callback")
    assert response.status_code == 501


def test_post_callback_register(client):
    return
    response = client.post("api/state/callback/register/")
    assert response.status_code == 200


def test_set_callback_update(client):
    return
    response = client.put("api/state/callback/{callback_id}/")
    assert response.status_code == 200


def test_delete_callback(client):
    return
    response = client.delete("api/state/callback/{callback_id}/")
    assert response.status_code == 200


def test_get_callback(client):
    return
    response = client.get("api/state/callback/{callback_id}")
    assert response.status_code == 200


# what is this api for?
def test_get_features_state(client):
    response = client.get("api/state")
    assert response.status_code == 200


##SENSORS

# ##VEHICLE


def test_get_ignition(client):
    response = client.get("/api/vehicle/ignition_key")
    assert response.status_code == 200


def test_get_vehicle_vin(client):
    response = client.get('/api/vehicle/vin')
    assert response.status_code == 200


def test_set_vehicle_vin(client):
    response = client.get("/api/vehicle/vin")
    assert response.status_code == 200


def test_get_vehicle_soc(client):
    response = client.get("/api/vehicle/soc")
    assert response.status_code == 200


##movables

def test_set_slideout_understand(client):
    response = client.put("/ui/movables/so/understand")
    assert response.status_code == 200


def test_get_slideout_settings(client):
    response = client.get("/ui/movables/so/settings")
    assert response.status_code == 200


def test_get_slideout_warning(client):
    response = client.get("/ui/movables/so/warning")
    assert response.status_code == 200


def test_get_slideout_screen(client):
    response = client.get("/ui/movables/so/screen")
    assert response.status_code == 200


def test_set_awning_understand(client):
    response = client.put("/ui/movables/aw/understand")
    assert response.status_code == 200


def test_get_awning_warning(client):
    response = client.get("/ui/movables/aw/warning")
    assert response.status_code == 200


def test_get_awning_screen(client):
    response = client.get("/ui/movables/aw/screen")
    assert response.status_code == 200


def test_get_awning_settings(client):
    response = client.get("/ui/movables/aw/settings")
    assert response.status_code == 200


# # Awnings

def test_ui_awning(client):
    response = client.get('/ui/movables/aw/screen')
    data = response.json()
    assert response.status_code == 200
    awnings = data.get('awnings')
    assert awnings is not None

    for awning in awnings:
        # Check if we only have the auto switches
        assert len(awning.get('switches', [])) == 2
        # Auto ExtendRetract Buttons have no subtext
        assert awning.get('switches')[0].get('subtext') is None
        assert awning.get('switches')[1].get('subtext') is None
        # assert awning.get('switches')[0].get('subtext') == 'Retract'
        # assert awning.get('switches')[1].get('subtext') == 'Extend'
