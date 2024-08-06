'''Model definition for the VANILLA floorplan for manufacturing.'''

from main_service.components.inputs.alerts import (
    ALERTS
)

# TODO: Figure out how to auto get schema for state
# print(dir(FuelTank))
# print(FuelTank.schema())
# state_schema_ref = FuelTank.schema().get('properties', {}).get('state', {}).get('$ref')
# print(state_schema_ref)
# state_schema = FuelTank.schema().get('definitions', {}).get(state_schema_ref.split('/')[-1])

# print(state_schema)

model_definition = {
    # $schema is a helper file, if present will validate the schema as per platform design
    "$schema": "./$schema.json",
    # id: TODO: This should be auto generated
    # "id": "s500.7054042.WM524T",
    # type is static to identify it as a componentGroup which defines a vehicle including all its options
    "type": "componentGroup",
    # description is static for the type
    "description": "component groups allow us to piece together rv components based on its device type, model, floorplan starting with lowest to greatest specificity",
    # deviceType identifies it as a group of vehicles that are similar
    "deviceType": "vanilla",
    # seriesModel is the numerical ID for the specific model
    "seriesModel": "vanilla",   # TODO: Confirm with Rick
    # floorPlan is the specific flooplan, a floorplan separates variants of the same vehicle
    "floorPlan": "VANILLA",
    # attributes can be used as Meta information that can be propagated to the UI as needed
    "attributes": {
        "name": "Vanilla Manufacturing Floorplan",
        "seriesName": "VANILLA",
        "seriesCode": "vanilla",
        "version": "1.0.0",          # TODO: Increment this version automatically upon generation
    },
    # optionCodes (dict)
    # are just a list of all possible options, nothing specifically happens here just a at a glance check what options do apply
    # optioncodes will be handled in filters further down in relatedComponents
    "optionCodes": [],
    # filters (dict)
    # that help query broader picture data and help to which modelYears and other meta info this plan applies to
    "filters": {},
    # components (list)
    # List of components that make up this model including options, instances etc.
    # This will drive which schemas/models get associated with this over APIs
    # Components in this case are a glue item between physical hardware abstraction and the
    # features they drive, a physical component could be split up in multiple
    # virtual components here
    "components": []
}

model_definition['id'] = '{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan')
)


config_definition = {
    "floorPlan": "",
    "componentGroup": "",
    "hal_options": [],
    "climate_components": {},
    "climate_defaults": {},

    "energy_mapping": {},
    "movable_mapping": {},
    "lighting_mapping": {},
    "energy_components": {},
    "features_components": {},
    "communication_components": {},
    "electrical_mapping": {
        "ac": {},
        "dc": {},
        "switches": {},
        "KEYPAD_CONTROLS": {},
        "SI_CONTROLS": {},
        "RV1_CONTROLS": {},
        "TOGGLE_ZONES": []
    },
    "alert_items": ALERTS,
    "hal_categories": {
        "vehicle": "modules.hardware.vanilla.hw_vehicle"
    },
    "can_mapping": {
        "vin_response": "vehicle",
        "vehicle_status_1": "vehicle",
        "vehicle_status_2": "vehicle",
        "state_of_charge": "vehicle",
        "dc_charging_state": "vehicle",
        "pb_park_brake": "vehicle",
        "tr_transmission_range": "vehicle",
        "odo_odometer": "vehicle",
        "aat_ambient_air_temperature": "vehicle",
    }
}


config_definition['componentGroup'] = '{}.{}.{}.{}'.format(
    model_definition.get('deviceType'),
    model_definition.get('seriesModel'),
    model_definition.get('floorPlan'),
    "componentGroup"
)
config_definition['floorPlan'] = model_definition.get('floorPlan')
