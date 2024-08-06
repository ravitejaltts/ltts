import os
import sys
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app

import pytest


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_get_meta_categories(client):
    response = client.get("/api/meta/categories")
    assert response.status_code == 200


def test_get_meta_category(client):
    response = client.get("/api/meta/categories/nonexisting")
    assert response.status_code == 404

    response = client.get("/api/meta/categories/lighting")
    assert response.status_code == 200
