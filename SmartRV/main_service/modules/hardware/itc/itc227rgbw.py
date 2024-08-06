'''Module for ITC lighting controllers.'''

import subprocess


# TODO: Provide HMI / Main handler to issue CAN commands
# TODO: Common interface for can inputs for CAN enabled devices


ZONE_TO_BIT = {
    0: 255, # All Zones
    1: 1,
    2: 2,
    3: 4,
    4: 8
}

CONTROLLER_ID_TO_ADDR = {
    # 0: (0xFF, 0xFF),    # All controllers
    # 1: (0x20, 0xDC),
    # 2: (0x20, 0xDD),
    # 3: (0x20, 0xDE),
    # 4: (0x20, 0xDF)
    0: 'FFFF',    # All controllers
    1: '20DC',
    2: '20DD',
    3: '20DE',
    4: '20DF'
}

MODES = {
    'WHITE': 0x80,
    'RGB': 0x00
}

class ITC(object):
    def __init__(self, cfg={}):
        self.cfg = cfg
        self.state = {}
        self.zones = {}
        self.zone_mapping = {}
        self.init_config()
        # 'zone_1_R_onOff'
        # 'zone_1_R_brt'
        # Iterate over zones that apply and create states
        print('ITC State', self.state)

    def init_config(self):
        controller_id = self.cfg.get('controller_id')
        print(f'Controller id = {controller_id}')
        #self.controller_id = CONTROLLER_ID_TO_ADDR.get(controller_id)
        self.controller_id =  '20DC'

        if self.controller_id is None:
            raise ValueError(f'Error initializing controller ID: {controller_id}')

        zones = self.cfg.get('zones')
        if zones is None:
            raise ValueError('No zones specified')

        for zone in zones:
            zone_key = f'zone_{zone.get("itc_zone")}'
            if 'channel' in zone:
                # Using single channel
                map_value = f"{zone.get('itc_zone')}{zone.get('channel')}"
                if self.state.get(zone_key) is None:
                    self.state[zone_key] = {
                        zone.get('channel'): zone.get('state')
                    }
                else:
                    self.state[zone_key][zone.get('channel')] = zone.get('state')
            else:
                # Full RGBW light
                self.state[zone_key] = zone.get('state')
                map_value = zone.get('itc_zone')

            self.zone_mapping[zone.get('instance')] = map_value

    def configure(self, cfg):
        '''Configure Lighting module.'''
        pass

    def handle_can_input(self, can_msg):
        '''Handle CAN messages.'''
        pass

    def zone_onOff(self, zone_id, onOff):
        '''Switches an ITC zone on / off depending on the type.'''
        # Set the color
        # TODO: check white value might be needed (it will make it more bright but less to the set color)
        # Get the current values that are not affected
        # Apply the value that applies to the channel affected
        # Assemble command to send

        # internal_zone = self.zone_mapping.get(zone_id)
        # print('Internal Zone', internal_zone)
        zone = self.state.get(f'zone_1')
        print('Zone', zone)

        r = zone.get('R')
        r_onOff = r.get('onOff')
        if onOff == 0:
            r_value = 0
        elif onOff == 1:
            r_brt = r.get('brt')
            print(r_brt)
            r_value = int(256 / 100 * r_brt)
            if r_value > 255:
                r_value = 255
            print(r_value)

        g_value = 0
        b_value = 0
        w_value = 0

        rgb_value = f'{r_value:02X}{g_value:02X}{b_value:02X}'
        cmd = f'cansend canb0s0 0CFC0044#{self.controller_id}01{zone_id:02X}01000000'
        print(cmd)
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True
        )

    def zone_brightness(self, zone_id, brt):
        pass

    def zone_rgb(self, zone_id, rgb):
        pass

    def zone_clrTmp(self, zone_id, clrTmp):
        pass


if __name__ == '__main__':
    zones = [
        {
            'id': 1,
            'instance': 1,

            'type': 'SIMPLE_DIM',
            'name': 'Hallway',
            'description': '',
            'code': 'lz',

            'controller_type': 'ITC 227X-RGBW',
            # TODO: Can we only work with the controller_type and look up the rest
            # from the component definition
            'controller': 1,
            'state': {
                'onOff': 0,
                'brt': 100
            },
            'itc_zone': 1,
            'channel': 'R'
        },
        {
            'id': 4,
            'instance': 4,

            'type': 'SIMPLE_DIM',
            'name': 'Haly',
            'description': '',
            'code': 'lz',

            'controller_type': 'ITC 227X-RGBW',
            # TODO: Can we only work with the controller_type and look up the rest
            # from the component definition
            'controller': 1,
            'state': {
                'onOff': 0,
                'brt': 100
            },
            'itc_zone': 1,
            'channel': 'W'
        }
    ]
    cfg = {
        'controller_id': 1,
        'zones': zones
    }
    import time
    itc_handler = ITC(cfg)
    print(itc_handler)
    print(itc_handler.zone_mapping)
    itc_handler.zone_onOff(1, 0)
    time.sleep(2)
    itc_handler.zone_onOff(1, 1)
    time.sleep(2)
    itc_handler.zone_onOff(1, 0)
