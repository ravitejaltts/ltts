#!/bin/bash

# Fail if any command fails
set -e

printf "\n\nDeploying...\n"

# Copy services
echo "Deploying SmartRV build..."
cp -r "$PI_SMART_RV_REPO_PATH/setup/build"/* "$PI_SMART_RV_PATH/"
cp -r "$PI_SMART_RV_REPO_PATH/libpygozer" "$PI_SMART_RV_PATH/"

# Copy frontend, if flag is set
if [[ "$build_all" = true ]]
then
    echo "Deploying Frontend build..."
    cp -r "$PI_FRONTEND_REPO_PATH/client/build"/* "$PI_FRONTEND_PATH/"
fi

# Restart
echo "Restarting services..."
sudo systemctl restart smartrv-main
sudo systemctl restart smartrv-iot
sudo systemctl restart smartrv-bluetooth

# TODO: Fix the dependency causing this to fail
#sudo systemctl restart smartrv-can

echo "Deploy complete"
