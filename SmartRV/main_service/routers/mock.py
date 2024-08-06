import datetime
import json
from typing import Optional, List


from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel

from .common import ResultLevel, not_implemented


class Level(BaseModel):
    value: float
    unit: str


mock_db = json.load(open('./routers/mockdb/db.json', 'r'))


router = APIRouter(
    prefix='/mock',
    tags=['MOCK',]
)


@router.get('/widgets')
async def widgets():
    '''Respond with current set of widgets.'''
    return mock_db.get('widgets', [])    


@router.get('/bottom-widgets')
async def bottom_widgets():
    '''Respond with current set of bottom widgets.'''
    return mock_db.get('bottom-widgets', [])


@router.get('/top-widgets')
async def top_widgets():
    '''Respond with current set of top widgets.'''
    return mock_db.get('top-widgets', [])    


@router.get('/weather')
async def weather():
    '''Respond with current weather.'''
    return mock_db.get('weather', {})


@router.put('/levels/fluid/{fluid_type}')
async def fluid_levels(fluid_type: str, level: Level):
    fluid = fluid_type.lower()
    if fluid not in ('fresh', 'grey', 'black', 'fuel'):
        raise HTTPException(f'Fluid type: "{fluid}" not supported')
    
    if not 'levels' in mock_db:
        mock_db['levels'] = {
            fluid: level
        }
    else:
         mock_db['levels'][fluid] = level
