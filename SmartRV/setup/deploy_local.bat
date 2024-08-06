SET WGO_PORT=22
SET WGO_LOCAL=root@172.20.36.25
REM Package folders
REM build_all.bat

echo %WGO_PORT%
echo %WGO_LOCAL%



ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %WGO_LOCAL% -p %WGO_PORT% "df -h"

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %WGO_LOCAL -p %WGO_PORT% "mount -o remount,rw /"

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P %WGO_PORT% -r ..\..\build\* %WGO_LOCAL%:/home/guf 

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %WGO_LOCAL% -p %WGO_PORT% "systemctl restart ui;systemctl restart kiosk;systemctl restart can"

# ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %WGO_LOCAL% -p %WGO_PORT% "mount -o remount,ro /"

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %WGO_LOCAL% -p %WGO_PORT% "df -h"

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null %WGO_LOCAL% -p %WGO_PORT% "reboot"