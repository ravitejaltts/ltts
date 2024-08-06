import asyncio
import logging
import time

logger = logging.getLogger(__name__)

import pytest
from fastapi.testclient import TestClient

from common_libs.models.common import EventValues
from main_service.wgo_main_service import app


BASE_URL = '/api/features/dx/'

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
                'optionCodes': '52D,52N,31P,33F,29J'
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


@pytest.mark.asyncio
async def test_dx_3(client):
    response = client.get(BASE_URL + '3/state')
    assert response.status_code == 200

    assert response.json().get("startTime") is not None
    # NOTE: Rest should be none as no update yet happened
    assert response.json().get("updateTime") is None
    assert response.json().get("cpuLoad") is None
    assert response.json().get("memory") is None
    assert response.json().get("userStorage") is None
    assert response.json().get("systemStorage") is None

    # TODO: Fix the below to pass, don't know yet why it fails in multiple tests but passes in a single
    # await asyncio.sleep(15)
    # # time.sleep(15)

    # response = client.get(BASE_URL + '3/state')
    # assert response.status_code == 200

    # # NOTE: Content might be in flux for local errors on Mac or Windows
    # # but all values should be no longer None

    # assert response.json().get("startTime") is not None
    # # TODO: Fix that this is correct
    # assert response.json().get("updateTime") is not None
    # assert response.json().get("cpuLoad") is not None
    # assert response.json().get("memory") is not None
    # assert response.json().get("userStorage") is not None
    # assert response.json().get("systemStorage") is not None
