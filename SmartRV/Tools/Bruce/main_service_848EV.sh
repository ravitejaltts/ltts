#!/bin/bash

if [[ -z "${WGO_SERVICE_UI_PORT}" ]]; then
  PORT=8000
else
  PORT="${WGO_SERVICE_UI_PORT}"
fi

export PYTHONPATH='/home/bruce/SmartRV'

cd ~/SmartRV/main_service
cd main_service

# export PYTHONPATH=$PYTHONPATH:/home/guf/pyPackages
# export PYTHONPATH=$PYTHONPATH:/home/guf/

export WGO_BIND_ADDR=0.0.0.0

sed -i -e 's/WM524T/848EC/g' /storage/UI_config.ini

python3 wgo_main_service.py $PORT
