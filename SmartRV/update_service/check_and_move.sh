#!/bin/bash

. ./functions.sh

# Check if the OTA script needs to update
. ./check_script.sh

if [ $? -ne 0 ]; then
    log_message "check_script failed!"
    exit 1
fi

# Check if the latest_bld file is present
BLD_NAME="${WGO_USER_STORAGE}/latest_bld"
OK_NAME="${WGO_USER_STORAGE}/OK"

if [ ! -f "$OK_NAME" ]; then
    exit 0
else
    # remove the OK file - pass or fail we run once
    rm -f "$OK_NAME"
    if [ $? -ne 0 ]; then
        log_message "Failed to remove OK file?"
    fi
fi

# OK file means we have work to do
# Adding this new script file so that if and OTA is updating
# from the previous version it will not have old script data
. ./local_worker.sh
