#!/bin/bash

# SET the PYTHONPATH variable globally somewhere else to find bt_service and other libs

export WGO_BLD=/smartrv
export WGO_HOME_DIR=/opt$WGO_BLD
export PYTHONPATH=$WGO_HOME_DIR:$PYTHONPATH

export WGO_FRONTEND_DIR=/opt/smartrv-frontend
export WGO_USER_STORAGE=/storage/wgo
export WGO_MAIN_HOST=http://localhost
export WGO_BIND_ADDR=0.0.0.0
export WGO_MAIN_PORT=8000
export WGO_CAN_PORT=8001
export WGO_IOT_SERVICE_PORT=8002
export WGO_BT_PORT=8005


cd $WGO_HOME_DIR
cd bt_service

python3 wgo_bt_service.py
