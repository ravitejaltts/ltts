LP_LEVEL_FULL = {
    "title": 'Tank 4 - LP Tank 1',
    "Instance": "4",
    "Fluid_Type": "LP",
    "Fluid_Level": "100",
    "Tank_Capacity": "0.0795",
    "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}
LP_LEVEL_HALF = {
    "title": 'Tank 4 - LP Tank 1',
    "Instance": "4",
    "Fluid_Type": "LP",
    "Fluid_Level": "50",
    "Tank_Capacity": "0.0795",
    "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}
LP_LEVEL_EMPTY = {
    "title": 'Tank 4 - LP Tank 1',
    "Instance": "4",
    "Fluid_Type": "LP",
    "Fluid_Level": "0",
    "Tank_Capacity": "0.0795",
    "NMEA_Reserved": "255",
    "name": "FLUID_LEVEL",
    'instance_key': ''
}

RV1_PARK_BRAKE_ENGAGED = {
    'name': 'RvSwitch',
    'Dipswitch': str(0x80),
    'Instance': '4',
    'Output7': '1'
}
RV1_PARK_BRAKE_RELEASED = {
    'name': 'RvSwitch',
    'Dipswitch': str(0x80),
    'Instance': '4',
    'Output7': '0'
}

RV1_IGNITION_ON = {
    'name': 'RvSwitch',
    'Dipswitch': str(0x80),
    'Instance': '4',
    'Output5': '1'
}

RV1_IGNITION_OFF = {
    'name': 'RvSwitch',
    'Dipswitch': str(0x80),
    'Instance': '4',
    'Output5': '0'
}

# for i in range(32):
#     index = i + 1
#     for msg in (RV1_PARK_BRAKE_ENGAGED, RV1_PARK_BRAKE_RELEASED):
#         if f'Output{index}' not in msg:
#             msg[f'Output{index}'] = '0'


INVALID_TEMP = {
    "title": "Setting Interior to invalid",
    "Instance": "2",
    "Ambient_Temp": "-17.78125",
    "name": "thermostat_ambient_status"
}

UNKOWN_TEMP = {
    "title": "Setting Interior to invalid",
    "Instance": "55",   # Fridge
    "Ambient_Temp": "Data Invalid",
    "name": "thermostat_ambient_status"
}

FRIDGE_ROUND_UP_TEMP = {
    "title": "Setting Fridge to 2.5C",
    "Instance": "55",   # Fridge
    "Ambient_Temp": "2.5",
    "name": "thermostat_ambient_status"
}

FRIDGE_ROUND_DOWN_TEMP = {
    "title": "Setting Fridge to 2.4C",
    "Instance": "55",   # Fridge
    "Ambient_Temp": "2.4",
    "name": "thermostat_ambient_status"
}

INTERIOR_HOT = {
    "title": "Setting Interior Temp to HOT 45 C",
    "Instance": "2",
    "Ambient_Temp": "45",
    "name": "thermostat_ambient_status"
}

INTERIOR_NORMAL = {
    "title": "Setting Interior Temp to OK 20 C",
    "Instance": "2",
    "Ambient_Temp": "20",
    "name": "thermostat_ambient_status"
}

INTERIOR_INVALID = {
    "title": "Setting Interior Temp to HOT 45 C",
    "Instance": "2",
    "Ambient_Temp": "Data Invalid",
    "name": "thermostat_ambient_status"
}

FRIDGE_IN_RANGE = {
    "title": "Setting Fridge to OK temp",
    "Instance": "55",   # Fridge
    "Ambient_Temp": "4",
    "name": "thermostat_ambient_status"
}

INTERIOR_COLD = {
    "title": "Setting Interior Temp to COLD 10 C",
    "Instance": "2",
    "Ambient_Temp": "10",
    "name": "thermostat_ambient_status"
}

EXTERIOR_HOT = {}
EXTERIOR_COLD = {}

ROOF_FAN_STATUS_1_OK = {
    'name': 'roof_fan_status_1',
    'Instance': '2'
}

AIR_CONDITIONER_STATUS_DEFAULT = {
    'name': 'air_conditioner_status',
    'Instance': '1'
}

HEAT_PUMP_STATUS_DEFAULT = {
    'name': 'heat_pump_status',
    'Instance': '1'
}

ENERGY_BMS_VOLTAGE_OK = {
    "Instance": "1",
    "name": "dc_source_status_1",
    'DC_Voltage': '12.8',
    'DC_Current': '0.0'
}

ENERGY_BMS_SOC_FULL = {
    "Instance": "1",
    'DC_Instance': '1',
    "name": "dc_source_status_2",
    'State_Of_Charge': '100.0',
    'Time_Remaining': '600',
    'Time_Remaining_Interpretation': 'Time to Empty',
    'Source_Temperature': '30.0'
}

ENERGY_BMS_HEALTH = {
    "name": "dc_source_status_3",
    'DC_Instance': '1',
    'State_Of_Health': '1',
    'Capacity_Remaining': '100'
}


ENERGY_INVERTER_OVERLOAD = {
    "Instance": "1",
    "RMS_Voltage": "120.0",
    "RMS_Current": "20.0",
    "Frequency": "60.0",
    "name": "inverter_ac_status_1"
}

ENERGY_INVERTER_NO_LOAD = {
    "Instance": "1",
    "RMS_Voltage": "120.0",
    "RMS_Current": "0.0",
    "Frequency": "60",
    "name": "inverter_ac_status_1"
}

ENERGY_INVERTER_1200W_LOAD = {
    "Instance": "1",
    "RMS_Voltage": "120.0",
    "RMS_Current": "10.0",
    "Frequency": "60",
    "name": "inverter_ac_status_1"
}

ENERGY_SOLAR_200W = {
    'name': 'solar_controller_status',
    'Instance': 1,
    'Charge_Voltage': '14.0',
    'Charge_Current': '14.0'
}


WATER_HEATER_DATA_INVALID = {
    'name': 'waterheater_status',
    'Instance': '1',
    'Set_Point_Temperature': 'Data Invalid',
    'Operating_Mode': 'Data Invalid'
}

WATER_HEATER_MODES_DATA_INVALID = {
    'name': 'waterheater_status_2',
    'Instance': '1',
    'Heat_Level': 'Data Invalid',
}

WATER_HEATER_OFF = {
    "Instance": "1",
    "Operating_Mode": "off",
    "Set_Point_Temperature": "42.0",
    "msg_name": "WATERHEATER_STATUS",
    "source_address": "64",
    "instance_key": "19FFF764__0__1"
}

WATER_HEATER_ON_COMBUSTION = {
    "Instance": "1",
    "Operating_Mode": "combustion",
    "Set_Point_Temperature": "42.0",
    "msg_name": "WATERHEATER_STATUS",
    "source_address": "64",
    "instance_key": "19FFF764__0__1"
}

ENERGY_BATTERY_STATUS_DEFAULT = {
    'name': 'battery_status',
    'Instance': '1',
    'Battery_Voltage': '12.9'
}

TM620_WH1_OK = {
    'name': 'prop_tm620_config_status',
    'Water_Heater_Instance': "1",
    'LIN_Bus_Connection': 'Connected',
    'Truma_Water_Heater_Error': 'Ok',
    'Truma_Control_Panel_Status': 'Not Busy'
}


TM620_WH1_LIN_ERROR = {
    'name': 'prop_tm620_config_status',
    'Water_Heater_Instance': "1",
    'LIN_Bus_Connection': 'No',
    'Truma_Water_Heater_Error': 'Ok',
    'Truma_Control_Panel_Status': 'Not Busy'
}


TM620_WH1_LIN_NODATA = {
    'name': 'prop_tm620_config_status',
    'Water_Heater_Instance': "1",
    'LIN_Bus_Connection': 'No Data',
    'Truma_Water_Heater_Error': 'Ok',
    'Truma_Control_Panel_Status': 'Not Busy'
}


TM620_WH1_WH_ERROR = {
    'name': 'prop_tm620_config_status',
    'Water_Heater_Instance': "1",
    'LIN_Bus_Connection': 'Connected',
    'Truma_Water_Heater_Error': 'Error',
    'Truma_Control_Panel_Status': 'Not Busy'
}


TM620_WH1_WH_NODATA = {
    'name': 'prop_tm620_config_status',
    'Water_Heater_Instance': "1",
    'LIN_Bus_Connection': 'Connected',
    'Truma_Water_Heater_Error': 'No Data',
    'Truma_Control_Panel_Status': 'Not Busy'
}


TM620_WH1_PANEL_BUSY = {
    'name': 'prop_tm620_config_status',
    'Water_Heater_Instance': "1",
    'LIN_Bus_Connection': 'Connected',
    'Truma_Water_Heater_Error': 'Ok',
    'Truma_Control_Panel_Status': 'Busy'
}

TM620_WH1_PANEL_NODATA = {
    'name': 'prop_tm620_config_status',
    'Water_Heater_Instance': "1",
    'LIN_Bus_Connection': 'Connected',
    'Truma_Water_Heater_Error': 'Ok',
    'Truma_Control_Panel_Status': 'Data Invalid'
}

SHORE_INVALID = {
    "Instance": "1",
    "RMS_Voltage": "120.0",
    "RMS_Current": "Data Invalid",
    "Frequency": "Data Invalid",
    "name": "charger_ac_status_1"
}

SHORE_0W = {
    "Instance": "1",
    "RMS_Voltage": "120.0",
    "RMS_Current": "0",
    "Frequency": "60",
    "name": "charger_ac_status_1"
}

SHORE_1200W = {
    "Instance": "1",
    "RMS_Voltage": "120.0",
    "RMS_Current": "10",
    "Frequency": "60",
    "name": "charger_ac_status_1"
}

SOLAR_16W = {
            'Instance': '1',
            'Charge_Voltage': '12.3',
            'Charge_Current': '1.32',
            'name': 'solar_controller_status'
        }

GENERATOR_RUNNING = {
    "Manufacturer_Code": "BEP Marine",
    "Dipswitch": "128",
    "Instance": "4",
    "Output13": "1",
    "name": "RvSwitch"
}

GENERATOR_STOPPED = {
    "Manufacturer_Code": "BEP Marine",
    "Dipswitch": "128",
    "Instance": "4",
    "Output13": "0",
    "name": "RvSwitch"
}

CZONE_MAIN_STUD_NO_LOAD = {
    "Instance": "252",
    "Battery_Voltage": "13.13",
    "Battery_Current": "0",
    "Sequence_Id": "0",
    "msg_name": "Battery_Status",
    "name": "Battery_Status",
    "source_address": "97",
    "instance_key": "19F21497__0__252"
}

CZONE_MAIN_STUD_MEDIUM_LOAD = {
    "Instance": "252",
    "Battery_Voltage": "13.0",
    "Battery_Current": "20",
    "Sequence_Id": "0",
    "msg_name": "Battery_Status",
    "name": "Battery_Status",
    "source_address": "97",
    "instance_key": "19F21497__0__252"
}

AWNING_STATUS_OK = {
    'name': 'awning_status',
    'Instance': '1',
    'Motion': 'No motion',
    'Position': 'Retracted'
}

AWNING_STATUS_2_DATA_INVALID = {
    'name': 'awning_status_2',
    'Instance': '1',
    'Motion_Sensitivity': 'Data Invalid'
}


DEFAULTS = {
    "inverter_ac_status_1": ENERGY_INVERTER_OVERLOAD,
    # 'dc_dimmer_command_2': None,
    "dc_source_status_3": ENERGY_BMS_HEALTH,

    "dc_source_status_1": ENERGY_BMS_VOLTAGE_OK,
    "dc_source_status_2": ENERGY_BMS_SOC_FULL,

    'thermostat_ambient_status': INTERIOR_HOT,
    'roof_fan_status_1': ROOF_FAN_STATUS_1_OK,
    # NOTE: air_conditioner_status is not handled anywhere
    # 'air_conditioner_status': AIR_CONDITIONER_STATUS_DEFAULT,
    # 'heat_pump_status': HEAT_PUMP_STATUS_DEFAULT,

    "inverter_status": None,

    "charger_ac_status_1": SHORE_1200W,
    # "charger_ac_status_2": None,
    # "charger_status": None,
    # "charger_status_2": None,
    "charger_configuration_status": None,
    "charger_configuration_status_2": None,

    "solar_controller_status": ENERGY_SOLAR_200W,

    # "dm_rv": None,
    # "request_for_dgn": None,

    "waterheater_status": WATER_HEATER_DATA_INVALID,
    "waterheater_status_2": WATER_HEATER_MODES_DATA_INVALID,
    "prop_tm620_config_status": TM620_WH1_OK,

    'battery_status': ENERGY_BATTERY_STATUS_DEFAULT,

    'fluid_level': LP_LEVEL_FULL,

    'awning_status': AWNING_STATUS_OK,
    'awning_status_2': AWNING_STATUS_2_DATA_INVALID,

    # "vin_response": None,
    # "aat_ambient_air_temperature": None,
    # "odo_odometer": None,
    # "vehicle_status_1": None,
    # "vehicle_status_2": None,
    # "state_of_charge": None,
    # "dc_charging_state": None,
    # "pb_park_brake": None,
    # "tr_transmission_range": None,

    # "heartbeat": None,
    # "rvswitch": None,
    # "rvoutput": None,
    # "czone_alerts": None,
    # "lighting_broadcast": None,
    # "prop_bms_status_6": None,
    # "prop_bms_status_1": None,
    # "prop_module_status_1": None
}
