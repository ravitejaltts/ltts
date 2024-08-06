#!/bin/bash
# Set and check environment variables

# Fail if any command fails
set -e

echo "PI_SMART_RV_PATH: $PI_SMART_RV_PATH"
echo "PI_FRONTEND_PATH: $PI_FRONTEND_PATH"
echo "PI_STORAGE_PATH: $PI_STORAGE_PATH"

# Check env vars
if [[ -z $PI_SMART_RV_REPO_PATH ]]
then
    echo "PI_SMART_RV_REPO_PATH is missing. Please add this to your shell environment variables."
    exit 1
else
    echo "PI_SMART_RV_REPO_PATH: $PI_SMART_RV_REPO_PATH"
fi

if [[ -z $PI_FRONTEND_REPO_PATH ]]
then
    echo "PI_FRONTEND_REPO_PATH is missing. Please add this to your shell environment variables."
    exit 1
else
    echo "PI_FRONTEND_REPO_PATH: $PI_FRONTEND_REPO_PATH"
fi