# Winnebago HMI SmartRV


## Questions


## HMI Testing
- Wireguard to Dave
- HMI is at 10.



## CAN

    ifconfig can0 down
    
    ip link set can0 type can bitrate 250000
    ifconfig can0 up
    

## Temperature

    cat /sys/class/hwmon/hwmon0/temp1_input

## Display

    # Off
    echo 4 > /sys/class/graphics/fb0/blank

    # On
    echo 0 > /sys/class/graphics/fb0/blank


    # Brightness
    cat 

    <!-- echo 100 > /sys/class/backlight/pwm-backlight.0/brightness -->
    echo 10 > /sys/class/backlight/backlight/brightness 

echo 0 > /sys/class/graphics/fb0/blank


### Links
https://support.garz-fricke.com/projects/Tanaro/Linux-Yocto/Releases/Yocto-dunfell-8.0/imx8mguf/




### ENV Variables
- WGO_SERVICE_UI_PORT
    Controls the port the UI Service runs on



### SETUP
10.10.10.101
- 3 Outlets
- Air Pressure
- Blink
- Charger
