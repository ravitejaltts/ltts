from typing import Optional, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

from pydantic import BaseModel, Field

PRIORITY = 0x38000000
DGN = 0xFFFF00
SOURCE_ADDRESS = 0xFF


class RawCANMessage(BaseModel):
    interface: str = 'canb0s0'
    arbitration_id: int
    arbitration_id_hex: Optional[str]
    data: List[int]


router = APIRouter(
    prefix='/testing',
    tags=['Testing/Mock',]
)


@router.get('/status')
async def status():
    return {'Status': 'OK'}


@router.put('/raw_can')
async def put_raw_can(msg: RawCANMessage) -> dict:
    print(msg)
    if msg.arbitration_id_hex is None:
        arbitration_id = msg.arbitration_id_hex
    else:
        arbitration_id = int(msg.arbitration_id_hex, 16)

    # TODO: Some basic validation to be added to the model
    # TODO: Raw can sending to happen here

    return {
        'Status': 'OK',
        'CAN_Priority': arbitration_id & PRIORITY >> 27,
        'DGN': hex((arbitration_id & DGN) >> 8),
        'SA': hex(arbitration_id & SOURCE_ADDRESS),
        'Length_Data': len(msg.data)
    }
