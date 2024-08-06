#!/bin/bash

ifconfig can0 down
ip link set can0 type can bitrate 250000 sample-point 0.875 restart-ms 250
ifconfig can0 up
