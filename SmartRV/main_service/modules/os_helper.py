'''Module to support all direct OS calls'''

import subprocess


def run_os_call(os_command, args):
    subprocess.call(os_command, args)


def get_brightness():
    '''Get brightness from G&F HMI'''
    cmd = 'cat /sys/devices/platform/backlight/backlight/backlight/brightness'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    value = int(result.stdout.strip())
    return value


def set_brightness(value):
    '''Set brightness of G&F HMI'''
    cmd = f'echo {value} > /sys/devices/platform/backlight/backlight/backlight/brightness'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return get_brightness()
