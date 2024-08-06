import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

import pytest

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app


# Create an instance of the 524T floorplan HAL in its

@pytest.fixture
def client():
    with TestClient(app) as c:
        print('Creating new instance of app')
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,291'
            }
        )
        yield c


def test_hal_electrical_dcswitch_negative_tests(client):
    '''Sample test on how we could access HAL directly as a lower level unit test.'''
    mapping = app.hal.electrical.handler.cfgMapping
    print('MAPPING', mapping['dc'])
    sample_switch = int(list(mapping['dc'].keys())[0])

    # Test that we get a type error when parameters are missing
    with pytest.raises(TypeError):
        app.hal.electrical.handler.dc_switch()

    # Test that a non valid dc_id fails with ValueError
    with pytest.raises(ValueError):
        app.hal.electrical.handler.dc_switch(-1, 1, 100)
    with pytest.raises(ValueError):
        app.hal.electrical.handler.dc_switch(999, 1, 100)

    # Test that 0 is currently disabled
    with pytest.raises(ValueError):
        app.hal.electrical.handler.dc_switch(0, 1, 100)

    # Test that a non valid onoff value raises
    with pytest.raises(ValueError):
        app.hal.electrical.handler.dc_switch(sample_switch, 2, 100)
    with pytest.raises(ValueError):
        app.hal.electrical.handler.dc_switch(sample_switch, -1, 100)
    with pytest.raises(ValueError):
        app.hal.electrical.handler.dc_switch(sample_switch, 5, 100)
    with pytest.raises(ValueError):
        app.hal.electrical.handler.dc_switch(sample_switch, "123", 100)

    #
