import json
import re
from typing import Union, Optional
from copy import deepcopy

import dictdiffer

from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import Response

# from . import jacks
# from . import awning
# from . import hvac        # Renamed to climate
from . import api_climate
from . import api_lighting
from . import api_watersystems
from . import api_electrical
from . import fans
from . import weather
from . import api_system

from . import can
# from . import sensors
from . import state
from . import api_energy
from . import api_settings
from . import api_vehicle
from . import api_movables
from . import api_connectivity

from . import api_features


from main_service.components.generate_templates import (
    gen_category_templates,
    gen_specific_category,
)
# from main_service.components.vehicles._500_XM524T import model_definition
from main_service.components.vehicles import MODEL_DICT

from main_service.modules.data_helper import get_unique_short_uuid
from main_service.modules.api_helper import validate_wc_api_call


from common_libs.models.common import (
    CODE_TO_ATTR,
    ATTR_TO_CODE
)


# async def validate_wc_api_call(request: Request, category: str, code: str, instance: int):
#     '''Get a generic state attribute/property.'''
#     if not hasattr(request.app.hal, category):
#         raise HTTPException(404, {'msg': f'Cannot find category {category}'})
#     handler = getattr(request.app.hal, category).handler

#     class_attribute = CODE_TO_ATTR.get(code)
#     if class_attribute is None:
#         raise HTTPException(404, {'msg': f'Cannot find code {code} in attributes'})

#     if not hasattr(handler, CODE_TO_ATTR.get(code)):
#         raise HTTPException(404, {'msg': f'Cannot find code {code}'})
#     componentType = getattr(handler, CODE_TO_ATTR.get(code))

#     if instance not in componentType:
#         raise HTTPException(404, {'msg': f'Cannot find instance {instance} for {code} in {category}'})
#     component = componentType[instance]

#     return component


router = APIRouter(
    prefix='/api',
    tags=[]
)

# # Level Jacks
# router.include_router(
#     jacks.router
# )

# # Awning
# router.include_router(
#     awning.router
# )

# HVAC
router.include_router(
    api_climate.router
)

# Connectivity
router.include_router(
    api_connectivity.router
)

# Lighting
router.include_router(
    api_lighting.router
)

# Water Systems
router.include_router(
    api_watersystems.router
)

# System
router.include_router(
    api_system.router
)

# Electrical
router.include_router(
    api_electrical.router
)

# Fans
router.include_router(
    fans.router
)

# State
router.include_router(
    state.router
)

# Energy Management
router.include_router(
    api_energy.router
)

# Settings
router.include_router(
    api_settings.router
)


@router.get('/status')
def health_check():
    '''Respond with current state of the UI Service.'''
    return {'Status': 'OK'}


# Temperature


# Slideout


# Water Heater


# Weather
router.include_router(
    weather.router
)

# Sensors / Currently not needed
# router.include_router(
#     sensors.router
# )

# Debug


# # Mock / Staging APIs
# router.include_router(
#     mock.router
# )

# CAN update handler
router.include_router(
    can.router
)

# Vehicle
router.include_router(
    api_vehicle.router
)

# Movable
router.include_router(
    api_movables.router
)

router.include_router(
    api_features.router
)


@router.get('/schemas')
async def get_schemas(
            s: str = Query(None, description='Systems for which to retrieve schemas.')
        ):
    '''Endpoint to retrieve all or filtered schemas by subsystems.'''
    # TODO: Generate the list of supported systems/modules instead of hard coding
    modules = s.split(',')

    schemas = {}

    for module in modules:
        module = module.lower()
        if module == 'lighting':
            schemas['lighting'] = await api_lighting.get_schemas()
        elif module == 'watersystems':
            schemas['watersystems'] = await api_watersystems.get_schemas()
        elif module == 'climate':
            schemas['climate'] = await api_climate.get_schemas()
        elif module == 'energy':
            schemas['energy'] = await api_energy.get_schemas()
        else:
            # Return none for unknown modules
            # TODO: Clarify if we want to return an error here, the request shall be made in accordance with available modules
            # from the API endpoint
            schemas[module] = None

    return schemas


@router.get('/definition')
async def get_definition():
    features = [
        ('lighting', api_lighting),
        ('watersystems', api_watersystems),
        ('energy', api_energy),
        ('climate', api_climate),
    ]

    schemas = {}
    categories = {}

    for cat in features:
        schemas[cat[0]] = await cat[1].get_schemas()
        try:
            categories[cat[0]] = await cat[1].get_definition()
        except AttributeError as err:
            print(err)

    print(categories)

    return {
        'schemas': schemas,
        'categories': categories
    }


@router.get('/state', tags=['STATE'])
async def get_state(request: Request, session_id: str = "") -> dict:
    '''Returns the application state attribute.

    full_state: Request full state if true, only changes when False
    session_id: Current session ID'''
    # TODO: Clarify if session ID is useful for state diffs

    if session_id:
        previous_session = request.app.sessions.get(session_id)
        if previous_session is None:
            raise HTTPException(404, {'msg': f'Session {session_id} not found'})

        state = deepcopy(request.app.hal.get_state())
        delta = dictdiffer.diff(
            state,
            previous_session
        )
        # print('delta', list(delta))
        state_delta = {}
        for item in delta:
            print('x', item, type(item))
            if item[0] == 'change':
                category, component = item[1].split('.')
                print('Category', category, 'Component', component)

                if category not in state_delta:
                    state_delta[category] = {}

                state_delta[category][component] = item[2][0]

        request.app.sessions[session_id] = state
        return {
            # 'session_id': session_id,
            **state_delta
        }
    else:
        # Get new session ID
        session_id = get_unique_short_uuid(request.app.sessions)
        # Get current state
        state = request.app.hal.get_state()
        request.app.sessions[session_id] = state       # TODO: Get current state
        return {
            'sessionId': session_id,
            **state
        }


@router.get('/halstate', tags=['STATE', ])
async def get_hal_state(request: Request):
    ''''''
    try:
        result = {}
        hal = request.app.hal
        # print(dir(hal))
        # print(hal.hal_categories)
        for key, value in hal.hal_categories.items():
            try:
                print(key, getattr(hal, key).handler.state)
            except AttributeError as err:
                print(err)
                continue

            result[key] = getattr(hal, key).handler.state
    except Exception as err:
        print("Hal_state exception", err)

    return result




@router.get('/{category}/{code}/{instance}/attributes')
async def get_generic_component_attributes(request: Request, category: str, code: str, instance: int):
    '''Get a generic component attribute.'''
    if not hasattr(request.app.hal, category):
        raise HTTPException(404, {'msg': f'Cannot find category {category}'})
    handler = getattr(request.app.hal, category).handler

    class_attribute = CODE_TO_ATTR.get(code)
    if class_attribute is None:
        raise HTTPException(404, {'msg': f'Cannot find code {code} in attributes'})

    if not hasattr(handler, CODE_TO_ATTR.get(code)):
        raise HTTPException(404, {'msg': f'Cannot find code {code}'})
    componentType = getattr(handler, CODE_TO_ATTR.get(code))

    if instance not in componentType:
        raise HTTPException(404, {'msg': f'Cannot find instance {instance} for {code} in {category}'})
    component = componentType[instance]

    return component.attributes


@router.get('/{category}/{code}/{instance}/schema')
async def get_generic_component_schema(request: Request, category: str, code: str, instance: int):
    '''Get a generic component attribute.'''
    if not hasattr(request.app.hal, category):
        raise HTTPException(404, {'msg': f'Cannot find category {category}'})
    handler = getattr(request.app.hal, category).handler

    class_attribute = CODE_TO_ATTR.get(code)
    if class_attribute is None:
        raise HTTPException(404, {'msg': f'Cannot find code {code} in attributes'})

    if not hasattr(handler, CODE_TO_ATTR.get(code)):
        raise HTTPException(404, {'msg': f'Cannot find code {code}'})
    componentType = getattr(handler, CODE_TO_ATTR.get(code))

    if instance not in componentType:
        raise HTTPException(404, {'msg': f'Cannot find instance {instance} for {code} in {category}'})
    component = componentType[instance]

    return component.state.schema()


@router.get('/{category}/{code}/{instance}/state')
async def get_generic_component_state(request: Request, category: str, code: str, instance: int):
    '''Get a generic component attribute.'''
    if not hasattr(request.app.hal, category):
        raise HTTPException(404, {'msg': f'Cannot find category {category}'})
    handler = getattr(request.app.hal, category).handler

    class_attribute = CODE_TO_ATTR.get(code)
    if class_attribute is None:
        raise HTTPException(404, {'msg': f'Cannot find code {code} in attributes'})

    if not hasattr(handler, CODE_TO_ATTR.get(code)):
        raise HTTPException(404, {'msg': f'Cannot find code {code}'})
    componentType = getattr(handler, CODE_TO_ATTR.get(code))

    if instance not in componentType:
        raise HTTPException(404, {'msg': f'Cannot find instance {instance} for {code} in {category}'})
    component = componentType[instance]

    return component.state


@router.put('/{category}/{code}/{instance}/defaults')
async def set_generic_component_state_defaults(request: Request, category: str, code: str, instance: int):
    '''Set a generic component to its default values as stored in the component / schema.'''
    component = await validate_wc_api_call(request, category, code, instance)

    # TODO: Perform the reset here
    component.set_state_defaults()

    return component.state


@router.get('/{category}/{code}/{instance}/state/{key}')
async def get_generic_state_key(request: Request, category: str, code: str, instance: int, key: str = None):
    '''Get a generic state attribute/property.'''
    if not hasattr(request.app.hal, category):
        raise HTTPException(404, {'msg': f'Cannot find category {category}'})
    handler = getattr(request.app.hal, category).handler

    class_attribute = CODE_TO_ATTR.get(code)
    if class_attribute is None:
        raise HTTPException(404, {'msg': f'Cannot find code {code} in attributes'})

    if not hasattr(handler, CODE_TO_ATTR.get(code)):
        raise HTTPException(404, {'msg': f'Cannot find code {code}'})
    componentType = getattr(handler, CODE_TO_ATTR.get(code))

    if instance not in componentType:
        raise HTTPException(404, {'msg': f'Cannot find instance {instance} for {code} in {category}'})
    component = componentType[instance]

    if hasattr(component.state, key):
        return getattr(component.state, key)
    else:
        raise HTTPException(404, {'msg': f'Cannot find attribute {key} in {category}, {code}, {instance}'})


@router.get('/meta/version')
async def get_version(request: Request):
    return request.app.__version__


@router.get('/meta/categories')
async def get_categories_templates(request: Request):
    print('App config', json.dumps(request.app.config, indent=4, sort_keys=True))
    print('Floorplan', request.app.hal.floorPlan)
    print('Option code', request.app.hal.optionCodes)

    model_definition = MODEL_DICT.get(request.app.hal.floorPlan)
    if model_definition is None:
        raise HTTPException(
            404, {'Cannot find floorplan': request.app.hal.floorPlan}
        )

    category_template, _, _, _ = gen_category_templates(model_definition)
    print(category_template)
    # return
    return category_template

    # {
    #     "id": "s500.1054042.WM524T.categories",
    #     "deviceType": "s500",
    #     "seriesModel": "1054042",
    #     "floorPlan": "WM524T",
    #     "version": "",
    #     "categories": {
    #         "vehicle": "s500.1054042.WM524T.vehicle.v1",
    #         "climate": "s500.1054042.WM524T.climate.v1",
    #         "energy": "s500.1054042.WM524T.energy.v1",
    #         "lighting": "s500.1054042.WM524T.lighting.v1",
    #         "movables": "s500.1054042.WM524T.movables.v1",
    #         "watersystems": "s500.1054042.WM524T.watersystems.v1",
    #         "system": "s500.1054042.WM524T.system.v1"
    #     }
    # }


@router.get('/meta/categories/{category}')
async def get_category_template(request: Request, category: str):
    # Get specific vehicle
    print('App config', json.dumps(request.app.config, indent=4, sort_keys=True))
    print('Floorplan', request.app.hal.floorPlan)
    print('Option code', request.app.hal.optionCodes)

    model_definition = MODEL_DICT.get(request.app.hal.floorPlan)
    if model_definition is None:
        raise HTTPException(404, {'Cannot find floorplan': request.app.hal.floorPlan})

    # Generate category templates
    # Drop all but the given category
    option_codes = ','.join(request.app.hal.optionCodes)
    try:
        result = gen_specific_category(model_definition, category, option_codes)
    except KeyError as err:
        print(err)
        result = None

    # Result is also none if the dictionary is created and the key e.g. 'domssupercategory' does not exist
    if result is None:
        raise HTTPException(
            404,
            {
                'Cannot find category': category,
                'floorplan': request.app.hal.floorPlan,
                'optioncodes': request.app.hal.optionCodes
            }
        )

    # Drop the schema from the response
    del result['$schema']

    return result


@router.get('/meta/categories/{category}/{floorplan}')
async def get_category_template_all(request: Request, category: str, floorplan: str, option_codes: str = None):
    '''Generate category tempalte with all possible options.'''
    if option_codes is not None:
        option_codes = [x.strip() for x in option_codes.split(',')]

    print('Requested Floorplan', floorplan)
    print('Option codes', option_codes)

    model_definition = MODEL_DICT.get(floorplan)
    if model_definition is None:
        raise HTTPException(404, {'Cannot find floorplan': floorplan})

    # Generate category templates
    try:
        result = gen_specific_category(
            model_definition,
            category,
            option_codes
        )
    except KeyError as err:
        print(err)
        result = None

    # Result is also none if the dictionary is created and the key e.g. 'domssupercategory' does not exist
    if result is None:
        raise HTTPException(
            404,
            {
                'Cannot find category': category,
                'floorplan': floorplan,
                'optioncodes': option_codes
            }
        )

    # Drop the schema from the response
    del result['$schema']

    return result
