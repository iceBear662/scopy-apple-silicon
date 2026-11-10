#!/bin/bash

cd build

cmake -DCMAKE_INSTALL_LOCAL_ONLY=1 -P cmake_install.cmake

cmake -P apps/cmake_install.cmake

cmake -P lib/cmake_install.cmake
