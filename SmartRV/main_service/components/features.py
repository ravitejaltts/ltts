from typing import (
    Any,
    Optional,
    List,
    Union,
    Literal
)
from enum import (
    Enum,
    IntEnum
)

from pydantic import (
    BaseModel,
    Field,
    ValidationError
)

from main_service.components.common import (
    BaseComponent,
    # ComponentTypeEnum
)

from common_libs.models.common import (
    RVEvents,
    EventValues
)

from main_service.modules.constants import (
    fahrenheit_2_celcius
)
from common_libs.models.notifications import (
    notifcation_from_weather_alert,
    prepare_display_note
)


CATEGORY = 'features'
COMP_TYPE_DIAGNOSTICS = 'dx'

PET_MONITOR_MAX_TEMP_DEFAULT = 32
PET_MONITOR_MIN_TEMP_DEFAULT = 16

PET_MONITOR_BAND = 3        # Celsius

WEATHER_DEFAULT_TIMER = 15  # Minutes in motion
WEATHER_DEFAULT_TRAVEL_DISTANCE = 60    # Miles ?


# TODO: Validate that all/most API calls using models with optional parameters can adhere to using
# Reset on None -> set_state -> None value found for property x -> basecomponent -> set_default -> inital -> attributes state.x -> save to DB -> return and set state.x

class WeatherFeatureState(BaseModel):
    """State for weather."""
    onOff: Optional[Literal[
        EventValues.OFF,
        EventValues.ON
    ]] = Field(
        EventValues.ON,
        description="Feature enabled / disabled",
        setting=True,
        store_db=True
        # eventId=None,
    )
    inMtnTimer: Optional[int] = Field(
        None,
        description='Minutes in motion to consider refreshing weather',
        initial=WEATHER_DEFAULT_TIMER,
        setting=True,
        store_db=True,
        # eventId=None
    )
    trvlDist: Optional[int] = Field(
        None,
        description='Distance to travel before making another call to weather endpoint',
        initial=WEATHER_DEFAULT_TRAVEL_DISTANCE,
        setting=True,
        store_db=True
        # eventId=None
    )
    # Reviewed are below
    process: Optional[Literal[
        EventValues.OFF,
        EventValues.ON
    ]] = Field(
        EventValues.OFF,
        description=(
            'If 1 then execute the weather feature GET request to obtain latest alerts.'
            'Only expected from the platform.'
            # TODO: Set as platform only, which is currently the same
        ),
        setting=True,
        # We do not emit an event when this changes, the feature itself might emit other events as needed
        eventId=None
    )


class WeatherFeature(BaseComponent):
    """Weather feature component.

    This allows an API to be hit to request updates
    to be performed and store settings around weather
    requests."""
    category: str = CATEGORY
    code: str = 'wx'
    type: str = "basic"
    state: WeatherFeatureState = WeatherFeatureState()

    def set_state(self, state):
        new_state = WeatherFeatureState(**state)
        self.state = new_state
        super().set_state(None)

        return self.state

    def get_weather(self):
        """Query the platfrom """

       # {{baseUri}}/weather
        pass

    def input_alert(self, app, wx_alert):
        '''Take a weather alert and change to fit our notifications'''
        wx_note = notifcation_from_weather_alert(wx_alert)
        with app.n_lock:
            app.event_notifications[wx_note.notification_id] = wx_note
        app.check_note_active(wx_note, EventValues.ON, True)


class PetMonitorFeatureState(BaseModel):
    '''State for the pet monitoring feature.
    This holds the settings that drive the further algorithm
    for event and alert generation.'''
    onOff: Optional[Literal[
        EventValues.OFF,
        EventValues.ON
    ]] = Field(
        None,
        description='Feature enabled / disabled',
        setting=True,
        eventId=RVEvents.PET_MONITOR_MODE_CHANGE,
        store_db=True,
        initial=EventValues.ON
    )
    enabled: Optional[Literal[
        EventValues.OFF,
        EventValues.ON
    ]] = Field(
        None,
        description='Has the user enabled this feature, this is setting to drive UI, and is a precondition for it to be show in home and drive notifications',
        setting=True,
        eventId=RVEvents.PET_MONITOR_ENABLED_CHANGE,
        store_db=True,
        initial=EventValues.ON
    )
    minTemp: Optional[float] = Field(
        None,
        description='The temperature that we should not exceed in the coach, drives warnings and alerts',
        setting=True,
        eventId=RVEvents.PET_MONITOR_TEMP_HIGH_SETTING_CHANGE,
        ge=PET_MONITOR_MIN_TEMP_DEFAULT,
        le=PET_MONITOR_MAX_TEMP_DEFAULT,
        store_db=True,
        initial=PET_MONITOR_MIN_TEMP_DEFAULT
    )
    maxTemp: Optional[float] = Field(
        None,
        description='The temperature that we should not drop below in the coach, drives warnings and alerts',
        setting=True,
        eventId=RVEvents.PET_MONITOR_TEMP_LOW_SETTING_CHANGE,
        ge=PET_MONITOR_MIN_TEMP_DEFAULT,
        le=PET_MONITOR_MAX_TEMP_DEFAULT,
        store_db=True,
        initial=PET_MONITOR_MAX_TEMP_DEFAULT
    )
    alerts: Optional[List[int]] = Field(
        [],
        description='Holds the list of current active alerts',
        setting=False
    )
    unit: Literal['F', 'C'] = Field(
        'C',
        description="Unit of temperature",
        setting=True
    )


class PetMonitorFeature(BaseComponent):
    """Pet Monitoring feature component.
    This allows an API to be hit to request updates
    to be performed and store settings around pet monitoring
    requests."""
    STATE_DEFAULTS = {
        'onOff': EventValues.ON,
        'enabled': EventValues.ON,
        'minTemp': PET_MONITOR_MIN_TEMP_DEFAULT,
        'maxTemp': PET_MONITOR_MAX_TEMP_DEFAULT
    }

    category: str = CATEGORY
    code: str = 'pm'
    type: str = 'basic'

    state: PetMonitorFeatureState = PetMonitorFeatureState()
    # def __init__(self, **data):
    #     # Let Pydantic do its initialization and validation first
    #     super().__init__(**data)
    #     # Now, Pydantic has already validated and assigned the fields
    #     # TODO add derived class to BaseComponent to use this new 'initial' field as below
    #     # then change the basecomponent to use the new class to any object with 'initial' defined
    #     # These initial state values will be overridden by a call to get_db_state is previously saved
    #     # Access the field description
    #     print('[FEATURES][PetMonitorFeature]', self.state.dict())

    def set_state(self, state):
        # Override None value to be the current values
        unit = state.get('unit')
        if unit == 'F':
            minTemp = state.get('minTemp')
            maxTemp = state.get('maxTemp')
            if minTemp is not None:
                state['minTemp'] = fahrenheit_2_celcius(minTemp)
            if maxTemp is not None:
                state['maxTemp'] = fahrenheit_2_celcius(maxTemp)

        new_state = PetMonitorFeatureState(**state)
        print('[PETMINDER] New State', new_state)
        print('[PETMINDER] Current State', self.state)

        if new_state.onOff == EventValues.ON:
            # NOTE: BUSINESS LOGIC: Also turn enabled on
            self.state.onOff = new_state.onOff
            self.state.enabled = EventValues.ON

        elif new_state.onOff == EventValues.OFF:
            self.state.onOff = new_state.onOff
            self.state.enabled = EventValues.OFF

        # Do not modify otherwise

        if new_state.enabled is not None:
            self.state.enabled = new_state.enabled

        if new_state.minTemp is not None:
            temp_low = new_state.minTemp
        else:
            temp_low = self.state.minTemp

        if new_state.maxTemp is not None:
            temp_high = new_state.maxTemp
        else:
            temp_high = self.state.maxTemp


        if temp_low > temp_high - PET_MONITOR_BAND:
            # The band is not held, see if we can push
            # TODO: Get this done properly
            # if new_state.minTemp:
            #     # Check if we can push max
            #     if temp_high + 1 < PET_MONITOR_MAX_TEMP_DEFAULT:
            #         temp_high += 1
            raise ValueError(f'Cannot set maxTemp lower than minTemp + {PET_MONITOR_BAND} deg C')


        else:
            self.state.minTemp = temp_low
            self.state.maxTemp = temp_high

        self.update_state()

        self.save_db_state()

        # NOTE: Bring that back once solid
        # # Enable subsequent required features
        # if self.state.enabled == EventValues.ON:
        #     print('$'*80, 'Turning on Thermostat to AUTO')
        #     print('PET MINDER set state', self.state)
        #     MAIN_THERMOSTAT = 1
        #     # NOTE: As per Marc F. turn AC on to the range of petminder
        #     # Retain the current state except set temp and mode
        #     # NOTE: This will not handle multiple zones, will there be a pet zone ? OR should it apply to all
        #     thermostat = self.hal.climate.handler.thermostat[MAIN_THERMOSTAT]
        #     thermostat_state = thermostat.state.dict()
        #     print('THERMOSTAT state current', thermostat_state)
        #     thermostat.state.onOff = EventValues.ON
        #     thermostat.state.setMode = EventValues.AUTO_HEAT_COOL
        #     thermostat.state.setTempCool = self.state.maxTemp
        #     thermostat.state.setTempHeat = self.state.minTemp

        #     thermostat.update_state()

        #     print('THERMOSTAT new state', thermostat.state)

        return self.state

    # def init_state(self):
    #     '''Get state from DB if present and apply, inject defaults where needed.

    #     Differs from set_state as it would not perform the same checks and HW actions.'''
    #     saved_state = self.get_db_state()
    #     if saved_state is None:
    #         # Set defaults
    #         # TODO: Get those from the
    #         self.state = PetMonitorFeatureState(
    #             onOff=EventValues.OFF,          # R3 of Pet Minder
    #             enabled=EventValues.OFF,        # R3 of Pet Minder
    #             minTemp=PET_MONITOR_MIN_TEMP_DEFAULT,
    #             maxTemp=PET_MONITOR_MAX_TEMP_DEFAULT
    #         )
    #     else:
    #         loaded_state = PetMonitorFeatureState(**saved_state)
    #         for key, value in loaded_state.dict().items():
    #             if value is None:
    #                 # Set default
    #                 if key in self.STATE_DEFAULTS:
    #                     setattr(loaded_state, key, self.STATE_DEFAULTS[key])
    #         self.state = loaded_state


class DiagnosticsState(BaseModel):
    # test: Literal[
    #         EventValues.OFF,
    #         EventValues.ON] = Field(
    #     EventValues.OFF,
    #     description='Current Circuit State',
    #     setting=False
    # )
    canInv: dict = Field(
        {},
        description='Contains the current CAN inventory, which can be a big object. Allow filtering for retrival, use the same filter as in query for scanning.',
        setting=False
    )
    canScan: Literal[EventValues.ON, EventValues.OFF] = Field(
        EventValues.OFF,
        description='Initiate a new can scan, can be filtered by query parameters to the API call',
        setting=True
    )
    errors: list = Field(
        [],
        description='Contains current list of active CAN related errors',
        setting=False
    )


class Diagnostics(BaseComponent):
    category: str = CATEGORY        # Temporary place for it as it is electrical
    code: str = COMP_TYPE_DIAGNOSTICS
    type: str = "CAN"
    state: DiagnosticsState = DiagnosticsState()
    instance: int = 2
    # Attributes shall contain all info that is needed to drive this circuit
    # And related information back to the system
    # It also needs to be related to a specific component
    attributes: dict = {
        'name': 'Diagnostics Multiplex Component',
        'description': 'Component to facilitate the various diagnostics needs, instances can drive different types of diagnostics'
    }


class RemoteTestState(BaseModel):
    id: str = Field(
        None,
        description='Unique ID for this remote test, based on timer. In conjunction with deviceType and plan become unique enough for tracking',
        setting=True
    )
    plan: str = Field(
        'DEFAULT_REGRESSION',
        description='Pre loaded / side loaded test plan name that will be executed.',
        setting=True
    )
    path: Optional[str] = Field(
        None,
        description='Holds a non default path to report results on. Otherwise use default'
    )


class RemoteTest(BaseComponent):
    category: str = CATEGORY        # Temporary place for it as it is electrical
    code: str = COMP_TYPE_DIAGNOSTICS
    type: str = "TEST_FACILITY"
    state: RemoteTestState = RemoteTestState()
    instance: int = 1
    # Attributes shall contain all info that is needed to drive this circuit
    # And related information back to the system
    # It also needs to be related to a specific component
    attributes: dict = {
        'name': 'Diagnostics Multiplex Component',
        'description': 'Component to facilitate the various diagnostics needs, instances can drive different types of diagnostics'
    }


class SystemOverviewState(BaseModel):
    startTime: Optional[float] = Field(
        None,
        description='Time when the MAIN service became operational in seconds from EPOCH',
        eventId=None,
        setting=False,
        store_db=False
    )
    updateTime: Optional[float] = Field(
        None,
        description='Time when this state was updated in seconds since EPOCH',
        eventId=None,
        setting=False,
        store_db=False
    )
    cpuLoad: Optional[int] = Field(
        None,
        description='Current CPU load in %',
        eventId=None,
        setting=False,
        store_db=False
    )
    memory: Optional[int] = Field(
        None,
        description='Memory usage in %',
        eventId=None,
        setting=False,
        store_db=False
    )
    userStorage: Optional[float] = Field(
        None,
        description='Free User storage in MiB for path "/storage"',
        eventId=None,
        setting=False,
        store_db=False
    )
    systemStorage: Optional[float] = Field(
        None,
        description='Free System storage in MiB for path "/"',
        eventId=None,
        setting=False,
        store_db=False
    )


class SystemOverview(BaseComponent):
    '''Component to provide linux system momentary load and information.'''
    category: str = CATEGORY        # Temporary place for it as it is electrical
    code: str = COMP_TYPE_DIAGNOSTICS
    type: str = "SYSTEM_OVERVIEW"
    state: SystemOverviewState = SystemOverviewState()

    instance: int = 3   # NOTE: Hard coded instance, not to be overwritten by vehicle template

    attributes = {
        'name': 'System Overview',
        'description': 'Provides access to the current load and uptime of the system.',
        'type': 'SYSTEM_OVERVIEW'
    }

    def set_state(self, state):
        '''Check and set incoming new state for System Overview.'''
        print('SETTING STATE for Diagnostics', state)
        new_state = SystemOverviewState(
            **state
        )

        if new_state.updateTime is not None:
            self.state.updateTime = new_state.updateTime

        if new_state.cpuLoad is not None:
            self.state.cpuLoad = new_state.cpuLoad

        if new_state.memory is not None:
            self.state.memory = new_state.memory

        if new_state.userStorage is not None:
            self.state.userStorage = new_state.userStorage

        if new_state.systemStorage is not None:
            self.state.systemStorage = new_state.systemStorage

        super().set_state(None)

        print('SETTING STATE for Diagnostics', self.state)

        return self.state


def get_base_features(model):
    # Check what the model supports, currently all of this
    # TODO: Create feature mapping to series, floorplan etc.
    # Check how complex such a mapping needs to be and build accordingly
    return [
        RemoteTest(
            attributes={
                'name': 'Remote Testing Facilitator',
                'description': 'Allows remote tests to be performed',
                'type': 'REMOTE_TEST'
            }
        ),
        Diagnostics(
            attributes={
                'name': 'CAN Diagnostics',
                'description': 'Provides access to CAN diagnostics',
                'type': 'CAN_INVENTORY'
            }
        ),
        SystemOverview(),
        PetMonitorFeature(
            instance=1,
            attributes={
                'name': 'Pet Monitoring',
                'description': 'Pet Monitoring Feature Virtual Component',
                'type': 'basic'
            },
            state=PetMonitorFeatureState()
        ),
        WeatherFeature(
            instance=1,
            attributes={
                'name': 'Weather Alerts',
                'description': 'Weather Alerts - Settings Virtual Component',
                'type': 'basic',
                'minTravelDistanceMiles': 60
            }
        )
    ]



if __name__ == "__main__":
    pass
