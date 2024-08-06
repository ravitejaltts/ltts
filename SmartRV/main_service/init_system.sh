#!/bin/bash

# Check if storage partition exists
PART_CHECK=$("lsblk")
if echo "$PART_CHECK" | grep -q "/storage"; then
    echo "Storage Partition present"
else
    echo "Storage Partition missing"
    # What to do to fix ?

    # Mount and run FSCK ?
    # Get the system specific storage partition
    # fsck /dev/mmcblk0p10

    # mkdir /storage
    # mount /dev/mmcblk0p10 /storage

    # If that fails recreate the partition and reboot
    # Recreate partition
    # mkfs.ext4 /dev/mmcblk0p10
    # Reboot
fi


# Turn display on
# TODO: Replace with a function in main_service on startup
# echo 0 > /sys/class/graphics/fb0/blank

# Set brightness to 80%
# echo 40 > /sys/devices/platform/backlight/backlight/backlight/brightness

# Remove kiosk-browser cache
# rm -rf /.cache/qt-kiosk-browser
# rm -rf /root/.cache/qt-kiosk-browser
# rm -rf /home/weston/.cache/qt-kiosk-browser

# Factory Reset
# cansend can0 0CFC0044#20DC66
# Config Lighting Controllers
# # Turn on
# cansend can0 0CFC0044#FFFF0A0100
# # Turn all zones off
# cansend can0 0CFC0044#FFFF06FF0000
# # Set Cycle times
# cansend can0 0CFC0044#FFFF32FFFFFFFF
# # Unlock / turn off
# cansend can0 0CFC0044#FFFF06FF0000
# # Set Lightmode to single color
# cansend can0 0CFC0044#FFFF02FF00
# # Set color to white
# cansend can0 0CFC0044#FFFF01FFFFFFFF00
# Set off
# Cut here after initializing within hw_lighting
# ------------------
# Set 'Doorset' to on
# cansend can0 0CFC0044#20DC06010100
# cansend can0 0CFC0044#20DC03011010

# # Set color temp range 3000K - 10000K
# # cansend can0 0CFC0044#FFFF3DFF0BB83000
# # cansend can0 0CFC0044#FFFF3C012000


# # Set bath light to 100% brightness but off, blips for a brief period
# cansend can0 0CFC0044#20DC06040100
# cansend can0 0CFC0044#20DC03046464
# cansend can0 0CFC0044#20DC06040000

# Set single color mode again to be sure
# All Zones and controllers
# cansend can0 0CFC0044#FFFF02FF00
