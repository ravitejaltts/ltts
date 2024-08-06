#!/bin/bash

systemctl stop smartrv-kiosk
rm -rf /home/weston/.cache/qt-kiosk-browser
systemctl start smartrv-kiosk
