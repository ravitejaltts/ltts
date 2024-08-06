# -------------------------------------------------------------------------
# Copyright (c) Winnebago Industries. All rights reserved.
# --------------------------------------------------------------------------

# Version for the service is in the main py file.
__version__ = "1.0.0"

import asyncio
import os
import threading
import time
import subprocess

# from six.moves import input
from fastapi import FastAPI, Request
from common_libs import environment
import uvicorn
# import requests

import logging
wgo_logger = logging.getLogger('system_service')
_env = environment()

try:
    from setproctitle import setproctitle
    setproctitle('WGO-System-Service')
except ImportError:
    pass


def vacuum_journal(size=25):
    cmd = 'journalctl --rotate'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    cmd = f'journalctl --vacuum-size={size}M'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    # print(result)
    return result


def free_memory():
    cmd = 'free && sync && echo 3 > /proc/sys/vm/drop_caches && free'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    # print(result)
    return result


def restart_browser():
    cmd = 'systemctl restart kiosk'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    wgo_logger.error(f'Restart browser result: {result}')
    return result


def restart_system():
    cmd	= 'reboot'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result


def memory_usage(freeup=True, limit=70, reboot_limit=10):
    '''
                  total        used        free      shared  buff/cache   available
    Mem:        1001760      571256      140724      122436      289780      200264
    Swap:             0           0           0'''
    test = '''              total        used        free      shared  buff/cache   available
    Mem:        1001760      571256      140724      122436      289780      200264
    Swap:             0           0           0'''

    cmd = 'free'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    # print(result)
    if result.returncode == 0:
        # Parse stdout
        stdout = result.stdout.decode('UTF-8')
    else:
        # Error
        print(result.stderr)

    for line in stdout.split('\n'):
        if line.strip().startswith('Mem:'):
            data = line.strip().split('    ')
            available = int(data[-1].strip())
            wgo_logger.debug(f'{time.time()}, {available}, {available / 1024}, {limit}')
            if (available / 1024) < limit:
                wgo_logger.error('Freeing Memory')
                free_memory()
                vacuum_journal()
                # Ballistic, will potentially fail if display is off
                # restart_browser()
            if (available / 1024) < reboot_limit:
                restart_system()


def storage_usage(limit=20):
    '''Check storage levels on various partitions.'''
    return

class SystemHandler(object):
    '''Handles all System maintenance tasks and watchdog functionality.'''
    def __init__(self, cfg):
        '''Sets up service handler.'''
        self.cfg = cfg
        self.setup()

    def setup(self):
        self.running = True

    def main_loop(self):
        wgo_logger.info('Starting WGO System main thread loop')
        loop_interval = self.cfg.get('mainloop_interval', 10)
        try:
            while True:
                if self.running is False:
                    break

                # Do something
                # Check memory and free if needed
                mem_check = memory_usage(
                    limit=self.cfg.get('cache_clearing_limit', 50)
                )
                # Check storage level
                storage_check = storage_usage()

                # Check Niceness and adjust as needed
                # can service
                # ui service
                # ssh
                # What else ?

                asyncio.sleep(loop_interval)
        except KeyboardInterrupt:
            wgo_logger.info('Exiting System Service...')
            return

class SystemBackgroundRunner:
    def __init__(self, cfg: dict):
        self.config = cfg
        self.handler = SystemHandler(self.config)
        self.th = threading.Thread(target=self.handler.main_loop, args=[])

    async def run_main(self):
        self.th.start()
        print('System Service Loop started')

    async def stop(self):
        self.handler.running = False
        self.th.join()


CFG = {
    # Limit when cache is cleared, as available memory goes below
    # BUG: This is needed to avoid HMI running out of memory due to caching
    'cache_clearing_limit': 60,
    # Interbal for main loop
    'mainloop_interval': 10,
}
runner = SystemBackgroundRunner(CFG)


# Set up FastAPI and read
app = FastAPI()

@app.get('/')
async def status():
    return {
        'result': 'OK',
        'version': '',
        'name': '',
        'uptime': ''
    }


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(runner.run_main())

@app.on_event('shutdown')
async def shutdown_event():
    await runner.stop()


if __name__ == "__main__":

    WGO_SERVICE_PORT = os.environ.get('WGO_SERVICE_SYSTEM_PORT', 8003)
    BIND_ADDRESS = _env.bind_address
    uvicorn.run(
        'system_service:app',
        host=BIND_ADDRESS,
        port=WGO_SERVICE_PORT,
        reload=True
    )
