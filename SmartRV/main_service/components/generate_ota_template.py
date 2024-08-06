import json, sys, os, re

from .inputs import telemetry_config as telemetry_definition

"""
=======
Read me
=======
This script generates an ota_template.json file for a given
version number, device type, series model, and floor plan.

The following files will need to have already been generated:
- Component Group Json and ALL associating component type files
- Config Template file
- Telemetry Config file

Please tweak the constants and file paths sections as needed
"""

"""
Constants
"""
DEFAULT_AGGREGATION_VALUE = 'latest'
DEFAULT_CODE_FORMAT_VALUE = '{componentTypeCode}[#]{code}'


def generate_ota_template(device_type: str, series_model: str, floor_plan: str, version: str):
    """
    File Paths
    """
    base_path = os.path.abspath(sys.argv[0])
    base_path = os.path.split(base_path)[0]
    component_group_file_path = f'{base_path}/generated/ComponentGroups/{device_type}.{series_model}.{floor_plan}.componentGroup.json'
    config_template_file_path = f'{base_path}/generated/ConfigTemplates/Config_{floor_plan}.json'
    telemetry_config_file_path = f'{base_path}/inputs/telemetry_config.json'
    output_file_path = f'{base_path}/generated/OtaTemplates/{device_type}.{series_model}.{floor_plan}.ota_template.json'

    """
    Execute
    """
    ota_template = {
        'version': version,
        'deviceType': device_type,
        'type': 'template',
        'seriesModel': series_model,
        'floorPlan': floor_plan,
        'messageVersion': '1',
        'hardwareVersion': 'SECORev1',
        'description': 'Generated by pipeline',
        'deepObjectSeparator': '.',
    }

    # Load Floor Plan Config Template file
    config_template = {}
    with open(config_template_file_path, 'r') as config_template_file:
        config_template = json.load(config_template_file)
    ota_template['alert_items'] = config_template['alert_items']

    # Load Component Group File
    component_group = {}
    with open(component_group_file_path, 'r') as component_group_file:
        component_group = json.load(component_group_file)

    # # Load Telemetry Config File
    # telemetry_config = {}
    # with open(telemetry_config_file_path, 'r') as telemetry_config_file:
    #     telemetry_config = json.load(telemetry_config_file)
    telemetry_config = telemetry_definition.template

    def format_code(code_format: str, values: dict) -> str:
        """
            Populates the named values for a code_format string.

            For example, if we are given the 'code_format' string of '{a}_{b}_{c}'
            and a 'values' dictionary of {'a': 'rick', 'b': 'dom', 'c': 'matt'},
            the returned result will be 'rick_dom_matt'
        """
        keys = re.findall(r'{\s*(.*?)\s*\}', code_format)
        for key in keys:
            value = values.get(key)
            if value is None:
                code_format = code_format.replace(f'{{{key}}}', '')
            code_format = code_format.replace(f'{{{key}}}', value)
        return code_format

    # Iterate through component types and generate properties
    properties = []
    component_types_done = []
    target_already_done = {}

    for component in component_group['components']:
        component_type_id = component['componentTypeId']
        component_path = f'{base_path}/generated/ComponentTypes/{component_type_id}.json'

        if component_type_id in component_types_done:
            print('Skipping component type ID', component_type_id)
            continue

        component_info = {}
        with open(component_path, 'r') as component_file:
            component_info = json.load(component_file)

        for component_info_property in component_info['properties']:
            event_id = component_info_property['id']
            if event_id is None:
                continue

            property_obj = {
                'id': event_id,
                'code': component_info_property['code'],
                'category': component_info['category'],
                'componentTypeCode':  component_info['code'],
            }

            # Generate routing property
            routing = []
            follow = False
            for target_type, target_obj in telemetry_config['targets'].items():
                if target_type not in target_already_done:
                    target_already_done[target_type] = []

                mappings = target_obj.get('mappings')
                if mappings is None:
                    continue

                follow = False
                event_ids = list(map(lambda x: x['id'], mappings))
                if event_id in event_ids:
                    if event_id == 8816:
                        print(f"Processing id {event_id}")
                        follow = True

                    if event_id in target_already_done[target_type]:
                        print('Skipping multi component type use event id', event_id)
                        continue

                    mapping_index = event_ids.index(event_id)
                    mapping = mappings[mapping_index]

                    # Aggregation
                    aggregation = mapping.get('aggregation')
                    if aggregation is None:
                        aggregation = DEFAULT_AGGREGATION_VALUE

                    # Code Format
                    code_format = target_obj.get('codeFormat')
                    if code_format is None:
                        code_format = DEFAULT_CODE_FORMAT_VALUE

                    code = format_code(code_format, property_obj)

                    routing_info = {
                        'target': target_type,
                        'code': code,
                        'aggregation': aggregation
                    }
                    if follow:
                        print(f"routing {routing_info}")

                    routing.append(routing_info)
                    target_already_done[target_type].append(event_id)

            if routing:
                property_obj['routings'] = routing
                properties.append(property_obj)

        component_types_done.append(component_type_id)

    ota_template['properties'] = properties

    # Targets
    def map_target(target_tuple: tuple):
        target_type, target = target_tuple
        new_target = {
            'id': target_type,
        }

        evt = target.get('evt')
        if evt is not None:
            new_target['evt'] = evt

        mtp = target.get('mtp')
        if mtp is not None:
            new_target['mtp'] = mtp

        intervalSeconds = target.get('intervalSeconds')
        if intervalSeconds is not None:
            new_target['intervalSeconds'] = intervalSeconds

        intervalSecondsFull = target.get('intervalSecondsFull')
        if intervalSecondsFull is not None:
            new_target['intervalSecondsFull'] = intervalSecondsFull

        return new_target

    ota_template['targets'] = list(map(map_target, telemetry_config['targets'].items()))

    with open(output_file_path, 'w') as output_file:
        config_template = json.dump(ota_template, output_file, indent=4)
