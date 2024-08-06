import os
import sys
import logging
from datetime import datetime

import requests
import json

logger = logging.getLogger(__name__)
import pytest

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app

from common_libs.models.common import EventValues


class Response(object):
    def __init__(self, code, data):
        self.code = code
        self.data = data

    def json(self):
        return json.dumps(self.data)

    def status_code(self):
        return self.code


class RequestsHandler(object):
    def __init__(self, host_url):
        self.HOST_URL = host_url
        print(self.HOST_URL)

    def build_url(self, path):
        if path.startswith('/'):
            path = path[1:]

        url = f'{self.HOST_URL}/{path}'
        print('URL', url)
        return url

    def get(self, path, headers={}):
        return requests.get(self.build_url(path))

    def put(self, path, json={}, headers={}):
        return requests.put(self.build_url(path), json=json)


@pytest.fixture
def client():
    if os.environ.get('WGO_TEST_HOST'):
        c = RequestsHandler(os.environ.get('WGO_TEST_HOST'))
        yield c
    else:
        with TestClient(app) as c:
            print('Creating new instance of app')
            print('Test Client Response', c.put(
                '/api/system/floorplan',
                json={
                    'floorPlan': 'WM524T',
                    'optionCodes': '52D,33F,31P,33F,29J'
                }
            ))
            yield c


def test_get_remote_state(client):
    response = client.get("/api/state", headers={})
    assert response.status_code == 200
    print(response.json())
    result = response.json()
    assert result.get('sessionId') is not None


def test_set_remote_lighting(client):
    response = client.get("/api/lighting/state", headers={})
    assert response.status_code == 200
    print(response.json())
    result = response.json()
    assert result.get('lz2') is not None

    response = client.put(
        "/api/lighting/lz/2/state",
        headers={},
        json={'onOff': EventValues.ON}
    )
    assert response.status_code == 200
    print(response.json())
    result = response.json()
    assert result.get('onOff') == EventValues.ON
