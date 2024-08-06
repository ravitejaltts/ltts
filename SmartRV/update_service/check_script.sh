#!/bin/bash

# This file checks our script which is only on the local machine
# and compare it to the downloaded script
# if the downloaded script from the last OTA is newer
# it will replace the local script before we execute.

. ./functions.sh

OK_NAME="${WGO_USER_STORAGE}/OK"


# Define the paths to the scripts
ota_script="./ota_worker.sh"
local_script="./local_worker.sh"

# Check if the two scripts are different
if ! cmp -s "$ota_script" "$local_script"; then
    if [ ! -f "$OK_NAME" ]; then # CHeck if user has given permission
        exit 0 # If no permission then exit
    fi
    # Remount /data directory as writable
    mount -o remount,rw /
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to remount / as writable."
        exit 1
    fi
    # Copy ota_script to local_script if they are different
    cp "$ota_script" "$local_script"
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to copy the script."
        exit 2
    fi
    # be sure it is executable
    chmod +x "$local_script"
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to make the script executable."
        exit 3
    fi
    log_message "Success: copied new local_worker.sh!"
fi

