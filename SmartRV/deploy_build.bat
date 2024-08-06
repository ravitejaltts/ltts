REM

REM Remove the services that might have duplication if not deleted completely
ssh %1 "rm -rf /home/guf/main_service"
ssh %1 "rm -rf /home/guf/bt_service"

scp -r * %1:/home/guf

REM Check if setup.sh needs to run
ssh %1 "cd /home/guf;chmod +x setup.sh;./setup.sh"
