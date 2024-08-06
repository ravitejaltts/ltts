#!/bin/bash

cd /home/guf
mkdir storage
cd storage
mkdir usb
mkdir sdcard

mount /dev/mmcblk1p1 sdcard
mount /dev/sda1 usb