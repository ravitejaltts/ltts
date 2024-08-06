## Untar the IOT service
## pass in the name of the tar.gz and it will go into a dir of the same name
# ex: python untar_srvice.py 'iot_0.1.01'

import tarfile
import sys
import subprocess
import os

def extract_pkg(i_name: str, from_dir = None, to_dir = None) -> str:
    '''Extract the package given the name and version.'''
    result = 'Failed'
    if from_dir == None:
        name_n_path = i_name
    else:
        os.chdir(from_dir)
        name_n_path = i_name

    command = f'gpg --homedir={from_dir} --batch --yes --pinentry-mode loopback --passphrase=Winnconnect2023 {name_n_path}.tar.gz.gpg'

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    print('OTA -gpg returned:',process.returncode)
    #print('OTA - cwd:',os.getcwd())

    if process.returncode == 0:
        # open file
        file = tarfile.open(f'{name_n_path}.tar.gz')

        # print file names
        print(file.getnames())

        # extract files
        if to_dir == None:
            file.extractall(from_dir)
        else:
            file.extractall(to_dir)

        # close file
        file.close()
        os.remove(f'{name_n_path}.tar.gz')
        result = 'Success'
    else:
        print("Failed to extract files")

    return result


if __name__ == '__main__':

    pkg = sys.argv[1]
    ver = sys.argv[2]

    rs = extract_pkg(pkg, ver)
    if rs == 'Success':
        print(f'The archive extracted was: {pkg} version: {ver}')

