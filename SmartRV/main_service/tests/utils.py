from time import sleep
import logging

logger = logging.getLogger(__name__)


def find_alert(response, alert_code):
    '''Iterate over notification response and find ecode.'''
    found_alert = False
    for item in response.json():
        print('ECODE  [find_alert]', item.get('ecode'))
        if item.get('ecode') == alert_code:
            found_alert = True
            break

    return found_alert


def check_ui_notifications(client, ecode):
    '''Get notificatiuons and check that a specific ecode is present.'''
    response = client.get('/ui/notifications')
    # assert response.json() == []
    print('NOTIFICATIONS.. [check_ui_notifications]', response.json())
    assert response.status_code == 200
    return find_alert(response, ecode)


def send_a_can_event(client, data, msg_name=None):
    '''Send fake data to the endpoint receiving CAN data.'''
    if msg_name is not None:
        system_name = msg_name.lower()
    else:
        system_name = data.get(
            'name',
            data.get('msg_name')
        )

    if system_name is None:
        raise ValueError('System Name is None')

    try:
        response = client.put(
            f'/api/can/event/{system_name.lower()}',
            json=data,
            timeout=2
        )
    except Exception as err:
        print(f" send can err {err}")
        response = None

    return response


def lighting_zone_helper(client, zone_id: int):
    """Duplicate code to run for each floorplan"""
    response = client.put(
        f"api/lighting/lz/{zone_id}/state", json={"onOff": 1}
    )
    assert response.status_code == 200

    print(f"Put Response {response.json()}")

    assert response.json().get("onOff") == 1

    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get(f"lz{zone_id}").get("onOff") == 1

    response = client.put(f"api/lighting/lz/{zone_id}/state", json={"onOff": 0})
    assert response.status_code == 200
    print(f"Put Response {response.json()}")

    assert response.json().get("onOff") == 0

    response = client.get("/api/lighting/state")
    assert response.status_code == 200
    print(f"Full State Response {response.json()}")

    assert response.json().get(f"lz{zone_id}").get("onOff") == 0


def preset_helper(client):
    preset_ids = [1, 2, 3]
    preset_save = {}
    for preset_id in preset_ids:
        zone_id = preset_id + 6 # just for testing
        response = client.put(
            f"api/lighting/lz/{zone_id}/state",
            json={
                "onOff": 1
            }
        )
        assert response.status_code == 200

        response = client.put(
            f"api/lighting/lg/{preset_id}/state",
            json={
                "save": 1
            }
        )
        assert response.status_code == 200

        logger.debug(f"Response {response.json()}")

        response = client.get("/api/lighting/state")
        assert response.status_code == 200
        preset_save[preset_id] = response.json()


    for preset_id in preset_ids:
        response = client.put(
            f"api/lighting/lg/{preset_id}/state",
            json={
                "onOff": 1
            }
        )
        assert response.status_code == 200

        response = client.get("/api/lighting/state")
        assert response.status_code == 200

        print(f"Both Response \n {response.json()} \n\n {preset_save[preset_id]}")

        for i in range(1, 17):
            zid = f"lz{i}"
            print(response.json())
            print('Response ZID', response.json().get(zid))
            print('Saved ZID', preset_save[preset_id].get(zid))

            assert response.json().get(zid) == preset_save[preset_id].get(zid)


if __name__ == '__main__':
    import requests
    import time

    from statistics import mean

    URLS = (
        'http://localhost:8000/api/lighting/lz/2/state',
        'http://localhost:8000/api/lighting/lg/1/state',
        'http://localhost:8000/api/watersystems/wp/1/state',
    )

    for url in URLS:
        exec_times = []
        for i in range(100):
            START = time.time()
            response = requests.get(url, timeout=5)
            END = time.time() - START
            # print('Time taken', END * 1000, 'ms', url)
            exec_times.append(END)

        average = mean(exec_times) * 1000

        print(url, 'AVERAGE', average)

    URL = 'http://localhost:8000/api/lighting/lz/2/state'
    # Get average time over 100 requests

    i = 0
    print('STRESS/LOAD Test', URL)
    while True:
        START = time.time()
        response = requests.get(URL, timeout=10)
        END = time.time() - START
        ms = END * 1000
        if ms > 50:
            print('\n', i, 'Above 50 ms:', int(ms), 'ms', URL)
            print('\t', response.json())
        else:
            print('.', end='', flush=True)
        i += 1
        time.sleep(0.25)
