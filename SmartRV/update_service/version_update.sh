#!/bin/bash

. ./functions.sh

LOGFILE="${WGO_USER_STORAGE}/logs/ota_service.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGFILE"
}

# Read the version from the latest_bld file
version=$(cat "$WGO_USER_STORAGE/latest_bld" | grep -o 'bld_.*' | sed 's/bld_//')

if [ -z "$version" ]; then
    log_message "Error: No valid version found in latest_bld file."
    exit 1
fi

# Use sed to update the JSON file
# This sed command looks for "version": followed by any non-comma characters and replaces it with "version": "new_version",
sed -i.bak "s/\(\"version\": \)[^,]*,/\1\"$version\",/" "$WGO_HOME_DIR/version.json"

log_message "Version updated to: $version"
