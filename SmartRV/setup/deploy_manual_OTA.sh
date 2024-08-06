#!/bin/bash

export REMOTE=$1
export WGO_PORT=22

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $REMOTE -p $WGO_PORT "df -h"

# ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT "mount -o remount,rw /"
