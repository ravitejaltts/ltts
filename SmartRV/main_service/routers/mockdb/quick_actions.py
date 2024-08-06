import json


quick_actions = [
    {
        "name": "WaterPumpAction",

        "title": "Water Pump",
        "subtext": "On",
      
        "type": "Simple",
        'Simple': {
            'onOff': 1
        },
        
        'actions': ['action_default', 'action_longpress'],
        
        "action_default": {
            "type": "api_call",
            "action": {
                "href": "/api/watersystems/pump/1",
                "type": "PUT",
                'params': {
                    '$onOff': 'int'
                }
            }
        },
     
        "action_longpress": {
            "type": "navigate",
            "action": {
                "href": "/home/watersystems"
            }
        }
    },
    {
        "name": "InverterAction",

        "title": "Inverter",
        "subtext": "On",

        'type': 'Simple',
        'Simple': {
            'onOff': 0
        },
        
        'actions': [
            'action_default', 
            'action_longpress'
        ],
        "action_default": {
            "type": "api_call",
            "action": {
                "href": "/api/electrical/dc/6",
                "type": "PUT",
                "params": {
                    "$onOff": 'int'
                }
            }
        },
        "action_longpress": {
            "type": "navigate",
            "action": {
               "href": "/home/lighting"
            }
        }
    },
    {
        "name": "WaterHeaterAction",

        "title": "Water Heater",
        "subtext": "On",

        'type': 'Simple',
        'Simple': {
            'onOff': 1
        },
        
        'actions': [
            'action_default', 
            'action_longpress'
        ],
        "action_default": {
            "type": "api_call",
            "action": {
                "href": "/api/watersystems/heater/1",
                "type": "PUT",
                "params": {
                    "$onOff": 'int'
                }
            }
        },
        "action_longpress": {
            "type": "navigate",
            "action": {
                "href": "/home/watersystems"
            }
        }
    },
    {
        "name": "MasterLightAction",

        "title": "Interior Lights",
        "subtext": "On",

        'type': 'Simple',
        'Simple': {
            'onOff': 1
        },
        
        'actions': [
            'action_default', 
            'action_longpress'
        ],
        "action_default": {
            "type": "api_call",
            "action": {
                "href": "/api/lighting/all/smarttoggle",
                "type": "PUT",
                "params": {
                    "$onOff": 'int'
                }
            }
        },
        "action_longpress": {
            "type": "navigate",
            "action": {
                "href": "/home/lighting"
            }
        }
    }
]


if __name__ == '__main__':
    print(json.dumps(quick_actions, indent=4))