export WGO_PORT=22
#export WGO_PORT=8022

export WGO_LOCAL=$1


# Package folders
./build_all.sh $2

export TARGET_FOLDER=/opt/smartrv
export FRONTEND_TARGET_FOLDER=/opt/smartrv-frontend
#export TARGET_FOLDER=/home/guf

# Get version details of the unit
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "cat /etc/os-release"

# Print out space free TODO: Add a check
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "df -h"

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "systemctl stop smartrv-can"

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "systemctl stop smartrv-iot"

# Make the system writable for the update
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "mount -o remount,rw /"

# Copy all services to the TARGET_FOLDER path
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r ../../build/* $WGO_LOCAL:$TARGET_FOLDER

# Copy frontend to new path
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r ../../Frontend/client/build/* $WGO_LOCAL:$FRONTEND_TARGET_FOLDER

# Check space after process done and print out
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "df -h"


ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "systemctl stop smartrv-main"
# Remove user DB for now (TODO: Create migration for PROD)
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "rm /storage/wgo/wgo_user.db"

# Stop Kiosk to prevent caches being written again before reboot
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "systemctl stop smartrv-kiosk"

# Clear frontend caches (browser)
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "rm -rf /.cache/qt-kiosk-browser;rm -rf /root/.cache/qt-kiosk-browser;rm -rf /home/weston/.cache/qt-kiosk-browser"

# Try to mount RO again (likely fails due to mount point being busy)
#ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "mount -o remount,ro /"

# Clean reboot
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "reboot"
