#!/bin/bash

# pip3 install poetry


# Build and package python
# Package and clean Python services
echo "B1"
source ../venv/bin/activate
python3 package_build.py ../../build
cd ../../
echo "B2"
find ./build/ -type d -name .pytest_cache -prune -exec rm -rf {} +;
echo "B3"
find ./build/ -type d -name __pycache__ -prune -exec rm -rf {} +;
echo "B4"
find ./build/ -type f -name '*.md' -prune -exec rm -f {} +;
echo "B5"
find ./build/ -type d -name '*venv*' -prune -exec rm -rf {} +;
find ./build/ -type d -name 'tests' -prune -exec rm -rf {} +;
find ./build/ -type d -name '.DS_Store' -prune -exec rm -f {} +;


echo "B6 - FRONTEND"
# Build Frontend
cd Frontend/client

if [[ "$1" = "api" ]]; then
    # Copy the files to
    cp -R ./build/* ../../build/main_service/base_static/
    cd ../../build
    ./launch_local.sh
    exit
fi

echo "B7 - Installing Frontend Dependencies"
npm i
echo "B8 - Running Frontend Build"
npm run build

# TODO: Remove Frontend
echo "B9 - Copy Frontend Build to base_static folder"
# Copy the files to
cp -R ./build/* ../../build/main_service/base_static/
