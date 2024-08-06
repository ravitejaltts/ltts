# https://github.com/PunchThrough/espresso-ble

import logging
# from tkinter import mainloop
from urllib import response

import dbus
import dbus.exceptions
import dbus.mainloop.glib
import dbus.mainloop.NULL_MAIN_LOOP
import dbus.service

from ble import (
    Advertisement,
    Characteristic,
    Service,
    Application,
    find_adapter,
    Descriptor,
    Agent,
    GATT_CHRC_IFACE
)

import struct
import requests
import array
from enum import Enum

import sys

MainLoop = None
try:
    from gi.repository import GLib
    MainLoop = GLib.MainLoop
except ImportError:
    import gobject as GObject

    MainLoop = GObject.MainLoop

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logHandler = logging.StreamHandler()
fileLogHandler = logging.FileHandler("logs.log")
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logHandler.setFormatter(formatter)
fileLogHandler.setFormatter(formatter)
logger.addHandler(fileLogHandler)
logger.addHandler(logHandler)

mainloop = None

BLUEZ_SERVICE_NAME = "org.bluez"
GATT_MANAGER_IFACE = "org.bluez.GattManager1"
LE_ADVERTISEMENT_IFACE = "org.bluez.LEAdvertisement1"
LE_ADVERTISING_MANAGER_IFACE = "org.bluez.LEAdvertisingManager1"

MANUFACTURER_NAME = "Winnebago"
MODEL_NUMBER = "438"
SERIAL_NUMBER = "15362"
FIRMWARE_VERSION = "0.1.0"
SOFTWARE_VERSION = "0.1.0"
HARDWARE_VERSION = "0.1.0"

BaseUrl = "http://localhost:8000"


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"


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
    mainloop.quit()


def get_bytes(arr: dbus.Array):
    return bytes(arr)


def _decodeApiRequest(data: bytes):
    print(data)
    requestId = data[0]
    method = data[1]

    url = ""
    urlStart = 4
    urlLength = (data[3] << 8) + data[2]
    if urlLength > 0:
        url = data[urlStart:urlStart+urlLength].decode("utf-8")

    body = []
    bodyStart = urlStart + urlLength + 2
    bodyLength = (data[urlStart+urlLength+1] << 8) + \
        data[urlStart+urlLength]
    if bodyLength > 0:
        body = data[bodyStart:bodyStart+bodyLength]

    return ApiRequest(requestId, method, url, body)


class DeviceInfoService(Service):
    """
    Device Info Service that reports information about the device.

    """
    UUID = '0000180a-0000-1000-8000-00805f9b34fb'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.UUID, True)
        self.add_characteristic(StaticReadCharacteristic(
            bus, 0, self, "00002a29-0000-1000-8000-00805f9b34fb", MANUFACTURER_NAME))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 1, self, "00002a24-0000-1000-8000-00805f9b34fb", MODEL_NUMBER))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 2, self, "00002a25-0000-1000-8000-00805f9b34fb", SERIAL_NUMBER))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 3, self, "00002a27-0000-1000-8000-00805f9b34fb", HARDWARE_VERSION))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 4, self, "00002a26-0000-1000-8000-00805f9b34fb", FIRMWARE_VERSION))
        self.add_characteristic(StaticReadCharacteristic(
            bus, 5, self, "00002a28-0000-1000-8000-00805f9b34fb", SOFTWARE_VERSION))


class ApiService(Service):
    """
    API Service that exposes the full OpenAPI definition

    """
    UUID = '468299FF-BC2A-48BC-84AF-BA68FC506B6C'

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.UUID, True)

        responseCharacteristic = ApiResponseCharacteristic(bus, 1, self)

        self.add_characteristic(ApiRequestCharacteristic(
            bus, 0, self, responseCharacteristic))
        self.add_characteristic(responseCharacteristic)


class StaticReadCharacteristic(Characteristic):
    def __init__(self, bus, index, service, uuid, stringValue):
        Characteristic.__init__(
            self, bus, index, uuid, ["read"], service,
        )

        self.value = stringValue.encode()

    def ReadValue(self, options):
        return self.value


class ApiRequest:
    def __init__(self, requestId, method, url, body):
        self.requestId = requestId
        self.method = method
        self.url = url
        self.body = body


class ApiResponseCharacteristic(Characteristic):
    UUID = '46829A02-BC2A-48BC-84AF-BA68FC506B6C'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
            self, bus, index, self.UUID, ["notify"], service,
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

    def _sendData(self, data):
        if not self.notifying:
            logger.info('Not notifying, suppressing API response')
            return False

        logger.info("Sending data: " + repr(data))
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': data}, [])

        return self.notifying

    def _sendApiResponse(self, requestId, response: requests.Response):
        try:
            if not self.notifying:
                print('Not notifying, suppressing API response')
                return False

            data = bytearray()
            data.append(requestId & 0xff)
            data.extend(response.status_code.to_bytes(2, 'little'))
            data.extend(len(response.content).to_bytes(2, 'little'))
            data.extend(response.content)

            value = dbus.Array(data, signature="y")

            self.PropertiesChanged(
                GATT_CHRC_IFACE, {'Value': value}, [])

            return self.notifying
        except Exception as err:
            logger.error(repr(err))


class ApiRequestCharacteristic(Characteristic):
    UUID = '46829A01-BC2A-48BC-84AF-BA68FC506B6C'

    def __init__(self, bus, index, service, responseCharacteristic: ApiResponseCharacteristic):
        Characteristic.__init__(
            self, bus, index, self.UUID, ["write"], service,
        )

        self.responseCharacteristic = responseCharacteristic

    def WriteValue(self, value, options):
        try:
            data = get_bytes(value)
            logger.info('Data: ' + repr(data))

            apiRequest = _decodeApiRequest(data)

            apiResponse = requests.get(BaseUrl + apiRequest.url)
            self.responseCharacteristic._sendApiResponse(
                apiRequest.requestId, apiResponse)
        except Exception as err:
            logger.error(repr(err))


class CharacteristicUserDescriptionDescriptor(Descriptor):
    """
    Writable CUD descriptor.
    """

    CUD_UUID = "2901"

    def __init__(
        self, bus, index, characteristic,
    ):

        self.value = array.array('B', characteristic.description)
        self.value = self.value.tolist()
        Descriptor.__init__(self, bus, index, self.CUD_UUID, [
                            "read"], characteristic)

    def ReadValue(self, options):
        return self.value

    def WriteValue(self, value, options):
        if not self.writable:
            raise NotPermittedException()
        self.value = value


class WinnConnectAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, "peripheral")
        self.add_manufacturer_data(
            0xFFFF, [0x12, 0x34],
        )
        self.add_local_name("Winnebago")


def register_ad_cb():
    logger.info("Advertisement registered")


def register_ad_error_cb(error):
    logger.critical("Failed to register advertisement: " + str(error))
    mainloop.quit()


AGENT_PATH = "/com/winnebago/agent"


def main():
    global mainloop

    x = dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    print(x)

    bus = dbus.SystemBus()
    adapter = find_adapter(bus)

    if not adapter:
        logger.critical("GattManager1 interface not found")
        return

    adapter_obj = bus.get_object(BLUEZ_SERVICE_NAME, adapter)

    adapter_props = dbus.Interface(
        adapter_obj, "org.freedesktop.DBus.Properties")

    # set the powered property on the controller to on
    adapter_props.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(1))

    service_manager = dbus.Interface(adapter_obj, GATT_MANAGER_IFACE)
    ad_manager = dbus.Interface(adapter_obj, LE_ADVERTISING_MANAGER_IFACE)

    advertisement = WinnConnectAdvertisement(bus, 0)
    obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez")

    agent = Agent(bus, AGENT_PATH)

    app = Application(bus)
    app.add_service(DeviceInfoService(bus, 2))
    app.add_service(ApiService(bus, 3))

    mainloop = MainLoop()

    agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
    agent_manager.RegisterAgent(AGENT_PATH, "NoInputNoOutput")

    ad_manager.RegisterAdvertisement(
        advertisement.get_path(),
        {},
        reply_handler=register_ad_cb,
        error_handler=register_ad_error_cb
    )

    logger.info("Registering GATT application...")

    service_manager.RegisterApplication(
        app.get_path(),
        {},
        reply_handler=register_app_cb,
        error_handler=register_app_error_cb
    )

    agent_manager.RequestDefaultAgent(AGENT_PATH)

    mainloop.run()


if __name__ == "__main__":
    main()
