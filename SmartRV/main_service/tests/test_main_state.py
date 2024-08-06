
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath('./..'))
sys.path.append(os.path.abspath('.'))

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

import pytest


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

##STATE

def test_get_full_state(client):
    response = client.get('api/state/full')
    assert response.status_code == 200

def test_get_callback_list(client):
    return
    response = client.get('api/state/callback')
    assert response.status_code == 200

def test_post_callback_register(client):
    return
    response = client.post('api/state/callback/register/')
    assert response.status_code == 200

def test_set_callback_update(client):
    return
    response = client.put('api/state/callback/{callback_id}/')
    assert response.status_code == 200

def test_delete_callback(client):
    return
    response = client.delete('api/state/callback/{callback_id}/')
    assert response.status_code == 200

def test_get_callback(client):
    return
    response = client.get('api/state/callback/{callback_id}')
    assert response.status_code == 200
#what is this api for?
def test_get_features_state(client):
    return
    response = client.get('api/state')
    assert response.status_code == 200
