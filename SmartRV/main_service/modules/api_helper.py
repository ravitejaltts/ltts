import time

from fastapi import Request, HTTPException

from common_libs.models.common import (
    CODE_TO_ATTR,
    ATTR_TO_CODE
)


async def validate_wc_api_call(request: Request, category: str, code: str, instance: int):
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

    # Check timestamps
    origin_timestamp = request.headers.get('origin-ts')
    if origin_timestamp is not None:
        # NOTE: We could make a key per endpoint to allow different times
        STALE_THRESHOLD = request.app.config.get('stale_request_timeout', 0.5)
        print(
            '[TIMESTAMP] VALIDATE API CALL',
            request.headers.get('origin-ts'),
            request.headers
        )
        current_time = time.time()
        origin_timestamp = int(origin_timestamp) / 1000
        if (current_time - origin_timestamp) > STALE_THRESHOLD:
            print(
                '[STALE] Request received is stale',
                current_time,
                origin_timestamp,
                current_time - origin_timestamp
            )
            raise HTTPException(400, {'msg': 'API call is stale and will not be executed.'})

    return component


async def validate_wc_state(request: Request, component_state, new_state: dict):
    '''Get a generic state attribute/property.'''
    try:
        validated = component_state.validate(new_state)
    except Exception as err:
        print('Validation error for', component_state, err)
        raise HTTPException(422, {'msg': f'State validation failure: {component_state} {err} {new_state}'})

    return validated
