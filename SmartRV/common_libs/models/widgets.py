from enum import Enum
from pydoc import describe
from typing import Optional, List, Union

from pydantic import BaseModel, Field


class SimpleSwitch(BaseModel):
    onOff: int


class SimpleLevel(BaseModel):
    max: int
    min: int
    current_value: float
    unit: str
    level_text: str
    