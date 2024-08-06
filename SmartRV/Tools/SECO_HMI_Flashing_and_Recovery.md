# SECO HMI Installation Routine


## Recovery through serial console (Pelican Case setups)

## Preconditions
- Device connected via LAN to the internet (Wifi technically works)
- Device can still boot uboot (boot fails at some point on regular boot)
- Power can be toggled (for rebooting and interrupting) either in person or remotely

## Bringup
- Establish serial connection to the HMI


        ~# screen /dev/TTYUSB0 115200

         

- Turn off power to HMI
- Power on
- Interrupt Autoboot by pressing ESC
- Switch to run the alternative bootloader once (this is a temporary setting)

        ~# env set script boot-alt.scr
        ~# run bootselect

Device should now load Flash N Go

- Check if device is connected

        ~# ping www.google.com

        PING www.google.com (172.217.14.196): 56 data bytes
        64 bytes from 172.217.14.196: icmp_seq=0 ttl=47 time=57.549 ms
        64 bytes from 172.217.14.196: icmp_seq=1 ttl=47 time=57.746 ms
    
- If device is not able to reach internet, verify settings in /etc/network/interfaces


        ~# nano /etc/network/interfaces

        ...
        auto eth0
        iface eth0 inet static
            address 192.168.1.1
            netmask 255.255.255.0
            gateway 192.168.1.100
            hwaddress ether 00:00:00:00:00:00


Change to
        
        auto eth0
        iface eth0 inet dhcp

Run the following command to restart network interface

        ifup eth0
    
Retry to reach Google


Mount SD card for storage (usually is at /dev/mmcblk1p1)

        ~# mkdir sdcard
        ~# mount /dev/mmcblk1p1
        ~# cd sdcard

### Option A (Install from SECO support page)


        # Actual URL might differ
        ~# export TFTP=https://support.garz-fricke.com/projects/Tanaro/Linux-Yocto/Releases/Yocto-dunfell-13.1/imx8mguf

        ~# curl $TFTP/fng-install.sh | sh

        ...

        ~# reboot

### Option B (Local Files)

    TBD

### Option C (Custom TFTP server)

        ~# export TFTP=http://{ip}/{path}
        # Point to the ip and path which contains the images and fng-install.sh

        ~# curl $TFTP/fng-install.sh | sh

        ...

        ~# reboot