#!/usr/bin/env bas
cd test_cmake
mkdir build
cmake -S . -B build
cmake --build build
cmake --install build
