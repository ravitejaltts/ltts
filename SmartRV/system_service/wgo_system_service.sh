#!/bin/bash

if [[ -z "${WGO_SERVICE_SYSTEM_PORT}" ]]; then
  PORT=8003
else
  PORT="${WGO_SERVICE_SYSTEM_PORT}"
fi


if [[ -z "${WGO_HOME_DIR}" ]]; then
  DIR="/home/guf/"
else
  DIR="${DIR}"
fi

cd $DIR
cd system_service

python3 system_service.py $PORT
