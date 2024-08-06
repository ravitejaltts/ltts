import asyncio
import logging
import time

logger = logging.getLogger(__name__)

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from common_libs.models.common import EventValues, RVEvents
from main_service.tests.can_messages import (
    TM620_WH1_LIN_ERROR,
    TM620_WH1_LIN_NODATA,
    TM620_WH1_OK,
    TM620_WH1_PANEL_BUSY,
    TM620_WH1_PANEL_NODATA,
    TM620_WH1_WH_ERROR,
    TM620_WH1_WH_NODATA,
    WATER_HEATER_OFF,
    WATER_HEATER_ON_COMBUSTION
)
from main_service.tests.utils import check_ui_notifications, send_a_can_event
from main_service.wgo_main_service import app

CATEGORY = 'watersystems'


@pytest.fixture
def client():
    with TestClient(app) as c:
        print('Creating new instance of app')
        print('Test Client Response', c.put(
            '/api/system/floorplan',
            json={
                'floorPlan': 'WM524T',
                'optionCodes': '52N,52D,31P,33F,29J'
            }
        ))
        yield c



def test_water_tanks_for_WM524T(client):
    # Fresh =1 , Grey = 2, Black = 3
    for instance in (1, 2, 3):
        for lvl in (0, 50, 100):
            msg = {
                "title": 'Tank 1 - Fresh - 100 %',
                "Instance": str(instance),
                "Fluid_Type": "Fresh Water",
                "Fluid_Level": str(lvl),
                # "Tank_Capacity": "0.1136",
                # "NMEA_Reserved": "255",
                "name": "FLUID_LEVEL",
                'instance_key': ''
            }
            response = send_a_can_event(client, msg)

            response = client.get(f'/api/{CATEGORY}/wt/{instance}/state')
            assert response.status_code == 200
            print(f"Water Tank Response {response.json()}")

            assert response.json().get('lvl') == float(lvl)

        # TODO: Add tests for the validation, so that wrong values are not accepted by CAN
        # for lvl in (-10, 101, None):
        #     msg = {
        #         "title": 'Tank 1 - Fresh - 100 %',
        #         "Instance": str(instance),
        #         "Fluid_Type": "Fresh Water",
        #         "Fluid_Level": str(lvl),
        #         # "Tank_Capacity": "0.1136",
        #         # "NMEA_Reserved": "255",
        #         "name": "FLUID_LEVEL",
        #         'instance_key': ''
        #     }
        #     response = send_a_can_event(client, msg)

        #     response = client.get(f'/api/{CATEGORY}/wt/{instance}/state')

        #     assert response.status_code == 200
        #     print(f"Water Tank Response {response.json()}")

        #     assert response.json().get('lvl') == float(100)

in_dev = pytest.mark.skip(
    reason="Refactor needed to pass tests on any platform"
)

@in_dev
@pytest.mark.asyncio
async def test_water_pumps_for_WM524T(client):
    # Fresh = 1
    for instance in (1, ):
        # Set OFF Initial
        response = client.put(
            f'/api/{CATEGORY}/wp/{instance}/state',
            json={
                'onOff': EventValues.OFF
            }
        )
        # Get intial state
        response = client.get(
            f'/api/{CATEGORY}/wp/{instance}/state'
        )
        assert response.json().get('onOff') == EventValues.OFF

        # Turn on / Turn Off
        response = client.put(
            f'/api/{CATEGORY}/wp/{instance}/state',
            json={
                'onOff': EventValues.ON
            }
        )

        assert response.json().get('onOff') == EventValues.ON

        # TODO: Figure out a robust cansend wait timer for the queue to handle sending
        await asyncio.sleep(1)

        last_message = app.can_sender.get_can_history().get('history_sent').pop()
        assert '1CFF0044#27990B0064FF7C0F' in last_message['cmd']

        response = client.put(
            f'/api/{CATEGORY}/wp/{instance}/state',
            json={
                'onOff': EventValues.OFF
            }
        )

        # TODO: Figure out a robust cansend wait timer for the queue to handle sending
        await asyncio.sleep(0.5)

        last_message = app.can_sender.get_can_history().get('history_sent').pop()
        assert '1CFF0044#27990B0000FF7C0F' in last_message['cmd']

        assert response.json().get('onOff') == EventValues.OFF

@in_dev
@pytest.mark.asyncio
async def test_water_heaters_for_WM524T(client):
    # Fresh = 1
    # Heating Pada Grey = 2, Black = 3 NOT TESTED YET

    for instance in (1, ):

        # Set mode to COMFORT
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "High level (COMFORT)"
        }
        result = send_a_can_event(client, can_msg)

        # Set state initial
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'onOff': EventValues.OFF
            }
        )
        # Get intial state
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.json().get('onOff') == EventValues.OFF

        # Turn on / Turn Off
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'onOff': EventValues.ON
            }
        )

        await asyncio.sleep(0.5)
        last_message = app.can_sender.get_can_history().get('history_sent').pop()
        print("[last can msg]",last_message)
        assert '19FE9844#0102FFFFFFFFFFFF' in last_message['cmd']

        assert response.json().get('onOff') == EventValues.ON

        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'onOff': EventValues.OFF
            }
        )

        await asyncio.sleep(0.5)
        last_message = app.can_sender.get_can_history().get('history_sent').pop()
        print(last_message)
        assert '19FFF644#0100FFFFFFFFFFFF' in last_message['cmd']

        assert response.json().get('onOff') == EventValues.OFF


def test_water_heaters_modes_for_WM524T(client):
    # Fresh = 1

    for instance in (1, ):
        # Set mode to COMFORT
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "High level (COMFORT)"
        }
        result = send_a_can_event(client, can_msg)
        # Get intial state
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT

        # Set to ECO
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.ECO
            }
        )
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.ECO

        # Set to COMFORT
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.COMFORT
            }
        )
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT

        # Adjust setTemp to max

        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': 49.0
            }
        )

        print(response.json())
        assert response.status_code == 200
        assert response.json().get('setTemp') == 49.0

        # Adjust setTemp to min

        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': 35.0
            }
        )

        print(response.json())
        assert response.status_code == 200
        assert response.json().get('setTemp') == 35.0

        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        # Expecting the setTemp value to be unchanged from previous successful test
        assert response.json().get('setTemp') == 35.0


        # Try to set over max

        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': 100
            }
        )
        assert response.status_code == 422

        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        # Expecting the setTemp value to be unchanged from previous successful test
        assert response.json().get('setTemp') == 35.0

        # Try to set under min
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': -10.0
            }
        )

        assert response.status_code == 422

        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        # Expecting the setTemp value to be unchanged from previous successful test
        assert response.json().get('setTemp') == 35.0


def test_water_heaters_modes_fahrenheit_for_WM524T(client):
    # Fresh = 1

    for instance in (1, ):
        # Set mode to COMFORT
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "High level (COMFORT)"
        }
        result = send_a_can_event(client, can_msg)
        # Get intial state
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT

        # Set to ECO
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.ECO
            }
        )
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.ECO

        # Set to COMFORT
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.COMFORT
            }
        )
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT

        # Adjust setTemp to max

        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': 108.0,
                'unit': 'F'
            }
        )

        print(response.json())
        assert response.status_code == 200
        assert response.json().get('setTemp') == 42.2

        # Adjust setTemp to min

        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': 95.0,
                'unit': 'F'
            }
        )

        print(response.json())
        assert response.status_code == 200
        assert response.json().get('setTemp') == 35.0

        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        # Expecting the setTemp value to be unchanged from previous successful test
        assert response.json().get('setTemp') == 35.0


        # Try to set over max

        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': 150,
                'unit': 'F'
            }
        )
        assert response.status_code == 422

        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        # Expecting the setTemp value to be unchanged from previous successful test
        assert response.json().get('setTemp') == 35.0

        # Try to set under min
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'setTemp': -10.0,
                'unit': 'F'
            }
        )

        assert response.status_code == 422

        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        # Expecting the setTemp value to be unchanged from previous successful test
        assert response.json().get('setTemp') == 35.0

@pytest.mark.asyncio
async def test_water_heaters_can_updates_for_WM524T(client):
    '''This test tries to emulate a decoded CAN message as received from TM-630.'''

    for instance in (1, ):
        # Set Inital State
        # Set to COMFORT
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.COMFORT,
                'onOff': EventValues.ON
            }
        )
        # Get intial state
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT
        assert response.json().get('onOff') == EventValues.ON

        # Turn on
        can_msg = {
            # "title": "Set Water Heater State Set_Point_temp to 40 C",
            "name": "waterheater_status",
            "Instance": "1",
            "Operating_Mode": "combustion",
            "Set_Point_Temperature": "40.0"
        }
        # Check it is ON
        # Check setTemp is 40
        result = send_a_can_event(client, can_msg)
        await asyncio.sleep(0.5)

        # NOTE: Cure to can status delays, the first incoming status after a change will be ignored
        # Sending again
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        await asyncio.sleep(0.5)
        # Check that it is OFF now and mode unchanged
        response = client.get(f'/api/{CATEGORY}/wh/{instance}/state')
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT
        assert response.json().get('onOff') == EventValues.ON

        # Set mode to ECO
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "Low level (ECO)"
        }
        result = send_a_can_event(client, can_msg)
        # Send twice due to the first being ignored
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        await asyncio.sleep(0.5)
        response = client.get(f'/api/{CATEGORY}/wh/{instance}/state')
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.ECO
        assert response.json().get('onOff') == EventValues.ON

        # Set mode to Default
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "Default"
        }
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        await asyncio.sleep(0.5)
        response = client.get(f'/api/{CATEGORY}/wh/{instance}/state')
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT

        # Set mode to ECO
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "Low level (ECO)"
        }
        result = send_a_can_event(client, can_msg)
        await asyncio.sleep(0.5)
        response = client.get(f'/api/{CATEGORY}/wh/{instance}/state')
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.ECO
        assert response.json().get('onOff') == EventValues.ON

        # Set mode to COMFORT
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "High level (COMFORT)"
        }
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        await asyncio.sleep(0.5)
        response = client.get(f'/api/{CATEGORY}/wh/{instance}/state')
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT
        assert response.json().get('onOff') == EventValues.ON

        # Turn Off
        can_msg = {
            # "title": "Set Water Heater State Set_Point_temp to 40 C",
            "name": "waterheater_status",
            "Instance": "1",
            "Operating_Mode": "Off",
            "Set_Point_Temperature": "40"
        }
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        result = send_a_can_event(client, can_msg)
        await asyncio.sleep(0.5)
        # Check that it is OFF now and mode unchanged
        response = client.get(f'/api/{CATEGORY}/wh/{instance}/state')
        assert response.status_code == 200
        assert response.json().get('mode') == EventValues.COMFORT
        assert response.json().get('onOff') == EventValues.ON
        assert response.json().get('setTemp') == 40.0


def test_tank_heaters_for_WM524T(client):
    '''This test tries to test the enable of the tankpads.'''

    for instance in (2, ):
        # Initial State
        # Set to enabled and on
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        assert response.json().get('onOff') == EventValues.ON
        assert response.json().get('cirOnOff') == EventValues.ON

        can_msg = {
            "Ambient_Temp": "44",  # C
            "Instance": str(0xF9),      # TM-1010 sensor
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        }

        result = send_a_can_event(client, can_msg)

        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        assert response.json().get('onOff') == EventValues.ON
        assert response.json().get('cirOnOff') == EventValues.OFF

        # No temp available
        can_msg = {
            "Ambient_Temp": "Data Invalid",  # C
            "Instance": str(0xF9),      # TM-1010 sensor
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        }
        result = send_a_can_event(client, can_msg)

        # Check circuit is ON
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        assert response.json().get('onOff') == EventValues.ON
        assert response.json().get('cirOnOff') == EventValues.ON

        can_msg = {
            "Ambient_Temp": "44",  # C
            "Instance": str(0xF9),      # TM-1010 sensor
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        }

        result = send_a_can_event(client, can_msg)

        # Get intial state
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        print(f"\nResponce json  = { response.json()}\n")
        assert response.json().get('onOff') == EventValues.ON
        assert response.json().get('cirOnOff') == EventValues.OFF

        # lower the outside temp below 40 F
        can_msg = {
            "Ambient_Temp": "3",  # C
            "Instance": str(0xF9),      # TM-1010 sensor
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        }
        result = send_a_can_event(client, can_msg)

        # Check circuit is ON
        response = client.get(
            f'/api/{CATEGORY}/wh/{instance}/state'
        )
        assert response.status_code == 200
        assert response.json().get('onOff') == EventValues.ON
        assert response.json().get('cirOnOff') == EventValues.ON


def test_water_heaters_lockouts_WM524T(client):
    '''This test tries to emulate a decoded CAN message as received from TM-630.'''

    for instance in (1, ):
        # Set Inital State
        # Set to COMFORT and
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.COMFORT,
                'onOff': EventValues.OFF
            }
        )

        # Set mode to COMFORT
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "DeCalc.(status only)"
        }
        result = send_a_can_event(client, can_msg)
        # Set to COMFORT and
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.COMFORT,
                'onOff': EventValues.OFF
            }
        )
        assert response.status_code == 423


        # Set mode to COMFORT
        can_msg = {
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "High level (COMFORT)"
        }
        result = send_a_can_event(client, can_msg)
        # Set to COMFORT and
        response = client.put(
            f'/api/{CATEGORY}/wh/{instance}/state',
            json={
                'mode': EventValues.COMFORT,
                'onOff': EventValues.OFF
            }
        )
        assert response.status_code == 200


def test_water_tank_calibration(client):
    '''Test the various calibation properties.'''

    # Set a know state
    result = client.put(
        '/api/watersystems/wt/1/state',
        json={
            'vltgMin': 0.6,
        }
    )
    assert result.status_code == 200

    result = client.put(
        '/api/watersystems/wt/1/state',
        json={
            'vltgMax': 4.0,
        }
    )
    assert result.status_code == 200

    # result = client.put(
    #     '/api/watersystems/wt/1/state',
    #     json={
    #         'cap': 50,
    #     }
    # )
    # assert result.status_code == 200

    # Update ALL
    assert result.json().get('vltgMin') == 0.6
    assert result.json().get('vltgMax') == 4.0
    # assert result.json().get('cap') == 50

    # result = client.get('/api/watersystems/wt/1/state')
    # assert result.status_code == 200
    # # assert result.json().get('cap') == 30   # Gals
    # assert result.json().get('vltg') is None
    # assert result.json().get('vltgMin') == 0.5
    # assert result.json().get('vltgMax') == 1.29

    can_msg = {
        'name': 'battery_status',
        'Instance': '101',  # Water tanks are 101 - 103
        'Battery_Voltage': "4.0"
    }
    result = send_a_can_event(client, can_msg)

    result = client.get('/api/watersystems/wt/1/state')
    assert result.status_code == 200
    assert result.json().get('vltg') == 4.0
    assert result.json().get('lvl') == 100

    can_msg = {
        'name': 'battery_status',
        'Instance': '101',  # Water tanks are 101 - 103
        'Battery_Voltage': "0.5"
    }
    result = send_a_can_event(client, can_msg)

    result = client.get('/api/watersystems/wt/1/state')
    assert result.status_code == 200
    assert result.json().get('vltg') == 0.5
    assert result.json().get('lvl') == 0


    can_msg = {
        'name': 'battery_status',
        'Instance': '101',  # Water tanks are 101 - 103
        'Battery_Voltage': "0.0"
    }
    result = send_a_can_event(client, can_msg)

    result = client.get('/api/watersystems/wt/1/state')
    assert result.status_code == 200
    assert result.json().get('vltg') == 0.0
    assert result.json().get('lvl') is None

    result = client.put(
        '/api/watersystems/wt/1/state',
        json={
            'vltgMin': 0.6,
            'vltgMax': 5.0
        }
    )
    assert result.status_code == 200
    # Min should update, the others not
    assert result.json().get('vltgMin') == 0.6
    assert result.json().get('vltgMax') == 4.0
    # assert result.json().get('cap') == 50

    # result = client.put(
    #     '/api/watersystems/wt/1/state',
    #     json={
    #         'cap': 50
    #     }
    # )
    # assert result.status_code == 200
    # assert result.json().get('vltgMin') == 0.6
    # assert result.json().get('vltgMax') == 4.0
    # # Cap should update, the others not
    # # assert result.json().get('cap') == 50

    result = client.put(
        '/api/watersystems/wt/1/state',
        json={
            'vltgMax': 3.5
        }
    )
    assert result.status_code == 200
    assert result.json().get('vltgMin') == 0.6
    # Max should update, the others not
    assert result.json().get('vltgMax') == 3.5
    # assert result.json().get('cap') == 50


@in_dev
def test_water_tank_state_validation(client):
    '''Test the various min/max values.'''
    result = client.get('/api/watersystems/wt/1/state')
    assert result.status_code == 200
    # assert result.json().get('cap') == 30   # Gals
    assert result.json().get('vltg') is None
    assert result.json().get('vltgMin') == 0.6
    assert result.json().get('vltgMax') == 3.5

    with pytest.raises(ValidationError):
        result = client.put(
            '/api/watersystems/wt/1/state',
            json={
                'vltgMin': 5.1,
            }
        )

    with pytest.raises(ValidationError):
        result = client.put(
            '/api/watersystems/wt/1/state',
            json={
                'vltgMin': -0.1,
            }
        )

    with pytest.raises(ValidationError):
        result = client.put(
            '/api/watersystems/wt/1/state',
            json={
                'vltgMin': "dom",
            }
        )

    result = client.put(
        '/api/watersystems/wt/1/state',
        json={
            'vltgMin': None,
        }
    )
    assert result.status_code == 200
    assert result.json().get('vltgMin') is not None
    # assert result.status_code == 422
    # Min should update, the others not


def test_tm620_prop_message_handling(client):
    '''Test the various failure causes and the trigger/clearance of an alert.'''
    # Any preconditions
    # Send CAN OK message
    _ = send_a_can_event(client, TM620_WH1_OK)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT.name) is False

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT.name) is False

    # Send LIN error message
    _ = send_a_can_event(client, TM620_WH1_LIN_ERROR)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT.name) is True

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT.name) is False

    # Send no data and see that notification remains unchanged
    _ = send_a_can_event(client, TM620_WH1_LIN_NODATA)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT.name) is True

    # Send OK
    _ = send_a_can_event(client, TM620_WH1_OK)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT.name) is False

    # Send No Data and check it still shows False
    _ = send_a_can_event(client, TM620_WH1_LIN_NODATA)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT.name) is False

    # Send OK to start next error type
    _ = send_a_can_event(client, TM620_WH1_OK)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT.name) is False

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT.name) is False

    # Send Water Heater error and repeat pattern above

    _ = send_a_can_event(client, TM620_WH1_WH_ERROR)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT.name) is False

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT.name) is True

    # Send no data and see that notification remains unchanged
    _ = send_a_can_event(client, TM620_WH1_WH_NODATA)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT.name) is True

    # Send OK
    _ = send_a_can_event(client, TM620_WH1_OK)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT.name) is False

    # Send No Data and check it still shows False
    _ = send_a_can_event(client, TM620_WH1_WH_NODATA)

    assert check_ui_notifications(
        client,
        RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT.name) is False


def test_waterheater_led(client):
    # Send CAN message for Waterheater off
    wh_on_can = send_a_can_event(client, WATER_HEATER_OFF)
    assert wh_on_can.status_code == 200

    time.sleep(0.5)
    can_history = list(app.can_send_runner.handler.can_history)
    # Check that we send the command to turn the LED off
    # {'cmd': ('cansend canb0s0 1CFF0044#27991D0000FF7C0F', '1CFF0044', '27991D0000FF7C0F')
    assert can_history[-1].get('cmd')[1] == '1CFF0044'
    assert can_history[-1].get('cmd')[2] == '27991D0000FF7C0F'

    # Send CAN message for Waterheater on
    wh_off_can = send_a_can_event(client, WATER_HEATER_ON_COMBUSTION)
    assert wh_off_can.status_code == 200
    time.sleep(0.5)
    # Check that we send the command to turn the LED on
    can_history = list(app.can_send_runner.handler.can_history)

    found_can = False
    for message in can_history:
        if message.get('cmd')[2] == '27991D0064FF7C0F':
            found_can = True
            break

    assert found_can is True



# TODO: Add test for panel busy, panel; busy showld show as a lcokout but not as an alert
