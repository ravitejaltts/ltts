#!/bin/bash

scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $2 -r ./pyPackages/site-packages/* $1:/usr/lib/python3.8/site-packages/