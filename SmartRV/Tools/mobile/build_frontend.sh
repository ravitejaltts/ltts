#!/bin/bash

# Fail if any command fails
set -e

printf "\n\nBuilding frontend...\n"
cd "$PI_FRONTEND_REPO_PATH/client"

echo "Installing node packages..."
npm install

echo "Building..."
npm run build

echo "Cleaning up..."
find ./build/ -type d -name .pytest_cache -prune -exec rm -rf {} \;
find ./build/ -type d -name __pycache__ -prune -exec rm -rf {} \;
find ./build/ -type f -name _"*.md" -prune -exec rm -rf {} \;