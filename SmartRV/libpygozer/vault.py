import os
from threading import Lock

from common_libs import environment

_env = environment()

class vault:
    _secret_stor = os.path.join(_env.storage_file_path(), '.secrets')

    def __init__(self):
        try:
            if not os.path.exists(self._secret_stor):
                os.mkdir(self._secret_stor)
        except:
            None

    def _create_path(self, *paths):
        return os.path.join(self._secret_stor, *paths)

    def get_secret(self, name):
       with open(self._create_path(name), 'r') as secret:
            blob = secret.read()
       return blob

    def remove_secret(self, name):
        handle = os.remove(self._create_path(name))
        return None

    def get_installation_cert(self):
        print('Local lib returning file.')
        with open('/opt/oem/installation.pem') as cert_file:
            blob = cert_file.read()
        return blob  # just read from a local file sans vault

    def put_secret(self, name, value):
        handle = open(self._create_path(name), 'w')
        handle.write(value)

    def has_secret(self, name):
        handle = self._create_path(name)
        return os.path.exists(handle)
