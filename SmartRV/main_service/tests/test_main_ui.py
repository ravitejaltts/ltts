import logging
from datetime import datetime

from fastapi.testclient import TestClient
import pytest

from main_service.wgo_main_service import app

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,52N,31P,33F,29J'
            }
        )
        yield c


def test_get_state(client):
    '''Tests the new state endpoint that can hold sessions.'''
    response = client.get('/api/state')
    assert response.status_code == 200
    print(response.json())
    result = response.json()
    assert result.get('sessionId') is not None


def test_get_ui_home(client):
    response = client.get("/ui/")
    assert response.status_code == 200


def test_get_ui_energy(client):
    response = client.get("/ui/ems/")
    assert response.status_code == 200


def test_get_ui_lighting(client):
    response = client.get("/ui/lighting")
    assert response.status_code == 200


def test_get_ui_climate(client):
    response = client.get("/ui/climate")
    assert response.status_code == 200


def test_get_ui_watersystems(client):
    response = client.get("/ui/watersystems/")
    assert response.status_code == 200

def test_get_ui_petminder(client):
    response = client.get("/ui/petmonitoring")
    assert response.status_code == 200

def test_get_ui_generator(client):
    response = client.get("/ui/generator/")
    assert response.status_code == 200


# Refrigerator
@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_success_fullhistory(client):
    current_date = datetime.now().strftime("%Y-%m-%d")
    response = client.put("/ui/refrigerator/fullhistory",
                          json={"date": current_date})
    assert response.status_code == 200


@pytest.mark.skip(reason='Refrigerator feature disabled until sensors are working')
def test_fail_fullhistory(client):
    response = client.put("/ui/refrigerator/fullhistory",
                          json={"date": "01-01-2023"})
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
    response_1 = client.put(
        "/api/climate/refrigerator/freezer/settings/restoredefault",
        json={"applianceType": "refrigerator"}
    )
    assert response_1.status_code == 200

    response_2 = client.put(
        "/api/climate/refrigerator/freezer/settings/restoredefault",
        json={"applianceType": "freezer"}
    )
    assert response_2.status_code == 200


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


@pytest.mark.skip(reason="This API works fine during proper runtime, need to evaluate why this fails as a test")
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
    response = client.get("/ui/slider")
    assert response.status_code == 200


def test_motd(client):
    return
    response = client.get("/ui/motd")
    assert response.status_code == 200


def test_reload_mock_db(client):
    return
    response = client.get("/ui/test_reload_mock_db")
    assert response.status_code == 200

# movables


def test_get_slideout_screen(client):
    response = client.get("/ui/movables/so/screen")
    assert response.status_code == 200


def test_get_slideout_warning(client):
    response = client.get("/ui/movables/so/warning")
    assert response.status_code == 200


def test_get_slideout_settings(client):
    response = client.get("/ui/movables/so/settings")
    assert response.status_code == 200


def test_set_slideout_understand(client):
    response = client.put("/ui/movables/so/understand")
    assert response.status_code == 200


def test_get_awning_screen(client):
    response = client.get("/ui/movables/aw/screen")
    assert response.status_code == 200


def test_get_awning_warning(client):
    response = client.get("/ui/movables/aw/warning")
    assert response.status_code == 200


def test_get_awning_settings(client):
    response = client.get("/ui/movables/aw/settings")
    assert response.status_code == 200


def test_set_awning_understand(client):
    response = client.put("/ui/movables/aw/understand")
    assert response.status_code == 200
