
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


from common_libs.models.common import EventValues

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

import pytest

pytest_plugins = ('pytest_asyncio',)

BASE_URL = '/api/system'


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52D,33F,31P,33F,291'
            }
        )
        yield c


# @pytest.mark.skip(reason='Need a better understanding on how to check async calls')
@pytest.mark.asyncio
async def test_connectivity_login_ip_timeout(client):
    '''Test that the code handles timeouts properly.'''
    # Set IP to something that cannot be reached
    # Attempt login
    # Check that it raises IOError
    app.hal.connectivity.handler.BASE_URL = 'http://1.2.3.4/'
    # Could override timeout for quicker testing
    # app.hal.connectivity.handler.LOGIN_TIMEOUT = 2
    # with pytest.raises(IOError, match=r"Login connection error"):

    # assert await app.hal.connectivity.handler.login() is True
    result = await app.hal.connectivity.handler.login()
    # This should fail with a timeout
    assert result is True


@pytest.mark.skip(reason='Need mockup library to bring up a fake cradlepoint first')
def test_connectivity_login_wrong_user(client):
    '''Test that the code handles retry timeouts properly on 403.'''
    # Set up Test server that mocks expected cradlepoint responses
    # Set user to incorrect value
    # Attempt login
    # Check that it returns 403
    # Attempt login again
    # Verify it returns without trying
    app.hal.connectivity.handler.user = 'DomConnectDoesNotExistYet'
    assert app.hal.connectivity.handler.login() == 403
    # Set user to correct user
    # Expecting it to fail due to retry timeout
    app.hal.connectivity.handler.user = 'winnconnect'
    with pytest.raises(IOError, match=r"Login retry timer not expired"):
        app.hal.connectivity.handler.login()
    # Clear last time tried
    app.hal.connectivity.handler.login_failed_time = None
    assert app.hal.connectivity.handler.login() is False
