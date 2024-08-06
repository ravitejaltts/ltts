#!/bin/bash

# Fail if any command fails
set -e

printf "\n\nBuilding services...\n"
cd "$PI_SMART_RV_REPO_PATH/setup"

# Package and clean python services
python3 package_build.py ./build

# Clean up files
echo "Cleaning up..."
find ./build/ -type d -name .pytest_cache -prune -exec rm -rf {} \;
find ./build/ -type d -name __pycache__ -prune -exec rm -rf {} \;
find ./build/ -type f -name _"*.md" -prune -exec rm -rf {} \;
find ./build/ -type d -name .venv -prune -exec rm -rf {} \;

echo "Build services completed"