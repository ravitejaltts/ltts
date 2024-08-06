import time
import requests
import sys
import logging

try:
    SET_TEMP = int(sys.argv[1])
except IndexError:
    SET_TEMP = 72
except ValueError:
    SET_TEMP = 72


try:
    MODE = int(sys.argv[2])
except IndexError:
    MODE = 0
except ValueError:
    MODE = 0

OFFSET = 2

BASE_API = 'http://localhost:8000/'
TEMP_READ = BASE_API + 'ui/'
CLIMATE = BASE_API + 'api/climate/ac/1'
HEATER = BASE_API + 'api/electrical/dc/19'

RETRY_MAX = 5
retry_counter = 0

FORMAT = '%(asctime)s %(message)s'

logging.basicConfig(
    filename='heattest.log',
    level=logging.DEBUG,
    format=FORMAT
)

# logging = logging.getlogging('ui')

def ac_on():
    logging.debug('Turning AC On')
    # Turn heater off
    heater_off()
    # Turn compressor on / fan hi
    settings = {'fanSpd': 52, 'compressor': 1}
    try:
        requests.put(CLIMATE, json=settings)
    except requests.exceptions.ConnectionError as err:
        return


def ac_off():
    logging.debug('Turning AC Off')
    # Turn compressor off
    # turn fan to off
    settings = {'fanSpd': 0, 'compressor': 0}
    try:
        requests.put(CLIMATE, json=settings)
    except requests.exceptions.ConnectionError as err:
        return

def heater_on():
    logging.debug('Heater On')
    # Turn AC off
    ac_off()
    # Turn heater on
    settings = {'onOff': 1}
    try:
        requests.put(HEATER, json=settings)
    except requests.exceptions.ConnectionError as err:
        return

def heater_off():
    logging.debug('Heater Off')
    # Turn heater off
    settings = {'onOff': 0}
    try:
        requests.put(HEATER, json=settings)
    except requests.exceptions.ConnectionError as err:
        return


def safety_shutoff():
    logging.error('Shutting off AC and Heater as not temp reading was possible')
    heater_off()
    ac_off()


while True:
    logging.debug(f'Retry counter: {retry_counter}')
    # Get temp
    try:
        current_temp_response = requests.get(TEMP_READ).json()
    except requests.exceptions.ConnectionError as err:
        logging.error('Could not connect to service for temp reading, retry in 5 seconds')
        if retry_counter >= RETRY_MAX:
            safety_shutoff()
            retry_counter = 0
        else:
            retry_counter += 1

        time.sleep(5)
        continue

    # print(current_temp_response)

    current_temp = current_temp_response.get('climateControl', {}).get('internalTemp')
    logging.debug(f'Current temperature: {current_temp}')


    if current_temp == '--':
        logging.error('No temperature received')
        # TODO: Check what to do in this case ?
        # Maybe time based shutdown of heater and cooling
        if retry_counter >= RETRY_MAX:
            safety_shutoff()
            retry_counter = 0
        else:
            retry_counter += 1
        time.sleep(5)
        continue
    elif current_temp is None:
        print('No temp could be read, waiting')
        # TODO: Check when this would be the case ?
        logging.error('Temperature is None')
        if retry_counter >= RETRY_MAX:
            safety_shutoff()
            retry_counter = 0
        else:
            retry_counter += 1
        time.sleep(5)
        continue

    current_temp = int(current_temp)

    if current_temp > (SET_TEMP + OFFSET) and MODE in (0, 2):
        # If yes then turn on AC
        ac_on()
    elif current_temp <= (SET_TEMP) and MODE in (0, 2):
        ac_off()

    if current_temp < (SET_TEMP - OFFSET) and MODE in (0, 1):
        heater_on()
    elif current_temp >= (SET_TEMP) and MODE in (0, 1):
        heater_off()

    retry_counter = 0

    time.sleep(5)
