import time
from asyncio import sleep as async_sleep

from fastapi import APIRouter, Request

from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

from fastapi import HTTPException

router = APIRouter(
    prefix='/connectivity',
    tags=['CONNECTIVITY']
)


@router.get('/geo')
async def get_geo(request: Request) -> dict:
    '''Return dictionary and geo as lat, lon floats in a string'''
    try:
        optin = self.hal.vehicle.handler.vehicle[2].state.usrOptIn
        geoloc = await request.app.hal.connectivity.handler.get_sys_gps({'usrOptIn': optin})

    except Exception as err:
        print(err)
        geoloc = {'position': ''}

    response = {
        'geo': geoloc
    }
    return response


@router.put('/cellular/onoff')
async def set_cellular_onoff(request: Request, body: dict = {'onOff': 1}):
    onoff = body.get('onOff')

    cellular_onoff = request.app.config.get('cellular', {}).get('onOff')
    if cellular_onoff is None:
        raise ValueError('Cellular on-Off is not part of the config')

    request.app.config['cellular']['onOff'] = onoff


@router.get('/cellular')
async def get_cellular(request: Request) -> dict:
    '''Return Cellular Status'''
    cellular_onoff = request.app.config.get('cellular', {}).get('onOff')
    if cellular_onoff is None:
        raise ValueError('Cellular on-Off is not part of the config')

    if cellular_onoff == 1:
        try:
            cellular = await request.app.hal.connectivity.handler.get_cellular_status()
        except Exception as err:
            print('Cellular Network not available', err)
            result = {
                'msg': str(err)
            }
            raise HTTPException(408, result)
    else:
        raise HTTPException(502, {'msg': 'Cellular is set to OFF'})
        # try:
        #     request.app.config['cellular']['signalStrength'] = cellular['signal']
        #     request.app.config['cellular']['status'] = cellular['status']
        # except KeyError:
        #     raise KeyError('cellular key missing in app config')

    return cellular


@router.get('/cellular/tcudata')
async def get_cellular_tcudata(request: Request) -> dict:
    '''Return Cellular Network.'''
    return request.app.hal.features.handler.state.get('modem', {})


@router.get('/wifi')
async def get_wifi(request: Request) -> dict:
    '''Return Wifi status'''
    wifi = await request.app.hal.connectivity.handler.get_wifi_status()
    return wifi


@router.get('/timezone')
async def get_timezone(request: Request) -> dict:
    '''Return dictionary with tz_offset as float in a string'''
    timezone = await request.app.hal.connectivity.handler.get_timezone()

    response = {
        'timezone': timezone
    }
    return response
