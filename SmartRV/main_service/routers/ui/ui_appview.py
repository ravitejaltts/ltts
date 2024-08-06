from multiprocessing.sharedctypes import Value
from fastapi import APIRouter, Request

from typing import List

from common_libs.models.gui import AppTab, AppFeature

# from main_service.modules.hardware.hal import hw_layer

from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

from main_service.modules.constants import (
    TEMP_UNIT_FAHRENHEIT,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_OFF,
    HVAC_MODE_STANDBY,
    HVAC_MODE_ERROR,
)

router = APIRouter(
    prefix='/appview',
    tags=['UI',]
)

features = {
    'lighting': {
        'name': 'AppFeatureLights',
        'title': 'Lights',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/lighting'
            }
        }
    },
    'energy': {
        'name': 'AppFeatureEms',
        'title': 'Energy Management',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/ems'
            }
        }
    },
    'refrigerator': {
        'name': 'AppFeatureRefrigerator',
        'title': 'Refrigeration',
        'subtext': None,
        'toptext_title': 'Temp',
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/refrigerator'
            }
        }
    },
    'watersystems': {
        'name': 'AppFeatureWatersystems',
        'title': 'Water Systems',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default':{
            'type': 'navigate',
            'action': {
                'href': '/home/watersystems'
            }
        }
    },
    'climate': {
        'name': 'AppFeatureClimate',
        'title': 'Climate Control',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/climatecontrol'
            }
        }
    },
    # 'inverter': {
    #     'name': 'AppFeatureInverter',
    #     'title': 'Inverter',
    #     'subtext': None,
    #     'toptext_title': None,
    #     'toptext_subtext': None,
    #     'icon': None,
    #     'actions': ['action_default',],
    #     'action_default': {
    #         'type': 'navigate',
    #         'action': {
    #             'href': '/home/inverter'
    #         }
    #     }
    # },
    'awning': {
        'name': 'AppFeatureAwning',
        'title': 'Awning',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/awning'
            }
        }
    },
    'slideout': {
        'name': 'AppFeatureSlideout',
        'title': 'Slide-Outs',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/slide-outs'
            }
        }
    },
    'petmonitoring': {
        'name': 'AppFeaturePetMonitoring',
        'title': 'Pet Minder',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/petmonitoring'
            }
        }
    },
    'fcp': {
        'name': 'AppFeatureDebug',
        'title': 'Functional Test Panel',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/functionaltests'
            }
        }
    },
    # 'ecp': {
    #     'name': 'AppFeatureEngineeringPanel',
    #     'title': 'Engineering Control Panel',
    #     'subtext': None,
    #     'toptext_title': None,
    #     'toptext_subtext': None,
    #     'icon': None,
    #     'actions': ['action_default',],
    #     'action_default': {
    #         'type': 'navigate_external',
    #         'action': {
    #             'href': 'http://localhost:8000/ecp/wgo.html'
    #         }
    #     }
    # },
    # 'uitest': {
    #     'name': 'AppFeatureUITestPanel',
    #     'title': 'UI Test Panel',
    #     'subtext': None,
    #     'toptext_title': None,
    #     'toptext_subtext': None,
    #     'icon': None,
    #     'actions': ['action_default',],
    #     'action_default': {
    #         'type': 'navigate',
    #         'action': {
    #             'href': '/home/uitests'
    #         }
    #     }
    # },
    # 'generator': {
    #     'name': 'AppFeatureGeneratorPanel',
    #     'title': 'Generator',
    #     'subtext': None,
    #     'toptext_title': None,
    #     'toptext_subtext': None,
    #     'icon': None,
    #     'actions': ['action_default',],
    #     'action_default': {
    #         'type': 'navigate',
    #         'action': {
    #             'href': '/home/generator'
    #         }
    #     }
    # },
    'manufacturing': {
        'name': 'AppFeatureManufacturing',
        'title': 'Manu- facturing',
        'subtext': None,
        'toptext_title': None,
        'toptext_subtext': None,
        'icon': None,
        'actions': ['action_default',],
        'action_default': {
            'type': 'navigate',
            'action': {
                'href': '/home/manufacturing'
            }
        }
    },
}

features_overrides = {
    'BF848EC': {
        'slideout': 'hidden',
        'awning': 'hidden',
        'fcp': 'debugOnly',
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
    },
    'DOMCOACH': {
        'slideout': 'hidden',
        'awning': 'hidden',
        'fcp': 'debugOnly',
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
    },
    'WM524T': {
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
        'fcp': 'debugOnly',
    },
    'IM524T': {
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
        'fcp': 'debugOnly',
    },
    'WM524R': {
        'ecp': 'hidden',
        'uitest': 'hidden',
        'manufacturing': 'hidden',
        'fcp': 'debugOnly',
    },
    'IM524R': {
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
        'fcp': 'debugOnly',
    },
    'WM524D': {
        'fcp': 'debugOnly',
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
    },
    'IM524D': {
        'fcp': 'debugOnly',
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
    },
    'WM524NP': {
        'fcp': 'debugOnly',
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
    },
    'IM524NP': {
        'fcp': 'debugOnly',
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
    },
    'ROBO500': {
        'ecp': 'debugOnly',
        'uitest': 'debugOnly',
        'manufacturing': 'debugOnly',
        'fcp': 'debugOnly',
    },
    'VANILLA': {
        'lighting': 'hidden',
        'energy': 'hidden',
        'refrigerator': 'hidden',
        'watersystems': 'hidden',
        'climate': 'hidden',
        'inverter': 'hidden',
        'fcp': 'hidden',
        'ecp': 'hidden',        # TODO: See if this can be made useful for manufacturing
        'slideout': 'hidden',
        'awning': 'hidden',
        'uitest': 'hidden',
        'manufacturing': None,
    }
}

DEFAULT = {
    'refrigerator': 'hidden',
    'inverter': 'hidden',
    'generator': 'hidden',
    'fcp': 'hidden',
    'ecp': 'hidden',        # TODO: See if this can be made useful for manufacturing
    'uitest': 'hidden',
    'manufacturing': None
}


@router.get('', response_model=List[AppTab])
async def get_appview(request: Request):
    '''List of subsystems / app view.'''

    app_features = []
    floorplan = request.app.hal.floorPlan
    floorplan_details = features_overrides.get(floorplan, DEFAULT)

    # For vanilla we want to force only the manufacturing screen and navigate there automatically
    if floorplan == 'VANILLA':
        return [
            AppTab(
                title='Features',
                items=[
                    features.get('manufacturing'),
                ]
            ),
        ]

    debug_menus = request.app.config.get('settings', {}).get('debugEnabled', False)
    # Get Status for each app
    # Lights
    # Get current status of lights
    light_status = request.app.hal.lighting.handler.light_status()

    lights_on = light_status.get('on')
    master_sub_text = f'{lights_on} Light{"s" if lights_on > 1 else ""} On'
    if lights_on == 0:
        master_sub_text = 'All lights off'
    features['lighting']['subtext'] = master_sub_text

    # Get Inverter Data

    if 'inverter' in features:
        quick_inverter_onOff = request.app.hal.energy.handler.inverter[1].state.onOff
        quick_inverter_subtext = 'On' if quick_inverter_onOff else 'Off'
        features['inverter']['subtext'] = quick_inverter_subtext

    # Climate Overview
    climate_zone_id = 1
    current_temp_unit = request.app.config.get('climate', {}).get('TempUnitPreference', TEMP_UNIT_FAHRENHEIT)

    thermostat = request.app.hal.climate.handler.thermostat[climate_zone_id]

    current_hvac_mode = thermostat.state.setMode
    current_tstat_state = thermostat.state.mode

    climate_zone_temp_settings = request.app.hal.climate.handler.get_climate_zone_temp_config(climate_zone_id, temp_unit=current_temp_unit)

    # Make sure we show only int not float
    heat_temp_set = int(climate_zone_temp_settings.get(EventValues.HEAT.name))
    cool_temp_set = int(climate_zone_temp_settings.get(EventValues.COOL.name))

    # New version
    if current_tstat_state == HVAC_MODE_HEAT:
        climate_subtext = f'Heat is on till {heat_temp_set}'
    elif current_tstat_state == HVAC_MODE_COOL:
        climate_subtext = f'Cool is on till {cool_temp_set}'
    elif current_tstat_state == HVAC_MODE_FAN_ONLY:
        climate_subtext = f'Fan Only Mode'
    elif current_tstat_state == HVAC_MODE_OFF:
        climate_subtext = f'Climate Off'
    elif current_tstat_state == HVAC_MODE_STANDBY:
        climate_subtext = 'Idle'
    else:
        # TODO: Check all possible states are properly handled
        # If there is no state known it will be None
        # Try to avoid by setting a default state if it makse sense
        # This caused issues not updating
        # climate_subtext = EventValues.OFF
        # climate_subtext = f'{current_hvac_state}'
        climate_subtext = f'Initializing'

    # Check if Thermostat is off
    #climate_zone_onOff = request.app.hal.climate.handler.get_zone(climate_zone_id)
    #climate_zone_onOff = 1 if climate_zone_onOff == None else climate_zone_onOff
    climate_zone_onOff = thermostat.state.onOff

    if climate_zone_onOff == 0:
        climate_subtext = f'Climate Off'

    internal_temp = thermostat.get_temperature(current_temp_unit)
    climate_toptext_title = 'Inside Temp'
    if internal_temp is None:
        internal_temp = '--'
    climate_toptext_subtext = f'{internal_temp}°'

    features['climate']['subtext'] = climate_subtext
    features['climate']['toptext_title'] = climate_toptext_title
    features['climate']['toptext_subtext'] = climate_toptext_subtext

    # Refrigerator
    # TODO: Get list from HW
    if hasattr(request.app.hal.climate.handler, 'refrigerator'):
        for instance, fridge in request.app.hal.climate.handler.refrigerator.items():
            if fridge.attributes.get('type') == 'REFRIGERATOR':
                current_fridge_temp = fridge.get_temperature(current_temp_unit)
                current_fridge_temp_toptext = f'{current_fridge_temp}°'

                features['refrigerator']['toptext_subtext'] = current_fridge_temp_toptext

                # TODO: Get from HW or Config
                alert_set = request.app.config.get('refrigerator', {}).get('TempAlertThreshold')
                if alert_set is None:
                    fridge_alert_text = ''
                else:
                    fridge_alert_text = 'Alert Set'

                features['refrigerator']['subtext'] = fridge_alert_text

    # Watersystems (get from HW)
    if hasattr(request.app.hal.watersystems.handler, 'water_pump'):
        water_pump = request.app.hal.watersystems.handler.water_pump[1]
        water_systems_subtext = ''
        if water_pump.state.onOff == EventValues.ON:
            water_systems_subtext = 'Water Pump On'

        features['watersystems']['subtext'] = water_systems_subtext

    if hasattr(request.app.hal, 'movables') and hasattr(request.app.hal.movables.handler, 'slideout'):
        slideout = request.app.hal.movables.handler.slideout[1]
        if slideout.state.mode in (EventValues.EXTENDING, EventValues.RETRACTING):
            slideout_state_text = slideout.state.mode.name.capitalize()
        else:
            slideout_state_text = 'Off'

        features['slideout']['subtext'] = slideout_state_text

    for feat_name, feature in features.items():
        if feature.get('name') is None:
            print(f'Feature not defined: {feat_name}')
            continue

        enabled_state = floorplan_details.get(feat_name)
        show = None
        if enabled_state == 'debugOnly' and debug_menus is False:
            show = False
        elif enabled_state == 'hidden':
            show = False
        else:
            show = True

        # Component based overrides
        # If some components are not provided in the option codes there is no reason to show the app tile
        if feat_name == 'generator':
            # Generator App tile is permanently disabled, need to refactor feature list vs. removing it here.
            show = False
            # Check if there is a generator available
            if not hasattr(request.app.hal.energy.handler, 'generator'):
                show = False

        elif feat_name == 'awning':
            if not hasattr(request.app.hal, 'movables') or not hasattr(request.app.hal.movables.handler, 'awning'):
                show = False

        elif feat_name == 'refrigerator':
            if not hasattr(request.app.hal.climate.handler, 'refrigerator'):
                show = False

        elif feat_name == 'petmonitoring':
            if not hasattr(request.app.hal.features.handler, 'pet_monitoring'):
                show = False
            else:
                # Add subtext on or off
                try:
                    pet_mon = request.app.hal.features.handler.pet_monitoring[1]
                except KeyError as err:
                    print(err)
                    show = False
                    features['petmonitoring']['subtext'] = 'ERROR'

                pet_mon_subtext = 'NA'
                if pet_mon.state.onOff == EventValues.ON:
                    pet_mon_subtext = 'On'
                elif pet_mon.state.onOff == EventValues.OFF:
                    pet_mon_subtext = 'Off'
                else:
                    pet_mon_subtext = 'ERR'

                features['petmonitoring']['subtext'] = pet_mon_subtext

                # TODO: Get clarification if this tile should show or not if feature is disabled

        if show is True:
            app_feature = AppFeature(
                name=feature.get('name'),
                title=feature.get('title'),
                subtext=feature.get('subtext'),
                toptext_title=feature.get('toptext_title'),
                toptext_subtext=feature.get('toptext_subtext'),
                icon=feature.get('icon'),
                actions=feature.get('actions'),
                action_default=feature.get('action_default')
            )
            app_features.append(app_feature)


    response = [
        AppTab(
            title='Features',
            items=app_features
        ),
        # AppTab(
        #     title='Automations',
        #     items=[
        #         AppFeature(
        #             name='AppAutomationSchedule',
        #             title='Automation Schedule',
        #             subtext='3 Automations',
        #             toptext_title=None,
        #             toptext_subtext=None,
        #             icon=None,
        #             actions=['action_default',],
        #             action_default={
        #                 'type': 'navigate',
        #                 'action': {
        #                     'href': '/home/automations'
        #                 }
        #             }
        #         ),
        #         AppFeature(
        #             name='AppAutomationSmartbuttons',
        #             title='Smart Buttons',
        #             subtext='4 Buttons',
        #             toptext_title=None,
        #             toptext_subtext=None,
        #             icon=None,
        #             actions=['action_default',],
        #             action_default={
        #                 'type': 'navigate',
        #                 'action': {
        #                     'href': '/home/smartbuttons'
        #                 }
        #             }
        #         )
        #     ]
        # ),
        # AppTab(
        #     title='Reports',
        #     items=[
        #         AppFeature(
        #             name='AppReportBattLevels',
        #             title='Battery Levels',
        #             subtext='Historic Data',
        #             toptext_title=None,
        #             toptext_subtext=None,
        #             icon=None,
        #             actions=['action_default',],
        #             action_default={
        #                 'type': 'navigate',
        #                 'action': {
        #                     'href': '/home/history/battery'
        #                 }
        #             }
        #         ),
        #         AppFeature(
        #             name='AppReportFreshLevels',
        #             title='Fresh Water',
        #             subtext='Historic Data',
        #             toptext_title=None,
        #             toptext_subtext=None,
        #             icon=None,
        #             actions=['action_default',],
        #             action_default={
        #                 'type': 'navigate',
        #                 'action': {
        #                     'href': '/home/history/freshwater'
        #                 }
        #             }
        #         ),
        #         AppFeature(
        #             name='AppReportWasteLevels',
        #             title='Waste Tanks',
        #             subtext='Historic Data',
        #             toptext_title=None,
        #             toptext_subtext=None,
        #             icon=None,
        #             actions=['action_default',],
        #             action_default={
        #                 'type': 'navigate',
        #                 'action': {
        #                     'href': '/home/history/wastewater'
        #                 }
        #             }
        #         )
        #     ]
        # )
    ]
    return response
