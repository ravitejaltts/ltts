import time
from datetime import datetime, timezone

import requests


API_URL = 'http://192.168.0.83:8000/api/lighting/lz/1/state'

PROC_START = time.time()

while True:
    start = time.time()
    try:
        response = requests.get(API_URL, timeout=0.5)
        print(f'{datetime.now(timezone.utc)} [TIME] {time.time() - start}')
    except Exception as err:
        print(err)
        print('Time from start', time.time() - PROC_START)

    time.sleep(0.2)
