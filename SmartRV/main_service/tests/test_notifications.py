import os
import sys
import logging
from datetime import datetime
import subprocess
import time
import importlib

logger = logging.getLogger(__name__)

from fastapi.testclient import TestClient
from main_service.wgo_main_service import app
from main_service.tests.utils import send_a_can_event, check_ui_notifications
from common_libs.models.common import RVEvents, EventValues
import pytest


def remove_db():
    file_path = '/storage/wgo/wgo_user.db'
    if os.path.isfile(file_path):
        os.remove(file_path)
    else:
        print(f"Error: {file_path} file not found")



@pytest.fixture
def client():

    remove_db()

    with TestClient(app) as c:
        c.put('/api/system/floorplan', json={'floorPlan': 'WM524T', 'optionCodes': '52D,33F,31P,33F,29J'})
        yield c



def test_water_sensor_voltage_alerts(client):
    FRESH = 101
    GRAY = 102
    BLACK = 103

    for sensor in (FRESH, GRAY, BLACK):
        SENSOR_OVERVOLTAGE = {
            "Instance": str(sensor),
            "Battery_Voltage": "6.0",
            # ...
            "msg_name": "Battery_Status",
            # ...
        }
        _ = send_a_can_event(client, SENSOR_OVERVOLTAGE)
        if sensor == FRESH:
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
            ) is True
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
            ) is False
        elif sensor == GRAY:
            assert check_ui_notifications(
                client,
                RVEvents.GRAY_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
            ) is True
            assert check_ui_notifications(
                client,
                RVEvents.GRAY_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
            ) is False
        elif sensor == BLACK:
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
            ) is True
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
            ) is False

    # NOTE: Currently no undervoltage alerts defined
    # for sensor in (FRESH, GRAY, BLACK):
    #     SENSOR_OVERVOLTAGE['Instance'] = str(sensor)
    #     SENSOR_OVERVOLTAGE["Battery_Voltage"] = "0.0"

    #     _ = send_a_can_event(client, SENSOR_OVERVOLTAGE)
    #     if sensor == FRESH:
    #         assert check_ui_notifications(
    #             client,
    #             RVEvents.FRESH_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
    #         ) is False
    #         assert check_ui_notifications(
    #             client,
    #             RVEvents.FRESH_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
    #         ) is True
    #     elif sensor == GRAY:
    #         assert check_ui_notifications(
    #             client,
    #             RVEvents.GRAY_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
    #         ) is False
    #         assert check_ui_notifications(
    #             client,
    #             RVEvents.GRAY_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
    #         ) is True
    #     elif sensor == BLACK:
    #         assert check_ui_notifications(
    #             client,
    #             RVEvents.BLACK_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
    #         ) is False
    #         assert check_ui_notifications(
    #             client,
    #             RVEvents.BLACK_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
    #         ) is True

    for sensor in (FRESH, GRAY, BLACK):
        SENSOR_OVERVOLTAGE = {
            "Instance": str(sensor),
            "Battery_Voltage": "5.0",
            # ...
            "msg_name": "Battery_Status",
            # ...
        }
        _ = send_a_can_event(client, SENSOR_OVERVOLTAGE)
        if sensor == FRESH:
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
            ) is False
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
            ) is False
        elif sensor == GRAY:
            assert check_ui_notifications(
                client,
                RVEvents.GRAY_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
            ) is False
            assert check_ui_notifications(
                client,
                RVEvents.GRAY_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
            ) is False
        elif sensor == BLACK:
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT.name
            ) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_SENSOR_UNDERVOLTAGE_ALERT.name
            ) is False


# Watersystems
def test_fresh_water_tank_alerts(client):
    '''Test all alerts for fresh water tank.'''
    INSTANCE = 1    # Fresh Tank
    for lvl in (0, 26, 50, 100, 0):
        msg = {
            "title": f'Tank {INSTANCE}',
            "Instance": str(INSTANCE),
            "Fluid_Type": "X Water",
            "Fluid_Level": str(lvl),
            # "Tank_Capacity": "0.1136",
            # "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        }
        _ = send_a_can_event(client, msg)

        if lvl == 0:
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_EMPTY.name) is True
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_FULL.name) is False

        elif lvl == 25:
            assert check_ui_notifications(
                client,
                RVEvents.FRESH_WATER_TANK_EMPTY.name) is False
            assert check_ui_notifications(
                client, RVEvents.FRESH_WATER_TANK_NOTICE.name) is True
            assert check_ui_notifications(
                client, RVEvents.FRESH_WATER_TANK_FULL.name) is False
        elif lvl == 50:
            assert check_ui_notifications(
                client, RVEvents.FRESH_WATER_TANK_EMPTY.name) is False
            assert check_ui_notifications(
                client, RVEvents.FRESH_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client, RVEvents.FRESH_WATER_TANK_FULL.name) is False
        elif lvl == 100:
            assert check_ui_notifications(
                client, RVEvents.FRESH_WATER_TANK_EMPTY.name) is False
            assert check_ui_notifications(
                client, RVEvents.FRESH_WATER_TANK_NOTICE.name) is False
            # NOTE: Fresh full is not a desired notifcation yet
            # assert check_ui_notifications(
            #     client, RVEvents.FRESH_WATER_TANK_FULL.name) is False


def test_gray_water_tank_alerts(client):
    '''Test all alerts for gray water tank.'''
    INSTANCE = 2    # Gray Tank
    for lvl in (0, 50, 76, 90, 100, 0):
        msg = {
            "title": f'Tank {INSTANCE}',
            "Instance": str(INSTANCE),
            "Fluid_Type": "X Water",
            "Fluid_Level": str(lvl),
            # "Tank_Capacity": "0.1136",
            # "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        }
        _ = send_a_can_event(client, msg)

        if lvl == 0:
            # NOTE: Gray water empty not a desired notification.
            # assert check_ui_notifications(
            #     client,
            #     RVEvents.GREY_WATER_TANK_EMPTY.name) is True
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_ABOVE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_FULL.name) is False
        elif lvl == 50:
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_ABOVE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_FULL.name) is False
        elif lvl == 90:
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_ABOVE.name) is True
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_FULL.name) is False
        elif lvl == 100:
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_ABOVE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.GREY_WATER_TANK_FULL.name) is True



def test_black_water_tank_alerts(client):
    '''Test all alerts for black water tank.'''
    INSTANCE = 3    # Black Tank
    # NOTE: Need to see the progression back down too
    for lvl in (0, 50, 75, 90, 100, 0):
        msg = {
            "title": f'Tank {INSTANCE}',
            "Instance": str(INSTANCE),
            "Fluid_Type": "X Water",
            "Fluid_Level": str(lvl),
            # "Tank_Capacity": "0.1136",
            # "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        }
        _ = send_a_can_event(client, msg)

        if lvl == 0:
            # NOTE: Black water empty not a desired notification.
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_ABOVE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_FULL.name) is False
        elif lvl == 50:
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_ABOVE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_FULL.name) is False
        elif lvl == 75:
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_NOTICE.name) is True
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_ABOVE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_FULL.name) is False
        elif lvl == 90:
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_ABOVE.name) is True
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_FULL.name) is False
        elif lvl == 100:
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_NOTICE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_ABOVE.name) is False
            assert check_ui_notifications(
                client,
                RVEvents.BLACK_WATER_TANK_FULL.name) is True


# Interior Temp
def test_interior_temp_high_low(client):
    '''Test to cover all alerts for temp high and low.
    COACH_TEMP_LOW = 50020
    COACH_TEMP_HIGH = 50021
    '''
    # Set temperature normal
    msg = {
        "title": 'Interior Temp',
        "Instance": "2",
        "name": "thermostat_ambient_status",
        "Ambient_Temp": "20"
    }
    _ = send_a_can_event(client, msg)

    # Alerts should be off when started
    assert check_ui_notifications(client, 'COACH_TEMP_HIGH') is False
    assert check_ui_notifications(client, 'COACH_TEMP_LOW') is False

    # Set Temp High
    msg = {
        "title": 'Interior Temp',
        "Instance": "2",
        "name": "thermostat_ambient_status",
        "Ambient_Temp": "40"
    }
    _ = send_a_can_event(client, msg)

    assert check_ui_notifications(client, 'COACH_TEMP_HIGH') is True
    assert check_ui_notifications(client, 'COACH_TEMP_LOW') is False

    # Set temperature normal
    msg = {
        "title": 'Interior Temp',
        "Instance": "2",
        "name": "thermostat_ambient_status",
        "Ambient_Temp": "20"
    }
    _ = send_a_can_event(client, msg)

    assert check_ui_notifications(client, 'COACH_TEMP_HIGH') is False
    assert check_ui_notifications(client, 'COACH_TEMP_LOW') is False

    # Set Temp Low
    msg = {
        "title": 'Interior Temp',
        "Instance": "2",
        "name": "thermostat_ambient_status",
        "Ambient_Temp": "-1.0"
    }
    _ = send_a_can_event(client, msg)

    assert check_ui_notifications(client, 'COACH_TEMP_HIGH') is False
    assert check_ui_notifications(client, 'COACH_TEMP_LOW') is True

    # Set temperature normal
    msg = {
        "title": 'Interior Temp',
        "Instance": "2",
        "name": "thermostat_ambient_status",
        "Ambient_Temp": "20"
    }
    _ = send_a_can_event(client, msg)

    assert check_ui_notifications(client, 'COACH_TEMP_HIGH') is False
    assert check_ui_notifications(client, 'COACH_TEMP_LOW') is False


# SOC Alerts
def test_soc_low(client):
    '''Test to cover alerting for low SOC and voltage ?.
    BATTERY_CHARGE_LOW = 50016
    BATTERY_CHARGE_LOW_CUTOFF = 50017
    '''
    for soc in (50, 15, 2, 50, 100):

        # Set good 50% SoC, charging
        msg = {
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge": str(float(soc)),
            "Time_Remaining": "201",
            "Time_Remaining_Interpretation": "Time to Full",
            "name": "DC_SOURCE_STATUS_2"
        }
        _ = send_a_can_event(client, msg)

        if soc == 2:
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_FULL.name) is False
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW.name) is False
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW_CUTOFF.name) is True
        elif soc == 15:
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_FULL.name) is False
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW.name) is True
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW_CUTOFF.name) is False
        elif soc == 50:
            # Alerts should be off when started
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_FULL.name) is False
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW.name) is False
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW_CUTOFF.name) is False
        elif soc == 100:
            # NOTE: Full has been removed as it caused too many notifications
            # assert check_ui_notifications(
            #     client, RVEvents.BATTERY_CHARGE_FULL.name) is True
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW.name) is False
            assert check_ui_notifications(
                client, RVEvents.BATTERY_CHARGE_LOW_CUTOFF.name) is False


# Test Shorepower Alert
def test_shore_connected_disconnected(client):
    '''Test to cover alerting for shore power being plugged in.
    SHORE_POWER_CONNECTED = 50024
    '''
    # Set shore off
    SHORE_OFF = {
        "Instance": "1",
        "RMS_Voltage": "120.0",
        "RMS_Current": "0.0",
        "Frequency": "",
        "name": "charger_ac_status_1"
    }
    SHORE_ON = {
        "Instance": "1",
        "RMS_Voltage": "120.0",
        "RMS_Current": "20.0",
        "Frequency": "",
        "name": "charger_ac_status_1"
    }
    _ = send_a_can_event(client, SHORE_OFF)

    assert check_ui_notifications(
        client, RVEvents.SHORE_POWER_CONNECTED.name) is False

    _ = send_a_can_event(client, SHORE_ON)
    assert check_ui_notifications(
        client, RVEvents.SHORE_POWER_CONNECTED.name) is True

    _ = send_a_can_event(client, SHORE_OFF)
    assert check_ui_notifications(
        client, RVEvents.SHORE_POWER_CONNECTED.name) is False
