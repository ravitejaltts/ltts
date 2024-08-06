import json
import sys
import os


try:
    from jsonschema import validate
    from jsonschema import ValidationError
    JSON_SCHEMA = True
except ImportError:
    JSON_SCHEMA = False

from common_libs.models.common import RVEvents, EventValues

from main_service.components.helper import (
    generate_component,
    create_component_jsons,
    create_model_jsons,
    create_component_category_jsons,
)

from main_service.components.movables import *
from main_service.components.lighting import *
from main_service.components.energy import *
from main_service.components.vehicle import *
from main_service.components.climate import *
from main_service.components.watersystems import *
from main_service.components.system import *
from main_service.components.features import *
from main_service.components.connectivity import *

from main_service.components.generate_ota_template import *

from main_service.components.vehicles import MODELS, CONFIGS

COMPONENTS = create_component_jsons(
    (
        # Movables
        SlideoutBasic,
        AwningRvc,
        LevelJacksRvc,
        # Lighting
        LightSimple,
        LightDimmable,
        LightRGBW,
        LightGroup,
        SmartLightGroup,

        # Climate
        Thermostat,
        HeaterBasic,
        RoofFanAdvanced,
        RefrigeratorBasic,
        HeaterACHeatPump,
        RefrigeratorBasic,
        ThermostatOutdoor,
        AcRvcTruma,
        AcRvcGe,
        ThermostatWired,
        ACBasic,

        # Energy
        InverterBasic,
        InverterAdvanced,
        ChargerAdvanced,
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
        LoadShedding500,
        LoadShedderComponent,
        LoadShedderCircuit,

        # Vehicle
        # VehicleId,
        VehicleSprinter,
        HouseDoorLock,
        VehicleLocation,
        VehicleETransit,
        # Virtual,

        # Watersystems
        WaterHeaterRvc,
        WaterHeaterSimple,
        WaterPumpDefault,
        WaterTankDefault,
        TankHeatingPad,
        ToiletCircuitDefault,

        # System
        LockoutBasic,
        LockoutDynamic,
        LockoutStatic,
        ServiceSettings,

        # Features
        WeatherFeature,
        PetMonitorFeature,
        Diagnostics,
        RemoteTest,
        SystemOverview,

        # Connectivity
        NetworkRouter,
    )
)


def validate_schema(folder, schema_file='$schema.json'):
    '''Validates schemas of the given files in a folder.'''
    print('Parsing', folder)
    folder_name = os.path.split(folder)[1]
    try:
        with open(os.path.join(folder, '..', '..', 'schemas', f'{folder_name}_$schema.json'), 'r') as schema_file:
            schema = json.load(schema_file)

        for fn in os.listdir(folder):
            if '$schema' in fn or '.categories.json' in fn:
                continue

            template_data = json.load(open(os.path.join(folder, fn), 'r'))

            try:
                validate(template_data, schema)
            except ValidationError as err:
                print(folder, fn, err)
                # print(template_data)
                raise
    except FileNotFoundError as err:
        print(err)
        return True

    return False


def generate_vehicle(vehicle):
    pass


def gen_category_templates(floorplan, option_codes=None):
    model = create_model_jsons([floorplan,])[0]
    # print(model)

    # Generate the component category templates for this model
    # https://dev.azure.com/WGO-Web-Development/Owners%20App/_wiki/wikis/Owners-App.wiki/961/Component-Category-Template

    categories, schemas = create_component_category_jsons(model, option_codes=option_codes)
    categories_manifest = {
        'id': '',
        'deviceType': model.get('deviceType'),
        'seriesModel': model.get('seriesModel'),
        'floorPlan': model.get('floorPlan'),
        'categories': {
            _k: '{}.{}.{}.{}.{}'.format(
                model.get('deviceType'),
                model.get('seriesModel'),
                model.get('floorPlan'),
                _k,
                'v1'    # TODO: define how this increments separately for each category
            ) for _k, _v in categories.items()
        }
    }
    categories_manifest['id'] = '{deviceType}.{seriesModel}.{floorPlan}.categories'.format(
        **categories_manifest
    )
    return categories_manifest, categories, model, schemas


def gen_specific_category(floorplan, category_name, option_codes=None):
    _, categories, model, schemas = gen_category_templates(floorplan, option_codes)

    category_template = {
        '$schema': './$schema.json',
        'id': '',
        'description': 'Generated from ComponentTypes and ComponentGroups',
        'deviceType': model.get('deviceType'),
        # 'code': '',
        'seriesModel': model.get('seriesModel'),
        'floorPlan': model.get('floorPlan'),
        'version': model.get('version', 'v1'),
        'type': 'categoryTemplate',
        'schemas': {},
        'categories': {}
    }

    # Accept failure with KeyError in API calling this
    category = categories[category_name]

    category_template['id'] = '{}.{}.{}.{}.{}'.format(
        category_template.get('deviceType', 'deviceType'),
        category_template.get('seriesModel', 'seriesModel'),
        category_template.get('floorPlan', 'floorPlan'),
        category_name,
        category_template.get('version', 'v1'),
    )
    # TODO: Do we retain the previously written manifest ?
    category_template['category'] = category_name
    categories = {}

    # category_template['code'] = cat_name
    category_template['schemas'] = schemas.get(category_name)
    category_template['categories'] = {
        category_name: category
    }

    if option_codes is not None:
        # Filter components that are not relevant
        pass

    return category_template


def generate_all(base_path=os.path.abspath(sys.argv[0]), write_to_data=True, create_folders=True):
    global COMPONENTS

    base_path = os.path.split(base_path)[0]
    base_path = os.path.join(base_path, 'generated')

    component_type_path = os.path.join(base_path, 'ComponentTypes')
    component_group_path = os.path.join(base_path, 'ComponentGroups')
    category_template_path = os.path.join(base_path, 'CategoryTemplates')
    config_template_path = os.path.join(base_path, 'ConfigTemplates')
    event_dump_path = os.path.join(base_path, 'Lookups')
    ota_template_path = os.path.join(base_path, 'OtaTemplates')

    folders_to_clean = [
        base_path,
        component_type_path,
        component_group_path,
        category_template_path,
        event_dump_path,
        ota_template_path,
        config_template_path,
    ]
    # Clean folders
    # TODO: Check if we even want this
    for path in folders_to_clean:
        # print('PATH', path)
        if not os.path.exists(path) and create_folders is True:
            # print('Making folder', path)
            os.makedirs(path)
        else:
            # Remove all files that exist
            for file in os.scandir(path):
                # TODO: inject schema from somehwere else so we can recreate
                # all folders
                if 'schema.json' in file.name:
                    continue
                elif os.path.isdir(file.path):
                    continue
                # print(file.path)
                os.remove(file.path)

    """
        Export Components
    """
    for c, comp in COMPONENTS.items():
        if c is None:
            raise ValueError(f'{c}, {comp}')

        with open(os.path.join(component_type_path, f'{c}.json'), 'w') as json_out:
            json.dump(comp, json_out, indent=4, sort_keys=True)

    """
        Export Configs
    """
    for config in CONFIGS:
        out_file_name = f"Config_{config['floorPlan']}.json"
        data_path = os.path.join(
            base_path,
            '..',
            '..',
            '..',
            'data',
            out_file_name
        )
        generated_config_path = os.path.join(
            config_template_path,
            out_file_name
        )
        if write_to_data is True:
            json.dump(config, open(data_path, 'w'), indent=4)

        json.dump(config, open(generated_config_path, 'w'), indent=4)

    # TODO: Copy now to the component folder in component Integration
    # TODO: Generate Vehicle templates based on new classes

    print('>'*80)
    print('Creating Models')
    print('>'*80)

    """
        Generate and Export Component Groups
    """
    error_found = ''
    for model in create_model_jsons(MODELS):
        """
            Component Groups
        """
        out_file_name = f'{model.get("id")}.componentGroup.json'
        result = json.dumps(model, indent=4)
        full_path = os.path.join(
            component_group_path,
            out_file_name
        )
        try:
            json.dump(model, open(full_path, 'w'), indent=4)
        except TypeError as err:
            print('Type Error', err)
            print(model)
            raise

        data_path = os.path.join(
            base_path,
            '..',
            '..',
            '..',
            'data',
            out_file_name
        )
        # print(data_path)
        # sys.exit(1)
        if write_to_data is True:
            json.dump(model, open(data_path, 'w'), indent=4)
        # print(result)

        # Generate the component category templates for this model
        # https://dev.azure.com/WGO-Web-Development/Owners%20App/_wiki/wikis/Owners-App.wiki/961/Component-Category-Template
        """
            Category Templates
        """
        device_type = model.get('deviceType')
        series_model = model.get('seriesModel')
        floor_plan = model.get('floorPlan')
        version = model.get('version', 'v1')
        category_template = {
            '$schema': './$schema.json',
            'id': '',
            'description': 'Generated from ComponentTypes and ComponentGroups',
            'deviceType': device_type,
            # 'code': '',
            'seriesModel': series_model,
            'floorPlan': floor_plan,
            'version': version,
            'type': 'categoryTemplate',
            'schemas': {},
            'categories': {}
        }
        categories, schemas = create_component_category_jsons(model)
        categories_manifest = {
            'id': '',
            'deviceType': device_type,
            'seriesModel': series_model,
            'floorPlan': floor_plan,
            'categories': {
                _k: '{}.{}.{}.{}.{}'.format(
                    device_type,
                    series_model,
                    floor_plan,
                    _k,
                    'v1'    # TODO: define how this increments separately for each category
                ) for _k, _v in categories.items()
            }
        }
        categories_manifest['id'] = '{deviceType}.{seriesModel}.{floorPlan}.categories'.format(
            **categories_manifest
        )
        # print(json.dumps(categories_manifest, indent=4))
        categories_out_file_path = os.path.join(
            category_template_path,
            # category_template.get('deviceType', 'deviceType'),
            # category_template.get('seriesModel', 'seriesModel'),
            # category_template.get('floorPlan', 'floorPlan')
        )
        if not os.path.exists(categories_out_file_path):
            os.makedirs(categories_out_file_path)

        manifest_out_file_name = os.path.join(
            categories_out_file_path,
            '{}.{}.{}.categories.json'.format(
                category_template.get('deviceType', 'deviceType'),
                category_template.get('seriesModel', 'seriesModel'),
                category_template.get('floorPlan', 'floorPlan')
            )
        )
        with open(manifest_out_file_name, 'w') as manifest:
            json.dump(categories_manifest, manifest, indent=4)

        for cat_name, category in categories.items():
            category_template['id'] = '{}.{}.{}.{}.{}'.format(
                category_template.get('deviceType', 'deviceType'),
                category_template.get('seriesModel', 'seriesModel'),
                category_template.get('floorPlan', 'floorPlan'),
                cat_name,
                category_template.get('version', 'v1'),
            )
            # TODO: Do we retain the previously written manifest ?
            category_template['category'] = cat_name
            categories = {}

            # [seriesModel]/[floorplan]/categories.json
            out_file_name = os.path.join(
                categories_out_file_path,
                f'{category_template["id"]}.json'.replace(':', '.')
            )

            # category_template['code'] = cat_name
            category_template['schemas'] = schemas.get(cat_name)
            category_template['categories'] = {
                cat_name: category
            }

            with open(out_file_name, 'w') as out_file:
                json.dump(
                    category_template,
                    out_file,
                    indent=4,
                    # sort_keys=True
                )

        """
            Generate ota template
        """
        try:
            generate_ota_template(device_type, series_model, floor_plan, version)
        except Exception as err:
            print(f"[ERROR] OTA Template Generation failed for deviceType: {device_type}, seriesModel: {series_model}, floorPlan: {floor_plan}, version: {version}")
            print(err)
            error_found = 'OTA_TEMPLATE_GENERATION'

    """
        Generate event values and RV event JSONs
    """
    event_list = [{'name': x.name, 'value': x.value} for x in RVEvents]
    event_path = os.path.join(event_dump_path, 'rv_events.json')
    json.dump(event_list, open(event_path, 'w'), indent=4)

    value_types = [{'name': x.name, 'value': x.value} for x in EventValues]
    value_path = os.path.join(event_dump_path, 'event_values.json')
    json.dump(value_types, open(value_path, 'w'), indent=4)

    if error_found:
        print('Error found during', error_found)
        print('Exiting')
        sys.exit(1)

    # TODO: Write the generator for known vehicle for testing
    # Validate schemas
    folders_to_validate = (
        component_type_path,
        component_group_path,
        category_template_path,
        # config_template_path,     # TODO: Get schema/create schema
        ota_template_path
    )

    if JSON_SCHEMA is True:
        for folder in folders_to_validate:
            validate_schema(folder)
    else:
        raise ImportError('Cannot load JSON_SCHEMA')

    print('<'*80)
    print('Valided schemas')
    print('<'*80)

    return folders_to_validate


if __name__ == "__main__":
    generate_all()
