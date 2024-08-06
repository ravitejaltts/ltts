#!/bin/bash

rm -rf pyPackages
mkdir pyPackages
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $2 -r $1:/usr/lib/python3.8/site-packages/ ./pyPackages

# Clean pycache files
cd pyPackages/site-packages

tar --exclude='*.pyc' --exclude='*__pycache__' -czvf ../pypackages.tgz --exclude=*/tests *

shasum -a 256 ../pypackages.tgz

cd ..
cd ..
