import os
import sys

class environment:

    _installation_path = os.environ.get('WGO_HOME_DIR', os.path.join(os.path.dirname(__file__), '..', '..'))
    _data_path = os.path.join(_installation_path, "data")
    _user_storage_path = os.environ.get('WGO_USER_STORAGE', None)

    main_host_uri = os.environ.get('WGO_MAIN_HOST', 'http://localhost')
    bind_address = os.environ.get('WGO_BIND_ADDR', '127.0.0.1')
    main_service_port = os.environ.get('WGO_MAIN_PORT', 8000)
    can_service_port = os.environ.get('WGO_CAN_PORT', 8001)
    iot_service_port = os.environ.get('WGO_IOT_SERVICE_PORT', 8002)
    bluetooth_service_port = os.environ.get('WGO_BT_PORT', 8005)

    def __init__(self):
        if (None == self._user_storage_path):
            this = os.path.abspath(sys.argv[0])
            this = os.path.split(this)[0]
            self._user_storage_path = os.path.join(this, 'storage')
        try:
            if not os.path.exists(self.storage_file_path()):
                os.mkdir(self.storage_file_path())
        except:
            None

        try:
            if not os.path.exists(self.log_file_path()):
                os.mkdir(self.log_file_path())
        except:
            None

        try:
            if not os.path.exists(self.certs_path()):
                os.mkdir(self.certs_path())
        except:
            None

    def app_installation_path(self):
        return self._installation_path

    def app_installation_path(self, *paths):
        return os.path.join(self._installation_path, *paths)

    def data_file_path(self):
        return self._data_path

    def data_file_path(self, *paths):
        return os.path.join(self._data_path, *paths)

    def storage_file_path(self):
        return os.path.abspath(self._user_storage_path)

    def storage_file_path(self, *paths):
        return os.path.join(self._user_storage_path, *paths)

    def log_file_path(self):
        return self.storage_file_path('logs')

    def log_file_path(self, *paths):
        return self.storage_file_path('logs', *paths)

    def package_file_path(self):
        return self.storage_file_path('packages')

    def package_file_path(self, *paths):
        return self.storage_file_path('packages', *paths)

    def vin_file_path(self):
        return self.storage_file_path('vin.txt')

    def config_path(self):
        return os.path.join(self._user_storage_path, 'config')

    ##### TODO replace this with calls to Gozer because certs can't be stored in the clear on disk
    ##### This is here for convenience/transition because there was interaction with the file system for certs and the paths were hard coded
    def certs_path(self):
        return self.storage_file_path('certs')

    def certs_path(self, *paths):
        return self.storage_file_path('certs', *paths)
    #####

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(environment, cls).__new__(cls)
        return cls.instance
