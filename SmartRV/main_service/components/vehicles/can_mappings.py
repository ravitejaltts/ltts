BASE_RVC = {
    "ambient_temperature": "climate",
    "roof_fan_status_1": "climate",
    "thermostat_ambient_status": "climate",
    "air_conditioner_status": 'climate',
    "heat_pump_status": 'climate',

    "dc_dimmer_command_2": "electrical",

    "dc_source_status_1": "energy",
    "dc_source_status_2": "energy",
    "dc_source_status_3": "energy",

    "inverter_ac_status_1": "energy",
    "inverter_status": "energy",

    "charger_ac_status_1": "energy",
    "charger_ac_status_2": "energy",
    "charger_status": "energy",
    "charger_status_2": "energy",
    "charger_configuration_status": "energy",
    "charger_configuration_status_2": "energy",

    "solar_controller_status": "energy",

    "dm_rv": "system",
    "request_for_dgn": "system",

    "waterheater_status": "watersystems",
    "waterheater_status_2": "watersystems",
    "prop_tm620_config_status": "watersystems",
}

BASE_NMEA2K = {
    "battery_status": "energy",

    "fluid_level": "watersystems",
}

BASE_RVC_MOVABLES = {
    "awning_status": "movables",
    "awning_status_2": "movables"
}

BASE_J1939 = {
    "vin_response": "vehicle",                  # Intermotive or Injected
    "aat_ambient_air_temperature": "vehicle",   # Intermotive
    "odo_odometer": "vehicle",                  # Intermotive
    "vehicle_status_1": "vehicle",
    "vehicle_status_2": "vehicle",
    "state_of_charge": "vehicle",
    "dc_charging_state": "vehicle",
    "pb_park_brake": "vehicle",
    "tr_transmission_range": "vehicle",
}

BASE_CZONE = {
    "heartbeat": "electrical",
    "rvswitch": "electrical",
    "rvoutput": "electrical",
    "czone_alerts": "electrical",
    # "czone_fast_data": "electrical"       # Removed until we have a proper use-case for this
}

_500_BASE = {
    "lighting_broadcast": "lighting",
    "prop_bms_status_6": "energy",
    "prop_bms_status_1": "energy",
    "prop_module_status_1": "energy",
}

for module in (BASE_RVC, BASE_RVC_MOVABLES, BASE_CZONE, BASE_NMEA2K, BASE_J1939):
    for key, value in module.items():
        _500_BASE[key] = value

print('[CAN][INIT] Can mapping for 500 Base', _500_BASE)


# TODO: Add 800 Base can mappings
_800_BASE = {}

for module in (BASE_RVC, BASE_CZONE, BASE_NMEA2K, BASE_J1939):
    for key, value in module.items():
        _800_BASE[key] = value


if __name__ == '__main__':
    print(_500_BASE)
