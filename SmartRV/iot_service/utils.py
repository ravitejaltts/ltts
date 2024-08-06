import os
import json
import shutil
from cryptography import x509
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import requests
import shutil

from enum import IntEnum, auto
import socket
import queue
import logging
from threading import Lock
from common_libs import environment
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

# from cryptography.hazmat.primitives.serialization.pkcs12 import (
#     serialize_key_and_certificates,
# )
from cryptography.hazmat.backends import default_backend

#from azure.iot.device import X509
#import tempfile
from libpygozer import vault

tlogger = logging.getLogger(__name__)

_env = environment()

BaseUrl = f"{_env.main_host_uri}:{_env.main_service_port}"

#  Used by IOT for device id
MIN_LENGTH = 3

class Iot_Status(IntEnum):
    FRESH_BOOT = 0
    CONFIG_OK = auto()
    CONFIG_NEEDED = auto()
    VIN_NEEDED = auto()
    VIN_ENTERED = auto()
    GETTING_VEHICLE_RECORDS = auto()
    VEHICLE_RECORDS_NOT_RECEIVED = auto()
    VEHICLE_RECORDS_LOADED = auto()
    VEHICLE_RECORD_MOVE = auto()
    REGISTATIONS_PATCH_CALL = auto()
    REGISTRATIONS_FAIL = auto()
    DPS_PROVISIONING = auto()
    DPS_FAIL = auto()
    FALLBACK_PREP = auto()
    DPS_CERTS_OK = auto()
    CONNECTING = auto()
    DPS_CERTS_MISSING = auto()
    PROVISIONED_INIT = auto()
    CONNECT_START = auto()
    CLIENT_FAIL = auto()
    CHECKING_FOR_INTERNET= 96  # Added to report missing internet at startup
    OFFLINE = 97
    CONNECTED = 98
    CONFIG_ERROR = 99


# REMOTE_SERVER = "http://azure.microsoft.com"
REMOTE_SERVER = "azure.microsoft.com"

class ClassUtils:
    q = queue.Queue(maxsize=100)
    logger = tlogger
    _json_result = {}
    _vault = vault()

    def add_to_json_store(self, key, value):
        """
        Prints the key-value pair and stores it in the json_result dictionary.
        """
        # Print the key-value pair
        print(f"{key}: {value}")

        # Add the key-value pair to the global dictionary
        self._json_result[key] = value

    def get_json_result(self):
        """
        Returns the current state of the json_result as a JSON string.
        """
        return json.dumps(self._json_result, indent=4)

    def setLogger(self, logger):
        self.logger = logger

    # Multi threads to write to this push
    def pushLog(self, msg: str, level: str = 'info'):
        logstr = f'{level}#{msg}'
        # Push to queue
        try:
            # print(logstr)
            self.q.put_nowait(logstr)
        except queue.Full:
            print(f"The queue is full! {msg}")

    def get_from_main(self, endpoint: str):
        apiResponse = requests.get(BaseUrl + endpoint)
        return apiResponse.json()

    def put_to_main(self, endpoint: str, data):
        apiResponse = requests.put(BaseUrl + endpoint,
                                   json=data)
        return apiResponse.json()

    # Should just be one threads writing
    def writeLogs(self):
        try:
            # Retrieving the log strings
            while True:
                logstr = self.q.get_nowait()
                parts = logstr.split('#', 1)  # the '1' ensures only the first '#' is used for splitting
                if parts[0] == 'error':
                    self.logger.error(parts[1])
                elif parts[0] == 'info':
                    self.logger.info(parts[1])
                else:
                    self.logger.debug(parts[1])

        except queue.Empty:
            return

    def has_secret(self, name):
        return self._vault.has_secret(name)

    def get_secret(self, name):
        return self._vault.get_secret(name)

    def put_secret(self, name, value):
        try:
            self._vault.put_secret(name, value)
        except Exception as err:
            print(f"Name: {name}  length: {len(value)}")
            print(f"Failed to save: {name} -> {err}")

    # def load_certificate(file_path: str) -> str:
    #     """
    #         LOAD for CSR
    #         Loads and returns a x509 base64 string at the `file_path`
    #     """
    #     Utils.pushLog(f'load_certificate  {file_path}')
    #     with open(file_path) as cert_file:
    #         cert_str = cert_file.read()
    #         # print(f'Cert Loading = {cert_str}')
    #         return Utils.strip_certificate(cert_str)

    @staticmethod
    def remove_empty_files(directory):
        """
        This function checks a directory and removes files with a length of 0 bytes.

        Parameters:
        directory (str): The path to the directory to be checked.

        Returns:
        None
        """
        # Check if the directory exists
        if not os.path.exists(directory):
            Utils.pushLog(f"Directory {directory} does not exist.")
            return

        # List all files in the directory
        files = os.listdir(directory)

        for file in files:
            file_path = os.path.join(directory, file)

            # Check if the path is a file
            if os.path.isfile(file_path):
                # Get the size of the file
                file_size = os.path.getsize(file_path)

                # If the file size is 0, remove the file
                if file_size == 0:
                    os.remove(file_path)
                    Utils.pushLog(f"Removed empty file: {file_path}")


    @staticmethod
    def checkCerts():
        """
        Temp mod to look for 0 length files in the vault.
        """
        Utils.remove_empty_files("/storage/vault/secrets")   # should use an env var but with the vault in the OS we don't have it.

    @staticmethod
    def strip_certificate(cert_str: str) -> str:
        """
            DATA for CSR
            Loads and returns a x509 base64 string at the `cert_str`
        """
        cert_str = cert_str.replace('-----BEGIN CERTIFICATE-----', '')
        cert_str = cert_str.replace('-----END CERTIFICATE-----', '')
        cert_str = cert_str.replace('-----BEGIN CERTIFICATE REQUEST-----', '')
        cert_str = cert_str.replace('-----END CERTIFICATE REQUEST-----', '')
        cert_str = cert_str.replace('-----BEGIN PRIVATE KEY-----', '')
        cert_str = cert_str.replace('-----END PRIVATE KEY-----', '')
        cert_str = cert_str.replace('\n', '')
        cert_str = cert_str.replace('\r', '')

        # print(f'Cert Loading = {cert_str}')
        return cert_str

    @staticmethod
    def load_device_cert_file(desired: str, env: str) -> str:
        """
            Using PEMs not CSR
        """
        Utils.pushLog(f'load_device_cert_file {desired} {env}')
        cert = None
        cert_str = None
        if desired is not None:  # !none we think we have a device cert
            if Utils.has_secret(desired):
                Utils.pushLog(f'load_pem_secret d0 {desired}')
                try:
                    cert_data = Utils.get_secret(desired)
                    cert = x509.load_pem_x509_certificate(cert_data.encode())
                except Exception as err:
                    Utils.pushLog(f'load_device_cert_file fail {err}')
                    Utils.checkCerts()
            else:
                Utils.pushLog(f'load_device_cert_file not found {desired}')

        # if cert is None: # fallback onto installation cert from the vault
        #     try:
        #         Utils.pushLog(f'load_device_cert_file default cert from vault')
        #         cert_data = Utils._vault.get_installation_cert().encode('utf-8')
        #         cert = x509.load_pem_x509_certificate(cert_data)
        #     except Exception as err:
        #         Utils.pushLog(f'failed to load installation cert from vault {err}')
        #         return None
        if cert is None:  # fallback onto .bak  cert from the vault if we have it
            if Utils.has_secret(f'{desired}.bak'):
                Utils.pushLog(f'load_pem_secret d0 {desired}.bak')
                try:
                    cert_data = Utils.get_secret(f'{desired}.bak')
                    cert = x509.load_pem_x509_certificate(cert_data.encode())
                    Utils.pushLog(f'loaded backup in load_device_cert_file {desired} will restore!')
                    Utils.restore_backup_cert(desired)
                except Exception as err:
                    Utils.pushLog(f'load_device_cert_file fail {err}')
                    Utils.checkCerts()
            else:
                Utils.pushLog(f'load_device_cert_file bakup!! not found {desired}')

        if cert is None:  # fallback onto installation cert from the vault
            # TODO: Check if this has failed
            desired = f"{env}-env.new"
            if Utils.has_secret(desired):
                Utils.pushLog(f'load_pem_secret d1 {desired}')
                try:
                    cert_data = Utils.get_secret(desired)
                    cert = x509.load_pem_x509_certificate(cert_data.encode())
                except Exception as err:
                    Utils.pushLog(f'load_device_cert_file fail {err}')
                    Utils.checkCerts()
            else:
                desired = f"{env}-env.pem"
                if Utils.has_secret(desired):
                    Utils.pushLog(f'load_pem_secret d2 {desired}')
                    try:
                        cert_data = Utils.get_secret(desired)
                        cert = x509.load_pem_x509_certificate(cert_data.encode())
                    except Exception as err:
                        Utils.pushLog(f'2 load_device_cert_file fail {err}')
                        Utils.checkCerts()
                        # do we have a recent WinnConnect-Installation in the vault
                        try:
                            Utils.pushLog('2 load_device_cert_file WinnConnect-Installation from vault')
                            cert_data = Utils.get_secret("WinnConnect-Installation.pem")
                            cert = x509.load_pem_x509_certificate(cert_data.encode())
                            Utils.pushLog('load_device_cert_file using WinnConnect-Installation.pem!!')
                        except Exception as err:
                            Utils.pushLog(f'2 failed to load installation cert from vault {err}')
                            # fallback onto original installation cert from the vault
                            try:
                                cert_data = Utils._vault.get_installation_cert()
                                cert = x509.load_pem_x509_certificate(cert_data.encode())
                                Utils.pushLog(f'load_device_cert_file using installation cert!!')
                            except Exception as err:
                                Utils.pushLog(f'2 failed to load ANY cert from vault 2 {err}')
                                return None
                else:
                    # do we have a recent WinnConnect-Installation in the vault
                    try:
                        Utils.pushLog('3 load_device_cert_file WinnConnect-Installation from vault')
                        cert_data = Utils.get_secret("WinnConnect-Installation.pem")
                        cert = x509.load_pem_x509_certificate(cert_data.encode())
                        Utils.pushLog('load_device_cert_file using WinnConnect-Installation.pem!!')
                    except Exception as err:
                        Utils.pushLog(f'3 failed to load WinnConnect cert from vault {err}')
                        # fallback onto original installation cert from the vault
                        try:
                            cert_data = Utils._vault.get_installation_cert()
                            cert = x509.load_pem_x509_certificate(cert_data.encode())
                            Utils.pushLog('load_device_cert_file using installation cert!!')
                        except Exception as err:
                            Utils.pushLog(f'3 failed to load ANY cert from vault 3 {err}')
                            return None

        cert_str = cert.public_bytes(Encoding.PEM).decode()
        cert_str = cert_str.replace('\n', '')
        cert_str = cert_str.replace('\r', '')
        #Utils.pushLog(f'cert string  {cert_str}')
        return cert_str

    @staticmethod
    def load_csr_file(vin: str, dev_id: str = None) -> str:
        "Set the environment - load the csr - trim only"
        result = None
        #csr = None
        #if Utils.has_secret(f"{vin}.csr") is False:
        # Create CSR
        try:
            Utils.create_csr(vin=vin, dev_id=dev_id)
            csr = Utils.get_secret(f"{vin}.csr")
            result = Utils.strip_certificate(csr)
        except Exception as err:
            Utils.pushLog(f'load_csr_file ERROR: {err}')
        if result is None:
            Utils.pushLog(f'failed to load CSR from vault')
            raise FileNotFoundError

        return result

    @staticmethod
    def check_backup_cert(desired: str):
        '''Do we have this cert backed up - if not save it'''
        if Utils.diff_in_vault(desired, f"{desired}.bak") is False:
            # Store it
            cert = Utils._vault.get_secret(desired)
            Utils._vault.put_secret(f"{desired}.bak", cert)
            Utils.pushLog(f'Cert {desired} backed up.')


    @staticmethod
    def have_internet(hostname=REMOTE_SERVER):
        try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname(hostname)
            # connect to the host -- tells us if the host is actually reachable
            s = socket.create_connection((host, 80), 2)
            s.close()
            return True
        except Exception:
            pass  # we ignore any errors, returning False
        return False

    @staticmethod
    def remove_BLD_dirs(latest: str):
        """
        Searches for directories in the given path that start with 'bld_'
        and removes them unless they match 'latest'.

        Args:
        - latest  (str): Directory to save directory.

        Returns:
        - None
        """
        # List all entries in the given directory
        for entry in os.listdir(_env.storage_file_path()):
            full_entry_path = _env.storage_file_path(entry)

            # Check if the entry is a directory, starts with 'xyz_', and is not 'xyz_save'
            if os.path.isdir(full_entry_path) and entry.startswith('bld_') and entry != 'latest':
                shutil.rmtree(full_entry_path)
                Utils.pushLog(f'Removed: {full_entry_path}')

    @staticmethod
    def diff_in_vault(name1, name2):
        '''Return True if equal'''
        if Utils._vault.has_secret(name1) is True and \
            Utils._vault.has_secret(name2) is True:
            s1 =  Utils._vault.get_secret(name1)
            s2 =  Utils._vault.get_secret(name2)
            # compare
            return s1 == s2
        else:
            return False

    @staticmethod
    def diff_vs_vault(name, value, save=True):
        result = True  # All call action if False - meaning cert was NEW
        '''Return True if equal'''
        if Utils._vault.has_secret(name) is True:
            s1 = Utils._vault.get_secret(name)
            # compare
            result = (s1 == value)
            if result is False and save is True:
                Utils._vault.put_secret(name, value)
                Utils.pushLog(f'Secret {name} replaced.')
        elif save is True:
                Utils._vault.put_secret(name, value)
                Utils.pushLog(f'New {name} saved.')
        else:
            Utils.pushLog(f'Not in vault {name} and not saved.')
            result = False
        return result

    @staticmethod
    def create_csr(vin, dev_id: str):
        desired = f"{vin}.key"
        my_key = None
        try:
            key_data = Utils.get_secret(desired)
            my_key = load_pem_private_key(
                data=key_data.encode(),
                password=None,
                backend=default_backend(),
            )
            Utils.pushLog(f"my_key came from vault: {desired}")

        except Exception as err:
            print(f"my_key err: {err}")
            try:
                certPath = _env.certs_path(desired)
                with open(certPath) as cert_file:
                    my_key = load_pem_private_key(
                            data=cert_file.read(),
                            password=None,
                            backend=default_backend(),
                        )
                    my_key_value = cert_file.read()
                Utils.put_secret(name=desired, value=my_key_value)
            except Exception as err:
                print(f"my_key path err: {err}")
                # need to generate
                my_key = rsa.generate_private_key(
                    public_exponent=65537, key_size=4096, backend=default_backend()
                )
                Utils.pushLog(f'create_csr keydata GENERATED.')
                my_key_value=my_key.private_bytes(
                        encoding=Encoding.PEM,
                        format=PrivateFormat.PKCS8,
                        encryption_algorithm=NoEncryption(),
                    ).decode("utf-8")

                Utils.put_secret(
                    name=desired,
                    value=my_key_value,
                )

        # cn1 = f"/CN={dev_id}"

        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(
                x509.Name(
                    [
                        x509.NameAttribute(NameOID.COMMON_NAME, dev_id),
                    ]
                )
            ).sign(my_key, hashes.SHA256(), default_backend())
        )

        #print(f"csr {csr.public_bytes(encoding=Encoding.PEM)}")
        Utils.put_secret(
            name=f"{vin}.csr",
            value=csr.public_bytes(encoding=Encoding.PEM).decode("utf-8"),
        )
        return csr
    @staticmethod
    def restore_backup_cert(desired: str):
        '''Needed the backup cert - make it the regular one.'''
        if Utils.has_secret(f"{desired}.bak") is False:
            # This should not happen if logic is correct
            Utils.pushLog(f'Cert {desired} backup error - not found.')
        else:  # We just used our .bak cert - so make them equal
            # Store it
            cert = Utils._vault.get_secret(f"{desired}.bak")
            Utils._vault.put_secret(desired, cert)
            Utils.pushLog(f'Cert {desired} restored from backup.')


# from cryptography import x509
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import serialization
    # @staticmethod
    # def create_pkcs12(public_cert, private_key):

    #     # Create the PKCS#12 (PFX) package
    #     pfx = serialize_key_and_certificates(
    #         name=None,
    #         key=private_key,
    #         cert=public_cert,
    #         cas=None,
    #         encryption_algorithm=serialization.NoEncryption()
    #     )

    #     return pfx
    #     # # Write the PFX package to a file
    #     # with open(output_path, 'wb') as f:
    #     #     f.write()

    @staticmethod
    def check_if_installation_cert(name1) -> bool:
        result = False
        if Utils._vault.has_secret(name1) is True :
            s1 =  Utils._vault.get_secret(name1).encode()
            try:
                certificates = x509.load_pem_x509_certificates(s1)
                for i, certificate in enumerate(certificates):
                    common_names = certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
                    if common_names:
                        if "WinnConnect-Installation" in common_names[0].value:
                            cname = "WinnConnect-Installation.pem"
                            data = certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
                            if Utils.diff_vs_vault(cname, data) is False:
                                Utils.pushLog('Contains - a NEW Installation-cert')
                                Utils.pushLog(f'New {cname} saved.')
                                result = True
                            else:
                                Utils.pushLog(f'Already had {cname} in vault.')
            except Exception as err:
                try:
                    print(f" Multiple cert check {name1} failed err: {err}")
                    print(f" Trying single cert check.")
                    certificate = x509.load_pem_x509_certificate(s1)
                    common_names = certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
                    if common_names:
                        if "WinnConnect-Installation" in common_names[0].value:
                            cname = "WinnConnect-Installation.pem"
                            data = certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
                            if Utils.diff_vs_vault(cname, data) is False:
                                Utils.pushLog('Contains - a NEW Installation-cert')
                                Utils.pushLog(f'New {cname} saved.')
                                result = True
                            else:
                                Utils.pushLog(f'Already had {cname} in vault.')
                except Exception as err:
                    print(f" Cert check {name1} failed err: {err}")
        return result

    @staticmethod
    def check_files_vs_vault(cert_dir: str = "/storage/wgo/certs"):
       # List all files in the directory
        file_list = os.listdir(cert_dir)

        # Loop through each file and read its contents into a string
        for file_name in file_list:
            file_path = os.path.join(cert_dir, file_name)
            # Check if the item in the directory is a file (not a directory)
            if os.path.isfile(file_path):

                with open(file_path, 'r') as file:
                    try:
                        file_contents = file.read()
                        print(f"Length of the data is: {file_contents}")

                        if Utils._vault.has_secret(file_name) is True:
                            # compare
                            if Utils.get_secret(file_name) == file_contents:
                                print(f"File and vault are equal> {file_name}")
                            else:
                                    print(f"File and vault NOT equal> {file_name}")
                                    Utils.put_secret(file_name, file_contents)

                        else:
                            # move to gozer
                            Utils.put_secret(file_name, file_contents)
                            print(f"MOVING File to vault > {file_name}")
                    except Exception as err:
                        print(f"File error {err}  {file_name}")


    @staticmethod
    def get_disk_space(directory='/storage'):
        statvfs = os.statvfs(directory)
        free_space_bytes = statvfs.f_frsize * statvfs.f_bavail
        return free_space_bytes

    @staticmethod
    def check_disk_space(directory='/storage', required_space_mb=200):
        """
        Checks if there is at least the specified amount of free disk space in the given directory.

        Parameters:
        directory (str): The directory to check for available disk space.
        required_space_mb (int): The required disk space in megabytes (MB).

        Returns:
        bool: True if there is enough free disk space, False otherwise.
        """
        required_space_bytes = required_space_mb * 1024 * 1024

        # Get the disk usage statistics
        statvfs = os.statvfs(directory)

        free_space_bytes = statvfs.f_frsize * statvfs.f_bavail
        return free_space_bytes >= required_space_bytes

    def disp_csr_from_vault(self, name1):
        if Utils.has_secret(name1) is True :
            s1 =  Utils.get_secret(name1).encode()
            csr = x509.load_pem_x509_csr(s1, default_backend())

            # Print the subject
            print("Subject:", csr.subject)

            # Print the public key
            public_key = csr.public_key()
            pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            print("\nPublic Key:\n", pem.decode())

            # If there are any extensions, print them
            if csr.extensions:
                print("\nExtensions:")
                for extension in csr.extensions:
                    print(extension)

    def disp_der_from_vault(self, name1):
        if self.has_secret(name1) is True :
            #pem_cert_data = "-----BEGIN CERTIFICATE-----\n"
            s1 =  self.get_secret(name1).encode()
            #pem_cert_data += base64.b64encode(s1).decode('ascii')
            #pem_cert_data += "\n-----END CERTIFICATE-----\n"
            try:
                certificates = x509.load_pem_x509_certificates(s1)

                if "WinnConnect-Installation" in certificates:
                    print(f"Contains - new Installation-cert")
                # Display the contents of the certificate
                #print(certificate.public_bytes(encoding=x509.serialization.Encoding.PEM))
                print(certificates)
                for item in certificates:
                    print(item)
                self._json_result = {}
                for i, certificate in enumerate(certificates):

                    if "WinnConnect-Installation" in certificate.subject:
                        print(f"\nCert {i} - the NEW Installation-cert\n\n")

                    print(f"\n   {name1}\n")
                    # Print various details from the certificate
                    self.add_to_json_store("Subject", str(certificate.subject))
                    subject = certificate.subject
                    common_names = subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
                    if common_names:
                        if "WinnConnect-Installation" in common_names[0].value:
                             print(f"\n\nCert {i} Contains - the NEW Installation-cert  {common_names[0].value} \n\n")
                    self.add_to_json_store("Issuer", str(certificate.issuer))
                    self.add_to_json_store("Serial_Number", str(certificate.serial_number))
                    self.add_to_json_store("Validity_Period", "as follows")
                    self.add_to_json_store("Not_Before", str(certificate.not_valid_before))
                    self.add_to_json_store("Not_After", str(certificate.not_valid_after))
                    #print("Public_Key:", certificate.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).)

            except Exception as err:
                self.add_to_json_store(f"Error", str(err))
            return self._json_result

# class InMemoryX509:
#     def __init__(self, cert_pem, key_pem):
#         self.cert_pem = Utils.get_secret(cert_pem)
#         self.key_pem = Utils.get_secret(key_pem)
#         #self.cert = x509.load_pem_x509_certificate(self.cert_pem, default_backend())
#         #self.key = serialization.load_pem_private_key(self.key_pem, password=None, backend=default_backend())

#     def get_azure_x509(self):
#         # Here, we would ideally write the cert and key to temporary files
#         # because the Azure IoT SDK expects file paths. However, for security,
#         # these should be handled carefully (e.g., using tempfile module)
#         with tempfile.NamedTemporaryFile(delete=False) as cert_file:
#             cert_file.write(self.cert_pem)
#             cert_file_path = cert_file.name

#         with tempfile.NamedTemporaryFile(delete=False) as key_file:
#             key_file.write(self.key_pem)
#             key_file_path = key_file.name

#         # Create the X509 object
#         x509_cert = X509(cert_file_path, key_file_path)

#         return x509_cert

#     # def __del__(self):
#     #    #  print(f"X Object is being destroyed")
#     #    os.remove(self.cert_file_path)
#     #    os.remove(self.key_file_path)


class LogExtra:
    def __init__(self, filename):
        self.logname = _env.log_file_path(filename)
        # Open the file and immediately close it to create or overwrite it
        try:
            with open(self.logname, 'w') as file:
                pass
        except:
            print("State log disabled.")

    def _check_size(self):
        # Get the size of the file
        try:
            if os.path.getsize(self.logname) > 20480:
                # Reset the file if it's over 20 KB
                open(self.logname, 'w').close()
            return os.path.getsize(self.logname)
        except OSError:
            return 0

    def append(self, text):
        # Check the size
        self._check_size()
        # Open the file in append mode and write the text
        try:
            with open(self.logname, 'a') as file:
                file.write(text + '\n')
        except:
            print("State log disabled.")

    def report(self):
        result = {}
        with open(self.logname, 'r') as file:
            result = file.read()
        return result

StateLog = LogExtra("iot_state.log")

Utils = ClassUtils()


def read_file_to_string(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content


# TODO: use a single function to read the release file in common libs
# shared with manufacturing UI and possibly other places
def read_data_after_version_id(file_path):
    version_id_value = ''
    if not os.path.exists(file_path):
        return version_id_value

    with open(file_path, 'r') as file:
        # Iterate over each line in the file
        for line in file:
            # Check if the current line starts with 'VERSION_ID='
            if line.startswith('VERSION_ID='):
                # Read and return the remainder of the file
                version_id_value = line.strip().split('VERSION_ID=', 1)[1].replace('\r', '')
                break  # Exit the loop as we found the target line
    return version_id_value


if __name__ == '__main__':

    #Utils.disp_csr_from_vault('1054042BB0D700000.csr')
    Utils.disp_der_from_vault('tst-apim-1054042BB0D700000.pem')
    print("********************")
    #Utils.disp_der_from_vault('tst-apim-1054042BB0D700000.pem.bak')
    Utils.disp_der_from_vault('tst-apim-1054042BB0D700000.chain.pem')
    print("********************")

    print(f'Diff was: {Utils.diff_vs_vault("tst-apim1054042BB0D700000.pem","xssxs",save=False)}')

    print(f'Diff was: {Utils.diff_vs_vault("tst-apim1054042BB0D700000.pem","",save=False)}')





    #
    # import time


    # for i in range(10):
    #     Utils._vault.put_secret(f"Test_{i}.nada",f"Bogus Data{i+121}")
    #     if Utils._vault.get_secret(f"Test_{i}.nada") == f"Bogus Data{i+121}":
    #         print(f"check: {i}")
    #         time.sleep(1)

    #     Utils._vault.remove_secret(f"Test_{i}.nada")
