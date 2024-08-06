"""WGO Constants"""

import csv
import os
from common_libs.models.common import EventValues
from common_libs import environment

_env = environment()


def _celcius_2_fahrenheit(temp_in_c, digits=0):
    '''Convert Celsius decimal number to Fahrenheit.'''
    fahrenheit = (temp_in_c * 9 / 5) + 32
    return round(fahrenheit, digits)


def fahrenheit_2_celcius(temp_in_f, digits=1):
    '''Convert Fahrenheit to Celsius'''
    celcius = (temp_in_f - 32) * 5/9
    return round(celcius, digits)


def read_component_types(path):
    '''Component tab from export as CSV
    https://winnebagoind.sharepoint.com/:x:/r/sites/CustomerDigitalStrategy/_layouts/15/doc2.aspx?sourcedoc=%7B002181d0-765c-4451-95ad-cc0615c68e02%7D&action=edit&activeCell=%27Data%20Elements%20848%27!D78&wdinitialsession=57ab61fe-2a9f-41c6-aab1-46e739c4f225&wdrldsc=7&wdrldc=1&wdrldr=AccessTokenExpiredWarning%2CRefreshingExpiredAccessT&cid=6db4f7a0-f373-4d0d-a7be-04f6b523e05d&clickparams=eyJBcHBOYW1lIjoiVGVhbXMtRGVza3RvcCIsIkFwcFZlcnNpb24iOiIyOC8yMzAyMDUwMTQyMSIsIkhhc0ZlZGVyYXRlZFVzZXIiOnRydWV9
    '''
    try:
        csv_data_file = open(path, 'r')
    except FileNotFoundError as err:
        print(err)
        return {}
    except Exception as err:
        print(err)
        return {}

    component_types = {}
    csv_handle = csv.DictReader(csv_data_file)
    for row in csv_handle:
        category = row['Category']
        code = row.get('\ufeffCode')

        if category in component_types:
            component_types[category][code] = row
        else:
            component_types[category] = {
                code: row
            }

    return component_types


GALLONS_2_LITER = 3.785

WATER_UNIT_GALLONS = 0
WATER_UNIT_LITER = 1
WATER_UNITS = {
    WATER_UNIT_GALLONS: 'Gallons',
    WATER_UNIT_LITER: 'Liters'
}

TEMP_UNIT_PREFERENCE_KEY = 'TempUnitPreference'
TEMP_UNIT_FAHRENHEIT = 'F'
TEMP_UNIT_CELCIUS = 'C'
TEMP_UNITS = {
    TEMP_UNIT_FAHRENHEIT: {
        'short': 'F',
        'long': 'Fahrenheit'
    },
    TEMP_UNIT_CELCIUS: {
        'short': 'C',
        'long': 'Celsius'
    }
}
# Degrees difference needed between heat and cool
TEMP_PROTECTIVE_RANGE = 3 * 5/9     # degrees Fahrenheit converted to Celsius


# TODO: Remove unnecessary constants and nesting
HVAC_MODE_AUTO = EventValues.AUTO
HVAC_MODE_HEAT = EventValues.HEAT
HVAC_MODE_COOL = EventValues.COOL
HVAC_MODE_FAN_ONLY = EventValues.FAN_ONLY
HVAC_MODE_OFF = EventValues.OFF
HVAC_MODE_STANDBY = EventValues.STANDBY
HVAC_MODE_ERROR = EventValues.FAULT

HVAC_MODES = {
    HVAC_MODE_AUTO: {
        'short': 'Auto',
        'long': 'Auto Mode'
    },
    HVAC_MODE_HEAT: {
        'short': 'Heat',
        'long': 'Heat'
    },
    HVAC_MODE_COOL: {
        'short': 'Cool',
        'long': 'Cool'
    },
    HVAC_MODE_FAN_ONLY: {
        'short': 'Fan',
        'long': 'Fan'
    },
    HVAC_MODE_OFF: {
        'short': 'Off',
        'long': 'OFF'
    },
    HVAC_MODE_STANDBY: {
        'short': 'Standby',
        'long': 'Standby'
    }
}

TIME_MODE_AM = 'AM'
TIME_MODE_PM = 'PM'
TIME_MODE_24H = '24H'
TIME_ZONE_PREFERENCE = 'TimeZonePreference'
TIME_ZONE_EASTERN = 'US/Eastern'
TIME_ZONE_CENTRAL = 'US/Central'
TIME_ZONE_MOUNTAIN = 'US/Mountain'
TIME_ZONE_PACIFIC = 'US/Pacific'
# TIME_ZONE = {
#         TIME_ZONE_EASTERN : 'US/Eastern',
#         TIME_ZONE_CENTRAL : 'US/Central',
#         TIME_ZONE_MOUNTAIN : 'US/Mountain',
#         TIME_ZONE_PACIFIC : 'US/Pacific'
#     }
DISTANCE_UNIT_MILES = 0
DISTANCE_UNIT_KILOMETERS = 1
DISTANCE_UNITS_PREFERENCE = 'DistanceUnits'
DISTANCE_UNITS = {
    DISTANCE_UNIT_MILES: 'Miles',
    DISTANCE_UNIT_KILOMETERS: 'Kilometers'
}

# WATER_UNIT_GALLONS = 0
# WATER_UNIT_LITER = 1
# WATER_UNITS = {
#     WATER_UNIT_GALLONS: 'Gallons',
#     WATER_UNIT_LITER: 'Liters'
# }
# TEMP_UNIT_PREFERENCE_KEY = 'TempUnitPreference'
# TEMP_UNIT_FAHRENHEIT = 0
# TEMP_UNIT_CELCIUS = 1
# TEMP_UNITS = {
#     TEMP_UNIT_FAHRENHEIT: {
#         'short': 'F',
#         'long': 'Fahrenheit'
#     },
#     TEMP_UNIT_CELCIUS: {
#         'short': 'C',
#         'long': 'Celsius'
#     }
# }


# Energy
CHARGE_LVL_1_STR = '1'
CHARGE_LVL_1_5_STR = '1.5'
CHARGE_LVL_2_STR = '2'
CHARGE_LVL_PRO_POWER_STR = 'PRO'

MAX_WATER_HEATERS = 2


# Component Types from CSV
COMP_PATH = _env.data_file_path('component_types.csv')
COMPONENT_TYPES = read_component_types(COMP_PATH)


if __name__ == '__main__':
    COMP_PATH = _env.data_file_path('component_types.csv')
    COMPONENT_TYPES = read_component_types(COMP_PATH)
    [print(k, v) for k, v in COMPONENT_TYPES.items()]
