#!/bin/bash

get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

LIBRARYPATH=$(get_abs_filename ".")

PYTHONPATH="$LIBRARYPATH:$PYTHONPATH"
export PYTHONPATH
echo $PYTHONPATH

WGO_MAIN_DEBUG=0
export WGO_MAIN_DEBUG

cd main_service
pip3 install poetry
poetry install

poetry run python wgo_main_service.py
