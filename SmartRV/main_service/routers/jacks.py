from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from pydantic import BaseModel

from .common import ResultLevel, not_implemented


router = APIRouter(
    prefix='/leveljacks',
    tags=['Levelling Jacks',]
)


class JackStatus(BaseModel):
    '''Status of the jack system'''
    pass


class JackResponse(BaseModel):
    '''Generic Response Model for Jacks'''
    result_code: int
    result_level: ResultLevel
    result_message: str


@router.get('/status', response_model=JackStatus)
async def status():
    '''Respond with current state of the the levelling jack system.'''
    return {'Status': 'OK'}


# Autolevel
@router.put('/autolevel/start', response_model=JackResponse)
async def jacks_autoelevel_start():
    '''Start Autolevel'''
    return not_implemented()


@router.put('/autolevel/stop', response_model=JackResponse)
async def jacks_autoelevel_stop():
    '''Stop Autolevel'''
    return not_implemented()


# Extend
@router.put('/extend/', response_model=JackResponse)
async def jacks_extend(jack_id: int):
    '''Extend the jacks as identified in RV-C.'''
    return not_implemented()


# Retract
@router.put('/retract/', response_model=JackResponse)
async def jacks_retract(jack_id: int):
    '''Retract the jacks as identified in RV-C.'''
    return not_implemented()


# Configure ?