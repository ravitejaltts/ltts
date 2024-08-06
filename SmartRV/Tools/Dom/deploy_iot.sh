export WGO_PORT=22
#export WGO_PORT=8022

export WGO_LOCAL=$1

# Package folders

#export TARGET_FOLDER=/opt/smartrv
export TARGET_FOLDER=/opt/smartrv/iot_service

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "mount -o remount,rw /"

# Copy my iot services to the TARGET_FOLDER path
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r /Users/dom/Documents/1_Projects/1_Winnebago/2_Dev/SmartRV/iot_service/* $WGO_LOCAL:$TARGET_FOLDER

# scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r /Users/dom/Documents/1_Projects/1_Winnebago/2_Dev/SmartRV/hmi_tools/place_bld.sh /opt/smartrv/utils

# Not in the image yet  maybe we need to copy all of  data for this iot update
# scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r /home/bruce/SmartRV/data//VANILLA_ota_template.json $WGO_LOCAL:/opt/smartrv/data

# present in /opt/oem
# scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r /opt/smartRv/oem/*  $WGO_LOCAL:/opt/smartrv/oem
