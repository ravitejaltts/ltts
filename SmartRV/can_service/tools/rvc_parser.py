import json

from rvc_decoders import (
    rvc_leveling_control_status,
    rvc_leveling_jack_status
)

DEBUG_DISPLAY = 0x01
DEBUG_WIFI_ENABLED = 0x02
DEBUG_WIFI_MODE = 0x04


RVC_LIB = json.load(
    open('rvc_dbc.json', 'r')
)


def trigger_debug(message) -> dict:
    '''Parse debug message and perform action as needed.'''
    print(message)
    print(dir(message))
    print(message.data)
    b0 = message.data[0]

    signals = {
        'DISPLAY_ON': b0 & DEBUG_DISPLAY,
        'WIFI_ON': (b0 & DEBUG_WIFI_ENABLED) >> 1,
        'WIFI_MODE': (b0 & DEBUG_WIFI_MODE) >> 2,
    }
    return {
        'result': 'OK', 
        'event': 'WGO_DEBUG', 
        'signals': signals
    }
    

def parse_can(msg) -> dict:
    response = {
        'result': '',
        'message': ''
    }

    if msg.arbitration_id in RVC_LIB:
        # Parse
        return {}
    elif msg.arbitration_id == 0x1EADBEEF:
        print("DEBUG TEST Message")
        result = trigger_debug(msg)
        print(json.dumps(result, indent=4, sort_keys=True))
        return result

    elif msg.arbitration_id == 0x0dffec51:
        print('RVC__LEVELING_JACK_STATUS')
        response['result'] = 'OK'
        response['message'] = 'RVC__LEVELING_JACK_STATUS'
        response['event'] = 'RVC__LEVELING_JACK_STATUS'
        # TODO: Decode
        print(msg.data)
        response['value'] = rvc_leveling_jack_status(msg)

    elif msg.arbitration_id == 0x0dffed51:
        print('RVC__LEVELING_CONTROL_STATUS')
        response['result'] = 'OK'
        response['message'] = 'RVC__LEVELING_CONTROL_STATUS'
        response['event'] = 'RVC__LEVELING_CONTROL_STATUS'
        # TODO: Decode
        print(msg.data)
        response['value'] = rvc_leveling_control_status(msg)
    
    elif msg.arbitration_id == 0x19feca51:
        print('RVC__DEBUG')
        response['result'] = 'OK'
        response['message'] = 'RVC__DEBUG'
        response['event'] = 'RVC__DEBUG'
        # TODO: Decode
        print(msg.data)
        response['value'] = {}

    else:
        print('Cannot find ID:', hex(msg.arbitration_id), 'in DB')
        response['result'] = 'ERROR'
        response['message'] = 'ID not in DB'

    return response


if __name__ == '__main__':
    class Msg(object):
        def __init__(self) -> None:
            super().__init__()
            self.arbitration_id = 'ffed'
    
    msg = Msg()
    print(parse_can(msg))
    