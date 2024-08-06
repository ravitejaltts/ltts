import os
import sys
import logging
from datetime import datetime
import subprocess
import asyncio

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
import time

import random
import pytest
from common_libs.models.common import EventValues


@pytest.fixture
def client():

    with TestClient(app) as c:
        c.put('/api/system/floorplan', json={'floorPlan': 'VANILLA'})
        yield c


# Test home redirect flag
def test_ui_home_redirect(client):
    '''Test that vanilla has a redirect flag in hom api.'''
    response = client.get('/ui/home')
    assert response.status_code == 200
    print(response.json())
    assert response.json().get('redirect') == '/home/manufacturing'


# Test UI endpoint for manufacturing
def test_ui_manufacturing(client):
    '''Test UI manufacturing endpoint data.'''
    response = client.get('/ui/manufacturing')
    assert response.status_code == 200
    data = response.json()
    print('DATA', data)
    assert data.get('overview', {}).get('title') == 'Manufacturing'
    assert data.get('navigationLock') is True
    assert data.get('hideSidebar') is True
