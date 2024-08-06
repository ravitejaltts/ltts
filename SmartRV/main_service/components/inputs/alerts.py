import json

from common_libs.models.notifications import NotificationTrigger, NotificationPriority
from common_libs.models.common import EventValues, RVEvents


ALERTS = {
    RVEvents.FRESH_WATER_TANK_FULL: {
        "notification_id": RVEvents.FRESH_WATER_TANK_FULL,
        "instance": 1,
        "priority": NotificationPriority.System_Notice,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.FRESH_WATER_TANK_FULL}",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [97, 66],
        "header": "Your Fresh Water Tank is full",
        "msg": "Fresh water tank is full",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.FRESH_WATER_TANK_NOTICE: {
        "notification_id": RVEvents.FRESH_WATER_TANK_NOTICE,
        "instance": 1,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": "watersystems:wt50034",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.LOW,
        "trigger_value": [25, 50],
        "header": "Fresh water tank is at 25%",
        "msg": "Fresh water tank is low",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence':
                    {
                        'over': [],
                        'under': [
                            RVEvents.FRESH_WATER_TANK_BELOW,
                            RVEvents.FRESH_WATER_TANK_EMPTY
                        ]
                    }
            }
        )
    },
    RVEvents.FRESH_WATER_TANK_BELOW: {
        "notification_id": RVEvents.FRESH_WATER_TANK_BELOW,
        "instance": 1,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": "watersystems:wt50008",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.LOW,
        "trigger_value": [10, 33],
        "header": "Fresh water tank is at 10%",
        "msg": "Fresh water tank is very low.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [RVEvents.FRESH_WATER_TANK_NOTICE],
                    'under': [RVEvents.FRESH_WATER_TANK_EMPTY]
                }
            }
        )
    },
    RVEvents.FRESH_WATER_TANK_EMPTY: {
        "notification_id": RVEvents.FRESH_WATER_TANK_EMPTY,
        "instance": 1,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": "watersystems:wt50007",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.LOW,
        "trigger_value": [3, 33],
        "header": "Your Fresh Water Tank is empty",
        "msg": "Fresh water tank is empty!",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.FRESH_WATER_TANK_NOTICE,
                        RVEvents.FRESH_WATER_TANK_BELOW
                    ],
                    'under': []
                }
            }
        )
    },
    RVEvents.GREY_WATER_TANK_NOTICE: {
        "notification_id": RVEvents.GREY_WATER_TANK_NOTICE,
        "instance": 2,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": "watersystems:wt50035",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [75, 50],
        "header": "Your Grey Water Tank is at 75%",
        "msg": "Grey water tank is high!",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [],
                    'under': [
                        RVEvents.GREY_WATER_TANK_ABOVE,
                        RVEvents.GREY_WATER_TANK_FULL
                    ]
                }
            }
        )
    },
    RVEvents.GREY_WATER_TANK_ABOVE: {
        "notification_id": RVEvents.GREY_WATER_TANK_ABOVE,
        "instance": 2,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": "watersystems:wt50011",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [90, 66],
        "header": "Your Grey Water Tank is at 90%",
        "msg": "Grey water tank is very high.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.GREY_WATER_TANK_NOTICE
                    ],
                    'under': [
                        RVEvents.GREY_WATER_TANK_FULL
                    ]
                }
            }
        )
    },
    RVEvents.GREY_WATER_TANK_FULL: {
        "notification_id": RVEvents.GREY_WATER_TANK_FULL,
        "instance": 2,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": "watersystems:wt50012",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [98, 66],
        "header": "Your Grey Water Tank is at full",
        "msg": "Grey Water is at the top!",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.GREY_WATER_TANK_ABOVE,
                        RVEvents.GREY_WATER_TANK_NOTICE
                    ],
                    'under': []
                }
            }
        )
    },
    RVEvents.BATTERY_CHARGE_LOW: {
        "notification_id": RVEvents.BATTERY_CHARGE_LOW,
        "instance": 1,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": "energy:ba50021",
        "trigger_events": [
            RVEvents.BMS_STATE_OF_CHARGE_CHANGE
        ],
        "trigger_type": NotificationTrigger.LOW,
        "trigger_value": [15, 33],
        "header": "Battery low",
        "msg": "Battery level very low.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [],
                    'under': [
                        RVEvents.BATTERY_CHARGE_LOW_CUTOFF
                    ]
                }
            }
        )
    },
    RVEvents.BATTERY_CHARGE_LOW_CUTOFF: {
        "notification_id": RVEvents.BATTERY_CHARGE_LOW_CUTOFF,
        "instance": 1,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": "energy:ba50017",
        "trigger_events": [
            RVEvents.BMS_STATE_OF_CHARGE_CHANGE
        ],
        "trigger_type": NotificationTrigger.LOW,
        "trigger_value": [2, 33],
        "header": "Battery OFF",
        "msg": "Battery Turned OFF, out of power!",
        "type": 1,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.BATTERY_CHARGE_LOW,
                    ],
                    'under': []
                }
            }
        ),
    },
    RVEvents.REFRIGERATOR_OUT_OF_RANGE: {
        "notification_id": RVEvents.REFRIGERATOR_OUT_OF_RANGE,
        "instance": 1,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": f"climate:rf{RVEvents.REFRIGERATOR_OUT_OF_RANGE.value}",
        "trigger_events": [
            RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE
        ],
        "trigger_type": NotificationTrigger.RANGE,
        "trigger_value": [4, 8],
        "header": "Refrigerator Temp",
        "msg": "Refrigerator Temp. out of range!",
        "type": 0,
        "meta": "{}",
    },
    RVEvents.FREEZER_OUT_OF_RANGE: {
        "ts_id": 0,
        "notification_id": RVEvents.FREEZER_OUT_OF_RANGE,
        "instance": 2,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": f"climate:fr{RVEvents.FREEZER_OUT_OF_RANGE.value}",
        "trigger_events": [
            RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE
        ],
        "trigger_type": NotificationTrigger.RANGE,
        "trigger_value": [-4, 0],
        "header": "Freezer Temp",
        "msg": "Freezer Temp. out of range!",
        "type": 0,
        "meta": "{}",
    },
    RVEvents.COACH_TEMP_LOW: {
        "notification_id": RVEvents.COACH_TEMP_LOW,
        "instance": 1,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"climate:th{RVEvents.COACH_TEMP_LOW}",
        "trigger_events": [
            RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE
        ],
        "trigger_type": NotificationTrigger.LOW,
        "trigger_value": [0.0, 7.0],
        "header": "Coach Temperature Low",
        "msg": "Coach temperature is low!",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.COACH_TEMP_HIGH: {
        "notification_id": RVEvents.COACH_TEMP_HIGH,
        "instance": 1,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"climate:th{RVEvents.COACH_TEMP_HIGH.value}",
        "trigger_events": [
            RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [35.0, 28.0],
        "header": "Coach Temperature High",
        "msg": "Coach temperature is high!",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.USER_NEEDS_TO_ACKNOWLEDGE_OTA_UPDATE: {
        "notification_id": RVEvents.USER_NEEDS_TO_ACKNOWLEDGE_OTA_UPDATE,
        "instance": 1,
        "priority": NotificationPriority.System_Notice,
        "user_selected": 1,
        "code": f"system:ot{RVEvents.USER_NEEDS_TO_ACKNOWLEDGE_OTA_UPDATE}",
        "trigger_events": [
            RVEvents.OTA_UPDATE_RECEIVED
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 32.22,
        "header": "OTA Received",
        "msg": "New Software Update Available",
        "type": 0,
        "meta": json.dumps(
            {
                'actions': {
                    'navigate': {
                        'action': {
                            'text': 'Details',
                            'href': "/setting/UiSettingsSoftwareUpdate"
                        }
                    }
                }
            }
        ),
    },
    RVEvents.SERVICE_MODE_ACTIVE: {
        "notification_id": RVEvents.SERVICE_MODE_ACTIVE,
        "instance": 1,
        "priority": NotificationPriority.System_Notice,
        "user_selected": 1,
        "code": f"system:ot{RVEvents.SERVICE_MODE_ACTIVE}",
        "trigger_events": [
            RVEvents.WINNCONNECT_SYSTEM_SETTINGS_SERVICE_MODE_CHANGE
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "Service Mode",
        "msg": "Service Mode is Active",
        "type": 0,
        "meta": json.dumps(
           {
                'actions': {
                    'api_call': {
                        'action': {
                            "type": 'PUT',
                            "text": "Exit Service Mode",
                            "href": "/api/system/us/1/state",
                            "params": {
                                "serviceModeOnOff": 0,
                            }
                        }
                    }
                }
            }
        ),
    },
    # TODO: Bring back with proper instances
    # "51000": {
    #     "notification_id": 51000,
    #     "instance": 1,        # Water Heater DSA would be 101
    #     "priority": 1,
    #     "user_selected": 1,
    #     "code": "system:cx51000",
    #     "trigger_events": [
    #         RVEvents.WINNCONNECT_SYSTEM_CAN_BUS_RVC_RED_LAMP_CHANGE
    #     ],
    #     "trigger_type": NotificationTrigger.ON,
    #     "trigger_value": 1,
    #     "header": "Water Heater Controller TM-620",
    #     "msg": "Water Heater Controller reporting a CAN issue",
    #     "type": 0
    # },
    RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT: {
        "notification_id": RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT,
        "instance": 1,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": f"features:pm{RVEvents.WATER_HEATER_OPERATING_LIN_FAILURE_ALERT}",
        "trigger_events": [
            RVEvents.WATER_HEATER_ERROR_CODES
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        # Header can message changed per PM (25 from spread sheet) requirement
        "header": "Truma AquaGo Connnection Error",
        "msg": "There is an issue with the lin cable communication from the Truma AquaGo.",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT: {
        "notification_id": RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT,
        "instance": 2,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": f"features:pm{RVEvents.WATER_HEATER_OPERATING_ERROR_FAILURE_ALERT}",
        "trigger_events": [
            RVEvents.WATER_HEATER_ERROR_CODES
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        # Header can message changed per PM (25 from spread sheet) requirement
        "header": "Truma AquaGO Error.",
        "msg": "There is an issue with your Truma AquaGo, check that the physical switch is on.",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.PET_MONITOR_TEMP_LOW_ALERT: {
        "notification_id": RVEvents.PET_MONITOR_TEMP_LOW_ALERT,
        "instance": 1,
        "priority": NotificationPriority.Pet_Minder_Warning,
        "user_selected": 1,
        "code": f"features:pm{RVEvents.PET_MONITOR_TEMP_LOW_ALERT}",
        "trigger_events": [
            RVEvents.PET_MONITOR_TEMP_LOW
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "RV Temp Below Pet Comfort",
        "msg": "Please consider turning the heat on in your coach.",
        "type": 0,
        "meta": json.dumps(
            {
                'actions': {
                    'api_call': {
                        'action': {
                            "type": 'PUT',
                            "text": "Auto Mode",
                            "href": "/api/climate/th/1/state",
                            "params": {
                                "onOff": 1,
                                "setMode": EventValues.AUTO
                            }
                        }
                    }
                }
            }
        )
    },
    RVEvents.PET_MONITOR_TEMP_HIGH_ALERT: {
        "notification_id": RVEvents.PET_MONITOR_TEMP_HIGH_ALERT,
        "instance": 1,
        "priority": NotificationPriority.Pet_Minder_Warning,
        "user_selected": 1,
        "code": f"features:pm{RVEvents.PET_MONITOR_TEMP_HIGH_ALERT}",
        "trigger_events": [
            RVEvents.PET_MONITOR_TEMP_HIGH
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "RV Temp Above Pet Comfort",
        "msg": "Please consider turning the air conditioning on in your coach.",
        "type": 0,
        "meta": json.dumps(
            {
                'actions': {
                    'api_call': {
                        'action': {
                            "type": 'PUT',
                            "text": "Auto Mode",
                            "href": "/api/climate/th/1/state",
                            "params": {
                                "onOff": 1,
                                "setMode": EventValues.AUTO
                            }
                        }
                    }
                }
            }
        )
    },
    RVEvents.PET_MONITOR_BATTERY_LOW_ALERT: {
        "notification_id": RVEvents.PET_MONITOR_BATTERY_LOW_ALERT,
        "instance": 1,
        "priority": NotificationPriority.Pet_Minder_Warning,
        "user_selected": 1,
        "code": f"features:pm{RVEvents.PET_MONITOR_BATTERY_LOW_ALERT}",
        "trigger_events": [
            RVEvents.PET_MONITOR_BATTERY_LOW
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        # Header can message changed per PM (25 from spread sheet) requirement
        "header": "RV Battery Is Low.",
        "msg": "Your RV battery is low. Please turn on the generator or plug in to Shore Power.",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.BLACK_WATER_TANK_NOTICE: {
        "notification_id": RVEvents.BLACK_WATER_TANK_NOTICE,
        "instance": 3,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.BLACK_WATER_TANK_NOTICE}",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [75, 50],
        "header": "Your Black Water Tank is at 75%",
        "msg": "Black water tank level is high",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [],
                    'under': [
                        RVEvents.BLACK_WATER_TANK_ABOVE,
                        RVEvents.BLACK_WATER_TANK_FULL
                    ]
                }
            }
        )
    },
    RVEvents.BLACK_WATER_TANK_ABOVE: {
        "notification_id": RVEvents.BLACK_WATER_TANK_ABOVE,
        "instance": 3,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.BLACK_WATER_TANK_ABOVE}",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [90, 66],
        "header": "Your Black Water Tank is at 90%",
        "msg": "Black water tank level is high.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.BLACK_WATER_TANK_NOTICE
                    ],
                    'under': [
                        RVEvents.BLACK_WATER_TANK_FULL
                    ]
                }
            }
        )
    },
    RVEvents.BLACK_WATER_TANK_FULL: {
        "notification_id": RVEvents.BLACK_WATER_TANK_FULL,
        "instance": 3,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": f"watersystems:{RVEvents.BLACK_WATER_TANK_FULL}",
        "trigger_events": [
            RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE
        ],
        "trigger_type": NotificationTrigger.HIGH,
        "trigger_value": [97, 66],
        "header": "Your Black Water Tank is full",
        "msg": "Black Water is at the top!",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.BLACK_WATER_TANK_ABOVE,
                        RVEvents.BLACK_WATER_TANK_NOTICE
                    ],
                    'under': []
                }
            }
        )
    },
    RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_AC_LOCK: {
        "notification_id": RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_AC_LOCK,
        "instance": 1,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_AC_LOCK}",
        "trigger_events": [
            RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "Inverter Overload: A/C has been disabled",
        "msg": "AC disabled to save power until capacity becomes available.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [],
                    'under': [
                        RVEvents.LOAD_SHEDDING_GENERIC_ALERT.value,
                        RVEvents.LOAD_SHEDDING_MICROWAVE_SHED.value,
                        RVEvents.LOAD_SHEDDING_COOKTOP_SHED.value
                    ]
                }
            }
        )
    },
    RVEvents.LOAD_SHEDDING_MICROWAVE_SHED: {
        "notification_id": RVEvents.LOAD_SHEDDING_MICROWAVE_SHED,
        "instance": 3,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.LOAD_SHEDDING_MICROWAVE_SHED}",
        "trigger_events": [
            RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": " Inverter Overload: Microwave has been disabled.",
        "msg": " Microwave, Cooktop, and A/C disabled to save power until capacity becomes available.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_AC_LOCK.value,
                        RVEvents.LOAD_SHEDDING_COOKTOP_SHED.value
                    ],
                    'under': [
                        RVEvents.LOAD_SHEDDING_GENERIC_ALERT.value
                    ]
                }
            }
        )
    },
    RVEvents.LOAD_SHEDDING_COOKTOP_SHED: {
        "notification_id": RVEvents.LOAD_SHEDDING_COOKTOP_SHED,
        "instance": 2,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:{RVEvents.LOAD_SHEDDING_COOKTOP_SHED}",
        "trigger_events": [
            RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "Inverter Overload: Cooktop has been disabled",
        "msg": "Cooktop and A/C disabled to save power until capacity becomes available.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_AC_LOCK.value
                    ],
                    'under': [
                        RVEvents.LOAD_SHEDDING_GENERIC_ALERT.value,
                        RVEvents.LOAD_SHEDDING_MICROWAVE_SHED.value
                    ]
                }
            }
        )
    },
    RVEvents.LOAD_SHEDDING_GENERIC_ALERT: {
        "notification_id": RVEvents.LOAD_SHEDDING_GENERIC_ALERT,
        "instance": 4,
        "priority": NotificationPriority.System_Critical,
        "user_selected": 1,
        "code": f"watersystems:{RVEvents.LOAD_SHEDDING_GENERIC_ALERT}",
        "trigger_events": [
            RVEvents.ENERGY_CONSUMER_SHED_CHANGE.value
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "Inverter Overloaded!",
        "msg": "Unable to prevent overload. You may need to restart the inverter to restore AC power.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.LOAD_SHEDDING_CLIMATE_ZONE_AC_LOCK.value,
                        RVEvents.LOAD_SHEDDING_MICROWAVE_SHED.value,
                        RVEvents.LOAD_SHEDDING_COOKTOP_SHED.value
                    ],
                    'under': []
                }
            }
        )
    },
    # Component not responding via RV-C communications
    # TODO: Finish adding and implementing
    RVEvents.RVC_COMPONENT_NOT_RESPONDING: {
        "notification_id": RVEvents.RVC_COMPONENT_NOT_RESPONDING,
        "instance": 3,
        "priority": NotificationPriority.System_Notice,
        "user_selected": 1,
        "code": f"system:{RVEvents.RVC_COMPONENT_NOT_RESPONDING}",
        "trigger_events": [
            # ??
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": [],
        "header": "WinnConnect has lost communications with {} component.",
        "msg": "Please try restarting your system.",
        "type": 0,
        "meta": json.dumps(
            {
                'precedence': {
                    'over': [
                        RVEvents.BLACK_WATER_TANK_ABOVE.value,
                        RVEvents.BLACK_WATER_TANK_NOTICE.value
                    ],
                    'under': []
                }
            }
        )
    },
    RVEvents.FRESH_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT: {
        "notification_id": RVEvents.FRESH_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT,
        "instance": 1,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE}",
        "trigger_events": [
            RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "WinnConnect detected an overvoltage in the fresh tank sensor.",
        "msg": "TBD.",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.GRAY_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT: {
        "notification_id": RVEvents.GRAY_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT,
        "instance": 2,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE}",
        "trigger_events": [
            RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "WinnConnect detected an overvoltage in the gray tank sensor.",
        "msg": "TBD.",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.BLACK_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT: {
        "notification_id": RVEvents.BLACK_WATER_TANK_SENSOR_OVERVOLTAGE_ALERT,
        "instance": 3,
        "priority": NotificationPriority.System_Warning,
        "user_selected": 1,
        "code": f"watersystems:wt{RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE}",
        "trigger_events": [
            RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "WinnConnect detected an overvoltage in the black tank sensor.",
        "msg": "TBD.",
        "type": 0,
        "meta": "{}"
    },
    RVEvents.SHORE_POWER_CONNECTED: {
        "notification_id": RVEvents.SHORE_POWER_CONNECTED,
        "instance": 2,
        "priority": NotificationPriority.System_Notice,
        "user_selected": 1,
        "code": f"energy:es{RVEvents.ENERGY_SOURCE_ACTIVE_CHANGE}",
        "trigger_events": [
            RVEvents.ENERGY_SOURCE_ACTIVE_CHANGE
        ],
        "trigger_type": NotificationTrigger.ON,
        "trigger_value": 1,
        "header": "Shore Power Detected",
        "msg": "Your AC power capacity is limited to the amperage of your shore power connection.",
        "type": 0,
        "meta": "{}"
    }
}


if __name__ == '__main__':
    print(json.dumps(ALERTS, indent=4))
