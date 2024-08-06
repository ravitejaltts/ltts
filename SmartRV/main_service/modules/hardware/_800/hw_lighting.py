# Does the light have zones ?
# Does the light have RGB capabilities
# Does the light have brightness, if yes, what is the value for 0% and 100% and in between
#
from copy import deepcopy
from multiprocessing.sharedctypes import Value
import subprocess
import time
import sys

try:
    from main_service.modules.hardware.itc.itc227rgbw import ITC, CONTROLLER_ID_TO_ADDR
    from main_service.modules.hardware.czone.control_x_plus import CZone
except ModuleNotFoundError:
    from itc.itc227rgbw import ITC, CONTROLLER_ID_TO_ADDR
    from czone.control_x_plus import CZone


from main_service.modules.hardware.common import BaseLighting

from  common_libs.models.common import (
    RVEvents,
    EventValues
)

# Monitor the CZONE light that CZONE currently controls
# This will change when we intercept the momentary switch can messges and
# implement the fuctions for the light czone is doing


# # Initialize lighting controllers used in the 800
czone = CZone(
    cfg={
        'mapping': {
            9: 14,
            10: 15
        },
        'controller_id': [0x00, 0x00],
        'zones': {}
    }
)
itc_1 = ITC(
    cfg={
        'controller_id': 1,
        'zones': {}
    }
)
itc_2 = ITC(
    cfg={
        'controller_id': 2,
        'zones': {}
    }
)


settings = {
    'title': 'Lighting System Settings',
    'configuration': None,
    'information': [
        {
            'title': 'MANUFACTURER INFORMATION',
            'items': [
                {
                    'title': 'Galley Light',
                    'sections': [
                        {
                            'title': None,
                            'items': [
                                {
                                    'key': 'Manufacturer',
                                    'value': 'ITC'
                                },
                                {
                                    'key': 'Product Model',
                                    'value': '???'
                                }
                            ]
                        }
                    ]
                },
                {
                    'title': 'Accent Light',
                    'sections': [
                        {
                            'title': None,
                            'items': [
                                {
                                    'key': 'Manufacturer',
                                    'value': 'ITC'
                                },
                                {
                                    'key': 'Product Model',
                                    'value': '???'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}


ZONE_TO_BIT = {
    1: 1,
    2: 2,
    3: 4,
    4: 8,
    5: 1,
    6: 2,
    7: 4,
    8: 8
}

CZONE_ZONES = (9, 10)
TOGGLED_ZONES = [10]


RGB_DEFAULT = '#ffd587'
COLOR_TEMP_DEFAULT = 5000
BRIGHTNESS_DEFAULT = 80
LED_MIN_BRIGHTNESS = 5

MASTER_DEFAULT = {
    'onOff': 0,
    'rgb': '#FFFFFF',
    'clrTmp': 4000,
    'brt': 80
}

# HW Defaults, might be overwritten elsewhere, based on user prefs etc.
zones = [
    {
        'id': 1,
        'type': 'RGBW',
        'name': 'Front Work',
        'description': 'Main ceiling lights',
        'code': 'lz',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_1,
        'state': {
            'rgb': RGB_DEFAULT,
            'brt': BRIGHTNESS_DEFAULT,
            'onOff': 0,
            'clrTmp': COLOR_TEMP_DEFAULT
        }
    },
    {
        'id': 2,
        'type': 'RGBW',
        'name': 'Main',
        'description': '',
        'code': 'lz',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_1,
        'state': {
            'rgb': RGB_DEFAULT,
            'brt': BRIGHTNESS_DEFAULT,
            'onOff': 1,
            'clrTmp': COLOR_TEMP_DEFAULT
        }
    },
    {
        'id': 3,
        'type': 'SIMPLE_DIM',
        'name': 'Bath',
        'description': '',
        'code': 'lz',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_1,

        'state': {
            'onOff': 0,
            'brt': 100
        },
        # Light is running as a dimmable light on RED
        'channel': 'R'
    },
    {
        'id': 4,
        'type': 'RGBW',
        'name': 'Galley',
        'description': '',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_1,
        'state': {
            'rgb': RGB_DEFAULT,
            'brt': BRIGHTNESS_DEFAULT,
            'onOff': 0,
            'clrTmp': COLOR_TEMP_DEFAULT
        }

    },
    {
        'id': 5,
        'type': 'RGBW',
        'name': 'Dinette',
        'description': '',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_2,
        'state': {
            'rgb': RGB_DEFAULT,
            'brt': BRIGHTNESS_DEFAULT,
            'onOff': 0,
            'clrTmp': COLOR_TEMP_DEFAULT
        }

    },
    {
        'id': 6,
        'type': 'RGBW',
        'name': 'Bed',
        'description': '',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_2,
        'state': {
            'rgb': RGB_DEFAULT,
            'brt': BRIGHTNESS_DEFAULT,
            'onOff': 0,
            'clrTmp': COLOR_TEMP_DEFAULT
        }

    },
    {
        'id': 7,
        'type': 'RGBW',
        'name': 'Floor',
        'description': '',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_2,
        'state': {
            'rgb': RGB_DEFAULT,
            'brt': BRIGHTNESS_DEFAULT,
            'onOff': 0,
            'clrTmp': COLOR_TEMP_DEFAULT
        }

    },
    {
        'id': 8,
        'type': 'RGBW',
        'name': 'Accent',
        'description': '',

        'controller_type': 'ITC 227X-RGBW',
        'controller': itc_2,
        'state': {
            'rgb': RGB_DEFAULT,
            'brt': BRIGHTNESS_DEFAULT,
            'onOff': 0,
            'clrTmp': COLOR_TEMP_DEFAULT
        }

    },
    {
        'id': 9,
        'type': 'SIMPLE_ONOFF',
        'state': {
            'onOff': 0
        },
        'name': 'Porch',
        'description': 'Outside light 1',

        'controller_type': 'CZone Control X Plus',
        'controller': czone
    },
    {
        'id': 10,
        'type': 'SIMPLE_ONOFF',
        'name': 'Service',
        'description': 'Outside light 2',
        'state': {
            'onOff': 0
        },

        'controller_type': 'CZone Control X Plus',
        'controller': czone
    }
]

zones_by_id = {x.get('id'): x for x in zones}

def default_light_setting():
    default_light_ids = []
    for zone in zones:
        if zone['name'] == 'Front Work' or zone['name'] == 'Main' or zone['name'] == 'Galley':
            default_light_ids.append(zone['id'])
    return default_light_ids

DEFAULT_LIGHTS = default_light_setting()

init_script = {
    # Should a real script go here for init
}

shutdown_script = {}


ZONE_DEFAULTS = {
    'RGBW': {
        'onOff': 0,
        'brt': 80,
        'rgb': '#FFFFFF',
        'clrTmp': 5000
    },
    'SimpleDim': {
        'onOff': 0,
        'brt': 100
    },
    'Simple': {
        'onOff': 0
    }
}


def load_state():
    '''Read state from storage or memory or CAN bus.'''
    state = {}
    for zone in zones:
        zone_id = zone.get('id')
        zone_type = zone.get('type')

        zone_default = zone.get(
            zone_type,
            ZONE_DEFAULTS[zone_type]
        )
        # print('Zone default: ', zone_default)

        state[zone_id] = zone_default

        return state

# TODO: Create lighting baseclass and add smarttoggle as a puttable method
class Lighting(BaseLighting):
    def __init__(self, config={}):
        BaseLighting.__init__(self, config=config)
        self.configBaseKey = 'lighting'
        # TODO: Get from config not in module global variable
        self.lighting_zones = zones


    def _is_channel_restricted(self, zone_id):
        '''Check if the given zone operates only a single channel of RGBW lighting.'''
        zone = zones_by_id.get(zones_by_id)
        if zone is None:
            raise ValueError(f'Zone {zone_id} not supported/available')

        channel = zone.get('channel')
        if channel in ('R', 'G', 'B', 'W'):
            return channel

        return None


    def _get_controller_id_from_zone(self, zone_id):
        if zone_id == 0:
            controller_id = 'FFFF'
        else:
            controller_id = zones_by_id[zone_id]['controller'].cfg['controller_id']
            controller_id = CONTROLLER_ID_TO_ADDR.get(controller_id)
            if controller_id is None:
                raise ValueError(f'Zone {zone_id} not found in zone mapping of controller')

        return controller_id


    def _send_ctr_command(self, controller_id, zone, command, value):
        cmd = f'cansend canb0s0 0CFC0044#{controller_id}{command}{zone}{value}'


    def _init_config(self):
        # Get zones
        # TODO:
        config_found = False
        for zone in zones:
            index = zone.get('id')
            key = f'{self.configBaseKey}.zone.{index}'
            config_value = self.HAL.app.get_config(key)
            #print('>>>', key, config_value)

            if config_value is not None:
                config_found = True
                # Do something with the light
                #print(f'Config for light zone {index} {config_value}')
                self._light_switch(index, config_value)
            else:
                # set a generic default off
                self._light_switch(
                    index,
                    {
                        'onOff': 0,
                        'brt': BRIGHTNESS_DEFAULT,
                        'rgb': '#FFFFFF',
                        'clrTmp': 5000
                    }
                )
        # Get presets handled on App level

    def _update_state(self, zone, new_state):
        if zone in self.state:
            zone_state = self.state[zone]
        else:
            zone_state = {}

        # print('Zone State', zone_state)

        updated_keys = []

        # Check for changes in the zone state keys
        for key, value in new_state.items():
            if key in zone_state:
                if value != zone_state.get(key):
                    updated_keys.append(key)
                    zone_state[key] = value
            else:
                zone_state[key] = value
                updated_keys.append(key)

        # print('Final zone state', zone_state)

        self.state[zone] = zone_state

        # print(self.state[zone], updated_keys)

        return updated_keys

    def setHAL(self, hal_obj):
        self.HAL = hal_obj

    def light_status(self):
        lights_on = 0
        lights_off = 0
        lights_unknown = 0

        for zone_id, zone_state in self.state.items():
            if zone_id in ('preset_1', 'preset_2', 'preset_3', 'smarttoggle', 'zone_0'):
                # print('Skipping', zone_id)
                continue

            #print('Zone state', zone_state, type(zone_state))

            if zone_state.get('onOff') == 1:
                lights_on += 1
            elif zone_state.get('onOff') == 0:
                lights_off += 1
            else:
                lights_unknown += 1

        return {
            'on': lights_on,
            'off': lights_off,
            'na': lights_unknown
        }

    def perform_reset(self):
        '''Execute a lighting reset.

        Might be needed if lighting controllers misbehave or SW issues block recovery.'''
        cmd = (
            # Enable saving to EEPROM
            'cansend canb0s0 0CFC0044#FFFF6E01;'
            # Set lighting controllers to single light mode
            'cansend canb0s0 0CFC0044#FFFF02FF00;'
            # Set lighting to white
            'cansend canb0s0 0CFC0044#FFFF01FFFFFFFF00;'
            # set brightness to 75%
            'cansend canb0s0 0CFC0044#FFFF03FF4040;'
            # Set color temp range 3000 - 9000 K
            'cansend canb0s0 0CFC0044#FFFF3DFF0BB82328;'
            # Save to EEPROM
            'cansend canb0s0 0CFC0044#FFFF6E00;'
        )
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )
        return result

    def enable_disco(self):
        '''Set the unit to disco mode to test lighting reset (and for fun).
        Might be needed if lighting controllers misbehave or SW issues block recovery.'''
        cmd = (
            # # Enable saving to EEPROM
            # 'cansend canb0s0 0CFC0044#FFFF6E01;'
            # Set lighting controllers to single light mode
            'cansend canb0s0 0CFC0044#FFFF07FF00;'
            # Set lighting to white
            # 'cansend canb0s0 0CFC0044#FFFF01FFFFFFFF00;'
            # # set brightness to 75%
            # 'cansend canb0s0 0CFC0044#FFFF03FF4040;'
            # # Set color temp range 3000 - 9000 K
            # 'cansend canb0s0 0CFC0044#FFFF3DFF0BB82328;'
            # # Save to EEPROM
            # 'cansend canb0s0 0CFC0044#FFFF6E00;'
        )
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )
        return result


    def get_hw_info(self):
        return {}


    def get_state(self, zone=None, key=None):
        '''Return state of lighting system.'''
        # if zone in CZONE_ZONES:
        #     return czone.state.get(zone)

        # else:
        if zone is not None:
            if key is None:
                # Return the whole zone
                # print('GetState', self.state)
                return self.state.get(zone)
            else:
                key_result = self.state.get(zone, {}).get(key)
                return key_result

        return self.state


    def get_master_light_state(self, zone_id=0):
        '''Get the current values/states for the master light switch.'''
        key = f'zone_{zone_id}'
        master_state = self.state.get(key, MASTER_DEFAULT)

        light_status = self.light_status()
        lights_on = light_status.get('on')
        # return 1 if lights_on > 0 else 0
        return master_state


    def set_master_light_state(self, new_state, zone_id=0):
        '''Set the new state for master light switch.'''
        key = f'zone_{zone_id}'
        self.state[key] = new_state


    def get_zones_ui(self):
        '''Assemble zone config for UI response.'''
        pass

    def get_zone(self, hmi_id):
        #Get the HMI lighting zone state
        # which when use channels is different
        return self.state.get(hmi_id, {})


    def _light_switch(self, zone_id, light_control):
        '''Apply the HW specific controls needed to set the light to desired state.

        Only meant to be called from HW layer here
        Assumes that data is validated before saved to the DB'''
        zone_details = zones_by_id.get(zone_id)
        zone_type = zone_details.get('type')
        onoff_result = None
        brightness_result = None
        rgb_result = None
        color_temp_result = None

        #print('[LIGHTING] Received', light_control)

        if zone_type == 'SIMPLE_ONOFF':
            onoff_result = self.zone_switch(zone_id, light_control['onOff'])
            # Check if ITC channel restricted
            if 'ITC' in zone_details.get('controller_type', ''):
                # This is an ITC circuit that needs a brightness to work
                # As it is also a simple light it will be statically set to 100%
                brightness_result = self.zone_brightness(zone_id, 100)

        elif zone_type == 'SIMPLE_DIM':
            onoff_result = self.zone_switch(zone_id, light_control['onOff'])
            brightness_result = self.zone_brightness(zone_id, light_control['brt'])
        elif zone_type == 'RGBW':
            onoff_result = self.zone_switch(zone_id, light_control['onOff'])
            brightness_result = self.zone_brightness(zone_id, light_control['brt'])
            rgb_result = self.zone_rgb(zone_id, light_control['rgb'])
            # TODO: Check if colorTmp or RGB was last active
            # Maybe by getting a reading or storing an extra variable in the configs
            # lighting.1.last_mode: 'RGB', 'TEMP' ?
            self._update_state(zone_id, {'clrTmp': color_temp_result})


        result = {
            'onOff': onoff_result,
            'brt': brightness_result,
            'rgb': rgb_result,
            'clrTmp': color_temp_result
        }
        return result

    def toggle_zone_switch(self, zone_id, on_off):
        if not on_off:
            return
        current_state = self.get_state(zone_id, None)['onOff']
        if current_state:
            self.zone_switch(zone_id, 0)
        else:
            self.zone_switch(zone_id, 1)

    def zone_switch(self, zone_id, on_off):
        if zone_id in CZONE_ZONES:
            result = czone.circuit_control(
                czone.cfg['mapping'].get(zone_id, zone_id),
                on_off,
                100
            )
        else:
            controller_id = self._get_controller_id_from_zone(zone_id)
            zone = '{:02X}'.format(ZONE_TO_BIT.get(zone_id, 0xff))
            if zone == 'FF':
                # TODO: Switch CZone as well
                pass

            cmd = f'cansend canb0s0 0CFC0044#{controller_id}02{zone}00'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True
            )

            # Switch ITC
            if on_off == 0:
                cmd = f'cansend canb0s0 0CFC0044#{controller_id}06{zone}0000'
            elif on_off == 1:
                cmd = f'cansend canb0s0 0CFC0044#{controller_id}06{zone}0100'
            else:
                cmd = f'cansend canb0s0 0CFC0044#{controller_id}06{zone}0100'
                on_off = 1

            #print('[LIGHTING] Sending', cmd)

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True
            )

            event_value = EventValues.ON if on_off == 1 else EventValues.OFF
            self.event_logger.add_event(
                RVEvents.LIGHTING_ZONE_MODE_CHANGE,
                zone_id,
                event_value
            )

        if zone_id == 0:
            for zone in zones:
                self._update_state(zone.get('id'), {'onOff': on_off})
        else:
            self._update_state(zone_id, {'onOff': on_off})

        return result


    def zone_brightness(self, zone_id: int, brightness: int):
        controller_id = self._get_controller_id_from_zone(zone_id)
        zone = '{:02X}'.format(ZONE_TO_BIT.get(zone_id, 0xff))
        if brightness is None:
            brightness = BRIGHTNESS_DEFAULT
        else:
            if brightness < LED_MIN_BRIGHTNESS:
                brightness = LED_MIN_BRIGHTNESS
            elif brightness > 100:
                brightness = 100
        brightness_hex = '{brightness:02X}{brightness:02X}'.format(brightness=brightness)

        cmd = f'cansend canb0s0 0CFC0044#{controller_id}03{zone}{brightness_hex}'

        #print('[LIGHTING] Sending', cmd)

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )

        self._update_state(zone_id, {'brt': brightness})

        self.event_logger.add_event(
            RVEvents.LIGHTING_ZONE_BRIGHTNESS_LEVEL_CHANGE,
            zone_id,
            brightness
        )

        return result


    def zone_rgb(self, zone_id: int, rgb: str):
        controller_id = self._get_controller_id_from_zone(zone_id)
        zone = '{:02X}'.format(ZONE_TO_BIT.get(zone_id, 0xff))
        rgb_value = rgb.replace('#', '')

        # Disabled colorTemp
        cmd = f'cansend canb0s0 0CFC0044#{controller_id}3C{zone}00'

        # print('[LIGHTING] Sending', cmd)
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )

        # Set controller to RBG mode
        cmd = f'cansend canb0s0 0CFC0044#{controller_id}02{zone}00'

        # print('[LIGHTING] Sending', cmd)
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )

        # Set the color
        # TODO: check white value might be needed (it will make it more bright but less to the set color)
        cmd = f'cansend canb0s0 0CFC0044#{controller_id}01{zone}{rgb_value}00'
        # print('[LIGHTING] Sending', cmd)
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )

        self._update_state(zone_id, {'rgb': rgb})

        self.event_logger.add_event(
            RVEvents.LIGHTING_ZONE_RGBW_COLOR_CHANGE,
            zone_id,
            rgb
        )

        # 0CFC0044#FFFF01ffff000000

        return result


    def zone_colortemp(self, zone_id: int, color_temp, rgb=None):
        # print('Updating color temp', color_temp)
        controller_id = self._get_controller_id_from_zone(zone_id)
        zone = '{:02X}'.format(ZONE_TO_BIT.get(zone_id, 0xff))
        c_temp = color_temp

        cmd = f'cansend canb0s0 0CFC0044#{controller_id}3C{zone}01{c_temp:04X}'
        # print('[LIGHTING] Sending', cmd)

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )

        self._update_state(zone_id, {'clrTmp': color_temp})
        if rgb is not None:
            # Update only the state for API but do not actually control
            self._update_state(zone_id, {'rgb': rgb})

        # TODO: Figure out what the right even is if any
        self.event_logger.add_event(
            RVEvents.LIGHTING_ZONE_COLOR_TEMP_CHANGE,
            zone_id,
            color_temp
        )

        return result


    def notification(self, level):
        '''Visualize notifications to the user based on criticality.'''
        # Get current settings/state and store
        # Flash color of desired zones in this coach/product
        # Set back
        if self.state.get('notification_running') is True:
            return
        if level == 'error':
            color = 'ff0000'
        elif level == 'warning':
            color = 'ffff00'
        else:
            color = '00ff00'

        self.state['notification_running'] = True

        DESIGNATED_ZONES = [7, 8]    # Accent and floor
        # TODO: Get the current color for the designated zones
        # current_settings = {}
        # for zone in DESIGNATED_ZONES:
        #     current_settings[zone] = self.state.get()

        for i in range(4):
            for zone in DESIGNATED_ZONES:
                self.zone_brightness(zone, 100)
                self.zone_rgb(zone, color)

            time.sleep(0.4)

            for zone in DESIGNATED_ZONES:
                self.zone_rgb(zone, 'ffffff')

            time.sleep(0.2)

        for zone in DESIGNATED_ZONES:
            self.zone_brightness(zone, 50)

        self.state['notification_running'] = False


    # def smartToggle(self, state):
    #     # print('SmartToggle to HW request', onOff)

    #     # TODO: Test if that is needed, currently leading to timing issue
    #     # if self.state.get('smarttoggle') == onOff.onOff:
    #     #     #ignore
    #     #     print('State is already as requested, ignoring')
    #     #     return onOff

    #     onoff = state.get('onOff')
    #     if onoff == 0:
    #         current_state = deepcopy(self.state)
    #         for k, v in current_state.items():
    #             self.savedState[k] = v

    #         # print('Saved state as', self.savedState)

    #         for zone in zones:
    #             self.zone_switch(zone.get('id'), on_off=0)

    #         self.state['smarttoggle'] = 0

    #     elif onoff == 1:
    #         # print('Saved State:', self.savedState.items())
    #         for k, v in self.savedState.items():
    #             if k in ('preset_1', 'preset_2', 'preset_3', 'smarttoggle', 'zone_0'):
    #                 continue

    #             self.zone_switch(k, v.get('onOff', 0))
    #         self.state['smarttoggle'] = 1
    #     else:
    #         self.state['smarttoggle'] = None
    #         raise ValueError(f'Cannot handle onOff value of {state}')

    #     event_value = EventValues.ON if onoff == 1 else EventValues.OFF
    #     self.event_logger.add_event(
    #         RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_OPERATING_MODE_CHANGE,
    #         0,
    #         event_value
    #     )

    #     return self.state.get('smarttoggle')

    def update_can_state(self, msg_name, can_msg):
        '''
        Received CAN message lighting_broadcast
        {
            'Data1': 'Zone4',
            'Data2': 'Single Color',
            'Data3': '255',
            'Data4': '255',
            'Data5': '255',
            'Data6': '0',
            'Data7': '80',
            'Data8': '100',
            'msg': 'Timestamp: 1671520635.783745    ID: 0cfe20dc    X Rx                DL:  8    04 00 ff ff ff 00 50 64     Channel: canb0s0',
            'msg_name': 'Lighting_Broadcast',
            'instance_key':
            'CFE20DC__Zone4__NA'
        }
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone2', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '80', 'Data8': '100', 'msg': 'Timestamp: 1671520635.788805    ID: 0cfe20dc    X Rx                DL:  8    02 00 ff ff ff 00 50 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone2__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone1', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '80', 'Data8': '100', 'msg': 'Timestamp: 1671520635.794988    ID: 0cfe20dc    X Rx                DL:  8    01 00 ff ff ff 00 50 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone1__NA'}
        Dec 20 07:17:17 WinnConnect  Received CAN message lighting_broadcast {'Data1': 'Zone3', 'Data2': 'Single Color', 'Data3': '36', 'Data4': '36', 'Data5': '36', 'Data6': '219', 'Data7': '100', 'Data8': '100', 'msg': 'Timestamp: 1671520635.798727    ID: 0cfe20dc    X Rx                DL:  8    03 00 24 24 24 db 64 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone3__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone4', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.803945    ID: 0cfe20dc    X Rx                DL:  8    04 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone4__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone3', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.808818    ID: 0cfe20dc    X Rx                DL:  8    03 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone3__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone2', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.813632    ID: 0cfe20dc    X Rx                DL:  8    02 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone2__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone1', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.818642    ID: 0cfe20dc    X Rx                DL:  8    01 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone1__NA'}
        '''
        # TODO: Implement handling of ITC zone status
        # TODO: Fix and bring back if needed

        # print('>>>>>Received CAN message', msg_name, can_msg)
        # # Get which controller DC, DD, DE, DF
        # instance_key = can_msg.get('instance_key')
        # if instance_key is None:
        #     return False, {}

        # pgn = instance_key.split('__')[0]
        # if pgn.endswith('DC'):
        #     controller_id = 1
        # elif pgn.endswith('DD'):
        #     controller_id = 2
        # else:
        #     return False, {}

        # print('>>>>> Lighting Controller', controller_id)
        # # 'Data1': 'Zone4',
        # controller_zone_id = int(can_msg.get('Data1').replace('Zone', ''))
        # # Zones are 1-4 on Controller 1 and 5-8 on Controller 2
        # zone_id = controller_zone_id * controller_id
        # zone_mode =  can_msg.get('Data2')
        # zone_brightness = int(can_msg.get('Data7'))
        # r = int(can_msg.get('Data3'))
        # g = int(can_msg.get('Data4'))
        # b = int(can_msg.get('Data5'))
        # w = int(can_msg.get('Data6'))
        # zone_rgb = f'{r:02X}{g:02X}{b:02X}'
        # print('>>>>> Lighting Zone', zone_id, 'Mode', zone_mode, 'Brightness', zone_brightness, 'rgb', zone_rgb)
        # # Update
        # # Brightness (applies only to RGB, white change in ITC app does not modify this value)

        # if zone_brightness == 0 and zone_rgb == '000000':
        #     self._update_state(zone_id, {'onOff': 0})
        # else:
        #     self._update_state(zone_id, {'onOff': 1})
        #     self._update_state(zone_id, {'brightness': zone_brightness})
        #     self._update_state(zone_id, {'rgb': zone_rgb})

        return False, {}

handler = Lighting()


if __name__ == '__main__':
    print(handler)
    for i in range(1, 11):
        print(handler._get_controller_id_from_zone(i))
