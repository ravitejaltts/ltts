import json
import random

from constants import APIMethods


def create_request_bytes(msg_dict):
    # request_bytes = [random.randint(0,255),]
    request_bytes = []
    # request_bytes = [1,]
    request_bytes.append(msg_dict.get('method').value)
    url_len = len(msg_dict.get('url'))
    request_bytes.extend(
        [url_len & 0xff, url_len & 0xff00]
    )
    request_bytes.extend([ord(x) for x in msg_dict.get('url', '')])
    body = msg_dict.get('body')
    if body is not None:
        body_len = len(body)
        request_bytes.extend(
            [body_len & 0xff, body_len & 0xff00]
        )
        request_bytes.extend([ord(x) for x in body])

    return request_bytes


def create_security_request():
    request_bytes = []
    request_bytes.extend(
        [4, 1, 0, 0]
    )
    request_bytes.append(0x0A)
    request_bytes.append(0x00)
    request_bytes.append(0x00)
    # Exp Date
    request_bytes.extend(
        [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,]
    )
    # Device ID
    request_bytes.extend(
        [ord(x) for x in '1234567890123456']
    )
    # Vehicle ID
    request_bytes.extend(
        [ord(x) for x in '123456789012345678901234']
    )
    # Mob pub key
    request_bytes.extend(
        [ord(x) for x in '123456789012345678901234567890123456789012']
    )
    # Signature
    request_bytes.extend(
        [ord(x) for x in '1'*200]
    )

    return request_bytes


if __name__ == '__main__':
    msg = {
        'method': APIMethods.GET,
        'url': '/ui/home',
        'body': None
    }
    print(''.join([f'{x:02X}' for x in create_request_bytes(msg)]))

    msg = {
        'method': APIMethods.PUT,
        'url': '/api/lighting/zone/1',
        'body': json.dumps({'onOff': 0})
    }
    print('onOff 0',
        ''.join([f'{x:02X}' for x in create_request_bytes(msg)])
    )

    msg = {
        'method': APIMethods.PUT,
        'url': '/api/lighting/zone/1',
        'body': json.dumps({'onOff': 1})
    }
    print('onOff 1',
        ''.join([f'{x:02X}' for x in create_request_bytes(msg)])
    )

    msg = {
        'method': APIMethods.PUT,
        'url': '/api/lighting/all/smarttoggle',
        'body': json.dumps({'onOff': 0})
    }
    print('SmartToggle',
        ''.join([f'{x:02X}' for x in create_request_bytes(msg)])
    )

    msg = {
        'method': APIMethods.PUT,
        'url': '/api/lighting/all/smarttoggle',
        'body': json.dumps({'onOff': 1})
    }
    print('SmartToggle',
        ''.join([f'{x:02X}' for x in create_request_bytes(msg)])
    )

    print('Fast Forward Security Request', 
        ''.join([f'{x:02X}' for x in create_security_request()])
    )
