import json
import sys
import os
import re

from copy import deepcopy

from main_service.components.common import (
    ComponentTypeEnum,
    COMPONENT_SEPARATOR,
    BaseAttributes
)

from main_service.components.catalog import component_catalog, component_schemas

abs_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
add_path = os.path.join(abs_path, '../../')
sys.path.append(
    add_path
)

from common_libs.models.common import RVEvents, EventValues


INJECTED_KEYS = (
    'setting',
    'eventId',
)


def schema_list(comp_list):
    for item in comp_list:
        schema = item.schema()
        print(schema.get('title'), json.dumps(schema, indent=4))
        if 'state' in schema['properties']:
            print(schema['properties']['state'])
            key = schema['properties']['state']['$ref'].split('/')[-1]
            state_schema = schema['definitions'].get(key)
            print(json.dumps(state_schema, indent=4, sort_keys=True))


def generate_component(component):
    '''Generates the component template as needed by platform.
    {
      "id" : "wh_simple",
      "deviceType": "common",
      "name" : "water heater",
      "type": "componentType",
      "code" : "wh", "category": "watersystems",
      "properties" :
        [ { "id": 2459, "code" : "temp", "type": "property", "propertyType": "number"},
          { "id": 2479, "code" : "stat", "type": "property", "propertyType": "string"},
          { "id": 2460, "code" : "onOff", "type": "property", "propertyType" : "number"}
       ]
    }
    '''
    template = {
        '$schema': "./$schema.json",
        'id': None,
        'deviceType': 'common',   # What is this ? What are the options ?
        'name': None,
        'type': 'componentType',
        'code': None,
        'category': None,
        'properties': [],
        'attributes': []
    }
    comp_instance = component()
    try:
        schema = component.schema()
    except TypeError as err:
        print('Type Error in schema', err, component, type(component), dir(component))
        raise

    # print('component', comp_instance.componentId)

    # These are the properties generated by the schema, not properties as used in the resulting json
    main_properties = schema.get('properties')
    # TODO: Update to use componentTypeId
    componentTypeId = main_properties.get(
        'componentId',
        main_properties.get(
            'componentTypeId', {}
        )
    ).get('default')

    category = comp_instance.category

    template['id'] = comp_instance.componentId

    componentType = comp_instance.code
    template['code'] = componentType

    try:
        template['name'] = ComponentTypeEnum[componentType]
    except KeyError as err:
        print('Unknown componentType', componentType)
        print(main_properties)
        print(component)
        raise

    template['category'] = category

    # Checking if state is present, if so get the reference to the state schema
    state_schema = comp_instance.state.schema()
    # print('state schema', state_schema)

    # Iterate over actual properties and add to the template
    for prop, value in state_schema.get('properties', {}).items():
        # print(prop)
        property = {
            'id': value.get('eventId'),
            'code': prop,
            # 'type': 'property',
            # Propertytype might be overwritten by conditions below and not use the schema one
            'propertyType': value.get('type'),
            'description': value.get('description')
        }
        if 'minimum' in value:
            property['minimum'] = value.get('minimum')
        if 'maximum' in value:
            property['maximum'] = value.get('maximum')

        # 'values' are used to list possible values either as eventValue or strings
        # Component definition will only care for the resulting value being int or string
        if 'values' in value:
            values = value.get('values', [])

            try:
                property['values'] = [c.name for c in values]
                property['propertyType'] = 'eventValues'
            except AttributeError as err:
                # print('Using as is representation instead of enum', value, err)
                # for a string list we accept that too
                property['values'] = [c for c in values]
                property['propertyType'] = 'string'
            # print(dir(values[0]))
            # Values indicate that it is of the type eventValues

        if 'anyOf' in value:
            # This is using Literal or possibly Union in the model definition
            # Extract values from there
            # This will win if both are defined
            values = []
            for value_item in value['anyOf']:
                for _k, _v in value_item.items():
                    # print(_k, _v)
                    values.extend(_v)

            values = list(set(values))
            property['values'] = [c.name for c in values]

        if 'enum' in value:
            # This is using Literal or possibly Union in the model definition
            # Extract values from there
            # This will win if both are defined

            if 'enum' in value:
            # This is using Literal or possibly Union in the model definition
            # Extract values from there
            # This will win if both are defined
                values = value.get('enum', [])
                # print(f'Value: {value}')
                if len(values) > 0:
                    if isinstance(values[0], type(1)):
                        # We need ito inject the eventvalues from enum
                        values = [EventValues(x) for x in values]
                        property['values'] = [c.name for c in values]
                        property['propertyType'] = 'eventValues'
                    else:
                        property['values'] = values

        if 'setting' in value:
            property['setting'] = value['setting']
        else:
            property['setting'] = True

        template['properties'].append(property)
        # print(property)

    comp_attributes = comp_instance.attributes
    attributes = {}
    # TODO: Add check for dict
    try:
        for k, v in comp_attributes.get('default', {}).items():
            # print(k, v)
            if 'values' in v:
                # print('Found values', v)
                try:
                    v['values'] = [EventValues(x).name for x in v['values']]
                except ValueError as err:
                    print(err)
                    continue

            attributes[k] = v
    except AttributeError as err:
        print(err)
        raise

    template['attributes'] = attributes

    # Schemas
    request_schema = None
    response_schema = None
    # We iterate over the properties to exclude the fields that are not setting from the request schema
    for key, schema_value in schema.get('definitions', {}).items():
        if 'State' not in key:
            print('Component Gen', key, schema_value)
            print('Not a State schema, ignore generation')
            print(schema.get('definitions'))
            print(comp_instance)
            continue
            # sys.exit()
        # Response Schema is the full schema/property list
        response_schema = deepcopy(schema_value)

        # Clean out all injected keys that do not belong into a schema
        if 'properties' not in response_schema:
            # No properties defined (happens on empty components that have no state of their own)
            pass
        else:
            for prop_name, prop in response_schema['properties'].items():
                # print(prop_name, prop)
                for inj_key in INJECTED_KEYS:
                    if inj_key in prop:
                        del prop[inj_key]

        request_schema = deepcopy(schema_value)
        non_settables = []

        if 'properties' not in request_schema:
            # No properties defined (happens on empty components that have no state of their own)
            pass
        else:
            for prop_name, prop in request_schema['properties'].items():
                # print(prop_name, prop)
                if prop.get('setting') is False:
                    non_settables.append(prop_name)

            for prop in non_settables:
                del request_schema['properties'][prop]

            # Clean out all injected keys that do not belong into a schema after iterating over them for controls
            for prop_name, prop in request_schema['properties'].items():
                # print(prop_name, prop)
                for inj_key in INJECTED_KEYS:
                    if inj_key in prop:
                        del prop[inj_key]

        # We shall break after the first state is found, as a component can only have one
        break

    if request_schema is None and response_schema is None:
        pass
    else:
        template['schemas'] = {
            'request': request_schema,
            'response': response_schema
        }

    return template


def create_component_jsons(components: list) -> dict:
    component_jsons = {}
    for component in components:
        result = generate_component(component)
        component_jsons[result.get("id")] = result

    return component_jsons


def create_model_jsons(models: list) -> dict:
    '''Generate models componentGroup files.'''
    component_groups = []
    for model in models:
        # TODO: Handle related components
        related_components = {}

        component_group = {
            "$schema": "./$schema.json",
            "id": model.get('id'),   # "s500.7054042.IM524T",
            "type": "componentGroup",
            "description": "component groups allow us to piece together rv components based on its device type, model, floorplan starting with lowest to greatest specificity",
            "deviceType": model.get('deviceType'),      # "s500",
            "seriesModel": model.get('seriesModel'),    # "7054042",
            "floorPlan": model.get('floorPlan'),        # "IM524T",
        }
        # Get attributes, we only iterate here to allow logic to modify the values
        # at a later time
        # {
        # "attributes": {
        #     "name": "????",
        #     "seriesName": "VIEW",
        #     "seriesCode": "500",
        #     "version": "1.0.0"
        # },
        component_group['attributes'] = {}
        for attr_key, attr_value in model.get('attributes', {}).items():
            component_group['attributes'][attr_key] = attr_value

        # Same here, only iterate to allow a way to modify in the future
        # Moved to attributes
        component_group['optionCodes'] = []
        for opt_code in model.get('optionCodes', []):
            component_group['optionCodes'].append(opt_code)

        # TODO: Check if making it a set would be desirable to avoid duplicates
        # "optionCodes": [
        #     "52D",
        #     "33F",
        #     "52N",
        #     "29J",
        #     "29P",
        #     "31T",
        #     "31P"
        # ],
        # Iterate over filters to allow later modification if needed
        component_group['filters'] = {}
        for filter_key, filter_value in model.get('filters', {}).items():
            component_group['filters'][filter_key] = filter_value
        # "filters": {
        #     "modelYears": ["2024", "2025"]
        # },
        component_group['components'] = []
        for component in model.get('components', []):
            filters = {}
            component.set_component_id()
            # catalog_schema = component_schemas.get(component.componentId)
            catalog_model = component_catalog.get(component.componentId)
            if catalog_model is None:
                raise KeyError(f'Cannot find component: {component.componentId}')
            # print('Component ID', component.componentId)
            # print(component)
            # print(catalog_model.component().attributes)
            converted_component = {
                'componentTypeId': component.componentId,
                'instance': component.instance,
                'attributes': None
            }

            # Add attributes from component first, then add/overwrite from componentGroup
            converted_component['attributes'] = {
                k: v for k, v in catalog_model.component().attributes.items()
            }

            for k, v in component.attributes.items():
                if k in converted_component['attributes']:
                    # print('Overwriting', k, v, 'was:', converted_component['attributes'][k])
                    pass
                converted_component['attributes'][k] = v

            # Get meta if present
            meta = component.meta
            if meta is not None:
                converted_component['meta'] = {
                    k: v for k, v in meta.items()
                }
            # print(component)
            if hasattr(component, 'optionCodes'):
                option_codes = getattr(component, 'optionCodes')
                if option_codes is not None:
                    if option_codes.startswith('-'):
                        option_codes = f'^((?!{option_codes.replace("-", "")}).)*$'

                    filters['optionCodes'] = option_codes

            if hasattr(component, 'relatedComponents'):
                related_components = getattr(
                    component,
                    'relatedComponents'
                )
                if related_components is not None:
                    # print('Adding relatedComponents')
                    converted_component['relatedComponents'] = related_components
                    # filters['relatedComponents'] = related_components

            # Now that filters ave been built, check if present and only then add the attribute to the outbound model
            if filters != {}:
                converted_component['filters'] = filters

            component_group['components'].append(converted_component)

        component_groups.append(component_group)

    return component_groups


def create_component_category_jsons(model: dict, option_codes: str = None) -> dict:
    '''Generate model component category files.
    {
        "id": "s800:1584342",
        "deviceType": "s800",
        "seriesModel" :"1584342",
        "floorPlan": "BF848R",
        "categories": {
            "energy": "energy:v1",
            "watersystem": "watersystem:v1",
            "lighting": "lighting:v1",
            "climate": "climate:v1"
        },
        "schemas": {
            // a collection of component schemas that further describe the device
        }
    }'''
    # print(model)
    # print(json.dumps(model, indent=4))

    deviceType = model.get('deviceType')
    seriesModel = model.get('seriesModel')
    floorPlan = model.get('floorPlan')
    version = model.get('version', 'v1')

    categories = {}
    schemas = {}

    components = model.get('components')

    for comp in components:
        componentTypeId = comp.get('componentTypeId')

        category, componentType = componentTypeId.split('.')
        catalog_schema = component_schemas.get(componentTypeId)
        # print(catalog_schema)
        if catalog_schema is None:
            print('No component found in catalog')
            schema = {}
            schema_name = 'NA'
            raise(ValueError(f'Cannot find {componentTypeId} in catalog. Make sure to import this'))
        else:
            schema = generate_component(catalog_schema)
            schema_name = componentType
            # schema.get('schemas', {}).get('response')

        schema_request_name = schema_name + '_request'
        schema_response_name = schema_name + '_response'

        if category not in categories:
            # print('Creating new category', category)
            # Create it now
            categories[category] = []
            schemas[category] = {}
        else:
            # print('Adding to', category)
            pass

        request_schema = schema.get('schemas', {}).get('request', {})
        request_schema['title'] = schema_request_name

        # if request_schema.get('properties') == {}:
        #     # Ignore empty schema ?
        #     schemas[category][schema_request_name] = None
        # else:
        schemas[category][schema_request_name] = request_schema

        response_schema = schema.get('schemas', {}).get('response', {})
        response_schema['title'] = schema_response_name
        schemas[category][schema_response_name] = response_schema

        out_component = {}
        instance = comp.get('instance')
        out_component['instance'] = instance
        out_component['componentType'] = componentType[:2]
        out_component['attributes'] = comp.get('attributes', {})
        if 'meta' in comp:
            out_component['meta'] = comp['meta']

        related_comps = comp.get('relatedComponents')
        if related_comps is not None:
            # print('Related Component', comp.get('relatedComponents'))
            out_component['relatedComponents'] = []
            for related_comp in related_comps:
                out_component['relatedComponents'].append(
                    {
                        'category': related_comp.get('componentTypeId').split('.')[0],
                        'componentType': related_comp.get('componentTypeId').split('.')[1].split('_')[0],
                        'instance': related_comp.get('instance')
                    }
                )
        else:
            try:
                del out_component['relatedComponents']
            except KeyError:
                pass

        filters = comp.get('filters')
        if filters is not None:
            out_component['filters'] = comp.get('filters')

            comp_filter = comp.get('filters', {}).get('optionCodes')
            if comp_filter is not None and option_codes is not None:
                # Check if this option code is in optioncodes
                print(comp, comp_filter)
                m = re.search(comp_filter, str(option_codes))
                if m is None:
                    print('Skipping not matching option code', option_codes, comp_filter)
                    del schemas[category][schema_request_name]
                    del schemas[category][schema_response_name]
                    continue
        else:
            # TODO: Figure out why we need this the dict should be created fresh for each component
            try:
                del out_component['filters']
            except KeyError:
                pass

        state_path = '{}.{}{}'.format(
            category,
            out_component['componentType'],
            instance
        )
        out_component['state'] = {
            'schema_request': schema_name + '_request',
            'schema_response': schema_name + '_response',
            'path': state_path,
            'overrideMappings': {}
        }

        categories[category].append(out_component)
        # print(json.dumps(out_component, indent=4))
        # print('<'*80)
        # input()

    # for comp_group in comp_groups:
    #     print('COMPONENT GROUP', comp_group)
    #     comp_header = {
    #         'id': f'{deviceType}:{seriesModel}:category:{version}',
    #         'deviceType': deviceType,
    #         'seriesModel': seriesModel,
    #         'floorPlan': floorPlan,
    #         'version': version
    #     }

    return categories, schemas


class ReplaceComp(object):
    def __init__(self, category, instance):
        self.category = category
        self.instance = instance


def replace_component(components, new_comp, delete=False):
    '''Replace the given component if found based on category and instance.'''
    index = None
    for i, comp in enumerate(components):
        if comp.category == new_comp.category:
            if comp.instance == new_comp.instance:
                index = i
                break

    if index is not None:
        if delete is True:
            components.pop(index)
        else:
            components[index] = new_comp

    return components


def update_component_attributes(components, new_comp, delete=True):
    '''Replace the given component if found based on category and instance.'''
    index = None
    for i, comp in enumerate(components):
        if comp.category == new_comp.category:
            if comp.instance == new_comp.instance:
                index = i
                break

    if index is not None:
        if delete is True:
            components.pop(index)
        else:
            components[index] = new_comp

    return components
