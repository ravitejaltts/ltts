#!/bin/bash

ssh $1 "mount -o remount,rw /"
ssh-copy-id -i $2 $1
ssh $1 "mount -o remount,ro /"

