# Introduction 
This repository contains all Coach HMI related code except Frontend and Supporting tooling.

# Getting Started
## MACOS
1. Install brew package manager: https://brew.sh/

        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Install Python 3.8 and nodejs

        brew install python@3.8
        brew install node
    
3. Create SSH key: https://docs.microsoft.com/en-us/azure/devops/repos/git/use-ssh-keys-to-authenticate?view=azure-devops#step-1-create-your-ssh-keys

4. Add SSH key to Azure DevOps:
    [SSH Settings Devops](https://dev.azure.com/WGO-Web-Development/_usersSettings/keys)

    Follow [Azure SSH Setup](https://docs.microsoft.com/en-us/azure/devops/repos/git/use-ssh-keys-to-authenticate?view=azure-devops)

5. Create a new folder to hold the code required and open a terminal to it (e.g. use CMD-Shift -> Terminal)

        mkdir WinnConnect
        cd WinnConnect

6. Clone Frontend code and SmartRV/WinnConnect code repos (in above folder)

        git clone git@ssh.dev.azure.com:v3/WGO-Web-Development/SmartRV/Frontend
        git clone git@ssh.dev.azure.com:v3/WGO-Web-Development/SmartRV/SmartRV


## Windows
Make sure you have administrative rights to install the rquired SW
1. Install Python 3.8
Download latest Python 3.8 from [Python](https://www.python.org/downloads/windows/). Versions 3.9 and 3.10 may also work locally, but are currently not used on the HMI code. Ensure that you enable 'ADD to PATH' during installation.

2. Install Node.js LTS (16 as of writing this)
https://nodejs.org/en/download

3. Create SSH key: https://docs.microsoft.com/en-us/azure/devops/repos/git/use-ssh-keys-to-authenticate?view=azure-devops#step-1-create-your-ssh-keys

4. Add SSH key to Azure DevOps:
    [SSH Settings Devops](https://dev.azure.com/WGO-Web-Development/_usersSettings/keys)

    Follow [Azure SSH Setup](https://docs.microsoft.com/en-us/azure/devops/repos/git/use-ssh-keys-to-authenticate?view=azure-devops)

5. Install git

6. Create new folder

7. Clone Frontend code and SmartRV/WinnConnect code repos (in above folder)

        git clone git@ssh.dev.azure.com:v3/WGO-Web-Development/SmartRV/Frontend
        git clone git@ssh.dev.azure.com:v3/WGO-Web-Development/SmartRV/SmartRV




# Build and Test
1. Go to Frontent folder and install packages
        
        cd Frontend/client
        npm install

1. Go to SmartRV setup folder

        cd ..
        cd SmartRV/setup

2. Run 'build_all.sh'

        ./build_all.sh
    
    or to build an run, perform

        ./build_all.sh run


This should create a build folder within WinnConnect folder that can be used for testing

        cd ../../build

9. Run the launch_local.sh script, you might have to accept popups to allow incoming connections

        ./launch_local.sh  

10. Open Chrome (Chrome is specifically useful as it is the embedded browser) or another browser and navigate to http://localhost:8000


# Further reading
## Wiki
Find more information on the software architecture and decisions here: [Software Architecture](https://dev.azure.com/WGO-Web-Development/SmartRV/_wiki/wikis/SmartRV.wiki/508/Software-Architecture)