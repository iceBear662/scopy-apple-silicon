#!/usr/bin/env bash

set -ex

cd build

# call install scripts directly because executing the install target re-builds
# (in that case, the re-build happens because timestamps have changed)
cmake -P cmake_install.cmake
