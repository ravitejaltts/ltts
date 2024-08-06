export WGO_PORT=22
#export WGO_PORT=8022

export WGO_LOCAL=$1

# Package folders

#export TARGET_FOLDER=/opt/smartrv
export TARGET_FOLDER=/storage/wgo

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "mount -o remount,rw /"

# Copy my can services to the TARGET_FOLDER path
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r /storage/wgo/* $WGO_LOCAL:$TARGET_FOLDER
