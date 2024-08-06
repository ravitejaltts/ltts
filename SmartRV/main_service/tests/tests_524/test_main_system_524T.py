
import os
import sys
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


from common_libs.models.common import EventValues

from fastapi.testclient import TestClient
from  main_service.wgo_main_service import app

import pytest


BASE_URL = '/api/system'


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put('/api/system/floorplan', json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,291'})
        yield c


def test_system_get_canfilter(client):
    result = client.get(
        BASE_URL + '/can/filter'
    )
    assert result.status_code == 200
    can_filter = result.json()
    # TODO: Get this list fromt the config
    expected_filter = (
        'fluid_level',
        'lighting_broadcast',
        'heartbeat',
        'rvswitch',
        'rvoutput',
        'roof_fan_status_1',
        'ambient_temperature',
        'thermostat_ambient_status',
        'dc_source_status_1',
        'dc_source_status_2',
        'dc_source_status_3',
        'battery_status',
        'prop_bms_status_6',
        'prop_module_status_1',
        'inverter_ac_status_1',
        'inverter_status',
        'charger_ac_status_1',
        'charger_ac_status_2',
        'charger_status',
        'charger_status_2',
        'solar_controller_status',
        'vehicle_status_1',
        'vehicle_status_2',
        'state_of_charge',
        'dc_charging_state',
        'pb_park_brake',
        'tr_transmission_range',
        'odo_odometer',
        'aat_ambient_air_temperature',
        'vin_response',
        'dc_dimmer_command_2',
        'waterheater_status',
        'waterheater_status_2'
    )

    logger.info(f"Can filter returned: {can_filter}")

    for item in expected_filter:
        assert (item in can_filter) is True
