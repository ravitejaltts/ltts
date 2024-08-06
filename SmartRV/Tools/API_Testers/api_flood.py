import json

import requests

from urllib3.exceptions import ProtocolError
# import urllib3.exceptions.ProtocolError


SCENARIO_A = (
    {
        "DC_Instance": "Main House Battery Bank",
        "Device_Priority": "Battery SOC/BMS device",
        "Source_Temperature": "23.0",
        "State_Of_Charge": "40.0",
        "Time_Remaining": "233",
        "Time_Remaining_Interpretation": "Time to Full",
        "name": "DC_SOURCE_STATUS_2",
        'instance_key': ''
    },
    {
        "Instance": "15",
        "Fluid_Type": "Live Well",
        "Fluid_Level": "25.62",
        "Tank_Capacity": "0.1893",
        "NMEA_Reserved": "255",
        "name": "FLUID_LEVEL",
        'instance_key': '19F21101__0__14',
    },
    {
        "Instance": "14",
        "Fluid_Type": "Live Well",
        "Fluid_Level": "24.0",
        "Tank_Capacity": "1.8927",
        "NMEA_Reserved": "255",
        "name": "FLUID_LEVEL",
        'instance_key': '19F21101__0__14'
    },
    {
        "Instance": "2",
        "Fluid_Type": "Waste Water",
        "Fluid_Level": "50.0",
        "Tank_Capacity": "0.0795",
        "NMEA_Reserved": "255",
        "name": "FLUID_LEVEL",
        'instance_key': ''
    },
    {
        "Instance": "1",
        "Fluid_Type": "Fresh Water",
        "Fluid_Level": "50.0",
        "Tank_Capacity": "0.1136",
        "NMEA_Reserved": "255",
        "name": "FLUID_LEVEL",
        'instance_key': ''
    },
    {
        "Instance": "4",
        "Battery_Voltage": "13.780000000000001",
        "Battery_Current": "160.0",
        "Sequence_ID": "0",
        "name": "Battery_Status"
    },
    {
        "Manufacturer_Code": "BEP Marine",
        "Dipswitch": "4",
        "Instance": "11",
        "Output1": "1",
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
        "Instance": "1",
        "Ambient_Temp": "22.75",
        "name": "Ambient_Temperature"
    },
    {
        "Instance": "55",
        "Ambient_Temp": "22.75",
        "name": "Ambient_Temperature"
    }
)


if __name__ == '__main__':
    import time
    import random

    host = '192.168.8.20'
    port = 8000
    
    api_home = f'http://{host}:{port}/ui/home'
    api_notifications = f'http://{host}:{port}/ui/notifications'
    
    i = 1
    start = time.time()
    while True:
        if i % 100 == 0:
            time_taken = time.time() - start
            print(
                i, 
                round(time_taken, 2), 
                int((time_taken / 1000) * 1000),
                'ms / request (AVG)'
            )
            start = time.time()
        
        try:
            result = requests.get(api_home)
            result = requests.get(api_notifications)
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/1', json={'onOff': 1})
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/2', json={'onOff': 1})
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/9', json={'onOff': 1})
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/10', json={'onOff': 1})
            
            r1 = random.randint(0, 255)
            r2 = random.randint(0, 255)
            
            g1 = random.randint(0, 255)
            g2 = random.randint(0, 255)
            
            b1 = random.randint(0, 255)
            b2 = random.randint(0, 255)
            
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/1', json={'onOff': 1, 'rgb': f'#{r1:02X}{g1:02X}{b1:02X}'})
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/2', json={'onOff': 1, 'rgb': f'#{r2:02X}{g2:02X}{b2:02X}'})
            
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/1', json={'onOff': 0})
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/2', json={'onOff': 0})
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/9', json={'onOff': 0})
            result = requests.put(f'http://{host}:{port}/api/lighting/zone/10', json={'onOff': 0})
            
        except ProtocolError as err:
            print(err)
            c = input('Continue ?')
        i += 1
    