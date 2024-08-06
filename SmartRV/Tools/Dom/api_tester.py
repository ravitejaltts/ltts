import requests


GET = 'GET'
PUT = 'PUT'


def assert_response(response, status_code=200, strict=False):
    if response.status_code != status_code:
        print(f'Error Expected {status_code} but got {response.status_code}')
        if strict is True:
            raise AssertionError(f'Response code not as expected')


    return response.status_code, response.json()


def make_request(url, r_type='GET', body=None, headers={}, expected_status=200, strict=True):
    global BASE_URL
    if r_type == 'GET':
        response = requests.get(BASE_URL + url, headers=headers)
    elif r_type == 'PUT':
        response = requests.put(BASE_URL + url, json=body, headers=headers)
    else:
        raise ValueError(f'Request type: {r_type} not supported')

    result = assert_response(response, status_code=expected_status, strict=strict)
    print(url, result[0])
    return result[1]


HOST = 'localhost'
PORT = 8000
BASE_URL = f'http://{HOST}:{PORT}'

# UI
## Home
home = make_request('/ui/home', r_type=GET)

### Quick Actions
for q_action in home.get('quickactions', []):
    q_action_api = q_action.get('action_default', {}).get('action', {})
    print(q_action_api)
    q_result = make_request(q_action_api.get('href'), r_type=q_action_api.get('type'), body={'onOff': 1})
    q_result = make_request(q_action_api.get('href'), r_type=q_action_api.get('type'), body={'onOff': 0})

########################################################
## Climate
climate = make_request('/ui/climate', r_type=GET)



########################################################
## Lighting
lighting = make_request('/ui/lighting', r_type=GET)


########################################################
## Refrigerator
# TODO: Fix ending /, should not be used
refrigerator = make_request('/ui/refrigerator/', r_type=GET)


########################################################
## Inverter
inverter = make_request('/ui/inverter/', r_type=GET)


########################################################
## Watersystems
watersystems = make_request('/ui/watersystems/', r_type=GET)



########################################################
## Energy
energy = make_request('/ui/ems/')
