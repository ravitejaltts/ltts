#!/bin/bash

rm -r /usr/share/bbb
rm -r /usr/share/guf-show-demo

# Remove all unneeded QT packages
# /usr/share/translations/


# Remove all folders that will be recreated (only needed to rerun this script)
rm -rf /tmp/*
rm -rf /home/guf/*

# Create all required folders
mkdir /tmp/hmi

# No longer necessary since 0.9.2
# # Create storage filesystem
# mkfs.ext4 /dev/mmcblk0p10
# mkdir /storage
# mount /dev/mmcblk0p10 /storage
