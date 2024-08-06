from enum import Enum

from pydantic import BaseModel, Field


class ProximityState(str, Enum):
    NO_CHANGE = 'NO_CHANGE'
    AWAY = 'AWAY'
    PRESENT_CLOSE = 'PRESENT_CLOSE'
    PRESENT_FAR = 'PRESENT_FAR'
    

class Proximity(BaseModel):
    '''Proximity setting model'''
    proximity_state: ProximityState = Field(
        ...,
        description='The states the proximity sensor can have, abstracted away in the given categories<br /><br />'
        'NO_CHANGE -> Proximity value unchanged<br />'
        'AWAY -> User considered away<br />'
        'PRESENT_CLOSE -> User considered close and attention to UI<br />'
        'PRESENT_FAR -> User considered in the vicinity, not clear if attenting the UI<br />'
    )
