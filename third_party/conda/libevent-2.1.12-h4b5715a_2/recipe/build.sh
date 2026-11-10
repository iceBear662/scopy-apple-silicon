#!/bin/bash
set -ex

mkdir build
cd build

cmake -G "Ninja" ${CMAKE_ARGS} \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH=$PREFIX \
    -DCMAKE_INSTALL_PREFIX=$PREFIX \
    ..

cmake --build . --config Release --target install

if [[ "$target_platform" == linux-* ]]; then
    # delete static libs
    rm $PREFIX/lib/libevent*.a
fi

# Remove Python script to avoid confusion and a Python dependency.
rm -fv "${PREFIX}/bin/event_rpcgen.py"
