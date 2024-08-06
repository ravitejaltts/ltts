import datetime

from typing import Optional, List

from logging import Logger

from fastapi import (
    APIRouter, 
    Request
)

from pydantic import (
    BaseModel, 
    Field
)

from .common import ResultLevel, not_implemented, BaseResponse


class StateHandler(object):
    '''Class to handle specific state transitions, callbacks and implement business logic.'''
    def __init__(self):
        self.state_obj = {}
        self.callback_table = {}
    
    def __repr__(self):
        return self.state_obj
    
    def add_callback(self, callback, args, kw_args={}):
        pass
    
    def push_update(self, source, event):
        pass
    
    def get_state(self):
        return self.state_obj

    def set_state(self, key, value):
        self.state_obj[key] = value
        return True


router = APIRouter(
    prefix='/state',
    tags=['STATE',]
)

router.STATE = StateHandler()
router.STATE.set_state('requests', 0)


@router.get('/full')
async def get_full_state(request: Request) -> dict:
    '''Returns the application state attribute.'''  
   
    return {
        'app_state': request.app.state,
        'coach_state': router.STATE.state_obj
    }


@router.get('/callback')
async def callback_list():
    return not_implemented()


@router.post('/callback/register/')
async def callback_register():
    return not_implemented()


@router.put('/callback/{callback_id}/')
async def callback_update():
    return not_implemented()


@router.get('/callback/{callback_id}')
async def callback_get():
    return not_implemented()


@router.delete('/callback/{callback_id}/')
async def callback_delete():
    return not_implemented()
