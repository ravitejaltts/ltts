import json
import time

import unittest

from requests.exceptions import ConnectTimeout

from hw_wineguard import handler as wineguard

test_state = json.load(open('tests/test_state.json', 'r'))


class TestWinguard(unittest.TestCase):
    def _set_state(self):
        wineguard.sys_status = test_state
        wineguard.sys_status_timestamp = time.time()
    
    def _set_unreachable_host(self):
        wineguard.host = '1.1.2.3'
    
    def _set_default_host(self):
        wineguard.host = '10.11.12.1'

    def test_gps_state(self):
        self._set_state()
        gps_status = wineguard.get_sys_gps()
        self.assertEqual(gps_status.get('iotposition'), '47.57125, -122.14265')
    
    def test_wifi_state(self):
        self._set_state()
        wifi_status = wineguard.get_wifi_status()
        assert wifi_status.get('signal') == '100%'
        assert wifi_status.get('ip') is None
        assert wifi_status.get('network') == 'NaudoNet2.0'
    
    def test_cellular_state(self):
        self._set_state()
        cellular_status = wineguard.get_cellular_status()
        assert cellular_status.get('signal') == 'No signal until connected'
    
    def test_connection_error(self):
        self._set_unreachable_host()
        with self.assertRaises(ConnectTimeout):
            wineguard.login()


if __name__ == '__main__':
    unittest.main()
