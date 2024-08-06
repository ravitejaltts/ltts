

import tarfile
import re
import tarfile
import sys
import subprocess
import os

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


def pk_service(i_name: str, from_dir = "./", to_dir = "./") -> str:
    '''Package the service input - return the package name'''
    result = "NA"

    try:
        version = get_package_version(i_name)

        archive_name = f"{i_name}_{version}"

        if i_name == 'data':
            with tarfile.open(archive_name + '.tar.gz', mode='w:gz') as archive:
                archive.add(f'{from_dir}/data/Default_Config.json')
                archive.add(f'{from_dir}/data/VANILLA_ota_template.json')
        else:
            with tarfile.open(archive_name + '.tar.gz', mode='w:gz') as archive:
                archive.add(f'{from_dir}/{i_name}',filter=lambda x: None if ('__pycache__' in x.name) else x,  recursive=True)

        command = f'gpg -c --yes --pinentry-mode loopback --passphrase=Winnconnect2023 {archive_name}.tar.gz'

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()

        if to_dir != None:
            os.replace(f'{archive_name}.tar.gz.gpg', f'{to_dir}/{archive_name}.tar.gz.gpg')

        if process.returncode == 0:
            os.remove(f'{archive_name}.tar.gz')
            result = f'{archive_name}.tar.gz.gpg'
        else:
            print('OTA -gpg returned:',process.returncode)
    except Exception as err:
        print(f" pk_service err: {err}")
        print(f"Working dir for pk_service err: {os.getcwd()}")


    return result

if __name__ == '__main__':

    service = sys.argv[1]

    ark = pk_service(service)
    print(f'The archive created is: {ark}')
