import json
import time
import random

telemetry_data = {
    # Timezone offset
    "tzo": -5,
    # Geo location, lat/lon
    "geo": "32.432,-85.547",
    # firmware version
    "fwv": "0.1.0",
    # Vehicle/Device Type
    "type": "S800",
    # Specific Model
    "mdl" : "",
    # Device ID
    "id": "JH4DC4460SS000830-0001",
    # Message Type
    # 1 = Telemetry
    # 2 = Critical Command/Request/Notification
    "mtp": "1",
    # Message Version / Schema
    "mver": "1",
    # Criticallity level
    # # Higher is ???
    # "lvl": 10,
    # Milliseconds since epoch
    "t": 16494337261000,

    "data": {
        "wh1Mode": 1,

        "wp1Mode": 1,
        "wp2Mode": 1,

        "ac1Mode": 0,

        "sc1Vltg": 454,

        "sc1Curr": 345,
        "sc1ChgState": 4,
        "sc1TmpState": 3,
        "sc1InptCurr":5,
        "sc1ArrVltg":345,
        "sc1EQTime": 32,
        "sc1Err": 0,

        "lb1ChgStat": 233, "lb1Tmp": 70, "lb1VltgStat": 3, "lb1DCCurr": 321, "lb1Hlth": 3, "lb1DschCap": 3, "lb1ChgState": 1, "lb1Err": 2,

        "rv1Mode": 1,

        "ch1Mode": 1, "ch1BtrySoc": 3, "ch1TTFull": 6054, "ch1BVltg": 29392, "ch1RPM": 300,

        "ch1Spd": 60, "ch1PdlPos":4, "ch1CoolTmp": 80, "ch1ChkStat":2,

        "ch1VIN": "JH4DC4460SS000830", "ch1IgnCyc": 45, "ch1Odomtr":490000,

        "ch1DTCs": "??????",

        "ts1Stat": "123", "ts1Humid": 60, "ts1Tmp": 70, "ts1AtmosP": 50,

        "ts2Stat": "123", "ts2Humid": 60, "ts2Tmp": 70, "ts2AtmosP": 50,

        "ts3Stat": "123", "ts3Humid": 60, "ts3Tmp": 70, "ts3AtmosP": 50,

        "wt1FLvl": 80, "wt1FCap": 100, "wt1FTyp": 2,

        "lz1rgbSet": 255, "lz1rgbBrt": 100, "lz1wBrt": 100, "lz1Zone": 1, "lz1Pwr": 1, "lz1Err": None,

        "lz2rgbSet": 244, "lz2rgbBrt": 132, "lz2wBrt": 0, "lz2Zone": 1, "lz2Pwr": 1, "lz2Err": 123,

        "lz3rgbSet": 244, "lz3rgbBrt": 132, "lz3wBrt": 0, "lz3Zone": 1, "lz3Pwr": 1, "lz3Err": 123,

        "lz4rgbSet": 244, "lz4rgbBrt": 132, "lz4wBrt": 0, "lz4Zone": 1, "lz4Pwr": 1, "lz4Err": 123,

        "lz5rgbSet": 244, "lz5rgbBrt": 132, "lz5wBrt": 0, "lz5Zone": 1, "lz5Pwr": 1, "lz5Err": 123,

        "lz6rgbSet": 244, "lz6rgbBrt": 132, "lz6wBrt": 0, "lz6Zone": 1, "lz6Pwr": 1, "lz6Err": 123,

        "lz7rgbSet": 244, "lz7rgbBrt": 132, "lz7wBrt": 0, "lz7Zone": 1, "lz7Pwr": 1, "lz7Err": 123,

        "lz8rgbSet": 244, "lz8rgbBrt": 132, "lz8wBrt": 0, "lz8Zone": 1, "lz8Pwr": 1, "lz8Err": 123,

        "lz9rgbSet": 244, "lz9rgbBrt": 132, "lz9wBrt": 0, "lz9Zone": 1, "lz9Pwr": 1, "lz9Err": 123,

        "lzargbSet": 244, "lzargbBrt": 132, "lzawBrt": 0, "lzaZone": 1, "lzaPwr": 1, "lzaErr": 123
    }
}

def get_mock_telemetry():
    telemetry_data['t'] = int(time.time() * 1000)
    return json.dumps(telemetry_data)


alert_data = {
      # Timezone offset
    "tzo": -5,
    # Geo location, lat/lon
    "geo": "32.432,-85.547",
    # firmware version
    "fwv": "0.1.0",
    # Vehicle/Device Type
    "type": "S800",
    # Specific Model
    "mdl" : "",
    # Device ID
    "id": "JH4DC4460SS000830-0001",
    # Message Type
    # 1 = Telemetry
    # 2 = Critical Command/Request/Notification
    "mtp": "2",
    # Message Version / Schema
    "mver": "1",
    # Criticallity level
    # # Higher is ???
    # "lvl": 10,
    # Milliseconds since epoch
    "t": 16494337261000,
    "notifications": []
}

notifications = [
    {'id': 124, 't': '', 'ecode': 'GREY1FULL', 'header': 'Gray water tank approaching full', 'body': 'Gray water tank is at 95% full', 'level': 1},
    {'id': 123, 't': '', 'ecode': 'BATLOW', 'header': 'Battery low', 'body': 'Battery voltage below 11.5V', 'level': 5},
    {'id': 125, 't': '', 'ecode': 'INTERNALTEMPHIGH', 'header': 'Internal temp high', 'body': 'Internal temperature is above 95 deg F', 'level': 10}
]


def get_mock_alert():
    alert_data['t'] = int(time.time() * 1000)

    # notification_count = random.randint(0, len(notifications))

    alert_data['notifications'] = []
    # for i in range(notification_count):
    notification = random.choice(notifications)
    notification['id'] = random.randint(1000, 5000)
    notification['t'] = int(time.time() * 1000) - 3

    alert_data['notifications'].append(notification)

    return json.dumps(alert_data)


if __name__ == '__main__':
    for i in range(10):
        print(get_mock_alert())
