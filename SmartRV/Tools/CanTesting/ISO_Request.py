import csv
import subprocess
import time

PAUSE = 0.05


def emit_iso_request(id_: int):
    msg = f'{id_:06X}'
    print(msg)
    cmd = f'cansend canb0s0 19EA0044#{msg}'
    print('\t', subprocess.run(cmd, shell=True, capture_output=True))


for i in range(131071):
    emit_iso_request(i)
    time.sleep(PAUSE)
