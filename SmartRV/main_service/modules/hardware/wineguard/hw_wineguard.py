import json

import requests
from requests.exceptions import ReadTimeout
# from bs4 import BeautifulSoup
# from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime
import time


try:
    from main_service.modules.hardware.common import HALBaseClass
except ImportError:
    import sys
    sys.path.insert(0,'/Users/dom/Documents/1_Projects/1_Winnebago/2_Dev/SmartRV/main_service/')
    from main_service.modules.hardware.common import HALBaseClass

from  common_libs.models.common import RVEvents, EventValues


BASE_URL = 'http://10.11.12.1'
# BASE_URL = 'http://localhost:8081'
LOGIN_URL = 'http://{host}/cgi-bin/luci/themes/winegard2/index.htm'
GPS_PAGE = 'http://{host}/cgi-bin/luci/themes/winegard2/gps.htm?refresh=REFRESH'
# GPS_PAGE = 'http://{host}/cgi-bin/luci/{stok}/themes/winegard2/gps.htm'

DEFAULT_USER = 'admin'
DEFAULT_PW = 'WinnConnect2022'


def extract_token(content):
    if not ';stok=' in content:
        raise IndexError('Cannot find token, login potentially incorrect')

    start = content.find(';stok=')
    print(start)
    end = content[start:].find('/')
    print(end)

    token = content[start:start+end]

    print('Token', token)
    return token


class WineGuard(HALBaseClass):
    def __init__(self, config={}, components=[], credentials={}, app=None):
        self.user = config.get('username', 'admin')
        self.password = config.get('password', 'WinnConnect2022')
        self.host = config.get('host', '10.11.12.1')
        # self.host = 'localhost:8080'
        self.token = None
        self.session = None
        self.last_known_gps = {
            'iotposition': ''
        }
        self.need_login = True  # False when login is successful
        # self.tf = TimezoneFinder()  # reuse
        self.tf = None
        self.tz = ""
        self.tzOffset = "-6.0"  # default matches FC position above
        self.CACHE_TIMEOUT = 15     # Seconds
        self.sys_status = {}
        self.sys_status_timestamp = 0.0
        self.COMP_INSTANCES = []

    def login(self) -> bool:
        result = False
        try:
            self.session = requests.Session()
            url = LOGIN_URL.format(host=self.host)
            print('Log-in url', url)
            response = self.session.post(
                url, data={
                    'luci_username': self.user,
                    'luci_password': self.password,
                    'luci_continue': 'CONTINUE'
                },
                timeout=10
            )
            print("Login response", response)
            if response.status_code == 403:
                if self.user != DEFAULT_USER or self.password != DEFAULT_PW:
                    # Try alternate default PW
                    self.user = DEFAULT_USER
                    self.password = DEFAULT_PW

                    return self.login()
                else:
                    # Fail and report that Wineguard unit cannot be accessed
                    self.need_login = True
                    return response.status_code

            else:
                # self.token = extract_token(response.content.decode('utf8'))
                self.need_login = False
        except requests.exceptions.ConnectTimeout as err:
            raise
        except Exception as err:
            print(err)
            result = True

        return result

    def get_wifi_ap(self):
        '''Read list of Wifi Hotspots in the area.'''
        # TODO:
        # Get current sys status
        # Start Scan
        # Check for changes in sys_status
        # Once done show networks

        pass

    def get_tz_offset(self):
        '''Return the last computed tz offset'''
        result = self.tzOffset
        return result

    def get_sys_overview(self, force=False):
        # http://10.11.12.1/cgi-bin/luci/sys_status?_=0.9113330564250821
        '''{"product":"GW-1000","models":[],"capabilities":"AP,DHCP,DNS,NAT,STA,4G","gateways":"192.168.4.1","country":"US","netmasks":"255.255.252.0","policy":"wan_only","wifi_status":"Connected to WiFi "NaudoNet2.0"","dnsaddrs":"192.168.12.1","showgps":"1","modelid":"connectgw2x2","model":"Winegard Gateway GW-1000","internet_status":"Connected to WiFi "NaudoNet2.0"","connect_status":"Connected","gps":{"view":[{"const":"GPS","elev":"80","prn":"02","azim":"340","snr":"25"},{"const":"GPS","elev":"56","prn":"05","azim":"077","snr":"28"},{"const":"GPS","elev":"","prn":"1","azim":"","snr":""},{"const":"GPS","elev":"","prn":"1","azim":"","snr":""},{"const":"GPS","elev":"","prn":"1","azim":"","snr":""},{"const":"GPS","elev":"","prn":"1","azim":"","snr":""},{"const":"GPS","elev":"08","prn":"11","azim":"066","snr":"16"},{"const":"GPS","elev":"04","prn":"12","azim":"167","snr":""},{"const":"GPS","elev":"06","prn":"13","azim":"108","snr":""},{"const":"GPS","elev":"09","prn":"15","azim":"139","snr":""},{"const":"GPS","elev":"02","prn":"16","azim":"326","snr":""},{"const":"GPS","elev":"42","prn":"18","azim":"257","snr":"29"},{"const":"GPS","elev":"30","prn":"20","azim":"050","snr":"26"},{"const":"GPS","elev":"09","prn":"23","azim":"201","snr":""},{"const":"GPS","elev":"25","prn":"25","azim":"187","snr":"21"},{"const":"GPS","elev":"29","prn":"26","azim":"302","snr":"22"},{"const":"GPS","elev":"81","prn":"29","azim":"081","snr":"38"},{"const":"GPS","elev":"02","prn":"31","azim":"260","snr":""}],"date":"2023/02/20","altitude":"131.0","wifi_only":true,"time":"03:54:12.0","fanSpd":"0.0","latitude":"47.57125","heading":"0.00","ttf":"34","gpsrate":300,"hdop":"1.0","fix":"3D","longitude":"-122.14265","heartbeat":true,"tracking":true,"satellites":"08"},"internet_gateway":"192.168.4.1","wifi_state":"connected","board":{"bootloader":"WGEX-BOOT-20220225 (Feb 25 2022 - 04:48:37)","machine":"mips","kernel":"4.14.162+","sw_distribution":"OpenWrt","hostname":"ConnectLOCO","rescue_image":"LEDE-AZTECH-20220408 good","sw_description":"OpenWrt 19.07 20220408","firmware":"LEDE-AZTECH-20220408","nodename":"ConnectLOCO","sysname":"Linux","needupdate":"yes","board":"WGEX-AZTECH","sw_version":"19.07","buildtime":"Fri Apr  8 23:19:37 2022","sw_target":"ramips/mt7621","system":"MediaTek MT7621 ver:1 eco:3","sw_revision":"20220408","config":"wgex-loco","version":"LEDE-20220408 #0 SMP Fri Apr 8 18:14:06 CDT 2022","board_name":"WGEX-AZTECH","release":"4.14.162+","macaddr":"00:17:1A:C4:33:B3","buildid":"1649459977","serial_no":"WGC00171AC433B3"},"networks":{"guest":{"rx_bytes":0,"ifname":"br-guest","tx_bytes":0,"netmask":"255.255.255.0","expires":-1,"ifdev":"br-guest","dnsaddrs":[],"rx_packets":0,"config_mask":"255.255.255.0","type":"bridge","proto":"static","config_ip":"10.11.13.1","uptime":14045,"ipaddr":"10.11.13.1","tx_packets":0,"macaddr":"92:06:38:10:A1:C9","is_up":true,"name":"guest"},"wwan":{"band":"NA","network":"down","cell":"unregistered","signal":0},"lan":{"rx_bytes":550272,"ifname":"br-lan","tx_bytes":2007884,"netmask":"255.255.255.0","expires":-1,"ifdev":"br-lan","dnsaddrs":[],"rx_packets":6422,"config_mask":"255.255.255.0","type":"bridge","proto":"static","config_ip":"10.11.12.1","uptime":14045,"ipaddr":"10.11.12.1","tx_packets":5195,"macaddr":"2E:E9:D7:AB:35:D3","is_up":true,"name":"lan"},"ewan":[],"wlwan":{"rx_bytes":81255,"ifname":"wlan0","ipaddr":"192.168.4.67","netmask":"255.255.252.0","expires":14320,"ifdev":"Client "NaudoNet2.0"","dnsaddrs":["192.168.12.1"],"rx_packets":355,"proto":"dhcp","tx_packets":167,"tx_bytes":24766,"uptime":80,"type":"wifi","gateway":"192.168.4.1","macaddr":"00:17:1A:C4:33:B5","is_up":true,"name":"wlwan_4"},"oem":{"rx_bytes":0,"ifname":"br-oem","tx_bytes":16030,"netmask":"255.255.255.0","expires":-1,"ifdev":"br-oem","dnsaddrs":[],"rx_packets":0,"config_mask":"255.255.255.0","type":"bridge","proto":"static","config_ip":"172.23.24.1","uptime":14044,"ipaddr":"172.23.24.1","tx_packets":99,"macaddr":"46:8E:27:2E:C3:D5","is_up":true,"name":"oem"}},"api_version":"API 1.4","subscription":{"plan_left":"1","inactivated":true,"unsubscribed":true,"rate_plan":"Winegard - 1MB US 30D Plan","plan_total":"1","plan_used":"0","percent_available":"100"},"showsensors":false,"modem_state":"none","ether_state":"none","sensors":true,"modem_signal":"No signal until connected","wifi_signal":"100%","internet_source":"wlwan_only","leveler":false,"auth":{"oem2ghz":{"encrypt":"WPA2","disabled":false,"encryption":"psk2","hidden":true,"country":"US","chan":"auto","ssid":"WinegardOEMC433B3","autoconnect":true,"invalid":"0"},"sta2ghz":{"encrypt":"WPA/WPA2","disabled":false,"encryption":"psk-mixed","bridged":"wan","hidden":false,"country":"US","chan":"auto","ssid":"NaudoNet2.0","autoconnect":true,"invalid":"0"},"modem":{"imsi":"310170862606028","disabled":true,"modem":"ec25","simslot":"0","iccid":"89011703278626060282","slots":"0 1 3","apn":"m2m005163.attz","provider":"WINEGARD","manufacturer":"Quectel","locked_provider":false,"firmware":"EC25AFFDR07A09M4G_01.003.01.003","plan":"Winegard ConnecT Data Plan","model":"EC25-AF(D)","carrier":"ATT","canupdate":"yes","imei":"864839047066523","update":"no"},"wifi2ghz":{"encrypt":"WPA2","disabled":false,"encryption":"psk2","hidden":false,"country":"US","chan":"auto","ssid":"Winegard2ghzC433B3","autoconnect":true,"invalid":"0"},"guest2ghz":{"encrypt":"WPA2","disabled":true,"encryption":"psk2","hidden":false,"country":"US","chan":"auto","ssid":"WinegardGuestC433B3","autoconnect":true,"invalid":"0"}}}'''
        if self.session is None:
            result = self.login()
            if result:
                print('Login result failed', result)
                raise ValueError('Cannot log in to retrieve system status')

        # TODO:
            # Check if cache timer expired unless forced
            # Requst new status
        now = time.time()
        need_update = False
        if force is False:
            if (now - self.sys_status_timestamp) > self.CACHE_TIMEOUT:
                need_update = True
        else:
            need_update = True

        if need_update is True:
            status_url = f'http://{self.host}/cgi-bin/luci/sys_status'
            try:
                response = self.session.get(status_url, timeout=10)
            except ReadTimeout as err:
                # TODO: How to handle internal here ?
                raise

            if response.status_code == 200:
                self.sys_status = response.json()
                self.sys_status_timestamp = time.time()
            elif response.status_code == 403:
                self.session = None
                return self.get_sys_overview(force=force)

            return response

    def get_cellular_status(self):
        '''Get cellular details from Wineguard.
        "wwan": {
            "rx_bytes": 10345,
            "ifname": "wwan0",
            "tx_bytes": 10636,
            "netmask": "255.255.255.252",
            "rssi": -87,
            "expires": 6834,
            "tx_packets": 103,
            "dnsaddrs": [
                "172.31.250.10",
                "172.31.250.11"
            ],
            "rx_packets": 79,
            "ipaddr": "10.32.211.253",
            "mode": "4G",
            "network": "connected",
            "lac": "11272",
            "band": "LTE BAND 2",
            "type": "ethernet",
            "mcc": "310",
            "ifdev": "wwan0",
            "mnc": "260",
            "cell": "registered (roaming)",
            "strength": -87,
            "cellid": "21688844",
            "access": "E-UTRAN",
            "proto": "dhcp",
            "uptime": 366,
            "name": "wwan_4",
            "gateway": "10.32.211.254",
            "is_up": true,
            "macaddr": "00:00:00:00:00:00",
            "signal": 52
        },
        ...
        "modem_status": "Connected to Cellular KORE User Data Plan "iot.kore.com"",
        ...
        "internet_status": "Connected to Cellular KORE User Data Plan "iot.kore.com"",
        ...
        "connect_status": "Connected",
        ...
        "auth": {
            ...
            "modem": {
                "imsi": "234500094375845",
                "disabled": false,
                "modem": "ec25",
                "simslot": "1",
                "iccid": "8910390000060149887F",
                "slots": "0 1 3",
                "apn": "iot.kore.com",
                "provider": "KORE",
                "manufacturer": "Quectel",
                "locked_provider": false,
                "firmware": "EC25AFFDR07A09M4G_01.003.01.003",
                "plan": "KORE User Data Plan",
                "model": "EC25-AF(D)",
                "carrier": "KORE",
                "canupdate": "yes",
                "imei": "864839047066523",
                "update": "ec25"
        },

        '''
        self.get_sys_overview()
        wwan = self.sys_status.get('networks', {}).get('wwan', {})
        modem = self.sys_status.get('auth', {}).get('modem', {})

        cellular = {
            'signal': self.sys_status.get('modem_signal'),
            'status': self.sys_status.get('modem_status'),
            'nwMode': wwan.get('mode'), # LTE
            'nwRSSI': wwan.get('rssi'), # Strength,
            'modemIMEI': modem.get('imei'),
            'modemICCID': modem.get('iccid'),
            'modemFirmware': modem.get('firmware'),
            'provider': wwan.get('provider'),
            'band': wwan.get('band'),
            'mccmnc': f'{wwan.get("mcc")}{wwan.get("mnc")}'
        }
        if cellular['modemICCID'] is not None and cellular['modemICCID'].endswith('F'):
            cellular['modemICCID'] = cellular['modemICCID'].replace('F', '')

        # TODO: Find the best place to put this
        rssi = cellular.get('nwRSSI')
        if rssi is None:
            self.event_logger.add_event(
                RVEvents.CELLULAR_CELLUAR_STATUS_CHANGE,
                1,
                EventValues.FALSE
            )
            # TODO: Should we update the status at all for RSSI if none ?
        else:
            self.event_logger.add_event(
                RVEvents.CELLULAR_CELLUAR_STATUS_CHANGE,
                1,
                EventValues.TRUE
            )
            self.event_logger.add_event(
                RVEvents.CELLULAR_STRENGTH_CHANGE,
                1,
                rssi
            )

        return cellular

    def get_wifi_status(self):
        # TODO: Define standard data for Wifi
        self.get_sys_overview()
        print(self.sys_status)

        wifi_state = self.sys_status.get('wifi_state')
        if wifi_state == 'none':
            wifi_state = None

        wifi_status = self.sys_status.get('wifi_status')
        if wifi_status is not None:
            wifi_status = wifi_status.replace('Connected to WiFi \"', '').replace('\"', '')

        wifi_nw = self.sys_status.get('networks', {})
        if wifi_nw == []:
            print('No networks')
            ip = 'NA'
        else:
            wlwan = wifi_nw.get('wlwan', [])
            if wlwan == []:
                ip = 'NA'
            else:
                ip = wlwan.get('ipaddr')

        wifi = {
            'signal': self.sys_status.get('wifi_signal'),
            'ip': ip,
            'network': wifi_status
        }
        return wifi

    def _enable_gps(self, timer=30):
        '''
            Turn on GPS reporting as needed
            timer: int
                Controlls how often the Wineguard unit pulls the data
        '''
        # 'http://10.11.12.1/cgi-bin/luci/themes/winegard2/gps.htm?gpstime=300&wifibox=on&wifionly=1&mqtt=TURN+ON+GPS+SERVICES'
        enable_gps_url = f'http://{self.host}/cgi-bin/luci/themes/winegard2/gps.htm?gpstime={timer}&mqtt=TURN+ON+GPS+SERVICES'
        response = self.session.get(enable_gps_url, timeout=10)
        return response

    def _disable_gps(self):
        '''
            Turn GPS reporting off
        '''
        disable_gps_url = 'http://{self.host}/cgi-bin/luci/themes/winegard2/gps.htm?gpstime=300&wifibox=on&wifionly=1&mqtt=TURN+OFF+GPS+SERVICES'
        response = self.session.get(disable_gps_url, timeout=10)
        return response

    def get_sys_gps(self):
        # TODO: Ensure that we properly configure timers for when to request a new items
        # Goal is to have IoT never wait for data

        self.get_sys_overview()
        # TODO: Check reporting rate and set to 30 seconds if needed
        gps = self.sys_status.get('gps')
        gps['iotposition'] = f'{gps.get("latitude")}, {gps.get("longitude")}'
        gps['position'] = f'{gps.get("latitude")}, {gps.get("longitude")}'

        self.event_logger.add_event(
            RVEvents.LOCATION_GEO_LOC_CHANGE,
            1,
            gps['position']
        )
        self.HAL.app.config['last_position'] = gps['position']
        self.last_known_gps = gps['position']

        return gps

    def set_internet_access(self, option: str='CELLULAR'):
        url = f'http://{self.host}/cgi-bin/luci/themes/winegard2/3g4gsetup1.htm'
        # self.session.get(url)
        if option == 'WIFI':
            value = 'wifionly'
        elif option == 'CELLULAR':
            value = '3g4gonly'
        else:
            raise ValueError(f'{option} is not a valid setting')

        response = self.session.post(url, data=f'internetaccess={value}&continue=SELECT')
        return response


module_init = (
    WineGuard,
    'communication_defaults',
    'components'
)


if __name__ == '__main__':
    import sys

    try:
        host = sys.argv[1]
        BASE_URL = host
    except IndexError as err:
        print(err)

    # Test defaults, no config/credentials
    creds = {'username': 'admin', 'password': 'WinnConnect2022'}
    handler = WineGuard(credentials=creds)

    handler.login()

    # handler._enable_gps(timer=30)
    # print(handler.get_sys_gps())
    # print(handler.get_sys_overview())
    # print(handler.sys_status)

    while True:
        # print('Wifi', handler.get_wifi_status())
        # print('Cellular', handler.get_cellular_status())

        # print(handler.set_internet_access('WIFI'))
        print(handler.set_internet_access('CELLULAR'))

        # print('Wifi', handler.get_wifi_status())
        # print('Cellular', handler.get_cellular_status())

        break
