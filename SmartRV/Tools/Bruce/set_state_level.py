import json
import sys
import time

import requests

import random

gen_onOff = 1
overload_onOff = 0
global load
load = 3.0
global cur_temp
cur_temp = 28
reg_temp = 27
high_temp = 36
low_temp = 9


def perform_action(action):
    global load
    global cur_temp
    global gen_onOff

    # Example action handler
    if action == "overload":
        print("overload activated.")
        overload_onOff = 1
        load = 20.1
    elif action == "lowload":
        print("lowload activated.")
        load = 5.0
    elif action == "verylow":
        print("verylow activated.")
        load = 1.0
    elif action == "midload":
        print("midload activated.")
        load = 12.2
    elif action == "lowtemp":
        print("lowtemp activated.")
        cur_temp = low_temp
    elif action == "regtemp":
        print("regtemp activated.")
        cur_temp = reg_temp
    elif action == "hightemp":
        print("hightemp activated.")
        cur_temp = high_temp
    elif action == "genoff":
        print("generator stopped.")
        gen_onOff = 0
    elif action == "genon":
        print("generator activated.")
        gen_onOff = 1
    elif action == "e":
        exit(0)
    else:
        print("No action selected.")

def wait_for_input():
    last_action = None
    try:
        user_input = input("Enter your command (overload, lowload, midload, verylow, lowtemp, hightemp, regtemp, genoff, genon or press Enter to repeat last action): ")

        if user_input.strip().lower() == "\r" or user_input == "":
            if last_action:
                print(f"Repeating {last_action}.")
                perform_action(last_action)
            else:
                print("No action.")
        else:
            perform_action(user_input.lower())
            last_action = user_input.lower()

    except KeyboardInterrupt:
        print("\nExiting.")





def get_scenario():
    global load
    global cur_temp
    global gen_onOff

    scenario = [

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
            "Fluid_Level": str(random.randint(0,100)),
            "Tank_Capacity": "0.1136",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        # Fridge
        {
            "Instance": "55",
            "Ambient_Temp": str(float(random.randint(1,4))),
            "name": "Ambient_Temperature"
        },
        # # Interior
        # {
        #     "Instance": "4",
        #     "Ambient_Temp": str(float(random.randint(8,34))),
        #     # "Ambient_Temp": "-45.0000",

        #     # 0 Fahrenheit - Error case for Thermistor
        #     # "Ambient_Temp": "-17.78125",
        #     "name": "Ambient_Temperature"
        # },# Indoor
        {
            "Instance": "2",
            "Ambient_Temp": str(cur_temp),
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        },
        {
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": "128",
            "Instance": "4",
            "Output7": "1",  # Park brake applied
            "name": "RvSwitch",

        },
        {
            "title": "Set Pin C5.13 to 1 (Output7)",
            "name": "rvswitch",
            "Manufacturer_Code": "BEP Marine",
            "Dipswitch": str(0x80),
            "Instance": str(0x4),
            "Output1": "0", "Output2": "0", "Output3": "0", "Output4": "0", "Output5": "1", "Output6": "0",  # 5 is ignition on
            "Output8": "0", "Output9": "0", "Output10": "0", "Output11": "0", "Output12": "0", "Output13": str(gen_onOff), "Output14": "1", "Output15": "1", "Output16": "0", "Output17": "0", "Output18": "0", "Output19": "0", "Output20": "0", "Output21": "0", "Output22": "0", "Output23": "0", "Output24": "0", "Output25": "0", "Output26": "0", "Output27": "0", "Output28": "0", "Output29": "0", "Output30": "0", "Output31": "0", "Output32": "0"
        },
        {
            'title': 'Set Solar -  Watts',
            'Instance': '1',
            'Charge_Voltage': '12.3',
            'Charge_Current': '1.32',
            'name': 'solar_controller_status'
        },
        #CZONE_MAIN_STUD_MEDIUM_LOAD =
        {
            "Instance": "252",
            "Battery_Voltage": "13.0",
            "Battery_Current": "20",
            "Sequence_Id": "0",
            "msg_name": "Battery_Status",
            "name": "Battery_Status",
            "source_address": "97",
            "instance_key": "19F21497__0__252"
        },
        # {
        #     "Instance": "1",
        #     "RMS_voltage": "118.65",
        #     "RMS_current": str(random.randint(0, 16)),
        #     "Frequency": "60.3046875",
        #     "name": "CHARGER_AC_STATUS_1",
        #     "instance_key": "19FFCAE1__0__1",
        # },  # ENERGY_INVERTER_OVERLOAD =
        # Outdoors
        {
            "Instance": str(0xF9),
            "Ambient_Temp": str(cur_temp),
            # "Ambient_Temp": "-45.0000",
            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "thermostat_ambient_status",
        },
        {
            "Instance": "1",
            "RMS_Voltage": "120.0",
            "RMS_Current": str(float(load)),
            "Frequency": "60",
            "name": "inverter_ac_status_1"
        },
        {
            "Instance": "1",
            "RMS_Voltage": "120.0",
            "RMS_Current": str(float(load)),
            "Frequency": "60",
            "name": "charger_ac_status_1"
        },
        {
            "DC_Instance": "1",
            "Device_Priority": "Battery SOC/BMS device",
            "State_Of_Health": str(random.randint(90, 95)),
            # "State_Of_Health": "95",
            "Capacity_Remaining": str(random.randint(75, 80)),
            "name": "DC_SOURCE_STATUS_3",
            "instance_key": "",
        },
        {
            "DC_Instance": "Main House Battery Bank",
            "Device_Priority": "Battery SOC/BMS device",
            "Source_Temperature": "23.0",
            # "State_Of_Charge": "10.1",
            "State_Of_Charge": str(random.randint(88, 94)),
            "Time_Remaining": "604",
            # "Time_Remaining_Interpretation": "Time to Full",
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
            "title": 'Fuel Tank - LP - x %',
            "Instance": 4,
            "Fluid_Type": "PROPANE",
            "Fluid_Level": str(64),
            # "Tank_Capacity": "0.1136",
            # "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            # "title": "Set Water Heater State Set_Point_temp to 40 C",
            "name": "waterheater_status",
            "Instance": "1",
            "Operating_Mode": "combustion",
            "Set_Point_Temperature": "40.0"
        },
    ]

    return scenario


if __name__ == '__main__':
    import random

    hosts = [
        ('localhost', 8000),
        # ('192.168.8.185', 8000),
        ('192.168.2.13', 8000),
    ]

    run_scenario = get_scenario()


    while True:
        print("One Full Loop", '-- Enter to run')
        # Run the function
        wait_for_input()
        run_scenario = get_scenario()

        for host in hosts:
            api = f"http://{host[0]}:{host[1]}/api/can/event/"

            for msg in run_scenario:
                # if msg.get('Instance') == "4":
                #     temp = random.randint(10, 40)
                #     msg['Ambient_Temp'] = str(temp)
                url = api + msg.get("name").lower()
                try:
                    print(msg.get("name"))
                    result = requests.put(url, json=msg, timeout=0.3)
                    print(result)
                    print(result.json())
                except Exception as err:
                    print(err)

