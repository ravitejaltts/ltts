#!/bin/bash
# Clean existing files and build caches

# Fail if any command fails
set -e

printf "\n\nCleaning...\n"

# Remove current version of services
echo "Cleaning '$PI_SMART_RV_PATH'"
rm -rf "$PI_SMART_RV_PATH/"*

# Remove current version of frontend, if flag is set
if [[ "$build_all" = true ]]
then
    echo "Cleaning '$PI_FRONTEND_PATH'"
    rm -rf "$PI_FRONTEND_PATH/"*
fi

# Clean storage files
echo "Cleaning '$PI_STORAGE_PATH'"
rm -f "$PI_STORAGE_PATH/wgo_user.db"

# Clean build folders
smart_rv_build_path="$PI_SMART_RV_REPO_PATH/setup/build"
echo "Cleaning '$smart_rv_build_path'"
rm -rf "$smart_rv_build_path/"*

frontend_build_path="$PI_FRONTEND_REPO_PATH/client/build"
echo "Cleaning '$frontend_build_path'"
rm -rf "$frontend_build_path/"*

echo "Clean complete"