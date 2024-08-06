import json
import sys
import time

import requests

import random


def get_random():
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
        # Interior
        {
            "Instance": "4",
            "Ambient_Temp": str(float(random.randint(8,34))),
            # "Ambient_Temp": "-45.0000",

            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "Ambient_Temperature"
        },
        
    ]
    
    return scenario


SCENARIOS = {
    'DEFAULT': [
        {
            "Instance": "2",
            "Fluid_Type": "Waste Water",
            "Fluid_Level": "99.9",
            "Tank_Capacity": "0.0795",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        {
            "Instance": "1",
            "Fluid_Type": "Fresh Water",
            "Fluid_Level": "1.0",
            "Tank_Capacity": "0.1136",
            "NMEA_Reserved": "255",
            "name": "FLUID_LEVEL",
            'instance_key': ''
        },
        # Fridge
        {
            "Instance": "55",
            "Ambient_Temp": "4.0",
            "name": "Ambient_Temperature"
        },
        # Interior
        {
            "Instance": "4",
            "Ambient_Temp": "33.7",
            # "Ambient_Temp": "-45.0000",

            # 0 Fahrenheit - Error case for Thermistor
            # "Ambient_Temp": "-17.78125",
            "name": "Ambient_Temperature"
        },
    ]
}


if __name__ == '__main__':
    import random
    #host = '192.168.8.184'
    host = 'localhost'
    
    hosts = [
        ('localhost', 8000),
        # ('192.168.8.185', 8000),
        ('172.20.36.25', 8000),
    ]
    
    loop = True
    
    try:
        scenario = sys.argv[1]
        run_scenario = get_random()
    except IndexError as err:
        print('error, using default')
        scenario = 'DEFAULT'
        run_scenario = SCENARIOS.get(scenario)
        
    
    if scenario is None:
        raise ValueError('No Scenario specified')
    
    
    while True:
        for host in hosts:
            api = f'http://{host[0]}:{host[1]}/api/can/event/'
            
            #if scenario.upper() == 'RANDOM':
                
            for msg in run_scenario:
                # if msg.get('Instance') == "4":
                #     temp = random.randint(10, 40)
                #     msg['Ambient_Temp'] = str(temp)
                url = api + msg.get('name').lower()
                result = requests.put(url, json=msg)
                print(result)
                print(result.json())

            run_scenario = get_random()
        if loop is True:            
            time.sleep(5)
        else:
            break
