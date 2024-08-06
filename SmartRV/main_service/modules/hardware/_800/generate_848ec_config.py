import json
import os
import sys

config_name = '848EV.json'

config = {
    # Version
    'version': '0.1',
    # basic settings
    'settings': {
        'activity_settings':{
            'inactiveTimeout': 360000,
            'offTimeout': 366000,
            # Page to navigate to after waking up / returning from lock screen
            'navigateTo': '/',
            'activityAPIs': {
                'type': 'PUT',
                'inactive': '/api/system/activity/idle',
                'active': '/api/system/activity/on',
                'off': '/api/system/activity/off'
            }
        }
    },
    # HW modules / HAL
    'hal': {
    },
    # Default values for various areas
    'defaults': {
        'BluetoothControlEnabled': 1,
        'VolumeUnitPreference': 0   # Gallons
    }
}

path = os.path.abspath(sys.argv[0])
path = os.path.split(path)[0] + '/' + config_name

json.dump(config, open(path, 'w'), indent=4, sort_keys=True)
