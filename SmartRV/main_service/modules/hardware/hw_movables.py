# Movables needs a baseclass to save states
# And either control simple devices or call their controls located in a nother file.

from copy import deepcopy
import subprocess
import time

import logging

wgo_logger = logging.getLogger("main_service")
from main_service.modules.logger import prefix_log, json_logger

from main_service.modules.hardware.common import HALBaseClass, shell_cmd

from main_service.components.catalog import component_catalog
from main_service.components.movables import (
    SlideoutBasic,
    SlideoutBasicState,
    AwningRvcState,
    AwningRvc,
    LevelJacksRvc,
    JackState,
)

from common_libs.models.common import RVEvents, EventValues


CODE_TO_ATTR = {
    'lj': 'leveling_jack',
    'so': 'slideout',
    'aw': 'awning'
}

# CareFree / RV-C Awning setting to translate to
# sensitivity * 20 * 2
# This gets us a percentage
AWNING_MTNSENSE_DEFAULT = 5
AWNING_MTNSENSEONOFF_DEFAULT = 1


class Movables(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        self.configBaseKey = "movables"
        # NOTE: We could just use dict.update instead of iterating
        for key, value in config.items():
            self.state[key] = value
        prefix_log(wgo_logger, __name__, f"Initial State: {self.state}")

        self.init_components(components, self.configBaseKey)

        # Should be done in the get_db_state of the BaseComponent
        # # Initialize Awning from db
        # if hasattr(self, 'awning'):
        #     for instance, awning in self.awning.items():
        #         db_state = awning.get_db_state()
        #         print('[AWNING] DB State', instance, db_state)
        #         if db_state is not None:
        #             awning.state.mtnSense = db_state.get('mtnSense', AWNING_MTNSENSE_DEFAULT)
        #             awning.state.mtnSenseOnOff = db_state.get('mtnSenseOnOff', AWNING_MTNSENSEONOFF_DEFAULT)

                    # Apply this state
                    # TODO: Find how this can be done through an init state all owned by the component
                    # awning.set_state(
                    #     {
                    #         'mtnSenseOnOff': awning.state.mtnSenseOnOff
                    #     }
                    # )

    # def change_awning(self, in_state: AwningRvcState, id=1):
    #     for key, value in in_state.items():
    #         print(f"Awning in state {key} {value}")
    #         if key == "mode":
    #             self.awning[id].state.mode = value
    #         elif key == "setPctExt":
    #             self.awning[id].state.setPctExt = value
    #         elif key == "mtnSense":
    #             self.awning[id].state.mtnSense = value
    #         elif key == "mtnSenseOnOff":
    #             self.awning[id].state.mtnSenseOnOff = value

    #     # State is set  - now perform any action
    #     if self.awning[id].state.mode == EventValues.OFF:
    #         # Send Stop Command
    #         pass
    #     elif self.awning[id].state.mode == EventValues.EXTENDING:
    #         if self.awning[id].state.setPctExt == 100:
    #             cmd = '01FFFFC8FFFFFFFF'
    #             self.HAL.app.can_sender.can_send_raw(
    #                 '19FEF244',
    #                 cmd
    #             )
    #         else:
    #             # Send increment out cmd
    #             pass
    #     elif self.awning[id].state.mode == EventValues.RETRACTING:
    #         if self.awning[id].state.setPctExt == 0:
    #             # Send close command
    #             cmd = '01FFFF00FFFFFFFF'
    #             self.HAL.app.can_sender.can_send_raw(
    #                 '19FEF244',
    #                 cmd
    #             )
    #         else:
    #             # Send incrment in
    #             pass

    #     return self.awning[1].state

    def set_motion_sense(self, awning_id, state):
        '''Control the awning sensitivity through AWNING_COMMAND_2
        As per CareFree: 19FDCC44#0128FFFF1022FFFF.'''
        awning = self.awning[awning_id]

        # Calculate sensitivity
        if state.mtnSenseOnOff == EventValues.OFF:
            print('[AWNING][MTNSENSE] Setting motion sensitivity to 0.')
            sensitivity = 0
        elif state.mtnSenseOnOff is None or state.mtnSenseOnOff == EventValues.ON:
            # This could be ON or NONE on mtnSenseOnOff
            sensitivity = state.mtnSense
            if awning.state.mtnSense is None:
                print('[AWNING][MTNSENSE] No mtnSense stored in awning state', awning.state)
                # Get the default
                awning.state.mtnSense = awning.state.schema().get(
                        'properties', {}
                    ).get(
                        'mtnSense', {}
                    ).get(
                        'initial', AWNING_MTNSENSE_DEFAULT
                    )
                sensitivity = awning.state.mtnSense
                state.mtnSense = sensitivity
                print('[AWNING][MTNSENSE]', awning.state.mtnSense, state.mtnSense, sensitivity)
            else:
                if state.mtnSense is None:
                    sensitivity = awning.state.mtnSense
                else:
                    sensitivity = state.mtnSense
                print(
                    '[AWNING][MTNSENSE] Incoming / Stored mtnSense',
                    state.mtnSense,
                    awning.state.mtnSense,
                    sensitivity
                )
                # sensitivity = state.mtnSense

                # print('[AWNING][MTNSENSE] Use stored mtnSense', awning.state.mtnSense)
                # sensitivity = awning.state.mtnSense

        sensitivity = sensitivity * 20 * 2
        print('[AWNING][MTNSENSE] Calculated sensitivity', sensitivity)

        # 0x10 is ignition signal that should retract and then lockout
        lockouts = 0x10         # Ignition
        # The below must be FF to not restrict movement while retracting already
        # when a lockout occurs
        move_lockouts = 0xff
        # This is set to take the inputs as high inputs (as received from the PSM)
        # 0x22 means high for both types of inputs
        lockout_signals = 0x22  # Active When input high

        # Send command
        cmd = f'01{sensitivity:02X}FF{move_lockouts:02X}{lockouts:02X}{lockout_signals:02X}FFFF'
        self.HAL.app.can_sender.can_send_raw(
            '19FDCC44',
            cmd
        )

    # Awning controls
    def move_awning(self, in_state, id=1):
        '''Perform required movements of the RVC awning.'''
        awning = self.awning[id]
        can_instance = 1

        print('In State', in_state)

        if in_state.mode == EventValues.OFF:
            # Need the value for OFF
            # Need to get the can_instance to send to
            cmd = f'{can_instance:02X}FF00FFFFFFFFFF'
            self.HAL.app.can_sender.can_send_raw(
                '19FEF244',
                cmd
            )
            awning.state.mode = EventValues.OFF
            awning.state.setPctExt = None

        elif in_state.mode == EventValues.EXTENDING:
            # We need to extend to pct or continuous
            print('We want to extend', in_state)
            if in_state.setPctExt is not None:
                # Set to that percentage
                pct = in_state.setPctExt * 2
                cmd = f"{can_instance:02X}FFFF{pct:02X}FFFFFFFF"
                self.HAL.app.can_sender.can_send_raw(
                    '19FEF244',
                    cmd
                )
                awning.state.setPctExt = in_state.setPctExt
            else:
                # Extend a single cmd
                cmd = f'{can_instance:02X}FF01FFFFFFFFFF'
                self.HAL.app.can_sender.can_send_raw(
                    '19FEF244',
                    cmd
                )
                awning.state.setPctExt = None

            awning.state.mode = EventValues.EXTENDING
            print('State after sending extend', awning.state)

        elif in_state.mode == EventValues.RETRACTING:
            # We need to extend to pct or continuous
            print('We want to retract')
            if in_state.setPctExt is not None:
                # Set to that percentage
                pct = in_state.setPctExt * 2
                cmd = f'{can_instance:02X}FFFF{pct:02X}FFFFFFFF'
                self.HAL.app.can_sender.can_send_raw(
                    '19FEF244',
                    cmd
                )
                awning.state.setPctExt = in_state.setPctExt
            else:
                # Retract a single cmd
                cmd = f'{can_instance:02X}FF02FFFFFFFFFF'
                self.HAL.app.can_sender.can_send_raw(
                    '19FEF244',
                    cmd
                )
                awning.state.setPctExt = None

            awning.state.mode = EventValues.RETRACTING

        print('Returning', awning.state)
        return awning.state

    def get_jacks(self):
        return self.leveling_jack.state

    # Jack controls
    def move_jacks(self, in_state: JackState, id=1):
        print(f"hw_movable jack change {in_state}")
        for key, value in in_state.items():
            if value is not None:
                if key == "mode":
                    if value == EventValues.RETRACTED or value == 0:
                        # Send all retract command
                        cmd = '0300000000000000'
                        self.HAL.app.can_sender.can_send_raw(
                            '19FFEE44',
                            cmd
                        )
                    elif value == EventValues.LEVELING:
                        self.state["jacks"][key] = value
                        # Send AUTO LEVEL command 6 times once every 150 MS
                        for cnt in range(1, 6):
                            cmd = '0800000000000000'
                            self.HAL.app.can_sender.can_send_raw(
                                '19FFEE44',
                                cmd
                            )
                            time.sleep(0.15)  # 150 ms sleep
                        # Drop to Extended state
                        value = EventValues.EXTENDED
                    elif value == EventValues.EXTENDED:
                        # State after LEVELING
                        pass
                    # STORE THE NEW STATE
                    self.state["jacks"][key] = value
                    self.leveling_jack[id].state.mode = value
        return self.leveling_jack[id].state

    # Slider controls
    def move_slideout(self, in_state: dict, id=1):
        # TODO NEED to check all conditions to move HERE!
        # TODO: Get this from electrical mapping
        CIRCUIT_RETRACT = 18
        CIRCUIT_EXTEND = 20

        slideout = self.slideout[id]
        slideout.check_lockouts()
        if slideout.state.lockouts:
            result = {
                'status': 'Lockout conditions not met'
            }
            print('ERR'*10, 'LOCKOUT', slideout.state.lockouts)
            # Turn circuits off
            self.HAL.electrical.handler.dc_switch(CIRCUIT_EXTEND, 0, output=0)
            self.HAL.electrical.handler.dc_switch(CIRCUIT_RETRACT, 0, output=0)
            raise ValueError(str(result))

        print(f"hw_movable slider change {in_state}")
        # new_state = slideout.move(in_state)
        # TODO: Using the new state, we are going to set the HW outputs accordingly
        print('New State', in_state)
        if in_state.mode == EventValues.RETRACTING:
            # Stop extending
            self.HAL.electrical.handler.dc_switch(CIRCUIT_EXTEND, 0, output=0)
            # Send retract message
            self.HAL.electrical.handler.dc_switch(CIRCUIT_RETRACT, 1, output=100)

        elif in_state.mode == EventValues.EXTENDING:
            # Stop retracting
            self.HAL.electrical.handler.dc_switch(CIRCUIT_RETRACT, 0, output=0)
            # Send extend message
            self.HAL.electrical.handler.dc_switch(CIRCUIT_EXTEND, 1, output=100)

        elif in_state.mode in (EventValues.OFF, EventValues.EXTENDED, EventValues.RETRACTED):
            self.HAL.electrical.handler.dc_switch(CIRCUIT_EXTEND, 0, output=0)
            self.HAL.electrical.handler.dc_switch(CIRCUIT_RETRACT, 0, output=0)

        return in_state

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        print('HW Movables msg_name', msg_name)
        updated = False
        result = None

        if msg_name == "awning_status":
            print('Handling Awning Status')
            instance = int(can_msg.get("Instance", 1))

            awning = self.awning[instance]

            motion = can_msg.get("Motion")  # String
            position = can_msg.get("Position")
            # TODO: Add the other data elements to the system
            print('Motion', motion)
            print('Position', position)
            if motion == 'No motion':
                awning.state.mode = EventValues.OFF
            elif motion == 'Extending':
                awning.state.mode = EventValues.EXTENDING
            elif motion == 'Retracting':
                awning.state.mode = EventValues.RETRACTING
            else:
                awning.state.mode = None

            if position == 'Retracted':
                awning.state.pctExt = 0
                awning.state.mode = EventValues.RETRACTED
            elif position == '100% Extended':
                awning.state.pctExt = 100
                awning.state.mode = EventValues.EXTENDED
            elif position == 'Data Invalid':
                awning.state.pctExt = None
                awning.state.mode = None
            else:
                awning.state.pctExt = int(float(position))
                if awning.state.mode == EventValues.OFF:
                    awning.state.mode = EventValues.EXTENDED

            updated = True
            result = awning.state

            awning.update_state()

        elif msg_name == 'awning_status_2':
            print('Handling Awning Status 2')
            instance = int(can_msg.get("Instance", 1))

            awning = self.awning.get(instance)
            if awning is None:
                print('[AWNING] Unknown awning instance received', instance)
                return False, {}

            # Check motion sensitivity
            mtn_sense = can_msg.get('Motion_Sensitivity')
            if mtn_sense == 'Data Invalid':
                pass
            else:
                mtn_sense = float(mtn_sense)
                # Convert to 0-5 from 0-100%
                mtn_sense_setting = int(mtn_sense / 20)
                if mtn_sense_setting != awning.state.mtnSense:
                    print('[AWNING][MTNSENSE] Received updated mtnSense settings from CAN', can_msg)
                    awning.state.mtnSense = mtn_sense_setting
                    updated = True

                if mtn_sense_setting > 0:
                    awning.state.mtnSenseOnOff = EventValues.ON
                else:
                    awning.state.mtnSenseOnOff = EventValues.OFF

            result = awning.state

        return result


module_init = (
    Movables,
    'movable_mapping',
    'components'
)
