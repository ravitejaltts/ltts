#!/bin/bash

set -a
source /etc/default/smartrv
set +a

LOGFILE="${WGO_LOG_PATH}/ota_service.log"
# always log time in UTC
log_message() {
    echo "$(date --utc) - $1" | tee -a "$LOGFILE"
}

last_error() {
  echo "$(date --utc) - $1" > "${WGO_LOG_PATH}/ota_exit_error.txt"
}

# Function to get the latest modification date of .json files
get_latest_modification_date() {
    local latest_date=$(find . -type f -name '*.json' -printf '%T@ %p\n' | sort -n | tail -1 | awk '{print $1}')
    if [ -n "$latest_date" ]; then
        latest_date=$(date -d @$latest_date +%Y-%m-%d)
        # log_message "Latest date identified: $latest_date"
        echo $latest_date
    else
        log_message "Error: Could not determine the latest modification date."
        exit 1
    fi
}

# Function to check for leftovers
check_leftovers() {
    local latest_date=$1
    local leftovers=$(find . -type f -name '*.json' ! -newermt "$latest_date")

    if [ -n "$leftovers" ]; then
        log_message "Error: There are old .json files left in the directory:"
        echo "$leftovers" >> /var/log/storage_cleaner.log
    fi
}


# Function to remove files that start with a dash
remove_dash_files() {
    find . -type f -name '-*' -exec rm -f -- {} +
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to remove files starting with a dash."
    fi
}

# Function to remove old .json files based on the latest modification date
remove_old_files() {
    # Check if a directory is passed as an argument
    if [ -z "$1" ]; then
        log_message "[remove_old_files] missing <directory> parameter"
        return 1
    fi

    # Get the directory from the first argument
    local directory=$1

    # Check if the provided argument is a directory
    if [ ! -d "$directory" ]; then
        log_message "[remove_old_files] Error: $directory is not a directory"
        return 1
    fi

    # Find the latest date of the files in the directory
    latest_date=$(find "$directory" -type f -printf "%TY-%Tm-%Td\n" | sort -u | tail -n 1)

    # If no files are found, exit
    if [ -z "$latest_date" ]; then
        echo "No files found in $directory"
        return 0
    fi

    # Find and remove files that are older than the latest date
    find "$directory" -type f -printf "%TY-%Tm-%Td %p\n" | awk -v latest_date="$latest_date" '$1 < latest_date {print $2}' | xargs -d '\n' rm -f

    if [ $? -ne 0 ]; then
        log_message "Error: Failed to remove old files."
    fi
}
# Function to check available memory in /storage partition
check_storage() {
    local available_space=$(df /storage | awk 'NR==2 {print $4}')
    echo $available_space
}

# Function to convert available space from KB to MB
convert_to_mb() {
    local available_space_kb=$1
    local available_space_mb=$((available_space_kb / 1024))
    echo $available_space_mb
}

