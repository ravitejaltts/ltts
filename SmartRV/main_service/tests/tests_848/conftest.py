import os

import pytest



# @pytest.hookimpl(hookwrapper=True)
# def pytest_sessionstart(session):
#     # will execute as early as possibledef test_setup_for_WM524T(client):
#     print('Setup FloorPlan')
#     print("Changing Floorplan to 848EC")
#     with open(os.environ.get('WGO_USER_STORAGE') + 'UI_config.ini', 'w') as ini_file:
#         ini_file.write(
#             '''[Vehicle]
# floorplan = 848EC'''
#         )
#     yield
#     print('Cleanup')


# @pytest.hookimpl(hookwrapper=True)
# def pytest_collection_modifyitems(items):
#     print("Changing Floorplan to 848EC")

#     with open(os.environ.get('WGO_USER_STORAGE') + 'UI_config.ini', 'w') as ini_file:
#         ini_file.write(
#             '''[Vehicle]
# floorplan = 848EC'''
#         )
