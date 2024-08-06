# https://github.com/PunchThrough/espresso-ble

import logging
import subprocess
import time

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.service
import requests

from bt_service.gatt.ble import (
    Advertisement,
    Characteristic,
    Service,
    Application,
    find_adapter,
    Descriptor,
    Agent,
    GATT_CHRC_IFACE,
    InvalidArgsException
)

import os
import queue
import sys
import threading
from logging.handlers import RotatingFileHandler

from bt_service.bt_helper import validate_signature
# from bt_service.constants import APIMethods
from common_libs.models.common import EventValues
from common_libs import environment
from common_libs.clients import BT_CLIENT
_env = environment()

FARFIELD_API = f'{_env.main_host_uri}:{_env.iot_service_port}/far_field_token'
DEVICEID_API = f'{_env.main_host_uri}:{_env.iot_service_port}/device_id'

MainLoop = None
try:
    from gi.repository import GLib
    MainLoop = GLib.MainLoop
except ImportError:
    import gobject as GObject

    MainLoop = GObject.MainLoop

LOG_MAX_FILE_SIZE = 20000
LOG_BACKUP_FILE_CNT = 1

logger = logging.getLogger('GATT')
# logger.setLevel(logging.DEBUG)
# # logger.setLevel(logging.INFO)
# logHandler = logging.StreamHandler()
# fileLogHandler = RotatingFileHandler(
#       _env.log_file_path('gatt_service.log'),
#       'a+',
#       maxBytes=LOG_MAX_FILE_SIZE,
#       backupCount=LOG_BACKUP_FILE_CNT
#     )
# formatter = logging.Formatter(
#     "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# logHandler.setFormatter(formatter)
# fileLogHandler.setFormatter(formatter)
# logger.addHandler(fileLogHandler)
# logger.addHandler(logHandler)

mainloop = None

response_queue = queue.Queue()

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"
ADAPTER_PATH = 'org.bluez.Adapter1'

MANUFACTURER_NAME = "Winnebago"
MANUFACTURER_NAME_DESC = "MANUFACTURER_NAME"

MODEL_NUMBER = "UNSET"
MODEL_NUMBER_DESC = "MODEL_NUMBER"

SERIAL_NUMBER = "UNSET"
SERIAL_NUMBER_DESC = "SERIAL_NUMBER"

FIRMWARE_VERSION = "UNSET"
FIRMWARE_VERSION_DESC = "FIRMWARE_VERSION"

SOFTWARE_VERSION = "UNSET"
SOFTWARE_VERSION_DESC = "SOFTWARE_VERSION"

HARDWARE_VERSION = "UNSET"
HARDWARE_VERSION_DESC = "HARDWARE_VERSION"

DEVICE_TYPE = "s500"        # TODO: Read from config (model template)
DEVICE_TYPE_DESC = "DEVICE_TYPE"

DEVICE_ID_DESC = 'DEVICE_ID'
DEVICE_ID = 'UNSET'

# BLE_SYSTEM_NAME = "WinnConnect"

RESPONSE_DELAY = 0.001       # Seconds between messages in response

UUID_DEVICE_INFO_DEVICE_TYPE = '46829001-BC2A-48BC-84AF-BA68FC506B6C'
UUID_DEVICE_INFO_DEVICE_ID = '46829002-BC2A-48BC-84AF-BA68FC506B6C'

UUID_SECURITY_REQUEST = '46829A01-BC2A-48BC-84AF-BA68FC506B6C'
UUID_SECURITY_RESPONSE = '46829A02-BC2A-48BC-84AF-BA68FC506B6C'

UUID_API_REQUEST = '46829A01-BC2A-48BC-84AF-BA68FC506B6C'
UUID_API_RESPONSE = '46829A02-BC2A-48BC-84AF-BA68FC506B6C'
UUID_STATE_UPDATE = '46829A03-BC2A-48BC-84AF-BA68FC506B6C'

UUID_LIGHTING_SERVICE = '468299FF-BC2A-48BC-84AF-BA68FC506B6C'
UUID_WATER_SERVICE = '46829921-BC2A-48BC-84AF-BA68FC506B6C'
UUID_CLIMATE_SERVICE = '46829923-BC2A-48BC-84AF-BA68FC506B6C'
UUID_ENERGY_SERVICE = '46829920-BC2A-48BC-84AF-BA68FC506B6C'
UUID_SECURITY_SERVICE = '46829900-BC2A-48BC-84AF-BA68FC506B6C'

UUID_COMBO_SERVICE = '46829969-BC2A-48BC-84AF-BA68FC506B6C'

HEADER_LENGTH = 4       # Bytes
HEADER_DIRECTION = 0x1  # Coach to Mobile
HEADER_ENCRYPTED = 0x2
HEADER_LAST_CHUNK = 0x4

HOME_DIR = os.environ.get('WGO_HOME_DIR', '.')
# STORAGE_PATH = _env._user_storage_path
PUB_KEY_NAME = "env_pub.pem"

FAST_FORWARD_AUTH_FAILED = 0xCA
UNRECOGNIZED_DEVICE = 0x01
IOT_SERVICE_NOT_CONNECTED = 0x02
IOT_SERVICE_FAILURE = 0x03
KEY_NOT_DETECTED_FAILURE = 0x04
UNKOWN_FAILURE = 0xFF

device_list = {}

try:
    BaseUrl = sys.argv[1]
except IndexError:
    BaseUrl = "http://localhost:8000"

HEADER = {
    'SOURCE': 'BLE'
}


def restart_service():
    # TODO: Get this from a variable or find a better way to kill the service
    try:
        requests.put(
            'http://localhost:8000/api/system/ble/restart',
            headers=HEADER,
            timeout=5
        )
    except Exception as err:
        print(err)


class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"


class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"


class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.InvalidValueLength"


class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"


def register_app_cb():
    logger.info("GATT application registered")


def register_app_error_cb(error):
    logger.critical("Failed to register application: " + str(error))
    # TODO: What to do here ? Restart bluetooth ?
    try:
        mainloop.quit()
    except AttributeError as err:
        logger.error(f'Cannot quit mainloop as it never initialized: {err}')
        sys.exit(101)


def get_bytes(arr: dbus.Array):
    return bytes(arr)


def _decodeApiRequest(data: bytes, correlation_id: int):
    # TODO: Remove after test is successful
    # requestId = data[0]
    # method = data[1]
    method = data[0]

    url = ""
    urlStart = 3
    # TODO: Conver to the proper int from bytes with little endian
    urlLength = (data[2] << 8) + data[1]

    if urlLength > 0:
        url = bytes(data[urlStart:urlStart+urlLength]).decode("utf-8")

    print('URL', url, flush=True)
    # logging.debug(f'API URL Requested: {url}')

    body = []
    bodyStart = urlStart + urlLength + 2
    if bodyStart < len(data):
        bodyLength = (data[urlStart+urlLength+1] << 8) + \
            data[urlStart+urlLength]
        if bodyLength > 0:
            body = bytes(
                data[bodyStart:bodyStart + bodyLength]
            )

    return ApiRequest(method, url, body)


def _decodeChunkRequest(chunk):
    '''Decode a chunked request into header flags and payload.'''

    # print('Received Chunk', chunk)

    header = _decodeHeader(chunk[0:4])
    payload = chunk[4:]
    is_final = header.get('isFinalChunk') == 1

    # print('Header', header)
    # print('Payload', payload)
    # print('is_final', is_final)

    return header, payload, is_final


def _decode_cert_body(data: bytes):
    '''
    0-7 Exp Date
    8-23 Mobile Device ID
    24-47 Vehicle ID
    48-X Mobile Pub Key
    X-N Signature'''

    exp_date = data[0:8]
    exp_date = int.from_bytes(bytes(exp_date), 'little')

    mobile_device_id = data[8:24]
    mobile_device_id = ''.join([f'{y:02X}' for y in mobile_device_id])

    device_id = data[24:48]
    try:
        bytes(device_id).decode('utf-8')
    except Exception as err:
        print('error', err)
    device_id = ''.join([f'{y:02X}' for y in device_id])

    mobile_pub_key = data[48:80]
    mobile_pub_key = ''.join([f'{y:02X}' for y in mobile_pub_key])

    signature = data[80:]
    signature = ''.join([f'{y:02X}' for y in signature])

    return {
        'expDate': exp_date,
        'mobileDeviceId': mobile_device_id,
        'deviceId': device_id,
        'mobilePubKey': mobile_pub_key,
        'signature': signature,
        'raw_cert': data[0:80],
        'raw_signature': data[80:]

    }


def _decodeHeader(header) -> dict:
    '''Decodes header bytes
    byte0: flags
        b0 : direction
            0: mobile to HMI
            1: HMI to Mobile
        b1 : isBodyEncrypted
            0: False
            1: True
        b2 : isfinalChunk
            0: False
            1: True
        b3-7: reserved
    byte1: correlation id
        Incremental number unique reference for the sender
    byte2-3: Reserved (consider setting FF)
    byte4-: Payload
    '''

    # print('Header', header)
    correlation_id = int(header[1])

    result = {
        'direction': header[0] & 0x01,
        'isBodyEncrypted': (header[0] & 0x02) >> 1,
        'isFinalChunk': (header[0] & 0x04) >> 2,
        'correlationId': correlation_id,
        'reserved': header[2:4]
    }
    return result


def disconnectDevice(device):
    '''Disconnect a given device.'''
    # TODO: Find proper way through adapter / dbus
    # Will not work if the service runs as user and not root/elevated

    mac = device.replace('/org/bluez/hci0/dev_', '').replace('_', ':')
    cmd = f'bluetoothctl disconnect {mac}'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    logger.debug(f'Disconnect result: {result}')


def response_worker(q):
    '''Worker thread to handle respones in the queue.
    Each queue item is expected as a
    tuple/list with function as the first and the argument as the second element.'''
    while True:
        item = q.get()
        logger.debug('Starting queue item')
        # Call function
        func = item[0]
        handler = item[1]
        correlation_id = item[2]
        arg = item[3]
        mtu = item[4]

        func(handler, correlation_id, arg, mtu)
        logger.debug(f'Finished Queue Item')
        q.task_done()


def send_data(handler, correlation_id: int, data, mtu: int) -> bool:
    global HEADER_LAST_CHUNK, HEADER_DIRECTION, HEADER_LENGTH

    if not handler.notifying:
        logger.info(f'Not notifying, suppressing {handler} API response')
        return False

    # TODO: Remove after figuring out proper offset that works
    if mtu > 180:
        mtu = 180

    mtu_real = (mtu - HEADER_LENGTH)
    # logger.debug(f'Read MTU: {mtu} / {mtu_real}')

    if len(data) <= mtu_real:
        header = [
            HEADER_LAST_CHUNK + HEADER_DIRECTION,
            correlation_id,
            0xff,
            0xff
        ]
        response_data = []
        response_data.extend(header)
        response_data.extend(data)

        response_data = dbus.Array(response_data, signature="y")

        print('GATT Response Data', response_data)

        result = handler.PropertiesChanged(
            GATT_CHRC_IFACE,
            {'Value': response_data}, []
        )
        logger.info(f'Single Notification sent with result: {result}')
    else:
        data_buffer = data[:]
        i = 1
        logger.info(f"Sending chunks: {len(data) / mtu_real}")

        while len(data_buffer) > mtu_real:
            chunk = data_buffer[:mtu_real]

            header = [
                HEADER_DIRECTION,
                correlation_id,
                0xff,
                0xff
            ]
            response_data = header[:]
            response_data.extend(chunk)

            response_data = dbus.Array(response_data, signature="y")
            handler.PropertiesChanged(GATT_CHRC_IFACE, {'Value': response_data}, [])
            # logger.info(f'Chunk Notification sent: {i}')
            data_buffer = data_buffer[mtu_real:]
            time.sleep(RESPONSE_DELAY)
            i += 1

        if len(data_buffer) > 0:
            header = [
                HEADER_LAST_CHUNK + HEADER_DIRECTION,
                correlation_id,
                0xff,
                0xff
            ]
            response_data = []
            response_data.extend(header)
            response_data.extend(data_buffer)

            response_data = dbus.Array(response_data, signature="y")
            handler.PropertiesChanged(GATT_CHRC_IFACE, {'Value': response_data}, [])
            logger.info(f"Last Chunk Notification sent with data, MTU: {mtu} / {mtu_real}")
        else:
            # Exact match of mtu, no actual payload
            header = [
                HEADER_LAST_CHUNK + HEADER_DIRECTION,
                correlation_id,
                0xff,
                0xff
            ]
            response_data = header[:]

            response_data = dbus.Array(response_data, signature="y")
            handler.PropertiesChanged(GATT_CHRC_IFACE, {'Value': response_data}, [])
            logger.info("Last Chunk Notification sent without data")

    return handler.notifying


def queue_data(handler, correlation_id, data, mtu):
    if not handler.notifying:
        logger.info('Not notifying, suppressing API response')
        return False

    # print('Queuing Response', data)

    response_queue.put(
        (
            send_data,
            handler,
            correlation_id,
            data,
            mtu
        )
    )


class DeviceInfoService(Service):
    """
    Device Info Service that reports information about the device.
    """

    UUID = '180A'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.UUID, True)

        self.add_characteristic(StaticReadCharacteristic(
            bus, 0, self, "00002a29-0000-1000-8000-00805f9b34fb",
            MANUFACTURER_NAME, "MANUFACTURER_NAME"))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 1, self, "00002a24-0000-1000-8000-00805f9b34fb",
            MODEL_NUMBER, "MODEL_NUMBER"))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 2, self, "00002a25-0000-1000-8000-00805f9b34fb",
            SERIAL_NUMBER, "SERIAL_NUMBER"))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 3, self, "00002a27-0000-1000-8000-00805f9b34fb",
            HARDWARE_VERSION, "HARDWARE_VERSION"))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 4, self, "00002a26-0000-1000-8000-00805f9b34fb",
            FIRMWARE_VERSION, "FIRMWARE_VERSION"))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 5, self, "00002a28-0000-1000-8000-00805f9b34fb",
            SOFTWARE_VERSION, "SOFTWARE_VERSION"))
        # self.add_characteristic(StaticReadCharacteristic(
        #     bus, 6, self, "46829001-BC2A-48BC-84AF-BA68FC506B6C",
        #         DEVICE_TYPE, "DEVICE_TYPE"))
        # self.add_characteristic(StaticReadCharacteristic(
        #     bus, 7, self, "46829002-BC2A-48BC-84AF-BA68FC506B6C",
        #         DEVICE_ID, "DEVICE_ID"))


class BleApiService(Service):
    def __init__(self, bus, index, uuid, name):
        Service.__init__(self, bus, index, uuid, True)

        responseCharacteristic = ApiResponseCharacteristic(
            bus,
            1,
            self,
            f'{name} Response Characteristic'
        )

        requestCharacteristic = ApiRequestCharacteristic(
            bus,
            0,
            self,
            responseCharacteristic,
            f'{name} Request Characteristic'
        )

        self.add_characteristic(requestCharacteristic)
        self.add_characteristic(responseCharacteristic)


class BleComboService(Service):
    def __init__(self, bus, index, uuid, name):
        Service.__init__(self, bus, index, uuid, True)

        responseCharacteristic = ApiResponseCharacteristic(
            bus,
            1,
            self,
            f'{name} Response Characteristic'
        )

        stateUpdateCharacteristic = StateUpdateCharacteristic(
            bus,
            2,
            self,
            f'{name} State Update Characteristic'
        )

        requestCharacteristic = ApiRequestCharacteristic(
            bus,
            0,
            self,
            responseCharacteristic,
            f'{name} Request Characteristic'
        )

        self.add_characteristic(requestCharacteristic)
        self.add_characteristic(responseCharacteristic)
        self.add_characteristic(stateUpdateCharacteristic)


class BleSecurityService(Service):
    def __init__(self, bus, index, uuid, name, cfg={}):
        Service.__init__(self, bus, index, uuid, True)
        global DEVICE_TYPE, BT_CONFIG, DEVICE_ID
        # TODO: Add the below
        # Receive 46829A01-BC2A-48BC-84AF-BA68FC506B6C
        # Transmit 46829A02-BC2A-48BC-84AF-BA68FC506B6C

        self.last_pairing_status = ''

        device_id = cfg.get('DEVICE_ID', DEVICE_ID)
        device_type = cfg.get('DEVICE_TYPE', DEVICE_TYPE)

        # Secret Info types ?

        responseCharacteristic = SecurityResponseCharacteristic(
            bus,
            1,
            self,
            f'{name} Response Characteristic'
        )

        requestCharacteristic = SecurityRequestCharacteristic(
            bus,
            0,
            self,
            responseCharacteristic,
            f'{name} Request Characteristic'
        )

        self.add_characteristic(requestCharacteristic)
        self.add_characteristic(responseCharacteristic)

        self.add_characteristic(
            StaticReadCharacteristic(
                bus,
                2,
                self,
                UUID_DEVICE_INFO_DEVICE_TYPE,
                device_type,
                "DEVICE_TYPE"
            )
        )
        self.add_characteristic(
            StaticReadCharacteristic(
                bus,
                3,
                self,
                UUID_DEVICE_INFO_DEVICE_ID,
                device_id,
                "DEVICE_ID"
            )
        )


class StaticReadCharacteristic(Characteristic):
    def __init__(self, bus, index, service, uuid, stringValue, description=None):
        Characteristic.__init__(
            self, bus, index, uuid, ["read"], service, description
        )

        self.value = stringValue.encode()

    def ReadValue(self, options):
        # NOTE: Doing nothing with options yet
        # dbus.Dictionary({dbus.String('device'): dbus.ObjectPath('/org/bluez/hci0/dev_7E_32_67_4B_14_47', variant_level=1), dbus.String('link'): dbus.String('LE', variant_level=1), dbus.String('mtu'): dbus.UInt16(517, variant_level=1)}, signature=dbus.Signature('sv'))
        # logger.info(f'Options: {options}')
        return self.value


class SecurityResponseCharacteristic(Characteristic):
    global response_queue, UUID_SECURITY_RESPONSE
    UUID = UUID_SECURITY_RESPONSE

    def __init__(self, bus, index, service, description=None):
        Characteristic.__init__(
            self, bus, index, self.UUID, ["notify"], service, description
        )

        self.notifying = False
        self.request_buffer = []
        self.last_request_id = 0

    def StartNotify(self):
        if self.notifying:
            return

        logger.debug("Security - Starting notifications")

        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            return

        logger.debug("Security - Stopping notifications")

        self.notifying = False

        # Check if there are other phones connected or services monitored
        # If not restart service
        # restart_service()

    def _sendSecurityResponse(self, correlation_id, response, mtu, send_data = False):
        '''Prepare response for queuing.'''
        data = []
        code = response.get('code')
        response_data = response.get('data')

        # data.append(code.to_bytes(1, 'little'))
        data.append(code)
        print('Data', data)
        if code == 0xCA or (send_data and response_data is not None):
            if len(response_data) > 0:
                data.extend(response_data)

        queue_data(self, correlation_id, data, mtu)


class SecurityRequestCharacteristic(Characteristic):
    # TODO: - Do we need to lock the device list
    global UUID_SECURITY_REQUEST, device_list
    UUID = UUID_SECURITY_REQUEST

    def __init__(self, bus, index, service, responseCharacteristic: SecurityResponseCharacteristic, description=None):
        Characteristic.__init__(
            self, bus, index, self.UUID, ["write"], service, description
        )
        self.service = service
        self.responseCharacteristic = responseCharacteristic
        self.request_buffer = []
        self.last_request_id = 0
        self.adapter = find_adapter(bus)

    def _decodeSecurityRequest(self, data: bytes, header: bytes):
        '''
            https://dev.azure.com/WGO-Web-Development/Owners%20App/_wiki/wikis/Owners-App.wiki/549/BLE-Messages
        '''
        method = data[0]
        print('Method', method)

        # 0x0A - fastforward
        # 0x00 - initial connection
        # 0x0B - farfield
        if method not in (0x0A, 0x00, 0x0B):
            raise ValueError(f'Method: {method} not supported')

        if method == 0x0B:
            # Proof token request
            mobile_device_id = data[1:16]
            return {
                'method': method,
                'mobileId': mobile_device_id,
            }
        else:
            cert_length = (data[2] << 8) + data[1]
            print('Cert Length', cert_length)

            cert_body = data[3:]

            # TODO: Suspended for further testing
            # if len(cert_body) != cert_length:
            #     raise IndexError(f'Received different length body, expected {cert_length},got {len(cert_body)}')

            print('Cert Body', cert_body)
            logger.debug(f'Cert Body {cert_body}')

            cert = _decode_cert_body(cert_body)
            print('Cert', cert)

            return {
                'method': method,
                'certificateLength': cert_length,
                'certificate': cert
            }

    def WriteValue(self, value, options):
        logger.debug(f'Security Request, {value}, {options}')
        logger.debug(f'{options}')

        mtu = options.get('mtu')
        device = options.get('device')

        logger.debug(f'MTU: {mtu}')
        try:
            data = get_bytes(value)

            logger.debug(data)
            # decode data into header and payload
            # Check if final
            # No -> add to buffer and exit

            header, payload, is_final = _decodeChunkRequest(data)
            logger.debug(f'ChunkDecode: {header}, {payload}, {is_final}')

            correlation_id = header.get('correlationId')

            self.request_buffer.extend(payload)
            if is_final is False:
                return

            try:
                securityRequest = self._decodeSecurityRequest(
                    self.request_buffer[:], header
                )
            except ValueError as err:
                logger.error(f'Error: {err}')
                # Close request and return
                self.request_buffer = []
                return

            logger.debug(f'Security Request: {securityRequest}')
            self.request_buffer = []

            method = securityRequest.get('method')
            return_data = False
            response = None

            if method == 0x0A:
                # Perform Fast forward Auth
                cert = securityRequest.get('certificate')
                certificate = cert.get('raw_cert')
                signature = cert.get('raw_signature')

                logger.debug('BLE FAST FORWARD AUTH')
                logger.debug('Running signature check')
                error = None
                try:
                    # On pass return False
                    validation_result = validate_signature(
                        PUB_KEY_NAME,
                        certificate,
                        signature
                    )
                except FileNotFoundError as err:
                    logger.error(f'Public Key File not found for validation {err}')
                    validation_result = True
                    error = 0x03

                if validation_result is True:
                    logger.debug('Signature check FAILED')
                    if error is None:
                        error = 0x01

                    response = {
                        'code': FAST_FORWARD_AUTH_FAILED,
                        'data': [error,]
                    }
                    device_list[device] = False
                else:
                    logger.debug('Signature check PASSED')
                    # Passing signature check result
                    response = {
                        'code': 0x4A
                    }
                    device_list[device] = True
                    logger.debug(f'Adding device: {device}')

            elif method == 0x0B:
                # Proof token request
                logger.debug('[BLE][FARFIELD][PAIRING] BLE PROOF TOKEN REQUEST')
                if device_list[device]:
                    mobile_device_id = securityRequest.get('mobileId')
                    logger.debug(f'[BLE][FARFIELD][PAIRING] Proof token request from device {mobile_device_id}')
                    # get token from IOT
                    try:
                        # TODO: Make this stuff async
                        farfield_response = requests.get(FARFIELD_API, timeout=4)
                        logger.debug(f'[BLE][FARFIELD][PAIRING] Farfield response status code: {farfield_response.status_code} / {type(farfield_response.status_code)}')
                        if farfield_response.status_code != 200:
                            logger.debug(f'[BLE][FARFIELD][PAIRING] Handling Farfield response code {farfield_response.status_code}')
                            failure_string = bytearray(bytes(str(farfield_response.status_code).encode('utf8')))
                            data = [IOT_SERVICE_FAILURE, ]
                            data.extend(failure_string)
                            if farfield_response.status_code == 503:
                                logger.debug('Handling Farfield response 503')
                                response = {
                                    'code': FAST_FORWARD_AUTH_FAILED,
                                    'data': [IOT_SERVICE_NOT_CONNECTED, ]
                                }
                                return_data = True
                            else:
                                logger.debug(f'Handling Farfield response {farfield_response.status_code}')
                                response = {
                                    'code': FAST_FORWARD_AUTH_FAILED,
                                    'data': data
                                }
                                return_data = True
                        else:
                            print('[BLE][FARFIELD][PAIRING] Farfield_response 200 Handling', farfield_response)
                            logger.debug(f'[BLE][FARFIELD][PAIRING] Farfield_response {farfield_response.json()}')
                            data = []
                            token = farfield_response.json().get('proofToken')
                            if EventValues.FAR_FIELD_LOCK == token:
                                response = {
                                    'code': FAST_FORWARD_AUTH_FAILED,   # TODO: Clarify if we want a seperate failure code
                                    'data': [KEY_NOT_DETECTED_FAILURE, ]
                                }
                                return_data = True
                            else:
                                # This is the SUCCESS
                                length = len(token)
                                data.extend(length.to_bytes(2, 'little'))
                                data.extend(map(ord, token))
                                response = {
                                    'code': 0x4A,
                                    'data': data
                                }
                                return_data = True
                    except Exception as err:
                        print('[BLE][FARFIELD][PAIRING] Farfield token fetch fail', err)
                        logger.error(f'[BLE][FARFIELD][PAIRING] Farfield token fetch fail {err}')
                        error_details = [x for x in str(err)]
                        data = [UNKOWN_FAILURE, ]
                        data.extend(error_details)
                        response = {
                            'code': FAST_FORWARD_AUTH_FAILED,
                            'data': data
                        }
                        return_data = True
                else:
                    logger.debug('[BLE][FARFIELD][PAIRING] Unknown device trying to far field pair')
                    response = {
                        'code': FAST_FORWARD_AUTH_FAILED,
                        'data': [UNRECOGNIZED_DEVICE, ]
                    }

            else:
                logger.error(f'Method error: {method}')
                response = {
                    'code': FAST_FORWARD_AUTH_FAILED,
                    'data': [UNRECOGNIZED_DEVICE, ]
                }
                device_list[device] = False

            # Store last pairing response
            self.service.last_pairing_status = str(response)

            logger.debug(f'Security Response: {correlation_id}, {response}, {mtu}, {return_data}')
            self.responseCharacteristic._sendSecurityResponse(
                correlation_id, response, mtu, return_data)

            if device_list[device] is False:
                # Disconnect
                logger.debug(f'Disconnecting {dir(self)}')
                try:
                    disconnectDevice(device)
                except Exception as err:
                    logger.error(f'{err}')

        except Exception as err:
            logger.error(repr(err))


class ApiRequest:
    def __init__(self, method, url, body):
        self.method = method
        self.url = url
        self.body = body


class ApiFailure:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content


class SecurityRequest:
    def __init__(self, method, url, body):
        self.method = method
        self.url = url
        self.body = body


class ApiResponseCharacteristic(Characteristic):
    global response_queue, UUID_API_RESPONSE
    UUID = UUID_API_RESPONSE

    def __init__(self, bus, index, service, description=None):
        Characteristic.__init__(
            self, bus, index, self.UUID, ["notify"], service, description
        )

        self.notifying = False

    def StartNotify(self):
        if self.notifying:
            return

        logger.debug("Starting notifications")

        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            return

        logger.debug("Stopping notifications")

        self.notifying = False

    def _sendApiResponse(self, correlation_id, response: requests.Response, mtu: int):
        try:
            if not self.notifying:
                print('Not notifying, suppressing API response')
                return False

            data = []
            data.extend(response.status_code.to_bytes(2, 'little'))
            data.extend(len(response.content).to_bytes(2, 'little'))
            data.extend(response.content)

            return queue_data(self, correlation_id, data, mtu)
        except Exception as err:
            logger.error(repr(err))

    def _sendApiFailure(self, correlation_id, response: ApiFailure, mtu: int):
        try:
            if not self.notifying:
                print('Not notifying, suppressing API response')
                return False

            data = []
            data.extend(response.status_code.to_bytes(2, 'little'))
            data.extend(len(response.content).to_bytes(2, 'little'))
            data.extend(response.content)

            return queue_data(self, correlation_id, data, mtu)
        except Exception as err:
            logger.error(repr(err))


class StateUpdateCharacteristic(Characteristic):
    global response_queue, UUID_STATE_UPDATE
    UUID = UUID_STATE_UPDATE

    def __init__(self, bus, index, service, description=None):
        Characteristic.__init__(
            self, bus, index, self.UUID, ["notify"], service, description
        )

        self.notifying = False

    def StartNotify(self):
        if self.notifying:
            return

        logger.debug("STATE UPDATE - Starting notifications")

        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            return

        logger.debug("STATE UPDATE - Stopping notifications")

        self.notifying = False

    def _sendApiResponse(self, correlation_id, response: requests.Response, mtu: int):
        try:
            if not self.notifying:
                print('Not notifying, suppressing API response')
                return False

            data = []
            data.extend(response.status_code.to_bytes(2, 'little'))
            data.extend(len(response.content).to_bytes(2, 'little'))
            data.extend(response.content)

            return queue_data(self, correlation_id, data, mtu)
        except Exception as err:
            logger.error(repr(err))


class ApiRequestCharacteristic(Characteristic):
    global UUID_API_REQUEST, device_list
    UUID = UUID_API_REQUEST

    def __init__(self, bus, index, service, responseCharacteristic: ApiResponseCharacteristic, description=None):
        Characteristic.__init__(
            self, bus, index, self.UUID, ["write"], service, description
        )

        self.responseCharacteristic = responseCharacteristic
        self.request_buffer = []

    def WriteValue(self, value, options):
        mtu = options.get('mtu')
        device = options.get('device')

        try:
            data = get_bytes(value)
            # logger.info('Data: ' + repr(data))

            header, payload, is_final = _decodeChunkRequest(data)
            correlation_id = header.get('correlationId')

            known_device = device_list.get(device)
            if known_device is None:
                # Disconnect here as it is not authenticated
                logger.debug(f'Unknown and unauthenticated device found: {device}')
                logger.debug(f'Disconnecting {dir(self)}')
                try:
                    self.responseCharacteristic._sendApiFailure(
                        correlation_id,
                        ApiFailure(401, '{}'),
                        mtu
                    )
                    disconnectDevice(device)
                except Exception as err:
                    logger.error(f'{err}')

                return

            if known_device is False:
                # Device is present but not authenticated
                logger.debug(f'Known device found, but not authenticated: {device}')
                logger.debug(f'Disconnecting {dir(self)}')
                try:
                    self.responseCharacteristic._sendApiFailure(
                        correlation_id,
                        ApiFailure(401, '{}'),
                        mtu
                    )
                    disconnectDevice(device)
                except Exception as err:
                    logger.error(f'{err}')
                return

            elif known_device is True:
                logger.debug(f'Authenticated device found: {device}')
        except Exception as err:
            logger.error(repr(err))
        try:
            data = get_bytes(value)

            # logger.info('Data: ' + repr(data))

            self.request_buffer.extend(payload)
            if is_final is False:
                return

            # logger.debug(f'API Full request: {self.request_buffer}')

            try:
                apiRequest = _decodeApiRequest(self.request_buffer[:], correlation_id)
            except ValueError as err:
                logger.error(f'Received error in decode API: {err}')
                self.request_buffer = []
                # TODO: Respond to error
                return

            if apiRequest.method == 4:
                apiResponse = requests.put(BaseUrl + apiRequest.url, data=apiRequest.body, headers=HEADER, timeout=5)
            else:
                apiResponse = requests.get(BaseUrl + apiRequest.url, headers=HEADER, timeout=5)

            # print('API RESPONSE', apiResponse.status_code, apiResponse.json())

            self.responseCharacteristic._sendApiResponse(
                correlation_id, apiResponse, mtu)
            self.request_buffer = []
        except Exception as err:
            logger.error(repr(err))
            self.request_buffer = []


class WinnConnectAdvertisement(Advertisement):
    def __init__(self, bus, index, vin, master_handle):
        super().__init__(bus, index, "peripheral", master_handle)
        self.add_manufacturer_data(
            0xFFFF, [0x12, 0x34],
        )
        local_name = 'WC-VIN=' + vin.upper()
        logger.debug(f'Local Name: {local_name}')
        self.add_local_name(local_name)
        self.add_service_uuid(DeviceInfoService.UUID)
        self.parent = master_handle

    def release_advertisement(self):
        print('Releasing Advertisement')
        self.is_advertising = False


AGENT_PATH = "/com/winnebago/agent"


class GATTHandler(object):
    def __init__(self, config, logger):
        self.config = {}
        self.logger = logger
        self.init_device(config)

        self.running = False
        self.pairable = False
        self.mainloop = MainLoop()

        self.advertisement = None
        self.bus = None
        self.adapter = None
        self.adapter_obj = None
        self.service_manager = None
        self.ad_manager = None
        self.app = None
        self.vin = self.config.get('VIN', DEVICE_ID)
        self.device_id = self.config.get('DEVICE_ID', DEVICE_ID)
        self.ble_obj = None
        self.is_advertising = False
        self.last_pairing_status = ''

    def init_device(self, config):
        '''Initialize device information like VIN, SW Version etc.'''
        global SOFTWARE_VERSION, MODEL_NUMBER, SERIAL_NUMBER, FIRMWARE_VERSION, HARDWARE_VERSION, DEVICE_TYPE, DEVICE_ID
        self.logger.info('Init Device Called')
        for key, value in config.items():
            self.config[key] = value

        SOFTWARE_VERSION = self.config.get('version', SOFTWARE_VERSION)
        MODEL_NUMBER = self.config.get('modelNumber', MODEL_NUMBER)
        SERIAL_NUMBER = self.config.get('serialNumber', SERIAL_NUMBER)
        FIRMWARE_VERSION = self.config.get('firmwareVersion', FIRMWARE_VERSION)

        HARDWARE_VERSION = self.config.get('hardwareVersion', HARDWARE_VERSION)
        DEVICE_TYPE = self.config.get('deviceType', DEVICE_TYPE)
        DEVICE_ID = self.config.get('DEVICE_ID', DEVICE_ID)

        # dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        # self.bus = dbus.SystemBus()
        # self.adapter = find_adapter(self.bus)

        # if not self.adapter:
        #     logger.critical("GattManager1 interface not found")
        #     return

        # self.init_adapter()

    def init_adapter(self):
        self.logger.info('Init Adapter Called')
        self.adapter_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter)

        self.adapter_props = dbus.Interface(
            self.adapter_obj, "org.freedesktop.DBus.Properties")

        # set the powered property on the controller to on
        self.adapter_props.Set(
            "org.bluez.Adapter1",
            "Powered",
            dbus.Boolean(1)
        )

        self.adapter_props.Set(
            "org.bluez.Adapter1",
            "Discoverable",
            dbus.Boolean(1)
        )
        # Default is 180 seconds, make this always on until setting is updated otherwise
        self.adapter_props.Set(
            "org.bluez.Adapter1",
            "DiscoverableTimeout",
            dbus.UInt32(0)
        )

        self.adapter_props.Set(
            "org.bluez.Adapter1",
            "PairableTimeout",
            dbus.UInt32(0)
        )

        self.adapter_props.Set(
            "org.bluez.Adapter1",
            "Alias",
            dbus.String(f"WC-VIN={self.vin.upper()}")
        )

        # NOTE: Reports read only
        # self.adapter_props.Set(
        #     "org.bluez.Adapter1",
        #     "Name",
        #     dbus.String(f"WC-VIN={self.vin.upper()}")
        # )

        self.service_manager = dbus.Interface(self.adapter_obj, GATT_MANAGER_IFACE)
        self.ad_manager = dbus.Interface(self.adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    def disconnect_device(self, device):
        self.logger.info(f'Disconnect Device Called: {device}')
        self.adapter.RemoveDevice(device)

    def register_ad_cb(self):
        self.logger.info("Advertisement registered - set True")
        self.is_advertising = True
        self.advertisement.is_advertising = True

    def register_ad_error_cb(self, error):
        self.logger.critical("Failed to register advertisement: " + str(error))
        self.is_advertising = False
        self.advertisement.is_advertising = True

    def create_advertisement(self):
        self.advertisement = WinnConnectAdvertisement(self.bus, 1, self.vin, self)
        print('Advertisement ', self.advertisement)
        self.logger.info(f'Advertisement {self.advertisement}')

        self.register_advertisement()

    def register_advertisement(self):
        self.logger.info('Register Advertisement Called')

        adman_ad = self.ad_manager.RegisterAdvertisement(
            self.advertisement.get_path(),
            {},
            reply_handler=self.register_ad_cb,
            error_handler=self.register_ad_error_cb
        )
        self.advertisement.is_advertising = True

        return

    def unregister_advertisement(self):
        self.logger.info('Unregister Advertisement Called')
        self.advertisement.Release()
        try:
            self.logger.debug('Unregister Advertisement called with {self.advertisement}')
            self.ad_manager.UnregisterAdvertisement(self.advertisement)

        except dbus.exceptions.DBusException as err:
            print(err)
        return

    def create_app(self):
        app = Application(self.bus)
        app.add_service(
            DeviceInfoService(
                self.bus,
                2
            )
        )
        app.add_service(
            BleSecurityService(
                self.bus,
                3,
                UUID_SECURITY_SERVICE,
                'Session',    # 'Session Service',
                cfg=self.config
            )
        )
        app.add_service(
            BleComboService(
                self.bus,
                4,
                UUID_COMBO_SERVICE,
                'Combo Service'
            )
        )

        return app

    def main_loop(self):
        try:
            global response_queue
            self.running = True
            # global mainloop
            # self.response_queue = queue.Queue()

            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

            self.bus = dbus.SystemBus()
            self.adapter = find_adapter(self.bus)

            if not self.adapter:
                self.logger.critical("GattManager1 interface not found")
                return

            self.init_adapter()

            # TODO: Get the VIN from main service before init
            self.vin = self.config.get('VIN')

            self.ble_obj = self.bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

            self.agent = Agent(self.bus, AGENT_PATH)

            self.app = self.create_app()
            self.service_manager.RegisterApplication(
                self.app.get_path(),
                {},
                reply_handler=register_app_cb,
                error_handler=register_app_error_cb
            )

            self.agent_manager = dbus.Interface(self.ble_obj, "org.bluez.AgentManager1")
            self.agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

            self.create_advertisement()

            self.logger.info("Registered WGO GATT application")

            # TODO: Create method to start and restart thread as needed
            self.queue_thread = threading.Thread(
                target=response_worker,
                args=(response_queue, ),
                daemon=True
            )
            self.queue_thread.start()
            self.logger.info('Started response QUEUE')

            # TODO: Remove if not needed
            self.agent_manager.RequestDefaultAgent(AGENT_PATH)

            self.mainloop.run()
        except Exception as err:
            self.logger.error(f'Main loop fail {err}')
            raise
