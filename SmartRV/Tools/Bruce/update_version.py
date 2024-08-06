# Packager code - better if run in Linux or osx

import tarfile
import re
import tarfile
import sys
import subprocess
import os
import json
from common_libs import environment


from untar_service import extract_pkg


VERSION_NOT_FOUND = "0.0.1"

def get_package_version( i_name) -> str:
    '''Give a service name (dir) find and return the version'''
    try:
        version = re.search(
            '^__version__\s*=\s*"(.*)"',
            open(f'{i_name.lower()}/{i_name.lower()}.py').read(),
            re.M
            ).group(1)
    except Exception as err:
        #print(f"get package version  err: {err}")
        #print(f"Working dir for err: {os.getcwd()}")
        #TODO What type of version to keep in these other files?
        return  VERSION_NOT_FOUND

    return version


_env = environment()


#by name and similar directory
services = { "modules":
    {
    "iot_service",
    "can_service",
    "data",
    "hmi_tools",
    "kiosk_config",
    "system_service",
    "main_service",
    "bt_service"
    }
}

_env = environment()

def get_versions(i_dir):
    '''Switch to the top level directory passed in to open the version file'''

    save_dir = os.getcwd()
    os.chdir(i_dir)

    vj = {}

    with open("version.json", 'r') as version_file:
        vj = json.loads(version_file.read())

    print(f'{json.dumps(vj, indent=4)}')

    for name in services['modules']:
        version = get_package_version(name)

        print(f'Service {name}, version {version}')
        if version == None or name == 'hal':
            pass;
        else:
            try:
                vj['modules'][f'{name}'] = version
            except:
                pass # not for now

    with open("version.json", 'w') as version_file:
        version_file.write(json.dumps(vj, indent=4))

    os.chdir(save_dir)
    return vj


import yaml

def update_yml(i_dir, newversions):

    save_dir = os.getcwd()
    os.chdir(i_dir)

    # Reading the existing YAML file
    with open('smartrv_version_variables.yml', 'r') as file:
        smartrv = yaml.safe_load(file)

    # Modifying the values in the dictionary
    smartrv['variables']['smartRvVersion'] = newversions['version']
    smartrv['variables']['dataModuleVersion'] = newversions['modules']['data']
    smartrv['variables']['hmiToolsModuleVersion'] = newversions['modules']['hmi_tools']
    smartrv['variables']['iotServiceModuleVersion'] = newversions['modules']['iot_service']
    smartrv['variables']['systemServiceModuleVersion'] = newversions['modules']['system_service']
    smartrv['variables']['uiServiceModuleVersion'] = newversions['modules']['main_service']
    smartrv['variables']['canServiceModuleVersion'] = newversions['modules']['can_service']
    smartrv['variables']['btServiceModuleVersion'] = newversions['modules']['bt_service']

    # Writing the updated dictionary back to the YAML file
    with open('smartrv_version_variables.yml', 'w') as file:
        yaml.safe_dump(smartrv, file, default_flow_style=False)

    os.chdir(save_dir)



if __name__ == '__main__':

    # total arguments
    n = len(sys.argv)
    print("Total arguments passed:", n)

    # Arguments passed
    print("\nName of Python script:", sys.argv[0])

    print("\nArguments passed:", end = " ")
    for i in range(1, n):
        print(sys.argv[i], end = " ")

    # Addition of numbers
    Sum = 0
    # Using argparse module
    for i in range(1, n):
        Sum += int(sys.argv[i])



    from_dir = ".."

    new_v = get_versions(from_dir)

    to_dir = os.path.join(from_dir, 'Pipelines', 'variables')
    update_yml(to_dir, new_v)

    print(f'Versions found: {new_v}')
    rel_version = new_v['version']
    print(f'Release found: {rel_version}')
