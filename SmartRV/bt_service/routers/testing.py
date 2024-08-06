from typing import Optional, List

from fastapi import (
    APIRouter, 
    # HTTPException
)
# from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse

# from pydantic import BaseModel, Field


router = APIRouter(
    prefix='/testing',
    tags=['Testing/Mock',]
)


@router.get('/status')
async def status():
    return {
        'Status': 'OK'
    }
