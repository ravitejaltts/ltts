#export WGO_PORT=22
#export WGO_PORT=8022
export WGO_PORT=8222

export WGO_LOCAL=$1

# Package folders
./build_all.sh

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "df -h"

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "mount -o remount,rw /"

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r ../../build/* $WGO_LOCAL:/home/guf 

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "reboot"

