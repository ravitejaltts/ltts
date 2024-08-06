import json

from common_libs.models.common import RVEvents


DEFAULT_TELEMETRY = [
    {
        "id": RVEvents.ENERGY_SOURCE_POWER_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_VOLTAGE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_CURRENT_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.BATTERY_TEMP_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LOCATION_USER_OPTIN_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LOCATION_GEO_LOC_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.FUEL_TANK_LEVEL_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_ONOFF_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CELLULAR_TCU_ID_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CELLULAR_IMEI_1_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CELLULAR_ICCID_1_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CELLULAR_IMEI_2_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CELLULAR_ICCID_2_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CHASSIS_VIN_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_STATE_OF_CHARGE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_VOLTAGE_STATUS_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_DC_CURRENT_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_DC_POWER_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TIME_REMAINING_INTERPRETATION_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TIME_REMAINING_TO_FULL_CHARGE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TIME_REMAINING_TO_EMPTY_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_WATER_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_OUTDOOR_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_FAN_SPEED_CHANGE,
        "aggregation": "latest"
    }
]
DEFAULT_EVENT = [
    {
        "id": RVEvents.ENERGY_SOURCE_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_ACTIVE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LEVELING_JACKS_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.GENERATOR_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.HEATER_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.HEATER_ENERGY_SOURCE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_CURRENT_HEAT_TEMPERATURE_SET_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_CURRENT_COOL_TEMPERATURE_SET_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_CURRENT_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ELECTRIC_HEATER_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AIR_CONDITIONER_FAN_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.INVERTER_CHARGER_INVERTER_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.EVENT_NOT_DEFINED,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LIGHTING_ZONE_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CHASSIS_VIN_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.SLIDEOUT_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_WATER_SET_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_ONOFF_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_PUMP_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LIGHTING_ZONE_BRIGHTNESS_LEVEL_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_PERCENT_EXTENDED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_MOTION_SENSE_SENSITIVITY_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_MOTION_SENSE_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_GENERAL_ONOFF_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_DOME_POSITION_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_FAN_DIRECTION_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_RAIN_SENSOR_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.OTA_UPDATE_RECEIVED,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CHASSIS_DOOR_LOCK_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CHASSIS_TRANSMISSION_NOT_IN_PARK_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_ENABLED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_TEMP_HIGH_SETTING_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_TEMP_LOW_SETTING_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_INTERIOR_TEMP_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_BATTERY_LOW,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_SHORE_DISCONECTED,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_TEMP_HIGH,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_TEMP_LOW,
        "aggregation": "latest"
    }

]
DEFAULT_TWIN = [
    {
        "id": RVEvents.LOCATION_GEO_LOC_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LOCKOUT_STATE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_ACTIVE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_POWER_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_VOLTAGE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_SOURCE_CURRENT_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.BATTERY_TEMP_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.FUEL_TANK_LEVEL_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_ONOFF_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LEVELING_JACKS_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.GENERATOR_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.REFRIGERATOR_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_STATE_OF_CHARGE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_VOLTAGE_STATUS_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_DC_CURRENT_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_DC_POWER_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TIME_REMAINING_INTERPRETATION_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TIME_REMAINING_TO_FULL_CHARGE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LITHIUM_ION_BATTERY_TIME_REMAINING_TO_EMPTY_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.HEATER_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.HEATER_ENERGY_SOURCE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_INDOOR_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_CURRENT_HEAT_TEMPERATURE_SET_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_CURRENT_COOL_TEMPERATURE_SET_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_CURRENT_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_GENERAL_ONOFF_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ELECTRIC_HEATER_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AIR_CONDITIONER_COMPRESSOR_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AIR_CONDITIONER_FAN_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AIR_CONDITIONER_FAN_SPEED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.INVERTER_CHARGER_INVERTER_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.EVENT_NOT_DEFINED,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LIGHTING_ZONE_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CHASSIS_VIN_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.SLIDEOUT_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_WATER_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_HEATER_WATER_SET_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_PUMP_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.LIGHTING_ZONE_BRIGHTNESS_LEVEL_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WATER_TANK_FLUID_LEVEL_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_OUTDOOR_TEMPERATURE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_PERCENT_EXTENDED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_MOTION_SENSE_SENSITIVITY_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.AWNING_MOTION_SENSE_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_DOME_POSITION_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_FAN_DIRECTION_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_FAN_SPEED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ROOF_VENT_RAIN_SENSOR_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.OTA_UPDATE_RECEIVED,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.CHASSIS_TRANSMISSION_NOT_IN_PARK_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_CONSUMER_WATTS_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_CONSUMER_CURRENT_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_CONSUMER_VOLTAGE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_CONSUMER_ACTIVE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.ENERGY_CONSUMER_SHED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_ENABLED_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_TEMP_HIGH_SETTING_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.PET_MONITOR_TEMP_LOW_SETTING_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.THERMOSTAT_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {
        "id": RVEvents.WINNCONNECT_SYSTEM_USER_SET_TEMPERATURE_UNIT_CHANGE,
        "aggregation": "latest"
    },
    {"id": RVEvents.SYSTEM_ACTIVITY_STATE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WATER_HEATER_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.WATER_PUMP_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.AWNING_MOTION_SENSE_TRIGGERED, "aggregation": "latest"},
    {"id": RVEvents.AWNING_LIGHT_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.AWNING_LIGHT_BRIGHTNESS_LEVEL_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.AWNING_LIGHT_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.AWNING_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_CURRENT_METER_AFTER_INVERTER_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_INVERTER_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_INVERTER_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_INVERTER_CURRENT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_INVERTER_FREQUENCY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_CHARGER_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_CHARGER_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_CHARGER_CURRENT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_CHARGER_FREQUENCY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_CHARGER_CAPACITY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CHARGER_CHARGER_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.LIGHTING_ZONE_NAME_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LIGHTING_ZONE_RGBW_COLOR_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LIGHTING_ZONE_COLOR_TEMP_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LIGHTING_ZONE_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_NAME_CHANGE, "aggregation": "latest"},
    {
        "id": RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_OPERATING_MODE_CHANGE,
        "aggregation": "latest"
    },
    {"id": RVEvents.LIGHTING_GROUP_LIGHT_SWITCH_LIGHT_MAPPINGS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LIGHTING_GROUP_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.GENERATOR_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_SCHEDULE_DAY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_COMPRESSOR_MIN_OFF_TIME_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_COMPRESSOR_MIN_ON_TIME_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_COOL_DIFFERENTIAL_TEMPERATURE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_COOL_TEMPERATURE_RANGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_HEAT_DIFFERENTIAL_TEMPERATURE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_HEAT_TEMPERATURE_RANGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_HEAT_COOL_MIN_DELTA_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_HEATER_MIN_OFF_TIME_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_HEATER_MIN_ON_TIME_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_HIGH_LOW_TEMPERATURE_WARNING_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.THERMOSTAT_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.FURNACE_OPERATING_MODE_CHANGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.FURNACE_FAN_SPEED_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.FURNACE_HEAT_OUTPUT_LEVEL_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.FURNACE_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.ELECTRIC_HEATER_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.SOLAR_CHARGER_SHUNT_DC_CURRENT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.SOLAR_CHARGER_SHUNT_DC_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.SOLAR_CHARGER_SHUNT_DC_POWER_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.SOLAR_CHARGER_SHUNT_ACTIVE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.SOLAR_CHARGER_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.LITHIUM_ION_BATTERY_STATE_OF_HEALTH_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LITHIUM_ION_BATTERY_REMAINING_DISCHARGE_CAPACITY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LITHIUM_ION_BATTERY_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.ALTERNATOR_CHARGER_STATE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ALTERNATOR_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ALTERNATOR_CURRENT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ALTERNATOR_TEMPERATURE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ALTERNATOR_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.ROOF_VENT_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_CHARGING_STATE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_SOC_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_REMAINING_TIME_TO_FULL_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_RPM_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_SPEED_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_COOLANT_TEMPERATURE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_MALFUNCTION_INDICATOR_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_NUMBER_OF_IGNITION_CYCLES_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_ODOMETER_READING_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_DTCS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_IGNITION_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_PRNDL_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_FUEL_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_PARK_BRAKE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_OUTSIDE_TEMPERATURE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_AVAILABLE_MILAGE_RANGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_CHARGINIG_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_12V_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_12V_SOC_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_PRO_POWER_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_TIRE_LOCATION_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_TIRE_PRESSURE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_CHARGING_STAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_CHARGING_TYPE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_DOOR_LOCK_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CHASSIS_CHASSIS_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.WATER_TANK_TANK_CAPACITY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WATER_TANK_FLUID_TYPE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WATER_TANK_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_SET_SCREEN_BRIGHTNESS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_CURRENT_SCREEN_BRIGHTNESS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_RV_SOFTWARE_VERSION_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_RV_ACTIVE_SOFTWARE_INSTALL_DATE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_RV_PREVIOUS_SOFTWARE_VERSION_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_RV_PREVIOUS_SOFTWARE_INSTALL_DATE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_DARK_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_USER_RESTART_TRIGGERED_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_MASTER_RESET_TRIGGERED_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_USER_SET_VOLUME_UNIT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_USER_SET_DISTANCE_UNIT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_USER_BACKUP_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_CAN_BUS_TIMEOUT, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_CAN_BUS_RVC_RED_LAMP_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_SYSTEM_CAN_BUS_RVC_YELLOW_LAMP_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_MICROCONTROLLER_MANUFACTURER_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_MICROCONTROLLER_MODEL_NAME_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_MICROCONTROLLER_MODEL_REVISION_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_OS_NAME_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_OS_REVISION_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_CURRENT_RAM_USAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_AVAILABLE_RAM_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_CPU_USAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_USED_STORAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_AVAILABLE_STORAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WINNCONNECT_HMI_HARDWARE_UTC_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.OTA_OPERATING_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.REFRIGERATOR_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.REFRIGERATOR_BREAKER_TRIPPED, "aggregation": "latest"},
    {"id": RVEvents.REFRIGERATOR_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.WIFI_OPERATING_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WIFI_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WIFI_ACCESS_POINT_HIDDEN_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WIFI_SECURITY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WIFI_STRENGTH_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WIFI_CONNECTED_DEVICES_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.WIFI_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.BLUETOOTH_OPERATING_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.BLUETOOTH_STRENGTH_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.BLUETOOTH_CONNECTED_DEVICES_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.BLUETOOTH_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.CELLULAR_OPERATING_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CELLULAR_STRENGTH_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CELLULAR_OPERATOR_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CELLULAR_CELLUAR_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.CELLULAR_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.LOCATION_OPERATING_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LOCATION_ALTITUDE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LOCATION_VISIBLE_SATS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.LOCATION_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_AC_CURRENT_METER_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_LOAD_SHEDDING_TRIGGER_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_ZONE_4_LOCAL_FLAG_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_ZONE_5_LOCAL_FLAG_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_SYSTEM_OVERLOAD_TRIGGER_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_AVC2_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_GENERATOR_STATE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_MANAGEMENT_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.PROPOWER_PRO_POWER_RELAY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.PROPOWER_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.PROPOWER_CURRENT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.PROPOWER_POWER_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.PROPOWER_ACTIVE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.PROPOWER_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_MODE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_OUTPUT_CURRENT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_STATUS_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_OUTPUT_VOLTAGE_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_CURRENT_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_FREQUENCY_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_OVERLOAD_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_LOAD_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.INVERTER_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.BATTERY_MODULE_COMMUNICATION_ERROR, "aggregation": "latest"},
    {"id": RVEvents.BATTERY_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.ENERGY_CONSUMER_ERROR_CODES, "aggregation": "latest"},
    {"id": RVEvents.FUEL_TANK_DISABLED_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.PET_MONITOR_INTERIOR_TEMP_CHANGE, "aggregation": "latest"},
    {"id": RVEvents.PET_MONITOR_BATTERY_LOW, "aggregation": "latest"},
    {"id": RVEvents.PET_MONITOR_SHORE_DISCONECTED, "aggregation": "latest"},
    {"id": RVEvents.PET_MONITOR_TEMP_HIGH, "aggregation": "latest"},
    {"id": RVEvents.PET_MONITOR_TEMP_LOW, "aggregation": "latest"},

    # SERVICE MODE SETTINGS
    {"id": RVEvents.WINNCONNECT_SYSTEM_SETTINGS_SERVICE_MODE_CHANGE, "aggregation": "latest"},
    ]

targets = {
    "standard": {
        "evt": "0",
        "mtp": "1",
        "intervalSeconds": RVEvents.FLOORPLAN_LOADED,
        "codeFormat": "{componentTypeCode}[#]{code}",
        "mappings": DEFAULT_TELEMETRY
    },
    "event": {
        "evt": "0",
        "mtp": "2",
        "intervalSeconds": 5,
        "codeFormat": "{componentTypeCode}[#]{code}",
        "mappings": DEFAULT_EVENT
    },
    "$twin": {
        "intervalSeconds": RVEvents.FLOORPLAN_LOADED,
        "chattyIntervalSeconds": 5,
        "codeFormat": "{category}.{componentTypeCode}[#].{code}",
        "mappings": DEFAULT_TWIN
    },
    "daily": {
        "evt": "0",
        "mtp": "3",
        "intervalSeconds": 86400
    },
    "alert": {
        "evt": "1",
        "mtp": "2",
        "intervalSeconds": 5
    },
    "ota": {
        "evt": "2",
        "mtp": "2",
        "intervalSeconds": 5
    },
    "request": {
        "evt": "3",
        "mtp": "2",
        "intervalSeconds": 5
    },
    "settings": {
        "evt": "4",
        "mtp": "2",
        "intervalSeconds": 5
    }
}

template = {
    'targets': targets
}


def export_json():
    # Check for duplicates
    targets = template['targets']
    for target, values in targets.items():
        print(target)
        if 'mappings' in values:
            map_list = []
            for mapping in values['mappings']:
                event_id = mapping.get('id')
                # print(event_id)
                if event_id in map_list:
                    print('\tDuplicate Value found', mapping)
                else:
                    map_list.append(event_id)

    return json.dumps(template, indent=4, sort_keys=True)


if __name__ == '__main__':

    with open('test.json', 'w') as out_file:
        out_file.write(export_json())

    for key, value in template.items():
        pass

    print([x.get('id').value for x in DEFAULT_TWIN])
