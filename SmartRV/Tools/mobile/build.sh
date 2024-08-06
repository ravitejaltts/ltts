#!/bin/bash

# Fail if any command fails
set -e

# Set env vars
export PI_SMART_RV_PATH="/opt/smartrv"
export PI_FRONTEND_PATH="/opt/smartrv-frontend"
export PI_STORAGE_PATH="/storage/wgo"

# Make all script paths relative
SCRIPT_PATH=$(dirname "$(realpath $0)")
echo "Running in $SCRIPT_PATH"
cd $SCRIPT_PATH

# Check the environment
./check_env.sh

help() {
    echo ""
    echo "Usage: $0 -h -a -p"
    echo "\t-h help"
    echo "\t-a build all"
    echo "\t-p pull"
    exit 1
}

export build_all=false
pull=false

while getopts hap opt
do
    case "$opt" in
        h)
            help
            ;;
        a)
            build_all=true
            ;;
        p)
            pull=true
            ;;
        ?)
            help
            ;;
    esac
done

# Always clean
./clean.sh

# Pull, if flag set
if [[ "$pull" = true ]]
then
    echo "Pulling SmartRV..."
    ./pull.sh -r "$PI_SMART_RV_REPO_PATH"

    if [[ "$build_all" = true ]]
    then
        echo "Pulling Frontend..."
        ./pull.sh -r "$PI_FRONTEND_REPO_PATH"
    fi
fi

# Build services
./build_services.sh

# Build frontend, if flag set
if [[ "$build_all" = true ]]
then
    ./build_frontend.sh
fi

# Deploy all
./deploy.sh