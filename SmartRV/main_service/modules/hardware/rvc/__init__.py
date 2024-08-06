from main_service.modules.hardware.common import shell_cmd


def generate_pgn(priority, dgn, source_address):
    '''Generate the pgn as number and hex string to be used in cansend and can module.'''
    pgn = 0
    pgn += (priority << 26)
    pgn += dgn << 8
    pgn += source_address

    return {
        'dec': pgn,
        'hex': f'{pgn:03X}'
    }


class RVC(object):
    '''CAN level class around RVC functionality.'''
    SOURCE_ADDRESS = 0x44       # WinnConnect source address

    def __init__(self, cfg={}):
        self.cfg = cfg
        self.HAL = None

    def setHAL(self, hal_obj):
        self.HAL = hal_obj

    def dc_dimmer_command(self, in_state: dict, instance: int = 1):
        '''Using DC_DIMMER_COMMAND from RVC.
        6.24.5'''
        PRIORITY = 6
        DGN = 0x1FFB9

        pgn = generate_pgn(PRIORITY, DGN, self.SOURCE_ADDRESS)

        print('PGN', pgn)

        print(f"hw_movable awning light change {in_state}")

        # TODO: Check the model
        onOff = in_state.get('onOff', 1)
        brt = in_state.get('brt', 100)      # Byte 1
        if brt is None:
            brt = 100

        if onOff == 0:
            brt = 0
        else:
            brt *= 2

        # Placeholders for other values
        brtRed = 0xff       # Byte 2
        brtGreen = 0xff     # Byte 3
        brtBlue = 0xff      # Byte 4

        onDur = 0xf
        offDur = 0xf
        byte5 = (offDur << 4) + onDur

        brtWhite = 0xff
        rampTime = 0xff


        cmd = (
            f'{instance:02X}'
            f'{brt:02X}'
            f'{brtRed:02X}{brtGreen:02X}{brtBlue:02X}{byte5:02X}{brtWhite:02X}{rampTime:02X}'
        )

        self.HAL.app.can_sender.can_send_raw(
            pgn.get("hex"),
            cmd
        )
        # result = shell_cmd(
        #         f'cansend canb0s0 {pgn.get("hex")}#'
        #         f'{instance:02X}'
        #         f'{brt:02X}'
        #         f'{brtRed:02X}{brtGreen:02X}{brtBlue:02X}{byte5:02X}{brtWhite:02X}{rampTime:02X}',
        #     print_it=1
        # )

        return

    def dc_dimmer_command_2(self, in_state: dict, instance: int):
        '''Using DC_DIMMER_COMMAND_2 from RVC.
        6.24.6'''
        PRIORITY = 6
        DGN = 0x1FFB9

        pgn = generate_pgn(PRIORITY, DGN, self.SOURCE_ADDRESS)

        raise NotImplementedError()


if __name__ == '__main__':
    rvc = RVC()
    rvc.dc_dimmer_command({'onOff': 1, 'brt': 50}, instance=1)
    rvc.dc_dimmer_command_2({'onOff': 1, 'brt': 50}, instance=1)
