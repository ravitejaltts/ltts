# Packager code - better if run in Linux or osx

import tarfile
import re
import tarfile
import sys
import subprocess
import os
import json
import yaml

VERSION_NOT_FOUND = "0.0.1"

def get_package_version( i_name) -> str:
    '''Give a service name (dir) find and return the version'''
    try:
        version = re.search(
            '^__version__\s*=\s*"(.*)"',
            open(f'{i_name.lower()}/wgo_{i_name.lower()}.py').read(),
            re.M
            ).group(1)
    except Exception as err:
        #print(f"get package version  err: {err}")
        #print(f"Working dir for err: {os.getcwd()}")
        #TODO What type of version to keep in these other files?
        return  VERSION_NOT_FOUND

    return version


#by name and similar directory
services = { "modules":
    {
    "iot_service",
    "can_service",
    "data",
    "common_libs",
    "hmi_tools",
    "kiosk_config",
    "system_service",
    "main_service",
    "bt_service",
    "update_service"
    }
}


def get_versions(i_dir):
    '''Switch to the top level directory passed in to open the version file'''

    save_dir = os.getcwd()
    os.chdir(i_dir)

    try:
        vj = {}

        with open("version.json", 'r') as version_file:
            vj = json.loads(version_file.read())

        print(f'{json.dumps(vj, indent=4)}')

        for name in services['modules']:
            version = get_package_version(name)

            # print(f'Service {name}, version {version}')
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
    except Exception as err:
        os.chdir(save_dir)
        raise



def update_yml(i_dir, newversions, increment_frontend = False):

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
    smartrv['variables']['commonLibsModuleVersion'] = newversions['modules']['common_libs']
    smartrv['variables']['updateServiceModuleVersion'] = newversions['modules']['update_service']
    if increment_frontend is True:
        plusOne = smartrv['variables']['smartrvFrontendModuleVersion'].split('.')
        plusOne[2] = str((int(plusOne[2]) + 1))
        plusOne = '.'.join(plusOne)
        smartrv['variables']['smartrvFrontendModuleVersion'] = plusOne

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


    incFront = False

    if n >= 2:
        incFront = (sys.argv[1] == "--Increment_FrontEnd")


    try:
        from_dir = ".."
        new_v = get_versions(from_dir)
    except Exception as err:
        # print(err)
        from_dir = "."
        new_v = get_versions(from_dir)



    to_dir = os.path.join(from_dir, 'Pipelines', 'variables')

    update_yml(to_dir, new_v, incFront)

    #rel_version = new_v['version']
    #print(f'Release found: {rel_version}')
    #print(f'Versions found: {new_v}')
    try:

        with open(os.path.join(to_dir, 'smartrv_version_variables.yml'), 'r') as file:
            print(file.read())
    except Exception as err:
        print(err)
