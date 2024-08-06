from optparse import Option
from typing import Optional, List, Union, Literal
from enum import Enum, IntEnum

from pydantic import BaseModel, Field

try:
    from common import (
        BaseComponent,
    )
except ImportError:
    from .common import (
        BaseComponent,
    )

from common_libs.models.common import RVEvents, EventValues


CATEGORY = 'connectivity'

# Location
# Cell Coverage
# Wifi Networks
# ...


class RouterState(BaseModel):
    gpsLoc: Optional[str] = Field(
        'NaN, NaN',
        description='GPS location as pulled/received by the router',
        #eventId=RVEvents.LOCATION_GEO_LOC_CHANGE,    # TODO: Add location change
        setting=False   # Can only be set programmatically
    )
    onOff: Literal[EventValues.ON, EventValues.OFF] = Field(
        EventValues.ON,
        description='Is cellular data enabled by end-user',
        eventId=RVEvents.CELLULAR_ENABLED_STATE_CHANGE,
        setting=True
    )
    signal: Optional[int] = Field(
        None,
        description='Holds the quality of the signal in a TBD numerical value, either bars or percent.',
        eventId=RVEvents.CELLULAR_STRENGTH_CHANGE,
        setting=False
    )
    status: Optional[str] = Field(
        None,
        description='Holds the string status such as OK, ERROR, SIM-FAULT etc., actual content TBD.',
        eventId=RVEvents.CELLULAR_CELLUAR_STATUS_CHANGE,
        setting=False
    )
    tcuId: Optional[str] = Field(
        None,
        description='Contains TCU_ID of the given TCU, for Cradlepoint S700 this is the MAC, which is used for NetCloud API calls.',
        eventId=RVEvents.CELLULAR_TCU_ID_CHANGE,
        setting=False
    )
    imei1: Optional[str] = Field(
        None,
        description='IMEI 1 is the first modem (S700 only modem) ID',
        eventId=RVEvents.CELLULAR_IMEI_1_CHANGE,
        setting=False
    )
    iccid1: Optional[str] = Field(
        None,
        description='ICCID 1 is the first SIM card',
        eventId=RVEvents.CELLULAR_ICCID_1_CHANGE,
        setting=False
    )
    imei2: Optional[str] = Field(
        None,
        description='IMEI 2 is the second modem (S700 only modem) ID',
        eventId=RVEvents.CELLULAR_IMEI_2_CHANGE,
        setting=False
    )
    iccid2: Optional[str] = Field(
        None,
        description='ICCID 2 is the second SIM card',
        eventId=RVEvents.CELLULAR_ICCID_2_CHANGE,
        setting=False
    )


class NetworkRouter(BaseComponent):
    category: str = CATEGORY
    code: str = 'ce'
    type: str = 'cradlepoint'   # Shall support all cradlepoints
    state: RouterState = RouterState()

    # def __init__(self, **data):
    #     # Let Pydantic do its initialization and validation first
    #     super().__init__(**data)
    #     # Now, Pydantic has already validated and assigned the fields
    #     # TODO add derived class to BaseComponent to use this new 'initial' field as below
    #     # then change the basecomponent to use the new class to any object with 'initial' defined
    #     # These initial state values will be overridden by a call to get_db_state is previously saved
    #     # Access the field description
    #     print('[COMMUNICATION][NetworkRouter]', self.state.dict())

    def set_state(self, in_state):
        state = self.state.validate(in_state)
        # TODO: Validate incoming state
        for key, value in in_state.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
        # Set and return
        # Emitting events should be ok, user opt out should not get this far
        print('[NETWORK] Setting Network State', in_state, state)
        super().set_state(in_state)
        # self.update_state()
        return self.state

    def get_location(self):
        # Get usrOptIn
        optin = self.hal.vehicle.handler.vehicle[2].state.usrOptIn
        location = self.hal.connectivity.handler.get_sys_gps(
            {
                'usrOptIn': optin
            }
        )
        self.set_state(location)
        return self.state


if __name__ == '__main__':
    pass
