import time

import pytest

from fastapi.testclient import TestClient

from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
from main_service.tests.can_messages import (
    SHORE_INVALID,
    SHORE_1200W,
    GENERATOR_RUNNING,
    GENERATOR_STOPPED
)

from common_libs.models.common import EventValues, RVEvents


PROPANE_FULL = {
    "title": 'Fuel Tank - LP - 100 %',
    "Instance": 4,
    "Fluid_Type": "PROPANE",
    "Fluid_Level": str(100),
    # "Tank_Capacity": "0.1136",
    # "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}

PROPANE_EMPTY = {
    "title": 'Fuel Tank - LP - 0 %',
    "Instance": 4,
    "Fluid_Type": "PROPANE",
    "Fluid_Level": str(0),
    # "Tank_Capacity": "0.1136",
    # "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}

PROPANE_HALF = {
    "title": 'Fuel Tank - LP - 50 %',
    "Instance": 4,
    "Fluid_Type": "PROPANE",
    "Fluid_Level": str(50),
    # "Tank_Capacity": "0.1136",
    # "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}




# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     return
#     logger.debug("Changing Floorplan to 848EC")
#     subprocess.call(["sed -i -e 's/WM524T/848EC/g' /storage/UI_config.ini"], shell=True)



@pytest.fixture
def client():
    '''Create test client and set option codes / floorplan for this file.'''
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,29J'
            }
        )
        yield c


# @pytest.mark.skip(reason='Fails in pipeline for no good reason, path issues on import')
def test_ui_energy_generator(client):
    '''Test that the generator UI does show the desired values.'''
    # Set Shore power invalid
    send_a_can_event(client, SHORE_INVALID)
    # Set Generator Running
    send_a_can_event(client, GENERATOR_RUNNING)
    # Set Shore power input
    send_a_can_event(client, SHORE_1200W)
    # Check that shore source is 0
    response = client.get('/ui/ems/')
    # Check that generator is the correct value
    assert response.status_code == 200
    sources = response.json().get('items', [])[0]
    source_widgets = sources.get('widgets', [])
    assert source_widgets[2].get('name') == 'EmsGeneratorWidget'
    assert source_widgets[2].get('active') == EventValues.TRUE
    assert source_widgets[2].get('subtext') == 1200
    # Check that Shore does not have active
    assert source_widgets[1].get('name') == 'EmsShoreWidget'
    assert source_widgets[1].get('active') == EventValues.FALSE
    assert source_widgets[1].get('subtext') == '--'

    # Turn Generator off
    send_a_can_event(client, GENERATOR_STOPPED)
    # Resend power
    send_a_can_event(client, SHORE_1200W)
    # flip check
    response = client.get('/ui/ems/')
    # Check that generator is the correct value
    assert response.status_code == 200
    sources = response.json().get('items', [])[0]
    source_widgets = sources.get('widgets', [])
    assert source_widgets[2].get('name') == 'EmsGeneratorWidget'
    assert source_widgets[2].get('active') == EventValues.FALSE
    assert source_widgets[2].get('subtext') == '--'
    # Check that Shore does not have active
    assert source_widgets[1].get('name') == 'EmsShoreWidget'
    assert source_widgets[1].get('active') == EventValues.TRUE
    assert source_widgets[1].get('subtext') == 1200

    send_a_can_event(client, SHORE_INVALID)

    response = client.get('/ui/ems/')
    # Check that generator is the correct value
    assert response.status_code == 200
    sources = response.json().get('items', [])[0]
    source_widgets = sources.get('widgets', [])
    assert source_widgets[2].get('name') == 'EmsGeneratorWidget'
    assert source_widgets[2].get('active') == EventValues.FALSE
    assert source_widgets[2].get('subtext') == '--'
    # Check that Shore does not have active
    assert source_widgets[1].get('name') == 'EmsShoreWidget'
    assert source_widgets[1].get('active') == EventValues.FALSE
    assert source_widgets[1].get('subtext') == '--'

# Removed from UI
# def test_ui_energy_shore(client):
#     response = client.get('/ui/shore/')
#     assert response.status_code == 200


# def test_ui_energy_solar(client):
#     response = client.get('/ui/solar/')
#     assert response.status_code == 200
