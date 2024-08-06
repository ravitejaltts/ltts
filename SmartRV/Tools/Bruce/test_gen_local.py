import json
import sys
import time

import requests

import random

distance = 154800
toggle_onOff = 1

def get_gen_test():
    scenario = [
        {
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "State_Of_Health": "95",
            "Capacity_Remaining": "75",
            "name": "DC_SOURCE_STATUS_3",
            "instance_key": "",
        },
        {
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            "State_Of_Charge": "77",
            "Time_Remaining": "604",
            "Time_Remaining_Interpretation": "Time to Empty",
            "name": "DC_SOURCE_STATUS_2",
            "instance_key": "",
        },
        {
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "DC_Voltage": "51.780000000000001",
            "DC_Current": "4.0",
            "name": "dc_source_status_1",
            "instance_key": "",
        },
        {
            "Instance": "15",
            "Fluid_Type": "Live Well",
            "Fluid_Level": "55.62",
            "Tank_Capacity": "1.8927",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            "instance_key": "19F21101__0__15",
        },
        {
            "Instance": "14",
            "Fluid_Type": "Live Well",
            "Fluid_Level": "40.5",
            "Tank_Capacity": "50",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            "instance_key": "19F21101__0__14",
        },
        {
            "Instance": "2",
            "Fluid_Type": "Waste Water",
            "Fluid_Level": "31",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            "instance_key": "",
        },
        {
            "Instance": "3",
            "Fluid_Type": "Black Water",
            "Fluid_Level": "24",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            "instance_key": "",
        },
        {
            "Instance": "1",
            "Fluid_Type": "Fresh Water",
            "Fluid_Level": "66",
            "Tank_Capacity": "0.1136",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            "instance_key": "",
        },
        {
            "Instance": "4",
            "Battery_Voltage": "51.780000000000001",
            # Factor 18 and assumed voltage of 53V for now
            # "Battery_Current": "0.0",
            "Battery_Current": "17.2",
            "Sequence_ID": "0",
            "name": "Battery_Status",
        },
        {
            "title": 'Fuel Tank - LP - 50 %',
            "Instance": 4,
            "Fluid_Type": "PROPANE",
            "Fluid_Level": str(50),
            # "Tank_Capacity": "0.1136",
            # "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        # Circuit Status SCI
        # {
        #     "Manufacturer_Code": "BEP Marine",
        #     "Dipswitch": "4",
        #     "Instance": "11",
        #     "Output1": str(random.randint(0, 1)),
        #     "Output2": str(random.randint(0, 1)),
        #     "Output3": str(random.randint(0, 1)),
        #     "Output4": str(random.randint(0, 1)),
        #     "Output5": str(random.randint(0, 1)),
        #     "Output6": str(random.randint(0, 1)),
        #     "Output7": str(random.randint(0, 1)),
        #     "Output8": str(random.randint(0, 1)),
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
        #     "name": "Heartbeat",
        # },
        # Circuit Status CZone
        {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "128",
            "Instance": "4",
            "Output1": "1",
            "Output2": "1",
            "Output3": "1",
            "Output4": "1",
            "Output5": "0",
            "Output6": "0",
            "Output7": "0",
            "Output8": "0",
            "Output9": "0",
            "Output10": "0",
            "Output11": "0",
            "Output12": "0",
            "Output13": str(toggle_onOff),
            #"Output13": str(1),
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
            "name": "RvSwitch",
        },
        # {
        # "Instance": "1",
        # "Position": "55",
        # "Motion": "Extending",
        # "name": "Awning_Status"
        # },
        # Outdoors
        {
            "Ambient_Temp": "3",
            "Instance": str(0xF9),      # TM-1010 sensor
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        },
        # ?? interior
        {
            "Instance": "2",
            "Ambient_Temp": "29" if toggle_onOff else "34",
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        },
        # # Fridge
        # {
        #     "Instance": "55",
        #     "Ambient_Temp": "3",
        #     "name": "thermostat_ambient_status",
        # },
        # Freezer ???
        # {
        #     "Instance": "56",
        #     "Ambient_Temp": "1",
        #     "name": "thermostat_ambient_status",
        # },
        # Lighting Status Controller 1
        # Lighting Status Controller 2
        # Circuit Status CZone Control X +
        # Circuit Status SI
        {
            "Charge_Percent": "9",
            "name": "STATE_OF_CHARGE",
            "instance_key": "",
        },
        {
            "Distance_Traveled": "2440",
            "name": "odo_odometer",
            "instance_key": "",
        },
        {
            "name": "AAT_AMBIENT_AIR_TEMPERATURE",
            "Temperature": "31",
        },
        # {
        #     "Instance": "1",
        #     "RMS_voltage": "118.65",
        #     "RMS_current": "5.0",
        #     "Frequency": "60.3046875",
        #     "name": "CHARGER_AC_STATUS_1",
        #     "instance_key": "19FFCAE1__0__1",
        # },
        # {
        #     "Instance": "65",
        #     "RMS_voltage": "118.65",
        #     "RMS_current": "5.0",
        #     "Frequency": "59.90625",
        #     "name": "INVERTER_AC_STATUS_1",
        #     "instance_key": "19FFD7E1__0__65",
        # },
        {
            "Charger_Instance": "49",
            "DC_Source_Instance": "1",
            "Charger_priority": "70",
            "Charge_voltage": "52.2",
            "Charge_current": "2",
            "Charger_temperature": "35",
            "name": "CHARGER_STATUS_2",
            "instance_key": "19FEA380__0__NA",
        },
        {
            "name": "PB_PARK_BRAKE",
            "Park_Break_Status": "applied"
            # "Park_Break_Status": "released"
            # "Park_Break_Status": "invalid data"
        },
        {
            "name": "VEHICLE_STATUS_2",
            "Key_Position": "Run",
            # "Ignition_Switch_Status": "Off"
            # "Ignition_Switch_Status": "invalid data"
        },
        {
            'name': 'RvSwitch',
            'Dipswitch': str(0x80),
            'Instance': '4',
            'Output5': '0'
        }
    ]

    return scenario


if __name__ == "__main__":
    import random

    # host = '192.168.8.184'
    host = "localhost"

    hosts = [
        ("localhost", 8000),
        #('192.168.1.12', 8000),
        # ('172.20.36.26', 8000),
    ]

    loop = True

    run_scenario = get_gen_test()
    scenario = "GEN TEST"

    if scenario is None:
        raise ValueError("No Scenario specified")

    while True:
        print("One Full Loop", '-- Enter to run')
        input()

        for host in hosts:
            api = f"http://{host[0]}:{host[1]}/api/can/event/"

            distance += 1000
            # if scenario.upper() == 'RANDOM':

            for msg in run_scenario:
                # if msg.get('Instance') == "4":
                #     temp = random.randint(10, 40)
                #     msg['Ambient_Temp'] = str(temp)
                url = api + msg.get("name").lower()
                try:
                    result = requests.put(url, json=msg)
                    print(result)
                    print(result.json())
                except Exception as err:
                    print(err)

            if toggle_onOff == 1:
                toggle_onOff = 0
            else:
                toggle_onOff = 1
            run_scenario = get_gen_test()

        if loop is True:
            #time.sleep(30)
            pass
        else:
            break
