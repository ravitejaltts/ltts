"""
    Class and methods to setup the IOT using calls to the platform
"""
from iot_service.platform_api import PlatformApi
from iot_service.utils import Utils, StateLog
import subprocess
from common_libs import environment


_env = environment()


class Provisioning:
    ssl_OK = False

    def __init__(self, api_url: str, iotself) -> None:
        self.iot = iotself
        self.ssl_OK = self.get_ssl_version()
        self.api = PlatformApi(api_url, iotself)

    def get_ssl_version(self):
        cmd1 = f"openssl version"
        process = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE)
        process.wait()
        result = False
        output = process.communicate()
        if "OpenSSL 3" in str(output[0]):
            # print('SSL OK to use')
            result = True
        else:
            Utils.pushLog(f"Wrong SSL {result}")
        return result

    def provision_device(self, vin: str, device_id: str):
        result = False
        if self.ssl_OK:
            try:
                if vin is not None and len(vin) == 17:
                    Utils.pushLog(f"create_csr calling with {vin} {device_id}")
                    csr_result = Utils.create_csr(vin, device_id)
                    """
                        Platform API Call
                    """
                    self.api.register_and_retrieve_certificate(vin, device_id=device_id)
                    # self.api.split_pfx(vin)
                    result = True
                else:
                    # Set status - improper VIN found
                    Utils.pushLog(f"VIN: none or wrong length: {vin}", 'error')
            except Exception as err:
                msg = f"VIN {vin} provisioning error {err}"
                Utils.pushLog(msg, "error")
                StateLog.append(msg)

        return result


if __name__ == '__main__':
    import logging

    # Create a logger
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)

    # Create a stream handler to send log messages to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter to define the log message format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)


    if True: # Split test
        print(f'\n\n Test starting - Split Key \n')
        my_provisioner = Provisioning(tst_api_url, "xxvin", logger)

        test_vin = "1054042BB00700000"
        test_dev_id = "1054042BB007-0000"

        my_provisioner.api.split_pfx(test_dev_id)


    else: # Provision finder test
        print(f'\n\n Test starting - api provisioning \n')

        my_provisioner = Provisioning(dev_api_url, logger)

        urls = [prod_api_url, tst_api_url, dev_api_url]

        test_vin = "1054042BB00500000"
        #test_vin = "1FTBW1XK2NKA46851"

        for api_url in urls:
            print('\n',api_url,'\n')
            my_provisioner.api.set_api(api_url)
            try:
                result = my_provisioner.api.get_device_info(vin=test_vin,cert_path=None)
                if result.success:
                    print('\n', result.__dict__())
                break
            except Exception as err:
                print('\n', err, '\n')
