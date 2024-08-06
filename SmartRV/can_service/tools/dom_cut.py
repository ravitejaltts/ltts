import cantools
import can
import time
from datetime import datetime

import csv


DATABASES = {
    # 'atc': {
    #     'db_file': 'dbc/atc.dbc'
    # },
    'careFree_Awning': {
        'db_file': 'dbc/CareFree_Awning.dbc'
    },
    'czone': {
        'db_file': 'dbc/czone.dbc',
    },
    'intermotive': {
        'db_file': 'dbc/InterMotive_1939CM517.dbc'
    },
    'j1939_itc': {
        'db_file': 'dbc/j1939_itc.dbc'
    },
    # 'j1939_Lighting': {
    #     'db_file': 'dbc/J1939_Lighting.dbc'
    # },
    'lippert': {
        'db_file': 'dbc/Lippert.dbc'
    },
    'nmea2k': {
        'db_file': 'dbc/nmea2k.dbc'
    },
    'rvc': {
        'db_file': 'dbc/rvc.dbc'
    },
    'rvc_lithionics': {
        'db_file': 'dbc/rvc_lithionics.dbc'
    },
    # 'tm-630': {
    #     'db_file': 'dbc/TM-630.dbc'
    # },
    'truma': {
        'db_file': 'dbc/Truma.dbc'
    # },
    # 'EcoFlow': {
    #     'db_file': 'dbc/EcoFlow.dbc'
    }
}

def clean_pgn(arbitration_id):
    '''Remove Priority and Source address from arbitration ID.
    This allows to re-use definitions of different sources, such as temp sensors.'''
    priority = (arbitration_id & 0xFE000000) >> 24
    pgn = arbitration_id & 0x01FFFF00
    source_address = arbitration_id & 0xFF
    return pgn

MSG_MAPPING = {}
decoded = {}

for db, db_file in DATABASES.items():
    cur_db = cantools.database.load_file(db_file['db_file'])
    for msg in cur_db.messages:
        MSG_MAPPING[msg.frame_id] = cur_db
        # if msg.name.lower() in default_list:
        #     msg_needed[msg.frame_id] = cur_db


config = {
    'bitrate': 250000,
    'channel': 'canb0s0'
}

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


bus = CANbus(
            can_cfg=config,
            database=MSG_MAPPING
        ).bus

GET_STATE = False
componet_id = None
previous_time_fridge = None
previous_time_freezer = None
temp_states = {}

COMP_MAP = {
    55: 'Fridge 55',
    56: 'Freezer 56',
    57: 'Instance 57',
    58: 'Instance 58',
}

header = ['Instance', 'Temp', 'Time', 'Voltage']

# csv_file_handle = open('Sensor_log.csv', 'a')
# csv_handle = csv.DictWriter(csv_file_handle, fieldnames=header)
# csv_handle
log_file = open(f'sensor_log.txt', 'a')

while True:
    for msg in bus:
        try:
            message = msg.arbitration_id
            source_address = hex(msg.arbitration_id)[-2:]
            db = MSG_MAPPING.get(message)
            msg_name = db.get_message_by_frame_id(message).name

            if msg_name == 'INTERNAL_BATTERY_STATUS':
                if source_address == '9f':
                    decoded = db.decode_message(
                        message, msg.data,
                        allow_truncated=True
                    )
                    instance = decoded.get('Device_Instance')
                    low_voltage = decoded.get('Low_Voltage_Warning')
                    batt_voltage = decoded.get('Battery_Voltage')
                    time_elapse = decoded.get('Time_Elapsed_Since_Last_Report')

                    decoded['report_received'] = datetime.now().strftime("%Y-%m-%d %H:%M")

                    temp_states[instance] = decoded

            elif msg_name == 'THERMOSTAT_AMBIENT_STATUS':
                if source_address == '9F':
                    decoded= db.decode_message(
                        message, msg.data,
                        allow_truncated=True
                    )
                    instance = decoded.get('Instance')
                    if instance in temp_states:
                        # Need to handle this specific next temp reading
                        comp_name = COMP_MAP.get(instance, 'NA')
                        report_data = temp_states.get(instance)
                        if report_data is None:
                            print('Instance data left the dictionary')
                            continue

                        cTemp = decoded.get('Ambient_Temp')
                        fTemp = (cTemp * 9)/5 + 32

                        now = datetime.now().strftime("%Y-%m-%d %H:%M")

                        log = (f'{comp_name} Temp = {cTemp} Deg C, {fTemp} Deg F, Low Voltage Warrning {report_data.get("low_voltage")}, Battery Voltage Report {report_data.get("batt_voltage")}, '
                               f'Time Now {now}, Previous Time {report_data.get("report_received")}, Time Elapse Device Reports : NA\n')
                        print(log)
                        log_file.write(log)
                        del temp_states[instance]

                        # Once done delete from the dict so temps do not get dumped
        except Exception as err:
            print(err)
            continue
