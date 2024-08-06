import time
import json

import base64

import httpx

from main_service.modules.hardware.common import HALBaseClass
from common_libs.models.common import RVEvents

try:
    from libpyzonedetect import zonedetect
except ImportError:
    # We need to mock the result, but do not glance over this
    # NOTE: Might only work on HMI
    from main_service.modules.hardware.mock.mock_timezone import zonedetect


BASE_URL = 'https://192.168.0.1/'
LOGIN_PATH = 'login/'
GPS_PATH = 'api/tree?q=$.config.system.gps.enabled&q=$.status.gps.fix&q=$.status.wan.devices&id=0'
MODEM_PATH = 'api/tree?q=$.config.wan.rules2&q=$.status.wan.devices&q=$.status.wan.primary_device&q=$.config.wan.datacap.enabled&q=$.config.wan.swans.enabled&q=$.status.wan.swans.cm&q=$.status.gpio.SIM_DOOR_DETECT&page=1&start=0&limit=25'
CONNECTION_PATH = 'api/tree?q=$.config.wan.rules2&q=$.status.wan.devices&q=$.status.wan.primary_device&q=$.config.wan.datacap.enabled&q=$.config.wan.swans.enabled&q=$.status.wan.swans.cm&q=$.status.gpio.SIM_DOOR_DETECT&page=1&start=0&limit=25'
WIFI_SETTINGS_PATH = 'api/config/wlan/radio/{radio_id}/bss/{radio_id}'
# DEFAULT_USER = 'admin'
# DEFAULT_PW = 'MM231300002390'   # This is as printed on the router, but it will change as per config we agree upon

DEFAULT_USER = 'winnconnect'
# NOTE: This is just obfuscated but not safe !
# Consider moving to vault if we need to retain access to the credentials
DEFAULT_PW = b'V2MyMTA0NSFXYzIxMDQ1IQ=='
DEFAULT_PW = base64.b64decode(DEFAULT_PW).decode('utf-8')

LOGIN_RETRY_TIMEOUT = 1800        # Second to retry login on failure, default of the Cradlepoint


def convert_to_decimal_location(fix):
    '''Converts a fix obj such as
    {'fix': {'latitude': {'degree': 0.0, 'minute': 0.0, 'second': 0.0}, 'longitude': {'degree': 0.0, 'minute': 0.0, 'second': 0.0}, 'from_sentence': None, 'satellites': 0, 'time': 0, 'lock': False, 'age': 0.0005294169532135129, 'altitude_meters': 0.0, 'ground_speed_knots': None, 'heading': None}
    to the needed decimal location along with the other data
    '''
    latitude_in = fix.get('latitude')
    longitude_in = fix.get('longitude')

    if latitude_in.get('degree') < 0:
        lat_factor = -1
    else:
        lat_factor = 1

    if longitude_in.get('degree') < 0:
        lon_factor = -1
    else:
        lon_factor = 1

    latitude = (
        abs(float(latitude_in.get('degree'))) +
        (float(latitude_in.get('minute')) / 60) +
        (float(latitude_in.get('second')) / (60 * 60))
    )

    longitude = (
        abs(float(longitude_in.get('degree'))) +
        (float(longitude_in.get('minute')) / 60) +
        (float(longitude_in.get('second')) / (60 * 60))
    )

    latitude *= lat_factor
    longitude *= lon_factor

    # Reduce here to 4 decimal points
    fix['position'] = f'{float(latitude):.4f},{float(longitude):.4f}'
    fix['lat'] = float(f'{float(latitude):.4f}')
    fix['lon'] = float(f'{float(longitude):.4f}')

    return fix


def check_gps_change(
        current_pos,
        new_pos,
        lat_diff_threshold=0.0001,
        lon_diff_threshold=0.0001) -> bool:
    '''Checks if the GPS location changed enough to be considered.'''
    if current_pos is None:
        # We know no location yet, take and report
        return True

    lat_diff = abs(current_pos[0] - new_pos[0])
    lon_diff = abs(current_pos[1] - new_pos[1])
    # TODO: Make the check configurable
    return lat_diff >= lat_diff_threshold or lon_diff >= lon_diff_threshold


class Connectivity(HALBaseClass):
    '''Cradlepoint specific for now, needs to be split so it can make a choice'''
    def __init__(self, config={}, components=[], app=None):
        global BASE_URL, LOGIN_RETRY_TIMEOUT
        HALBaseClass.__init__(
            self,
            config=config,
            components=components,
            app=app
        )
        self.configBaseKey = 'connectivity'
        self.init_components(components, self.configBaseKey)

        # Specific attributes
        self.BASE_URL = BASE_URL
        self.user = config.get('username', DEFAULT_USER)
        self.password = config.get('password', DEFAULT_PW)

        self.last_known_gps = None      # Holds the last GPS we use for weather and apply to the vehicle
        self.last_full_gps = {}       # Holds the actual GPS fix for monitoring and for applications that need it always updated
        self.session = None

        self.login_state = {
            'need_login': True,
            'success': None,
            'last_failed': 0.0,
            'last_failed_reason': ''
        }

        self.last_modem_info = {}
        self.LOGIN_TIMEOUT = 3

    async def login(self) -> bool:
        '''Log in and maintain session to cradlepoint.'''
        result = False
        print('Credentials user:', self.user)
        if self.session is None:
            basic = httpx.BasicAuth(
                username=self.user,
                password=self.password
            )
            self.session = httpx.AsyncClient(auth=basic, verify=False)
            # self.session = requests.Session()
            self.session.auth = (self.user, self.password)
        else:
            # We want to exit if we do not need to log in, either through
            # 403 receiveed on API call
            # or on first attempt
            if self.login_state.get('need_login') is False:
                print('[CONNECTIVITY] Login not required right now')
                return result

        if self.login_state.get('last_failed') is not None:
            if time.time() - self.login_state.get('last_failed') < LOGIN_RETRY_TIMEOUT:
                # Skip this time
                print('[CONNECTIVITY] Failed login before, exiting out')
                print('LOGIN State', self.login_state)
                return True

        try:
            url = self.BASE_URL + LOGIN_PATH
            print('[CONNECTIVITY] Log-in url', url)
            response = await self.session.post(
                url, data={
                    'cprouterusername': self.user,
                    'cprouterpassword': self.password,
                },
                timeout=self.LOGIN_TIMEOUT,
            )

            print('LOGIN RESPONSE', response.status_code)
            status_code = response.status_code
        except httpx.ConnectTimeout:
            self.login_state['need_login'] = True
            self.login_state['last_failed'] = None  # Do not set this until we get locked back
            self.login_state['success'] = False
            self.login_state['last_failed_reason'] = 'Connection Timeout'
            result = True
            print('LOGIN State', self.login_state)
            status_code = 408
        except Exception as log_err:
            print('LOGIN ERROR', log_err)
            self.login_state['need_login'] = True
            self.login_state['last_failed'] = time.time()
            self.login_state['success'] = False
            self.login_state['last_failed_reason'] = 'Connection Issue'
            result = True
            print('LOGIN State', self.login_state)
            status_code = 503

        # print("[CONNECTIVITY] Login response", response)
        # print("[CONNECTIVITY] Login response", response.text)
        # print("[CONNECTIVITY] Login response", response.content)
        # print("[CONNECTIVITY] Login response", response.headers)
        if status_code == 403:
            # NOTE: This might not happen on a cradlepoint ?
            # TODO: Test with wrong PW set
            self.login_state['need_login'] = True
            self.login_state['last_failed'] = time.time()
            self.login_state['success'] = False
            self.login_state['last_failed_reason'] = 'Authentication Error'
            print('LOGIN State', self.login_state)
            return True
        elif status_code == 302:
            # Check headers for success or fail redirect
            # Success
            # /admin/?v=7.24.21-99315ef58b-s700-c4d
            # Failure
            # /login/?error=auth&referer=/admin/
            # /login/?error=locked&lockout_time=1800&referer=/admin/
            print("[CONNECTIVITY] Login Headers", response.headers)
            location = response.headers.get('location', '')
            if 'error=auth' in location:
                print('Error logging in with default user creds', location)
                # We failed to log in
                self.login_state['need_login'] = True
                self.login_state['last_failed'] = time.time()
                self.login_state['success'] = False
                self.login_state['last_failed_reason'] = 'Authentication Error'
                raise IOError(self.login_state['last_failed_reason'])
            elif 'error=locked' in location:
                # We are locked out for a period of time
                self.login_state['need_login'] = True
                self.login_state['last_failed'] = time.time()
                self.login_state['success'] = False
                self.login_state['last_failed_reason'] = 'Locked Login Error'
                raise IOError(self.login_state['last_failed_reason'])
            else:
                # Assume success when it starts with /admin/
                if location.startswith('/admin/'):
                    self.login_state['need_login'] = False
                    self.login_state['last_failed'] = None
                    self.login_state['success'] = True
                    self.login_state['last_failed_reason'] = 'NA'
                else:
                    print('Unhandled case of location', location, 'assume failure')
                    self.login_state['need_login'] = True
                    self.login_state['last_failed'] = time.time()
                    self.login_state['success'] = False
                    self.login_state['last_failed_reason'] = f'Unknown Error: {location}'
                    raise IOError(self.login_state['last_failed_reason'])

        if 'Cradlepoint S700' in self.app.system_diagnostics['devices']:
            self.app.system_diagnostics['devices']['Cradlepoint S700'] = {}

        if self.login_state['success'] is False:
            stale = True
        elif self.login_state['success'] is True:
            stale = False

        self.app.system_diagnostics['devices']['Cradlepoint S700'] = {
            'last_seen': time.time(),
            'category': 'connectivity',
            'stale': stale
        }
        print('LOGIN State', self.login_state)
        return result

    async def get_system_details(self):
        '''Fetch all data that can be used by different parsers.'''
        await self.login()
        modem_result = await self.session.get(BASE_URL + MODEM_PATH, timeout=2)
        # print('System result', modem_result)
        if modem_result.status_code == 200:
            return modem_result.json()
        else:
            raise IOError(f'Got error response: {modem_result.status_code}')

    async def get_modem_info(self):
        '''Get modem info from cradlepoint.'''
        data = await self.get_system_details()
        modem_data = {}

        self.last_modem_info = data
        # print(data)
        # print(json.dumps(data, indent=4))
        devices = data.get('data', {}).get('status', {}).get('wan', {}).get('devices')
        if devices is not None:
            # Likely auth issue ?
            for key, value in devices.items():
                # print(key)
                if key.startswith('mdm'):
                    diagnostics = value.get('diagnostics', {})
                    info = value.get('info', {})

                    sim_id = info.get('sim', 'X').replace('sim', '')
                    modem_data[f'ICCID{sim_id}'] = diagnostics.get('ICCID')
                    modem_data[f'IMEI{sim_id}'] = diagnostics.get('DISP_IMEI')
                elif key.startswith('ethernet-wan'):
                    # Get MAC that can be used in netcloud
                    info = value.get('info', {})
                    wan_mac = info.get('mac')
                    modem_data['TCU_ID'] = wan_mac

        return modem_data

    async def get_connection_status(self):
        '''Retrieve per modem connection status.

        "...status": {
            "link_flags": [
                "broadcast",
                "multicast",
                "noarp"
            ],
            "link_state": "down",
            "capped": false,
            "configured": true,
            "connection_state": "disconnected",
            "summary": "available (operation failed)",
            "error_text": "CPPM failed: no carrier",
            "idle": false,
            "plugged": true,
            "sequential_fails": 1,
            "suspended": false,
            "suspend_time": null,
            "uptime": null,
            "manual_activate": "none",
            "factory_defaults_status": "none",
            "reason": "Failover",
            "isActiveSib": false,
            "dep_wandevs": [],
            "active_dep_wandev": null,
            "idle_check": {
                "history": [],
                "average": null,...'''
        # login = await self.login()
        try:
            data = await self.get_system_details()
        except httpx.ConnectError as err:
            print(err)
            return {}
        except httpx.TimeoutException as err:
            print(err)
            return {}
        except IOError as err:
            print(err)
            return {}

        connection_status = {}
        devices = data.get('data', {}).get('status', {}).get('wan', {}).get('devices')
        if devices is not None:
            for key, value in devices.items():
                info = value.get('info', {})
                status = value.get('status', {})
                if key.startswith('mdm'):
                    # This is a modem
                    sim_id = info.get('sim')

                    connection_status[sim_id] = status.get('connection_state')
                    connection_status[f'{sim_id}_signal'] = status.get('signal_strength')
                elif key.startswith('ethernet-wan'):
                    connection_status['eth-wan'] = status.get('connection_state')

        return connection_status


    async def get_wifi_status(self):
        '''Obtain current Wifi connection status from cradlepoint.'''
        return {
            'msg': 'NotImplemented'
        }

    async def update_wifi(self, wifi_id, settings):
        '''{"ssid":"DOMCONNECT-REG2","basic_rates":{}}'''
        await self.login()
        path = BASE_URL + WIFI_SETTINGS_PATH.format(radio_id=wifi_id)
        print('PATH', path)
        update_wifi_result = await self.session.put(
            path,
            data=settings
        )
        print(update_wifi_result.request)
        print(update_wifi_result.request.headers)
        print(update_wifi_result.status_code)
        print(update_wifi_result.text)
        return update_wifi_result

    async def get_sys_overview(self):
        '''What is the system overview if any on a cradlepoint ?
        Carry over from Wineguard.'''
        raise NotImplementedError('get_sys_overview needs rework for Cradlepoint')

    # TODO: use decorator to check if we are loggedin, log in if not and handle failure
    async def get_sys_gps(self, settings):
        '''Get GPS data from cradlepoint.'''
        # TODO: Ensure that we properly configure timers for when to request a new items
        # Goal is to have IoT never wait for data
        await self.login()

        print('[check_gps_task] STARTED get_sys_gps', BASE_URL + GPS_PATH)

        gps_response = await self.session.get(BASE_URL + GPS_PATH, timeout=5)
        print('[check_gps_task] GPS Response', gps_response)
        try:
            response_data = gps_response.json()
        except Exception as err:
            print('[get_sys_gps] ERROR', err)
            return None

        success = response_data.get('success')
        if success is False:
            print('[GPS][check_gps_task] Not a success', response_data)
            print('[GPS] Error Response', response_data)
            raise IOError('Not authenticated')

        # print('[GPS][check_gps_task] Response data', response_data)

        # Check if gps is configured
        gps_enabled = response_data.get(
                'data', {}
            ).get(
                'config', {}
            ).get(
                'system', {}
            ).get(
                'gps', {}
            ).get(
                'enabled'
            )

        gps_opt_in = self.HAL.vehicle.handler.vehicle[2].state.usrOptIn
        print('[GPS][CONNECTIVITY][check_gps_task] GPS Enabled', gps_enabled, " User OptIn", gps_opt_in)
        if gps_enabled is not True or gps_opt_in is False:
            print(
                '[GPS][check_gps_task] GPS not enabled or opted out, returning',
                gps_enabled,
                gps_opt_in
            )
            return None

        gps_data = response_data.get(
            'data', {}).get('status', {}).get('gps', {})

        print('[GPS][check_gps_task] GPS Data', gps_data)

        gps_fix = gps_data.get('fix', {})

        gps_fix = convert_to_decimal_location(gps_fix)
        print('[GPS][check_gps_task] GPS FIX', gps_fix)

        # Check if location is valid
        if gps_fix.get('lock', False) is False:
            print('[GPS][check_gps_task] GPS LOCK is FALSE, returning NONE')
            return None
        # else:
        #     gps_fix['lock'] = True

        print('[check_gps_task] Before check gps change')

        if gps_fix['lock'] is False:
            # What to do?
            pass

        if check_gps_change(self.last_known_gps, (gps_fix['lat'], gps_fix['lon'])):
            # Only update is .0001 moved

            self.last_known_gps = (gps_fix['lat'], gps_fix['lon'])

            self.event_logger.add_event(
                RVEvents.LOCATION_GEO_LOC_CHANGE,
                1,
                gps_fix['position']
            )
            # Check related component for a vehicle
            # Use set_state for the vehicle gps location state property
            # self.HAL.app.config['last_position'] = gps_data['position']

            print('[check_gps_task] in check change')

        # We keep track of the last fix
        self.last_full_gps = gps_fix
        print('[check_gps_task] After', self.last_known_gps)

        return gps_fix

    async def get_timezone(self, location: tuple=None):
        '''Return the Timezone string for frontend use.'''
        if location is None:
            # Get the current location
            location = (35.0715, -82.5216)

        # TODO: Do it based on the real location
        # TODO: Add unit tests
        z = zonedetect()

        return z.lookup_zone(*location)

    async def get_tz_offset(self):
        '''Return the numerical value for the TZ offset for telemetry.

        '''
        raise NotImplementedError('TBD')

    async def get_cellular_status(self):
        '''Get connection status for settings display.'''
        await self.login()
        try:
            result = await self.session.get(BASE_URL + CONNECTION_PATH, timeout=5)
        except httpx.ConnectError as err:
            print('ERROR', err)
        return result.json()


async def run_test(conn_handler):
    conn_handler.setEventLogger(fake_logger)
    login = await conn_handler.login()
    return login


module_init = (
    Connectivity,
    'connectivity_defaults',
    'components'
)


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()

    def fake_logger(event):
        print(event)

    class FakeAttribute:
        def __init__(self, key, value):
            setattr(self, key, value)

    class FakeApp:
        def __init__(self):
            self.system_diagnostics = {
                'devices': {}
            }
            self.hal = FakeAttribute(
                'vehicle',
                FakeAttribute('handler',
                              FakeAttribute('vehicle', {2: {}}))
            )

    handler = Connectivity()
    # handler.BASE_URL = "http://1.2.3.4/"
    handler.app = FakeApp()
    # result = loop.run_until_complete(run_test(handler))
    # print(result)
    # assert result is False
    # result = loop.run_until_complete(handler.get_sys_gps({'usrOptIn': True}))
    # print(result)
    # result = loop.run_until_complete(handler.get_modem_info())
    # print(result)
    result = loop.run_until_complete(handler.get_connection_status())
    print(result)

    # wrong_handler = Connectivity()
    # # Wrong PW
    # wrong_handler.user = 'domwronguser'
    # wrong_handler.app = FakeApp()

    # for i in range(2):
    #     try:
    #         result = loop.run_until_complete(run_test(wrong_handler))
    #         print('Login Result', result)
    #     except Exception as err:
    #         print(err)

    # # Log in with correct PW
    # result = loop.run_until_complete(run_test(handler))

    # settings = {
    #     "ssid": "DOMCONNECT-REG6", "basic_rates": {}
    # }
    # result = loop.run_until_complete(handler.update_wifi(0, settings))
    # print(result)



    # gps_status = handler.session.get(BASE_URL + GPS_PATH, timeout=5)
    # print(
    #     json.dump(
    #         gps_status.json(),
    #         open('gps_status.json', 'w'),
    #         indent=4
    #     )
    # )

    # print(handler.get_sys_gps())

    # ROBO 42.50785886512475, -83.51899471615106

    # fake_data = {
    #     "latitude": {
    #         "degree": 42.0,
    #         "minute": 30.0,
    #         "second": 28.26884
    #     },
    #     "longitude": {
    #         "degree": -83.0,
    #         "minute": 31.0,
    #         "second": 8.38098
    #     },
    #     "from_sentence": None,
    #     "satellites": 0,
    #     "time": 0,
    #     "lock": False,
    #     "age": 0.00048629200318828225,
    #     "altitude_meters": 0.0,
    #     "ground_speed_knots": None,
    #     "heading": None
    # }
    # print(convert_to_decimal_location(fake_data))
