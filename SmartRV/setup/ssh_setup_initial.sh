#!/bin/bash


# Option A
# Compress all repos in its current form in the parent folder and send as a single file

# Option B
# Set up git and check out from Repos
# TODO: Deploy git on device
# -------------------------------------

# Take parameters for username and ip
# Write setup script in file
# Chmod +x
# execute and read output

echo "Make writable if necessary"
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 -p $2 "mount -o remount,rw /"
#echo "Removing unneeded file catalogue"
# cat units/seco/fstab | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 -p $2 "cat > /etc/fstab;cat /etc/fstab"
# No longer necessary for 0.9.2
# cat prepare_guf.sh | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 -p $2 "cat > /tmp/remove_guf.sh;cd /tmp;chmod +x remove_guf.sh;./remove_guf.sh"

# GIT packaging
# git archive HEAD -o ${PWD##*/}.zip

echo "Packaging services"
./build_all.sh
./package.sh

echo "Transferring package"
# scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $WGO_PORT -r ../../build/* $WGO_LOCAL:/home/guf
cat package.tgz | ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 -p $2 "cat > /tmp/package.tgz;cd /tmp;tar -xzvf package.tgz -C ./hmi;mv -u hmi/* /home/guf/"
# TODO: Add dependency packages
echo 'Running setup script on target'
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $1 -p $2 "cd /home/guf;chmod +x setup.sh;./setup.sh"
# Remove setup.sh after success
# TODO: Figure out if we want to reboot separately, otherwise the pull won't work
# ./pull_python_packages.sh $1 $2
