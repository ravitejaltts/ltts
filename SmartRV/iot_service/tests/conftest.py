import os
import pytest

from fastapi.testclient import TestClient
from iot_service.wgo_iot_service import app

import signal
# import threading
# import time
capp = None

@pytest.fixture(scope="session")
def client():
    global capp

    if capp is None:
        with TestClient(app) as c:
            print('Creating new instance of iot app')
            capp = c
            yield c

    yield capp


def pytest_sessionfinish(session, exitstatus):
    """Called after the whole test run finished."""
    if exitstatus == 2:
        print("Caught exit code 2, handling it.")
        session.exitstatus = 0
    else:
        session.exitstatus = exitstatus


@pytest.fixture(autouse=True)
def handle_sigint():
    original_sigint_handler = signal.getsignal(signal.SIGINT)

    def sigint_handler(signum, frame):
        print("SIGINT received. Performing cleanup...")
        # Perform any necessary cleanup here
        pytest.exit("Exiting due to SIGINT")

    signal.signal(signal.SIGINT, sigint_handler)

    yield

    signal.signal(signal.SIGINT, original_sigint_handler)


def rename_file(old_name, new_name):
    try:
        ffrom = os.path.join(os.environ.get("WGO_USER_STORAGE", ""), old_name)
        fto = os.path.join(os.environ.get("WGO_USER_STORAGE", ""), new_name)

        if os.path.exists(ffrom):
            if not os.path.exists(fto):
                os.rename(ffrom, fto)
                print(f"Renamed {ffrom} to {fto}")
            else:
                print(f"Already saved {ffrom} to {fto}")
                print(f"Removing {ffrom}")
                os.remove(ffrom)
        else:
            print(f"The file {ffrom} does not exist.")
    except Exception as e:
        print(f"NO exisiting file: {ffrom}")



def copy_file(old_name, new_name):
    try:
        ffrom = os.path.join(os.environ.get("WGO_USER_STORAGE", ""), old_name)
        fto = os.path.join(os.environ.get("WGO_USER_STORAGE", ""), new_name)

        if os.path.exists(ffrom):
            if not os.path.exists(fto):
                os.copy(ffrom, fto)
                print(f"Replaced {ffrom} to {fto}")

        else:
            print(f"The file {ffrom} does not exist.")
    except Exception as e:
        print(f"NO exisiting file: {ffrom}")



@pytest.hookimpl(hookwrapper=True)
def pytest_sessionstart(session):
    # will execute as early as possibledef test_setup_for_WM524T(client):
    print('Rename Iot_config.ini to store it.')
    rename_file('Iot_config.ini', 'Iot_config.sav')

    print('Rename vin.txt to store it.')
    rename_file('vin.txt', 'vin.sav')

    print('Rename UI_config.ini to store it.')
    rename_file('UI_config.ini', 'UI_config.sav')
    yield
    print('Cleanup')


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Cleanup a testing directory once we are finished."""
    def restore_inis():
        print('Need to restore the ini files.')
        copy_file('vin.sav', 'vin.txt')
        copy_file('UI_config.sav', 'UI_config.txt')
        copy_file('Iot_config.sav', 'Iot_config.txt')
        yield

    request.addfinalizer(restore_inis)
