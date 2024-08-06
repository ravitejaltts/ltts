import json
import sys

from common_libs.models.common import  EventValues
from common_libs import environment

_env = environment()

# setting path
sys.path.append('../../SmartRV')

from main_service.modules.constants import (
    fahrenheit_2_celcius
)

#This holds the default configuration dictionary for the 848 ec  in this file
config_848ec = {
    'hal_cfg': {
        'lighting': 'modules.hardware._800.hw_lighting',
        'watersystems': 'modules.hardware._800.hw_watersystems',
        'electrical': 'modules.hardware._800.hw_electrical',
        'climate': 'modules.hardware._800.hw_climate',
        'energy': 'modules.hardware._800.hw_energy',
        'vehicle': 'modules.hardware._800.hw_vehicle',
        },

    'electrical_mapping': {
        'ac': {},
        'dc': {
            0x05: {
                'id': 0x05,
                'output_id': 1,
                'short': 'LightController1',
                'long': 'A.1 Lighting controller 1 (Z1-Z4)',
                'description': 'Controls power to ITC lighting controller 1 20DC'
            },
            0x06: {
                'id': 0x06,
                'output_id': 2,
                'short': 'LightController2',
                'long': 'A.2 Lighting controller 2 (Z5-Z8)',
                'description': 'Controls power to ITC lighting controller 2 20DD'
            },
            0x21: {
                'id': 0x21,
                'output_id': 3,
                'short': '12VDCPowerPort/Dometic RVC',
                'long': 'A.3 12VDCPowerPort/Dometic RVC',
                'description': ''
            },
            0x16: {
                'id': 0x16,
                'output_id': 4,
                'short': 'Refrigerator',
                'long': 'A.4 Refrigerator',
                'description': 'Refrigerator power on/off, does not control compressor or fridge settings'
            },
            0x22: {
                'id': 0x22,
                'output_id': 5,
                'short': 'ACCompressor',
                'long': 'B.1 AC Compressor On/Off control',
                'description': ''
            },
            0x0d: {
                'id': 0x0d,
                'output_id': 6,
                'short': 'ProPower',
                'long': 'B.2 Pro Power Relay',
                'description': 'Switches Pro Power input on/off'
            },
            0x07: {
                'id': 0x07,
                'output_id': 7,
                'short': 'FreshWaterPump',
                'long': 'B.3 Fresh Water Pump Power',
                'description': 'Provides power to Fresh water pump, fresh water pump might stop when enough pressure is built up.'
            },
            0x08: {
                'id': 0x08,
                'output_id': 8,
                'short': 'GreyWaterPump',
                'long': 'B.4 Gray Water Pump',
                'description': 'Provides power to the gray water pump, pump might not operate when senspore does not detect water.'
            },
            0x09: {
                'id': 0x09,
                'output_id': 9,
                'short': 'RoofFan',
                'long': 'B.5 Roof Vent Fan Power',
                'description': 'Provides power to the roof fan (does not control other than power on/off)'
            },
            0x0b: {
                'id': 0x0b,
                'output_id': 11,
                'short': 'WinnConnect',
                'long': 'B.7 WinnConnect Power on/off',
                'description': 'Turns power to WinnConnect on/off'
            },
            0x0c: {
                'id': 0x0c,
                'output_id': 12,
                'short': 'KiBPower',
                'long': 'B.8 KiB Sensor Power Regulator',
                'description': 'Provides power to the KiB Sensors through a 12V to 5V regulator.'
            },
            0x11: {
                'id': 0x11,
                'output_id': 13,
                'short': 'ACFanHigh',
                'long': 'B.9 AC Fan High',
                'description': 'Sets AC fan speed to on and high speed'
            },
            0x0e: {
                'id': 0x0e,
                'output_id': 14,
                'short': 'LightZone9',
                'long': 'B.10 Lighting Zone 9 (Front)',
                'description': 'Provides Power to Lighting Zone 9 (Front)'
            },
            0x0f: {
                'id': 0x0f,
                'output_id': 15,
                'short': 'LightZone10',
                'long': 'B.11 Lighting Zone 10 (Rear)',
                'description': 'Provides Power to Lighting Zone 10 (Rear)'
            },
            0x10: {
                'id': 0x10,
                'output_id': 16,
                'short': 'ACFanLow',
                'long': 'B.12 AC Fan Low',
                'description': 'Sets AC Fan speed to on and low speed'
            },
            0x12: {
                'id': 0x12,
                'output_id': 18,
                'short': 'TechCabFan',
                'long': 'C.4 Tech Cabinet Fan Power',
                'description': None
            },
            0x13: {
                'id': 0x13,
                'output_id': 19,
                'short': 'Heater',
                'long': 'C.5 Space Heater Relay',
                'description': ''
            },
            0x19: {
                'id': 0x19,
                'output_id': 20,
                'short': 'WirelessCharger',
                'long': 'C.6 Wireless Charger Power',
                'description': ''
            },
            0x15: {
                'id': 0x15,
                'output_id': 21,
                'short': 'Inverter',
                'long': 'C.7 Inverter Internal Relay on/off',
                'description': 'Turns inverter on and off'
            },
            0x17: {
                'id': 0x17,
                'output_id': 23,
                'short': 'Wineguard',
                'long': 'C.9 Wineguard Router Power',
                'description': ''
            },
            0x18: {
                'id': 0x18,
                'output_id': 24,
                'short': 'Water Heater',
                'long': 'C.10 Water Heater Relay',
                'description': '',
                'inverted': True

            },
        },
        'switches': {
            'bank_4': {
                1: {'last_modified': None, 'onOff': None},
                2: {'last_modified': None, 'onOff': None},
                3: {'last_modified': None, 'onOff': None},
                4: {'last_modified': None, 'onOff': None},
                5: {'last_modified': None, 'onOff': None},
                6: {'last_modified': None, 'onOff': None},
                7: {'last_modified': None, 'onOff': None},
                8: {'last_modified': None, 'onOff': None}
            }
        }
    },

    'climate_defaults': {
        # Single Zone system
        'num_zones': 1,
        'zone_1': {
            # Currently set temperature to reach, might cause heating or cooling
            # if system is off, then will not
            'set_temperature': fahrenheit_2_celcius(73),
            # HVAC mode
            #0 off
            #1 cooling
            #2 heating
            #3 fan
            'hvac_mode': EventValues.AUTO.value,
            'set_temperature_AUTO': fahrenheit_2_celcius(70),
            'set_temperature_COOL': fahrenheit_2_celcius(78),
            'set_temperature_HEAT': fahrenheit_2_celcius(68),
        },
        # Sets the min temp the HW supports
        # Change to celcius
        'min_temp_set': fahrenheit_2_celcius(60),
        # Sets the max temp the HW supports
        # Change to celcius
        'max_temp_set': fahrenheit_2_celcius(95),
        'initial_state': {
            # Premier Fan
            'zone_1__fan_1': {
                'fanSpd': EventValues.AUTO_OFF.value,
                'compressor': 0
            },
            # Dometic Fans
            'zone_1__fan_2': {
                'onOff': 0,
                'fanSpd': EventValues.OFF.value,
                'dome': 0,
                'direction': EventValues.FAN_OUT.value
            },
            'zone_1_climate_mode': EventValues.AUTO.value,
            'zone_1__onOff': 1
        },
        'fan_mapping': {
            1: 4,
            # Dometic isntance 4
            2: 4,
            4: 4
        }
    }
}


if __name__ == '__main__':
    print(config_848ec)

    with open(_env.storage_file_path('Default_Config.json'), 'w') as out_file:
        json.dump(config_848ec, out_file, indent=4, sort_keys=True)
