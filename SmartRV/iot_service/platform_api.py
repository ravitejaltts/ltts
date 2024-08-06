import requests, json
from iot_service.models.registration_info_response import RegistrationInfoResponse
from iot_service.models.registration_response import RegistrationResponse
import subprocess, base64, sys, os
from common_libs import environment
from common_libs.clients import IOT_CLIENT
from iot_service.utils import Utils, MIN_LENGTH, Iot_Status
from urllib.parse import urlparse
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    NoEncryption,
)
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    load_key_and_certificates,
    serialize_key_and_certificates
)
from cryptography.hazmat.backends import default_backend
from datetime import datetime

_env = environment()

class PlatformApi:
    api_uri: str
    """The URI used to talk to the platform"""

    def __init__(self, api_url: str, i_iot):
        """
        `api_url` - The URL to talk to the platform API
        """
        self.api_url = api_url
        self.iot = i_iot
        # if len(api_url) >= MIN_LENGTH:
        #     parsed_url = urlparse(api_url)
        #     self.platform_env = parsed_url.hostname.split(".")[0]
        # else:
        #     self.platform_env = None
        self.key1 = None
        self.output_cert_path = None
        self.vin = None

    def set_api(self, api_url: str):
        self.api_url = api_url
        # if len(api_url) >= MIN_LENGTH:
        #     parsed_url = urlparse(api_url)
        #     self.platform_env = parsed_url.hostname.split(".")[0]

    def get_device_info(self, vin: str) -> RegistrationInfoResponse:
        """
        Gets information about a device based on its vin
        """
        Utils.pushLog(f"Called get_device_info with {vin} ")
        self.vin = vin
        if self.iot.platform_env() is None:
            return None
        try:
            # print(f"get_device_info get_our_pem {cert_path}")
            installation_certificate = self.get_our_pem(f"{self.iot.platform_env()}-{vin}", newOK=True)
            if installation_certificate is None:
                installation_certificate = self.get_our_pem(f"{self.iot.platform_env()}-{vin}")
        except Exception as err:
            Utils.pushLog(f"ERROR get_device_info cert: {err} ")
            try:
                installation_certificate = Utils.load_device_cert_file(None, self.iot.platform_env())
            except Exception as err:
                Utils.pushLog(f"get_device_info 1 err: {err}")
                return None

        if installation_certificate is not None:
            path = "registrations"
            query = {"vin": vin}
            headers = {"Device-Certificate": installation_certificate}
            Utils.pushLog(f"\nget_device_info {self.api_url}/{path} query {query}\n")

            response = requests.get(
                f"{self.api_url}/{path}", params=query, headers=headers
            )
            if response.status_code != 200:
                raise Exception(
                    f"\n\nHTTP Code - {response.status_code}:\n{json.dumps(response.json(), indent=2)}\n\n"
                )
            try:
                # TODO: rename if we got it using 'new cert'
                response_dict = response.json()
                result = RegistrationInfoResponse(response_dict)
                Utils.pushLog(f"\nRegistration Info reponse: {result}\n")
            except Exception as err:
                Utils.pushLog(f"get_device_info 2 err {err}")
                return None

            return result
        else:
            return None


    def register_and_retrieve_certificate(self, vin: str, device_id: str) -> RegistrationResponse:
        """
        Registers a new device to the platform using the vin and CSR.a `Certificate` should be the installation certificate or an existing device certificate
        """
        Utils.pushLog(f"register_and_retrieve_certificate called with vin {vin} id {device_id}")

        installation_certificate = self.get_our_pem(f"{self.iot.platform_env()}-{vin}", newOK=True)

        if installation_certificate is None:
            raise Exception(f"\n\nNo Certs for: {vin}\n\n")
        try:
            csr = Utils.load_csr_file(vin=vin, dev_id=device_id)
            if csr is None:
                # Failed we should have this
                raise Exception(f"\n\nNo CSR found for: {vin}\n\n")

            path = "registrations/register"
            body = {
                "vin": vin,
                "csr": csr,
            }
            tcu = self.iot.tcu()
            if tcu is not None:
                body["attributes"] = dict(tcu)
                Utils.pushLog(
                f"register_and_retrieve_certificate Adding attributes: {dict(tcu)} "
            )

            headers = {
                "Content-Type": "application/json",
                "Device-Certificate": installation_certificate,
            }
            # msg = f"register_and_retrieve_certificate Body: {body} "
            # print(msg)
            # Utils.pushLog(msg)

            response = requests.patch(
                f"{self.api_url}/{path}", json.dumps(body), headers=headers
            )
        except Exception as err:
            Utils.pushLog(
                f"register_and_retrieve_certificate ERROR: {err} "
            )

        if response.status_code != 200:
            Utils.pushLog(
                f"register_and_retrieve_certificate - {response.status_code} PATCH ERROR {response.json()} "
            )
            raise Exception(f"\n\nHTTP Code - {response.status_code}:\n")
        else:
            Utils.pushLog(f"register_and_retrieve_certificate 200: ts: {datetime.now()}")

        response_dict = response.json()

        result = RegistrationResponse(response_dict)
        # print(f"registration response: {result.__dict__()}")

        # self.output_cert_path = _env.certs_path(f"{vin}-0000.pub.pfx")
        """  pfx_name = f"{self.iot.platform_env()}-{vin}.pub.pfx"
        self.output_cert_path = _env.certs_path(pfx_name)
        with open(self.output_cert_path, "wb") as cert_file:
            out = base64.b64decode(result.certificate)
            cert_file.write(out) """
        if result.success is True:
            if self.move_pfx(result.certificate, self.iot.platform_env(), vin, device_id) is True:
                self.iot.update_status(Iot_Status.DPS_PROVISIONING, "The device was able to get pfx and certs!")
            else:
                self.iot.update_status(Iot_Status.DPS_CERTS_MISSING, "The register PATCH was missing the pfx!")

            self.device_id = result.device_id
            #Utils.pushLog(f"Certificate saved to: {self.output_cert_path}")
            Utils.pushLog(f"Device Id: {result.device_id}")
            Utils.pushLog(f"DPS Host: {result.dps_host}")
            Utils.pushLog(f"DPS Scope: {result.dps_scope}")
        else:
            Utils.pushLog(f"register patch fail: {result.device_id}")
            raise ValueError


    """
    openssl pkcs12 -export -in $1.pub.pfx -inkey $1.key -out $1.pfx -nodes # Create Full PFX Bundle (w/ private keys)
    openssl pkcs12 -in $1.pfx -out $1.pem -clcerts -nodes -nokeys # Just leaf certificates (used in platform api calls and iot hub connection)
    openssl pkcs12 -in $1.pfx -out $1.chain.pem -nodes -nokeys # Leaf certificate + chain. Used for DPS provision step.
    """

    def print_cert(self, certificate):
        # Print various details from the certificate
        print("Subject:", certificate.subject)
        print("Issuer:", certificate.issuer)
        print("Validity Period:")
        print(" - Not Before:", certificate.not_valid_before, " - Not After:", certificate.not_valid_after)
        # print("Public Key:")
        # print(certificate.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode())


    def move_pfx(self, pfx_cert: None, env, vin, dev_id, device_env: bool = False):
        '''Testing function to verify against existing certs
        '''
        result = False  # Cert was new
        try:
            if pfx_cert is None:
                Utils.pushLog(f"move_pfx is NONE", "error")
                return False
            # Extract certificates (the password is None since the PFX file is not password-protected)
            (
                none_key,  # Function needs this but we don't expect it
                main_certificate,
                additional_certificates,
            ) = load_key_and_certificates(
                base64.b64decode(pfx_cert), password=None, backend=default_backend()
            )
            main_cert_is_first = False
            # certificate in PEM format
            if main_certificate:
                # Check is this a new cert?
                name = f"{env}-{vin}.pem"
                new_cert = main_certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
                if dev_id in new_cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value:
                    main_cert_is_first = True
                    if Utils.diff_vs_vault(name, new_cert) is False:
                        # print(main_certificate.public_bytes(serialization.Encoding.PEM))
                        self.iot.cert_update_in_progress = True  # New cert saved
                    else:
                        print(f'Already had this env pem: {name}')
                    result = True
                else:
                    print("Main cert was not device!")
            else:
                if additional_certificates:
                    client_certificate = additional_certificates[0]
                    # Save the client certificate to a file in PEM format
                    if device_env is True: # Environement Cert
                        cname = f"{env}-env.raw"
                        value=client_certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
                        if Utils.diff_vs_vault(cname, value) is True:
                            print(f'Already had this raw secret: {cname}')
                        Utils.check_if_installation_cert(cname)

                    else:  # Device Cert
                        value = client_certificate.public_bytes(serialization.Encoding.PEM).decode('utf-8')
                        name = f"{env}-{vin}.pem"
                        print(f'Trying to check: {name}  {client_certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value}')
                        if dev_id in client_certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value:
                            print("Additional[0] cert WAS device!")
                            main_cert_is_first = True
                            if Utils.diff_vs_vault(name, value) is False:
                                self.iot.cert_update_in_progress = True  # New cert saved
                            else:
                                print(f'Already had this dev cert: {name}')
                        else:
                            print("Additional[0] cert was not device!")

                    result = True

            # TODO: Add this to BlueTooth in vault fetch
            # Save the certificate chain (if any) in PEM format
            # if additional_certificates is not None and device_env is False:

            #     env_certificate = additional_certificates[-2]
            #     # Save the env public certificate to a file in PEM format
            #     name = 'env_pub.pem'
            #     value = env_certificate.public_key().public_bytes(
            #                     serialization.Encoding.PEM,
            #                     serialization.PublicFormat.SubjectPublicKeyInfo,
            #                 ).decode('utf-8')

            #     if "WinnConnect-Intermediate" in cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value:
            #         if "WinnConnect-Root" in cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value:
            #             if Utils.diff_vs_vault(name, value) is True:
            #                 Utils.pushLog(f'Already had this pub pem:  {name}.')

            if device_env is False:
                try:
                    # Save the certificate in PEM format
                    if additional_certificates:
                        cnt = 0
                        for cert in additional_certificates:
                            print(f"Cert number: {cnt} ****************  {cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value}  *****\n")
                            self.print_cert(cert)
                            # Subject: <Name(CN=7054042BB007-0001)>
                            if dev_id in cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value:
                                ### This is the device cert
                                name = f"{env}-{vin}.pem"
                                print("Device cert identified:", name)
                                value=cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')
                                if Utils.diff_vs_vault(name, value) is False:
                                    # print(main_certificate.public_bytes(serialization.Encoding.PEM))
                                    self.iot.cert_update_in_progress = True  # New cert saved
                                else:
                                    print(f'Already had this device pem: {name}')
                            elif "WinnConnect-Intermediate" in cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value:
                                if "WinnConnect-Root" in cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value:
                                    name = 'env_pub.pem'
                                    print("Env cert identified:", name)
                                    value = cert.public_key().public_bytes(
                                         serialization.Encoding.PEM,
                                         serialization.PublicFormat.SubjectPublicKeyInfo,
                                         ).decode('utf-8')
                                    if Utils.diff_vs_vault(name, value) is True:
                                        Utils.pushLog(f'Already had this pub pem:  {name}.')

                    else:
                        print("Main cert only - no additional certs found!")
                except Exception as err:
                    print(f"show additional err: {err}")



                buffer = b""
                if main_cert_is_first is True:
                    if main_certificate:
                        buffer = main_certificate.public_bytes(serialization.Encoding.PEM)
                    for cert in additional_certificates:
                        buffer += cert.public_bytes(serialization.Encoding.PEM)
                else:
                    for cert in reversed(additional_certificates):
                        buffer += cert.public_bytes(serialization.Encoding.PEM)
                    if main_certificate:
                        buffer += main_certificate.public_bytes(serialization.Encoding.PEM)
                # Write the certificates to the PEM file
                Utils.put_secret(f"{env}-{vin}.chain.pem", buffer.decode('utf-8'))
                result = True

            return result
        except Exception as err:
            Utils.pushLog(f"move_pfx {err}", "error")
            raise err


    def get_our_pem(self, name: str, newOK: bool = False) -> str:
        # Try for our device id or use installation.pem
        if newOK is True and self.iot.use_bak_certs is False:
            cert_file = f"{name}.pem"
        else:
            cert_file = f"{name}.pem.bak"

        cert_data = Utils.load_device_cert_file(cert_file, self.iot.platform_env())
        if cert_data is None:
            Utils.pushLog("get_our_pem not found including installation.pem", "error")

        return cert_data


    async def get_weather_forcast(self):
        Utils.pushLog("get_weather_forcast called.")

        installation_certificate = self.get_our_pem(f"{self.iot.platform_env()}-{self.vin}", newOK=True)

        if installation_certificate is None:
            raise Exception(f"\n\nNo Cert for: {self.vin}\n\n")
        try:

            path = self.api_url.replace("devices", "weather/weather")

            Utils.pushLog(
                f"get_weather_forcast path: {path} ts: {datetime.now()}"
            )

            headers = {
                "Content-Type": "application/json",
                "Device-Certificate": installation_certificate,
            }
            self.iot.iot_telemetry.get_fresh_gps()

            if self.iot.iot_telemetry.iot_position is None or self.iot.iot_telemetry.iot_position == "NA":
                 Utils.pushLog(f"get_weather_forcast failed for position: NA ")
                 return {}
            else:
                if self.iot.iot_telemetry.usrOptIn is True:
                    print(f"usrOptIn: {self.iot.iot_telemetry.usrOptIn}, Position: {self.iot.iot_telemetry.iot_position}")
                else:
                    return {"usrOptIn": False}

            # TODO: Check if this is awaitable
            self.iot.iot_telemetry.get_fresh_gps()

            current_p = self.iot.iot_telemetry.iot_position
            lat_str, lng_str = current_p.split(',')

            if current_p is None or float(lat_str) == 0.0 or float(lng_str) == 0:
                # We must have a valid lat long , neither should be 0
                Utils.pushLog(
                f"get_weather_forcast failed for position: {current_p} "
            )
                return {}

            params={'lat': float(lat_str),
                    'lng': float(lng_str),
                    'current': True,
                    'alerts': True,
                    'forecastDays': 3,
                    'forecastHours': 8}

            response = await IOT_CLIENT.get(
                path,
                params=params,
                headers=headers,
                timeout=15,  # Seconds timeout
            )
        except Exception as err:
            Utils.pushLog(
                f"get_weather_forcast ERROR: {err} "
            )
            raise err

        if response.status_code != 200:
            Utils.pushLog(
                f"get_weather_forcast - {response.status_code} GET ERROR {response.json()} "
            )
            Utils.pushLog(
                f"get_weather_forcast failed -path {path} parameters {params} ts: {datetime.now()}"
            )
            raise Exception(f"\n\nHTTP Code - {response.status_code}:\n")
        else:
            Utils.pushLog(f"get_weather_forcast 200: ts: parameters {params} ts: {datetime.now()}")

        response_dict = response.json()
        print(response_dict)

        # Now call back to Main + api/wx/1/report
        try:
            apiResponse = await IOT_CLIENT.put(
                self.iot.iot_telemetry.baseUrl + "/api/features/wx/1/report", data=response.content
            )
            Utils.pushLog(f"weather report sent to main {apiResponse}")
            events = json.loads(apiResponse.text)
        except Exception as err:
            # logger.error(repr(err))
            # Utils.pushLog(f'send_events_to_main_service err: {repr(err)}')
            Utils.pushLog(f'send_weather_to_main_service err: {err}')

        return  # Not much to return - this is run as a task

    def post_alert_register(self):
        Utils.pushLog("post_alert_register called.")

        installation_certificate = self.get_our_pem(f"{self.iot.platform_env()}-{self.vin}", newOK=True)

        if installation_certificate is None:
            raise Exception(f"\n\nNo Cert for: {self.vin}\n\n")
        try:

            path = self.api_url.replace("devices", "weather/alert/subscriptions")

            headers = {
                "Content-Type": "application/json",
                "Device-Certificate": installation_certificate,
            }
            self.iot.iot_telemetry.get_fresh_gps()

            current_p = self.iot.iot_telemetry.iot_position
            lat_str, lng_str = current_p.split(',')

            Utils.pushLog(
                f"get_weather_forcast for location: {current_p} "
            )

            if current_p is None or float(lat_str) == 0.0 or float(lng_str) == 0:
                # We must have a valid lat long , neither should be 0
                Utils.pushLog(
                f"post_alert_register failed for position: {current_p} "
            )
                return {"post_alert_register failed for position: {current_p} "}

            params={'lat': float(lat_str), 'lng': float(lng_str)}

            response = requests.post(
                path, params=params, headers=headers
            )
        except Exception as err:
            Utils.pushLog(
                f"post_alert_register ERROR: {err} "
            )
            return {}

        if response.status_code != 200:
            Utils.pushLog(
                f"post_alert_register - {response.status_code} GET ERROR {response.json()} "
            )
            if  response.status_code == 500:
                return {"Result": "Cloud Server Error"}
            else:
                raise Exception(f"\n\nHTTP Code - {response.status_code}:\n")
        else:
            Utils.pushLog(f"post_alert_register 200: ts: {datetime.now()}")

        response_dict = response.json()
        print(response_dict)
        return response_dict


if __name__ == "__main__":
    import time

    desired = "1054042BB0D700000"

    def print_cert(certificate):
        # Print various details from the certificate
        print("Subject:", certificate.subject)
        print("Issuer:", certificate.issuer)
        print("Serial Number:", certificate.serial_number)
        print("Validity Period:")
        print(" - Not Before:", certificate.not_valid_before)
        print(" - Not After:", certificate.not_valid_after)
        print("Public Key:")
        print(certificate.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode())


    def disp_cert_from_vault(name1):
        if Utils.has_secret(name1) is True :
            #pem_cert_data = "-----BEGIN CERTIFICATE-----\n"
            s1 =  Utils.get_secret(name1)
            #pem_cert_data += base64.b64encode(s1).decode('ascii')
            #pem_cert_data += "\n-----END CERTIFICATE-----\n"
            #try:
            certificate = x509.load_pem_x509_certificate(s1)
            # Display the contents of the certificate
            print_cert(certificate=certificate)
        else:
            print(f"Secret not found {name1} {Utils.has_secret(name1)}")

    disp_cert_from_vault(name1="dev-apim-1054042BB0D700000.pem.bak")


    def move_pfx(pfx_cert: None, env, vin, device_env: bool = False):
        '''Testing function to verify against existing certs
        '''
        try:
            if pfx_cert is None:
                Utils.pushLog(f"move_pfx is NONE", "error")
                return False
            # Extract certificates (the password is None since the PFX file is not password-protected)
            (
                none_key,  # Function needs this but we don't expect it
                main_certificate,
                additional_certificates,
            ) = load_key_and_certificates(
                base64.b64decode(pfx_cert), password=None, backend=default_backend()
            )
            try:
                # Save the certificate in PEM format
                if additional_certificates:
                    cnt = 0
                    for cert in additional_certificates:
                        print(f"Cert number: {cnt} *********************\n")
                        print_cert(cert)
                        cnt += 1
                else:
                    print("Main cert only - no additional certs found!")
            except Exception as err:
                print(f"show additional err: {err}")

            if main_certificate:
                print(main_certificate.public_bytes(serialization.Encoding.PEM))
                Utils.put_secret(
                    name=f"{env}-{vin}.pem",
                    value=main_certificate.public_bytes(serialization.Encoding.PEM),
                )
            else:
                if additional_certificates:
                    # cnt = 0
                    # for cert in additional_certificates:
                    #     print(f"Cert number: {cnt} *********************\n")
                    #     print_cert(cert)
                    #     cnt += 1

                    client_certificate = additional_certificates[0]
                    # Save the client certificate to a file in PEM format
                    Utils.put_secret(
                        name=f"{env}-{vin}.pem",
                        value=client_certificate.public_bytes(serialization.Encoding.PEM),
                        )
                    #print_cert(client_certificate)

            # Save the certificate chain (if any) in PEM format
            if additional_certificates is not None and device_env is False:
                env_certificate = additional_certificates[-2]
                # Save the env public certificate to a file in PEM format
                name = 'env_pub.pem'
                value = env_certificate.public_key().public_bytes(
                                serialization.Encoding.PEM,
                                serialization.PublicFormat.SubjectPublicKeyInfo,
                            )
                if Utils.diff_vs_vault(name, value) is True:
                    Utils.pushLog(f'Already had this secret:  {name}.')
                #print_cert(env_certificate)

            if device_env is False:
                buffer = b""
                if main_certificate:
                        buffer = main_certificate.public_bytes(serialization.Encoding.PEM)
                for cert in additional_certificates:
                        buffer += cert.public_bytes(serialization.Encoding.PEM)
                # Write the certificates to the PEM file
                Utils.put_secret(f"{env}-{vin}.chain.pem", buffer.decode('utf-8')
                )


            return True
        except Exception as err:
            Utils.pushLog(f"move_pfx {err}", "error")
            Utils.checkCerts()
            self.use_bak_certs = True
            raise err

    s1 =  Utils.get_secret("tst-apim-env.newraw")
    print(f"move returned: {move_pfx(s1,'tstraw', 101, True)}")


    # def move_pfx(pfx_cert: None, env, vin):
    #     '''Testing function to verify against existing certs
    #     '''
    #     # Extract certificates (the password is None since the PFX file is not password-protected)
    #     (
    #         none_key,  # Function needs this but we don't expect it
    #         main_certificate,
    #         additional_certificates,
    #     ) = load_key_and_certificates(
    #         pfx_cert, password=None, backend=default_backend()
    #     )

    #     # Save the certificate in PEM format
    #     if main_certificate:
    #         print(main_certificate.public_bytes(serialization.Encoding.PEM))
    #         Utils.put_secret(
    #             name=f"{env}-{vin}.pem",
    #             value=main_certificate.public_bytes(serialization.Encoding.PEM),
    #         )
    #     else:
    #         if additional_certificates:
    #             client_certificate = additional_certificates[0]
    #             # Save the client certificate to a file in PEM format
    #             Utils.put_secret(
    #                 name=f"{env}-{vin}.pem",
    #                 value=client_certificate.public_bytes(serialization.Encoding.PEM),
    #                 )
    #             #print_cert(client_certificate)

    #     # Save the certificate chain (if any) in PEM format
    #     if additional_certificates:
    #         env_certificate = additional_certificates[-2]
    #         # Save the env public certificate to a file in PEM format
    #         with open('_env.certs_path("env_pub.pem")', "w") as cert_file:
    #             cert_file.write(
    #                 env_certificate.public_key()
    #                 .public_bytes(
    #                     serialization.Encoding.PEM,
    #                     serialization.PublicFormat.SubjectPublicKeyInfo,
    #                 )
    #                 .
    #             )
    #         #print_cert(env_certificate)


    #     buffer = b""
    #     if main_certificate:
    #             buffer = main_certificate.public_bytes(serialization.Encoding.PEM)
    #     for cert in additional_certificates:
    #             buffer += cert.public_bytes(serialization.Encoding.PEM)
    #     # Write the certificates to the PEM file
    #     Utils.put_secret(f"{env}-{vin}.chain.pem", buffer.decode('utf-8')
    #     )

    #     return

    # Load the PFX file

    # pfx_desired = f"/storage/wgo/certs-nov17-am/dev-apim-1054042BB0D700000.pub.pfx"
    # #certPath = _env.certs_path(pfx_desired)


    # # Convert from DER to PEM format
    # pem_cert_data = "-----BEGIN CERTIFICATE-----\n"
    # with open(pfx_desired, "rb") as cert_file:
    #     pfx_cert = cert_file.read()
    #     pem_cert_data += base64.b64encode(pfx_cert).decode('ascii')
    # pem_cert_data += "\n-----END CERTIFICATE-----\n"

    # print(pem_cert_data)

    #move_provisioning_pfx(pem_cert_data, "tst-apim", "1054042BB0D700000")


    #pfx_data = move_pfx(pfx_cert, "dev-apim", desired)

"""
    # Extract certificates (the password is None since the PFX file is not password-protected)
    private_key, main_certificate, additional_certificates = load_key_and_certificates(
        pfx_data, password=None, backend=default_backend()
    )

    # Save the certificate in PEM format
    if main_certificate:
        cert_path = 'certificate.pem'
        print(main_certificate.public_bytes(serialization.Encoding.PEM))

    # Save the certificate chain (if any) in PEM format
    if additional_certificates:

        for i, certificate in enumerate(additional_certificates):

            # Print various details from the certificate
            print("Subject:", certificate.subject)
            print("Issuer:", certificate.issuer)
            print("Serial Number:", certificate.serial_number)
            print("Validity Period:")
            print(" - Not Before:", certificate.not_valid_before)
            print(" - Not After:", certificate.not_valid_after)
            print("Public Key:")
            print(certificate.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).)


        env_certificate = additional_certificates[-2]

        # Save the last certificate to a file in PEM format
        with open('/storage/wgo/certs/env_pub_t.pem', 'w') as cert_file:
            cert_file.write(env_certificate.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).)
 """


# openssl x509 -pubkey -noout -in my-env.pem  > env_pub.pem

# try:
#     my_key = Utils.get_secret(desired)
# except Exception as err:
#     print(f"my_key err: {err}")
#     try:
#         certPath = _env.certs_path(desired)
#         with open(certPath) as cert_file:
#             my_key_value = cert_file.read()
#         Utils.put_secret(name=desired, value=my_key_value)
#     except Exception as err:
#         print(f"my_key path err: {err}")
#         # need to generate
#         # my_key = PKey()
#         # my_key.generate_key(type=TYPE_RSA, bits=4096)
#         # my_key_value = dump_privatekey(type=FILETYPE_PEM, pkey=my_key).decode('utf-8')

#         my_key_value = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=2048,
#             backend=default_backend()
#         )

#         Utils.put_secret(name=desired, value=my_key_value.private_bytes(
#                 encoding=Encoding.PEM,
#                 format=PrivateFormat.PKCS8,
#                 encryption_algorithm=NoEncryption()
#             ).decode('utf-8'))

"""

    testPlatform = PlatformApi(api_url="https://dev-apim.azure.dev", i_iot=None)

    testPlatform.create_csr(vin=desired, dev_id="1054042BB0D7-0000")
 """


# 'openssl pkcs12 -export -in {input_cert_path} -inkey {key1} -out {output_pfx_path} --passout pass: -passin pass:"" '
