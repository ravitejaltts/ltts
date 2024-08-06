#!/bin/bash

# __version__ = "0.3.0"

. ./functions.sh

# Check if the latest_bld file is present
BLD_NAME="${WGO_USER_STORAGE}/latest_bld"
OK_NAME="${WGO_USER_STORAGE}/OK"

# Check when IOT ends - is an OTA update waiting?
./check_and_move.sh
cnm=$?
if [ $cnm -ne 0 ]; then
        log_message "Error: Failed exit code $cnm from check and move."
        systemctl restart smartrv-kiosk
fi
# Align the disk
sync

# Restart IOT if check and move did not reboot the system
log_message "OTA service done."

exit 0
