#!/bin/bash

# Package and clean Python services
poetry run python package_build.py ../../build
cd ../../
find ./build/ -type d -name .pytest_cache -prune -exec rm -rf {} \;
find ./build/ -type d -name __pycache__ -prune -exec rm -rf {} \;
find ./build/ -type f -name _"*.md" -prune -exec rm -rf {} \;

# Build Frontend
cd Frontend/client

npm run build
