'''Module to handle all externbal clients and make them commonly available'''

from common_libs import environment

_env = environment()

try:
    import httpx as http_lib
except ImportError:
    import requests as http_lib


def get_http_client():
    '''Helper to see if httpx is available.'''
    if http_lib.__name__ == 'requests':
        return http_lib.Session()
    elif http_lib.__name__ == 'httpx':
        return http_lib.AsyncClient()


class HTTPHandler:
    '''Helper class to wrap around most common HTTP calls.'''
    def __init__(self, cfg: dict = None):
        if cfg is None:
            self.cfg = {}
        else:
            self.cfg = cfg
        self.client = get_http_client()

        if http_lib.__name__ == 'httpx':
            self._get = self.async_get
            self.put = self.async_put
            self.post = self.async_post
            self.patch = self.async_patch

    def async_get(self, *args, **kwargs):
        pass

    def async_put(self, *args, **kwargs):
        pass

    def async_post(self, *args, **kwargs):
        pass

    def async_patch(self, *args, **kwargs):
        pass


# Set up clients
IOT_CLIENT = get_http_client()
MAIN_CLIENT = get_http_client()
CAN_CLIENT = get_http_client()
BT_CLIENT = get_http_client()


# Set up base URLs
IOT_BASE_URL = f'http://localhost:{_env.iot_service_port}'
BT_BASE_URL = f'http://localhost:{_env.bluetooth_service_port}'
MAIN_BASE_URL = f'http://localhost:{_env.main_service_port}'
CAN_BASE_URL = f'http://localhost:{_env.can_service_port}'
