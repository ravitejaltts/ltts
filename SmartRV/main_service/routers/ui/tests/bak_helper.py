from common_libs.models.common import (
    LogEvent,
    RVEvents,
    EventValues
)

from ..helper import (
    get_tank_level_text,
    get_pump_text,
    get_heater_text
)


def test_level_text():
    # Set system language ENV variable
    level = {'lvl': 100}
    assert get_tank_level_text(level) == 'Full'
    level = {'lvl': 99}
    assert get_tank_level_text(level) == '99%'
    level = {'lvl': 50}
    assert get_tank_level_text(level) == '50%'
    level = {'lvl': 1}
    assert get_tank_level_text(level) == '1%'
    level = {'lvl': 0}
    assert get_tank_level_text(level) == 'Empty'


def test_pump_text():
    assert get_pump_text(0) == 'Off'
    assert get_pump_text(1) == 'On'
    assert get_pump_text(2) == 'Unknown'
    assert get_pump_text(99) == 'Unknown'
    assert get_pump_text('HELLO') == 'Unknown'


def test_heater_text():
    assert get_heater_text(0) == 'Off'
    assert 'On' in get_heater_text(1)
    assert get_heater_text(2) == 'Unknown'
    assert get_heater_text('TEST') == 'Unknown'
