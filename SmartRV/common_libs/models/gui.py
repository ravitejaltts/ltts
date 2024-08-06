from enum import Enum
from pydoc import describe
from typing import Optional, List, Union

from  common_libs.models.common import EventValues

from pydantic import BaseModel, Field

try:
    from .common import KeyValue
except ImportError as err:
    # Needed for local testing
    print(err)
    from common import KeyValue
    print('Importing locally')


class IconState(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    UNAVAILABLE = 'unavailable'


# class SystemState(IconState):
#     pass


class IconWidget(BaseModel):
    '''Model for header icons such as wifi/ bt etc.'''
    name: str = Field(
        ...,
        description='Name used to uniquely identify the icon for automation'
    )
    icon: str = Field(
        ...,
        description='Icon name as specified by frontend application assets',
        example='top-wifi-icon'
    )
    status: IconState = Field(
        ...,
        description='Status of icon can be active/inactive or unavailable'
    )
    data: List[KeyValue] = Field(
        ...,
        description='List of key values for this icon'
    )


class HeaderWidgets(BaseModel):
    icons: List[IconWidget]


class ActionType(str, Enum):
    NAVIGATE = 'navigate'
    API_CALL = 'api_call'
    DISMISS = 'dismiss'
    NONE = 'none'


class NavigateAction(BaseModel):
    href: str = Field(
        ...,
        example='/home/somepage'
    )
    delay: Optional[int] = 0
    event_href: Optional[str] = Field(
        ...,
        description='HREF to a tracking event'
    )


class APIAction(BaseModel):
    href: str
    type: str
    params: Optional[dict]
    text: Optional[str] = Field(
        ...,
        description='Text if this action needs to show a button'
    )


class DismissAction(BaseModel):
    delay: int = 0
    event_href: Optional[str] = Field(
        ...,
        description='HREF to a tracking event'
    )
    text: Optional[str] = Field(
        ...,
        description='Text if this action needs to show a button'
    )


class Action(BaseModel):
    '''Model detailing the action to perform when e.g. clicked on a button.'''
    type: ActionType = Field(
        ...,
        example="navigate"
    )

    # action: Union[APIAction, NavigateAction, DismissAction]
    action: Optional[dict]
    active: Optional[bool]
    name: Optional[str]


class QuickActionWidget(BaseModel):
    name: str

    # UI will deal with icons for current state by adding suffix e.g. active, inactive
    # DECISION: UI handles styling due to complexitites surrounding dark mode, ada compliance etc.

    title: str
    subtext: str

    state: IconState

    action_active: Action
    action_inactive: Action
    action_longpress: Action


class LevelWidget(BaseModel):
    name: str = Field(
        ...,
        description='Automation unique name',
        example='FreshWaterLevel'
    )

    icon: str

    color_fill: str = Field(
        ...,
        description='RGB Hex color for the filled portion of the level',
        example='#3a3a3c'
    )
    color_empty: str = Field(
        ...,
        description='RGB Hex color for the empty portion of the level',
        example='#e5e5ea'
    )

    level: int = Field(
        ...,
        description='Level in percent',
        example=75
    )

    level_text: str = Field(
        ...,
        description='string representation of value, could be 100%, full, empty, 1/4.',
        example='75%'
    )

    title: str = Field(
        ...,
        description='Title explaining what this level is about',
        example='Fresh Water'
    )
    subtext: str = Field(
        ...,
        description='Smart Subtext.',
        example='6 Days'
    )

    action: Action


class TemperatureWidget(BaseModel):
    current_temp: int
    set_temp: int
    mode: str
    action_increase: Action
    action_decrease: Action


class SmartButtonWidget(BaseModel):
    icon: str

    title: str
    text: str

    action_clicked: Action
    action_longpress: Optional[Action]


class GaugeType(str, Enum):
    SEGMENTED = 'SEGMENTED'
    CONTINUOUS = 'CONTINUOUS'


class GaugeWidget(BaseModel):
    value: Union[int, float] = Field(
        ...,
        example=2.6
    )
    value_text: str = Field(
        ...,
        example='kW'
    )

    type: GaugeType = Field(
        ...,
        example='SEGMENTED'
    )

    title: str = Field(
        ...,
        example='Current Draw'
    )
    text: str = Field(
        ...,
        example='From 8 Sources'
    )


class WidgetType(str, Enum):
    QUICK_ACTION = 'QUICK_ACTION'
    LEVEL = 'LEVEL'
    TEMPERATURE = 'TEMPERATURE'
    SMART_BUTTON = 'SMART_BUTTON'
    GAUGE = 'GAUGE'


class Widget(BaseModel):
    type: WidgetType
    widget: Union[
        LevelWidget,
        QuickActionWidget,
        TemperatureWidget,
        SmartButtonWidget,
        GaugeWidget
    ]


class NotificationFooter(BaseModel):
    actions: List[str]
    action_dismiss: Optional[DismissAction]
    action_navigate: Optional[NavigateAction]


class Notification(BaseModel):
    id: int
    level: str
    header: str
    body: str
    footer: NotificationFooter


class AppIcon(BaseModel):
    src: str


class AppFeature(BaseModel):
    name: str
    title: str
    subtext: Optional[str]
    toptext_title: Optional[str]
    toptext_subtext: Optional[str]
    icon: Optional[AppIcon]
    actions: List[str]
    action_default: Optional[dict]


class AppTab(BaseModel):
    '''AppView Tab.'''
    title: str
    items: List[AppFeature]


class ClimateWidget(BaseModel):
    '''Climate Home Widget.'''
    widget: str = 'CLIMATE_HOME'

    title: Optional[str]

    climateSystemMode: str
    climateCurrentMode: Optional[str]
    climateModeText: str
    climateModeSubtext: str

    unit: str

    interiorTemp: str
    interiorTempText: str

    setTemp: Optional[float]
    setTempText: str

    fanState: List[dict]

    actions: List[Action]


class Motd(BaseModel):
    iconType: str='ASSET'
    icon: str='WGO'
    title: str
    text: str
    actions: list=[]
    name: str='HomeMotdMessage'


### Widgets for Functional Control Panel

class Opts(BaseModel):
    key: str
    value: Union[int, str]
    selected: Optional[bool]
    enabled: bool = True


class BaseFCPWidget(BaseModel):
    category: str   # This defines which feature group this widget belongs to
    title: str      # Most basic text that show prominently across all widgets
    subtext: Optional[str]

    # Override in inheriting model
    type: str = "DEFAULT"

    # TODO: Define this according to action spec
    action: Optional[dict]
    state: Optional[dict]


class InfoLabel(BaseFCPWidget):
    # Override
    type: str="WIDGET_INFOLABEL"
    text: str       # Text on the right hand side


class OptionWidget(BaseFCPWidget):
    # Override
    type: str="WIDGET_OPTIONS"

    option_param: str       # Which parameter does the option update
    options: List[Opts]


class SliderWidget(BaseFCPWidget):
    # Override
    type: str="WIDGET_SLIDER"

    min: int
    max: int
    step: int
    unit: str

    # State
    # value: int


class FCPLevelWidget(BaseFCPWidget):
    # Override
    type: str = "WIDGET_LEVEL"
    # Subtext
    # level_text: str

    min: int
    max: int
    unit: str

    # State
    # value: float


class ButtonWidget(BaseFCPWidget):
    # Override
    type: str = "WIDGET_BUTTON"


class ToggleWidget(BaseFCPWidget):
    type: str = "WIDGET_TOGGLE"
    state: dict = {'onOff': 0}


class DeadManSwitch(BaseModel):
    '''Defines the model for a dead man switch for UI / FCP.'''
    type: str = 'DEADMAN_SWITCH'
    title: Optional[str]
    subtext: Optional[str]
    name: str
    intervalMs: int = 250
    holdDelayMs: int = 0
    enabled: bool = True
    option_param: str       # Which parameter does the option update
    options: List[Opts]
    actions: dict = {
        "PRESS": {},
        "HOLD": {},
        "RELEASE": {}
    }
    state: Optional[dict]


class FCPDeadMan(DeadManSwitch, BaseFCPWidget):
    type: str = 'DEADMAN_SWITCH_FCP'


if __name__ == '__main__':

    deadman = DeadManSwitch(
        title='Dom Test',
        name='DomTest',
        option_param='mode',
        options=[
            {
                'key': 'UP',
                'value': 123
            },
            {
                'key': 'OFF',
                'value': 0
            },
            {
                'key': 'DOWN',
                'value': 124
            },
        ],
        state={
            'mode': 0
        }
    )
    print('>' * 80)
    print('Deadman Widget')
    print(deadman)
    print(deadman.schema())
    print(deadman.json())
    print('<' * 80)

    deadman_fcp = FCPDeadMan(
        title="LP Generator",
        type="DEADMAN_SWITCH_FCP",
        name="LPGenTest",
        option_param="mode",
        options=[
            {
                'key': 'OFF',
                'value': 0
            },
            {
                'key': 'ON',
                'value': 124,
                'enabled': False
            }
        ],
        category='Energy',
        state={
            'mode': 'OFF'
        },
        holdDelayMs=500,
        actions={
            'PRESS': None,
            'HOLD': {
                'type': 'api_call',
                'action': {
                    'href': '/deadman/test/HOLD',
                    'type': 'PUT',
                    'params': {
                        '$mode': 'int'
                    }
                }
            },
            'RELEASE': {
                'type': 'api_call',
                'action': {
                    'href': '/deadman/test/RELEASE',
                    'type': 'PUT',
                    'params': {
                        '$mode': 'int'
                    }
                }
            }
        }
    )
    print('>' * 80)
    print('Deadman FCP Widget')
    print(deadman_fcp)
    print(deadman_fcp.schema())
    print(deadman_fcp.json())
    print('<' * 80)

    # Perform model tests
    current_slider_value = 50
    slider = SliderWidget(
        title='Display Brightness',
        category='system',
        subtext=f'{current_slider_value} %',

        min=10,
        max=100,
        step=5,
        unit='%',

        state={
            'value': current_slider_value
        },
        action={
            'type': 'api_call',
            'action': {
                'type': 'PUT',
                'href': 'http:/localhost:8000/api/system/display/brightness',
                'params': {
                    '$value': 'int'
                }
            }
        }
    )
    print('>' * 80)
    print('Slider Widget')
    print(slider)
    print(slider.schema())
    print(slider.json())
    print('<' * 80)

    ## Toggle
    current_toggle_state = 0
    toggle = ToggleWidget(
        title='Water Pump',
        category='watersystems',

        state={
            'onOff': current_toggle_state,
        },

        action={
            'type': 'api_call',
            'action': {
                'href': f'http://localhost:8000/api/electrical/dc/1',
                'type': 'PUT',
                'params': {
                    # OnOff in this case is part of the schema, if easier we can move to state key
                    '$onOff': 'int'
                }
            }
        }

    )
    print('Toggle Widget')
    print(toggle)
    print(toggle.schema())
    print(toggle.json())
    print('<' * 80)


    ## InfoLabel
    label = InfoLabel(
        title='SW Version',
        category='system',
        subtext='Updated 01/01/23',

        text="0.4.4H1"
    )

    print('Label Widget')
    print(label)
    print(label.schema())
    print(label.json())
    print('<' * 80)


    ## Option Widget
    options = OptionWidget(
        category='climate',
        title='Fan 1 Speed',

        option_param='fanSpd',
        options=[
            Opts(
                key='OFF',
                value=EventValues.OFF.value,
                selected=True
            ),
            Opts(
                key='LOW',
                value=EventValues.LOW.value,
                selected=False
            ),
            Opts(
                key='MED',
                value=EventValues.MEDIUM.value,
                selected=False
            ),
            Opts(
                key='HIGH',
                value=EventValues.HIGH.value,
                selected=False
            )
        ],

        action={
            'type': 'api_call',
            'action': {
                'href': f'http://localhost:8000/api/climate/zones/1/fans/1/state',
                'type': 'PUT',
                'params': {
                    '$fanSpd': 'int'
                    # TODO: Clarify that each widget only controls one dynamic aspect
                    # Might need
                }
            }
        },
        state={
            "fanSpd": 0
        }
    )

    print('Options Widget')
    print(options)
    print(options.schema())
    print(options.json())
    print('<' * 80)


    ## Level
    current_soc = 50.7
    level = FCPLevelWidget(
        category='energy',
        title='Battery SoC',
        subtext=f'SoC: {current_soc} %',

        min=0,
        max=100,
        unit='%',

        state={
            'value': current_soc
        }
    )

    print('Level Widget')
    print(level)
    print(level.schema())
    print(level.json())
    print('<' * 80)


    ## Button
    button = ButtonWidget(
        category='system',
        title='Reboot',
        subtext='Restart WinnConnect HMI',

        action={
            'type': 'api_call',
            'action': {
                'href': f'http://localhost:8000/api/system/reboot',
                'type': 'PUT',
                'params': {}
            }
        }

    )

    print('button Widget')
    print(button)
    print(button.schema())
    print(button.json())
    print('<' * 80)

    import json
    for s in (button, level, options, label, toggle, slider, deadman, deadman_fcp):
        print(s, s.schema())
        print(s.json())
        obj = json.loads(s.json())
        json.dump(obj, open(obj.get('type') + '.json', 'w'), indent=4)
