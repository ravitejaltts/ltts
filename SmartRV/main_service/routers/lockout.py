from enum import Enum

from fastapi import HTTPException
from pydantic.main import BaseModel


class LockoutStatus(BaseModel):
    '''Shared model containing all states that relate to lock-out conditions.
    
    PRNDL
    IGNITION
    SPEED'''
    prndl: str
    ignition: bool
    speed: float