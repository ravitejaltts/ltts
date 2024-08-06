import json


level_states = [
    {
        "name": "HouseBatteryLevel",
        "icon": "",
        "color_fill": "#55b966",
        "color_empty": "#e5e5ea",

        'type': 'simpleLevel',
        'simpleLevel': {
            'max': 100,
            'min': 0,
            'current_value': 100,
            'unit': '%',
            'level_text': 'Full'
        },

        "title": "House Battery",
        "subtext": "6 Days",

        'actions': ['action_navigate',],
        "action_navigate": {
            "type": "navigate",
            "action": {
                "href": "/home/battery"
            }
        }
    },

    {
        "name": "FreshTankLevel",
        "icon": "",
        "color_fill": "#0ca9da",
        "color_empty": "#e5e5ea",

        'type': 'simpleLevel',
        'simpleLevel': {
            'max': 100,
            'min': 0,
            'current_value': 72,
            'unit': '%',
            'level_text': '72%'
        },

        "title": "Fresh Water",
        "subtext": "3 Days",

        'actions': ['action_navigate',],
        "action_navigate": {
            "type": "navigate",
            "action": {
                "href": "/home/levels"
            }
        }
    },
    {
        "name": "GreyTankLevel",
        "icon": "",
        "color_fill": "#3a3a3c",
        "color_empty": "#e5e5ea",

        'type': 'simpleLevel',
        'simpleLevel': {
            'max': 100,
            'min': 0,
            'current_value': 3,
            'unit': '%',
            'level_text': '3%'
        },

        "title": "Gray Tank",
        "subtext": "6 Days",

        'actions': ['action_navigate',],
        "action_navigate": {
            "type": "navigate",
            "action": {
                "href": "/home/levels"
            }
        }
    }
]

if __name__ == '__main__':
    print(json.dumps(level_states, indent=4))
