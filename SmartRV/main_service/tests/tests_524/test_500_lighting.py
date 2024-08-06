
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app

from common_libs.models.common import RVEvents, EventValues

import pytest

# # Plugin 1
# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print("Changing Floorplan to WM524T")
#     logger.debug("Changing Floorplan to WM524T")
#     subprocess.call(["sed -i -e 's/848EC/WM524T/g' /storage/UI_config.ini"], shell=True)

# TODO: Review endpoints if they could require a NotImplementError handler on success
# as some endpoints might not apply to a particular model


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes':
                    '52D,'
                    '33F,'
                    '31P,'
                    '33F,'
                    '291'
            }
        )
        yield c


@pytest.mark.skip(reason="New pytest error - on NotImplementedError")
def test_lighting_overview(client):
    # TODO: Fix test once properly implemented
    with pytest.raises(NotImplementedError):
        response = client.get('/api/lighting')


def test_lighting_state(client):
    response = client.get('/api/lighting/state')
    assert response.status_code == 200


def test_get_lighting_zone(client):
    zone_id = 2
    endpoint = f'/api/lighting/lz/{zone_id}/state'
    response = client.get(endpoint)
    assert response.status_code == 200


def test_set_lighting_zone(client):
    zone_id = 2
    response = client.put(
        f'/api/lighting/lz/{zone_id}/state',
        json={
            "brt": 100,
            "onOff": 1,
            "rgb": "string",        # Not required for 500 series, but should not break
            "clrTmp": 10000
        }
    )
    assert response.status_code == 200


def test_lighting_group_defaults(client):
    for lg in (0, 1, 2, 3):
        response = client.get(f'/api/lighting/lg/{lg}/state')
        assert response.status_code == 200


def test_activate_lighting_group_defaults(client):
    # Need to be sure we have saved the lg before we ask it to activate
    for lg in (1, 2, 3):
        response = client.put(
            f'/api/lighting/lg/{lg}/state',
            json={
                'save': 1
            })
        assert response.status_code == 200
    for lg in (0, 1, 2, 3):
        response = client.put(
            f'/api/lighting/lg/{lg}/state',
            json={
                'onOff': 1
            })
        assert response.status_code == 200

        response = client.get(
            f'/api/lighting/lg/{lg}/state')
        assert response.status_code == 200
        assert response.json().get('onOff') == 1



def test_set_lighting_group_defaults(client):
    for lg in (1, 2, 3):
        response = client.put(
            f'/api/lighting/lg/{lg}/state',
            json={
                'save': 1
            })
        assert response.status_code == 200


def test_set_lighting_group_smart_brt(client):
    response = client.put(
        f'/api/lighting/lg/0/state',
        json={
            'onOff': EventValues.ON,
            'brt': 76.666
        })
    assert response.status_code == 200
    assert response.json().get('brt') == 77


def test_get_lighting_settings(client):
    response = client.get(f'/api/lighting/settings')
    assert response.status_code == 200


def test_get_lighting_reset(client):
    response = client.put(f'/api/lighting/reset')
    assert response.status_code == 200


def test_get_non_existing_lz(client):
    response = client.get('/api/lighting/lz/-1/state')
    assert response.status_code == 404


def test_set_non_positive_lz(client):
    response = client.put('/api/lighting/lz/-1/state')
    assert response.status_code == 422


def test_set_non_existing_lz(client):
    response = client.put('/api/lighting/lz/999/state', json={'onOff': 1})
    assert response.status_code == 404


def test_get_non_existing_lg(client):
    response = client.get('/api/lighting/lg/-1/state')
    assert response.status_code == 404


def test_set_non_existing_lg(client):
    response = client.put('/api/lighting/lg/-1/state', json={'onOff': 1})
    assert response.status_code == 404


def test_smart_lg_settings(client):
    LG = 0

    response = client.get(f'/api/lighting/lg/{LG}/state')
    assert response.status_code == 200

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'brt': 50
        }
    )
    assert response.status_code == 200
    assert response.json().get('brt') == 50


def test_exterior_lg_settings(client):
    LG = 100

    response = client.get(f'/api/lighting/lg/{LG}/state')
    assert response.status_code == 200

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'onOff': EventValues.ON
        }
    )
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.ON

    for i, lz in app.hal.lighting.handler.lighting_zone.items():
        if lz.attributes.get('exterior') is True:
            assert lz.state.onOff == 1

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'onOff': EventValues.OFF
        }
    )
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.OFF

    for i, lz in app.hal.lighting.handler.lighting_zone.items():
        if lz.attributes.get('exterior') is True:
            assert lz.state.onOff == EventValues.OFF


def test_master_lg_settings(client):
    '''Test that settings like brt on master lighting group
    only impacts the lights turned on.'''
    LG = 101    # MASTER ALL

    # Drop config for this test as previous tests could impact the saved brightness
    for i, _ in app.hal.lighting.handler.lighting_zone.items():
        _ = client.put(f'/api/lighting/lz/{i}/defaults')

    response = client.get(f'/api/lighting/lg/{LG}/state')
    assert response.status_code == 200

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'brt': 55
        }
    )
    assert response.status_code == 200
    assert response.json().get('brt') == 55

    for i, lz in app.hal.lighting.handler.lighting_zone.items():
        if lz.state.onOff == EventValues.ON:
            assert lz.state.brt == 55   # Set value above
        else:
            # As we do not drop the database, we cannot check for default value here
            if lz.state.brt != 80:
                raise ValueError(f'Lighting Zone: {i}, {lz} BRT wrong')

            assert lz.state.brt == 80   # Should be something else

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'onOff': EventValues.ON
        }
    )
    assert response.status_code == 200

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'brt': 75
        }
    )

    for i, lz in app.hal.lighting.handler.lighting_zone.items():
        if lz.attributes.get('hidden') is False:
            assert lz.state.onOff == 1
            assert lz.state.brt == 75   # Default value


def test_all_off(client):
    LG = 101    # MASTER ALL
    LZ_DRAWERS = 16

    response = client.get(f'/api/lighting/lz/{LZ_DRAWERS}/state')
    assert response.status_code == 200

    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'onOff': True
        }
    )

    response = client.get(f'/api/lighting/lz/{LZ_DRAWERS}/state')
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.ON



    response = client.put(
        f'/api/lighting/lg/{LG}/state',
        json={
            'onOff': False
        }
    )

    response = client.get(f'/api/lighting/lz/{LZ_DRAWERS}/state')
    assert response.status_code == 200
    assert response.json().get('onOff') == EventValues.ON


def test_czone_set_lighting_zone(client):
    # Set to R with lighting zone 17
    client.put(
        '/api/system/floorplan',
        json={
            'floorPlan': 'WM524R',
            'optionCodes': '52N,31P,29J,33W'
        }
    )
    zone_id = 17
    response = client.put(
        f'/api/lighting/lz/{zone_id}/state',
        json={
            "brt": 100,
            "onOff": 1
        }
    )
    assert response.status_code == 200
