#!/bin/bash

. ./functions.sh

# Check if the latest_bld file is present
BLD_NAME="${WGO_USER_STORAGE}/latest_bld"
OK_NAME="${WGO_USER_STORAGE}/OK"

if [ -f "$BLD_NAME" ]; then
    # reset the log file
    #"Start" > $LOGFILE

    first_line=$(head -n 1 "$BLD_NAME"  | xargs)
    length=${#first_line}
    if [ $length -lt 3 ]; then
        log_message "Error: BLD_NAME not long enough!!."
        last_error  "Error: BLD_NAME not long enough!!."
        ## ensure the firstline is not empty which would move the root dir
        systemctl restart smartrv-kiosk
        exit 0
    else
        log_message "BLD_NAME $first_line "
    fi
    log_message "BLD Line -  $first_line"
    SOURCE_DIR="${WGO_USER_STORAGE}/${first_line}"

    # Check if the DEST_DIR environment variable is set
    if [ -z "$WGO_HOME_DIR" ]; then
        log_message "Error: WGO_HOME_DIR environment variable is not set."
        last_error "Error: WGO_HOME_DIR environment variable is not set."
        systemctl restart smartrv-kiosk
        exit 0
    fi

    log_message "Found destination directory: $WGO_HOME_DIR"

    # Check if the source directory exists
    if [ ! -d "$SOURCE_DIR" ]; then
        log_message "Error: Source directory '$SOURCE_DIR' does not exist."
        last_error "Error: Source directory '$SOURCE_DIR' does not exist."
        systemctl restart smartrv-kiosk
        exit 0
    fi

    log_message "Found source directory: $SOURCE_DIR"

    mount -o remount,rw /
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to remount / as writable."
        last_error "Error: Failed to remount / as writable."
        exit 1
    fi

    # Stop the smartrv services
    systemctl stop smartrv-iot
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to stop iot service."
        last_error "Error: Failed to stop iot service."
        # Attemp recovery
        systemctl start smartrv-main
        mount -o remount,r /
        exit 4
    fi

    # Stop the smartrv services
    systemctl stop smartrv-can
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to stop can service."
        last_error "Error: Failed to stop can service."
        # Attemp recovery
        systemctl start smartrv-main
        systemctl start smartrv-iot
        mount -o remount,r /
        exit 5
    fi

    systemctl stop smartrv-main
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to stop main service."
        last_error "Error: Failed to stop main service."
        # Attemp recovery
        mount -o remount,r /
        systemctl start smartrv-main
        systemctl start smartrv-iot
        systemctl start smartrv-can
        exit 6
    fi

    systemctl stop smartrv-bluetooth
    if [ $? -ne 0 ]; then
        log_message "Error: Failed to stop bluetooth service."
        last_error "Error: Failed to stop bluetooth service."
        # Attemp recovery
        mount -o remount,r /
        systemctl start smartrv-main
        systemctl start smartrv-iot
        systemctl start smartrv-can
        exit 7
    fi

    log_message "/ remounted as writable successfully."

    # Copy new and replace files
    cp -r "$SOURCE_DIR/." "$WGO_HOME_DIR/" 2>/storage/wgo/logs/ota_error.log
    # we added a copy below which eliminated a check that this one worked

    if [ $? -eq 0 ]; then
        log_message "cp services successful!"
    else
        log_message "cp services FAILED - s: $SOURCE_DIR d: $WGO_HOME_DIR"
        last_error "cp services FAILED - s: $SOURCE_DIR d: $WGO_HOME_DIR"
        # exit , reboot and retry?
        #exit 8
        # or exit, not reboot and go around again which exit 0 will do
        # this is a bad state with unknown serices having failed to copy
        exit 0
    fi

    # Copy frontend
    cp -r "$SOURCE_DIR/smartrv-frontend/." "$WGO_FRONTEND_DIR/" 2>/storage/wgo/logs/ota_error.log

    if [ $? -eq 0 ]; then
        log_message "cp frontend successful!"
        /opt/smartrv/update_service/version_update.sh
    else
        log_message "cp frontend FAILED!"
        last_error "cp frontend FAILED!"
        # exit , reboot and retry?
        #exit 8
        # or exit, not reboot and go around again which exit 0 will do
        # this is a bad state with unknown serices having failed to copy
        exit 0
    fi

    # Check if the cp was successful
    if [ $? -eq 0 ]; then
        log_message "version update successful!"

        cat "$BLD_NAME" > "${WGO_USER_STORAGE}/part_III" 2>/storage/wgo/logs/ota_error.log
         if [ $? -eq 0 ]; then
            # remove the OK file - this will be double check
            rm -f "$OK_NAME"

            # remove the latest_bld file
            rm -f "$BLD_NAME"
        else
            # This will send the script around again leaving the OK
            log_message "Error: Failed to cat part_III file."
            # We will need to check that the OK file exists but "$BLD_NAME" does not
            exit 9
        fi
    else
        log_message "Error: Failed to cp directory."
        last_error "Error: Failed to cp directory."
    fi
fi

# Check if the latest_bld file is present
PARTII_NAME="${WGO_USER_STORAGE}/part_III"

if [[ -f "$PARTII_NAME" ]]; then
    # Run the second section of the script
    log_message "Running remove section of the script..."
    # (Your commands for the second section go here)

    first_line=$(head -n 1 "$PARTII_NAME"  | xargs)
    log_message "BLD Line -  $first_line"
    length=${#first_line}
    if [ $length -lt 3 ]; then
        log_message "Error: Remove BLD_NAME not long enough!!."
        last_error "Error: Remove BLD_NAME not long enough!!."
        ## ensure the firstline is not empty which would move the root dir
    else
        SOURCE_DIR="${WGO_USER_STORAGE}/${first_line}"

        # Check if the source directory exists
        if [ -d "$SOURCE_DIR" ]; then
            log_message "Remove Source directory '$SOURCE_DIR' "

        # Remove the original directory
            rm -rf "$SOURCE_DIR"
            if [ $? -eq 0 ]; then
                log_message "Original directory removed."
            else
                log_message "Error: Failed to remove the original directory."
            fi
        fi
    fi

    #WGO_USER_STORAGE
    PKDIRECTORY="${WGO_USER_STORAGE}/packages"

    # Check if the directory exists
    if [ -d "$PKDIRECTORY" ]; then

        # Go to the specified directory
        cd $PKDIRECTORY
        if [ $? -eq 0 ]; then
            log_message "Packages in  '$PKDIRECTORY' "

            # Remove files that start with a dash - they would stop the next remove all function
            find . -type f -name '-*' -exec rm -f -- {} +
            if [ $? -ne 0 ]; then
                log_message "Error: Failed to remove files starting with a dash."
            fi

            # 1: Remove everything except .json files
            find . -type f -name '*.json' ! -newermt "$release_date" -exec rm -f -- {} +
            if [ $? -ne 0 ]; then
                log_message "Failed to remove non-.json files from packages dir."
            fi
            # 2: Remove empty directories
            find . -depth -type d -empty -exec rmdir ./{} +
            if [ $? -ne 0 ]; then
                log_message "Failed to find / remove empty directories from packages dir. There may not be any."
            fi
            # 3: Check if there are any files or directories left other than .json files
            leftovers=$(find . -type f ! -name '*.json' -o -type d ! -empty)

            if [ -n "$leftovers" ]; then
                echo "Error: There are files or non-empty directories left in the directory other than .json files:" >> error_log.txt
                echo "$leftovers" >> error_log.txt
            else
                echo "Success: Only .json files are left in the directory."
            fi

        else
            log_message "Error: failed to cd to Directory '$PKDIRECTORY' ."
            last_error "Error: failed to cd to Directory '$PKDIRECTORY' ."
        fi
    else
        log_message "Error: Directory '$PKDIRECTORY' does not exist."
        last_error "Error: Directory '$PKDIRECTORY' does not exist."
    fi

    #!/bin/bash

    log_message "Starting Frontend cleanup process..."

    remove_old_files /opt/smartrv/smartrv-frontend/static/js
    if [ $? -ne 0 ]; then
            log_message "Fail - Frontend clean 1 not found /opt/smartrv/smartrv-frontend/static/js"
            exit
    fi

    remove_old_files /opt/smartrv/smartrv-frontend/static/css
    if [ $? -ne 0 ]; then
            log_message "Fail - Frontend clean 2 not found /opt/smartrv/smartrv-frontend/static/css"
            exit
    fi

    # Not sure this is needed - seems to copy the complete dir
    remove_old_files /opt/smartrv-frontend/static/js
    if [ $? -ne 0 ]; then
            log_message "Fail - Frontend dir not found /opt/smartrv-frontend/static/js"
            exit
    fi

    remove_old_files /opt/smartrv-frontend/static/css
    if [ $? -ne 0 ]; then
            log_message "Fail - Frontend dir not found /opt/smartrv-frontend/static/css"
            exit
    fi
    log_message "Cleanup completed."

    # Stop Kiosk
    systemctl stop smartrv-kiosk

    # Clear Browser Cache
    rm -rf /.cache/qt-kiosk-browser
    rm -rf /root/.cache/qt-kiosk-browser
    rm -rf /home/weston/.cache/qt-kiosk-browser

    # No need to restart the kiosk as we reboot down below

    # Once done, remove 'partII'
    rm -f "$PARTII_NAME"
    sleep 1 # settle
    sync
    sleep 2 # settle
    mount -o remount,ro /  # might not work so we reboot next

    ## Call system reboot here
    # The only way to ensure read only root
    log_message "Services restart needed system will shutdown."
    last_error "OTA Done - restarting"
    /bin/systemctl reboot

else
    # Done no file to process
    log_message "Finished: no file to process $BLD_NAME"
fi
