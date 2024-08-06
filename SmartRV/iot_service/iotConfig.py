import configparser
import json

import os
from common_libs import environment
from threading import Lock
from iot_service.utils import Utils, Iot_Status
_env = environment()

HOME_DIR = os.environ.get("WGO_HOME_DIR", '.')

try:
    VERSION = json.load(
        open(
            os.path.join(
                HOME_DIR,
                'version.json'
            ),
            'r'
        )
    )
except IOError as err:
    print('IOError', err)
    try:
        VERSION = json.load(
            open('../version.json', 'r')
        )
    except IOError as err:
        print('IOError', err)
        VERSION = {
            'version': __version__,
        }

# Inject more data
VERSION['debug'] = True


class IotConfig():

    configLock = Lock()  # lock for multi threads
    # Initialize the ConfigParser object
    configParser = configparser.ConfigParser()

    def __init__(self, main, version):
        self.version_data = version

        self.iot = main
        # TCU data needs to be upper case keys for the platform
        self.configParser.optionxform = str  # This preserves the original case of keys

        filereadresult = self.configParser.read(
            _env.storage_file_path("Iot_config.ini")
        )
        try:
            have_ini = filereadresult[0].find("Iot_config.ini") != -1
        except Exception as err:
            print(f"Error reading Iot_config.ini: {err}")
            have_ini = False

        if not have_ini:
            self.create_ini()
            if self.get_key("Device", "vin") is None:
                self.iot.update_status(Iot_Status.VIN_NEEDED, "Waiting for VIN.")
        else:
            update = False
            # Check ini for recently added things it might not have
            if self.get_key("Device", "fallback_api_url") == "":
                self.set_key("Device","fallback_api_url", self.get_key("Device", "api_url", ""))
                update = True
            try:
                if self.get_key("Platform", "temp_api_url", "") == "":
                    update = True
                if self.get_key('Platform', 'last_id', "") == "":
                    update = True
            except Exception as err:
                print(f"Error init key: {err}")
                self.configParser["Platform"] = {
                    "temp_api_url": "",
                    "last_id": "",
                    "transfer_failed": "0",
                    "expiration_time": "0.0",
                }
                update = True
            if update is True:
                self.saveConfig()

    def get_key(self, section, key, default=""):
        ''' Get your key or return it with the default'''
        _value = default
        _section = None
        try:
            _section = self.configParser[section]
        except Exception as err:
            msg = f"[Config] get_key {err}"
            self.configParser[section] = ""
            self.configParser[section][key] = default
        if _section is not None:
            try:
                _value = self.configParser[section][key]
            except:
                self.configParser[section][key] = default
        return _value

    def set_key(self, section, key, value):
        """store the key - don't forget to call save when added your keys"""
        try:
            _section = self.configParser[section]
        except:
            self.configParser[section] = None
        try:
            self.configParser[section][key] = value
        except Exception as err:
            msg = f"[Config] set_key {err}"
            Utils.pushLog(msg, 'error')
            self.configParser[section][key] = None

    def create_ini(self):
        # we know this is a new bootup and we don't have all we need
        self.iot.update_status(Iot_Status.CONFIG_NEEDED, f"Create our INI file!")
        #
        self.configParser.read_dict(
            {
                "Device": {
                    "vin": "",
                    "assigned_hub": "",
                    "cert_pp": "Winn23",
                    "provisioning_host": "global.azure-devices-provisioning.net",
                    "id_scope": "One0075D1E7",
                    # registration_id"": "",
                    "device_id": "",
                    "platform_env": "",
                    "far_field": "",
                    "csr_required": "",
                    "device_type": "",
                    "serial_number": "",
                    "option_codes": "",
                    "model_year": "",
                    "api_url": "",
                    "software_version": self.version_data,
                },
                "States": {
                    "configured": "False",
                    "chatty_mode": "False",
                    "chatty_expires": "",
                    "connected": "False",
                    "provisioned": "False",
                },
                "Platform": {
                    "last_id": "",
                    "transfer_failed": "0"
                },
                "OTA": {
                    "allow_auto": "False",
                    "state": "7",
                    "desired": "N",
                    "error_count": "0",
                    "waiting": '',
                    "waiting_ts": '',
                    "telemetry_file": "VANILLA_ota_template.json"
                },
                "TCU": {}
            }
        )
        self.saveConfig()

    def saveConfig(self):
        """Used to store config and provisioning etc between service restarts"""
        with self.configLock:
            with open(_env.storage_file_path("Iot_config.ini"), "w") as configfile:
                self.configParser.write(configfile)
