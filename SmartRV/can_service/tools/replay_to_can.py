import time
import datetime

import requests

import can
import cantools


state_host = 'http://localhost:8000/api/can/event/{system}'

SEND_TO_CAN = True


# Copied from can_helper.py
def clean_pgn(arbitration_id):
    '''Remove Priority and Source address from arbitration ID.
    This allows to re-use definitions of different sources, such as temp sensors.'''
    priority = (arbitration_id & 0xFE000000) >> 24
    pgn = arbitration_id & 0x01FFFF00
    source_address = arbitration_id & 0xFF
    return pgn


def send_state(msg_name, msg):
    to_send = {}
    to_send = {k: str(v) for (k, v) in msg.items()}
    to_send['msg_name'] = msg_name

    url = state_host.format(system=msg_name.lower())

    requests.put(url, json=to_send, timeout=0.5)


def detect_file_type(filename):
    '''Detect if the given input file is busmaster,
    SavvyCAN or candump with or without timestamps.'''
    is_busmaster = False
    is_candump = False
    has_timestamps = False

    with open(filename, 'r') as data:
        for line in data:
            if line.startswith('***') and 'BUSMASTER' in line:
                is_busmaster = True
                break

    detected = None
    if is_busmaster:
        detected = 'BUSMASTER'
    elif is_candump:
        detected = 'CANDUMP'

    return detected


def decode_busm_timestamp(timestamp):
    '''15:14:54:7855'''
    epoch = datetime.datetime(1900, 1, 1)
    return (datetime.datetime.strptime(
        timestamp,
        "%H:%M:%S:%f"
    ) - epoch).total_seconds()


def decode_candump(filename, can_bus, timestamps=True, factor=1, pause=None):
    start_time = None
    # factor = 1          # >1 slower, <1 faster
    # pause = None        # Seconds or None, if <=0 wait for input

    error_pgns = []

    print(f'Running Log Replay for {in_file}')
    start = time.time()
    with open(filename, 'r') as candata:
        for line in candata:
            try:
                if line.strip():
                    print(line.strip())
                    try:
                        timestamp, _bus, arb_id, length, data = line.strip().split('  ')
                    except ValueError as err:
                        print(err)
                        print(line)
                        continue
                    timestamp = float(timestamp.strip().replace('(', '').replace(')', ''))

                    if start_time is None:
                        start_time = timestamp

                    offset = timestamp - start_time

                    while time.time() < (start + (offset * factor)):
                        time.sleep(0.0001)

                    arb_id = int(arb_id.strip(), 16)
                    # data = data.strip().encode('utf8')
                    data = [int(i, 16) for i in data.split(' ')]

                    if len(data) < 8:
                        for i in range(8 - len(data)):
                            data.append(0xff)

                    data = bytes(data)

                    pgn = clean_pgn(arb_id)

                    if pgn in msg_mapping:
                        db = msg_mapping[pgn]
                    else:
                        db = None

                    decoded = False
                    msg_name = None

                    if db is None:
                        print('No database for for ', hex(pgn), arb_id, ' '.join([f'{x:02X}' for x in data]))
                        continue

                    try:
                        msg_name = db.get_message_by_frame_id(pgn).name
                        print('MSG NAME', msg_name)
                        decoded = db.decode_message(
                            pgn,
                            data,
                            allow_truncated=True
                        )
                        # if msg_name == 'THERMOSTAT_AMBIENT_STATUS':
                        #     print(pgn, msg_name, decoded)
                        #     input()
                    except KeyError as err:
                        print('KeyError', err)
                        error_pgns.append(pgn)
                        continue
                    except Exception as err:
                        print(hex(pgn), err, line, data)
                        input()
                        continue

                    if decoded is not False:
                        print(hex(pgn), msg_name, decoded)
                        # input('Enter to send')
                        send_state(msg_name, decoded)
                    # handler.send(arb_id, data)
                    if SEND_TO_CAN is True:
                        msg = can.Message(
                            arbitration_id=arb_id,
                            data=data,
                            is_extended_id=True
                        )
                        can_bus.send(msg)
                    print('.', end='', flush=True)

            except KeyboardInterrupt:
                break

            if pause is not None:
                if pause <= 0:
                    input('Press ENTER to send next message')
                else:
                    time.sleep(pause)

    print(f'\n\nIteration took: {time.time() - start} seconds')
    for err in set(error_pgns):
        print(hex(err))


def decode_busmaster(filename, can_bus, factor=1, pause=None):
    start = time.time()
    start_time = None
    # factor = 1          # >1 slower, <1 faster
    # pause = None        # Seconds or None, if <=0 wait for input

    error_pgns = []

    with open(filename, 'r') as candata:
        for line in candata:
            try:
                line = line.strip()
                if line:
                    if line.startswith('***'):
                        continue

                    '''15:15:24:3845 Rx 1 0x19FE9964 x 8 01 F2 FF FF FF FF FF FF'''
                    try:
                        timestamp, direction, _, arb_id, _, length, data = line.split(' ', maxsplit=6)
                    except ValueError as err:
                        print(err)
                        print(line)
                        print(len(line.split(' ')))
                        raise
                    timestamp = decode_busm_timestamp(timestamp)

                    if start_time is None:
                        start_time = timestamp

                    offset = timestamp - start_time

                    while time.time() < (start + (offset * factor)):
                        time.sleep(0.0001)

                    arb_id = int(arb_id.strip(), 16)
                    # data = data.strip().encode('utf8')
                    data = [int(i, 16) for i in data.split(' ')]

                    if len(data) < 8:
                        for i in range(8 - len(data)):
                            data.append(0xff)

                    data = bytes(data)

                    pgn = clean_pgn(arb_id)

                    if pgn in msg_mapping:
                        db = msg_mapping[pgn]
                    else:
                        db = None

                    decoded = False
                    msg_name = None

                    if db is None:
                        print('No database for for ', hex(pgn), arb_id, ' '.join([f'{x:02X}' for x in data]))
                        continue

                    try:
                        msg_name = db.get_message_by_frame_id(pgn).name
                        print('MSG NAME', msg_name)
                        decoded = db.decode_message(
                            pgn,
                            data,
                            allow_truncated=True
                        )
                        # if msg_name == 'THERMOSTAT_AMBIENT_STATUS':
                        #     print(pgn, msg_name, decoded)
                        #     input()
                    except KeyError as err:
                        print('KeyError', err)
                        error_pgns.append(pgn)
                        continue
                    except Exception as err:
                        print(hex(pgn), err, line, data)
                        input()
                        continue

                    if decoded is not False:
                        print(hex(pgn), msg_name, decoded)
                        # input('Enter to send')
                        send_state(msg_name, decoded)
                    # handler.send(arb_id, data)
                    if SEND_TO_CAN is True:
                        msg = can.Message(
                            arbitration_id=arb_id,
                            data=data,
                            is_extended_id=True
                        )
                        can_bus.send(msg)
                    print('.', end='', flush=True)

            except KeyboardInterrupt:
                break

            if pause is not None:
                if pause <= 0:
                    input('Press ENTER to send next message')
                else:
                    time.sleep(pause)

    print(f'\n\nIteration took: {time.time() - start_time} seconds')
    for err in set(error_pgns):
        print(hex(err))


# Load databases in increasing specificity (start with generic and then overwrite existing messages that have the same PGN)
DATABASES = {
    'rvc': cantools.database.load_file('../dbc/rvc.dbc'),
    'nmea2k': cantools.database.load_file('../dbc/nmea2k.dbc'),
    'czone': cantools.database.load_file('../dbc/czone.dbc'),
    'itc': cantools.database.load_file('../dbc/j1939_itc.dbc')
}

msg_mapping = {}

for db_name, db in DATABASES.items():
    print(db_name, 'Messages', db.messages)

    for msg in db.messages:
        msg_mapping[msg.frame_id] = db


if __name__ == '__main__':
    import sys
    in_file = sys.argv[1]

    # Detect input type
    file_type = detect_file_type(in_file)
    print('Filetype', file_type)

    CAN_BUS = 'canb0s0'
    CAN_BITRATE = 250000

    canbus = can.ThreadSafeBus(
        interface='socketcan',
        channel=CAN_BUS,
        bitrate=CAN_BITRATE,
        timeout=2
    )

    if file_type == 'BUSMASTER':
        decode_busmaster(in_file, canbus)
    elif file_type == 'CANDUMP':
        decode_candump(in_file, canbus)
    else:
        print('[ERROR] Cannot detect file type')
        sys.exit(1)
