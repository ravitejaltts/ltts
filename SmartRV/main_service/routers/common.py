from enum import Enum
from optparse import Option

from typing import Optional, List

from fastapi import HTTPException
from pydantic.main import BaseModel, Field


class ResultLevel(Enum):
    '''Enum of result codes strings
    OK, INFO, WARNING, ERROR, FATAL
    '''
    OK = 'OK'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    FATAL = 'FATAL'


class BaseResponse(BaseModel):
    '''Basic action response'''
    result_code: int
    result_level: ResultLevel
    result_message: str
    result_key: Optional[str] = Field(
        None,
        description='If present indicates the key that holds the response values, e.g. "water_pump"'
    )


def not_implemented():
    raise HTTPException(
        status_code=501,
        detail='Not implemented'
    )


class APIItem(BaseModel):
    path: str = Field(
        description='API path required to trigger'
    )
    PUT: Optional[dict] = Field(
        description='Required data/schema/params to trigger a change like onOff, set a settings'
    )
    GET: Optional[dict] = Field(
        description='Expected return schema for a GET request'
    )


class BaseAPIResponse(BaseModel):
    '''Basic common API response'''
    # Count of items in the response under given key
    count: int = Field(
        description='Number of systems in response'
    )
    # The key this response refers to, e.g. 'lighting'
    key: str = Field(
        description='String key used to find the system list in the response.'
    )
    # Any settings not directly related to one of the results under key
    hwSystemSettings: Optional[dict] = Field(
        description='Map of settings applicable to the overall system.'
    )
    schemas: Optional[dict]


class BaseAPIModel(BaseModel):
    '''Basic API model that all pieces of EQ adhere to.'''
    id: int = Field(
        description='Internal ID used to trigger specific API calls. Mapped against physical HW and CAN instances where applicable.'
    )
    type: str = Field(
        description='From a defined list of types that are applicable for the specific system.'
    )
    name: str = Field(
        description='String representation, potentially in local language to use on UI'
    )
    description: str = Field(
        description='Internal description for testing, could be re-used for help texts if desired'
    )
    state: Optional[dict] = Field(
        description='Tpye specific state map/dict that will correlate to the schema applicable, like onOff, brightness, etc.'
    )
    api: Optional[APIItem] = Field(
        description='API description'
    )
    information: Optional[dict] = Field(
        description='Information surrounding a piece of equipment, like Firmware version etc.'
    )
    settings: Optional[dict] = Field(
        description='Settings for a specific piece of equipment'
    )
    