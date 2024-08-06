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

try:
    from common_libs.models.common import RVEvents, EventValues
except ImportError as err:
    import sys
    import os
    abs_path = os.path.split(os.path.abspath(sys.argv[0]))[0]
    add_path = os.path.join(abs_path, '../')
    sys.path.append(
        add_path
    )
    from common_libs.models.common import RVEvents, EventValues


CATEGORY = 'vehicle'

# Odo
# VIN
# Ignition
# Gear
# Park Brake
# Vehicle Power / Pro-Power
# TODO: Should we combine these data points in one or more Vehicle Status' ?


class VINState(BaseModel):
    vin: str = Field(
        None,
        description='VIN of the vehicle.',
        eventId=RVEvents.CHASSIS_VIN_CHANGE,
        setting=False
    )


class VehicleId(BaseComponent):
    category: str = CATEGORY
    code: str = 'ch'
    type: str = 'vin'
    # componentId: str = 'ch_vin'
    state: VINState = VINState()


class HouseDoorLockState(BaseModel):
    lock: Literal[
        EventValues.LOCK,
        EventValues.UNLOCK,
        EventValues.LOCKED,
        EventValues.UNLOCKED
    ] = Field(
        EventValues.UNLOCKED,
        description='Basic door lock state',
        eventId=RVEvents.CHASSIS_DOOR_LOCK_CHANGE,
        setting=True
    )


class HouseDoorLock(BaseComponent):
    category: str = CATEGORY
    code: str = 'dl'
    type: str = 'basic'
    # componentId: str = f'{CATEGORY}.dl_basic'
    state: HouseDoorLockState = HouseDoorLockState()

    def set_state(self, new_state):
        '''Check if state is valid and transition the HW.'''
        try:
            new_state = HouseDoorLockState(**new_state)
        except Exception as err:
            print(err)
            raise ValueError(f'Cannot set state to {new_state}')

        print('New State', new_state)
        print('New State for lock', new_state.lock)
        if new_state.lock not in (EventValues.LOCK, EventValues.UNLOCK):
            raise ValueError(f'Cannot set lock to: {new_state.lock}')

        # TODO: Trigger HAL action for the given state
        self.hal.vehicle.handler.set_door_lock(self.instance, new_state)

        # Transition the state to what it is supposed to be after executing the command
        if new_state.lock == EventValues.LOCK:
            new_state.lock = EventValues.LOCKED
        elif new_state.lock == EventValues.UNLOCK:
            new_state.lock = EventValues.UNLOCKED
        else:
            raise ValueError(f'Unexpected lock state: {new_state.lock}')

        self.state = new_state
        # Emit state events
        super().set_state(None)
        return self.state


class VehicleSprinterState(BaseModel):
    vin: str = Field(
        None,
        description='VIN (Vehicle Identification Number, unique global ID for this vehicle)',
        eventId=RVEvents.CHASSIS_VIN_CHANGE,
        setting=False,
    )
    odo: float = Field(
        0.0,
        description='Odometer reading in KM unless converted.',
        eventId=RVEvents.CHASSIS_ODOMETER_READING_CHANGE,
        setting=False
        )
    ign: Literal[
        EventValues.FALSE,
        EventValues.TRUE] = Field(
            EventValues.FALSE,
            description='Ignition state',
            eventId=RVEvents.CHASSIS_IGNITION_STATUS_CHANGE,
            setting=False
        )
    parkBrk: Literal[
        EventValues.FALSE,
        EventValues.TRUE] = Field(
            EventValues.FALSE,
            description='Current state of the park brake as received by the PSM',
            eventId=RVEvents.CHASSIS_PARK_BRAKE_CHANGE,
            setting=False
        )
    notInPark: Literal[
        EventValues.FALSE,
        EventValues.TRUE] = Field(
            EventValues.TRUE,
            description='Current state of the transition as received by the PSM',
            eventId=RVEvents.CHASSIS_TRANSMISSION_NOT_IN_PARK_CHANGE,
            setting=False
        )
    pbIgnCombo: Literal[
        EventValues.FALSE,
        EventValues.TRUE] = Field(
            EventValues.FALSE,
            description='Combo signal for Park brake and Ignition. Used in Slideout.',
            eventId=RVEvents.CHASSIS_PARK_BRAKE_IGNITION_COMBO_CHANGE,
            setting=False
        )
    lock: Literal[
            EventValues.LOCKED,
            EventValues.UNLOCKED
        ] = Field(
            EventValues.UNLOCKED,
            description='Vehicle door lock status as reported by the PSM, this is separate from the house door lock although the are acting together vehicle to house.',
            eventID=RVEvents.CHASSIS_DOOR_LOCK_CHANGE,
            setting=False
        )
    batVltg: float = Field(
        0.0,
        description='Chassis Battery Voltage',
        eventId=RVEvents.CHASSIS_12V_VOLTAGE_CHANGE,
        setting=False
    )
    engRun: Literal[
            EventValues.FALSE,
            EventValues.TRUE
        ] = Field(
            EventValues.FALSE,
            description='Current State of the engine running input as received by the PSM',
            eventID=RVEvents.CHASSIS_ENGINE_RUNNING_CHANGE,
            setting=False,
        )


class VehicleSprinter(BaseComponent):
    category: str = CATEGORY
    code: str = 'ch'
    type: str = 'sprinter_psm'
    state: VehicleSprinterState = VehicleSprinterState()


class VehicleETransitState(BaseModel):
    vin: str = Field(
        None,
        description='VIN (Vehicle Identification Number, unique global ID for this vehicle)',
        eventId=RVEvents.CHASSIS_VIN_CHANGE,
        setting=False,
    )
    odo: float = Field(
        0.0,
        description='Odometer reading in KM unless converted.',
        eventId=RVEvents.CHASSIS_ODOMETER_READING_CHANGE,
        setting=False
        )
    ign: Literal[
        0,
        1] = Field(
            0,
            description='Ignition state',
            eventId=RVEvents.CHASSIS_IGNITION_STATUS_CHANGE,
            setting=False
        )
    parkBrk: Literal[
        0,
        1] = Field(
            EventValues.OFF,
            description='Current state of the park brake as received by the PSM',
            eventId=RVEvents.CHASSIS_PARK_BRAKE_CHANGE,
            setting=False
        )
    notInPark: Literal[0,
                       1
        ] = Field(
            EventValues.ON,
            description='Current state of the transition as received by the PSM',
            eventId=RVEvents.CHASSIS_TRANSMISSION_NOT_IN_PARK_CHANGE,
            setting=False
        )
    lock: Literal[
        EventValues.LOCKED,
        EventValues.UNLOCKED
    ] = Field(
        EventValues.UNLOCKED,
        description='Vehicle door lock status as reported by the PSM, this is separate from the house door lock although the are acting together vehicle to house.',
        eventID=RVEvents.CHASSIS_DOOR_LOCK_CHANGE,
        setting=False
    )
    batVltg: float = Field(
        0.0,
        description='Chassis Battery Voltage',
        eventId=RVEvents.CHASSIS_12V_VOLTAGE_CHANGE,
        setting=False
    )


class VehicleETransit(BaseComponent):
    category: str = CATEGORY
    code: str = 'ch'
    type: str = 'etransit_imotive'
    state: VehicleETransitState = VehicleETransitState()


class VehicleLocationState(BaseModel):
    pos: Optional[str] = Field(
        'NA',
        description='Current location as decimal lat,lon',
        eventId=RVEvents.LOCATION_GEO_LOC_CHANGE,
        setting=False
    )
    usrOptIn: Optional[bool] = Field(
        True,
        description='Did user opt in to location gathering',
        eventId=RVEvents.LOCATION_USER_OPTIN_CHANGE,
        setting=True
    )


class VehicleLocation(BaseComponent):
    category: str = CATEGORY
    code: str = 'ch'
    type: str = 'location_basic'
    state: VehicleLocationState = VehicleLocationState()

    def set_state(self, new_state):
        print('check_gps_task 1b1', new_state)
        try:
            new_state = VehicleLocationState(**new_state)
        except Exception as err:
            print(err)
            raise ValueError(f'Cannot set state to {new_state}')

        # TODO: Reduce resolution or do movement calculation before emitting events
        # Check threshold for location
        # if self.state.pos != 'NA':
        #     lat, lon = self.state.pos.split(',')
        #     lon = lon.strip()

        #     new_lat, new_lon = new_state.pos.split(',')
        #     new_lon = new_lon.strip()

        self.state = new_state
        if self.state.usrOptIn is False:
            self.state.pos = "User Opted Out!"
        # Emit state events
        super().set_state(None)
        return self.state

if __name__ == '__main__':
    import json

    from helper import generate_component

    for component in (VehicleId,):
        print(json.dumps(generate_component(component), indent=4))
