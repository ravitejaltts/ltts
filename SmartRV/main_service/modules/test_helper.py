import random
import subprocess
import time
import os


ATC_LIGHTS = (
    110,
    111,
    112,
    113,
    114,
    115,
    116,
    117,
    118,
    119,
    120,
    121,
    122,
    123,
    124,
    125
)

ATC_MODES = (
    1,
    3
)

TMP = '/tmp'


def light_cmd(light_id, mode, brightness=200):
    cmd = 'cansend canb0s0 19FEDB44#{0:02X}FF{1:02X}{2:02X}FFFFFFFF'.format(
        light_id,
        brightness,
        mode
    )
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True)
    print(result)


def all_lights_off():
    '''Send predetermined commands to turn lights off.'''
    # Get ATC light instances and add
    for light in ATC_LIGHTS:
        light_cmd(light, 0x3)


def all_lights_on():
    '''Send predetermined commands to turn lights on.'''
    # Get ATC light instances and add
    for light in ATC_LIGHTS:
        light_cmd(light, 0x1)


def lightshow():
    # increment, decrement
    all_lights_off()
    for i in range(5):
        for light_id in ATC_LIGHTS:
            light_cmd(light_id, 0x3)
            time.sleep(0.25)

        time.sleep(3)

        for light_id in ATC_LIGHTS:
            light_cmd(light_id, 0x1)
            time.sleep(0.25)

    all_lights_off()


def random_lights():
    all_lights_off()

    for i in range(100):
        light = random.choice(ATC_LIGHTS)
        mode = random.choice(ATC_MODES)
        brightness = random.randint(0,200)
        light_cmd(light, mode, brightness)
        time.sleep(0.1)

    all_lights_off()


def weston_debug(onOff, app):
    if onOff == 1:
        cmd = 'systemctl stop weston@root'
        result = subprocess.run(cmd, shell=True, capture_output=True)
        cmd = 'weston --debug --tty=1'
        proc = subprocess.run(cmd, shell=True)
        app.debug_proc = proc
        subprocess.run(
            'systemctl restart kiosk',
            shell=True
        )
    else:
        # Ignore for now
        pass

    return

def weston_screenshot():
    cmd = 'weston-screenshooter'
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=TMP,
        capture_output=True
    )
    print('Screenshot result', result)
    # Get screenshot
    screenshots = os.listdir(TMP)
    screenshots = [
        os.path.abspath(x) for x in screenshots
            if os.path.splitext(x)[1] == '.png'
    ]
    print(screenshots)

    # TODO: Copy screenshot to the static folder

    try:
        return screenshots[0]
    except IndexError:
        print('No screenshots found')
        return None


def delete_screenshot(path):
    # Delete screenshot after providing it
    return


if __name__ == '__main__':
    all_lights_off()

    random_lights()
    # time.sleep(5)
    # all_lights_on()
    lightshow()
