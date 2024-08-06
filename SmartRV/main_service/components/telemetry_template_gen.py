import json
import sys
import os

abs_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
add_path = os.path.join(abs_path, "../")
sys.path.append(add_path)
# from  common_libs.models.common import RVEvents, EventValues


# from helper import (
#     generate_component,
#     create_component_jsons,
#     create_model_jsons,
# )


from movables import SlideoutBasic, AwningRvc, LevelJacksRvc

from lighting import LightSimple, LightDimmable, LightRGBW

from energy import (
    InverterBasic,
    InverterAdvanced,
    EnergyConsumer,
    PowerSourceSolar,
    PowerSourceShore,
    PowerSourceAlternator,
    PowerSourceProPower,
    PowerSourceGenerator,
    BatteryManagement,
    GeneratorPropane,
    GeneratorDiesel,
    BatteryPack,
    FuelTank,
)

from vehicle import (
    VehicleId,
)

from climate import (
    Thermostat,
    HeaterBasic,
    RoofFanAdvanced,
    RefrigeratorBasic,
    HeaterACHeatPump,
    RefrigeratorBasic,
    ThermostatOutdoor,
    AcRvcTruma,
    AcRvcTrumaState,
    AcRvcGe,
    AcRvcGeState,
)

from watersystems import (
    WaterHeaterRvc,
    WaterHeaterRvcState,
    WaterHeaterSimple,
    WaterHeaterSimpleState,
    WaterPumpDefault,
    WaterPumpState,
    WaterTankDefault,
    WaterTankState,
)

from vehicles import MODELS

from features import PetMonitorFeatureState

from connectivity import RouterState


if __name__ == "__main__":
    base_path = os.path.abspath(sys.argv[0])
    base_path = os.path.split(base_path)[0]
    base_path = os.path.join(base_path, "generated")

    component_type_path = os.path.join(base_path, "ComponentTypes")
    # component_group_path = os.path.join(base_path, 'ComponentGroups')
    telemetry_config_path = os.path.join(base_path, "OtaTemplates")
    previous_file_found = False

    props = []
    telem_file = ""

    # Clean folders
    for path in (telemetry_config_path,):
        # Remove all files that exist
        for file in os.scandir( telemetry_config_path):
            if "vanilla.vanilla.VANILLA.ota_template.json" in file.name:
                print(f"File found {file.path} \n  OK \n")
                telem_file = file.name
                previous_file_found = True
                break
                # os.remove(file.path)
            elif os.path.isdir(file.path):
                continue

    if not previous_file_found:
        raise "Previous Telemetry not found!"

        ex = ' {  \
            "id": 7800,\
            "code": "temp",\
            "category": "energy",\
            "componentTypeCode": "ba",\
            "routings": [\
                {\
                    "interval": "standard",\
                    "messageType": "",\
                    "code": "ba[#]temp",\
                    "aggregation": "latest"\
                }\
            ]\
        }, '
    for f in os.listdir(component_type_path):
        # print(c, json.dumps(comp, indent=4))
        with open(os.path.join(component_type_path, f), "r") as json_in:
            file_data = json.loads(json_in.read())
            # print(f'FILE DATA {json.dumps(file_data, indent=3)}')
            print(f'\n\n System {file_data.get("category")}.{file_data.get("code")}\n')

            # print(f'Properties {file_data.get("properties") }\n')
            for prop in file_data.get("properties"):
                print(f'Property {prop.get("code")} event {prop.get("id") }')

                if prop.get("id") is not None:

                    tel = {
                        "id": prop.get("id"),
                        "code": prop.get("code"),
                        "category": file_data.get("category"),
                        "componentTypeCode": file_data.get("code"),
                        "routings": [
                            {
                                "target": "event",
                                "code": f"{file_data.get('code')}[#]{prop.get('code')}",
                                "aggregation": "latest",
                            },
                            {
                                "target": "$twin",
                                "code": f"{file_data.get('category')}.{file_data.get('code')}[#].{prop.get('code')}",
                            },
                        ],
                    }
                    print(tel)
                    props.append(tel)


            print(json.dumps(props, indent=3))


    tel_data = {}
    with open(os.path.join(telemetry_config_path, telem_file), "r") as json_tel:
            tel_data = json.loads(json_tel.read())

            old = tel_data["properties"]
            print("\n\n\n\n\n old = new ", old == props)

    tel_data["properties"] = props

    with open(os.path.join(telemetry_config_path, telem_file), "w") as json_tel:
            json.dump(tel_data, json_tel, indent=4)


    # for model in create_model_jsons(MODELS):
    #     out_file_name = f'{model.get("id")}.json'
    #     result = json.dumps(model, indent=4)
    #     full_path = os.path.join(base_path, 'ComponentGroups', out_file_name)
    #     try:
    #         json.dump(model, open(full_path, 'w'), indent=4)
    #     except TypeError as err:
    #         print(err)
    #         print(model)
    #         raise

    #     data_path = os.path.join(base_path, '..', '..', '..', 'data', out_file_name)
    #     # print(data_path)
    #     # sys.exit(1)
    #     json.dump(model, open(data_path, 'w'), indent=4)
    #     # print(result)

    # Copy the file to data

    # TODO: Write the generator for known vehicle for testing
