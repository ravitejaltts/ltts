import json
from common_libs.models.common import EventValues

# Overview is for the tile on the left
overview = {
    'title': 'Lighting',
     'settings': {
        'href': '/pages/lighting/settings'
    },
    'switches': [
        {
            'title': '1',
            'subtext': 'Preset Switch',
            'action': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/preset/1/on',
                    'type': 'PUT'
                }
            }
        },
        {
            'title': '2',
            'subtext': 'Preset Switch',
            'action': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/preset/2/on',
                    'type': 'PUT'
                }
            }
        },
        {
            'title': '3',
            'subtext': 'Preset Switch',
            'action': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/preset/3/on',
                    'type': 'PUT'
                }
            }
        }
    ]
}


lights = {
    'master': {
        'title': 'Light Master',
        'type': 'Simple',
        'Simple': {
            'onOff': 1
        },
        'subtext': '5 Lights On',
        'actions': ['action_default',],

        'action_default': {
            'type': 'api_call',
            'action': {
                'href': '/api/lighting/all/smarttoggle',
                'type': 'PUT',
                'params': {
                    '$onOff': 'int'
                }
            }
        }
    },
    'lights': [
        {
            'title': 'Main',
            'subtext': '100%',
            'type': 'RGBW',
            'RGBW': {
                'rgb': '#ffe6c1',
                'onOff': 1,
                'brightness': 100,
                'colorTemp': None
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/1',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'hex',
                        '$colorTemp': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 1
        },
        {
            'title': 'Front Work',
            'subtext': '55%',
            'type': 'RGBW',
            'RGBW': {
                'rgb': '#ffeacc',
                'onOff': 1,
                'brightness': 55,
                'colorTemp': None
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/2',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'hex',
                        '$colorTemp': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 2
        },
        {
            'title': 'Dinette',
            'subtext': EventValues.OFF,
            'type': 'RGBW',
            'RGBW': {
                'rgb': '#d1d1d6',
                'brightness': 50,
                'onOff': 0,
                'colorTemp': None
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/3',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'hex',
                        '$colorTemp': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 3
        },
        {
            'title': 'Galley',
            'subtext': EventValues.OFF,
            'type': 'RGBW',
            'RGBW': {
                'rgb': '#d1d1d6',
                'onOff': 0,
                'brightness': 50,
                'colorTemp': None
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/4',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'hex',
                        '$colorTemp': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 4
        },
        {
            'title': 'Accent',
            'subtext': '85%',
            'type': 'RGBW',
            'RGBW': {
                'rgb': '#f693ff',
                'onOff': 1,
                'brightness': 85,
                'colorTemp': None
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/5',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'hex',
                        '$colorTemp': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 5
        },
        {
            'title': 'Floor',
            'subtext': '85%',
            'type': 'RGBW',
            'RGBW': {
                'rgb': '#bdfbff',
                'brightness': 85,
                'onOff': 1,
                'colorTemp': None
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/6',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'hex',
                        '$colorTemp': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 6
        },
        {
            'title': 'Bed',
            'subtext': '25%',
            'type': 'RGBW',
            'RGBW': {
                'rgb': '#f4a22a',
                'onOff': 1,
                'brightness': 25,
                'colorTemp': None
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/7',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$rgb': 'hex',
                        '$colorTemp': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 7
        },
        {
            'title': 'Porch',
            'subtext': EventValues.OFF,
            'type': 'SimpleDim',
            'SimpleDim': {
                'brightness': 100,
                'onOff': 0
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/9',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 9
        },
        {
            'title': 'Undefined',
            'subtext': EventValues.OFF,
            'type': 'SimpleDim',
            'SimpleDim': {
                'brightness': 100,
                'onOff': 0
            },
            'actions': ['action_default',],
            'action_default': {
                'type': 'api_call',
                'action': {
                    'href': '/api/lighting/zone/10',
                    'type': 'PUT',
                    'params': {
                        '$onOff': 'int',
                        '$brightness': 'int'
                    }
                }
            },
            'zone_id': 10
        }
    ]
}

lighting = {
    'overview': overview,
    'lights': lights
}


if __name__ == '__main__':
    print(
        json.dumps(
            lighting,
            indent=4,
            # sort_keys=True
        )
    )
