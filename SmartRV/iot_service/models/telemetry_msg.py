from typing import Optional, List
import json

from pydantic import BaseModel, Field


class AlertMsg(BaseModel):
    id: str
    type: str
    code: str
    category: str
    instance: str
    header: str
    message: str
    priority: str
    active: bool
    opened: int
    dismissed: int
    meta: Optional[dict]


class RequestMsg(BaseModel):
    id: str  # id supplied by the platform is returned
    source: str  # id of the src
    name: str # "APIRequest"
    requested : int # int milliseconds
    completed : int # int milliseconds
    url: str # "/api/endpoint"
    body: Optional[dict] # optional body parameters
    result: Optional[str] # optional returned data


