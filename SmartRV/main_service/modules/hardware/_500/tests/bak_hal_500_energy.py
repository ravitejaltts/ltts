import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath("./.."))
sys.path.append(os.path.abspath("."))

import pytest

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app


# Create an instance of the 524T floorplan HAL in its

@pytest.fixture
def client():
    with TestClient(app) as c:
        print('Creating new instance of app')
        c.put('/api/system/floorplan', json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,29J'})
        yield c


def test_hal_energy_generator(client):
    '''Sample test on how we could access HAL directly as a lower level unit test.'''
    generator = app.hal.energy.handler.generator[1]
    assert generator is not None
