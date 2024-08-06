import logging
import json
import os
from libpygozer import vault

from common_libs.system.system_logger import prefix_log

from common_libs import environment
_env = environment()

wgo_logger = logging.getLogger('main_service')


def get_telemetry_file(tfile: str) -> dict:
    '''Check the possible locations in order to load our telemetry file - falling back to vanilla if needed.'''
    result = {}
    try:  # First see if it is in the build area
        result = json.load(open(_env.app_installation_path(tfile), 'r'))
    except Exception as e:
        try:
            prefix_log(wgo_logger, "get_telemetry_file", e)
            result = json.load(open(_env.package_file_path(tfile), 'r'))
        except Exception as e:
            prefix_log(wgo_logger, "get_telemetry_file", "Loading Telemetry VANILLA_ota_template.json")
            result = json.load(
                    open(_env.data_file_path("VANILLA_ota_template.json"), "r"))
    return result


class SpecialStorageClass():
    _vault = None

    def __init__(self):
        try:
            # self._vault = vault()
            self._vault = None
        except Exception:
            prefix_log(wgo_logger, "SpecialStorageClass", "Security module not present!")

    def put_secure_blob(self, name: str, blob: str):
        '''Keep our keys and certs private'''
        if self._vault is not None:
            self._vault.put_secret(name, blob)
        else:
            prefix_log(wgo_logger, f"SpecialStorageClass" ,f"Storing unsecure not implemented {name}.")

    def get_secure_blob(self, name: str) -> str:
        '''Keep our keys and certs private'''
        blob = None
        if self._vault is not None:
            blob = self._vault.get_secret(name)
            prefix_log(wgo_logger, f"SpecialStorageClass" ,f"blob {name}")
        else:
            # Try cert dir
            prefix_log(wgo_logger, f"SpecialStorageClass" ,"Fetching from certs dir normally.")
            certPath = _env.certs_path(name)
            if os.path.isfile(certPath):
                with open(certPath, 'r') as cert_file:
                    blob = cert_file.read()

        return blob

    def restore_cert(self, name: str) -> bool:
        '''Restore a cert so we can act on the file with X500'''
        try:
            success = True
            if self._vault is not None:
                blob = self._vault.get_secret(name)
                certPath = _env.certs_path(name)
                with open(certPath, 'w') as cert_file:
                    cert_file.write(blob)

            certPath = _env.certs_path(name)
            success = os.path.isfile(certPath)
            return success
        except Exception as err:
            prefix_log(wgo_logger, f"SpecialStorageClass" ,f"restore_cert {name} {err}")
            return False

    def find_store_certs(self):
        '''check the certs dir for any secrets and move them'''
        if self._vault is not None:
            # List all files in the cert  directory
            files = os.listdir(_env.certs_path())
            # Print each file name

            prefix_log(wgo_logger, "SpecialStorageClass", f"files {files}")
            print(files)
            for file_name in files:
                prefix_log(wgo_logger, "SpecialStorageClass", f"Securing {file_name}")
                print(file_name)
                try:
                    with open(_env.certs_path(file_name), 'r') as cert_file:
                        blob = cert_file.read()
                        self._vault.put_secret(file_name, blob)
                except Exception as err:
                    prefix_log(wgo_logger, "SpecialStorageClass", f"{file_name} find_store_certs {err}")
        else:
            prefix_log(wgo_logger, "SpecialStorageClass", "Not implemented")
            print("Lfail")


SStorage = SpecialStorageClass()


if __name__ == '__main__':
    print("Start")
    SStorage.find_store_certs()

    files = os.listdir("/storage/wgo/certs_in_storage")
    # Print each file name

    prefix_log(wgo_logger, f"SpecialStorageClass", f"files {files}")
    for file_name in files:
        print(f"Testing {file_name}")
        prefix_log(wgo_logger, "SpecialStorageClass", f"Securing {file_name}")
        try:
            with open(f"/storage/wgo/certs_in_storage/{file_name}", 'r') as cert_file:
                blob = cert_file.read()
                if blob != SStorage.get_secure_blob(file_name):
                    print(f"Fail to match {file_name} {blob}")
                else:
                    print(f"Matched {file_name}")
                    SStorage.restore_cert(file_name)
        except Exception as err:
            prefix_log(wgo_logger, "SpecialStorageClass", f"{file_name} find_store_certs {err}")

    print("End")
