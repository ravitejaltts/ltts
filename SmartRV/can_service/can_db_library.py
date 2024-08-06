import time

import can
import cantools

#msgs, instance_keys = load_databases()

# print(x)

#for msg_id, db in msgs.items():
 #   print(hex(msg_id), db.get_message_by_frame_id(msg_id))
#

class CANbus(object):
    def __init__(self, can_cfg, database):
        print('Initializing CAN bus', can_cfg)
        self.cfg = can_cfg

        counter = 0
        MAX_COUNT = 5
        self.bus = None
        while counter < MAX_COUNT:
            try:
                self.bus = can.ThreadSafeBus(
                    interface='socketcan',
                    channel=self.cfg.get('channel', 'canb0s0'),
                    bitrate=self.cfg.get('bitrate', 250000),
                    timeout=2
                )
                break
            except OSError as err:
                print('Error', err)
                counter += 1
                time.sleep(2)
                continue

        if self.bus is None:
            raise OSError(f'CAN cannot be opened: {self.cfg}')

        self.db = database



    def encode_msg(self, message_name, data, db=None):
        # Try to find message in DBs
        # Unless db is specified
        # Get database per name
        # Find message by name
        # encode data
        # return msg to be sent
        msg = None
        return msg

    def send_msg(can_id, msg):
        # Try sending msg
        pass


def check_czone_heartbeat(source_addr, msg, inventory):
    '''Check if the given heartbeat needs to go into sources.
    CZone source addresses cna change, so a heartbeat message would uniquely
    the CZone device.'''
    CZONE_MAPPING = {
        0x36: {
            'name': 'CXPLUS'
        },
        0x0B: {
            'name': 'SCI'
        },
        0x0D: {
            'name': 'SI'
        },
        0x1D: {
            'name': 'KEYPAD'
        },
        0x30: {
            'name': 'RV1'
        },
        0x10: {
            'name': 'DISPLAY'
        }
    }

    instance = int(msg.get('Instance'))

    if source_addr in inventory:
        # We do not want to override existing inventory
        return

    if instance in CZONE_MAPPING:
        device = CZONE_MAPPING.get(instance, {})
        inventory.update(
            {
                source_addr: {
                    'name': device.get('name', 'UNNAMED CZONE'),
                    'category': 'electrical',
                    'last_seen': None,
                    'stale_interval': 5,
                    'msgs': {}
                }
            }
        )
    else:
        print('[CZONE] Unhandled Instance', instance)
        inventory.update(
            {
                source_addr: {
                    'name': 'UNKNOWN CZONE',
                    'category': 'electrical',
                    'last_seen': None,
                    'stale_interval': 5,
                    'msgs': {}
                }
            }
        )

    print('[CZONE] Handled Instance', hex(instance), inventory.get(source_addr))
