from collections import deque
import subprocess
import threading
import asyncio
import time


CAN_IGNORE_MAP = {
    # Ignore the following messages, we map based on sent PGN
    # Outgoing messages map to the key for incoming messages
    # NOTE: This has shortcomings for messages of the same name
    # from different sources or instances within
    '19FFF644': ['waterheater_status',],        # WATERHEATER_COMMAND
    '19FE9844': ['waterheater_status_2',],      # WATERHEATER_COMMAND_2
    # '0CFC0044': ['lighting_broadcast',],        # LIGHTING


    # Incoming messages
    'waterheater_status': {     # 1FFF7
        'current_count': 3,     # Initialize as Accept, and only upon sending set to 0
        'ignore_count': 3       # How many messages do we ignore
    },
    'waterheater_status_2': {   # 1FE99
        'current_count': 3,     # Initialize as Accept, and only upon sending set to 0
        'ignore_count': 3       # How many messages do we ignore
    },
    # 'lighting_broadcast': {     # CFE20DC
    #     'current_count': 8,     # Initialize as Accept, and only upon sending set to 0
    #     'ignore_count': 8       # 2 Full cycles fopr each zone
    # }

}


class CANAPIForwardBackgroundRunner:
    '''Keeps thread running for HAL updates.'''
    def __init__(self, can_cfg: dict):
        self.config = can_cfg
        # TODO: Check if it helps to pass the app
        # Would need to create the runner on Start the rather than globally
        self.handler = HALUpdater(self.config)
        self.th = threading.Thread(target=self.handler.run_send_loop)

    async def run_main(self):
        self.th.start()
        print('[THREADS] API Sender started')

    def stop(self):
        self.handler.running = False
        if self.th.is_alive():
            self.th.join()


class HALUpdater(object):
    '''Handles sending of HAL Updates'''
    def __init__(self, cfg={}):
        self.running = True
        self.api_queue = deque(maxlen=30)

    def run_send_loop(self):
        while self.running is True:
            try:
                # FIFO
                next_cmd = self.api_queue.popleft()
            except IndexError:
                time.sleep(0.0001)
                continue

            print('[APISENDER] Next Command', next_cmd)
            func = next_cmd.get('func')
            args = next_cmd.get('args')
            try:
                result = func(*args)
            except Exception as err:
                print('[APISENDER] Error executing command)', err)
                result = 'ERROR'

            print('[APISENDER] Result:', result)


class CANSendBackgroundRunner:
    def __init__(self, can_cfg: dict, can_ignore_state: dict):
        self.config = can_cfg
        # TODO: Check if it helps to pass the app
        # Would need to create the runner on Start the rather than globally
        self.handler = CanSender(cfg=self.config, can_ignore_state=can_ignore_state)
        self.th = threading.Thread(target=self.handler.run_send_loop)

    async def run_main(self):
        self.th.start()
        print('CAN Sender started')

    def stop(self):
        self.handler.running = False
        if self.th.is_alive():
            self.th.join()


class CanSender(object):
    def __init__(self, cfg={}, can_ignore_state={}):
        self.bus = cfg.get('bus', 'canb0s0')
        self.bus_speed = cfg.get('speed', '250000')
        self.source_address = 0x44  # RV-C Network device TODO: Validate that this is a true statement
        self.can_queue = deque(maxlen=500)
        self.can_history = deque(maxlen=1000)
        # Keep track a few items for retrieval through APIs
        self.status = {
            'max_queue_length': 0
        }
        self.running = True
        # NOTE: Test that this indeed passes in the reference to the original dictionary in app
        self.can_ignore_state = can_ignore_state
        self.can_ignore_state['init'] = True

    def can_send_raw(self, pgn, data):
        cmd = f'cansend {self.bus} {pgn}#{data}'
        self.can_queue.append((cmd, pgn, data))
        return

    def get_can_history(self):
        '''Return data of current and historical sent data/commands.'''
        return {
            'current_queue_length': len(self.can_queue),
            'max_queue_length': self.status.get('max_queue_length'),
            'history_sent': self.can_history
        }

    def run_send_loop(self):
        success = False
        while self.running is True:
            try:
                # FIFO
                next_cmd = self.can_queue.popleft()
            except IndexError:
                time.sleep(0.0001)
                continue

            queue_length = len(self.can_queue)
            if queue_length > self.status.get('max_queue_length'):
                self.status['max_queue_length'] = queue_length

            # print('[QUEUE] Sending queue length', queue_length)
            # print('[QUEUE] CMD attempt:', next_cmd)

            try:
                result = subprocess.run(
                    next_cmd[0].split(' '),
                    capture_output=True
                )
                if result.returncode == 0:
                    success = True
            except FileNotFoundError as err:
                # NOTE: This occurs when cansend or the requested command is not present
                # on windows and mac that is acceptable for testing
                # print('FileNotFound', err)
                # print('CMD attempt:', next_cmd)
                success = False
                result = None

            # print('CAN SEND', next_cmd.split(' '), result)
            self.can_history.append(
                {
                    'timestamp': time.time(),
                    'cmd': next_cmd,
                    'success': success
                }
            )

            # Check if we need to reset ignore count
            pgn = next_cmd[1]
            can_ignore = self.can_ignore_state.get(pgn)
            if can_ignore is not None:
                # We iterate over the related msg names to ignore
                for msg in can_ignore:
                    print('[CAN][IGNORE] Resetting', msg)

                    # We set the current counter to 0 so it ignores up to ignore_count
                    self.can_ignore_state[msg]['current_count'] = 0


def run_main_func(runner):
    print(runner.handler)
    for i in range(25):
        print(i)
        print(runner.handler.can_send_raw('19FF2044', f'{i:02X}FFFFFFFFFFFFFF'))
    print(runner.handler.get_can_history())
    print(len(runner.handler.get_can_history()))


if __name__ == '__main__':
    import time
    runner = CANSendBackgroundRunner({})

    x = asyncio.run(runner.run_main())
    print(x)
    while True:
        run_main_func(runner)
        time.sleep(5)
        runner.stop()
        print(runner.handler.get_can_history())
        break
