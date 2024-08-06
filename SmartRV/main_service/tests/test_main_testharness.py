
import os
import sys
import logging
from datetime import datetime
import pytest
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath('./..'))
sys.path.append(os.path.abspath('.'))

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

##TESTHARNESS

def test_testharness_status(client):
    response = client.get('/testharness/status')
    assert response.status_code == 200


def test_testharness_quickactions(client):
    response = client.get('/testharness/quick_actions')
    assert response.status_code == 200


def test_testharness_notifications(client):
    response = client.put('/testharness/notifications', json = {})
    assert response.status_code == 200


def test_testharness_state(client):
    response = client.put('/testharness/state', json = {})
    assert response.status_code == 200


def test_testharness_state_value(client):
    response = client.put('/testharness/state_value', json = {})
    assert response.status_code == 200


def test_testharness_proximity(client):
    response = client.put('/testharness/proximity', json = {"proximity_state": "NO_CHANGE"})
    assert response.status_code == 200


# NOTE: Removed this API endpoint for now
# def test_raw_can(client):
#     response = client.put(
#         '/testharness/raw_can',
#         json={
#             "can_interface": "canb0s0",
#             "cansend": "19FF0444#0102030405060708"
#         }
#     )
#     assert response.status_code == 200


def test_testharness_stats(client):
    response = client.get('/testharness/stats')
    assert response.status_code == 200


@pytest.mark.skip(reason="ui_debug feature might need to be removed from test harness, has not been maintained.")
def test_testharness_ui_debug(client):
    response = client.put('/testharness/ui_debug')
    assert response.status_code == 200


def test_testharness_screenshot(client):
    response = client.get('/testharness/screenshot')
    assert response.status_code == 200


def test_testharness_algo(client):
    response = client.put('/testharness/algo/climate', json = {"onOff": 1})
    assert response.status_code == 200


def test_testharness_algo_name(client):
    algo_name = 'climate'
    response = client.get(f'/testharness/algo/{algo_name}')
    assert response.status_code == 200


def test_testharness_config(client):
    response = client.get('/testharness/config')
    assert response.status_code == 200


def test_testharness_config_set(client):
    response = client.put(
        '/testharness/config',
        json = {
            'cfg_key': 'test',
            'cfg_value': 'theworld'
        }
    )
    assert response.status_code == 200

    response = client.get('/testharness/config')
    print(response)


def test_spotcheck_watersystems_component_init(client):
    '''This test shall spot check that components across all categories initialize.'''
    # Test waterystems
    # {
    #     "instance": 1,
    #     "category": "watersystems",
    #     "meta": null,
    #     "code": "wp",
    #     "properties": null,
    #     "attributes": {
    #         "name": "Fresh Water Pump",
    #         "description": "Fresh Water Pump",
    #         "type": "FRESH"
    #     },
    #     "optionCodes": null,
    #     "relatedComponents": null,
    #     "eventIds": {
    #         "onOff": 5200
    #     },
    #     "type": "FRESH|GREY|BLACK|PROPANE|?",
    #     "componentId": "watersystems.wp_default",
    #     "state": {
    #         "onOff": 0
    #     }
    # }
    response = client.get('/testharness/component/watersystems/water_pump/1')
    assert response.status_code == 200
    print('Response', response)
    assert response.json().get('instance') == 1
    assert response.json().get('state') != None
    assert response.json().get('attributes') != None
    assert response.json().get('eventIds') != None
    assert response.json().get('eventIds', {}).get('onOff') == RVEvents.WATER_PUMP_OPERATING_MODE_CHANGE


def test_spotcheck_energy_component_init(client):
    '''This test shall spot check that components across all categories initialize.'''
    # {
    #     "instance": 1,
    #     "category": "energy",
    #     "meta": null,
    #     "code": "bm",
    #     "properties": null,
    #     "attributes": {
    #         "type": "LITHIONICS",
    #         "batCnt": {
    #         "description": "How many battieries/modules are connected to this BMS",
    #         "propertyType": "integer",
    #         "minimum": 1
    #         },
    #         "name": "battery management",
    #         "nominalVoltage": "12.8V"
    #     },
    #     "optionCodes": null,
    #     "relatedComponents": null,
    #     "eventIds": {
    #         "temp": 7800,
    #         "soc": 7809,
    #         "vltg": 7801,
    #         "dcCur": 7802,
    #         "dcPwr": 7803,
    #         "tte": 7808,
    #         "minsTillFull": 7807,
    #         "minsTillEmpty": 7806
    #     },
    #     "description": "No description",
    #     "type": "LITHIONICS",
    #     "componentId": "energy.bm_basic",
    #     "state": {
    #         "temp": null,
    #         "soc": 0,
    #         "vltg": 0,
    #         "dcCur": 0,
    #         "dcPwr": 0,
    #         "tte": 523,
    #         "minsTillFull": null,
    #         "minsTillEmpty": null
    #     }
    # }
    response = client.get('/testharness/component/energy/battery_management/1')
    assert response.status_code == 200
    assert response.json().get('instance') == 1
    assert response.json().get('state') is not None
    assert response.json().get('state', {}).get('temp') is None
    assert response.json().get('attributes') is not None
    assert response.json().get('eventIds') is not None
    assert response.json().get('eventIds', {}).get('temp') == 7800


def test_spotcheck_climate_component_init(client):
    '''This test shall spot check that components across all categories initialize.
    {
      "instance": 1,
      "category": "climate",
      "meta": null,
      "code": "th",
      "properties": null,
      "attributes": {
        "name": "Thermostat",
        "description": {
          "description": "Describes the component for internal use",
          "propertyType": "string",
          "default": ""
        }
      },
      "optionCodes": null,
      "relatedComponents": null,
      "eventIds": {
        "onOff": null,
        "temp": 6802,
        "setTempHeat": 6803,
        "setTempCool": 6804,
        "setMode": null,
        "mode": 6816,
        "unit": null
      },
      "min_setable": 15.5,
      "max_setable": 35,
      "band": 3,
      "componentId": "climate.th_virtual",
      "state": {
        "onOff": 1,
        "temp": null,
        "setTempHeat": 20.555555555555557,
        "setTempCool": 23.555555555555557,
        "setMode": 517,
        "mode": 0,
        "unit": "C"
      }
    }'''

    response = client.get('/testharness/component/climate/thermostat/1')
    assert response.status_code == 200
    assert response.json().get('instance') == 1
    assert response.json().get('state') is not None
    # Is this true to be none here?
    #assert response.json().get('state', {}).get('temp') is None
    assert response.json().get('attributes') is not None
    assert response.json().get('eventIds') is not None
    assert response.json().get('eventIds', {}).get('temp') == RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE


@pytest.mark.skip(reason="Lighting is not converted to the new component style yet")
def test_spotcheck_lighting_component_init(client):
    '''This test shall spot check that components across all categories initialize.'''
    response = client.get('/testharness/component/lighting/lighting_zone/1')
    assert response.status_code == 200
    assert response.json().get('instance') == 1
    assert response.json().get('state') is not None
    assert response.json().get('state', {}).get('temp') is None
    assert response.json().get('attributes') is not None
    assert response.json().get('eventIds') is not None
    # assert response.json().get('eventIds', {}).get('temp') == 7800
