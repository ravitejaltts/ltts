#!/bin/bash

rm package.tgz
cd ../../build
tar -czvf ../SmartRV/setup/package.tgz --exclude=*/tests  .
cd ../SmartRV/setup
# Generate checksum and echo for piping
shasum -a 256 package.tgz

# TODO: use vars to avoid renaming in multiple lines
