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
from tar_service_version import (
    pk_service,
    VERSION_NOT_FOUND,
    get_package_version
)
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
    "common_libs"
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
        try:
            vj['modules'][f'{name}'] = version
        except:
            pass # not for now

    with open("version.json", 'w') as version_file:
        version_file.write(json.dumps(vj, indent=4))

    os.chdir(save_dir)
    return vj



def check_dirs(i_dir):
     pass



def check_dir(i_dir):
    #print(f'CWD = {os.getcwd()}')
    if not os.path.exists(i_dir):
        os.mkdir(i_dir)


def check_dir_structure(i_ver, full_ver, i_dir):

    save_dir = os.getcwd()
    os.chdir(i_dir)
    check_dir(_env.storage_file_path())
    check_dir(_env.storage_file_path('vdt'))
    check_dir(_env.storage_file_path(f'vdt/{i_ver}'))
    check_dir(_env.storage_file_path(f'vdt/modules'))
    for module in full_ver['modules']:
        check_dir(_env.storage_file_path(f'vdt/modules/{module}'))
        m_ver = full_ver['modules'][f'{module}']
        check_dir(_env.storage_file_path(f'vdt/modules/{module}/{m_ver}'))

    os.chdir(save_dir)


def build_meta(i_ver, full_ver, i_dir):
    meta_info = {
        "deviceType": "vdt",
        "version": i_ver,
        "name": "meta.json",
        "type": "meta",
        "container": "deviceType",
        "files": []
    }
    for idx, module in enumerate(full_ver['modules']):
        m_ver = full_ver['modules'][f'{module}']
        fname = f'{module}_{m_ver}.tar.gz.gpg'
        fstat = os.stat(_env.storage_file_path(f'vdt/modules/{module}/{m_ver}/{fname}'))
        f_info = {
            "name": fname,
            "description": "HMI software",
            "module": module,
            "version": m_ver,
            "type": "bundle",
            "size": fstat.st_size,
            "container": "deviceType",
            "install": "NA",
            "ordinal": idx
        }
        meta_info["files"].append(f_info)

    return meta_info



if __name__ == '__main__':
    from_dir = "SmartRV"

    new_v = get_versions(from_dir)

    print(f'Versions found: {new_v}')
    rel_version = new_v['version']
    print(f'Release found: {rel_version}')

    check_dir_structure(rel_version, new_v, from_dir)

    save_dir = os.getcwd()
    os.chdir(from_dir)

    for module in services['modules']:
        m_ver = new_v['modules'][f'{module}']
        ark = pk_service(module, './', _env.storage_file_path(f'vdt/modules/{module}/{m_ver}'))
        print(f'The archive created is: {ark}')

    r = build_meta(rel_version, new_v, from_dir)

    #print(f"Done {json.dumps(r, indent=4)}")
    fname = _env.storage_file_path(f'vdt/{rel_version}/meta.json')
    with open(fname, 'w', encoding='utf-8') as metafile:
        metafile.write(json.dumps(r, indent=4))

    os.chdir(save_dir)
