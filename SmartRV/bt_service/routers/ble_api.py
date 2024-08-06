from typing import Optional, List
import sys
import json
import logging

from fastapi import (
    APIRouter,
    Request
)

from pydantic import BaseModel, Field

from common_libs.models.common import LogEvent
from bt_service.gatt.app import (
    device_list
    )


logger = logging.getLogger('Gatt')




class PairingState(BaseModel):
    pairable: bool
    advertise: bool=Field(
        True
    )


class BTDevice(BaseModel):
    '''Model for paired device info.'''
    ssid: str
    name: str
    pairedDate: Optional[str]


router = APIRouter(
    prefix='/gatt',
    tags=['Testing/Mock', ]
)


@router.get('/status')
async def status():
    return {
        'Status': 'OK'
    }


@router.put('/pairing')
async def set_pairing(state: PairingState):
    return {}


@router.get('/devices')
async def get_device_list() -> list:
    '''Get list of devices that are curerntly paired with the unit.'''
    return device_list


routerD = APIRouter(
    prefix='/updates',
    tags=['Device Interface',]
)


@routerD.put('/event')
async def put_event(request: Request, i_event: LogEvent) -> dict:
    try:
        print(f'BT event received  {i_event}')
        # request.app.iot_device_client.check_m2_event(i_event)
        # queue for device
    except Exception as err:
        print("M2event err ", err)
    return {
        'status': 'OK',
        'result': True
    }
