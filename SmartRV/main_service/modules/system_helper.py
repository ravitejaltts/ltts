"""Module to support on system calls."""

import subprocess
import os
import sys
import requests
import signal
import time

from configparser import ConfigParser

from common_libs.models.common import LogEvent, RVEvents
from common_libs import environment
from common_libs.clients import IOT_CLIENT, MAIN_CLIENT
_env = environment()


SUPPORTED_SERVICES = (
    'can',
    'ui',
    'kiosk',
    'bluetooth',
    'ble_gatt',
    'iot',
)


def get_display_brightness():
    # TODO: Get image version into this function
    # cmd = 'cat /sys/devices/platform/backlight/backlight/backlight/brightness'
    # Image after 0.10
    filename = '/dev/backlight/actual_brightness'
    if not os.path.exists(filename):
        filename = '/sys/devices/platform/lvds_backlight@0/backlight/lvds_backlight@0/actual_brightness'
    # cmd = 'cat /dev/backlight/actual_brightness'

    try:
        with open(filename, 'r') as brightness_readout:
            brightness = brightness_readout.read()
    except FileNotFoundError as err:
        print('Cannot find file', err)
        brightness = '0'

    try:
        brightness = int(brightness.strip())
    except ValueError as err:
        if sys.platform.startswith('darwin'):
            return 75
        else:
            print('Cannot get display brightness', err)
            brightness = 75
        # TODO: Handle testing on a system where this is expected to fail
        # return the input value for Laptop testing which does not accept this command
    return brightness


def set_display_brightness(value):
    # TODO: Get image version into this function
    print(f'Setting brightness to: {value} %')

    filename = '/dev/backlight/brightness'
    if not os.path.exists(filename):
        # NOTE: Cannot write to that file
        filename = '/sys/devices/platform/lvds_backlight@0/backlight/lvds_backlight@0/brightness'

    try:
        value = int(value)
    except ValueError as err:
        print('Error converting value', err)
        value = 75

    try:
        with open(filename, 'w') as brightness_setting:
            brightness_setting.write(str(value))
    except FileNotFoundError as err:
        if sys.platform.startswith('darwin'):
            return value
        else:
            print('Cannot set brightness', err)
    except Exception as err:
        print('Unhandled Exception', err)

    return get_display_brightness()


def set_display_default():
    user_settings_file = os.path.join(
        _env.config_path(),
        'display.ini'
    )
    display_config = ConfigParser()
    display_config['Display'] = {
        'brightness': 75,
        'dimmertimeout': 5 * 60,    # 5 minutes
        'dimmerblankoffset': 0
    }
    try:
        with open(user_settings_file, 'w') as display_settings:
            display_config.write(display_settings)
    except FileNotFoundError:
        # Make sure folders exists
        os.makedirs(
            os.path.split(user_settings_file)[0]
        )
        return set_display_default()


def save_display_config(settings):
    user_settings_file = os.path.join(
        _env.config_path(),
        'display.ini'
    )

    brightness = settings.get('brightness')
    timeout = settings.get('inactiveTimeout')
    offset = settings.get('offTimeout', 0)

    if timeout == 0:
        # Set 7 days for timeout
        timeout = 3600 * 24 * 7

    display_config = ConfigParser()
    display_config['Display'] = {
        'brightness': brightness,
        'dimmertimeout': timeout,
        'dimmerblankoffset': offset
    }
    try:
        with open(user_settings_file, 'w') as display_settings:
            display_config.write(display_settings)
    except FileNotFoundError:
        # Make sure folders exists
        os.makedirs(
            os.path.split(user_settings_file)[0]
        )
        return save_display_config(settings)

    return display_config['Display']


def set_display_off():
    set_display_brightness(0)
    # subprocess.run(
    #     'echo 4 > /sys/class/graphics/fb0/blank',
    #     shell=True
    # )


def set_display_on():
    subprocess.run(
        'echo 0 > /sys/class/graphics/fb0/blank',
        shell=True
    )


def clear_caches():
    '''Clear caches that the browser might use when system was writable.
    This likely fails often.'''
    subprocess.run(
        'rm -rf /.cache/qt-kiosk-browser;'
        'rm -rf /root/.cache/qt-kiosk-browser;'
        'rm -rf /home/weston/.cache/qt-kiosk-browser',
        shell=True
    )


def check_partitions(storage_partition='/dev/mmcblk0p10'):
    #     PART_CHECK=$("lsblk")
    if not os.path.exists('/storage'):
        print('Storage partition missing')

    # if echo "$PART_CHECK" | grep -q "/storage"; then
    #     echo "Storage Partition present"
    # else
    #     echo "Storage Partition missing"
    # What to do to fix ?

    # Mount and run FSCK ?
    # Get the system specific storage partition
    # result = subprocess.run(f'fsck {storage_partition}', shell=True, capture_output=True)
    # print(result)
    # fsck /dev/mmcblk0p10

    # mkdir /storage
    # mount /dev/mmcblk0p10 /storage

    # If that fails recreate the partition and reboot
    # Recreate partition
    # mkfs.ext4 /dev/mmcblk0p10
    # Reboot


def get_system_processes():
    cmd = 'ps -aux'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result


def restart_service(service):
    '''Restart the given service'''
    # TODO: Check received service for injection
    if service == 'ble':
        cmd = 'systemctl restart bluetooth;systemctl restart ble_gatt'

    else:
        if service not in SUPPORTED_SERVICES:
            raise ValueError(f'Service "{service}" not supported')
        cmd = f'systemctl restart {service}'

    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result


def shutdown_system():
    '''Shutdown system.'''
    cmd = 'shutdown -h now'
    subprocess.run(cmd.split(' '), capture_output=True)
    return


def reboot_system():
    '''Reboot system.'''
    cmd = 'reboot'
    subprocess.run(cmd, capture_output=True)
    return


async def ok_ota_system(app):
    '''Ok IOT to update system.'''
    IOT_OK_URL = 'http://localhost:8002/ota_start'
    try:
        response = await IOT_CLIENT.put(IOT_OK_URL, timeout=5)
        response = response.json()

        if response.get('result', None) == 'OTA not ready.':
            # Return the empty dict - which is failure
            response = {}
            print('ok_ota_system received: OTA not ready.')
        else:
            print(f'ok_ota_system {response}')
            # Clear the alert
            app.event_logger(
                LogEvent(
                    timestamp=time.time(),
                    event=RVEvents.OTA_UPDATE_RECEIVED,
                    instance=1,
                    value=0,
                    )
                )
    except requests.exceptions.ConnectionError:
        response = {}
    except Exception as err:
        print(err)
        response = {}

    return response


def shutdown_main_system():
    # Let pytest return as it used to.
    if 'pytest' in sys.modules:
        return
    signal.raise_signal(signal.SIGINT)
    # Get the current process ID
    current_pid = os.getpid()
    # Define the service name
    service_name = "WGO-MAIN-Service"

    # Use the subprocess module to execute the pgrep command and capture the output
    try:
        pids = subprocess.check_output(["pgrep", "-f", service_name]).decode().strip().split('\n')
        pids = [pid for pid in pids if pid]  # Filter out any empty strings
        print(f"Found PIDs for service '{service_name}': {pids} current {current_pid}")
        for pid in pids:
            if pid is not current_pid:
                subprocess.run(['kill', f"{pid}"])
                subprocess.run(['kill', f"{pid}"])
        subprocess.run(['kill', f"-9 {current_pid}"])
        subprocess.run(['kill', f"-9 {current_pid}"])

    except subprocess.CalledProcessError as e:
        # Handle the exception (e.g., no PIDs found, command error)
        print(f"No processes with the name '{service_name}' found.")


def ifconfig():
    '''Get ifconfig output.'''
    cmd = 'ifconfig -a'
    result = subprocess.run(cmd.split(' '), capture_output=True)
    return result


def get_ip(iface='eth0'):
    '''Get IP address.'''
    if sys.platform.startswith('darwin'):
        # INFO: Doms Laptop
        cmd = f'ifconfig en7 | grep "inet "'
    else:
        # cmd = f"ip -f inet addr show {iface} | sed -En -e 's/.*inet ([0-9.]+).*/\1/p'"
        cmd = f"ip -f inet addr show {iface}"

    result = subprocess.run(cmd.split(' '), capture_output=True)
    output = result.stdout.decode('utf8')

    ip_addr = []

    for line in output.split('\n'):
        if 'inet' in line:
            line = line.strip()
            ip = line.split(' ')[1].split('/')[0]
            print('IP', line, ip)
            ip_addr.append(
                line.split(' ')[1].split('/')[0]
            )

    output = ', '.join(ip_addr)

    if 'netmask' in output:
        try:
            # IFCONFIG output with grep
            return output.split('netmask')[0].strip().split(' ')[1].decode('utf8')
        except IndexError as err:
            print('ERROR get_ip()', err)

    return output


def get_bt_mac():
    '''Get MAC address from bluetooth.'''
    # if sys.platform.startswith('darwin'):
    #     # INFO: Doms Laptop
    # else:
    #     # cmd = f"ip -f inet addr show {iface} | sed -En -e 's/.*inet ([0-9.]+).*/\1/p'"
    cmd = "bluetoothctl list"

    result = subprocess.run(cmd.split(' '), capture_output=True)
    output = result.stdout.decode('utf8')

    mac_addr = []

    for line in output.split('\n'):
        if 'Controller' in line:
            line = line.strip()
            mac = line.split(' ')[1]
            mac_addr.append(
                mac
            )

    output = ', '.join(mac_addr)

    return output


def get_iot_status(app):
    # TODO: Replace with ENV URL
    IOT_URL = 'http://localhost:8002/status'
    try:
        response = requests.get(IOT_URL, timeout=0.5).json()
        app.iot_status = response
    except requests.exceptions.ConnectionError:
        response = {}
        app.iot_status["status"] = 'ERROR'
        app.iot_status["msg"] = 'No connection to IoT service'
    except Exception as err:
        print('get_iot_status error', err)
        app.iot_status["status"] = err
        app.iot_status["msg"] = 'No connection to IoT service'
    # print('[get_iot_status]', app.iot_status)
    return app.iot_status


async def get_bt_status():
    # TODO: Replace with ENV URL
    BT_URL = 'http://localhost:8005/status'
    try:
        response = await MAIN_CLIENT.get(BT_URL, timeout=0.5)
        response = response.json()
    except Exception as err:
        print(err)
        response = {}

    return response


def read_current_version_about():
    with open('../data/about.html', 'r') as about:
        content = about.read()
    return content


def get_os_release():
    '''root@winnconnect:~# cat /etc/os-release
    ID=winnebago-connect
    NAME="Winnebago Connect"
    VERSION="v0.10.16-dev (alphaville)"
    VERSION_ID=v0.10.16-dev
    PRETTY_NAME="Winnebago Connect v0.10.16-dev (alphaville)"
    DISTRO_CODENAME="alphaville"'''
    os_dict = {}
    try:
        with open('/etc/os-release', 'r') as os_release:
            os_data = os_release.read()
    except Exception as e:
        print('Error reading os-release', e)
        return os_dict

    for line in os_data.split('\n'):
        if '=' in line:
            key, value = line.split('=', maxsplit=1)
            key = key.lower()
            os_dict[key] = value

    return os_dict


def read_about_from_bld_directory():
    """
    Reads the contents of 'about.html' from the first directory in the given storage path
    that starts with 'bld_'.
    """
    try:
        storage_path = _env.storage_file_path() + '/'
        # List all directories in the storage path
        directories = [d for d in os.listdir(storage_path) if os.path.isdir(os.path.join(storage_path, d))]

        # Find the first directory that starts with 'bld_'
        bld_directory = next((d for d in directories if d.startswith('bld_')), None)

        if bld_directory is None:
            return "No directory starting with 'bld_' found."

        # Construct the path to the 'about.md' file
        about_path = os.path.join(storage_path, bld_directory, 'data/about.html')

        # Read the 'about.md' file
        if os.path.exists(about_path):
            with open(about_path, 'r') as file:
                return file.read()
        else:
            return "'about.html' file not found."

    except Exception as e:
        return f"An error occurred reading the about: {e}"


def get_free_storage(path='/'):
    '''Read free storage for root or given path.'''
    cmd = 'df -h'
    result = subprocess.run(cmd.split(), capture_output=True, check=False)
    storage_for_path = 'NA'
    try:

        for line in result.stdout.decode('utf8').split('\n'):
            if not line.strip():
                continue
            elements = line.split(' ')
            elements = [x.strip() for x in elements if x.strip()]

            if path == elements[-1]:
                storage_for_path = elements[3] + ' / ' + elements[4]
                break
    except IndexError as e:
        print('Error getting element indices', e)
        storage_for_path = 'CANNOT READ'

    free_storage = f'{path}: {storage_for_path}'

    return free_storage


def get_free_storage_mb(path='/'):
    '''Read free storage for root or given path in MiB.'''
    cmd = 'df -h -B MiB'
    result = subprocess.run(cmd.split(), capture_output=True, check=False)
    storage_for_path = -1.0, -1.0
    try:
        for line in result.stdout.decode('utf8').split('\n'):
            if not line.strip():
                continue
            elements = line.split(' ')
            elements = [x.strip() for x in elements if x.strip()]

            if path == elements[-1]:
                storage_for_path = float(elements[3].replace('MiB', '')), float(elements[4].replace('%', ''))
                break
    except IndexError as e:
        print('Error getting element indices', e)
        storage_for_path = 'CANNOT READ', 'CANNOT READ'

    return storage_for_path


def get_cpu_load():
    '''
    %Cpu(s):  6.8 us,  5.4 sy,  0.0 ni, 86.5 id,  0.0 wa,  1.4 hi,  0.0 si,  0.0 st
    '''
    cmd = 'top -b -n 1'
    result = subprocess.run(cmd.split(), capture_output=True, check=False)
    cpu_load = -1

    for line in result.stdout.decode('utf8').split('\n'):
        if not line.strip():
            continue
        if '%Cpu' in line:
            for item in line.split(','):
                if item.endswith('id'):
                    print('Idle', item)
                    cpu_load = 100 - float(
                        item.strip().replace(' id', '')
                    )
                    print('CPU', cpu_load)
                    break

    return round(cpu_load, 1)


def get_memory_usage():
    '''
    top - 22:38:59 up 4 min,  2 users,  load average: 1.01, 0.86, 0.41
    Tasks: 198 total,   1 running, 197 sleeping,   0 stopped,   0 zombie
    %Cpu(s): 11.2 us,  4.3 sy,  0.0 ni, 83.1 id,  0.0 wa,  1.2 hi,  0.2 si,  0.0 st
    MiB Mem :   3927.1 total,   3036.5 free,    564.7 used,    325.9 buff/cache
    MiB Swap:      0.0 total,      0.0 free,      0.0 used.   3176.6 avail Mem
    '''
    cmd = 'top -b -n 1'
    result = subprocess.run(cmd.split(), capture_output=True, check=False)

    total = None
    free = None

    for line in result.stdout.decode('utf8').split('\n'):
        if not line.strip():
            continue

        if 'MiB Mem' in line:
            for item in line.split(','):
                if item.endswith('total'):
                    # MiB Mem :   3927.1 total, ...
                    total = item.split(':')[1].strip().replace('total', '').strip()
                elif item.endswith('free'):
                    free = item.replace('free', '').strip()

        if total is not None and free is not None:
            total = float(total)
            free = float(free)
            break

    if total is None or free is None:
        return -1.0, -1.0, -1.0

    return round(total - free, 1), total, free


if __name__ == '__main__':
    print(get_free_storage_mb('/'))
    print(get_cpu_load())
