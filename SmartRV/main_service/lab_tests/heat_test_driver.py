import requests

BASE_URL = 'http://172.20.36.26:8000'
TEMP_UPDATE = f'{BASE_URL}/api/can/event/ambient_temperature'

TEMP_TEMPLATE = {
    'Instance': '1',
    'Ambient_Temp': '27.9375',
    "name": "thermostat_ambient_status"
}

instance = input('Test which instance (1/55): ')
TEMP_TEMPLATE['Instance'] = instance

print('Testing against instance: ', TEMP_TEMPLATE['Instance'])

current_temp = 22.0

while True:
    temp = input('Enter temp: ')
    if temp == '':
        continue
    if temp == '--':
        temp_set = '--'
    else:
        temp_set = float(temp)

    print('Setting temp to ', temp_set)
    temp_obj = TEMP_TEMPLATE
    temp_obj['Ambient_Temp'] = str(temp_set)
    requests.put(TEMP_UPDATE, json=temp_obj)
