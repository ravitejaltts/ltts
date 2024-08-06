import json
import time

import cantools
import can

from can_service.can_db_library import (
    CANbus,
    check_czone_heartbeat
)
from common_libs.clients import CAN_CLIENT


# MSG_MAPPING = {}
# INSTANCE_KEYS = {}

# Seconds
CAN_RETRY_TIMEOUT = 1
CAN_BUS_TIMEOUT = 5     # Seconds between the last can message received and now during check

MAIN_EVENT_URL = 'http://localhost:8000/event_log'

# Interval in which we check for stale CAN messages, if a state has not been updated for
# the given period of time, we might need to trigger a stale data alert to the main service
STALE_CHECK_INTERVAL = 10

# Resend even unchanged messages if last time they were sent is longer than that ago
RESEND_INTERVAL = 30

UPDATE_IGNORE_KEYS = (
    'msg',  # This is the full message incl. timestamp, so changes
    'Sequence_ID',  # We are not using this and it changes
    'DC_Type'   # Strange CZone behavior as it should not change
)

# TODO: Get these from the HW layer for the specific model
IMPORTANT_MESSAGES = [
    # All thermostat readings
    'THERMOSTAT_AMBIENT_STATUS',      # No longer needed due to the 30 seconds resend or have a smaller resend timer for this message ?
    # ALL DM_RV messages
    'rvswitch',
    # 'DM_RV',
    # Dometic Thermistor reporting
    '19FF9CCF__0__4',
    # AC Current Meter and LVL detection
    '19F21101__0__14',
    '19F21101__0__15',
    # TODO: Make this ** capable as well
    '19F21102__0__14',
    '19F21102__0__15',
    # TODO: Make this ** capable as well
    '19F21100__0__14',
    '19F21100__0__15',
    # TESTING AREA
    '18FF918F__0__1',
    # Need all light switches RV1 and SI
    #'1CFF0497__0__48',
    #'1DFF0997__0__48',
    # Debugging / Dev
    # 'LIGHTING_BROADCAST'
    # Keypad Heatbeat
    # '1CFF0400__0__29',
]

# Want to pass this always now
# 0x1CFF0400

MSG_EXPECTATION_TIMER = {
    # Instance Key to expect
    # TODO: Get from HW layer / Vehicle template
    # Seconds
    # Fridge Temp 848EC/R
    '19FF9C9F': {
        'timer_stale': 10,
        'timer_startup': 60,
        'callback': None,
        'args': None
    }
}

STALE_DEFAULT_TIMER = 30
STARTUP_DEFAULT_TIMER = 60

# TODO: Just a test if that speeds up processing, would pull that from main service on start
DEFAULT_SUPPORTED_MSG = {
    "fluid_level": "watersystems",
    "lighting_broadcast": "lighting",
    "heartbeat": "electrical",
    "rvswitch": "electrical",
    "rvoutput": "electrical",
    "roof_fan_status_1": "climate",
    "ambient_temperature": "climate",
    "thermostat_ambient_status": "climate",
    "dc_source_status_1": "energy",
    "dc_source_status_2": "energy",
    "dc_source_status_3": "energy",
    "battery_status": "energy",
    "prop_bms_status_6": "energy",
    "prop_bms_status_1": "energy",
    "prop_module_status_1": "energy",
    "inverter_ac_status_1": "energy",
    "inverter_status": "energy",
    "charger_ac_status_1": "energy",
    "charger_ac_status_2": "energy",
    "charger_status": "energy",
    "charger_status_2": "energy",
    "charger_configuration_status": "energy",
    "charger_configuration_status_2": "energy",
    "solar_controller_status": "energy",
    "vehicle_status_1": "vehicle",
    "vehicle_status_2": "vehicle",
    "state_of_charge": "vehicle",
    "dc_charging_state": "vehicle",
    "pb_park_brake": "vehicle",
    "tr_transmission_range": "vehicle",
    "odo_odometer": "vehicle",
    "aat_ambient_air_temperature": "vehicle",
    "vin_response": "vehicle",
    "dc_dimmer_command_2": "electrical",
    "waterheater_status": "watersystems",
    "waterheater_status_2": "watersystems",
    "prop_tm620_config_status":"watersystems",
    "awning_status": "movables",
    "awning_status_2": "movables",

    "dm_rv": "system",
}

DYNAMIC_SOURCES = {
    # PGN, func should respond with an
    # object that fits the state checker below
    0xFF04: {
        'func': check_czone_heartbeat
    }
}

DEFAULT_STALE_CONFIG = {
    0x46: {
        'name': 'BMS',              # friendly name
        'category': 'energy',
        'last_seen': None,          # Will be updated later
        'stale_interval': 5,        # Seconds
        'msgs': {}                  # TODO: Add later
    },
    0x42: {
        'name': 'Inverter',
        'category': 'energy',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0x64: {
        'name': 'TM-620',
        'category': 'watersystems',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    # 0x01: {         # Changed to 02 as Dom home is the only outlier
    #     'name': 'SI',
    #     'category': 'electrical',
    #     'last_seen': None,
    #     'stale_interval': 5,
    #     'msgs': {}
    # },
    # 0x02: {         # Changed to 02 as Dom home is the only outlier
    #     'name': 'SI',
    #     'category': 'electrical',
    #     'last_seen': None,
    #     'stale_interval': 5,
    #     'msgs': {}
    # },
    # 0x00: {
    #     'name': 'KEYPAD',
    #     'category': 'electrical',
    #     'last_seen': None,
    #     'stale_interval': 5,
    #     'msgs': {}
    # },
    0xFA: {
        'name': 'TM-1010',
        'category': 'energy',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0xDC: {
        'name': 'VersiControl ITC Controller',
        'category': 'lighting',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    # 0x97: {
    #     'name': 'RV1',
    #     'category': 'electrical',
    #     'last_seen': None,
    #     'stale_interval': 5,
    #     'msgs': {}
    # },
    0xCF: {
        'name': 'TRUMA AC',
        'category': 'climate',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0xCC: {
        'name': 'Dometic GW - BATH',
        'category': 'climate',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0xCD: {
        'name': 'Dometic GW - LOUNGE',
        'category': 'climate',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0xBF: {
        'name': 'Awning DRC12',
        'category': 'movables',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0xDF: {
        'name': 'Awning DRCHub',
        'category': 'movables',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0x8F: {
        'name': 'Awning DRCMoLED',
        'category': 'movables',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    },
    0x80: {
        'name': 'Wakespeed WS500',
        'category': 'energy',
        'last_seen': None,
        'stale_interval': 5,
        'msgs': {}
    }
}


# TODO: Move this to a config file
# ------------------------------------------------------------
def load_all_databases(default_list=None):
    DATABASES = {
        'nmea2k': {
            'db_file': 'dbc/nmea2k.dbc',
            # Instance keys are tightly coupled with dbc naming
            'instance_keys': {
                # Fluid
                0x1f21100: 'nmea2k__Fluid_Instance',
                # Temperature
                0x1fd0c00: 'nmea2k__Temperature_Instance',
                # Binary Bank Status
                0x1f20d00: 'nmea2k__Binary_Device_Bank_Instance'
            }
        },
        'j1939_itc': {
            'db_file': 'dbc/j1939_itc.dbc',
            # Instance keys are tightly coupled with dbc naming
            'instance_keys': {
                # Zone per Controller, controllers are separated by arbitration ID
                0xfe2000: 'Data1'
            }
        },
        'rvc': {
            'db_file': 'dbc/rvc.dbc',
            # Instance keys are tightly coupled with dbc naming
            'instance_keys': {
                # Zone per Controller, controllers are separated by arbitration ID
                0x1fea700: 'rvc__roof_fan_status_1',
                0x1ff9c00: 'rvc__ambient_temperature',
            }
        },
        'lithionics': {
            'db_file': 'dbc/rvc_lithionics.dbc',
            'instance_keys': {}
        },
        'czone': {
            'db_file': 'dbc/czone.dbc',
            'instance_keys': {
                0xff0400: 'czone__Heartbeat'
            }
        },
        'intermotive': {
            'db_file': 'dbc/InterMotive_1939CM517.dbc',
            'instance_keys': {}
        },
        'tm-6x0': {
            'db_file': 'dbc/TM-630.dbc',
            'instance_keys': {
            }
        }
    }

    msg_mapping = {}
    instance_keys = {}
    msg_needed = {}

    main_db = None

    for db, db_file in DATABASES.items():
        if main_db is None:
            main_db = cantools.database.load_file(db_file['db_file'])
        else:
            main_db.add_dbc_file(db_file['db_file'])

    for msg in main_db.messages:
        msg_mapping[msg.frame_id] = main_db
        if msg.name.lower() in default_list:
            msg_needed[msg.frame_id] = main_db

        for k, v in db_file['instance_keys'].items():
            instance_keys[k] = v

    try:
        main_can_file = open('/storage/wgo/main_can.dbc', 'w')
        main_can_file.write(main_db.as_dbc_string())
    except Exception as err:
        print(err)
        print(main_db.as_dbc_string())

    return msg_mapping, instance_keys, msg_needed
# ------------------------------------------------------------

# MSG_MAPPING, INSTANCE_KEYS = load_databases()


def clean_pgn(arbitration_id):
    '''Remove Priority and Source address from arbitration ID.
    This allows to re-use definitions of different sources, such as temp sensors.'''
    priority = (arbitration_id & 0xFE000000) >> 24
    pgn = arbitration_id & 0x01FFFF00
    source_address = arbitration_id & 0xFF
    return pgn


def pgn_full(arbitration_id):
    '''Remove Priority and Source address from arbitration ID.
    This allows to re-use definitions of different sources, such as temp sensors.'''
    priority = (arbitration_id & 0xFE000000) >> 24
    pgn = arbitration_id & 0x01FFFF00
    source_address = arbitration_id & 0xFF
    return priority, pgn, source_address


def increment_stats(msg_id, stats):
    hex_id = f'{msg_id:08X}'
    if hex_id in stats:
        stats[hex_id] += 1
    else:
        stats[hex_id] = 1

    stats[f'{hex_id}_last_update_time'] = time.time()


def generate_instance_key(arb_id, msg, instance_keys):
    '''For given message check if msg contains instance info.
    This will generate a key for the state that is unique per instance.'''
    # Get arb_id
    # Check known instance_keys
    instance = instance_keys.get(clean_pgn(arb_id))
    instance_value = msg.get(instance, 0)

    # Look for Instance in the CAN message to uniquely identify
    # this message from the same sender
    # Relevant for several things like ITC controller, RV1 and instances from TM-1010
    payload_instance = msg.get(
        'Instance',
        msg.get('DSA', 'NA')    # DM_RV Messages
    )

    instance_key = f'{arb_id:02X}__{instance_value}__{payload_instance}'

    msg['instance_key'] = instance_key

    return instance_key


def parse_can(msg):
    '''Parse basic message and pass on to decode.'''
    # Get priority
    # Get PGN
    # Get source address
    arb_id = msg.arbitration_id
    # Dissect
    data = msg.data
    channel = msg.channel

    return {
        'arbitration_id': '{0:02X}'.format(arb_id),
        'priority': '{0}'.format((arb_id & 0xf8000000) >> 24),
        'pgn': '{0:02X}'.format((arb_id & 0x01ffff00) >> 8),
        'pgn_dec': '{0}'.format((arb_id & 0x01ffff00) >> 8),
        'pgn_raw': arb_id & 0x01ffff00,
        'source_address': '{0:02X}'.format(arb_id & 0xff),
        'source_address_dec': '{0}'.format(arb_id & 0xff),
        'data': data,
        'channel': channel,
        'type': 'J1939',
        'is_rx': msg.is_rx,
        'timestamp': msg.timestamp
    }


class CanHandler:
    def __init__(self, config: dict) -> None:
        global default_supported_msg
        self.config = config
        self.logger = config.get('logger')
        self.logger.debug('Started logging in CAN Handler')

        self.load_databases(DEFAULT_SUPPORTED_MSG)

        # Initialize HW specific state, initial readouts etc.
        self.state = {}
        self.msg_statistics = {}
        self.msg_name_statistics = {}
        self.msg_stale_map = MSG_EXPECTATION_TIMER
        self.inventory = {}     # Keeps track of source address and pgns
        self.msg_received_list = {}
        # TODO: Set this with the config from main specific to the vehicle
        self.set_stale_checker()

        self.bus = CANbus(
            can_cfg=self.config,
            database=self.MSG_MAPPING
        ).bus

        self.running = True
        self.last_stale_check = 0
        self.started_read_loop = None
        self.last_can_received_time = None
        self.can_bus_health_ok = True

        self.debug_decoder = {}

    def load_databases(self, filter_dict):
        self.MSG_MAPPING, self.INSTANCE_KEYS, self.MSG_NEEDED = load_all_databases(
            default_list=filter_dict
        )

    def set_stale_checker(self, config=None):
        '''Set the stale checker dictionary'''
        print('Init Stale Check Inventory')
        self.inventory = {}
        if config is None:
            for key, value in DEFAULT_STALE_CONFIG.items():
                # Default to stale None
                value['stale'] = None
                self.inventory[key] = value

    def set_filter(self, can_filter: dict):
        '''key:values of messages we do want.'''
        new_filter = []
        for key, value in can_filter.items():
            new_filter.append(key)

        self.load_databases(new_filter)
        # TODO: Do we need a lock ?
        # self.MSG_NEEDED = new_filter

        # TODO: Change this to PGN once we have clarity on how to have specific OGN filters created

    def init_can_bus(self):
        '''Send required initialization commands so that the canbus properly comes up
        and initial states are available to the system. '''
        print('Inititalizing CAN bus')
        self.bus = CANbus(
            can_cfg=self.config,
            database=self.MSG_MAPPING
        ).bus

    def shutdown_can_bus(self):
        pass

    async def stale_msg_check(self):
        '''Check if any messages are stale that need to be received in a fixed interval for the sytem to operate.
        Example is the ambient temperature used for the climate controls.'''
        msg = f'Running Stale msg check at: {time.time()}'
        self.logger.debug(msg)

        is_stale = False

        # Check when last check was done
        # 19FF9C9F
        try:
            now = time.time()
            if self.last_can_received_time is not None:
                delta = now - self.last_can_received_time
                if delta > CAN_BUS_TIMEOUT:
                    print(f'CAN bus seems dead, no message for {delta} seconds')
                    self.can_bus_health_ok = False
                    # TODO: Make this httpx
                    try:
                        _ = await CAN_CLIENT.put(
                            MAIN_EVENT_URL, data={
                                'timestamp': now,
                                'event': 8813,
                                'instance': 0,
                                'value': True,
                                'meta': {}
                            },
                            timeout=0.5
                        )
                    except Exception as err:
                        print(err)

                else:
                    if self.can_bus_health_ok is False:
                        # TODO: Send positive message only if we recovered from a CAN bus issue
                        print('CAN bus 0 transitioned to OK from Failure')
                        pass
                    self.can_bus_health_ok = True

            # Iterate over inventory

            now = time.time()
            for source, details in self.inventory.items():
                stale_interval = details.get('stale_interval')
                if stale_interval is not None:
                    last_seen = details.get('last_seen')
                    if last_seen is None:
                        print(f'[STALE] Never seen this device yet: {details.get("name")} / {source:02X}')
                    else:
                        if now - last_seen > stale_interval:
                            print(f'[STALE] Device turned stale: {details.get("name")} / {source:02X}')
                            is_stale = True
                            details['stale'] = True
                        else:
                            # We are good ? At least not stale
                            print(f'[STALE] Device OK: {details.get("name")} / {source:02X} / {details}')
                            stale = details.get('stale')
                            if stale is True:
                                # Device recovered, need to set flag
                                details['recovered'] = True
                            else:
                                details['recovered'] = False

                            details['stale'] = False
                else:
                    # We cannot be stale, so nothing to do
                    print('[STALE] No stale interval set', hex(source), details)

            # for msg, cfg in MSG_EXPECTATION_TIMER.items():
            #     if msg in self.msg_statistics:
            #         last_updated = self.msg_statistics.get(msg + '_last_update_time')
            #         if last_updated is None:
            #             self.logger.debug(f'No update time yet: {msg}')
            #             continue

            #         if (now - last_updated) > cfg.get('timer_stale', STALE_DEFAULT_TIMER):
            #             self.logger.debug(f'MSG is stale: {msg}')
            #             if cfg.get('callback') is not None:
            #                 args = cfg.get('args', [])
            #                 callback = cfg.get('callback')
            #                 callback(*args)
            #             else:
            #                 self.logger.debug('Callback not set')
            #     else:
            #         # TODO: Figure out how to handle the message missing completely, likely compare expected time from startup
            #         self.logger.debug(f'{msg} not yet received')
            #         if (now - self.started_read_loop) > cfg.get('timer_startup', STARTUP_DEFAULT_TIMER):
            #             self.logger.debug(f'{msg} not received within required time')

            self.last_stale_check = time.time()
        except Exception as err:
            self.logger.error(f'Error when running stale check: {err}')
            print('Error when running stale check', err)

        return is_stale

    def read_loop(self, callback):
        '''After setup, main loop to run.
        Callback will be run to determine further action on a CAN packet'''
        self.started_read_loop = time.time()
        msg_count = 0
        undecoded_msg_count = 0
        decoded_msg_count = 0
        # for msg in self.bus:
        while True:
            # Check if it should continue
            if self.running is False:
                self.logger.debug('Ending read loop')
                self.shutdown_can_bus()
                break

            for msg in self.bus:
                msg_count += 1
                if msg_count % 100 == 0:
                    print('MSG received', msg_count)

                try:
                    if msg is None:
                        self.logger.debug(f'MSG without can ?, {msg}')
                        continue

                    self.last_can_received_time = time.time()

                    increment_stats(msg.arbitration_id, self.msg_statistics)
                    # Get a re-usable PGN
                    # We only process messages that are in the mapping
                    # if pgn_clean in self.MSG_MAPPING:
                    decode_pgn = msg.arbitration_id
                    source_address = msg.arbitration_id & 0xFF

                    # Check if the PGN is found without cleaning it (preferred for specific filtering)
                    if decode_pgn not in self.MSG_NEEDED:
                        decode_pgn = clean_pgn(msg.arbitration_id)

                    if decode_pgn in self.MSG_NEEDED:
                        db = self.MSG_NEEDED.get(decode_pgn)
                        decoded = db.decode_message(
                            decode_pgn, msg.data,
                            allow_truncated=True
                        )

                        decoded_msg_count += 1
                        if decoded_msg_count % 20 == 0:
                            print('Decoded MSG count', decoded_msg_count)

                        msg_name = db.get_message_by_frame_id(decode_pgn).name

                        decoded['msg'] = msg
                        decoded['msg_name'] = msg_name
                        decoded['source_address'] = f'{source_address:02X}'

                        # TODO: Check if any component needs dynamic source address detection
                        # TODO: Handle exceptions properly
                        # print('DYNAMIC_FUNC', hex(decode_pgn >> 8))
                        dynamic_source = DYNAMIC_SOURCES.get(decode_pgn >> 8)
                        if dynamic_source is not None:
                            dynamic_func = dynamic_source.get('func')
                            _ = dynamic_func(source_address, decoded, self.inventory)

                        # Update state and inventory with this decoded message
                        instance_key, updated = self.update_state(decoded)

                        if instance_key not in self.msg_received_list:
                            self.msg_received_list[instance_key] = decoded

                        # TODO: Add checking for updates in some messages only
                        if updated is False and (
                                    instance_key in IMPORTANT_MESSAGES or
                                    msg_name in IMPORTANT_MESSAGES):

                            # Modify this to allow for time intervals on reporting
                            updated = True

                        elif (time.time() - self.msg_received_list[instance_key].get('last_sent_to_main', 0)) > RESEND_INTERVAL:
                            # We want to send messages anyway, even if unchanged every X seconds
                            print('[CAN] Resending unchanged message', instance_key)
                            updated = True

                        if updated is True:
                            result = callback(decoded)
                            print('[CAN][API][QUEUE] Length', result)
                            # Update the time we updated main service
                            self.msg_received_list[instance_key]['last_sent_to_main'] = time.time()

                    else:
                        undecoded_msg_count += 1
                        if undecoded_msg_count % 100 == 0:
                            print('Undecoded messages', undecoded_msg_count)
                        # Add to device stats ?
                        # self.update_inventory(msg)

                except can.CanError as err:
                    # : Error receiving: [Errno 100] Network is down
                    self.logger.error(f'CANError: {err}')
                    time.sleep(CAN_RETRY_TIMEOUT)
                    self.init_can_bus()
        return

    def update_inventory(self, msg):
        '''Update internal inventory that can be pulled for stale check or
        last known messages.'''
        arb_id = msg.arbitration_id
        source_address = arb_id & 0xFF
        pgn = (arb_id & 0x01FFFF00) >> 8

        # if source_address not in self.inventory:
        #     print('[CZONE] Inventory', hex(source_address))
        #     # Set the default setting
        #     self.inventory[source_address] = {
        #         'name': f'UNHANDLED_{source_address:02X}',
        #         'last_seen': time.time(),
        #         'stale_interval': None,
        #         'msgs': {}
        #     }
        # else:
        #     self.inventory[source_address]['last_seen'] = time.time()

        # NOTE: Not sure what we what want to do with messages
        # that are not in the inventory
        if source_address in self.inventory:
            self.inventory[source_address]['last_seen'] = time.time()
        else:
            return arb_id, source_address, pgn

        if pgn not in self.inventory[source_address]['msgs']:
            self.inventory[source_address]['msgs'][pgn] = {
                'last_received': time.time()
            }
        else:
            self.inventory[source_address]['msgs'][pgn]['last_received'] = time.time()

        print(f'[INVENTORY] Updated inventory for: {source_address:02X}', hex(arb_id), hex(pgn))

        return arb_id, source_address, pgn

    def update_state(self, msg, emit_same=False):
        '''Checks if given message state has updated or not.'''
        changed = False
        print('[CAN][INVENTORY][update_state] Updating inventory for', hex(msg.get('msg').arbitration_id))
        arb_id, source_address, pgn = self.update_inventory(msg.get('msg'))
        print('[CAN][INVENTORY][update_state] Success')

        # Instance key does not account for in message instances for e.g. fluid levels
        instance_key = generate_instance_key(arb_id, msg, self.INSTANCE_KEYS)
        # Check if msg_id already exists
        # Check if instance key exists
        if instance_key in self.state:
            # Compare
            cur_state = self.state.get(instance_key)
            if cur_state is None:
                raise ValueError(f'Current state for arbitration ID: {instance_key} missing')

            for key, value in msg.items():
                # TODO: Validate we can 'safely' ignore Sequence_Id of NMEA2K / RVC
                if key in UPDATE_IGNORE_KEYS:
                    continue

                if key in cur_state:
                    if cur_state[key] != value:
                        # print('Key update:', key, 'Old:', cur_state[key], 'New:', value)
                        changed = True
                        break
                else:
                    changed = True
                    break
        else:
            # Create new
            changed = True

        if changed is True:
            self.state[instance_key] = msg

        return instance_key, changed

    def get_state(self):
        '''Get the current state of the CAN service'''
        return self.state

    def get_statistics(self, msg_id=None):
        '''Get all statistics or a specific msg.'''
        if msg_id is None:
            return self.msg_statistics
        else:
            return self.msg_statistics.get(msg_id)

    def reset_state(self):
        '''Delete state for all keys.'''
        key_list = []
        for key, value in self.state.items():
            print(key, value)
            key_list.append(key)

        for key in key_list:
            del(self.state[key])


if __name__ == '__main__':
    config = {
        'bitrate': 250000,
        'channel': 'canb0s0'
    }
    handler = CanHandler(config)
    handler.read_loop()
