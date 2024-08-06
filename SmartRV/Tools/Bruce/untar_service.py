## Untar the IOT service
## pass in the name of the tar.gz and it will go into a dir of the same name   
# ex: python untar_srvice.py 'iot_0.1.01' 

import tarfile
import sys
import subprocess


def extract_pkg(i_name: str, i_version, from_dir = None, to_dir = None) -> str:
    '''Extract the package given the name and version.'''
    result = 'Failed'
    if from_dir == None:
        command = f'gpg --batch --yes --pinentry-mode loopback --passphrase=Winnconnect2023 {i_name}_{i_version}.tar.gz.gpg'
    else:
        command = f'gpg --batch --yes --pinentry-mode loopback --passphrase=Winnconnect2023 {from_dir}/{i_name}_{i_version}.tar.gz.gpg'
 
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    print('OTA -gpg returned:',process.returncode)

    if process.returncode == 0:
        # open file
        file = tarfile.open(f'{i_name}_{i_version}.tar.gz')
        
        # print file names
        print(file.getnames())
        
        # extract files
        if to_dir == None:
            file.extractall(f'./{i_version}')
        else:
            file.extractall(f'{to_dir}')
            
        # close file
        file.close()
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

