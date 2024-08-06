import os
import sys
import logging
from datetime import datetime

from copy import deepcopy

logger = logging.getLogger(__name__)

# from common_libs.models.common import RVEvents, EventValues

try:
    from movables import *
    from lighting import *
    from climate import *
    from energy import *
    from vehicle import *
    from watersystems import *
except ImportError:
    from main_service.components.movables import *
    from main_service.components.lighting import *
    from main_service.components.climate import *
    from main_service.components.energy import *
    from main_service.components.vehicle import *
    from main_service.components.watersystems import *

import pytest

# global_vars = globals()
# global_keys = list(global_vars.keys())
# print(global_vars, global_keys)

# components = {}
# for key in global_keys:
#     print(global_vars[key])
#     try:
#         comp = global_vars[key]()
#     except TypeError as err:
#         print('Cannot create instance', key)
#         continue

#     if hasattr(comp, 'component'):
#         # Assume a componentclass
#         components[key] = deepcopy(global_vars[key])

# print(components)



# Component Generation

def test_default_movables_component():
    '''Test to make sure all movables components have the empty default
    for state and state does initialize as empty state as well.'''
    for comp in (SlideoutBasic, AwningRvc, LevelJacksRvc):
        comp_instance = comp()
        assert comp_instance.state is not None


def test_default_energy_component():
    '''Test to make sure all energy components have the empty default
    for state and state does initialize as empty state as well.'''
    for comp in (SlideoutBasic, AwningRvc, LevelJacksRvc):
        comp_instance = comp()
        assert comp_instance.state is not None


def test_default_climate_component():
    '''Test to make sure all climate components have the empty default
    for state and state does initialize as empty state as well.'''
    for comp in (Thermostat, ThermostatOutdoor, HeaterBasic, HeaterACHeatPump, RoofFanAdvanced, RefrigeratorBasic, AcRvcGe, AcRvcTruma):
        comp_instance = comp()
        assert comp_instance.state is not None


def test_default_lighting_component():
    '''Test to make sure all lighting components have the empty default
    for state and state does initialize as empty state as well.'''
    for comp in (LightSimple, LightDimmable, LightRGBW, LightGroup):
        comp_instance = comp()
        assert comp_instance.state is not None


def test_default_energy_component():
    '''Test to make sure all energy components have the empty default
    for state and state does initialize as empty state as well.'''
    for comp in (InverterBasic, InverterAdvanced, EnergyConsumer, GeneratorBasic, GeneratorPropane, GeneratorDiesel, BatteryManagement, BatteryPack, FuelTank):
        comp_instance = comp()
        assert comp_instance.state is not None


def test_default_vehicle_component():
    '''Test to make sure all vehicle components have the empty default
    for state and state does initialize as empty state as well.'''
    for comp in (VehicleId, HouseDoorLock, VehicleSprinter):
        comp_instance = comp()
        assert comp_instance.state is not None


def test_default_watersystem_component():
    '''Test to make sure all watersytem components have the empty default
    for state and state does initialize as empty state as well.'''
    for comp in (
            WaterTankDefault,
            WaterPumpDefault,
            WaterHeaterSimple,
            WaterHeaterRvc,
            TankHeatingPad):

        comp_instance = comp()
        assert comp_instance.state is not None


# @pytest.mark.skip(reason='Path in pipeline not the same')
# def test_ota_gen_failure():
#     import subprocess
#     path = os.path.split(os.path.abspath(sys.argv[0]))[0]
#     print('PATH', path)
#     path = os.path.join(path, '..', '..', 'main_service', 'components')
#     CMD = 'python3 generate_templates.py'
#     result = subprocess.run(
#         CMD.split(' '),
#         cwd=path
#     )
#     print(result)
#     assert result.returncode == 0

#     # Now load an erroneous template and run again
