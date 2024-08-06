import random


def get_unique_short_uuid(session_dict):
    '''Generate a short UUID as state session'''
    new_token = random.randint(0, 65535)
    new_token = f'{new_token:04X}'
    if new_token in session_dict:
        # Generate a new one
        return get_unique_short_uuid(session_dict)

    return new_token



def byte_flip(value, byte_count=2):
    '''Flip bytes for processing of little endian data bus like CAN.'''
    #TODO: Implement more than two bytes
    if byte_count > 2:
        raise NotImplementedError('Cannot handle more than two bytes yet')

    if value > (256**byte_count)-1:
        raise ValueError(f'Input value exceeds max value for bytes')
    elif value < 0:
        raise ValueError(f'Input value cannot be negative')

    left = (value & 0xff00) >> 8
    right = value & 0xff

    flipped_int = (right << 8) + left
    return flipped_int


def compare_dict(dict_a, dict_b):
    '''Compare two dictionaries and return differences'''
    pass


def index_list(in_list, key_name):
    result = {}
    for i, item in enumerate(in_list):
        if isinstance(item, type({})):
            # run flatten_dict
            sub_result = flatten_dict(item)
            for k, v in sub_result.items():
                result[k] = v
        elif isinstance(item, type([])):
            # Run this function again
            sub_result = index_list(item, key_name + f'[{i}]')
            for k, v in sub_result.items():
                result[k] = v
        else:
            result[key_name + f'[{i}]'] = item

    return result


def flatten_dict(in_dict, key_list=[], result={}, separator='.'):
    '''Flatten a dictionary to a shallow copy.'''
    for key, value in in_dict.items():
        key_list.append(str(key))
        if isinstance(value, type({})):
            # Run function again
            value = flatten_dict(value, key_list=key_list, result=result, separator=separator)

        elif isinstance(value, type([])):
            # Iterate through and keep enumerated id
            sub_result = index_list(value, separator.join(key_list))
            for k, v in sub_result.items():
                result[k] = v
        else:
            result[separator.join(key_list)] = value

        if key_list:
            key_list.pop()

    return result


def expand_flat_dict(in_dict):
    '''Expand a flat dictionary into nested dict.'''
    pass


if __name__ == '__main__':
    sessions = {}
    for i in range(50):
        new_id = get_unique_short_uuid(sessions)
        sessions[new_id] = {}

    print('Sessions', len(sessions))
    print(sessions)
    x = {
        'a': {
            'b': {
                'c': 'DomTestValue',
                'e': 'DomAgain'
            }
        },
        'd': 'Dom',
        'f': ['1', '2', '3'],
        'g': [
            {
                'd1': ['dd', 'da', 'de']
            }
        ]
    }
    # print(x)
    result = flatten_dict(x)
    print(result)
    assert result.get('a.b.e') == 'DomAgain'
    assert result.get('g.d1[1]') == 'da'

    for lvl in [0, 1, 64, 255, 256, 1200, 1400, 2000, 2400, 3600, 4000, 5000, 5700, 5800, 6600, 6700, 7200, 65535]:
        flipped = byte_flip(lvl)
        print(lvl, flipped, f'{flipped:04X}')
        print('---------')
