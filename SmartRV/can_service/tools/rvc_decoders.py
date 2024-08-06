from data_helper import bitShifter


MAPPING = {
    '1FFED__OPERATION_MODE': {
        '0': 'Inactive',
        '1': 'Suspension raise (all air springs) active',
        '2': 'Suspension dump (all air springs) active',
        '3': 'Store active (store jacks/go to ride height)',
        '4': 'Manual air leveling.',
        '5': 'Automatic air leveling active',
        '6': 'Start deploy kick-down jacks',
        '7': 'Manual hydraulic leveling',
        '8': 'Automatic hydraulic/electric leveling active',
        '9': 'Kneel active (dump front bags only)',
        '10': 'Auto Hitch Height',
        '11': 'Abort Function',
        '34': 'Jack calibration mode',
        '41': 'Manual air leveling: Four point',
        '42': 'Manual air leveling: Biax mode',
        '43': 'Manual air leveling: 3 point mode',
        '44': 'Manual air leveling: Multi point mode 5+',
        '51': 'Automatic air leveling – Four point',
        '52': 'Automatic air leveling – Biax mode',
        '53': 'Automatic air leveling – 3 point mode',
        '54': 'Automatic air leveling: Multi point mode 5+',
        '71': 'Manual hydraulic/electric leveling: Four point',
        '72': 'Manual hydraulic/electric leveling: Biax mode',
        '73': 'Manual hydraulic/electric leveling: 3 point mode 74: Manual hydraulic leveling: Multi point mode 5+ 81 – Automatic hydraulic leveling – Four point',
        '82': 'Automatic hydraulic leveling – Biax mode',
        '83': 'Automatic hydraulic leveling – 3 point mode',
        '84': 'Automatic hydraulic leveling: Multi point mode 5+ 99: Acknowledge / Clear jack error'
    },
    '1FFED__PARK_BRAKE': {
        '0': 'Leveling System May Operate',
        '1': 'Leveling system may not operate because of Park Brake status'
    },
    '1FFED__LOW_VOLTAGE': {
        '0': 'Leveling System May Operate',
        '1': 'Leveling system may not operate because of Low Voltage status'
    },
    '1FFED__IGNITION_KEY': {
        '0': 'Leveling System May Operate',
        '1': 'Leveling system may not operate because of Ignition status'
    },
    'OffOnVoid': {
        '0': 'Off',
        '1': 'On',
        '3': 'Void/Disabled'
    },
    'JackOnOffVoid': {
        '0': 'Off',
        '1': 'Jack is extended. Coach is not safe to move',
        '3': 'Void/Disabled'
    },
    'PressureOffOnVoid': {
        '0': 'No action',
        '1': 'Pressure detected. Jack is bearing weight on the ground',
        '3': 'Void/Disabled'
    }
}


def decode_rvc(msg, dgn: str, msg_name: str, mapping: dict) -> dict:
    '''Decodes can message against mapping dictionary.'''
    global MAPPING

    decoded = {
        'DGN': dgn,
        'MSG_NAME': msg_name
    }

    bit_msg = bitShifter(msg.data)
    for item in mapping:
        item_name = item['name']
        
        value_map = item.get('value_map')
        value = bit_msg.pop(item['bits'])

        if value_map is None:
            value_map = dgn + '__' + item['name']

        decoded[item_name] = (
            value,
            MAPPING.get(value_map, {}).get(str(value), 'NOTFOUND') 
        )
    
    return decoded


def encode_rvc():
    '''Encode rvc message based on mapping and input dictionary'''
    raise NotImplementedError('Not implemented yet')


def rvc_leveling_control_status(msg):
    '''Decodes RVC 6.13.2 LEVELING_CONTROL_STATUS.
    DGN 1FFEDh'''
    DGN = '1FFED'
    mapping = [
        # 0
        {'bits': 8, 'name': 'OPERATION_MODE'},
        # 1
        {'bits': 2, 'name': 'AUTOMATIC_JACK_STABILIZATION_STATUS'},
        {'bits': 2, 'name': 'AIR_LEVELING_SLEEP_MODE'},
        {'bits': 2, 'name': 'AIR_RE-LEVELING_MODE'},
        {'bits': 2, 'name': 'VOID'},
        # 2
        {'bits': 2, 'name': 'EXCESSIVE_SLOPE_INITIAL_WARNING'},
        {'bits': 2, 'name': 'EXCESSIVE_SLOPE_FINAL_WARNING'},
        {'bits': 2, 'name': 'LEVELING_SYSTEM_MASTER_WARNING'},
        {'bits': 2, 'name': 'VOID'},
        # 3
        {'bits': 2, 'name': 'JACK_RETRACTING_LEFT_REAR', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_EXTENDING_LEFT_REAR', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_RETRACTING_RIGHT_FRONT', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_EXTENDING_RIGHT_FRONT', 'value_map': 'OffOnVoid'},
        # 4
        {'bits': 2, 'name': 'JACK_RETRACTING_RIGHT_REAR', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_EXTENDING_RIGHT_REAR', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_RETRACTING_LEFT_FRONT', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_EXTENDING_LEFT_FRONT', 'value_map': 'OffOnVoid'},
        # 5
        {'bits': 2, 'name': 'JACK_RETRACTING_LEFT_MIDDLE', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_EXTENDING_LEFT_MIDDLE', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_RETRACTING_RIGHT_MIDDLE', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_EXTENDING_RIGHT_MIDDLE', 'value_map': 'OffOnVoid'},
        # 6
        {'bits': 2, 'name': 'JACK_RETRACTING-TONGUE', 'value_map': 'OffOnVoid'},
        {'bits': 2, 'name': 'JACK_EXTENDING-TONGUE', 'value_map': 'OffOnVoid'},
        {'bits': 4, 'name': 'B6_REST_RESERVED'},
        # 7
        {'bits': 2, 'name': 'PARK_BRAKE'},
        {'bits': 2, 'name': 'IGNITION_KEY'},
        {'bits': 2, 'name': 'LOW_VOLTAGE'},
        {'bits': 2, 'name': 'OTHER_LOCKOUT'}
    ]
    return decode_rvc(msg, DGN, 'LEVELING_CONTROL_STATUS', mapping)


def rvc_leveling_jack_status(msg):
    '''Decodes RVC 6.13.4 LEVELING_JACK_STATUS.
    DGN 1FFECh'''
    DGN = '1FFEC'
    mapping = [
        # 0 (Jacks)
        {'bits': 4, 'name': 'JACK_TYPE'},
        {'bits': 4, 'name': 'NUMBER_OF_JACKS'},
        # 1 (Extension)
        {'bits': 2, 'name': 'EXTENSION-LEFT_REAR', 'value_map': 'JackOnOffVoid'},
        {'bits': 2, 'name': 'EXTENSION-RIGHT_FRONT', 'value_map': 'JackOnOffVoid'},
        {'bits': 2, 'name': 'EXTENSION-RIGHT_REAR', 'value_map': 'JackOnOffVoid'},
        {'bits': 2, 'name': 'EXTENSION-LEFT_FRONT', 'value_map': 'JackOnOffVoid'},
        # 2 (Aux)
        {'bits': 2, 'name': 'EXTENSION-AUX_JACK1', 'value_map': 'JackOnOffVoid'},
        {'bits': 2, 'name': 'EXTENSION-AUX_JACK2', 'value_map': 'JackOnOffVoid'},
        {'bits': 2, 'name': 'EXTENSION-AUX_JACK3', 'value_map': 'JackOnOffVoid'},
        {'bits': 2, 'name': 'EXTENSION-AUX_JACK4', 'value_map': 'JackOnOffVoid'},
        # 3 (Stability)
        {'bits': 2, 'name': 'STABILITY-LEFT_REAR', 'value_map': 'PressureOffOnVoid'},
        {'bits': 2, 'name': 'STABILITY-RIGHT_FRONT', 'value_map': 'PressureOffOnVoid'},
        {'bits': 2, 'name': 'STABILITY-RIGHT_REAR', 'value_map': 'PressureOffOnVoid'},
        {'bits': 2, 'name': 'STABILITY-LEFT_FRONT', 'value_map': 'PressureOffOnVoid'},
        # 4 (Stability / Aux)
        {'bits': 2, 'name': 'STABILITY-AUX1', 'value_map': 'PressureOffOnVoid'},
        {'bits': 2, 'name': 'STABILITY-AUX2', 'value_map': 'PressureOffOnVoid'},
        {'bits': 2, 'name': 'STABILITY-AUX3', 'value_map': 'PressureOffOnVoid'},
        {'bits': 2, 'name': 'STABILITY-AUX4', 'value_map': 'PressureOffOnVoid'}
    ]
    return decode_rvc(msg, DGN, 'LEVELING_JACK_STATUS', mapping)
   

def rvc_debug(msg) -> dict:
    '''Devoces RVC 3.2.5 DM_RV
    Example: 11 51 00 00 a1 ff ff 0f 
    '''
    result = {}
    for i, byte in enumerate(msg.data):
        print(i, hex(byte))
    
    return result


if __name__ == '__main__':
    class Msg(object):
        def __init__(self) -> None:
            super().__init__()
            self.arbitration_id = 'ffed'
            # Leveling Jack status
            # self.data = b'@\x55\x00\x00\x00\x00\x00\x00'
            # Leveling control status
            # self.data = b'\x00\x00\x00\x00\x00\xff\xff\xc0'
            # self.data = b'\x48\x00\x00\x40\x00\xff\xff\xc0'
            self.data = b'\x03\x00\x00\x00\x00\xff\xff\xd0'
            # DM RM
            # self.data = b'\x11Q\x00\x00\xa1\xff\xff\x0f'
    
    msg = Msg()
    # print(rvc_leveling_jack_status(msg))
    result = rvc_leveling_control_status(msg)
    for key, value in result.items():
        print(key, value)
    