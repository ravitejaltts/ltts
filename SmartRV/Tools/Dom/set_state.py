import json
import sys
import time

import requests

import random

distance = 154800


def get_random():
    scenario = [
        # {
        #     "DC_Instance": "Main House Battery Bank",
        #     "Device_Priority": "Battery SOC/BMS device",
        #     "Source_Temperature": "23.0",
        #     # "State_Of_Charge": "10.1",
        #     "State_Of_Charge": str(random.randint(0,100)),
        #     "Time_Remaining": "604",
        #     # "Time_Remaining_Interpretation": "Time to Full",
        #     "Time_Remaining_Interpretation": "Time to Empty",
        #     "name": "DC_SOURCE_STATUS_2",
        #     'instance_key': ''
        # },
        {
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            # "State_Of_Charge": "10.1",
            "State_Of_Charge": "100",    #    str(random.randint(0,100)),
            "Time_Remaining": "604",
            # "Time_Remaining_Interpretation": "Time to Full",
            "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        # {
        #     "Instance": "15",
        #     "Fluid_Type": "Live Well",
        #     # "Fluid_Level": "25.62",
        #     "Fluid_Level": str(random.randint(0,100)),
        #     "Tank_Capacity": "1.8927",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': '19F21101__0__15',
        # },
        # {
        #     "Instance": "14",
        #     "Fluid_Type": "Live Well",
        #     # "Fluid_Level": "39",
        #     "Fluid_Level": "40.5",
        #     "Tank_Capacity": str(random.randint(0,100)),
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': '19F21101__0__14'
        # },
        {
            "Instance": "2",
            "Fluid_Type": "Waste Water",
            "Fluid_Level": str(random.randint(0,100)),
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "Instance": "1",
            "Fluid_Type": "Fresh Water",
            "Fluid_Level": str(random.randint(0, 100)),
            "Tank_Capacity": "0.1136",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "Instance": "3",
            "Fluid_Type": "Black Water",
            "Fluid_Level": str(random.randint(0, 100)),
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        # {
        #     "Instance": "4",
        #     "Battery_Voltage": "13.780000000000001",
        #     # Factor 18 and assumed voltage of 53V for now
        #     # "Battery_Current": "0.0",
        #     "Battery_Current": str(random.randint(0,100)),
        #     "Sequence_ID": "0",
        #     "name": "Battery_Status"
        # },
        # Circuit Status SCI
        # {
        #     "Manufacturer_Code": "BEP Marine",
        #     "Dipswitch": "4",
        #     "Instance": "11",
        #     "Output1": str(random.randint(0,1)),
        #     "Output2": str(random.randint(0,1)),
        #     "Output3": str(random.randint(0,1)),
        #     "Output4": str(random.randint(0,1)),
        #     "Output5": str(random.randint(0,1)),
        #     "Output6": str(random.randint(0,1)),
        #     "Output7": str(random.randint(0,1)),
        #     "Output8": str(random.randint(0,1)),
        #     "Output9": "0",
        #     "Output10": "0",
        #     "Output11": "0",
        #     "Output12": "0",
        #     "Output13": "0",
        #     "Output14": "0",
        #     "Output15": "0",
        #     "Output16": "0",
        #     "Output17": "0",
        #     "Output18": "0",
        #     "Output19": "0",
        #     "Output20": "0",
        #     "Output21": "0",
        #     "Output22": "0",
        #     "Output23": "0",
        #     "Output24": "0",
        #     "Byte8": "0",
        #     "name": "Heartbeat"
        # },
        # Circuit Status KEYPAD
        {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "1",
            "Instance": "29",
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "0",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "1",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        },
        # Circuit Status CZone
        # {
        #     "Manufacturer_Code": "BEP Marine",
        #     "Dipswitch": "1",
        #     "Instance": "54",
        #     # "Output1": "1",
        #     # "Output2": "1",
        #     # "Output3": "1",
        #     # "Output4": "1",
        #     # "Output5": "0",
        #     # "Output6": "0",
        #     # "Output7": "0",
        #     # "Output8": "0",
        #     # "Output9": "0",
        #     # "Output10": "0",
        #     # "Output11": "0",
        #     # "Output12": "0",
        #     # "Output13": "0",
        #     # "Output14": "0",
        #     # "Output15": "0",
        #     # "Output16": "0",
        #     # "Output17": "0",
        #     # "Output18": "0",
        #     # "Output19": "0",
        #     # "Output20": "0",
        #     # "Output21": "0",
        #     "Output22": str(random.randint(0,1)),
        #     # "Output23": "0",
        #     # "Output24": "0",
        #     "Byte8": "0",
        #     "name": "Heartbeat"
        # },
        # Interior
        # {
        #     "Instance": "4",
        #     "Ambient_Temp": str(random.randint(8,34)),
        #     # "Ambient_Temp": "-45.0000",

        #     # 0 Fahrenheit - Error case for Thermistor
        #     # "Ambient_Temp": "-17.78125",
        #     "name": "Ambient_Temperature"
        # },
        # Fridge
        # {
        #     "Instance": "55",
        #     "Ambient_Temp": str(random.randint(1,20)),
        #     "name": "thermostat_ambient_status"
        # },
        # {
        #     "Instance": "2",
        #     "Ambient_Temp": str(random.randint(40,60)),
        #     "name": "thermostat_ambient_status"
        # },
        # {
        #     "Instance": "2",
        #     "Ambient_Temp": str(random.randint(40,50)),
        #     "name": "thermostat_ambient_status"
        # },
        # {
        #     "Instance": "2",
        #     "Ambient_Temp": str(random.randint(0,5)),
        #     "name": "thermostat_ambient_status"
        # },
        {
            "Instance": "4",
            "Ambient_Temp": str(random.randint(0,5)),
            "name": "thermostat_ambient_status"
        },
        # {
        #     "Instance": "3",
        #     "Ambient_Temp": str(random.randint(0,40)),
        #     "name": "thermostat_ambient_status"
        # },
        # {
        #     "Instance": "4",
        #     "Ambient_Temp": str(input('temp:')),
        #     "name": "thermostat_ambient_status"
        # },
        {
            "Instance": "249",
            "Ambient_Temp": str(random.randint(1,20)),
            "name": "thermostat_ambient_status"
        },
        # Lighting Status Controller 1
        # Lighting Status Controller 2
        # Circuit Status CZone Control X +
        # Circuit Status SI
        # {
        #     "Charge_Percent": str(random.randint(0,12)),
        #     "name": "STATE_OF_CHARGE",
        #     'instance_key': ''
        # },
        # {
        #     "Distance_Traveled": str(distance),
        #     "name": "odo_odometer",
        #     'instance_key': ''
        # },
        {
            "name": "AAT_AMBIENT_AIR_TEMPERATURE",
            "Temperature": str(random.randint(0,40))
        },
        # {
        #     "name": "PB_PARK_BRAKE",
        #     "Park_Break_Status": "applied"
        #     # "Park_Break_Status": "released"
        #     # "Park_Break_Status": "invalid data"
        # }
    ]

    return scenario


SCENARIOS = {
    'DEFAULT': [
        {
            "title": "Setting cold",
            "Instance": "4",
            "Ambient_Temp": str("3"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Setting hot",
            "Instance": "4",
            "Ambient_Temp": str("40"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Setting ok",
            "Instance": "4",
            "Ambient_Temp": str("20"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "House Battery Full - Discharging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge": "100",
            "Time_Remaining": "604",
            # "Time_Remaining_Interpretation": "Time to Full",
            "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 20 - Discharging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge":  "20",
            "Time_Remaining": "30",
            # "Time_Remaining_Interpretation": "Time to Full",
            "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 20 - Charging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge":  "20",
            "Time_Remaining": "134",
            "Time_Remaining_Interpretation": "Time to Full",
            # "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 0 - Charging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge":  "20",
            "Time_Remaining": "134",
            "Time_Remaining_Interpretation": "Time to Full",
            # "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": 'Tank 2 - Fresh - 100 %',
            "Instance": "1",
            "Fluid_Type": "Fresh Water",
            "Fluid_Level": "0.0",
            "Tank_Capacity": "0.1136",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "title": 'Tank 1 - Fresh - Empty',
            "Instance": "1",
            "Fluid_Type": "Fresh Water",
            "Fluid_Level": "0.0",
            "Tank_Capacity": "0.1136",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "title": 'Tank 1 - Fresh - 50 %',
            "Instance": "1",
            "Fluid_Type": "Fresh Water",
            "Fluid_Level": "0.0",
            "Tank_Capacity": "0.1136",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "title": 'Tank 2 - Waste - 50%',
            "Instance": "2",
            "Fluid_Type": "Waste Water",
            "Fluid_Level": "50",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "title": 'Tank 2 - Waste - 99.9%',
            "Instance": "2",
            "Fluid_Type": "Waste Water",
            "Fluid_Level": "99.9",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "title": 'Tank 2 - Waste - 0%',
            "Instance": "2",
            "Fluid_Type": "Waste Water",
            "Fluid_Level": "0",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        # {
        #     "Instance": "15",
        #     "Fluid_Type": "Live Well",
        #     # "Fluid_Level": "25.62",
        #     "Fluid_Level": "12.62",
        #     "Tank_Capacity": "1.8927",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': '19F21101__0__15',
        # },
        # {
        #     "Instance": "14",
        #     "Fluid_Type": "Live Well",
        #     "Fluid_Level": "39",
        #     # "Fluid_Level": "40.5",
        #     "Tank_Capacity": "1.8927",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': '19F21101__0__14'
        # },
        # {
        #     "Instance": "4",
        #     "Battery_Voltage": "13.780000000000001",
        #     # Factor 18 and assumed voltage of 53V for now
        #     # "Battery_Current": "0.0",
        #     "Battery_Current": "85.0",
        #     "Sequence_ID": "0",
        #     "name": "Battery_Status"
        # },
        # # Circuit Status SCI
        # {
        #     "Manufacturer_Code": "BEP Marine",
        #     "Dipswitch": "4",
        #     "Instance": "11",
        #     "Output1": "0",
        #     "Output2": "1",
        #     "Output3": "0",
        #     "Output4": "0",
        #     "Output5": "0",
        #     "Output6": "0",
        #     "Output7": "0",
        #     "Output8": "0",
        #     "Output9": "0",
        #     "Output10": "0",
        #     "Output11": "0",
        #     "Output12": "0",
        #     "Output13": "0",
        #     "Output14": "0",
        #     "Output15": "0",
        #     "Output16": "0",
        #     "Output17": "0",
        #     "Output18": "0",
        #     "Output19": "0",
        #     "Output20": "0",
        #     "Output21": "0",
        #     "Output22": "0",
        #     "Output23": "0",
        #     "Output24": "0",
        #     "Byte8": "0",
        #     "name": "Heartbeat"
        # },
        # # Circuit Status CZone
        # {
        #     "Manufacturer_Code": "BEP Marine",
        #     "Dipswitch": "1",
        #     "Instance": "54",
        #     # "Output1": "1",
        #     # "Output2": "1",
        #     # "Output3": "1",
        #     # "Output4": "1",
        #     # "Output5": "0",
        #     # "Output6": "0",
        #     # "Output7": "0",
        #     # "Output8": "0",
        #     # "Output9": "0",
        #     # "Output10": "0",
        #     # "Output11": "0",
        #     # "Output12": "0",
        #     # "Output13": "0",
        #     # "Output14": "0",
        #     # "Output15": "0",
        #     # "Output16": "0",
        #     # "Output17": "0",
        #     # "Output18": "0",
        #     # "Output19": "0",
        #     # "Output20": "0",
        #     # "Output21": "0",
        #     "Output22": "0",
        #     # "Output23": "0",
        #     # "Output24": "0",
        #     "Byte8": "0",
        #     "name": "Heartbeat"
        # },
        # # Interior
        # {
        #     "Instance": "4",
        #     "Ambient_Temp": "21.50",
        #     # "Ambient_Temp": "-45.0000",

        #     # 0 Fahrenheit - Error case for Thermistor
        #     # "Ambient_Temp": "-17.78125",
        #     "name": "Ambient_Temperature"
        # },
        # # Fridge
        # {
        #     "Instance": "55",
        #     "Ambient_Temp": "3",
        #     "name": "Ambient_Temperature"
        # },
        # # Lighting Status Controller 1
        # # Lighting Status Controller 2
        # # Circuit Status CZone Control X +
        # # Circuit Status SI
        # {
        #     "Charge_Percent": str(random.randint(0,100)),
        #     "name": "STATE_OF_CHARGE",
        #     'instance_key': ''
        # },
        # {
        #     "Distance_Traveled": str(distance),
        #     "name": "odo_odometer",
        #     'instance_key': ''
        # },
        # {
        #     "name": "AAT_AMBIENT_AIR_TEMPERATURE",
        #     "Temperature": "16"
        # },
        # # {
        # #     "name": "PB_PARK_BRAKE",
        # #     "Park_Break_Status": "applied"
        # #     # "Park_Break_Status": "released"
        # #     # "Park_Break_Status": "invalid data"
        # # }
    ],
    'SOLAR': [
        {
            'title': 'Set Solar - 0 Watts',
            'Instance': '1',
            'Charge_Voltage': '12.3',
            'Charge_Current': '0',
            'name': 'solar_controller_status'
        },
        {
            'title': 'Set Solar - 250 Watts',
            'Instance': '1',
            'Charge_Voltage': '12.3',
            'Charge_Current': '20.32',
            'name': 'solar_controller_status'
        },
        {
            'title': 'Set Shore Power - 0',
            'name': 'charger_ac_status_1',
            'Instance': '1',
            'RMS_Voltage': '120',
            'RMS_Current': '0',
            'Frequency': '60',
        },
        {
            'title': 'Set Shore Power - 3600',
            'name': 'charger_ac_status_1',
            'Instance': '1',
            'RMS_Voltage': '120',
            'RMS_Current': '30',
            'Frequency': '60',
        }
    ],
    'CLIMATE': [
        {
            "title": "Setting cold",
            "Instance": "2",
            "Ambient_Temp": str("3"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Setting hot",
            "Instance": "2",
            "Ambient_Temp": str("40"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Setting Invalid Temp -17.78125 C",
            "Instance": "2",
            "Ambient_Temp":  "-17.78125",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Setting Normal Temp - 68 F / 20 C",
            "Instance": "2",
            "Ambient_Temp": str("20"),
            "name": "thermostat_ambient_status"
        },
    ],
    'CLIMATE_HOT': [
        {
            "title": "Setting hot",
            "Instance": "2",
            "Ambient_Temp": str("40"),
            "name": "thermostat_ambient_status"
        },
    ],
    'HOUSEBATTERY': [
        {
            "title": "House Battery Out of Range Voltage",
            "DC_Instance": "Main House Battery Bank",
            "DC_Voltage": "1233.780000000000001",
            "DC_Current": "160.0",
            "name": "DC_SOURCE_STATUS_1",
        },
        {
            "title": "House Battery Full - Discharging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge": "100",
            "Time_Remaining": "604",
            # "Time_Remaining_Interpretation": "Time to Full",
            "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery Full - Discharging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge": "100",
            "Time_Remaining": "604",
            # "Time_Remaining_Interpretation": "Time to Full",
            "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 20 - Discharging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge":  "20",
            "Time_Remaining": "30",
            # "Time_Remaining_Interpretation": "Time to Full",
            "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 20 - Charging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge":  "20",
            "Time_Remaining": "134",
            "Time_Remaining_Interpretation": "Time to Full",
            # "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 0 - Charging",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge":  "0",
            "Time_Remaining": "134",
            "Time_Remaining_Interpretation": "Time to Full",
            # "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 0 - HOT",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "120.0",
            "State_Of_Charge":  "50",
            "Time_Remaining": "134",
            "Time_Remaining_Interpretation": "Time to Full",
            # "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        {
            "title": "House Battery 0 - NORMAL TEMP",
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "30.0",
            "State_Of_Charge":  "50",
            "Time_Remaining": "134",
            "Time_Remaining_Interpretation": "Time to Full",
            # "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            'instance_key': ''
        },
        [
            {
                "title": "House Battery 0 - NORMAL TEMP",
                "DC_Instance": "Main House Battery Bank",
                "Device_Priority": "Battery SOC/BMS device",
                "Source_Temperature": "30.0",
                "State_Of_Charge":  "50",
                "Time_Remaining": "134",
                "Time_Remaining_Interpretation": "Time to Full",
                # "Time_Remaining_Interpretation": "Time to Empty",
                "name": "DC_SOURCE_STATUS_2",
                'instance_key': ''
            }

        ]

    ],
    'LEVELS': [
        {
            "title": 'Tank 4 - LP Tank 1',
            "Instance": "4",
            "Fluid_Type": "LP",
            "Fluid_Level": "90",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "title": 'Tank 4 - LP Tank 1',
            "Instance": "4",
            "Fluid_Type": "LP",
            "Fluid_Level": "0",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        # {
        #     "title": 'Tank 1 - Fresh - 100 %',
        #     "Instance": "1",
        #     "Fluid_Type": "Fresh Water",
        #     "Fluid_Level": "100",
        #     "Tank_Capacity": "0.1136",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # {
        #     "title": 'Tank 1 - Fresh - Empty',
        #     "Instance": "1",
        #     "Fluid_Type": "Fresh Water",
        #     "Fluid_Level": "0.0",
        #     "Tank_Capacity": "0.1136",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # {
        #     "title": 'Tank 1 - Fresh - 50 %',
        #     "Instance": "1",
        #     "Fluid_Type": "Fresh Water",
        #     "Fluid_Level": "50",
        #     "Tank_Capacity": "0.1136",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # {
        #     "title": 'Tank 2 - Waste - 50%',
        #     "Instance": "2",
        #     "Fluid_Type": "Waste Water",
        #     "Fluid_Level": "50",
        #     "Tank_Capacity": "0.0795",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # {
        #     "title": 'Tank 2 - Waste - 99.9%',
        #     "Instance": "2",
        #     "Fluid_Type": "Waste Water",
        #     "Fluid_Level": "99.9",
        #     "Tank_Capacity": "0.0795",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # {
        #     "title": 'Tank 2 - Waste - 0%',
        #     "Instance": "2",
        #     "Fluid_Type": "Waste Water",
        #     "Fluid_Level": "0",
        #     "Tank_Capacity": "0.0795",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # {
        #     "title": 'Tank 3 - Black - 0%',
        #     "Instance": "3",
        #     "Fluid_Type": "Black Water",
        #     "Fluid_Level": "0",
        #     "Tank_Capacity": "0.0795",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # {
        #     "title": 'Tank 3 - Black - 90%',
        #     "Instance": "3",
        #     "Fluid_Type": "Black Water",
        #     "Fluid_Level": "90",
        #     "Tank_Capacity": "0.0795",
        #     "NMEA_Reserved": "255",
        #     "name": "FLUID_LEVEL",
        #     'instance_key': ''
        # },
        # [
        #     {
        #         "title": 'Tank 3 - Black - 100%',
        #         "Instance": "3",
        #         "Fluid_Type": "Black Water",
        #         "Fluid_Level": "100",
        #         "Tank_Capacity": "0.0795",
        #         "NMEA_Reserved": "255",
        #         "name": "FLUID_LEVEL",
        #         'instance_key': ''
        #     },
        #     {
        #         "title": 'Tank 2 - Waste - 100%',
        #         "Instance": "2",
        #         "Fluid_Type": "Waste Water",
        #         "Fluid_Level": "100",
        #         "Tank_Capacity": "0.0795",
        #         "NMEA_Reserved": "255",
        #         "name": "FLUID_LEVEL",
        #         'instance_key': ''
        #     },
        #     {
        #         "title": 'Tank 1 - Fresh - 50 %',
        #         "Instance": "1",
        #         "Fluid_Type": "Fresh Water",
        #         "Fluid_Level": "100",
        #         "Tank_Capacity": "0.1136",
        #         "NMEA_Reserved": "255",
        #         "name": "FLUID_LEVEL",
        #         'instance_key': ''
        #     }
        # ]
    ],
    'KEYPAD': [
        {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "1",
            "Instance": "29",
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "1",
            "Output6": "1",
            "Output7": "1",
            "Output8": "1",
            "Output9": "0",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        },
        {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "1",
            "Instance": "29",
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "0",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "0",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        },
        {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "1",
            "Instance": "29",
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "0",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "0",
            "Output10": "1",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        },
        {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "1",
            "Instance": "29",
            "Output1": "0",
            "Output2": "0",
            "Output3": "0",
            "Output4": "0",
            "Output5": "0",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "0",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": "0",
            "Output14": "0",
            "Output15": "0",
            "Output16": "0",
            "Output17": "0",
            "Output18": "0",
            "Output19": "0",
            "Output20": "0",
            "Output21": "0",
            "Output22": "0",
            "Output23": "0",
            "Output24": "0",
            "Byte8": "0",
            "name": "Heartbeat"
        },
    ],
    'CLIMATE_CAN_TEST': [
        {
            "title": "Setting Interior",
            "Instance": "2",
            "Ambient_Temp": str("20"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "AC Unit Temp",
            "Instance": "1",
            "Ambient_Temp": str("25"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Outdoor Temp",
            "Instance": str(0xf9),
            "Ambient_Temp": str("30"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Bathroom",
            "Instance": "3",
            "Ambient_Temp": str("35"),
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Fridge",
            "Instance": str(55),
            "Ambient_Temp": "40",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Freezer",
            "Instance": str(56),
            "Ambient_Temp": "45",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Fridge",
            "Instance": str(55),
            "Ambient_Temp": "41",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Freezer",
            "Instance": str(56),
            "Ambient_Temp": "46",
            "name": "thermostat_ambient_status"
        }
    ],
    'ROOF_FAN': [
        {
            'title': 'Set Main FAN',
            'Instance': '2',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '60.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        },
        {
            'title': 'Set Main FAN- LOW',
            'Instance': '2',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '20.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        },
        {
            'title': 'Set Main FAN - Dome Closed',
            'Instance': '2',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '60.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Closed',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        },
        {
            'title': 'Set Bath FAN',
            'Instance': '3',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '60.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        },
        {
            'title': 'Set Bath FAN - LOW Speed',
            'Instance': '3',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '20.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Open',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        },
        {
            'title': 'Set Bath FAN - Closed',
            'Instance': '3',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '60.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Closed',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        },
        {
            'title': 'Set UNKNOWN FAN',
            'Instance': '5',
            'System_Status': 'Off',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '60.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Closed',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        },
        {
            'title': 'Set Main FAN- On, Closed, 100 % Speed',
            'Instance': '2',
            'System_Status': 'On',
            'Fan_Mode': 'Auto',
            'Speed_Mode': 'Auto (Variable)',
            'Light': 'Off',
            'Fan_Speed_Setting': '100.0',
            'Wind_Direction_Switch': 'Air Out',
            'Dome_Position': 'Closed',
            'Deprecated': '0',
            'Ambient_Temperature': '-273.0',
            'Setpoint': '-273.0',
            'name': 'roof_fan_status_1',
            'instance_key': '19FEA7CE__0__2'
        }
    ],
    'RV1_CIRCUIT_TEST': [
        {
            "title": "Set all Outputs on bank0 to 0",
            "name": "RvOutput",
            "Manufacturer_Code":
            "BEP Marine",
            "Dipswitch": "233",
            "Instance": "0",
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0", "Output5": "0", "Output6": "0", "Output7": "0", "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": "0", "Output14": "0", "Output15": "0", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        },
        {
            "title": "Set Output 14 to 1",
            "name": "RvOutput",
            "Manufacturer_Code":
            "BEP Marine",
            "Dipswitch": "233",
            "Instance": str(int(0)),
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0", "Output5": "0", "Output6": "0", "Output7": "0", "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": "0",
            "Output14": "1", "Output15": "1", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        },
        {
            "title": "Set Output 103 to 1",
            "name": "RvOutput",
            "Manufacturer_Code":
            "BEP Marine",
            "Dipswitch": "233",
            "Instance": str(int(0x60)),
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0", "Output5": "0", "Output6": "0", "Output7": "1", "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": "0",
            "Output14": "1", "Output15": "1", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        },
        {
            "title": "Set Output 103 to 0",
            "name": "RvOutput",
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "233",
            "Instance": str(int(0x60)),
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0", "Output5": "0", "Output6": "0", "Output7": "0", "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": "0",
            "Output14": "0", "Output15": "0", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        }
    ],
    'WATER_HEATER': [
        # CM_ "1FFF7";
        # BO_ 2181035776 WATERHEATER_STATUS: 8  Vector__XXX
        #     SG_ Instance:
        #         0|8@1+  (1,0)   [0|255] ""    Vector__XXX
        #     SG_ Operating_Mode:
        #         8|8@1+  (1,0)   [0|255] ""    Vector__XXX
        #     SG_ Heat_Set_Point:
        #         16|16@1+  (0.03125,-273) [-8736|56799] "deg C"    Vector__XXX

        # VAL_ 2181035776 Operating_Mode
        #     0 "Off"
        #     1 "Combustion (Aquago/Combi)"
        #     2 "Electric (Combi only)"
        #     3 "Combustion & Electric (Combi only)"
        #     255 "Data Invalid";
        {
            "title": "Set Water Heater State Set_Point_temp to 40 C",
            "name": "waterheater_status",
            "Instance": "1",
            "Operating_Mode": "Combustion (Aquago/Combi)",
            "Heat_Set_Point": "40"
        },
        {
            "title": "Set Water Heater State Set_Point_temp to 35 C",
            "name": "waterheater_status",
            "Instance": "1",
            "Operating_Mode": "Combustion (Aquago/Combi)",
            "Heat_Set_Point": "35"
        },
        {
            "title": "Set Water Heater State Set_Point_temp to 34 C",
            "name": "waterheater_status",
            "Instance": "1",
            "Operating_Mode": "Combustion (Aquago/Combi)",
            "Heat_Set_Point": "34"
        },
        {
            "title": "Set Water Heater onOff to 0",
            "name": "waterheater_status",
            "Instance": "1",
            "Operating_Mode": "Off",
            "Heat_Set_Point": "40"
        }
    ],
    'WATER_HEATER_LOCKOUT': [
        {
            "title": "Set Water Heater Mode to decalcification",
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "DeCalc.(status only)"
        },
        {
            "title": "Set Water Heater Mode to ECO",
            "name": "waterheater_status_2",
            "Instance": "1",
            "Heat_Level": "Low level (ECO)"
        }
    ],
    'PSM_RV1_SWITCH_INPUT_TEST': [
        {
            "title": "Set all Switch Inputs on bank 4 to 0",
            "name": "rvswitch",
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": str(0x80),
            "Instance": str(0x04),
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0", "Output5": "0", "Output6": "0", "Output7": "0", "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": "0", "Output14": "0", "Output15": "0", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        },
        {
            "title": "Set Pin C5.13 to 1 (Output7)",
            "name": "rvswitch",
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": str(0x80),
            "Instance": str(0x4),
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0", "Output5": "0", "Output6": "0",
            "Output7": "1",
            "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": "0", "Output14": "1", "Output15": "1", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        },
        {
            "title": "Set Pin C5.14 to 1 (Output5)",
            "name": "rvswitch",
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": str(0x80),
            "Instance": str(0x4),
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0",
            "Output5": "1",
            "Output6": "0", "Output7": "0", "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": "0", "Output14": "1", "Output15": "1", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        }
    ],
    'UNSUPPORTED_MSG': [
        {
            'Instance': '14',
            'Fluid_Type': 'Live Well',
            'Fluid_Level': '40.5',
            'Tank_Capacity': '50',
            'NMEA_Reserved': '255',
            'name': 'FLUID_LEVEL',
            'instance_key':
            '19F21101__0__14'
        },
    ],
    'FRIDGE': [
        {
            "title": "Fridge Data Invalid",
            "Instance": "55",
            "Ambient_Temp": "Data Invalid",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Fridge In Default Range",
            "Instance": "55",
            "Ambient_Temp": "2",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Fridge Out of Default Range",
            "Instance": "55",
            "Ambient_Temp": "6",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Fridge Still out of Default Range",
            "Instance": "55",
            "Ambient_Temp": "6",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Fridge In Default Range",
            "Instance": "55",
            "Ambient_Temp": "2",
            "name": "thermostat_ambient_status"
        },
        {
            "title": "Fridge Still In Default Range",
            "Instance": "55",
            "Ambient_Temp": "2",
            "name": "thermostat_ambient_status"
        }
    ],
    'AWNING': [
        {
            "title": "Awning - Fully Retracted",
            "Instance": "1",
            "name": "awning_status",
            "Motion": "No Motion",
            "Position": "Retracted"
        },
        {
            "title": "Awning - Extending: 25%",
            "Instance": "1",
            "name": "awning_status",
            "Motion": "Extending",
            "Position": "50"
        },
        {
            "title": "Awning - Extending: 90%",
            "Instance": "1",
            "name": "awning_status",
            "Motion": "Extending",
            "Position": "180"
        },
        {
            "title": "Awning - Extended: 100%",
            "Instance": "1",
            "name": "awning_status",
            "Motion": "No motion",
            "Position": "100% Extended"
        },
        {
            "title": "Awning - Retracting: 60%",
            "Instance": "1",
            "name": "awning_status",
            "Motion": "Retracting",
            "Position": "120"
        },

    ]
}


if __name__ == '__main__':
    import random

    hosts = [
        # ('localhost', 8000),
        ('10.11.12.118', 8000),
        # ('canvm', 8000),
        # ('10.11.12.180', 8000),
        # ('10.11.12.123', 8000),
        # ('10.211.55.3', 8000),
        # ('192.168.8.184', 8000),
        # ('172.16.100.50', 8000),
        # ('192.168.12.203', 8000),
    ]

    loop = True

    try:
        scenario = sys.argv[1]
        run_scenario = SCENARIOS.get(scenario)
    except IndexError as err:
        print('No scenario provided, using DEFAULT', err)
        scenario = 'DEFAULT'
        run_scenario = SCENARIOS.get(scenario)


    if run_scenario is None:
        print('Available Scenarios')
        [print(x) for x, _ in SCENARIOS.items()]
        sys.exit(1)


    while True:
        distance += 1000
        for i, msg in enumerate(run_scenario):
            if isinstance(msg, type([])):
                # Run multiple steps
                msgs = msg
                title = 'Group Setting: ' + msg[0].get('title', 'NA')
            else:
                msgs = [msg,]
                title = 'Setting: ' + msg.get('title', 'NA')

            print(title, '-- Enter to run')
            input()

            for host in hosts:
                for msg in msgs:
                    api = f'http://{host[0]}:{host[1]}/api/can/event/'
                    # if msg.get('Instance') == "4":
                    #     temp = random.randint(10, 40)
                    #     msg['Ambient_Temp'] = str(temp)
                    url = api + msg.get('name').lower()
                    print('Calling', url, msg)
                    try:
                        result = requests.put(url, json=msg)
                        print(result)
                        print(result.json())
                    except Exception as err:
                        print(err)

        # run_scenario = get_random()

        print('Next loop')

        if loop is True:
            time.sleep(1)
            # pass
        else:
            break
