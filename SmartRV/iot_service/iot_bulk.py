import os
import time
import json
import platform
import logging
from common_libs import environment
from datetime import datetime
from logging.handlers import RotatingFileHandler

_env = environment()

TELEMETRY_MAX_FILE_SIZE = 50000
TELEMETRY_BACKUP_FILE_CNT = 6

M1_FILE_NAME = "m1_bulk_telemetry"
BULK_FILE_PRE = "bulk_evt_0_mver_1."
M2_FILE_NAME = "m2_bulk_event"

m1_bulk_handler = RotatingFileHandler(
    _env.storage_file_path(f'{M1_FILE_NAME}.stor'),
    "a+",
    maxBytes=TELEMETRY_MAX_FILE_SIZE,
    backupCount=TELEMETRY_BACKUP_FILE_CNT,
)

m2_bulk_handler = RotatingFileHandler(
    _env.storage_file_path(f'{M2_FILE_NAME}.stor'),
    "a+",
    maxBytes=TELEMETRY_MAX_FILE_SIZE,
    backupCount=TELEMETRY_BACKUP_FILE_CNT,
)
logging.basicConfig(level=logging.CRITICAL, format="%(message)s")

m1_bulk_store = logging.getLogger("m1_bulk_sav")
m1_bulk_store.handlers.clear()
m1_bulk_store.addHandler(m1_bulk_handler)


m2_bulk_store = logging.getLogger("m2_bulk_sav")
m2_bulk_store.handlers.clear()
m2_bulk_store.addHandler(m2_bulk_handler)


logger = logging.getLogger("bulk-error")


def retrieve_m1_bulk_messages(_fname: str = M1_FILE_NAME):
    """retrieve_bulk_messages from a logfile removes each file in rotation
    as the file is read it will return a file
    which can be deleted on ok Upload"""
    try:
        m1_bulk_store.handlers.clear()
        m1_bulk_handler.close()
        deviceId = None
        # get current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        print("Current date & time : ", current_datetime)
        # convert datetime obj to string
        str_current_datetime = str(current_datetime)
        m1_up_file = None
        for filename in os.listdir(_env.storage_file_path()):
            if filename.startswith(_fname):
                # print(filename)
                data = {}
                with open(_env.storage_file_path(filename), "r") as file1:
                    # data = file.read()
                    while True:
                        # Get next line from file
                        line = file1.readline()
                        if len(line) > 0:
                            obj = json.loads(line)

                            if "id" in obj and "type" in obj:
                                deviceId = obj["id"]
                                # deviceType = obj["type"]
                                if deviceId not in data:
                                    data[deviceId] = []

                                data[deviceId].append(line)

                        if not line:
                            break
                # Save to bulk-upload-file
                if deviceId != None:
                    # create a file object along with extension
                    m1_up_file = (
                        BULK_FILE_PRE + str_current_datetime + ".json"
                    ).replace(" ", "_")
                    with open(_env.storage_file_path(m1_up_file), "w") as file_out:
                        file_out.write("".join(data[deviceId]))
                    time.sleep(3)
                os.remove(_env.storage_file_path(filename))

        m1_bulk_store.addHandler(m1_bulk_handler)

        if m1_up_file == None:
            for filename in os.listdir(_env.storage_file_path()):
                if filename.startswith(BULK_FILE_PRE) and filename.endswith(".json"):
                    m1_up_file = filename
                    break

        if m1_up_file == None:
            return None
        else:
            # returning the full file name.
            return _env.storage_file_path(m1_up_file)

    except Exception as err:
        print("Error", repr(err))

    m1_bulk_store.addHandler(m1_bulk_handler)
    return None


def retrieve_m2_bulk_messages(m2_fname: str = M2_FILE_NAME):
    """retrieve_bulk_messages from a logfile removes each file in rotation as it is read
    it should be called until it return None"""
    try:
        m2_bulk_store.handlers.clear()
        m2_bulk_handler.close()
        deviceId = None
        # get current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        print("Current date & time : ", current_datetime)
        # convert datetime obj to string
        str_current_datetime = str(current_datetime)
        m2_up_file = None
        for filename in os.listdir(_env.storage_file_path()):
            if filename.startswith(m2_fname):
                # print(filename)
                data = {}
                with open(_env.storage_file_path(filename), "r") as file1:
                    # data = file.read()
                    while True:
                        # Get next line from file
                        line = file1.readline()
                        if len(line) > 0:
                            obj = json.loads(line)
                            if "id" in obj and "type" in obj:
                                deviceId = obj["id"]
                                # deviceType = obj["type"]
                                if deviceId not in data:
                                    data[deviceId] = []
                                data[deviceId].append(line)
                        if not line:
                            break
                # Save to bulk-upload-file
                if deviceId != None:
                    # create a file object along with extension
                    m2_up_file = (
                        BULK_FILE_PRE + str_current_datetime + ".json"
                    ).replace(" ", "_")
                    with open(_env.storage_file_path(m2_up_file), "w") as file_out:
                        file_out.write("".join(data[deviceId]))
                    time.sleep(3)

                os.remove(_env.storage_file_path(filename))

        m2_bulk_store.addHandler(m2_bulk_handler)

        if m2_up_file == None:
            for filename in os.listdir(_env.storage_file_path()):
                if filename.startswith(BULK_FILE_PRE) and filename.endswith(".json"):
                    m2_up_file = filename
                    break

        if m2_up_file == None:
            return None
        else:
            # returning the full file name.
            return _env.storage_file_path(m2_up_file)

    except Exception as err:
        print("Error", repr(err))

    m2_bulk_store.addHandler(m2_bulk_handler)
    return None


if __name__ == "__main__":
    for i in range(500):
        msg = {
            "id": "7112BW111TEST0015-0000",
            "tzo": 0.0,
            "fwv": "0.2.5BW1",
            "type": "vdt",
            "mdl": "",
            "evt": "0",
            "mtp": "1",
            "mver": "1",
            "t": "39985",
            "data": {
                "ch1SOC": 1,
                "ic15ChgCur": 13,
                "sc4Shnt": 3,
                "th1InTmp": 14,
                "th6InTmp": 15,
                "th99InTmp": 1,
                "wt1Lvl": 80,
                "wt2Lvl": 61,
            },
        }
        msg["t"] = f"{i}"
        m1_bulk_store.critical(json.dumps(msg))

    # bulk_msg = retrieve_m1_bulk_messages()
    # while bulk_msg != None:
    #     #print(bulk_msg)
    #     bulk_msg = retrieve_m1_bulk_messages()

    for i in range(30000, 30099):
        msg = {
            "id": "7112BW111TEST0015-0000",
            "tzo": 0.0,
            "fwv": "0.2.5BW1",
            "type": "vdt",
            "mdl": "",
            "evt": "0",
            "mtp": "1",
            "mver": "1",
            "t": "39985",
            "data": {
                "ch1SOC": 1,
                "ic15ChgCur": 13,
                "sc4Shnt": 3,
                "th1InTmp": 14,
                "th6InTmp": 15,
                "th99InTmp": 1,
                "wt1Lvl": 80,
                "wt2Lvl": 61,
            },
        }
        msg["t"] = f"{i}"
        m1_bulk_store.critical(json.dumps(msg))

    bulk_msg = retrieve_m1_bulk_messages()

    for i in range(30000, 30099):
        msg = {
            "id": "7112BW111TEST0015-0000",
            "tzo": 0.0,
            "fwv": "0.2.5BW1",
            "type": "vdt",
            "mdl": "",
            "evt": "0",
            "mtp": "1",
            "mver": "1",
            "t": "39985",
            "data": {
                "ch1SOC": 1,
                "ic15ChgCur": 13,
                "sc4Shnt": 3,
                "th1InTmp": 14,
                "th6InTmp": 15,
                "th99InTmp": 1,
                "wt1Lvl": 80,
                "wt2Lvl": 61,
            },
        }
        msg["t"] = f"{i}"
        m1_bulk_store.critical(json.dumps(msg))

    # while bulk_msg != None:
    #     #print(bulk_msg)
    #     bulk_msg = retrieve_m1_bulk_messages()

    for i in range(30000, 30099):
        msg = {
            "id": "7112BW111TEST0015-0000",
            "tzo": 0.0,
            "fwv": "0.2.5BW1",
            "type": "vdt",
            "mdl": "",
            "evt": "0",
            "mtp": "2",
            "mver": "1",
            "t": "39985",
            "data": {
                "ch1SOC": 1,
                "ic15ChgCur": 13,
                "sc4Shnt": 3,
                "th1InTmp": 14,
                "th6InTmp": 15,
                "th99InTmp": 1,
                "wt1Lvl": 80,
                "wt2Lvl": 61,
            },
        }
        msg["t"] = f"{i}"
        m2_bulk_store.critical(json.dumps(msg))

    # bulk_msg = retrieve_m2_bulk_messages()
    # while bulk_msg != None:
    #     #print(bulk_msg)
    #     bulk_msg = retrieve_m2_bulk_messages()

    for i in range(30000, 30299):
        msg = {
            "id": "7112BW111TEST0015-0000",
            "tzo": 0.0,
            "fwv": "0.2.5BW1",
            "type": "vdt",
            "mdl": "",
            "evt": "0",
            "mtp": "2",
            "mver": "1",
            "t": "39985",
            "data": {
                "ch1SOC": 1,
                "ic15ChgCur": 13,
                "sc4Shnt": 3,
                "th1InTmp": 14,
                "th6InTmp": 15,
                "th99InTmp": 1,
                "wt1Lvl": 80,
                "wt2Lvl": 61,
            },
        }
        msg["t"] = f"{i}"
        m2_bulk_store.critical(json.dumps(msg))


    print("Done", "\n")
