from .constants import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_FAN_ONLY,
    TEMP_UNIT_FAHRENHEIT,
    # celcius_2_fahrenheit,
    HVAC_MODES
)

from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

def get_temp_unit_preferences(units, selected):
    '''Assemble list for UI of possible options and their value.
    [
        {
            'key': 'Fahrenheit / F',
            'value': 0,
            'selected': True
        },
        {
            'key': 'Celsius / C',
            'value': 1,
            'selected': False
        }
    ]
    '''
    ui_result = []
    for key_value, names in units.items():
        result = {
            'key': f'{names["long"]} / {names["short"]}',
            'value': key_value,
            'selected': True if key_value == selected else False
        }
        ui_result.append(result)

    return ui_result


def get_ac_modes(modes, selected):
    '''
    options': [
        {
            'key': EventValues.AUTO,
            'value': 0,
            'selected': True
        },
        {
            'key': EventValues.HEAT,
            'value': 1,
            'selected': False
        },
        {
            'key': 'Cool',
            'value': 2,
            'selected': False
        },
        {
            'key': 'Fan',
            'value': 3,
            'selected': False
        }
    ],
    '''
    ui_result = []
    for key_value, names in modes.items():
        if key_value in (EventValues.STANDBY, EventValues.FAULT, EventValues.OFF):
            # Ignore
            continue
        #print("key_value", key_value)
        result = {
            'key': HVAC_MODES.get(key_value, {}).get('short'),
            'value': key_value,
            'selected': True if key_value == selected else False
        }
        ui_result.append(result)

    return ui_result


def get_fan_options(fan_modes, hvac_mode, selected):
    '''
    options: [
        {
            'key': EventValues.AUTO,
            'value': EventValues.AUTO_OFF,
            'selected': True
        },
        OR
        {
            'key': EventValues.OFF,
            'value': 0,
            'selected': True
        },


        {
            'key': EventValues.LOW,
            'value': 1,
            'selected': False
        },
        {
            'key': 'High',
            'value': 2,
            'selected': False
        }
    ],
    '''
    fan_result = []

    if hvac_mode == EventValues.FAN_ONLY:
        fan_result.append(
            {
                'key': EventValues.OFF.name,
                'value': EventValues.OFF,
                'selected': True if selected == EventValues.OFF else False
            }
        )
    elif hvac_mode == EventValues.COOL or hvac_mode == EventValues.AUTO:
        fan_result.append(
            {
                'key': EventValues.AUTO.name,
                'value': EventValues.AUTO,
                'selected': True if selected == EventValues.AUTO else False
            }
        )

    if hvac_mode == EventValues.COOL or hvac_mode == EventValues.FAN_ONLY or hvac_mode == EventValues.AUTO:
        fan_result.extend(
            [
                {
                    'key': EventValues.LOW.name,
                    'value': EventValues.LOW,
                    'selected': True if selected == EventValues.LOW else False
                },
                {
                    'key': EventValues.MEDIUM.name,
                    'value': EventValues.MEDIUM,
                    'selected': True if selected == EventValues.MEDIUM else False
                },
                {
                    'key': 'HIGH',
                    'value': EventValues.HIGH,
                    'selected': True if selected == EventValues.HIGH else False
                }
            ]
        )

    return fan_result


LOCKOUT_TEMPLATES = {
    'aw': {
        EventValues.PARK_BRAKE_APPLIED: {      # Park Brake Not Set
            'title': 'Helpful Tip',
            'subtext': 'Turn on ignition for the chassis to provide proper voltage to the awning.'
        },
        EventValues.IGNITION_ON: {
            'title': 'Awning Disabled',
            'subtext': 'Awning control is disabled because the chassis ignition is on. Turn off the ignition before use.'
        }

    },
    'so': {
        EventValues.PARK_BRAKE_APPLIED: {      # Park Brake Not Set
            'title': 'Slide-Out Disabled',
            'subtext': 'Slide-Out controls are disabled because parking brake is not engaged.'
        },
        EventValues.PSM_PB_IGN_COMBO: {      # Park Brake Not Set
            'title': 'Slide-Out Disabled',
            'subtext': 'Slide-Out controls are disabled because ignition and/or parking brake not engaged.'
        }
    },
    'ge': {
        EventValues.FUEL_EMPTY: {
            'title': 'Generator Disabled',
            'subtext': 'LP tank empty'
        }
    },
    'wh': {
        EventValues.DECALC_WATERHEATER_LOCKOUT: {
            'title': 'Water heater currently in decalcification mode',
            'subtext': 'Please wait for the process to finish'
        }
    }
}
