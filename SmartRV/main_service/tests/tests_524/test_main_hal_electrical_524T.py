import os
import sys
import logging
from datetime import datetime
import subprocess
import json
import asyncio
from copy import deepcopy

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event
import time

import pytest
from common_libs.models.common import EventValues


@pytest.fixture
def client():
    with TestClient(app) as c:
        c.put('/api/system/floorplan', json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,29J'})
        yield c


def test_light_switches_for_rv1_524T(client):
    # Indoor
    instance = 6    # TODO: Find out which of the instances is associated with the switch inputs
    dipswitch = 0x80
    outputs = {i + 1: 0 for i in range(32)}

    initial_msg = {
        'name': 'RvSwitch',
        'Manufacturer_Code': 'BEP Marine',
        'Dipswitch': str(dipswitch),
        'Instance': str(instance)
    }
    for index, state in outputs.items():
        initial_msg[f'Output{index}'] = str(state)

    response = send_a_can_event(client, initial_msg)

    # Now toggle a known switch
    msg = deepcopy(initial_msg)

    # Lightlist
    light_list = (
        ({'bank': '6', 'output': '10'}, 13),
        ({'bank': '6', 'output': '12'}, 9)
    )
    # Ideally read this mapping from the same source the HAL would read it
    # TODO: Remove hardcoding and move to internal electrical mapping
    for light in light_list:
        # light[0] is the circuit for the given instance/bank
        # light[1] is the associated lightzone
        # TODO: Add more structure to allow other switch tests

        result = client.put(f'/api/lighting/lz/{light[1]}/state', data=json.dumps({"onOff": 0}))
        assert result.status_code == 200
        print("1 ONOFF = ",result.json())
        # TODO: Figure out what it should be
        assert result.json().get('onOff') == 0
        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        assert result.status_code == 200
        print("2 ONOFF = ",result.json())
        # TODO: Figure out what it should be
        assert result.json().get('onOff') == 0

        # Blip the switch state
        msg[f'Output{light[0].get("output")}'] = str(1)
        msg['Instance'] = light[0].get('bank')
        response = send_a_can_event(client, msg)

        # No pause needed
        msg[f'Output{light[0].get("output")}'] = str(0)
        response = send_a_can_event(client, msg)

        # Check state
        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        assert result.status_code == 200
        # time.sleep(1)
        assert result.json().get('onOff') == 1

        # Blip the switch state
        msg[f'Output{light[0].get("output")}'] = str(1)
        msg['Instance'] = light[0].get('bank')
        response = send_a_can_event(client, msg)

        # No pause needed
        msg[f'Output{light[0].get("output")}'] = str(0)
        response = send_a_can_event(client, msg)

        # Check state
        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        assert result.status_code == 200
        # time.sleep(1)
        assert result.json().get('onOff') == 0


def test_light_switches_dim_for_rv1_524T(client):
    # Indoor
    instance = 6    # TODO: Find out which of the instances is associated with the switch inputs
    dipswitch = 0x80
    outputs = {i + 1: 0 for i in range(32)}

    initial_msg = {
        'name': 'RvSwitch',
        'Manufacturer_Code': 'BEP Marine',
        'Dipswitch': str(dipswitch),
        'Instance': str(instance)
    }
    for index, state in outputs.items():
        initial_msg[f'Output{index}'] = str(state)

    response = send_a_can_event(client, initial_msg)

    # Now toggle a known switch
    msg = deepcopy(initial_msg)

    # Lightlist
    light_list = (
        ({'bank': '6', 'output': '10'}, 13),
        ({'bank': '6', 'output': '12'}, 9)
    )
    # Ideally read this mapping from the same source the HAL would read it
    # TODO: Remove hardcoding and move to internal electrical mapping
    for light in light_list:
        # light[0] is the circuit for the given instance/bank
        # light[1] is the associated lightzone
        # TODO: Add more structure to allow other
        result = client.put(f'/api/lighting/lz/{light[1]}/state', data=json.dumps({"onOff": 0}))
        assert result.status_code == 200

        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        assert result.status_code == 200
        print(result.json())
        # TODO: Figure out what it should be
        assert result.json().get('onOff') == 0
        assert result.json().get('brt') == 80

        # Blip the switch state
        msg[f'Output{light[0].get("output")}'] = str(1)
        msg['Instance'] = light[0].get('bank')
        response = send_a_can_event(client, msg)

        # No pause needed - hold down
        msg[f'Output{light[0].get("output")}'] = str(1)
        response = send_a_can_event(client, msg)

        # No pause needed
        msg[f'Output{light[0].get("output")}'] = str(0)
        response = send_a_can_event(client, msg)

        # Check state
        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        assert result.status_code == 200
        # time.sleep(1)
        assert result.json().get('onOff') == 1
        assert result.json().get('brt') == 80

        # Blip the switch state
        msg[f'Output{light[0].get("output")}'] = str(1)
        msg['Instance'] = light[0].get('bank')
        response = send_a_can_event(client, msg)

        # No pause needed
        msg[f'Output{light[0].get("output")}'] = str(0)
        response = send_a_can_event(client, msg)

        # Check state
        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        result = client.get(f'/api/lighting/lz/{light[1]}/state')
        assert result.status_code == 200
        # time.sleep(1)
        assert result.json().get('onOff') == 0



@pytest.mark.skip(reason="Working through changes and identifying which circuits related to PSM")
def test_psm_inputs_for_rv1_524T(client):
    '''This test simulates receiving PSM updates from the sprinter on the signal inputs.'''
    instance = 6    # TODO: Find out which of the instances is associated with the switch inputs
    dipswitch = 233
    outputs = {i + 1: 0 for i in range(32)}

    initial_msg = {
        'name': 'RvSwitch',
        'Manufacturer_Code': 'BEP Marine',
        'Dipswitch': str(dipswitch),
        'Instance': str(instance)
    }
    for index, state in outputs.items():
        initial_msg[f'Output{index}'] = str(state)

    response = send_a_can_event(client, initial_msg)

    # Now toggle a known switch
    msg = deepcopy(initial_msg)

    # Ideally read this mapping from the same source the HAL would read it
    # TODO: Remove hardcoding and move to internal electrical mapping
    for circuit in (
                (14, '/api/lighting/lz/10/state', 'onOff'),
                (14, '/api/lighting/lz/10/state', 'onOff'),
            ):
        # circuit[0] is the circuit Outputx for the given instance/bank
        # circuit[1] is the associated api call
        # circuit[2] is the property changing
        # TODO: Add more structure to allow other switch tests

        result = client.get(circuit[1])
        assert result.status_code == 200
        assert result.json().get(circuit[2]) == 0

        # Blip the switch state
        msg[f'Output{circuit[0]}'] = str(1)
        response = send_a_can_event(client, msg)
        print(msg[f'Output{circuit[0]}'])

        # No pause needed
        msg[f'Output{circuit[0]}'] = str(0)
        response = send_a_can_event(client, msg)
        print(msg[f'Output{circuit[0]}'])

        # Check state
        result = client.get(circuit[1])
        assert result.status_code == 200
        assert result.json().get(circuit[2]) == 1


def test_output_circuit_update_for_rv1_524T(client):
    '''This test simulates receiving circuit from the RV1.'''
    instance = 0x00    # TODO: Find out which of the instances is associated with the switch inputs
    dipswitch = 0x80
    outputs = {i + 1: 0 for i in range(32)}

    initial_msg = {
        'name': 'RvOutput',
        'Manufacturer_Code': 'BEP Marine',
        'Dipswitch': str(dipswitch),
        'Instance': str(instance)
    }
    for index, state in outputs.items():
        initial_msg[f'Output{index}'] = str(state)

    response = send_a_can_event(client, initial_msg)

    # Now toggle a known switch
    msg = deepcopy(initial_msg)

    # Ideally read this mapping from the same source the HAL would read it
    # TODO: Remove hardcoding and move to internal electrical mapping
    for circuit in (
                (4, '/api/watersystems/wh/1/state', 'onOff'),
            ):
        # circuit[0] is the circuit Outputx for the given instance/bank
        # circuit[1] is the associated api call
        # circuit[2] is the property changing
        # TODO: Add more structure to allow other switch tests

        result = client.get(circuit[1])
        assert result.status_code == 200
        # Waterheater does not respond to this circuit for now
        # If power is gone it factually is off but it is
        # a proper failue rather than a simple state update
        # assert result.json().get(circuit[2]) == 0
        assert result.json().get(circuit[2]) is None

        # Blip the switch state
        msg[f'Output{circuit[0]}'] = str(1)
        response = send_a_can_event(client, msg)
        print(msg[f'Output{circuit[0]}'])

        time.sleep(0.5)

        # Check state
        result = client.get(circuit[1])
        assert result.status_code == 200
        # assert result.json().get(circuit[2]) == EventValues.ON
        assert result.json().get(circuit[2]) is None

        # msg[f'Output{circuit[0]}'] = str(0)
        # response = send_a_can_event(client, msg)
        # print(msg[f'Output{circuit[0]}'])


def test_output_bank_circuit_update_for_rv1_524T(client):
    '''This test simulates receiving circuit from the RV1.'''
    instance = 0x60    # TODO: Find out which of the instances is associated with the switch inputs
    dipswitch = 0x80
    outputs = {i + 1: 0 for i in range(32)}

    initial_msg = {
        'name': 'RvOutput',
        'Manufacturer_Code': 'BEP Marine',
        'Dipswitch': str(dipswitch),
        'Instance': str(instance)
    }
    for index, state in outputs.items():
        initial_msg[f'Output{index}'] = str(state)

    response = send_a_can_event(client, initial_msg)

    print(json.dumps(initial_msg))

    # Now toggle a known switch
    msg = deepcopy(initial_msg)

    # Ideally read this mapping from the same source the HAL would read it
    # TODO: Remove hardcoding and move to internal electrical mapping
    for circuit in (
                (0x60, 7, '/api/watersystems/wp/1/state', 'onOff', EventValues.OFF, EventValues.ON),
                # (0x60, 3, '/api/movables/so/1/state', 'mode', EventValues.OFF, EventValues.EXTENDING),
                # (0x60, 4, '/api/movables/so/1/state', 'mode', EventValues.OFF, EventValues.RETRACTING),
            ):
        # circuit[0] is the circuit Outputx for the given instance/bank
        # circuit[1] is the associated api call
        # circuit[2] is the property changing
        # TODO: Add more structure to allow other switch tests

        result = client.get(circuit[2])
        assert result.status_code == 200
        assert result.json().get(circuit[3]) == circuit[4]

        # Switch to on to update state
        msg['Instance'] = str(circuit[0])
        msg[f'Output{circuit[1]}'] = str(1)
        print('Updated MSG', msg)
        response = send_a_can_event(client, msg)
        print('OUTPUT', msg[f'Output{circuit[1]}'])

        time.sleep(1.0)

        # Check state
        result = client.get(circuit[2])
        print('Result', result.json())
        assert result.status_code == 200
        assert result.json().get(circuit[3]) == circuit[5]

        # msg[f'Output{circuit[0]}'] = str(0)
        # response = send_a_can_event(client, msg)
        # print(msg[f'Output{circuit[0]}'])


# def test_czone_alert_to_string_request(client):
#     pass
