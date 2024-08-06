#!/bin/bash

if [[ -z "$1" ]]; then 
    PATH="/home/guf"
else
    PATH="$1"
fi

if [[ -z "$2" ]]; then
    ALL=""
else 
    ALL="-r"
fi

echo $ALL
echo $PATH

# scp -P 8022 -r root@localhost:"$PATH" ./pull/
/usr/bin/scp $ALL -P 8022 root@localhost:$PATH ./pull/
