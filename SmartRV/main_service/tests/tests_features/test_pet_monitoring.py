import os
import sys
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
import pytest

from main_service.wgo_main_service import app

from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import INTERIOR_HOT, INTERIOR_COLD
from common_libs.models.common import RVEvents, EventValues
from main_service.components.inputs.pet_minder import pet_alerts
from common_libs.models.notifications import NotificationPriority as priority
from common_libs.models.notifications import priority_to_level

BASE_URL = '/api/features/pm/'

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
def client():
    with TestClient(app) as c:
        # Get current floorplan and options and save
        current_floorplan = c.get(
            '/api/system/floorplan'
        ).json()
        current_optioncodes = c.get(
            '/api/system/optioncodes'
        ).json()
        current_optioncodes = ','.join(current_optioncodes)
        print('PyTest Client Current Floorplan', current_floorplan, current_optioncodes)
        # Put floorplan
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,52N,33F,31P,33F,29J'
            }
        )
        yield c
        # Reset floorplan and options
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': current_floorplan,
                'optionCodes': current_optioncodes
            }
        )


# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print("Changing Floorplan to WM524T")
#     logger.debug("Changing Floorplan to WM524T")
#     subprocess.call("sed -i -e 's/848EC/WM524T/g' /storage/UI_config.ini", shell=True)


@pytest.mark.asyncio
async def test_pm_defaults(client):
    # msg = {
    #     "Instance": "1",
    #     "Position": "10",
    #     "Motion": "No motion",
    #     "name": "Awning_Status"
    # }

    # response = send_a_can_event(client, msg)

    response = client.get(BASE_URL + '1/state')
    assert response.status_code == 200

    print('RESPONSE PM', response.json())

    assert response.json().get("onOff") is not None
    assert response.json().get("enabled") is not None
    assert response.json().get("minTemp") is not None
    assert response.json().get("maxTemp") is not None


@pytest.mark.asyncio
async def test_pm_onoff(client):
    '''Test PM feature

    1. Default state
    2. Turning off and see that it is removed from UI home API
    3. Turn On and see it reports again
    4. Turn On and Enable and check that works.'''
    response = client.put(
        BASE_URL + '1/state',
        json={
            'onOff': EventValues.OFF
        }
    )
    assert response.status_code == 200
    assert response.json().get("onOff") == EventValues.OFF
    # Enabled should automatically turn off then
    assert response.json().get("enabled") == EventValues.OFF
    # UI - Check that petmonitoring is gone
    response = client.get('/ui/home')
    assert response.status_code == 200
    assert response.json().get("petmonitoring") is None

    # Turn it back on
    response = client.put(
        BASE_URL + '1/state',
        json={
            'onOff': EventValues.ON
        }
    )
    assert response.status_code == 200
    assert response.json().get("onOff") == EventValues.ON
    # Does not auto enable the feature
    assert response.json().get("enabled") == EventValues.ON
    # Check the Home UI endpoint showing the petmonitoring data

    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    logger.debug(current_notifications)

    for t_note in current_notifications:
        response = client.put(f"/ui/notifications/{t_note.get('id')}/dismiss")

    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    assert current_notifications == []

    response = client.get('/ui/home')
    assert response.status_code == 200

    assert response.json().get("petmonitoring") is not None

    response = client.put(
        BASE_URL + '1/state',
        json={
            'enabled': EventValues.ON
        }
    )
    assert response.status_code == 200
    assert response.json().get("onOff") == EventValues.ON
    # Does not auto enable the feature
    assert response.json().get("enabled") == EventValues.ON


@pytest.mark.asyncio
async def test_pm_status_hot(client):
    '''Test PM feature

    1. Turn on and enable
    2. Send high temp value
    3. Check UI state reflects the status and severity
    4. TBD'''
    response = client.put(
        BASE_URL + '1/state',
        json={
            'onOff': EventValues.ON,
            'enabled': EventValues.ON,
            "minTemp": 18,
            "maxTemp": 30,
            "unit": "C"
        }
    )
    assert response.status_code == 200
    assert response.json().get("onOff") == EventValues.ON
    assert response.json().get("enabled") == EventValues.ON

    # Send CAN message
    # UI - Check that petmonitoring is gone
    response = client.get('/ui/home')
    assert response.status_code == 200
    assert response.json().get("petmonitoring") is not None

    tstat = {
        "onOff": 1,
        "setTempHeat": 61,
        "setTempCool": 71,
        "setMode": EventValues.COOL,
        "unit": "F"
    }

    response = client.put("/api/climate/th/1/state", json=tstat)
    assert response.status_code == 200
    await asyncio.sleep(1)

    response = send_a_can_event(client, INTERIOR_HOT)

    await asyncio.sleep(1)
    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    logger.debug(current_notifications)

    for t_note in current_notifications:
        response = client.put(f"/ui/notifications/{t_note.get('id')}/dismiss")
        await asyncio.sleep(2)


    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    assert current_notifications == []

    response = client.get('/ui/home')
    assert response.status_code == 200
    pet_mon = response.json().get("petmonitoring")
    print('UI PETMON', pet_mon)
    pet_alert_items = pet_alerts.get('PM14', {})

    assert pet_mon.get('status', {}).get('level') == priority_to_level(priority.Pet_Minder_Warning)
    assert pet_mon.get('status', {}).get('title') == pet_alert_items.get('Headline', None)
    assert pet_alert_items.get('Temp Status', None)[:35] in pet_mon.get('status', {}).get('subtitle')
    assert pet_mon.get('status', {}).get('body') == pet_alert_items.get('Short Description', None)

    tstat = {
        "onOff": 1,
        "setMode": EventValues.HEAT,
    }

    response = client.put("/api/climate/th/1/state", json=tstat)

    assert response.status_code == 200
    await asyncio.sleep(1)

    response = send_a_can_event(client, INTERIOR_HOT)

    await asyncio.sleep(1)

    current_notifications = client.get(
            '/ui/notifications'
        ).json()

    for t_note in current_notifications:
        response = client.put(f"/ui/notifications/{t_note.get('id')}/dismiss")
        await asyncio.sleep(1)

    response = client.get('/ui/home')
    assert response.status_code == 200
    pet_mon = response.json().get("petmonitoring", {})
    pet_alert_items = pet_alerts.get('PM10', {})

    assert pet_mon.get('status', {}).get('level') == priority_to_level(priority.Pet_Minder_Warning)
    assert pet_mon.get('status', {}).get('title') == pet_alert_items.get('Headline', None)
    # assert pet_alert_items.get('Temp Status', None)[:35] in pet_mon.get('status', {}).get('subtitle')
    assert pet_mon.get('status', {}).get('body') == pet_alert_items.get('Short Description', None)


# @pytest.mark.skip(reason='Cannot figure out why the test uses an external python file to check for something that is stored in alerts.py')
@pytest.mark.asyncio
async def test_pm_status_cold(client):
    '''Test PM feature

    1. Turn on and enable
    2. Send low temp value
    3. Check UI state reflects the status and severity
    4. TBD'''
    response = client.put(
        BASE_URL + '1/state',
        json={
            'onOff': EventValues.ON,
            'enabled': EventValues.ON,
            "minTemp": 18,
            "maxTemp": 28,
            "unit": "C"
        }
    )
    assert response.status_code == 200
    assert response.json().get("onOff") == EventValues.ON
    assert response.json().get("enabled") == EventValues.ON

    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    logger.debug(current_notifications)

    for t_note in current_notifications:
        response = client.put(f"/ui/notifications/{t_note.get('id')}/dismiss")


    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    assert current_notifications == []

    # UI - Check that petmonitoring is gone
    response = client.get('/ui/home')
    assert response.status_code == 200
    assert response.json().get("petmonitoring") is not None

    # Send CAN message
    response = send_a_can_event(client, INTERIOR_COLD)

    await asyncio.sleep(1)

    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    logger.debug(current_notifications)

    for t_note in current_notifications:
        response = client.put(f"/ui/notifications/{t_note.get('id')}/dismiss")

    current_notifications = client.get(
            '/ui/notifications'
        ).json()
    assert current_notifications == []

    response = client.get('/ui/home')
    assert response.status_code == 200
    pet_mon = response.json().get("petmonitoring")
    print('UI PETMON', pet_mon)
    pet_alert_items = pet_alerts.get('PM4', {})

    assert pet_mon.get('status', {}).get('level') == priority_to_level(priority.Pet_Minder_Warning)
    assert pet_mon.get('status', {}).get('title') == pet_alert_items.get('Headline', None)
    assert pet_alert_items.get('Temp Status', None)[:35] in pet_mon.get('status', {}).get('subtitle')
    assert pet_mon.get('status', {}).get('body') == pet_alert_items.get('Short Description', None)

    # Set the heat on

    tstat = {
        "onOff": 1,
        "setTempHeat": 72,
        "setTempCool": 80,
        "setMode": EventValues.HEAT,
        "unit": "F"
    }

    response = client.put("/api/climate/th/1/state", json=tstat)

    assert response.status_code == 200

    response = send_a_can_event(client, INTERIOR_COLD)

    await asyncio.sleep(1)

    response = client.get('/ui/home')
    assert response.status_code == 200
    pet_mon = response.json().get("petmonitoring")
    print('UI PETMON', pet_mon)
    pet_alert_items = pet_alerts.get('PM8', {})

    assert pet_mon.get('status', {}).get('level') == priority_to_level(priority.Pet_Minder_Warning)
    assert pet_mon.get('status', {}).get('title') == pet_alert_items.get('Headline', None)
    assert pet_alert_items.get('Temp Status', None)[:35] in pet_mon.get('status', {}).get('subtitle')
    assert pet_mon.get('status', {}).get('body') == pet_alert_items.get('Short Description', None)


@pytest.mark.asyncio
async def test_pm_app_view(client):
    '''Test UI AppView'''
    response = client.get('/ui/appview')
    assert response.status_code == 200
    # Appview features are actually tabs and only the app view is shown
    # Get first item and the it is a list of Apps
    features = response.json()[0].get('items', [])
    pet_mon = None
    for feature in features:
        if feature.get('name') == 'AppFeaturePetMonitoring':
            pet_mon = feature
            break

    assert pet_mon is not None
    assert pet_mon.get('subtext') == 'On'
    assert pet_mon.get('title') == 'Pet Minder'
