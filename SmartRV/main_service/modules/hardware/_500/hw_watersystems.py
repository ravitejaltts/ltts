from common_libs.models.common import EventValues, RVEvents
from main_service.modules.constants import (
    GALLONS_2_LITER,
    WATER_UNIT_GALLONS,
    WATER_UNIT_LITER,
)
from main_service.modules.hardware._500.hw_climate import OUTSIDE_TEMP_ID

# from common_libs.models.watersystems import (
#     SIMPLE_WATER_HEATER,
#     SIMPLE_PUMP,
#     SIMPLE_TANK
# )
from main_service.modules.hardware.common import BaseWaterSystems
from main_service.modules.hardware.czone.control_rv_1 import CZone

OUTSIDE_TANK_PAD_THRESHOLD = 4.44    # 40 F

# Moving into Watersystems class above
# TODO: Read from floorplan
# ------------------------------------------------
# tanks = [1, 2, 3, 4]
# pumps = [1,]
# heaters = [1,]

THIS_SYSTEM = "WATERSYSTEMS"


INSTANCE_TO_TANK = {
    # This maps a CAN instance to the internal instance
    # Ideally it is the same like here, but to allow
    # mismatches we need to map it here
    1: 1,   # Fresh
    2: 2,   # Grey
    3: 3,   # Black,
    4: 1,    # Propane Tank (need to get this to energy through instance matching),
    101: 1,  # DC Meter Fresh
    102: 2,  # DC Meter Gray
    103: 3,  # DC Meter Black
}

INSTANCE_TO_HEATER = {
    1: 1,   # Water heater instance on TM620 is 1
}

FRESHWATER_TANK_1 = 1
GREYWATER_TANK_1 = 2
BLACKWATER_TANK_1 = 3

WATER_TANKS = (
    FRESHWATER_TANK_1,
    GREYWATER_TANK_1,
    BLACKWATER_TANK_1
)

# TODO: Move this to user config
FRESHWATER_LOW_THRESHOLD = 15.0   # %
FUEL_EMPTY_THRESHOLD = 2  # %

DATA_INVALID = 'Data Invalid'   # As set in the NMEA2K / Other DBC files

WATER_HEATER_LIGHT_CIRCUIT = 29     # TODO: Move to a component (e.g. Electrical Two - Way Rocker With Status light)

# TODO: Define Config object to move to JSON / generated code
config = {
    'tanks': {
        'count': 4,
        'items': []
    },
    'pumps': {
        'count': 2,
        'items': []
    },
    'waterHeaters': {
        'count': 1,
        'items': []
    }
}

mapping = {
    # Freshwater
    'wp1': {
        'id': 11,
        'name': 'Fresh Water',
        'subType': 'SIMPLE_PUMP',
        'type': 'FRESH',
        'description': 'Fresh Water Pump, auto engages when pressure falls',
        'state': {
            'onOff': 0
        }
    },
    # Electrical Water heater
    'wh1': {
        'id': 24,
        'inverted': True,
        'name': 'Water Heater',
        'subType': 'SIMPLE_WATER_HEATER',
        'type': 'FRESH',
        'description': 'Water Heater with manual dial to control heat',
        'information': None
    },
    # Fresh Water Tank
    'wt1': {
        'id': 1,
        'type': 'FRESH',
        'name': 'Fresh Water',
        'subType': 'SIMPLE_TANK',
        'lvl': None,
        'state': {'lvl': None},
        'cap': 0,
        'description': 'Fresh water tank',
        'information': None,
        'uiclass': 'FreshTankLevel',
        "color_fill": "#0ca9da",
        "color_empty": "#e5e5ea"
    },
    # Grey Water Tank
    'wt2': {
        'id': 2,
        'type': 'GREY',
        'name': 'Waste Water',
        'subType': 'SIMPLE_TANK',
        'lvl': None,
        'state': {'lvl': None},
        'cap': 0,
        'description': 'Gray / Waste water tank',
        'information': None,
        'uiclass': 'GreyTankLevel',
        "color_fill": "#3a3a3c",
        "color_empty": "#e5e5ea"
    },
    # BLACK Water Tank
    'wt3': {
        'id': 3,
        'type': 'BLACK',
        'name': 'Black Water',
        'subType': 'SIMPLE_TANK',
        'lvl': None,
        'state': {'lvl': None},
        'cap': 0,
        'description': 'Black / Waste water tank',
        'information': None,
        'uiclass': 'BlackTankLevel',
        "color_fill": "#3a3a3c",
        "color_empty": "#e5e5ea"
    },
    # TODO: Remove from here
    # Propane
    'wt4': {
        'id': 4,
        'type': 'PROPANE',
        'name': 'Propane',
        'subType': 'SIMPLE_TANK',
        'lvl': None,
        'state': {'lvl': None},
        'cap': 18,
        'description': 'Propane tank',
        'uiclass': 'HouseBatteryLevel',
        'information': None
    }
}

# TODO: Fold into the above and read from file/template
information = [
    {
        'title': 'MANUFACTURER INFORMATION',
        'items': [
            {
                'title': 'Water Pump',
                'sections': [
                    {
                        'title': None,
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'Shurflo'
                            },
                            {
                                'key': 'Product Model',
                                'value': '12345'
                            },
                            {
                                'key': 'Part#',
                                'value': '12345'
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Water Heater',
                'sections': [
                    {
                        'title': None,
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'GE'
                            },
                            {
                                'key': 'Product Model',
                                'value': 'ABC123'
                            },
                            {
                                'key': 'Part#',
                                'value': '12345'
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Fresh Tank',
                'sections': [
                    {
                        'title': 'TANK',
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'Winnebago Outdoors'
                            },
                            {
                                'key': 'Product Model',
                                'value': '???'
                            },
                            {
                                'key': 'Part#',
                                # Convert this to the selected unit before reporting out
                                'value': '30 gal.'
                            }
                        ]
                    },
                    {
                        'title': 'SENSOR',
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'KIB'
                            },
                            {
                                'key': 'Product Model',
                                'value': 'PSI-G-3PSI'
                            },
                            {
                                'key': 'Part#',
                                'value': 'N/A'
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Gray Tank',
                'sections': [
                    {
                        'title': 'TANK',
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'Winnebago Outdoors'
                            },
                            {
                                'key': 'Product Model',
                                'value': '???'
                            },
                            {
                                'key': 'Tank Volume',
                                # Convert this to the selected unit before reporting out
                                'value': '46 gal.'
                            }
                        ]
                    },
                    {
                        'title': 'SENSOR',
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'KIB'
                            },
                            {
                                'key': 'Product Model',
                                'value': 'PSI-G-3PSI'
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'Black Tank',
                'sections': [
                    {
                        'title': 'TANK',
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'Winnebago Outdoors'
                            },
                            {
                                'key': 'Product Model',
                                'value': '???'
                            },
                            {
                                'key': 'Tank Volume',
                                # Convert this to the selected unit before reporting out
                                'value': '47 gal.'
                            }
                        ]
                    },
                    {
                        'title': 'SENSOR',
                        'items': [
                            {
                                'key': 'Manufacturer',
                                'value': 'KIB'
                            },
                            {
                                'key': 'Product Model',
                                'value': 'PSI-G-3PSI'
                            }
                        ]
                    }
                ]
            }
        ]
    }
]

# Initialize lighting controllers used in the 800
czone = CZone(
    cfg={
        'mapping': mapping
    },
    load_from='hw_watersystems'
)

# Read mapping from CZone config or derivative

# ------------------------------------------------

init_script = {
    # Should a real script go here for init
}

shutdown_script = {}


TANK_SENSOR_MAX_VOLTAGE = 5.0   # Tank sensors should nto report > 5.0, that could be a power supply issue


def scale_voltage(volts, val_min=0, val_max=100, vlt_min=0.0, vlt_max=5.0):
    '''Scale a given voltage as percentage in a given band.
    If exceeding low or high boundaries clamp to those min/max values unless
    they are actively set to None.'''
    percent = 1 / (vlt_max - vlt_min) * (volts - vlt_min)
    # print('%', percent, type(percent))
    result = percent * 100
    if val_min is not None and result < val_min:
        return val_min
    elif val_max is not None and result > val_max:
        return val_max
    else:
        return result


# TODO: Move to shared code ?
def tank_readout(tank, unit=WATER_UNIT_GALLONS, decimals=0):
    # print('Tanks State in', tank)
    # print('Tank Attributes', tank.attributes)
    # Tank Attributes {'name': 'Fresh Water', 'description': 'Fresh Water', 'type': 'FRESH', 'cap': 60, 'unit': 'GALLONS'}

    # Get the attributes for capacity

    # Tank capacity is not read from the CZone as it might not be the only source for this, we rather set it in the template statically in GALs
    # tank_capacity = float(tank.attributes.get('cap', 0)) * 1000 / GALLONS_2_LITER       # In Gallons
    tank_capacity = float(tank.attributes.get('cap', 0))
    print('Tank Capacity', tank_capacity)
    tank_level = tank.state.lvl
    if tank_level is None:
        tank_fill = None
    else:
        tank_level = float(tank_level)
        tank_fill = tank_level / 100.0 * tank_capacity
        tank_level = int(tank_level)

    # TODO: Move this to constants same as for temp units
    if unit == WATER_UNIT_GALLONS:
        tank_unit = 'gal.'
        capacity = tank_capacity
    elif unit == WATER_UNIT_LITER:
        tank_unit = 'l.'
        if tank_fill is not None:
            tank_fill = tank_fill * GALLONS_2_LITER
        capacity = tank_capacity * GALLONS_2_LITER

    tank_result = {
        'level_raw': tank_level,
        'lvl': tank_level,
        'cap': capacity,
        'fill': tank_fill,
        'unit': tank_unit
    }
    return tank_result


# TODO: Align on the right way and place to pass in HAL
class WaterSystem(BaseWaterSystems):
    def __init__(self, config={}, components=[], app=None):
        BaseWaterSystems.__init__(self, config=config, components=components, app=app)
        self.configBaseKey = "watersystems"

        self.init_components(components, self.configBaseKey)

    def get_hw_info(self):
        return {}

    def get_tanks(self):
        '''Read list of tanks in the water system, read state and return.'''
        tanks = {k: v for (k, v) in getattr(self, self.CODE_TO_ATTR.get('wt')).items()}

        return tanks

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        '''Take a CAN message targeted for Watersystems, such as fluids etc.'''
        # {'Fluid_Instance': 1, 'Fluid_Type': 'Fresh Water', 'Fluid_Level': 0.0, 'Tank_Capacity': 0.08710000000000001,
        # 'NMEA_Reserved': 255, 'msg': None, 'msg_name': 'FLUID_LEVEL', 'instance_key': '19F21102__1'}
        updated = False
        state = None
        # print(' CAN msg n Name: ' ,msg_name, can_msg)
        FUEL_TANK_PROPANE = 4

        if msg_name == 'fluid_level':
            print('FLUID LEVEL', can_msg)
            # Get Instance and mapped instance
            can_instance = int(can_msg["Instance"])
            tank_instance = INSTANCE_TO_TANK.get(can_instance)

            can_level = can_msg['Fluid_Level']

            # We should handle propane in energy, but mapping it there is a
            # little cumbersome
            if can_instance == FUEL_TANK_PROPANE:
                tank = self.HAL.energy.handler.fuel_tank[tank_instance]
                state = tank.update_can_state(msg_name, can_msg)
            else:
                tank = self.water_tank.get(tank_instance)
                # TODO: Bring this back later, SHOULD not be used at all as we use voltage
                # updated, state = tank.update_can_state(msg_name, can_msg)

                if can_level == DATA_INVALID:
                    print('[TANK] Got Data invalid reported')
                    tank.state.lvl = None
                else:
                    new_level = float(can_level)
                    tank.state.lvl = new_level

                updated = True
                tank.update_state()

            state = tank.state

        elif msg_name == 'waterheater_status':      # 1FFF7
            # CM_ "1FFF7";
            # BO_ 2181035776 WATERHEATER_STATUS: 8  Vector__XXX
            #     SG_ Instance:
            #         0|8@1+  (1,0)   [0|255] ""    Vector__XXX
            #     SG_ Operating_Mode:
            #         8|8@1+  (1,0)   [0|255] ""    Vector__XXX
            #     SG_ Heat_Set_Point:
            #         16|16@1+  (0.03125,-273) [-8736|56799] "deg C"    Vector__XXX

            # VAL_ 2181035776 Operating_Mode
            #     0 "Off"
            #     1 "Combustion (Aquago/Combi)"
            #     2 "Electric (Combi only)"
            #     3 "Combustion & Electric (Combi only)"
            #     255 "Data Invalid";
            # TODO: Check instance, if it needs mapping
            power = 0
            instance = int(can_msg.get('Instance'))
            heater_instance = INSTANCE_TO_HEATER.get(instance)
            water_heater = self.water_heater[heater_instance]

            # RVC DBC
            heat_set_point = can_msg.get('Set_Point_Temperature')
            # TRUMA DBC has Heat_Set_Point
            # heat_set_point = can_msg.get('Heat_Set_Point')
            if heat_set_point == 'Data Invalid':
                heat_set_point = None
            else:
                print('[WATERSYSTEMS][HEATER] Heat Set Point:', heat_set_point)
                # TODO: Change to use proper temperature check function as we might get out of bounds values
                # As this comes from the HW, it should be OK, but better also check against our business rules
                water_heater.state.setTemp = float(heat_set_point)

            op_mode = can_msg.get('Operating_Mode')
            print('[WATERSYSTEMS][HEATER] op_mode received:', op_mode)
            if op_mode == 'Data Invalid':
                op_mode = None
            elif op_mode == 'Off':
                water_heater.state.op_mode = EventValues.OFF
            elif op_mode == 'combustion':
                water_heater.state.op_mode = EventValues.COMBUSTION
                water_heater.state.onOff = EventValues.ON
            elif op_mode == 'electric':
                water_heater.state.op_mode = EventValues.ELECTRIC
                water_heater.state.onOff = EventValues.ON
            elif op_mode == 'gas/electric (both)':
                water_heater.state.op_mode = EventValues.GAS_ELECTRIC
                water_heater.state.onOff = EventValues.ON
            else:
                print('[WATERSYSTEMS][HEATER] No matching op_mode found', op_mode)
                op_mode = None

            if water_heater.state.onOff == EventValues.ON:
                onOff = EventValues.ON
                power = 100   # Set LED on
            else:
                onOff = EventValues.OFF
                power = 0

            # TODO:
                # Figure out how do do the below without hard coding but through a new component and component relationships
                # Test That we handle the switch inputs on high
                # Test that this LED does works as expected when CAN updates happen
            self.HAL.electrical.handler.dc_switch(
                WATER_HEATER_LIGHT_CIRCUIT,
                onOff,
                power
            )
            updated = True
            state = water_heater.state

        elif msg_name == 'prop_tm620_config_status':  # "0EF44"
            instance = int(can_msg.get('Water_Heater_Instance'))
            heater_instance = INSTANCE_TO_HEATER.get(instance)
            water_heater = self.water_heater[heater_instance]

            LIN_Bus_Connection = can_msg.get('LIN_Bus_Connection')

            if LIN_Bus_Connection == 'No':
                self.event_logger.add_event(
                    RVEvents.WATER_HEATER_ERROR_CODES,
                    1,
                    EventValues.ON
                )
            elif LIN_Bus_Connection == 'Connected':
                self.event_logger.add_event(
                    RVEvents.WATER_HEATER_ERROR_CODES,
                    1,
                    EventValues.OFF
                )

            truma_Water_Heater_Error = can_msg.get('Truma_Water_Heater_Error')

            if truma_Water_Heater_Error == 'Error':
                self.event_logger.add_event(
                    RVEvents.WATER_HEATER_ERROR_CODES,
                    2,
                    EventValues.ON
                )
            elif truma_Water_Heater_Error == 'Ok':
                self.event_logger.add_event(
                    RVEvents.WATER_HEATER_ERROR_CODES,
                    2,
                    EventValues.OFF
                )

            state = {
                'error': truma_Water_Heater_Error
            }

            # TODO: add new alert for when error is present and combustion is true, and test cases for it


            # truma_Control_Panel_Status = can_msg.get('Truma_Control_Panel_Status')


            # print(f'''\n
            # prop_tm620_config_status\n
            # instance : {instance}\n
            # lIN_Bus_Connection : {lIN_Bus_Connection} \n
            # truma_Control_Panel_Status : {truma_Control_Panel_Status}\n
            # truma_Water_Heater_Error : {truma_Water_Heater_Error}\n
            # # ''')

        elif msg_name == 'waterheater_status_2':    # 1FE99
            # CM_ "1FE99";
            # BO_ 2180946176 WATERHEATER_STATUS_2: 8  Vector__XXX
            #     SG_ Instance:
            #         0|8@1+  (1,0)   [0|255] ""    Vector__XXX
            #     SG_ Heat_Level:
            #         8|4@1+  (1,0)   [0|15] ""    Vector__XXX

            # VAL_ 2180946176 Heat_Level
            #     0 "Default"
            #     1 "Low level (ECO)"
            #     2 "High level (COMFORT)"
            #     3 "Anti-freezing"
            #     13 "DeCalc.(status only)"
            #     15 "Data Invalid";

            # Handle Water Heater Status for TM-630 or RVC enabled heater
            # Instance mapping desirable if instance is not 1
            # TODO: Add check if instance needs mapping
            updated = False
            instance = int(can_msg.get('Instance'))
            heater_instance = INSTANCE_TO_HEATER.get(instance)
            water_heater = self.water_heater[heater_instance]

            heat_level = can_msg.get('Heat_Level')
            mode = None

            print('[WATERSYSTEMS][HEATER] Heat Level Received', heat_level)
            if heat_level == 'Default':
                # What EventValue is it supposed to be for Default ?
                mode = EventValues.COMFORT
                updated = True
            elif heat_level == 'Low level (ECO)':
                mode = EventValues.ECO
                updated = True
            elif heat_level == 'High level (COMFORT)':
                mode = EventValues.COMFORT
                updated = True
            elif heat_level == "Anti-freezing":
                mode = EventValues.ANTI_FREEZE
                updated = True
            elif heat_level == "DeCalc.(status only)":
                mode = EventValues.DECALCIFICATION
                updated = True
            else:  # 15 "Data Invalid"  or ??
                print('[WATERSYSTEMS][HEATER] Unknown heat level', heat_level)
                print('Unknown heat_level', heat_level)
                # TODO: Emit an error event so we can close these gaps one by one

            print('[WATERSYSTEMS][HEATER] Before assignment', water_heater.state.mode)
            water_heater.state.mode = mode

            # Not handling other messages yet, AFAIK coming with 524NP CombiD and not Aquago
            print('[WATERSYSTEMS][HEATER] waterheater_status END New state', state)
            # set or clear the lockout here EventValues.DECALC_WATERHEATER
            lockout = self.HAL.system.handler.lockouts[EventValues.DECALC_WATERHEATER_LOCKOUT]
            lockout.state.active = (mode == EventValues.DECALCIFICATION)

            state = water_heater.state.dict()
            print('[WATERSYSTEMS][HEATER] waterheater_status_2 END New state', state)

        elif msg_name == 'battery_status':
            # TODO: Move this to the water tank component

            instance = int(can_msg.get('Instance'))
            tank_id = INSTANCE_TO_TANK.get(instance)
            tank = self.water_tank.get(tank_id)
            if tank is None:
                raise KeyError(f'No instane {instance} found in tanks')

            try:
                voltage = float(can_msg.get('Battery_Voltage'))
            except ValueError as err:
                print('VOLTAGE CONVERSION ERROR', err)
                voltage = None

            print('[VOLTAGE]:', voltage, tank_id)

            if voltage is None:
                tank.state.lvl = None
                tank.state.vltg = None
            elif voltage == 0.0:
                tank.state.lvl = None
                tank.state.vltg = 0.0
                self.event_logger.add_event(
                    RVEvents.WATER_TANK_SENSOR_UNDERVOLTAGE,
                    tank_id,
                    EventValues.TRUE
                )
                self.event_logger.add_event(
                    RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE,
                    tank_id,
                    EventValues.FALSE
                )
                # TODO: Also emit an alert that the tank sensor is not receiving power
                # The floor for an empty tank is ~0.5 V for KiB sensors
            elif voltage > TANK_SENSOR_MAX_VOLTAGE:
                # Invalid high voltage received
                tank.state.vltg = voltage
                tank.state.lvl = None
                self.event_logger.add_event(
                    RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE,
                    tank_id,
                    EventValues.TRUE
                )
                self.event_logger.add_event(
                    RVEvents.WATER_TANK_SENSOR_UNDERVOLTAGE,
                    tank_id,
                    EventValues.FALSE
                )

            else:
                # Get values for tank
                v_min = tank.state.vltgMin
                v_max = tank.state.vltgMax
                if v_min is None or v_max is None:
                    # Throw error message
                    tank.state.lvl = None
                else:
                    level = scale_voltage(
                        voltage,
                        vlt_min=v_min,
                        vlt_max=v_max
                    )
                    print('[VOLTAGE][LEVEL]', level, tank_id)
                    tank.state.lvl = round(level, 0)

                tank.state.vltg = voltage

                self.event_logger.add_event(
                    RVEvents.WATER_TANK_SENSOR_UNDERVOLTAGE,
                    tank_id,
                    EventValues.FALSE
                )
                self.event_logger.add_event(
                    RVEvents.WATER_TANK_SENSOR_OVERVOLTAGE,
                    tank_id,
                    EventValues.FALSE
                )

        return state

    # TODO: See if that does anything
    # def heater_control(self, heater_id: int, state: dict):
    #     print(f'Water Heater Switch {state}')
    #     water_heater = self.water_heater[instance]
    #     return water_heater.set_state(state)

    def set_wh_switch_state(self, params):
        '''Update the water heater based on physical switch from electrical.'''
        # print("Setting WH switch state", params)
        instance = params.get('instance', 1)
        if params.get('active') is True:
            onOff = params.get('onOff')
            state = {
                'onOff': onOff
            }
            print("Setting WH switch state", instance, state)

            water_heater = self.water_heater[instance]
            return water_heater.set_state(state)
        else:
            return None

    def set_water_heater_state(self, instance: int):
        '''Switch Heater System as needed with canbus - incoming state already verified.'''
        # Make sure this supports the heating pads as well in the future that only have onOff
        # Are heater pads RVC?
        state = self.water_heater[instance].state

        print('[WATERHEATER] Incoming state to HAL set_water_heater_state', state.dict())

        # Check if we set onOff
        onOff = state.onOff
        mode = state.mode
        setTemp = state.setTemp

        if onOff is not None:
            cmd = f'01{onOff:02X}FFFFFFFFFFFF'
            self.HAL.app.can_sender.can_send_raw(
                '19FFF644',
                cmd
            )
            print('[WATERHEATER] Sent onOff', cmd)
        if mode is not None and onOff == EventValues.ON:
            pgn = '19FE9844'
            if mode == EventValues.ECO:
                cmd = '0101FFFFFFFFFFFF'
                self.HAL.app.can_sender.can_send_raw(
                    pgn,
                    cmd
                )
                print('[WATERHEATER] Sent mode', cmd)

            elif mode == EventValues.COMFORT:
                # update to comfort mode
                cmd = '0102FFFFFFFFFFFF'
                self.HAL.app.can_sender.can_send_raw(
                    pgn,
                    cmd
                )
                print('[WATERHEATER] Sent mode', cmd)

        if setTemp is not None and onOff == EventValues.ON:
            print(f'Water Heater temp request {setTemp}')

            # Send requested temp to the Heater
            # TODO: Move this to a helper function as it encodes RV-C data
            cvtemp = (setTemp + 273.0) / 0.03125
            ftemp = hex(round(cvtemp)).replace('0x', '')
            rtemp = ftemp[-2:] + ftemp[:2]
            print(f'[WATERHEATER][SETTEMP] {rtemp} / {cvtemp}')
            self.HAL.app.can_sender.can_send_raw(
                '19FFF644',
                f'01FF{rtemp}FFFFFFFF'
            )
            print('[WATERHEATER] Sent temp', cmd)

    def check_tank_pad_state(self, instance: int):
        """This function checks the outside temp and actually turns ON the
        circuit when temp is below 40F."""
        # print("\n\n CHECKING TANK PADS\n\n")
        heater = self.water_heater.get(instance)
        if heater is None:
            return

        circuit_onOFF = EventValues.OFF
        outside_temp = self.HAL.climate.handler.thermostat[OUTSIDE_TEMP_ID].state.temp
        if heater.state.onOff == EventValues.ON:
            if outside_temp is not None:
                # print('[OUTSIDE TEMP]', outside_temp)
                if outside_temp <= OUTSIDE_TANK_PAD_THRESHOLD:
                    circuit_onOFF = EventValues.ON
            else:
                # We have no temp need to activate and let tankpad decide
                circuit_onOFF = EventValues.ON

        # TODO: Move this into the init as a one of detection to avoid recomputation
        circuit_ids = []
        for heater_id, heater_comp in self.water_heater.items():
            if heater_comp.attributes.get('controller') == 'CZONE':
                # Find circuits
                circuits = heater_comp.attributes.get('circuits')
                if circuits is not None:
                    circuit_ids.extend(circuits)

        for cir_id in circuit_ids:
            self.HAL.electrical.handler.dc_switch(
                cir_id,
                circuit_onOFF,
                output=100
            )

        # Record the result in the state
        self.water_heater[instance].state.cirOnOff = circuit_onOFF
        self.water_heater[instance].update_state()

    def set_toilet_circuit_state(self, instance: int, new_state: dict):
        # TODO: Refactor this to be more generic, if the same as the pump in logic,
        # we should define a central logic that can handle CZONE circuit components

        toilet_circuit = self.toilet_circuit[instance]

        current_toilet_circuit_state = toilet_circuit.state.dict()
        print(f'\nToilet object: {toilet_circuit}\n')
        # Do something
        print(toilet_circuit.state)
        if current_toilet_circuit_state != new_state:
            print('New State is different', current_toilet_circuit_state, new_state)

            toilet_circuit.state.onOff = new_state['onOff']
            print(f"\nToilet circuit: {toilet_circuit.attributes.get('circuitId')}\n")

            # BMAPPING TO THE CIRCUIT
            _ = czone.circuit_control(
                toilet_circuit.attributes.get('circuitId'),
                toilet_circuit.state.onOff,
                100
            )

        return toilet_circuit.state

    def pump_switch(self, pump, new_state):
        '''Turn Pump on or off.'''
        # Get controller type
        controller = pump.attributes.get('controller')
        if controller is None:
            raise ValueError('No controller provided, no sensible defaults')

        if controller == 'CZONE':
            circuits = pump.attributes.get('circuits')
            if circuits is None:
                raise ValueError(f'Missing circuit definition')

            for circuit in circuits:
                self.HAL.electrical.handler.dc_switch(
                    circuit,
                    new_state.onOff,
                    100
                )
        else:
            raise NotImplementedError(f'Controller Type: {controller} not supported')


# TODO: Make sure to read the right mappings
module_init = (
    WaterSystem,
    'electrical_mapping',
    'components'
)


if __name__ == '__main__':
    print(handler)
