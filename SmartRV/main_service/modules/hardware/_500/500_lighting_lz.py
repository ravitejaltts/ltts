import json


output = '500_lighting_lz.json'

BRIGHTNESS_DEFAULT = 80

lighting = {
    'lz': [
        {
            'id': 1,
            'type': 'SIMPLE_DIM',
            'name': 'Front Work',
            'description': 'Main ceiling lights',
            'code': 'lz',
            'defaultState': {
                'onOff': 0,
                'brt': BRIGHTNESS_DEFAULT,
            }
        },
        {
            'id': 2,
            'type': 'SIMPLE_DIM',
            'name': 'Front Work',
            'description': 'Main ceiling lights',
            'code': 'lz',
            'defaultState': {
                'onOff': 0,
                'brt': BRIGHTNESS_DEFAULT,
            }
        },
        {
            'id': 3,
            'type': 'SIMPLE_DIM',
            'name': 'Front Work',
            'description': 'Main ceiling lights',
            'code': 'lz',
            'defaultState': {
                'onOff': 0,
                'brt': BRIGHTNESS_DEFAULT,
            }
        },
        {
            'id': 4,
            'type': 'SIMPLE_DIM',
            'name': 'Front Work',
            'description': 'Main ceiling lights',
            'code': 'lz',
            'defaultState': {
                'onOff': 0,
                'brt': BRIGHTNESS_DEFAULT,
            }
        },
        {
            'id': 5,
            'type': 'SIMPLE_DIM',
            'name': 'Front Work',
            'description': 'Main ceiling lights',
            'code': 'lz',
            'defaultState': {
                'onOff': 0,
                'brt': BRIGHTNESS_DEFAULT,
            }
        },
        {
            'id': 6,
            'type': 'SIMPLE_DIM',
            'name': 'Front Work',
            'description': 'Main ceiling lights',
            'code': 'lz',
            'defaultState': {
                'onOff': 0,
                'brt': BRIGHTNESS_DEFAULT,
            }
        }
    ]
}

json.dump(lighting, open(output, 'w'), indent=4, sort_keys=True)
