
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
import pytest
import importlib

def is_dbus_bindings_installed():
    try:
        importlib.import_module('_dbus_bindings')
        return True
    except ImportError:
        return False

non_mac = pytest.mark.skipif(
    sys.platform.startswith('darwin') or not is_dbus_bindings_installed(),
    reason="DBUS module not available on MAC or if dbus is not running as on WSL"
)
# if sys.platform.startswith("darwin"):
#     pytest.skip("skipping windows-only tests", allow_module_level=True)


@non_mac
@pytest.fixture
def client():
    from bt_service.wgo_bt_service import app
    with TestClient(app) as c:
        yield c


@non_mac
def test_app_runner_handle(client):
    assert client.runner is not None


@non_mac
def test_service_state(client):
    response = client.get('/status')
    assert response.status_code == 200


@non_mac
def test_service_set_vin(client):
    vin = 'ABC1234567890DEFG'
    response = client.put(f'/vin/{vin}')
    assert response.status_code == 200


@non_mac
def test_service_get_vin(client):
    response = client.get('/vin')
    assert response.status_code == 200
