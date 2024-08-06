#!/bin/bash
export WGO_PORT=22
export WGO_LOCAL=$1

ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $WGO_LOCAL -p $WGO_PORT
